import sys
from collections.abc import Mapping
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import JsonValue

SCRIPT = Path(__file__).resolve().parents[3] / "scripts/yahoo_live_acceptance.py"
SPEC = spec_from_file_location("tiaf_yahoo_live_acceptance", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
live = cast(Any, module_from_spec(SPEC))
sys.modules[SPEC.name] = live
SPEC.loader.exec_module(live)


class FakeLiveYahooClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, JsonValue]]] = []
        self.server_name = "Yahoo Finance MCP Server"
        self.server_version = "test-version"

    def __enter__(self) -> "FakeLiveYahooClient":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def call_tool(
        self, tool_name: str, arguments: Mapping[str, JsonValue]
    ) -> Mapping[str, object]:
        self.calls.append((tool_name, dict(arguments)))
        ticker = str(arguments["ticker"])
        if tool_name == "yfinance_get_stock_info":
            return {
                "structuredContent": {
                    "ticker": ticker,
                    "name": f"{ticker} Limited",
                    "currency": "INR",
                    "current_price": 100.0,
                }
            }
        if tool_name == "yfinance_get_stock_financials":
            return {
                "structuredContent": {
                    "ticker": ticker,
                    "statement_type": "Income Statement",
                    "period_type": "annual",
                    "data": {
                        "FY2026": {
                            "Total Revenue": 1000.0,
                            "Uncertain Yahoo Field": 7.0,
                        }
                    },
                }
            }
        if tool_name == "yfinance_get_earnings_dates":
            return {
                "structuredContent": {
                    "ticker": ticker,
                    "earnings_history": [
                        {
                            "date": "2026-06-30",
                            "eps_estimate": 10.0,
                            "eps_reported": 11.0,
                            "surprise_percent": 10.0,
                        }
                    ],
                }
            }
        if tool_name == "yfinance_get_stock_news":
            return {
                "structuredContent": {
                    "ticker": ticker,
                    "news": [
                        {
                            "title": "Reliance announces project update",
                            "description": "Factual update.",
                            "publisher": "Example News",
                            "link": "https://example.test/reliance-update",
                            "published": "2026-09-09T04:30:00Z",
                        }
                    ],
                }
            }
        if tool_name == "yfinance_get_stock_recommendations":
            return {
                "structuredContent": {
                    "error": f"No recommendations found for {ticker}"
                }
            }
        raise AssertionError(f"unexpected tool: {tool_name}")


def test_without_live_flag_makes_no_external_call(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.argv", ["yahoo_live_acceptance.py"])
    monkeypatch.setattr(
        live,
        "YahooMcpClient",
        lambda: (_ for _ in ()).throw(AssertionError("connector constructed")),
    )
    assert live.main() == 0
    assert "disabled" in capsys.readouterr().out


def test_missing_uvx_stops_before_connector_construction(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.argv", ["yahoo_live_acceptance.py", "--live"])
    monkeypatch.setattr(live.shutil, "which", lambda command: None)
    monkeypatch.setattr(
        live,
        "YahooMcpClient",
        lambda: (_ for _ in ()).throw(AssertionError("connector constructed")),
    )
    assert live.main() == 2
    output = capsys.readouterr().out
    assert "not installed" in output
    assert "do not" not in output.casefold()


def test_bounded_fake_run_proves_full_acceptance_path(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    client = FakeLiveYahooClient()
    monkeypatch.setattr("sys.argv", ["yahoo_live_acceptance.py", "--live"])
    monkeypatch.setattr(live.shutil, "which", lambda command: "/test/uvx")
    monkeypatch.setattr(live, "YahooMcpClient", lambda: client)
    assert live.main() == 0
    output = capsys.readouterr().out
    assert '"accepted": true' in output
    assert '"fallback_rate_limited_to_yahoo": true' in output
    assert '"offline_replay_and_fingerprints_exact": true' in output
    assert '"empty_recommendations_not_failure": true' in output
    assert len(client.calls) == 10
