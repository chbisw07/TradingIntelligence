import json

import pytest
from mcp.types import CallToolResult, TextContent
from pydantic import JsonValue

from tiaf.market_intelligence.providers import (
    TAPETIDE_READ_TOOLS,
    TapetideCredentialError,
    TapetideMalformedResultError,
    TapetideMcpClient,
    TapetideProcessLaunchError,
    TapetideSchemaDriftError,
    TapetideToolNotAllowedError,
)
from tiaf.market_intelligence.providers.tapetide_mcp import _provider_native_payload


class FakeWorkerTapetideClient(TapetideMcpClient):
    """Exercise the synchronous facade without launching a normal unit-test process."""

    def _worker_main(self) -> None:
        self._advertised_tools = TAPETIDE_READ_TOOLS
        self._server_name = "tapetide-test"
        self._server_version = "1.0.0"
        self._ready.set()
        while True:
            pending = self._requests.get()
            if pending is None:
                self._stopped.set()
                return
            pending.response = {
                "isError": False,
                "structuredContent": {"symbol": pending.arguments["symbol"]},
            }
            pending.completed.set()


def test_allowlisted_call_succeeds_through_reusable_sync_facade() -> None:
    with FakeWorkerTapetideClient("test-token") as client:
        response = client.call_tool("get_company_profile", {"symbol": "RELIANCE"})
        assert response["structuredContent"] == {"symbol": "RELIANCE"}
        assert client.server_name == "tapetide-test"
        assert client.server_version == "1.0.0"


def test_non_allowlisted_tool_is_rejected_before_worker_start() -> None:
    client = FakeWorkerTapetideClient("test-token")
    with pytest.raises(TapetideToolNotAllowedError, match="read-only allowlist"):
        client.call_tool("add_to_watchlist", {"symbols": ["RELIANCE"]})
    assert client._thread is None


def test_missing_token_is_a_clear_preflight_failure() -> None:
    with pytest.raises(TapetideCredentialError, match="TAPETIDE_TOKEN is required"):
        TapetideMcpClient.from_environment(
            environment={},
            load_repository_env=False,
        )


def test_provider_error_result_preserves_is_error_and_parsed_json() -> None:
    result = CallToolResult(
        isError=True,
        content=[TextContent(type="text", text='{"code":"429","error":"rate limit"}')],
    )
    payload = _provider_native_payload(result)
    assert payload == {
        "isError": True,
        "content": [
            {"type": "text", "text": '{"code":"429","error":"rate limit"}'}
        ],
        "structuredContent": {"code": "429", "error": "rate limit"},
    }


def test_non_json_provider_error_becomes_provider_native_error_text() -> None:
    result = CallToolResult(
        isError=True,
        content=[TextContent(type="text", text="provider unavailable")],
    )
    payload = _provider_native_payload(result)
    assert payload["structuredContent"] == {"error": "provider unavailable"}


def test_empty_mcp_result_is_rejected_as_malformed() -> None:
    with pytest.raises(TapetideMalformedResultError, match="no JSON or text"):
        _provider_native_payload(CallToolResult(content=[]))


def test_allowlisted_but_unadvertised_tool_reports_schema_drift() -> None:
    class DriftClient(FakeWorkerTapetideClient):
        def _worker_main(self) -> None:
            self._advertised_tools = frozenset({"get_company_profile"})
            self._ready.set()
            pending = self._requests.get()
            if pending is not None:
                pending.completed.set()

    client = DriftClient("test-token")
    try:
        with pytest.raises(TapetideSchemaDriftError, match="not advertised"):
            client.call_tool("get_financials", {"symbol": "RELIANCE"})
    finally:
        client.close()


def test_secret_is_never_in_launch_failure() -> None:
    secret = "super-secret-token-value"
    client = TapetideMcpClient(secret, command="definitely-not-an-installed-command")
    with pytest.raises(TapetideProcessLaunchError) as captured:
        client.start()
    assert secret not in str(captured.value)


def test_secret_is_redacted_from_provider_native_result() -> None:
    secret = "provider-result-secret"
    result = CallToolResult(
        isError=False,
        content=[
            TextContent(
                type="text",
                text=f"Tapetide rate limit reached; TAPETIDE_TOKEN={secret}",
            )
        ],
        structuredContent={
            "error": f"Authorization: Bearer {secret}",
            "nested": {"value": secret},
        },
    )

    serialized = json.dumps(_provider_native_payload(result, secret=secret))
    assert secret not in serialized
    assert "[REDACTED]" in serialized


def test_connector_accepts_json_arguments_without_mutating_them() -> None:
    arguments: dict[str, JsonValue] = {"symbol": "KAYNES", "include": ["identity"]}
    original = dict(arguments)
    with FakeWorkerTapetideClient("test-token") as client:
        client.call_tool("get_company_profile", arguments)
    assert arguments == original
