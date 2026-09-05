"""Tests for normalized quote snapshots."""

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from tiaf.contracts import DataQuality, FreshnessState
from tiaf.data import (
    InstrumentKey,
    InstrumentType,
    MarketSegment,
    QuoteFieldAvailability,
    QuoteSnapshot,
)

OBSERVED = datetime(2026, 9, 5, 4, 30, tzinfo=UTC)
KOLKATA = ZoneInfo("Asia/Kolkata")


def equity(symbol: str = "RELIANCE") -> InstrumentKey:
    return InstrumentKey(
        symbol=symbol,
        exchange="NSE",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
    )


def quote(**changes: object) -> QuoteSnapshot:
    values: dict[str, object] = {
        "instrument": equity(),
        "ltp": 3010.5,
        "open": 2990,
        "high": 3020,
        "low": 2980,
        "previous_close": 2985,
        "volume": 1000,
        "bid": 3010,
        "ask": 3011,
        "open_interest": 500,
        "observed_at": OBSERVED,
        "received_at": OBSERVED + timedelta(seconds=1),
        "source_provider": " Provider A ",
        "freshness": FreshnessState.FRESH,
        "quality": DataQuality.GOOD,
        "availability": QuoteFieldAvailability.AVAILABLE,
    }
    values.update(changes)
    return QuoteSnapshot.model_validate(values)


def test_quote_normalizes_timestamps_and_provider() -> None:
    snapshot = quote()

    assert snapshot.observed_at == OBSERVED.astimezone(KOLKATA)
    assert snapshot.observed_at.tzinfo == KOLKATA
    assert snapshot.source_provider == "provider a"


@pytest.mark.parametrize("field", ["ltp", "open", "high", "low", "bid", "ask"])
def test_quote_rejects_negative_prices(field: str) -> None:
    with pytest.raises(ValidationError):
        quote(**{field: -0.01})


def test_quote_rejects_inverted_bid_ask() -> None:
    with pytest.raises(ValidationError, match="ask must be greater"):
        quote(bid=3012, ask=3011)


def test_quote_rejects_absurd_observation_clock_skew() -> None:
    with pytest.raises(ValidationError, match="implausibly later"):
        quote(
            observed_at=OBSERVED + timedelta(days=2),
            received_at=OBSERVED,
        )


def test_quote_json_round_trip_emits_ist_offset() -> None:
    snapshot = quote()
    dumped = snapshot.model_dump(mode="json")
    restored = QuoteSnapshot.model_validate(dumped)

    assert restored == snapshot
    assert dumped["observed_at"] == "2026-09-05T10:00:00+05:30"
