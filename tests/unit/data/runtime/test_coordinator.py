"""Fetch coordinator, stale fallback, metrics, and single-flight tests."""

import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Event, Lock
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from tiaf.contracts import FreshnessState
from tiaf.data.runtime import (
    CacheEntry,
    CacheKey,
    DataFetchCoordinator,
    FetchDisposition,
    FreshnessRequirement,
    InMemoryCacheBackend,
    ProviderGateState,
    ProviderScheduleBlockedError,
)

IST = ZoneInfo("Asia/Kolkata")
NOW = datetime(2026, 9, 6, 12, 0, tzinfo=IST)
KEY = CacheKey(namespace="market", provider="test", operation="quote")
REQUIREMENT = FreshnessRequirement(
    fresh_for_seconds=10,
    aging_for_seconds=30,
    max_stale_seconds=300,
    use_stored_at_if_observed_missing=True,
)


class WallClock:
    def __init__(self, value: datetime = NOW) -> None:
        self.value = value

    def __call__(self) -> datetime:
        return self.value


def coordinator_with_entry(age: float) -> tuple[DataFetchCoordinator, InMemoryCacheBackend]:
    cache = InMemoryCacheBackend()
    cache.put(
        KEY,
        CacheEntry(
            key=KEY,
            value="cached",
            stored_at=NOW - timedelta(seconds=age),
            observed_at=NOW - timedelta(seconds=age),
            source_provider="test",
        ),
    )
    return DataFetchCoordinator(cache, wall_clock=WallClock()), cache


def test_fresh_cache_avoids_fetch() -> None:
    coordinator, _ = coordinator_with_entry(5)
    result = coordinator.get_or_fetch(
        KEY, REQUIREMENT, lambda: pytest.fail("must not fetch"), "test", "quote"
    )
    assert result.value == "cached"
    assert result.disposition is FetchDisposition.CACHE
    assert result.freshness is FreshnessState.FRESH


def test_aging_cache_is_accepted_when_allowed() -> None:
    coordinator, _ = coordinator_with_entry(20)
    result = coordinator.get_or_fetch(KEY, REQUIREMENT, lambda: "new", "test", "quote")
    assert result.value == "cached"
    assert result.freshness is FreshnessState.AGING


def test_aging_cache_is_refetched_when_not_allowed() -> None:
    coordinator, _ = coordinator_with_entry(20)
    requirement = REQUIREMENT.model_copy(update={"allow_aging": False})
    result = coordinator.get_or_fetch(KEY, requirement, lambda: "new", "test", "quote")
    assert result.value == "new"
    assert result.disposition is FetchDisposition.PROVIDER


def test_stale_cache_is_rejected_normally() -> None:
    coordinator, _ = coordinator_with_entry(100)
    result = coordinator.get_or_fetch(KEY, REQUIREMENT, lambda: "new", "test", "quote")
    assert result.value == "new"
    assert not result.stale_fallback_used


def test_stale_fallback_requires_explicit_permission() -> None:
    coordinator, _ = coordinator_with_entry(100)

    def fail() -> str:
        raise OSError("provider unavailable")

    with pytest.raises(OSError, match="provider unavailable"):
        coordinator.get_or_fetch(KEY, REQUIREMENT, fail, "test", "quote")


def test_stale_fallback_is_returned_with_visible_state() -> None:
    coordinator, _ = coordinator_with_entry(100)

    def fail() -> str:
        raise OSError("provider unavailable")

    result = coordinator.get_or_fetch(
        KEY,
        REQUIREMENT,
        fail,
        "test",
        "quote",
        allow_stale_on_error=True,
    )
    assert result.value == "cached"
    assert result.freshness is FreshnessState.STALE
    assert result.stale_fallback_used


def test_stale_fallback_is_rejected_beyond_maximum() -> None:
    coordinator, _ = coordinator_with_entry(100)
    requirement = REQUIREMENT.model_copy(update={"max_stale_seconds": 50})

    def fail() -> str:
        raise OSError("provider unavailable")

    with pytest.raises(OSError):
        coordinator.get_or_fetch(
            KEY, requirement, fail, "test", "quote", allow_stale_on_error=True
        )


def test_cache_miss_fetches_once_and_stores() -> None:
    coordinator = DataFetchCoordinator(wall_clock=WallClock())
    calls = 0

    def fetch() -> str:
        nonlocal calls
        calls += 1
        return "fresh"

    first = coordinator.get_or_fetch(KEY, REQUIREMENT, fetch, "test", "quote")
    second = coordinator.get_or_fetch(KEY, REQUIREMENT, fetch, "test", "quote")
    assert calls == 1
    assert first.disposition is FetchDisposition.PROVIDER
    assert second.disposition is FetchDisposition.CACHE
    assert coordinator.cache.contains(KEY)


def test_provider_error_is_propagated() -> None:
    coordinator = DataFetchCoordinator(wall_clock=WallClock())
    failure = RuntimeError("broken")

    def fail() -> str:
        raise failure

    with pytest.raises(RuntimeError) as caught:
        coordinator.get_or_fetch(KEY, REQUIREMENT, fail, "test", "quote")
    assert caught.value is failure


def test_provider_block_is_typed_and_counted() -> None:
    coordinator = DataFetchCoordinator(wall_clock=WallClock())
    coordinator.disable_provider("test", "maintenance")
    with pytest.raises(ProviderScheduleBlockedError) as caught:
        coordinator.get_or_fetch(KEY, REQUIREMENT, lambda: "new", "test", "quote")
    assert caught.value.gate_state is ProviderGateState.DISABLED
    assert coordinator.stats().provider_blocked == 1


def test_acceptable_cache_remains_available_when_provider_disabled() -> None:
    coordinator, _ = coordinator_with_entry(1)
    coordinator.disable_provider("test", "maintenance")
    result = coordinator.get_or_fetch(
        KEY, REQUIREMENT, lambda: pytest.fail("must not fetch"), "test", "quote"
    )
    assert result.disposition is FetchDisposition.CACHE


def test_force_refresh_bypasses_acceptable_cache() -> None:
    coordinator, _ = coordinator_with_entry(1)
    result = coordinator.get_or_fetch(
        KEY, REQUIREMENT, lambda: "forced", "test", "quote", force_refresh=True
    )
    assert result.value == "forced"
    assert result.disposition is FetchDisposition.PROVIDER


def test_observed_timestamp_is_retained_and_normalized() -> None:
    coordinator = DataFetchCoordinator(wall_clock=WallClock())
    utc_observed = NOW.astimezone(ZoneInfo("UTC"))
    result = coordinator.get_or_fetch(
        KEY,
        REQUIREMENT,
        lambda: {"value": 1},
        "test",
        "quote",
        observed_at_getter=lambda _: utc_observed,
    )
    assert result.observed_at == NOW
    assert "+05:30" in result.model_dump_json()


def test_naive_observed_timestamp_is_rejected() -> None:
    coordinator = DataFetchCoordinator(wall_clock=WallClock())
    with pytest.raises(ValueError, match="timezone-aware"):
        coordinator.get_or_fetch(
            KEY,
            REQUIREMENT,
            lambda: 1,
            "test",
            "quote",
            observed_at_getter=lambda _: datetime(2026, 9, 6),
        )


def test_simultaneous_identical_requests_use_one_fetch() -> None:
    coordinator = DataFetchCoordinator(wall_clock=WallClock())
    started = Event()
    release = Event()
    start_together = Event()
    calls = 0
    calls_lock = Lock()

    def fetch() -> str:
        nonlocal calls
        with calls_lock:
            calls += 1
        started.set()
        assert release.wait(2)
        return "shared"

    def request() -> object:
        assert start_together.wait(2)
        return coordinator.get_or_fetch(KEY, REQUIREMENT, fetch, "test", "quote")

    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = [pool.submit(request) for _ in range(10)]
        start_together.set()
        assert started.wait(2)
        deadline = time.monotonic() + 2
        while coordinator.stats().coalesced_requests < 9 and time.monotonic() < deadline:
            release.wait(0.001)
        release.set()
        results = [future.result(timeout=2) for future in futures]

    assert calls == 1
    assert {result.value for result in results} == {"shared"}  # type: ignore[attr-defined]
    assert sum(result.coalesced for result in results) == 9  # type: ignore[attr-defined]


def test_single_flight_shares_failure_and_cleans_up() -> None:
    coordinator = DataFetchCoordinator(wall_clock=WallClock())
    started = Event()
    release = Event()
    start_together = Event()
    failure = RuntimeError("shared failure")

    def fail() -> str:
        started.set()
        assert release.wait(2)
        raise failure

    def request() -> None:
        assert start_together.wait(2)
        coordinator.get_or_fetch(KEY, REQUIREMENT, fail, "test", "quote")

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(request) for _ in range(6)]
        start_together.set()
        assert started.wait(2)
        deadline = time.monotonic() + 2
        while coordinator.stats().coalesced_requests < 5 and time.monotonic() < deadline:
            release.wait(0.001)
        release.set()
        errors = []
        for future in futures:
            with pytest.raises(RuntimeError) as caught:
                future.result(timeout=2)
            errors.append(caught.value)

    assert all(error is failure for error in errors)
    recovered = coordinator.get_or_fetch(KEY, REQUIREMENT, lambda: "ok", "test", "quote")
    assert recovered.value == "ok"


def test_different_keys_fetch_independently() -> None:
    coordinator = DataFetchCoordinator(wall_clock=WallClock())
    first_started = Event()
    second_started = Event()
    other = KEY.model_copy(update={"instrument_identity": "other"})

    def first_fetch() -> str:
        first_started.set()
        assert second_started.wait(2)
        return "first"

    def second_fetch() -> str:
        second_started.set()
        assert first_started.wait(2)
        return "second"

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(
            coordinator.get_or_fetch, KEY, REQUIREMENT, first_fetch, "test", "quote"
        )
        second = pool.submit(
            coordinator.get_or_fetch, other, REQUIREMENT, second_fetch, "test", "quote"
        )
        assert first.result(timeout=2).value == "first"
        assert second.result(timeout=2).value == "second"


def test_runtime_metrics_are_immutable_and_complete() -> None:
    coordinator = DataFetchCoordinator(wall_clock=WallClock())
    coordinator.get_or_fetch(KEY, REQUIREMENT, lambda: "new", "test", "quote")
    coordinator.get_or_fetch(KEY, REQUIREMENT, lambda: "unused", "test", "quote")
    stats = coordinator.stats()
    assert stats.fetches == 1
    assert stats.hits == 1
    assert stats.misses == 1
    assert stats.fresh_hits == 1
    with pytest.raises(ValidationError):
        stats.fetches = 3


def test_fetch_result_json_round_trip_and_immutability() -> None:
    coordinator = DataFetchCoordinator(wall_clock=WallClock())
    result = coordinator.get_or_fetch(KEY, REQUIREMENT, lambda: [1, 2], "test", "quote")
    dumped = result.model_dump(mode="json")
    assert dumped["value"] == [1, 2]
    assert dumped["cache_key"]["parameters"] == []
    assert type(result).model_validate(dumped) == result
    with pytest.raises(ValidationError):
        result.value = [3]
