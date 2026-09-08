"""Event identity, normalization, PIT, correction, and serialization tests."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from tiaf.events import (
    EventFamily,
    EventMateriality,
    EventNormalizationError,
    EventNovelty,
    EventRelevance,
    EventType,
    InMemoryEventProvider,
    classify_explicit_action,
    event_dataset_json,
    load_event_dataset_json,
    materiality_from_relative_size,
    normalize_title,
    revision_state,
)

from ._support import ACQUIRED, HORIZON, NOW, PUBLISHED, event, structured, typed_request


def test_event_times_normalize_to_kolkata_and_naive_is_rejected() -> None:
    utc_event = event(
        published_at=PUBLISHED.astimezone(UTC),
        acquired_at=ACQUIRED.astimezone(UTC),
    )
    assert utc_event.publication_time.isoformat().endswith("+05:30")
    payload = utc_event.model_dump(mode="json")
    assert str(payload["publication_time"]).endswith("+05:30")
    with pytest.raises(ValidationError, match="timezone-aware"):
        event(published_at=datetime(2026, 9, 9, 10, 0))


def test_semantic_collections_are_tuples_and_json_remains_arrays() -> None:
    item = event(facts=[])
    assert isinstance(item.structured_facts, tuple)
    assert isinstance(item.model_dump(mode="json")["structured_facts"], list)
    with pytest.raises(ValidationError, match="frozen"):
        item.normalized_title = "replacement"


def test_title_normalization_is_deterministic_not_sentiment_analysis() -> None:
    assert normalize_title("  Order—Won!  ₹500 Cr ") == "order won 500 cr"


def test_explicit_classification_and_unknown_do_not_parse_headline_tone() -> None:
    assert classify_explicit_action("DIVIDEND_DECLARED") == (
        EventFamily.DIVIDEND,
        EventType.DIVIDEND_DECLARED,
    )
    assert classify_explicit_action("wonderful-looking headline") == (
        EventFamily.OTHER,
        EventType.UNKNOWN,
    )


@pytest.mark.parametrize(
    ("relative_size", "expected"),
    [
        (25.0, EventMateriality.CRITICAL),
        (10.0, EventMateriality.HIGH),
        (2.0, EventMateriality.MODERATE),
        (0.5, EventMateriality.LOW),
        (0.1, EventMateriality.IMMATERIAL),
        (None, EventMateriality.UNKNOWN),
    ],
)
def test_materiality_uses_relative_scale_only(
    relative_size: float | None, expected: EventMateriality
) -> None:
    assert materiality_from_relative_size(relative_size, horizon=HORIZON) is expected


def test_same_event_across_sources_clusters_without_dropping_sources() -> None:
    first = event()
    second = event(
        event_id="event:news",
        source_suffix="news",
        underlying_key=first.underlying_event_key,
        novelty=EventNovelty.DUPLICATE,
    )
    dataset = InMemoryEventProvider((first, second)).fetch(typed_request())
    assert len(dataset.clusters) == 1
    assert set(dataset.clusters[0].event_ids) == {"event:primary", "event:news"}
    assert len(dataset.events) == 2


def test_unrelated_same_source_records_are_not_over_deduplicated() -> None:
    first = event(underlying_key=None, title="Order one")
    second = event(
        event_id="event:second",
        underlying_key=None,
        title="Order two",
        published_at=PUBLISHED + timedelta(minutes=1),
        acquired_at=ACQUIRED + timedelta(minutes=1),
    )
    second = second.model_copy(
        update={"source": second.source.model_copy(update={"document_id": "DOC-second"})}
    )
    dataset = InMemoryEventProvider((first, second)).fetch(typed_request())
    assert len(dataset.clusters) == 2


def test_active_source_conflict_is_preserved() -> None:
    first = event(facts=(structured("order_value", 500.0, unit="INR_CRORE"),))
    second = event(
        event_id="event:news",
        source_suffix="news",
        facts=(structured("order_value", 650.0, unit="INR_CRORE"),),
    )
    dataset = InMemoryEventProvider((first, second)).fetch(typed_request())
    assert dataset.clusters[0].contradiction_fields == ("order_value",)


def test_future_publication_and_acquisition_are_excluded() -> None:
    future = event(
        published_at=NOW + timedelta(minutes=1),
        acquired_at=NOW + timedelta(minutes=2),
    )
    dataset = InMemoryEventProvider((future,)).fetch(typed_request())
    assert dataset.events == ()
    assert dataset.clusters == ()


def test_later_correction_cannot_rewrite_earlier_historical_evidence() -> None:
    prior = event()
    correction = event(
        event_id="event:correction",
        event_type=EventType.ORDER_LOST,
        published_at=NOW + timedelta(hours=1),
        acquired_at=NOW + timedelta(hours=1, minutes=2),
        novelty=EventNovelty.CORRECTION,
        revision=1,
        supersedes=prior.event_id,
    )
    provider = InMemoryEventProvider((prior, correction))
    earlier = provider.fetch(typed_request())
    assert earlier.clusters[0].active_event_ids == (prior.event_id,)
    later_at = NOW + timedelta(hours=2)
    later = provider.fetch(typed_request(as_of=later_at))
    assert set(later.clusters[0].event_ids) == {prior.event_id, correction.event_id}
    assert later.clusters[0].active_event_ids == (correction.event_id,)
    assert later.clusters[0].superseded_event_ids == (prior.event_id,)


def test_invalid_cross_source_correction_is_rejected() -> None:
    prior = event()
    correction = event(
        event_id="event:correction",
        source_suffix="different",
        novelty=EventNovelty.CORRECTION,
        revision=1,
        supersedes=prior.event_id,
    )
    with pytest.raises(EventNormalizationError, match="preserve entity and source"):
        revision_state((prior, correction))


def test_narrow_window_can_select_correction_without_returning_old_antecedent() -> None:
    prior = event(
        published_at=PUBLISHED - timedelta(days=2), acquired_at=ACQUIRED - timedelta(days=2)
    )
    correction = event(
        event_id="event:correction",
        event_type=EventType.ORDER_LOST,
        novelty=EventNovelty.CORRECTION,
        revision=1,
        supersedes=prior.event_id,
    )
    request = typed_request().model_copy(update={"start_at": PUBLISHED - timedelta(hours=1)})
    dataset = InMemoryEventProvider((prior, correction)).fetch(request)
    assert dataset.clusters[0].event_ids == (correction.event_id,)
    assert dataset.clusters[0].active_event_ids == (correction.event_id,)


def test_dataset_round_trip_preserves_arrays_fingerprint_and_timestamps() -> None:
    dataset = InMemoryEventProvider((event(),)).fetch(typed_request())
    payload = event_dataset_json(dataset)
    rebuilt = load_event_dataset_json(payload)
    assert rebuilt == dataset
    assert '"events":[' in payload
    assert "+05:30" in payload


def test_provider_filters_minimum_relevance_without_conflating_materiality() -> None:
    low = event(relevance=EventRelevance.LOW, materiality=EventMateriality.HIGH)
    request = typed_request(minimum=EventRelevance.MODERATE)
    assert InMemoryEventProvider((low,)).fetch(request).events == ()
