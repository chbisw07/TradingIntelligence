"""Deterministic JSON helpers for Agent audit records."""

import json

from pydantic import ValidationError

from ._validation import validate_no_secrets
from .errors import AgentOutputValidationError
from .models import AgentRunRecord


def agent_record_json(record: AgentRunRecord, *, indent: int | None = 2) -> str:
    """Serialize one run record with stable keys and normal JSON arrays."""
    payload = record.model_dump(mode="json")
    validate_no_secrets(payload)
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":") if indent is None else None,
        indent=indent,
        ensure_ascii=False,
    )


def load_agent_record_json(value: str) -> AgentRunRecord:
    """Reconstruct and validate one serialized Agent run record."""
    try:
        payload = json.loads(value)
        validate_no_secrets(payload)
        return AgentRunRecord.model_validate(payload)
    except (TypeError, ValueError, ValidationError) as exc:
        raise AgentOutputValidationError(str(exc)) from exc
