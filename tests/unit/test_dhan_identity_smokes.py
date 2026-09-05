"""Smoke-script identity validation must happen before provider transport."""

import runpy
import sys
from collections.abc import Callable
from datetime import date
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tiaf.data import InstrumentKey, InstrumentType, MarketSegment
from tiaf.data.providers.dhan import DhanIdentityMismatchError


def _reliance() -> InstrumentKey:
    return InstrumentKey(
        symbol="RELIANCE",
        exchange="NSE",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
        trading_symbol="RELIANCE",
        provider_instrument_id="2885",
    )


@pytest.mark.parametrize(
    "script,argv",
    [
        (
            "scripts/dhan_market_data_smoke.py",
            ["smoke", "--symbol", "RELIANCE", "--security-id", "1333"],
        ),
        (
            "scripts/dhan_option_chain_smoke.py",
            ["smoke", "--symbol", "RELIANCE", "--security-id", "1333"],
        ),
    ],
)
def test_identity_mismatch_stops_before_provider_construction(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    script: str,
    argv: list[str],
) -> None:
    namespace = runpy.run_path(script)
    provider_constructed = False

    def reject_identity(**kwargs: Any) -> InstrumentKey:
        raise DhanIdentityMismatchError(
            "Identity mismatch: RELIANCE resolves to 2885, supplied 1333. "
            "No provider request was made.",
            provider="DHAN",
        )

    class ForbiddenProvider:
        def __init__(self) -> None:
            nonlocal provider_constructed
            provider_constructed = True

    monkeypatch.setattr(sys, "argv", argv)
    main = cast(Callable[[], int], namespace["main"])
    main.__globals__["resolve_dhan_diagnostic_instrument"] = reject_identity
    main.__globals__["DhanMarketDataProvider"] = ForbiddenProvider
    assert main() == 2
    assert provider_constructed is False
    output = capsys.readouterr().out
    assert "No provider request was made" in output
    assert "access-token" not in output.casefold()


def test_market_smoke_symbol_only_resolves_before_quote(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    namespace = runpy.run_path("scripts/dhan_market_data_smoke.py")
    captured: dict[str, Any] = {}
    instrument = _reliance()

    def resolve_identity(**kwargs: Any) -> InstrumentKey:
        captured.update(kwargs)
        return instrument

    class FakeProvider:
        def get_quote(self, requested: InstrumentKey) -> SimpleNamespace:
            captured["requested"] = requested
            return SimpleNamespace(model_dump_json=lambda indent: "{}")

    monkeypatch.setattr(sys, "argv", ["smoke", "--symbol", "RELIANCE"])
    main = cast(Callable[[], int], namespace["main"])
    main.__globals__["resolve_dhan_diagnostic_instrument"] = resolve_identity
    main.__globals__["DhanMarketDataProvider"] = FakeProvider
    assert main() == 0
    assert captured["security_id"] is None
    assert captured["requested"] == instrument


def test_option_chain_smoke_symbol_only_resolves_underlying_before_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    namespace = runpy.run_path("scripts/dhan_option_chain_smoke.py")
    captured: dict[str, Any] = {}
    instrument = _reliance()

    def resolve_identity(**kwargs: Any) -> InstrumentKey:
        captured.update(kwargs)
        return instrument

    class FakeProvider:
        def get_option_expiries(self, requested: InstrumentKey) -> SimpleNamespace:
            captured["requested"] = requested
            return SimpleNamespace(expiries=(date(2026, 9, 24),))

    monkeypatch.setattr(sys, "argv", ["smoke", "--symbol", "RELIANCE"])
    main = cast(Callable[[], int], namespace["main"])
    main.__globals__["resolve_dhan_diagnostic_instrument"] = resolve_identity
    main.__globals__["DhanMarketDataProvider"] = FakeProvider
    assert main() == 0
    assert captured["security_id"] is None
    assert captured["requested"] == instrument
