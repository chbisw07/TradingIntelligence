"""Pure captured-input qualification; no acquisition, labeling or inference."""

from datetime import datetime

from tiaf.data.models import OHLCVBar
from tiaf.evaluation.forecast_contracts import (
    EvidenceReference,
    ForecastWindow,
    QualifiedCloseObservation,
)

from .enums import (
    DataBasis,
    ForecastRealizationMode,
    ForecastReason,
    KnowledgeBasis,
    QualificationStatus,
)
from .errors import ForecastAdmissionError
from .identity import semantic_fingerprint


def window_evidence(window: ForecastWindow) -> tuple[EvidenceReference, ...]:
    return (
        window.schedule.source,
        *window.schedule.exception_notice_refs,
        window.reference.source,
        window.reference.action_coverage_ref,
    )


def validate_knowledge(
    evidence: tuple[EvidenceReference, ...],
    cutoff: datetime,
    mode: ForecastRealizationMode,
    basis: KnowledgeBasis,
) -> None:
    """Validate supplied knowledge clocks, not authenticity of their assertions."""
    if cutoff.tzinfo is None or cutoff.utcoffset() is None:
        raise ValueError("cutoff must be timezone-aware")
    if not isinstance(mode, ForecastRealizationMode) or not isinstance(basis, KnowledgeBasis):
        raise ValueError("knowledge validation requires typed mode and basis")
    if mode is ForecastRealizationMode.ACTUAL_ISSUANCE and basis is not (
        KnowledgeBasis.CAPTURED_AS_KNOWN
    ):
        raise ForecastAdmissionError(ForecastReason.KNOWLEDGE_CUTOFF_VIOLATION)
    for source in evidence:
        source = EvidenceReference.model_validate(source)
        if source.data_basis is not DataBasis.SYNTHETIC_FIXTURE:
            raise ForecastAdmissionError(ForecastReason.EMPIRICAL_PROFILE_NOT_ENABLED)
        if source.available_at > cutoff:
            raise ForecastAdmissionError(ForecastReason.KNOWLEDGE_CUTOFF_VIOLATION)
        if basis is KnowledgeBasis.CAPTURED_AS_KNOWN and source.admitted_at > cutoff:
            raise ForecastAdmissionError(ForecastReason.KNOWLEDGE_CUTOFF_VIOLATION)


def validate_required_evidence(window: ForecastWindow) -> None:
    """Required absence never becomes a generated estimate or an invented price."""
    window = ForecastWindow.model_validate(window)
    schedule, close = window.schedule, window.reference
    if not schedule.complete or schedule.qualification is not QualificationStatus.QUALIFIED:
        raise ForecastAdmissionError(ForecastReason.CALENDAR_UNQUALIFIED)
    sessions = {session.session_id: session for session in schedule.sessions}
    if not all(
        sessions[key].subject_eligible for key in (close.session_id, window.target_session_id)
    ):
        raise ForecastAdmissionError(ForecastReason.SCOPE_UNSUPPORTED)
    if close.qualification is QualificationStatus.STALE:
        raise ForecastAdmissionError(ForecastReason.EVIDENCE_STALE)
    if close.value is None:
        raise ForecastAdmissionError(ForecastReason.EVIDENCE_MISSING)
    if close.qualification is not QualificationStatus.QUALIFIED:
        raise ForecastAdmissionError(ForecastReason.EVIDENCE_UNQUALIFIED)
    if close.action_coverage == "UNKNOWN":
        raise ForecastAdmissionError(ForecastReason.ACTION_COVERAGE_UNKNOWN)
    if close.action_coverage == "AFFECTED":
        raise ForecastAdmissionError(ForecastReason.ACTION_AFFECTED)


def validate_reference_bar(close: QualifiedCloseObservation, bar: OHLCVBar) -> None:
    """Check companion/bar correspondence, not source authority or exact float precision."""
    close = QualifiedCloseObservation.model_validate(close)
    bar = OHLCVBar.model_validate(bar.model_dump(mode="python"))
    if (
        close.value is None
        or bar.instrument != close.subject
        or bar.interval != "1d"
        or bar.end_at != close.observed_at
        or float(close.value) != bar.close
        or close.bar_ref.fingerprint != semantic_fingerprint(bar)
    ):
        raise ForecastAdmissionError(ForecastReason.EVIDENCE_UNQUALIFIED)
