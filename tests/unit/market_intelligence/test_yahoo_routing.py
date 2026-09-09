from collections.abc import Mapping

from pydantic import JsonValue

from tiaf.market_intelligence import (
    CapabilityRoutePolicy,
    MarketIntelligenceCapability,
    MarketIntelligenceRegistry,
    MarketIntelligenceRouter,
    ProviderFailureKind,
    ProviderResultStatus,
    RoutingMode,
    tapetide_normalizer,
    yahoo_secondary_route_policy,
)
from tiaf.market_intelligence.providers import (
    TapetideMarketIntelligenceProvider,
    YahooMarketIntelligenceProvider,
    yahoo_normalizer,
)

from ._support import AS_OF, request


class StaticClient:
    def __init__(self, response: Mapping[str, object] | Exception) -> None:
        self.response = response
        self.calls: list[tuple[str, dict[str, JsonValue]]] = []

    def call_tool(
        self, tool_name: str, arguments: Mapping[str, JsonValue]
    ) -> Mapping[str, object]:
        self.calls.append((tool_name, dict(arguments)))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def registry_with(
    tapetide_client: StaticClient,
    yahoo_client: StaticClient,
) -> MarketIntelligenceRegistry:
    registry = MarketIntelligenceRegistry()
    registry.register(
        TapetideMarketIntelligenceProvider(tapetide_client), tapetide_normalizer()
    )
    registry.register(
        YahooMarketIntelligenceProvider(yahoo_client, wall_clock=lambda: AS_OF),
        yahoo_normalizer(),
    )
    return registry


def yahoo_financials(value: float = 100.0) -> Mapping[str, object]:
    return {
        "structuredContent": {
            "ticker": "RELIANCE.NS",
            "statement_type": "Income Statement",
            "period_type": "annual",
            "data": {"FY2026": {"Total Revenue": value}},
        }
    }


def test_tapetide_rate_limited_routes_to_real_yahoo_adapter() -> None:
    tapetide = StaticClient(
        {
            "isError": False,
            "content": [
                {"type": "text", "text": "Tapetide rate limit reached. Request denied."}
            ],
        }
    )
    yahoo = StaticClient(yahoo_financials())
    run = MarketIntelligenceRouter(registry_with(tapetide, yahoo)).execute(
        request(required=("fundamental.revenue",), max_calls=2, max_cost=2),
        yahoo_secondary_route_policy(
            MarketIntelligenceCapability.READ_FINANCIALS,
            required_canonical_metrics=("fundamental.revenue",),
        ),
        run_id="yahoo-rate-fallback",
    )
    assert tapetide.calls and yahoo.calls
    assert tuple(item.status for item in run.audits) == (
        ProviderResultStatus.RATE_LIMITED,
        ProviderResultStatus.SUCCESS,
    )
    assert run.failures[0].kind is ProviderFailureKind.RATE_LIMIT
    assert run.batches[0].provider_id == "yahoo"
    assert run.batches[0].canonical_evidence[0].metric == "fundamental.revenue"
    assert run.coverage.sufficient


def test_tapetide_unavailable_routes_to_yahoo() -> None:
    tapetide = StaticClient(RuntimeError("transport unavailable"))
    yahoo = StaticClient(yahoo_financials())
    run = MarketIntelligenceRouter(registry_with(tapetide, yahoo)).execute(
        request(required=("fundamental.revenue",), max_calls=2, max_cost=2),
        yahoo_secondary_route_policy(
            MarketIntelligenceCapability.READ_FINANCIALS,
            required_canonical_metrics=("fundamental.revenue",),
        ),
        run_id="yahoo-unavailable-fallback",
    )
    assert tapetide.calls and yahoo.calls
    assert run.audits[0].status is ProviderResultStatus.UNAVAILABLE
    assert run.audits[1].status is ProviderResultStatus.SUCCESS
    assert run.coverage.sufficient


def test_tapetide_unsupported_capability_routes_to_yahoo_earnings() -> None:
    tapetide = StaticClient({})
    yahoo = StaticClient(
        {
            "structuredContent": {
                "ticker": "RELIANCE.NS",
                "earnings_history": [
                    {
                        "date": "2026-09-30",
                        "eps_estimate": 12.0,
                        "eps_reported": None,
                        "surprise_percent": None,
                    }
                ],
            }
        }
    )
    capability = MarketIntelligenceCapability.READ_EARNINGS_CALENDAR
    run = MarketIntelligenceRouter(registry_with(tapetide, yahoo)).execute(
        request(capability, max_calls=2, max_cost=2),
        CapabilityRoutePolicy(
            capability=capability,
            mode=RoutingMode.PRIMARY_WITH_FALLBACK,
            provider_ids=("tapetide", "yahoo"),
            maximum_provider_calls=2,
        ),
        run_id="yahoo-unsupported-fallback",
    )
    assert tapetide.calls == []
    assert yahoo.calls
    assert run.audits[0].provider_id == "yahoo"
    assert len(run.batches[0].normalized_events) == 1


def test_rate_limited_fallback_forbidden_does_not_call_yahoo() -> None:
    tapetide = StaticClient(
        {
            "isError": False,
            "content": [{"type": "text", "text": "Tapetide rate limit reached."}],
        }
    )
    yahoo = StaticClient(yahoo_financials())
    run = MarketIntelligenceRouter(registry_with(tapetide, yahoo)).execute(
        request(max_calls=2, max_cost=2),
        CapabilityRoutePolicy(
            capability=MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.PRIMARY_WITH_FALLBACK,
            provider_ids=("tapetide", "yahoo"),
            maximum_provider_calls=2,
            fallback_statuses=(ProviderResultStatus.OUT_OF_COVERAGE,),
        ),
        run_id="yahoo-forbidden-fallback",
    )
    assert tapetide.calls
    assert yahoo.calls == []
    assert run.failures[0].kind is ProviderFailureKind.RATE_LIMIT


def test_both_providers_fail_without_fabricated_evidence() -> None:
    tapetide = StaticClient(RuntimeError("transport unavailable"))
    yahoo = StaticClient({"structuredContent": {"error": "financials out of coverage"}})
    run = MarketIntelligenceRouter(registry_with(tapetide, yahoo)).execute(
        request(max_calls=2, max_cost=2),
        yahoo_secondary_route_policy(MarketIntelligenceCapability.READ_FINANCIALS),
        run_id="both-providers-fail",
    )
    assert tapetide.calls and yahoo.calls
    assert run.batches == ()
    assert not run.coverage.sufficient
    assert {item.kind for item in run.failures} >= {
        ProviderFailureKind.PROVIDER_UNAVAILABLE,
        ProviderFailureKind.OUT_OF_COVERAGE,
    }


def test_multi_source_preserves_both_values_and_creates_contradiction() -> None:
    tapetide = StaticClient(
        {
            "structuredContent": {
                "source_url": "https://example.test/tapetide/reliance",
                "published_at": "2026-08-01",
                "data": {"FY2026": {"Revenue from Operations": 100.0}},
            }
        }
    )
    yahoo = StaticClient(yahoo_financials(110.0))
    run = MarketIntelligenceRouter(registry_with(tapetide, yahoo)).execute(
        request(required=("fundamental.revenue",), max_calls=2, max_cost=2),
        yahoo_secondary_route_policy(
            MarketIntelligenceCapability.READ_FINANCIALS,
            mode=RoutingMode.MULTI_SOURCE,
            required_canonical_metrics=("fundamental.revenue",),
        ),
        run_id="yahoo-multi-source",
    )
    assert tuple(item.provider_id for item in run.batches) == ("tapetide", "yahoo")
    values = tuple(
        item.value for batch in run.batches for item in batch.canonical_evidence
    )
    assert values == (100.0, 110.0)
    assert len(run.contradictions) == 1
    assert run.contradictions[0].provider_ids == ("tapetide", "yahoo")
    assert run.contradictions[0].resolution.value == "UNRESOLVED"
    assert run.compute_fingerprint() == run.fingerprint
    calls_before_replay = (len(tapetide.calls), len(yahoo.calls))
    restored = type(run).model_validate_json(run.model_dump_json())
    assert restored == run
    assert restored.compute_fingerprint() == run.fingerprint
    assert (len(tapetide.calls), len(yahoo.calls)) == calls_before_replay
