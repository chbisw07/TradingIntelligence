"""Pinned A6.1 baseline policy and deterministic geometry/spread primitives."""

from decimal import Decimal

from tiaf.contracts import OptionType

from .contracts import (
    ExpressionPreferences,
    HorizonAgeLimit,
    HorizonDurationLimit,
    PositiveDecimal,
    ResidualLifeRule,
    SpreadAssessment,
    SpreadTierPolicy,
    TradeExpressionPolicy,
)
from .enums import (
    A6ErrorCode,
    ExpressionHorizonClass,
    MoneynessLabel,
    SpreadEligibility,
    SpreadQualityTier,
    SubjectClass,
)
from .errors import UnsupportedA6PolicyError

_BASELINE_POLICY_ID = "a6-policy:deterministic-long-option"
_BASELINE_VERSION = "1.0-draft"
_BASELINE_PROFILE_ID = "a6-profile:baseline"


def deterministic_policy(*, version: str = _BASELINE_VERSION) -> TradeExpressionPolicy:
    """Return the generic engineering baseline accepted by the A6 architecture."""
    if version != _BASELINE_VERSION:
        raise UnsupportedA6PolicyError(
            A6ErrorCode.UNKNOWN_POLICY_VERSION,
            f"unsupported deterministic A6 policy version: {version}",
        )
    return TradeExpressionPolicy(
        policy_id=_BASELINE_POLICY_ID,
        policy_version=_BASELINE_VERSION,
        profile_id=_BASELINE_PROFILE_ID,
        evaluator_id="a6-evaluator:admission-foundation",
        evaluator_version="1.0",
        normalizer_id="a6-normalizer:canonical-contracts",
        normalizer_version="1.0",
        supported_subject_classes=(SubjectClass.EQUITY, SubjectClass.INDEX),
        allowed_horizons=(
            ExpressionHorizonClass.DAY,
            ExpressionHorizonClass.POSITIONAL,
        ),
        max_candidate_expiries=3,
        max_strikes_per_chain=512,
        max_evaluated_candidates=9,
        strike_neighborhood=(
            MoneynessLabel.ATM,
            MoneynessLabel.ITM1,
            MoneynessLabel.OTM1,
        ),
        quote_max_age_seconds=60,
        spot_max_age_seconds=60,
        upstream_age_limits=(
            HorizonAgeLimit(
                horizon_class=ExpressionHorizonClass.DAY,
                max_age_seconds=15 * 60,
            ),
            HorizonAgeLimit(
                horizon_class=ExpressionHorizonClass.POSITIONAL,
                max_age_seconds=24 * 60 * 60,
            ),
        ),
        horizon_duration_limits=(
            HorizonDurationLimit(horizon_class=ExpressionHorizonClass.DAY),
            HorizonDurationLimit(
                horizon_class=ExpressionHorizonClass.POSITIONAL,
                maximum_seconds=90 * 24 * 60 * 60,
            ),
        ),
        require_observation_time=True,
        require_qualified_expiration=True,
        hard_spread_limit_bps=Decimal("500"),
        spread_tiers=(
            SpreadTierPolicy(
                tier=SpreadQualityTier.TIER_0,
                upper_bound_inclusive_bps=Decimal("100"),
            ),
            SpreadTierPolicy(
                tier=SpreadQualityTier.TIER_1,
                lower_bound_exclusive_bps=Decimal("100"),
                upper_bound_inclusive_bps=Decimal("500"),
            ),
        ),
        minimum_top_quantity_exclusive=Decimal("0"),
        residual_life_rules=(
            ResidualLifeRule(
                horizon_class=ExpressionHorizonClass.DAY,
                minimum_seconds=24 * 60 * 60,
            ),
            ResidualLifeRule(
                horizon_class=ExpressionHorizonClass.POSITIONAL,
                minimum_seconds=72 * 60 * 60,
            ),
        ),
        premium_cap_is_hard_gate=True,
        known_event_blocks=True,
        allowed_preferences=("MONEYNESS_ORDER", "PREMIUM_CAP", "EVENT_CLEAR"),
        max_alternatives=2,
        require_qualified_coverage=True,
        max_provider_calls=0,
        max_model_calls=0,
        rule_order=(
            "REQUEST_IDENTITY",
            "A4_ADMISSION",
            "SUBJECT_AND_HORIZON",
            "COVERAGE_QUALIFICATION",
            "TIMING_AND_FRESHNESS",
            "EVENT_EVIDENCE",
        ),
    )


def require_supported_policy(policy: TradeExpressionPolicy) -> TradeExpressionPolicy:
    expected = deterministic_policy(version=policy.policy_version)
    if policy != expected:
        raise UnsupportedA6PolicyError(
            A6ErrorCode.UNKNOWN_POLICY_VERSION,
            "A6 policy identity or content is unsupported",
        )
    return policy


def validate_preferences(
    preferences: ExpressionPreferences,
    policy: TradeExpressionPolicy,
) -> None:
    """Ensure caller preferences only narrow/reorder the closed policy set."""
    if not set(preferences.moneyness_order) <= set(policy.strike_neighborhood):
        raise UnsupportedA6PolicyError(
            A6ErrorCode.UNSUPPORTED_PREFERENCE,
            "moneyness preference is outside the policy neighborhood",
        )
    if preferences.premium_cap is not None and "PREMIUM_CAP" not in policy.allowed_preferences:
        raise UnsupportedA6PolicyError(
            A6ErrorCode.UNSUPPORTED_PREFERENCE,
            "premium cap is not allowed by policy",
        )
    if preferences.require_event_clear and "EVENT_CLEAR" not in policy.allowed_preferences:
        raise UnsupportedA6PolicyError(
            A6ErrorCode.UNSUPPORTED_PREFERENCE,
            "event-clear preference is not allowed by policy",
        )


def resolve_moneyness_geometry(
    *,
    listed_strikes: tuple[PositiveDecimal, ...],
    underlying_price: PositiveDecimal,
    option_type: OptionType,
) -> tuple[tuple[MoneynessLabel, Decimal], ...]:
    """Resolve ATM and actual neighboring strikes without inventing intervals."""
    strikes = tuple(Decimal(value) for value in listed_strikes)
    if not strikes or len(strikes) != len(set(strikes)):
        raise ValueError("listed strikes must be non-empty and unique")
    if any(right <= left for left, right in zip(strikes, strikes[1:], strict=False)):
        raise ValueError("listed strikes must be strictly increasing")
    spot = Decimal(underlying_price)
    atm_index = min(
        range(len(strikes)),
        key=lambda index: (abs(strikes[index] - spot), strikes[index]),
    )
    result: list[tuple[MoneynessLabel, Decimal]] = [(MoneynessLabel.ATM, strikes[atm_index])]
    lower = strikes[atm_index - 1] if atm_index > 0 else None
    higher = strikes[atm_index + 1] if atm_index + 1 < len(strikes) else None
    if option_type is OptionType.CE:
        if lower is not None:
            result.append((MoneynessLabel.ITM1, lower))
        if higher is not None:
            result.append((MoneynessLabel.OTM1, higher))
    else:
        if higher is not None:
            result.append((MoneynessLabel.ITM1, higher))
        if lower is not None:
            result.append((MoneynessLabel.OTM1, lower))
    return tuple(result)


def assess_spread(
    *,
    quote_ref: str,
    bid: Decimal | None,
    ask: Decimal | None,
    top_bid_quantity: Decimal | None,
    top_ask_quantity: Decimal | None,
    policy: TradeExpressionPolicy,
) -> SpreadAssessment:
    """Apply only deterministic quote/spread gates; this is not candidate ranking."""
    require_supported_policy(policy)
    if bid is None or ask is None:
        return SpreadAssessment(
            quote_ref=quote_ref,
            eligibility=SpreadEligibility.UNKNOWN,
            quality_tier=SpreadQualityTier.UNKNOWN,
            reason_code="MISSING_BID_OR_ASK",
        )
    if bid <= 0:
        return SpreadAssessment(
            quote_ref=quote_ref,
            eligibility=SpreadEligibility.INELIGIBLE,
            quality_tier=SpreadQualityTier.NOT_ELIGIBLE,
            reason_code="NON_POSITIVE_BID",
        )
    if ask <= 0 or ask < bid:
        return SpreadAssessment(
            quote_ref=quote_ref,
            eligibility=SpreadEligibility.INELIGIBLE,
            quality_tier=SpreadQualityTier.NOT_ELIGIBLE,
            reason_code="INVALID_OR_CROSSED_ASK",
        )
    if top_bid_quantity is None or top_ask_quantity is None:
        return SpreadAssessment(
            quote_ref=quote_ref,
            eligibility=SpreadEligibility.UNKNOWN,
            quality_tier=SpreadQualityTier.UNKNOWN,
            reason_code="MISSING_TOP_QUANTITY",
        )
    minimum = policy.minimum_top_quantity_exclusive
    if top_bid_quantity <= minimum or top_ask_quantity <= minimum:
        return SpreadAssessment(
            quote_ref=quote_ref,
            eligibility=SpreadEligibility.INELIGIBLE,
            quality_tier=SpreadQualityTier.NOT_ELIGIBLE,
            reason_code="NON_POSITIVE_TOP_QUANTITY",
        )
    absolute = ask - bid
    midpoint = (ask + bid) / Decimal(2)
    relative = Decimal(10_000) * absolute / midpoint
    if relative > policy.hard_spread_limit_bps:
        return SpreadAssessment(
            quote_ref=quote_ref,
            absolute_spread=absolute,
            midpoint=midpoint,
            relative_spread_bps=relative,
            eligibility=SpreadEligibility.INELIGIBLE,
            quality_tier=SpreadQualityTier.NOT_ELIGIBLE,
            reason_code="SPREAD_ABOVE_HARD_LIMIT",
        )
    tier = (
        SpreadQualityTier.TIER_0
        if relative <= policy.spread_tiers[0].upper_bound_inclusive_bps
        else SpreadQualityTier.TIER_1
    )
    return SpreadAssessment(
        quote_ref=quote_ref,
        absolute_spread=absolute,
        midpoint=midpoint,
        relative_spread_bps=relative,
        eligibility=SpreadEligibility.ELIGIBLE,
        quality_tier=tier,
        reason_code="SPREAD_ELIGIBLE",
    )
