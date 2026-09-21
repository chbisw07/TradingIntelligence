"""Independent deterministic endpoint labeler; no forecast, store or execution imports."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from tiaf.forecasting.enums import QualificationStatus
from tiaf.forecasting.identity import ArtifactReference, CapturedBlobReference

from .forecast_contracts import (
    EvidenceReference,
    ForecastTargetSpec,
    ForecastWindow,
    OutcomeJournalEntry,
    QualifiedCloseObservation,
)


def endpoint_direction(reference: Decimal, terminal: Decimal) -> Literal[0, 1]:
    """Shared target arithmetic; callers own basis, clock and evidence qualification."""
    if not reference.is_finite() or not terminal.is_finite() or min(reference, terminal) <= 0:
        raise ValueError("INVALID_DIRECTION_ENDPOINT")
    return 1 if terminal > reference else 0


def resolve_outcome(
    *,
    entry_id: str,
    target: ForecastTargetSpec,
    window: ForecastWindow,
    terminal: QualifiedCloseObservation | None,
    check_evidence: tuple[EvidenceReference, ...],
    evaluated_at: datetime,
    recorded_at: datetime,
    closure: tuple[CapturedBlobReference, ...],
    revision: int = 0,
    predecessor: ArtifactReference | None = None,
    revision_reason: str | None = None,
    invalidation: str = "NONE",
    invalidation_evidence: tuple[EvidenceReference, ...] = (),
) -> OutcomeJournalEntry:
    """Label supplied qualified facts once; missingness is not a negative outcome."""
    target = ForecastTargetSpec.model_validate(target)
    window = ForecastWindow.model_validate(window)
    terminal = None if terminal is None else QualifiedCloseObservation.model_validate(terminal)
    reference = window.reference
    sources = (
        window.schedule.source,
        *window.schedule.exception_notice_refs,
        reference.source,
        reference.action_coverage_ref,
        *check_evidence,
        *invalidation_evidence,
    )
    if terminal is not None:
        sources += (terminal.source, terminal.action_coverage_ref)
    available = max(source.admitted_at for source in sources)
    if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
        raise ValueError("EVALUATION_TIME_MUST_BE_AWARE")
    closed = evaluated_at >= window.target_resolve_time
    state = "CLOSED" if closed else "OPEN"
    observation, eligibility, reason = "MISSING", "PENDING", "truth:missing-terminal"
    label: int | None = None
    ambiguous = invalidation != "NONE" or any(
        close.action_coverage == "UNKNOWN" or close.qualification is QualificationStatus.AMBIGUOUS
        for close in (reference, terminal)
        if close is not None
    )
    invalid = (
        not window.schedule.complete
        or window.schedule.qualification is not QualificationStatus.QUALIFIED
        or not all(
            s.subject_eligible
            for s in window.schedule.sessions
            if s.session_id in (reference.session_id, window.target_session_id)
        )
        or reference.value is None
        or reference.qualification is not QualificationStatus.QUALIFIED
        or any(
            (
                close.qualification is not QualificationStatus.QUALIFIED
                and not (
                    close is terminal
                    and close.value is None
                    and close.qualification is QualificationStatus.MISSING
                )
            )
            or close.action_coverage == "AFFECTED"
            for close in (reference, terminal)
            if close is not None
        )
    )
    if ambiguous:
        state, observation, eligibility, reason = (
            "UNOBSERVABLE",
            "UNQUALIFIED",
            "AMBIGUOUS",
            "truth:ambiguous-source-or-window",
        )
    elif invalid:
        state, observation, eligibility, reason = (
            "UNOBSERVABLE",
            "UNQUALIFIED",
            "INELIGIBLE",
            "truth:unqualified-endpoint",
        )
    elif terminal is None or terminal.value is None:
        if evaluated_at >= window.outcome_due_at:
            state, eligibility, reason = "CENSORED", "INELIGIBLE", "truth:missing-after-deadline"
    elif closed:
        assert reference.value is not None
        label = endpoint_direction(reference.value, terminal.value)
        state, observation, eligibility, reason = (
            "CLOSED",
            "COMPLETE",
            "ELIGIBLE",
            "truth:qualified-endpoint",
        )
    return OutcomeJournalEntry.model_validate(
        {
            "entry_id": entry_id,
            "target": target,
            "window": window,
            "terminal": terminal,
            "check_evidence": check_evidence,
            "invalidation": invalidation,
            "invalidation_evidence": invalidation_evidence,
            "evaluated_at": evaluated_at,
            "recorded_at": recorded_at,
            "qualification_available_at": available,
            "outcome_event_time": terminal.observed_at if label is not None and terminal else None,
            "label_available_at": available if label is not None else None,
            "window_state": state,
            "observation_state": observation,
            "label_eligibility": eligibility,
            "label": label,
            "reasons": (reason,),
            "revision": revision,
            "predecessor": predecessor,
            "revision_reason": revision_reason,
            "closure": closure,
        }
    )
