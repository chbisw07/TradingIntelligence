"""Supplied FF-1 data qualification facts, independent of any learned model.

Unknown assertions stay representable. Qualification evaluates them; a hash
does not authenticate an entitlement, source, calendar or historical clock.
"""

from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal, Self
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BeforeValidator, Field, StrictBool, StrictInt, field_validator, model_validator

from tiaf.data.models import InstrumentKey
from tiaf.data.resolution.models import ResolutionResult
from tiaf.evaluation.forecast_contracts import (
    EvidenceReference,
    ForecastTargetSpec,
    ForecastWindow,
    QualifiedSessionSchedule,
)
from tiaf.forecasting.enums import DataBasis
from tiaf.forecasting.identity import (
    ArtifactReference,
    ForecastDateTime,
    LogicalId,
    exact_decimal,
    semantic_fingerprint,
)
from tiaf.forecasting.research_contracts import (
    FeatureVector,
    FF1FeatureSchema,
    ResearchContract,
    ResearchDate,
)
from tiaf.planner.models import Sha256


class QualificationState(StrEnum):
    QUALIFIED = "QUALIFIED"
    NOT_QUALIFIED = "NOT_QUALIFIED"
    UNKNOWN = "UNKNOWN"


class QualificationReason(StrEnum):
    RIGHTS_UNQUALIFIED = "RIGHTS_UNQUALIFIED"
    SECURITY_IDENTITY = "SECURITY_IDENTITY"
    CALENDAR_UNQUALIFIED = "CALENDAR_UNQUALIFIED"
    INVALID_SESSION = "INVALID_SESSION"
    MISSING_SESSION = "MISSING_SESSION"
    DUPLICATE_SESSION = "DUPLICATE_SESSION"
    CONFLICTING_DUPLICATE = "CONFLICTING_DUPLICATE"
    NON_CHRONOLOGICAL = "NON_CHRONOLOGICAL"
    INVALID_BAR = "INVALID_BAR"
    MISSING_VOLUME = "MISSING_VOLUME"
    INVALID_VOLUME = "INVALID_VOLUME"
    ZERO_VOLUME_BASELINE = "ZERO_VOLUME_BASELINE"
    CORPORATE_ACTION_UNRESOLVED = "CORPORATE_ACTION_UNRESOLVED"
    CORPORATE_ACTION_AFFECTED = "CORPORATE_ACTION_AFFECTED"
    PRICE_BASIS_UNSUPPORTED = "PRICE_BASIS_UNSUPPORTED"
    PROVENANCE_UNQUALIFIED = "PROVENANCE_UNQUALIFIED"
    KNOWLEDGE_CUTOFF_VIOLATION = "KNOWLEDGE_CUTOFF_VIOLATION"
    INSUFFICIENT_LOOKBACK = "INSUFFICIENT_LOOKBACK"
    TARGET_UNAVAILABLE = "TARGET_UNAVAILABLE"
    MATURATION_UNQUALIFIED = "MATURATION_UNQUALIFIED"
    FEATURE_UNAVAILABLE = "FEATURE_UNAVAILABLE"
    NO_ELIGIBLE_OBSERVATIONS = "NO_ELIGIBLE_OBSERVATIONS"


class DataRightsQualification(ResearchContract):
    record_id: LogicalId
    source_artifact: ArtifactReference
    subject: InstrumentKey
    coverage_start: ResearchDate
    coverage_end: ResearchDate
    local_research: QualificationState
    model_training: QualificationState
    derived_feature_storage: QualificationState
    evaluation_artifact_retention: QualificationState
    replay_evidence_retention: QualificationState
    basis_refs: tuple[ArtifactReference, ...] = ()
    assessed_at: ForecastDateTime
    valid_until: ForecastDateTime | None = None

    @property
    def reference(self) -> ArtifactReference:
        return ArtifactReference(
            artifact_id=self.record_id,
            artifact_version="2.0",
            fingerprint=semantic_fingerprint(self),
        )


class EmpiricalSourceIdentity(ResearchContract):
    source_id: LogicalId
    provider_id: LogicalId
    origin_id: LogicalId
    capture: ArtifactReference
    source_timezone: str
    data_basis: DataBasis
    rights_ref: ArtifactReference
    acquisition_at: ForecastDateTime | None = None
    provenance_ref: ArtifactReference | None = None

    @field_validator("source_timezone")
    @classmethod
    def known_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ValueError, ZoneInfoNotFoundError) as exc:
            raise ValueError("UNKNOWN_SOURCE_TIMEZONE") from exc
        return value


class SecurityIdentityQualification(ResearchContract):
    resolution: ResolutionResult
    valid_from: ResearchDate
    valid_through: ResearchDate
    state: QualificationState
    evidence: EvidenceReference | None = None


class SessionCalendarQualification(ResearchContract):
    """Bounded segments of the existing complete, versioned schedule contract."""

    schedules: tuple[QualifiedSessionSchedule, ...] = Field(min_length=1, max_length=128)
    state: QualificationState
    authority_refs: tuple[ArtifactReference, ...] = ()


class CorporateActionQualification(ResearchContract):
    subject: InstrumentKey
    from_session: ResearchDate
    through_session: ResearchDate
    basis: Literal["ADJUSTED", "UNADJUSTED", "UNKNOWN"]
    state: QualificationState
    coverage: Literal["UNAFFECTED", "AFFECTED", "UNKNOWN"]
    complete: StrictBool
    evidence: EvidenceReference | None = None


ExactSourceNumber = Annotated[Decimal, BeforeValidator(exact_decimal)]


class DailyBarInput(ResearchContract):
    """Prequalification decimal companion; invalid envelopes remain reportable.

    Once qualified this projects to the existing OHLCVBar, not a new candle API.
    Floats, bools, NaN and infinity reject at ingestion, never silently repaired.
    """

    row_id: LogicalId
    session_id: LogicalId
    session_date: ResearchDate
    instrument: InstrumentKey
    provider_security_id: str = Field(min_length=1, max_length=100)
    open: ExactSourceNumber | None
    high: ExactSourceNumber | None
    low: ExactSourceNumber | None
    close: ExactSourceNumber | None
    volume: StrictInt | None
    provenance: EvidenceReference | None = None
    final: StrictBool = True


class OutcomeMaturationInput(ResearchContract):
    """Supplied Evaluation policy/deadline; qualification never invents one."""

    target_session_id: LogicalId
    outcome_due_at: ForecastDateTime
    policy_ref: ArtifactReference
    evidence: EvidenceReference


class EmpiricalDataset(ResearchContract):
    schema_id: Literal["tiaf.ff1.supplied-dataset"] = "tiaf.ff1.supplied-dataset"
    dataset_id: LogicalId
    target: ForecastTargetSpec
    source: EmpiricalSourceIdentity
    rights: DataRightsQualification
    security: SecurityIdentityQualification
    calendar: SessionCalendarQualification
    actions: tuple[CorporateActionQualification, ...] = Field(max_length=8192)
    maturation: tuple[OutcomeMaturationInput, ...] = Field(default=(), max_length=8192)
    coverage_start: ResearchDate
    coverage_end: ResearchDate
    rows: tuple[DailyBarInput, ...] = Field(max_length=8192)
    reference_session_ids: tuple[LogicalId, ...] = Field(min_length=1, max_length=4096)

    @model_validator(mode="after")
    def bounded_identity(self) -> Self:
        if self.coverage_end < self.coverage_start:
            raise ValueError("DATASET_COVERAGE_REVERSED")
        if len(set(self.reference_session_ids)) != len(self.reference_session_ids):
            raise ValueError("DUPLICATE_REFERENCE_SLOT")
        if len({row.row_id for row in self.rows}) != len(self.rows):
            raise ValueError("DUPLICATE_ROW_ID")
        if len({m.target_session_id for m in self.maturation}) != len(self.maturation):
            raise ValueError("DUPLICATE_MATURATION_SLOT")
        return self

    @property
    def fingerprint(self) -> str:
        return semantic_fingerprint(self)


class DailyBarQualification(ResearchContract):
    row_id: LogicalId
    session_id: LogicalId
    reasons: tuple[QualificationReason, ...]


class ObservationEligibility(ResearchContract):
    target: ForecastTargetSpec
    slot_id: LogicalId
    reference_session_id: LogicalId
    window: ForecastWindow | None
    observation_id: LogicalId | None
    information_cutoff: ForecastDateTime | None
    as_of: ForecastDateTime | None
    computed_at: ForecastDateTime
    realization_mode: Literal["SIMULATED_ISSUANCE"] = "SIMULATED_ISSUANCE"
    feature_schema: FF1FeatureSchema
    raw_data_fingerprint: Sha256
    input_row_ids: tuple[LogicalId, ...]
    eligible: StrictBool
    reasons: tuple[QualificationReason, ...]
    features: FeatureVector | None
    label: None = None
    label_state: Literal["NOT_RESOLVED_FF1_1"] = "NOT_RESOLVED_FF1_1"

    @model_validator(mode="after")
    def eligibility(self) -> Self:
        if self.eligible != (not self.reasons) or self.eligible != (self.features is not None):
            raise ValueError("OBSERVATION_ELIGIBILITY_MISMATCH")
        if (self.window is None) != (self.observation_id is None):
            raise ValueError("OBSERVATION_WINDOW_ID_MISMATCH")
        if self.slot_id != "ff1-slot:" + semantic_fingerprint(
            (self.target, self.reference_session_id)
        ):
            raise ValueError("OBSERVATION_SLOT_MISMATCH")
        if self.eligible and self.window is None:
            raise ValueError("ELIGIBLE_WINDOW_REQUIRED")
        if self.window is not None:
            if (
                self.window.reference.subject != self.target.subject
                or self.window.reference.session_id != self.reference_session_id
                or self.information_cutoff is None
                or self.as_of is None
                or not self.window.reference.observed_at
                <= self.information_cutoff
                <= self.as_of
                < self.window.target_open_time
                or self.as_of > self.computed_at
                or self.observation_id
                != "ff-observation:"
                + semantic_fingerprint(
                    {
                        "target": self.target,
                        "window": self.window,
                        "information_cutoff": self.information_cutoff,
                        "as_of": self.as_of,
                    }
                )
            ):
                raise ValueError("OBSERVATION_IDENTITY_OR_CLOCK_MISMATCH")
        if self.features is not None and (
            self.features.feature_schema != self.feature_schema
            or self.features.input_fingerprint != self.raw_data_fingerprint
        ):
            raise ValueError("OBSERVATION_FEATURE_ID_MISMATCH")
        return self

    @property
    def fingerprint(self) -> str:
        """Includes feature schema, raw inputs, identity and eligibility; excludes run clock."""
        return semantic_fingerprint(self.model_dump(exclude={"computed_at"}))


class ReasonCount(ResearchContract):
    reason: QualificationReason
    count: Annotated[StrictInt, Field(ge=1)]


class EmpiricalDatasetQualification(ResearchContract):
    schema_id: Literal["tiaf.ff1.dataset-qualification"] = "tiaf.ff1.dataset-qualification"
    dataset_id: LogicalId
    dataset_fingerprint: Sha256
    data_basis: DataBasis
    policy: Literal["FF1_1_QUALIFICATION_1.0"] = "FF1_1_QUALIFICATION_1.0"
    assessed_at: ForecastDateTime
    feature_schema: FF1FeatureSchema
    rights_ref: ArtifactReference
    source_fingerprint: Sha256
    security_fingerprint: Sha256
    calendar_fingerprint: Sha256
    actions_fingerprint: Sha256
    bars: tuple[DailyBarQualification, ...]
    observations: tuple[ObservationEligibility, ...]
    reasons: tuple[QualificationReason, ...]
    verdicts: tuple[str, ...]
    requested_observations: Annotated[StrictInt, Field(ge=0)]
    eligible_observations: Annotated[StrictInt, Field(ge=0)]
    excluded_observations: Annotated[StrictInt, Field(ge=0)]
    reason_counts: tuple[ReasonCount, ...]
    empirical_fitting_authorized: Literal[False] = False
    authorization_reason: Literal["NO_LEARNING_GRANT_FF1_1"] = "NO_LEARNING_GRANT_FF1_1"
    fingerprint: Sha256 | None = None

    @property
    def feature_set_fingerprint(self) -> str:
        return semantic_fingerprint(
            {
                "schema": self.feature_schema,
                "observations": tuple(
                    {
                        "id": o.observation_id,
                        "slot": o.slot_id,
                        "input": o.raw_data_fingerprint,
                        "eligible": o.eligible,
                        "reasons": o.reasons,
                        "features": o.features,
                    }
                    for o in self.observations
                ),
            }
        )

    @model_validator(mode="after")
    def partition_and_seal(self) -> Self:
        if len({o.slot_id for o in self.observations}) != len(self.observations):
            raise ValueError("DUPLICATE_OBSERVATION_SLOT")
        eligible = sum(o.eligible for o in self.observations)
        if (
            self.requested_observations,
            self.eligible_observations,
            self.excluded_observations,
        ) != (len(self.observations), eligible, len(self.observations) - eligible):
            raise ValueError("QUALIFICATION_POPULATION_MISMATCH")
        expected = tuple(
            ReasonCount(reason=reason, count=count)
            for reason in QualificationReason
            if (count := sum(reason in o.reasons for o in self.observations))
        )
        if self.reason_counts != expected:
            raise ValueError("QUALIFICATION_REASON_COUNTS_MISMATCH")
        if self.verdicts != qualification_verdicts(self.reasons, self.data_basis):
            raise ValueError("QUALIFICATION_VERDICT_MISMATCH")
        if not eligible and QualificationReason.NO_ELIGIBLE_OBSERVATIONS not in self.reasons:
            raise ValueError("EMPTY_POPULATION_CANNOT_QUALIFY")
        if any(o.feature_schema != self.feature_schema for o in self.observations):
            raise ValueError("QUALIFICATION_SCHEMA_MISMATCH")
        required_reasons = {
            r
            for o in self.observations
            for r in o.reasons
            if r
            not in (
                QualificationReason.INSUFFICIENT_LOOKBACK,
                QualificationReason.TARGET_UNAVAILABLE,
            )
        } | {
            r
            for b in self.bars
            for r in b.reasons
            if r is not QualificationReason.DUPLICATE_SESSION
        }
        if not required_reasons.issubset(self.reasons):
            raise ValueError("QUALIFICATION_BLOCKING_REASONS_DROPPED")
        fingerprint = semantic_fingerprint(self.model_dump(exclude={"fingerprint"}))
        if self.fingerprint is not None and self.fingerprint != fingerprint:
            raise ValueError("QUALIFICATION_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", fingerprint)
        return self


def qualification_verdicts(
    reasons: tuple[QualificationReason, ...],
    basis: DataBasis,
) -> tuple[str, ...]:
    """Closed deterministic report vocabulary, including synthetic-only success."""
    r = QualificationReason
    if not reasons:
        return (
            "SYNTHETIC_ENGINEERING_ONLY"
            if basis is DataBasis.SYNTHETIC_FIXTURE
            else "QUALIFIED_FOR_FF1_RESEARCH",
        )
    groups = {
        "HOLD_DATA_RIGHTS": {r.RIGHTS_UNQUALIFIED},
        "HOLD_SECURITY_IDENTITY": {r.SECURITY_IDENTITY},
        "HOLD_CALENDAR": {r.CALENDAR_UNQUALIFIED, r.INVALID_SESSION},
        "HOLD_CORPORATE_ACTIONS": {
            r.CORPORATE_ACTION_UNRESOLVED,
            r.CORPORATE_ACTION_AFFECTED,
            r.PRICE_BASIS_UNSUPPORTED,
        },
        "HOLD_PIT_PROVENANCE": {r.PROVENANCE_UNQUALIFIED, r.KNOWLEDGE_CUTOFF_VIOLATION},
    }
    result = [name for name, values in groups.items() if values.intersection(reasons)]
    if set(reasons) - set().union(*groups.values()):
        result.append("HOLD_DATA_QUALITY")
    return tuple(result)
