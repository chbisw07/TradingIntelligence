"""One statically registered, pure BaseRate primitive; no I/O, clock or loader."""

import sys
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Annotated, Literal, Protocol, Self

import pydantic
from pydantic import Field, model_validator

from .capture import CapturedArtifact, capture_artifact
from .contracts import BinaryProbabilityOutput, ForecastAbsence, ForecastRequest
from .enums import ForecastRealizationMode, ForecastReason, ForecastStatus
from .errors import ForecastIntegrityError
from .identity import ArtifactReference, ForecastContract
from .support import AdmittedSupport, BaseRatePolicy


class ForecasterDescriptor(ForecastContract):
    schema_id: Literal["tiaf.ff.forecaster-descriptor"] = "tiaf.ff.forecaster-descriptor"
    forecaster_id: Literal["forecaster:historical-base-rate"] = "forecaster:historical-base-rate"
    implementation_version: Literal["1.0"] = "1.0"
    family: Literal["PRIMITIVE"] = "PRIMITIVE"
    target_id: Literal["equity.next_session_close.return_gt_zero"] = (
        "equity.next_session_close.return_gt_zero"
    )
    target_version: Literal["1.0"] = "1.0"
    realization_modes: tuple[ForecastRealizationMode, ...] = tuple(ForecastRealizationMode)
    required_evidence: Literal["PIT_QUALIFIED_TWENTY_TRANSITION_WITNESS"] = (
        "PIT_QUALIFIED_TWENTY_TRANSITION_WITNESS"
    )
    deterministic: Literal[True] = True
    replay: Literal["RECORDED_AND_EXACT_PINNED"] = "RECORDED_AND_EXACT_PINNED"
    optional_dependencies: tuple[str, ...] = ()
    max_attempts: Literal[1] = 1
    local_deadline_seconds: Literal[1] = 1
    code_ref: ArtifactReference
    configuration_ref: ArtifactReference


class GenerationPayload(ForecastContract):
    status: ForecastStatus
    output: Annotated[BinaryProbabilityOutput | ForecastAbsence, Field(discriminator="kind")]

    @model_validator(mode="after")
    def output_status(self) -> Self:
        if (self.status is ForecastStatus.GENERATED) != isinstance(
            self.output, BinaryProbabilityOutput
        ):
            raise ValueError("GENERATION_STATUS_OUTPUT_MISMATCH")
        return self


def implementation_artifacts() -> tuple[CapturedArtifact, ...]:
    """Reviewed code-owned declarations, not a source-file scan or executable payload."""
    code = capture_artifact(
        "code:historical-base-rate-1.0",
        {
            "implementation": "HistoricalBaseRateForecaster/1.0",
            "algorithm": "finite-python-int-ratio-k-over-n",
            "minimum": 20,
            "smoothing": False,
            "executable": False,
        },
    )
    policy = capture_artifact("policy:baserate-1.0", BaseRatePolicy())
    descriptor = capture_artifact(
        "descriptor:historical-base-rate-1.0",
        ForecasterDescriptor(
            code_ref=code.reference,
            configuration_ref=policy.reference,
        ),
    )
    return code, policy, descriptor


class Forecaster(Protocol):
    def descriptor(self) -> ForecasterDescriptor: ...

    def forecast(self, request: ForecastRequest, support: AdmittedSupport) -> GenerationPayload: ...


def dependency_artifact() -> CapturedArtifact:
    return capture_artifact(
        "dependencies:ff-runtime-1.0",
        {
            "python": ".".join(map(str, sys.version_info[:3])),
            "pydantic": pydantic.__version__,
            "numeric_policy": "finite-python-int-ratio-k-over-n/1.0",
            "serializer": "tiaf.ff.canonical-json/1.0",
        },
    )


@dataclass(frozen=True, slots=True)
class HistoricalBaseRateForecaster:
    def descriptor(self) -> ForecasterDescriptor:
        code, policy, _ = implementation_artifacts()
        return ForecasterDescriptor(code_ref=code.reference, configuration_ref=policy.reference)

    def forecast(self, request: ForecastRequest, support: AdmittedSupport) -> GenerationPayload:
        request = ForecastRequest.model_validate(request)
        support = AdmittedSupport.model_validate(support)
        if support.request_fingerprint != request.semantic_fingerprint:
            raise ForecastIntegrityError("ADMITTED_SUPPORT_REQUEST_MISMATCH")
        n, k = support.summary.qualified_count, support.summary.positive_count
        if n < 20:
            return GenerationPayload(
                status=ForecastStatus.UNAVAILABLE,
                output=ForecastAbsence(
                    reasons=(ForecastReason.HISTORY_SUPPORT_INSUFFICIENT,),
                ),
            )
        return GenerationPayload(
            status=ForecastStatus.GENERATED, output=BinaryProbabilityOutput(probability=k / n)
        )


_REGISTRY: Mapping[tuple[str, str], Forecaster] = MappingProxyType(
    {
        ("forecaster:historical-base-rate", "1.0"): HistoricalBaseRateForecaster(),
    }
)


def registered_forecasters() -> tuple[ForecasterDescriptor, ...]:
    return tuple(_REGISTRY[key].descriptor() for key in sorted(_REGISTRY))


def resolve_forecaster(forecaster_id: str, implementation_version: str) -> Forecaster:
    try:
        return _REGISTRY[forecaster_id, implementation_version]
    except KeyError:
        raise ForecastIntegrityError("FORECASTER_NOT_REGISTERED_EXACT_VERSION") from None
