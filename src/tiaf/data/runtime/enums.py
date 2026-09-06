"""Stable enums for the provider-neutral data runtime."""

from enum import StrEnum


class CacheDisposition(StrEnum):
    """How a cache lookup was handled."""

    HIT_FRESH = "HIT_FRESH"
    HIT_AGING = "HIT_AGING"
    HIT_STALE = "HIT_STALE"
    MISS = "MISS"
    BYPASSED = "BYPASSED"


class FetchDisposition(StrEnum):
    """How a fetch result was obtained."""

    CACHE = "CACHE"
    PROVIDER = "PROVIDER"
    COALESCED = "COALESCED"
    REJECTED = "REJECTED"
    UNAVAILABLE = "UNAVAILABLE"


class ProviderGateState(StrEnum):
    """Current provider scheduling state."""

    READY = "READY"
    RATE_LIMITED = "RATE_LIMITED"
    COOLDOWN = "COOLDOWN"
    DISABLED = "DISABLED"


class RequestPriority(StrEnum):
    """Data-fetch priority; unrelated to trading or position priority."""

    BACKGROUND = "BACKGROUND"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RateLimitScope(StrEnum):
    """Identity over which a rate constraint is enforced."""

    PROVIDER = "PROVIDER"
    OPERATION = "OPERATION"
    REQUEST_KEY = "REQUEST_KEY"
