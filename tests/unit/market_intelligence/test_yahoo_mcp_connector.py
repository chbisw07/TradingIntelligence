import pytest
from mcp.types import CallToolResult, TextContent
from pydantic import JsonValue

from tiaf.market_intelligence.providers import (
    YAHOO_READ_TOOLS,
    YahooMalformedResultError,
    YahooMcpClient,
    YahooProcessLaunchError,
    YahooSchemaDriftError,
    YahooToolNotAllowedError,
)
from tiaf.market_intelligence.providers.yahoo_mcp import _provider_native_payload


class FakeWorkerYahooClient(YahooMcpClient):
    def __init__(self) -> None:
        super().__init__(command="true")

    def _worker_main(self) -> None:
        self._advertised_tools = YAHOO_READ_TOOLS
        self._server_name = "Yahoo Finance MCP Server"
        self._server_version = "FastMCP 4.0.3"
        self._ready.set()
        while True:
            pending = self._requests.get()
            if pending is None:
                self._stopped.set()
                return
            pending.response = {
                "isError": False,
                "structuredContent": {"ticker": pending.arguments["ticker"]},
            }
            pending.completed.set()


def test_allowlisted_yahoo_call_uses_reusable_sync_facade() -> None:
    with FakeWorkerYahooClient() as client:
        response = client.call_tool(
            "yfinance_get_stock_info",
            {"ticker": "RELIANCE.NS", "response_format": "json"},
        )
        assert response["structuredContent"] == {"ticker": "RELIANCE.NS"}
        assert client.server_name == "Yahoo Finance MCP Server"


def test_non_allowlisted_yahoo_tool_is_rejected_before_worker_start() -> None:
    client = FakeWorkerYahooClient()
    with pytest.raises(YahooToolNotAllowedError, match="read-only allowlist"):
        client.call_tool("yfinance_get_options_chain", {"ticker": "RELIANCE.NS"})
    assert client._thread is None


def test_json_text_result_is_preserved_as_provider_native_payload() -> None:
    result = CallToolResult(
        isError=False,
        content=[TextContent(type="text", text='{"ticker":"RELIANCE.NS","price":1}')],
    )
    assert _provider_native_payload(result)["structuredContent"] == {
        "ticker": "RELIANCE.NS",
        "price": 1,
    }


def test_fastmcp_string_result_wrapper_is_preserved_for_adapter_unwrapping() -> None:
    encoded = '{"ticker":"RELIANCE.NS","name":"Reliance Industries Limited"}'
    result = CallToolResult(
        isError=False,
        content=[TextContent(type="text", text=encoded)],
        structuredContent={"result": encoded},
    )
    payload = _provider_native_payload(result)
    assert payload["structuredContent"] == {"result": encoded}
    assert payload["content"] == [{"type": "text", "text": encoded}]


def test_provider_error_result_preserves_error_semantics() -> None:
    result = CallToolResult(
        isError=True,
        content=[TextContent(type="text", text='{"error":"service unavailable"}')],
    )
    payload = _provider_native_payload(result)
    assert payload["isError"] is True
    assert payload["structuredContent"] == {"error": "service unavailable"}


def test_empty_yahoo_mcp_result_is_malformed() -> None:
    with pytest.raises(YahooMalformedResultError, match="no JSON or text"):
        _provider_native_payload(CallToolResult(content=[]))


def test_allowlisted_but_unadvertised_yahoo_tool_reports_schema_drift() -> None:
    class DriftClient(FakeWorkerYahooClient):
        def _worker_main(self) -> None:
            self._advertised_tools = frozenset({"yfinance_get_stock_info"})
            self._ready.set()
            pending = self._requests.get()
            if pending is not None:
                pending.completed.set()

    client = DriftClient()
    try:
        with pytest.raises(YahooSchemaDriftError, match="not advertised"):
            client.call_tool(
                "yfinance_get_stock_financials",
                {"ticker": "RELIANCE.NS"},
            )
    finally:
        client.close()


def test_missing_uvx_is_a_sanitized_launch_failure() -> None:
    client = YahooMcpClient(command="definitely-not-an-installed-command")
    with pytest.raises(YahooProcessLaunchError, match="command is not installed"):
        client.start()


def test_yahoo_connector_does_not_mutate_json_arguments() -> None:
    arguments: dict[str, JsonValue] = {
        "ticker": "KAYNES.NS",
        "response_format": "json",
    }
    original = dict(arguments)
    with FakeWorkerYahooClient() as client:
        client.call_tool("yfinance_get_stock_info", arguments)
    assert arguments == original
