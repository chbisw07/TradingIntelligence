"""Provider-neutral live derivatives contract tests."""

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from tiaf.contracts import DataQuality, FreshnessState, OptionType
from tiaf.data import (
    ExpiryListSnapshot,
    InstrumentKey,
    InstrumentType,
    MarketSegment,
    OptionChainSnapshot,
    OptionGreeks,
    OptionMarketSnapshot,
    OptionStrikeSnapshot,
)

NOW = datetime(2026, 9, 5, 4, 31, tzinfo=UTC)
EXPIRY = date(2026, 9, 24)


def underlying() -> InstrumentKey:
    return InstrumentKey(
        symbol="RELIANCE",
        exchange="NSE",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
        provider_instrument_id="1333",
    )


def side(option_type: OptionType = OptionType.CE, **changes: object) -> OptionMarketSnapshot:
    instrument_type = (
        InstrumentType.CALL_OPTION
        if option_type is OptionType.CE
        else InstrumentType.PUT_OPTION
    )
    values: dict[str, object] = {
        "instrument": InstrumentKey(
            symbol="RELIANCE",
            exchange="NSE",
            segment=MarketSegment.NSE_FNO,
            instrument_type=instrument_type,
            expiry=EXPIRY,
            strike=3000,
            option_type=option_type,
            provider_instrument_id="49081",
        ),
        "option_type": option_type,
        "strike": 3000,
        "expiry": EXPIRY,
        "security_id": "49081",
        "ltp": 146.9,
        "bid": 146.8,
        "ask": 147.2,
        "greeks": OptionGreeks(delta=0.5, gamma=0.01, theta=-2.0, vega=4.0),
        "observed_at": NOW,
        "source_provider": "DHAN",
        "freshness": FreshnessState.UNKNOWN,
        "quality": DataQuality.GOOD,
    }
    values.update(changes)
    return OptionMarketSnapshot.model_validate(values)


def test_option_greeks_serialize_and_round_trip() -> None:
    greeks = OptionGreeks(delta=0.51, gamma=0.012, theta=-4.2, vega=7.5)
    dumped = greeks.model_dump(mode="json")
    assert dumped == {
        "schema_version": "1.0",
        "delta": 0.51,
        "gamma": 0.012,
        "theta": -4.2,
        "vega": 7.5,
    }
    assert OptionGreeks.model_validate(dumped) == greeks


@pytest.mark.parametrize(
    "changes",
    [
        {"option_type": OptionType.PE},
        {"strike": 3100},
        {"expiry": date(2026, 10, 1)},
        {"security_id": "99999"},
        {"bid": 150, "ask": 149},
    ],
)
def test_option_market_snapshot_rejects_inconsistent_identity(
    changes: dict[str, object],
) -> None:
    values = side().model_dump()
    values.update(changes)
    with pytest.raises(ValidationError):
        OptionMarketSnapshot.model_validate(values)


def test_option_market_accepts_missing_fields_and_negative_theta() -> None:
    snapshot = side(
        ltp=None,
        bid=None,
        ask=None,
        greeks={"delta": None, "gamma": None, "theta": -12.0, "vega": None},
        quality=DataQuality.DEGRADED,
    )
    assert snapshot.greeks.theta == -12.0


def test_strike_requires_a_side_and_matching_strikes() -> None:
    with pytest.raises(ValidationError, match="at least one side"):
        OptionStrikeSnapshot(strike=3000)
    with pytest.raises(ValidationError, match="call strike"):
        OptionStrikeSnapshot(strike=3100, call=side())


def test_strike_accepts_ce_only_pe_only_and_both() -> None:
    call = side()
    put = side(OptionType.PE)
    assert OptionStrikeSnapshot(strike=3000, call=call).put is None
    assert OptionStrikeSnapshot(strike=3000, put=put).call is None
    assert OptionStrikeSnapshot(strike=3000, call=call, put=put).put == put


def test_chain_requires_ordered_unique_strikes() -> None:
    first = OptionStrikeSnapshot(strike=3000, call=side())
    second_side = side(
        instrument=side().instrument.model_copy(update={"strike": 3100}),
        strike=3100,
    )
    second = OptionStrikeSnapshot(strike=3100, call=second_side)
    common = {
        "underlying": underlying(),
        "expiry": EXPIRY,
        "observed_at": NOW,
        "received_at": NOW,
        "source_provider": "dhan",
        "freshness": FreshnessState.UNKNOWN,
        "quality": DataQuality.GOOD,
    }
    with pytest.raises(ValidationError, match="ordered ascending"):
        OptionChainSnapshot.model_validate({**common, "strikes": (second, first)})
    with pytest.raises(ValidationError, match="duplicate"):
        OptionChainSnapshot.model_validate({**common, "strikes": (first, first)})


def test_chain_validates_context_and_empty_policy() -> None:
    wrong = side(
        instrument=side().instrument.model_copy(update={"symbol": "TCS"}),
    )
    strike = OptionStrikeSnapshot(strike=3000, call=wrong)
    common = {
        "underlying": underlying(),
        "expiry": EXPIRY,
        "observed_at": NOW,
        "received_at": NOW,
        "source_provider": "dhan",
        "freshness": FreshnessState.UNKNOWN,
    }
    with pytest.raises(ValidationError, match="underlying symbol"):
        OptionChainSnapshot.model_validate(
            {**common, "strikes": (strike,), "quality": DataQuality.GOOD}
        )
    with pytest.raises(ValidationError, match="UNAVAILABLE"):
        OptionChainSnapshot.model_validate(
            {**common, "strikes": (), "quality": DataQuality.GOOD}
        )
    unavailable = OptionChainSnapshot.model_validate(
        {**common, "strikes": (), "quality": DataQuality.UNAVAILABLE}
    )
    assert unavailable.strikes == ()


def test_semantic_collections_are_tuples_and_json_arrays() -> None:
    expiry_list = ExpiryListSnapshot.model_validate(
        {
            "underlying": underlying(),
            "expiries": ["2026-09-24", "2026-10-01"],
            "observed_at": NOW,
            "received_at": NOW,
            "source_provider": "DHAN",
            "freshness": FreshnessState.UNKNOWN,
            "quality": DataQuality.GOOD,
        }
    )
    assert isinstance(expiry_list.expiries, tuple)
    assert isinstance(expiry_list.model_dump(mode="json")["expiries"], list)
    with pytest.raises(AttributeError):
        expiry_list.expiries.append(EXPIRY)  # type: ignore[attr-defined]


def test_expiry_list_requires_ordering_uniqueness_and_unavailable_empty() -> None:
    common = {
        "underlying": underlying(),
        "observed_at": NOW,
        "received_at": NOW,
        "source_provider": "dhan",
        "freshness": FreshnessState.UNKNOWN,
        "quality": DataQuality.GOOD,
    }
    with pytest.raises(ValidationError, match="ordered ascending"):
        ExpiryListSnapshot.model_validate(
            {**common, "expiries": (date(2026, 10, 1), EXPIRY)}
        )
    with pytest.raises(ValidationError, match="duplicate"):
        ExpiryListSnapshot.model_validate({**common, "expiries": (EXPIRY, EXPIRY)})
    with pytest.raises(ValidationError, match="UNAVAILABLE"):
        ExpiryListSnapshot.model_validate({**common, "expiries": ()})


def test_derivative_timestamps_normalize_to_ist_and_reject_naive() -> None:
    snapshot = side()
    assert snapshot.observed_at.isoformat().endswith("+05:30")
    dumped = snapshot.model_dump(mode="json")
    assert str(dumped["observed_at"]).endswith("+05:30")
    assert OptionMarketSnapshot.model_validate(dumped) == snapshot
    with pytest.raises(ValidationError, match="timezone-aware"):
        side(observed_at=datetime(2026, 9, 5, 10, 0))


def test_frozen_models_reject_attribute_replacement() -> None:
    with pytest.raises(ValidationError):
        side().ltp = 1.0
