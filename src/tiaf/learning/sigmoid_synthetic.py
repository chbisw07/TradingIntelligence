"""Compiled FF-2.2 source adapter: authored Logistic coefficients, never a base fit."""

from dataclasses import dataclass
from typing import Literal

from pydantic import Field

from tiaf.forecasting.contracts import BinaryProbabilityOutput
from tiaf.forecasting.enums import ForecastRealizationMode, ForecastStatus
from tiaf.forecasting.identity import ArtifactReference, ForecastDateTime, semantic_fingerprint
from tiaf.forecasting.inference_contracts import (
    ForecasterCapability,
    ForecasterKey,
    ForecasterLifecycle,
    ForecasterRole,
    InferenceDescriptor,
    InferenceProvenance,
    LifecycleIdentity,
    NeutralInferenceRequest,
    NeutralInferenceResult,
    run_inference,
)
from tiaf.forecasting.lifecycle_provenance import NeutralInferenceCapture

from .forecast_artifacts import Finite, SealedResearch
from .forecaster_training import reference
from .sigmoid_math import logit, sigmoid

SOURCE_KEY = ForecasterKey(
    forecaster_id="forecaster:ff2-synthetic-logistic",
    implementation_version="ff2.synthetic.source.1",
)
TARGET = "synthetic:next-step-direction"


def pin(name: str) -> ArtifactReference:
    return ArtifactReference(
        artifact_id="ff2-synthetic:" + name,
        artifact_version="1.0",
        fingerprint=semantic_fingerprint(("FF2_COMPILED_SYNTHETIC_V1", name)),
    )


class SyntheticLogisticModel(SealedResearch):
    """An authored one-feature Logistic reference, NOT any FF-1 learned artifact."""

    intercept: Finite = Field(default=0.0, ge=0.0, le=0.0)
    coefficient: Finite = Field(default=1.0, ge=1.0, le=1.0)
    feature_definition: Literal["LOGIT_OF_AUTHORED_GRID"] = "LOGIT_OF_AUTHORED_GRID"
    origin: Literal["AUTHORED_NOT_TRAINED"] = "AUTHORED_NOT_TRAINED"


class SyntheticCalibrationInput(SealedResearch):
    recipe: Literal["ff2.synthetic.source-grid.1"] = "ff2.synthetic.source-grid.1"
    index: int = Field(ge=0, lt=120, strict=True)
    at: ForecastDateTime

    @property
    def value(self) -> float:
        return logit((0.1, 0.2, 0.4, 0.6, 0.8, 0.9)[self.index % 6])


@dataclass(frozen=True)
class SyntheticLogisticAdapter:
    native: SyntheticCalibrationInput

    def descriptor(self) -> InferenceDescriptor:
        return InferenceDescriptor(
            identity=LifecycleIdentity(
                key=SOURCE_KEY,
                family="LOGISTIC_REGRESSION",
                role=ForecasterRole.CHALLENGER,
                lifecycle=ForecasterLifecycle.EXPERIMENTAL,
            ),
            capabilities=(
                ForecasterCapability.INFERENCE,
                ForecasterCapability.ARTIFACT_BACKED,
                ForecasterCapability.CALIBRATION_COMPATIBLE,
                ForecasterCapability.REPLAYABLE,
            ),
            modes=(ForecastRealizationMode.SIMULATED_ISSUANCE,),
        )

    def request(self) -> NeutralInferenceRequest:
        native = SyntheticCalibrationInput.model_validate(self.native)
        return NeutralInferenceRequest(
            key=SOURCE_KEY,
            observation_id=f"synthetic:ff2-observation-{native.index}",
            target_id=TARGET,
            subject="synthetic:asset",
            mode=ForecastRealizationMode.SIMULATED_ISSUANCE,
            information_cutoff=native.at,
            as_of=native.at,
            computed_at=native.at,
            context_ref=reference("sigmoidinput", native),
            input_ref=reference("sigmoidinput", native),
            feature_schema=pin("schema"),
            experiment=pin("source-experiment"),
        )

    def forecast(self, request: NeutralInferenceRequest) -> NeutralInferenceResult:
        if request != self.request():
            raise ValueError("SYNTHETIC_SOURCE_REQUEST_MISMATCH")
        model = SyntheticLogisticModel()
        return NeutralInferenceResult(
            request=request,
            descriptor=self.descriptor(),
            status=ForecastStatus.GENERATED,
            output=BinaryProbabilityOutput(
                probability=sigmoid(model.intercept + model.coefficient * self.native.value)
            ),
            artifacts=InferenceProvenance(
                context=request.context_ref,
                composition=pin("source-composition"),
                model=reference("sigmoidmodel", model),
                training=pin("authored-no-base-fit"),
            ),
        )


def synthetic_source(native: SyntheticCalibrationInput) -> NeutralInferenceCapture:
    adapter = SyntheticLogisticAdapter(SyntheticCalibrationInput.model_validate(native))
    return NeutralInferenceCapture(result=run_inference(adapter.request(), adapter))
