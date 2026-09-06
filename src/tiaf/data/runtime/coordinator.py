"""Cache/freshness/scheduling coordination with key-scoped single flight."""

from collections.abc import Callable
from datetime import datetime
from threading import Event, RLock
from typing import Any, TypeVar, cast

from tiaf.contracts import FreshnessState
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data.normalization import normalize_datetime_to_ist, normalize_provider_name
from tiaf.data.runtime.cache import CacheBackend, InMemoryCacheBackend
from tiaf.data.runtime.enums import CacheDisposition, FetchDisposition, RequestPriority
from tiaf.data.runtime.errors import ProviderScheduleBlockedError
from tiaf.data.runtime.freshness import classify_entry_freshness, is_cache_acceptable
from tiaf.data.runtime.models import (
    CacheEntry,
    CacheKey,
    FetchResult,
    FreshnessAssessment,
    FreshnessRequirement,
    RuntimeStats,
    cache_disposition_for,
)
from tiaf.data.runtime.scheduler import ProviderScheduler

T = TypeVar("T")


def _wall_now() -> datetime:
    return datetime.now(TIAF_TIMEZONE)


class _Flight[T]:
    def __init__(self) -> None:
        self.event = Event()
        self.result: FetchResult[T] | None = None
        self.error: Exception | None = None


class DataFetchCoordinator:
    """Coordinate factual reads without hiding provider waits or stale fallback."""

    def __init__(
        self,
        cache: CacheBackend | None = None,
        scheduler: ProviderScheduler | None = None,
        *,
        wall_clock: Callable[[], datetime] = _wall_now,
    ) -> None:
        self.cache = cache or InMemoryCacheBackend()
        self.scheduler = scheduler or ProviderScheduler(wall_clock=wall_clock)
        self._wall_clock = wall_clock
        self._lock = RLock()
        self._flights: dict[CacheKey, _Flight[Any]] = {}
        self._fetches = 0
        self._coalesced_requests = 0
        self._provider_blocked = 0
        self._stale_fallbacks = 0

    def get_or_fetch(
        self,
        key: CacheKey,
        freshness_requirement: FreshnessRequirement,
        fetch_fn: Callable[[], T],
        provider: str,
        operation: str,
        *,
        request_priority: RequestPriority = RequestPriority.NORMAL,
        allow_stale_on_error: bool = False,
        force_refresh: bool = False,
        observed_at_getter: Callable[[T], datetime | None] | None = None,
    ) -> FetchResult[T]:
        """Return acceptable cached facts or perform one eligible provider fetch."""
        current = normalize_datetime_to_ist(self._wall_clock())
        cached: CacheEntry[Any] | None = None
        assessment: FreshnessAssessment | None = None
        if force_refresh:
            if allow_stale_on_error:
                cached = self.cache.get(key)
                if cached is not None:
                    assessment = classify_entry_freshness(
                        cached, freshness_requirement, current
                    )
            self.cache.record_disposition(CacheDisposition.BYPASSED)
        else:
            cached = self.cache.get(key)
            if cached is None:
                self.cache.record_disposition(CacheDisposition.MISS)
            else:
                assessment = classify_entry_freshness(cached, freshness_requirement, current)
                self.cache.record_disposition(cache_disposition_for(assessment.state))
                if is_cache_acceptable(assessment, freshness_requirement):
                    return self._cached_result(cached, assessment)

        with self._lock:
            existing = self._flights.get(key)
            if existing is None:
                flight: _Flight[T] = _Flight()
                self._flights[key] = cast(_Flight[Any], flight)
                leader = True
            else:
                flight = cast(_Flight[T], existing)
                self._coalesced_requests += 1
                leader = False

        if not leader:
            flight.event.wait()
            if flight.error is not None:
                raise flight.error
            if flight.result is None:
                raise RuntimeError("single-flight completed without a result")
            return flight.result.model_copy(
                update={"disposition": FetchDisposition.COALESCED, "coalesced": True}
            )

        try:
            result = self._fetch_as_leader(
                key=key,
                requirement=freshness_requirement,
                fetch_fn=fetch_fn,
                provider=provider,
                operation=operation,
                priority=request_priority,
                stale_entry=cached,
                stale_assessment=assessment,
                allow_stale_on_error=allow_stale_on_error,
                observed_at_getter=observed_at_getter,
            )
            flight.result = result
            return result
        except Exception as exc:
            flight.error = exc
            raise
        finally:
            flight.event.set()
            with self._lock:
                self._flights.pop(key, None)

    def invalidate(self, key: CacheKey) -> bool:
        return self.cache.delete(key)

    def invalidate_namespace(self, namespace: str) -> int:
        return self.cache.invalidate_namespace(namespace)

    def invalidate_instrument(self, instrument_identity: str) -> int:
        return self.cache.invalidate_instrument(instrument_identity)

    def enable_provider(self, provider: str) -> None:
        self.scheduler.enable_provider(provider)

    def disable_provider(self, provider: str, reason: str) -> None:
        self.scheduler.disable_provider(provider, reason)

    def stats(self) -> RuntimeStats:
        cache_stats = self.cache.stats()
        with self._lock:
            return RuntimeStats(
                **cache_stats.model_dump(),
                fetches=self._fetches,
                coalesced_requests=self._coalesced_requests,
                provider_blocked=self._provider_blocked,
                stale_fallbacks=self._stale_fallbacks,
            )

    def _fetch_as_leader(
        self,
        *,
        key: CacheKey,
        requirement: FreshnessRequirement,
        fetch_fn: Callable[[], T],
        provider: str,
        operation: str,
        priority: RequestPriority,
        stale_entry: CacheEntry[Any] | None,
        stale_assessment: FreshnessAssessment | None,
        allow_stale_on_error: bool,
        observed_at_getter: Callable[[T], datetime | None] | None,
    ) -> FetchResult[T]:
        try:
            decision = self.scheduler.reserve(provider, operation, str(key))
            if not decision.allowed:
                with self._lock:
                    self._provider_blocked += 1
                raise ProviderScheduleBlockedError(
                    provider=provider,
                    operation=operation,
                    retry_after_seconds=decision.retry_after_seconds,
                    reason=decision.reason or "provider schedule blocked",
                    gate_state=decision.state,
                )
            with self._lock:
                self._fetches += 1
            value = fetch_fn()
            fetched_at = normalize_datetime_to_ist(self._wall_clock())
            observed_at = self._extract_observed_at(value, observed_at_getter)
            source_provider = self._extract_source_provider(value, provider)
            stored = self.cache.put(
                key,
                CacheEntry(
                    key=key,
                    value=value,
                    stored_at=fetched_at,
                    observed_at=observed_at,
                    source_provider=source_provider,
                    metadata={"request_priority": priority.value},
                ),
            )
            self.scheduler.record_success(provider, operation, at=fetched_at)
            assessment = classify_entry_freshness(stored, requirement, fetched_at)
            return FetchResult(
                value=value,
                cache_key=key,
                disposition=FetchDisposition.PROVIDER,
                freshness=assessment.state,
                age_seconds=assessment.age_seconds,
                fetched_at=fetched_at,
                observed_at=observed_at,
                source_provider=source_provider,
                metadata={"request_priority": priority.value},
            )
        except Exception as exc:
            if not isinstance(exc, ProviderScheduleBlockedError):
                self.scheduler.record_failure(provider, operation, str(exc))
            fallback = self._stale_fallback(
                stale_entry,
                stale_assessment,
                requirement,
                allow_stale_on_error,
                priority,
            )
            if fallback is not None:
                return cast(FetchResult[T], fallback)
            raise

    def _stale_fallback(
        self,
        entry: CacheEntry[Any] | None,
        assessment: FreshnessAssessment | None,
        requirement: FreshnessRequirement,
        allowed: bool,
        priority: RequestPriority,
    ) -> FetchResult[Any] | None:
        if (
            not allowed
            or entry is None
            or assessment is None
            or assessment.state is not FreshnessState.STALE
            or assessment.age_seconds is None
            or requirement.max_stale_seconds is None
            or assessment.age_seconds > requirement.max_stale_seconds
        ):
            return None
        with self._lock:
            self._stale_fallbacks += 1
        return FetchResult(
            value=entry.value,
            cache_key=entry.key,
            disposition=FetchDisposition.CACHE,
            freshness=FreshnessState.STALE,
            age_seconds=assessment.age_seconds,
            observed_at=entry.observed_at,
            source_provider=entry.source_provider,
            stale_fallback_used=True,
            metadata={"request_priority": priority.value},
        )

    @staticmethod
    def _cached_result(
        entry: CacheEntry[Any], assessment: FreshnessAssessment
    ) -> FetchResult[Any]:
        return FetchResult(
            value=entry.value,
            cache_key=entry.key,
            disposition=FetchDisposition.CACHE,
            freshness=assessment.state,
            age_seconds=assessment.age_seconds,
            observed_at=entry.observed_at,
            source_provider=entry.source_provider,
        )

    @staticmethod
    def _extract_observed_at(
        value: T, getter: Callable[[T], datetime | None] | None
    ) -> datetime | None:
        observed = getter(value) if getter is not None else getattr(value, "observed_at", None)
        if observed is None:
            return None
        if not isinstance(observed, datetime):
            raise TypeError("observed_at must be a datetime when present")
        return normalize_datetime_to_ist(observed)

    @staticmethod
    def _extract_source_provider(value: object, fallback: str) -> str:
        source = getattr(value, "source_provider", fallback)
        if not isinstance(source, str):
            raise TypeError("source_provider must be a string when present")
        return normalize_provider_name(source)
