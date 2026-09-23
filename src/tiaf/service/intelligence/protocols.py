"""Logical adapter interfaces and pure contract checks. No transport or orchestration."""

from enum import StrEnum
from typing import Literal, Protocol, Self, runtime_checkable

from pydantic import Field, ValidationError, model_validator

from tiaf.forecasting.identity import ForecastDateTime, LogicalId

from .common import IntelligenceContract, unique
from .envelopes import IntelligenceRequest, IntelligenceResponse
from .identity import CapabilityDeclaration, ProducerIdentity, ServiceIdentity


class ServiceErrorCode(StrEnum):
    UNAVAILABLE = "UNAVAILABLE"
    TIMEOUT = "TIMEOUT"
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    VERSION_MISMATCH = "VERSION_MISMATCH"
    PROVENANCE_MISMATCH = "PROVENANCE_MISMATCH"
    UNSUPPORTED_CAPABILITY = "UNSUPPORTED_CAPABILITY"


class ServiceFailure(IntelligenceContract):
    code: ServiceErrorCode
    request_id: LogicalId
    service: ServiceIdentity


class IntelligenceServiceError(ValueError):
    def __init__(self, code: ServiceErrorCode) -> None:
        self.code = code
        super().__init__(code.value)


class ServiceDescriptor(IntelligenceContract):
    service: ServiceIdentity
    capabilities: tuple[CapabilityDeclaration, ...] = Field(min_length=1, max_length=32)
    producers: tuple[ProducerIdentity, ...] = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def bindings(self) -> Self:
        unique(tuple(c.capability_id for c in self.capabilities), "CAPABILITY")
        unique(tuple(p.producer_id for p in self.producers), "PRODUCER")
        if any(
            p.service != self.service or p.capability not in self.capabilities
            for p in self.producers
        ):
            raise ValueError("DESCRIPTOR_PRODUCER_BINDING_MISMATCH")
        return self


class ServiceHealth(IntelligenceContract):
    service: ServiceIdentity
    observed_at: ForecastDateTime
    status: Literal["READY", "UNAVAILABLE", "UNKNOWN"]


class DeploymentMetadata(IntelligenceContract):
    """Operational reference, deliberately outside semantic identity/fingerprint."""

    transport: Literal["LOCAL", "REMOTE"]
    deployment_id: LogicalId
    elapsed_ms: float = Field(ge=0, allow_inf_nan=False)


@runtime_checkable
class IntelligenceService(Protocol):
    def describe(self) -> ServiceDescriptor: ...

    def analyze(self, request: IntelligenceRequest) -> IntelligenceResponse: ...

    def health(self) -> ServiceHealth: ...


@runtime_checkable
class LocalAdapter(IntelligenceService, Protocol):
    """In-process implementation of the same logical contract; no auto-wrapper."""

    def deployment(self) -> DeploymentMetadata: ...


@runtime_checkable
class RemoteAdapter(IntelligenceService, Protocol):
    """Future wire boundary; failures use IntelligenceServiceError/ServiceFailure.

    Implementations must validate decoded output against the admitted request.
    No endpoint, HTTP/gRPC, retries, authentication or network implementation here.
    """

    def deployment(self) -> DeploymentMetadata: ...

    def encode_request(self, request: IntelligenceRequest) -> str: ...

    def decode_response(
        self, payload: str, request: IntelligenceRequest
    ) -> IntelligenceResponse: ...


def validate_request(request: IntelligenceRequest, descriptor: ServiceDescriptor) -> None:
    """Pure semantic admission, not a caller authorization or capability grant."""
    try:
        request = IntelligenceRequest.model_validate(request.model_dump())
        descriptor = ServiceDescriptor.model_validate(descriptor.model_dump())
    except ValidationError as exc:
        raise IntelligenceServiceError(ServiceErrorCode.INVALID_REQUEST) from exc
    if request.service != descriptor.service:
        raise IntelligenceServiceError(ServiceErrorCode.VERSION_MISMATCH)
    if request.capability not in descriptor.capabilities:
        raise IntelligenceServiceError(ServiceErrorCode.UNSUPPORTED_CAPABILITY)
    if request.expected_producer not in descriptor.producers:
        raise IntelligenceServiceError(ServiceErrorCode.PROVENANCE_MISMATCH)


def validate_response(
    request: IntelligenceRequest, response: IntelligenceResponse, descriptor: ServiceDescriptor
) -> IntelligenceResponse:
    """Defensive reconstruction and exact binding, even for model_copy/construct callers."""
    validate_request(request, descriptor)
    try:
        response = IntelligenceResponse.model_validate(response.model_dump())
    except ValidationError as exc:
        raise IntelligenceServiceError(ServiceErrorCode.INVALID_RESPONSE) from exc
    if response.producer.service != request.service:
        raise IntelligenceServiceError(ServiceErrorCode.VERSION_MISMATCH)
    if response.producer != request.expected_producer:
        raise IntelligenceServiceError(ServiceErrorCode.PROVENANCE_MISMATCH)
    if (
        response.request_id != request.request_id
        or response.style != request.style
        or response.created_at < request.created_at
    ):
        raise IntelligenceServiceError(ServiceErrorCode.INVALID_RESPONSE)
    claim = response.primary_claim
    if claim is not None and (
        claim.resolution != request.resolution
        or claim.as_of != request.as_of
        or claim.information_cutoff != request.information_cutoff
        or claim.realization != request.realization
    ):
        raise IntelligenceServiceError(ServiceErrorCode.INVALID_RESPONSE)
    return response
