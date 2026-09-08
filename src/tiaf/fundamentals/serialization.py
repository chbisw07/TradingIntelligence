"""Deterministic JSON serialization for fundamental evidence datasets."""

import json

from .models import FundamentalDataset


def fundamental_dataset_json(dataset: FundamentalDataset) -> str:
    """Serialize one validated dataset with stable key ordering."""
    return json.dumps(
        dataset.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def load_fundamental_dataset_json(payload: str) -> FundamentalDataset:
    """Reconstruct and fully validate a serialized fundamental dataset."""
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise ValueError("fundamental dataset JSON must contain an object")
    return FundamentalDataset.model_validate(value)

