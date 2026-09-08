"""Provider-neutral event source protocol and bounded in-memory adapter."""

from collections import defaultdict
from datetime import timedelta
from typing import Protocol, runtime_checkable

from .dedupe import DEDUPE_VERSION, cluster_events
from .models import EventDataset, EventRequest, NormalizedEvent, event_fingerprint
from .normalization import NORMALIZATION_VERSION, point_in_time_events
from .quality import weakest_freshness, weakest_quality
from .relevance import meets_relevance


class EventProviderError(RuntimeError):
    """Typed provider-neutral event acquisition failure."""


@runtime_checkable
class EventProvider(Protocol):
    """Read-only source of normalized event records."""

    def identity(self) -> tuple[str, str]: ...

    def resolve_subject(self, symbol: str) -> str | None: ...

    def fetch(self, request: EventRequest) -> EventDataset: ...


class InMemoryEventProvider:
    """Deterministic fixture/caller-data adapter with exact entity indexing."""

    def __init__(
        self,
        events: tuple[NormalizedEvent, ...],
        *,
        provider_id: str = "tiaf.in-memory-events",
        provider_version: str = "1.0",
        validity_minutes: int = 15,
        point_in_time_limitation: str | None = None,
    ) -> None:
        if validity_minutes <= 0:
            raise ValueError("event validity_minutes must be positive")
        event_ids = tuple(item.event_id for item in events)
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("event provider requires unique event IDs")
        self._events = events
        self._identity = (provider_id, provider_version)
        self._validity = timedelta(minutes=validity_minutes)
        self._limitation = point_in_time_limitation
        indexed: dict[str, list[NormalizedEvent]] = defaultdict(list)
        for event in events:
            symbols = {
                item.canonical_symbol
                for item in (event.primary_entity, *event.related_entities)
                if item.canonical_symbol is not None
            }
            for symbol in symbols:
                indexed[symbol].append(event)
        self._by_symbol = {key: tuple(value) for key, value in indexed.items()}

    def identity(self) -> tuple[str, str]:
        return self._identity

    def resolve_subject(self, symbol: str) -> str | None:
        canonical = symbol.strip().upper()
        return canonical if canonical in self._by_symbol else None

    def fetch(self, request: EventRequest) -> EventDataset:
        source = self._by_symbol.get(request.subject, ())
        visible = point_in_time_events(source, as_of=request.as_of)
        selected = tuple(
            item
            for item in visible
            if request.start_at <= item.publication_time <= request.end_at
            and item.family in request.families
            and (not request.source_classes or item.source.source_class in request.source_classes)
            and meets_relevance(item.relevance, request.minimum_relevance)
        )
        clusters = cluster_events(selected)
        matched_cluster_count = len(clusters)
        if len(clusters) > request.max_results:
            newest = sorted(
                clusters,
                key=lambda cluster: max(
                    item.publication_time
                    for item in selected
                    if item.event_id in set(cluster.event_ids)
                ),
                reverse=True,
            )[: request.max_results]
            allowed = {event_id for cluster in newest for event_id in cluster.event_ids}
            selected = tuple(item for item in selected if item.event_id in allowed)
            clusters = tuple(sorted(newest, key=lambda item: item.cluster_id))
        provider_id, provider_version = self._identity
        quality = weakest_quality(tuple(item.quality for item in selected))
        freshness = weakest_freshness(tuple(item.freshness for item in selected))
        fingerprint = event_fingerprint(
            request.subject,
            provider_id,
            provider_version,
            request.as_of,
            selected,
            clusters,
            matched_cluster_count,
            self._limitation,
        )
        acquired_at = max((item.acquisition_time for item in selected), default=request.as_of)
        return EventDataset(
            dataset_id=f"event:{request.request_id}:{fingerprint[:16]}",
            subject=request.subject,
            provider_id=provider_id,
            provider_version=provider_version,
            normalization_version=NORMALIZATION_VERSION,
            dedupe_version=DEDUPE_VERSION,
            requested_as_of=request.as_of,
            acquired_at=acquired_at,
            valid_until=request.as_of + self._validity,
            events=selected,
            clusters=clusters,
            matched_cluster_count=matched_cluster_count,
            truncated=matched_cluster_count > len(clusters),
            quality=quality,
            freshness=freshness,
            point_in_time_limitation=self._limitation,
            fingerprint=fingerprint,
        )
