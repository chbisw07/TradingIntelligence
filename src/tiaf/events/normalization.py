"""Deterministic title and point-in-time revision normalization."""

import re
import unicodedata
from collections import defaultdict
from datetime import datetime

from .models import NormalizedEvent

NORMALIZATION_VERSION = "1.0"
_SPACE = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s]", flags=re.UNICODE)


class EventNormalizationError(ValueError):
    """A normalized event set is inconsistent or ambiguous."""


def normalize_title(value: str) -> str:
    """Create a conservative comparison title without interpreting its tone."""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return _SPACE.sub(" ", _PUNCT.sub(" ", normalized)).strip()


def point_in_time_events(
    events: tuple[NormalizedEvent, ...],
    *,
    as_of: datetime,
) -> tuple[NormalizedEvent, ...]:
    """Retain records both published and acquired by decision time."""
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise EventNormalizationError("point-in-time boundary must be timezone-aware")
    return tuple(
        sorted(
            (
                item
                for item in events
                if item.publication_time <= as_of and item.acquisition_time <= as_of
            ),
            key=lambda item: (item.publication_time, item.acquisition_time, item.event_id),
        )
    )


def revision_state(
    events: tuple[NormalizedEvent, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return active and superseded IDs while preserving all visible versions."""
    by_id = {item.event_id: item for item in events}
    if len(by_id) != len(events):
        raise EventNormalizationError("event IDs must be unique")
    superseded: set[str] = set()
    grouped: dict[tuple[str, str, str], list[NormalizedEvent]] = defaultdict(list)
    for item in events:
        if item.underlying_event_key is not None:
            key = (
                item.primary_entity.entity_id,
                item.source.source_id,
                item.underlying_event_key,
            )
            grouped[key].append(item)
        if item.supersedes_event_id is not None:
            prior = by_id.get(item.supersedes_event_id)
            if prior is None:
                # A narrow request window may contain the correction but not its
                # older antecedent. The explicit ID is still retained; there is
                # no absent record to mark superseded in this result set.
                continue
            if (
                prior.primary_entity.entity_id != item.primary_entity.entity_id
                or prior.source.source_id != item.source.source_id
            ):
                raise EventNormalizationError("correction must preserve entity and source identity")
            if prior.revision >= item.revision:
                raise EventNormalizationError("correction revision must increase")
            superseded.add(prior.event_id)
    for values in grouped.values():
        revisions = [(item.underlying_event_key, item.revision) for item in values]
        if len(revisions) != len(set(revisions)):
            raise EventNormalizationError("ambiguous same-source event revision")
    active = tuple(item.event_id for item in events if item.event_id not in superseded)
    return active, tuple(item.event_id for item in events if item.event_id in superseded)
