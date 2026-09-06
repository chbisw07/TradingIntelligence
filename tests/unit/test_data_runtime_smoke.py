"""Read-only A1.6 data-runtime smoke behavior without network access."""

import runpy
import sys
from collections.abc import Callable
from datetime import datetime
from types import SimpleNamespace
from typing import cast

import pytest

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data import InstrumentKey, InstrumentType, MarketSegment


def test_data_runtime_smoke_fetches_once_then_uses_cache(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    namespace = runpy.run_path("scripts/data_runtime_smoke.py")
    instrument = InstrumentKey(
        symbol="RELIANCE",
        exchange="NSE",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
        provider_instrument_id="2885",
    )
    provider_calls = 0

    class FakeResolver:
        def resolve(self, query: object) -> SimpleNamespace:
            return SimpleNamespace(
                resolved=SimpleNamespace(instrument=instrument),
                ambiguous=False,
            )

    class FakeProvider:
        def get_quote(self, requested: InstrumentKey) -> SimpleNamespace:
            nonlocal provider_calls
            provider_calls += 1
            assert requested == instrument
            return SimpleNamespace(
                observed_at=datetime.now(TIAF_TIMEZONE),
                received_at=datetime.now(TIAF_TIMEZONE),
                source_provider="dhan",
            )

    monkeypatch.setattr(sys, "argv", ["data-runtime-smoke"])
    main = cast(Callable[[], int], namespace["main"])
    main.__globals__["DhanInstrumentResolver"] = FakeResolver
    main.__globals__["DhanMarketDataProvider"] = FakeProvider
    assert main() == 0
    assert provider_calls == 1
    output = capsys.readouterr().out
    assert "first request: PROVIDER" in output
    assert "second request: CACHE" in output
