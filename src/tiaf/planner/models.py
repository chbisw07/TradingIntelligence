"""Immutable orchestration control contracts, never an investment verdict."""

from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from tiaf.agents import (
    AgentBudget,
    AgentCapability,
    AgentEvidencePack,
    AgentEvidenceReference,
    AgentOpinionV2,
    AgentRunRecord,
    AgentUsage,
    AnalysisMode,
    ModelTier,
    SpecialistCapability,
    SpecialistId,
)
from tiaf.context import AnalysisPurpose
from tiaf.contracts import ContractModel, EvidenceType, Horizon, TradeStyle
from tiaf.contracts.common import NonEmptyStr, Symbol, TiafDateTime
from tiaf.data import InstrumentType
from tiaf.market_intelligence import ResearchDepth

from .digests import digest

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class Intent(StrEnum):
    LIVE = "LIVE"
    CAPTURED = "CAPTURED"
    REPLAY = "REPLAY"


class Disposition(StrEnum):
    RECOVERABLE = "RECOVERABLE"
    UNSUPPORTED = "UNSUPPORTED"
    NOT_WORTH_COST = "NOT_WORTH_COST"
    BUDGET_BLOCKED = "BUDGET_BLOCKED"
    PERMISSION_DENIED = "PERMISSION_DENIED"


class NodeStatus(StrEnum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    REUSED = "REUSED"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    SUPERSEDED = "SUPERSEDED"


class StopReason(StrEnum):
    TERMINAL_FAILURE = "TERMINAL_FAILURE"
    DEADLINE_EXCEEDED = "DEADLINE_EXCEEDED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    ABSTENTION_ACCEPTED = "ABSTENTION_ACCEPTED"
    DEPTH_LIMIT = "DEPTH_LIMIT"
    UNSUPPORTED_REMAINING = "UNSUPPORTED_REMAINING"
    NO_USEFUL_NEW_EVIDENCE = "NO_USEFUL_NEW_EVIDENCE"
    REQUIRED_WORK_COMPLETE = "REQUIRED_WORK_COMPLETE"
    EVIDENCE_SUFFICIENT = "EVIDENCE_SUFFICIENT"


class OrchestrationBounds(ContractModel):
    max_specialists: int = Field(default=9, ge=1, le=9)
    concurrency: int = Field(default=3, ge=1, le=3)
    max_enrichment_rounds: int = Field(default=2, ge=0, le=2)
    max_replans: int = Field(default=2, ge=0, le=2)
    max_attempts_per_specialist: int = Field(default=2, ge=1, le=2)
    max_invocations: int = Field(default=18, ge=1, le=18)
    max_provider_calls: int = Field(default=0, ge=0)
    max_graph_nodes: int = Field(default=32, ge=1)
    max_graph_edges: int = Field(default=64, ge=0)


class InstrumentContext(ContractModel):
    symbol: Symbol
    instrument_type: InstrumentType
    underlying: Symbol | None = None
    underlying_type: InstrumentType | None = None
    expiry: TiafDateTime | None = None
    fno_eligible: bool | None = None
    eligibility_reference: NonEmptyStr | None = None
    benchmark_reference: NonEmptyStr | None = None
    sector_reference: NonEmptyStr | None = None

    @model_validator(mode="after")
    def attributed(self) -> Self:
        if self.fno_eligible is not None and self.eligibility_reference is None:
            raise ValueError("known F&O eligibility requires an attributable reference")
        if (self.underlying is None) != (self.underlying_type is None):
            raise ValueError("underlying identity and type must be supplied together")
        return self


class EvidenceInventory(ContractModel):
    inventory_id: NonEmptyStr
    a2_pack: AgentEvidencePack
    references: tuple[AgentEvidenceReference, ...] = ()
    normalized_run_ids: tuple[NonEmptyStr, ...] = ()
    prior_run_ids: tuple[NonEmptyStr, ...] = ()
    confirmation_ids: tuple[NonEmptyStr, ...] = ()
    graph_ids: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def unique(self) -> Self:
        refs = (*self.a2_pack.references, *self.references)
        if len({r.evidence_id for r in refs}) != len(refs):
            raise ValueError("duplicate inventory evidence ID")
        if any(r.subject != self.a2_pack.subject for r in refs):
            raise ValueError("inventory subject mismatch")
        return self

    def all_references(self) -> tuple[AgentEvidenceReference, ...]:
        return (*self.a2_pack.references, *self.references)


class OrchestrationRequest(ContractModel):
    request_id: NonEmptyStr
    run_id: NonEmptyStr
    correlation_id: NonEmptyStr | None = None
    instrument: InstrumentContext
    purpose: AnalysisPurpose = AnalysisPurpose.OPPORTUNITY
    trade_style: TradeStyle = TradeStyle.POSITIONAL
    horizon: Horizon
    inventory: EvidenceInventory
    analysis_mode: AnalysisMode = AnalysisMode.DETERMINISTIC_ONLY
    research_depth: ResearchDepth = ResearchDepth.L1_BASIC_CONTEXT
    permit_deep_research: bool = False
    permit_confirmation: bool = False
    include_macro: bool = False
    allowed_capabilities: tuple[AgentCapability, ...] = (AgentCapability.READ_A2_EVIDENCE,)
    budget: AgentBudget = Field(default_factory=AgentBudget)
    bounds: OrchestrationBounds = Field(default_factory=OrchestrationBounds)
    no_llm: bool = True
    allowed_model_tiers: tuple[ModelTier, ...] = (ModelTier.NONE,)
    max_model_tier: ModelTier = ModelTier.NONE
    as_of: TiafDateTime
    deadline: TiafDateTime | None = None
    intent: Intent = Intent.CAPTURED
    replay_source_run_id: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        subject = self.instrument.underlying or self.instrument.symbol
        if self.inventory.a2_pack.subject != subject:
            raise ValueError("A2 subject must match explicit analysis subject")
        if not self.inventory.a2_pack.analysis_context_ids:
            raise ValueError("orchestration requires captured A2 context identity")
        if AgentCapability.READ_A2_EVIDENCE not in self.allowed_capabilities:
            raise ValueError("A2 read authority required")
        if len(set(self.allowed_capabilities)) != len(self.allowed_capabilities):
            raise ValueError("duplicate capability")
        if not self.no_llm or self.max_model_tier != ModelTier.NONE:
            raise ValueError("A3.8 deterministic planner supports no-LLM execution only")
        if self.allowed_model_tiers != (ModelTier.NONE,):
            raise ValueError("no-LLM policy forbids model tiers")
        if self.deadline is not None and self.deadline <= self.as_of:
            raise ValueError("deadline must follow as-of")
        if self.intent is Intent.REPLAY and not self.replay_source_run_id:
            raise ValueError("replay requires source run identity")
        for ref in self.inventory.all_references():
            if ref.observed_at is not None and ref.observed_at > self.as_of:
                raise ValueError("evidence observed after as-of")
            if ref.acquired_at is not None and ref.acquired_at > self.as_of:
                raise ValueError("uncaptured future acquisition is not point-in-time eligible")
        ids = {r.evidence_id for r in self.inventory.all_references()}
        for ref_id in (
            self.instrument.eligibility_reference,
            self.instrument.benchmark_reference,
            self.instrument.sector_reference,
        ):
            if ref_id is not None and ref_id not in ids:
                raise ValueError("instrument context reference is not captured")
        return self

    @property
    def subject(self) -> str:
        return self.instrument.underlying or self.instrument.symbol


class SpecialistDependencySpec(ContractModel):
    capability: SpecialistCapability
    policy_version: Literal["1.0"] = "1.0"
    hard_evidence: tuple[EvidenceType, ...]
    optional_evidence: tuple[EvidenceType, ...] = ()
    upstream: tuple[SpecialistId, ...] = ()
    required: bool = True
    include_baseline_facts: bool = True
    required_metrics: tuple[NonEmptyStr, ...] = ()
    required_metadata: tuple[NonEmptyStr, ...] = ()


class PlanNode(ContractModel):
    node_id: NonEmptyStr
    specialist: SpecialistId
    dependencies: tuple[NonEmptyStr, ...] = ()
    required: bool
    evidence_types: tuple[EvidenceType, ...]


class SkippedSpecialist(ContractModel):
    specialist: SpecialistId
    reason: NonEmptyStr
    unresolved: bool = False


class EvidenceTaskPlan(ContractModel):
    task_id: NonEmptyStr
    kind: Literal["ACQUIRE", "CONFIRM", "RESEARCH"]
    consumers: tuple[NonEmptyStr, ...]
    prerequisites: tuple[NonEmptyStr, ...] = ()
    evidence_type: EvidenceType | None = None
    reason: NonEmptyStr
    conditional: bool = True


class AnalysisPlan(ContractModel):
    plan_id: NonEmptyStr
    version: int = Field(ge=1)
    parent_version: int | None = None
    request_digest: Sha256
    planner_version: Literal["1.0"] = "1.0"
    policy_version: Literal["1.0"] = "1.0"
    registry: tuple[SpecialistDependencySpec, ...]
    nodes: tuple[PlanNode, ...]
    skipped: tuple[SkippedSpecialist, ...]
    waves: tuple[tuple[NonEmptyStr, ...], ...]
    bounds: OrchestrationBounds
    evidence_tasks: tuple[EvidenceTaskPlan, ...] = ()
    specialist_budget: AgentBudget = Field(default_factory=AgentBudget)

    @model_validator(mode="after")
    def valid_dag(self) -> Self:
        ids = tuple(n.node_id for n in self.nodes)
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate node ID")
        if self.parent_version != (self.version - 1 if self.version > 1 else None):
            raise ValueError("invalid plan lineage")
        flat = tuple(n for wave in self.waves for n in wave)
        if len(flat) != len(ids) or set(flat) != set(ids):
            raise ValueError("waves must contain every node exactly once")
        seen: set[str] = set()
        nodes = {n.node_id: n for n in self.nodes}
        for wave in self.waves:
            if not wave or len(wave) > self.bounds.concurrency:
                raise ValueError("invalid wave width")
            for node_id in wave:
                if not set(nodes[node_id].dependencies) <= seen:
                    raise ValueError("cycle, missing dependency, or invalid completion barrier")
            seen.update(wave)
        return self


class PlanDecision(ContractModel):
    sequence: int = Field(ge=1)
    action: NonEmptyStr
    reason: NonEmptyStr
    rule_version: Literal["1.0"] = "1.0"
    trigger_ids: tuple[NonEmptyStr, ...] = ()
    affected_nodes: tuple[NonEmptyStr, ...] = ()
    expected_coverage: tuple[NonEmptyStr, ...] = ()
    disposition: Disposition | None = None


class Reservation(ContractModel):
    accounting_id: NonEmptyStr
    budget: AgentBudget
    provider_calls: int = Field(default=0, ge=0)
    actual: AgentUsage | None = None
    actual_provider_calls: int | None = Field(default=None, ge=0)
    state: Literal["OUTSTANDING", "SETTLED", "UNKNOWN"] = "OUTSTANDING"


class NodeAttempt(ContractModel):
    node_id: NonEmptyStr
    plan_version: int
    status: NodeStatus
    input_digest: Sha256
    consumed_digest: Sha256
    consumed_ids: tuple[NonEmptyStr, ...]
    record: AgentRunRecord | None = None
    reason: str | None = None
    superseded: bool = False
    started_at: TiafDateTime | None = None
    completed_at: TiafDateTime | None = None


class NodeOutcome(ContractModel):
    node_id: NonEmptyStr
    status: NodeStatus
    required: bool
    reason: str | None = None
    run_record_id: NonEmptyStr | None = None


class OrchestrationResult(ContractModel):
    run_id: NonEmptyStr
    status: Literal["COMPLETE", "PARTIAL", "INSUFFICIENT_EVIDENCE", "ABSTAIN"]
    opinions: tuple[AgentOpinionV2, ...]
    a2_reference: NonEmptyStr
    a2_fingerprint: NonEmptyStr
    gaps: tuple[NonEmptyStr, ...]
    conflicts: tuple[NonEmptyStr, ...]
    stop_reasons: tuple[StopReason, ...]
    usage: AgentUsage
    provider_calls: int
    research_ids: tuple[NonEmptyStr, ...] = ()
    confirmation_ids: tuple[NonEmptyStr, ...] = ()
    graph_ids: tuple[NonEmptyStr, ...] = ()
    skipped: tuple[SkippedSpecialist, ...] = ()
    usage_is_complete: bool = True
    held_usage: AgentUsage = Field(default_factory=AgentUsage)
    held_provider_calls: int = Field(default=0, ge=0)
    outcomes: tuple[NodeOutcome, ...] = ()

    @property
    def primary_stop(self) -> StopReason:
        return self.stop_reasons[0]


class CapturedArtifact(ContractModel):
    artifact_id: NonEmptyStr
    kind: NonEmptyStr
    canonical_json: NonEmptyStr
    checksum: Sha256

    @model_validator(mode="after")
    def intact(self) -> Self:
        if digest(self.canonical_json) != self.checksum:
            raise ValueError("captured artifact checksum mismatch")
        return self
