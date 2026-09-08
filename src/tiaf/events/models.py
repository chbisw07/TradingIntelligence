"""Immutable provider-neutral contracts for event and filing evidence."""

import hashlib
import json
import math
from typing import Annotated, Literal, Self

from pydantic import (
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    StringConstraints,
    model_validator,
)

from tiaf.agents._validation import require_unique, validate_safe_metadata
from tiaf.contracts import ContractModel, DataQuality, FreshnessState, Horizon
from tiaf.contracts.common import Metadata, NonEmptyStr, Symbol, TiafDateTime

from .enums import (
    EntityKind,
    EntityMappingStatus,
    EventFamily,
    EventMateriality,
    EventNovelty,
    EventRelevance,
    EventSourceClass,
    EventStatus,
    EventType,
    StructuredFactKind,
)

type StructuredFactValue = StrictStr | StrictInt | StrictFloat | StrictBool
UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class EventEntity(ContractModel):
    """Explicit canonical or explicitly related entity; never a fuzzy guess."""

    entity_id: NonEmptyStr
    kind: EntityKind
    name: NonEmptyStr
    canonical_symbol: Symbol | None = None
    relation: NonEmptyStr = "PRIMARY"
    mapping_status: EntityMappingStatus

    @model_validator(mode="after")
    def validate_mapping(self) -> Self:
        if (
            self.mapping_status
            in {EntityMappingStatus.EXACT, EntityMappingStatus.EXPLICIT_RELATED}
            and self.canonical_symbol is None
        ):
            raise ValueError("resolved event entity requires a canonical symbol")
        return self


class EventSource(ContractModel):
    """Source and acquisition identity without provider transport details."""

    source_id: NonEmptyStr
    source_class: EventSourceClass
    publisher: NonEmptyStr
    provider_id: NonEmptyStr
    source_reference: NonEmptyStr
    document_id: NonEmptyStr | None = None
    revision_marker: NonEmptyStr | None = None


class StructuredEventFact(ContractModel):
    """One typed scalar explicitly supplied by a source or extractor."""

    field_id: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            pattern=r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$",
        ),
    ]
    kind: StructuredFactKind
    value: StructuredFactValue
    unit: NonEmptyStr | None = None
    currency: NonEmptyStr | None = None
    locator: NonEmptyStr | None = None
    extraction_method: NonEmptyStr = "SOURCE_STRUCTURED"
    extraction_version: NonEmptyStr = "1.0"

    @model_validator(mode="after")
    def validate_value_kind(self) -> Self:
        if isinstance(self.value, float) and not math.isfinite(self.value):
            raise ValueError("structured event fact must be finite")
        actual = (
            StructuredFactKind.BOOLEAN
            if isinstance(self.value, bool)
            else StructuredFactKind.INTEGER
            if isinstance(self.value, int)
            else StructuredFactKind.NUMBER
            if isinstance(self.value, float)
            else StructuredFactKind.TEXT
        )
        if self.kind is StructuredFactKind.DATE:
            if not isinstance(self.value, str):
                raise ValueError("DATE structured facts require ISO text")
        elif self.kind is not actual:
            raise ValueError("structured event fact kind does not match value")
        if self.currency is not None and self.unit is None:
            raise ValueError("currency requires an explicit unit")
        return self


class NormalizedEvent(ContractModel):
    """One source record for an event, preserving all information-time fields."""

    schema_version: Literal["1.0"] = "1.0"
    event_id: NonEmptyStr
    family: EventFamily
    event_type: EventType
    primary_entity: EventEntity
    related_entities: tuple[EventEntity, ...] = ()
    source: EventSource
    publication_time: TiafDateTime
    event_time: TiafDateTime | None = None
    acquisition_time: TiafDateTime
    normalized_title: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=500),
    ]
    structured_facts: tuple[StructuredEventFact, ...] = ()
    content_reference: NonEmptyStr | None = None
    bounded_excerpt: (
        Annotated[
            str,
            StringConstraints(strip_whitespace=True, min_length=1, max_length=1000),
        ]
        | None
    ) = None
    relevance: EventRelevance
    materiality: EventMateriality
    novelty: EventNovelty
    status: EventStatus = EventStatus.UNKNOWN
    quality: DataQuality
    freshness: FreshnessState
    underlying_event_key: NonEmptyStr | None = None
    revision: int = Field(default=0, ge=0)
    supersedes_event_id: NonEmptyStr | None = None
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_event(self) -> Self:
        validate_safe_metadata(self.metadata)
        if self.acquisition_time < self.publication_time:
            raise ValueError("event acquisition cannot predate publication")
        if self.supersedes_event_id == self.event_id:
            raise ValueError("event cannot supersede itself")
        if self.novelty is EventNovelty.CORRECTION and self.supersedes_event_id is None:
            raise ValueError("correction requires supersedes_event_id")
        if self.supersedes_event_id is not None and self.revision == 0:
            raise ValueError("superseding event requires a positive revision")
        if self.relevance is EventRelevance.DIRECT and (
            self.primary_entity.mapping_status is not EntityMappingStatus.EXACT
            or self.primary_entity.canonical_symbol is None
        ):
            raise ValueError("DIRECT relevance requires exact primary entity mapping")
        require_unique(
            tuple(item.entity_id for item in self.related_entities), "related entity IDs"
        )
        if self.primary_entity.entity_id in {item.entity_id for item in self.related_entities}:
            raise ValueError("primary entity cannot be repeated as related entity")
        require_unique(tuple(item.field_id for item in self.structured_facts), "event fact fields")
        return self


class EventCluster(ContractModel):
    """One underlying event with source records and current PIT versions visible."""

    cluster_id: NonEmptyStr
    subject: Symbol
    family: EventFamily
    event_type: EventType
    event_ids: tuple[NonEmptyStr, ...]
    active_event_ids: tuple[NonEmptyStr, ...]
    superseded_event_ids: tuple[NonEmptyStr, ...] = ()
    contradiction_fields: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_cluster(self) -> Self:
        if not self.event_ids or not self.active_event_ids:
            raise ValueError("event cluster requires records and active records")
        for values, label in (
            (self.event_ids, "cluster event IDs"),
            (self.active_event_ids, "active event IDs"),
            (self.superseded_event_ids, "superseded event IDs"),
            (self.contradiction_fields, "contradiction fields"),
        ):
            require_unique(values, label)
        if not set(self.active_event_ids) <= set(self.event_ids):
            raise ValueError("active event IDs must belong to cluster")
        if not set(self.superseded_event_ids) <= set(self.event_ids):
            raise ValueError("superseded event IDs must belong to cluster")
        if set(self.active_event_ids) & set(self.superseded_event_ids):
            raise ValueError("active and superseded event IDs must be disjoint")
        return self


class EventRequest(ContractModel):
    """Bounded semantic request consumed by an event provider."""

    request_id: NonEmptyStr
    subject: Symbol
    as_of: TiafDateTime
    horizon: Horizon
    start_at: TiafDateTime
    end_at: TiafDateTime
    families: tuple[EventFamily, ...]
    source_classes: tuple[EventSourceClass, ...] = ()
    required_freshness: FreshnessState
    minimum_relevance: EventRelevance
    max_results: int = Field(ge=1, le=500)

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        if not self.families:
            raise ValueError("event request requires at least one family")
        require_unique(self.families, "event families")
        require_unique(self.source_classes, "event source classes")
        if self.end_at <= self.start_at or self.end_at > self.as_of:
            raise ValueError("event request window must increase and end by as_of")
        return self


class EventDataset(ContractModel):
    """Normalized PIT event records plus non-destructive clusters."""

    schema_version: Literal["1.0"] = "1.0"
    dataset_id: NonEmptyStr
    subject: Symbol
    provider_id: NonEmptyStr
    provider_version: NonEmptyStr
    normalization_version: NonEmptyStr
    dedupe_version: NonEmptyStr
    requested_as_of: TiafDateTime
    acquired_at: TiafDateTime
    valid_until: TiafDateTime
    events: tuple[NormalizedEvent, ...]
    clusters: tuple[EventCluster, ...]
    matched_cluster_count: int = Field(ge=0)
    truncated: bool
    quality: DataQuality
    freshness: FreshnessState
    point_in_time_limitation: NonEmptyStr | None = None
    fingerprint: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]

    @model_validator(mode="after")
    def validate_dataset(self) -> Self:
        event_ids = tuple(item.event_id for item in self.events)
        require_unique(event_ids, "dataset event IDs")
        require_unique(tuple(item.cluster_id for item in self.clusters), "cluster IDs")
        if {event_id for cluster in self.clusters for event_id in cluster.event_ids} != set(
            event_ids
        ):
            raise ValueError("clusters must cover every event exactly")
        if sum(len(item.event_ids) for item in self.clusters) != len(event_ids):
            raise ValueError("an event cannot belong to multiple clusters")
        if self.matched_cluster_count < len(self.clusters):
            raise ValueError("matched cluster count cannot be below returned clusters")
        if self.truncated != (self.matched_cluster_count > len(self.clusters)):
            raise ValueError("event truncation flag must match cluster counts")
        if self.valid_until <= self.requested_as_of:
            raise ValueError("event dataset valid_until must follow requested_as_of")
        return self


def event_fingerprint(
    subject: str,
    provider_id: str,
    provider_version: str,
    as_of: object,
    events: tuple[NormalizedEvent, ...],
    clusters: tuple[EventCluster, ...],
    matched_cluster_count: int,
    limitation: str | None,
) -> str:
    """Return stable identity for the exact normalized event evidence set."""
    payload = {
        "subject": subject,
        "provider_id": provider_id,
        "provider_version": provider_version,
        "as_of": str(as_of),
        "events": [item.model_dump(mode="json") for item in events],
        "clusters": [item.model_dump(mode="json") for item in clusters],
        "matched_cluster_count": matched_cluster_count,
        "limitation": limitation,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode()).hexdigest()
