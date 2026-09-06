"""Immutable models for cache, freshness, scheduling, and fetch results."""

import math
from typing import Annotated, Any, Self

from pydantic import BeforeValidator, Field, field_validator, model_validator

from tiaf.contracts import ContractModel, FreshnessState
from tiaf.contracts.common import Metadata, NonEmptyStr, TiafDateTime
from tiaf.data.normalization import normalize_provider_name
from tiaf.data.runtime.enums import (
    CacheDisposition,
    FetchDisposition,
    ProviderGateState,
    RateLimitScope,
)

NormalizedProvider = Annotated[str, BeforeValidator(normalize_provider_name)]

_SENSITIVE_PARAMETER_PARTS = (
    "api_key",
    "apikey",
    "authorization",
    "client_id",
    "credential",
    "password",
    "secret",
    "token",
)


def _normalize_identifier(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().casefold()
    return value


class CacheKey(ContractModel):
    """Deterministic identity of one factual data request."""

    namespace: Annotated[NonEmptyStr, BeforeValidator(_normalize_identifier)]
    provider: NormalizedProvider | None = None
    instrument_identity: NonEmptyStr | None = None
    operation: Annotated[NonEmptyStr, BeforeValidator(_normalize_identifier)]
    parameters: tuple[tuple[str, str], ...] = ()

    @field_validator("parameters", mode="before")
    @classmethod
    def canonicalize_parameters(cls, value: Any) -> Any:
        """Accept JSON/list pairs and establish canonical key/value ordering."""
        if value is None:
            return ()
        if isinstance(value, (str, bytes)):
            raise ValueError("parameters must contain name/value pairs")
        try:
            raw_parameters = tuple(value)
            if any(
                isinstance(parameter, (str, bytes)) or len(parameter) != 2
                for parameter in raw_parameters
            ):
                raise ValueError
            parameters = tuple(
                (str(parameter[0]).strip(), str(parameter[1]).strip())
                for parameter in raw_parameters
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("parameters must contain name/value pairs") from exc
        for name, _ in parameters:
            if not name:
                raise ValueError("cache parameter names must not be empty")
            normalized = name.casefold().replace("-", "_")
            if any(part in normalized for part in _SENSITIVE_PARAMETER_PARTS):
                raise ValueError(f"credentials are not permitted in cache keys: {name}")
        return tuple(sorted(parameters, key=lambda parameter: (parameter[0], parameter[1])))

    def __str__(self) -> str:
        """Return a credential-safe, deterministic representation for logs."""
        provider = self.provider or "*"
        instrument = self.instrument_identity or "*"
        parameters = "&".join(f"{name}={value}" for name, value in self.parameters)
        base = f"{self.namespace}:{provider}:{instrument}:{self.operation}"
        return f"{base}?{parameters}" if parameters else base


class CacheEntry[T](ContractModel):
    """One immutable cached value and its factual timestamps."""

    key: CacheKey
    value: T
    stored_at: TiafDateTime
    observed_at: TiafDateTime | None = None
    expires_at: TiafDateTime | None = None
    source_provider: NormalizedProvider | None = None
    metadata: Metadata = Field(default_factory=dict)
    generation: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_expiry(self) -> Self:
        if self.expires_at is not None and self.expires_at < self.stored_at:
            raise ValueError("expires_at must not be earlier than stored_at")
        return self


class FreshnessRequirement(ContractModel):
    """Caller-relative age bounds for accepting factual data."""

    fresh_for_seconds: float = Field(ge=0)
    aging_for_seconds: float | None = Field(default=None, ge=0)
    max_stale_seconds: float | None = Field(default=None, ge=0)
    allow_aging: bool = True
    allow_stale: bool = False
    use_stored_at_if_observed_missing: bool = False

    @model_validator(mode="after")
    def validate_threshold_order(self) -> Self:
        values = (
            self.fresh_for_seconds,
            self.aging_for_seconds,
            self.max_stale_seconds,
        )
        if any(value is not None and not math.isfinite(value) for value in values):
            raise ValueError("freshness thresholds must be finite")
        aging_boundary = self.aging_for_seconds or self.fresh_for_seconds
        if self.aging_for_seconds is not None:
            if self.aging_for_seconds < self.fresh_for_seconds:
                raise ValueError("aging_for_seconds must be at least fresh_for_seconds")
        if self.max_stale_seconds is not None:
            if self.max_stale_seconds < aging_boundary:
                raise ValueError("max_stale_seconds must be at least the aging boundary")
        return self


class FreshnessAssessment(ContractModel):
    """Deterministic classification with the timestamp used to derive it."""

    state: FreshnessState
    age_seconds: float | None = Field(default=None, ge=0)
    based_on: TiafDateTime | None = None
    used_stored_at: bool = False


class CacheStats(ContractModel):
    """Immutable cache metric snapshot."""

    entries: int = Field(ge=0)
    hits: int = Field(ge=0)
    misses: int = Field(ge=0)
    fresh_hits: int = Field(ge=0)
    aging_hits: int = Field(ge=0)
    stale_hits: int = Field(ge=0)
    puts: int = Field(ge=0)
    evictions: int = Field(ge=0)


class RuntimeStats(CacheStats):
    """Combined cache and coordinator metric snapshot."""

    fetches: int = Field(ge=0)
    coalesced_requests: int = Field(ge=0)
    provider_blocked: int = Field(ge=0)
    stale_fallbacks: int = Field(ge=0)


class RatePolicy(ContractModel):
    """One explicit minimum-spacing and/or rolling-window provider rule."""

    provider: NormalizedProvider
    operation: Annotated[NonEmptyStr, BeforeValidator(_normalize_identifier)]
    minimum_interval_seconds: float | None = Field(default=None, gt=0)
    max_requests: int | None = Field(default=None, gt=0)
    window_seconds: float | None = Field(default=None, gt=0)
    key_scope: RateLimitScope = RateLimitScope.OPERATION
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_rate_shape(self) -> Self:
        if (self.max_requests is None) != (self.window_seconds is None):
            raise ValueError("max_requests and window_seconds must be supplied together")
        if self.minimum_interval_seconds is None and self.max_requests is None:
            raise ValueError("a rate policy requires at least one constraint")
        return self


class ProviderGateDecision(ContractModel):
    """Explicit provider eligibility result; the scheduler never sleeps."""

    provider: NormalizedProvider
    operation: Annotated[NonEmptyStr, BeforeValidator(_normalize_identifier)]
    state: ProviderGateState
    allowed: bool
    retry_after_seconds: float | None = Field(default=None, ge=0)
    next_allowed_monotonic: float | None = Field(default=None, ge=0)
    reason: NonEmptyStr | None = None
    checked_at: TiafDateTime


class FetchResult[T](ContractModel):
    """Immutable result retaining acquisition path, age, and attribution."""

    value: T
    cache_key: CacheKey
    disposition: FetchDisposition
    freshness: FreshnessState
    age_seconds: float | None = Field(default=None, ge=0)
    fetched_at: TiafDateTime | None = None
    observed_at: TiafDateTime | None = None
    source_provider: NormalizedProvider | None = None
    stale_fallback_used: bool = False
    coalesced: bool = False
    metadata: Metadata = Field(default_factory=dict)


def cache_disposition_for(state: FreshnessState) -> CacheDisposition:
    """Map public freshness into the deliberately smaller cache taxonomy."""
    if state is FreshnessState.FRESH:
        return CacheDisposition.HIT_FRESH
    if state is FreshnessState.AGING:
        return CacheDisposition.HIT_AGING
    return CacheDisposition.HIT_STALE
