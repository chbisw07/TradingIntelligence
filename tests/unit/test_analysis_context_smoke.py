"""Read-only AnalysisContext smoke CLI tests without network access."""

import runpy
import sys
from collections.abc import Callable
from datetime import datetime
from typing import cast

import pytest

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data import InstrumentQuery
from tiaf.data.resolution import ResolutionResult
from tiaf.data.runtime import (
    DataFetchCoordinator,
    ProviderScheduler,
    RatePolicy,
    RatePolicyRegistry,
)

from .context._support import NOW, FakeMarketProvider, FakeResolver, quote, resolved


def test_analysis_context_smoke_builds_and_reuses_factual_context(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    namespace = runpy.run_path("scripts/analysis_context_smoke.py")
    market = FakeMarketProvider()
    current = datetime.now(TIAF_TIMEZONE)
    market.quote_value = quote(observed_at=current, received_at=current)
    market.history_value = market.history_value.model_copy(update={"observed_at": current})

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "analysis-context-smoke",
            "--symbol",
            "RELIANCE",
            "--history-interval",
            "1d",
            "--lookback-days",
            "90",
            "--repeat",
        ],
    )
    main = cast(Callable[[], int], namespace["main"])
    main.__globals__["DhanMarketDataProvider"] = lambda: market
    main.__globals__["DhanInstrumentResolver"] = FakeResolver
    assert main() == 0

    output = capsys.readouterr().out
    assert "TRADINGINTELLIGENCE ANALYSIS CONTEXT" in output
    assert "FIRST BUILD" in output
    assert "SECOND BUILD" in output
    assert "Source          : PROVIDER" in output
    assert "Source          : CACHE" in output
    assert "BUY" not in output
    assert "SELL" not in output
    assert market.quote_calls == 1
    assert len(market.history_calls) == 1


def test_analysis_context_smoke_requires_explicit_derivatives_expiry(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    namespace = runpy.run_path("scripts/analysis_context_smoke.py")
    monkeypatch.setattr(
        sys,
        "argv",
        ["analysis-context-smoke", "--include-derivatives"],
    )
    main = cast(Callable[[], int], namespace["main"])
    assert main() == 2
    assert "--expiry is required" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("flag", "required", "complete"),
    [
        ("--include-derivatives", "YES", "NO"),
        ("--optional-derivatives", "NO", "YES"),
    ],
)
def test_analysis_context_smoke_exposes_derivative_requirement_role(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    flag: str,
    required: str,
    complete: str,
) -> None:
    namespace = runpy.run_path("scripts/analysis_context_smoke.py")
    market = FakeMarketProvider()
    current = datetime.now(TIAF_TIMEZONE)
    market.quote_value = quote(observed_at=current, received_at=current)
    market.history_value = market.history_value.model_copy(update={"observed_at": current})
    monkeypatch.setattr(
        sys,
        "argv",
        ["analysis-context-smoke", flag, "--expiry", "2035-01-01"],
    )
    main = cast(Callable[[], int], namespace["main"])
    main.__globals__["DhanMarketDataProvider"] = lambda: market
    main.__globals__["DhanInstrumentResolver"] = FakeResolver

    assert main() == 0

    output = capsys.readouterr().out
    option_section = output.split("Option Chain", maxsplit=1)[1].split(
        "Overall", maxsplit=1
    )[0]
    assert "Requested       : YES" in option_section
    assert f"Required        : {required}" in option_section
    assert "Status          : FAILED" in option_section
    assert f"Complete        : {complete}" in output


def test_analysis_context_batch_smoke_preserves_order_and_failures(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    namespace = runpy.run_path("scripts/analysis_context_smoke.py")
    missing_query = InstrumentQuery(symbol="HDFCBANK")
    missing = ResolutionResult(
        query=missing_query,
        matches=(),
        not_found=True,
        observed_at=NOW,
    )
    resolver = FakeResolver({"HDFCBANK": missing})
    market = FakeMarketProvider()
    current = datetime.now(TIAF_TIMEZONE)
    market.quote_value = quote(observed_at=current, received_at=current)
    market.history_value = market.history_value.model_copy(update={"observed_at": current})
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "analysis-context-smoke",
            "--symbols",
            "RELIANCE,HDFCBANK,KAYNES",
        ],
    )
    main = cast(Callable[[], int], namespace["main"])
    main.__globals__["DhanMarketDataProvider"] = lambda: market
    main.__globals__["DhanInstrumentResolver"] = lambda: resolver

    assert main() == 0

    output = capsys.readouterr().out
    reliance_position = output.index("1. RELIANCE")
    hdfc_position = output.index("2. HDFCBANK")
    kaynes_position = output.index("3. KAYNES")
    assert reliance_position < hdfc_position < kaynes_position
    hdfc_section = output[hdfc_position:kaynes_position]
    assert "Status          : ERROR" in hdfc_section
    assert "Error Type      : AnalysisContextResolutionError" in hdfc_section


def test_analysis_context_batch_smoke_prints_scheduler_deferrals_truthfully(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    namespace = runpy.run_path("scripts/analysis_context_smoke.py")
    current = datetime.now(TIAF_TIMEZONE)
    market = FakeMarketProvider()
    market.quote_value = quote(observed_at=current, received_at=current)
    market.history_value = market.history_value.model_copy(update={"observed_at": current})
    outcomes: dict[str, ResolutionResult] = {}
    for symbol, provider_id in (("HDFCBANK", "1333"), ("KAYNES", "12092")):
        query = InstrumentQuery(symbol=symbol)
        match = resolved(symbol, provider_id)
        outcomes[symbol] = ResolutionResult(
            query=query,
            matches=(match,),
            resolved=match,
            observed_at=current,
            source_provider="test",
        )
    resolver = FakeResolver(outcomes)
    scheduler = ProviderScheduler(
        RatePolicyRegistry(
            (
                RatePolicy(
                    provider="test",
                    operation="quote",
                    minimum_interval_seconds=2,
                ),
            )
        ),
        monotonic_clock=lambda: 100.0,
        wall_clock=lambda: current,
    )
    coordinator = DataFetchCoordinator(scheduler=scheduler, wall_clock=lambda: current)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "analysis-context-smoke",
            "--symbols",
            "RELIANCE,HDFCBANK,KAYNES",
        ],
    )
    main = cast(Callable[[], int], namespace["main"])
    main.__globals__["DhanMarketDataProvider"] = lambda: market
    main.__globals__["DhanInstrumentResolver"] = lambda: resolver
    main.__globals__["DataFetchCoordinator"] = lambda **_: coordinator

    assert main() == 0

    output = capsys.readouterr().out
    reliance_position = output.index("1. RELIANCE")
    hdfc_position = output.index("2. HDFCBANK")
    kaynes_position = output.index("3. KAYNES")
    assert reliance_position < hdfc_position < kaynes_position
    assert "Status          : COMPLETE_CONTEXT" in output[reliance_position:hdfc_position]
    for section in (output[hdfc_position:kaynes_position], output[kaynes_position:]):
        assert "Status          : DEFERRED" in section
        assert "Reason          : PROVIDER_SCHEDULE_BLOCKED" in section
        assert "Provider        : test" in section
        assert "Operation       : quote" in section
        assert "Gate State      : RATE_LIMITED" in section
        assert "Retry After     : 2.00 sec" in section
        assert "Quality" not in section
        assert "Retrieval Fresh." not in section
    assert market.quote_calls == 1
