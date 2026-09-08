"""A3.4 bounded provider, READ_FUNDAMENTALS gateway, and cache tests."""

from datetime import timedelta

from tiaf.agents import (
    AgentCapability,
    EvidenceGatewayPolicy,
    EvidenceGatewayRegistry,
    EvidenceGatewayRuntime,
    EvidenceGatewayStatus,
    GatewayCacheStatus,
)
from tiaf.contracts import DataQuality, FreshnessState
from tiaf.fundamentals import (
    FundamentalEvidenceGateway,
    FundamentalFamily,
    FundamentalMetric,
    InMemoryFundamentalProvider,
    PeriodRequirement,
    ReportingPeriodKind,
)

from ._support import NOW, facts, fundamental_request, gateway_request


def runtime(
    provider: InMemoryFundamentalProvider,
) -> EvidenceGatewayRuntime:
    return EvidenceGatewayRuntime(
        EvidenceGatewayRegistry((FundamentalEvidenceGateway(provider),)),
        EvidenceGatewayPolicy(
            enabled_capabilities=(AgentCapability.READ_FUNDAMENTALS,)
        ),
        wall_clock=lambda: NOW,
        elapsed_clock=lambda: 0.0,
    )


def test_in_memory_adapter_filters_families_and_exact_history_depth() -> None:
    provider = InMemoryFundamentalProvider(facts())
    request = fundamental_request().model_copy(
        update={"families": (FundamentalFamily.INCOME,)}
    )
    dataset = provider.fetch(request)

    assert dataset.facts
    assert {item.family for item in dataset.facts} == {FundamentalFamily.INCOME}
    assert all(item.published_at <= request.as_of for item in dataset.facts)
    assert dataset.provider_id == "tiaf.in-memory-fundamentals"


def test_gateway_preserves_normalized_fact_provenance_and_a2_identity() -> None:
    request = gateway_request()
    run = runtime(InMemoryFundamentalProvider(facts())).fetch(request)

    assert run.result.status is EvidenceGatewayStatus.SUCCESS
    assert run.result.usage.tool_calls == 1
    assert run.result.evidence_pack is not None
    pack = run.result.evidence_pack
    assert pack.deterministic_assessment_id == "a2-assessment"
    assert pack.evidence_fingerprint == run.result.evidence_fingerprint
    assert pack.metadata["provider_id"] == "tiaf.in-memory-fundamentals"
    assert all(reference.facts for reference in pack.references)
    assert all(reference.source_reference is not None for reference in pack.references)
    assert all(
        (reference.source_reference or "").startswith("fixture://")
        for reference in pack.references
    )
    assert all(
        any(parameter.name == "period_id" for parameter in reference.facts[0].parameters)
        for reference in pack.references
    )


def test_gateway_cache_reuses_same_semantic_company_period_source_and_asof() -> None:
    request = gateway_request()
    evidence_runtime = runtime(InMemoryFundamentalProvider(facts()))

    first = evidence_runtime.fetch(request)
    second = evidence_runtime.fetch(request)

    assert first.result.cache_status is GatewayCacheStatus.MISS
    assert second.result.cache_status is GatewayCacheStatus.HIT
    assert second.result.usage.tool_calls == 0
    assert second.result.evidence_fingerprint == first.result.evidence_fingerprint


def test_gateway_reports_partial_missing_family_without_fabrication() -> None:
    limited = tuple(
        item for item in facts() if item.family is FundamentalFamily.INCOME
    )
    run = runtime(InMemoryFundamentalProvider(limited)).fetch(gateway_request())

    assert run.result.status is EvidenceGatewayStatus.PARTIAL
    assert run.result.evidence_pack is not None
    assert run.result.evidence_pack.missing_evidence
    assert any("Missing families" in warning for warning in run.result.warnings)


def test_provider_marks_underfilled_annual_and_missing_quarter_history() -> None:
    provider = InMemoryFundamentalProvider(facts())
    request = fundamental_request().model_copy(
        update={
            "periods": (
                PeriodRequirement(kind=ReportingPeriodKind.FISCAL_YEAR, count=3),
                PeriodRequirement(kind=ReportingPeriodKind.FISCAL_QUARTER, count=4),
            )
        }
    )
    dataset = provider.fetch(request)

    assert dataset.missing_periods == request.periods


def test_gateway_excludes_facts_published_after_decision_time() -> None:
    future = facts()[0].model_copy(
        update={
            "fact_id": "future-publication",
            "published_at": NOW + timedelta(days=1),
            "acquired_at": NOW + timedelta(days=2),
        }
    )
    provider = InMemoryFundamentalProvider((future,))
    run = runtime(provider).fetch(gateway_request())

    assert run.result.status is EvidenceGatewayStatus.MISSING
    assert run.result.evidence_pack is None


def test_gateway_does_not_upgrade_stale_or_partial_provider_facts() -> None:
    stale = facts(quality=DataQuality.PARTIAL, freshness=FreshnessState.STALE)
    run = runtime(InMemoryFundamentalProvider(stale)).fetch(gateway_request())

    assert run.result.status is EvidenceGatewayStatus.STALE
    assert run.result.quality is DataQuality.PARTIAL
    assert run.result.freshness is FreshnessState.STALE


def test_gateway_request_vocabulary_has_no_transport_escape_hatch() -> None:
    request = gateway_request()
    assert request.capability is AgentCapability.READ_FUNDAMENTALS
    assert all(
        item.startswith(("family:", "period:"))
        for item in request.requested_attributes
    )
    assert not set(type(request).model_fields) & {
        "url",
        "uri",
        "query",
        "sql",
        "headers",
        "credentials",
    }


def test_source_conflict_survives_gateway_projection() -> None:
    first = next(
        item for item in facts() if item.metric is FundamentalMetric.ROE
    )
    alternate = first.model_copy(
        update={
            "fact_id": "fact:roe:alternate",
            "value": 31.0,
            "source_provider": "fixture.exchange.alternate",
            "source_reference": "fixture://alternate/roe",
        }
    )
    provider = InMemoryFundamentalProvider((*facts(), alternate))
    run = runtime(provider).fetch(gateway_request())

    assert run.result.evidence_pack is not None
    values = {
        reference.facts[0].value
        for reference in run.result.evidence_pack.references
        if reference.facts[0].metric_id == FundamentalMetric.ROE.value
    }
    assert values == {22.0, 31.0}
