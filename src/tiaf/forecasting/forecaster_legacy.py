"""Legacy FLC-1 native wire contracts and exact adapter-edge admission.

Existing captures stay lossless. New families use inference_contracts, not these
intentionally finite compatibility codecs.
"""

from typing import Literal, Protocol, Self

from pydantic import model_validator

from .contracts import BinaryProbabilityOutput, ForecastAbsence, ForecastRequest
from .enums import ForecastRealizationMode, ForecastReason, ForecastStatus
from .errors import ForecastIntegrityError
from .forecasters import GenerationPayload, registered_forecasters, resolve_forecaster
from .identity import (
    ArtifactReference,
    ForecastContract,
    ForecastDateTime,
    semantic_fingerprint,
)
from .inference_contracts import (
    ForecasterArtifacts,
    ForecasterCapability,
    ForecasterFamily,
    ForecasterKey,
    ForecasterLifecycle,
    ForecasterRole,
    InferenceDescriptor,
    LifecycleIdentity,
)
from .logistic_forecasts import ResearchForecastRequest, ResearchForecastResult


def describe_forecaster(key: ForecasterKey) -> InferenceDescriptor:
    """Read-only adaptation view, no registry storage or registration API.

    BaseRate still resolves through the sole legacy registry. The existing
    unregistered Logistic research implementation has one exact compiled route;
    it is not inserted into the frozen FF-0 registry/runtime.
    """
    key = ForecasterKey.model_validate(key)
    learned = key == ForecasterKey(
        forecaster_id="forecaster:logistic-regression", implementation_version="1.0"
    )
    modes: tuple[ForecastRealizationMode, ...]
    if learned:
        modes = (ForecastRealizationMode.SIMULATED_ISSUANCE,)
    else:
        legacy = resolve_forecaster(key.forecaster_id, key.implementation_version).descriptor()
        modes = legacy.realization_modes
    return InferenceDescriptor(
        identity=LifecycleIdentity(
            key=key,
            family=(
                ForecasterFamily.LOGISTIC_REGRESSION if learned else ForecasterFamily.PRIMITIVE
            ),
            role=ForecasterRole.CHALLENGER if learned else ForecasterRole.BENCHMARK,
            lifecycle=(
                ForecasterLifecycle.EXPERIMENTAL if learned else ForecasterLifecycle.UNSPECIFIED
            ),
        ),
        capabilities=(
            ForecasterCapability.INFERENCE,
            ForecasterCapability.CALIBRATION_COMPATIBLE,
            ForecasterCapability.REPLAYABLE,
            *((ForecasterCapability.ARTIFACT_BACKED,) if learned else ()),
        ),
        modes=modes,
    )


def inference_descriptors() -> tuple[InferenceDescriptor, ...]:
    keys = tuple(
        ForecasterKey(
            forecaster_id=d.forecaster_id, implementation_version=d.implementation_version
        )
        for d in registered_forecasters()
    ) + (
        ForecasterKey(forecaster_id="forecaster:logistic-regression", implementation_version="1.0"),
    )
    if len(set(keys)) != len(keys):
        raise ForecastIntegrityError("DUPLICATE_FORECASTER_ID_VERSION")
    return tuple(describe_forecaster(key) for key in keys)


class InferenceRequest(ForecastContract):
    schema_id: Literal["tiaf.flc.inference-request"] = "tiaf.flc.inference-request"
    key: ForecasterKey
    native: ForecastRequest | ResearchForecastRequest
    context_ref: ArtifactReference
    computed_at: ForecastDateTime

    @property
    def target_id(self) -> str:
        if isinstance(self.native, ForecastRequest):
            target = self.native.target
            return f"{target.target_id}/{target.target_version}"
        return self.native.target_id

    @property
    def subject(self) -> str:
        if isinstance(self.native, ForecastRequest):
            key = self.native.target.subject
            return f"{key.symbol}:{key.exchange}:{key.segment.value}:{key.instrument_type.value}"
        return self.native.subject

    @property
    def mode(self) -> ForecastRealizationMode:
        if isinstance(self.native, ForecastRequest):
            return self.native.realization_mode
        return ForecastRealizationMode.SIMULATED_ISSUANCE

    @property
    def information_cutoff(self) -> ForecastDateTime:
        if isinstance(self.native, ForecastRequest):
            return self.native.information_cutoff
        return self.native.origin.information_cutoff

    @property
    def as_of(self) -> ForecastDateTime:
        if isinstance(self.native, ForecastRequest):
            return self.native.as_of
        return self.native.origin.simulation_as_of

    @model_validator(mode="after")
    def native_scope(self) -> Self:
        if isinstance(self.native, ForecastRequest):
            expected = ("forecaster:historical-base-rate", "1.0")
            if self.computed_at < self.as_of:
                raise ValueError("COMPUTATION_BEFORE_AS_OF")
        else:
            c = self.native.composition
            expected = (c.forecaster_id, c.forecaster_version)
            if self.computed_at <= self.as_of:
                raise ValueError("RESEARCH_COMPUTATION_NOT_AFTER_AS_OF")
        if (self.key.forecaster_id, self.key.implementation_version) != expected:
            raise ValueError("NATIVE_FORECASTER_IDENTITY_MISMATCH")
        return self


class InferenceResult(ForecastContract):
    schema_id: Literal["tiaf.flc.inference-result"] = "tiaf.flc.inference-result"
    request: InferenceRequest
    descriptor: InferenceDescriptor
    artifacts: ForecasterArtifacts
    native: GenerationPayload | ResearchForecastResult

    @model_validator(mode="after")
    def lineage(self) -> Self:
        if (
            self.request.key != self.descriptor.identity.key
            or self.descriptor != describe_forecaster(self.request.key)
            or self.request.context_ref != self.artifacts.context
            or self.request.mode not in self.descriptor.modes
        ):
            raise ValueError("INFERENCE_LINEAGE_MISMATCH")
        if isinstance(self.native, ResearchForecastResult):
            if (
                self.native.request != self.request.native
                or self.native.computed_at != self.request.computed_at
                or self.artifacts.model is None
                or self.artifacts.scaler is None
                or self.artifacts.training is None
                or self.artifacts.model.fingerprint
                != self.native.request.composition.model_fingerprint
                or self.artifacts.scaler.fingerprint
                != self.native.request.composition.scaler_fingerprint
                or self.artifacts.training.fingerprint
                != self.native.request.training_run_fingerprint
                or self.artifacts.composition.fingerprint
                != semantic_fingerprint(self.native.request.composition)
            ):
                raise ValueError("NATIVE_RESULT_LINEAGE_MISMATCH")
        elif not isinstance(self.request.native, ForecastRequest) or self.artifacts.model:
            raise ValueError("NATIVE_RESULT_FAMILY_MISMATCH")
        return self

    @property
    def status(self) -> ForecastStatus:
        if isinstance(self.native, GenerationPayload):
            return self.native.status
        # This is an inference availability view, NOT an Evaluation disposition.
        return (
            ForecastStatus.GENERATED
            if self.native.status == "GENERATED"
            else ForecastStatus.UNAVAILABLE
        )

    @property
    def output(self) -> BinaryProbabilityOutput | ForecastAbsence:
        if self.native.output is not None:
            return self.native.output
        assert isinstance(self.native, ResearchForecastResult)
        reason = {
            "PROTECTED": ForecastReason.POLICY_ABSTENTION,
            "EXCLUDED": ForecastReason.EVIDENCE_UNQUALIFIED,
            "UNAVAILABLE": ForecastReason.EVIDENCE_MISSING,
        }[self.native.status]
        return ForecastAbsence(reasons=(reason,))


class InferenceForecaster(Protocol):
    def descriptor(self) -> InferenceDescriptor: ...

    def forecast(self, request: InferenceRequest) -> InferenceResult: ...

