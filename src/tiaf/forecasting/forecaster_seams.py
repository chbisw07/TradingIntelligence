"""Additive FLC inference envelopes; legacy purpose-specific contracts stay intact.

These are internal data contracts, not activation grants or a replacement capture
store. Native requests remain authoritative for target, clocks and provenance.
"""

from enum import StrEnum
from typing import Literal, Protocol, Self, TypeVar

from pydantic import Field, model_validator

from .contracts import BinaryProbabilityOutput, ForecastAbsence, ForecastRequest
from .enums import ForecastRealizationMode, ForecastReason, ForecastStatus
from .errors import ForecastIntegrityError
from .forecasters import GenerationPayload, registered_forecasters, resolve_forecaster
from .identity import (
    ArtifactReference,
    ForecastContract,
    ForecastDateTime,
    LogicalId,
    semantic_fingerprint,
)
from .logistic_forecasts import ResearchForecastRequest, ResearchForecastResult


class ForecasterRole(StrEnum):
    BENCHMARK = "BENCHMARK"
    CHALLENGER = "CHALLENGER"


class ForecasterLifecycle(StrEnum):
    UNSPECIFIED = "UNSPECIFIED"
    EXPERIMENTAL = "EXPERIMENTAL"
    VALIDATED = "VALIDATED"
    SHADOW = "SHADOW"
    APPROVED = "APPROVED"
    SUSPENDED = "SUSPENDED"
    RETIRED = "RETIRED"


class ForecasterFamily(StrEnum):
    PRIMITIVE = "PRIMITIVE"
    LOGISTIC_REGRESSION = "LOGISTIC_REGRESSION"


class ForecasterCapability(StrEnum):
    INFERENCE = "INFERENCE"
    TRAINING = "TRAINING"
    DIAGNOSTICS = "DIAGNOSTICS"
    CALIBRATION_COMPATIBLE = "CALIBRATION_COMPATIBLE"
    ARTIFACT_BACKED = "ARTIFACT_BACKED"
    REPLAYABLE = "REPLAYABLE"


class ForecasterKey(ForecastContract):
    forecaster_id: LogicalId
    implementation_version: str = Field(pattern=r"^[A-Za-z0-9_.-]{1,40}$")


class LifecycleIdentity(ForecastContract):
    key: ForecasterKey
    family: ForecasterFamily
    role: ForecasterRole
    lifecycle: ForecasterLifecycle
    approval: Literal["NOT_GRANTED_BY_INFERENCE"] = "NOT_GRANTED_BY_INFERENCE"
    activation_eligible: Literal[False] = False


class InferenceDescriptor(ForecastContract):
    identity: LifecycleIdentity
    capabilities: tuple[ForecasterCapability, ...]
    modes: tuple[ForecastRealizationMode, ...]

    @model_validator(mode="after")
    def unique(self) -> Self:
        if len(set(self.capabilities)) != len(self.capabilities):
            raise ValueError("DUPLICATE_CAPABILITY")
        if not self.modes or len(set(self.modes)) != len(self.modes):
            raise ValueError("INVALID_REALIZATION_MODES")
        return self

    def supports(self, capability: ForecasterCapability) -> bool:
        """False is explicit valid absence, never permission to execute."""
        return capability in self.capabilities


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


class ForecasterArtifacts(ForecastContract):
    """References only; support artifacts are not learned model artifacts."""

    context: ArtifactReference
    composition: ArtifactReference
    model: ArtifactReference | None = None
    scaler: ArtifactReference | None = None
    training: ArtifactReference | None = None

    @model_validator(mode="after")
    def learned_closure(self) -> Self:
        supplied = (self.model is not None, self.scaler is not None, self.training is not None)
        if any(supplied) and not all(supplied):
            raise ValueError("INCOMPLETE_LEARNED_ARTIFACT_REFERENCES")
        return self


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


class TrainingRequest(ForecastContract):
    """Proposal only. A qualification reference is not an execution grant.

    No protected/consumed partition or data rows fit this boundary. FLC-2 must
    resolve external qualification and custody before implementing any trainer.
    """

    key: ForecasterKey
    inputs: tuple[ArtifactReference, ...] = Field(min_length=1)
    configuration: ArtifactReference
    qualification: ArtifactReference
    partition: Literal["TRAIN"] = "TRAIN"
    status: Literal["PROPOSED_NOT_AUTHORIZED"] = "PROPOSED_NOT_AUTHORIZED"


class TrainingResult(ForecastContract):
    request: TrainingRequest
    status: Literal["NOT_EXECUTED"] = "NOT_EXECUTED"
    # No executable training implementation or success claim exists in FLC-1.
    artifact: None = None


class TrainableForecaster(Protocol):
    def train(self, request: TrainingRequest) -> TrainingResult: ...


DiagnosticOutput = TypeVar("DiagnosticOutput", bound=ForecastContract, covariant=True)


class DiagnosticRequest(ForecastContract):
    key: ForecasterKey
    artifact: ArtifactReference
    kind: LogicalId


class DiagnosticReport[DiagnosticPayload: ForecastContract](ForecastContract):
    request: DiagnosticRequest
    payload: DiagnosticPayload
    authority: Literal["DESCRIPTIVE_ONLY"] = "DESCRIPTIVE_ONLY"


class DiagnosableForecaster(Protocol[DiagnosticOutput]):
    def diagnose(self, request: DiagnosticRequest) -> DiagnosticOutput: ...


class CalibratableOutput(ForecastContract):
    """Raw-output composition hint, not a calibrator or qualification."""

    output: BinaryProbabilityOutput
    forecaster: LifecycleIdentity
    input_forecast: ArtifactReference
    status: Literal["RAW_COMPATIBLE_NOT_QUALIFIED"] = "RAW_COMPATIBLE_NOT_QUALIFIED"
    fit_authorized: Literal[False] = False
    apply_authorized: Literal[False] = False
