"""Caller-relative factual freshness classification and policy registry."""

from datetime import datetime
from threading import RLock
from typing import Any

from tiaf.contracts import FreshnessState
from tiaf.data.normalization import normalize_datetime_to_ist
from tiaf.data.runtime.models import CacheEntry, FreshnessAssessment, FreshnessRequirement


def classify_entry_freshness(
    entry: CacheEntry[Any],
    requirement: FreshnessRequirement,
    now: datetime,
) -> FreshnessAssessment:
    """Classify an entry without inventing an observation timestamp."""
    current = normalize_datetime_to_ist(now)
    based_on = entry.observed_at
    used_stored_at = False
    if based_on is None and requirement.use_stored_at_if_observed_missing:
        based_on = entry.stored_at
        used_stored_at = True
    if based_on is None:
        return FreshnessAssessment(state=FreshnessState.UNKNOWN)

    age = (current - based_on).total_seconds()
    if age < 0:
        return FreshnessAssessment(state=FreshnessState.UNKNOWN, based_on=based_on)
    if entry.expires_at is not None and current >= entry.expires_at:
        state = FreshnessState.STALE
    elif age <= requirement.fresh_for_seconds:
        state = FreshnessState.FRESH
    elif requirement.aging_for_seconds is not None:
        state = (
            FreshnessState.AGING
            if age <= requirement.aging_for_seconds
            else FreshnessState.STALE
        )
    else:
        state = FreshnessState.STALE
    return FreshnessAssessment(
        state=state,
        age_seconds=age,
        based_on=based_on,
        used_stored_at=used_stored_at,
    )


def is_cache_acceptable(
    assessment: FreshnessAssessment,
    requirement: FreshnessRequirement,
) -> bool:
    """Return whether the caller explicitly accepts this classified entry."""
    if assessment.state is FreshnessState.FRESH:
        return True
    if assessment.state is FreshnessState.AGING:
        return requirement.allow_aging
    if assessment.state is FreshnessState.STALE and requirement.allow_stale:
        return (
            requirement.max_stale_seconds is not None
            and assessment.age_seconds is not None
            and assessment.age_seconds <= requirement.max_stale_seconds
        )
    return False


class FreshnessPolicyRegistry:
    """Thread-safe registry of explicit operation defaults.

    The generic runtime deliberately starts empty: consumers may override a
    registered operation policy per request, and no market-wide TTL is assumed.
    """

    def __init__(self) -> None:
        self._policies: dict[str, FreshnessRequirement] = {}
        self._lock = RLock()

    def register(self, operation: str, requirement: FreshnessRequirement) -> None:
        normalized = operation.strip().casefold()
        if not normalized:
            raise ValueError("operation must not be empty")
        with self._lock:
            self._policies[normalized] = requirement

    def get(self, operation: str) -> FreshnessRequirement | None:
        with self._lock:
            return self._policies.get(operation.strip().casefold())

    def require(self, operation: str) -> FreshnessRequirement:
        requirement = self.get(operation)
        if requirement is None:
            raise KeyError(f"no freshness policy registered for {operation!r}")
        return requirement

    def operations(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._policies))
