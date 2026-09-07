"""A2.7 expiry, ATM, premium, IV, Greeks, spread, and safety tests."""

import math
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from tiaf.context import AnalysisContext
from tiaf.contracts import DataQuality, OptionType
from tiaf.data import OptionChainSnapshot
from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    builtin_feature_registry,
)

from ..context._support import EXPIRY, NOW
from ._derivatives_support import (
    context_with_failed_option_chain,
    context_with_option_chain,
    context_without_option_chain_request,
    option_chain,
)


def _result(
    feature_id: str, *, context: AnalysisContext | None = None
) -> FeatureResult:
    selected = context if context is not None else context_with_option_chain()
    return DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        selected, FeatureRequest(feature_id=feature_id)
    )


def _replace_atm_side(
    field: str, value: object, option_type: OptionType
) -> OptionChainSnapshot:
    chain = option_chain()
    atm = chain.strikes[2]
    side = atm.call if option_type is OptionType.CE else atm.put
    assert side is not None
    changed_side = side.model_copy(update={field: value})
    changed_atm = atm.model_copy(
        update={"call" if option_type is OptionType.CE else "put": changed_side}
    )
    return chain.model_copy(
        update={"strikes": (*chain.strikes[:2], changed_atm, *chain.strikes[3:])}
    )


@pytest.mark.parametrize(
    ("spot", "expected"),
    ((1400.0, 1400.0), (1370.0, 1350.0), (1380.0, 1400.0), (1375.0, 1350.0)),
)
def test_atm_uses_nearest_listed_strike_and_lower_tie(spot: float, expected: float) -> None:
    result = _result(
        "derivatives.atm_strike",
        context=context_with_option_chain(option_chain(spot=spot)),
    )
    assert result.status is FeatureStatus.AVAILABLE
    assert result.value == expected


def test_unsorted_defensive_snapshot_is_normalized_before_atm_resolution() -> None:
    chain = option_chain()
    unsorted = chain.model_copy(update={"strikes": tuple(reversed(chain.strikes))})
    result = _result(
        "derivatives.atm_strike", context=context_with_option_chain(unsorted)
    )
    assert result.value == 1400.0


@pytest.mark.parametrize("mutation", ("duplicate", "malformed"))
def test_duplicate_or_malformed_strike_fails_safely(mutation: str) -> None:
    chain = option_chain()
    if mutation == "duplicate":
        strikes = (*chain.strikes[:2], chain.strikes[1], *chain.strikes[3:])
    else:
        bad = chain.strikes[2].model_copy(update={"strike": "bad"})
        strikes = (*chain.strikes[:2], bad, *chain.strikes[3:])
    result = _result(
        "derivatives.atm_strike",
        context=context_with_option_chain(chain.model_copy(update={"strikes": strikes})),
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


def test_empty_chain_is_insufficient() -> None:
    chain = option_chain().model_copy(update={"strikes": ()})
    result = _result(
        "derivatives.atm_strike", context=context_with_option_chain(chain)
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


@pytest.mark.parametrize("spot", (None, 0.0, -1.0, math.nan, math.inf))
def test_missing_or_invalid_spot_never_escapes_geometry(spot: float | None) -> None:
    chain = option_chain().model_copy(update={"underlying_ltp": spot})
    result = _result(
        "derivatives.atm_distance_percent", context=context_with_option_chain(chain)
    )
    expected = FeatureStatus.INSUFFICIENT_DATA if spot is None else FeatureStatus.FAILED
    assert result.status is expected
    assert result.value is None


def test_strike_count_does_not_require_spot() -> None:
    chain = option_chain().model_copy(update={"underlying_ltp": None})
    assert _result(
        "derivatives.strike_count", context=context_with_option_chain(chain)
    ).value == 5


def test_atm_distance_uses_chain_spot_not_quote() -> None:
    context = context_with_option_chain(option_chain(spot=1410.0))
    assert context.quote is not None
    context = context.model_copy(update={"quote": context.quote.model_copy(update={"ltp": 9999})})
    result = _result("derivatives.atm_distance_percent", context=context)
    assert result.value == pytest.approx((1410 - 1400) / 1410 * 100)
    assert result.metadata["underlying_ltp_source"] == "option_chain_snapshot"


@pytest.mark.parametrize(
    ("feature_id", "expected"),
    (
        ("derivatives.atm_ce_ltp", 30.0),
        ("derivatives.atm_pe_ltp", 30.0),
        ("derivatives.atm_straddle_premium", 60.0),
        ("derivatives.atm_straddle_percent_of_spot", 60 / 1400 * 100),
        ("derivatives.atm_ce_iv", 12.125),
        ("derivatives.atm_pe_iv", 22.875),
        ("derivatives.atm_mean_iv", 17.5),
        ("derivatives.atm_iv_difference", -10.75),
    ),
)
def test_atm_premium_and_iv_values_are_exact(feature_id: str, expected: float) -> None:
    result = _result(feature_id)
    assert result.value == pytest.approx(expected)


@pytest.mark.parametrize(
    ("feature_id", "missing_side"),
    (
        ("derivatives.atm_ce_ltp", OptionType.CE),
        ("derivatives.atm_pe_ltp", OptionType.PE),
        ("derivatives.atm_straddle_premium", OptionType.CE),
        ("derivatives.atm_mean_iv", OptionType.PE),
    ),
)
def test_required_atm_side_missing_is_local_insufficient(
    feature_id: str, missing_side: OptionType
) -> None:
    chain = option_chain()
    atm = chain.strikes[2].model_copy(
        update={"call" if missing_side is OptionType.CE else "put": None}
    )
    chain = chain.model_copy(
        update={"strikes": (*chain.strikes[:2], atm, *chain.strikes[3:])}
    )
    result = _result(feature_id, context=context_with_option_chain(chain))
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


@pytest.mark.parametrize("bad_iv", (-1.0, math.nan, math.inf, "bad"))
def test_malformed_iv_fails_without_recomputation(bad_iv: object) -> None:
    chain = _replace_atm_side("implied_volatility", bad_iv, OptionType.CE)
    result = _result("derivatives.atm_ce_iv", context=context_with_option_chain(chain))
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


@pytest.mark.parametrize(
    ("feature_id", "expected"),
    (
        ("derivatives.atm_ce_delta", 0.5),
        ("derivatives.atm_pe_delta", -0.5),
        ("derivatives.atm_ce_gamma", 0.012),
        ("derivatives.atm_pe_gamma", 0.012),
        ("derivatives.atm_ce_theta", -1.2),
        ("derivatives.atm_pe_theta", -1.2),
        ("derivatives.atm_ce_vega", 2.2),
        ("derivatives.atm_pe_vega", 2.2),
    ),
)
def test_atm_provider_greeks_are_preserved(feature_id: str, expected: float) -> None:
    assert _result(feature_id).value == pytest.approx(expected)


@pytest.mark.parametrize("bad_delta", (-1.01, 1.01, math.nan, math.inf))
def test_invalid_delta_fails_safely(bad_delta: float) -> None:
    chain = option_chain()
    atm = chain.strikes[2]
    assert atm.call is not None
    greeks = atm.call.greeks.model_copy(update={"delta": bad_delta})
    call = atm.call.model_copy(update={"greeks": greeks})
    changed = atm.model_copy(update={"call": call})
    chain = chain.model_copy(
        update={"strikes": (*chain.strikes[:2], changed, *chain.strikes[3:])}
    )
    result = _result("derivatives.atm_ce_delta", context=context_with_option_chain(chain))
    assert result.status is FeatureStatus.FAILED


def test_missing_greek_does_not_invalidate_atm_iv() -> None:
    chain = option_chain()
    atm = chain.strikes[2]
    assert atm.call is not None
    greeks = atm.call.greeks.model_copy(update={"gamma": None})
    call = atm.call.model_copy(update={"greeks": greeks})
    changed = atm.model_copy(update={"call": call})
    chain = chain.model_copy(
        update={"strikes": (*chain.strikes[:2], changed, *chain.strikes[3:])}
    )
    context = context_with_option_chain(chain)
    assert (
        _result("derivatives.atm_ce_gamma", context=context).status
        is FeatureStatus.INSUFFICIENT_DATA
    )
    assert _result("derivatives.atm_ce_iv", context=context).value == 12.125


@pytest.mark.parametrize("option_type", (OptionType.CE, OptionType.PE))
def test_atm_spread_percent_is_midpoint_normalized(option_type: OptionType) -> None:
    feature_id = f"derivatives.atm_{option_type.value.lower()}_bid_ask_spread_percent"
    assert _result(feature_id).value == pytest.approx(2 / 30 * 100)


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    (
        ("bid", None, FeatureStatus.INSUFFICIENT_DATA),
        ("ask", None, FeatureStatus.INSUFFICIENT_DATA),
        ("bid", 0.0, FeatureStatus.INSUFFICIENT_DATA),
        ("ask", 0.0, FeatureStatus.INSUFFICIENT_DATA),
        ("bid", 40.0, FeatureStatus.FAILED),
        ("ask", math.inf, FeatureStatus.FAILED),
    ),
)
def test_missing_placeholder_or_malformed_spread_is_safe(
    field: str, value: object, expected: FeatureStatus
) -> None:
    chain = _replace_atm_side(field, value, OptionType.CE)
    result = _result(
        "derivatives.atm_ce_bid_ask_spread_percent",
        context=context_with_option_chain(chain),
    )
    assert result.status is expected
    assert result.value is None


def test_expiry_and_calendar_days_use_chain_as_of_date() -> None:
    assert _result("derivatives.expiry_date").value == EXPIRY.isoformat()
    assert _result("derivatives.days_to_expiry").value == (EXPIRY - NOW.date()).days


def test_zero_dte_is_valid() -> None:
    observed = datetime(2026, 9, 29, 9, 15, tzinfo=ZoneInfo("Asia/Kolkata"))
    result = _result(
        "derivatives.days_to_expiry",
        context=context_with_option_chain(option_chain(observed_at=observed)),
    )
    assert result.value == 0


def test_utc_timestamp_is_normalized_before_calendar_day_calculation() -> None:
    utc = datetime(2026, 9, 28, 20, 0, tzinfo=ZoneInfo("UTC"))
    chain = option_chain(observed_at=utc)
    result = _result(
        "derivatives.days_to_expiry", context=context_with_option_chain(chain)
    )
    assert result.value == 0
    offset = result.as_of.utcoffset()
    assert offset is not None
    assert offset.total_seconds() == 19_800


def test_past_expiry_fails_safely() -> None:
    observed = datetime(2026, 9, 30, 9, 15, tzinfo=ZoneInfo("Asia/Kolkata"))
    result = _result(
        "derivatives.expiry_date",
        context=context_with_option_chain(option_chain(observed_at=observed)),
    )
    assert result.status is FeatureStatus.FAILED


@pytest.mark.parametrize(
    ("quality", "status"),
    (
        (DataQuality.GOOD, FeatureStatus.AVAILABLE),
        (DataQuality.PARTIAL, FeatureStatus.PARTIAL),
        (DataQuality.DEGRADED, FeatureStatus.PARTIAL),
    ),
)
def test_option_chain_quality_is_never_upgraded(
    quality: DataQuality, status: FeatureStatus
) -> None:
    result = _result(
        "derivatives.atm_ce_iv",
        context=context_with_option_chain(option_chain(quality=quality), quality=quality),
    )
    assert result.quality is quality
    assert result.status is status


def test_not_requested_and_failed_chain_return_no_value() -> None:
    not_requested = _result(
        "derivatives.atm_strike", context=context_without_option_chain_request()
    )
    failed = _result(
        "derivatives.atm_strike", context=context_with_failed_option_chain()
    )
    assert not_requested.status is FeatureStatus.NOT_APPLICABLE
    assert failed.status is FeatureStatus.INSUFFICIENT_DATA
    assert not_requested.value is failed.value is None


def test_acquisition_time_semantics_are_preserved_without_fabrication() -> None:
    result = _result("derivatives.atm_strike")
    assert result.as_of == NOW
    assert result.source_observed_at == NOW
    assert (
        result.metadata["source_time_semantics"]
        == "option_chain_acquisition_time_no_authoritative_market_timestamp"
    )
