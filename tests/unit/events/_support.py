"""Deterministic A3.5 event records, requests, and evidence packs."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from tiaf.agents import (
    AgentBudget,
    AgentCapability,
    AgentEvidencePack,
    AgentRequest,
    AnalysisMode,
    EvidenceGatewayRequest,
    SpecialistId,
)
from tiaf.context import AnalysisPurpose
from tiaf.contracts import DataQuality, EvidenceType, FreshnessState, Horizon, TradeStyle
from tiaf.data import InstrumentType
from tiaf.events import (
    EntityKind,
    EntityMappingStatus,
    EventEntity,
    EventFamily,
    EventMateriality,
    EventNovelty,
    EventRelevance,
    EventRequest,
    EventSource,
    EventSourceClass,
    EventStatus,
    EventType,
    InMemoryEventProvider,
    NormalizedEvent,
    StructuredEventFact,
    StructuredFactKind,
    event_evidence_pack,
    event_gateway_attributes,
)

TZ = ZoneInfo("Asia/Kolkata")
NOW = datetime(2026, 9, 9, 12, 0, tzinfo=TZ)
PUBLISHED = datetime(2026, 9, 9, 10, 0, tzinfo=TZ)
ACQUIRED = datetime(2026, 9, 9, 10, 5, tzinfo=TZ)
HORIZON = Horizon(label="positionald", min_days=5, max_days=20)


def entity(symbol: str = "RELIANCE") -> EventEntity:
    return EventEntity(
        entity_id=f"NSE:{symbol}",
        kind=EntityKind.COMPANY,
        name=f"{symbol} Limited",
        canonical_symbol=symbol,
        mapping_status=EntityMappingStatus.EXACT,
    )


def source(
    source_class: EventSourceClass = EventSourceClass.EXCHANGE_FILING,
    *,
    suffix: str = "primary",
) -> EventSource:
    return EventSource(
        source_id=f"fixture:{suffix}",
        source_class=source_class,
        publisher=f"Fixture {suffix}",
        provider_id="fixture.events",
        source_reference=f"fixture://events/{suffix}",
        document_id=f"DOC-{suffix}" if source_class is EventSourceClass.EXCHANGE_FILING else None,
    )


def structured(
    field_id: str,
    value: str | int | float | bool,
    *,
    unit: str | None = None,
) -> StructuredEventFact:
    kind = (
        StructuredFactKind.BOOLEAN
        if isinstance(value, bool)
        else StructuredFactKind.INTEGER
        if isinstance(value, int)
        else StructuredFactKind.NUMBER
        if isinstance(value, float)
        else StructuredFactKind.TEXT
    )
    return StructuredEventFact(field_id=field_id, kind=kind, value=value, unit=unit)


def event(
    *,
    event_id: str = "event:primary",
    family: EventFamily = EventFamily.ORDER_CONTRACT,
    event_type: EventType = EventType.ORDER_AWARDED,
    source_class: EventSourceClass = EventSourceClass.EXCHANGE_FILING,
    source_suffix: str = "primary",
    published_at: datetime = PUBLISHED,
    acquired_at: datetime = ACQUIRED,
    relevance: EventRelevance = EventRelevance.DIRECT,
    materiality: EventMateriality = EventMateriality.HIGH,
    novelty: EventNovelty = EventNovelty.NEW,
    status: EventStatus = EventStatus.CONFIRMED,
    underlying_key: str | None = "RELIANCE:ORDER:2026-09-09",
    revision: int = 0,
    supersedes: str | None = None,
    facts: tuple[StructuredEventFact, ...] | list[StructuredEventFact] = (),
    quality: DataQuality = DataQuality.GOOD,
    freshness: FreshnessState = FreshnessState.FRESH,
    title: str = "Company event disclosed",
) -> NormalizedEvent:
    return NormalizedEvent(
        event_id=event_id,
        family=family,
        event_type=event_type,
        primary_entity=entity(),
        source=source(source_class, suffix=source_suffix),
        publication_time=published_at,
        event_time=published_at - timedelta(minutes=10),
        acquisition_time=acquired_at,
        normalized_title=title,
        structured_facts=tuple(facts),
        content_reference=f"fixture://content/{event_id}",
        relevance=relevance,
        materiality=materiality,
        novelty=novelty,
        status=status,
        quality=quality,
        freshness=freshness,
        underlying_event_key=underlying_key,
        revision=revision,
        supersedes_event_id=supersedes,
    )


def typed_request(
    *,
    as_of: datetime = NOW,
    minimum: EventRelevance = EventRelevance.INCIDENTAL,
    sources: tuple[EventSourceClass, ...] = (),
) -> EventRequest:
    return EventRequest(
        request_id="event-read",
        subject="RELIANCE",
        as_of=as_of,
        horizon=HORIZON,
        start_at=as_of - timedelta(days=7),
        end_at=as_of,
        families=tuple(EventFamily),
        source_classes=sources,
        required_freshness=FreshnessState.FRESH,
        minimum_relevance=minimum,
        max_results=50,
    )


def gateway_request(
    *,
    capability: AgentCapability = AgentCapability.READ_NEWS,
    as_of: datetime = NOW,
    sources: tuple[EventSourceClass, ...] = (),
) -> EvidenceGatewayRequest:
    typed = typed_request(as_of=as_of, sources=sources)
    return EvidenceGatewayRequest(
        request_id=typed.request_id,
        capability=capability,
        allowed_capabilities=(capability,),
        subject=typed.subject,
        instrument_type=InstrumentType.EQUITY,
        horizon=typed.horizon,
        purpose=AnalysisPurpose.OPPORTUNITY,
        evidence_type=EvidenceType.NEWS,
        requested_attributes=event_gateway_attributes(typed),
        as_of=typed.as_of,
        required_freshness=typed.required_freshness,
        start_at=typed.start_at,
        end_at=typed.end_at,
        context_references=("a2-context",),
        evidence_fingerprint="a" * 64,
        deterministic_baseline_reference="a2-assessment",
        requesting_specialist=SpecialistId.NEWS_EVENT,
        budget=AgentBudget(max_tool_calls=1),
        timeout_seconds=2.0,
    )


def pack(events: tuple[NormalizedEvent, ...]) -> AgentEvidencePack:
    provider = InMemoryEventProvider(events)
    dataset = provider.fetch(typed_request())
    return event_evidence_pack(gateway_request(), dataset, created_at=NOW)


def agent_request(evidence: AgentEvidencePack) -> AgentRequest:
    return AgentRequest(
        request_id=evidence.request_id,
        run_id="run-news-event",
        subject=evidence.subject,
        instrument_type=InstrumentType.EQUITY,
        horizon=HORIZON,
        specialist=SpecialistId.NEWS_EVENT,
        purpose=AnalysisPurpose.OPPORTUNITY,
        trade_style=TradeStyle.POSITIONAL,
        analysis_mode=AnalysisMode.DETERMINISTIC_ONLY,
        task="Interpret only supplied normalized event evidence.",
        a2_context_ids=evidence.analysis_context_ids,
        a2_evidence_ids=("a2:evidence",),
        deterministic_baseline_reference=evidence.deterministic_assessment_id,
        evidence_fingerprint=evidence.evidence_fingerprint,
        allowed_capabilities=(
            AgentCapability.READ_A2_EVIDENCE,
            AgentCapability.READ_FILINGS,
            AgentCapability.READ_NEWS,
        ),
        budget=AgentBudget(),
        created_at=NOW,
    )
