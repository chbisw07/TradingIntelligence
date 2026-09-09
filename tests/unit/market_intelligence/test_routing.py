from collections.abc import Mapping

from pydantic import JsonValue

from tiaf.agents import AgentBudget
from tiaf.contracts import Horizon
from tiaf.market_intelligence import (
    CanonicalEvidenceProjection,
    CapabilityRoutePolicy,
    MarketIntelligenceCapability,
    MarketIntelligenceRegistry,
    MarketIntelligenceRequest,
    MarketIntelligenceResearchController,
    MarketIntelligenceResearchPolicy,
    MarketIntelligenceResearchRequest,
    MarketIntelligenceRouter,
    NormalizedEvidenceBatch,
    PointInTimeQuality,
    ProviderFailureKind,
    ProviderFetchResult,
    ProviderResultStatus,
    RoutingMode,
    RuleBasedNormalizer,
    SemanticMappingQuality,
    SemanticRule,
    tapetide_normalizer,
)
from tiaf.market_intelligence.providers import (
    FixtureMarketIntelligenceProvider,
    TapetideMarketIntelligenceProvider,
)

from ._support import declaration, observation, request, result


def _register(
    registry: MarketIntelligenceRegistry,
    provider_id: str,
    results: dict[tuple[str, str], ProviderFetchResult],
    rules: tuple[SemanticRule, ...],
) -> FixtureMarketIntelligenceProvider:
    provider = FixtureMarketIntelligenceProvider(
        provider_id,
        (declaration(),),
        results,
    )
    registry.register(provider, RuleBasedNormalizer(provider_id, rules))
    return provider


REVENUE_RULE = SemanticRule(
    "Revenue",
    "fundamental.revenue",
    SemanticMappingQuality.EXACT,
    rule_id="fixture-revenue",
)
PROFIT_RULE = SemanticRule(
    "Profit",
    "fundamental.net_income",
    SemanticMappingQuality.EXACT,
    rule_id="fixture-profit",
)


class RateLimitedTapetideClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, JsonValue]]] = []

    def call_tool(
        self, tool_name: str, arguments: Mapping[str, JsonValue]
    ) -> Mapping[str, object]:
        self.calls.append((tool_name, dict(arguments)))
        return {
            "isError": False,
            "content": [
                {
                    "type": "text",
                    "text": "Tapetide rate limit reached. Request denied. Retry in 60s.",
                }
            ],
        }


class NeverNormalizeRateLimit(RuleBasedNormalizer):
    def __init__(self) -> None:
        super().__init__("tapetide")

    def normalize(
        self,
        request: MarketIntelligenceRequest,
        result: ProviderFetchResult,
    ) -> NormalizedEvidenceBatch:
        raise AssertionError("rate-limited provider result must not be normalized")


def test_primary_failure_falls_back_and_substitutes_provider() -> None:
    registry = MarketIntelligenceRegistry()
    first = _register(registry, "primary", {}, (REVENUE_RULE,))
    second_result = result("secondary", observation("secondary", "s1", "Revenue", 100))
    second = _register(
        registry,
        "secondary",
        {(MarketIntelligenceCapability.READ_FINANCIALS.value, "RELIANCE"): second_result},
        (REVENUE_RULE,),
    )
    run = MarketIntelligenceRouter(registry).execute(
        request(required=("fundamental.revenue",)),
        CapabilityRoutePolicy(
            capability=MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.PRIMARY_WITH_FALLBACK,
            provider_ids=("primary", "secondary"),
            maximum_provider_calls=2,
            required_canonical_metrics=("fundamental.revenue",),
        ),
        run_id="run-fallback",
    )
    assert first.calls and second.calls
    assert run.audits[0].status is ProviderResultStatus.OUT_OF_COVERAGE
    assert run.coverage.sufficient
    assert run.batches[0].provider_id == "secondary"


def test_rate_limited_primary_falls_back_when_policy_permits() -> None:
    registry = MarketIntelligenceRegistry()
    primary_client = RateLimitedTapetideClient()
    registry.register(
        TapetideMarketIntelligenceProvider(primary_client), NeverNormalizeRateLimit()
    )
    key = (MarketIntelligenceCapability.READ_FINANCIALS.value, "RELIANCE")
    secondary = _register(
        registry,
        "secondary",
        {key: result("secondary", observation("secondary", "s1", "Revenue", 100))},
        (REVENUE_RULE,),
    )

    run = MarketIntelligenceRouter(registry).execute(
        request(required=("fundamental.revenue",), max_calls=2, max_cost=2),
        CapabilityRoutePolicy(
            capability=MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.PRIMARY_WITH_FALLBACK,
            provider_ids=("tapetide", "secondary"),
            maximum_provider_calls=2,
            required_canonical_metrics=("fundamental.revenue",),
        ),
        run_id="run-rate-limit-fallback",
    )

    assert primary_client.calls and secondary.calls
    assert tuple(audit.status for audit in run.audits) == (
        ProviderResultStatus.RATE_LIMITED,
        ProviderResultStatus.SUCCESS,
    )
    assert run.failures[0].kind is ProviderFailureKind.RATE_LIMIT
    assert run.coverage.sufficient
    assert run.batches[0].provider_id == "secondary"


def test_rate_limited_primary_stops_when_policy_forbids_fallback() -> None:
    registry = MarketIntelligenceRegistry()
    primary_client = RateLimitedTapetideClient()
    registry.register(
        TapetideMarketIntelligenceProvider(primary_client), NeverNormalizeRateLimit()
    )
    secondary = _register(registry, "secondary", {}, (REVENUE_RULE,))

    run = MarketIntelligenceRouter(registry).execute(
        request(required=("fundamental.revenue",), max_calls=2, max_cost=2),
        CapabilityRoutePolicy(
            capability=MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.PRIMARY_WITH_FALLBACK,
            provider_ids=("tapetide", "secondary"),
            maximum_provider_calls=2,
            required_canonical_metrics=("fundamental.revenue",),
            fallback_statuses=(ProviderResultStatus.OUT_OF_COVERAGE,),
        ),
        run_id="run-rate-limit-no-fallback",
    )

    assert primary_client.calls
    assert secondary.calls == []
    assert tuple(audit.status for audit in run.audits) == (
        ProviderResultStatus.RATE_LIMITED,
    )
    assert run.failures[0].kind is ProviderFailureKind.RATE_LIMIT
    assert run.batches == ()
    assert not run.coverage.sufficient


def test_future_available_fixture_evidence_is_excluded() -> None:
    from datetime import timedelta

    registry = MarketIntelligenceRegistry()
    key = (MarketIntelligenceCapability.READ_FINANCIALS.value, "RELIANCE")
    future = observation(
        "future-provider",
        "future-1",
        "Revenue",
        100,
        available_at=request().as_of + timedelta(days=1),
    )
    provider = _register(
        registry,
        "future-provider",
        {key: result("future-provider", future)},
        (REVENUE_RULE,),
    )
    run = MarketIntelligenceRouter(registry).execute(
        request(required=("fundamental.revenue",)),
        CapabilityRoutePolicy(
            capability=MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.FIRST_SUCCESS,
            provider_ids=("future-provider",),
            maximum_provider_calls=1,
        ),
        run_id="run-pit",
    )
    assert provider.calls
    assert run.batches == ()
    assert not run.coverage.sufficient


def test_unregistered_provider_is_a_typed_gap_not_a_crash() -> None:
    run = MarketIntelligenceRouter(MarketIntelligenceRegistry()).execute(
        request(required=("fundamental.revenue",)),
        CapabilityRoutePolicy(
            capability=MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.FIRST_SUCCESS,
            provider_ids=("disabled-provider",),
            maximum_provider_calls=1,
        ),
        run_id="run-disabled",
    )
    assert run.audits == ()
    assert run.failures[0].kind is ProviderFailureKind.PROVIDER_UNAVAILABLE
    assert not run.coverage.sufficient


def test_route_pit_requirement_skips_ineligible_provider_without_calling_it() -> None:
    registry = MarketIntelligenceRegistry()
    provider = _register(registry, "limited", {}, (REVENUE_RULE,))
    run = MarketIntelligenceRouter(registry).execute(
        request(required=("fundamental.revenue",)),
        CapabilityRoutePolicy(
            capability=MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.FIRST_SUCCESS,
            provider_ids=("limited",),
            maximum_provider_calls=1,
            minimum_point_in_time_quality=PointInTimeQuality.EXACT,
        ),
        run_id="run-quality-skip",
    )
    assert provider.calls == []
    assert run.failures[0].kind is ProviderFailureKind.OUT_OF_COVERAGE


def test_first_success_stops_without_fanout() -> None:
    registry = MarketIntelligenceRegistry()
    primary_result = result("primary", observation("primary", "p1", "Revenue", 100))
    primary = _register(
        registry,
        "primary",
        {(MarketIntelligenceCapability.READ_FINANCIALS.value, "RELIANCE"): primary_result},
        (REVENUE_RULE,),
    )
    secondary = _register(registry, "secondary", {}, (REVENUE_RULE,))
    run = MarketIntelligenceRouter(registry).execute(
        request(required=("fundamental.revenue",)),
        CapabilityRoutePolicy(
            capability=MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.FIRST_SUCCESS,
            provider_ids=("primary", "secondary"),
            maximum_provider_calls=2,
            required_canonical_metrics=("fundamental.revenue",),
        ),
        run_id="run-first",
    )
    assert primary.calls
    assert secondary.calls == []
    assert run.usage.tool_calls == 1


def test_split_capability_evidence_uses_bounded_multi_source_enrichment() -> None:
    registry = MarketIntelligenceRegistry()
    revenue = result("financial-a", observation("financial-a", "a1", "Revenue", 100))
    profit = result("financial-b", observation("financial-b", "b1", "Profit", 10))
    key = (MarketIntelligenceCapability.READ_FINANCIALS.value, "RELIANCE")
    _register(registry, "financial-a", {key: revenue}, (REVENUE_RULE,))
    _register(registry, "financial-b", {key: profit}, (PROFIT_RULE,))
    run = MarketIntelligenceRouter(registry).execute(
        request(required=("fundamental.revenue", "fundamental.net_income")),
        CapabilityRoutePolicy(
            capability=MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.MULTI_SOURCE,
            provider_ids=("financial-a", "financial-b"),
            maximum_provider_calls=2,
            minimum_successful_providers=2,
            required_canonical_metrics=(
                "fundamental.revenue",
                "fundamental.net_income",
            ),
        ),
        run_id="run-split",
    )
    assert run.coverage.sufficient
    assert run.coverage.coverage == 1
    assert tuple(item.provider_id for item in run.batches) == (
        "financial-a",
        "financial-b",
    )


def test_conflicting_sources_are_preserved_not_overwritten() -> None:
    registry = MarketIntelligenceRegistry()
    key = (MarketIntelligenceCapability.READ_FINANCIALS.value, "RELIANCE")
    _register(
        registry,
        "a",
        {key: result("a", observation("a", "a1", "Revenue", 100))},
        (REVENUE_RULE,),
    )
    _register(
        registry,
        "b",
        {key: result("b", observation("b", "b1", "Revenue", 110))},
        (REVENUE_RULE,),
    )
    run = MarketIntelligenceRouter(registry).execute(
        request(required=("fundamental.revenue",)),
        CapabilityRoutePolicy(
            capability=MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.MULTI_SOURCE,
            provider_ids=("a", "b"),
            maximum_provider_calls=2,
            minimum_successful_providers=2,
        ),
        run_id="run-conflict",
    )
    assert len(run.batches) == 2
    assert all(
        isinstance(item, CanonicalEvidenceProjection)
        for batch in run.batches
        for item in batch.canonical_evidence
    )
    assert len(run.contradictions) == 1
    assert run.contradictions[0].resolution.value == "UNRESOLVED"


def test_tool_budget_stops_progressive_enrichment() -> None:
    registry = MarketIntelligenceRegistry()
    key = (MarketIntelligenceCapability.READ_FINANCIALS.value, "RELIANCE")
    first = result("a", observation("a", "a1", "Revenue", 100))
    _register(registry, "a", {key: first}, (REVENUE_RULE,))
    second = _register(registry, "b", {}, (PROFIT_RULE,))
    run = MarketIntelligenceRouter(registry).execute(
        request(required=("fundamental.revenue", "fundamental.net_income"), max_calls=1),
        CapabilityRoutePolicy(
            capability=MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.MULTI_SOURCE,
            provider_ids=("a", "b"),
            maximum_provider_calls=2,
            minimum_successful_providers=2,
        ),
        run_id="run-budget",
    )
    assert second.calls == []
    assert run.decisions[-1].action.value == "STOP_BUDGET"
    assert not run.coverage.sufficient


def test_run_reconstructs_and_fingerprint_is_stable() -> None:
    registry = MarketIntelligenceRegistry()
    key = (MarketIntelligenceCapability.READ_FINANCIALS.value, "RELIANCE")
    one = result("a", observation("a", "a1", "Revenue", 100))
    _register(registry, "a", {key: one}, (REVENUE_RULE,))
    run = MarketIntelligenceRouter(registry).execute(
        request(),
        CapabilityRoutePolicy(
            capability=MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.FIRST_SUCCESS,
            provider_ids=("a",),
            maximum_provider_calls=1,
        ),
        run_id="run-replay",
    )
    assert type(run).model_validate_json(run.model_dump_json()) == run
    assert run.compute_fingerprint() == run.fingerprint
    assert run.usage.llm_calls == run.usage.input_tokens == run.usage.output_tokens == 0


def test_authoritative_confirmation_escalates_only_after_ambiguity() -> None:
    registry = MarketIntelligenceRegistry()
    key = (MarketIntelligenceCapability.READ_FINANCIALS.value, "RELIANCE")
    ambiguous = result("primary", observation("primary", "p1", "Sales", 100))
    exact = result("authority", observation("authority", "a1", "Revenue", 100))
    _register(registry, "primary", {key: ambiguous}, ())
    authority = _register(registry, "authority", {key: exact}, (REVENUE_RULE,))
    run = MarketIntelligenceRouter(registry).execute(
        request(required=("fundamental.revenue",)),
        CapabilityRoutePolicy(
            capability=MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.AUTHORITATIVE_CONFIRMATION,
            provider_ids=("primary", "authority"),
            authoritative_provider_ids=("authority",),
            maximum_provider_calls=2,
            required_canonical_metrics=("fundamental.revenue",),
        ),
        run_id="run-authority",
    )
    assert authority.calls
    assert run.coverage.sufficient
    assert run.audits[-1].provider_id == "authority"


def test_shared_upstream_lineage_is_not_independent_contradiction() -> None:
    registry = MarketIntelligenceRegistry()
    key = (MarketIntelligenceCapability.READ_FINANCIALS.value, "RELIANCE")
    _register(
        registry,
        "a",
        {key: result("a", observation("a", "source-1", "Revenue", 100))},
        (REVENUE_RULE,),
    )
    copied = observation("b", "copy-1", "Revenue", 110, lineage=("source-1",))
    _register(registry, "b", {key: result("b", copied)}, (REVENUE_RULE,))
    run = MarketIntelligenceRouter(registry).execute(
        request(required=("fundamental.revenue",)),
        CapabilityRoutePolicy(
            capability=MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.MULTI_SOURCE,
            provider_ids=("a", "b"),
            maximum_provider_calls=2,
            minimum_successful_providers=2,
        ),
        run_id="run-lineage",
    )
    assert run.contradictions == ()


def test_one_research_request_routes_split_capabilities_without_provider_awareness() -> None:
    financial_cap = MarketIntelligenceCapability.READ_FINANCIALS
    customer_cap = MarketIntelligenceCapability.READ_CUSTOMER_EXPOSURE
    registry = MarketIntelligenceRegistry()
    customer_key = (customer_cap.value, "RELIANCE")

    class TapetideClient:
        def call_tool(
            self, tool_name: str, arguments: Mapping[str, JsonValue]
        ) -> Mapping[str, object]:
            assert tool_name == "get_financials"
            assert arguments["symbol"] == "RELIANCE"
            return {
                "structuredContent": {
                    "source_url": "https://example.test/reliance-filing",
                    "published_at": "2025-05-01",
                    "data": {"FY2025": {"Revenue from Operations": 100}},
                }
            }

    registry.register(TapetideMarketIntelligenceProvider(TapetideClient()), tapetide_normalizer())
    customer_observation = observation(
        "research-fixture",
        "c1",
        "Customer dependency",
        0.25,
        capability=customer_cap,
        period=None,
    )
    customer_provider = FixtureMarketIntelligenceProvider(
        "research-fixture",
        (declaration(customer_cap),),
        {customer_key: result("research-fixture", customer_observation)},
    )
    customer_rule = SemanticRule(
        "Customer dependency",
        "company.customer_exposure",
        SemanticMappingQuality.EXACT,
        rule_id="fixture-customer-exposure",
        requires_period=False,
    )
    registry.register(
        customer_provider,
        RuleBasedNormalizer("research-fixture", (customer_rule,)),
    )
    financial_request = request(
        financial_cap, required=("fundamental.revenue",), max_calls=1, max_cost=1
    )
    customer_request = request(
        customer_cap,
        required=("company.customer_exposure",),
        max_calls=1,
        max_cost=1,
    )
    research_request = MarketIntelligenceResearchRequest(
        research_request_id="research-request-1",
        subject="RELIANCE",
        as_of=financial_request.as_of,
        horizon=Horizon(label="POSITIONAL"),
        capability_requests=(financial_request, customer_request),
        budget=AgentBudget(max_tool_calls=2, max_cost_units=2, max_elapsed_seconds=30),
    )
    policy = MarketIntelligenceResearchPolicy(
        plan_id="split-provider-plan",
        plan_version="1.0",
        routes=(
            CapabilityRoutePolicy(
                capability=financial_cap,
                mode=RoutingMode.FIRST_SUCCESS,
                provider_ids=("tapetide",),
                maximum_provider_calls=1,
                required_canonical_metrics=("fundamental.revenue",),
            ),
            CapabilityRoutePolicy(
                capability=customer_cap,
                mode=RoutingMode.FIRST_SUCCESS,
                provider_ids=("research-fixture",),
                maximum_provider_calls=1,
                required_canonical_metrics=("company.customer_exposure",),
            ),
        ),
    )
    run = MarketIntelligenceResearchController(MarketIntelligenceRouter(registry)).execute(
        research_request, policy, research_run_id="research-run-1"
    )
    assert tuple(item.request.capability for item in run.capability_runs) == (
        financial_cap,
        customer_cap,
    )
    assert all(item.coverage.sufficient for item in run.capability_runs)
    assert run.usage.tool_calls == 2
    assert run.usage.llm_calls == 0
    assert type(run).model_validate_json(run.model_dump_json()) == run
