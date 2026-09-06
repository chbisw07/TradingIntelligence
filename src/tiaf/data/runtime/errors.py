"""Typed runtime-layer errors."""

from tiaf.data.normalization import normalize_provider_name
from tiaf.data.runtime.enums import ProviderGateState


class DataRuntimeError(Exception):
    """Base error for cache and provider scheduling failures."""


class ProviderScheduleBlockedError(DataRuntimeError):
    """Raised when a provider call is not currently eligible."""

    def __init__(
        self,
        provider: str,
        operation: str,
        retry_after_seconds: float | None,
        reason: str,
        gate_state: ProviderGateState,
    ) -> None:
        self.provider = normalize_provider_name(provider)
        self.operation = operation.strip().casefold()
        self.retry_after_seconds = retry_after_seconds
        self.reason = reason
        self.gate_state = gate_state
        retry = "unknown" if retry_after_seconds is None else f"{retry_after_seconds:.6f}s"
        super().__init__(
            f"provider {self.provider!r} operation {self.operation!r} is "
            f"{gate_state}: {reason}; retry after {retry}"
        )
