"""Framework-free canonical digests; transport clocks are not market evidence."""

import hashlib
import json
from typing import Any

from pydantic import BaseModel


def digest(value: Any) -> str:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def semantic(value: Any) -> Any:
    """Remove run-observation clocks only; retain as-of, availability and deadlines."""
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    if isinstance(value, dict):
        return {
            k: semantic(v)
            for k, v in value.items()
            if k
            not in {
                "started_at",
                "completed_at",
                "confirmed_at",
                "elapsed_seconds",
                "runtime_adapter",
            }
        }
    if isinstance(value, (list, tuple)):
        return [semantic(v) for v in value]
    return value
