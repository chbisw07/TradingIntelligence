"""Family-neutral, immutable binary inference semantics; no native model imports.

An explicitly bound adapter owns native validation and numerical execution. The
common runner checks its declared contract, not its trustworthiness or authority.
No registry lookup, loader, model fitting, approval or activation occurs here.
"""

from enum import StrEnum
from typing import Annotated, Literal, Protocol, Self, TypeVar, runtime_checkable

from pydantic import Field, model_validator

from .contracts import BinaryProbabilityOutput, ForecastAbsence
from .enums import ForecastRealizationMode, ForecastStatus
from .errors import ForecastIntegrityError
from .identity import ArtifactReference, ForecastContract, ForecastDateTime, LogicalId

FamilyIdentifier = Annotated[str, Field(pattern=r"^[A-Z][A-Z0-9_]{0,63}$")]


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
    """Legacy spelling constants, not the closed domain of family identifiers."""

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
    family: FamilyIdentifier
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


class InferenceProvenance(ForecastContract):
    """Typed optional components; native adapters own model/scaler dependencies.

    Unlike the old learned triplet codec, a new family need not have a scaler.
    References establish identity, not custody, qualification or use authority.
    """

    context: ArtifactReference
    composition: ArtifactReference
    model: ArtifactReference | None = None
    scaler: ArtifactReference | None = None
    training: ArtifactReference | None = None


class NeutralInferenceRequest(ForecastContract):
    """No native payload: immutable references bind adapter-owned validated inputs."""

    schema_id: Literal["tiaf.flc.neutral-inference-request"] = "tiaf.flc.neutral-inference-request"
    key: ForecasterKey
    observation_id: LogicalId
    target_id: str = Field(min_length=1, max_length=200)
    subject: str = Field(min_length=1, max_length=200)
    mode: ForecastRealizationMode
    information_cutoff: ForecastDateTime
    as_of: ForecastDateTime
    computed_at: ForecastDateTime
    context_ref: ArtifactReference
    input_ref: ArtifactReference
    feature_schema: ArtifactReference | None = None
    experiment: ArtifactReference | None = None

    @model_validator(mode="after")
    def clocks(self) -> Self:
        if not self.information_cutoff <= self.as_of <= self.computed_at:
            raise ValueError("INFERENCE_CLOCK_ORDER")
        return self


class NeutralInferenceResult(ForecastContract):
    schema_id: Literal["tiaf.flc.neutral-inference-result"] = "tiaf.flc.neutral-inference-result"
    request: NeutralInferenceRequest
    descriptor: InferenceDescriptor
    artifacts: InferenceProvenance
    status: ForecastStatus
    output: BinaryProbabilityOutput | ForecastAbsence
    native_result: ArtifactReference | None = None

    @model_validator(mode="after")
    def lineage(self) -> Self:
        if (
            self.request.key != self.descriptor.identity.key
            or self.request.mode not in self.descriptor.modes
            or not self.descriptor.supports(ForecasterCapability.INFERENCE)
            or self.request.context_ref != self.artifacts.context
        ):
            raise ValueError("INFERENCE_LINEAGE_MISMATCH")
        if (
            self.descriptor.supports(ForecasterCapability.ARTIFACT_BACKED)
            and self.artifacts.model is None
        ):
            raise ValueError("INFERENCE_MODEL_REFERENCE_REQUIRED")
        if (self.status == ForecastStatus.GENERATED) != isinstance(
            self.output, BinaryProbabilityOutput
        ):
            raise ValueError("INFERENCE_OUTPUT_STATUS_MISMATCH")
        return self


@runtime_checkable
class InferenceAdapter(Protocol):
    """Bound native input/context. No optional lifecycle capability is executed."""

    def descriptor(self) -> InferenceDescriptor: ...

    def request(self) -> NeutralInferenceRequest: ...

    def forecast(self, request: NeutralInferenceRequest) -> NeutralInferenceResult: ...


def run_inference(
    request: NeutralInferenceRequest, adapter: InferenceAdapter
) -> NeutralInferenceResult:
    """Revalidate even model_copy/construct values and bind exact metadata at both ends."""
    if not isinstance(adapter, InferenceAdapter):
        raise ForecastIntegrityError("INVALID_INFERENCE_ADAPTER")
    request = NeutralInferenceRequest.model_validate(request)
    descriptor = InferenceDescriptor.model_validate(adapter.descriptor())
    bound = NeutralInferenceRequest.model_validate(adapter.request())
    if (
        request != bound
        or request.key != descriptor.identity.key
        or request.mode not in descriptor.modes
        or not descriptor.supports(ForecasterCapability.INFERENCE)
    ):
        raise ForecastIntegrityError("INFERENCE_ADAPTER_REQUEST_MISMATCH")
    result = NeutralInferenceResult.model_validate(adapter.forecast(request))
    if result.request != request or result.descriptor != descriptor:
        raise ForecastIntegrityError("INFERENCE_ADAPTER_RESULT_MISMATCH")
    return result


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
