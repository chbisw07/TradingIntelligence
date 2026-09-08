"""Conservative deterministic event clustering and conflict preservation."""

import hashlib
from collections import defaultdict

from .models import EventCluster, NormalizedEvent
from .normalization import normalize_title, revision_state

DEDUPE_VERSION = "1.0"


def cluster_events(events: tuple[NormalizedEvent, ...]) -> tuple[EventCluster, ...]:
    """Group explicit underlying keys, then exact normalized identities only."""
    by_id = {item.event_id: item for item in events}
    keys = {item.event_id: item.underlying_event_key or _conservative_key(item) for item in events}
    for _ in events:
        for event in events:
            if event.supersedes_event_id in by_id:
                keys[event.event_id] = keys[event.supersedes_event_id]
    grouped: dict[str, list[NormalizedEvent]] = defaultdict(list)
    for event in events:
        grouped[keys[event.event_id]].append(event)
    clusters: list[EventCluster] = []
    for key in sorted(grouped):
        records = tuple(
            sorted(grouped[key], key=lambda item: (item.publication_time, item.event_id))
        )
        families = {item.family for item in records}
        types = {item.event_type for item in records}
        subjects = {item.primary_entity.canonical_symbol for item in records}
        if len(subjects) != 1:
            raise ValueError("cluster requires one canonical primary subject")
        subject = next(iter(subjects))
        if subject is None:
            raise ValueError("cluster requires one canonical primary subject")
        active, superseded = revision_state(records)
        active_records = tuple(item for item in records if item.event_id in set(active))
        conflicts = _contradiction_fields(active_records)
        family = (
            next(iter(families))
            if len(families) == 1
            else sorted(families, key=lambda item: item.value)[0]
        )
        event_type = (
            next(iter(types)) if len(types) == 1 else sorted(types, key=lambda item: item.value)[0]
        )
        digest = hashlib.sha256(key.encode()).hexdigest()[:24]
        clusters.append(
            EventCluster(
                cluster_id=f"event-cluster:{digest}",
                subject=subject,
                family=family,
                event_type=event_type,
                event_ids=tuple(item.event_id for item in records),
                active_event_ids=active,
                superseded_event_ids=superseded,
                contradiction_fields=conflicts,
            )
        )
    return tuple(clusters)


def _conservative_key(event: NormalizedEvent) -> str:
    document = event.source.document_id
    if document is not None:
        return f"document:{event.primary_entity.entity_id}:{event.source.source_id}:{document}"
    day = (event.event_time or event.publication_time).date().isoformat()
    return ":".join(
        (
            "exact",
            event.primary_entity.entity_id,
            event.family.value,
            event.event_type.value,
            day,
            normalize_title(event.normalized_title),
        )
    )


def _contradiction_fields(events: tuple[NormalizedEvent, ...]) -> tuple[str, ...]:
    values: dict[str, set[tuple[object, str | None, str | None]]] = defaultdict(set)
    for event in events:
        for fact in event.structured_facts:
            values[fact.field_id].add((fact.value, fact.unit, fact.currency))
    return tuple(sorted(name for name, distinct in values.items() if len(distinct) > 1))
