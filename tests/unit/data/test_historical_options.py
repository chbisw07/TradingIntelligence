"""Provider-neutral rolling historical-option model tests."""

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from tiaf.contracts import DataQuality, OptionType
from tiaf.data import (
    ExpiryFlag,
    HistoricalOptionBar,
    HistoricalOptionExpiryCode,
    HistoricalOptionSeries,
    InstrumentKey,
    InstrumentType,
    MarketSegment,
    RelativeStrike,
)

NOW = datetime(2026, 8, 1, 3, 45, tzinfo=UTC)


def underlying() -> InstrumentKey:
    return InstrumentKey(
        symbol="RELIANCE",
        exchange="NSE",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
        provider_instrument_id="1333",
    )


@pytest.mark.parametrize(
    ("value", "normalized", "offset"),
    [
        ("ATM", "ATM", 0),
        (" atm+3 ", "ATM+3", 3),
        ("atm-10", "ATM-10", -10),
        ("ATM+27", "ATM+27", 27),
    ],
)
def test_relative_strike_valid_values(value: str, normalized: str, offset: int) -> None:
    strike = RelativeStrike.model_validate(value)
    assert str(strike) == normalized
    assert strike.offset == offset
    assert strike.model_dump(mode="json") == normalized


@pytest.mark.parametrize("value", ["", "ATM++", "ATM+X", "+1", "12345", "ATM+0", "ATM-0"])
def test_relative_strike_rejects_malformed_values(value: str) -> None:
    with pytest.raises(ValidationError):
        RelativeStrike.model_validate(value)


def test_expiry_flag_and_code_serialize_to_wire_values() -> None:
    assert ExpiryFlag.MONTH.value == "MONTH"
    assert ExpiryFlag.WEEK.value == "WEEK"
    assert int(HistoricalOptionExpiryCode.NEAR) == 1
    assert int(HistoricalOptionExpiryCode.NEXT) == 2
    assert int(HistoricalOptionExpiryCode.FAR) == 3


def bar(**changes: object) -> HistoricalOptionBar:
    values: dict[str, object] = {
        "underlying": underlying(),
        "option_type": OptionType.CE,
        "expiry_flag": ExpiryFlag.MONTH,
        "expiry_code": HistoricalOptionExpiryCode.NEXT,
        "relative_strike": "ATM",
        "start_at": NOW,
        "open": 100,
        "high": 110,
        "low": 95,
        "close": 105,
        "implied_volatility": 18.5,
        "volume": 1000,
        "open_interest": 5000,
        "actual_strike": 3000,
        "spot": 3005,
        "source_provider": "DHAN",
        "quality": DataQuality.GOOD,
    }
    values.update(changes)
    return HistoricalOptionBar.model_validate(values)


def test_bar_validates_ohlc_and_nonnegative_values() -> None:
    assert bar().start_at.isoformat().endswith("+05:30")
    with pytest.raises(ValidationError, match="high"):
        bar(high=99)
    with pytest.raises(ValidationError, match="low"):
        bar(low=106)
    with pytest.raises(ValidationError):
        bar(implied_volatility=-1)
    with pytest.raises(ValidationError):
        bar(actual_strike=0)


def test_bar_allows_truthful_missing_fields() -> None:
    value = bar(open=None, high=None, low=None, close=101, quality=DataQuality.DEGRADED)
    assert value.open is None
    assert value.close == 101


def series_bars() -> tuple[HistoricalOptionBar, HistoricalOptionBar]:
    first = bar()
    second = bar(start_at=datetime(2026, 8, 1, 4, 0, tzinfo=UTC))
    return first, second


def series(**changes: object) -> HistoricalOptionSeries:
    values: dict[str, object] = {
        "underlying": underlying(),
        "option_type": OptionType.CE,
        "expiry_flag": ExpiryFlag.MONTH,
        "expiry_code": HistoricalOptionExpiryCode.NEXT,
        "relative_strike": "ATM",
        "interval": "15m",
        "bars": series_bars(),
        "requested_from": date(2026, 8, 1),
        "requested_to": date(2026, 8, 2),
        "observed_at": NOW,
        "source_provider": "DHAN",
        "quality": DataQuality.GOOD,
    }
    values.update(changes)
    return HistoricalOptionSeries.model_validate(values)


def test_series_requires_chronology_uniqueness_and_context() -> None:
    first, second = series_bars()
    with pytest.raises(ValidationError, match="ordered"):
        series(bars=(second, first))
    with pytest.raises(ValidationError, match="duplicate"):
        series(bars=(first, first))
    wrong_side = bar(option_type=OptionType.PE)
    with pytest.raises(ValidationError, match="option_type"):
        series(bars=(wrong_side,))
    wrong_provider = bar(source_provider="OTHER")
    with pytest.raises(ValidationError, match="source provider"):
        series(bars=(wrong_provider,))


def test_series_empty_policy_and_requested_range() -> None:
    with pytest.raises(ValidationError, match="empty bars"):
        series(bars=())
    assert series(bars=(), quality=DataQuality.UNAVAILABLE).bars == ()
    with pytest.raises(ValidationError, match="requested_to"):
        series(requested_to=date(2026, 8, 1))
    with pytest.raises(ValidationError, match="half-open"):
        series(
            requested_from=date(2026, 7, 31),
            requested_to=date(2026, 8, 1),
            quality=DataQuality.UNAVAILABLE,
        )


def test_series_tuple_immutability_json_arrays_and_round_trip() -> None:
    value = series(bars=list(series_bars()))
    assert isinstance(value.bars, tuple)
    dumped = value.model_dump(mode="json")
    assert isinstance(dumped["bars"], list)
    assert dumped["expiry_code"] == 2
    assert dumped["relative_strike"] == "ATM"
    assert HistoricalOptionSeries.model_validate(dumped) == value
    with pytest.raises(AttributeError):
        value.bars.append(bar())  # type: ignore[attr-defined]


def test_historical_option_models_reject_naive_timestamps_and_are_frozen() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        bar(start_at=datetime(2026, 8, 1, 9, 15))
    with pytest.raises(ValidationError):
        bar().close = 1
