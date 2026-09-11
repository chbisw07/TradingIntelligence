"""Immutable contracts for deterministic A4 challenge and arbitration."""

from typing import Literal, Self

from pydantic import model_validator

from tiaf.contracts import ContractModel, Horizon
from tiaf.contracts.common import NonEmptyStr, Symbol, TiafDateTime
from tiaf.planner.models import Sha256
from tiaf.source_semantics import A4SemanticInputProjection
from tiaf.source_semantics.contracts import QualifiedId
from tiaf.source_semantics.enums import SourceEntityRole

from .enums import (
    A4Disposition,
    A4EvidenceCapability,
    A4ExecutionStatus,
    A4FailureCode,
    A4ReplayMode,
    ArbitrationDisposition,
    ChallengeFamily,
    ChallengeStatus,
    EvidenceNeedStatus,
    FailureStage,
    FindingSeverity,
    InvalidationKind,
    Materiality,
    PremisePolarity,
    PremiseRole,
    ScopeRelevance,
    SupportState,
    ThesisRole,
    ThesisSupport,
    UncertaintyKind,
)


def _unique(values: tuple[object, ...], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must be unique")


class A4DeterministicPolicy(ContractModel):
    policy_id: QualifiedId
    policy_version: NonEmptyStr
    challenge_policy_id: QualifiedId
    challenge_policy_version: NonEmptyStr
    arbitration_policy_id: QualifiedId
    arbitration_policy_version: NonEmptyStr
    max_theses: Literal[2] = 2
    max_escalation_rounds: Literal[0] = 0
    max_model_calls: Literal[0] = 0
    rule_order: tuple[NonEmptyStr, ...]

    @model_validator(mode="after")
    def bounded_rules(self) -> Self:
        if not self.rule_order:
            raise ValueError("A4 policy requires an explicit rule order")
        _unique(self.rule_order, "A4 rule order")
        return self


class ArgumentPremise(ContractModel):
    premise_id: QualifiedId
    role: PremiseRole
    polarity: PremisePolarity
    claim_refs: tuple[QualifiedId, ...] = ()
    evidence_refs: tuple[NonEmptyStr, ...] = ()
    reason_refs: tuple[NonEmptyStr, ...] = ()
    proposition_refs: tuple[QualifiedId, ...] = ()
    comparison_refs: tuple[QualifiedId, ...] = ()
    source_qualification_refs: tuple[QualifiedId, ...] = ()
    dependency_refs: tuple[QualifiedId, ...] = ()
    support_state: SupportState
    reason_code: NonEmptyStr
    scope_relevance: ScopeRelevance
    horizon_relevant: bool

    @model_validator(mode="after")
    def cited_and_unique(self) -> Self:
        if not (self.claim_refs or self.evidence_refs or self.reason_refs):
            raise ValueError("argument premise requires an admitted citation")
        for values, label in (
            (self.claim_refs, "premise claim refs"),
            (self.evidence_refs, "premise evidence refs"),
            (self.reason_refs, "premise reason refs"),
            (self.proposition_refs, "premise proposition refs"),
            (self.comparison_refs, "premise comparison refs"),
            (self.source_qualification_refs, "premise qualification refs"),
            (self.dependency_refs, "premise dependency refs"),
        ):
            _unique(values, label)
        return self


class InvalidationCondition(ContractModel):
    condition_id: QualifiedId
    premise_ref: QualifiedId
    kind: InvalidationKind
    cited_refs: tuple[NonEmptyStr, ...]
    reason_code: NonEmptyStr

    @model_validator(mode="after")
    def has_citation(self) -> Self:
        if not self.cited_refs:
            raise ValueError("invalidation condition requires cited input")
        _unique(self.cited_refs, "invalidation cited refs")
        return self


class InvestmentThesis(ContractModel):
    thesis_id: QualifiedId
    thesis_version: Literal["1.0"] = "1.0"
    role: ThesisRole
    opposed_thesis_ref: QualifiedId | None = None
    parent_a2_assessment_ref: NonEmptyStr
    parent_a3_package_ref: NonEmptyStr
    parent_a39_fingerprint_ref: Sha256
    subject: Symbol
    objective: NonEmptyStr
    horizon: Horizon
    directional_interpretation: NonEmptyStr | None = None
    premise_refs: tuple[QualifiedId, ...]
    assumption_refs: tuple[QualifiedId, ...] = ()
    support_refs: tuple[NonEmptyStr, ...] = ()
    opposition_refs: tuple[NonEmptyStr, ...] = ()
    gaps: tuple[NonEmptyStr, ...] = ()
    risks: tuple[NonEmptyStr, ...] = ()
    invalidation_conditions: tuple[InvalidationCondition, ...] = ()
    conclusion_relation: NonEmptyStr
    conclusion_policy_id: QualifiedId
    support: ThesisSupport

    @model_validator(mode="after")
    def valid_role_and_dependencies(self) -> Self:
        if not self.premise_refs:
            raise ValueError("thesis requires at least one premise")
        if self.role is ThesisRole.PRIMARY and self.opposed_thesis_ref is not None:
            raise ValueError("primary thesis cannot oppose itself")
        if self.role is ThesisRole.COUNTER and self.opposed_thesis_ref is None:
            raise ValueError("counter-thesis requires opposed primary thesis")
        if not set(self.assumption_refs) <= set(self.premise_refs):
            raise ValueError("thesis assumptions must be thesis premises")
        _unique(self.premise_refs, "thesis premise refs")
        return self


class A4EvidenceNeed(ContractModel):
    schema_id: Literal["tiaf.a4.evidence-need"] = "tiaf.a4.evidence-need"
    schema_version: Literal["1.0"] = "1.0"
    evidence_need_id: QualifiedId
    parent_a4_run_id: QualifiedId
    parent_projection_id: QualifiedId
    parent_projection_fingerprint: Sha256
    subject: Symbol
    objective: NonEmptyStr
    original_as_of: TiafDateTime
    semantic_question: NonEmptyStr
    requested_evidence_family: NonEmptyStr
    requested_capability: A4EvidenceCapability
    claim_ref: QualifiedId | None = None
    predicate_ref: QualifiedId | None = None
    field_ref: NonEmptyStr | None = None
    horizon: Horizon
    challenge_refs: tuple[QualifiedId, ...]
    dispute_refs: tuple[QualifiedId, ...] = ()
    materiality: Materiality
    reason_codes: tuple[NonEmptyStr, ...]
    expected_resolvable_question: NonEmptyStr
    minimum_source_roles: tuple[SourceEntityRole, ...]
    require_point_in_time_eligible: Literal[True] = True
    require_independent_evidence: bool = False
    require_authoritative_source: bool = False
    allow_partial_evidence: bool = False
    required: bool
    dedupe_key: Sha256
    permitted_authority_refs: tuple[QualifiedId, ...]
    budget_ref: QualifiedId
    deadline_ref: QualifiedId | None = None
    policy_id: QualifiedId
    policy_version: NonEmptyStr
    created_at: TiafDateTime
    status: Literal[EvidenceNeedStatus.OPEN] = EvidenceNeedStatus.OPEN

    @property
    def need_id(self) -> str:
        """Compatibility spelling used by A4.1 result-reference validation."""
        return self.evidence_need_id

    @model_validator(mode="after")
    def bounded_need(self) -> Self:
        if not self.challenge_refs:
            raise ValueError("evidence need requires an originating finding")
        if not self.reason_codes:
            raise ValueError("evidence need requires a reason code")
        if not self.minimum_source_roles or not self.permitted_authority_refs:
            raise ValueError("evidence need requires bounded source and authority scope")
        for values, label in (
            (self.challenge_refs, "evidence-need challenge refs"),
            (self.dispute_refs, "evidence-need dispute refs"),
            (self.reason_codes, "evidence-need reason codes"),
            (self.minimum_source_roles, "evidence-need source roles"),
            (self.permitted_authority_refs, "evidence-need authority refs"),
        ):
            _unique(values, label)
        return self


class ChallengeFinding(ContractModel):
    finding_id: QualifiedId
    challenged_thesis_ref: QualifiedId
    challenged_premise_ref: QualifiedId | None = None
    family: ChallengeFamily
    severity: FindingSeverity
    materiality: Materiality
    cited_support_refs: tuple[NonEmptyStr, ...] = ()
    cited_opposition_refs: tuple[NonEmptyStr, ...] = ()
    dispute_refs: tuple[QualifiedId, ...] = ()
    affected_conclusion: NonEmptyStr
    status: ChallengeStatus
    reason_code: NonEmptyStr
    evidence_need_ref: QualifiedId | None = None

    @model_validator(mode="after")
    def has_basis(self) -> Self:
        if not (
            self.cited_support_refs
            or self.cited_opposition_refs
            or self.dispute_refs
        ):
            raise ValueError("challenge finding requires cited basis")
        return self


class ArbitrationFinding(ContractModel):
    finding_id: QualifiedId
    issue_ref: QualifiedId
    thesis_refs: tuple[QualifiedId, ...]
    argument_refs: tuple[QualifiedId, ...] = ()
    disposition: ArbitrationDisposition
    rule_id: QualifiedId
    policy_id: QualifiedId
    decisive_evidence_refs: tuple[NonEmptyStr, ...] = ()
    decisive_condition_refs: tuple[QualifiedId, ...] = ()
    reason_code: NonEmptyStr
    dissent_refs: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def preserves_issue(self) -> Self:
        if not self.thesis_refs:
            raise ValueError("arbitration finding requires a thesis")
        _unique(self.thesis_refs, "arbitration thesis refs")
        return self


class ResidualUncertainty(ContractModel):
    uncertainty_id: QualifiedId
    affected_thesis_ref: QualifiedId
    affected_premise_ref: QualifiedId | None = None
    kind: UncertaintyKind
    materiality: Materiality
    consequence_code: NonEmptyStr
    resolution_requirement: NonEmptyStr
    evidence_need_refs: tuple[QualifiedId, ...] = ()


class A4Failure(ContractModel):
    failure_id: QualifiedId
    stage: FailureStage
    code: A4FailureCode
    reason_code: NonEmptyStr
    child_codes: tuple[NonEmptyStr, ...] = ()


class A4Usage(ContractModel):
    provider_calls: Literal[0] = 0
    model_calls: Literal[0] = 0
    input_tokens: Literal[0] = 0
    output_tokens: Literal[0] = 0
    model_cost_units: Literal[0] = 0
    model_cost_knowledge: Literal["KNOWN_ZERO"] = "KNOWN_ZERO"
    parent_usage_refs: tuple[NonEmptyStr, ...]
    parent_cost_knowledge: tuple[tuple[NonEmptyStr, NonEmptyStr], ...] = ()


class A4Result(ContractModel):
    schema_id: Literal["tiaf.a4.deterministic-result"] = "tiaf.a4.deterministic-result"
    schema_version: Literal["1.0"] = "1.0"
    result_id: QualifiedId
    input_projection_id: QualifiedId
    input_projection_fingerprint: Sha256
    policy_id: QualifiedId
    policy_version: NonEmptyStr
    challenge_policy_id: QualifiedId
    challenge_policy_version: NonEmptyStr
    arbitration_policy_id: QualifiedId
    arbitration_policy_version: NonEmptyStr
    primary_thesis: InvestmentThesis
    counter_thesis: InvestmentThesis | None = None
    surviving_thesis_refs: tuple[QualifiedId, ...] = ()
    premises: tuple[ArgumentPremise, ...]
    challenge_findings: tuple[ChallengeFinding, ...]
    arbitration_findings: tuple[ArbitrationFinding, ...]
    residual_uncertainties: tuple[ResidualUncertainty, ...]
    evidence_needs: tuple[A4EvidenceNeed, ...] = ()
    disposition: A4Disposition | None
    execution_status: A4ExecutionStatus
    original_a2_assessment_ref: NonEmptyStr
    original_a2_evidence_fingerprint: NonEmptyStr
    original_a3_package_ref: NonEmptyStr
    original_a3_semantic_fingerprint: Sha256
    invalidation_conditions: tuple[InvalidationCondition, ...]
    usage: A4Usage
    failures: tuple[A4Failure, ...] = ()
    semantic_fingerprint: Sha256

    @model_validator(mode="after")
    def result_relationships(self) -> Self:
        thesis_ids = {self.primary_thesis.thesis_id}
        if self.counter_thesis is not None:
            thesis_ids.add(self.counter_thesis.thesis_id)
        if not set(self.surviving_thesis_refs) <= thesis_ids:
            raise ValueError("surviving thesis reference is unresolved")
        if self.execution_status is A4ExecutionStatus.FAILED:
            if self.disposition is not None:
                raise ValueError("failed A4 execution cannot have a disposition")
        elif self.disposition is None:
            raise ValueError("non-failed A4 execution requires a disposition")
        if self.disposition is A4Disposition.SUPPORTIVE and (
            self.primary_thesis.thesis_id not in self.surviving_thesis_refs
        ):
            raise ValueError("SUPPORTIVE requires surviving primary thesis")
        if self.disposition is A4Disposition.CONFLICTED and self.counter_thesis is None:
            raise ValueError("CONFLICTED requires an explicit counter-thesis")
        premise_ids = {item.premise_id for item in self.premises}
        for thesis in (self.primary_thesis, self.counter_thesis):
            if thesis is not None and not set(thesis.premise_refs) <= premise_ids:
                raise ValueError("thesis premise reference is unresolved")
        return self


class A4RunRecord(ContractModel):
    schema_id: Literal["tiaf.a4.deterministic-run"] = "tiaf.a4.deterministic-run"
    schema_version: Literal["1.0"] = "1.0"
    run_id: QualifiedId
    input_projection: A4SemanticInputProjection
    policy: A4DeterministicPolicy
    result: A4Result
    evaluated_at: TiafDateTime
    fingerprint: Sha256


class A4Capture(ContractModel):
    schema_id: Literal["tiaf.a4.deterministic-capture"] = "tiaf.a4.deterministic-capture"
    schema_version: Literal["1.0"] = "1.0"
    capture_id: QualifiedId
    projection_json: NonEmptyStr
    projection_checksum: Sha256
    projection_fingerprint: Sha256
    run_json: NonEmptyStr
    run_checksum: Sha256
    run_fingerprint: Sha256
    exact_capture_checksum: Sha256
    captured_at: TiafDateTime


class A4ReplayResult(ContractModel):
    replay_id: QualifiedId
    mode: Literal[A4ReplayMode.RECORDED] = A4ReplayMode.RECORDED
    record: A4RunRecord
    provider_calls: Literal[0] = 0
    model_calls: Literal[0] = 0
    replayed_at: TiafDateTime
    fingerprint: Sha256


class A4VerificationResult(ContractModel):
    verification_id: QualifiedId
    mode: Literal[A4ReplayMode.DETERMINISTIC_VERIFICATION] = (
        A4ReplayMode.DETERMINISTIC_VERIFICATION
    )
    recorded_run_fingerprint: Sha256
    verified_run_fingerprint: Sha256
    exact_match: bool
    provider_calls: Literal[0] = 0
    model_calls: Literal[0] = 0
    verified_at: TiafDateTime
    fingerprint: Sha256


class A4PolicyComparison(ContractModel):
    comparison_id: QualifiedId
    mode: Literal[A4ReplayMode.POLICY_COMPARISON] = A4ReplayMode.POLICY_COMPARISON
    original_policy: tuple[QualifiedId, NonEmptyStr]
    candidate_policy: tuple[QualifiedId, NonEmptyStr]
    original_run_fingerprint: Sha256
    candidate_run_fingerprint: Sha256
    original_disposition: A4Disposition
    candidate_disposition: A4Disposition
    exact_match: bool
    compared_at: TiafDateTime
    fingerprint: Sha256
