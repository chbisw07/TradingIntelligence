"""A3.3 consumes accepted A2 result contracts through lossless scalar projections."""

from tiaf.agents import EvidenceFactKind
from tiaf.agents.specialists.technical import (
    baseline_facts,
    feature_fact,
    indicator_facts,
    multi_timeframe_constituent_facts,
)
from tiaf.baseline import BaselineEngine, default_policy
from tiaf.contracts import FreshnessState, TradeStyle
from unit.baseline._support import baseline_request


def test_accepted_a2_feature_and_indicator_results_project_without_recalculation() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    request = baseline_request(policy, include_indicators=True)
    feature_result = request.primary_features.results[0]
    assert request.indicators is not None
    indicator_result = request.indicators.results[0]

    projected_feature = feature_fact(
        feature_result,
        freshness=FreshnessState.FRESH,
    )
    projected_indicators = indicator_facts(
        indicator_result,
        freshness=FreshnessState.FRESH,
    )

    assert projected_feature.kind is EvidenceFactKind.FEATURE
    assert projected_feature.metric_id == feature_result.request.feature_id
    assert projected_feature.value == feature_result.value
    assert tuple(
        (item.name, item.value) for item in projected_feature.parameters
    ) == feature_result.request.parameters
    assert projected_indicators[0].kind is EvidenceFactKind.INDICATOR
    assert projected_indicators[0].metric_id == f"indicator.{indicator_result.indicator_id}"
    assert projected_indicators[0].value == indicator_result.values[0].value
    assert projected_indicators[0].output_name == indicator_result.values[0].name


def test_a2_baseline_projection_preserves_direction_score_and_class() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    request = baseline_request(policy)
    assessment = BaselineEngine().assess(request)

    projected = baseline_facts(assessment, freshness=FreshnessState.FRESH)
    values = {item.metric_id: item.value for item in projected}

    assert values == {
        "baseline.direction": assessment.market_state.direction.value,
        "baseline.opportunity_score": assessment.opportunity_score,
        "baseline.candidate_class": assessment.candidate_class.value,
    }
    assert all(item.source_evidence == (assessment.assessment_id,) for item in projected)


def test_a2_mtf_projection_preserves_retained_constituent_intervals() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    request = baseline_request(policy, include_mtf=True)
    assert request.multi_timeframe_context is not None

    projected = multi_timeframe_constituent_facts(
        request.multi_timeframe_context,
        freshness=FreshnessState.FRESH,
    )

    assert projected
    assert {item.interval for item in projected} == {"1d"}
    assert all(item.value is not None for item in projected)
