"""Mocked Dhan rolling historical/expired-options adapter tests."""

from collections.abc import Mapping
from datetime import date, datetime, time
from typing import Any

import pytest

from tiaf.contracts import DataQuality, OptionType
from tiaf.data import (
    ExpiryFlag,
    HistoricalOptionExpiryCode,
    HistoricalOptionsDataProvider,
    InstrumentNotFoundError,
    MarketSegment,
    ProviderBadResponseError,
    ProviderCapability,
    RelativeStrike,
    UnsupportedCapabilityError,
)
from tiaf.data.normalization import TIAF_TIMEZONE
from tiaf.data.providers.dhan import DhanMarketDataProvider, plan_rolling_option_chunks

from ._support import (
    FIXED_NOW,
    RecordingTransport,
    dhan_config,
    equity,
    index,
    rolling_option_response,
    rolling_option_side,
)

START = date(2026, 8, 1)
END = date(2026, 8, 15)


def provider_with(transport: RecordingTransport) -> DhanMarketDataProvider:
    return DhanMarketDataProvider(
        dhan_config(),
        transport=transport,
        clock=lambda: FIXED_NOW,
    )


def fetch(
    provider: DhanMarketDataProvider,
    *,
    underlying: Any = None,
    interval: str = "15m",
    flag: ExpiryFlag = ExpiryFlag.MONTH,
    code: HistoricalOptionExpiryCode | int = HistoricalOptionExpiryCode.NEXT,
    strike: str = "ATM",
    option_type: OptionType = OptionType.CE,
    start: date = START,
    end: date = END,
) -> Any:
    return provider.get_historical_options(
        underlying or equity(),
        interval,
        flag,
        code,
        RelativeStrike.model_validate(strike),
        option_type,
        start,
        end,
    )


def epoch(day: date, hour: int = 9, minute: int = 15) -> int:
    return int(datetime.combine(day, time(hour, minute), tzinfo=TIAF_TIMEZONE).timestamp())


def test_protocol_and_capability_are_advertised() -> None:
    provider = provider_with(RecordingTransport(lambda path, body: rolling_option_response()))
    assert isinstance(provider, HistoricalOptionsDataProvider)
    assert ProviderCapability.HISTORICAL_OPTIONS in provider.capabilities()


@pytest.mark.parametrize(
    ("underlying", "segment", "instrument"),
    [
        (equity(), "NSE_FNO", "OPTSTK"),
        (equity(segment=MarketSegment.NSE_FNO), "NSE_FNO", "OPTSTK"),
        (index(), "NSE_FNO", "OPTIDX"),
        (equity(segment=MarketSegment.BSE_EQUITY), "BSE_FNO", "OPTSTK"),
    ],
)
def test_request_body_maps_underlying_and_all_factual_fields(
    underlying: Any,
    segment: str,
    instrument: str,
) -> None:
    transport = RecordingTransport(lambda path, body: rolling_option_response())
    result = fetch(provider_with(transport), underlying=underlying)
    assert result.underlying == underlying
    assert transport.calls == [
        (
            "/charts/rollingoption",
            {
                "exchangeSegment": segment,
                "interval": "15",
                "securityId": underlying.provider_instrument_id,
                "instrument": instrument,
                "expiryFlag": "MONTH",
                "expiryCode": 2,
                "strike": "ATM",
                "drvOptionType": "CALL",
                "requiredData": [
                    "open",
                    "high",
                    "low",
                    "close",
                    "iv",
                    "volume",
                    "strike",
                    "oi",
                    "spot",
                ],
                "fromDate": "2026-08-01",
                "toDate": "2026-08-15",
            },
        )
    ]


@pytest.mark.parametrize(
    ("interval", "wire"),
    [("1m", "1"), ("5m", "5"), ("15m", "15"), ("25m", "25"), ("1h", "60")],
)
def test_supported_interval_mappings(interval: str, wire: str) -> None:
    transport = RecordingTransport(lambda path, body: rolling_option_response())
    fetch(provider_with(transport), interval=interval)
    assert transport.calls[0][1]["interval"] == wire


@pytest.mark.parametrize(
    ("option_type", "response_side", "wire"),
    [(OptionType.CE, "ce", "CALL"), (OptionType.PE, "pe", "PUT")],
)
def test_call_put_mapping_and_requested_side_parsing(
    option_type: OptionType,
    response_side: str,
    wire: str,
) -> None:
    transport = RecordingTransport(
        lambda path, body: rolling_option_response(side=response_side)
    )
    result = fetch(provider_with(transport), option_type=option_type)
    assert transport.calls[0][1]["drvOptionType"] == wire
    assert all(bar.option_type is option_type for bar in result.bars)


def test_ohlc_iv_oi_volume_actual_strike_and_spot_are_preserved() -> None:
    provider = provider_with(RecordingTransport(lambda path, body: rolling_option_response()))
    result = fetch(provider)
    bar = result.bars[0]
    assert (bar.open, bar.high, bar.low, bar.close) == (100.0, 105.0, 98.0, 103.0)
    assert bar.implied_volatility == 18.5
    assert bar.volume == 1000
    assert bar.open_interest == 5000
    assert bar.actual_strike == 3000.0
    assert bar.spot == 3005.0
    assert bar.start_at.isoformat().endswith("+05:30")
    assert result.quality is DataQuality.GOOD


def test_missing_values_degrade_quality_without_fabrication() -> None:
    values = rolling_option_side()
    values["iv"][0] = None
    provider = provider_with(
        RecordingTransport(lambda path, body: rolling_option_response(values=values))
    )
    result = fetch(provider)
    assert result.bars[0].implied_volatility is None
    assert result.bars[0].quality is DataQuality.PARTIAL
    assert result.quality is DataQuality.PARTIAL


def test_null_requested_side_returns_explicit_unavailable_series() -> None:
    provider = provider_with(
        RecordingTransport(lambda path, body: {"data": {"ce": None, "pe": None}})
    )
    result = fetch(provider)
    assert result.bars == ()
    assert result.quality is DataQuality.UNAVAILABLE


@pytest.mark.parametrize("failure", ["unequal", "timestamp", "missing", "shape"])
def test_malformed_parallel_response_is_rejected(failure: str) -> None:
    values = rolling_option_side()
    if failure == "unequal":
        values["close"].pop()
        response: dict[str, Any] = rolling_option_response(values=values)
    elif failure == "timestamp":
        values["timestamp"][0] = "invalid"
        response = rolling_option_response(values=values)
    elif failure == "missing":
        del values["spot"]
        response = rolling_option_response(values=values)
    else:
        response = {"data": []}
    provider = provider_with(RecordingTransport(lambda path, body: response))
    with pytest.raises(ProviderBadResponseError):
        fetch(provider)


def test_response_bars_are_sorted_and_json_round_trip() -> None:
    values = rolling_option_side([epoch(START, 9, 30), epoch(START, 9, 15)])
    provider = provider_with(
        RecordingTransport(lambda path, body: rolling_option_response(values=values))
    )
    result = fetch(provider)
    assert result.bars[0].start_at < result.bars[1].start_at
    dumped = result.model_dump(mode="json")
    assert isinstance(dumped["bars"], list)
    assert type(result).model_validate(dumped) == result


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        (date(2026, 7, 1), date(2026, 7, 31), ((date(2026, 7, 1), date(2026, 7, 31)),)),
        (
            date(2026, 7, 1),
            date(2026, 8, 1),
            ((date(2026, 7, 1), date(2026, 7, 31)), (date(2026, 7, 31), date(2026, 8, 1))),
        ),
        (
            date(2026, 6, 1),
            date(2026, 7, 31),
            ((date(2026, 6, 1), date(2026, 7, 1)), (date(2026, 7, 1), date(2026, 7, 31))),
        ),
    ],
)
def test_chunk_planner_exact_boundaries(
    start: date,
    end: date,
    expected: tuple[tuple[date, date], ...],
) -> None:
    assert plan_rolling_option_chunks(start, end) == expected


def test_multi_year_chunk_plan_is_adjacent_complete_and_bounded() -> None:
    start = date(2021, 1, 1)
    end = date(2026, 1, 1)
    chunks = plan_rolling_option_chunks(start, end)
    assert chunks[0][0] == start
    assert chunks[-1][1] == end
    assert all(
        left[1] == right[0]
        for left, right in zip(chunks[:-1], chunks[1:], strict=True)
    )
    assert all((chunk_end - chunk_start).days <= 30 for chunk_start, chunk_end in chunks)


def test_multichunk_requests_use_noninclusive_adjacent_boundaries_without_gaps() -> None:
    def handler(path: str, body: Mapping[str, Any]) -> dict[str, Any]:
        chunk_start = date.fromisoformat(str(body["fromDate"]))
        return rolling_option_response(values=rolling_option_side([epoch(chunk_start)]))

    transport = RecordingTransport(handler)
    result = fetch(
        provider_with(transport),
        start=date(2026, 7, 1),
        end=date(2026, 8, 1),
    )
    assert [(call[1]["fromDate"], call[1]["toDate"]) for call in transport.calls] == [
        ("2026-07-01", "2026-07-31"),
        ("2026-07-31", "2026-08-01"),
    ]
    assert [bar.start_at.date() for bar in result.bars] == [date(2026, 7, 1), date(2026, 7, 31)]


def test_identical_boundary_candles_are_deduplicated() -> None:
    shared = rolling_option_response(values=rolling_option_side([epoch(date(2026, 7, 15))]))
    provider = provider_with(RecordingTransport(lambda path, body: shared))
    result = fetch(provider, start=date(2026, 7, 1), end=date(2026, 8, 1))
    assert len(result.bars) == 1
    assert result.metadata["deduplicated_boundary_bars"] == 1


def test_conflicting_duplicate_candles_are_rejected() -> None:
    call_count = 0

    def handler(path: str, body: Mapping[str, Any]) -> dict[str, Any]:
        nonlocal call_count
        values = rolling_option_side([epoch(date(2026, 7, 15))])
        values["close"][0] += call_count
        call_count += 1
        return rolling_option_response(values=values)

    provider = provider_with(RecordingTransport(handler))
    with pytest.raises(ProviderBadResponseError, match="conflicting duplicate"):
        fetch(provider, start=date(2026, 7, 1), end=date(2026, 8, 1))


def test_weekly_expiry_flag_and_far_code_are_preserved_in_request() -> None:
    transport = RecordingTransport(lambda path, body: rolling_option_response())
    result = fetch(
        provider_with(transport),
        flag=ExpiryFlag.WEEK,
        code=HistoricalOptionExpiryCode.FAR,
    )
    assert transport.calls[0][1]["expiryFlag"] == "WEEK"
    assert transport.calls[0][1]["expiryCode"] == 3
    assert result.expiry_flag is ExpiryFlag.WEEK
    assert result.expiry_code is HistoricalOptionExpiryCode.FAR


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (HistoricalOptionExpiryCode.NEAR, 1),
        (HistoricalOptionExpiryCode.NEXT, 2),
        (HistoricalOptionExpiryCode.FAR, 3),
    ],
)
def test_every_expiry_code_is_required_and_serialized_as_an_integer(
    code: HistoricalOptionExpiryCode,
    expected: int,
) -> None:
    transport = RecordingTransport(
        lambda path, body: {"data": {"ce": None, "pe": None}}
    )
    fetch(provider_with(transport), code=code)
    request = transport.calls[0][1]
    assert "expiryCode" in request
    assert request["expiryCode"] == expected
    assert type(request["expiryCode"]) is int


def test_none_expiry_code_is_rejected_before_transport() -> None:
    transport = RecordingTransport(lambda path, body: rolling_option_response())
    provider = provider_with(transport)
    with pytest.raises(ValueError, match="expiry_code is required"):
        provider.get_historical_options(
            underlying=equity(),
            interval="15m",
            expiry_flag=ExpiryFlag.MONTH,
            expiry_code=None,  # type: ignore[arg-type]
            relative_strike=RelativeStrike.model_validate("ATM"),
            option_type=OptionType.CE,
            start_date=START,
            end_date=END,
        )
    assert transport.calls == []


def test_zero_expiry_code_is_rejected_before_transport() -> None:
    transport = RecordingTransport(lambda path, body: rolling_option_response())
    provider = provider_with(transport)
    with pytest.raises(ValueError, match="invalid historical-option request value"):
        fetch(provider, code=0)
    assert transport.calls == []


def test_zero_factual_values_and_atm_zero_offset_are_preserved() -> None:
    values = rolling_option_side()
    for field in ("open", "high", "low", "close", "iv", "volume", "oi", "spot"):
        values[field] = [0 for _ in values[field]]
    provider = provider_with(
        RecordingTransport(lambda path, body: rolling_option_response(values=values))
    )
    result = fetch(provider, strike="ATM", code=1)
    first = result.bars[0]
    assert result.relative_strike.offset == 0
    assert (
        first.open,
        first.high,
        first.low,
        first.close,
        first.implied_volatility,
        first.volume,
        first.open_interest,
        first.spot,
    ) == (0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0)


def test_invalid_inputs_fail_without_network() -> None:
    transport = RecordingTransport(lambda path, body: rolling_option_response())
    provider = provider_with(transport)
    with pytest.raises(InstrumentNotFoundError):
        fetch(provider, underlying=equity(security_id="invalid"))
    with pytest.raises(UnsupportedCapabilityError):
        fetch(provider, interval="1d")
    with pytest.raises(UnsupportedCapabilityError):
        fetch(provider, strike="ATM+4")
    with pytest.raises(ValueError, match="future-only"):
        fetch(provider, start=date(2026, 9, 5), end=date(2026, 9, 6))
    assert transport.calls == []


def test_index_strike_limit_accepts_ten_and_rejects_eleven() -> None:
    transport = RecordingTransport(lambda path, body: rolling_option_response())
    provider = provider_with(transport)
    fetch(provider, underlying=index(), strike="ATM-10")
    with pytest.raises(UnsupportedCapabilityError):
        fetch(provider, underlying=index(), strike="ATM+11")
