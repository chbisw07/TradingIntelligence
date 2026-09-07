"""A2.9 component, direction, quality, and class behavior."""

import pytest

from tiaf.baseline import (
    BaselineDirection,
    BaselineEngine,
    CandidateClass,
    ComponentName,
    ExplanationCode,
    OpportunityAssessment,
    ScoreSemantics,
    default_policy,
    summarize_assessment,
)
from tiaf.contracts import DataQuality, FreshnessState, TradeStyle
from tiaf.features import FeatureStatus

from ._support import POSITIVE_VALUES, baseline_request, values_for


@pytest.mark.parametrize(
    ("profile", "expected"),
    (
        ("positive", BaselineDirection.POSITIVE),
        ("negative", BaselineDirection.NEGATIVE),
        ("neutral", BaselineDirection.NEUTRAL),
        ("conflicted", BaselineDirection.CONFLICTED),
    ),
)
def test_direction_fixtures(profile: str, expected: BaselineDirection) -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    assessment = BaselineEngine((policy,)).assess(baseline_request(policy, profile=profile))
    assert assessment.market_state.direction is expected


def test_every_component_is_present_and_decomposable() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    assessment = BaselineEngine((policy,)).assess(baseline_request(policy))
    assert {item.component for item in assessment.market_state.components} == set(ComponentName)
    trend = next(
        item
        for item in assessment.market_state.components
        if item.component is ComponentName.TREND_QUALITY
    )
    assert trend.positive_score is not None and trend.negative_score is not None
    assert len(trend.contributions) == 3
    assert all(item.source_context_id for item in trend.contributions)


def test_missing_optional_relative_is_unavailable_not_neutral() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    assessment = BaselineEngine((policy,)).assess(baseline_request(policy, include_relative=False))
    relative = next(
        item
        for item in assessment.market_state.components
        if item.component is ComponentName.RELATIVE_STRENGTH
    )
    assert not relative.available
    assert relative.score is None
    assert len(relative.missing_evidence) == 2


def test_failed_required_evidence_produces_no_trade() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    assessment = BaselineEngine((policy,)).assess(
        baseline_request(policy, omit=frozenset({"trend.slope"}))
    )
    assert assessment.candidate_class is CandidateClass.NO_TRADE
    assert ExplanationCode.EVIDENCE_MISSING in assessment.explanation_codes


def test_failed_critical_results_produce_no_trade_without_fabricated_scores() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    assessment = BaselineEngine((policy,)).assess(
        baseline_request(
            policy,
            quality=DataQuality.UNAVAILABLE,
            status=FeatureStatus.FAILED,
        )
    )
    assert assessment.candidate_class is CandidateClass.NO_TRADE
    assert assessment.market_state.quality is DataQuality.UNAVAILABLE
    assert all(
        item.score is None
        for item in assessment.market_state.components
        if item.component
        in {
            ComponentName.DIRECTIONAL_STRUCTURE,
            ComponentName.TREND_QUALITY,
            ComponentName.MOMENTUM,
        }
    )


@pytest.mark.parametrize(
    ("quality", "status", "expected"),
    (
        (DataQuality.GOOD, FeatureStatus.AVAILABLE, DataQuality.GOOD),
        (DataQuality.PARTIAL, FeatureStatus.PARTIAL, DataQuality.PARTIAL),
        (DataQuality.DEGRADED, FeatureStatus.PARTIAL, DataQuality.DEGRADED),
    ),
)
def test_quality_is_preserved_and_affects_scores(
    quality: DataQuality, status: FeatureStatus, expected: DataQuality
) -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    good = BaselineEngine((policy,)).assess(baseline_request(policy))
    assessment = BaselineEngine((policy,)).assess(
        baseline_request(policy, quality=quality, status=status)
    )
    assert assessment.market_state.quality is expected
    if quality is not DataQuality.GOOD:
        assert assessment.opportunity_score < good.opportunity_score


def test_stale_critical_evidence_is_no_trade_and_never_scored() -> None:
    policy = default_policy(TradeStyle.DAY)
    assessment = BaselineEngine((policy,)).assess(
        baseline_request(policy, primary_freshness=FreshnessState.STALE)
    )
    assert assessment.candidate_class is CandidateClass.NO_TRADE
    assert ExplanationCode.EVIDENCE_STALE in assessment.explanation_codes
    assert all(
        not item.contributions
        for item in assessment.market_state.components
        if any(key.startswith("PRIMARY:") for key in item.missing_evidence)
    )


@pytest.mark.parametrize(
    ("freshness", "penalty"),
    (
        (FreshnessState.AGING, 4.0),
        (FreshnessState.UNKNOWN, 8.0),
    ),
)
def test_non_stale_freshness_uses_explicit_policy_penalty(
    freshness: FreshnessState,
    penalty: float,
) -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    engine = BaselineEngine((policy,))
    fresh = engine.assess(baseline_request(policy))
    changed = engine.assess(baseline_request(policy, primary_freshness=freshness))
    assert changed.opportunity_score == pytest.approx(max(0.0, fresh.opportunity_score - penalty))


def test_same_snapshot_and_policy_are_byte_stable() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    request = baseline_request(policy)
    first = BaselineEngine((policy,)).assess(request)
    second = BaselineEngine((policy,)).assess(request)
    assert first == second
    assert first.model_dump_json() == second.model_dump_json()
    assert OpportunityAssessment.model_validate(first.model_dump(mode="json")) == first


def test_high_extension_reduces_opportunity_and_can_mark_mature() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    early_values = dict(POSITIVE_VALUES)
    early_values.update(
        {"extension.ema": 0.1, "momentum.return_20": 1.0, "extension.range": 1.0}
    )
    mature_values = dict(early_values)
    mature_values.update(
        {
            "extension.ema": 6.0,
            "extension.range": 5.0,
            "momentum.return_20": 30.0,
        }
    )
    engine = BaselineEngine((policy,))
    early = engine.assess(baseline_request(policy, values=early_values))
    mature = engine.assess(baseline_request(policy, values=mature_values))
    assert mature.opportunity_score < early.opportunity_score
    assert mature.candidate_class is CandidateClass.MATURE_AVOID_CHASE
    assert mature.chase_risk_score >= policy.classification_thresholds.mature_extension


def test_remaining_room_is_direction_specific_and_not_a_target() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    positive = BaselineEngine((policy,)).assess(baseline_request(policy, profile="positive"))
    negative = BaselineEngine((policy,)).assess(baseline_request(policy, profile="negative"))
    for assessment in (positive, negative):
        room = next(
            item
            for item in assessment.market_state.components
            if item.component is ComponentName.REMAINING_ROOM
        )
        assert room.score is not None
        assert len(room.contributions) == 2
        assert room.semantics is ScoreSemantics.DIRECTIONAL_SUPPORT
        assert room.score_basis_direction is assessment.market_state.direction
        expected = (
            ExplanationCode.POSITIVE_ROOM_AVAILABLE
            if assessment.market_state.direction is BaselineDirection.POSITIVE
            else ExplanationCode.NEGATIVE_ROOM_AVAILABLE
        )
        assert expected in room.score_explanation_codes
        assert {
            ExplanationCode.POSITIVE_ROOM_AVAILABLE,
            ExplanationCode.NEGATIVE_ROOM_AVAILABLE,
        } <= set(room.explanation_codes)


def test_optional_derivatives_affect_feasibility_without_direction_oracle() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    without = BaselineEngine((policy,)).assess(baseline_request(policy))
    with_chain = BaselineEngine((policy,)).assess(
        baseline_request(policy, include_derivatives=True)
    )
    component = next(
        item
        for item in with_chain.market_state.components
        if item.component is ComponentName.DERIVATIVES_CONTEXT
    )
    assert component.available and component.positive_score is None
    assert with_chain.market_state.direction is without.market_state.direction


def test_multi_timeframe_alignment_retains_factual_contributors() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    assessment = BaselineEngine((policy,)).assess(baseline_request(policy, include_mtf=True))
    component = next(
        item
        for item in assessment.market_state.components
        if item.component is ComponentName.MULTI_TIMEFRAME_ALIGNMENT
    )
    assert component.available
    assert component.positive_score is not None
    assert len(component.contributions) == 4
    assert ExplanationCode.MTF_ALIGNED in component.score_explanation_codes
    assert ExplanationCode.MTF_POSITIVE_EVIDENCE in component.explanation_codes
    assert component.contributions[0].metadata["contributing_intervals"] == ["1d"]


def test_mtf_reason_uses_policy_alignment_and_conflict_thresholds() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    engine = BaselineEngine((policy,))
    mixed_values = values_for("positive")
    mixed_values.update(
        {
            "mtf.positive": 0.34,
            "mtf.negative": 0.0,
            "mtf.agreement": 0.34,
            "mtf.disagreement": 0.66,
        }
    )
    mixed = engine.assess(
        baseline_request(policy, include_mtf=True, values=mixed_values)
    )
    mixed_component = next(
        item
        for item in mixed.market_state.components
        if item.component is ComponentName.MULTI_TIMEFRAME_ALIGNMENT
    )
    assert mixed_component.score is not None
    assert mixed_component.score < policy.classification_thresholds.minimum_alignment
    assert mixed_component.score_explanation_codes == (ExplanationCode.MTF_MIXED,)

    conflict_values = values_for("positive")
    conflict_values.update({"mtf.positive": 0.8, "mtf.negative": 0.8})
    conflicted = engine.assess(
        baseline_request(policy, include_mtf=True, values=conflict_values)
    )
    conflict_component = next(
        item
        for item in conflicted.market_state.components
        if item.component is ComponentName.MULTI_TIMEFRAME_ALIGNMENT
    )
    assert conflict_component.positive_score is not None
    assert conflict_component.negative_score is not None
    assert conflict_component.score_explanation_codes == (ExplanationCode.MTF_CONFLICTED,)


def test_component_score_basis_prevents_negative_momentum_display_contradiction() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    assessment = BaselineEngine((policy,)).assess(
        baseline_request(policy, profile="negative")
    )
    momentum = next(
        item
        for item in assessment.market_state.components
        if item.component is ComponentName.MOMENTUM
    )
    assert momentum.score_basis_direction is BaselineDirection.NEGATIVE
    assert momentum.score == momentum.negative_score
    assert ExplanationCode.NEGATIVE_MOMENTUM in momentum.score_explanation_codes
    rendered = summarize_assessment(assessment)
    assert "NEGATIVE; positive=" in rendered
    assert "Score Reasons               : NEGATIVE_MOMENTUM" in rendered


def test_relative_outperformance_can_have_zero_dominant_side_support() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    values = values_for("negative")
    values.update({"relative.spread": 4.0, "relative.consistency": 0.75})
    assessment = BaselineEngine((policy,)).assess(
        baseline_request(policy, values=values)
    )
    relative = next(
        item
        for item in assessment.market_state.components
        if item.component is ComponentName.RELATIVE_STRENGTH
    )
    assert assessment.market_state.negative_direction_score > (
        assessment.market_state.positive_direction_score
    )
    assert relative.score_basis_direction is BaselineDirection.NEGATIVE
    assert relative.score == 0.0
    assert relative.positive_score is not None and relative.positive_score > 0.0
    assert relative.negative_score == 0.0
    assert relative.score_explanation_codes == ()
    assert ExplanationCode.RELATIVE_OUTPERFORMANCE in relative.explanation_codes


def test_indicators_are_bounded_supporting_evidence_not_oracles() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    engine = BaselineEngine((policy,))
    without = engine.assess(baseline_request(policy))
    with_indicators = engine.assess(baseline_request(policy, include_indicators=True))
    trend = next(
        item
        for item in with_indicators.market_state.components
        if item.component is ComponentName.TREND_QUALITY
    )
    assert {item.source.value for item in trend.contributions} >= {"PRIMARY", "INDICATOR"}
    assert with_indicators.market_state.direction is without.market_state.direction


def test_all_four_candidate_classes_have_explicit_fixtures() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    engine = BaselineEngine((policy,))
    early = engine.assess(baseline_request(policy))
    no_trade = engine.assess(baseline_request(policy, profile="neutral"))
    mature_values = values_for("positive")
    mature_values.update(
        {
            "momentum.return_20": 30.0,
            "extension.ema": 6.0,
            "extension.range": 5.0,
        }
    )
    mature = engine.assess(baseline_request(policy, values=mature_values))
    top_values = values_for("positive")
    top_values.update(
        {
            "momentum.return_5": 20.0,
            "momentum.return_20": 30.0,
            "participation.balance": 1.0,
            "participation.relative_volume": 3.0,
            "extension.ema": 0.1,
            "extension.range": 1.0,
        }
    )
    top = engine.assess(baseline_request(policy, values=top_values))
    assert (
        early.candidate_class,
        top.candidate_class,
        mature.candidate_class,
        no_trade.candidate_class,
    ) == (
        CandidateClass.EARLY_OPPORTUNITY,
        CandidateClass.TOP_MOVER,
        CandidateClass.MATURE_AVOID_CHASE,
        CandidateClass.NO_TRADE,
    )


def test_early_opportunity_threshold_is_inclusive() -> None:
    base_policy = default_policy(TradeStyle.POSITIONAL)
    engine = BaselineEngine((base_policy,))
    score = engine.assess(baseline_request(base_policy)).opportunity_score
    exact_thresholds = base_policy.classification_thresholds.model_copy(
        update={"early_opportunity_score": score}
    )
    exact_policy = base_policy.model_copy(update={"classification_thresholds": exact_thresholds})
    above_thresholds = exact_thresholds.model_copy(
        update={"early_opportunity_score": score + 0.000001}
    )
    above_policy = base_policy.model_copy(update={"classification_thresholds": above_thresholds})
    assert (
        BaselineEngine((exact_policy,)).assess(baseline_request(exact_policy)).candidate_class
        is CandidateClass.EARLY_OPPORTUNITY
    )
    assert (
        BaselineEngine((above_policy,)).assess(baseline_request(above_policy)).candidate_class
        is CandidateClass.NO_TRADE
    )


def test_top_mover_is_not_forced_to_have_best_opportunity_score() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    top_values = values_for("positive")
    top_values.update(
        {
            "momentum.return_5": 20.0,
            "momentum.return_20": 30.0,
            "participation.balance": 1.0,
            "participation.relative_volume": 3.0,
            "extension.ema": 1.9,
            "extension.range": 1.0,
        }
    )
    early_values = values_for("positive")
    early_values.update(
        {"extension.ema": 0.1, "momentum.return_20": 1.0, "extension.range": 1.0}
    )
    engine = BaselineEngine((policy,))
    top = engine.assess(baseline_request(policy, values=top_values))
    early = engine.assess(baseline_request(policy, values=early_values))
    assert top.candidate_class is CandidateClass.TOP_MOVER
    assert early.candidate_class is CandidateClass.EARLY_OPPORTUNITY
    assert early.opportunity_score > top.opportunity_score


def test_twenty_bar_return_is_one_fact_with_two_explicit_policy_roles() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    momentum_rule = next(
        item for item in policy.evidence_rules if item.rule_id == "momentum.return_20"
    )
    extension_rule = next(
        item for item in policy.evidence_rules if item.rule_id == "extension.return"
    )
    assert momentum_rule.selector == extension_rule.selector
    request = baseline_request(policy)
    matches = tuple(
        item
        for item in request.primary_features.results
        if item.request.feature_id == "return.percent"
        and item.request.parameters == (("bars", 20),)
    )
    assert len(matches) == 1
