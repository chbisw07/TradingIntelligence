"""Exact Evaluation-owned joins over immutable captures, never generation or truth writes."""

from datetime import datetime

from tiaf.forecasting.capture import ForecastCapture
from tiaf.forecasting.enums import ForecastStatus
from tiaf.forecasting.errors import ForecastIntegrityError

from .forecast_contracts import EvaluationLink, OutcomeJournalEntry, outcome_key


def link_forecast_outcome(
    capture: ForecastCapture, outcome: OutcomeJournalEntry, *, created_at: datetime
) -> EvaluationLink:
    capture = ForecastCapture.model_validate(capture)
    outcome = OutcomeJournalEntry.model_validate(outcome)
    request = capture.result.request
    if (
        request.target != outcome.target
        or outcome_key(request.target, request.window) != outcome.key
    ):
        raise ForecastIntegrityError("LINK_TARGET_SUBJECT_WINDOW_MISMATCH")
    if request.window != outcome.window:
        raise ForecastIntegrityError("LINK_REFERENCE_SCHEDULE_POLICY_MISMATCH")
    if created_at.tzinfo is None or created_at.utcoffset() is None:
        raise ValueError("LINK_TIME_MUST_BE_AWARE")
    if created_at < max(capture.recorded_at, outcome.recorded_at):
        raise ForecastIntegrityError("LINK_PREDATES_PINNED_RECORDS")
    reasons: list[str] = []
    if capture.result.status is not ForecastStatus.GENERATED:
        reasons.append("link:forecast-absent")
    if outcome.label_eligibility != "ELIGIBLE":
        reasons.append("link:label-not-eligible")
    return EvaluationLink.model_validate(
        {
            "capture_ref": capture.reference,
            "run_id": capture.result.run_id,
            "result_id": capture.result.result_id,
            "observation_id": request.observation_id,
            "outcome_key": outcome.key,
            "outcome_ref": outcome.reference,
            "realization_mode": request.realization_mode,
            "created_at": created_at,
            "eligibility": "NOT_EVALUABLE" if reasons else "ENGINEERING_LINK_ELIGIBLE",
            "reasons": tuple(reasons) if reasons else ("link:synthetic-inspection-only",),
        }
    )
