"""Provider-neutral evidence references, claims, and missing-evidence contracts."""

import math
import re
from enum import StrEnum
from typing import Annotated, Self

from pydantic import (
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    field_validator,
    model_validator,
)

from tiaf.context import EvidenceStatus
from tiaf.contracts import (
    ContractModel,
    DataQuality,
    EvidenceSource,
    EvidenceType,
    FreshnessState,
)
from tiaf.contracts.common import Metadata, NonEmptyStr, Symbol, TiafDateTime

from ._validation import require_unique, validate_safe_metadata
from .enums import AgentCapability, CitationRole, ClaimKind, EvidenceImportance

UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
type EvidenceFactValue = StrictStr | StrictInt | StrictFloat | StrictBool
type EvidenceFactParameterValue = EvidenceFactValue | None
_FACT_METRIC_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")

_QUALITY_ORDER = {
    DataQuality.GOOD: 0,
    DataQuality.PARTIAL: 1,
    DataQuality.DEGRADED: 2,
    DataQuality.UNAVAILABLE: 3,
}
_FRESHNESS_ORDER = {
    FreshnessState.FRESH: 0,
    FreshnessState.AGING: 1,
    FreshnessState.STALE: 2,
    FreshnessState.UNKNOWN: 3,
}


class EvidenceFactKind(StrEnum):
    """Accepted origin shape of one supplied scalar fact."""

    FEATURE = "FEATURE"
    INDICATOR = "INDICATOR"
    BASELINE = "BASELINE"
    FUNDAMENTAL = "FUNDAMENTAL"


class EvidenceFactParameter(ContractModel):
    """One immutable parameter needed to identify an A2 calculation exactly."""

    name: NonEmptyStr
    value: EvidenceFactParameterValue


class EvidenceFact(ContractModel):
    """Immutable scalar projection of an already-computed evidence value."""

    fact_id: NonEmptyStr
    kind: EvidenceFactKind
    metric_id: NonEmptyStr
    value: EvidenceFactValue
    unit: NonEmptyStr | None = None
    parameters: tuple[EvidenceFactParameter, ...] = ()
    output_name: NonEmptyStr | None = None
    interval: NonEmptyStr | None = None
    as_of: TiafDateTime
    quality: DataQuality
    freshness: FreshnessState
    source_evidence: tuple[NonEmptyStr, ...]

    @model_validator(mode="after")
    def validate_fact(self) -> Self:
        if not _FACT_METRIC_PATTERN.fullmatch(self.metric_id):
            raise ValueError("fact metric_id must be a canonical dotted identifier")
        if isinstance(self.value, float) and not math.isfinite(self.value):
            raise ValueError("evidence fact value must be finite")
        names = tuple(item.name for item in self.parameters)
        require_unique(names, "evidence fact parameters")
        if not self.source_evidence:
            raise ValueError("evidence fact requires source evidence")
        require_unique(self.source_evidence, "evidence fact source evidence")
        if self.kind is EvidenceFactKind.INDICATOR and self.output_name is None:
            raise ValueError("indicator fact requires output_name")
        if self.kind is not EvidenceFactKind.INDICATOR and self.output_name is not None:
            raise ValueError("only indicator facts accept output_name")
        return self


class AgentEvidenceReference(ContractModel):
    """One immutable, access-safe reference to supplied evidence."""

    evidence_id: NonEmptyStr
    evidence_type: EvidenceType
    subject: Symbol
    producer_id: NonEmptyStr
    producer_version: NonEmptyStr
    source: EvidenceSource
    availability: EvidenceStatus
    quality: DataQuality | None = None
    freshness: FreshnessState | None = None
    observed_at: TiafDateTime | None = None
    acquired_at: TiafDateTime | None = None
    checksum: NonEmptyStr | None = None
    source_reference: NonEmptyStr | None = None
    failure_code: NonEmptyStr | None = None
    failure_detail: NonEmptyStr | None = None
    facts: tuple[EvidenceFact, ...] = ()
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_availability(self) -> Self:
        factual = {
            EvidenceStatus.AVAILABLE,
            EvidenceStatus.PARTIAL,
            EvidenceStatus.STALE,
        }
        if self.availability in factual:
            if self.quality is None or self.freshness is None:
                raise ValueError("available evidence requires quality and freshness")
            if self.availability is EvidenceStatus.STALE:
                if self.freshness is not FreshnessState.STALE:
                    raise ValueError("STALE availability requires STALE freshness")
            elif self.freshness is FreshnessState.STALE:
                raise ValueError("STALE freshness requires STALE availability")
            if self.checksum is None:
                raise ValueError("available evidence requires a checksum")
        elif any(
            value is not None
            for value in (self.quality, self.freshness, self.observed_at, self.checksum)
        ):
            raise ValueError("unavailable evidence cannot claim factual quality/provenance")
        if self.availability not in factual and self.facts:
            raise ValueError("unavailable evidence cannot carry factual values")
        require_unique(tuple(item.fact_id for item in self.facts), "evidence fact IDs")
        if any(
            self.observed_at is not None and item.as_of > self.observed_at
            for item in self.facts
        ):
            raise ValueError("evidence fact cannot postdate reference observation")
        if self.availability is EvidenceStatus.FAILED:
            if self.failure_code is None or self.failure_detail is None:
                raise ValueError("FAILED evidence requires typed failure details")
        elif self.failure_code is not None or self.failure_detail is not None:
            raise ValueError("failure details are valid only for FAILED evidence")
        if (
            self.observed_at is not None
            and self.acquired_at is not None
            and self.acquired_at < self.observed_at
        ):
            raise ValueError("acquired_at cannot predate observed_at")
        return self


class EvidenceCitation(ContractModel):
    """One supporting or contradicting link from a claim to supplied evidence."""

    evidence_id: NonEmptyStr
    role: CitationRole
    locator: NonEmptyStr | None = None
    qualification: NonEmptyStr | None = None


class EvidenceClaim(ContractModel):
    """Auditable factual or interpretive statement with mandatory citations."""

    claim_id: NonEmptyStr
    kind: ClaimKind
    statement: NonEmptyStr
    evidence_type: EvidenceType
    citations: tuple[EvidenceCitation, ...]
    as_of: TiafDateTime
    provenance: NonEmptyStr
    quality: DataQuality
    freshness: FreshnessState
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_citations(self) -> Self:
        if not self.citations:
            raise ValueError("evidence claim requires at least one citation")
        keys = tuple((item.evidence_id, item.role) for item in self.citations)
        require_unique(keys, "claim citations")
        return self


class MissingEvidenceRequest(ContractModel):
    """A specialist's typed request for evidence it cannot acquire itself."""

    missing_request_id: NonEmptyStr
    evidence_type: EvidenceType
    capability: AgentCapability
    subject: Symbol
    reason: NonEmptyStr
    importance: EvidenceImportance
    required_freshness: FreshnessState | None = None
    start_at: TiafDateTime | None = None
    end_at: TiafDateTime | None = None
    requested_at: TiafDateTime
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_time_range(self) -> Self:
        if (self.start_at is None) != (self.end_at is None):
            raise ValueError("missing-evidence time range requires both bounds")
        if self.start_at is not None and self.end_at is not None:
            if self.end_at <= self.start_at:
                raise ValueError("missing-evidence end_at must be later than start_at")
        return self


class AgentEvidencePack(ContractModel):
    """Bounded immutable references supplied to one specialist invocation."""

    pack_id: NonEmptyStr
    request_id: NonEmptyStr
    subject: Symbol
    evidence_fingerprint: NonEmptyStr
    references: tuple[AgentEvidenceReference, ...]
    analysis_context_ids: tuple[NonEmptyStr, ...] = ()
    feature_bundle_ids: tuple[NonEmptyStr, ...] = ()
    indicator_bundle_ids: tuple[NonEmptyStr, ...] = ()
    relative_strength_evidence_ids: tuple[NonEmptyStr, ...] = ()
    multi_timeframe_context_ids: tuple[NonEmptyStr, ...] = ()
    derivatives_evidence_ids: tuple[NonEmptyStr, ...] = ()
    deterministic_assessment_id: NonEmptyStr
    overall_quality: DataQuality
    overall_freshness: FreshnessState
    evidence_coverage: UnitFloat
    missing_evidence: tuple[MissingEvidenceRequest, ...] = ()
    created_at: TiafDateTime
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_pack(self) -> Self:
        if not self.references:
            raise ValueError("Agent evidence pack requires explicit evidence references")
        reference_ids = tuple(item.evidence_id for item in self.references)
        require_unique(reference_ids, "evidence reference IDs")
        if any(item.subject != self.subject for item in self.references):
            raise ValueError("all evidence references must match the pack subject")
        collections = (
            (self.analysis_context_ids, "analysis context IDs"),
            (self.feature_bundle_ids, "feature bundle IDs"),
            (self.indicator_bundle_ids, "indicator bundle IDs"),
            (self.relative_strength_evidence_ids, "relative-strength evidence IDs"),
            (self.multi_timeframe_context_ids, "multi-timeframe context IDs"),
            (self.derivatives_evidence_ids, "derivatives evidence IDs"),
            (
                tuple(item.missing_request_id for item in self.missing_evidence),
                "missing-evidence request IDs",
            ),
        )
        for values, label in collections:
            require_unique(values, label)
        if any(item.subject != self.subject for item in self.missing_evidence):
            raise ValueError("missing-evidence requests must match the pack subject")
        if self.evidence_coverage > 0 and not any(
            item.availability
            in {EvidenceStatus.AVAILABLE, EvidenceStatus.PARTIAL, EvidenceStatus.STALE}
            for item in self.references
        ):
            raise ValueError("positive evidence coverage requires usable evidence")
        factual = tuple(
            item
            for item in self.references
            if item.availability
            in {EvidenceStatus.AVAILABLE, EvidenceStatus.PARTIAL, EvidenceStatus.STALE}
        )
        expected_quality = (
            max(
                (item.quality for item in factual if item.quality is not None),
                key=_QUALITY_ORDER.__getitem__,
            )
            if factual
            else DataQuality.UNAVAILABLE
        )
        expected_freshness = (
            max(
                (item.freshness for item in factual if item.freshness is not None),
                key=_FRESHNESS_ORDER.__getitem__,
            )
            if factual
            else FreshnessState.UNKNOWN
        )
        if self.overall_quality is not expected_quality:
            raise ValueError("pack quality must equal weakest factual evidence quality")
        if self.overall_freshness is not expected_freshness:
            raise ValueError("pack freshness must equal weakest factual evidence freshness")
        if any(
            item.acquired_at is not None and item.acquired_at > self.created_at
            for item in self.references
        ):
            raise ValueError("evidence pack cannot predate referenced acquisition")
        return self

    def reference(self, evidence_id: str) -> AgentEvidenceReference | None:
        """Return a supplied reference without fetching or recalculating evidence."""
        return next(
            (item for item in self.references if item.evidence_id == evidence_id),
            None,
        )
