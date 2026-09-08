"""Explicit entity relevance and magnitude-based materiality helpers."""

from tiaf.contracts import Horizon

from .enums import (
    EntityMappingStatus,
    EventMateriality,
    EventRelevance,
)
from .models import NormalizedEvent

RELEVANCE_ORDER = {
    EventRelevance.DIRECT: 0,
    EventRelevance.HIGH: 1,
    EventRelevance.MODERATE: 2,
    EventRelevance.LOW: 3,
    EventRelevance.INCIDENTAL: 4,
    EventRelevance.UNKNOWN: 5,
}
MATERIALITY_ORDER = {
    EventMateriality.CRITICAL: 0,
    EventMateriality.HIGH: 1,
    EventMateriality.MODERATE: 2,
    EventMateriality.LOW: 3,
    EventMateriality.IMMATERIAL: 4,
    EventMateriality.UNKNOWN: 5,
}


def assess_entity_relevance(event: NormalizedEvent, subject: str) -> EventRelevance:
    """Assess only explicit mappings; unresolved or absent mentions are not guessed."""
    canonical = subject.strip().upper()
    primary = event.primary_entity
    if (
        primary.mapping_status is EntityMappingStatus.EXACT
        and primary.canonical_symbol == canonical
    ):
        return EventRelevance.DIRECT
    related = tuple(
        item
        for item in event.related_entities
        if item.canonical_symbol == canonical
        and item.mapping_status is EntityMappingStatus.EXPLICIT_RELATED
    )
    return EventRelevance.HIGH if related else EventRelevance.UNKNOWN


def materiality_from_relative_size(
    relative_size_percent: float | None,
    *,
    horizon: Horizon,
) -> EventMateriality:
    """Generic scale-aware baseline; unknown stays unknown instead of using raw value."""
    del horizon  # retained in the explicit policy seam; A3.5 does not fit horizon thresholds
    if relative_size_percent is None:
        return EventMateriality.UNKNOWN
    magnitude = abs(relative_size_percent)
    if magnitude >= 20:
        return EventMateriality.CRITICAL
    if magnitude >= 10:
        return EventMateriality.HIGH
    if magnitude >= 2:
        return EventMateriality.MODERATE
    if magnitude >= 0.5:
        return EventMateriality.LOW
    return EventMateriality.IMMATERIAL


def meets_relevance(value: EventRelevance, minimum: EventRelevance) -> bool:
    """Return whether a relevance state meets the requested threshold."""
    return RELEVANCE_ORDER[value] <= RELEVANCE_ORDER[minimum]
