"""Portable contracts for one governed A4 evidence-enrichment round."""

from typing import Any, Literal, Self

from pydantic import Field, model_validator

from tiaf.a4 import A4EvidenceCapability, A4EvidenceNeed, A4RunRecord
from tiaf.agents import AgentBudget, AgentCapability, AgentUsage
from tiaf.contracts import ContractModel, EvidenceType
from tiaf.contracts.common import NonEmptyStr, TiafDateTime
from tiaf.planner.digests import digest
from tiaf.planner.models import OrchestrationRequest, Sha256
from tiaf.source_semantics import (
    A4SemanticInputProjection,
    ProjectionBuildInput,
    SourceEntityRole,
)
from tiaf.workflows import OrchestrationRunRecord

from .enums import (
    EnrichmentStopReason,
    EvidenceCaptureStatus,
    EvidenceChangeKind,
    EvidenceNeedAdmissionOutcome,
    FindingLineageState,
    WorkflowAdapter,
)


class EvidenceBridgePolicy(ContractModel):
    policy_id: NonEmptyStr = "a4-enrichment-policy:deterministic"
    policy_version: NonEmptyStr = "1.0"
    bridge_id: NonEmptyStr = "a4-planner-bridge:1"
    bridge_version: NonEmptyStr = "1.0"
    max_enrichment_rounds: Literal[1] = 1
    max_successor_cycles: Literal[1] = 1
    supported_capabilities: tuple[A4EvidenceCapability, ...] = tuple(A4EvidenceCapability)

    @model_validator(mode="after")
    def unique_capabilities(self) -> Self:
        if len(set(self.supported_capabilities)) != len(self.supported_capabilities):
            raise ValueError("bridge policy capabilities must be unique")
        return self


class EvidenceBridgeGrant(ContractModel):
    grant_id: NonEmptyStr
    authority_refs: tuple[NonEmptyStr, ...]
    source_roles: tuple[SourceEntityRole, ...]
    capabilities: tuple[A4EvidenceCapability, ...]
    entitlement_refs: tuple[NonEmptyStr, ...]
    profile_refs: tuple[NonEmptyStr, ...]
    budget_refs: tuple[NonEmptyStr, ...]
    budget: AgentBudget
    max_provider_calls: int = Field(ge=0, le=1)
    deadline: TiafDateTime | None = None
    permit_live_read: bool = False
    processed_dedupe_keys: tuple[Sha256, ...] = ()
    resolved_need_ids: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def bounded_and_unique(self) -> Self:
        for values, label in (
            (self.authority_refs, "authority refs"),
            (self.source_roles, "source roles"),
            (self.capabilities, "capabilities"),
            (self.entitlement_refs, "entitlements"),
            (self.profile_refs, "profiles"),
            (self.budget_refs, "budget refs"),
            (self.processed_dedupe_keys, "processed dedupe keys"),
            (self.resolved_need_ids, "resolved need IDs"),
        ):
            if len(set(values)) != len(values):
                raise ValueError(f"duplicate {label}")
        return self


class EvidenceNeedAdmission(ContractModel):
    admission_id: NonEmptyStr
    evidence_need_id: NonEmptyStr
    parent_a4_run_id: NonEmptyStr
    outcome: EvidenceNeedAdmissionOutcome
    reason_code: NonEmptyStr
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    grant_id: NonEmptyStr
    admitted_budget: AgentBudget | None = None
    admitted_provider_calls: int = Field(default=0, ge=0, le=1)
    decided_at: TiafDateTime
    fingerprint: Sha256

    @property
    def admitted(self) -> bool:
        return self.outcome is EvidenceNeedAdmissionOutcome.ADMITTED

    @model_validator(mode="after")
    def decision_shape(self) -> Self:
        if self.admitted != (self.admitted_budget is not None):
            raise ValueError("only admitted needs carry an executable budget")
        if not self.admitted and self.admitted_provider_calls:
            raise ValueError("denied need cannot reserve provider calls")
        identity = digest(
            self.model_dump(
                mode="json", exclude={"admission_id": True, "fingerprint": True}
            )
        )
        if self.admission_id != f"a4-need-admission:{identity[:24]}":
            raise ValueError("evidence-need admission ID mismatch")
        expected = digest(self.model_dump(mode="json", exclude={"fingerprint": True}))
        if self.fingerprint != expected:
            raise ValueError("evidence-need admission fingerprint mismatch")
        return self


class A4PlannerBridgePlan(ContractModel):
    plan_ref: NonEmptyStr
    evidence_need_id: NonEmptyStr
    admission_fingerprint: Sha256
    semantic_capability: A4EvidenceCapability
    planner_capabilities: tuple[AgentCapability, ...]
    evidence_type: EvidenceType
    orchestration_request: OrchestrationRequest
    bridge_id: NonEmptyStr
    bridge_version: NonEmptyStr
    enrichment_round: Literal[1] = 1
    successor_cycle: Literal[1] = 1
    fingerprint: Sha256

    @model_validator(mode="after")
    def intact(self) -> Self:
        identity = digest(
            self.model_dump(mode="json", exclude={"plan_ref": True, "fingerprint": True})
        )
        if self.plan_ref != f"a4-planner-plan:{identity[:24]}":
            raise ValueError("A4 Planner bridge plan ID mismatch")
        expected = digest(self.model_dump(mode="json", exclude={"fingerprint": True}))
        if self.fingerprint != expected:
            raise ValueError("A4 Planner bridge plan fingerprint mismatch")
        return self


class EvidenceRoundExecution(ContractModel):
    execution_id: NonEmptyStr
    plan_ref: NonEmptyStr
    adapter: WorkflowAdapter
    workflow_record: OrchestrationRunRecord | None = None
    status: Literal["COMPLETED", "FAILED"]
    failure_codes: tuple[NonEmptyStr, ...] = ()
    usage: AgentUsage
    provider_calls: int = Field(ge=0, le=1)
    started_at: TiafDateTime
    completed_at: TiafDateTime
    fingerprint: Sha256

    @model_validator(mode="after")
    def honest_execution(self) -> Self:
        if self.completed_at < self.started_at:
            raise ValueError("execution completed before it started")
        if self.status == "COMPLETED" and self.workflow_record is None:
            raise ValueError("completed execution requires the A3.8 workflow record")
        if self.status == "FAILED" and not self.failure_codes:
            raise ValueError("failed execution requires a failure code")
        if self.usage.llm_calls or self.usage.input_tokens or self.usage.output_tokens:
            raise ValueError("A4.2 forbids model usage")
        identity = digest(
            self.model_dump(
                mode="json", exclude={"execution_id": True, "fingerprint": True}
            )
        )
        if self.execution_id != f"a4-enrichment-execution:{identity[:24]}":
            raise ValueError("A4 enrichment execution ID mismatch")
        expected = digest(self.model_dump(mode="json", exclude={"fingerprint": True}))
        if self.fingerprint != expected:
            raise ValueError("A4 enrichment execution fingerprint mismatch")
        return self


class SuccessorEvidenceCapture(ContractModel):
    capture_id: NonEmptyStr
    evidence_need_id: NonEmptyStr
    workflow_run_fingerprint: Sha256
    status: EvidenceCaptureStatus
    change_kind: EvidenceChangeKind
    successor_input: ProjectionBuildInput | None = None
    new_evidence_ids: tuple[NonEmptyStr, ...] = ()
    reused_evidence_ids: tuple[NonEmptyStr, ...] = ()
    affected_challenge_refs: tuple[NonEmptyStr, ...] = ()
    resolved_gap_ids: tuple[NonEmptyStr, ...] = ()
    workflow_evidence_crosswalk: tuple[tuple[NonEmptyStr, NonEmptyStr], ...] = ()
    genuinely_new: bool
    independent: bool | None = None
    relevant: bool
    live_acquisition: bool = False
    acquired_at: TiafDateTime
    usage: AgentUsage
    failure_codes: tuple[NonEmptyStr, ...] = ()
    information_fingerprint: Sha256
    fingerprint: Sha256

    @model_validator(mode="after")
    def honest_capture(self) -> Self:
        is_new = self.status in {
            EvidenceCaptureStatus.NEW_INFORMATION,
            EvidenceCaptureStatus.PARTIAL,
        }
        if is_new and (not self.genuinely_new or not self.new_evidence_ids):
            raise ValueError("new-information capture requires genuinely new evidence IDs")
        if self.status is EvidenceCaptureStatus.NO_NEW_INFORMATION and (
            self.genuinely_new or self.new_evidence_ids or self.successor_input is not None
        ):
            raise ValueError("no-new-information capture cannot fabricate a successor")
        if self.status is EvidenceCaptureStatus.FAILED and not self.failure_codes:
            raise ValueError("failed capture requires a failure code")
        if self.successor_input is not None and (
            tuple(sorted(self.successor_input.new_evidence_ids))
            != tuple(sorted(self.new_evidence_ids))
        ):
            raise ValueError("capture and successor new evidence IDs differ")
        if self.usage.llm_calls or self.usage.input_tokens or self.usage.output_tokens:
            raise ValueError("A4.2 evidence capture cannot contain model usage")
        identity = digest(
            self.model_dump(
                mode="json", exclude={"capture_id": True, "fingerprint": True}
            )
        )
        if self.capture_id != f"a4-successor-evidence:{identity[:24]}":
            raise ValueError("successor evidence capture ID mismatch")
        expected = digest(self.model_dump(mode="json", exclude={"fingerprint": True}))
        if self.fingerprint != expected:
            raise ValueError("successor evidence capture fingerprint mismatch")
        return self


class FindingLineage(ContractModel):
    parent_finding_ref: NonEmptyStr | None = None
    successor_finding_ref: NonEmptyStr | None = None
    family: NonEmptyStr
    reason_code: NonEmptyStr
    state: FindingLineageState


class A4EnrichmentOutcome(ContractModel):
    outcome_id: NonEmptyStr
    parent_a4_run_id: NonEmptyStr
    parent_a4_result_id: NonEmptyStr
    parent_projection_id: NonEmptyStr
    evidence_need_id: NonEmptyStr
    admission: EvidenceNeedAdmission
    bridge_plan: A4PlannerBridgePlan | None = None
    execution: EvidenceRoundExecution | None = None
    evidence_capture: SuccessorEvidenceCapture | None = None
    successor_projection: A4SemanticInputProjection | None = None
    successor_a4_run: A4RunRecord | None = None
    finding_lineage: tuple[FindingLineage, ...] = ()
    stop_reason: EnrichmentStopReason
    original_disposition: NonEmptyStr
    final_disposition: NonEmptyStr
    enrichment_rounds: int = Field(ge=0, le=1)
    successor_cycles: int = Field(ge=0, le=1)
    provider_calls: int = Field(ge=0, le=1)
    usage: AgentUsage
    failure_codes: tuple[NonEmptyStr, ...] = ()
    completed_at: TiafDateTime
    fingerprint: Sha256

    @model_validator(mode="after")
    def bounded_lineage(self) -> Self:
        successor_fields = (self.successor_projection, self.successor_a4_run)
        if any(item is None for item in successor_fields) != all(
            item is None for item in successor_fields
        ):
            raise ValueError("successor projection and A4 run must appear together")
        if self.successor_a4_run is not None and (
            self.successor_a4_run.input_projection != self.successor_projection
        ):
            raise ValueError("successor A4 run does not evaluate successor projection")
        if self.enrichment_rounds > 1 or self.successor_cycles > 1:
            raise ValueError("A4.2 is bounded to one enrichment and successor cycle")
        if self.usage.llm_calls or self.usage.input_tokens or self.usage.output_tokens:
            raise ValueError("A4.2 outcome cannot contain model usage")
        identity = digest(
            self.model_dump(
                mode="json", exclude={"outcome_id": True, "fingerprint": True}
            )
        )
        if self.outcome_id != f"a4-enrichment-outcome:{identity[:24]}":
            raise ValueError("A4 enrichment outcome ID mismatch")
        expected = digest(self.model_dump(mode="json", exclude={"fingerprint": True}))
        if self.fingerprint != expected:
            raise ValueError("A4 enrichment outcome fingerprint mismatch")
        return self


class A4EnrichmentChain(ContractModel):
    schema_id: Literal["tiaf.a4.enrichment-chain"] = "tiaf.a4.enrichment-chain"
    parent_run: A4RunRecord
    evidence_need: A4EvidenceNeed
    grant: EvidenceBridgeGrant
    policy: EvidenceBridgePolicy
    outcome: A4EnrichmentOutcome
    fingerprint: Sha256

    @classmethod
    def seal(cls, **fields: Any) -> Self:
        provisional = cls.model_construct(fingerprint="0" * 64, **fields)
        value = provisional.model_dump(mode="python")
        value["fingerprint"] = digest(
            provisional.model_dump(mode="json", exclude={"fingerprint"})
        )
        return cls.model_validate(value)

    @model_validator(mode="after")
    def intact(self) -> Self:
        expected = digest(self.model_dump(mode="json", exclude={"fingerprint"}))
        if self.fingerprint != expected:
            raise ValueError("A4 enrichment chain fingerprint mismatch")
        if self.evidence_need.parent_a4_run_id != self.parent_run.run_id:
            raise ValueError("evidence need parent run mismatch")
        if self.outcome.parent_a4_run_id != self.parent_run.run_id:
            raise ValueError("outcome parent run mismatch")
        return self


class A4EnrichmentCapture(ContractModel):
    capture_id: NonEmptyStr
    chain_json: NonEmptyStr
    chain_checksum: Sha256
    chain_fingerprint: Sha256
    captured_at: TiafDateTime


class A4EnrichmentReplayResult(ContractModel):
    replay_id: NonEmptyStr
    chain: A4EnrichmentChain
    provider_calls: Literal[0] = 0
    model_calls: Literal[0] = 0
    replayed_at: TiafDateTime
    fingerprint: Sha256


class A4EnrichmentVerificationResult(ContractModel):
    verification_id: NonEmptyStr
    recorded_fingerprint: Sha256
    verified_fingerprint: Sha256
    exact_match: bool
    provider_calls: Literal[0] = 0
    model_calls: Literal[0] = 0
    verified_at: TiafDateTime
    fingerprint: Sha256


class A4EnrichmentPolicyComparison(ContractModel):
    comparison_id: NonEmptyStr
    original_policy: tuple[NonEmptyStr, NonEmptyStr]
    candidate_policy: tuple[NonEmptyStr, NonEmptyStr]
    original_admission_fingerprint: Sha256
    candidate_admission_fingerprint: Sha256
    exact_match: bool
    compared_at: TiafDateTime
    fingerprint: Sha256
