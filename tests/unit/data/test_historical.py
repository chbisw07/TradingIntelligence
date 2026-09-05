"""Tests for normalized OHLCV bars and historical series."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from tiaf.contracts import DataQuality, FreshnessState
from tiaf.data import HistoricalSeries, InstrumentKey, InstrumentType, MarketSegment, OHLCVBar

BASE_TIME = datetime(2026, 9, 5, 4, 30, tzinfo=UTC)


def equity(symbol: str = "RELIANCE") -> InstrumentKey:
    return InstrumentKey(
        symbol=symbol,
        exchange="NSE",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
    )


def bar(
    *,
    minute: int = 0,
    instrument: InstrumentKey | None = None,
    interval: str = "1m",
    **changes: object,
) -> OHLCVBar:
    start = BASE_TIME + timedelta(minutes=minute)
    values: dict[str, object] = {
        "instrument": instrument or equity(),
        "interval": interval,
        "start_at": start,
        "end_at": start + timedelta(minutes=1),
        "open": 100,
        "high": 105,
        "low": 98,
        "close": 103,
        "volume": 1000,
        "source_provider": "provider-a",
    }
    values.update(changes)
    return OHLCVBar.model_validate(values)


def series(bars: object, **changes: object) -> HistoricalSeries:
    values: dict[str, object] = {
        "instrument": equity(),
        "interval": "1m",
        "bars": bars,
        "source_provider": "provider-a",
        "observed_at": BASE_TIME + timedelta(minutes=10),
        "freshness": FreshnessState.FRESH,
        "quality": DataQuality.GOOD,
    }
    values.update(changes)
    return HistoricalSeries.model_validate(values)


@pytest.mark.parametrize(
    "changes",
    [
        {"high": 102},
        {"low": 101},
        {"open": -1},
    ],
)
def test_bar_rejects_invalid_price_envelope(changes: dict[str, object]) -> None:
    values = bar().model_dump()
    values.update(changes)
    with pytest.raises(ValidationError):
        OHLCVBar.model_validate(values)


def test_bar_rejects_invalid_time_ordering() -> None:
    with pytest.raises(ValidationError, match="end_at must be later"):
        bar(end_at=BASE_TIME)


def test_bar_normalizes_common_interval_alias() -> None:
    assert bar(interval="1min").interval == "1m"


def test_series_accepts_list_and_stores_ordered_tuple() -> None:
    historical = series([bar(minute=0), bar(minute=1)])

    assert isinstance(historical.bars, tuple)
    assert not hasattr(historical.bars, "append")
    assert [item.start_at for item in historical.bars] == sorted(
        item.start_at for item in historical.bars
    )


def test_series_rejects_descending_bars() -> None:
    with pytest.raises(ValidationError, match="ordered ascending"):
        series([bar(minute=1), bar(minute=0)])


def test_series_rejects_duplicate_start_times() -> None:
    with pytest.raises(ValidationError, match="duplicate"):
        series([bar(minute=0), bar(minute=0)])


def test_series_rejects_instrument_mismatch() -> None:
    with pytest.raises(ValidationError, match="series instrument"):
        series([bar(instrument=equity("TCS"))])


def test_series_rejects_interval_mismatch() -> None:
    with pytest.raises(ValidationError, match="series interval"):
        series([bar(interval="5m")])


@pytest.mark.parametrize("quality", [DataQuality.UNAVAILABLE, DataQuality.PARTIAL])
def test_empty_series_is_allowed_for_unavailable_or_partial_quality(
    quality: DataQuality,
) -> None:
    assert series([], quality=quality).bars == ()


def test_empty_good_series_is_rejected() -> None:
    with pytest.raises(ValidationError, match="empty bars"):
        series([])


def test_series_rejects_reversed_requested_window() -> None:
    with pytest.raises(ValidationError, match="requested_to"):
        series(
            [bar()],
            requested_from=BASE_TIME + timedelta(hours=1),
            requested_to=BASE_TIME,
        )


def test_series_json_round_trip_uses_arrays() -> None:
    historical = series([bar(minute=0), bar(minute=1)])
    dumped = historical.model_dump(mode="json")
    restored = HistoricalSeries.model_validate(dumped)

    assert isinstance(dumped["bars"], list)
    assert isinstance(restored.bars, tuple)
    assert restored == historical
