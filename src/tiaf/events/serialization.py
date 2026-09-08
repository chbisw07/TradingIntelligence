"""Stable JSON round-trip helpers for event evidence."""

import json

from .models import EventDataset


def event_dataset_json(dataset: EventDataset) -> str:
    return json.dumps(
        dataset.model_dump(mode="json"), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )


def load_event_dataset_json(payload: str) -> EventDataset:
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise ValueError("event dataset JSON must contain an object")
    return EventDataset.model_validate(value)
