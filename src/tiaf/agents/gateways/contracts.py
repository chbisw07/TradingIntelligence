"""Immutable provider-neutral gateway requests, results, and audit records."""

from typing import Annotated, Literal, Self

from pydantic import Field, JsonValue, field_validator, model_validator

from tiaf.agents._validation import require_unique, validate_no_secrets, validate_safe_metadata
from tiaf.agents.budget import AgentBudget, AgentUsage
from tiaf.agents.enums import AgentCapability, SpecialistId
from tiaf.agents.evidence import AgentEvidencePack, AgentEvidenceReference
from tiaf.agents.models import AgentFailure, ReasoningField, ReasoningModelIdentity
from tiaf.context import AnalysisPurpose
from tiaf.contracts import ContractModel, DataQuality, EvidenceType, FreshnessState, Horizon
from tiaf.contracts.common import Metadata, NonEmptyStr, Symbol, TiafDateTime
from tiaf.data import InstrumentType

from .enums import (
    AuthorizationDecision,
    EvidenceGatewayStatus,
    GatewayCacheStatus,
    ModelCapability,
    ModelTier,
    ReasoningGatewayStatus,
)

NonNegativeFiniteFloat = Annotated[float, Field(ge=0, allow_inf_nan=False)]
PositiveFiniteFloat = Annotated[float, Field(gt=0, allow_inf_nan=False)]
Temperature = Annotated[float, Field(ge=0, le=2, allow_inf_nan=False)]


class GatewayIdentity(ContractModel):
    """Stable identity of a controlled gateway implementation."""

    gateway_id: NonEmptyStr
    gateway_version: NonEmptyStr


class EvidenceGatewayRequest(ContractModel):
    """One semantic evidence read with no arbitrary transport escape hatch."""

    schema_version: Literal["1.0"] = "1.0"
    request_id: NonEmptyStr
    capability: AgentCapability
    allowed_capabilities: tuple[AgentCapability, ...]
    subject: Symbol
    instrument_type: InstrumentType
    horizon: Horizon
    purpose: AnalysisPurpose
    evidence_type: EvidenceType
    requested_attributes: tuple[NonEmptyStr, ...] = ()
    as_of: TiafDateTime
    required_freshness: FreshnessState
    start_at: TiafDateTime | None = None
    end_at: TiafDateTime | None = None
    context_references: tuple[NonEmptyStr, ...] = ()
    evidence_fingerprint: NonEmptyStr | None = None
    deterministic_baseline_reference: NonEmptyStr | None = None
    requesting_specialist: SpecialistId
    correlation_id: NonEmptyStr | None = None
    budget: AgentBudget
    timeout_seconds: PositiveFiniteFloat
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        require_unique(self.allowed_capabilities, "allowed capabilities")
        require_unique(self.requested_attributes, "requested attributes")
        require_unique(self.context_references, "context references")
        if (self.start_at is None) != (self.end_at is None):
            raise ValueError("evidence time range requires both bounds")
        if self.start_at is not None and self.end_at is not None:
            if self.end_at <= self.start_at:
                raise ValueError("evidence end_at must follow start_at")
            if self.end_at > self.as_of:
                raise ValueError("evidence time range cannot extend beyond as_of")
        return self


class EvidenceGatewayContext(ContractModel):
    """Bounded invocation context supplied to an authorized gateway."""

    authorized_capabilities: tuple[AgentCapability, ...]
    remaining_budget: AgentBudget
    invoked_at: TiafDateTime
    deadline_at: TiafDateTime


class EvidenceGatewayResult(ContractModel):
    """Typed evidence outcome that preserves the accepted A2 pack unchanged."""

    schema_version: Literal["1.0"] = "1.0"
    request_id: NonEmptyStr
    capability: AgentCapability
    subject: Symbol
    status: EvidenceGatewayStatus
    gateway_identity: GatewayIdentity
    evidence_pack: AgentEvidencePack | None = None
    evidence_fingerprint: NonEmptyStr | None = None
    source_timestamps: tuple[TiafDateTime, ...] = ()
    acquired_at: TiafDateTime | None = None
    produced_at: TiafDateTime
    valid_until: TiafDateTime | None = None
    freshness: FreshnessState | None = None
    quality: DataQuality | None = None
    cache_status: GatewayCacheStatus = GatewayCacheStatus.NOT_CACHEABLE
    usage: AgentUsage = Field(default_factory=AgentUsage)
    warnings: tuple[NonEmptyStr, ...] = ()
    failure: AgentFailure | None = None
    retry_after: TiafDateTime | None = None
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        require_unique(self.source_timestamps, "source timestamps")
        require_unique(self.warnings, "warnings")
        factual = {
            EvidenceGatewayStatus.SUCCESS,
            EvidenceGatewayStatus.PARTIAL,
            EvidenceGatewayStatus.STALE,
        }
        if self.status in factual:
            if (
                self.evidence_pack is None
                or self.evidence_fingerprint is None
                or self.freshness is None
                or self.quality is None
                or self.acquired_at is None
                or self.failure is not None
            ):
                raise ValueError("factual gateway result requires evidence provenance")
            if self.evidence_pack.subject != self.subject:
                raise ValueError("gateway evidence subject must match result")
            if self.evidence_pack.evidence_fingerprint != self.evidence_fingerprint:
                raise ValueError("gateway evidence fingerprint must be preserved")
            if self.status is EvidenceGatewayStatus.STALE:
                if self.freshness is not FreshnessState.STALE:
                    raise ValueError("STALE result requires STALE freshness")
            elif self.freshness is FreshnessState.STALE:
                raise ValueError("STALE freshness requires STALE status")
        elif self.evidence_pack is not None:
            raise ValueError("non-factual gateway result cannot expose evidence")
        failure_statuses = {
            EvidenceGatewayStatus.BUDGET_EXCEEDED,
            EvidenceGatewayStatus.TIMEOUT,
            EvidenceGatewayStatus.UNAUTHORIZED_CAPABILITY,
            EvidenceGatewayStatus.INVALID_REQUEST,
            EvidenceGatewayStatus.INVALID_OUTPUT,
            EvidenceGatewayStatus.FAILED,
        }
        if self.status in failure_statuses and self.failure is None:
            raise ValueError("gateway failure status requires sanitized failure")
        if self.status not in failure_statuses and self.failure is not None:
            raise ValueError("non-failure gateway status cannot carry failure")
        if self.status is EvidenceGatewayStatus.DEFERRED:
            if self.retry_after is None:
                raise ValueError("DEFERRED result requires retry_after")
        elif self.retry_after is not None:
            raise ValueError("retry_after is valid only for DEFERRED results")
        if self.acquired_at is not None and self.acquired_at > self.produced_at:
            raise ValueError("produced_at cannot predate evidence acquisition")
        return self


class EvidenceGatewayAuditRecord(ContractModel):
    """Replayable audit of one evidence authorization/invocation decision."""

    schema_version: Literal["1.0"] = "1.0"
    gateway_run_id: NonEmptyStr
    request_id: NonEmptyStr
    capability: AgentCapability
    gateway_identity: GatewayIdentity
    subject: Symbol
    evidence_fingerprint: NonEmptyStr | None = None
    authorization: AuthorizationDecision
    cache_status: GatewayCacheStatus
    status: EvidenceGatewayStatus
    usage: AgentUsage
    latency_seconds: NonNegativeFiniteFloat
    started_at: TiafDateTime
    completed_at: TiafDateTime
    failure: AgentFailure | None = None
    correlation_id: NonEmptyStr | None = None


class EvidenceGatewayRun(ContractModel):
    """Result plus its immutable audit record."""

    result: EvidenceGatewayResult
    audit: EvidenceGatewayAuditRecord

    @model_validator(mode="after")
    def validate_projection(self) -> Self:
        result, audit = self.result, self.audit
        if (
            result.request_id != audit.request_id
            or result.capability is not audit.capability
            or result.gateway_identity != audit.gateway_identity
            or result.status is not audit.status
            or result.cache_status is not audit.cache_status
            or result.usage != audit.usage
            or result.failure != audit.failure
        ):
            raise ValueError("gateway audit must exactly project its result")
        return self


class ReasoningGatewayRequest(ContractModel):
    """One schema-bound reasoning task with explicit authority and budget."""

    schema_version: Literal["1.0"] = "1.0"
    reasoning_request_id: NonEmptyStr
    run_id: NonEmptyStr
    specialist: SpecialistId
    specialist_version: NonEmptyStr
    subject: Symbol
    horizon: Horizon
    task: NonEmptyStr
    instructions: tuple[ReasoningField, ...]
    evidence_references: tuple[AgentEvidenceReference, ...]
    evidence_fingerprint: NonEmptyStr
    requested_model_tier: ModelTier
    allowed_model_capabilities: tuple[ModelCapability, ...]
    budget: AgentBudget
    prompt_version: NonEmptyStr
    policy_version: NonEmptyStr
    output_schema_id: NonEmptyStr
    estimated_input_tokens: int = Field(ge=0)
    temperature: Temperature | None = None
    timeout_seconds: PositiveFiniteFloat
    correlation_id: NonEmptyStr | None = None
    created_at: TiafDateTime
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_reasoning_request(self) -> Self:
        if not self.instructions:
            raise ValueError("reasoning request requires structured instructions")
        if not self.evidence_references:
            raise ValueError("reasoning request requires evidence references")
        require_unique(tuple(item.name for item in self.instructions), "instruction fields")
        require_unique(
            tuple(item.evidence_id for item in self.evidence_references),
            "reasoning evidence references",
        )
        require_unique(self.allowed_model_capabilities, "allowed model capabilities")
        if any(item.subject != self.subject for item in self.evidence_references):
            raise ValueError("reasoning evidence must match request subject")
        validate_no_secrets(self.model_dump(mode="json", exclude={"metadata"}))
        return self


class ReasoningGatewayResult(ContractModel):
    """Provider-neutral structured reasoning result and true observed usage."""

    schema_version: Literal["1.0"] = "1.0"
    response_id: NonEmptyStr
    reasoning_request_id: NonEmptyStr
    status: ReasoningGatewayStatus
    requested_model_tier: ModelTier
    actual_model_tier: ModelTier
    provider_identity: ReasoningModelIdentity | None = None
    fields: tuple[ReasoningField, ...] = ()
    usage: AgentUsage = Field(default_factory=AgentUsage)
    finish_reason: NonEmptyStr | None = None
    prompt_version: NonEmptyStr
    policy_version: NonEmptyStr
    specialist_version: NonEmptyStr
    model_configuration: tuple[ReasoningField, ...] = ()
    downgrade_reason: NonEmptyStr | None = None
    cache_key: NonEmptyStr | None = None
    warnings: tuple[NonEmptyStr, ...] = ()
    failure: AgentFailure | None = None
    produced_at: TiafDateTime

    @model_validator(mode="after")
    def validate_reasoning_result(self) -> Self:
        require_unique(tuple(item.name for item in self.fields), "reasoning output fields")
        require_unique(
            tuple(item.name for item in self.model_configuration),
            "model configuration fields",
        )
        require_unique(self.warnings, "reasoning warnings")
        if self.status is ReasoningGatewayStatus.SUCCESS:
            if not self.fields or self.provider_identity is None or self.failure is not None:
                raise ValueError("successful reasoning requires model output and identity")
        elif self.fields:
            raise ValueError("non-successful reasoning cannot expose accepted output")
        failure_statuses = {
            ReasoningGatewayStatus.UNAVAILABLE,
            ReasoningGatewayStatus.BUDGET_EXCEEDED,
            ReasoningGatewayStatus.TIMEOUT,
            ReasoningGatewayStatus.UNAUTHORIZED_CAPABILITY,
            ReasoningGatewayStatus.INVALID_REQUEST,
            ReasoningGatewayStatus.MODEL_OUTPUT_INVALID,
            ReasoningGatewayStatus.PROVIDER_FAILURE,
            ReasoningGatewayStatus.FAILED,
        }
        if self.status in failure_statuses and self.failure is None:
            raise ValueError("reasoning failure status requires sanitized failure")
        if self.status not in failure_statuses and self.failure is not None:
            raise ValueError("non-failure reasoning status cannot carry failure")
        if self.actual_model_tier is ModelTier.NONE and self.provider_identity is not None:
            raise ValueError("NONE tier cannot claim a provider identity")
        if self.actual_model_tier is not self.requested_model_tier:
            if self.downgrade_reason is None:
                raise ValueError("tier change requires an explicit downgrade reason")
        elif self.downgrade_reason is not None:
            raise ValueError("unchanged tier cannot claim a downgrade")
        return self


class ReasoningGatewayAuditRecord(ContractModel):
    """Replayable model-selection, budget, usage, and failure record."""

    schema_version: Literal["1.0"] = "1.0"
    gateway_run_id: NonEmptyStr
    gateway_identity: GatewayIdentity
    reasoning_request_id: NonEmptyStr
    provider_id: NonEmptyStr | None = None
    model_id: NonEmptyStr | None = None
    model_version: NonEmptyStr | None = None
    requested_model_tier: ModelTier
    actual_model_tier: ModelTier
    prompt_version: NonEmptyStr
    policy_version: NonEmptyStr
    specialist_version: NonEmptyStr
    evidence_fingerprint: NonEmptyStr
    status: ReasoningGatewayStatus
    usage: AgentUsage
    latency_seconds: NonNegativeFiniteFloat
    started_at: TiafDateTime
    completed_at: TiafDateTime
    failure: AgentFailure | None = None
    correlation_id: NonEmptyStr | None = None


class ReasoningGatewayRun(ContractModel):
    """Reasoning result plus its immutable audit record."""

    result: ReasoningGatewayResult
    audit: ReasoningGatewayAuditRecord

    @model_validator(mode="after")
    def validate_projection(self) -> Self:
        result, audit = self.result, self.audit
        identity = result.provider_identity
        if (
            result.reasoning_request_id != audit.reasoning_request_id
            or result.requested_model_tier is not audit.requested_model_tier
            or result.actual_model_tier is not audit.actual_model_tier
            or result.prompt_version != audit.prompt_version
            or result.policy_version != audit.policy_version
            or result.specialist_version != audit.specialist_version
            or result.status is not audit.status
            or result.usage != audit.usage
            or result.failure != audit.failure
            or (identity.provider_id if identity else None) != audit.provider_id
            or (identity.model_id if identity else None) != audit.model_id
            or (identity.model_version if identity else None) != audit.model_version
        ):
            raise ValueError("reasoning audit must exactly project its result")
        return self


JsonObject = dict[str, JsonValue]
