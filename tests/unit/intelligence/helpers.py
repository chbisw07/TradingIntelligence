"""Test-only services and synthetic contract builders; never acquire or fit data."""

from datetime import datetime, timedelta
from typing import Any

from pydantic import ValidationError

from tiaf.agents.models import ReasoningModelIdentity
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.enums import ForecastRealizationMode
from tiaf.forecasting.identity import ArtifactReference, ForecastContract, canonical_json
from tiaf.forecasting.identity import semantic_fingerprint as fingerprint
from tiaf.forecasting.inference_contracts import ForecasterKey
from tiaf.service.intelligence import (
    AbsoluteMaturity,
    BinaryValue,
    CapabilityDeclaration,
    CapabilityKind,
    ClaimKind,
    DeploymentMetadata,
    EvaluableClaim,
    IntelligenceRequest,
    IntelligenceResponse,
    IntelligenceServiceError,
    ProducerIdentity,
    ProducerType,
    ResolutionContract,
    ResponseProvenance,
    ServiceDescriptor,
    ServiceErrorCode,
    ServiceHealth,
    ServiceIdentity,
    validate_request,
    validate_response,
)

AT = datetime(2030, 1, 2, 10, tzinfo=TIAF_TIMEZONE)


def change[T: ForecastContract](value: T, /, **updates: Any) -> T:
    return type(value).model_validate({**value.model_dump(), **updates})


def ref(name: str) -> ArtifactReference:
    return ArtifactReference(
        artifact_id=f"synthetic:{name}", artifact_version="1.0", fingerprint=fingerprint(name)
    )


def producer(name: str = "forecast", *, llm: bool = False) -> ProducerIdentity:
    return ProducerIdentity(
        producer_id=f"synthetic:{name}",
        producer_type=ProducerType.LLM if llm else ProducerType.FORECASTER,
        service=ServiceIdentity(service_id=f"service:{name}", service_version="2.0"),
        configuration_version="3.0",
        capability=CapabilityDeclaration(
            capability_id=f"capability:{name}",
            capability_version="4.0",
            kind=CapabilityKind.SYNTHESIS if llm else CapabilityKind.FORECAST,
            claim_kinds=tuple(ClaimKind),
        ),
        model=None
        if llm
        else ForecasterKey(forecaster_id=f"model:{name}", implementation_version="5.0"),
        llm=ReasoningModelIdentity(
            provider_id="synthetic-provider",
            model_id="synthetic-model",
            model_version=None,
            configuration_id="synthetic-config",
        )
        if llm
        else None,
        prompt_version="6.0" if llm else None,
        tool_config_version="7.0" if llm else None,
        orchestration_version="8.0" if llm else None,
    )


def resolution(kind: ClaimKind = ClaimKind.BINARY) -> ResolutionContract:
    return ResolutionContract(
        resolution_id="resolution:synthetic",
        claim_kind=kind,
        target=ref("target"),
        target_semantics="Synthetic terminal value strictly above reference",
        resolver=ref("resolver"),
        subject="synthetic:asset",
        reference_at=AT,
        reference_evidence=(ref("reference"),),
        maturity=AbsoluteMaturity(at=AT + timedelta(days=1)),
        mode="ENDPOINT",
    )


def claim(owner: ProducerIdentity | None = None) -> EvaluableClaim:
    return EvaluableClaim(
        claim_id="claim:primary",
        request_id="query:synthetic",
        producer=owner or producer(),
        information_cutoff=AT,
        as_of=AT,
        created_at=AT,
        realization=ForecastRealizationMode.ACTUAL_ISSUANCE,
        value=BinaryValue(probability=0.0),
        resolution=resolution(),
    )


def request(owner: ProducerIdentity | None = None) -> IntelligenceRequest:
    owner = owner or producer()
    return IntelligenceRequest(
        request_id="query:synthetic",
        service=owner.service,
        capability=owner.capability,
        expected_producer=owner,
        information_cutoff=AT,
        as_of=AT,
        created_at=AT,
        realization=ForecastRealizationMode.ACTUAL_ISSUANCE,
        style="EVALUABLE",
        resolution=resolution(),
        inputs=(ref("input"),),
    )


def response(owner: ProducerIdentity | None = None) -> IntelligenceResponse:
    owner = owner or producer()
    return IntelligenceResponse(
        response_id="response:synthetic",
        request_id="query:synthetic",
        producer=owner,
        created_at=AT,
        style="EVALUABLE",
        primary_claim=claim(owner),
        provenance=ResponseProvenance(native_output=ref("native")),
    )


class SyntheticLocal:
    def __init__(
        self, owner: ProducerIdentity | None = None, *, failure: ServiceErrorCode | None = None
    ) -> None:
        self.owner = owner or producer()
        self.failure = failure

    def describe(self) -> ServiceDescriptor:
        return ServiceDescriptor(
            service=self.owner.service,
            capabilities=(self.owner.capability,),
            producers=(self.owner,),
        )

    def health(self) -> ServiceHealth:
        return ServiceHealth(service=self.owner.service, observed_at=AT, status="READY")

    def deployment(self) -> DeploymentMetadata:
        return DeploymentMetadata(transport="LOCAL", deployment_id="deploy:local", elapsed_ms=0)

    def analyze(self, admitted: IntelligenceRequest) -> IntelligenceResponse:
        validate_request(admitted, self.describe())
        if self.failure is not None:
            raise IntelligenceServiceError(self.failure)
        return validate_response(admitted, response(self.owner), self.describe())


class SyntheticRemote(SyntheticLocal):
    """In-memory wire round trip, NOT a network implementation."""

    def deployment(self) -> DeploymentMetadata:
        return DeploymentMetadata(transport="REMOTE", deployment_id="deploy:remote", elapsed_ms=7)

    def encode_request(self, admitted: IntelligenceRequest) -> str:
        validate_request(admitted, self.describe())
        return canonical_json(admitted)

    def decode_response(self, payload: str, admitted: IntelligenceRequest) -> IntelligenceResponse:
        try:
            result = IntelligenceResponse.model_validate_json(payload)
        except ValidationError as exc:
            raise IntelligenceServiceError(ServiceErrorCode.INVALID_RESPONSE) from exc
        return validate_response(admitted, result, self.describe())

    def analyze(self, admitted: IntelligenceRequest) -> IntelligenceResponse:
        decoded = IntelligenceRequest.model_validate_json(self.encode_request(admitted))
        result = super().analyze(decoded)
        return self.decode_response(canonical_json(result), admitted)
