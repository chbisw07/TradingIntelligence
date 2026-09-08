"""Public provider-neutral A3.5 event/news evidence API."""

from .classification import CLASSIFICATION_VERSION, classify_explicit_action
from .dedupe import DEDUPE_VERSION, cluster_events
from .enums import (
    CatalystDirection,
    CatalystHorizon,
    CatalystStrength,
    ContradictionState,
    EntityKind,
    EntityMappingStatus,
    EventFamily,
    EventMateriality,
    EventNovelty,
    EventRelevance,
    EventSourceClass,
    EventStatus,
    EventType,
    ExecutionRiskState,
    SourceQualityState,
    StructuredFactKind,
)
from .gateway import EventEvidenceGateway, event_evidence_pack, event_gateway_attributes
from .models import (
    EventCluster,
    EventDataset,
    EventEntity,
    EventRequest,
    EventSource,
    NormalizedEvent,
    StructuredEventFact,
    event_fingerprint,
)
from .normalization import (
    NORMALIZATION_VERSION,
    EventNormalizationError,
    normalize_title,
    point_in_time_events,
    revision_state,
)
from .provider import EventProvider, EventProviderError, InMemoryEventProvider
from .quality import source_quality_state, weakest_freshness, weakest_quality
from .relevance import assess_entity_relevance, materiality_from_relative_size, meets_relevance
from .serialization import event_dataset_json, load_event_dataset_json

__all__ = [
    "CLASSIFICATION_VERSION",
    "DEDUPE_VERSION",
    "NORMALIZATION_VERSION",
    "CatalystDirection",
    "CatalystHorizon",
    "CatalystStrength",
    "ContradictionState",
    "EntityKind",
    "EntityMappingStatus",
    "EventCluster",
    "EventDataset",
    "EventEntity",
    "EventEvidenceGateway",
    "EventFamily",
    "EventMateriality",
    "EventNormalizationError",
    "EventNovelty",
    "EventProvider",
    "EventProviderError",
    "EventRelevance",
    "EventRequest",
    "EventSource",
    "EventSourceClass",
    "EventStatus",
    "EventType",
    "ExecutionRiskState",
    "InMemoryEventProvider",
    "NormalizedEvent",
    "SourceQualityState",
    "StructuredEventFact",
    "StructuredFactKind",
    "assess_entity_relevance",
    "classify_explicit_action",
    "cluster_events",
    "event_dataset_json",
    "event_evidence_pack",
    "event_fingerprint",
    "event_gateway_attributes",
    "load_event_dataset_json",
    "materiality_from_relative_size",
    "meets_relevance",
    "normalize_title",
    "point_in_time_events",
    "revision_state",
    "source_quality_state",
    "weakest_freshness",
    "weakest_quality",
]
