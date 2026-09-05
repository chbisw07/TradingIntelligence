"""Pure normalization and freshness helpers for provider data."""

import math
from datetime import datetime
from zoneinfo import ZoneInfo

from tiaf.contracts import FreshnessState

TIAF_TIMEZONE = ZoneInfo("Asia/Kolkata")

_INTERVAL_ALIASES = {
    "1m": "1m",
    "1min": "1m",
    "1minute": "1m",
    "5m": "5m",
    "5min": "5m",
    "5minute": "5m",
    "15m": "15m",
    "15min": "15m",
    "15minute": "15m",
    "1h": "1h",
    "60m": "1h",
    "60min": "1h",
    "1hour": "1h",
    "1d": "1d",
    "1day": "1d",
    "day": "1d",
    "daily": "1d",
}


def _normalize_non_empty(value: str, field_name: str) -> str:
    """Strip a string and reject empty normalized values."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def normalize_symbol(value: str) -> str:
    """Normalize a provider-neutral symbol without imposing naming rules."""
    return _normalize_non_empty(value, "symbol").upper()


def normalize_exchange(value: str) -> str:
    """Normalize a provider-neutral exchange name."""
    return _normalize_non_empty(value, "exchange").upper()


def normalize_provider_name(value: str) -> str:
    """Normalize a provider name for stable comparisons and attribution."""
    return _normalize_non_empty(value, "provider name").casefold()


def normalize_datetime_to_ist(value: datetime) -> datetime:
    """Normalize an aware datetime to the canonical TIAF timezone."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(TIAF_TIMEZONE)


def normalize_interval(value: str) -> str:
    """Normalize a small set of common intervals and preserve unknown labels."""
    compact = _normalize_non_empty(value, "interval").replace(" ", "")
    if compact.endswith("M") and compact[:-1].isdigit():
        raise ValueError("uppercase M interval is ambiguous; use an explicit unit")
    normalized = compact.casefold()
    return _INTERVAL_ALIASES.get(normalized, normalized)


def age_seconds(observed_at: datetime, now: datetime) -> float:
    """Return deterministic elapsed seconds between two aware timestamps."""
    observed = normalize_datetime_to_ist(observed_at)
    current = normalize_datetime_to_ist(now)
    return (current - observed).total_seconds()


def classify_freshness(
    age_seconds: float,
    fresh_for: float,
    aging_for: float,
) -> FreshnessState:
    """Classify an age using caller-supplied, non-market-specific thresholds."""
    values = (age_seconds, fresh_for, aging_for)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("freshness values must be finite")
    if age_seconds < 0 or fresh_for < 0 or aging_for < 0:
        raise ValueError("freshness values must be non-negative")
    if aging_for < fresh_for:
        raise ValueError("aging_for must be greater than or equal to fresh_for")
    if age_seconds <= fresh_for:
        return FreshnessState.FRESH
    if age_seconds <= aging_for:
        return FreshnessState.AGING
    return FreshnessState.STALE
