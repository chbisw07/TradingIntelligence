from collections.abc import Callable
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from tiaf.agents import AgentBudget, AgentCapability
from tiaf.contracts import DataQuality, FreshnessState, Horizon
from tiaf.events import (
    EntityKind,
    EntityMappingStatus,
    EventCluster,
    EventEntity,
    EventFamily,
    EventMateriality,
    EventNovelty,
    EventRelevance,
    EventSource,
    EventSourceClass,
    EventStatus,
    EventType,
    NormalizedEvent,
    StructuredEventFact,
    StructuredFactKind,
)
from tiaf.market_intelligence import (
    AuthoritativeConfirmationGateway,
    AuthoritativeConfirmationRequest,
    AuthoritativeConfirmationResult,
    AuthoritativeDocumentKind,
    AuthoritativeEscalationPolicy,
    CapabilityRoutePolicy,
    ConfirmationStatus,
    DiscoveredClaim,
    DocumentContentCache,
    DocumentExtractionRule,
    DocumentParseStatus,
    MarketIntelligenceCapability,
    MarketIntelligenceRegistry,
    MarketIntelligenceRouter,
    MaterialityTrigger,
    OfficialSourceKind,
    OfficialSourceRegistration,
    ProviderFailureKind,
    RoutingMode,
    SourceAuthority,
    SourceValidationError,
    authoritative_event_graph_edge,
    merge_authoritative_event,
)
from tiaf.market_intelligence.providers import (
    AuthoritativeDocumentNormalizer,
    BseOfficialSourceProvider,
    CompanyIrOfficialSourceProvider,
    NseOfficialSourceProvider,
    OfficialDocumentLocator,
    OfficialDocumentResponse,
    OfficialDocumentTransportError,
    default_official_source_registry,
)

IST = ZoneInfo("Asia/Kolkata")
AS_OF = datetime(2026, 9, 10, 12, tzinfo=IST)
PUBLISHED = datetime(2026, 8, 29, 18, tzinfo=IST)


class FakeTransport:
    def __init__(
        self,
        content: bytes,
        *,
        mime_type: str = "text/html",
        final_url: str = "https://www.ril.com/results/q1.html",
        failure: ProviderFailureKind | None = None,
    ) -> None:
        self.content = content
        self.mime_type = mime_type
        self.final_url = final_url
        self.failure = failure
        self.calls = 0

    def fetch(
        self,
        url: str,
        *,
        validate_url: Callable[[str], None],
        max_bytes: int,
        timeout_seconds: float,
    ) -> OfficialDocumentResponse:
        assert max_bytes > 0
        assert timeout_seconds > 0
        self.calls += 1
        validate_url(url)
        validate_url(self.final_url)
        if self.failure is not None:
            raise OfficialDocumentTransportError("bounded failure", kind=self.failure)
        return OfficialDocumentResponse(
            requested_url=url,
            final_url=self.final_url,
            status_code=200,
            mime_type=self.mime_type,
            content=self.content,
            acquired_at=AS_OF,
        )


def ir_registration() -> OfficialSourceRegistration:
    return OfficialSourceRegistration(
        source_id="reliance_ir",
        provider_id="reliance_ir",
        display_name="Reliance Industries Investor Relations",
        kind=OfficialSourceKind.COMPANY_IR,
        authority=SourceAuthority.AUTHORITATIVE,
        official_domains=("ril.com",),
    )


def exact_rule(
    field_id: str = "revenue_from_operations",
    label: str = "Revenue from Operations",
) -> DocumentExtractionRule:
    return DocumentExtractionRule(
        field_id=f"rule:{field_id}",
        source_label=label,
        canonical_metric=field_id,
        kind="NUMBER",
        unit="INR crore",
        currency="INR",
        period="Q1 FY2027",
        statement_basis="CONSOLIDATED",
    )


def locator(
    *,
    subject: str = "RELIANCE",
    document_kind: AuthoritativeDocumentKind = AuthoritativeDocumentKind.FINANCIAL_RESULT,
    rules: tuple[DocumentExtractionRule, ...] = (exact_rule(),),
    url: str = "https://www.ril.com/results/q1.html",
    revision: int = 0,
    supersedes: str | None = None,
) -> OfficialDocumentLocator:
    return OfficialDocumentLocator(
        locator_id=f"ril-q1-{revision}",
        subject=subject,
        capability=MarketIntelligenceCapability.READ_FINANCIALS,
        document_kind=document_kind,
        source_url=url,
        title="Q1 FY2027 Financial Results",
        provider_document_id=f"RIL-Q1-{revision}",
        filing_reference="RIL/SE/2026-27/42",
        published_at=PUBLISHED,
        period="Q1 FY2027",
        financial_year="FY2027",
        quarter="Q1",
        statement_basis="CONSOLIDATED",
        audited=False,
        unit="INR crore",
        currency="INR",
        extraction_rules=rules,
        event_family=EventFamily.CORPORATE_RESULTS,
        event_type=EventType.RESULTS_REPORTED,
        underlying_event_key="RELIANCE:RESULTS:Q1-FY2027",
        revision=revision,
        supersedes_document_id=supersedes,
    )


def claim(
    revenue: float = 100.0,
    *,
    include_pat: bool = False,
    materiality: EventMateriality = EventMateriality.HIGH,
) -> DiscoveredClaim:
    facts = [
        StructuredEventFact(
            field_id="revenue_from_operations",
            kind=StructuredFactKind.NUMBER,
            value=revenue,
            unit="INR crore",
            currency="INR",
        )
    ]
    if include_pat:
        facts.append(
            StructuredEventFact(
                field_id="pat",
                kind=StructuredFactKind.NUMBER,
                value=20.0,
                unit="INR crore",
                currency="INR",
            )
        )
    return DiscoveredClaim(
        claim_id="claim:reliance:q1",
        subject="RELIANCE",
        capability=MarketIntelligenceCapability.READ_FINANCIALS,
        asserted_facts=tuple(facts),
        discovery_evidence_ids=("tapetide:sales", "yahoo:total-revenue"),
        event_cluster_id="cluster:reliance:q1",
        materiality=materiality,
        published_at=PUBLISHED,
        available_from=PUBLISHED,
        created_at=AS_OF,
    )


def confirmation_request(
    discovered: DiscoveredClaim | None = None,
    *,
    kinds: tuple[AuthoritativeDocumentKind, ...] = (
        AuthoritativeDocumentKind.FINANCIAL_RESULT,
    ),
) -> AuthoritativeConfirmationRequest:
    discovered = discovered or claim()
    return AuthoritativeConfirmationRequest(
        request_id="confirm:reliance:q1",
        claim=discovered,
        as_of=AS_OF,
        horizon=Horizon(label="POSITIONAL"),
        authority=AgentCapability.READ_FUNDAMENTALS,
        allowed_authorities=(AgentCapability.READ_FUNDAMENTALS,),
        accepted_document_kinds=kinds,
        eligible_source_kinds=(OfficialSourceKind.COMPANY_IR,),
        required_fields=tuple(item.field_id for item in discovered.asserted_facts),
        materiality_triggers=(MaterialityTrigger.FINANCIAL_RESULTS,),
        budget=AgentBudget(max_tool_calls=1, max_cost_units=0, max_elapsed_seconds=30),
        route_policy_id="official-confirmation",
        route_policy_version="1.0",
    )


def execute(
    content: bytes,
    *,
    discovered: DiscoveredClaim | None = None,
    rules: tuple[DocumentExtractionRule, ...] = (exact_rule(),),
    kinds: tuple[AuthoritativeDocumentKind, ...] = (
        AuthoritativeDocumentKind.FINANCIAL_RESULT,
    ),
    located_kind: AuthoritativeDocumentKind = AuthoritativeDocumentKind.FINANCIAL_RESULT,
    transport_failure: ProviderFailureKind | None = None,
    located_subject: str = "RELIANCE",
) -> tuple[AuthoritativeConfirmationResult, FakeTransport, DocumentContentCache]:
    registry = default_official_source_registry((ir_registration(),))
    cache = DocumentContentCache()
    transport = FakeTransport(content, failure=transport_failure)
    provider = CompanyIrOfficialSourceProvider(
        "reliance_ir",
        registry,
        (locator(subject=located_subject, document_kind=located_kind, rules=rules),),
        transport,
        cache,
    )
    providers = MarketIntelligenceRegistry()
    providers.register(provider, AuthoritativeDocumentNormalizer(provider.identity.provider_id))
    route = CapabilityRoutePolicy(
        policy_id="official-confirmation",
        policy_version="1.0",
        capability=MarketIntelligenceCapability.READ_FINANCIALS,
        mode=RoutingMode.AUTHORITATIVE_CONFIRMATION,
        provider_ids=(provider.identity.provider_id,),
        authoritative_provider_ids=(provider.identity.provider_id,),
        maximum_provider_calls=1,
        required_canonical_metrics=tuple(
            item.field_id for item in (discovered or claim()).asserted_facts
        ),
        minimum_source_authority=SourceAuthority.AUTHORITATIVE,
    )
    result = AuthoritativeConfirmationGateway(MarketIntelligenceRouter(providers)).execute(
        confirmation_request(discovered, kinds=kinds),
        route,
        run_id="official-run-1",
        confirmation_id="confirmation-1",
    )
    return result, transport, cache


def test_official_source_registry_accepts_nse_bse_and_validated_company_ir() -> None:
    registry = default_official_source_registry((ir_registration(),))
    nse = registry.validate("nse_official", "https://www.nseindia.com/companies-listing")
    bse = registry.validate("bse_official", "https://api.bseindia.com/announcements")
    assert nse.source.authority is SourceAuthority.AUTHORITATIVE
    assert bse.source.kind is OfficialSourceKind.EXCHANGE_OR_REGULATOR
    ir = registry.validate("reliance_ir", "https://www.ril.com/investors/results")
    assert ir.source.kind is OfficialSourceKind.COMPANY_IR


@pytest.mark.parametrize(
    "url",
    (
        "https://nseindia.com.evil.example/filing.pdf",
        "https://evil-nseindia.com/filing.pdf",
        "http://www.nseindia.com/filing.pdf",
        "https://user:secret@www.nseindia.com/filing.pdf",
        "https://www.nseindia.com/filing.pdf?access_token=secret",
    ),
)
def test_official_source_registry_rejects_unofficial_or_unsafe_domains(url: str) -> None:
    registry = default_official_source_registry()
    with pytest.raises(SourceValidationError):
        registry.validate("nse_official", url)


def test_redirect_final_domain_is_validated() -> None:
    registry = default_official_source_registry()
    with pytest.raises(SourceValidationError) as exc:
        registry.validate(
            "nse_official",
            "https://www.nseindia.com/filing",
            final_url="https://mirror.example/filing",
        )
    assert exc.value.kind is ProviderFailureKind.INVALID_REDIRECT


def test_materiality_policy_triggers_high_value_and_skips_routine_low_value() -> None:
    policy = AuthoritativeEscalationPolicy()
    high = policy.evaluate(
        EventMateriality.HIGH,
        (MaterialityTrigger.MAJOR_ORDER_WIN,),
    )
    low = policy.evaluate(
        EventMateriality.LOW,
        (MaterialityTrigger.ROUTINE_LOW_MATERIALITY,),
    )
    assert high.should_confirm is True
    assert low.should_confirm is False


def test_content_cache_deduplicates_bytes_but_documents_keep_provenance() -> None:
    cache = DocumentContentCache()
    nse = cache.put(b"same official bytes")
    bse = cache.put(b"same official bytes")
    assert nse.content_hash == bse.content_hash
    assert len(cache) == 1
    assert cache.get(nse.content_hash) == b"same official bytes"


def test_revision_bytes_create_new_fingerprint_without_overwrite() -> None:
    cache = DocumentContentCache()
    original = cache.put(b"version one")
    revised = cache.put(b"version two corrected")
    assert original.content_hash != revised.content_hash
    assert len(cache) == 2
    assert cache.get(original.content_hash) == b"version one"


def test_parser_extracts_explicit_metric_and_never_guesses_missing_fact() -> None:
    from tiaf.market_intelligence import PlainTextHtmlDocumentParser

    parser = PlainTextHtmlDocumentParser()
    parsed = parser.parse(
        b"<html><title>Results</title><p>Revenue from Operations: 100</p></html>",
        "text/html",
        (exact_rule(), exact_rule("pat", "Profit After Tax")),
    )
    assert parsed.status is DocumentParseStatus.PARTIAL
    assert [(item.field_id, item.value) for item in parsed.facts] == [
        ("revenue_from_operations", 100.0)
    ]
    assert all(item.field_id != "pat" for item in parsed.facts)


def test_parser_failure_and_unsupported_pdf_are_typed_without_false_fact() -> None:
    from tiaf.market_intelligence import PlainTextHtmlDocumentParser

    parser = PlainTextHtmlDocumentParser()
    empty = parser.parse(b"   ", "text/plain", (exact_rule(),))
    pdf = parser.parse(b"%PDF-1.7", "application/pdf", (exact_rule(),))
    assert empty.status is DocumentParseStatus.FAILED
    assert empty.failure_kind is ProviderFailureKind.PARSE_FAILURE
    assert pdf.status is DocumentParseStatus.UNSUPPORTED
    assert pdf.failure_kind is ProviderFailureKind.UNSUPPORTED_DOCUMENT_TYPE
    assert not empty.facts and not pdf.facts


def test_exact_official_financial_metric_confirms_without_deleting_discovery() -> None:
    result, transport, _ = execute(
        b"<html><title>Results</title><p>Revenue from Operations: 100</p></html>"
    )
    assert result.status is ConfirmationStatus.CONFIRMED
    assert result.confirmed_facts[0].canonical_metric == "revenue_from_operations"
    assert result.request.claim.discovery_evidence_ids == (
        "tapetide:sales",
        "yahoo:total-revenue",
    )
    assert result.authoritative_documents[0].source.validated_domain == "www.ril.com"
    assert transport.calls == 1


def test_partial_contradicted_ambiguous_not_found_unavailable_and_out_of_coverage() -> None:
    partial, _, _ = execute(
        b"Revenue from Operations: 100",
        discovered=claim(include_pat=True),
        rules=(exact_rule(), exact_rule("pat", "Profit After Tax")),
    )
    contradicted, _, _ = execute(b"Revenue from Operations: 90")
    ambiguous, _, _ = execute(b"Official results without configured values", rules=())
    not_found, _, _ = execute(
        b"unused",
        kinds=(AuthoritativeDocumentKind.ANNUAL_REPORT,),
    )
    unavailable, _, _ = execute(
        b"unused",
        transport_failure=ProviderFailureKind.ACCESS_RESTRICTED,
    )
    out_of_coverage, _, _ = execute(b"unused", located_subject="HDFCBANK")
    assert partial.status is ConfirmationStatus.PARTIALLY_CONFIRMED
    assert contradicted.status is ConfirmationStatus.CONTRADICTED
    assert ambiguous.status is ConfirmationStatus.AMBIGUOUS
    assert not_found.status is ConfirmationStatus.NOT_FOUND
    assert unavailable.status is ConfirmationStatus.UNAVAILABLE
    assert out_of_coverage.status is ConfirmationStatus.OUT_OF_COVERAGE
    assert len({ConfirmationStatus.NOT_FOUND, ConfirmationStatus.CONTRADICTED}) == 2


def test_confirmation_json_replay_is_exact_and_contract_is_frozen() -> None:
    result, transport, _ = execute(b"Revenue from Operations: 100")
    payload = result.model_dump_json()
    replayed = AuthoritativeConfirmationResult.model_validate_json(payload)
    assert replayed == result
    assert replayed.semantic_fingerprint == result.semantic_fingerprint
    assert transport.calls == 1
    with pytest.raises(ValidationError):
        result.status = ConfirmationStatus.AMBIGUOUS


def test_document_revision_links_without_overwriting_prior_version() -> None:
    original_result, _, _ = execute(b"Revenue from Operations: 100")
    original = original_result.authoritative_documents[0]
    revised_payload = original.model_dump(mode="json")
    revised_payload.update(
        {
            "document_id": "authdoc:revised",
            "content_hash": "b" * 64,
            "content_reference": f"sha256:{'b' * 64}",
            "revision": 1,
            "supersedes_document_id": original.document_id,
        }
    )
    revised = type(original).model_validate(revised_payload)
    assert revised.supersedes_document_id == original.document_id
    assert revised.content_hash != original.content_hash
    assert original.supersedes_document_id is None


def test_nse_bse_and_company_ir_adapters_share_canonical_provider_protocol() -> None:
    registry = default_official_source_registry((ir_registration(),))
    cache = DocumentContentCache()
    transport = FakeTransport(b"Revenue from Operations: 100")
    nse = NseOfficialSourceProvider(
        registry,
        (locator(url="https://www.nseindia.com/filing.html"),),
        transport,
        cache,
    )
    bse = BseOfficialSourceProvider(
        registry,
        (locator(url="https://www.bseindia.com/filing.html"),),
        transport,
        cache,
    )
    company = CompanyIrOfficialSourceProvider(
        "reliance_ir",
        registry,
        (locator(),),
        transport,
        cache,
    )
    assert {item.identity.provider_id for item in (nse, bse, company)} == {
        "nse_official",
        "bse_official",
        "reliance_ir",
    }
    assert all(item.manifest.read_only for item in (nse, bse, company))


def base_event(event_id: str, source_class: EventSourceClass) -> NormalizedEvent:
    return NormalizedEvent(
        event_id=event_id,
        family=EventFamily.CORPORATE_RESULTS,
        event_type=EventType.RESULTS_REPORTED,
        primary_entity=EventEntity(
            entity_id="company:RELIANCE",
            kind=EntityKind.COMPANY,
            name="RELIANCE",
            canonical_symbol="RELIANCE",
            mapping_status=EntityMappingStatus.EXACT,
        ),
        source=EventSource(
            source_id=f"source:{event_id}",
            source_class=source_class,
            publisher="Publisher",
            provider_id="provider",
            source_reference=f"https://example.com/{event_id}",
        ),
        publication_time=PUBLISHED,
        acquisition_time=AS_OF,
        normalized_title="Q1 results",
        relevance=EventRelevance.DIRECT,
        materiality=EventMateriality.HIGH,
        novelty=EventNovelty.NEW,
        status=EventStatus.CONFIRMED,
        quality=DataQuality.GOOD,
        freshness=FreshnessState.FRESH,
        underlying_event_key="RELIANCE:RESULTS:Q1-FY2027",
    )


def test_authoritative_event_joins_one_cluster_without_economic_event_inflation() -> None:
    discovery = base_event("event:news", EventSourceClass.TRUSTED_NEWS)
    official = base_event("event:nse", EventSourceClass.EXCHANGE_FILING)
    cluster = EventCluster(
        cluster_id="cluster:results",
        subject="RELIANCE",
        family=discovery.family,
        event_type=discovery.event_type,
        event_ids=(discovery.event_id,),
        active_event_ids=(discovery.event_id,),
    )
    enriched = merge_authoritative_event(cluster, official)
    assert enriched.cluster_id == cluster.cluster_id
    assert enriched.event_ids == ("event:news", "event:nse")
    assert len((enriched,)) == 1


def test_authoritative_event_projects_to_existing_evidence_graph_contract() -> None:
    result, _, _ = execute(b"Revenue from Operations: 100")
    document = result.authoritative_documents[0]
    event = base_event("event:official", EventSourceClass.COMPANY_RELEASE)
    event = event.model_copy(
        update={
            "source": event.source.model_copy(update={"document_id": document.document_id})
        }
    )
    edge = authoritative_event_graph_edge(
        document,
        event,
        edge_id="edge:results",
        source_node_id="company:reliance",
        target_node_id="catalyst:q1-results",
        materiality=0.8,
    )
    assert edge.provenance.evidence_ids == (document.document_id, event.event_id)
    assert edge.status.value == "CONFIRMED"


def test_authoritative_http_transport_is_read_only_and_provider_local() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[3]
    source = (
        root / "src/tiaf/market_intelligence/providers/authoritative_http.py"
    ).read_text()
    assert 'client.stream("GET"' in source
    assert all(method not in source for method in ("client.post(", "client.put(", "client.delete("))
    specialist_source = "\n".join(
        path.read_text() for path in (root / "src/tiaf/agents/specialists").rglob("*.py")
    ).casefold()
    assert "authoritative_http" not in specialist_source
    assert "nse_official" not in specialist_source
    assert "bse_official" not in specialist_source


def test_ipo_document_kinds_preserve_fingerprint_without_scoring() -> None:
    assert AuthoritativeDocumentKind.IPO_DRHP.value == "IPO_DRHP"
    assert AuthoritativeDocumentKind.IPO_RHP.value == "IPO_RHP"
    assert AuthoritativeDocumentKind.PROSPECTUS.value == "PROSPECTUS"
    result, _, _ = execute(
        b"IPO source document",
        kinds=(AuthoritativeDocumentKind.IPO_DRHP,),
        located_kind=AuthoritativeDocumentKind.IPO_DRHP,
        rules=(),
    )
    document = result.authoritative_documents[0]
    assert len(document.content_hash) == 64
    assert document.source.authority is SourceAuthority.AUTHORITATIVE
    assert "score" not in type(document).model_fields
