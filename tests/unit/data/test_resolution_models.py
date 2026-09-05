"""Contract tests for provider-neutral instrument resolution."""

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from tiaf.contracts import DataQuality, OptionType
from tiaf.data import InstrumentKey, InstrumentType, MarketSegment
from tiaf.data.resolution import (
    InstrumentQuery,
    ResolutionKind,
    ResolutionPolicy,
    ResolutionResult,
    ResolvedInstrument,
)


@pytest.mark.parametrize("value", ["reliance", " RELIANCE ", "Reliance"])
def test_query_normalizes_symbol(value: str) -> None:
    assert InstrumentQuery(symbol=value).symbol == "RELIANCE"


@pytest.mark.parametrize("field", ["symbol", "trading_symbol", "provider_instrument_id"])
def test_query_accepts_each_primary_identifier(field: str) -> None:
    assert InstrumentQuery.model_validate({field: " 1333 "})


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"symbol": ""},
        {"symbol": "R", "strike": 100},
        {"symbol": "R", "option_type": "CE"},
        {"symbol": "R", "instrument_type": "CALL_OPTION"},
        {
            "symbol": "R",
            "instrument_type": "CALL_OPTION",
            "expiry": "2026-09-24",
            "strike": 100,
            "option_type": "PE",
        },
        {
            "symbol": "R",
            "instrument_type": "PUT_OPTION",
            "expiry": "2026-09-24",
            "strike": 0,
            "option_type": "PE",
        },
    ],
)
def test_query_rejects_invalid_or_incoherent_payloads(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        InstrumentQuery.model_validate(payload)


def _resolved() -> ResolvedInstrument:
    observed = datetime(2026, 9, 5, 4, 30, tzinfo=UTC)
    instrument = InstrumentKey(
        symbol="RELIANCE",
        exchange="NSE",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
        trading_symbol="RELIANCE",
        provider_instrument_id="1333",
    )
    return ResolvedInstrument(
        instrument=instrument,
        provider_name="DHAN",
        provider_instrument_id="1333",
        company_name="Reliance Industries",
        lot_size=1,
        tick_size=0.05,
        source_record_id="dhan:NSE_EQUITY:1333",
        source_observed_at=observed,
        resolution_kind=ResolutionKind.PROVIDER_ID,
        quality=DataQuality.GOOD,
    )


def test_resolved_instrument_normalizes_provider_and_timestamp() -> None:
    resolved = _resolved()
    assert resolved.provider_name == "dhan"
    assert resolved.source_observed_at.isoformat().endswith("+05:30")


def test_resolution_models_are_frozen_and_matches_are_tuples() -> None:
    resolved = _resolved()
    result = ResolutionResult.model_validate(
        {
            "query": InstrumentQuery(symbol="RELIANCE"),
            "matches": [resolved],
            "resolved": resolved,
            "observed_at": resolved.source_observed_at,
        }
    )
    assert isinstance(result.matches, tuple)
    with pytest.raises(ValidationError):
        result.ambiguous = True


def test_resolution_json_round_trip_keeps_arrays() -> None:
    resolved = _resolved()
    result = ResolutionResult(
        query=InstrumentQuery(symbol="RELIANCE"),
        matches=(resolved,),
        resolved=resolved,
        observed_at=resolved.source_observed_at,
    )
    dumped = result.model_dump(mode="json")
    assert isinstance(dumped["matches"], list)
    assert ResolutionResult.model_validate(dumped) == result


@pytest.mark.parametrize(
    "values",
    [
        {"matches": (), "resolved": None, "ambiguous": False, "not_found": False},
        {"matches": (), "resolved": _resolved(), "ambiguous": False, "not_found": True},
        {"matches": (_resolved(),), "resolved": None, "ambiguous": False, "not_found": False},
        {
            "matches": (_resolved(), _resolved()),
            "resolved": _resolved(),
            "ambiguous": True,
            "not_found": False,
        },
    ],
)
def test_resolution_result_rejects_impossible_states(values: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        ResolutionResult.model_validate(
            {
                "query": InstrumentQuery(symbol="RELIANCE"),
                "observed_at": datetime(2026, 9, 5, tzinfo=UTC),
                **values,
            }
        )


def test_full_option_query_is_valid() -> None:
    query = InstrumentQuery(
        symbol="reliance",
        instrument_type=InstrumentType.CALL_OPTION,
        expiry=date(2026, 9, 24),
        strike=3000,
        option_type=OptionType.CE,
    )
    assert query.strike == 3000


def test_resolution_policy_is_frozen_normalized_and_json_clean() -> None:
    policy = ResolutionPolicy(
        primary_exchange=" bse ",
        primary_fno_exchange="nse",
        prefer_primary_cash_listing=True,
    )
    assert policy.primary_exchange == "BSE"
    assert policy.model_dump(mode="json") == {
        "schema_version": "1.0",
        "primary_exchange": "BSE",
        "primary_fno_exchange": "NSE",
        "prefer_primary_cash_listing": True,
    }
    with pytest.raises(ValidationError):
        policy.primary_exchange = "NSE"
