"""FLC-2 Learning identities and read-only native Logistic views, not fit authority.

The FLC-1 proposal-only TrainingRequest/Result remain unchanged. These sealed
Learning records describe actual jobs separately; neither an identity nor a
successful result is permission to train, promote, register or activate.
"""

from typing import Literal, Self, cast

from pydantic import Field, model_validator

from tiaf.forecasting.forecaster_seams import ForecasterFamily, ForecasterKey
from tiaf.forecasting.identity import (
    ArtifactReference,
    ForecastDateTime,
    LogicalId,
    semantic_fingerprint,
)
from tiaf.planner.models import Sha256

from .forecast_artifacts import (
    Finite,
    FoldManifest,
    LibraryVersions,
    SealedResearch,
)
from .forecast_jobs import FifthTrainingJob, TrainingJob

JobStatus = Literal["TRAINED", "UNAVAILABLE", "FAILED"]


def reference(kind: str, value: SealedResearch) -> ArtifactReference:
    """Content identity only: not a physical path, loader or authority alias."""
    return ArtifactReference(
        artifact_id=f"flc:{kind}",
        artifact_version=value.schema_version,
        fingerprint=cast(str, value.fingerprint),
    )


class ExperimentIdentity(SealedResearch):
    experiment_id: LogicalId
    candidate_id: LogicalId
    forecaster: ForecasterKey
    design_reference: ArtifactReference


class TrainingIdentity(SealedResearch):
    experiment: ExperimentIdentity
    family: ForecasterFamily
    target_id: str = Field(min_length=1)
    target_version: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    feature_schema_id: str = Field(min_length=1)
    feature_schema_version: str = Field(min_length=1)
    feature_schema_fingerprint: Sha256
    population_fingerprint: Sha256
    split_reference: ArtifactReference
    configuration_fingerprint: Sha256
    qualification_fingerprint: Sha256
    dataset_fingerprint: Sha256
    research_profile_fingerprint: Sha256
    dependency_lock_fingerprint: Sha256
    implementation_fingerprint: Sha256
    authority_reference: ArtifactReference
    created_at: ForecastDateTime
    purpose: Literal["READ_ONLY_LEGACY", "SYNTHETIC_ENGINEERING"]
    evidence_partition: Literal["TRAIN"] = "TRAIN"
    protected_evidence_used: Literal[False] = False


class ResourcePolicy(SealedResearch):
    timeout_seconds: int = Field(gt=0)
    memory_bytes: int = Field(gt=0)
    numeric_threads: int = Field(gt=0)
    attempts: Literal[1] = 1


class TrainingExecution(SealedResearch):
    request_reference: ArtifactReference
    native_job_reference: ArtifactReference
    started_at: ForecastDateTime
    completed_at: ForecastDateTime
    status: JobStatus
    libraries: LibraryVersions | None
    resources: ResourcePolicy
    worker_identity: LogicalId | None = None
    elapsed_seconds: Finite = Field(ge=0)
    cpu_seconds: Finite | None = Field(default=None, ge=0)
    peak_rss_kib: int | None = Field(default=None, ge=0)
    monetary_cost: Literal["UNPRICED"] = "UNPRICED"

    @model_validator(mode="after")
    def clocks(self) -> Self:
        if self.completed_at < self.started_at:
            raise ValueError("EXECUTION_CLOCK_ORDER")
        return self


class PreprocessorIdentity(SealedResearch):
    artifact: ArtifactReference
    implementation: str = Field(min_length=1)
    request_reference: ArtifactReference
    population_fingerprint: Sha256
    configuration_fingerprint: Sha256


class ModelArtifactIdentity(SealedResearch):
    artifact: ArtifactReference
    forecaster: ForecasterKey
    family: ForecasterFamily
    model_version: str = Field(min_length=1)
    request_reference: ArtifactReference
    execution_reference: ArtifactReference
    subject: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    feature_schema_id: str = Field(min_length=1)
    configuration_fingerprint: Sha256
    preprocessor_reference: ArtifactReference | None = None
    created_at: ForecastDateTime


class TrainingResult(SealedResearch):
    status: JobStatus
    request_reference: ArtifactReference
    execution_reference: ArtifactReference
    model_identity: ModelArtifactIdentity | None = None
    preprocessor_identity: PreprocessorIdentity | None = None
    diagnostic_references: tuple[ArtifactReference, ...] = ()
    failure_reason: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def links(self) -> Self:
        trained = self.status == "TRAINED"
        if trained != (self.model_identity is not None) or trained != (self.failure_reason is None):
            raise ValueError("RESULT_STATUS_MISMATCH")
        model, scaler = self.model_identity, self.preprocessor_identity
        if scaler is not None and model is None:
            raise ValueError("FAILED_RESULT_HAS_PREPROCESSOR")
        if model is not None and (
            model.request_reference != self.request_reference
            or model.execution_reference != self.execution_reference
            or model.preprocessor_reference
            != (reference("preprocessor", scaler) if scaler else None)
        ):
            raise ValueError("RESULT_MODEL_LINEAGE_MISMATCH")
        if scaler is not None and scaler.request_reference != self.request_reference:
            raise ValueError("RESULT_PREPROCESSOR_LINEAGE_MISMATCH")
        return self


class TrainingBundle(SealedResearch):
    request: TrainingIdentity
    execution: TrainingExecution
    result: TrainingResult

    @model_validator(mode="after")
    def links(self) -> Self:
        req, exe, result = self.request, self.execution, self.result
        if (
            exe.request_reference != reference("request", req)
            or result.request_reference != reference("request", req)
            or result.execution_reference != reference("execution", exe)
            or result.status != exe.status
            or req.created_at > exe.started_at
        ):
            raise ValueError("TRAINING_BUNDLE_LINEAGE_MISMATCH")
        return self


def logistic_request(
    manifest: FoldManifest,
    experiment: ExperimentIdentity,
    *,
    created_at: ForecastDateTime,
    purpose: Literal["READ_ONLY_LEGACY", "SYNTHETIC_ENGINEERING"],
) -> TrainingIdentity:
    """Read-only metadata extraction. Historical grants are NEVER renewed here."""
    manifest = FoldManifest.model_validate(manifest.model_dump())
    key = ForecasterKey(
        forecaster_id="forecaster:logistic-regression", implementation_version="1.0"
    )
    if experiment.forecaster != key:
        raise ValueError("UNSUPPORTED_TRAINING_IMPLEMENTATION")
    g = manifest.grant
    return TrainingIdentity(
        experiment=experiment,
        family=ForecasterFamily.LOGISTIC_REGRESSION,
        target_id=manifest.target_id,
        target_version=manifest.target_id.rsplit("/", 1)[1],
        subject=manifest.subject,
        feature_schema_id=manifest.feature_schema_id,
        feature_schema_version=manifest.feature_schema_id.rsplit("/", 1)[1],
        feature_schema_fingerprint=g.feature_schema_fingerprint,
        population_fingerprint=manifest.training_values_fingerprint,
        split_reference=reference("manifest", manifest),
        configuration_fingerprint=semantic_fingerprint(
            (manifest.model_config_value, manifest.scaler_config)
        ),
        qualification_fingerprint=g.qualification_fingerprint,
        dataset_fingerprint=g.dataset_fingerprint,
        research_profile_fingerprint=g.research_profile_fingerprint,
        dependency_lock_fingerprint=g.dependency_lock_fingerprint,
        implementation_fingerprint=g.code_fingerprint,
        authority_reference=reference("nativegrant", g),
        created_at=created_at,
        purpose=purpose,
    )


def normalize_logistic(
    request: TrainingIdentity,
    manifest: FoldManifest,
    job: TrainingJob | FifthTrainingJob,
) -> TrainingBundle:
    """Adapt an existing job without fitting, regenerating or rewriting it."""
    request = TrainingIdentity.model_validate(request.model_dump())
    job = type(job).model_validate(job.model_dump())
    expected = logistic_request(
        manifest,
        request.experiment,
        created_at=request.created_at,
        purpose=request.purpose,
    )
    if request != expected or (
        job.manifest_fingerprint != manifest.fingerprint
        or job.grant_fingerprint != manifest.grant.fingerprint
        or job.fold_id != manifest.fold_id
    ):
        raise ValueError("NATIVE_TRAINING_LINEAGE_MISMATCH")
    g, artifact = manifest.grant, job.artifact
    exe = TrainingExecution(
        request_reference=reference("request", request),
        native_job_reference=reference(
            "fifthjob" if isinstance(job, FifthTrainingJob) else "job", job
        ),
        started_at=job.started_at,
        completed_at=job.completed_at,
        status=job.status,
        libraries=artifact.versions if artifact else None,
        resources=ResourcePolicy(
            timeout_seconds=g.fit_timeout_seconds,
            memory_bytes=g.worker_memory_mib * 1024**2,
            numeric_threads=g.numeric_threads,
        ),
        elapsed_seconds=job.elapsed_seconds,
        cpu_seconds=job.cpu_seconds,
        peak_rss_kib=job.peak_rss_kib,
    )
    scaler = (
        None
        if artifact is None
        else PreprocessorIdentity(
            artifact=reference("scaler", artifact.reconstruction.scaler),
            implementation="StandardScaler",
            request_reference=reference("request", request),
            population_fingerprint=request.population_fingerprint,
            configuration_fingerprint=cast(str, artifact.reconstruction.scaler.config.fingerprint),
        )
    )
    model = (
        None
        if artifact is None
        else ModelArtifactIdentity(
            artifact=reference("model", artifact),
            forecaster=request.experiment.forecaster,
            family=request.family,
            model_version=artifact.artifact_version,
            request_reference=reference("request", request),
            execution_reference=reference("execution", exe),
            subject=request.subject,
            target_id=request.target_id,
            feature_schema_id=request.feature_schema_id,
            configuration_fingerprint=request.configuration_fingerprint,
            preprocessor_reference=reference("preprocessor", scaler) if scaler else None,
            created_at=artifact.created_at,
        )
    )
    return TrainingBundle(
        request=request,
        execution=exe,
        result=TrainingResult(
            status=job.status,
            request_reference=reference("request", request),
            execution_reference=reference("execution", exe),
            model_identity=model,
            preprocessor_identity=scaler,
            failure_reason=job.reason,
        ),
    )
