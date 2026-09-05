"""Tests for data normalization and deterministic freshness helpers."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from tiaf.contracts import FreshnessState
from tiaf.data import (
    age_seconds,
    classify_freshness,
    normalize_datetime_to_ist,
    normalize_exchange,
    normalize_interval,
    normalize_provider_name,
    normalize_symbol,
)

KOLKATA = ZoneInfo("Asia/Kolkata")


def test_symbol_exchange_and_provider_normalization() -> None:
    assert normalize_symbol(" reliance ") == "RELIANCE"
    assert normalize_exchange(" nse ") == "NSE"
    assert normalize_provider_name(" Provider A ") == "provider a"


@pytest.mark.parametrize(
    ("source", "expected"),
    [("1min", "1m"), (" 5m ", "5m"), ("60min", "1h"), ("daily", "1d")],
)
def test_common_interval_normalization(source: str, expected: str) -> None:
    assert normalize_interval(source) == expected


def test_unknown_interval_is_conservatively_normalized() -> None:
    assert normalize_interval(" 2H ") == "2h"


def test_ambiguous_uppercase_m_interval_is_rejected() -> None:
    with pytest.raises(ValueError, match="ambiguous"):
        normalize_interval("1M")


def test_utc_datetime_is_normalized_to_asia_kolkata() -> None:
    source = datetime(2026, 9, 5, 4, 30, tzinfo=UTC)
    normalized = normalize_datetime_to_ist(source)

    assert normalized == source.astimezone(KOLKATA)
    assert normalized.tzinfo == KOLKATA
    assert normalized.isoformat() == "2026-09-05T10:00:00+05:30"


def test_naive_datetime_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        normalize_datetime_to_ist(datetime(2026, 9, 5, 10))


def test_age_seconds_accepts_different_aware_zones() -> None:
    observed = datetime(2026, 9, 5, 4, 30, tzinfo=UTC)
    now = datetime(2026, 9, 5, 10, 1, tzinfo=KOLKATA)

    assert age_seconds(observed, now) == 60


@pytest.mark.parametrize(
    ("age", "expected"),
    [
        (30, FreshnessState.FRESH),
        (60, FreshnessState.FRESH),
        (61, FreshnessState.AGING),
        (300, FreshnessState.AGING),
        (301, FreshnessState.STALE),
    ],
)
def test_freshness_uses_caller_supplied_thresholds(
    age: float,
    expected: FreshnessState,
) -> None:
    assert classify_freshness(age, fresh_for=60, aging_for=300) is expected


@pytest.mark.parametrize(
    ("age", "fresh_for", "aging_for"),
    [(-1, 60, 300), (1, -1, 300), (1, 300, 60), (float("inf"), 60, 300)],
)
def test_invalid_freshness_inputs_are_rejected(
    age: float,
    fresh_for: float,
    aging_for: float,
) -> None:
    with pytest.raises(ValueError):
        classify_freshness(age, fresh_for, aging_for)
