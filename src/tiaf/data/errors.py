"""Typed, provider-neutral market-data failures."""

from typing import Any, ClassVar

from tiaf.data.enums import DataFailureKind, ProviderCapability
from tiaf.data.normalization import normalize_provider_name


class TIAFDataError(Exception):
    """Base error carrying stable failure metadata for logging and handling."""

    default_failure_kind: ClassVar[DataFailureKind] = DataFailureKind.UNKNOWN
    default_retryable: ClassVar[bool] = False

    def __init__(
        self,
        detail: str,
        *,
        provider: str | None = None,
        failure_kind: DataFailureKind | None = None,
        retryable: bool | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        normalized_detail = detail.strip()
        if not normalized_detail:
            raise ValueError("error detail must not be empty")
        super().__init__(normalized_detail)
        self.provider = normalize_provider_name(provider) if provider is not None else None
        self.failure_kind = failure_kind or self.default_failure_kind
        self.retryable = self.default_retryable if retryable is None else retryable
        self.detail = normalized_detail
        self.metadata = dict(metadata or {})

    def to_dict(self) -> dict[str, Any]:
        """Return a stable log-friendly representation."""
        return {
            "error_type": type(self).__name__,
            "provider": self.provider,
            "failure_kind": self.failure_kind.value,
            "retryable": self.retryable,
            "detail": self.detail,
            "metadata": self.metadata,
        }


class ProviderError(TIAFDataError):
    """Base class for failures attributable to a data provider."""


class ProviderAuthError(ProviderError):
    """Provider authentication or authorization failed."""

    default_failure_kind = DataFailureKind.AUTH


class ProviderRateLimitError(ProviderError):
    """Provider rate limit prevented the request."""

    default_failure_kind = DataFailureKind.RATE_LIMIT
    default_retryable = True


class ProviderTimeoutError(ProviderError):
    """Provider request exceeded its time budget."""

    default_failure_kind = DataFailureKind.TIMEOUT
    default_retryable = True


class ProviderNetworkError(ProviderError):
    """Provider could not be reached reliably."""

    default_failure_kind = DataFailureKind.NETWORK
    default_retryable = True


class ProviderBadResponseError(ProviderError):
    """Provider response could not be normalized or validated."""

    default_failure_kind = DataFailureKind.BAD_RESPONSE


class InstrumentNotFoundError(ProviderError):
    """Requested instrument could not be resolved by the provider."""

    default_failure_kind = DataFailureKind.NOT_FOUND


class UnsupportedCapabilityError(ProviderError):
    """Provider does not advertise the requested capability."""

    default_failure_kind = DataFailureKind.UNSUPPORTED

    def __init__(
        self,
        capability: ProviderCapability,
        *,
        provider: str | None = None,
        detail: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        error_metadata = dict(metadata or {})
        error_metadata["capability"] = capability.value
        super().__init__(
            detail or f"provider does not support {capability.value}",
            provider=provider,
            metadata=error_metadata,
        )
        self.capability = capability


class StaleDataError(ProviderError):
    """Provider data exceeded a caller-defined freshness policy."""

    default_failure_kind = DataFailureKind.STALE
    default_retryable = True


class PartialDataError(ProviderError):
    """Provider returned an incomplete result that cannot satisfy the request."""

    default_failure_kind = DataFailureKind.PARTIAL
