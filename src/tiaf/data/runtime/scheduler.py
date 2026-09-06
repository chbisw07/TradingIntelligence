"""Deterministic, non-sleeping in-process provider gate."""

import time
from collections import deque
from collections.abc import Callable
from datetime import datetime
from threading import RLock

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data.normalization import normalize_datetime_to_ist, normalize_provider_name
from tiaf.data.runtime.enums import ProviderGateState, RateLimitScope
from tiaf.data.runtime.models import ProviderGateDecision, RatePolicy
from tiaf.data.runtime.rate_policy import RatePolicyRegistry

type _HistoryKey = tuple[tuple[object, ...], str]


def _wall_now() -> datetime:
    return datetime.now(TIAF_TIMEZONE)


class ProviderScheduler:
    """Atomically reserves provider capacity and reports explicit blocks."""

    def __init__(
        self,
        policies: RatePolicyRegistry | None = None,
        *,
        monotonic_clock: Callable[[], float] = time.monotonic,
        wall_clock: Callable[[], datetime] = _wall_now,
    ) -> None:
        self._policies = policies or RatePolicyRegistry()
        self._monotonic_clock = monotonic_clock
        self._wall_clock = wall_clock
        self._lock = RLock()
        self._history: dict[_HistoryKey, deque[float]] = {}
        self._disabled: dict[str, str] = {}
        self._cooldowns: dict[str, tuple[float, str]] = {}
        self._last_success: dict[tuple[str, str], datetime] = {}
        self._last_failure: dict[tuple[str, str], tuple[datetime, str]] = {}

    @property
    def policies(self) -> RatePolicyRegistry:
        return self._policies

    def can_execute(
        self,
        provider: str,
        operation: str,
        request_key: str | None = None,
        *,
        now_monotonic: float | None = None,
    ) -> ProviderGateDecision:
        now = self._monotonic_clock() if now_monotonic is None else now_monotonic
        with self._lock:
            return self._decision(provider, operation, request_key, now)

    def reserve(
        self,
        provider: str,
        operation: str,
        request_key: str | None = None,
        *,
        now_monotonic: float | None = None,
    ) -> ProviderGateDecision:
        """Check and reserve all applicable constraints as one atomic action."""
        now = self._monotonic_clock() if now_monotonic is None else now_monotonic
        with self._lock:
            decision = self._decision(provider, operation, request_key, now)
            if not decision.allowed:
                return decision
            for policy in self._policies.policies_for(provider, operation):
                history = self._history.setdefault(
                    self._history_key(policy, operation, request_key), deque()
                )
                self._prune(history, policy, now)
                history.append(now)
                if policy.window_seconds is None:
                    while len(history) > 1:
                        history.popleft()
            return decision

    def next_allowed_at(
        self,
        provider: str,
        operation: str,
        request_key: str | None = None,
        *,
        now_monotonic: float | None = None,
    ) -> float | None:
        return self.can_execute(
            provider,
            operation,
            request_key,
            now_monotonic=now_monotonic,
        ).next_allowed_monotonic

    def record_success(
        self, provider: str, operation: str, *, at: datetime | None = None
    ) -> None:
        timestamp = normalize_datetime_to_ist(at or self._wall_clock())
        key = (normalize_provider_name(provider), operation.strip().casefold())
        with self._lock:
            self._last_success[key] = timestamp

    def record_rate_limit(
        self,
        provider: str,
        retry_after_seconds: float,
        reason: str = "provider reported a rate limit",
        *,
        now_monotonic: float | None = None,
    ) -> None:
        if retry_after_seconds < 0:
            raise ValueError("retry_after_seconds must be non-negative")
        normalized_reason = reason.strip()
        if not normalized_reason:
            raise ValueError("rate-limit reason must not be empty")
        now = self._monotonic_clock() if now_monotonic is None else now_monotonic
        normalized = normalize_provider_name(provider)
        with self._lock:
            self._cooldowns[normalized] = (now + retry_after_seconds, normalized_reason)

    def record_failure(
        self,
        provider: str,
        operation: str,
        reason: str,
        *,
        at: datetime | None = None,
    ) -> None:
        timestamp = normalize_datetime_to_ist(at or self._wall_clock())
        key = (normalize_provider_name(provider), operation.strip().casefold())
        with self._lock:
            self._last_failure[key] = (timestamp, reason)

    def disable_provider(self, provider: str, reason: str) -> None:
        normalized_reason = reason.strip()
        if not normalized_reason:
            raise ValueError("disable reason must not be empty")
        with self._lock:
            self._disabled[normalize_provider_name(provider)] = normalized_reason

    def enable_provider(self, provider: str) -> None:
        with self._lock:
            self._disabled.pop(normalize_provider_name(provider), None)

    def _decision(
        self,
        provider: str,
        operation: str,
        request_key: str | None,
        now: float,
    ) -> ProviderGateDecision:
        normalized_provider = normalize_provider_name(provider)
        normalized_operation = operation.strip().casefold()
        checked_at = normalize_datetime_to_ist(self._wall_clock())
        disabled_reason = self._disabled.get(normalized_provider)
        if disabled_reason is not None:
            return ProviderGateDecision(
                provider=normalized_provider,
                operation=normalized_operation,
                state=ProviderGateState.DISABLED,
                allowed=False,
                reason=disabled_reason,
                checked_at=checked_at,
            )

        cooldown = self._cooldowns.get(normalized_provider)
        if cooldown is not None:
            until, reason = cooldown
            if now < until:
                return ProviderGateDecision(
                    provider=normalized_provider,
                    operation=normalized_operation,
                    state=ProviderGateState.COOLDOWN,
                    allowed=False,
                    retry_after_seconds=until - now,
                    next_allowed_monotonic=until,
                    reason=reason,
                    checked_at=checked_at,
                )
            del self._cooldowns[normalized_provider]

        next_times: list[float] = []
        for policy in self._policies.policies_for(normalized_provider, normalized_operation):
            history = self._history.setdefault(
                self._history_key(policy, normalized_operation, request_key), deque()
            )
            self._prune(history, policy, now)
            if policy.minimum_interval_seconds is not None and history:
                next_times.append(history[-1] + policy.minimum_interval_seconds)
            if (
                policy.max_requests is not None
                and policy.window_seconds is not None
                and len(history) >= policy.max_requests
            ):
                next_times.append(history[-policy.max_requests] + policy.window_seconds)

        blocked_until = max((value for value in next_times if value > now), default=None)
        if blocked_until is not None:
            return ProviderGateDecision(
                provider=normalized_provider,
                operation=normalized_operation,
                state=ProviderGateState.RATE_LIMITED,
                allowed=False,
                retry_after_seconds=blocked_until - now,
                next_allowed_monotonic=blocked_until,
                reason="configured provider rate policy",
                checked_at=checked_at,
            )
        return ProviderGateDecision(
            provider=normalized_provider,
            operation=normalized_operation,
            state=ProviderGateState.READY,
            allowed=True,
            next_allowed_monotonic=now,
            checked_at=checked_at,
        )

    @staticmethod
    def _policy_identity(policy: RatePolicy) -> tuple[object, ...]:
        return (
            policy.provider,
            policy.operation,
            policy.minimum_interval_seconds,
            policy.max_requests,
            policy.window_seconds,
            policy.key_scope,
        )

    def _history_key(
        self,
        policy: RatePolicy,
        operation: str,
        request_key: str | None,
    ) -> _HistoryKey:
        if policy.key_scope is RateLimitScope.PROVIDER:
            scope = policy.provider
        elif policy.key_scope is RateLimitScope.OPERATION:
            scope = f"{policy.provider}:{operation.strip().casefold()}"
        else:
            if request_key is None:
                raise ValueError("request_key is required for REQUEST_KEY rate policies")
            scope = f"{policy.provider}:{operation.strip().casefold()}:{request_key}"
        return self._policy_identity(policy), scope

    @staticmethod
    def _prune(history: deque[float], policy: RatePolicy, now: float) -> None:
        if policy.window_seconds is not None:
            boundary = now - policy.window_seconds
            while history and history[0] <= boundary:
                history.popleft()
