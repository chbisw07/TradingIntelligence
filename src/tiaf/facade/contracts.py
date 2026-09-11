"""Immutable contracts for local capability discovery, admission and results."""

from typing import Literal, Self

from pydantic import Field, model_validator

from tiaf.a3_hardening import A3ReplayResult, A3VerificationResult
from tiaf.baseline import DeterministicBaselineRequest, OpportunityAssessment
from tiaf.context import AnalysisPurpose
from tiaf.contracts import ContractModel, Horizon
from tiaf.contracts.common import NonEmptyStr, Symbol, TiafDateTime
from tiaf.planner.models import Sha256
from tiaf.service.opportunity_intelligence import StructuredOpportunityIntelligence
from tiaf.source_semantics import A4SemanticInputProjection
from tiaf.source_semantics.contracts import QualifiedId

from .enums import (
    ArtifactKind,
    CapabilityAvailability,
    CostKnowledge,
    EffectClass,
    FacadeAuthorityScope,
    FacadeStatus,
    InterfaceLevel,
    ReplayResultKind,
    ReplaySupport,
)


class InvocationBudget(ContractModel):
    max_tool_calls: int = Field(default=0, ge=0)
    max_model_calls: int = Field(default=0, ge=0)
    max_input_tokens: int = Field(default=0, ge=0)
    max_output_tokens: int = Field(default=0, ge=0)
    max_cost_units: int = Field(default=0, ge=0)
    max_elapsed_seconds: float = Field(default=30.0, gt=0, allow_inf_nan=False)

    def intersect(self, *others: "InvocationBudget") -> "InvocationBudget":
        values = (self, *others)
        return InvocationBudget(
            max_tool_calls=min(item.max_tool_calls for item in values),
            max_model_calls=min(item.max_model_calls for item in values),
            max_input_tokens=min(item.max_input_tokens for item in values),
            max_output_tokens=min(item.max_output_tokens for item in values),
            max_cost_units=min(item.max_cost_units for item in values),
            max_elapsed_seconds=min(item.max_elapsed_seconds for item in values),
        )


class CapabilityDescriptor(ContractModel):
    capability_id: NonEmptyStr
    capability_version: Literal["1.0"] = "1.0"
    interface_level: InterfaceLevel
    request_schema_id: QualifiedId
    request_schema_version: Literal["1.0"] = "1.0"
    result_schema_id: QualifiedId
    result_schema_version: Literal["1.0"] = "1.0"
    effect: EffectClass
    deterministic: bool
    model_supported: bool
    replay_support: ReplaySupport
    required_authority_scope: FacadeAuthorityScope
    cost_knowledge: CostKnowledge
    availability: CapabilityAvailability = CapabilityAvailability.AVAILABLE
    deprecated: bool = False
    replacement_capability_id: NonEmptyStr | None = None

    @model_validator(mode="after")
    def replacement_rules(self) -> Self:
        if self.deprecated != (self.replacement_capability_id is not None):
            raise ValueError("deprecated capability requires exactly one replacement")
        return self


class CallerGrant(ContractModel):
    caller_id: QualifiedId
    grant_id: QualifiedId
    allowed_capabilities: tuple[NonEmptyStr, ...]
    authority_scopes: tuple[FacadeAuthorityScope, ...]
    authority_refs: tuple[QualifiedId, ...]
    entitlement_refs: tuple[QualifiedId, ...] = ()
    allowed_profiles: tuple[QualifiedId, ...]
    engineering_allowed: bool = False
    live_allowed: bool = False
    model_allowed: bool = False
    budget_ceiling: InvocationBudget = Field(default_factory=InvocationBudget)


class OperatorPolicy(ContractModel):
    policy_id: QualifiedId
    policy_version: NonEmptyStr
    allowed_capabilities: tuple[NonEmptyStr, ...]
    authority_scopes: tuple[FacadeAuthorityScope, ...]
    authority_refs: tuple[QualifiedId, ...]
    entitlement_refs: tuple[QualifiedId, ...] = ()
    allowed_profiles: tuple[QualifiedId, ...]
    engineering_enabled: bool = False
    live_enabled: bool = False
    model_enabled: bool = False
    budget_ceiling: InvocationBudget = Field(default_factory=InvocationBudget)
    model_policy_ref: QualifiedId = "model-policy:no-llm"


class TrustedArtifact(ContractModel):
    artifact_ref: QualifiedId
    kind: ArtifactKind
    content: NonEmptyStr
    checksum: Sha256
    required_authority_refs: tuple[QualifiedId, ...] = ()
    required_entitlement_refs: tuple[QualifiedId, ...] = ()


class TrustedFacadeConfig(ContractModel):
    operator: OperatorPolicy
    caller_grants: tuple[CallerGrant, ...]
    artifacts: tuple[TrustedArtifact, ...] = ()
    artifact_root_ref: QualifiedId
    single_writer: Literal[True] = True

    @model_validator(mode="after")
    def unique_startup_identity(self) -> Self:
        caller_ids = tuple(item.caller_id for item in self.caller_grants)
        artifact_refs = tuple(item.artifact_ref for item in self.artifacts)
        if len(caller_ids) != len(set(caller_ids)):
            raise ValueError("caller grants must have unique caller IDs")
        if len(artifact_refs) != len(set(artifact_refs)):
            raise ValueError("artifacts must have unique logical references")
        return self


class InvocationScope(ContractModel):
    request_id: NonEmptyStr
    correlation_id: NonEmptyStr
    subject: Symbol
    objective: AnalysisPurpose
    horizon: Horizon
    as_of: TiafDateTime
    profile_ref: QualifiedId
    requested_authority_ref: QualifiedId
    requested_budget: InvocationBudget = Field(default_factory=InvocationBudget)
    position_context_ref: QualifiedId | None = None
    admitted_artifact_refs: tuple[QualifiedId, ...] = ()


class FacadeOperationRequest(ContractModel):
    capability_id: NonEmptyStr
    scope: InvocationScope


class BaselineAssessRequest(FacadeOperationRequest):
    capability_id: Literal["baseline.assess"] = "baseline.assess"
    baseline_request: DeterministicBaselineRequest

    @model_validator(mode="after")
    def scope_matches_baseline(self) -> Self:
        if (
            self.scope.subject != self.baseline_request.subject
            or self.scope.horizon != self.baseline_request.horizon
            or self.scope.as_of != self.baseline_request.requested_at
            or self.scope.objective is not AnalysisPurpose.OPPORTUNITY
            or self.scope.admitted_artifact_refs
        ):
            raise ValueError("facade scope must match baseline request identity")
        return self


class OpportunityAssembleRequest(FacadeOperationRequest):
    capability_id: Literal["opportunity.assemble"] = "opportunity.assemble"
    orchestration_capture_ref: QualifiedId

    @model_validator(mode="after")
    def capture_is_admitted(self) -> Self:
        if self.scope.admitted_artifact_refs != (self.orchestration_capture_ref,):
            raise ValueError("opportunity scope must identify exactly its capture reference")
        return self


class A4InputProjectRequest(FacadeOperationRequest):
    capability_id: Literal["a4_input.project"] = "a4_input.project"
    build_input_ref: QualifiedId

    @model_validator(mode="after")
    def input_is_admitted(self) -> Self:
        if self.scope.admitted_artifact_refs != (self.build_input_ref,):
            raise ValueError("projection scope must identify exactly its input reference")
        return self


class RecordedReplayRequest(FacadeOperationRequest):
    capability_id: Literal["replay.recorded"] = "replay.recorded"
    artifact_ref: QualifiedId

    @model_validator(mode="after")
    def artifact_is_admitted(self) -> Self:
        if self.scope.admitted_artifact_refs != (self.artifact_ref,):
            raise ValueError("replay scope must identify exactly its artifact reference")
        return self


class ReplayVerifyRequest(FacadeOperationRequest):
    capability_id: Literal["replay.verify"] = "replay.verify"
    artifact_ref: QualifiedId

    @model_validator(mode="after")
    def artifact_is_admitted(self) -> Self:
        if self.scope.admitted_artifact_refs != (self.artifact_ref,):
            raise ValueError("verification scope must identify exactly its artifact reference")
        return self


class CapabilityListRequest(ContractModel):
    capability_id: Literal["capabilities.list"] = "capabilities.list"
    request_id: NonEmptyStr
    correlation_id: NonEmptyStr
    profile_ref: QualifiedId
    requested_authority_ref: QualifiedId


class EffectiveAdmission(ContractModel):
    admission_id: QualifiedId
    caller_id: QualifiedId
    caller_grant_id: QualifiedId
    operator_policy_id: QualifiedId
    operator_policy_version: NonEmptyStr
    capability_id: NonEmptyStr
    capability_version: NonEmptyStr
    authority_scope: FacadeAuthorityScope
    effective_authority_ref: QualifiedId
    effective_entitlement_refs: tuple[QualifiedId, ...]
    profile_ref: QualifiedId
    effective_budget: InvocationBudget
    model_policy_ref: QualifiedId
    effect: EffectClass
    admitted_at: TiafDateTime


class InvocationUsage(ContractModel):
    tool_calls: int = Field(default=0, ge=0)
    model_calls: int = Field(default=0, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    cost_units: int = Field(default=0, ge=0)
    cost_knowledge: CostKnowledge = CostKnowledge.KNOWN_ZERO
    elapsed_seconds: float = Field(default=0, ge=0, allow_inf_nan=False)


class InvocationMetadata(ContractModel):
    request_id: NonEmptyStr
    run_id: QualifiedId
    correlation_id: NonEmptyStr
    capability_id: NonEmptyStr
    capability_version: NonEmptyStr
    status: FacadeStatus
    subject: Symbol | None = None
    objective: AnalysisPurpose | None = None
    horizon: Horizon | None = None
    as_of: TiafDateTime | None = None
    profile_ref: QualifiedId
    effective_authority_ref: QualifiedId
    budget_ref: QualifiedId
    model_policy_ref: QualifiedId
    position_context_ref: QualifiedId | None = None
    operator_policy_ref: QualifiedId
    operator_policy_version: NonEmptyStr
    effect: EffectClass
    admitted_artifact_refs: tuple[QualifiedId, ...] = ()
    policy_refs: tuple[tuple[NonEmptyStr, NonEmptyStr], ...] = ()
    warnings: tuple[NonEmptyStr, ...] = ()
    gaps: tuple[NonEmptyStr, ...] = ()
    usage: InvocationUsage
    created_at: TiafDateTime
    started_at: TiafDateTime
    completed_at: TiafDateTime


class CapabilityListResult(ContractModel):
    schema_id: Literal["tiaf.facade.capability-list-result"] = (
        "tiaf.facade.capability-list-result"
    )
    schema_version: Literal["1.0"] = "1.0"
    metadata: InvocationMetadata
    capabilities: tuple[CapabilityDescriptor, ...]


class BaselineAssessResult(ContractModel):
    schema_id: Literal["tiaf.facade.baseline-assess-result"] = (
        "tiaf.facade.baseline-assess-result"
    )
    schema_version: Literal["1.0"] = "1.0"
    metadata: InvocationMetadata
    assessment: OpportunityAssessment


class OpportunityAssembleResult(ContractModel):
    schema_id: Literal["tiaf.facade.opportunity-assemble-result"] = (
        "tiaf.facade.opportunity-assemble-result"
    )
    schema_version: Literal["1.0"] = "1.0"
    metadata: InvocationMetadata
    intelligence: StructuredOpportunityIntelligence
    run_fingerprint: Sha256
    capture_checksum: Sha256


class A4InputProjectResult(ContractModel):
    schema_id: Literal["tiaf.facade.a4-input-project-result"] = (
        "tiaf.facade.a4-input-project-result"
    )
    schema_version: Literal["1.0"] = "1.0"
    metadata: InvocationMetadata
    projection: A4SemanticInputProjection


class RecordedReplayResult(ContractModel):
    schema_id: Literal["tiaf.facade.recorded-replay-result"] = (
        "tiaf.facade.recorded-replay-result"
    )
    schema_version: Literal["1.0"] = "1.0"
    metadata: InvocationMetadata
    kind: ReplayResultKind
    a3_replay: A3ReplayResult | None = None
    foundation_projection: A4SemanticInputProjection | None = None

    @model_validator(mode="after")
    def exactly_one_result(self) -> Self:
        if (self.a3_replay is None) == (self.foundation_projection is None):
            raise ValueError("recorded replay requires exactly one typed result")
        return self


class ReplayVerifyResult(ContractModel):
    schema_id: Literal["tiaf.facade.replay-verify-result"] = (
        "tiaf.facade.replay-verify-result"
    )
    schema_version: Literal["1.0"] = "1.0"
    metadata: InvocationMetadata
    verification: A3VerificationResult


class FacadeErrorRecord(ContractModel):
    schema_id: Literal["tiaf.facade.error"] = "tiaf.facade.error"
    schema_version: Literal["1.0"] = "1.0"
    request_id: NonEmptyStr
    correlation_id: NonEmptyStr
    capability_id: NonEmptyStr
    status: FacadeStatus
    message: NonEmptyStr
    child_codes: tuple[NonEmptyStr, ...] = ()
    occurred_at: TiafDateTime


type FacadeRequest = (
    BaselineAssessRequest
    | OpportunityAssembleRequest
    | A4InputProjectRequest
    | RecordedReplayRequest
    | ReplayVerifyRequest
)
type FacadeResult = (
    BaselineAssessResult
    | OpportunityAssembleResult
    | A4InputProjectResult
    | RecordedReplayResult
    | ReplayVerifyResult
)
