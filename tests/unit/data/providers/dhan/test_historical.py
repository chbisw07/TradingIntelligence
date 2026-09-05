"""Mocked Dhan daily and intraday historical adapter tests."""

from collections.abc import Mapping
from datetime import UTC, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import pytest

from tiaf.data import HistoricalSeries, ProviderBadResponseError, UnsupportedCapabilityError
from tiaf.data.providers.dhan import DhanInstrumentType, DhanMarketDataProvider

from ._support import FIXED_NOW, RecordingTransport, call_option, dhan_config, equity

KOLKATA = ZoneInfo("Asia/Kolkata")
START = datetime(2026, 9, 1, 3, 45, tzinfo=UTC)
END = datetime(2026, 9, 2, 3, 45, tzinfo=UTC)
FIRST_BAR = datetime(2026, 9, 1, 9, 15, tzinfo=KOLKATA)
SECOND_BAR = datetime(2026, 9, 1, 9, 16, tzinfo=KOLKATA)


def historical_response(
    timestamps: list[int] | None = None,
    *,
    include_oi: bool = True,
) -> dict[str, Any]:
    values = timestamps or [int(FIRST_BAR.timestamp()), int(SECOND_BAR.timestamp())]
    payload: dict[str, Any] = {
        "timestamp": values,
        "open": [100, 103],
        "high": [105, 106],
        "low": [98, 102],
        "close": [103, 105],
        "volume": [1000, 1200],
    }
    if include_oi:
        payload["open_interest"] = [500, 550]
    return payload


def provider_with(
    transport: RecordingTransport,
    *,
    historical_instrument_types: Mapping[str, DhanInstrumentType] | None = None,
) -> DhanMarketDataProvider:
    return DhanMarketDataProvider(
        dhan_config(),
        transport=transport,
        clock=lambda: FIXED_NOW,
        historical_instrument_types=historical_instrument_types,
    )


def test_daily_historical_normalization_uses_calendar_day_boundaries() -> None:
    response = historical_response()
    for field in ("timestamp", "open", "high", "low", "close", "volume", "open_interest"):
        response[field] = response[field][:1]
    transport = RecordingTransport(lambda path, payload: response)

    series = provider_with(transport).get_historical(equity(), "1d", START, END)

    assert transport.calls[0] == (
        "/charts/historical",
        {
            "securityId": "1333",
            "exchangeSegment": "NSE_EQ",
            "instrument": "EQUITY",
            "oi": False,
            "fromDate": "2026-09-01",
            "toDate": "2026-09-02",
        },
    )
    assert series.bars[0].start_at.timetz() == time(0, tzinfo=KOLKATA)
    assert series.bars[0].end_at - series.bars[0].start_at == timedelta(days=1)


@pytest.mark.parametrize(
    ("requested_interval", "dhan_interval", "normalized_interval", "minutes"),
    [
        ("1m", "1", "1m", 1),
        ("5m", "5", "5m", 5),
        ("15m", "15", "15m", 15),
        ("25m", "25", "25m", 25),
        ("60m", "60", "1h", 60),
        ("1h", "60", "1h", 60),
    ],
)
def test_supported_intraday_interval_mapping(
    requested_interval: str,
    dhan_interval: str,
    normalized_interval: str,
    minutes: int,
) -> None:
    transport = RecordingTransport(lambda path, payload: historical_response())

    series = provider_with(transport).get_historical(
        equity(), requested_interval, START, END
    )

    path, body = transport.calls[0]
    assert path == "/charts/intraday"
    assert body["interval"] == dhan_interval
    assert series.interval == normalized_interval
    assert series.bars[0].end_at - series.bars[0].start_at == timedelta(minutes=minutes)


def test_historical_bars_are_sorted_and_normalized_to_asia_kolkata() -> None:
    reversed_timestamps = [int(SECOND_BAR.timestamp()), int(FIRST_BAR.timestamp())]
    transport = RecordingTransport(
        lambda path, payload: historical_response(reversed_timestamps)
    )

    series = provider_with(transport).get_historical(equity(), "1m", START, END)

    assert tuple(bar.start_at for bar in series.bars) == (FIRST_BAR, SECOND_BAR)
    assert all(bar.start_at.tzinfo == KOLKATA for bar in series.bars)


def test_duplicate_historical_timestamp_is_rejected() -> None:
    duplicate = int(FIRST_BAR.timestamp())
    transport = RecordingTransport(
        lambda path, payload: historical_response([duplicate, duplicate])
    )

    with pytest.raises(ProviderBadResponseError, match="series failed"):
        provider_with(transport).get_historical(equity(), "1m", START, END)


def test_unequal_historical_arrays_are_rejected_without_truncation() -> None:
    response = historical_response()
    response["close"] = [103]
    transport = RecordingTransport(lambda path, payload: response)

    with pytest.raises(ProviderBadResponseError, match="unequal lengths"):
        provider_with(transport).get_historical(equity(), "1m", START, END)


def test_historical_open_interest_is_optional_and_preserved() -> None:
    with_oi = RecordingTransport(lambda path, payload: historical_response())
    without_oi = RecordingTransport(
        lambda path, payload: historical_response(include_oi=False)
    )

    oi_series = provider_with(with_oi).get_historical(equity(), "1m", START, END)
    no_oi_series = provider_with(without_oi).get_historical(equity(), "1m", START, END)

    assert tuple(bar.open_interest for bar in oi_series.bars) == (500, 550)
    assert all(bar.open_interest is None for bar in no_oi_series.bars)


def test_derivative_history_uses_explicit_dhan_instrument_mapping() -> None:
    transport = RecordingTransport(lambda path, payload: historical_response())
    provider = provider_with(
        transport,
        historical_instrument_types={"49081": DhanInstrumentType.OPTSTK},
    )

    provider.get_historical(call_option(), "1m", START, END)

    assert transport.calls[0][1]["instrument"] == "OPTSTK"
    assert transport.calls[0][1]["oi"] is True


def test_derivative_history_without_explicit_subtype_is_rejected() -> None:
    transport = RecordingTransport(lambda path, payload: historical_response())

    with pytest.raises(UnsupportedCapabilityError, match="explicit Dhan derivative"):
        provider_with(transport).get_historical(call_option(), "1m", START, END)


def test_unsupported_interval_is_typed() -> None:
    transport = RecordingTransport(lambda path, payload: historical_response())

    with pytest.raises(UnsupportedCapabilityError, match="30m"):
        provider_with(transport).get_historical(equity(), "30m", START, END)


def test_intraday_range_over_90_days_is_not_silently_changed() -> None:
    transport = RecordingTransport(lambda path, payload: historical_response())

    with pytest.raises(UnsupportedCapabilityError, match="over 90 days"):
        provider_with(transport).get_historical(
            equity(),
            "1m",
            START,
            START + timedelta(days=91),
        )

    assert transport.calls == []


def test_historical_requires_ordered_aware_range() -> None:
    transport = RecordingTransport(lambda path, payload: historical_response())
    provider = provider_with(transport)

    with pytest.raises(ValueError, match="later than"):
        provider.get_historical(equity(), "1m", START, START)
    with pytest.raises(ValueError, match="timezone-aware"):
        provider.get_historical(equity(), "1m", datetime(2026, 9, 1), END)


def test_historical_series_serializes_and_round_trips() -> None:
    transport = RecordingTransport(lambda path, payload: historical_response())
    series = provider_with(transport).get_historical(equity(), "5m", START, END)

    restored = HistoricalSeries.model_validate_json(series.model_dump_json())

    assert restored == series
    assert isinstance(series.model_dump(mode="json")["bars"], list)
    assert series.model_dump(mode="json")["bars"][0]["start_at"].endswith("+05:30")
