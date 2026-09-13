from decimal import Decimal

import pytest

from tiaf.contracts import OptionType
from tiaf.trade_expression import (
    ExpressionPreferences,
    MoneynessLabel,
    SpreadEligibility,
    SpreadQualityTier,
    TradeExpressionPolicy,
    UnsupportedA6PolicyError,
    assess_spread,
    deterministic_policy,
    resolve_moneyness_geometry,
)


def test_baseline_policy_is_pinned_versioned_and_deterministic() -> None:
    policy = deterministic_policy()
    assert policy.policy_version == "1.0-draft"
    assert policy.fingerprint() == deterministic_policy().fingerprint()
    assert policy.max_candidate_expiries == 3
    assert policy.max_strikes_per_chain == 512
    assert policy.max_evaluated_candidates == 9
    assert policy.quote_max_age_seconds == 60
    assert policy.spot_max_age_seconds == 60
    assert [item.max_age_seconds for item in policy.upstream_age_limits] == [900, 86400]
    assert [item.minimum_seconds for item in policy.residual_life_rules] == [86400, 259200]
    assert policy.horizon_duration_limits[1].maximum_seconds == 90 * 86400
    assert policy.hard_spread_limit_bps == 500
    assert policy.max_alternatives == 2
    assert policy.max_provider_calls == policy.max_model_calls == 0


def test_unknown_policy_version_is_typed_error() -> None:
    with pytest.raises(UnsupportedA6PolicyError):
        deterministic_policy(version="999")


def test_preferences_are_closed_and_cannot_override_hard_policy() -> None:
    preferences = ExpressionPreferences(
        moneyness_order=(MoneynessLabel.OTM1, MoneynessLabel.ATM),
        premium_cap=Decimal("100"),
        premium_currency="INR",
    )
    assert preferences.moneyness_order == (MoneynessLabel.OTM1, MoneynessLabel.ATM)
    policy = deterministic_policy()
    assert policy.hard_spread_limit_bps == 500
    assert policy.premium_cap_is_hard_gate
    with pytest.raises(Exception):
        ExpressionPreferences.model_validate({"moneyness_order": ["ATM"], "cheapest_first": True})


def test_moneyness_geometry_uses_lower_tie_and_actual_neighbors() -> None:
    strikes = (Decimal("90"), Decimal("100"), Decimal("115"), Decimal("140"))
    ce = dict(
        resolve_moneyness_geometry(
            listed_strikes=strikes,
            underlying_price=Decimal("107.5"),
            option_type=OptionType.CE,
        )
    )
    pe = dict(
        resolve_moneyness_geometry(
            listed_strikes=strikes,
            underlying_price=Decimal("107.5"),
            option_type=OptionType.PE,
        )
    )
    assert ce == {
        MoneynessLabel.ATM: Decimal("100"),
        MoneynessLabel.ITM1: Decimal("90"),
        MoneynessLabel.OTM1: Decimal("115"),
    }
    assert pe == {
        MoneynessLabel.ATM: Decimal("100"),
        MoneynessLabel.ITM1: Decimal("115"),
        MoneynessLabel.OTM1: Decimal("90"),
    }


def test_moneyness_rejects_duplicates_and_unsorted_input() -> None:
    for strikes in (
        (Decimal("100"), Decimal("100")),
        (Decimal("110"), Decimal("100")),
    ):
        with pytest.raises(ValueError):
            resolve_moneyness_geometry(
                listed_strikes=strikes,
                underlying_price=Decimal("105"),
                option_type=OptionType.CE,
            )


@pytest.mark.parametrize(
    "bid,ask,expected_tier",
    [
        (Decimal("99.5"), Decimal("100.5"), SpreadQualityTier.TIER_0),
        (Decimal("97.5"), Decimal("102.5"), SpreadQualityTier.TIER_1),
    ],
)
def test_spread_boundaries_are_exact(
    bid: Decimal, ask: Decimal, expected_tier: SpreadQualityTier
) -> None:
    result = assess_spread(
        quote_ref="quote:spread",
        bid=bid,
        ask=ask,
        top_bid_quantity=Decimal("1"),
        top_ask_quantity=Decimal("1"),
        policy=deterministic_policy(),
    )
    assert result.eligibility is SpreadEligibility.ELIGIBLE
    assert result.quality_tier is expected_tier
    assert result.relative_spread_bps in {Decimal("100"), Decimal("500")}


def test_spread_missing_zero_depth_and_over_limit_are_distinct() -> None:
    policy = deterministic_policy()
    missing = assess_spread(
        quote_ref="quote:missing",
        bid=None,
        ask=Decimal("100"),
        top_bid_quantity=Decimal("1"),
        top_ask_quantity=Decimal("1"),
        policy=policy,
    )
    zero_depth = assess_spread(
        quote_ref="quote:zero-depth",
        bid=Decimal("99"),
        ask=Decimal("100"),
        top_bid_quantity=Decimal("0"),
        top_ask_quantity=Decimal("1"),
        policy=policy,
    )
    wide = assess_spread(
        quote_ref="quote:wide",
        bid=Decimal("90"),
        ask=Decimal("110"),
        top_bid_quantity=Decimal("1"),
        top_ask_quantity=Decimal("1"),
        policy=policy,
    )
    assert missing.eligibility is SpreadEligibility.UNKNOWN
    assert zero_depth.reason_code == "NON_POSITIVE_TOP_QUANTITY"
    assert wide.reason_code == "SPREAD_ABOVE_HARD_LIMIT"


def test_spread_primitives_do_not_rank_or_select_candidates() -> None:
    fields = TradeExpressionPolicy.model_fields
    assert "weights" not in fields
    assert "preferred_candidate" not in fields
