"""Immutable contracts for the provider-neutral market-intelligence fabric."""

import hashlib
import json
from datetime import timedelta
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

from tiaf.agents import (
    AgentBudget,
    AgentCapability,
    AgentEvidenceReference,
    AgentOpinionV2,
    AgentUsage,
)
from tiaf.agents._validation import validate_safe_metadata
from tiaf.contracts import ContractModel, DataQuality, FreshnessState, Horizon
from tiaf.contracts.common import Metadata, NonEmptyStr, Symbol, TiafDateTime
from tiaf.events import NormalizedEvent
from tiaf.fundamentals import FundamentalFact
from tiaf.market_context import ContextObservation

from .authoritative_models import AuthoritativeDocumentEvidence
from .enums import (
    AvailabilityBasis,
    CapabilitySupport,
    ContradictionResolution,
    DerivationClass,
    EnrichmentAction,
    EvidenceOutputType,
    MarketIntelligenceCapability,
    PointInTimeQuality,
    ProviderFailureKind,
    ProviderResultStatus,
    RoutingMode,
    SemanticMappingQuality,
    SourceAuthority,
    authorities_for,
)

type ObservationValue = StrictStr | StrictInt | StrictFloat | StrictBool
UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


def _unique(values: tuple[object, ...], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must be unique")


class ProviderIdentity(ContractModel):
    provider_id: NonEmptyStr
    display_name: NonEmptyStr
    adapter_version: NonEmptyStr


class ProviderCapabilityConstraints(ContractModel):
    supported_markets: tuple[NonEmptyStr, ...] = ()
    supported_exchanges: tuple[NonEmptyStr, ...] = ()
    supported_instrument_types: tuple[NonEmptyStr, ...] = ()
    supported_periods: tuple[NonEmptyStr, ...] = ()
    semantic_filters: tuple[NonEmptyStr, ...] = ()
    expected_freshness: FreshnessState = FreshnessState.UNKNOWN
    maximum_age: timedelta | None = None
    maximum_historical_coverage: timedelta | None = None
    supports_historical_as_of: bool = False
    output_types: tuple[EvidenceOutputType, ...]
    source_authority: SourceAuthority = SourceAuthority.UNKNOWN
    point_in_time_quality: PointInTimeQuality = PointInTimeQuality.UNKNOWN
    revision_limitations: tuple[NonEmptyStr, ...] = ()
    maximum_records: int | None = Field(default=None, gt=0)
    cost_units_per_call: float = Field(default=0, ge=0, allow_inf_nan=False)
    rate_limit_description: NonEmptyStr | None = None
    expected_latency_class: NonEmptyStr | None = None
    cacheable: bool = True
    upstream_lineage_id: NonEmptyStr | None = None
    normalizer_id: NonEmptyStr
    normalizer_version: NonEmptyStr
    native_schema_version: NonEmptyStr
    limitations: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_constraints(self) -> Self:
        if self.maximum_age is not None and self.maximum_age.total_seconds() < 0:
            raise ValueError("maximum_age cannot be negative")
        if (
            self.maximum_historical_coverage is not None
            and self.maximum_historical_coverage.total_seconds() < 0
        ):
            raise ValueError("maximum_historical_coverage cannot be negative")
        if not self.output_types:
            raise ValueError("capability constraints require an output type")
        _unique(self.output_types, "output types")
        return self


class ProviderCapabilityDeclaration(ContractModel):
    capability: MarketIntelligenceCapability
    support: CapabilitySupport
    constraints: ProviderCapabilityConstraints | None = None
    notes: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_declaration(self) -> Self:
        if self.support is CapabilitySupport.UNSUPPORTED:
            if self.constraints is not None:
                raise ValueError("unsupported capability cannot claim constraints")
        elif self.constraints is None:
            raise ValueError("supported capability requires explicit constraints")
        return self


class ProviderManifest(ContractModel):
    identity: ProviderIdentity
    source_authority: SourceAuthority
    capabilities: tuple[ProviderCapabilityDeclaration, ...]
    read_only: bool = True
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_manifest(self) -> Self:
        if not self.read_only:
            raise ValueError("market-intelligence providers must be read-only")
        _unique(tuple(item.capability for item in self.capabilities), "capability declarations")
        if any(
            item.constraints is not None
            and item.constraints.source_authority is not self.source_authority
            for item in self.capabilities
        ):
            raise ValueError("capability source authority must match provider manifest")
        return self

    def declaration_for(
        self, capability: MarketIntelligenceCapability
    ) -> ProviderCapabilityDeclaration | None:
        return next((item for item in self.capabilities if item.capability is capability), None)


class MarketIntelligenceRequest(ContractModel):
    request_id: NonEmptyStr
    capability: MarketIntelligenceCapability
    authority: AgentCapability
    allowed_authorities: tuple[AgentCapability, ...]
    subject: Symbol
    as_of: TiafDateTime
    horizon: Horizon
    required_freshness: FreshnessState
    required_canonical_metrics: tuple[NonEmptyStr, ...] = ()
    budget: AgentBudget
    attributes: Metadata = Field(default_factory=dict)

    _safe_attributes = field_validator("attributes")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_authorization(self) -> Self:
        expected = authorities_for(self.capability)
        if self.authority not in expected:
            raise ValueError(f"{self.capability} requires coarse authority in {expected}")
        if self.authority not in self.allowed_authorities:
            raise ValueError("fine capability is outside the request authority ceiling")
        _unique(self.allowed_authorities, "allowed authorities")
        _unique(self.required_canonical_metrics, "required canonical metrics")
        return self


class ProviderNativeObservation(ContractModel):
    observation_id: NonEmptyStr
    provider_id: NonEmptyStr
    adapter_version: NonEmptyStr = "1.0"
    provider_tool: NonEmptyStr | None = None
    provider_endpoint: NonEmptyStr | None = None
    native_record_id: NonEmptyStr | None = None
    native_schema_version: NonEmptyStr = "unknown"
    capability: MarketIntelligenceCapability
    subject: Symbol
    native_field: NonEmptyStr
    native_label: NonEmptyStr
    value: ObservationValue
    unit: NonEmptyStr | None = None
    scale: NonEmptyStr | None = None
    currency: NonEmptyStr | None = None
    period_label: NonEmptyStr | None = None
    native_semantics: NonEmptyStr | None = None
    observed_at: TiafDateTime | None = None
    published_at: TiafDateTime | None = None
    available_from: TiafDateTime
    acquired_at: TiafDateTime
    availability_basis: AvailabilityBasis
    point_in_time_quality: PointInTimeQuality
    point_in_time_limitation: NonEmptyStr | None = None
    source_reference: NonEmptyStr | None = None
    source_quality: DataQuality
    revision: int = Field(default=0, ge=0)
    revision_id: NonEmptyStr | None = None
    restatement_semantics: NonEmptyStr | None = None
    payload_checksum: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")] | None = None
    content_reference: NonEmptyStr | None = None
    output_type: EvidenceOutputType
    derivation_class: DerivationClass
    lineage_observation_ids: tuple[NonEmptyStr, ...] = ()
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_provenance(self) -> Self:
        if self.acquired_at < self.available_from:
            raise ValueError("acquisition cannot predate availability")
        if self.published_at is not None and self.available_from < self.published_at:
            raise ValueError("availability cannot predate publication")
        if self.observation_id in self.lineage_observation_ids:
            raise ValueError("observation cannot cite itself as lineage")
        _unique(self.lineage_observation_ids, "lineage observation IDs")
        return self


class ProviderFailure(ContractModel):
    kind: ProviderFailureKind
    provider_id: NonEmptyStr
    capability: MarketIntelligenceCapability
    message: NonEmptyStr
    retryable: bool = False
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)


class ProviderFetchResult(ContractModel):
    provider_id: NonEmptyStr
    capability: MarketIntelligenceCapability
    status: ProviderResultStatus
    observations: tuple[ProviderNativeObservation, ...] = ()
    failures: tuple[ProviderFailure, ...] = ()
    cost_units: float = Field(default=0, ge=0, allow_inf_nan=False)
    elapsed_seconds: float = Field(default=0, ge=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if any(item.provider_id != self.provider_id for item in self.observations):
            raise ValueError("observation provider must match result provider")
        if any(item.capability is not self.capability for item in self.observations):
            raise ValueError("observation capability must match result capability")
        if self.status is ProviderResultStatus.SUCCESS and not self.observations:
            raise ValueError("successful provider result requires observations")
        if self.status not in {ProviderResultStatus.SUCCESS, ProviderResultStatus.PARTIAL}:
            if not self.failures:
                raise ValueError("unsuccessful provider result requires typed failure")
        return self


class NormalizationRecord(ContractModel):
    record_id: NonEmptyStr
    observation_id: NonEmptyStr
    provider_id: NonEmptyStr
    native_field: NonEmptyStr
    canonical_metric: NonEmptyStr | None = None
    mapping_quality: SemanticMappingQuality
    derivation_class: DerivationClass
    rule_id: NonEmptyStr
    rule_version: NonEmptyStr
    rationale: NonEmptyStr = "explicit provider mapping rule"
    conversion: NonEmptyStr | None = None
    scale_details: NonEmptyStr | None = None
    source_observation_ids: tuple[NonEmptyStr, ...] = ()
    emitted_evidence_id: NonEmptyStr | None = None
    warnings: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_mapping(self) -> Self:
        if self.mapping_quality in {
            SemanticMappingQuality.AMBIGUOUS,
            SemanticMappingQuality.PROVIDER_DEFINED,
        }:
            if self.emitted_evidence_id is not None:
                raise ValueError(
                    "ambiguous/provider-defined mapping cannot emit canonical evidence"
                )
        elif self.canonical_metric is None:
            raise ValueError("non-ambiguous mapping requires a canonical metric")
        return self


class CanonicalEvidenceProjection(ContractModel):
    """Provenance envelope for an accepted canonical fact/event/context output."""

    evidence_id: NonEmptyStr
    metric: NonEmptyStr
    value: ObservationValue
    unit: NonEmptyStr | None = None
    currency: NonEmptyStr | None = None
    period: NonEmptyStr | None = None
    available_from: TiafDateTime
    source_reference: NonEmptyStr
    provider_id: NonEmptyStr
    source_observation_id: NonEmptyStr
    mapping_quality: SemanticMappingQuality
    derivation_class: DerivationClass

    @model_validator(mode="after")
    def validate_canonical_mapping(self) -> Self:
        if self.mapping_quality not in {
            SemanticMappingQuality.EXACT,
            SemanticMappingQuality.WELL_SUPPORTED,
        }:
            raise ValueError("canonical projection requires an accepted semantic mapping")
        return self


class NormalizedEvidenceBatch(ContractModel):
    provider_id: NonEmptyStr
    capability: MarketIntelligenceCapability
    native_observations: tuple[ProviderNativeObservation, ...]
    normalization_records: tuple[NormalizationRecord, ...]
    canonical_evidence: tuple[CanonicalEvidenceProjection, ...] = ()
    fundamental_facts: tuple[FundamentalFact, ...] = ()
    normalized_events: tuple[NormalizedEvent, ...] = ()
    authoritative_documents: tuple[AuthoritativeDocumentEvidence, ...] = ()
    context_observations: tuple[ContextObservation, ...] = ()
    evidence_references: tuple[AgentEvidenceReference, ...] = ()
    gaps: tuple[ProviderFailure, ...] = ()


class ContradictionGroup(ContractModel):
    contradiction_id: NonEmptyStr
    subject: Symbol
    canonical_metric: NonEmptyStr
    period_label: NonEmptyStr | None = None
    observation_ids: tuple[NonEmptyStr, ...]
    normalization_record_ids: tuple[NonEmptyStr, ...]
    evidence_ids: tuple[NonEmptyStr, ...]
    values: tuple[ObservationValue, ...]
    mapping_qualities: tuple[SemanticMappingQuality, ...]
    provider_ids: tuple[NonEmptyStr, ...]
    resolution: ContradictionResolution = ContradictionResolution.UNRESOLVED
    authoritative_evidence_id: NonEmptyStr | None = None
    material: bool = True
    source_quality_notes: tuple[NonEmptyStr, ...] = ()
    lineage_notes: tuple[NonEmptyStr, ...] = ()
    escalation_audit_id: NonEmptyStr | None = None
    notes: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_contradiction(self) -> Self:
        if len(self.evidence_ids) < 2 or len(self.provider_ids) < 2:
            raise ValueError("contradiction requires distinct evidence and providers")
        _unique(self.observation_ids, "contradiction observation IDs")
        _unique(self.normalization_record_ids, "normalization record IDs")
        _unique(self.evidence_ids, "contradiction evidence IDs")
        _unique(self.provider_ids, "contradiction provider IDs")
        if len(self.values) != len(self.evidence_ids):
            raise ValueError("contradiction values must align with evidence IDs")
        if len(self.mapping_qualities) != len(self.evidence_ids):
            raise ValueError("mapping qualities must align with evidence IDs")
        if self.resolution is ContradictionResolution.RESOLVED_BY_AUTHORITY:
            if self.authoritative_evidence_id not in self.evidence_ids:
                raise ValueError("authoritative resolution must identify grouped evidence")
        elif self.authoritative_evidence_id is not None:
            raise ValueError("authoritative evidence is only valid for authority resolution")
        return self


class ProviderCallAudit(ContractModel):
    sequence: int = Field(gt=0)
    provider_id: NonEmptyStr
    capability: MarketIntelligenceCapability
    status: ProviderResultStatus
    observation_ids: tuple[NonEmptyStr, ...] = ()
    failure_kinds: tuple[ProviderFailureKind, ...] = ()
    cost_units: float = Field(ge=0, allow_inf_nan=False)
    elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)
    cache_reused: bool = False
    skip_reason: NonEmptyStr | None = None


class EvidenceCoverageAssessment(ContractModel):
    required_metrics: tuple[NonEmptyStr, ...]
    covered_metrics: tuple[NonEmptyStr, ...]
    missing_metrics: tuple[NonEmptyStr, ...]
    ambiguous_metrics: tuple[NonEmptyStr, ...]
    stale_metrics: tuple[NonEmptyStr, ...] = ()
    quality_limitations: tuple[NonEmptyStr, ...] = ()
    point_in_time_limitations: tuple[NonEmptyStr, ...] = ()
    contradiction_ids: tuple[NonEmptyStr, ...] = ()
    source_lineage_ids: tuple[NonEmptyStr, ...] = ()
    coverage: UnitFloat
    sufficient: bool


class EnrichmentDecision(ContractModel):
    sequence: int = Field(ge=0)
    action: EnrichmentAction
    reason: NonEmptyStr
    next_provider_id: NonEmptyStr | None = None
    policy_rule: NonEmptyStr = "deterministic-sufficiency-v1"
    expected_evidence_value: NonEmptyStr | None = None


class CapabilityRoutePolicy(ContractModel):
    policy_id: NonEmptyStr = "market-intelligence-route"
    policy_version: NonEmptyStr = "1.0"
    capability: MarketIntelligenceCapability
    mode: RoutingMode
    provider_ids: tuple[NonEmptyStr, ...]
    authoritative_provider_ids: tuple[NonEmptyStr, ...] = ()
    maximum_provider_calls: int = Field(gt=0)
    minimum_successful_providers: int = Field(default=1, gt=0)
    required_canonical_metrics: tuple[NonEmptyStr, ...] = ()
    require_authoritative_on_ambiguity: bool = True
    minimum_source_authority: SourceAuthority = SourceAuthority.UNKNOWN
    minimum_point_in_time_quality: PointInTimeQuality = PointInTimeQuality.UNKNOWN
    maximum_cost_units: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    maximum_elapsed_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    fallback_statuses: tuple[ProviderResultStatus, ...] = (
        ProviderResultStatus.UNAVAILABLE,
        ProviderResultStatus.STALE,
        ProviderResultStatus.OUT_OF_COVERAGE,
        ProviderResultStatus.RATE_LIMITED,
        ProviderResultStatus.TIMEOUT,
        ProviderResultStatus.INVALID_OUTPUT,
        ProviderResultStatus.FAILED,
    )
    stop_policy_id: NonEmptyStr = "deterministic-sufficiency-v1"

    @model_validator(mode="after")
    def validate_policy(self) -> Self:
        if not self.provider_ids:
            raise ValueError("route policy requires providers")
        _unique(self.provider_ids, "route provider IDs")
        if self.maximum_provider_calls > len(self.provider_ids):
            raise ValueError("maximum provider calls cannot exceed configured providers")
        if self.minimum_successful_providers > self.maximum_provider_calls:
            raise ValueError("minimum successes cannot exceed maximum calls")
        if not set(self.authoritative_provider_ids) <= set(self.provider_ids):
            raise ValueError("authoritative providers must belong to the route")
        return self


class MarketIntelligenceRun(ContractModel):
    run_id: NonEmptyStr
    request: MarketIntelligenceRequest
    policy: CapabilityRoutePolicy
    batches: tuple[NormalizedEvidenceBatch, ...]
    contradictions: tuple[ContradictionGroup, ...] = ()
    audits: tuple[ProviderCallAudit, ...]
    decisions: tuple[EnrichmentDecision, ...]
    coverage: EvidenceCoverageAssessment
    usage: AgentUsage
    failures: tuple[ProviderFailure, ...] = ()
    started_at: TiafDateTime
    completed_at: TiafDateTime
    fingerprint: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]

    @model_validator(mode="after")
    def validate_run(self) -> Self:
        if self.policy.capability is not self.request.capability:
            raise ValueError("route policy must match requested capability")
        if self.completed_at < self.started_at:
            raise ValueError("run completion cannot predate start")
        if self.fingerprint != self.compute_fingerprint():
            raise ValueError("run fingerprint does not match replay-visible content")
        return self

    def compute_fingerprint(self) -> str:
        payload = {
            "request": self.request.model_dump(mode="json"),
            "policy": self.policy.model_dump(mode="json"),
            "batches": [item.model_dump(mode="json") for item in self.batches],
            "contradictions": [item.model_dump(mode="json") for item in self.contradictions],
            "audits": [
                {
                    "sequence": item.sequence,
                    "provider_id": item.provider_id,
                    "capability": item.capability,
                    "status": item.status,
                    "observation_ids": item.observation_ids,
                    "failure_kinds": item.failure_kinds,
                    "cost_units": item.cost_units,
                }
                for item in self.audits
            ],
            "decisions": [item.model_dump(mode="json") for item in self.decisions],
            "coverage": self.coverage.model_dump(mode="json"),
            "failures": [item.model_dump(mode="json") for item in self.failures],
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(encoded.encode()).hexdigest()

    @classmethod
    def fingerprint_for(
        cls,
        *,
        run_id: str,
        request: MarketIntelligenceRequest,
        policy: CapabilityRoutePolicy,
        batches: tuple[NormalizedEvidenceBatch, ...],
        contradictions: tuple[ContradictionGroup, ...],
        audits: tuple[ProviderCallAudit, ...],
        decisions: tuple[EnrichmentDecision, ...],
        coverage: EvidenceCoverageAssessment,
        usage: AgentUsage,
        failures: tuple[ProviderFailure, ...],
        started_at: TiafDateTime,
        completed_at: TiafDateTime,
    ) -> str:
        provisional = cls.model_construct(
            run_id=run_id,
            request=request,
            policy=policy,
            batches=batches,
            contradictions=contradictions,
            audits=audits,
            decisions=decisions,
            coverage=coverage,
            usage=usage,
            failures=failures,
            started_at=started_at,
            completed_at=completed_at,
            fingerprint="0" * 64,
        )
        return provisional.compute_fingerprint()


class MarketIntelligenceResearchRequest(ContractModel):
    """One bounded multi-capability evidence request issued by a research planner."""

    research_request_id: NonEmptyStr
    subject: Symbol
    as_of: TiafDateTime
    horizon: Horizon
    capability_requests: tuple[MarketIntelligenceRequest, ...]
    budget: AgentBudget

    @model_validator(mode="after")
    def validate_capability_requests(self) -> Self:
        if not self.capability_requests:
            raise ValueError("research request requires at least one capability")
        _unique(
            tuple(item.capability for item in self.capability_requests),
            "research request capabilities",
        )
        for item in self.capability_requests:
            if item.subject != self.subject or item.as_of != self.as_of:
                raise ValueError("capability requests must share research subject and as-of")
            if item.horizon != self.horizon:
                raise ValueError("capability requests must share research horizon")
        if sum(item.budget.max_tool_calls for item in self.capability_requests) > (
            self.budget.max_tool_calls
        ):
            raise ValueError("capability call budgets exceed the research budget")
        if sum(item.budget.max_cost_units for item in self.capability_requests) > (
            self.budget.max_cost_units
        ):
            raise ValueError("capability cost budgets exceed the research budget")
        return self


class MarketIntelligenceResearchPolicy(ContractModel):
    plan_id: NonEmptyStr
    plan_version: NonEmptyStr
    routes: tuple[CapabilityRoutePolicy, ...]

    @model_validator(mode="after")
    def validate_routes(self) -> Self:
        if not self.routes:
            raise ValueError("research policy requires capability routes")
        _unique(tuple(item.capability for item in self.routes), "research policy capabilities")
        return self

    def route_for(self, capability: MarketIntelligenceCapability) -> CapabilityRoutePolicy:
        route = next((item for item in self.routes if item.capability is capability), None)
        if route is None:
            raise LookupError(f"no route configured for {capability}")
        return route


class MarketIntelligenceResearchRun(ContractModel):
    research_run_id: NonEmptyStr
    request: MarketIntelligenceResearchRequest
    policy: MarketIntelligenceResearchPolicy
    capability_runs: tuple[MarketIntelligenceRun, ...]
    usage: AgentUsage
    fingerprint: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]

    @model_validator(mode="after")
    def validate_research_run(self) -> Self:
        expected = tuple(item.capability for item in self.request.capability_requests)
        actual = tuple(item.request.capability for item in self.capability_runs)
        if actual != expected:
            raise ValueError("research run must preserve requested capability order")
        if self.fingerprint != self.compute_fingerprint():
            raise ValueError("research run fingerprint does not match capability runs")
        return self

    def compute_fingerprint(self) -> str:
        payload = {
            "request": self.request.model_dump(mode="json"),
            "policy": self.policy.model_dump(mode="json"),
            "capability_run_fingerprints": [item.fingerprint for item in self.capability_runs],
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode()).hexdigest()

    @classmethod
    def fingerprint_for(
        cls,
        request: MarketIntelligenceResearchRequest,
        policy: MarketIntelligenceResearchPolicy,
        capability_runs: tuple[MarketIntelligenceRun, ...],
    ) -> str:
        payload = {
            "request": request.model_dump(mode="json"),
            "policy": policy.model_dump(mode="json"),
            "capability_run_fingerprints": [item.fingerprint for item in capability_runs],
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode()).hexdigest()


class AmbiguousEvidenceProjection(ContractModel):
    """Bounded native-semantic evidence retained for synthesis without raw payloads."""

    observation_id: NonEmptyStr
    provider_id: NonEmptyStr
    native_field: NonEmptyStr
    value: ObservationValue
    mapping_quality: SemanticMappingQuality
    available_from: TiafDateTime
    source_reference: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_ambiguity(self) -> Self:
        if self.mapping_quality not in {
            SemanticMappingQuality.PROVIDER_DEFINED,
            SemanticMappingQuality.AMBIGUOUS,
        }:
            raise ValueError("ambiguous projection must retain a non-canonical mapping")
        return self


class MarketIntelligenceSynthesisContext(ContractModel):
    """Safe optional-reasoning input: normalized evidence only, never native payloads."""

    context_id: NonEmptyStr
    subject: Symbol
    as_of: TiafDateTime
    horizon: Horizon
    canonical_evidence: tuple[CanonicalEvidenceProjection, ...]
    fundamental_facts: tuple[FundamentalFact, ...] = ()
    normalized_events: tuple[NormalizedEvent, ...] = ()
    context_observations: tuple[ContextObservation, ...] = ()
    evidence_references: tuple[AgentEvidenceReference, ...] = ()
    normalization_records: tuple[NormalizationRecord, ...]
    ambiguous_observation_ids: tuple[NonEmptyStr, ...]
    ambiguous_evidence: tuple[AmbiguousEvidenceProjection, ...]
    contradictions: tuple[ContradictionGroup, ...]
    graph_node_ids: tuple[NonEmptyStr, ...] = ()
    graph_edge_ids: tuple[NonEmptyStr, ...] = ()
    research_component_ids: tuple[NonEmptyStr, ...] = ()
    evidence_gaps: tuple[ProviderFailure, ...] = ()
    prior_opinions: tuple[AgentOpinionV2, ...] = ()
    a2_evidence_fingerprint: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    allowed_authorities: tuple[AgentCapability, ...]
    budget: AgentBudget
    output_schema_id: NonEmptyStr
    authority_constraints: tuple[NonEmptyStr, ...]

    @model_validator(mode="after")
    def validate_ambiguous_references(self) -> Self:
        projected_ids = tuple(item.observation_id for item in self.ambiguous_evidence)
        if projected_ids != self.ambiguous_observation_ids:
            raise ValueError("ambiguous evidence must align with its observation IDs")
        return self
