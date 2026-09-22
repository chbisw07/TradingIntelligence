"""Pure, explicitly bound legacy adapters. No fit, source lookup, store or clock."""

from dataclasses import dataclass
from typing import Self

from pydantic import model_validator

from tiaf.learning.forecast_jobs import TrainingRun

from .capture import strict_json
from .contracts import ForecastComposition, ForecastRequest
from .errors import ForecastIntegrityError
from .forecaster_seams import (
    ForecasterArtifacts,
    ForecasterKey,
    InferenceDescriptor,
    InferenceForecaster,
    InferenceRequest,
    InferenceResult,
    describe_forecaster,
)
from .forecasters import resolve_forecaster
from .identity import ArtifactReference, ForecastContract, canonical_json, semantic_fingerprint
from .logistic_forecasts import ResearchForecastRequest, generate, model_for
from .logistic_projection import ForecastProjection
from .support import BaseRateArtifact, admit_support


def reference(kind: str, value: object) -> ArtifactReference:
    fingerprint = semantic_fingerprint(value)
    return ArtifactReference(
        artifact_id=f"flc-{kind}:{fingerprint}", artifact_version="1.0", fingerprint=fingerprint
    )


class BaseRateContext(ForecastContract):
    artifact: BaseRateArtifact
    composition: ForecastComposition

    @model_validator(mode="after")
    def bound_artifact(self) -> Self:
        node = self.composition.nodes[0]
        if node.artifact_ref != self.artifact.reference:
            raise ValueError("BASERATE_COMPOSITION_ARTIFACT_MISMATCH")
        return self

    @property
    def reference(self) -> ArtifactReference:
        return reference("baserate-context", self)


class LogisticContext(ForecastContract):
    """Already admitted, outcome-blind projection and immutable native fit records.

    No fifth-fold/final-holdout type is accepted. This does not authorize using
    private empirical inputs: callers still need the existing governance gates.
    """

    source: ForecastProjection
    training: TrainingRun

    @property
    def reference(self) -> ArtifactReference:
        return reference("logistic-context", self)


@dataclass(frozen=True, slots=True)
class BaseRateInferenceAdapter:
    context: BaseRateContext

    def descriptor(self) -> InferenceDescriptor:
        return describe_forecaster(
            ForecasterKey(
                forecaster_id="forecaster:historical-base-rate", implementation_version="1.0"
            )
        )

    def forecast(self, request: InferenceRequest) -> InferenceResult:
        request = InferenceRequest.model_validate(request)
        context = BaseRateContext.model_validate(self.context)
        if (
            request.key != self.descriptor().identity.key
            or request.context_ref != context.reference
            or not isinstance(request.native, ForecastRequest)
            or request.mode != context.composition.nodes[0].realization_mode
        ):
            raise ForecastIntegrityError("INFERENCE_CONTEXT_MISMATCH")
        legacy = resolve_forecaster(request.key.forecaster_id, request.key.implementation_version)
        payload = legacy.forecast(request.native, admit_support(context.artifact, request.native))
        return InferenceResult(
            request=request,
            descriptor=self.descriptor(),
            artifacts=ForecasterArtifacts(
                context=context.reference, composition=reference("composition", context.composition)
            ),
            native=payload,
        )


@dataclass(frozen=True, slots=True)
class LogisticInferenceAdapter:
    context: LogisticContext

    def descriptor(self) -> InferenceDescriptor:
        return describe_forecaster(
            ForecasterKey(
                forecaster_id="forecaster:logistic-regression", implementation_version="1.0"
            )
        )

    def forecast(self, request: InferenceRequest) -> InferenceResult:
        request = InferenceRequest.model_validate(request)
        context = LogisticContext.model_validate(self.context)
        if (
            request.key != self.descriptor().identity.key
            or request.context_ref != context.reference
            or not isinstance(request.native, ResearchForecastRequest)
        ):
            raise ForecastIntegrityError("INFERENCE_CONTEXT_MISMATCH")
        # All legacy qualification, model, dependency, feature and cutoff checks
        # stay with their owner. generate only reconstructs; it cannot train.
        native = generate(
            request.native.origin, context.source, context.training, request.computed_at
        )
        if native.request != request.native:
            raise ForecastIntegrityError("NATIVE_REQUEST_PIN_MISMATCH")
        c = native.request.composition
        model = model_for(context.training, native.request.fold_id)
        return InferenceResult(
            request=request,
            descriptor=self.descriptor(),
            artifacts=ForecasterArtifacts(
                context=context.reference,
                composition=reference("composition", c),
                model=ArtifactReference(
                    artifact_id="flc-model:" + c.model_fingerprint,
                    artifact_version=model.artifact_version,
                    fingerprint=c.model_fingerprint,
                ),
                scaler=ArtifactReference(
                    artifact_id="flc-scaler:" + c.scaler_fingerprint,
                    artifact_version="1.0",
                    fingerprint=c.scaler_fingerprint,
                ),
                training=ArtifactReference(
                    artifact_id="flc-training:" + native.request.training_run_fingerprint,
                    artifact_version="1.0",
                    fingerprint=native.request.training_run_fingerprint,
                ),
            ),
            native=native,
        )


def resolve_inference_forecaster(
    key: ForecasterKey, context: BaseRateContext | LogisticContext
) -> InferenceForecaster:
    """Exact, read-only adapter dispatch, not a second mutable registry."""
    descriptor = describe_forecaster(key)  # Unknown ID/version fails before binding.
    adapter: InferenceForecaster
    if isinstance(context, BaseRateContext):
        adapter = BaseRateInferenceAdapter(BaseRateContext.model_validate(context))
    else:
        adapter = LogisticInferenceAdapter(LogisticContext.model_validate(context))
    if adapter.descriptor() != descriptor:
        raise ForecastIntegrityError("INFERENCE_CONTEXT_FAMILY_MISMATCH")
    return adapter


def recorded_inference_replay(encoded: str, fingerprint: str) -> InferenceResult:
    """Decode a supplied FLC envelope; no artifact lookup or numeric execution.

    This neither replaces legacy captured replay nor claims exact pinned numeric
    verification. The caller must supply a trusted expected envelope hash.
    """
    value = strict_json(encoded)
    if canonical_json(value) != encoded or semantic_fingerprint(value) != fingerprint:
        raise ForecastIntegrityError("INFERENCE_REPLAY_FINGERPRINT_MISMATCH")
    return InferenceResult.model_validate(value)
