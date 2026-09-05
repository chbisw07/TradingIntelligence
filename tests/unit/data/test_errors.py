"""Tests for typed provider and data failures."""

from tiaf.data import (
    DataFailureKind,
    ProviderError,
    ProviderRateLimitError,
    TIAFDataError,
    UnsupportedCapabilityError,
)
from tiaf.data.enums import ProviderCapability


def test_provider_error_hierarchy_and_log_representation() -> None:
    error = ProviderRateLimitError(
        "Request quota exhausted",
        provider=" Provider A ",
        metadata={"request_group": "quotes"},
    )

    assert isinstance(error, ProviderError)
    assert isinstance(error, TIAFDataError)
    assert error.failure_kind is DataFailureKind.RATE_LIMIT
    assert error.retryable is True
    assert error.to_dict() == {
        "error_type": "ProviderRateLimitError",
        "provider": "provider a",
        "failure_kind": "RATE_LIMIT",
        "retryable": True,
        "detail": "Request quota exhausted",
        "metadata": {"request_group": "quotes"},
    }


def test_unsupported_capability_error_is_typed() -> None:
    error = UnsupportedCapabilityError(
        ProviderCapability.NEWS,
        provider="provider-a",
    )

    assert error.failure_kind is DataFailureKind.UNSUPPORTED
    assert error.retryable is False
    assert error.capability is ProviderCapability.NEWS
    assert error.to_dict()["metadata"] == {"capability": "NEWS"}
