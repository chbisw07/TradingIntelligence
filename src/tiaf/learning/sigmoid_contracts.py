"""FF-2.2 additive, family-neutral calibration codecs; no empirical authority."""

from typing import Literal, Self

from pydantic import Field, StrictInt, model_validator

from tiaf.forecasting.contracts import BinaryProbabilityOutput, ForecastEdge
from tiaf.forecasting.identity import ArtifactReference, ForecastDateTime, semantic_fingerprint
from tiaf.forecasting.inference_contracts import ForecasterCapability, ForecasterKey
from tiaf.forecasting.lifecycle_provenance import NeutralInferenceCapture

from .calibration_contracts import CalibrationComponent, Probability
from .forecast_artifacts import Finite, SealedResearch
from .forecaster_training import TrainingBundle, reference

VERSION = "ff2.synthetic.sigmoid.1"


class CalibrationSample(SealedResearch):
    probabilities: tuple[Probability, ...] = Field(min_length=2, max_length=4096)
    labels: tuple[StrictInt, ...] = Field(min_length=2, max_length=4096)

    @model_validator(mode="after")
    def dimensions(self) -> Self:
        if len(self.probabilities) != len(self.labels) or not set(self.labels) <= {0, 1}:
            raise ValueError("CALIBRATION_BINARY_LABELS_AND_SHAPE_REQUIRED")
        return self


def synthetic_sample() -> CalibrationSample:
    """Compiled authoring recipe, not a caller-asserted synthetic provenance flag."""
    return CalibrationSample(
        probabilities=tuple(p for p in (0.1, 0.2, 0.4, 0.6, 0.8, 0.9) for _ in range(10)),
        labels=tuple(int(i < positives) for positives in (2, 3, 4, 6, 7, 8) for i in range(10)),
    )


class SigmoidParameters(SealedResearch):
    adapter_version: Literal["ff2.synthetic.sigmoid.1"] = "ff2.synthetic.sigmoid.1"
    intercept: Finite
    slope: Finite = Field(gt=0)
    transform: Literal["SIGMOID_INTERCEPT_PLUS_SLOPE_LOGIT_CLAMPED_P"] = (
        "SIGMOID_INTERCEPT_PLUS_SLOPE_LOGIT_CLAMPED_P"
    )
    epsilon: Finite = Field(default=1e-15, ge=1e-15, le=1e-15)


class SigmoidArtifact(SealedResearch):
    component: CalibrationComponent
    parameters: SigmoidParameters
    feature_schema: ArtifactReference
    source_training: ArtifactReference
    fit_request: ArtifactReference
    fit_grant: ArtifactReference
    fit_attempt: ArtifactReference
    sample: ArtifactReference
    fitted_at: ForecastDateTime
    scope: Literal["COMPILED_SYNTHETIC_ONLY"] = "COMPILED_SYNTHETIC_ONLY"
    qualified: Literal[False] = False

    @model_validator(mode="after")
    def binding(self) -> Self:
        if (
            self.component.implementation_version != VERSION
            or self.component.family != "calibration:sigmoid-logit"
            or self.component.configuration_fingerprint
            != semantic_fingerprint(
                (VERSION, "a=0;b=1;unweighted;no-penalty;newton-armijo-32;tol=1e-8;max=1000")
            )
            or self.component.created_at > self.fitted_at
        ):
            raise ValueError("SIGMOID_COMPONENT_BINDING")
        return self


class CalibratedCandidate(SealedResearch):
    """Versioned extension of FLC-5 composition, not a new common inference family."""

    profile: Literal["ff2.synthetic.calibrated-wrapper.1"] = "ff2.synthetic.calibrated-wrapper.1"
    experiment_id: Literal["experiment:ff2-synthetic-engineering-001"] = (
        "experiment:ff2-synthetic-engineering-001"
    )
    artifact: SigmoidArtifact
    source_composition: ArtifactReference
    edge: ForecastEdge
    approval: Literal["NOT_GRANTED"] = "NOT_GRANTED"
    activation: Literal[False] = False

    @model_validator(mode="after")
    def endpoints(self) -> Self:
        if self.edge != ForecastEdge(
            source_node_id=self.artifact.component.source_forecaster.forecaster_id,
            target_node_id="forecaster:ff2-synthetic-calibrated",
        ):
            raise ValueError("CALIBRATED_EDGE_MISMATCH")
        return self

    @property
    def candidate_id(self) -> str:
        return f"candidate:ff2-synthetic:{self.fingerprint}"

    @property
    def key(self) -> ForecasterKey:
        return ForecasterKey(
            forecaster_id=self.candidate_id, implementation_version="ff2.calibrated-wrapper.1"
        )


class CalibratedCapture(SealedResearch):
    candidate: CalibratedCandidate
    source: NeutralInferenceCapture
    fit: TrainingBundle
    raw_probability: Probability
    calibrated_probability: Probability
    created_at: ForecastDateTime
    lineage: tuple[ArtifactReference, ...] = Field(min_length=3, max_length=3)
    output_semantics: Literal["TRANSFORMED_NOT_QUALIFIED"] = "TRANSFORMED_NOT_QUALIFIED"
    grants_activation: Literal[False] = False

    @model_validator(mode="after")
    def closure(self) -> Self:
        raw, artifact = self.source.result, self.candidate.artifact
        component = artifact.component
        if not isinstance(raw.output, BinaryProbabilityOutput):
            raise ValueError("CALIBRATION_SOURCE_ABSENT")
        if (
            self.raw_probability != raw.output.probability
            or not raw.descriptor.supports(ForecasterCapability.CALIBRATION_COMPATIBLE)
            or raw.request.key != component.source_forecaster
            or raw.artifacts.model != component.source_model
            or raw.artifacts.scaler != component.source_preprocessor
            or raw.artifacts.training != artifact.source_training
            or raw.request.feature_schema != artifact.feature_schema
            or raw.request.target_id != component.target.target_id
            or raw.request.mode != component.mode
            or raw.artifacts.composition != self.candidate.source_composition
            or self.fit.result.status != "TRAINED"
            or self.fit.result.model_identity is None
            or self.fit.result.model_identity.artifact != reference("sigmoidartifact", artifact)
            or artifact.fit_request != reference("request", self.fit.request)
            or self.fit.execution.native_job_reference != reference("sigmoidartifact", artifact)
            or self.fit.result.model_identity.execution_reference
            != reference("execution", self.fit.execution)
            or self.fit.result.model_identity.request_reference != artifact.fit_request
            or self.fit.request.configuration_fingerprint != component.configuration_fingerprint
            or self.fit.request.feature_schema_fingerprint != artifact.feature_schema.fingerprint
            or self.fit.request.target_id != component.target.target_id
            or self.fit.request.subject != raw.request.subject
            or self.fit.request.experiment.experiment_id != self.candidate.experiment_id
            or self.fit.request.experiment.forecaster.forecaster_id != component.calibrator_id
            or self.fit.request.experiment.forecaster.implementation_version
            != component.implementation_version
            or self.fit.execution.completed_at != artifact.fitted_at
            or not artifact.fitted_at <= raw.request.computed_at <= self.created_at
            or self.lineage
            != (
                reference("sigmoidcandidate", self.candidate),
                reference("neutralinfercapture", self.source),
                reference("bundle", self.fit),
            )
        ):
            raise ValueError("CALIBRATED_CAPTURE_LINEAGE_MISMATCH")
        return self
