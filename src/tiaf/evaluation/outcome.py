"""Anti-lookahead attachment and factual excursion calculations."""

from datetime import datetime
from uuid import NAMESPACE_URL, uuid5

from tiaf.baseline import BaselineDirection, CandidateClass
from tiaf.contracts import DataQuality

from .errors import OutcomeEvaluationError
from .models import (
    BaselineOutcome,
    BaselineRunRecord,
    ExcursionMetrics,
    OutcomeObservation,
    OutcomePath,
    OutcomeWindow,
)
from .snapshot import canonical_json


def create_outcome_path(
    run: BaselineRunRecord,
    *,
    assessment_reference_price: float,
    window: OutcomeWindow,
    observations: tuple[OutcomeObservation, ...],
    quality: DataQuality,
    complete: bool,
    captured_at: datetime,
    warnings: tuple[str, ...] = (),
) -> OutcomePath:
    """Attach an explicit later price path without changing the original run."""
    if window.start_at < run.decision_at:
        raise OutcomeEvaluationError("outcome window cannot begin before decision time")
    semantic = {
        "run_id": run.run_id,
        "assessment_id": run.assessment.assessment_id,
        "evidence_fingerprint": run.evidence_fingerprint,
        "subject": run.subject,
        "assessment_reference_price": assessment_reference_price,
        "window": window.model_dump(mode="json"),
        "observations": [item.model_dump(mode="json") for item in observations],
        "quality": quality.value,
        "complete": complete,
        "warnings": list(warnings),
    }
    return OutcomePath(
        outcome_path_id=str(uuid5(NAMESPACE_URL, f"tiaf:outcome-path:{canonical_json(semantic)}")),
        run_id=run.run_id,
        assessment_id=run.assessment.assessment_id,
        evidence_fingerprint=run.evidence_fingerprint,
        subject=run.subject,
        assessment_reference_price=assessment_reference_price,
        window=window,
        observations=observations,
        quality=quality,
        complete=complete,
        captured_at=captured_at,
        warnings=warnings,
    )


def calculate_excursions(
    path: OutcomePath,
    *,
    direction: BaselineDirection,
    candidate_class: CandidateClass,
) -> ExcursionMetrics:
    """Calculate raw and direction-relative percentages without execution assumptions."""
    reference = path.assessment_reference_price
    ending = (path.observations[-1].close / reference - 1.0) * 100.0
    maximum_high = max(item.high for item in path.observations)
    minimum_low = min(item.low for item in path.observations)
    raw_upside = max(0.0, (maximum_high / reference - 1.0) * 100.0)
    raw_downside = min(0.0, (minimum_low / reference - 1.0) * 100.0)
    directional = (
        candidate_class is not CandidateClass.NO_TRADE
        and direction in {BaselineDirection.POSITIVE, BaselineDirection.NEGATIVE}
    )
    mfe: float | None = None
    mae: float | None = None
    if directional and direction is BaselineDirection.POSITIVE:
        mfe = raw_upside
        mae = raw_downside
    elif directional:
        mfe = -raw_downside
        mae = -raw_upside
    return ExcursionMetrics(
        ending_return_percent=ending,
        maximum_upside_excursion_percent=raw_upside,
        maximum_downside_excursion_percent=raw_downside,
        mfe_percent=mfe,
        mae_percent=mae,
        realized_range_percent=(maximum_high - minimum_low) / reference * 100.0,
        bars_observed=len(path.observations),
    )


def evaluate_outcome(
    run: BaselineRunRecord,
    path: OutcomePath,
    *,
    evaluated_at: datetime,
) -> BaselineOutcome:
    """Measure a later path while retaining original direction/class by reference."""
    if (
        path.run_id != run.run_id
        or path.assessment_id != run.assessment.assessment_id
        or path.evidence_fingerprint != run.evidence_fingerprint
        or path.subject != run.subject
    ):
        raise OutcomeEvaluationError("outcome path does not belong to baseline run")
    metrics = calculate_excursions(
        path,
        direction=run.direction,
        candidate_class=run.candidate_class,
    )
    identity = canonical_json(
        {
            "run_id": run.run_id,
            "outcome_path_id": path.outcome_path_id,
            "metrics": metrics.model_dump(mode="json"),
        }
    )
    return BaselineOutcome(
        baseline_outcome_id=str(uuid5(NAMESPACE_URL, f"tiaf:baseline-outcome:{identity}")),
        run_id=run.run_id,
        assessment_id=run.assessment.assessment_id,
        evidence_fingerprint=run.evidence_fingerprint,
        subject=run.subject,
        original_direction=run.direction,
        original_candidate_class=run.candidate_class,
        path=path,
        metrics=metrics,
        evaluated_at=evaluated_at,
    )
