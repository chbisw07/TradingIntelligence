"""Immutable contracts for local capability discovery, admission and results."""

from typing import Literal, Self

from pydantic import Field, model_validator

from tiaf.a3_hardening import A3ReplayResult, A3VerificationResult
from tiaf.a4 import A4Result as DeterministicA4Result
from tiaf.a5 import A5ReplayResult, PositionIntelligenceResult
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
    CapabilityDependencyKind,
    CapabilityDiscoveryState,
    CapabilityEntitlement,
    CapabilityReadinessState,
    CapabilityRegistrationState,
    CapabilitySemanticRole,
    CostKnowledge,
    EffectClass,
    FacadeAuthorityScope,
    FacadeStatus,
    InterfaceLevel,
    MonitoringCompatibility,
    PluggabilityLevel,
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


class CapabilityDependency(ContractModel):
    dependency_id: QualifiedId
    kind: CapabilityDependencyKind
    version_specifier: NonEmptyStr


class CapabilityDiscoveryDescriptor(CapabilityDescriptor):
    """Versioned, non-binding discovery declaration for one facade capability."""

    descriptor_schema_version: Literal["1.0"] = "1.0"
    descriptor_id: QualifiedId
    semantic_role: CapabilitySemanticRole
    pluggability_level: PluggabilityLevel
    replaceable: bool
    composable: bool
    required_dependencies: tuple[CapabilityDependency, ...] = ()
    optional_dependencies: tuple[CapabilityDependency, ...] = ()
    required_authorities: tuple[FacadeAuthorityScope, ...]
    required_entitlements: tuple[CapabilityEntitlement, ...] = ()
    registration_state: CapabilityRegistrationState = CapabilityRegistrationState.REGISTERED
    discovery_state: CapabilityDiscoveryState = CapabilityDiscoveryState.REGISTERED
    readiness_state: CapabilityReadinessState = (
        CapabilityReadinessState.REQUIRES_RUNTIME_CHECK
    )
    monitoring_compatibility: MonitoringCompatibility
    limitations: tuple[QualifiedId, ...]

    @model_validator(mode="after")
    def deterministic_discovery_identity(self) -> Self:
        expected_id = f"descriptor:{self.capability_id}/{self.capability_version}"
        if self.descriptor_id != expected_id:
            raise ValueError("descriptor ID must match capability identity and version")
        if self.required_authorities != (self.required_authority_scope,):
            raise ValueError("discovery authority metadata must match invocation scope")
        required = tuple(
            (item.kind.value, item.dependency_id, item.version_specifier)
            for item in self.required_dependencies
        )
        optional = tuple(
            (item.kind.value, item.dependency_id, item.version_specifier)
            for item in self.optional_dependencies
        )
        if required != tuple(sorted(set(required))):
            raise ValueError("required dependencies must be unique and sorted")
        if optional != tuple(sorted(set(optional))):
            raise ValueError("optional dependencies must be unique and sorted")
        if set(required) & set(optional):
            raise ValueError("a dependency cannot be both required and optional")
        entitlements = tuple(item.value for item in self.required_entitlements)
        if entitlements != tuple(sorted(set(entitlements))):
            raise ValueError("required entitlements must be unique and sorted")
        if self.limitations != tuple(sorted(set(self.limitations))):
            raise ValueError("limitations must be unique and sorted")
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


class A4EvaluateRequest(FacadeOperationRequest):
    capability_id: Literal["a4.evaluate"] = "a4.evaluate"
    projection_capture_ref: QualifiedId

    @model_validator(mode="after")
    def projection_is_admitted(self) -> Self:
        if self.scope.admitted_artifact_refs != (self.projection_capture_ref,):
            raise ValueError("A4 scope must identify exactly its projection capture")
        return self


class PositionAssessRequest(FacadeOperationRequest):
    """Assess one authorized, captured A5 request through its logical reference."""

    capability_id: Literal["position.assess"] = "position.assess"
    position_request_ref: QualifiedId

    @model_validator(mode="after")
    def position_request_is_admitted(self) -> Self:
        if self.scope.admitted_artifact_refs != (self.position_request_ref,):
            raise ValueError("position scope must identify exactly its request artifact")
        if self.scope.position_context_ref != self.position_request_ref:
            raise ValueError("position context must be the admitted logical request reference")
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
    schema_version: Literal["1.0", "1.1"] = "1.1"
    metadata: InvocationMetadata
    capabilities: tuple[CapabilityDescriptor, ...]
    discovery_metadata: tuple[CapabilityDiscoveryDescriptor, ...] = ()

    @model_validator(mode="after")
    def discovery_matches_legacy_catalog(self) -> Self:
        capability_ids = tuple(item.capability_id for item in self.capabilities)
        if capability_ids != tuple(sorted(set(capability_ids))):
            raise ValueError("capabilities must be unique and sorted")
        discovery_ids = tuple(item.capability_id for item in self.discovery_metadata)
        if self.schema_version == "1.0":
            if discovery_ids:
                raise ValueError("legacy capability-list result cannot contain R2 metadata")
            return self
        if discovery_ids != capability_ids:
            raise ValueError("R2 discovery metadata must exactly cover visible capabilities")
        for descriptor, discovery in zip(
            self.capabilities, self.discovery_metadata, strict=True
        ):
            discovery_only = set(CapabilityDiscoveryDescriptor.model_fields) - set(
                CapabilityDescriptor.model_fields
            )
            legacy = discovery.model_dump(exclude=discovery_only)
            if CapabilityDescriptor.model_validate(legacy) != descriptor:
                raise ValueError("R2 discovery metadata must preserve legacy descriptor fields")
            if discovery.discovery_state is not CapabilityDiscoveryState.DISCOVERABLE:
                raise ValueError("visible R2 metadata must be marked DISCOVERABLE")
        return self


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


class A4EvaluateResult(ContractModel):
    schema_id: Literal["tiaf.facade.a4-evaluate-result"] = (
        "tiaf.facade.a4-evaluate-result"
    )
    schema_version: Literal["1.0"] = "1.0"
    metadata: InvocationMetadata
    evaluation: DeterministicA4Result
    run_fingerprint: Sha256


class PositionAssessResult(ContractModel):
    schema_id: Literal["tiaf.facade.position-assess-result"] = (
        "tiaf.facade.position-assess-result"
    )
    schema_version: Literal["1.0"] = "1.0"
    metadata: InvocationMetadata
    assessment: PositionIntelligenceResult
    run_fingerprint: Sha256
    position_request_checksum: Sha256
    monitoring_statement: Literal["ADVISORY_MONITORING_INTENT_ONLY_NOT_SCHEDULED"] = (
        "ADVISORY_MONITORING_INTENT_ONLY_NOT_SCHEDULED"
    )


class RecordedReplayResult(ContractModel):
    schema_id: Literal["tiaf.facade.recorded-replay-result"] = (
        "tiaf.facade.recorded-replay-result"
    )
    schema_version: Literal["1.0"] = "1.0"
    metadata: InvocationMetadata
    kind: ReplayResultKind
    a3_replay: A3ReplayResult | None = None
    foundation_projection: A4SemanticInputProjection | None = None
    a5_replay: A5ReplayResult | None = None

    @model_validator(mode="after")
    def exactly_one_result(self) -> Self:
        values = (self.a3_replay, self.foundation_projection, self.a5_replay)
        if sum(item is not None for item in values) != 1:
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
    | A4EvaluateRequest
    | PositionAssessRequest
    | RecordedReplayRequest
    | ReplayVerifyRequest
)
type FacadeResult = (
    BaselineAssessResult
    | OpportunityAssembleResult
    | A4InputProjectResult
    | A4EvaluateResult
    | PositionAssessResult
    | RecordedReplayResult
    | ReplayVerifyResult
)
