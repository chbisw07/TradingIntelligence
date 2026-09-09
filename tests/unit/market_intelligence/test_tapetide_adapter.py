from collections.abc import Mapping
from datetime import datetime

from pydantic import JsonValue

from tiaf.market_intelligence import (
    AvailabilityBasis,
    CapabilitySupport,
    EvidenceOutputType,
    MarketIntelligenceCapability,
    PointInTimeQuality,
    ProviderFailureKind,
    ProviderResultStatus,
    SemanticMappingQuality,
    tapetide_normalizer,
)
from tiaf.market_intelligence.providers import TapetideMarketIntelligenceProvider

from ._support import request

RATE_LIMIT_TEXT = """Tapetide rate limit reached
Request denied. Retry in 17819s.
You've reached the Tapetide free tier limit for today.
Your quota resets in about 5 hours at 2026-09-10 00:00:00 IST.
Free plan (50 MCP tool calls/day).
"""


class FakeTapetideClient:
    def __init__(self, response: Mapping[str, object] | None = None) -> None:
        self.response = response or {
            "structuredContent": {
                "source_url": "https://example.test/filing",
                "published_at": "2025-05-01",
                "data": {"FY2025": {"Revenue from Operations": 100, "Sales": 101}},
            }
        }
        self.calls: list[tuple[str, dict[str, JsonValue]]] = []

    def call_tool(self, tool_name: str, arguments: Mapping[str, JsonValue]) -> Mapping[str, object]:
        self.calls.append((tool_name, dict(arguments)))
        return self.response


def test_tapetide_financials_uses_validated_read_tool_and_preserves_native_labels() -> None:
    client = FakeTapetideClient()
    provider = TapetideMarketIntelligenceProvider(client)
    fetched = provider.fetch(request())
    assert client.calls == [("get_financials", {"symbol": "RELIANCE", "section": "profit_loss"})]
    assert fetched.status is ProviderResultStatus.SUCCESS
    assert {item.native_field for item in fetched.observations} == {
        "Revenue from Operations",
        "Sales",
    }


def test_tapetide_date_only_availability_is_conservative_kolkata_end_of_day() -> None:
    provider = TapetideMarketIntelligenceProvider(FakeTapetideClient())
    item = provider.fetch(request()).observations[0]
    assert item.available_from == datetime.fromisoformat("2025-05-01T23:59:59.999999+05:30")
    assert item.availability_basis is AvailabilityBasis.ESTIMATED_DATE
    assert item.point_in_time_quality is PointInTimeQuality.CONSERVATIVE


def test_live_financial_shape_preserves_metric_period_and_provider_record_reference() -> None:
    client = FakeTapetideClient(
        {
            "structuredContent": {
                "data": [
                    {
                        "id": 42,
                        "availability": [
                            {
                                "period": "Mar 2025",
                                "available_from": "2025-04-22",
                                "basis": "provider",
                            }
                        ],
                        "data": {
                            "Sales": {"Mar 2025": 100},
                            "Net Profit": {"Mar 2025": 10},
                        },
                        "pct_changes": {"Sales": {"Mar 2025": 5}},
                    }
                ]
            }
        }
    )
    req = request()
    fetched = TapetideMarketIntelligenceProvider(client).fetch(req)
    observations = {item.native_field: item for item in fetched.observations}
    assert {"Sales", "Net Profit", "Sales pct_change"} <= observations.keys()
    assert observations["Sales"].period_label == "Mar 2025"
    assert observations["Sales"].source_reference == "tapetide:get_financials:42"
    assert observations["Sales"].available_from == datetime.fromisoformat(
        "2025-04-22T23:59:59.999999+05:30"
    )
    assert all(
        "availability" not in str(item.metadata["native_path"])
        for item in observations.values()
    )

    normalized = tapetide_normalizer().normalize(req, fetched)
    by_field = {item.native_field: item for item in normalized.normalization_records}
    assert by_field["Sales"].mapping_quality is SemanticMappingQuality.PROVIDER_DEFINED
    assert by_field["Sales"].emitted_evidence_id is None
    assert by_field["Net Profit"].mapping_quality is SemanticMappingQuality.WELL_SUPPORTED
    assert by_field["Net Profit"].emitted_evidence_id is not None
    assert by_field["Sales pct_change"].derivation_class.value == "PROVIDER_DERIVED"


def test_tapetide_manifest_explicitly_declares_every_capability() -> None:
    provider = TapetideMarketIntelligenceProvider(FakeTapetideClient())
    assert {item.capability for item in provider.manifest.capabilities} == set(
        MarketIntelligenceCapability
    )
    unsupported = provider.manifest.declaration_for(
        MarketIntelligenceCapability.READ_CUSTOMER_EXPOSURE
    )
    assert unsupported is not None
    assert unsupported.support is CapabilitySupport.UNSUPPORTED


def test_unsupported_capability_never_reaches_transport() -> None:
    client = FakeTapetideClient()
    provider = TapetideMarketIntelligenceProvider(client)
    fetched = provider.fetch(request(MarketIntelligenceCapability.READ_CUSTOMER_EXPOSURE))
    assert client.calls == []
    assert fetched.status is ProviderResultStatus.UNSUPPORTED
    assert fetched.failures[0].kind is ProviderFailureKind.UNSUPPORTED_CAPABILITY


def test_news_arguments_are_bounded_and_tool_name_cannot_be_injected() -> None:
    client = FakeTapetideClient()
    provider = TapetideMarketIntelligenceProvider(client)
    req = request(MarketIntelligenceCapability.READ_NEWS).model_copy(
        update={"attributes": {"limit": 5, "tool_name": "write_order"}}
    )
    provider.fetch(req)
    assert client.calls[0] == (
        "get_stock_events",
        {"symbol": "RELIANCE", "type": "news", "limit": 5},
    )


def test_index_membership_uses_live_advertised_date_argument() -> None:
    client = FakeTapetideClient()
    provider = TapetideMarketIntelligenceProvider(client)
    provider.fetch(request(MarketIntelligenceCapability.READ_INDEX_MEMBERSHIP_ASOF))
    assert client.calls[0] == (
        "get_index_membership_asof",
        {"symbol": "RELIANCE", "date": "2026-09-09"},
    )


def test_malformed_payload_becomes_typed_failure() -> None:
    client = FakeTapetideClient({"content": [{"text": "not-json"}]})
    fetched = TapetideMarketIntelligenceProvider(client).fetch(request())
    assert fetched.status is ProviderResultStatus.INVALID_OUTPUT
    assert fetched.failures[0].kind is ProviderFailureKind.MALFORMED_PAYLOAD


def test_transport_timeout_becomes_retryable_typed_failure() -> None:
    class TimeoutClient:
        def call_tool(
            self, tool_name: str, arguments: Mapping[str, JsonValue]
        ) -> Mapping[str, object]:
            raise TimeoutError

    fetched = TapetideMarketIntelligenceProvider(TimeoutClient()).fetch(request())
    assert fetched.status is ProviderResultStatus.TIMEOUT
    assert fetched.failures[0].kind is ProviderFailureKind.TIMEOUT
    assert fetched.failures[0].retryable


def test_provider_error_payload_is_not_misrepresented_as_evidence() -> None:
    client = FakeTapetideClient(
        {
            "isError": True,
            "structuredContent": {"code": "404", "message": "Unknown symbol"},
        }
    )
    fetched = TapetideMarketIntelligenceProvider(client).fetch(request())
    assert fetched.observations == ()
    assert fetched.status is ProviderResultStatus.OUT_OF_COVERAGE
    assert fetched.failures[0].kind is ProviderFailureKind.UNKNOWN_SYMBOL


def test_rate_limit_payload_is_a_retryable_typed_failure() -> None:
    client = FakeTapetideClient(
        {"isError": True, "structuredContent": {"code": "429", "error": "rate limit"}}
    )
    fetched = TapetideMarketIntelligenceProvider(client).fetch(request())
    assert fetched.status is ProviderResultStatus.RATE_LIMITED
    assert fetched.failures[0].kind is ProviderFailureKind.RATE_LIMIT
    assert fetched.failures[0].retryable


def test_transport_success_with_rate_limit_text_is_not_evidence() -> None:
    client = FakeTapetideClient(
        {
            "isError": False,
            "content": [{"type": "text", "text": RATE_LIMIT_TEXT}],
        }
    )
    req = request()
    fetched = TapetideMarketIntelligenceProvider(client).fetch(req)

    assert fetched.status is ProviderResultStatus.RATE_LIMITED
    assert fetched.observations == ()
    assert len(fetched.failures) == 1
    failure = fetched.failures[0]
    assert failure.kind is ProviderFailureKind.RATE_LIMIT
    assert failure.retryable
    assert failure.metadata["retry_after_seconds"] == 17819
    assert failure.metadata["reset_at"] == "2026-09-10T00:00:00+05:30"
    assert str(failure.metadata["acquired_at"]).endswith("+05:30")
    assert "Tapetide rate limit reached" in failure.message

def test_rate_limit_without_retry_metadata_remains_typed() -> None:
    client = FakeTapetideClient(
        {
            "isError": False,
            "content": [
                {
                    "type": "text",
                    "text": "Tapetide rate limit reached. Request denied.",
                }
            ],
        }
    )
    fetched = TapetideMarketIntelligenceProvider(client).fetch(request())

    assert fetched.status is ProviderResultStatus.RATE_LIMITED
    assert fetched.failures[0].kind is ProviderFailureKind.RATE_LIMIT
    assert "retry_after_seconds" not in fetched.failures[0].metadata
    assert "reset_at" not in fetched.failures[0].metadata


def test_normal_success_json_text_is_not_misclassified() -> None:
    client = FakeTapetideClient(
        {
            "isError": False,
            "content": [
                {
                    "type": "text",
                    "text": (
                        '{"published_at":"2025-05-01",'
                        '"data":{"FY2025":{"Net Profit":10}}}'
                    ),
                }
            ],
        }
    )
    fetched = TapetideMarketIntelligenceProvider(client).fetch(request())

    assert fetched.status is ProviderResultStatus.SUCCESS
    assert fetched.observations
    assert fetched.failures == ()


def test_unrecognized_explicit_provider_error_is_typed_unknown() -> None:
    client = FakeTapetideClient(
        {
            "isError": False,
            "content": [
                {
                    "type": "text",
                    "text": "Provider error: upstream rejected this unusual operation.",
                }
            ],
        }
    )
    fetched = TapetideMarketIntelligenceProvider(client).fetch(request())

    assert fetched.status is ProviderResultStatus.UNAVAILABLE
    assert fetched.observations == ()
    assert fetched.failures[0].kind is ProviderFailureKind.UNKNOWN


def test_provider_failure_serialization_redacts_credential_shaped_text() -> None:
    secret = "secret-value-that-must-not-leak"
    client = FakeTapetideClient(
        {
            "isError": False,
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Tapetide rate limit reached; TAPETIDE_TOKEN={secret}; "
                        f"Authorization: Bearer {secret}"
                    ),
                }
            ],
        }
    )
    fetched = TapetideMarketIntelligenceProvider(client).fetch(request())

    serialized = fetched.model_dump_json()
    assert fetched.status is ProviderResultStatus.RATE_LIMITED
    assert secret not in serialized
    assert serialized.count("[REDACTED]") == 2


def test_stale_response_preserves_observations_and_reports_typed_gap() -> None:
    client = FakeTapetideClient(
        {
            "structuredContent": {
                "source_url": "https://example.test/filing",
                "published_at": "2025-05-01",
                "stale": True,
                "data": {"FY2025": {"Revenue from Operations": 100}},
            }
        }
    )
    fetched = TapetideMarketIntelligenceProvider(client).fetch(request())
    assert fetched.status is ProviderResultStatus.PARTIAL
    assert fetched.observations
    assert fetched.failures[0].kind is ProviderFailureKind.STALE


def test_null_native_value_remains_an_explicit_unavailable_gap() -> None:
    client = FakeTapetideClient(
        {
            "structuredContent": {
                "source_url": "https://example.test/filing",
                "published_at": "2025-05-01",
                "data": {"FY2025": {"Sales": None, "Net Profit": 10}},
            }
        }
    )
    fetched = TapetideMarketIntelligenceProvider(client).fetch(request())
    assert fetched.status is ProviderResultStatus.PARTIAL
    assert {item.native_field for item in fetched.observations} == {"Net Profit"}
    assert any(
        item.kind is ProviderFailureKind.OUT_OF_COVERAGE
        and item.metadata["native_path"] == "data.FY2025.Sales"
        for item in fetched.failures
    )


def test_multi_event_payload_preserves_each_record_identity_reference_and_date() -> None:
    client = FakeTapetideClient(
        {
            "structuredContent": {
                "data": [
                    {
                        "id": "event-1",
                        "date": "2026-08-01",
                        "url": "https://example.test/event-1",
                        "title": "First filing",
                    },
                    {
                        "id": "event-2",
                        "date": "2026-08-02",
                        "url": "https://example.test/event-2",
                        "title": "Second filing",
                    },
                ]
            }
        }
    )
    fetched = TapetideMarketIntelligenceProvider(client).fetch(
        request(MarketIntelligenceCapability.READ_FILINGS)
    )
    titles = {
        item.value: item
        for item in fetched.observations
        if item.native_field == "title"
    }
    assert titles["First filing"].native_record_id == "event-1"
    assert titles["First filing"].source_reference == "https://example.test/event-1"
    assert titles["First filing"].available_from == datetime.fromisoformat(
        "2026-08-01T23:59:59.999999+05:30"
    )
    assert titles["Second filing"].native_record_id == "event-2"
    assert titles["Second filing"].source_reference == "https://example.test/event-2"
    assert titles["Second filing"].available_from == datetime.fromisoformat(
        "2026-08-02T23:59:59.999999+05:30"
    )


def test_interpreted_tapetide_summary_is_not_declared_primary_evidence() -> None:
    provider = TapetideMarketIntelligenceProvider(FakeTapetideClient())
    declaration = provider.manifest.declaration_for(
        MarketIntelligenceCapability.READ_EARNINGS_CALL_CONTEXT
    )
    assert declaration is not None and declaration.constraints is not None
    assert declaration.constraints.output_types == (EvidenceOutputType.INTERPRETED_AI,)
