import json
from collections.abc import Mapping
from math import nan

import pytest
from pydantic import JsonValue

from tiaf.market_intelligence import (
    CapabilitySupport,
    MarketIntelligenceCapability,
    NormalizedEvidenceBatch,
    ProviderFailureKind,
    ProviderResultStatus,
    RoutingMode,
    SemanticMappingQuality,
    yahoo_secondary_route_policy,
)
from tiaf.market_intelligence.providers import (
    YahooMarketIntelligenceProvider,
    YahooSymbolMapper,
    india_yahoo_symbol_mapper,
    yahoo_normalizer,
)

from ._support import AS_OF, request


class FakeYahooClient:
    def __init__(self, response: Mapping[str, object]) -> None:
        self.response = response
        self.calls: list[tuple[str, dict[str, JsonValue]]] = []

    def call_tool(
        self, tool_name: str, arguments: Mapping[str, JsonValue]
    ) -> Mapping[str, object]:
        self.calls.append((tool_name, dict(arguments)))
        return self.response


def provider(
    response: Mapping[str, object],
    mapper: YahooSymbolMapper | None = None,
) -> tuple[YahooMarketIntelligenceProvider, FakeYahooClient]:
    client = FakeYahooClient(response)
    return (
        YahooMarketIntelligenceProvider(client, mapper, wall_clock=lambda: AS_OF),
        client,
    )


def fastmcp_response(payload: Mapping[str, object]) -> Mapping[str, object]:
    encoded = json.dumps(payload)
    return {
        "structuredContent": {"result": encoded},
        "content": [{"type": "text", "text": encoded}],
    }


def test_explicit_india_symbol_mapping_never_guesses_suffixes() -> None:
    mapper = india_yahoo_symbol_mapper()
    assert mapper.resolve("RELIANCE") == "RELIANCE.NS"
    assert mapper.resolve("hdfcbank") == "HDFCBANK.NS"
    assert mapper.resolve("KAYNES") == "KAYNES.NS"
    assert mapper.resolve("ATHERENERG") == "ATHERENERG.NS"
    assert mapper.resolve("UNKNOWN") is None


def test_unknown_symbol_mapping_fails_before_transport() -> None:
    yahoo, client = provider({"structuredContent": {}}, YahooSymbolMapper(()))
    fetched = yahoo.fetch(request())
    assert client.calls == []
    assert fetched.status is ProviderResultStatus.OUT_OF_COVERAGE
    assert fetched.failures[0].kind is ProviderFailureKind.UNKNOWN_SYMBOL


def test_manifest_declares_only_bounded_supported_capabilities() -> None:
    yahoo, _ = provider({"structuredContent": {}})
    profile = yahoo.manifest.declaration_for(
        MarketIntelligenceCapability.READ_COMPANY_PROFILE
    )
    financials = yahoo.manifest.declaration_for(
        MarketIntelligenceCapability.READ_FINANCIALS
    )
    point_in_time = yahoo.manifest.declaration_for(
        MarketIntelligenceCapability.READ_POINT_IN_TIME_FINANCIALS
    )
    assert profile is not None and profile.support is CapabilitySupport.FULL
    assert financials is not None and financials.support is CapabilitySupport.PARTIAL
    assert point_in_time is not None
    assert point_in_time.support is CapabilitySupport.UNSUPPORTED
    assert "credential" not in str(yahoo.manifest.metadata).casefold()


def test_profile_uses_json_mode_preserves_ticker_and_emits_conservative_canonical() -> None:
    yahoo, client = provider(
        fastmcp_response(
            {
                "ticker": "RELIANCE.NS",
                "name": "Reliance Industries Limited",
                "current_price": 1500.0,
                "currency": "INR",
                "market_cap": 20_000_000,
                "pe_ratio": 24.5,
                "forward_pe": 22.0,
                "sector": "Energy",
                "industry": "Oil & Gas",
                "description": "Integrated energy and consumer company.",
            }
        )
    )
    req = request(MarketIntelligenceCapability.READ_COMPANY_PROFILE)
    fetched = yahoo.fetch(req)
    assert client.calls == [
        (
            "yfinance_get_stock_info",
            {"ticker": "RELIANCE.NS", "response_format": "json"},
        )
    ]
    assert fetched.status is ProviderResultStatus.SUCCESS
    assert all(item.subject == "RELIANCE" for item in fetched.observations)
    assert all(item.metadata["yahoo_ticker"] == "RELIANCE.NS" for item in fetched.observations)
    assert all(item.provider_id == "yahoo" for item in fetched.observations)

    batch = yahoo_normalizer().normalize(req, fetched)
    metrics = {item.metric for item in batch.canonical_evidence}
    assert {"company.name", "market.last_price", "valuation.market_cap"} <= metrics
    assert {"company.sector", "company.industry", "company.description"} <= metrics
    forward = next(
        item for item in batch.normalization_records if item.native_field == "forward_pe"
    )
    assert forward.mapping_quality is SemanticMappingQuality.PROVIDER_DEFINED
    assert forward.emitted_evidence_id is None


def test_financials_preserve_statement_period_and_ambiguous_native_field() -> None:
    yahoo, client = provider(
        fastmcp_response(
            {
                "ticker": "RELIANCE.NS",
                "statement_type": "Income Statement",
                "period_type": "annual",
                "data": {
                    "2026-03-31": {
                        "Total Revenue": 1000.0,
                        "Net Income": 100.0,
                        "Unusual Provider Field": 7.0,
                    }
                },
            }
        )
    )
    req = request().model_copy(
        update={"attributes": {"statement_type": "income", "period": "annual", "limit": 3}}
    )
    fetched = yahoo.fetch(req)
    assert client.calls == [
        (
            "yfinance_get_stock_financials",
            {
                "ticker": "RELIANCE.NS",
                "response_format": "json",
                "statement_type": "income",
                "period": "annual",
                "limit": 3,
            },
        )
    ]
    assert {item.period_label for item in fetched.observations} == {"2026-03-31"}
    assert all(
        item.metadata["statement_type"] == "Income Statement"
        for item in fetched.observations
    )

    batch = yahoo_normalizer().normalize(req, fetched)
    assert {item.metric for item in batch.canonical_evidence} == {
        "fundamental.revenue",
        "fundamental.net_income",
    }
    ambiguous = next(
        item
        for item in batch.normalization_records
        if item.native_field == "Unusual Provider Field"
    )
    assert ambiguous.mapping_quality is SemanticMappingQuality.AMBIGUOUS
    assert ambiguous.emitted_evidence_id is None


def test_earnings_dates_become_factual_events_without_probabilities() -> None:
    yahoo, client = provider(
        fastmcp_response(
            {
                "ticker": "RELIANCE.NS",
                "next_earnings_date": "2026-09-30",
                "earnings_history": [
                    {
                        "date": "2026-06-30",
                        "eps_estimate": 10.0,
                        "eps_reported": 11.0,
                        "surprise_percent": 10.0,
                    },
                    {
                        "date": "2026-09-30",
                        "eps_estimate": 12.0,
                        "eps_reported": None,
                        "surprise_percent": None,
                    },
                ],
            }
        )
    )
    req = request(MarketIntelligenceCapability.READ_EARNINGS_CALENDAR).model_copy(
        update={"attributes": {"limit": 6, "future_only": False}}
    )
    fetched = yahoo.fetch(req)
    assert client.calls == [
        (
            "yfinance_get_earnings_dates",
            {
                "ticker": "RELIANCE.NS",
                "response_format": "json",
                "limit": 6,
                "future_only": False,
            },
        )
    ]
    batch = yahoo_normalizer().normalize(req, fetched)
    assert len(batch.normalized_events) == 2
    assert all(item.event_time is not None for item in batch.normalized_events)
    past, future = sorted(
        batch.normalized_events, key=lambda item: item.event_time or AS_OF
    )
    assert past.event_type.value == "RESULTS_REPORTED"
    assert past.status.value == "COMPLETED"
    assert future.status.value == "ANNOUNCED"
    facts = {item.field_id: item.value for item in past.structured_facts}
    assert facts == {
        "earnings.date": "2026-06-30",
        "earnings.eps_estimate": 10.0,
        "earnings.eps_reported": 11.0,
        "earnings.surprise_percent": 10.0,
    }
    assert all("probability" not in item.field_id for item in past.structured_facts)


def test_next_earnings_date_remains_usable_when_history_is_empty() -> None:
    yahoo, _ = provider(
        fastmcp_response(
            {
                "ticker": "RELIANCE.NS",
                "next_earnings_date": "2026-09-30",
                "earnings_history": [],
            }
        )
    )
    req = request(MarketIntelligenceCapability.READ_EARNINGS_CALENDAR)
    fetched = yahoo.fetch(req)
    batch = yahoo_normalizer().normalize(req, fetched)
    assert fetched.status is ProviderResultStatus.SUCCESS
    assert len(batch.normalized_events) == 1
    assert batch.normalized_events[0].event_time is not None
    assert batch.normalized_events[0].event_time.isoformat().startswith("2026-09-30T")
    assert {item.field_id for item in batch.normalized_events[0].structured_facts} == {
        "earnings.date"
    }


def test_news_becomes_secondary_event_without_invented_sentiment() -> None:
    yahoo, _ = provider(
        fastmcp_response(
            {
                "ticker": "RELIANCE.NS",
                "news": [
                    {
                        "title": "Reliance announces project update",
                        "description": "A factual project update.",
                        "publisher": "Example News",
                        "link": "https://example.test/reliance-update",
                        "published": "2026-09-09T04:30:00Z",
                        "type": "STORY",
                    }
                ],
            }
        )
    )
    req = request(MarketIntelligenceCapability.READ_NEWS)
    fetched = yahoo.fetch(req)
    batch = yahoo_normalizer().normalize(req, fetched)
    assert len(batch.normalized_events) == 1
    event = batch.normalized_events[0]
    assert event.source.provider_id == "yahoo"
    assert event.source.publisher == "Example News"
    assert event.source.source_reference == "https://example.test/reliance-update"
    assert event.publication_time.isoformat() == "2026-09-09T10:00:00+05:30"
    assert event.metadata["sentiment_available"] is False
    assert all("sentiment" not in item.field_id for item in event.structured_facts)
    assert event.underlying_event_key is not None


@pytest.mark.parametrize(
    "payload",
    (
        {"error": "No recommendations found for RELIANCE.NS"},
        {"ticker": "RELIANCE.NS", "recommendations": []},
    ),
)
def test_empty_recommendations_are_valid_empty_evidence_not_failure(
    payload: Mapping[str, object],
) -> None:
    yahoo, _ = provider({"structuredContent": payload})
    fetched = yahoo.fetch(request(MarketIntelligenceCapability.READ_ANALYST_FORECASTS))
    assert fetched.status is ProviderResultStatus.PARTIAL
    assert fetched.observations == ()
    assert fetched.failures == ()


def test_zero_native_value_survives_while_non_finite_value_is_a_gap() -> None:
    yahoo, _ = provider(
        {
            "structuredContent": {
                "ticker": "RELIANCE.NS",
                "currency": "INR",
                "current_price": 0.0,
                "market_cap": nan,
            }
        }
    )
    fetched = yahoo.fetch(request(MarketIntelligenceCapability.READ_COMPANY_PROFILE))
    prices = [item for item in fetched.observations if item.native_field == "current_price"]
    assert len(prices) == 1
    assert prices[0].value == 0.0
    assert prices[0].currency == "INR"
    assert all(item.native_field != "market_cap" for item in fetched.observations)
    assert fetched.status is ProviderResultStatus.SUCCESS
    assert fetched.failures == ()


@pytest.mark.parametrize(
    ("capability", "payload"),
    (
        (
            MarketIntelligenceCapability.READ_FINANCIALS,
            {
                "ticker": "RELIANCE.NS",
                "statement_type": "Income Statement",
                "period_type": "annual",
                "data": {},
            },
        ),
        (
            MarketIntelligenceCapability.READ_NEWS,
            {"ticker": "RELIANCE.NS", "news": []},
        ),
        (
            MarketIntelligenceCapability.READ_EARNINGS_CALENDAR,
            {"ticker": "RELIANCE.NS", "earnings_history": []},
        ),
    ),
)
def test_valid_empty_collections_are_partial_not_false_out_of_coverage(
    capability: MarketIntelligenceCapability,
    payload: Mapping[str, object],
) -> None:
    yahoo, _ = provider(fastmcp_response(payload))
    fetched = yahoo.fetch(request(capability))
    assert fetched.status is ProviderResultStatus.PARTIAL
    assert fetched.observations == ()
    assert fetched.failures == ()


def test_native_profile_without_canonical_projection_is_not_out_of_coverage() -> None:
    yahoo, _ = provider(fastmcp_response({"ticker": "RELIANCE.NS"}))
    req = request(MarketIntelligenceCapability.READ_COMPANY_PROFILE)
    fetched = yahoo.fetch(req)
    batch = yahoo_normalizer().normalize(req, fetched)
    assert fetched.status is ProviderResultStatus.SUCCESS
    assert fetched.observations
    assert batch.canonical_evidence == ()


@pytest.mark.parametrize(
    ("capability", "message"),
    (
        (
            MarketIntelligenceCapability.READ_FINANCIALS,
            "No income statement data found for RELIANCE.NS",
        ),
        (
            MarketIntelligenceCapability.READ_NEWS,
            "No news found for RELIANCE.NS",
        ),
        (
            MarketIntelligenceCapability.READ_EARNINGS_CALENDAR,
            "No earnings dates found for RELIANCE.NS",
        ),
    ),
)
def test_explicit_provider_empty_messages_are_partial_not_coverage_failures(
    capability: MarketIntelligenceCapability,
    message: str,
) -> None:
    yahoo, _ = provider(fastmcp_response({"error": message}))
    fetched = yahoo.fetch(request(capability))
    assert fetched.status is ProviderResultStatus.PARTIAL
    assert fetched.observations == ()
    assert fetched.failures == ()


def test_yahoo_provider_error_is_typed_without_fabricated_evidence() -> None:
    yahoo, _ = provider(
        {"isError": False, "structuredContent": {"error": "Yahoo rate limit reached"}}
    )
    fetched = yahoo.fetch(request())
    assert fetched.status is ProviderResultStatus.RATE_LIMITED
    assert fetched.observations == ()
    assert fetched.failures[0].kind is ProviderFailureKind.RATE_LIMIT
    assert fetched.failures[0].retryable


def test_yahoo_transport_failure_is_typed_and_provider_error_redacts_secrets() -> None:
    class BrokenClient:
        def call_tool(
            self, tool_name: str, arguments: Mapping[str, JsonValue]
        ) -> Mapping[str, object]:
            raise RuntimeError("transport internals")

    unavailable = YahooMarketIntelligenceProvider(
        BrokenClient(), wall_clock=lambda: AS_OF
    ).fetch(request())
    assert unavailable.status is ProviderResultStatus.UNAVAILABLE
    assert unavailable.failures[0].kind is ProviderFailureKind.PROVIDER_UNAVAILABLE
    assert unavailable.observations == ()

    secret = "must-not-leak"
    yahoo, _ = provider(
        {
            "structuredContent": {
                "error": f"Failed to fetch profile; API_KEY={secret}"
            }
        }
    )
    failed = yahoo.fetch(request())
    assert secret not in failed.model_dump_json()
    assert "[REDACTED]" in failed.failures[0].message


def test_normalized_yahoo_batch_round_trips_offline_with_stable_json() -> None:
    yahoo, _ = provider(
        {
            "structuredContent": {
                "ticker": "RELIANCE.NS",
                "name": "Reliance Industries Limited",
            }
        }
    )
    req = request(MarketIntelligenceCapability.READ_COMPANY_PROFILE)
    batch = yahoo_normalizer().normalize(req, yahoo.fetch(req))
    dumped = batch.model_dump_json()
    assert NormalizedEvidenceBatch.model_validate_json(dumped).model_dump_json() == dumped


def test_explicit_route_configuration_keeps_yahoo_secondary_and_earnings_primary() -> None:
    fallback = yahoo_secondary_route_policy(MarketIntelligenceCapability.READ_FINANCIALS)
    assert fallback.provider_ids == ("tapetide", "yahoo")
    assert fallback.mode is RoutingMode.PRIMARY_WITH_FALLBACK
    earnings = yahoo_secondary_route_policy(
        MarketIntelligenceCapability.READ_EARNINGS_CALENDAR
    )
    assert earnings.provider_ids == ("yahoo",)
    assert earnings.mode is RoutingMode.FIRST_SUCCESS
