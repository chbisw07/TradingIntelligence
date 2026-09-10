from __future__ import annotations

from datetime import timedelta
from typing import cast

import pytest
from pydantic import ValidationError

from tiaf.agents import AgentBudget, AgentCapability, AgentUsage
from tiaf.contracts import DataQuality, FreshnessState, Horizon
from tiaf.events import EventMateriality, StructuredEventFact, StructuredFactKind
from tiaf.market_intelligence import (
    AuthoritativeConfirmationRequest,
    AuthoritativeConfirmationResult,
    AuthoritativeConfirmationTask,
    AuthoritativeDocumentKind,
    AvailabilityBasis,
    CapabilityRoutePolicy,
    CapabilitySupport,
    ConfirmationReasonCode,
    ConfirmationStatus,
    DeepResearchIntegrationController,
    DeepResearchResult,
    DerivationClass,
    DiscoveredClaim,
    EpistemicKind,
    EvidenceOutputType,
    GraphEdgeStatus,
    MarketIntelligenceCapability,
    MarketIntelligenceRegistry,
    MarketIntelligenceRequest,
    MarketIntelligenceResearchController,
    MarketIntelligenceResearchPolicy,
    MarketIntelligenceResearchRequest,
    MarketIntelligenceRouter,
    MaterialityTrigger,
    OfficialSourceKind,
    PointInTimeQuality,
    ProviderCapabilityConstraints,
    ProviderCapabilityDeclaration,
    ProviderFetchResult,
    ProviderNativeObservation,
    ProviderResultStatus,
    ResearchAssertion,
    ResearchDepth,
    ResearchStatus,
    RoutingMode,
    RuleBasedNormalizer,
    SemanticMappingQuality,
    SemanticRule,
    SourceAuthority,
    authority_for,
)
from tiaf.market_intelligence.providers import FixtureMarketIntelligenceProvider

from ._support import AS_OF


def _native(
    provider_id: str,
    capability: MarketIntelligenceCapability,
    observation_id: str,
    field: str,
    value: str | int | float | bool,
    *,
    period: str | None = None,
) -> ProviderNativeObservation:
    return ProviderNativeObservation(
        observation_id=observation_id,
        provider_id=provider_id,
        capability=capability,
        subject="RELIANCE",
        native_field=field,
        native_label=field,
        value=value,
        period_label=period,
        available_from=AS_OF - timedelta(days=1),
        acquired_at=AS_OF,
        availability_basis=AvailabilityBasis.PROVIDER_AVAILABLE_FROM,
        point_in_time_quality=PointInTimeQuality.EXACT,
        source_reference=f"https://example.test/{provider_id}/{observation_id}",
        source_quality=DataQuality.GOOD,
        output_type=EvidenceOutputType.SECONDARY_STRUCTURED,
        derivation_class=DerivationClass.REPORTED,
    )


def _declaration(capability: MarketIntelligenceCapability) -> ProviderCapabilityDeclaration:
    return ProviderCapabilityDeclaration(
        capability=capability,
        support=CapabilitySupport.FULL,
        constraints=ProviderCapabilityConstraints(
            output_types=(EvidenceOutputType.SECONDARY_STRUCTURED,),
            source_authority=SourceAuthority.TRUSTED_SECONDARY,
            point_in_time_quality=PointInTimeQuality.EXACT,
            cost_units_per_call=0,
            normalizer_id="fixture",
            normalizer_version="1.0",
            native_schema_version="1.0",
        ),
    )


def _fetch_result(
    provider_id: str,
    capability: MarketIntelligenceCapability,
    *observations: ProviderNativeObservation,
) -> ProviderFetchResult:
    return ProviderFetchResult(
        provider_id=provider_id,
        capability=capability,
        status=ProviderResultStatus.SUCCESS,
        observations=observations,
    )


def _registry(
    provider_results: dict[
        str, dict[tuple[str, str], ProviderFetchResult]
    ],
    capabilities: tuple[MarketIntelligenceCapability, ...],
) -> tuple[MarketIntelligenceRegistry, dict[str, FixtureMarketIntelligenceProvider]]:
    registry = MarketIntelligenceRegistry()
    providers: dict[str, FixtureMarketIntelligenceProvider] = {}
    rules = (
        SemanticRule(
            "Name",
            "company.name",
            SemanticMappingQuality.EXACT,
            rule_id="fixture-name",
            requires_period=False,
        ),
        SemanticRule(
            "Sector",
            "company.sector",
            SemanticMappingQuality.WELL_SUPPORTED,
            rule_id="fixture-sector",
            requires_period=False,
        ),
        SemanticRule(
            "Industry",
            "company.industry",
            SemanticMappingQuality.WELL_SUPPORTED,
            rule_id="fixture-industry",
            requires_period=False,
        ),
        SemanticRule(
            "Revenue",
            "fundamental.revenue",
            SemanticMappingQuality.EXACT,
            rule_id="fixture-revenue",
        ),
        SemanticRule(
            "EBITDA",
            "fundamental.ebitda",
            SemanticMappingQuality.EXACT,
            rule_id="fixture-ebitda",
        ),
        SemanticRule(
            "Supplier",
            None,
            SemanticMappingQuality.AMBIGUOUS,
            rule_id="fixture-supplier-ambiguous",
            requires_period=False,
        ),
    )
    for provider_id, results in provider_results.items():
        provider = FixtureMarketIntelligenceProvider(
            provider_id,
            tuple(_declaration(item) for item in capabilities),
            results,
        )
        registry.register(provider, RuleBasedNormalizer(provider_id, rules))
        providers[provider_id] = provider
    return registry, providers


def _capability_request(
    capability: MarketIntelligenceCapability,
    subject: str,
    *,
    max_calls: int = 1,
    required: tuple[str, ...] = (),
) -> MarketIntelligenceRequest:
    authority = authority_for(capability)
    return MarketIntelligenceRequest(
        request_id=f"request:{subject}:{capability.value}",
        capability=capability,
        authority=authority,
        allowed_authorities=(authority,),
        subject=subject,
        as_of=AS_OF,
        horizon=Horizon(label="POSITIONAL"),
        required_freshness=FreshnessState.UNKNOWN,
        required_canonical_metrics=required,
        budget=AgentBudget(
            max_tool_calls=max_calls,
            max_cost_units=10,
            max_elapsed_seconds=30,
        ),
    )


def _execute(
    registry: MarketIntelligenceRegistry,
    capability_requests: tuple[MarketIntelligenceRequest, ...],
    routes: tuple[CapabilityRoutePolicy, ...],
    *,
    subject: str = "RELIANCE",
) -> DeepResearchResult:
    request = MarketIntelligenceResearchRequest(
        research_request_id=f"research:{subject}",
        subject=subject,
        as_of=AS_OF,
        horizon=Horizon(label="POSITIONAL"),
        capability_requests=capability_requests,
        budget=AgentBudget(
            max_tool_calls=sum(item.budget.max_tool_calls for item in capability_requests),
            max_cost_units=sum(
                item.budget.max_cost_units for item in capability_requests
            ),
            max_elapsed_seconds=120,
        ),
    )
    policy = MarketIntelligenceResearchPolicy(
        plan_id="deep-research-fixture",
        plan_version="1.0",
        routes=routes,
    )
    return DeepResearchIntegrationController(
        MarketIntelligenceResearchController(MarketIntelligenceRouter(registry))
    ).execute(
        request,
        policy,
        research_id=f"deep:{subject}",
        objective="bounded company research",
        depth=ResearchDepth.L2_INVESTMENT_RESEARCH,
        a2_evidence_fingerprint="a" * 64,
    )


def _route(
    capability: MarketIntelligenceCapability,
    providers: tuple[str, ...],
    *,
    mode: RoutingMode = RoutingMode.FIRST_SUCCESS,
    required: tuple[str, ...] = (),
) -> CapabilityRoutePolicy:
    return CapabilityRoutePolicy(
        capability=capability,
        mode=mode,
        provider_ids=providers,
        maximum_provider_calls=len(providers),
        minimum_successful_providers=(2 if mode is RoutingMode.MULTI_SOURCE else 1),
        required_canonical_metrics=required,
    )


def test_multicapability_no_llm_context_graph_gaps_and_replay() -> None:
    profile = MarketIntelligenceCapability.READ_COMPANY_PROFILE
    financials = MarketIntelligenceCapability.READ_FINANCIALS
    supplier = MarketIntelligenceCapability.READ_SUPPLIER_EXPOSURE
    results = {
        (profile.value, "RELIANCE"): _fetch_result(
            "primary",
            profile,
            _native("primary", profile, "name", "Name", "Reliance Industries"),
            _native("primary", profile, "sector", "Sector", "Energy"),
        ),
        (financials.value, "RELIANCE"): _fetch_result(
            "primary",
            financials,
            _native("primary", financials, "revenue", "Revenue", 100, period="FY2026"),
        ),
    }
    registry, _ = _registry({"primary": results}, (profile, financials, supplier))
    output = _execute(
        registry,
        (
            _capability_request(profile, "RELIANCE"),
            _capability_request(financials, "RELIANCE"),
            _capability_request(supplier, "RELIANCE"),
        ),
        (
            _route(profile, ("primary",)),
            _route(financials, ("primary",)),
            _route(supplier, ("primary",)),
        ),
    )

    assert output.usage.llm_calls == output.usage.input_tokens == output.usage.output_tokens == 0
    assert output.profile.status is ResearchStatus.PARTIAL
    assert output.context.a2_evidence_fingerprint == "a" * 64
    assert output.context.provider_ids == ("primary",)
    assert output.context.evidence_quality
    assert any(gap.capability == supplier.value for gap in output.context.research_gaps)
    assert any(edge.relation.value == "BELONGS_TO_SECTOR" for edge in output.evidence_graph.edges)
    assert "native_observations" not in type(output.context).model_fields
    restored = DeepResearchResult.model_validate_json(output.model_dump_json())
    assert restored == output
    assert restored.semantic_fingerprint == output.semantic_fingerprint


def test_primary_sufficiency_avoids_unnecessary_secondary_call() -> None:
    capability = MarketIntelligenceCapability.READ_FINANCIALS
    key = (capability.value, "RELIANCE")
    registry, providers = _registry(
        {
            "primary": {
                key: _fetch_result(
                    "primary",
                    capability,
                    _native("primary", capability, "p-revenue", "Revenue", 100, period="FY2026"),
                )
            },
            "secondary": {
                key: _fetch_result(
                    "secondary",
                    capability,
                    _native("secondary", capability, "s-revenue", "Revenue", 100, period="FY2026"),
                )
            },
        },
        (capability,),
    )
    output = _execute(
        registry,
        (
            _capability_request(
                capability,
                "RELIANCE",
                max_calls=2,
                required=("fundamental.revenue",),
            ),
        ),
        (_route(capability, ("primary", "secondary"), required=("fundamental.revenue",)),),
    )
    assert providers["primary"].calls
    assert providers["secondary"].calls == []
    assert output.profile.status is ResearchStatus.SUCCESS


def test_primary_failure_falls_back_and_both_fail_stays_a_gap() -> None:
    capability = MarketIntelligenceCapability.READ_FINANCIALS
    key = (capability.value, "RELIANCE")
    registry, providers = _registry(
        {
            "primary": {},
            "secondary": {
                key: _fetch_result(
                    "secondary",
                    capability,
                    _native("secondary", capability, "revenue", "Revenue", 100, period="FY2026"),
                )
            },
        },
        (capability,),
    )
    fallback = _execute(
        registry,
        (_capability_request(capability, "RELIANCE", max_calls=2),),
        (_route(capability, ("primary", "secondary")),),
    )
    assert providers["primary"].calls and providers["secondary"].calls
    assert fallback.acquisition.capability_runs[0].batches[0].provider_id == "secondary"

    failed_registry, _ = _registry({"primary": {}, "secondary": {}}, (capability,))
    failed = _execute(
        failed_registry,
        (_capability_request(capability, "RELIANCE", max_calls=2),),
        (_route(capability, ("primary", "secondary")),),
    )
    assert failed.context.canonical_facts == ()
    assert failed.profile.status is ResearchStatus.INSUFFICIENT_EVIDENCE
    assert failed.context.research_gaps


@pytest.mark.parametrize("secondary_sector", ["Energy", "Industrials"])
def test_multi_source_graph_dedupes_agreement_and_preserves_conflict(
    secondary_sector: str,
) -> None:
    capability = MarketIntelligenceCapability.READ_COMPANY_PROFILE
    key = (capability.value, "RELIANCE")
    registry, _ = _registry(
        {
            "primary": {
                key: _fetch_result(
                    "primary",
                    capability,
                    _native("primary", capability, "p-sector", "Sector", "Energy"),
                )
            },
            "secondary": {
                key: _fetch_result(
                    "secondary",
                    capability,
                    _native("secondary", capability, "s-sector", "Sector", secondary_sector),
                )
            },
        },
        (capability,),
    )
    output = _execute(
        registry,
        (_capability_request(capability, "RELIANCE", max_calls=2),),
        (_route(capability, ("primary", "secondary"), mode=RoutingMode.MULTI_SOURCE),),
    )
    sector_edges = [
        item for item in output.evidence_graph.edges if item.relation.value == "BELONGS_TO_SECTOR"
    ]
    if secondary_sector == "Energy":
        assert len(sector_edges) == 1
        assert output.context.contradictions == ()
    else:
        assert len(sector_edges) == 2
        assert len(output.context.contradictions) == 1
        assert all(item.status is GraphEdgeStatus.UNCERTAIN for item in sector_edges)
        assert all(item.contradiction_unresolved for item in sector_edges)


def test_ambiguous_dependency_does_not_create_an_invented_graph_edge() -> None:
    capability = MarketIntelligenceCapability.READ_SUPPLIER_EXPOSURE
    key = (capability.value, "RELIANCE")
    registry, _ = _registry(
        {
            "primary": {
                key: _fetch_result(
                    "primary",
                    capability,
                    _native("primary", capability, "supplier", "Supplier", "Example Ltd"),
                )
            }
        },
        (capability,),
    )
    output = _execute(
        registry,
        (_capability_request(capability, "RELIANCE"),),
        (_route(capability, ("primary",)),),
    )
    assert output.context.ambiguous_evidence
    assert output.evidence_graph.edges == ()
    assert output.profile.status is ResearchStatus.INSUFFICIENT_EVIDENCE


def test_fact_cannot_be_promoted_and_result_rejects_out_of_context_citation() -> None:
    with pytest.raises(ValidationError, match="cannot be promoted"):
        ResearchAssertion(
            assertion_id="fact",
            kind=EpistemicKind.FACT,
            statement="Not directly evidenced",
            evidence_ids=("evidence",),
            supporting_assertion_ids=("another-assertion",),
        )

    capability = MarketIntelligenceCapability.READ_FINANCIALS
    key = (capability.value, "RELIANCE")
    registry, _ = _registry(
        {
            "primary": {
                key: _fetch_result(
                    "primary",
                    capability,
                    _native("primary", capability, "revenue", "Revenue", 100, period="FY2026"),
                )
            }
        },
        (capability,),
    )
    output = _execute(
        registry,
        (_capability_request(capability, "RELIANCE"),),
        (_route(capability, ("primary",)),),
    )
    payload = output.model_dump(mode="json")
    components = cast(list[dict[str, object]], payload["components"])
    assertions = cast(list[dict[str, object]], components[0]["assertions"])
    assertions[0]["evidence_ids"] = ["outside-context"]
    with pytest.raises(ValidationError, match="outside the context"):
        DeepResearchResult.model_validate(payload)


def test_inference_and_hypothesis_require_explicit_epistemic_lineage() -> None:
    inference = ResearchAssertion(
        assertion_id="inference",
        kind=EpistemicKind.INFERENCE,
        statement="Margins appear sensitive to an evidenced input.",
        supporting_assertion_ids=("fact",),
        reasoning="The cited fact identifies the input relationship.",
    )
    hypothesis = ResearchAssertion(
        assertion_id="hypothesis",
        kind=EpistemicKind.HYPOTHESIS,
        statement="Margins may improve if that input becomes cheaper.",
        supporting_assertion_ids=(inference.assertion_id,),
        assumptions=("the input price declines",),
        invalidation_conditions=("the input price remains elevated",),
    )
    assert inference.evidence_ids == ()
    assert hypothesis.assumptions and hypothesis.invalidation_conditions
    with pytest.raises(ValidationError, match="invalidation conditions"):
        ResearchAssertion(
            assertion_id="invalid-hypothesis",
            kind=EpistemicKind.HYPOTHESIS,
            statement="Unconditional claim",
            supporting_assertion_ids=("fact",),
            assumptions=("one assumption",),
        )


def test_hdfcbank_sector_safety_withholds_industrial_interpretation() -> None:
    profile = MarketIntelligenceCapability.READ_COMPANY_PROFILE
    financials = MarketIntelligenceCapability.READ_FINANCIALS
    results = {
        (profile.value, "HDFCBANK"): _fetch_result(
            "primary",
            profile,
            _native("primary", profile, "bank-sector", "Sector", "Financial Services").model_copy(
                update={"subject": "HDFCBANK"}
            ),
        ),
        (financials.value, "HDFCBANK"): _fetch_result(
            "primary",
            financials,
            _native("primary", financials, "bank-ebitda", "EBITDA", 10, period="FY2026").model_copy(
                update={"subject": "HDFCBANK"}
            ),
        ),
    }
    registry, _ = _registry({"primary": results}, (profile, financials))
    output = _execute(
        registry,
        (
            _capability_request(profile, "HDFCBANK"),
            _capability_request(financials, "HDFCBANK"),
        ),
        (_route(profile, ("primary",)), _route(financials, ("primary",))),
        subject="HDFCBANK",
    )
    statements = tuple(
        assertion.statement for component in output.components for assertion in component.assertions
    )
    assert not any("ebitda" in item.casefold() for item in statements)
    assert any("Sector safety withheld" in gap.description for gap in output.components[0].gaps)
    assert any(item.metric == "fundamental.ebitda" for item in output.context.canonical_facts)


def test_atherenerg_sparse_history_remains_missing() -> None:
    capability = MarketIntelligenceCapability.READ_FINANCIALS
    registry, _ = _registry({"primary": {}}, (capability,))
    output = _execute(
        registry,
        (_capability_request(capability, "ATHERENERG"),),
        (_route(capability, ("primary",)),),
        subject="ATHERENERG",
    )
    assert output.context.canonical_facts == ()
    assert output.profile.status is ResearchStatus.INSUFFICIENT_EVIDENCE
    assert all(not item.assertions for item in output.components)


class _ConfirmationGateway:
    def __init__(self, result: AuthoritativeConfirmationResult) -> None:
        self.result = result
        self.calls = 0

    def execute(
        self,
        request: AuthoritativeConfirmationRequest,
        route_policy: CapabilityRoutePolicy,
        *,
        run_id: str,
        confirmation_id: str,
    ) -> AuthoritativeConfirmationResult:
        del request, route_policy, run_id, confirmation_id
        self.calls += 1
        return self.result


def test_material_claim_authoritative_result_is_linked_into_replay() -> None:
    capability = MarketIntelligenceCapability.READ_FINANCIALS
    key = (capability.value, "RELIANCE")
    registry, _ = _registry(
        {
            "primary": {
                key: _fetch_result(
                    "primary",
                    capability,
                    _native("primary", capability, "revenue", "Revenue", 100, period="FY2026"),
                )
            }
        },
        (capability,),
    )
    cap_request = _capability_request(capability, "RELIANCE")
    acquisition_request = MarketIntelligenceResearchRequest(
        research_request_id="research:authority",
        subject="RELIANCE",
        as_of=AS_OF,
        horizon=Horizon(label="POSITIONAL"),
        capability_requests=(cap_request,),
        budget=AgentBudget(max_tool_calls=2, max_cost_units=10, max_elapsed_seconds=60),
    )
    policy = MarketIntelligenceResearchPolicy(
        plan_id="authority",
        plan_version="1.0",
        routes=(_route(capability, ("primary",)),),
    )
    discovery_id = RuleBasedNormalizer(
        "primary",
        (
            SemanticRule(
                "Revenue",
                "fundamental.revenue",
                SemanticMappingQuality.EXACT,
                rule_id="fixture-revenue",
            ),
        ),
    ).normalize(cap_request, registry.provider("primary").fetch(cap_request)).canonical_evidence[
        0
    ].evidence_id
    claim = DiscoveredClaim(
        claim_id="claim:revenue",
        subject="RELIANCE",
        capability=capability,
        asserted_facts=(
            StructuredEventFact(
                field_id="fundamental.revenue",
                kind=StructuredFactKind.NUMBER,
                value=100.0,
            ),
        ),
        discovery_evidence_ids=(discovery_id,),
        materiality=EventMateriality.HIGH,
        available_from=AS_OF - timedelta(days=1),
        created_at=AS_OF,
    )
    confirmation_request = AuthoritativeConfirmationRequest(
        request_id="confirm:revenue",
        claim=claim,
        as_of=AS_OF,
        horizon=Horizon(label="POSITIONAL"),
        authority=AgentCapability.READ_FUNDAMENTALS,
        allowed_authorities=(AgentCapability.READ_FUNDAMENTALS,),
        accepted_document_kinds=(AuthoritativeDocumentKind.FINANCIAL_RESULT,),
        eligible_source_kinds=(OfficialSourceKind.EXCHANGE_OR_REGULATOR,),
        required_fields=("fundamental.revenue",),
        materiality_triggers=(MaterialityTrigger.FINANCIAL_RESULTS,),
        budget=AgentBudget(max_tool_calls=1, max_cost_units=0, max_elapsed_seconds=30),
        route_policy_id="official",
        route_policy_version="1.0",
    )
    reason_codes = (ConfirmationReasonCode.DOCUMENT_NOT_FOUND,)
    confirmation_fingerprint = AuthoritativeConfirmationResult.fingerprint_for(
        confirmation_id="confirmation:revenue",
        request=confirmation_request,
        status=ConfirmationStatus.NOT_FOUND,
        authoritative_documents=(),
        authoritative_evidence_ids=(),
        confirmed_facts=(),
        unresolved_discrepancies=(),
        source_authority=None,
        reason_codes=reason_codes,
        route_run_id="official:run",
        route_run_fingerprint="f" * 64,
        route_audits=(),
        event_cluster_id=None,
        evidence_graph_node_ids=(),
        confirmed_at=AS_OF,
        quality=DataQuality.UNAVAILABLE,
    )
    confirmation = AuthoritativeConfirmationResult(
        confirmation_id="confirmation:revenue",
        request=confirmation_request,
        status=ConfirmationStatus.NOT_FOUND,
        reason_codes=reason_codes,
        route_run_id="official:run",
        route_run_fingerprint="f" * 64,
        route_audits=(),
        confirmed_at=AS_OF,
        quality=DataQuality.UNAVAILABLE,
        usage=AgentUsage(tool_calls=1),
        semantic_fingerprint=confirmation_fingerprint,
    )
    gateway = _ConfirmationGateway(confirmation)
    output = DeepResearchIntegrationController(
        MarketIntelligenceResearchController(MarketIntelligenceRouter(registry)),
        authoritative_gateway=gateway,
    ).execute(
        acquisition_request,
        policy,
        research_id="deep:authority",
        objective="confirm a material reported financial",
        depth=ResearchDepth.L2_INVESTMENT_RESEARCH,
        a2_evidence_fingerprint="a" * 64,
        confirmation_tasks=(
            AuthoritativeConfirmationTask(
                request=confirmation_request,
                route_policy=CapabilityRoutePolicy(
                    policy_id="official",
                    capability=capability,
                    mode=RoutingMode.AUTHORITATIVE_CONFIRMATION,
                    provider_ids=("official",),
                    authoritative_provider_ids=("official",),
                    maximum_provider_calls=1,
                ),
                run_id="official:run",
                confirmation_id="confirmation:revenue",
            ),
        ),
    )
    assert gateway.calls == 1
    assert output.confirmations == (confirmation,)
    assert output.confirmations[0].request.claim.discovery_evidence_ids == (discovery_id,)
    assert output.confirmations[0].status is ConfirmationStatus.NOT_FOUND
    assert DeepResearchResult.model_validate_json(output.model_dump_json()) == output
