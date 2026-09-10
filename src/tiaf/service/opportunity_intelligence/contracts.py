"""Immutable observation products, deliberately without investment-action fields."""

from enum import StrEnum
from typing import Literal, Self

from pydantic import Field, model_validator

from tiaf.agents import AgentConfidence, AgentStance, AgentUsage, SpecialistId
from tiaf.baseline.enums import BaselineDirection, CandidateClass
from tiaf.baseline.models import OpportunityAssessment as BaselineAssessment
from tiaf.context import AnalysisPurpose
from tiaf.contracts import ContractModel, DataQuality, FreshnessState, Horizon, TradeStyle
from tiaf.contracts.common import NonEmptyStr, Symbol, TiafDateTime
from tiaf.data import InstrumentType
from tiaf.planner.digests import digest
from tiaf.planner.models import Sha256


class CaptureIntegrityError(ValueError):
    """Invalid captured handoff, not a market-evidence insufficiency."""


class Truth(StrEnum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"


class OpportunityState(StrEnum):
    OPPORTUNITY = "OPPORTUNITY"
    WATCH = "WATCH"
    WAIT = "WAIT"
    AVOID = "AVOID"
    NO_TRADE = "NO_TRADE"
    CONFLICTED = "CONFLICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class FieldMapping(ContractModel):
    specialist: SpecialistId
    field: NonEmptyStr
    values: tuple[NonEmptyStr, ...]
    effect: Literal["SUPPORT", "COMPANY_CONFLICT", "QUALIFICATION", "CHASE", "TIMING"]


class OpportunitySynthesisPolicy(ContractModel):
    policy_id: Literal["a3.9-observation-v1"] = "a3.9-observation-v1"
    version: Literal["1.0"] = "1.0"
    mappings: tuple[FieldMapping, ...]
    directional_fields: tuple[str, ...] = ("TECHNICAL.stance",)
    core: tuple[SpecialistId, ...] = (
        SpecialistId.TECHNICAL,
        SpecialistId.OPPORTUNITY_QUALITY,
        SpecialistId.OPPORTUNITY_RISK,
    )
    usable_quality: tuple[DataQuality, ...] = (DataQuality.GOOD, DataQuality.PARTIAL)
    usable_freshness: tuple[FreshnessState, ...] = (FreshnessState.FRESH, FreshnessState.AGING)
    rule_order: tuple[str, ...] = (
        "CORE_UNUSABLE",
        "UNRESOLVED_CONFLICT",
        "CRITICAL_RISK",
        "TIMING_RESTRICTION",
        "BASELINE_NO_TRADE",
        "SUPPORTED_SETUP",
        "QUALIFIED_SUPPORT",
        "NO_SUPPORTED_SETUP",
    )


class OpportunityIntelligenceRequest(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    request_id: NonEmptyStr
    capture_json: NonEmptyStr
    capture_checksum: Sha256
    policy: OpportunitySynthesisPolicy


class SourceLocator(ContractModel):
    specialist: SpecialistId | None = None
    opinion_id: str | None = None
    run_id: str | None = None
    schema_id: str | None = None
    field: NonEmptyStr
    claim_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    fact_ids: tuple[str, ...] = ()
    artifact_ids: tuple[str, ...] = ()


class Facet(ContractModel):
    field: NonEmptyStr
    value: NonEmptyStr
    usable: Truth
    source: SourceLocator


class SpecialistContribution(ContractModel):
    specialist: SpecialistId
    role: Literal["FIRST_ORDER", "DOWNSTREAM_SUMMARY"]
    applicability: Literal["APPLICABLE", "NOT_APPLICABLE", "UNKNOWN"]
    required: bool
    outcome: str
    reason: str | None = None
    opinion_id: str | None = None
    run_id: str | None = None
    specialist_version: str | None = None
    policy_version: str | None = None
    input_digest: str | None = None
    stance: AgentStance | None = None
    usable: Truth = Truth.UNKNOWN
    facets: tuple[Facet, ...] = ()
    confidence: AgentConfidence | None = None
    confidence_basis: tuple[str, ...] = ()
    quality: DataQuality | None = None
    freshness: FreshnessState | None = None
    baseline_agreement: str | None = None
    evidence_ids: tuple[str, ...] = ()
    missing_ids: tuple[str, ...] = ()
    material_missing_ids: tuple[str, ...] = ()
    reason_codes: tuple[str, ...] = ()


class BaselineView(ContractModel):
    assessment_id: str
    evidence_fingerprint: str
    availability: Literal["CAPTURED_PROJECTION", "MISSING_CONTENT"]
    direction: BaselineDirection | None = None
    candidate_class: CandidateClass | None = None
    opportunity_score: float | None = Field(default=None, ge=0, le=100, allow_inf_nan=False)
    eligible: bool | None = None
    eligibility_basis: Literal["CAPTURED", "NOT_CAPTURED"] = "NOT_CAPTURED"
    evidence_ids: tuple[str, ...] = ()
    content_source: str
    full_assessment_available: bool = False
    captured_assessment: BaselineAssessment | None = None
    pack_checksum: Sha256

    @model_validator(mode="after")
    def complete_projection(self) -> Self:
        values = (self.direction, self.candidate_class, self.opportunity_score)
        if self.availability == "CAPTURED_PROJECTION" and any(v is None for v in values):
            raise ValueError("baseline projection must be complete")
        if self.availability == "MISSING_CONTENT" and any(v is not None for v in values):
            raise ValueError("missing baseline content cannot invent partial values")
        return self


class Contradiction(ContractModel):
    contradiction_id: str
    kind: Literal[
        "BASELINE_DISAGREEMENT",
        "CROSS_DOMAIN_TENSION",
        "SAME_PROPOSITION",
        "SOURCE_DISCREPANCY",
        "AUTHORITATIVE_FIELD",
    ]
    code: str
    blocking: Truth
    sources: tuple[SourceLocator, ...]


class LineageGroup(ContractModel):
    lineage_id: str
    roots: tuple[str, ...]
    opinion_ids: tuple[str, ...]
    families: tuple[str, ...]
    independence: Literal["UNKNOWN"] = "UNKNOWN"


class CompletenessProfile(ContractModel):
    required: tuple[SpecialistId, ...]
    optional: tuple[SpecialistId, ...]
    applicable: tuple[SpecialistId, ...]
    not_applicable: tuple[SpecialistId, ...]
    unknown_applicability: tuple[SpecialistId, ...]
    usable: tuple[SpecialistId, ...]
    partial: tuple[SpecialistId, ...]
    stale: tuple[SpecialistId, ...]
    missing: tuple[SpecialistId, ...]
    failed: tuple[SpecialistId, ...]
    blocked: tuple[SpecialistId, ...]
    numerator: int
    denominator: int
    gaps: tuple[str, ...]

    @property
    def coverage(self) -> float | None:
        return self.numerator / self.denominator if self.denominator else None


class BiasSummary(ContractModel):
    scope: Literal["UNDERLYING_PRICE_STRUCTURE_WITH_CONTEXT"] = (
        "UNDERLYING_PRICE_STRUCTURE_WITH_CONTEXT"
    )
    headline: AgentStance
    price_direction: AgentStance
    domain_views: tuple[tuple[SpecialistId, AgentStance], ...]
    sources: tuple[SourceLocator, ...]


class PredicateTrace(ContractModel):
    predicate: str
    value: Truth
    sources: tuple[SourceLocator, ...]
    reason_codes: tuple[str, ...]
    policy_version: Literal["1.0"] = "1.0"


class RuleTrace(ContractModel):
    rule_id: str
    value: Truth
    state: OpportunityState
    predicates: tuple[str, ...]


class IntelligenceReason(ContractModel):
    reason_id: str
    code: str
    category: Literal["SUPPORT", "OPPOSITION", "RISK", "GAP", "CONTEXT"]
    template_id: Literal[
        "QUOTED_TYPED_FIELD",
        "CAPTURED_OUTCOME",
        "CAPTURED_CONTRADICTION",
        "BENCHMARK_AND_OBSERVATION",
    ]
    parameters: tuple[tuple[str, str], ...]
    sources: tuple[SourceLocator, ...]
    epistemic: Literal["INFERENCE", "WORKFLOW", "QUOTED_SOURCE"]
    horizon_relevance: Literal["CAPTURED_REQUEST"] = "CAPTURED_REQUEST"
    rule_ids: tuple[str, ...] = ()


class Prerequisite(ContractModel):
    requirement_id: str
    source: SourceLocator
    reason: str
    automatic_execution: Literal[False] = False


class ContextSummary(ContractModel):
    artifact_id: str
    kind: str
    status: str | None = None
    confirmed_fields: tuple[str, ...] = ()
    unresolved_fields: tuple[str, ...] = ()
    epistemics: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()


class OpportunitySummary(ContractModel):
    state: OpportunityState
    primary_rule: str
    matched_rules: tuple[str, ...]
    bias: BiasSummary
    quality: Facet | None = None
    risk: Facet | None = None
    maturity: Facet | None = None
    extension: Facet | None = None
    remaining_room: tuple[Facet, ...] = ()


class OrchestrationAuditLink(ContractModel):
    run_id: str
    semantic_fingerprint: str
    capture_checksum: Sha256
    active_opinion_ids: tuple[str, ...]
    superseded_opinion_ids: tuple[str, ...]
    stop_reasons: tuple[str, ...]
    imported_usage: AgentUsage
    held_usage: AgentUsage
    imported_provider_calls: int
    held_provider_calls: int
    usage_is_complete: bool


class StructuredOpportunityIntelligence(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    intelligence_id: str
    request_id: str
    subject: Symbol
    instrument_type: InstrumentType
    purpose: AnalysisPurpose
    trade_style: TradeStyle
    horizon: Horizon
    as_of: TiafDateTime
    policy_id: str
    policy_version: str
    summary: OpportunitySummary
    baseline: BaselineView
    contributions: tuple[SpecialistContribution, ...]
    contradictions: tuple[Contradiction, ...]
    completeness: CompletenessProfile
    reasons: tuple[IntelligenceReason, ...]
    lineages: tuple[LineageGroup, ...]
    contexts: tuple[ContextSummary, ...]
    prerequisites: tuple[Prerequisite, ...]
    audit: OrchestrationAuditLink

    def semantic_payload(self) -> dict[str, object]:
        return self.model_dump(
            mode="json", exclude={"audit": {"capture_checksum", "imported_usage"}}
        ) | {
            "imported_consumption": self.audit.imported_usage.model_dump(
                exclude={"elapsed_seconds"}
            )
        }


class IntelligenceRunRecord(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    request: OpportunityIntelligenceRequest
    result: StructuredOpportunityIntelligence
    predicates: tuple[PredicateTrace, ...]
    rules: tuple[RuleTrace, ...]
    fingerprint: Sha256
    assembled_at: TiafDateTime
    assembly_usage: AgentUsage

    def compute_fingerprint(self) -> str:
        return digest(
            {
                "result": self.result.semantic_payload(),
                "policy": self.request.policy.model_dump(mode="json"),
                "predicates": [p.model_dump(mode="json") for p in self.predicates],
                "rules": [r.model_dump(mode="json") for r in self.rules],
            }
        )

    @model_validator(mode="after")
    def intact(self) -> Self:
        if self.fingerprint != self.compute_fingerprint():
            raise ValueError("intelligence semantic fingerprint mismatch")
        if self.result.request_id != self.request.request_id:
            raise ValueError("intelligence request identity mismatch")
        if (
            self.result.baseline.candidate_class is CandidateClass.NO_TRADE
            and self.result.summary.state is OpportunityState.OPPORTUNITY
        ):
            raise ValueError("A2 NO_TRADE cannot become OPPORTUNITY")
        matched = tuple(r.rule_id for r in self.rules if r.value is Truth.TRUE)
        if (
            not matched
            or matched != self.result.summary.matched_rules
            or matched[0] != self.result.summary.primary_rule
            or tuple(r.rule_id for r in self.rules) != self.request.policy.rule_order
            or next(r.state for r in self.rules if r.value is Truth.TRUE)
            != self.result.summary.state
        ):
            raise ValueError("rule trace and summary disagree")
        if self.assembly_usage.model_copy(update={"elapsed_seconds": 0}) != AgentUsage():
            raise ValueError("assembly cannot consume provider/model budgets")
        return self


class DeterministicComparison(ContractModel):
    exact_match: bool
    recorded_fingerprint: Sha256
    verified_fingerprint: Sha256
