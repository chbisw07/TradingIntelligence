"""A2.7 exact-window OI, volume, concentration, and weighted-strike tests."""

import math

import pytest

from tiaf.contracts import OptionType
from tiaf.data import OptionChainSnapshot
from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    builtin_feature_registry,
)

from ._derivatives_support import context_with_option_chain, option_chain


def _result(
    feature_id: str,
    *,
    n: int = 2,
    chain: OptionChainSnapshot | None = None,
) -> FeatureResult:
    return DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context_with_option_chain(chain),
        FeatureRequest(
            feature_id=feature_id,
            parameters=(("strikes_each_side", n),),
        ),
    )


def _replace_side_field(
    strike_index: int,
    option_type: OptionType,
    field: str,
    value: object,
) -> OptionChainSnapshot:
    chain = option_chain()
    strike = chain.strikes[strike_index]
    side = strike.call if option_type is OptionType.CE else strike.put
    assert side is not None
    changed_side = side.model_copy(update={field: value})
    changed_strike = strike.model_copy(
        update={"call" if option_type is OptionType.CE else "put": changed_side}
    )
    return chain.model_copy(
        update={
            "strikes": (
                *chain.strikes[:strike_index],
                changed_strike,
                *chain.strikes[strike_index + 1 :],
            )
        }
    )


@pytest.mark.parametrize(
    ("feature_id", "expected"),
    (
        ("derivatives.ce_iv_mean", 12.125),
        ("derivatives.pe_iv_mean", 22.875),
        ("derivatives.ce_oi_total", 150),
        ("derivatives.pe_oi_total", 150),
        ("derivatives.oi_put_call_ratio", 1.0),
        ("derivatives.ce_volume_total", 15),
        ("derivatives.pe_volume_total", 15),
        ("derivatives.volume_put_call_ratio", 1.0),
        ("derivatives.ce_max_oi_strike", 1500.0),
        ("derivatives.pe_max_oi_strike", 1300.0),
        ("derivatives.ce_max_oi", 50),
        ("derivatives.pe_max_oi", 50),
        ("derivatives.ce_oi_top1_fraction", 1 / 3),
        ("derivatives.pe_oi_top1_fraction", 1 / 3),
        ("derivatives.ce_oi_weighted_strike", 1433.3333333333333),
        ("derivatives.pe_oi_weighted_strike", 1366.6666666666667),
    ),
)
def test_exact_full_window_values(feature_id: str, expected: float) -> None:
    assert _result(feature_id).value == pytest.approx(expected)


def test_requested_window_has_exact_metadata_and_no_tail_leakage() -> None:
    result = _result("derivatives.ce_oi_total", n=1)
    assert result.value == 90
    assert result.metadata["requested_strike_count"] == 3
    assert result.metadata["actual_strike_count"] == 3
    assert result.metadata["window_min_strike"] == 1350.0
    assert result.metadata["window_max_strike"] == 1450.0


def test_edge_window_is_insufficient_instead_of_silently_reduced() -> None:
    chain = option_chain().model_copy(update={"underlying_ltp": 1300.0})
    result = _result("derivatives.ce_oi_total", n=1, chain=chain)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None


@pytest.mark.parametrize("bad_n", (-1, True, 1.5, "1", None))
def test_window_parameter_is_exact_nonnegative_integer(bad_n: object) -> None:
    request = FeatureRequest(
        feature_id="derivatives.ce_oi_total",
        parameters=(("strikes_each_side", bad_n),),  # type: ignore[arg-type]
    )
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    if bad_n is None:
        with pytest.raises(Exception, match="nonnegative integer"):
            engine.compute_one(context_with_option_chain(), request)
    else:
        with pytest.raises(Exception, match="nonnegative integer"):
            engine.compute_one(context_with_option_chain(), request)


def test_zero_each_side_supports_single_atm_strike() -> None:
    assert _result("derivatives.ce_oi_weighted_strike", n=0).value == 1400.0
    assert _result("derivatives.ce_oi_top1_fraction", n=0).value == 1.0


@pytest.mark.parametrize(
    ("feature_id", "field", "option_type"),
    (
        ("derivatives.ce_oi_total", "open_interest", OptionType.CE),
        ("derivatives.pe_oi_total", "open_interest", OptionType.PE),
        ("derivatives.ce_volume_total", "volume", OptionType.CE),
        ("derivatives.pe_volume_total", "volume", OptionType.PE),
    ),
)
def test_missing_required_window_field_is_insufficient(
    feature_id: str, field: str, option_type: OptionType
) -> None:
    chain = _replace_side_field(2, option_type, field, None)
    result = _result(feature_id, chain=chain)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


@pytest.mark.parametrize("option_type", (OptionType.CE, OptionType.PE))
def test_window_iv_missingness_is_side_local(option_type: OptionType) -> None:
    chain = _replace_side_field(2, option_type, "implied_volatility", None)
    feature_id = f"derivatives.{option_type.value.lower()}_iv_mean"
    assert _result(feature_id, chain=chain).status is FeatureStatus.INSUFFICIENT_DATA


@pytest.mark.parametrize("bad_iv", (-1.0, math.nan, math.inf))
def test_window_iv_rejects_malformed_values(bad_iv: float) -> None:
    chain = _replace_side_field(2, OptionType.CE, "implied_volatility", bad_iv)
    assert _result("derivatives.ce_iv_mean", chain=chain).status is FeatureStatus.FAILED


@pytest.mark.parametrize(
    ("feature_id", "field", "option_type", "bad_value"),
    (
        ("derivatives.ce_oi_total", "open_interest", OptionType.CE, -1),
        ("derivatives.ce_oi_total", "open_interest", OptionType.CE, 1.5),
        ("derivatives.pe_oi_total", "open_interest", OptionType.PE, math.inf),
        ("derivatives.ce_volume_total", "volume", OptionType.CE, -1),
        ("derivatives.pe_volume_total", "volume", OptionType.PE, math.nan),
    ),
)
def test_malformed_counts_fail_safely(
    feature_id: str,
    field: str,
    option_type: OptionType,
    bad_value: object,
) -> None:
    chain = _replace_side_field(2, option_type, field, bad_value)
    result = _result(feature_id, chain=chain)
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


def test_missing_strike_side_is_not_paired_by_adjacency() -> None:
    chain = option_chain()
    strike = chain.strikes[1].model_copy(update={"call": None})
    changed = chain.model_copy(
        update={"strikes": (chain.strikes[0], strike, *chain.strikes[2:])}
    )
    result = _result("derivatives.ce_oi_total", chain=changed)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


@pytest.mark.parametrize(
    ("feature_id", "field"),
    (
        ("derivatives.oi_put_call_ratio", "open_interest"),
        ("derivatives.volume_put_call_ratio", "volume"),
    ),
)
def test_zero_ce_ratio_denominator_fails_safely(feature_id: str, field: str) -> None:
    chain = option_chain()
    for index in range(len(chain.strikes)):
        chain = _replace_field_on_chain(chain, index, OptionType.CE, field, 0)
    result = _result(feature_id, chain=chain)
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


def _replace_field_on_chain(
    chain: OptionChainSnapshot,
    strike_index: int,
    option_type: OptionType,
    field: str,
    value: object,
) -> OptionChainSnapshot:
    strike = chain.strikes[strike_index]
    side = strike.call if option_type is OptionType.CE else strike.put
    assert side is not None
    changed_side = side.model_copy(update={field: value})
    changed_strike = strike.model_copy(
        update={"call" if option_type is OptionType.CE else "put": changed_side}
    )
    return chain.model_copy(
        update={
            "strikes": (
                *chain.strikes[:strike_index],
                changed_strike,
                *chain.strikes[strike_index + 1 :],
            )
        }
    )


@pytest.mark.parametrize(
    "feature_id",
    (
        "derivatives.ce_oi_top1_fraction",
        "derivatives.pe_oi_top1_fraction",
        "derivatives.ce_oi_weighted_strike",
        "derivatives.pe_oi_weighted_strike",
    ),
)
def test_zero_total_oi_statistics_fail_safely(feature_id: str) -> None:
    chain = option_chain()
    option_type = OptionType.CE if ".ce_" in feature_id else OptionType.PE
    for index in range(len(chain.strikes)):
        chain = _replace_field_on_chain(
            chain, index, option_type, "open_interest", 0
        )
    assert _result(feature_id, chain=chain).status is FeatureStatus.FAILED


def test_max_oi_tie_uses_closest_to_atm_then_lower_strike() -> None:
    chain = option_chain()
    for index, value in enumerate((1, 99, 1, 99, 1)):
        chain = _replace_field_on_chain(
            chain, index, OptionType.CE, "open_interest", value
        )
    assert _result("derivatives.ce_max_oi_strike", chain=chain).value == 1350.0


def test_concentration_examples_are_exact() -> None:
    chain = option_chain()
    for index, value in enumerate((0, 0, 100, 0, 0)):
        chain = _replace_field_on_chain(
            chain, index, OptionType.CE, "open_interest", value
        )
    assert _result("derivatives.ce_oi_top1_fraction", chain=chain).value == 1.0

    even = option_chain()
    for index in range(len(even.strikes)):
        even = _replace_field_on_chain(
            even, index, OptionType.CE, "open_interest", 10
        )
    assert _result("derivatives.ce_oi_top1_fraction", chain=even).value == 0.2


def test_weighted_strike_is_bounded_by_positive_oi_window() -> None:
    value = _result("derivatives.pe_oi_weighted_strike").value
    assert isinstance(value, float)
    assert 1300 <= value <= 1500
