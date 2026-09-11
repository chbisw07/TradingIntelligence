"""Immutable provider-neutral source, claim, dispute and A4-input contracts."""

from typing import Annotated, Literal, Self

from pydantic import (
    AfterValidator,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    model_validator,
)

from tiaf.a3_hardening import A2CaptureMode, PortableA3ReplayPackage
from tiaf.contracts import ContractModel, DataQuality, FreshnessState, Horizon
from tiaf.contracts.common import NonEmptyStr, Symbol, TiafDateTime
from tiaf.planner.models import Sha256

from .enums import (
    AssertionValueKind,
    AuthorityApplicability,
    ClaimRole,
    ComparabilityStatus,
    ConfirmationAdmissibility,
    DerivationRole,
    DisputeCategory,
    DisputeState,
    EpistemicMappingStatus,
    EpistemicRole,
    IdentityKnowledge,
    IndependenceDimension,
    IndependenceRelation,
    MeasureRole,
    MeasureType,
    Missingness,
    SourceEntityRole,
)


def _reject_url(value: str) -> str:
    if "://" in value:
        raise ValueError("canonical semantic identity cannot contain an arbitrary URL")
    return value


QualifiedId = Annotated[
    str,
    Field(pattern=r"^[a-z][a-z0-9_.-]*:[A-Za-z0-9][A-Za-z0-9_.:/-]*$"),
    AfterValidator(_reject_url),
]
ScalarValue = StrictStr | StrictInt | StrictFloat | StrictBool


def _unique(values: tuple[object, ...], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must be unique")


class SourceEntityIdentity(ContractModel):
    source_id: QualifiedId
    role: SourceEntityRole
    knowledge: IdentityKnowledge
    display_name: NonEmptyStr | None = None
    jurisdiction: NonEmptyStr | None = None
    original_a3_source_ids: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def known_has_identity(self) -> Self:
        if self.knowledge is IdentityKnowledge.KNOWN and self.display_name is None:
            raise ValueError("known source identity requires display name")
        _unique(self.original_a3_source_ids, "original A3 source IDs")
        return self


class ProviderAdapterIdentity(ContractModel):
    provider_id: QualifiedId
    adapter_id: QualifiedId
    adapter_version: NonEmptyStr
    original_provider_id: NonEmptyStr | None = None


class UpstreamOriginIdentity(ContractModel):
    origin_id: QualifiedId
    knowledge: IdentityKnowledge
    source_ids: tuple[QualifiedId, ...] = ()
    basis: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_origin(self) -> Self:
        _unique(self.source_ids, "origin source IDs")
        if self.knowledge is IdentityKnowledge.UNKNOWN and self.source_ids:
            raise ValueError("unknown origin cannot claim known source identities")
        return self


class DocumentFamilyIdentity(ContractModel):
    family_id: QualifiedId
    source_id: QualifiedId
    document_kind: NonEmptyStr
    subject: Symbol


class DocumentVersionIdentity(ContractModel):
    document_version_id: QualifiedId
    family_id: QualifiedId
    content_hash: Sha256
    published_at: TiafDateTime | None = None
    available_from: TiafDateTime
    original_document_id: NonEmptyStr | None = None
    locator_refs: tuple[QualifiedId, ...] = ()
    revision_number: int = Field(default=0, ge=0)
    correction_kind: Literal["NONE", "CORRECTION", "RESTATEMENT", "CLARIFICATION"] = "NONE"
    supersedes_document_version_id: QualifiedId | None = None
    corrected_predicates: tuple[QualifiedId, ...] = ()
    corrected_periods: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def revision_is_explicit(self) -> Self:
        if self.published_at is not None and self.available_from < self.published_at:
            raise ValueError("document availability cannot predate publication")
        if self.document_version_id == self.supersedes_document_version_id:
            raise ValueError("document version cannot supersede itself")
        explicit = self.correction_kind != "NONE"
        if explicit != (self.supersedes_document_version_id is not None):
            raise ValueError("only an explicit correction/restatement/clarification supersedes")
        if explicit and self.revision_number == 0:
            raise ValueError("explicit document revision requires positive revision number")
        if explicit and not (self.corrected_predicates or self.corrected_periods):
            raise ValueError("explicit document revision requires predicate or period scope")
        _unique(self.locator_refs, "document locator refs")
        return self


class EvidenceOccurrenceIdentity(ContractModel):
    occurrence_id: QualifiedId
    evidence_id: NonEmptyStr
    source_id: QualifiedId
    provider_adapter_id: QualifiedId | None = None
    origin_id: QualifiedId
    document_version_id: QualifiedId | None = None
    observed_at: TiafDateTime | None = None
    acquired_at: TiafDateTime

    @model_validator(mode="after")
    def observed_before_acquired(self) -> Self:
        if self.observed_at is not None and self.acquired_at < self.observed_at:
            raise ValueError("occurrence acquisition cannot predate observation")
        return self


class AuthorityScope(ContractModel):
    authority_domain: QualifiedId
    subject: Symbol
    jurisdiction: NonEmptyStr | None = None
    predicate_id: QualifiedId
    period: NonEmptyStr | None = None
    effective_from: TiafDateTime | None = None
    effective_to: TiafDateTime | None = None
    statement_basis: NonEmptyStr | None = None

    @model_validator(mode="after")
    def valid_interval(self) -> Self:
        if self.effective_from and self.effective_to and self.effective_to < self.effective_from:
            raise ValueError("authority effective interval is reversed")
        return self


class AuthorityAssessment(ContractModel):
    assessment_id: QualifiedId
    source_id: QualifiedId
    document_version_id: QualifiedId | None = None
    scope: AuthorityScope
    source_role: SourceEntityRole
    authenticity_basis: tuple[NonEmptyStr, ...]
    applicability: AuthorityApplicability
    policy_id: QualifiedId
    policy_version: NonEmptyStr
    limitations: tuple[NonEmptyStr, ...] = ()
    assessed_at: TiafDateTime

    @model_validator(mode="after")
    def applicable_has_basis(self) -> Self:
        if self.applicability is AuthorityApplicability.APPLICABLE and not self.authenticity_basis:
            raise ValueError("applicable authority requires authenticity basis")
        _unique(self.limitations, "authority limitations")
        return self


class PropositionKey(ContractModel):
    proposition_id: QualifiedId
    subject: Symbol
    predicate_id: QualifiedId
    predicate_version: NonEmptyStr
    qualifiers: tuple[tuple[NonEmptyStr, NonEmptyStr], ...] = ()
    negated: bool = False
    unit: NonEmptyStr | None = None
    currency: NonEmptyStr | None = None
    reporting_period: NonEmptyStr | None = None
    effective_interval: tuple[TiafDateTime, TiafDateTime] | None = None
    consolidation_basis: Literal["STANDALONE", "CONSOLIDATED", "NOT_APPLICABLE", "UNKNOWN"] = (
        "UNKNOWN"
    )
    segment: NonEmptyStr | None = None
    accounting_basis: NonEmptyStr | None = None
    statement_basis: NonEmptyStr | None = None
    adjustment_basis: Literal["ADJUSTED", "UNADJUSTED", "NOT_APPLICABLE", "UNKNOWN"] = "UNKNOWN"
    measure_type: MeasureType
    measure_role: MeasureRole
    horizon: Horizon | None = None
    target_interval: tuple[TiafDateTime, TiafDateTime] | None = None

    @model_validator(mode="after")
    def validate_semantics(self) -> Self:
        if self.currency is not None and self.unit is None:
            raise ValueError("currency requires unit")
        if self.effective_interval and self.effective_interval[1] < self.effective_interval[0]:
            raise ValueError("effective interval is reversed")
        if self.target_interval and self.target_interval[1] < self.target_interval[0]:
            raise ValueError("target interval is reversed")
        keys = tuple(key for key, _ in self.qualifiers)
        _unique(keys, "proposition qualifier keys")
        return self


class AssertionValue(ContractModel):
    kind: AssertionValueKind
    scalar: ScalarValue | None = None
    lower: StrictInt | StrictFloat | None = None
    upper: StrictInt | StrictFloat | None = None
    direction: NonEmptyStr | None = None

    @model_validator(mode="after")
    def exactly_one_shape(self) -> Self:
        fields = {
            AssertionValueKind.SCALAR: self.scalar is not None,
            AssertionValueKind.INTERVAL: self.lower is not None and self.upper is not None,
            AssertionValueKind.DIRECTION: self.direction is not None,
            AssertionValueKind.MISSING: all(
                value is None for value in (self.scalar, self.lower, self.upper, self.direction)
            ),
        }
        if not fields[self.kind]:
            raise ValueError("assertion value does not match its kind")
        active = sum(
            value is not None for value in (self.scalar, self.lower, self.upper, self.direction)
        )
        if self.kind is AssertionValueKind.INTERVAL:
            if active != 2 or self.upper < self.lower:  # type: ignore[operator]
                raise ValueError("assertion interval is invalid")
        elif self.kind is not AssertionValueKind.MISSING and active != 1:
            raise ValueError("assertion value has conflicting shapes")
        return self


class AssertionIdentity(ContractModel):
    assertion_id: QualifiedId
    proposition: PropositionKey
    value: AssertionValue
    epistemic_role: EpistemicRole
    derivation_role: DerivationRole
    occurrence_ids: tuple[QualifiedId, ...]
    original_claim_ids: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def has_occurrence(self) -> Self:
        if not self.occurrence_ids:
            raise ValueError("assertion requires an evidence occurrence")
        _unique(self.occurrence_ids, "assertion occurrence IDs")
        return self


class AdmissionIdentity(ContractModel):
    admission_id: QualifiedId
    run_id: NonEmptyStr
    capture_id: NonEmptyStr
    assertion_id: QualifiedId
    as_of: TiafDateTime
    available_from: TiafDateTime
    projection_policy_id: QualifiedId
    projection_policy_version: NonEmptyStr
    comparison_policy_id: QualifiedId
    comparison_policy_version: NonEmptyStr
    source_ids: tuple[QualifiedId, ...]
    mapping_status: EpistemicMappingStatus
    limitations: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def point_in_time(self) -> Self:
        if self.available_from > self.as_of:
            raise ValueError("admission cannot include evidence unavailable at as-of")
        _unique(self.source_ids, "admission source IDs")
        return self


class TransformRule(ContractModel):
    rule_id: QualifiedId
    version: NonEmptyStr
    from_unit: NonEmptyStr
    to_unit: NonEmptyStr
    multiplier: float = Field(gt=0, allow_inf_nan=False)
    tolerance: float | None = Field(default=None, ge=0, allow_inf_nan=False)


class ComparisonAssessment(ContractModel):
    comparison_id: QualifiedId
    assertion_ids: tuple[QualifiedId, QualifiedId]
    status: ComparabilityStatus
    rule_id: QualifiedId | None = None
    rule_version: NonEmptyStr | None = None
    transform_multiplier: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    tolerance: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    transformed_values: tuple[ScalarValue, ScalarValue] | None = None
    reasons: tuple[NonEmptyStr, ...]

    @model_validator(mode="after")
    def validate_comparison(self) -> Self:
        if self.assertion_ids[0] == self.assertion_ids[1]:
            raise ValueError("comparison requires two distinct assertions")
        transformed = self.status is ComparabilityStatus.COMPARABLE_WITH_TRANSFORM
        rule_fields = (
            self.rule_id,
            self.rule_version,
            self.transform_multiplier,
            self.transformed_values,
        )
        if transformed != all(item is not None for item in rule_fields):
            raise ValueError("transformed comparison requires complete transform identity")
        if not transformed and any(item is not None for item in (*rule_fields, self.tolerance)):
            raise ValueError("non-transformed comparison cannot contain transform fields")
        if not self.reasons:
            raise ValueError("comparison requires a reason")
        return self


class DisputeEvent(ContractModel):
    event_id: QualifiedId
    state: DisputeState
    recorded_at: TiafDateTime
    evidence_ids: tuple[NonEmptyStr, ...] = ()
    policy_id: QualifiedId
    policy_version: NonEmptyStr
    reason: NonEmptyStr


class DisputeRecord(ContractModel):
    dispute_id: QualifiedId
    category: DisputeCategory
    assertion_ids: tuple[QualifiedId, ...]
    events: tuple[DisputeEvent, ...]
    successor_dispute_id: QualifiedId | None = None

    @model_validator(mode="after")
    def validate_history(self) -> Self:
        if len(self.assertion_ids) < 2 or not self.events:
            raise ValueError("dispute requires two assertions and history")
        _unique(self.assertion_ids, "dispute assertion IDs")
        _unique(tuple(event.event_id for event in self.events), "dispute event IDs")
        if self.events[0].state is not DisputeState.DETECTED:
            raise ValueError("dispute history must begin at DETECTED")
        terminal = {
            DisputeState.CONFIRMED_CONFLICT,
            DisputeState.UNRESOLVED,
            DisputeState.NOT_COMPARABLE,
            DisputeState.RESOLVED_BY_SCOPE,
            DisputeState.RESOLVED_BY_REVISION,
            DisputeState.RESOLVED_BY_AUTHORITATIVE_FIELD,
            DisputeState.SUPERSEDED,
        }
        if any(event.state in terminal for event in self.events[:-1]):
            raise ValueError("terminal dispute state must be last")
        if any(
            self.events[index].recorded_at < self.events[index - 1].recorded_at
            for index in range(1, len(self.events))
        ):
            raise ValueError("dispute history must be time ordered")
        final = self.events[-1]
        if final.state in terminal and not final.evidence_ids:
            raise ValueError("terminal dispute event requires cited evidence")
        if (final.state is DisputeState.SUPERSEDED) != (self.successor_dispute_id is not None):
            raise ValueError("superseded dispute requires exactly one successor ID")
        return self


class IndependenceAssessment(ContractModel):
    assessment_id: QualifiedId
    dimension: IndependenceDimension
    relation: IndependenceRelation
    left_occurrence_id: QualifiedId
    right_occurrence_id: QualifiedId
    parent_occurrence_ids: tuple[QualifiedId, ...] = ()
    independence_basis_ids: tuple[QualifiedId, ...] = ()
    basis: tuple[NonEmptyStr, ...] = ()
    policy_id: QualifiedId
    policy_version: NonEmptyStr

    @model_validator(mode="after")
    def validate_basis(self) -> Self:
        if self.left_occurrence_id == self.right_occurrence_id:
            raise ValueError("independence requires two distinct occurrences")
        if self.relation is IndependenceRelation.INDEPENDENT and (
            not self.basis or len(self.independence_basis_ids) < 2
        ):
            raise ValueError("independence requires two explicit non-provider basis identities")
        if self.relation is IndependenceRelation.UNKNOWN and self.parent_occurrence_ids:
            raise ValueError("unknown relation cannot claim parent lineage")
        _unique(self.parent_occurrence_ids, "parent occurrence IDs")
        _unique(self.independence_basis_ids, "independence basis IDs")
        return self


class EpistemicProjection(ContractModel):
    projection_id: QualifiedId
    assertion_id: QualifiedId
    claim_role: ClaimRole
    epistemic_role: EpistemicRole
    derivation_role: DerivationRole
    mapping_status: EpistemicMappingStatus
    mapping_rule_id: QualifiedId | None = None
    limitations: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def mapped_rule(self) -> Self:
        if self.mapping_status is EpistemicMappingStatus.MAPPED and self.mapping_rule_id is None:
            raise ValueError("mapped epistemic projection requires mapping rule")
        if (
            self.derivation_role is DerivationRole.PROVIDER_DERIVED
            and self.claim_role is ClaimRole.OBSERVED_REPORTED_VALUE
            and self.mapping_rule_id is None
        ):
            raise ValueError("provider-derived value cannot become reported without mapping")
        return self


class ConfirmationFieldProjection(ContractModel):
    field_id: NonEmptyStr
    discovered_assertion_ids: tuple[QualifiedId, ...]
    authoritative_assertion_ids: tuple[QualifiedId, ...] = ()
    comparison_ids: tuple[QualifiedId, ...] = ()
    authority_assessment_ids: tuple[QualifiedId, ...] = ()
    admissibility: ConfirmationAdmissibility
    document_version_ids: tuple[QualifiedId, ...] = ()
    unresolved_gaps: tuple[NonEmptyStr, ...] = ()


class ConfirmationProjection(ContractModel):
    projection_id: QualifiedId
    confirmation_id: NonEmptyStr
    recorded_status: NonEmptyStr
    recorded_semantic_fingerprint: Sha256
    fields: tuple[ConfirmationFieldProjection, ...]
    all_document_version_ids: tuple[QualifiedId, ...] = ()


class ConfirmationFieldBinding(ContractModel):
    field_id: NonEmptyStr
    discovered_assertion_ids: tuple[QualifiedId, ...]
    authoritative_assertion_ids: tuple[QualifiedId, ...] = ()
    comparison_ids: tuple[QualifiedId, ...] = ()
    authority_assessment_ids: tuple[QualifiedId, ...] = ()
    document_versions: tuple[DocumentVersionIdentity, ...] = ()

    @model_validator(mode="after")
    def discovered_required(self) -> Self:
        if not self.discovered_assertion_ids:
            raise ValueError("confirmation binding requires discovered assertion")
        return self


class ProjectionGap(ContractModel):
    gap_id: QualifiedId
    missingness: Missingness
    code: NonEmptyStr
    affected_reference: NonEmptyStr
    reason: NonEmptyStr


class ExcludedEvidence(ContractModel):
    evidence_id: NonEmptyStr
    reason: NonEmptyStr


class A4ProjectionHeader(ContractModel):
    schema_id: Literal["tiaf.a4.semantic-input-projection"] = "tiaf.a4.semantic-input-projection"
    schema_version: Literal["1.0"] = "1.0"
    projection_policy_id: QualifiedId
    projection_policy_version: NonEmptyStr
    comparison_policy_id: QualifiedId
    comparison_policy_version: NonEmptyStr
    subject: Symbol
    objective: NonEmptyStr
    horizon: Horizon
    evidence_as_of: TiafDateTime
    created_at: TiafDateTime
    run_id: NonEmptyStr
    correlation_id: NonEmptyStr
    authority_ref: QualifiedId
    profile_ref: QualifiedId
    budget_ref: QualifiedId
    model_policy_ref: QualifiedId


class FrozenParentReferences(ContractModel):
    a3_package_id: NonEmptyStr
    a3_package_semantic_fingerprint: Sha256
    a3_package_exact_checksum: Sha256
    a38_capture_checksum: Sha256
    a38_semantic_fingerprint: Sha256
    a39_capture_checksum: Sha256
    a39_semantic_fingerprint: Sha256
    a2_mode: A2CaptureMode
    a2_assessment_id: NonEmptyStr
    a2_evidence_fingerprint: NonEmptyStr


class OpportunityOpinionView(ContractModel):
    a39_state: NonEmptyStr
    a39_reason_ids: tuple[NonEmptyStr, ...]
    a39_gap_ids: tuple[NonEmptyStr, ...]
    active_opinion_ids: tuple[NonEmptyStr, ...]
    superseded_opinion_ids: tuple[NonEmptyStr, ...]
    original_a2_direction: NonEmptyStr | None = None
    original_a2_candidate_class: NonEmptyStr | None = None
    original_a2_score: float | None = Field(default=None, ge=0, le=100, allow_inf_nan=False)
    full_a2_evidence_available: bool


class EvidenceQualification(ContractModel):
    evidence_id: NonEmptyStr
    quality: DataQuality | None = None
    freshness: FreshnessState | None = None
    directness: Literal["DIRECT", "INDIRECT", "UNKNOWN"] = "UNKNOWN"
    completeness: Literal["COMPLETE", "PARTIAL", "UNKNOWN"] = "UNKNOWN"


class A4SemanticInputProjection(ContractModel):
    projection_id: QualifiedId
    header: A4ProjectionHeader
    parents: FrozenParentReferences
    parent_projection_id: QualifiedId | None = None
    parent_evidence_as_of: TiafDateTime | None = None
    new_evidence_ids: tuple[NonEmptyStr, ...] = ()
    opportunity: OpportunityOpinionView
    sources: tuple[SourceEntityIdentity, ...] = ()
    providers: tuple[ProviderAdapterIdentity, ...] = ()
    origins: tuple[UpstreamOriginIdentity, ...] = ()
    document_families: tuple[DocumentFamilyIdentity, ...] = ()
    document_versions: tuple[DocumentVersionIdentity, ...] = ()
    occurrences: tuple[EvidenceOccurrenceIdentity, ...] = ()
    assertions: tuple[AssertionIdentity, ...] = ()
    admissions: tuple[AdmissionIdentity, ...] = ()
    authority_assessments: tuple[AuthorityAssessment, ...] = ()
    comparisons: tuple[ComparisonAssessment, ...] = ()
    disputes: tuple[DisputeRecord, ...] = ()
    independence: tuple[IndependenceAssessment, ...] = ()
    epistemic_projections: tuple[EpistemicProjection, ...] = ()
    confirmation_projections: tuple[ConfirmationProjection, ...] = ()
    evidence_qualifications: tuple[EvidenceQualification, ...] = ()
    gaps: tuple[ProjectionGap, ...] = ()
    excluded_evidence: tuple[ExcludedEvidence, ...] = ()
    referenced_artifact_digests: tuple[tuple[NonEmptyStr, Sha256], ...] = ()
    usage_cost_knowledge: tuple[tuple[NonEmptyStr, NonEmptyStr], ...] = ()
    semantic_fingerprint: Sha256


class ProjectionBuildInput(ContractModel):
    package: PortableA3ReplayPackage
    header: A4ProjectionHeader
    parent_projection_id: QualifiedId | None = None
    parent_evidence_as_of: TiafDateTime | None = None
    new_evidence_ids: tuple[NonEmptyStr, ...] = ()
    sources: tuple[SourceEntityIdentity, ...] = ()
    providers: tuple[ProviderAdapterIdentity, ...] = ()
    origins: tuple[UpstreamOriginIdentity, ...] = ()
    document_families: tuple[DocumentFamilyIdentity, ...] = ()
    document_versions: tuple[DocumentVersionIdentity, ...] = ()
    occurrences: tuple[EvidenceOccurrenceIdentity, ...] = ()
    assertions: tuple[AssertionIdentity, ...] = ()
    admissions: tuple[AdmissionIdentity, ...] = ()
    authority_assessments: tuple[AuthorityAssessment, ...] = ()
    comparisons: tuple[ComparisonAssessment, ...] = ()
    disputes: tuple[DisputeRecord, ...] = ()
    independence: tuple[IndependenceAssessment, ...] = ()
    epistemic_projections: tuple[EpistemicProjection, ...] = ()
    confirmation_projections: tuple[ConfirmationProjection, ...] = ()
    evidence_qualifications: tuple[EvidenceQualification, ...] = ()
    gaps: tuple[ProjectionGap, ...] = ()
    excluded_evidence: tuple[ExcludedEvidence, ...] = ()
    referenced_artifact_digests: tuple[tuple[NonEmptyStr, Sha256], ...] = ()
    usage_cost_knowledge: tuple[tuple[NonEmptyStr, NonEmptyStr], ...] = ()
    requires_full_a2_assertion_ids: tuple[QualifiedId, ...] = ()

    @model_validator(mode="after")
    def successor_rules(self) -> Self:
        successor_fields = (
            self.parent_projection_id,
            self.parent_evidence_as_of,
            self.new_evidence_ids,
        )
        if any(bool(item) for item in successor_fields) and not all(
            bool(item) for item in successor_fields
        ):
            raise ValueError("successor requires parent projection, parent as-of and new evidence")
        if self.parent_evidence_as_of and self.header.evidence_as_of <= self.parent_evidence_as_of:
            raise ValueError("successor evidence as-of must be later than parent")
        return self


class FoundationCapture(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    capture_id: QualifiedId
    build_input_json: NonEmptyStr
    build_input_checksum: Sha256
    projection_json: NonEmptyStr
    projection_checksum: Sha256
    projection_semantic_fingerprint: Sha256
    exact_capture_checksum: Sha256
    captured_at: TiafDateTime


class ProjectionPolicyComparison(ContractModel):
    comparison_id: QualifiedId
    original_projection_id: QualifiedId
    compared_projection_id: QualifiedId
    original_policy: tuple[QualifiedId, NonEmptyStr]
    compared_policy: tuple[QualifiedId, NonEmptyStr]
    original_fingerprint: Sha256
    compared_fingerprint: Sha256
    created_at: TiafDateTime
