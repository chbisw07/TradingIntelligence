from datetime import timedelta

import pytest
from pydantic import ValidationError

from tiaf.agents import AgentBudget, AgentCapability
from tiaf.contracts import DataQuality, FreshnessState, Horizon
from tiaf.market_intelligence import (
    AmbiguousEvidenceProjection,
    BusinessModelAssessment,
    CompanyResearchProfile,
    DerivationClass,
    EpistemicKind,
    EvidenceGraphEdge,
    EvidenceGraphNode,
    EvidenceGraphProvenance,
    GraphEdgeStatus,
    GraphNodeKind,
    GraphRelation,
    MarketIntelligenceSynthesisContext,
    PointInTimeQuality,
    ResearchAssertion,
    ResearchDepth,
    ResearchGap,
    ResearchHypothesis,
    ResearchStatus,
    SemanticMappingQuality,
    SparseEvidenceGraph,
)

from ._support import AS_OF


def _nodes() -> tuple[EvidenceGraphNode, EvidenceGraphNode]:
    return (
        EvidenceGraphNode(
            node_id="company:reliance",
            kind=GraphNodeKind.COMPANY,
            canonical_name="Reliance Industries",
        ),
        EvidenceGraphNode(
            node_id="commodity:oil",
            kind=GraphNodeKind.COMMODITY,
            canonical_name="Crude oil",
        ),
    )


def _edge(*, available_offset: int = -1) -> EvidenceGraphEdge:
    return EvidenceGraphEdge(
        edge_id="edge-1",
        source_node_id="company:reliance",
        target_node_id="commodity:oil",
        relation=GraphRelation.EXPOSED_TO_COMMODITY,
        status=GraphEdgeStatus.REPORTED,
        materiality=0.8,
        evidence_quality=DataQuality.GOOD,
        confidence_basis="company filing explicitly names the exposure",
        provenance=EvidenceGraphProvenance(
            provider_id="fixture",
            evidence_ids=("evidence-1",),
            available_from=AS_OF + timedelta(days=available_offset),
            acquired_at=AS_OF + timedelta(days=max(available_offset, 0)),
            last_verified_at=AS_OF + timedelta(days=max(available_offset, 0)),
            derivation_class=DerivationClass.REPORTED,
        ),
    )


def test_sparse_graph_requires_existing_endpoints_and_provenance() -> None:
    graph = SparseEvidenceGraph(graph_id="g", nodes=_nodes(), edges=(_edge(),))
    assert graph.neighborhood("company:reliance", as_of=AS_OF) == (_edge(),)
    assert SparseEvidenceGraph.model_validate_json(graph.model_dump_json()) == graph
    with pytest.raises(ValidationError, match="endpoints"):
        SparseEvidenceGraph(graph_id="g", nodes=(_nodes()[0],), edges=(_edge(),))


def test_graph_neighborhood_is_point_in_time_safe() -> None:
    graph = SparseEvidenceGraph(graph_id="g", nodes=_nodes(), edges=(_edge(available_offset=1),))
    assert graph.neighborhood("company:reliance", as_of=AS_OF) == ()


def test_graph_updates_are_immutable() -> None:
    original = SparseEvidenceGraph(graph_id="g")
    updated = original.with_updates(nodes=_nodes())
    assert original.nodes == ()
    assert len(updated.nodes) == 2


@pytest.mark.parametrize("kind", [EpistemicKind.FACT, EpistemicKind.INFERENCE])
def test_fact_and_inference_cannot_be_uncited(kind: EpistemicKind) -> None:
    with pytest.raises(ValidationError):
        ResearchAssertion(
            assertion_id="a",
            kind=kind,
            statement="A claim",
            reasoning="because" if kind is EpistemicKind.INFERENCE else None,
        )


def test_inference_requires_reasoning_and_hypothesis_requires_conditions() -> None:
    with pytest.raises(ValidationError, match="explicit reasoning"):
        ResearchAssertion(
            assertion_id="a",
            kind=EpistemicKind.INFERENCE,
            statement="A claim",
            evidence_ids=("e1",),
        )
    hypothesis = ResearchAssertion(
        assertion_id="h",
        kind=EpistemicKind.HYPOTHESIS,
        statement="Margins may improve",
        assumptions=("input costs decline",),
        invalidation_conditions=("input costs rise",),
        evidence_ids=("e1",),
    )
    assert hypothesis.evidence_ids == ("e1",)


def test_research_components_support_abstention_and_composition() -> None:
    component = BusinessModelAssessment(
        component_id="business-1",
        subject="RELIANCE",
        as_of=AS_OF,
        horizon=Horizon(label="POSITIONAL"),
        status=ResearchStatus.INSUFFICIENT_EVIDENCE,
        gaps=(
            ResearchGap(
                gap_id="gap-1",
                capability="READ_COMPANY_PROFILE",
                description="No point-in-time company description",
                blocking=True,
            ),
        ),
        quality=DataQuality.UNAVAILABLE,
        freshness=FreshnessState.UNKNOWN,
        point_in_time_quality=PointInTimeQuality.UNKNOWN,
        producer_id="research-fixture",
        producer_version="1.0",
        policy_id="research-policy",
        policy_version="1.0",
        evidence_fingerprint="f" * 64,
        created_at=AS_OF,
    )
    profile = CompanyResearchProfile(
        profile_id="profile-1",
        subject="RELIANCE",
        as_of=AS_OF,
        horizon=Horizon(label="POSITIONAL"),
        depth=ResearchDepth.L2_INVESTMENT_RESEARCH,
        status=ResearchStatus.PARTIAL,
        component_ids=(component.component_id,),
        evidence_fingerprint="f" * 64,
        missing_component_types=("CUSTOMER_EXPOSURE",),
    )
    assert profile.component_ids == ("business-1",)


def test_hypothesis_component_enforces_hypothesis_label() -> None:
    fact = ResearchAssertion(
        assertion_id="f",
        kind=EpistemicKind.FACT,
        statement="Reported revenue increased",
        evidence_ids=("e1",),
    )
    with pytest.raises(ValidationError, match="HYPOTHESIS assertion"):
        ResearchHypothesis(
            component_id="hypothesis-1",
            subject="RELIANCE",
            as_of=AS_OF,
            horizon=Horizon(label="POSITIONAL"),
            status=ResearchStatus.SUCCESS,
            assertions=(fact,),
            quality=DataQuality.GOOD,
            freshness=FreshnessState.FRESH,
            point_in_time_quality=PointInTimeQuality.EXACT,
            producer_id="research-fixture",
            producer_version="1.0",
            policy_id="research-policy",
            policy_version="1.0",
            evidence_fingerprint="f" * 64,
            created_at=AS_OF,
        )


def test_synthesis_context_accepts_only_normalized_references_and_no_raw_payload_field() -> None:
    context = MarketIntelligenceSynthesisContext(
        context_id="context-1",
        subject="RELIANCE",
        as_of=AS_OF,
        horizon=Horizon(label="POSITIONAL"),
        canonical_evidence=(),
        normalization_records=(),
        ambiguous_observation_ids=("native-1",),
        ambiguous_evidence=(
            AmbiguousEvidenceProjection(
                observation_id="native-1",
                provider_id="fixture",
                native_field="Sales",
                value=100,
                mapping_quality=SemanticMappingQuality.AMBIGUOUS,
                available_from=AS_OF,
            ),
        ),
        contradictions=(),
        a2_evidence_fingerprint="a" * 64,
        allowed_authorities=(AgentCapability.READ_FUNDAMENTALS,),
        budget=AgentBudget(max_elapsed_seconds=30),
        output_schema_id="research-synthesis-v1",
        authority_constraints=("no provider calls", "no trading actions"),
    )
    assert "native_observations" not in type(context).model_fields
    assert "raw_payload" not in type(context).model_fields
    assert context.budget.max_llm_calls == 0
