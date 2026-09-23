"""FLC-2 codecs in the existing research store owner; no second I/O engine.

No latest/active aliases or registry writes. Caller-pinned content references
resolve exactly. A custody declaration is not an availability or use grant.
"""

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Literal

from pydantic import Field, TypeAdapter

from tiaf.forecasting.contracts import BinaryProbabilityOutput
from tiaf.forecasting.identity import ArtifactReference, ForecastDateTime, LogicalId
from tiaf.forecasting.logistic_store import ResearchForecastStore

from .forecast_artifacts import Five, FoldManifest, LogisticArtifact, SealedResearch, reconstruct
from .forecast_jobs import FifthTrainingJob, TrainingJob
from .forecaster_authority import TrainingAttempt, TrainingAuthorization
from .forecaster_lifecycle import (
    ActivationState,
    ApprovalDecision,
    LifecycleHistory,
    LifecycleObservation,
    LifecycleRecord,
    LifecycleSubject,
    TransitionRequest,
)
from .forecaster_training import (
    ExperimentIdentity,
    ModelArtifactIdentity,
    PreprocessorIdentity,
    TrainingBundle,
    TrainingExecution,
    TrainingIdentity,
    TrainingResult,
    normalize_logistic,
    reference,
)
from .synthetic_trials import SyntheticJob, SyntheticModel, SyntheticSpec, normalize


class CustodyClass(StrEnum):
    TRACKED_REPOSITORY_METADATA = "TRACKED_REPOSITORY_METADATA"
    LOCAL_RESEARCH_ARTIFACT = "LOCAL_RESEARCH_ARTIFACT"
    PRIVATE_LICENSED_DATA = "PRIVATE_LICENSED_DATA"
    GENERATED_EPHEMERAL = "GENERATED_EPHEMERAL"


class ArtifactPersistence(SealedResearch):
    artifact_reference: ArtifactReference
    custody: CustodyClass
    location_reference: LogicalId
    declared_at: ForecastDateTime
    availability: Literal["NOT_CHECKED"] = "NOT_CHECKED"
    use_authorized: Literal[False] = False


class AvailabilityObservation(SealedResearch):
    artifact_reference: ArtifactReference
    checked_at: ForecastDateTime
    status: Literal["PRESENT_VERIFIED", "UNAVAILABLE"]
    reason: str | None = Field(default=None, min_length=1)
    use_authorized: Literal[False] = False


class ForecasterStore(ResearchForecastStore):
    """Additive codec profile, exactly the existing bounded canonical store."""

    record_types = MappingProxyType(
        {
            **ResearchForecastStore.record_types,
            "manifest": FoldManifest,
            "job": TrainingJob,
            "fifthjob": FifthTrainingJob,
            "experiment": ExperimentIdentity,
            "request": TrainingIdentity,
            "execution": TrainingExecution,
            "result": TrainingResult,
            "bundle": TrainingBundle,
            "modelidentity": ModelArtifactIdentity,
            "preprocessor": PreprocessorIdentity,
            "custody": ArtifactPersistence,
            "availability": AvailabilityObservation,
            "subject": LifecycleSubject,
            "transition": TransitionRequest,
            "approval": ApprovalDecision,
            "event": LifecycleRecord,
            "history": LifecycleHistory,
            "observation": LifecycleObservation,
            "activation": ActivationState,
            "authorization": TrainingAuthorization,
            "attempt": TrainingAttempt,
            "trialspec": SyntheticSpec,
            "trialjob": SyntheticJob,
            "trialmodel": SyntheticModel,
        }
    )

    def resolve(self, ref: ArtifactReference) -> SealedResearch:
        ref = ArtifactReference.model_validate(ref.model_dump())
        prefix, _, kind = ref.artifact_id.partition(":")
        if prefix != "flc" or kind not in self.record_types:
            raise ValueError("UNKNOWN_ARTIFACT_IDENTITY")
        value = self.get(kind, ref.fingerprint)
        if reference(kind, value) != ref:
            raise ValueError("ARTIFACT_VERSION_MISMATCH")
        return value

    def inspect_availability(
        self, ref: ArtifactReference, *, at: ForecastDateTime
    ) -> AvailabilityObservation:
        try:
            self.resolve(ref)
        except (ValueError, OSError):
            return AvailabilityObservation(
                artifact_reference=ref,
                checked_at=at,
                status="UNAVAILABLE",
                reason="MISSING_INVALID_OR_UNSUPPORTED_ARTIFACT",
            )
        return AvailabilityObservation(
            artifact_reference=ref, checked_at=at, status="PRESENT_VERIFIED"
        )


def persist_training(
    store: ForecasterStore,
    request: TrainingIdentity,
    manifest: FoldManifest | SyntheticSpec,
    job: TrainingJob | FifthTrainingJob | SyntheticJob,
) -> TrainingBundle:
    if isinstance(manifest, SyntheticSpec):
        if not isinstance(job, SyntheticJob):
            raise ValueError("SYNTHETIC_JOB_REQUIRED")
        bundle = normalize(request, manifest, job)
        for kind, child in (
            ("experiment", request.experiment),
            ("trialspec", manifest),
            ("request", request),
            ("trialjob", job),
            ("execution", bundle.execution),
        ):
            store.put(kind, child)
        if job.artifact is not None:
            assert bundle.result.model_identity and bundle.result.preprocessor_identity
            store.put("scaler", job.artifact.reconstruction.scaler)
            store.put("preprocessor", bundle.result.preprocessor_identity)
            store.put("trialmodel", job.artifact)
            store.put("modelidentity", bundle.result.model_identity)
        store.put("result", bundle.result)
        store.put("bundle", bundle)
        return bundle
    if isinstance(job, SyntheticJob):
        raise ValueError("NATIVE_JOB_REQUIRED")
    bundle = normalize_logistic(request, manifest, job)
    # Children before parent: persistence failure cannot create a complete bundle.
    values: list[tuple[str, SealedResearch]] = [
        ("experiment", request.experiment),
        ("manifest", manifest),
        ("request", request),
        ("fifthjob" if isinstance(job, FifthTrainingJob) else "job", job),
        ("execution", bundle.execution),
    ]
    model, scaler = bundle.result.model_identity, bundle.result.preprocessor_identity
    if job.artifact is not None and model is not None and scaler is not None:
        values.extend(
            [
                ("scaler", job.artifact.reconstruction.scaler),
                ("preprocessor", scaler),
                ("model", job.artifact),
                ("modelidentity", model),
            ]
        )
    values.extend([("result", bundle.result), ("bundle", bundle)])
    for kind, value in values:
        store.put(kind, value)
    return bundle


def restore_training(store: ForecasterStore, bundle_ref: ArtifactReference) -> TrainingBundle:
    bundle = store.resolve(bundle_ref)
    if not isinstance(bundle, TrainingBundle):
        raise ValueError("TRAINING_BUNDLE_REQUIRED")
    manifest = store.resolve(bundle.request.split_reference)
    job = store.resolve(bundle.execution.native_job_reference)
    if isinstance(manifest, SyntheticSpec) and isinstance(job, SyntheticJob):
        expected = normalize(bundle.request, manifest, job)
    elif isinstance(manifest, FoldManifest) and isinstance(job, (TrainingJob, FifthTrainingJob)):
        expected = normalize_logistic(bundle.request, manifest, job)
    else:
        raise ValueError("NATIVE_TRAINING_RECORD_REQUIRED")
    if expected != bundle:
        raise ValueError("TRAINING_REPLAY_MISMATCH")
    refs = [
        reference("experiment", bundle.request.experiment),
        reference("request", bundle.request),
        reference("execution", bundle.execution),
        reference("result", bundle.result),
    ]
    model, scaler = bundle.result.model_identity, bundle.result.preprocessor_identity
    if model is not None:
        refs.extend([reference("modelidentity", model), model.artifact])
    if scaler is not None:
        refs.extend([reference("preprocessor", scaler), scaler.artifact])
    for ref in refs:
        store.resolve(ref)
    return bundle


@dataclass(frozen=True)
class RestoredLogisticPredictor:
    """Pure numeric leaf, not an issuance/admission interface or runtime binding.

    FLC-1 still owns complete forecast envelopes. This codec probe is also useful for
    synthetic fits which must NOT masquerade as qualified empirical FF-1 handoffs.
    """

    identity: ModelArtifactIdentity
    artifact: LogisticArtifact

    def __post_init__(self) -> None:
        identity = ModelArtifactIdentity.model_validate(self.identity.model_dump())
        artifact = LogisticArtifact.model_validate(self.artifact.model_dump())
        if (
            identity.artifact != reference("model", artifact)
            or identity.forecaster.forecaster_id != artifact.forecaster_id
            or identity.forecaster.implementation_version != artifact.implementation_version
        ):
            raise ValueError("PREDICTOR_ARTIFACT_IDENTITY_MISMATCH")
        object.__setattr__(self, "identity", identity)
        object.__setattr__(self, "artifact", artifact)

    def predict(self, features: Five) -> BinaryProbabilityOutput:
        features = TypeAdapter(Five).validate_python(features)
        return BinaryProbabilityOutput(
            probability=reconstruct(self.artifact.reconstruction, features)
        )


def restore_predictor(
    store: ForecasterStore, bundle_ref: ArtifactReference
) -> RestoredLogisticPredictor:
    bundle = restore_training(store, bundle_ref)
    identity = bundle.result.model_identity
    if identity is None:
        raise ValueError("MODEL_UNAVAILABLE")
    artifact = store.resolve(identity.artifact)
    if not isinstance(artifact, LogisticArtifact):
        raise ValueError("UNSUPPORTED_MODEL_CODEC")
    return RestoredLogisticPredictor(identity, artifact)
