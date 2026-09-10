"""Deterministic A3.6.2 integration from normalized MI evidence to research output."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Annotated, Protocol, Self, cast

from pydantic import Field, model_validator

from tiaf.agents import AgentBudget, AgentCapability, AgentOpinionV2, AgentUsage
from tiaf.contracts import ContractModel, DataQuality, FreshnessState, Horizon
from tiaf.contracts.common import NonEmptyStr, Symbol, TiafDateTime
from tiaf.events import EventMateriality, EventSourceClass, NormalizedEvent

from .authoritative_models import (
    AuthoritativeConfirmationRequest,
    AuthoritativeConfirmationResult,
)
from .enums import (
    DerivationClass,
    EpistemicKind,
    GraphEdgeStatus,
    GraphNodeKind,
    GraphRelation,
    MarketIntelligenceCapability,
    PointInTimeQuality,
    ResearchDepth,
    ResearchStatus,
    SemanticMappingQuality,
)
from .graph import (
    EvidenceGraphEdge,
    EvidenceGraphNode,
    EvidenceGraphProvenance,
    SparseEvidenceGraph,
)
from .models import (
    AmbiguousEvidenceProjection,
    CanonicalEvidenceProjection,
    CapabilityRoutePolicy,
    ContradictionGroup,
    MarketIntelligenceResearchPolicy,
    MarketIntelligenceResearchRequest,
    MarketIntelligenceResearchRun,
    NormalizationRecord,
)
from .research import (
    BusinessModelAssessment,
    CatalystRegister,
    CompanyResearchProfile,
    CompetitivePosition,
    ContradictingEvidence,
    CustomerExposure,
    IndustryStructureAssessment,
    InternationalExposure,
    ManagementEvidence,
    PolicyExposure,
    ResearchAssertion,
    ResearchComponent,
    ResearchGap,
    ResearchHypothesis,
    RiskRegister,
    SupplyChainExposure,
)
from .routing import MarketIntelligenceResearchController

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
type ResearchOutputComponent = (
    BusinessModelAssessment
    | IndustryStructureAssessment
    | SupplyChainExposure
    | CustomerExposure
    | CompetitivePosition
    | ManagementEvidence
    | InternationalExposure
    | PolicyExposure
    | RiskRegister
    | CatalystRegister
    | ResearchHypothesis
    | ContradictingEvidence
)


class ContextEvidenceQuality(ContractModel):
    """Compact normalized quality/PIT envelope; never a provider-native payload."""

    evidence_id: NonEmptyStr
    provider_id: NonEmptyStr
    quality: DataQuality
    freshness: FreshnessState
    point_in_time_quality: PointInTimeQuality
    available_from: TiafDateTime
    source_reference: NonEmptyStr


class DeepResearchContextPack(ContractModel):
    """Replay-safe synthesis input containing normalized evidence only."""

    context_id: NonEmptyStr
    subject: Symbol
    as_of: TiafDateTime
    horizon: Horizon
    objective: NonEmptyStr
    depth: ResearchDepth
    acquisition_run_fingerprint: Sha256
    a2_evidence_fingerprint: Sha256
    provider_ids: tuple[NonEmptyStr, ...] = ()
    canonical_facts: tuple[CanonicalEvidenceProjection, ...] = ()
    evidence_quality: tuple[ContextEvidenceQuality, ...] = ()
    ambiguous_evidence: tuple[AmbiguousEvidenceProjection, ...] = ()
    normalization_records: tuple[NormalizationRecord, ...] = ()
    normalized_events: tuple[NormalizedEvent, ...] = ()
    contradictions: tuple[ContradictionGroup, ...] = ()
    authoritative_confirmations: tuple[AuthoritativeConfirmationResult, ...] = ()
    research_gaps: tuple[ResearchGap, ...] = ()
    graph_nodes: tuple[EvidenceGraphNode, ...] = ()
    graph_edges: tuple[EvidenceGraphEdge, ...] = ()
    catalyst_event_ids: tuple[NonEmptyStr, ...] = ()
    risk_event_ids: tuple[NonEmptyStr, ...] = ()
    prior_opinions: tuple[AgentOpinionV2, ...] = ()
    allowed_authorities: tuple[AgentCapability, ...]
    budget: AgentBudget
    authority_constraints: tuple[NonEmptyStr, ...]
    evidence_fingerprint: Sha256

    @model_validator(mode="after")
    def validate_context(self) -> Self:
        for values, label in (
            (tuple(item.evidence_id for item in self.canonical_facts), "canonical evidence IDs"),
            (
                tuple(item.observation_id for item in self.ambiguous_evidence),
                "ambiguous observation IDs",
            ),
            (tuple(item.gap_id for item in self.research_gaps), "research gap IDs"),
            (self.catalyst_event_ids, "catalyst event IDs"),
            (self.risk_event_ids, "risk event IDs"),
            (self.provider_ids, "provider IDs"),
            (
                tuple(item.evidence_id for item in self.evidence_quality),
                "evidence quality IDs",
            ),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{label} must be unique")
        event_ids = {item.event_id for item in self.normalized_events}
        if not set(self.catalyst_event_ids) <= event_ids:
            raise ValueError("catalyst IDs must identify normalized context events")
        if not set(self.risk_event_ids) <= event_ids:
            raise ValueError("risk IDs must identify normalized context events")
        context_evidence_ids = (
            {item.evidence_id for item in self.canonical_facts}
            | event_ids
            | {
                document.document_id
                for confirmation in self.authoritative_confirmations
                for document in confirmation.authoritative_documents
            }
        )
        if not {item.evidence_id for item in self.evidence_quality} <= context_evidence_ids:
            raise ValueError("quality records must identify normalized context evidence")
        if not {item.provider_id for item in self.evidence_quality} <= set(self.provider_ids):
            raise ValueError("quality record providers must belong to context provenance")
        if "native_observations" in type(self).model_fields:
            raise ValueError("raw provider observations cannot enter deep-research context")
        return self


class DeepResearchResult(ContractModel):
    """Complete immutable research snapshot suitable for provider-free replay."""

    research_id: NonEmptyStr
    acquisition: MarketIntelligenceResearchRun
    context: DeepResearchContextPack
    components: tuple[ResearchOutputComponent, ...]
    profile: CompanyResearchProfile
    evidence_graph: SparseEvidenceGraph
    confirmations: tuple[AuthoritativeConfirmationResult, ...] = ()
    usage: AgentUsage
    created_at: TiafDateTime
    semantic_fingerprint: Sha256

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        request = self.acquisition.request
        if (self.context.subject, self.context.as_of, self.context.horizon) != (
            request.subject,
            request.as_of,
            request.horizon,
        ):
            raise ValueError("research context must match the acquisition request")
        if self.profile.subject != request.subject or self.profile.as_of != request.as_of:
            raise ValueError("research profile must match the acquisition request")
        component_ids = tuple(item.component_id for item in self.components)
        if component_ids != self.profile.component_ids:
            raise ValueError("profile component IDs must preserve output component order")
        if self.confirmations != self.context.authoritative_confirmations:
            raise ValueError("context and result confirmations must agree")
        if self.context.graph_nodes != self.evidence_graph.nodes:
            raise ValueError("context graph nodes must match the replay graph")
        if self.context.graph_edges != self.evidence_graph.edges:
            raise ValueError("context graph edges must match the replay graph")
        if self.usage.llm_calls or self.usage.input_tokens or self.usage.output_tokens:
            raise ValueError("deterministic A3.6.2 baseline cannot report model usage")
        request.budget.ensure_within(self.usage)
        self._validate_assertion_lineage()
        if self.semantic_fingerprint != self.compute_fingerprint():
            raise ValueError("deep-research semantic fingerprint does not match content")
        return self

    def _validate_assertion_lineage(self) -> None:
        assertions = {
            assertion.assertion_id: assertion
            for component in self.components
            for assertion in component.assertions
        }
        if len(assertions) != sum(len(item.assertions) for item in self.components):
            raise ValueError("research assertion IDs must be unique")
        evidence_ids = _context_evidence_ids(self.context)
        for assertion in assertions.values():
            if not set(assertion.evidence_ids) <= evidence_ids:
                raise ValueError("research assertion cites evidence outside the context pack")
            for support_id in assertion.supporting_assertion_ids:
                support = assertions.get(support_id)
                if support is None:
                    raise ValueError("research assertion cites unknown supporting assertion")
                if assertion.kind is EpistemicKind.INFERENCE:
                    if support.kind is not EpistemicKind.FACT:
                        raise ValueError("INFERENCE may only promote cited FACT assertions")
                elif assertion.kind is EpistemicKind.HYPOTHESIS:
                    if support.kind is EpistemicKind.HYPOTHESIS:
                        raise ValueError(
                            "HYPOTHESIS cannot be supported only by another hypothesis"
                        )

    def compute_fingerprint(self) -> str:
        payload = {
            "acquisition_fingerprint": self.acquisition.fingerprint,
            "context": self.context.model_dump(mode="json"),
            "components": [item.model_dump(mode="json") for item in self.components],
            "profile": self.profile.model_dump(mode="json"),
            "evidence_graph": self.evidence_graph.model_dump(mode="json"),
            "confirmation_fingerprints": [
                item.semantic_fingerprint for item in self.confirmations
            ],
            "usage": {
                "llm_calls": self.usage.llm_calls,
                "tool_calls": self.usage.tool_calls,
                "input_tokens": self.usage.input_tokens,
                "output_tokens": self.usage.output_tokens,
                "cost_units": self.usage.cost_units,
            },
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class AuthoritativeConfirmationTask:
    """One explicit material-claim confirmation within an integration run."""

    request: AuthoritativeConfirmationRequest
    route_policy: CapabilityRoutePolicy
    run_id: str
    confirmation_id: str


class _AuthoritativeConfirmationExecutor(Protocol):
    def execute(
        self,
        request: AuthoritativeConfirmationRequest,
        route_policy: CapabilityRoutePolicy,
        *,
        run_id: str,
        confirmation_id: str,
    ) -> AuthoritativeConfirmationResult: ...


class DeepResearchIntegrationController:
    """Acquire, enrich, confirm, assemble, and fingerprint one bounded research request."""

    policy_id = "deep-research-deterministic"
    policy_version = "1.0"

    def __init__(
        self,
        research_controller: MarketIntelligenceResearchController,
        *,
        authoritative_gateway: _AuthoritativeConfirmationExecutor | None = None,
    ) -> None:
        self._research_controller = research_controller
        self._authoritative_gateway = authoritative_gateway

    def execute(
        self,
        request: MarketIntelligenceResearchRequest,
        policy: MarketIntelligenceResearchPolicy,
        *,
        research_id: str,
        objective: str,
        depth: ResearchDepth,
        a2_evidence_fingerprint: str,
        evidence_graph: SparseEvidenceGraph | None = None,
        confirmation_tasks: tuple[AuthoritativeConfirmationTask, ...] = (),
        prior_opinions: tuple[AgentOpinionV2, ...] = (),
    ) -> DeepResearchResult:
        acquisition = self._research_controller.execute(
            request,
            policy,
            research_run_id=f"{research_id}:acquisition",
        )
        confirmations: list[AuthoritativeConfirmationResult] = []
        for task in confirmation_tasks:
            if self._authoritative_gateway is None:
                raise ValueError("authoritative confirmation task requires a configured gateway")
            if task.request.claim.subject != request.subject:
                raise ValueError("confirmation subject must match research subject")
            discovered = set(task.request.claim.discovery_evidence_ids)
            if not discovered <= _acquisition_evidence_ids(acquisition):
                raise ValueError("confirmation claim must link to acquired discovery evidence")
            confirmations.append(
                self._authoritative_gateway.execute(
                    task.request,
                    task.route_policy,
                    run_id=task.run_id,
                    confirmation_id=task.confirmation_id,
                )
            )
        usage = _combined_usage(acquisition, tuple(confirmations))
        request.budget.ensure_within(usage)
        return self.assemble(
            acquisition,
            research_id=research_id,
            objective=objective,
            depth=depth,
            a2_evidence_fingerprint=a2_evidence_fingerprint,
            evidence_graph=evidence_graph,
            confirmations=tuple(confirmations),
            prior_opinions=prior_opinions,
            usage=usage,
        )

    def assemble(
        self,
        acquisition: MarketIntelligenceResearchRun,
        *,
        research_id: str,
        objective: str,
        depth: ResearchDepth,
        a2_evidence_fingerprint: str,
        evidence_graph: SparseEvidenceGraph | None = None,
        confirmations: tuple[AuthoritativeConfirmationResult, ...] = (),
        prior_opinions: tuple[AgentOpinionV2, ...] = (),
        usage: AgentUsage | None = None,
    ) -> DeepResearchResult:
        request = acquisition.request
        canonical = tuple(
            item
            for run in acquisition.capability_runs
            for batch in run.batches
            for item in batch.canonical_evidence
        )
        records = tuple(
            item
            for run in acquisition.capability_runs
            for batch in run.batches
            for item in batch.normalization_records
        )
        events = _dedupe_events(
            tuple(
                item
                for run in acquisition.capability_runs
                for batch in run.batches
                for item in batch.normalized_events
            )
        )
        ambiguous = _ambiguous_projections(acquisition)
        evidence_quality = _evidence_quality(acquisition, canonical, events, confirmations)
        gaps = _research_gaps(acquisition)
        graph = _update_graph(evidence_graph, acquisition, canonical, events)
        evidence_fingerprint = _evidence_fingerprint(
            acquisition, canonical, ambiguous, events, confirmations, graph, gaps
        )
        context = DeepResearchContextPack(
            context_id=f"{research_id}:context",
            subject=request.subject,
            as_of=request.as_of,
            horizon=request.horizon,
            objective=objective,
            depth=depth,
            acquisition_run_fingerprint=acquisition.fingerprint,
            a2_evidence_fingerprint=a2_evidence_fingerprint,
            provider_ids=tuple(
                dict.fromkeys(
                    [
                        audit.provider_id
                        for run in acquisition.capability_runs
                        for audit in run.audits
                    ]
                    + [
                        document.source.provider_id
                        for confirmation in confirmations
                        for document in confirmation.authoritative_documents
                    ]
                )
            ),
            canonical_facts=canonical,
            evidence_quality=evidence_quality,
            ambiguous_evidence=ambiguous,
            normalization_records=records,
            normalized_events=events,
            contradictions=tuple(
                item for run in acquisition.capability_runs for item in run.contradictions
            ),
            authoritative_confirmations=confirmations,
            research_gaps=gaps,
            graph_nodes=graph.nodes,
            graph_edges=graph.edges,
            catalyst_event_ids=tuple(item.event_id for item in events),
            risk_event_ids=(),
            prior_opinions=prior_opinions,
            allowed_authorities=tuple(
                dict.fromkeys(
                    authority
                    for item in request.capability_requests
                    for authority in item.allowed_authorities
                )
            ),
            budget=request.budget,
            authority_constraints=(
                "normalized evidence only",
                "no provider or transport access from synthesis",
                "no calibrated forecast probability",
                "no trade expression or broker operation",
                "no model calls in deterministic baseline",
            ),
            evidence_fingerprint=evidence_fingerprint,
        )
        components = _components(acquisition, context, research_id)
        assertion_count = sum(len(item.assertions) for item in components)
        profile_status = (
            ResearchStatus.INSUFFICIENT_EVIDENCE
            if assertion_count == 0
            else ResearchStatus.PARTIAL
            if gaps or context.contradictions
            else ResearchStatus.SUCCESS
        )
        profile = CompanyResearchProfile(
            profile_id=f"{research_id}:profile",
            subject=request.subject,
            as_of=request.as_of,
            horizon=request.horizon,
            depth=depth,
            status=profile_status,
            component_ids=tuple(item.component_id for item in components),
            evidence_ids=tuple(sorted(_context_evidence_ids(context))),
            evidence_fingerprint=evidence_fingerprint,
            prior_opinions=prior_opinions,
            missing_component_types=tuple(
                item.component_type
                for item in components
                if item.status is ResearchStatus.INSUFFICIENT_EVIDENCE
            ),
        )
        observed_usage = usage or acquisition.usage
        provisional = DeepResearchResult.model_construct(
            research_id=research_id,
            acquisition=acquisition,
            context=context,
            components=components,
            profile=profile,
            evidence_graph=graph,
            confirmations=confirmations,
            usage=observed_usage,
            created_at=request.as_of,
            semantic_fingerprint="0" * 64,
        )
        return DeepResearchResult(
            research_id=research_id,
            acquisition=acquisition,
            context=context,
            components=components,
            profile=profile,
            evidence_graph=graph,
            confirmations=confirmations,
            usage=observed_usage,
            created_at=request.as_of,
            semantic_fingerprint=provisional.compute_fingerprint(),
        )


def _acquisition_evidence_ids(run: MarketIntelligenceResearchRun) -> set[str]:
    return {
        item.evidence_id
        for capability_run in run.capability_runs
        for batch in capability_run.batches
        for item in batch.canonical_evidence
    } | {
        item.event_id
        for capability_run in run.capability_runs
        for batch in capability_run.batches
        for item in batch.normalized_events
    }


def _context_evidence_ids(context: DeepResearchContextPack) -> set[str]:
    return (
        {item.evidence_id for item in context.canonical_facts}
        | {item.event_id for item in context.normalized_events}
        | {
            item.document_id
            for confirmation in context.authoritative_confirmations
            for item in confirmation.authoritative_documents
        }
        | {
            item.authoritative_evidence_id
            for confirmation in context.authoritative_confirmations
            for item in confirmation.confirmed_facts
        }
    )


def _combined_usage(
    acquisition: MarketIntelligenceResearchRun,
    confirmations: tuple[AuthoritativeConfirmationResult, ...],
) -> AgentUsage:
    usages = (acquisition.usage, *(item.usage for item in confirmations))
    return AgentUsage(
        llm_calls=sum(item.llm_calls for item in usages),
        tool_calls=sum(item.tool_calls for item in usages),
        input_tokens=sum(item.input_tokens for item in usages),
        output_tokens=sum(item.output_tokens for item in usages),
        cost_units=sum(item.cost_units for item in usages),
        elapsed_seconds=sum(item.elapsed_seconds for item in usages),
        metadata={
            "capability_runs": len(acquisition.capability_runs),
            "authoritative_confirmations": len(confirmations),
            "baseline": "NO_LLM",
        },
    )


def _ambiguous_projections(
    acquisition: MarketIntelligenceResearchRun,
) -> tuple[AmbiguousEvidenceProjection, ...]:
    projected: list[AmbiguousEvidenceProjection] = []
    seen: set[str] = set()
    for run in acquisition.capability_runs:
        for batch in run.batches:
            observations = {item.observation_id: item for item in batch.native_observations}
            for record in batch.normalization_records:
                if record.mapping_quality not in {
                    SemanticMappingQuality.AMBIGUOUS,
                    SemanticMappingQuality.PROVIDER_DEFINED,
                }:
                    continue
                if record.observation_id in seen:
                    continue
                observation = observations[record.observation_id]
                projected.append(
                    AmbiguousEvidenceProjection(
                        observation_id=observation.observation_id,
                        provider_id=observation.provider_id,
                        native_field=observation.native_field,
                        value=observation.value,
                        mapping_quality=record.mapping_quality,
                        available_from=observation.available_from,
                        source_reference=observation.source_reference,
                    )
                )
                seen.add(record.observation_id)
    return tuple(projected)


def _evidence_quality(
    acquisition: MarketIntelligenceResearchRun,
    canonical: tuple[CanonicalEvidenceProjection, ...],
    events: tuple[NormalizedEvent, ...],
    confirmations: tuple[AuthoritativeConfirmationResult, ...],
) -> tuple[ContextEvidenceQuality, ...]:
    observations = {
        item.observation_id: item
        for run in acquisition.capability_runs
        for batch in run.batches
        for item in batch.native_observations
    }
    quality: list[ContextEvidenceQuality] = []
    for evidence in canonical:
        observation = observations[evidence.source_observation_id]
        quality.append(
            ContextEvidenceQuality(
                evidence_id=evidence.evidence_id,
                provider_id=evidence.provider_id,
                quality=observation.source_quality,
                freshness=FreshnessState.UNKNOWN,
                point_in_time_quality=observation.point_in_time_quality,
                available_from=evidence.available_from,
                source_reference=evidence.source_reference,
            )
        )
    for event in events:
        quality.append(
            ContextEvidenceQuality(
                evidence_id=event.event_id,
                provider_id=event.source.provider_id,
                quality=event.quality,
                freshness=event.freshness,
                point_in_time_quality=(
                    PointInTimeQuality.CONSERVATIVE
                    if event.publication_time < event.acquisition_time
                    else PointInTimeQuality.LIMITED
                ),
                available_from=event.publication_time,
                source_reference=event.source.source_reference,
            )
        )
    for confirmation in confirmations:
        for document in confirmation.authoritative_documents:
            quality.append(
                ContextEvidenceQuality(
                    evidence_id=document.document_id,
                    provider_id=document.source.provider_id,
                    quality=confirmation.quality,
                    freshness=FreshnessState.UNKNOWN,
                    point_in_time_quality=document.point_in_time_quality,
                    available_from=document.available_from,
                    source_reference=document.final_url,
                )
            )
    return tuple({item.evidence_id: item for item in quality}.values())


def _research_gaps(acquisition: MarketIntelligenceResearchRun) -> tuple[ResearchGap, ...]:
    gaps: list[ResearchGap] = []
    seen: set[tuple[str, str, str]] = set()
    for run in acquisition.capability_runs:
        failures = tuple(run.failures) + tuple(
            gap for batch in run.batches for gap in batch.gaps
        )
        for failure in failures:
            key = (failure.capability.value, failure.kind.value, failure.message)
            if key in seen:
                continue
            seen.add(key)
            gaps.append(
                ResearchGap(
                    gap_id=_digest("gap", *key),
                    capability=failure.capability.value,
                    description=f"{failure.kind.value}: {failure.message}",
                    blocking=False,
                )
            )
        has_evidence = any(
            batch.canonical_evidence
            or batch.normalized_events
            or batch.authoritative_documents
            for batch in run.batches
        )
        if not has_evidence:
            key = (run.request.capability.value, "NO_NORMALIZED_EVIDENCE", "")
            if key not in seen:
                seen.add(key)
                gaps.append(
                    ResearchGap(
                        gap_id=_digest("gap", *key),
                        capability=run.request.capability.value,
                        description="No safely normalized evidence was acquired for this family",
                        blocking=False,
                    )
                )
    return tuple(gaps)


def _dedupe_events(events: tuple[NormalizedEvent, ...]) -> tuple[NormalizedEvent, ...]:
    return tuple({item.event_id: item for item in events}.values())


def _evidence_fingerprint(
    acquisition: MarketIntelligenceResearchRun,
    canonical: tuple[CanonicalEvidenceProjection, ...],
    ambiguous: tuple[AmbiguousEvidenceProjection, ...],
    events: tuple[NormalizedEvent, ...],
    confirmations: tuple[AuthoritativeConfirmationResult, ...],
    graph: SparseEvidenceGraph,
    gaps: tuple[ResearchGap, ...],
) -> str:
    payload = {
        "acquisition": acquisition.fingerprint,
        "canonical": [item.model_dump(mode="json") for item in canonical],
        "ambiguous": [item.model_dump(mode="json") for item in ambiguous],
        "events": [item.model_dump(mode="json") for item in events],
        "confirmations": [item.semantic_fingerprint for item in confirmations],
        "graph": graph.model_dump(mode="json"),
        "gaps": [item.model_dump(mode="json") for item in gaps],
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _update_graph(
    existing: SparseEvidenceGraph | None,
    acquisition: MarketIntelligenceResearchRun,
    canonical: tuple[CanonicalEvidenceProjection, ...],
    events: tuple[NormalizedEvent, ...],
) -> SparseEvidenceGraph:
    graph = existing or SparseEvidenceGraph(graph_id=f"graph:{acquisition.request.subject}")
    subject = acquisition.request.subject
    company_id = f"company:{subject.casefold()}"
    nodes = {item.node_id: item for item in graph.nodes}
    nodes.setdefault(
        company_id,
        EvidenceGraphNode(
            node_id=company_id,
            kind=GraphNodeKind.COMPANY,
            canonical_name=subject,
        ),
    )
    edges = list(graph.edges)
    semantic_edges = {
        (item.source_node_id, item.relation, item.target_node_id) for item in edges
    }
    observations = {
        item.observation_id: item
        for run in acquisition.capability_runs
        for batch in run.batches
        for item in batch.native_observations
    }
    contradictions = {
        evidence_id: contradiction.contradiction_id
        for run in acquisition.capability_runs
        for contradiction in run.contradictions
        for evidence_id in contradiction.evidence_ids
    }
    relation_map = {
        "company.sector": (GraphNodeKind.SECTOR, GraphRelation.BELONGS_TO_SECTOR),
        "company.industry": (GraphNodeKind.INDUSTRY, GraphRelation.BELONGS_TO_INDUSTRY),
    }
    for evidence in canonical:
        mapping = relation_map.get(evidence.metric)
        if mapping is None or not isinstance(evidence.value, str):
            continue
        kind, relation = mapping
        slug = _slug(evidence.value)
        target_id = f"{kind.value.casefold()}:{slug}"
        nodes.setdefault(
            target_id,
            EvidenceGraphNode(
                node_id=target_id,
                kind=kind,
                canonical_name=evidence.value,
            ),
        )
        semantic_key = (company_id, relation, target_id)
        if semantic_key in semantic_edges:
            continue
        observation = observations[evidence.source_observation_id]
        contradiction_id = contradictions.get(evidence.evidence_id)
        edges.append(
            EvidenceGraphEdge(
                edge_id=_digest("edge", company_id, relation.value, target_id),
                source_node_id=company_id,
                target_node_id=target_id,
                relation=relation,
                status=(
                    GraphEdgeStatus.UNCERTAIN
                    if contradiction_id is not None
                    else GraphEdgeStatus.REPORTED
                ),
                materiality=0.5,
                evidence_quality=observation.source_quality,
                confidence_basis=(
                    "conflicting normalized provider evidence; materiality uses neutral "
                    "baseline"
                    if contradiction_id is not None
                    else "normalized provider evidence; materiality uses neutral baseline"
                ),
                provenance=EvidenceGraphProvenance(
                    provider_id=evidence.provider_id,
                    evidence_ids=(evidence.evidence_id,),
                    source_references=(evidence.source_reference,),
                    observed_at=observation.observed_at,
                    available_from=evidence.available_from,
                    acquired_at=observation.acquired_at,
                    last_verified_at=observation.acquired_at,
                    derivation_class=evidence.derivation_class,
                ),
                valid_from=evidence.available_from,
                contradiction_group_id=contradiction_id,
                contradiction_unresolved=contradiction_id is not None,
            )
        )
        semantic_edges.add(semantic_key)
    materiality = {
        EventMateriality.CRITICAL: 1.0,
        EventMateriality.HIGH: 0.8,
        EventMateriality.MODERATE: 0.6,
        EventMateriality.LOW: 0.3,
        EventMateriality.IMMATERIAL: 0.0,
        EventMateriality.UNKNOWN: 0.0,
    }
    for event in events:
        target_id = f"catalyst:{event.event_id.casefold()}"
        nodes.setdefault(
            target_id,
            EvidenceGraphNode(
                node_id=target_id,
                kind=GraphNodeKind.CATALYST,
                canonical_name=event.normalized_title,
            ),
        )
        semantic_key = (company_id, GraphRelation.HAS_CATALYST, target_id)
        if semantic_key in semantic_edges:
            continue
        edges.append(
            EvidenceGraphEdge(
                edge_id=_digest("edge", company_id, GraphRelation.HAS_CATALYST.value, target_id),
                source_node_id=company_id,
                target_node_id=target_id,
                relation=GraphRelation.HAS_CATALYST,
                status=(
                    GraphEdgeStatus.CONFIRMED
                    if event.source.source_class
                    in {
                        EventSourceClass.EXCHANGE_FILING,
                        EventSourceClass.REGULATORY_FILING,
                        EventSourceClass.COMPANY_RELEASE,
                        EventSourceClass.OFFICIAL_GOVERNMENT,
                    }
                    else GraphEdgeStatus.REPORTED
                ),
                materiality=materiality[event.materiality],
                evidence_quality=event.quality,
                confidence_basis=(
                    "normalized event evidence; zero materiality means provider did not score it"
                ),
                provenance=EvidenceGraphProvenance(
                    provider_id=event.source.provider_id,
                    evidence_ids=(event.event_id,),
                    source_references=(event.source.source_reference,),
                    observed_at=event.event_time,
                    available_from=event.publication_time,
                    acquired_at=event.acquisition_time,
                    last_verified_at=event.acquisition_time,
                    derivation_class=DerivationClass.REPORTED,
                ),
                valid_from=event.publication_time,
            )
        )
        semantic_edges.add(semantic_key)
    return SparseEvidenceGraph(
        graph_id=graph.graph_id,
        nodes=tuple(nodes.values()),
        edges=tuple(edges),
    )


_COMPONENT_CAPABILITIES: tuple[
    tuple[type[ResearchComponent], tuple[MarketIntelligenceCapability, ...]], ...
] = (
    (
        BusinessModelAssessment,
        (
            MarketIntelligenceCapability.READ_COMPANY_PROFILE,
            MarketIntelligenceCapability.READ_COMPANY_IDENTITY,
            MarketIntelligenceCapability.READ_FINANCIALS,
            MarketIntelligenceCapability.READ_FINANCIAL_RATIOS,
            MarketIntelligenceCapability.READ_VALUATION_CONTEXT,
            MarketIntelligenceCapability.READ_SHAREHOLDING,
        ),
    ),
    (
        IndustryStructureAssessment,
        (
            MarketIntelligenceCapability.READ_PEERS,
            MarketIntelligenceCapability.READ_INDUSTRY_CONTEXT,
            MarketIntelligenceCapability.READ_COMPETITORS,
            MarketIntelligenceCapability.READ_SECTOR_CONTEXT,
        ),
    ),
    (CustomerExposure, (MarketIntelligenceCapability.READ_CUSTOMER_EXPOSURE,)),
    (
        SupplyChainExposure,
        (
            MarketIntelligenceCapability.READ_SUPPLIER_EXPOSURE,
            MarketIntelligenceCapability.READ_SUPPLY_CHAIN_EXPOSURE,
        ),
    ),
    (ManagementEvidence, (MarketIntelligenceCapability.READ_MANAGEMENT_EVIDENCE,)),
    (
        InternationalExposure,
        (
            MarketIntelligenceCapability.READ_GEOGRAPHIC_EXPOSURE,
            MarketIntelligenceCapability.READ_INTERNATIONAL_CONTEXT,
        ),
    ),
    (PolicyExposure, (MarketIntelligenceCapability.READ_POLICY_REGULATION,)),
    (
        RiskRegister,
        (
            MarketIntelligenceCapability.READ_GOVERNANCE_RISK,
            MarketIntelligenceCapability.READ_PROMOTER_PLEDGE,
            MarketIntelligenceCapability.READ_CREDIT_RATINGS,
        ),
    ),
    (
        CatalystRegister,
        (
            MarketIntelligenceCapability.READ_NEWS,
            MarketIntelligenceCapability.READ_FILINGS,
            MarketIntelligenceCapability.READ_CORPORATE_ACTIONS,
            MarketIntelligenceCapability.READ_EARNINGS_CALENDAR,
            MarketIntelligenceCapability.READ_EARNINGS_CALL_CONTEXT,
        ),
    ),
)


def _components(
    acquisition: MarketIntelligenceResearchRun,
    context: DeepResearchContextPack,
    research_id: str,
) -> tuple[ResearchOutputComponent, ...]:
    requested = {item.capability for item in acquisition.request.capability_requests}
    evidence_capability = {
        evidence.evidence_id: run.request.capability
        for run in acquisition.capability_runs
        for batch in run.batches
        for evidence in batch.canonical_evidence
    }
    event_capability = {
        event.event_id: run.request.capability
        for run in acquisition.capability_runs
        for batch in run.batches
        for event in batch.normalized_events
    }
    gaps_by_capability: dict[str, list[ResearchGap]] = {}
    for gap in context.research_gaps:
        gaps_by_capability.setdefault(gap.capability, []).append(gap)
    is_bank = any(
        item.metric in {"company.sector", "company.industry"}
        and isinstance(item.value, str)
        and any(token in item.value.casefold() for token in ("bank", "financial service"))
        for item in context.canonical_facts
    )
    unsafe_bank_tokens = ("ebitda", "capacity", "inventory", "operating_leverage")
    output: list[ResearchOutputComponent] = []
    for component_type, capabilities in _COMPONENT_CAPABILITIES:
        relevant = requested.intersection(capabilities)
        if not relevant:
            continue
        assertions: list[ResearchAssertion] = []
        component_gaps = [
            gap
            for capability in relevant
            for gap in gaps_by_capability.get(capability.value, ())
        ]
        for evidence in context.canonical_facts:
            if evidence_capability[evidence.evidence_id] not in relevant:
                continue
            if is_bank and any(token in evidence.metric.casefold() for token in unsafe_bank_tokens):
                component_gaps.append(
                    ResearchGap(
                        gap_id=_digest("sector-safety", evidence.evidence_id),
                        capability=evidence_capability[evidence.evidence_id].value,
                        description=(
                            f"Sector safety withheld industrial interpretation of {evidence.metric}"
                        ),
                    )
                )
                continue
            assertions.append(_canonical_fact_assertion(evidence))
        for event in context.normalized_events:
            if event_capability[event.event_id] in relevant:
                assertions.append(
                    ResearchAssertion(
                        assertion_id=_digest("assertion", event.event_id),
                        kind=EpistemicKind.FACT,
                        statement=(
                            f"Normalized event evidence reports: {event.normalized_title}."
                        ),
                        evidence_ids=(event.event_id,),
                    )
                )
        component_gaps = list({item.gap_id: item for item in component_gaps}.values())
        status = (
            ResearchStatus.INSUFFICIENT_EVIDENCE
            if not assertions
            else ResearchStatus.PARTIAL
            if component_gaps
            else ResearchStatus.SUCCESS
        )
        component_id = f"{research_id}:{component_type.__name__}"
        output.append(
            cast(
                ResearchOutputComponent,
                component_type(
                component_id=component_id,
                subject=acquisition.request.subject,
                as_of=acquisition.request.as_of,
                horizon=acquisition.request.horizon,
                status=status,
                assertions=tuple(assertions),
                gaps=tuple(component_gaps),
                quality=_component_quality(assertions, component_gaps),
                freshness=FreshnessState.UNKNOWN,
                point_in_time_quality=_point_in_time_quality(acquisition, relevant),
                producer_id="tiaf.deep-research.deterministic",
                producer_version="1.0",
                policy_id=DeepResearchIntegrationController.policy_id,
                policy_version=DeepResearchIntegrationController.policy_version,
                evidence_fingerprint=context.evidence_fingerprint,
                    created_at=acquisition.request.as_of,
                ),
            )
        )
    contradictions = tuple(
        item for run in acquisition.capability_runs for item in run.contradictions
    )
    if contradictions:
        output.append(
            ContradictingEvidence(
                component_id=f"{research_id}:ContradictingEvidence",
                subject=acquisition.request.subject,
                as_of=acquisition.request.as_of,
                horizon=acquisition.request.horizon,
                status=ResearchStatus.PARTIAL,
                contradiction_ids=tuple(item.contradiction_id for item in contradictions),
                quality=DataQuality.PARTIAL,
                freshness=FreshnessState.UNKNOWN,
                point_in_time_quality=_point_in_time_quality(acquisition, requested),
                producer_id="tiaf.deep-research.deterministic",
                producer_version="1.0",
                policy_id=DeepResearchIntegrationController.policy_id,
                policy_version=DeepResearchIntegrationController.policy_version,
                evidence_fingerprint=context.evidence_fingerprint,
                created_at=acquisition.request.as_of,
            )
        )
    return tuple(output)


def _canonical_fact_assertion(evidence: CanonicalEvidenceProjection) -> ResearchAssertion:
    qualifiers = tuple(
        item
        for item in (
            evidence.unit,
            evidence.currency,
            f"period {evidence.period}" if evidence.period else None,
        )
        if item is not None
    )
    suffix = f" ({', '.join(qualifiers)})" if qualifiers else ""
    return ResearchAssertion(
        assertion_id=_digest("assertion", evidence.evidence_id),
        kind=EpistemicKind.FACT,
        statement=f"{evidence.metric} is reported as {evidence.value}{suffix}.",
        evidence_ids=(evidence.evidence_id,),
    )


def _component_quality(
    assertions: list[ResearchAssertion], gaps: list[ResearchGap]
) -> DataQuality:
    if not assertions:
        return DataQuality.UNAVAILABLE
    return DataQuality.PARTIAL if gaps else DataQuality.GOOD


def _point_in_time_quality(
    acquisition: MarketIntelligenceResearchRun,
    capabilities: set[MarketIntelligenceCapability],
) -> PointInTimeQuality:
    qualities = [
        observation.point_in_time_quality
        for run in acquisition.capability_runs
        if run.request.capability in capabilities
        for batch in run.batches
        for observation in batch.native_observations
    ]
    rank = {
        PointInTimeQuality.UNKNOWN: 0,
        PointInTimeQuality.LIMITED: 1,
        PointInTimeQuality.CONSERVATIVE: 2,
        PointInTimeQuality.EXACT: 3,
    }
    return min(qualities, key=lambda item: rank[item], default=PointInTimeQuality.UNKNOWN)


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return normalized or _digest("node", value)[:16]


def _digest(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()
