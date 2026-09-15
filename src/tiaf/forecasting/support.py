"""Pinned synthetic count witnesses and bounded pre-forecaster qualification.

No Outcome Journal query, current-target observation, fit or source acquisition.
"""

from typing import Annotated, Literal, Self

from pydantic import Field, StrictBool, StrictInt, model_validator

from tiaf.data.models import OHLCVBar
from tiaf.evaluation.forecast_contracts import (
    EvidenceReference,
    ForecastTargetSpec,
    QualifiedCloseObservation,
    QualifiedSessionSchedule,
)
from tiaf.planner.models import Sha256

from .capture import CapturedArtifact, strict_json
from .contracts import ForecastArtifactIdentity, ForecastRequest
from .enums import DataBasis, ForecastReason, QualificationStatus
from .errors import ForecastAdmissionError, ForecastIntegrityError
from .evidence import validate_knowledge, validate_reference_bar
from .execution import Count, SupportSummary
from .identity import (
    ArtifactReference,
    ForecastContract,
    ForecastDateTime,
    LogicalId,
    semantic_fingerprint,
)


class BaseRatePolicy(ForecastContract):
    schema_id: Literal["tiaf.ff.baserate-policy"] = "tiaf.ff.baserate-policy"
    window_transitions: Annotated[StrictInt, Field(ge=20, le=20)] = 20
    minimum_support: Annotated[StrictInt, Field(ge=20, le=20)] = 20
    selection: Literal["LAST_SCHEDULED_TRANSITIONS_AT_FIT_CUTOFF"] = (
        "LAST_SCHEDULED_TRANSITIONS_AT_FIT_CUTOFF"
    )
    replacement: Literal["NO_BACKFILL"] = "NO_BACKFILL"
    estimate: Literal["UNSMOOTHED_K_OVER_N"] = "UNSMOOTHED_K_OVER_N"


class HistoricalTransition(ForecastContract):
    reference_session_id: LogicalId
    terminal_session_id: LogicalId
    reference: QualifiedCloseObservation | None
    terminal: QualifiedCloseObservation | None
    label: Annotated[StrictInt, Field(ge=0, le=1)] | None
    label_source: EvidenceReference
    label_available_at: ForecastDateTime | None
    label_revision: Annotated[StrictInt, Field(ge=0)] = 0
    included: StrictBool
    exclusion_reasons: tuple[LogicalId, ...] = ()

    @property
    def sources(self) -> tuple[EvidenceReference, ...]:
        return (
            self.label_source,
            *(
                source
                for close in (self.reference, self.terminal)
                if close is not None
                for source in (close.source, close.action_coverage_ref)
            ),
        )

    @model_validator(mode="after")
    def row_identity(self) -> Self:
        for session, close in (
            (self.reference_session_id, self.reference),
            (self.terminal_session_id, self.terminal),
        ):
            if close is not None and close.session_id != session:
                raise ValueError("SUPPORT_CLOSE_SESSION_MISMATCH")
        if self.included == bool(self.exclusion_reasons):
            raise ValueError("SUPPORT_EXCLUSION_REQUIRES_REASON")
        if (self.label is None) != (self.label_available_at is None):
            raise ValueError("SUPPORT_LABEL_AVAILABILITY_MISMATCH")
        if self.label_available_at is not None and (
            self.label_source.available_at != self.label_available_at
            or any(source.available_at > self.label_available_at for source in self.sources)
        ):
            raise ValueError("SUPPORT_LABEL_PREDATES_REQUIRED_FACTS")
        if self.label is not None:
            if self.reference is None or self.terminal is None:
                raise ValueError("SUPPORT_LABEL_REQUIRES_ENDPOINTS")
            left, right = self.reference.value, self.terminal.value
            if left is None or right is None or self.label != int(right > left):
                raise ValueError("SUPPORT_LABEL_PRICE_MISMATCH")
        return self


class BaseRateArtifact(ForecastContract):
    """Authored counts plus complete ordered window; immutable, never fitted on a request."""

    schema_id: Literal["tiaf.ff.baserate-artifact"] = "tiaf.ff.baserate-artifact"
    artifact_id: LogicalId
    target: ForecastTargetSpec
    forecaster_id: Literal["forecaster:historical-base-rate"] = "forecaster:historical-base-rate"
    implementation_version: Literal["1.0"] = "1.0"
    configuration_ref: ArtifactReference
    code_ref: ArtifactReference
    schedule: QualifiedSessionSchedule
    selection_evidence: tuple[EvidenceReference, ...] = Field(min_length=1)
    fit_knowledge_cutoff: ForecastDateTime
    prepared_at: ForecastDateTime
    rows: tuple[HistoricalTransition, ...] = Field(min_length=20, max_length=20)
    positive_count: Count
    eligible_count: Count
    data_basis: Literal["SYNTHETIC_FIXTURE"] = "SYNTHETIC_FIXTURE"

    @property
    def reference(self) -> ArtifactReference:
        return ArtifactReference(
            artifact_id=self.artifact_id,
            artifact_version="1.0",
            fingerprint=semantic_fingerprint(self),
        )

    @property
    def fit_evidence(self) -> tuple[EvidenceReference, ...]:
        items = (
            self.schedule.source,
            *self.schedule.exception_notice_refs,
            *self.selection_evidence,
            *(source for row in self.rows if row.included for source in row.sources),
        )
        return tuple(sorted(set(items), key=lambda item: item.artifact.artifact_id))

    @property
    def identity(self) -> ForecastArtifactIdentity:
        return ForecastArtifactIdentity(
            artifact=self.reference,
            configuration_ref=self.configuration_ref,
            code_ref=self.code_ref,
            fit_knowledge_cutoff=self.fit_knowledge_cutoff,
            prepared_at=self.prepared_at,
            fit_evidence=self.fit_evidence,
        )

    @model_validator(mode="after")
    def witness(self) -> Self:
        schedule = self.schedule
        if not schedule.complete or schedule.qualification is not QualificationStatus.QUALIFIED:
            raise ValueError("SUPPORT_CALENDAR_UNQUALIFIED")
        known = [s for s in schedule.sessions if s.closes_at <= self.fit_knowledge_cutoff]
        if len(known) < 21:
            raise ValueError("SUPPORT_WINDOW_SCHEDULE_MISSING")
        selected = known[-21:]
        expected = [(a.session_id, b.session_id) for a, b in zip(selected, selected[1:])]
        if [(r.reference_session_id, r.terminal_session_id) for r in self.rows] != expected:
            raise ValueError("SUPPORT_WINDOW_NOT_LAST_TWENTY_ADJACENT")
        sessions = {s.session_id: s for s in selected}
        versions: dict[str, QualifiedCloseObservation] = {}
        for row in self.rows:
            for close in (row.reference, row.terminal):
                if close is not None and (
                    close.subject != self.target.subject
                    or close.observed_at != sessions[close.session_id].closes_at
                ):
                    raise ValueError("SUPPORT_ENDPOINT_IDENTITY_MISMATCH")
                if close is not None:
                    old = versions.get(close.session_id)
                    if old is not None and old != close:
                        raise ValueError("SUPPORT_INCONSISTENT_SHARED_CLOSE")
                    versions[close.session_id] = close
            eligible = (
                row.label is not None
                and row.label_available_at is not None
                and row.label_available_at <= self.fit_knowledge_cutoff
                and all(
                    sessions[key].subject_eligible
                    for key in (row.reference_session_id, row.terminal_session_id)
                )
                and all(
                    close is not None
                    and close.qualification is QualificationStatus.QUALIFIED
                    and close.action_coverage == "UNAFFECTED"
                    for close in (row.reference, row.terminal)
                )
                and all(s.available_at <= self.fit_knowledge_cutoff for s in row.sources)
            )
            if row.included != eligible:
                raise ValueError("SUPPORT_ELIGIBILITY_WITNESS_MISMATCH")
        if self.eligible_count != sum(r.included for r in self.rows) or self.positive_count != sum(
            r.label == 1 for r in self.rows if r.included
        ):
            raise ValueError("SUPPORT_COUNT_WITNESS_MISMATCH")
        sources = (*self.fit_evidence, *(s for row in self.rows for s in row.sources))
        if any(s.data_basis is not DataBasis.SYNTHETIC_FIXTURE for s in sources):
            raise ValueError("EMPIRICAL_SUPPORT_NOT_ENABLED")
        if any(s.admitted_at > self.prepared_at for s in sources):
            raise ValueError("SUPPORT_ARTIFACT_PREDATES_CAPTURE")
        self.identity  # Validate fit/preparation clocks without changing the artifact.
        return self


class AdmittedSupport(ForecastContract):
    """Only eligible historical label refs/counts reach the primitive, never journal access."""

    request_fingerprint: Sha256
    summary: SupportSummary


def validate_support_bars(artifact: BaseRateArtifact, blobs: tuple[CapturedArtifact, ...]) -> None:
    by_ref = {blob.reference: blob for blob in blobs}
    for row in artifact.rows:
        for close in (row.reference, row.terminal):
            if close is None or close.qualification is not QualificationStatus.QUALIFIED:
                continue
            if close.bar_ref not in by_ref:
                raise ForecastIntegrityError("SUPPORT_BAR_MISSING")
            try:
                bar = OHLCVBar.model_validate(strict_json(by_ref[close.bar_ref].content_json))
                validate_reference_bar(close, bar)
            except ValueError:
                raise ForecastIntegrityError("SUPPORT_BAR_MISMATCH") from None


def admit_support(artifact: BaseRateArtifact, request: ForecastRequest) -> AdmittedSupport:
    artifact = BaseRateArtifact.model_validate(artifact)
    request = ForecastRequest.model_validate(request)
    if artifact.target != request.target:
        raise ForecastAdmissionError(ForecastReason.SCOPE_UNSUPPORTED)
    if artifact.fit_knowledge_cutoff > request.information_cutoff:
        raise ForecastAdmissionError(ForecastReason.KNOWLEDGE_CUTOFF_VIOLATION)
    if any(
        row.terminal is not None and row.terminal.observed_at >= request.window.target_open_time
        for row in artifact.rows
    ):
        raise ForecastAdmissionError(ForecastReason.KNOWLEDGE_CUTOFF_VIOLATION)
    if any(s.available_at >= request.information_cutoff for s in artifact.fit_evidence):
        raise ForecastAdmissionError(ForecastReason.KNOWLEDGE_CUTOFF_VIOLATION)
    validate_knowledge(
        artifact.fit_evidence,
        artifact.fit_knowledge_cutoff,
        request.realization_mode,
        request.knowledge_basis,
    )
    return AdmittedSupport(
        request_fingerprint=request.semantic_fingerprint,
        summary=SupportSummary(
            artifact_ref=artifact.reference,
            positive_count=artifact.positive_count,
            qualified_count=artifact.eligible_count,
            outcome_refs=tuple(row.label_source.artifact for row in artifact.rows if row.included),
        ),
    )
