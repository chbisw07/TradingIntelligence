"""Lossless scalar projections from accepted A2 contracts into an A3 evidence pack."""

import hashlib
import json

from tiaf.agents.evidence import (
    EvidenceFact,
    EvidenceFactKind,
    EvidenceFactParameter,
)
from tiaf.baseline.models import OpportunityAssessment
from tiaf.contracts import FreshnessState
from tiaf.features.enums import FeatureStatus
from tiaf.features.models import FeatureResult
from tiaf.features.multi_timeframe import MultiTimeframeContext
from tiaf.indicators.models import IndicatorResult


def feature_fact(
    result: FeatureResult,
    *,
    freshness: FreshnessState,
    fact_id: str | None = None,
) -> EvidenceFact:
    """Project one already-computed scalar A2 feature without recalculating it."""
    if result.status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
        raise ValueError("only usable A2 feature results can become evidence facts")
    value = result.value
    if value is None or isinstance(value, tuple):
        raise ValueError("A3 technical evidence facts require scalar A2 feature values")
    identity = json.dumps(
        {
            "interval": result.request.interval,
            "parameters": result.request.parameters,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    identity_digest = hashlib.sha256(identity.encode()).hexdigest()[:16]
    return EvidenceFact(
        fact_id=fact_id
        or (
            f"feature:{result.source_context_id}:{result.request.feature_id}:"
            f"{identity_digest}"
        ),
        kind=EvidenceFactKind.FEATURE,
        metric_id=result.request.feature_id,
        value=value,
        unit=result.unit,
        parameters=tuple(
            EvidenceFactParameter(name=name, value=value)
            for name, value in result.request.parameters
        ),
        interval=result.request.interval,
        as_of=result.as_of,
        quality=result.quality,
        freshness=freshness,
        source_evidence=result.source_evidence,
    )


def indicator_facts(
    result: IndicatorResult,
    *,
    freshness: FreshnessState,
) -> tuple[EvidenceFact, ...]:
    """Project all supplied scalar outputs of one usable A2 indicator result."""
    if result.status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
        raise ValueError("only usable A2 indicator results can become evidence facts")
    return tuple(
        EvidenceFact(
            fact_id=f"indicator:{result.result_id}:{output.name}",
            kind=EvidenceFactKind.INDICATOR,
            metric_id=f"indicator.{result.indicator_id}",
            value=output.value,
            unit=output.unit,
            parameters=tuple(
                EvidenceFactParameter(name=name, value=value)
                for name, value in result.parameters
            ),
            output_name=output.name,
            interval=result.interval,
            as_of=result.as_of,
            quality=result.quality,
            freshness=freshness,
            source_evidence=result.source_evidence,
        )
        for output in result.values
    )


def multi_timeframe_constituent_facts(
    context: MultiTimeframeContext,
    *,
    freshness: FreshnessState,
) -> tuple[EvidenceFact, ...]:
    """Copy usable scalar A2 facts from each retained independent timeframe."""
    return tuple(
        feature_fact(result, freshness=freshness)
        for timeframe in context.timeframes
        if timeframe.feature_bundle is not None
        for result in timeframe.feature_bundle.results
        if result.status in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
        and result.value is not None
        and not isinstance(result.value, tuple)
    )


def baseline_facts(
    assessment: OpportunityAssessment,
    *,
    freshness: FreshnessState,
) -> tuple[EvidenceFact, ...]:
    """Project the accepted A2.9 result for comparison, never modification."""
    def project(suffix: str, metric_id: str, value: str | float) -> EvidenceFact:
        return EvidenceFact(
            fact_id=f"baseline:{assessment.assessment_id}:{suffix}",
            kind=EvidenceFactKind.BASELINE,
            metric_id=metric_id,
            value=value,
            interval=assessment.primary_timeframe,
            as_of=assessment.created_at,
            quality=assessment.market_state.quality,
            freshness=freshness,
            source_evidence=(assessment.assessment_id,),
        )

    return (
        project(
            "direction",
            "baseline.direction",
            assessment.market_state.direction.value,
        ),
        project(
            "opportunity-score",
            "baseline.opportunity_score",
            assessment.opportunity_score,
        ),
        project(
            "candidate-class",
            "baseline.candidate_class",
            assessment.candidate_class.value,
        ),
    )
