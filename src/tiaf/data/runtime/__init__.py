"""Public provider-neutral cache, freshness, and scheduling runtime."""

from tiaf.data.runtime.cache import CacheBackend, InMemoryCacheBackend
from tiaf.data.runtime.coordinator import DataFetchCoordinator
from tiaf.data.runtime.enums import (
    CacheDisposition,
    FetchDisposition,
    ProviderGateState,
    RateLimitScope,
    RequestPriority,
)
from tiaf.data.runtime.errors import DataRuntimeError, ProviderScheduleBlockedError
from tiaf.data.runtime.freshness import (
    FreshnessPolicyRegistry,
    classify_entry_freshness,
    is_cache_acceptable,
)
from tiaf.data.runtime.models import (
    CacheEntry,
    CacheKey,
    CacheStats,
    FetchResult,
    FreshnessAssessment,
    FreshnessRequirement,
    ProviderGateDecision,
    RatePolicy,
    RuntimeStats,
)
from tiaf.data.runtime.rate_policy import RatePolicyRegistry
from tiaf.data.runtime.scheduler import ProviderScheduler

__all__ = [
    "CacheBackend",
    "CacheDisposition",
    "CacheEntry",
    "CacheKey",
    "CacheStats",
    "DataFetchCoordinator",
    "DataRuntimeError",
    "FetchDisposition",
    "FetchResult",
    "FreshnessAssessment",
    "FreshnessPolicyRegistry",
    "FreshnessRequirement",
    "InMemoryCacheBackend",
    "ProviderGateDecision",
    "ProviderGateState",
    "ProviderScheduleBlockedError",
    "ProviderScheduler",
    "RateLimitScope",
    "RatePolicy",
    "RatePolicyRegistry",
    "RequestPriority",
    "RuntimeStats",
    "classify_entry_freshness",
    "is_cache_acceptable",
]
