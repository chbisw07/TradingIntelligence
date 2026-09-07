"""Descriptive corpus and frozen-ranking evaluation statistics."""

from collections import Counter
from datetime import datetime
from statistics import fmean
from uuid import NAMESPACE_URL, uuid5

from tiaf.baseline import BaselineDirection, CandidateClass, OpportunityRanking
from tiaf.contracts import DataQuality

from .errors import OutcomeEvaluationError
from .models import (
    BaselineOutcome,
    BaselineRunRecord,
    EvaluationMetrics,
    ExcursionMetrics,
    ObservedStatistics,
    RankingEvaluation,
    RankingOutcomeItem,
    RegressionCheckResult,
)
from .snapshot import canonical_json


def observed_statistics(metrics: tuple[ExcursionMetrics, ...]) -> ObservedStatistics:
    """Return arithmetic means over factual observations, omitting undefined MFE/MAE."""
    mfe = tuple(item.mfe_percent for item in metrics if item.mfe_percent is not None)
    mae = tuple(item.mae_percent for item in metrics if item.mae_percent is not None)
    return ObservedStatistics(
        count=len(metrics),
        average_ending_return_percent=(
            fmean(item.ending_return_percent for item in metrics) if metrics else None
        ),
        average_mfe_percent=fmean(mfe) if mfe else None,
        average_mae_percent=fmean(mae) if mae else None,
    )


def evaluate_ranking(
    ranking: OpportunityRanking,
    outcomes: tuple[BaselineOutcome, ...],
    *,
    evaluated_at: datetime,
) -> RankingEvaluation:
    """Associate outcomes with original ranks without recalculating eligibility or order."""
    by_assessment = {item.assessment_id: item for item in outcomes}
    expected = {item.assessment_id for item in ranking.assessments}
    if len(by_assessment) != len(outcomes) or set(by_assessment) != expected:
        raise OutcomeEvaluationError("ranking evaluation requires one outcome per assessment")
    rank_by_assessment = {item.assessment_id: item.rank for item in ranking.items}
    items = tuple(
        RankingOutcomeItem(
            subject=assessment.subject,
            assessment_id=assessment.assessment_id,
            original_rank=rank_by_assessment.get(assessment.assessment_id),
            original_candidate_class=assessment.candidate_class,
            originally_eligible=assessment.eligible,
            metrics=by_assessment[assessment.assessment_id].metrics,
        )
        for assessment in ranking.assessments
    )
    ranked = tuple(
        sorted(
            (item for item in items if item.original_rank),
            key=lambda item: item.original_rank or 0,
        )
    )
    requested = ranking.requested_top_n or len(ranked)
    top_n_items = ranked[:requested]
    eligible = tuple(item.metrics for item in items if item.originally_eligible)
    no_trade = tuple(item.metrics for item in items if not item.originally_eligible)
    identity = canonical_json(
        {
            "ranking_id": ranking.ranking_id,
            "outcomes": sorted(item.baseline_outcome_id for item in outcomes),
        }
    )
    return RankingEvaluation(
        ranking_evaluation_id=str(uuid5(NAMESPACE_URL, f"tiaf:ranking-evaluation:{identity}")),
        ranking_id=ranking.ranking_id,
        evidence_fingerprints=tuple(
            sorted(item.evidence_fingerprint for item in outcomes)
        ),
        items=items,
        top_1=observed_statistics(tuple(item.metrics for item in ranked[:1])),
        top_n=observed_statistics(tuple(item.metrics for item in top_n_items)),
        eligible_population=observed_statistics(eligible),
        no_trade_population=observed_statistics(no_trade),
        evaluated_at=evaluated_at,
    )


def aggregate_metrics(
    runs: tuple[BaselineRunRecord, ...],
    checks: tuple[RegressionCheckResult, ...],
    outcomes: tuple[BaselineOutcome, ...] = (),
) -> EvaluationMetrics:
    """Aggregate counts and raw observed averages; never calculate simulated returns."""
    directions = Counter(item.direction for item in runs)
    classes = Counter(item.candidate_class for item in runs)
    qualities = Counter(item.quality for item in runs)
    from .enums import RegressionStatus

    return EvaluationMetrics(
        runs_evaluated=len(runs),
        replay_pass_count=sum(item.status is RegressionStatus.PASS for item in checks),
        replay_fail_count=sum(item.status is RegressionStatus.FAIL for item in checks),
        direction_counts=tuple((item, directions[item]) for item in BaselineDirection),
        class_counts=tuple((item, classes[item]) for item in CandidateClass),
        quality_counts=tuple((item, qualities[item]) for item in DataQuality),
        observed_outcomes=observed_statistics(tuple(item.metrics for item in outcomes)),
    )
