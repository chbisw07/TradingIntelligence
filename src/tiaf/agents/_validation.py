"""Shared validation helpers for Agent-domain public metadata."""

from typing import Any

from tiaf.contracts.common import Metadata

_FORBIDDEN_KEY_PARTS = (
    "access_token",
    "account_id",
    "api_key",
    "apikey",
    "authorization",
    "broker_account",
    "client_id",
    "credential",
    "password",
    "secret",
)
_FORBIDDEN_VALUE_MARKERS = (
    "access_token=",
    "access-token:",
    "api_key=",
    "api-key:",
    "authorization:",
    "client_secret=",
    "password=",
)


def validate_no_secrets(value: object) -> None:
    """Reject credential-shaped keys recursively from an Agent artifact."""
    pending: list[Any] = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            for key, item in current.items():
                normalized = str(key).casefold().replace("-", "_")
                if any(part in normalized for part in _FORBIDDEN_KEY_PARTS):
                    raise ValueError(f"secret-bearing field is not permitted: {key}")
                pending.append(item)
        elif isinstance(current, (list, tuple)):
            pending.extend(current)
        elif isinstance(current, str):
            normalized_value = current.casefold()
            if any(marker in normalized_value for marker in _FORBIDDEN_VALUE_MARKERS):
                raise ValueError("credential-shaped text is not permitted")


def validate_safe_metadata(value: Metadata) -> Metadata:
    """Validate public metadata and return it for Pydantic field validators."""
    validate_no_secrets(value)
    return value


def require_unique(values: tuple[object, ...], label: str) -> None:
    """Reject duplicate immutable semantic collection members."""
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must be unique")
