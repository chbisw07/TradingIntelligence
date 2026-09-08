"""Controlled READ_NEWS/READ_FILINGS gateway and lossless evidence projection."""

import hashlib
import json
import re
from datetime import datetime

from tiaf.agents import (
    AgentCapability,
    AgentEvidencePack,
    AgentEvidenceReference,
    AgentFailure,
    AgentUsage,
    EvidenceFact,
    EvidenceFactKind,
    EvidenceFactParameter,
)
from tiaf.agents.gateways import (
    EvidenceGatewayContext,
    EvidenceGatewayRequest,
    EvidenceGatewayResult,
    EvidenceGatewayStatus,
    GatewayCacheStatus,
    GatewayIdentity,
)
from tiaf.context import EvidenceStatus
from tiaf.contracts import DataQuality, EvidenceSource, EvidenceType, FreshnessState

from .dedupe import DEDUPE_VERSION
from .enums import EventFamily, EventRelevance, EventSourceClass
from .models import EventDataset, EventRequest, NormalizedEvent
from .normalization import NORMALIZATION_VERSION
from .provider import EventProvider, EventProviderError
from .quality import source_quality_state

GATEWAY_ID = "tiaf.events"
GATEWAY_VERSION = "1.0"
_PRIMARY_CLASSES = {
    EventSourceClass.EXCHANGE_FILING,
    EventSourceClass.REGULATORY_FILING,
}
_FIELD_ID = re.compile(r"[^a-z0-9._-]+")


def event_gateway_attributes(request: EventRequest) -> tuple[str, ...]:
    """Encode typed event filters in the existing bounded gateway vocabulary."""
    return (
        *(f"family:{item.value}" for item in request.families),
        *(f"source:{item.value}" for item in request.source_classes),
        f"relevance:{request.minimum_relevance.value}",
        f"max:{request.max_results}",
        f"normalization:{NORMALIZATION_VERSION}",
        f"dedupe:{DEDUPE_VERSION}",
    )


class EventEvidenceGateway:
    """Acquire bounded normalized records; never expose URL-fetch authority."""

    def __init__(self, provider: EventProvider) -> None:
        if not isinstance(provider, EventProvider):
            raise TypeError("event provider does not satisfy protocol")
        self._provider = provider
        provider_id, provider_version = provider.identity()
        self._identity = GatewayIdentity(
            gateway_id=f"{GATEWAY_ID}:{provider_id}",
            gateway_version=f"{GATEWAY_VERSION}+{provider_version}",
        )

    def identity(self) -> GatewayIdentity:
        return self._identity

    def capabilities(self) -> tuple[AgentCapability, ...]:
        return (AgentCapability.READ_FILINGS, AgentCapability.READ_NEWS)

    def can_handle(self, request: EvidenceGatewayRequest) -> bool:
        return (
            request.capability in self.capabilities() and request.evidence_type is EvidenceType.NEWS
        )

    def fetch(
        self,
        request: EvidenceGatewayRequest,
        context: EvidenceGatewayContext,
    ) -> EvidenceGatewayResult:
        if request.deterministic_baseline_reference is None:
            return self._failure(request, context.invoked_at, "A2 baseline reference is required")
        if request.start_at is None or request.end_at is None:
            return self._failure(request, context.invoked_at, "event gateway requires a time range")
        subject = self._provider.resolve_subject(request.subject)
        if subject is None:
            return EvidenceGatewayResult(
                request_id=request.request_id,
                capability=request.capability,
                subject=request.subject,
                status=EvidenceGatewayStatus.MISSING,
                gateway_identity=self._identity,
                produced_at=context.invoked_at,
                cache_status=GatewayCacheStatus.MISS,
                usage=AgentUsage(tool_calls=1),
                warnings=("Canonical event subject is unavailable",),
            )
        try:
            families, sources, minimum, maximum = _parse_attributes(request.requested_attributes)
            if request.capability is AgentCapability.READ_FILINGS:
                if sources and not set(sources) <= _PRIMARY_CLASSES:
                    raise ValueError("READ_FILINGS accepts only filing source classes")
                sources = sources or tuple(sorted(_PRIMARY_CLASSES, key=lambda item: item.value))
            dataset = self._provider.fetch(
                EventRequest(
                    request_id=request.request_id,
                    subject=subject,
                    as_of=request.as_of,
                    horizon=request.horizon,
                    start_at=request.start_at,
                    end_at=request.end_at,
                    families=families,
                    source_classes=sources,
                    required_freshness=request.required_freshness,
                    minimum_relevance=minimum,
                    max_results=maximum,
                )
            )
        except (EventProviderError, ValueError) as exc:
            return self._failure(request, context.invoked_at, str(exc))
        if not dataset.events:
            return EvidenceGatewayResult(
                request_id=request.request_id,
                capability=request.capability,
                subject=request.subject,
                status=EvidenceGatewayStatus.MISSING,
                gateway_identity=self._identity,
                produced_at=context.invoked_at,
                cache_status=GatewayCacheStatus.MISS,
                usage=AgentUsage(tool_calls=1),
                warnings=("No point-in-time event records satisfy the request",),
            )
        pack = event_evidence_pack(
            request, dataset, created_at=max(context.invoked_at, dataset.acquired_at)
        )
        status = _gateway_status(dataset)
        return EvidenceGatewayResult(
            request_id=request.request_id,
            capability=request.capability,
            subject=request.subject,
            status=status,
            gateway_identity=self._identity,
            evidence_pack=pack,
            evidence_fingerprint=dataset.fingerprint,
            source_timestamps=tuple(sorted({item.publication_time for item in dataset.events})),
            acquired_at=dataset.acquired_at,
            produced_at=max(context.invoked_at, dataset.acquired_at),
            valid_until=dataset.valid_until,
            freshness=dataset.freshness,
            quality=dataset.quality,
            cache_status=GatewayCacheStatus.MISS,
            usage=AgentUsage(tool_calls=1),
            warnings=tuple(
                item
                for item in (
                    dataset.point_in_time_limitation,
                    (
                        f"Event result limited to {len(dataset.clusters)} of "
                        f"{dataset.matched_cluster_count} matching clusters"
                        if dataset.truncated
                        else None
                    ),
                )
                if item is not None
            ),
        )

    def _failure(
        self, request: EvidenceGatewayRequest, produced_at: datetime, detail: str
    ) -> EvidenceGatewayResult:
        return EvidenceGatewayResult(
            request_id=request.request_id,
            capability=request.capability,
            subject=request.subject,
            status=EvidenceGatewayStatus.INVALID_REQUEST,
            gateway_identity=self._identity,
            produced_at=produced_at,
            cache_status=GatewayCacheStatus.MISS,
            usage=AgentUsage(tool_calls=1),
            failure=AgentFailure(error_type="EventGatewayRequestError", detail=detail),
        )


def event_evidence_pack(
    request: EvidenceGatewayRequest,
    dataset: EventDataset,
    *,
    created_at: datetime,
) -> AgentEvidencePack:
    """Project every source record while marking active cluster versions."""
    if request.deterministic_baseline_reference is None:
        raise ValueError("event evidence pack requires A2 baseline identity")
    clusters = {event_id: cluster for cluster in dataset.clusters for event_id in cluster.event_ids}
    references = tuple(
        _event_reference(item, dataset, clusters[item.event_id]) for item in dataset.events
    )
    return AgentEvidencePack(
        pack_id=f"{dataset.dataset_id}:agent-pack",
        request_id=request.request_id,
        subject=request.subject,
        evidence_fingerprint=dataset.fingerprint,
        references=references,
        analysis_context_ids=request.context_references,
        deterministic_assessment_id=request.deterministic_baseline_reference,
        overall_quality=dataset.quality,
        overall_freshness=dataset.freshness,
        evidence_coverage=(
            len(dataset.clusters) / dataset.matched_cluster_count
            if dataset.matched_cluster_count
            else 0.0
        ),
        created_at=created_at,
        metadata={
            "provider_id": dataset.provider_id,
            "provider_version": dataset.provider_version,
            "normalization_version": dataset.normalization_version,
            "dedupe_version": dataset.dedupe_version,
            "cluster_count": len(dataset.clusters),
            "point_in_time_limitation": dataset.point_in_time_limitation,
        },
    )


def _event_reference(
    event: NormalizedEvent, dataset: EventDataset, cluster: object
) -> AgentEvidenceReference:
    from .models import EventCluster

    if not isinstance(cluster, EventCluster):
        raise TypeError("event record requires a cluster")
    common = (
        EvidenceFactParameter(name="cluster_id", value=cluster.cluster_id),
        EvidenceFactParameter(name="active", value=event.event_id in cluster.active_event_ids),
        EvidenceFactParameter(name="source_id", value=event.source.source_id),
        EvidenceFactParameter(name="source_class", value=event.source.source_class.value),
    )
    raw = (
        ("family", event.family.value),
        ("type", event.event_type.value),
        ("relevance", event.relevance.value),
        ("materiality", event.materiality.value),
        ("novelty", event.novelty.value),
        ("status", event.status.value),
        ("source_quality", source_quality_state(event.source.source_class).value),
        ("publication_time", event.publication_time.isoformat()),
        ("acquisition_time", event.acquisition_time.isoformat()),
        ("title", event.normalized_title),
    )
    facts = [
        EvidenceFact(
            fact_id=f"{event.event_id}:{name}",
            kind=EvidenceFactKind.EVENT,
            metric_id=f"event.{name}",
            value=value,
            parameters=common,
            as_of=event.publication_time,
            quality=event.quality,
            freshness=event.freshness,
            source_evidence=(event.source.source_reference,),
        )
        for name, value in raw
    ]
    if event.event_time is not None:
        facts.append(
            EvidenceFact(
                fact_id=f"{event.event_id}:event_time",
                kind=EvidenceFactKind.EVENT,
                metric_id="event.event_time",
                value=event.event_time.isoformat(),
                parameters=common,
                as_of=event.publication_time,
                quality=event.quality,
                freshness=event.freshness,
                source_evidence=(event.source.source_reference,),
            )
        )
    for item in event.structured_facts:
        metric = _FIELD_ID.sub("_", item.field_id.casefold()).strip("._-")
        facts.append(
            EvidenceFact(
                fact_id=f"{event.event_id}:fact:{metric}",
                kind=EvidenceFactKind.EVENT,
                metric_id=f"event.fact.{metric}",
                value=item.value,
                unit=item.unit,
                parameters=(*common, EvidenceFactParameter(name="locator", value=item.locator)),
                as_of=event.publication_time,
                quality=event.quality,
                freshness=event.freshness,
                source_evidence=(event.source.source_reference,),
            )
        )
    canonical = json.dumps(event.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    availability = (
        EvidenceStatus.STALE
        if event.freshness is FreshnessState.STALE
        else EvidenceStatus.PARTIAL
        if event.quality is not DataQuality.GOOD
        else EvidenceStatus.AVAILABLE
    )
    return AgentEvidenceReference(
        evidence_id=event.event_id,
        evidence_type=EvidenceType.NEWS,
        subject=dataset.subject,
        producer_id=dataset.provider_id,
        producer_version=dataset.provider_version,
        source=EvidenceSource.INTERNAL
        if dataset.provider_id.startswith("tiaf.")
        else EvidenceSource.THIRD_PARTY,
        availability=availability,
        quality=event.quality,
        freshness=event.freshness,
        observed_at=event.publication_time,
        acquired_at=event.acquisition_time,
        checksum=hashlib.sha256(canonical.encode()).hexdigest(),
        source_reference=event.source.source_reference,
        facts=tuple(facts),
        metadata={
            "cluster_id": cluster.cluster_id,
            "active": event.event_id in cluster.active_event_ids,
            "superseded": event.event_id in cluster.superseded_event_ids,
            "contradiction_fields": list(cluster.contradiction_fields),
            "source_id": event.source.source_id,
            "source_class": event.source.source_class.value,
            "document_id": event.source.document_id,
            "revision": event.revision,
            "supersedes_event_id": event.supersedes_event_id,
            "primary_entity_id": event.primary_entity.entity_id,
            "primary_mapping_status": event.primary_entity.mapping_status.value,
            "related_entity_ids": [item.entity_id for item in event.related_entities],
        },
    )


def _parse_attributes(
    attributes: tuple[str, ...],
) -> tuple[tuple[EventFamily, ...], tuple[EventSourceClass, ...], EventRelevance, int]:
    families: list[EventFamily] = []
    sources: list[EventSourceClass] = []
    relevance: EventRelevance | None = None
    maximum: int | None = None
    for attribute in attributes:
        key, separator, value = attribute.partition(":")
        if not separator:
            raise ValueError(f"unsupported event gateway attribute: {attribute}")
        if key == "family":
            families.append(EventFamily(value))
        elif key == "source":
            sources.append(EventSourceClass(value))
        elif key == "relevance":
            relevance = EventRelevance(value)
        elif key == "max":
            maximum = int(value)
        elif (key, value) not in {
            ("normalization", NORMALIZATION_VERSION),
            ("dedupe", DEDUPE_VERSION),
        }:
            raise ValueError(f"unsupported event gateway attribute: {attribute}")
    if not families or relevance is None or maximum is None:
        raise ValueError("event gateway requires family, relevance, and max attributes")
    if len(families) != len(set(families)) or len(sources) != len(set(sources)):
        raise ValueError("event gateway attributes must be unique")
    if not 1 <= maximum <= 500:
        raise ValueError("event gateway max must be between 1 and 500")
    return tuple(families), tuple(sources), relevance, maximum


def _gateway_status(dataset: EventDataset) -> EvidenceGatewayStatus:
    if dataset.freshness is FreshnessState.STALE:
        return EvidenceGatewayStatus.STALE
    if dataset.quality is not DataQuality.GOOD or dataset.truncated:
        return EvidenceGatewayStatus.PARTIAL
    return EvidenceGatewayStatus.SUCCESS
