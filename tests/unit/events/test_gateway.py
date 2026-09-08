"""Controlled A3.5 READ_NEWS/READ_FILINGS gateway and cache tests."""

from tiaf.agents import (
    AgentCapability,
    EvidenceGatewayPolicy,
    EvidenceGatewayRegistry,
    EvidenceGatewayRuntime,
    EvidenceGatewayStatus,
    GatewayCacheStatus,
)
from tiaf.events import EventEvidenceGateway, EventSourceClass, InMemoryEventProvider

from ._support import NOW, event, gateway_request


def runtime(provider: InMemoryEventProvider) -> EvidenceGatewayRuntime:
    return EvidenceGatewayRuntime(
        EvidenceGatewayRegistry((EventEvidenceGateway(provider),)),
        EvidenceGatewayPolicy(
            enabled_capabilities=(
                AgentCapability.READ_FILINGS,
                AgentCapability.READ_NEWS,
            )
        ),
        wall_clock=lambda: NOW,
        elapsed_clock=lambda: 0.0,
    )


def test_read_news_preserves_event_times_clusters_source_and_a2_identity() -> None:
    run = runtime(InMemoryEventProvider((event(),))).fetch(gateway_request())
    assert run.result.status is EvidenceGatewayStatus.SUCCESS
    assert run.result.evidence_pack is not None
    pack = run.result.evidence_pack
    assert pack.deterministic_assessment_id == "a2-assessment"
    assert pack.evidence_fingerprint == run.result.evidence_fingerprint
    reference = pack.references[0]
    assert reference.metadata["cluster_id"]
    assert reference.metadata["active"] is True
    assert reference.observed_at is not None
    assert reference.acquired_at is not None
    assert {item.metric_id for item in reference.facts} >= {
        "event.family",
        "event.type",
        "event.publication_time",
        "event.acquisition_time",
    }


def test_read_filings_accepts_primary_filing_records() -> None:
    request = gateway_request(capability=AgentCapability.READ_FILINGS)
    run = runtime(InMemoryEventProvider((event(),))).fetch(request)
    assert run.result.status is EvidenceGatewayStatus.SUCCESS


def test_read_filings_rejects_non_filing_source_constraint_before_provider() -> None:
    request = gateway_request(
        capability=AgentCapability.READ_FILINGS,
        sources=(EventSourceClass.TRUSTED_NEWS,),
    )
    run = runtime(InMemoryEventProvider((event(),))).fetch(request)
    assert run.result.status is EvidenceGatewayStatus.INVALID_REQUEST
    assert run.result.failure is not None
    assert "only filing" in run.result.failure.detail


def test_gateway_cache_keys_semantic_window_filters_source_and_versions() -> None:
    evidence_runtime = runtime(InMemoryEventProvider((event(),)))
    first = evidence_runtime.fetch(gateway_request())
    second = evidence_runtime.fetch(gateway_request())
    assert first.result.cache_status is GatewayCacheStatus.MISS
    assert second.result.cache_status is GatewayCacheStatus.HIT
    assert second.result.usage.tool_calls == 0


def test_gateway_request_has_no_transport_escape_hatch() -> None:
    request = gateway_request()
    assert not set(type(request).model_fields) & {
        "url",
        "uri",
        "query",
        "sql",
        "headers",
        "credentials",
    }
    assert all(
        item.startswith(("family:", "source:", "relevance:", "max:", "normalization:", "dedupe:"))
        for item in request.requested_attributes
    )


def test_gateway_reports_bounded_truncation_as_partial_coverage() -> None:
    records = tuple(
        event(
            event_id=f"event:bounded:{index}",
            source_suffix=f"bounded:{index}",
            underlying_key=f"bounded:{index}",
        )
        for index in range(51)
    )
    run = runtime(InMemoryEventProvider(records)).fetch(gateway_request())
    assert run.result.status is EvidenceGatewayStatus.PARTIAL
    assert run.result.evidence_pack is not None
    assert run.result.evidence_pack.evidence_coverage == 50 / 51
    assert any("limited to 50 of 51" in warning for warning in run.result.warnings)


def test_unknown_subject_and_empty_pit_window_are_typed_missing() -> None:
    provider = InMemoryEventProvider((event(),))
    unknown = gateway_request().model_copy(update={"subject": "UNKNOWN"})
    assert runtime(provider).fetch(unknown).result.status is EvidenceGatewayStatus.MISSING
    empty_provider = InMemoryEventProvider(())
    assert (
        runtime(empty_provider).fetch(gateway_request()).result.status
        is EvidenceGatewayStatus.MISSING
    )
