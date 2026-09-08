"""Read-only grouping of event evidence references into dedupe clusters."""

from dataclasses import dataclass

from tiaf.agents import AgentEvidencePack, AgentEvidenceReference
from tiaf.context import EvidenceStatus
from tiaf.events import (
    EventFamily,
    EventMateriality,
    EventNovelty,
    EventRelevance,
    EventStatus,
    EventType,
    SourceQualityState,
)


@dataclass(frozen=True)
class EventEvidenceRecord:
    reference: AgentEvidenceReference
    cluster_id: str
    active: bool
    family: EventFamily
    event_type: EventType
    relevance: EventRelevance
    materiality: EventMateriality
    novelty: EventNovelty
    status: EventStatus
    source_quality: SourceQualityState
    contradiction_fields: tuple[str, ...]
    structured_facts: tuple[tuple[str, object], ...]


@dataclass(frozen=True)
class EventEvidenceCluster:
    cluster_id: str
    records: tuple[EventEvidenceRecord, ...]
    active_records: tuple[EventEvidenceRecord, ...]


class EventFactBook:
    """Group supplied projections; never acquire or recalculate source evidence."""

    def __init__(self, evidence: AgentEvidencePack) -> None:
        usable = {EvidenceStatus.AVAILABLE, EvidenceStatus.PARTIAL, EvidenceStatus.STALE}
        records: list[EventEvidenceRecord] = []
        for reference in evidence.references:
            if reference.availability not in usable:
                continue
            values = {
                fact.metric_id: fact.value
                for fact in reference.facts
                if fact.metric_id.startswith("event.")
            }
            required = {
                "event.family",
                "event.type",
                "event.relevance",
                "event.materiality",
                "event.novelty",
                "event.status",
                "event.source_quality",
            }
            if not required <= set(values):
                continue
            cluster_id = reference.metadata.get("cluster_id")
            active = reference.metadata.get("active")
            conflicts = reference.metadata.get("contradiction_fields", [])
            if not isinstance(cluster_id, str) or not isinstance(active, bool):
                continue
            if not isinstance(conflicts, list) or not all(
                isinstance(item, str) for item in conflicts
            ):
                continue
            structured = tuple(
                (name.removeprefix("event.fact."), value)
                for name, value in sorted(values.items())
                if name.startswith("event.fact.")
            )
            records.append(
                EventEvidenceRecord(
                    reference=reference,
                    cluster_id=cluster_id,
                    active=active,
                    family=EventFamily(str(values["event.family"])),
                    event_type=EventType(str(values["event.type"])),
                    relevance=EventRelevance(str(values["event.relevance"])),
                    materiality=EventMateriality(str(values["event.materiality"])),
                    novelty=EventNovelty(str(values["event.novelty"])),
                    status=EventStatus(str(values["event.status"])),
                    source_quality=SourceQualityState(str(values["event.source_quality"])),
                    contradiction_fields=tuple(item for item in conflicts if isinstance(item, str)),
                    structured_facts=structured,
                )
            )
        grouped: dict[str, list[EventEvidenceRecord]] = {}
        for item in records:
            grouped.setdefault(item.cluster_id, []).append(item)
        self.clusters = tuple(
            EventEvidenceCluster(
                cluster_id=cluster_id,
                records=tuple(values),
                active_records=tuple(item for item in values if item.active),
            )
            for cluster_id, values in sorted(grouped.items())
            if any(item.active for item in values)
        )
