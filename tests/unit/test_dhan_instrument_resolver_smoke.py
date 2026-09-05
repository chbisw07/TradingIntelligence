"""CLI regressions for the credential-free instrument resolver smoke utility."""

import runpy
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast

import pytest

from tiaf.contracts import DataQuality
from tiaf.data import InstrumentKey, InstrumentType, MarketSegment
from tiaf.data.resolution import (
    InstrumentQuery,
    ResolutionKind,
    ResolutionPolicy,
    ResolutionResult,
    ResolvedInstrument,
)


def _match() -> ResolvedInstrument:
    observed_at = datetime(2026, 9, 5, tzinfo=UTC)
    instrument = InstrumentKey(
        symbol="RELIANCE",
        exchange="NSE",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
        trading_symbol="RELIANCE",
        provider_instrument_id="2885",
    )
    return ResolvedInstrument(
        instrument=instrument,
        provider_name="DHAN",
        provider_instrument_id="2885",
        source_record_id="dhan:NSE_EQUITY:2885",
        source_observed_at=observed_at,
        resolution_kind=ResolutionKind.EXACT,
        quality=DataQuality.GOOD,
    )


def test_cli_symbol_lookup_reaches_resolver(monkeypatch: pytest.MonkeyPatch) -> None:
    namespace = runpy.run_path("scripts/dhan_instrument_resolver_smoke.py")
    captured: dict[str, InstrumentQuery] = {}
    match = _match()

    class FakeResolver:
        def resolve(self, query: InstrumentQuery) -> ResolutionResult:
            captured["query"] = query
            return ResolutionResult(
                query=query,
                matches=(match,),
                resolved=match,
                observed_at=match.source_observed_at,
            )

    monkeypatch.setattr(sys, "argv", ["resolver", "--symbol", "reliance", "--exchange", "nse"])
    main = cast(Callable[[], int], namespace["main"])
    main.__globals__["DhanInstrumentResolver"] = FakeResolver
    assert main() == 0
    assert captured["query"].symbol == "RELIANCE"
    assert captured["query"].exchange == "NSE"


def test_cli_exact_option_filters_reach_resolver(monkeypatch: pytest.MonkeyPatch) -> None:
    namespace = runpy.run_path("scripts/dhan_instrument_resolver_smoke.py")
    captured: dict[str, InstrumentQuery] = {}

    class FakeResolver:
        def resolve(self, query: InstrumentQuery) -> ResolutionResult:
            captured["query"] = query
            return ResolutionResult(
                query=query,
                matches=(),
                not_found=True,
                observed_at=datetime(2026, 9, 5, tzinfo=UTC),
            )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "resolver",
            "--symbol",
            "RELIANCE",
            "--segment",
            "NSE_FNO",
            "--instrument-type",
            "CALL_OPTION",
            "--expiry",
            "2026-09-24",
            "--strike",
            "3000",
            "--option-type",
            "CE",
        ],
    )
    main = cast(Callable[[], int], namespace["main"])
    main.__globals__["DhanInstrumentResolver"] = FakeResolver
    assert main() == 1
    query = captured["query"]
    assert query.instrument_type is InstrumentType.CALL_OPTION
    assert query.strike == 3000
    assert query.option_type is not None and query.option_type.value == "CE"


def test_cli_lists_fno_underlyings_without_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    namespace = runpy.run_path("scripts/dhan_instrument_resolver_smoke.py")
    match = _match()

    class FakeResolver:
        policy = ResolutionPolicy()

        def get_fno_underlyings(
            self, *, exchange: str | None = None
        ) -> tuple[ResolvedInstrument, ...]:
            assert exchange == "NSE"
            return (match,)

    monkeypatch.setattr(sys, "argv", ["resolver", "--list-fno-underlyings"])
    main = cast(Callable[[], int], namespace["main"])
    main.__globals__["DhanInstrumentResolver"] = FakeResolver
    assert main() == 0


def test_cli_refresh_is_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    namespace = runpy.run_path("scripts/dhan_instrument_resolver_smoke.py")
    state = SimpleNamespace(refreshed=False)

    class FakeResolver:
        policy = ResolutionPolicy()

        def refresh(self) -> None:
            state.refreshed = True

        def get_fno_underlyings(
            self, *, exchange: str | None = None
        ) -> tuple[ResolvedInstrument, ...]:
            assert exchange == "NSE"
            return ()

    monkeypatch.setattr(
        sys,
        "argv",
        ["resolver", "--list-fno-underlyings", "--refresh"],
    )
    main = cast(Callable[[], int], namespace["main"])
    main.__globals__["DhanInstrumentResolver"] = FakeResolver
    assert main() == 0
    assert state.refreshed is True


def test_cli_reports_policy_selected_resolution(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    namespace = runpy.run_path("scripts/dhan_instrument_resolver_smoke.py")
    base = _match()
    selected = base.model_copy(update={"resolution_kind": ResolutionKind.POLICY_SELECTED})

    class FakeResolver:
        def resolve(self, query: InstrumentQuery) -> ResolutionResult:
            return ResolutionResult(
                query=query,
                matches=(selected,),
                resolved=selected,
                observed_at=selected.source_observed_at,
                metadata={"policy_applied": True, "preferred_exchange": "NSE"},
            )

    monkeypatch.setattr(sys, "argv", ["resolver", "--symbol", "RELIANCE"])
    main = cast(Callable[[], int], namespace["main"])
    main.__globals__["DhanInstrumentResolver"] = FakeResolver
    assert main() == 0
    output = capsys.readouterr().out
    assert "Resolution: POLICY_SELECTED" in output
    assert "Primary exchange: NSE" in output
