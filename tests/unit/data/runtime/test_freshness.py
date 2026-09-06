"""Caller-relative freshness classification tests."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from tiaf.contracts import FreshnessState
from tiaf.data.runtime import (
    CacheEntry,
    CacheKey,
    FreshnessPolicyRegistry,
    FreshnessRequirement,
    classify_entry_freshness,
)

IST = ZoneInfo("Asia/Kolkata")
NOW = datetime(2026, 9, 6, 12, 0, tzinfo=IST)
KEY = CacheKey(namespace="market", operation="quote")
REQUIREMENT = FreshnessRequirement(fresh_for_seconds=10, aging_for_seconds=30)


def make_entry(*, observed_age: float | None, stored_age: float = 1) -> CacheEntry[int]:
    observed = None if observed_age is None else NOW - timedelta(seconds=observed_age)
    return CacheEntry(
        key=KEY,
        value=1,
        stored_at=NOW - timedelta(seconds=stored_age),
        observed_at=observed,
    )


@pytest.mark.parametrize(
    ("age", "expected"),
    [
        (0, FreshnessState.FRESH),
        (10, FreshnessState.FRESH),
        (10.1, FreshnessState.AGING),
        (30, FreshnessState.AGING),
        (30.1, FreshnessState.STALE),
    ],
)
def test_classification_boundaries(age: float, expected: FreshnessState) -> None:
    assessment = classify_entry_freshness(make_entry(observed_age=age), REQUIREMENT, NOW)
    assert assessment.state is expected


def test_missing_observation_is_unknown_by_default() -> None:
    assessment = classify_entry_freshness(make_entry(observed_age=None), REQUIREMENT, NOW)
    assert assessment.state is FreshnessState.UNKNOWN
    assert assessment.age_seconds is None


def test_stored_at_fallback_must_be_explicit() -> None:
    requirement = REQUIREMENT.model_copy(update={"use_stored_at_if_observed_missing": True})
    assessment = classify_entry_freshness(
        make_entry(observed_age=None, stored_age=5), requirement, NOW
    )
    assert assessment.state is FreshnessState.FRESH
    assert assessment.used_stored_at


def test_observed_at_is_preferred_over_recent_storage() -> None:
    assessment = classify_entry_freshness(
        make_entry(observed_age=40, stored_age=1), REQUIREMENT, NOW
    )
    assert assessment.state is FreshnessState.STALE
    assert assessment.age_seconds == 40


def test_explicit_expiry_forces_stale() -> None:
    cached = make_entry(observed_age=1).model_copy(update={"expires_at": NOW})
    assert classify_entry_freshness(cached, REQUIREMENT, NOW).state is FreshnessState.STALE


def test_future_observation_is_unknown_not_fabricated_fresh() -> None:
    assessment = classify_entry_freshness(make_entry(observed_age=-1), REQUIREMENT, NOW)
    assert assessment.state is FreshnessState.UNKNOWN


@pytest.mark.parametrize(
    "values",
    [
        {"fresh_for_seconds": -1},
        {"fresh_for_seconds": 10, "aging_for_seconds": 9},
        {"fresh_for_seconds": 10, "max_stale_seconds": 9},
        {"fresh_for_seconds": float("inf")},
    ],
)
def test_invalid_freshness_thresholds_are_rejected(values: dict[str, float]) -> None:
    with pytest.raises(ValidationError):
        FreshnessRequirement.model_validate(values)


def test_freshness_registry_is_explicit_and_configurable() -> None:
    registry = FreshnessPolicyRegistry()
    assert registry.get("quote") is None
    registry.register(" Quote ", REQUIREMENT)
    assert registry.require("quote") == REQUIREMENT
    assert registry.operations() == ("quote",)


def test_freshness_json_uses_asia_kolkata_offset() -> None:
    assessment = classify_entry_freshness(make_entry(observed_age=5), REQUIREMENT, NOW)
    assert "+05:30" in assessment.model_dump_json()
