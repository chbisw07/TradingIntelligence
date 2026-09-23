"""Versioned synthetic Logistic capability inside the FLC-2 training service.

No input data/path/symbol field exists. Integer indices are artificial sequence
positions, not market sessions. Frozen FF-1 contracts/worker are not extended.
"""

import hashlib
import math
from pathlib import Path
from typing import Final, Literal, Self, cast

from pydantic import Field, StrictBool, model_validator

from tiaf.forecasting.forecaster_seams import ForecasterFamily, ForecasterKey
from tiaf.forecasting.identity import ArtifactReference, ForecastDateTime, semantic_fingerprint
from tiaf.planner.models import Sha256

from .forecast_artifacts import Finite, Five, LibraryVersions, Reconstruction, SealedResearch
from .forecaster_training import (
    ExperimentIdentity,
    ModelArtifactIdentity,
    PreprocessorIdentity,
    ResourcePolicy,
    TrainingBundle,
    TrainingExecution,
    TrainingIdentity,
    TrainingResult,
    reference,
)

VERSION: Final = "flc3.synthetic.1"
RECIPE: Final = "flc3.synthetic.temporal-integer-patterns.1"
KEY = ForecasterKey(forecaster_id="forecaster:logistic-regression", implementation_version=VERSION)
TARGET: Final = "synthetic:positive-label"
FEATURES: Final = "synthetic:five-patterns-v1"
DATASET = semantic_fingerprint((RECIPE, "680 authored sequence positions; no market data"))
QUALIFICATION = semantic_fingerprint((DATASET, "SYNTHETIC_ONLY; TRAIN_THEN_DEVELOPMENT"))
PROFILE = semantic_fingerprint((RECIPE, "DEVELOPMENT_ONLY; no protected evidence"))


def code_pin() -> str:
    root = Path(__file__).resolve().parents[1]
    names = (
        "learning/synthetic_trials.py",
        "learning/synthetic_trial_worker.py",
        "learning/forecaster_trial_service.py",
        "learning/forecaster_reference.py",
        "learning/forecaster_training.py",
        "learning/forecaster_custody.py",
        "learning/forecaster_authority.py",
        "learning/optimization.py",
        "learning/optimization_contracts.py",
        "evaluation/optimization_evaluation.py",
        "evaluation/forecast_comparison_metrics.py",
        "learning/forecast_artifacts.py",
    )
    return semantic_fingerprint(
        tuple((n, hashlib.sha256((root / n).read_bytes()).hexdigest()) for n in names)
    )


def dependency_pin() -> str:
    return hashlib.sha256(
        (
            Path(__file__).resolve().parents[3] / "requirements/ff1-training-linux-py312.lock"
        ).read_bytes()
    ).hexdigest()


class SyntheticConfig(SealedResearch):
    config_version: Literal["flc3.synthetic.config.1"] = "flc3.synthetic.config.1"
    C: Finite = Field(ge=0.05, le=10.0)
    fit_intercept: StrictBool
    solver: Literal["lbfgs"] = "lbfgs"
    seed: Literal[1729] = 1729


class SyntheticSpec(SealedResearch):
    worker_version: Literal["flc3.synthetic.1"] = VERSION
    recipe: Literal["flc3.synthetic.temporal-integer-patterns.1"] = RECIPE
    subject: Literal["SYNTHETIC:INTEGER_PATTERN"] = "SYNTHETIC:INTEGER_PATTERN"
    config: SyntheticConfig
    fold: Literal[0, 1]
    created_at: ForecastDateTime
    dependency_lock_fingerprint: Sha256
    implementation_fingerprint: Sha256


def row(index: int) -> tuple[Five, int]:
    if type(index) is not int or not 0 <= index < 680:
        raise ValueError("SYNTHETIC_POSITION_OUTSIDE_RECIPE")
    x = (
        math.sin(index * 0.17),
        math.cos(index * 0.11),
        (index % 13) / 13.0,
        math.sin(index * 0.07),
        7.0,
    )
    return x, int(x[0] + 0.35 * x[1] - 0.3 + 0.7 * math.sin(index * 0.91) > 0)


def training_rows(spec: SyntheticSpec) -> tuple[tuple[Five, int], ...]:
    return tuple(row(i) for i in range(600 + spec.fold * 40))


def development_rows(spec: SyntheticSpec) -> tuple[tuple[Five, int], ...]:
    start = 600 + spec.fold * 40
    return tuple(row(i) for i in range(start, start + 40))


def training_request(
    spec: SyntheticSpec, experiment: ExperimentIdentity, authority: ArtifactReference
) -> TrainingIdentity:
    spec = SyntheticSpec.model_validate(spec.model_dump())
    if experiment.forecaster != KEY:
        raise ValueError("EXACT_SYNTHETIC_IMPLEMENTATION_REQUIRED")
    return TrainingIdentity(
        experiment=experiment,
        family=ForecasterFamily.LOGISTIC_REGRESSION,
        target_id=TARGET,
        target_version="1.0",
        subject=spec.subject,
        feature_schema_id=FEATURES,
        feature_schema_version="1.0",
        feature_schema_fingerprint=semantic_fingerprint(FEATURES),
        population_fingerprint=semantic_fingerprint(training_rows(spec)),
        split_reference=reference("trialspec", spec),
        configuration_fingerprint=cast(str, spec.config.fingerprint),
        qualification_fingerprint=QUALIFICATION,
        dataset_fingerprint=DATASET,
        research_profile_fingerprint=PROFILE,
        dependency_lock_fingerprint=spec.dependency_lock_fingerprint,
        implementation_fingerprint=spec.implementation_fingerprint,
        authority_reference=authority,
        created_at=spec.created_at,
        purpose="SYNTHETIC_ENGINEERING",
    )


class SyntheticModel(SealedResearch):
    artifact_adapter_version: Literal["flc3.synthetic.artifact.1"] = "flc3.synthetic.artifact.1"
    worker_version: Literal["flc3.synthetic.1"] = VERSION
    spec: SyntheticSpec
    request_reference: ArtifactReference
    reconstruction: Reconstruction
    versions: LibraryVersions
    n_iter: int = Field(ge=1, lt=1000)
    created_at: ForecastDateTime
    role: Literal["CHALLENGER"] = "CHALLENGER"
    lifecycle: Literal["EXPERIMENTAL"] = "EXPERIMENTAL"

    @model_validator(mode="after")
    def lineage(self) -> Self:
        s = self.reconstruction.scaler
        if s.n != 600 + self.spec.fold * 40 or s.training_fingerprint != self.spec.fingerprint:
            raise ValueError("SYNTHETIC_SCALER_LINEAGE")
        if self.created_at < self.spec.created_at:
            raise ValueError("SYNTHETIC_MODEL_CLOCK")
        return self


class SyntheticJob(SealedResearch):
    spec: SyntheticSpec
    request_reference: ArtifactReference
    status: Literal["TRAINED", "UNAVAILABLE", "FAILED"]
    reason: str | None = None
    artifact: SyntheticModel | None = None
    started_at: ForecastDateTime
    completed_at: ForecastDateTime
    elapsed_seconds: Finite = Field(ge=0)
    timeout_seconds: Finite = Field(gt=0, le=60)
    worker_identity: Literal["worker:flc3-synthetic-v1"] = "worker:flc3-synthetic-v1"

    @model_validator(mode="after")
    def outcome(self) -> Self:
        ok = self.status == "TRAINED"
        if ok != (self.artifact is not None) or ok != (self.reason is None):
            raise ValueError("SYNTHETIC_JOB_STATUS")
        if self.completed_at < self.started_at:
            raise ValueError("SYNTHETIC_JOB_CLOCK")
        if self.started_at < self.spec.created_at:
            raise ValueError("SYNTHETIC_JOB_BEFORE_REQUEST")
        if self.artifact and not self.started_at <= self.artifact.created_at <= self.completed_at:
            raise ValueError("SYNTHETIC_ARTIFACT_EXECUTION_CLOCK")
        if self.artifact and (
            self.artifact.spec != self.spec
            or self.artifact.request_reference != self.request_reference
        ):
            raise ValueError("SYNTHETIC_JOB_LINEAGE")
        return self


def normalize(request: TrainingIdentity, spec: SyntheticSpec, job: SyntheticJob) -> TrainingBundle:
    job = SyntheticJob.model_validate(job.model_dump())
    if (
        request != training_request(spec, request.experiment, request.authority_reference)
        or job.spec != spec
        or job.request_reference != reference("request", request)
    ):
        raise ValueError("SYNTHETIC_TRAINING_LINEAGE")
    artifact = job.artifact
    execution = TrainingExecution(
        request_reference=reference("request", request),
        native_job_reference=reference("trialjob", job),
        started_at=job.started_at,
        completed_at=job.completed_at,
        status=job.status,
        libraries=artifact.versions if artifact else None,
        resources=ResourcePolicy(
            timeout_seconds=math.ceil(job.timeout_seconds),
            memory_bytes=512 * 1024**2,
            numeric_threads=1,
        ),
        worker_identity=job.worker_identity,
        elapsed_seconds=job.elapsed_seconds,
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
            artifact=reference("trialmodel", artifact),
            forecaster=KEY,
            family=request.family,
            model_version=artifact.artifact_adapter_version,
            request_reference=reference("request", request),
            execution_reference=reference("execution", execution),
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
        execution=execution,
        result=TrainingResult(
            status=job.status,
            request_reference=reference("request", request),
            execution_reference=reference("execution", execution),
            model_identity=model,
            preprocessor_identity=scaler,
            failure_reason=job.reason,
        ),
    )
