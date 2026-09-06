"""Provider-neutral rate policy registry."""

from threading import RLock

from tiaf.data.normalization import normalize_provider_name
from tiaf.data.runtime.models import RatePolicy


class RatePolicyRegistry:
    """Thread-safe explicit policy collection keyed by provider and operation."""

    def __init__(self, policies: tuple[RatePolicy, ...] = ()) -> None:
        self._lock = RLock()
        self._policies = list(policies)

    def register(self, policy: RatePolicy) -> None:
        with self._lock:
            self._policies.append(policy)

    def policies_for(self, provider: str, operation: str) -> tuple[RatePolicy, ...]:
        normalized_provider = normalize_provider_name(provider)
        normalized_operation = operation.strip().casefold()
        with self._lock:
            return tuple(
                policy
                for policy in self._policies
                if policy.provider == normalized_provider
                and policy.operation in {normalized_operation, "*"}
            )

    def all(self) -> tuple[RatePolicy, ...]:
        with self._lock:
            return tuple(self._policies)
