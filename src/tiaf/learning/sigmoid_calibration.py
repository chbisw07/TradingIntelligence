"""FF-2.2 bounded Learning capability over FLC identity/authority/custody owners.

No empirical loader, configurable base trainer, calibration grid or promotion.
The old FLC-5 authored-table capability and all native/raw codecs are untouched.
"""

import os
import subprocess
import sys
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from time import monotonic
from types import MappingProxyType
from typing import Literal, cast

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.contracts import BinaryProbabilityOutput, ForecastEdge
from tiaf.forecasting.enums import ForecastRealizationMode
from tiaf.forecasting.identity import (
    ArtifactReference,
    ForecastDateTime,
    canonical_json,
    semantic_fingerprint,
)
from tiaf.forecasting.inference_contracts import ForecasterKey
from tiaf.forecasting.lifecycle_provenance import NeutralInferenceCapture

from .calibration_contracts import CalibrationComponent, CalibrationTarget
from .forecast_artifacts import SealedResearch
from .forecaster_authority import TrainingAttempt, TrainingAuthorization, admit_training
from .forecaster_custody import ForecasterStore
from .forecaster_training import (
    ExperimentIdentity,
    ModelArtifactIdentity,
    ResourcePolicy,
    TrainingBundle,
    TrainingExecution,
    TrainingIdentity,
    TrainingResult,
    reference,
)
from .sigmoid_contracts import (
    VERSION,
    CalibratedCandidate,
    CalibratedCapture,
    CalibrationSample,
    SigmoidArtifact,
    SigmoidParameters,
    synthetic_sample,
)
from .sigmoid_math import transform
from .sigmoid_synthetic import (
    SOURCE_KEY,
    TARGET,
    SyntheticCalibrationInput,
    SyntheticLogisticModel,
    pin,
    synthetic_source,
)

CONFIGURATION = semantic_fingerprint(
    (VERSION, "a=0;b=1;unweighted;no-penalty;newton-armijo-32;tol=1e-8;max=1000")
)
CALIBRATOR_KEY = ForecasterKey(
    forecaster_id="calibrator:ff2-synthetic-sigmoid", implementation_version=VERSION
)


class SigmoidStore(ForecasterStore):
    """Codec-only extension. Existing bounded canonical store engine owns I/O."""

    record_types = MappingProxyType(
        {
            **ForecasterStore.record_types,
            "sigmoidsample": CalibrationSample,
            "sigmoidartifact": SigmoidArtifact,
            "sigmoidcandidate": CalibratedCandidate,
            "sigmoidcapture": CalibratedCapture,
            "sigmoidinput": SyntheticCalibrationInput,
            "sigmoidmodel": SyntheticLogisticModel,
            "neutralinfercapture": NeutralInferenceCapture,
        }
    )


def synthetic_fit_request(at: ForecastDateTime) -> TrainingIdentity:
    """Exact compile-time recipe and current executable pins, not caller-selected data."""
    sample = synthetic_sample()
    code = tuple(
        (name, sha256(Path(__file__).with_name(name).read_bytes()).hexdigest())
        for name in (
            "sigmoid_contracts.py",
            "sigmoid_math.py",
            "sigmoid_worker.py",
            "sigmoid_synthetic.py",
            "sigmoid_calibration.py",
        )
    )
    return TrainingIdentity(
        experiment=ExperimentIdentity(
            experiment_id="experiment:ff2-synthetic-engineering-001",
            candidate_id="candidate:ff2-synthetic-fit-001",
            forecaster=CALIBRATOR_KEY,
            design_reference=pin("synthetic-engineering-design"),
        ),
        family="SIGMOID_CALIBRATOR",
        target_id=TARGET,
        target_version="1.0",
        subject="synthetic:asset",
        feature_schema_id="ff2.synthetic.logit-grid",
        feature_schema_version="1.0",
        feature_schema_fingerprint=pin("schema").fingerprint,
        population_fingerprint=semantic_fingerprint(sample),
        split_reference=pin("calibration-only"),
        configuration_fingerprint=CONFIGURATION,
        qualification_fingerprint=pin("qualification").fingerprint,
        dataset_fingerprint=semantic_fingerprint(sample),
        research_profile_fingerprint=pin("profile").fingerprint,
        dependency_lock_fingerprint=semantic_fingerprint((sys.version, "stdlib-math-newton-v1")),
        implementation_fingerprint=semantic_fingerprint(code),
        authority_reference=pin("authority"),
        created_at=at,
        purpose="SYNTHETIC_ENGINEERING",
    )


def _claim(store: SigmoidStore, request: TrainingIdentity, grant: TrainingAuthorization) -> None:
    attempt = TrainingAttempt(
        grant_reference=reference("authorization", grant),
        request_reference=reference("request", request),
    )
    raw = (canonical_json(attempt) + "\n").encode()
    if store.bytes + len(raw) > 2 * 1024**3 or store.count + 1 > 65536:
        raise ValueError("RESEARCH_CORPUS_LIMIT")
    # Same exclusive-claim pattern as FLC-2. Put is intentionally NOT used for the claim.
    with store._path("attempt", cast(str, attempt.fingerprint)).open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    directory = os.open(store.root, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    store.count += 1
    store.bytes += len(raw)
    if store.resolve(reference("attempt", attempt)) != attempt:
        raise ValueError("CALIBRATION_CLAIM_MISMATCH")


def fit_synthetic_once(
    store: SigmoidStore,
    request: TrainingIdentity,
    grant: TrainingAuthorization,
    sample: CalibrationSample,
) -> tuple[SigmoidArtifact, TrainingBundle]:
    """No arbitrary empirical fit route, including after relabeling a supplied sample."""
    request = TrainingIdentity.model_validate(request)
    grant = TrainingAuthorization.model_validate(grant)
    sample = CalibrationSample.model_validate(sample)
    if request != synthetic_fit_request(request.created_at) or sample != synthetic_sample():
        raise ValueError("ONLY_COMPILED_SYNTHETIC_CALIBRATION_ALLOWED")
    if not store.writable or tuple(store.root.glob("attempt-*.json")):
        raise ValueError("CALIBRATION_ATTEMPT_CONSUMED_OR_READ_ONLY")
    started = datetime.now(TIAF_TIMEZONE)
    admit_training(
        request, grant, input_fingerprint=semantic_fingerprint(sample), root=store.root, at=started
    )
    if grant.authority_reference != request.authority_reference:
        raise ValueError("CALIBRATION_AUTHORITY_MISMATCH")
    store.put("authorization", grant)
    store.put("request", request)
    store.put("sigmoidsample", sample)
    _claim(store, request, grant)  # Irreversible before any fitting; crash never licenses retry.
    begin = monotonic()
    worker = subprocess.run(
        [sys.executable, "-m", "tiaf.learning.sigmoid_worker"],
        capture_output=True,
        check=True,
        text=True,
        timeout=60,
        env={
            **os.environ,
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
        },
    )
    parameters = SigmoidParameters.model_validate_json(worker.stdout)
    completed = datetime.now(TIAF_TIMEZONE)
    component = CalibrationComponent(
        calibrator_id="calibrator:ff2-synthetic-sigmoid",
        implementation_version=VERSION,
        family="calibration:sigmoid-logit",
        target=CalibrationTarget(
            target_id=TARGET,
            target_version="1.0",
            positive_event="synthetic:terminal-greater-than-reference",
            horizon="synthetic:one-step",
            cutoff_policy=pin("cutoff"),
        ),
        source_forecaster=SOURCE_KEY,
        source_model=reference("sigmoidmodel", SyntheticLogisticModel()),
        mode=ForecastRealizationMode.SIMULATED_ISSUANCE,
        configuration_fingerprint=CONFIGURATION,
        created_at=request.created_at,
    )
    artifact = SigmoidArtifact(
        component=component,
        parameters=parameters,
        feature_schema=pin("schema"),
        source_training=pin("authored-no-base-fit"),
        fit_request=reference("request", request),
        fit_grant=reference("authorization", grant),
        fit_attempt=reference(
            "attempt",
            TrainingAttempt(
                grant_reference=reference("authorization", grant),
                request_reference=reference("request", request),
            ),
        ),
        sample=reference("sigmoidsample", sample),
        fitted_at=completed,
    )
    execution = TrainingExecution(
        request_reference=reference("request", request),
        native_job_reference=reference("sigmoidartifact", artifact),
        started_at=started,
        completed_at=completed,
        status="TRAINED",
        libraries=None,
        resources=ResourcePolicy(timeout_seconds=60, memory_bytes=512 * 1024**2, numeric_threads=1),
        worker_identity="worker:ff2-synthetic-sigmoid-v1",
        elapsed_seconds=monotonic() - begin,
    )
    identity = ModelArtifactIdentity(
        artifact=reference("sigmoidartifact", artifact),
        forecaster=CALIBRATOR_KEY,
        family="SIGMOID_CALIBRATOR",
        model_version=VERSION,
        request_reference=reference("request", request),
        execution_reference=reference("execution", execution),
        subject=request.subject,
        target_id=TARGET,
        feature_schema_id=request.feature_schema_id,
        configuration_fingerprint=CONFIGURATION,
        created_at=completed,
    )
    result = TrainingResult(
        status="TRAINED",
        request_reference=reference("request", request),
        execution_reference=reference("execution", execution),
        model_identity=identity,
    )
    bundle = TrainingBundle(request=request, execution=execution, result=result)
    for kind, value in (
        ("sigmoidartifact", artifact),
        ("execution", execution),
        ("modelidentity", identity),
        ("result", result),
        ("bundle", bundle),
    ):
        store.put(kind, value)
    return artifact, bundle


def compose(
    artifact: SigmoidArtifact, source_composition: ArtifactReference
) -> CalibratedCandidate:
    artifact = SigmoidArtifact.model_validate(artifact)
    return CalibratedCandidate(
        artifact=artifact,
        source_composition=source_composition,
        edge=ForecastEdge(
            source_node_id=artifact.component.source_forecaster.forecaster_id,
            target_node_id="forecaster:ff2-synthetic-calibrated",
        ),
    )


def apply_synthetic(
    store: SigmoidStore,
    candidate: CalibratedCandidate,
    fit: TrainingBundle,
    native: SyntheticCalibrationInput,
    source: NeutralInferenceCapture,
) -> CalibratedCapture:
    candidate, fit = (
        CalibratedCandidate.model_validate(candidate),
        TrainingBundle.model_validate(fit),
    )
    native, source = (
        SyntheticCalibrationInput.model_validate(native),
        NeutralInferenceCapture.model_validate(source),
    )
    if source != synthetic_source(native):
        raise ValueError("ONLY_COMPILED_SYNTHETIC_SOURCE_ALLOWED")
    artifact = candidate.artifact
    if (
        store.resolve(reference("sigmoidartifact", artifact)) != artifact
        or store.resolve(reference("bundle", fit)) != fit
    ):
        raise ValueError("CALIBRATION_FIT_CUSTODY_MISMATCH")
    output = source.result.output
    if not isinstance(output, BinaryProbabilityOutput):
        raise ValueError("CALIBRATION_SOURCE_ABSENT")
    capture = CalibratedCapture(
        candidate=candidate,
        source=source,
        fit=fit,
        raw_probability=output.probability,
        calibrated_probability=transform(artifact.parameters, output.probability),
        created_at=native.at,
        lineage=(
            reference("sigmoidcandidate", candidate),
            reference("neutralinfercapture", source),
            reference("bundle", fit),
        ),
    )
    for kind, value in (
        ("sigmoidmodel", SyntheticLogisticModel()),
        ("sigmoidinput", native),
        ("sigmoidcandidate", candidate),
        ("neutralinfercapture", source),
        ("sigmoidcapture", capture),
    ):
        store.put(kind, value)
    return capture


class SigmoidReplay(SealedResearch):
    target: ArtifactReference
    status: Literal["MATCH", "MISMATCH", "UNAVAILABLE", "UNSUPPORTED"]
    capture: CalibratedCapture | None = None
    grants_execution: Literal[False] = False


def _replay_resolve(store: SigmoidStore, ref: ArtifactReference) -> SealedResearch:
    ref = ArtifactReference.model_validate(ref)
    prefix, _, kind = ref.artifact_id.partition(":")
    if prefix != "flc" or kind not in store.record_types:
        raise ValueError("UNKNOWN_CALIBRATION_REFERENCE")
    path = store._path(kind, ref.fingerprint)
    if not path.exists() and not path.is_symlink():
        raise FileNotFoundError("CALIBRATION_DEPENDENCY_UNAVAILABLE")
    return store.resolve(ref)


def replay_sigmoid(
    store: SigmoidStore,
    target: ArtifactReference,
    *,
    reconstruct: bool = False,
) -> SigmoidReplay:
    """Read-only captured verification, never transform/fit/inference/evaluation."""
    if reconstruct:
        return SigmoidReplay(target=target, status="UNSUPPORTED")
    try:
        capture = _replay_resolve(store, target)
        if not isinstance(capture, CalibratedCapture):
            raise ValueError("WRONG_CALIBRATION_REPLAY_TARGET")
        raw, artifact, bundle = capture.source.result, capture.candidate.artifact, capture.fit
        if bundle.result.model_identity is None:
            raise ValueError("CALIBRATION_MODEL_IDENTITY_MISSING")
        expected: tuple[tuple[str, SealedResearch], ...] = (
            ("sigmoidcandidate", capture.candidate),
            ("neutralinfercapture", capture.source),
            ("bundle", bundle),
            ("sigmoidartifact", artifact),
            ("request", bundle.request),
            ("execution", bundle.execution),
            ("result", bundle.result),
            ("modelidentity", bundle.result.model_identity),
            ("sigmoidsample", synthetic_sample()),
            ("sigmoidmodel", SyntheticLogisticModel()),
        )
        for kind, record in expected:
            if _replay_resolve(store, reference(kind, record)) != record:
                raise ValueError("CALIBRATION_REPLAY_DEPENDENCY_MISMATCH")
        native = _replay_resolve(store, raw.request.input_ref)
        if (
            not isinstance(native, SyntheticCalibrationInput)
            or native.at != raw.request.computed_at
        ):
            raise ValueError("CALIBRATION_REPLAY_INPUT_MISMATCH")
        grant = _replay_resolve(store, artifact.fit_grant)
        attempt = _replay_resolve(store, artifact.fit_attempt)
        if not isinstance(grant, TrainingAuthorization) or attempt != TrainingAttempt(
            grant_reference=artifact.fit_grant, request_reference=artifact.fit_request
        ):
            raise ValueError("CALIBRATION_REPLAY_AUTHORITY_MISMATCH")
        admit_training(
            bundle.request,
            grant,
            input_fingerprint=semantic_fingerprint(synthetic_sample()),
            root=store.root,
            at=bundle.execution.started_at,
        )
        if artifact.sample != reference("sigmoidsample", synthetic_sample()):
            raise ValueError("CALIBRATION_REPLAY_SAMPLE_MISMATCH")
        if grant.authority_reference != bundle.request.authority_reference:
            raise ValueError("CALIBRATION_REPLAY_GRANT_MISMATCH")
        return SigmoidReplay(target=target, status="MATCH", capture=capture)
    except FileNotFoundError:
        return SigmoidReplay(target=target, status="UNAVAILABLE")
    except (ValueError, TypeError):
        return SigmoidReplay(target=target, status="MISMATCH")
