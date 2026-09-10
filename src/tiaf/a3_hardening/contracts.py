"""Immutable A3.10 replay, comparison, accounting and closure contracts."""

from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from tiaf.agents import AgentStance, AgentUsage, SpecialistId
from tiaf.agents.evidence import AgentEvidencePack
from tiaf.baseline import BaselineDirection, CandidateClass
from tiaf.context import AnalysisPurpose
from tiaf.contracts import ContractModel, Horizon
from tiaf.contracts.common import NonEmptyStr, Symbol, TiafDateTime
from tiaf.data import InstrumentType
from tiaf.planner.digests import digest
from tiaf.planner.models import Sha256
from tiaf.service.opportunity_intelligence import OpportunityState
from tiaf.service.opportunity_intelligence.contracts import BaselineView

NonNegativeFloat = Annotated[float, Field(ge=0, allow_inf_nan=False)]
PositiveInt = Annotated[int, Field(gt=0)]
RawNonEmptyStr = Annotated[str, Field(min_length=1)]


class A3HardeningError(ValueError):
    """Base error for A3.10 package, replay and evaluation boundaries."""


class PackageIntegrityError(A3HardeningError):
    """A captured package is corrupt or internally inconsistent."""


class PolicyComparisonError(A3HardeningError):
    """A requested policy comparison is unsupported or mislabeled as replay."""


class BlobKind(StrEnum):
    A2_CAPTURE = "A2_CAPTURE"
    A38_CAPTURE = "A38_CAPTURE"
    A39_CAPTURE = "A39_CAPTURE"


class A2CaptureMode(StrEnum):
    FULL_BASELINE_CASE = "FULL_BASELINE_CASE"
    ORIGINAL_A38_PROJECTION = "ORIGINAL_A38_PROJECTION"


class CaptureStatus(StrEnum):
    COMPLETE = "COMPLETE"
    PARTIAL_RECORDED_ONLY = "PARTIAL_RECORDED_ONLY"
    NON_REPLAYABLE = "NON_REPLAYABLE"


class CaptureOrigin(StrEnum):
    SYNTHETIC = "SYNTHETIC"
    LIVE = "LIVE"
    CAPTURED_UNKNOWN = "CAPTURED_UNKNOWN"


class ReplayMode(StrEnum):
    RECORDED = "RECORDED"
    DETERMINISTIC_VERIFICATION = "DETERMINISTIC_VERIFICATION"
    POLICY_COMPARISON = "POLICY_COMPARISON"


class VerificationDisposition(StrEnum):
    REEXECUTED_DETERMINISTIC = "REEXECUTED_DETERMINISTIC"
    RECORDED_ONLY = "RECORDED_ONLY"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNVERIFIABLE = "UNVERIFIABLE"


class DirectionAxis(StrEnum):
    ALIGNED = "ALIGNED"
    OPPOSED = "OPPOSED"
    A3_INSUFFICIENT = "A3_INSUFFICIENT"
    A3_DIRECTIONAL_A2_NEUTRAL = "A3_DIRECTIONAL_A2_NEUTRAL"
    A2_CONFLICTED = "A2_CONFLICTED"
    NON_COMPARABLE = "NON_COMPARABLE"


class OpportunityAxis(StrEnum):
    ALIGNED_OPPORTUNITY = "ALIGNED_OPPORTUNITY"
    ALIGNED_TIMING_CAUTION = "ALIGNED_TIMING_CAUTION"
    BASELINE_NO_TRADE_WATCH = "BASELINE_NO_TRADE_WATCH"
    BASELINE_NO_TRADE_PRESERVED = "BASELINE_NO_TRADE_PRESERVED"
    A3_RESTRICTION_ADDED = "A3_RESTRICTION_ADDED"
    A3_EVIDENCE_INSUFFICIENT = "A3_EVIDENCE_INSUFFICIENT"
    SEMANTIC_DIVERGENCE = "SEMANTIC_DIVERGENCE"
    NON_COMPARABLE = "NON_COMPARABLE"


class DisagreementClass(StrEnum):
    ALIGNED = "ALIGNED"
    A3_MORE_CONSERVATIVE = "A3_MORE_CONSERVATIVE"
    A3_MORE_PERMISSIVE = "A3_MORE_PERMISSIVE"
    DIRECTION_CONFLICT = "DIRECTION_CONFLICT"
    TIMING_CONFLICT = "TIMING_CONFLICT"
    EVIDENCE_GAP_DIFFERENCE = "EVIDENCE_GAP_DIFFERENCE"
    RISK_CONTEXT_DIFFERENCE = "RISK_CONTEXT_DIFFERENCE"
    BASELINE_NO_TRADE_PRESERVED = "BASELINE_NO_TRADE_PRESERVED"
    NON_COMPARABLE = "NON_COMPARABLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class AdditionCategory(StrEnum):
    COMPANY_QUALITY = "COMPANY_QUALITY"
    EVENT_CATALYST_CONTEXT = "EVENT_CATALYST_CONTEXT"
    SECTOR_MACRO_CONTEXT = "SECTOR_MACRO_CONTEXT"
    DERIVATIVES_CONTEXT = "DERIVATIVES_CONTEXT"
    EXTENSION_TIMING_RESTRICTION = "EXTENSION_TIMING_RESTRICTION"
    EVIDENCE_INSUFFICIENCY = "EVIDENCE_INSUFFICIENCY"
    SOURCE_CONTRADICTION_CONFIRMATION = "SOURCE_CONTRADICTION_CONFIRMATION"
    EXPLICIT_MISSING_EVIDENCE = "EXPLICIT_MISSING_EVIDENCE"
    RISK_RESTRICTION = "RISK_RESTRICTION"
    PRESERVED_SPECIALIST_DISAGREEMENT = "PRESERVED_SPECIALIST_DISAGREEMENT"


class AdditionStatus(StrEnum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    UNKNOWN = "UNKNOWN"


class CostKnowledge(StrEnum):
    KNOWN_ZERO = "KNOWN_ZERO"
    KNOWN_NONZERO = "KNOWN_NONZERO"
    UNKNOWN = "UNKNOWN"
    UNPRICED = "UNPRICED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class UsageDisposition(StrEnum):
    FRESH = "FRESH"
    FALLBACK = "FALLBACK"
    REUSED = "REUSED"
    REPLAY = "REPLAY"


class FailureCategory(StrEnum):
    EVIDENCE_PROVIDER = "EVIDENCE_PROVIDER"
    SPECIALIST = "SPECIALIST"
    ORCHESTRATION = "ORCHESTRATION"
    REPLAY_CAPTURE = "REPLAY_CAPTURE"


class FailureCode(StrEnum):
    RATE_LIMITED = "RATE_LIMITED"
    UNAVAILABLE = "UNAVAILABLE"
    TIMEOUT = "TIMEOUT"
    MALFORMED = "MALFORMED"
    AMBIGUOUS = "AMBIGUOUS"
    OUT_OF_COVERAGE = "OUT_OF_COVERAGE"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    BUDGET_BLOCKED = "BUDGET_BLOCKED"
    EXCEPTION = "EXCEPTION"
    INVALID_OUTPUT = "INVALID_OUTPUT"
    ABSTAIN = "ABSTAIN"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNSUPPORTED = "UNSUPPORTED"
    INVALID_REQUEST = "INVALID_REQUEST"
    UNSAFE_DAG = "UNSAFE_DAG"
    DEADLINE_EXCEEDED = "DEADLINE_EXCEEDED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    TERMINAL_FAILURE = "TERMINAL_FAILURE"
    PARTIAL_COMPLETION = "PARTIAL_COMPLETION"
    MISSING_ARTIFACT = "MISSING_ARTIFACT"
    CHECKSUM_MISMATCH = "CHECKSUM_MISMATCH"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    POLICY_VERSION_MISMATCH = "POLICY_VERSION_MISMATCH"
    CORRUPT_REFERENCE = "CORRUPT_REFERENCE"
    NON_REPLAYABLE_MODEL_OUTPUT = "NON_REPLAYABLE_MODEL_OUTPUT"
    UNCLASSIFIED = "UNCLASSIFIED"


class DegradationStatus(StrEnum):
    NONE = "NONE"
    DEGRADED_COMPLETE = "DEGRADED_COMPLETE"
    PARTIAL = "PARTIAL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NON_REPLAYABLE = "NON_REPLAYABLE"


class EvidenceStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ClosureReadiness(StrEnum):
    READY_FOR_CLOSURE_REVIEW = "READY_FOR_CLOSURE_REVIEW"
    NOT_READY = "NOT_READY"


class BlobReference(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    kind: BlobKind
    schema_id: NonEmptyStr
    content_schema_version: NonEmptyStr
    checksum: Sha256
    byte_length: int = Field(gt=0)
    relative_path: NonEmptyStr

    @model_validator(mode="after")
    def content_addressed(self) -> Self:
        if self.relative_path != f"blobs/sha256/{self.checksum}.json":
            raise ValueError("blob path must be its SHA-256 content address")
        return self


class CapturedBlob(ContractModel):
    reference: BlobReference
    content: RawNonEmptyStr


class A2CaptureDescriptor(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    mode: A2CaptureMode
    blob: BlobReference
    assessment_id: NonEmptyStr
    evidence_fingerprint: NonEmptyStr
    eligibility_captured: bool


class A2ProjectionCapture(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    a2_pack: AgentEvidencePack
    baseline: BaselineView

    @model_validator(mode="after")
    def linked(self) -> Self:
        if (
            self.a2_pack.deterministic_assessment_id != self.baseline.assessment_id
            or self.a2_pack.evidence_fingerprint != self.baseline.evidence_fingerprint
        ):
            raise ValueError("A2 projection pack and baseline identity differ")
        return self


class CaptureCompleteness(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    status: CaptureStatus
    required_kinds: tuple[BlobKind, ...]
    present_kinds: tuple[BlobKind, ...]
    missing_kinds: tuple[BlobKind, ...] = ()
    reasons: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def consistent(self) -> Self:
        missing = tuple(k for k in self.required_kinds if k not in self.present_kinds)
        if missing != self.missing_kinds:
            raise ValueError("capture missing-kind projection is inconsistent")
        if self.status is CaptureStatus.COMPLETE and (missing or self.reasons):
            raise ValueError("complete capture cannot report missing/non-replayable reasons")
        return self


class A3ReplayPackageManifest(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    package_id: NonEmptyStr
    subject: Symbol
    instrument_type: InstrumentType
    horizon: Horizon
    as_of: TiafDateTime
    purpose: AnalysisPurpose
    a2_capture: A2CaptureDescriptor
    a38_capture: BlobReference
    a39_capture: BlobReference
    version_snapshots: tuple[tuple[NonEmptyStr, NonEmptyStr], ...]
    plan_versions: tuple[int, ...]
    registry_snapshots: tuple[tuple[NonEmptyStr, NonEmptyStr], ...]
    admitted_evidence_ids: tuple[NonEmptyStr, ...]
    active_opinion_ids: tuple[NonEmptyStr, ...]
    superseded_opinion_ids: tuple[NonEmptyStr, ...]
    specialist_input_digests: tuple[tuple[NonEmptyStr, Sha256], ...]
    specialist_output_fingerprints: tuple[tuple[NonEmptyStr, Sha256], ...]
    artifact_ids: tuple[NonEmptyStr, ...]
    projection_digests: tuple[Sha256, ...]
    reservation_ids: tuple[NonEmptyStr, ...]
    outcome_statuses: tuple[tuple[NonEmptyStr, NonEmptyStr], ...]
    stop_reasons: tuple[NonEmptyStr, ...]
    a2_evidence_fingerprint: NonEmptyStr
    a2_assessment_id: NonEmptyStr
    a38_semantic_fingerprint: Sha256
    a38_exact_checksum: Sha256
    a39_semantic_fingerprint: Sha256
    a39_exact_checksum: Sha256
    completeness: CaptureCompleteness
    origin: CaptureOrigin
    source_reference: NonEmptyStr
    fixture_builder_version: NonEmptyStr | None = None
    package_semantic_fingerprint: Sha256
    exact_package_checksum: Sha256
    created_at: TiafDateTime

    @model_validator(mode="after")
    def origin_truth(self) -> Self:
        if self.origin is CaptureOrigin.SYNTHETIC and self.fixture_builder_version is None:
            raise ValueError("synthetic package requires fixture-builder version")
        if self.origin is CaptureOrigin.LIVE and self.source_reference.startswith("synthetic"):
            raise ValueError("live package cannot cite a synthetic source")
        return self


class PortableA3ReplayPackage(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    manifest: A3ReplayPackageManifest
    blobs: tuple[CapturedBlob, ...]


class A3ReplayRequest(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    request_id: NonEmptyStr
    mode: ReplayMode
    package: PortableA3ReplayPackage
    requested_at: TiafDateTime


class A3ReplayResult(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    replay_id: NonEmptyStr
    package_id: NonEmptyStr
    mode: Literal[ReplayMode.RECORDED] = ReplayMode.RECORDED
    status: Literal["REPLAYED"] = "REPLAYED"
    a2_mode: A2CaptureMode
    a38_fingerprint: Sha256
    a39_fingerprint: Sha256
    semantic_match: bool
    replay_usage: AgentUsage
    replayed_at: TiafDateTime
    fingerprint: Sha256

    @model_validator(mode="after")
    def intact(self) -> Self:
        payload = {
            "package_id": self.package_id,
            "mode": self.mode,
            "a2_mode": self.a2_mode,
            "a38_fingerprint": self.a38_fingerprint,
            "a39_fingerprint": self.a39_fingerprint,
            "semantic_match": self.semantic_match,
        }
        if digest(payload) != self.fingerprint:
            raise ValueError("recorded-replay fingerprint mismatch")
        if self.replay_id != f"recorded:{self.fingerprint[:24]}":
            raise ValueError("recorded-replay identity mismatch")
        return self


class VerificationComponent(ContractModel):
    component: NonEmptyStr
    disposition: VerificationDisposition
    recorded_fingerprint: NonEmptyStr
    verified_fingerprint: NonEmptyStr | None = None
    match: bool | None = None
    reason: NonEmptyStr | None = None


class A3VerificationResult(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    verification_id: NonEmptyStr
    package_id: NonEmptyStr
    mode: Literal[ReplayMode.DETERMINISTIC_VERIFICATION] = ReplayMode.DETERMINISTIC_VERIFICATION
    components: tuple[VerificationComponent, ...]
    passed: bool
    execution_usage: AgentUsage
    verified_at: TiafDateTime
    fingerprint: Sha256

    @model_validator(mode="after")
    def intact(self) -> Self:
        payload = {
            "package_id": self.package_id,
            "components": [item.model_dump(mode="json") for item in self.components],
            "passed": self.passed,
        }
        if digest(payload) != self.fingerprint:
            raise ValueError("verification fingerprint mismatch")
        if self.verification_id != f"verification:{self.fingerprint[:24]}":
            raise ValueError("verification identity mismatch")
        return self


class A3PolicyComparisonRecord(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    comparison_id: NonEmptyStr
    package_id: NonEmptyStr
    old_policy_id: NonEmptyStr
    old_policy_version: NonEmptyStr
    new_policy_id: NonEmptyStr
    new_policy_version: NonEmptyStr
    old_fingerprint: Sha256
    new_fingerprint: Sha256
    exact_match: bool
    differences: tuple[NonEmptyStr, ...]
    execution_usage: AgentUsage
    compared_at: TiafDateTime
    fingerprint: Sha256

    @model_validator(mode="after")
    def intact(self) -> Self:
        payload = {
            "package_id": self.package_id,
            "old_policy": (self.old_policy_id, self.old_policy_version),
            "new_policy": (self.new_policy_id, self.new_policy_version),
            "old_fingerprint": self.old_fingerprint,
            "new_fingerprint": self.new_fingerprint,
            "differences": self.differences,
        }
        if digest(payload) != self.fingerprint:
            raise ValueError("policy-comparison fingerprint mismatch")
        if self.comparison_id != f"policy-comparison:{self.fingerprint[:24]}":
            raise ValueError("policy-comparison identity mismatch")
        return self


class A2Side(ContractModel):
    assessment_id: NonEmptyStr
    evidence_fingerprint: NonEmptyStr
    capture_mode: A2CaptureMode
    direction: BaselineDirection | None = None
    candidate_class: CandidateClass | None = None
    opportunity_score: float | None = Field(default=None, ge=0, le=100)
    eligible: bool | None = None
    eligibility_basis: Literal["CAPTURED", "NOT_CAPTURED"]
    reason_refs: tuple[NonEmptyStr, ...] = ()
    warnings: tuple[NonEmptyStr, ...] = ()


class A3Side(ContractModel):
    intelligence_id: NonEmptyStr
    fingerprint: Sha256
    state: OpportunityState
    price_direction: AgentStance
    qualified_bias: AgentStance
    quality: NonEmptyStr | None = None
    risk: NonEmptyStr | None = None
    maturity: NonEmptyStr | None = None
    extension: NonEmptyStr | None = None
    remaining_room: tuple[NonEmptyStr, ...] = ()
    completeness_numerator: int = Field(ge=0)
    completeness_denominator: int = Field(ge=0)
    gaps: tuple[NonEmptyStr, ...] = ()
    contradiction_ids: tuple[NonEmptyStr, ...] = ()
    reason_refs: tuple[NonEmptyStr, ...] = ()


class InformationAddition(ContractModel):
    category: AdditionCategory
    status: AdditionStatus
    source_refs: tuple[NonEmptyStr, ...] = ()


class A2A3ComparisonRecord(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    comparison_id: NonEmptyStr
    package_id: NonEmptyStr
    subject: Symbol
    horizon: Horizon
    as_of: TiafDateTime
    a2: A2Side
    a3: A3Side
    direction_axis: DirectionAxis
    opportunity_axis: OpportunityAxis
    disagreements: tuple[DisagreementClass, ...]
    information_additions: tuple[InformationAddition, ...]
    common_evidence_roots: tuple[NonEmptyStr, ...]
    comparison_policy_id: Literal["a3.10-observational-comparison-v1"] = (
        "a3.10-observational-comparison-v1"
    )
    comparison_policy_version: Literal["1.0"] = "1.0"
    compared_at: TiafDateTime
    fingerprint: Sha256

    @model_validator(mode="after")
    def intact(self) -> Self:
        payload = {
            "a2": self.a2.model_dump(mode="json"),
            "a3": self.a3.model_dump(mode="json"),
            "direction_axis": self.direction_axis,
            "opportunity_axis": self.opportunity_axis,
            "disagreements": self.disagreements,
            "information_additions": [
                item.model_dump(mode="json") for item in self.information_additions
            ],
            "common_evidence_roots": self.common_evidence_roots,
            "policy": f"{self.comparison_policy_id}/{self.comparison_policy_version}",
        }
        if digest(payload) != self.fingerprint:
            raise ValueError("A2/A3 comparison fingerprint mismatch")
        if self.comparison_id != f"a2-a3:{self.fingerprint[:24]}":
            raise ValueError("A2/A3 comparison identity mismatch")
        return self


class CostMeasure(ContractModel):
    knowledge: CostKnowledge
    amount: NonNegativeFloat | None = None
    currency: NonEmptyStr | None = None
    configured_units: NonNegativeFloat | None = None
    source_refs: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def valid_knowledge(self) -> Self:
        if self.knowledge is CostKnowledge.KNOWN_ZERO:
            if self.amount != 0 or self.currency is None:
                raise ValueError("known-zero monetary cost requires zero amount/currency")
        elif self.knowledge is CostKnowledge.KNOWN_NONZERO:
            if self.amount is None or self.amount <= 0 or self.currency is None:
                raise ValueError("known-nonzero monetary cost requires positive amount/currency")
        elif self.amount is not None or self.currency is not None:
            raise ValueError("unknown/unpriced/not-applicable cost cannot carry amount/currency")
        return self


class UsageAttribution(ContractModel):
    attribution_id: NonEmptyStr
    phase: NonEmptyStr
    capability: NonEmptyStr | None = None
    specialist: SpecialistId | None = None
    provider_id: NonEmptyStr | None = None
    model_id: NonEmptyStr | None = None
    attempt_id: NonEmptyStr | None = None
    accounting_id: NonEmptyStr | None = None
    reservation_id: NonEmptyStr | None = None
    parent_accounting_id: NonEmptyStr | None = None
    disposition: UsageDisposition
    usage: AgentUsage
    provider_calls: int = Field(default=0, ge=0)
    monetary_cost: CostMeasure
    included_in_original_total: bool


class UsageGroupSummary(ContractModel):
    key: NonEmptyStr
    attempts: int = Field(ge=0)
    provider_calls: int = Field(ge=0)
    model_calls: int = Field(ge=0)
    failures: int = Field(ge=0)
    reused: int = Field(ge=0)
    service_times: tuple[NonNegativeFloat, ...] = ()


class A3CostSummary(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    package_id: NonEmptyStr
    original_captured_usage: AgentUsage
    original_held_usage: AgentUsage
    replay_execution_usage: AgentUsage
    provider_monetary_cost: CostMeasure
    model_monetary_cost: CostMeasure
    unknown_or_unpriced_count: int = Field(ge=0)
    attributions: tuple[UsageAttribution, ...]
    provider_mix: tuple[UsageGroupSummary, ...]
    specialist_mix: tuple[UsageGroupSummary, ...]
    fallback_attempts: int = Field(ge=0)
    reuse_count: int = Field(ge=0)
    reuse_eligible_count: int = Field(ge=0)
    reuse_ratio: float | None = Field(default=None, ge=0, le=1)
    fingerprint: Sha256

    @model_validator(mode="after")
    def reconciled_identity(self) -> Self:
        included = tuple(
            item.usage for item in self.attributions if item.included_in_original_total
        )
        fields = ("llm_calls", "tool_calls", "input_tokens", "output_tokens", "cost_units")
        if any(
            sum(getattr(item, field) for item in included)
            != getattr(self.original_captured_usage, field)
            for field in fields
        ):
            raise ValueError("included leaf attribution does not reconcile to original usage")
        if len({item.attribution_id for item in self.attributions}) != len(self.attributions):
            raise ValueError("duplicate usage attribution identity")
        payload = {
            "original_usage": self.original_captured_usage.model_dump(
                mode="json", exclude={"elapsed_seconds"}
            ),
            "held_usage": self.original_held_usage.model_dump(
                mode="json", exclude={"elapsed_seconds"}
            ),
            "provider_cost": self.provider_monetary_cost.model_dump(mode="json"),
            "model_cost": self.model_monetary_cost.model_dump(mode="json"),
            "attributions": [
                item.model_dump(mode="json", exclude={"usage": {"elapsed_seconds"}})
                for item in self.attributions
            ],
            "fallback_attempts": self.fallback_attempts,
            "reuse_count": self.reuse_count,
            "reuse_eligible_count": self.reuse_eligible_count,
        }
        if digest(payload) != self.fingerprint:
            raise ValueError("cost-summary fingerprint mismatch")
        return self


class A3FailureEvent(ContractModel):
    failure_id: NonEmptyStr
    category: FailureCategory
    code: FailureCode
    phase: NonEmptyStr
    original_type: NonEmptyStr
    original_code: NonEmptyStr
    original_message_ref: Sha256
    artifact_ids: tuple[NonEmptyStr, ...] = ()
    attempt_id: NonEmptyStr | None = None
    node_id: NonEmptyStr | None = None
    provider_id: NonEmptyStr | None = None
    specialist: SpecialistId | None = None
    retry_of: NonEmptyStr | None = None
    fallback_for: NonEmptyStr | None = None
    terminal: bool
    usage_refs: tuple[NonEmptyStr, ...] = ()
    affected_capabilities: tuple[NonEmptyStr, ...] = ()
    affected_predicates: tuple[NonEmptyStr, ...] = ()


class DegradationSummary(ContractModel):
    status: DegradationStatus
    surviving_capabilities: tuple[NonEmptyStr, ...]
    failed_capabilities: tuple[NonEmptyStr, ...]
    skipped_capabilities: tuple[NonEmptyStr, ...]
    required_impact: tuple[NonEmptyStr, ...]
    optional_impact: tuple[NonEmptyStr, ...]
    a38_status: NonEmptyStr
    a39_state: OpportunityState
    completeness_numerator: int = Field(ge=0)
    completeness_denominator: int = Field(ge=0)
    prerequisite_ids: tuple[NonEmptyStr, ...]


class A3FailureSummary(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    package_id: NonEmptyStr
    events: tuple[A3FailureEvent, ...]
    degradation: DegradationSummary
    fingerprint: Sha256

    @model_validator(mode="after")
    def intact(self) -> Self:
        expected = digest(
            {
                "events": [item.model_dump(mode="json") for item in self.events],
                "degradation": self.degradation.model_dump(mode="json"),
            }
        )
        if expected != self.fingerprint:
            raise ValueError("failure-summary fingerprint mismatch")
        if len({item.failure_id for item in self.events}) != len(self.events):
            raise ValueError("duplicate failure identity")
        return self


class HardeningCheck(ContractModel):
    check_id: NonEmptyStr
    status: EvidenceStatus
    evidence_refs: tuple[NonEmptyStr, ...]
    required: bool = True


class A3HardeningResult(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    evaluation_id: NonEmptyStr
    package_id: NonEmptyStr
    replay_fingerprint: Sha256
    verification_fingerprint: Sha256
    comparison_fingerprint: Sha256
    cost_fingerprint: Sha256
    failure_fingerprint: Sha256
    checks: tuple[HardeningCheck, ...]
    passed: bool
    evaluated_at: TiafDateTime
    fingerprint: Sha256

    @model_validator(mode="after")
    def intact(self) -> Self:
        expected_pass = all(
            item.status is EvidenceStatus.PASS for item in self.checks if item.required
        )
        if expected_pass != self.passed:
            raise ValueError("hardening pass flag differs from required checks")
        payload = {
            "replay_fingerprint": self.replay_fingerprint,
            "verification_fingerprint": self.verification_fingerprint,
            "comparison_fingerprint": self.comparison_fingerprint,
            "cost_fingerprint": self.cost_fingerprint,
            "failure_fingerprint": self.failure_fingerprint,
            "checks": [item.model_dump(mode="json") for item in self.checks],
            "passed": self.passed,
        }
        if digest(payload) != self.fingerprint:
            raise ValueError("hardening-result fingerprint mismatch")
        if self.evaluation_id != f"a3-hardening:{self.fingerprint[:24]}":
            raise ValueError("hardening-result identity mismatch")
        return self


class CorpusCase(ContractModel):
    case_id: NonEmptyStr
    package_id: NonEmptyStr
    origin: CaptureOrigin
    strata: tuple[NonEmptyStr, ...]
    fixture_builder_version: NonEmptyStr | None = None
    source_reference: NonEmptyStr

    @model_validator(mode="after")
    def honest_origin(self) -> Self:
        if self.origin is CaptureOrigin.SYNTHETIC and self.fixture_builder_version is None:
            raise ValueError("synthetic corpus case requires fixture-builder version")
        return self


class A3CorpusManifest(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    corpus_id: NonEmptyStr
    cases: tuple[CorpusCase, ...]
    created_at: TiafDateTime
    fingerprint: Sha256

    @model_validator(mode="after")
    def intact(self) -> Self:
        expected = digest(
            {
                "corpus_id": self.corpus_id,
                "cases": [item.model_dump(mode="json") for item in self.cases],
            }
        )
        if expected != self.fingerprint:
            raise ValueError("corpus-manifest fingerprint mismatch")
        if len({item.case_id for item in self.cases}) != len(self.cases):
            raise ValueError("duplicate corpus case identity")
        return self


class MilestoneEvidence(ContractModel):
    evidence_id: NonEmptyStr
    category: NonEmptyStr
    status: EvidenceStatus
    required: bool
    artifact_refs: tuple[NonEmptyStr, ...]
    observed_at: TiafDateTime
    note: NonEmptyStr


class A3ClosureReadinessRecord(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    closure_record_id: NonEmptyStr
    baseline_tag: Literal["tiaf-a3.9"] = "tiaf-a3.9"
    evidence: tuple[MilestoneEvidence, ...]
    unresolved_deferrals: tuple[NonEmptyStr, ...]
    known_risks: tuple[NonEmptyStr, ...]
    readiness: ClosureReadiness
    assessed_at: TiafDateTime
    fingerprint: Sha256

    @model_validator(mode="after")
    def honest_readiness(self) -> Self:
        ready = all(item.status is EvidenceStatus.PASS for item in self.evidence if item.required)
        if ready != (self.readiness is ClosureReadiness.READY_FOR_CLOSURE_REVIEW):
            raise ValueError("closure readiness must follow required evidence")
        expected = digest(
            {
                "baseline_tag": self.baseline_tag,
                "evidence": [item.model_dump(mode="json") for item in self.evidence],
                "unresolved_deferrals": self.unresolved_deferrals,
                "known_risks": self.known_risks,
            }
        )
        if expected != self.fingerprint:
            raise ValueError("closure-readiness fingerprint mismatch")
        if self.closure_record_id != f"a3-closure:{self.fingerprint[:24]}":
            raise ValueError("closure-readiness identity mismatch")
        return self
