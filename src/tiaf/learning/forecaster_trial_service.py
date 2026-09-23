"""Versioned worker adapter behind execute_synthetic_once, not optimizer training."""

import math
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import cast

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.capture import strict_json
from tiaf.forecasting.identity import canonical_json, semantic_fingerprint

from .forecaster_authority import TrainingAttempt, TrainingAuthorization, admit_training
from .forecaster_custody import ForecasterStore, persist_training
from .forecaster_training import TrainingBundle, TrainingIdentity, reference
from .synthetic_trial_worker import WorkerInput
from .synthetic_trials import (
    SyntheticJob,
    SyntheticSpec,
    code_pin,
    dependency_pin,
    training_request,
)


def execute_trial(
    store: ForecasterStore,
    request: TrainingIdentity,
    grant: TrainingAuthorization,
    spec: SyntheticSpec,
    timeout_seconds: float,
) -> TrainingBundle:
    tick = time.monotonic()
    spec = SyntheticSpec.model_validate(spec.model_dump())
    if not store.writable or not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 60:
        raise ValueError("SYNTHETIC_RESOURCE_OR_CUSTODY_POLICY")
    if (
        spec.implementation_fingerprint != code_pin()
        or spec.dependency_lock_fingerprint != dependency_pin()
    ):
        raise ValueError("SYNTHETIC_IMPLEMENTATION_PIN_MISMATCH")
    if (
        request != training_request(spec, request.experiment, request.authority_reference)
        or grant.authority_reference != request.authority_reference
    ):
        raise ValueError("ONLY_VERSIONED_SYNTHETIC_RECIPE_ALLOWED")
    start = datetime.now(TIAF_TIMEZONE)
    admit_training(
        request, grant, input_fingerprint=semantic_fingerprint(spec), root=store.root, at=start
    )
    attempt = TrainingAttempt(
        grant_reference=reference("authorization", grant),
        request_reference=reference("request", request),
    )
    # A request is single-attempt even if a caller supplies a newly named grant.
    for path in store.root.glob("attempt-*.json"):
        prior = store.get("attempt", path.stem.split("-", 1)[1])
        if (
            isinstance(prior, TrainingAttempt)
            and prior.request_reference == attempt.request_reference
        ):
            raise ValueError("SYNTHETIC_ATTEMPT_ALREADY_CONSUMED")
    store.put("authorization", grant)
    store.put("request", request)
    raw = (canonical_json(attempt) + "\n").encode()
    if store.bytes + len(raw) > 2 * 1024**3 or store.count + 1 > 65536:
        raise ValueError("RESEARCH_CORPUS_LIMIT")
    with store._path("attempt", cast(str, attempt.fingerprint)).open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    store.bytes += len(raw)
    store.count += 1
    if store.get("attempt", cast(str, attempt.fingerprint)) != attempt:
        raise ValueError("SYNTHETIC_CLAIM_NOT_PERSISTED")
    env = {
        name: "1"
        for name in (
            "OPENBLAS_NUM_THREADS",
            "OMP_NUM_THREADS",
            "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS",
            "BLIS_NUM_THREADS",
        )
    }
    env.update(PATH=os.defpath, PYTHONHASHSEED="1729")
    try:
        remaining = timeout_seconds - (time.monotonic() - tick)
        if remaining <= 0:
            raise subprocess.TimeoutExpired("synthetic", timeout_seconds)
        completed = subprocess.run(
            [sys.executable, "-m", "tiaf.learning.synthetic_trial_worker"],
            input=WorkerInput(
                spec=spec, request_reference=reference("request", request)
            ).model_dump_json(),
            text=True,
            capture_output=True,
            env=env,
            timeout=remaining,
            check=False,
        )
        if completed.returncode or len(completed.stdout.encode()) > 1024**2:
            raise ValueError("SYNTHETIC_WORKER_OUTPUT")
        output = strict_json(completed.stdout)
        if not isinstance(output, dict) or set(output) not in (
            {"status", "artifact"},
            {"status", "reason"},
        ):
            raise ValueError("SYNTHETIC_WORKER_PROTOCOL")
        job = SyntheticJob(
            **output,
            spec=spec,
            request_reference=reference("request", request),
            started_at=start,
            completed_at=datetime.now(TIAF_TIMEZONE),
            elapsed_seconds=time.monotonic() - tick,
            timeout_seconds=timeout_seconds,
        )
    except (subprocess.TimeoutExpired, OSError, ValueError) as exc:
        job = SyntheticJob(
            spec=spec,
            request_reference=reference("request", request),
            status="FAILED",
            reason="TRAINING_TIMEOUT"
            if isinstance(exc, subprocess.TimeoutExpired)
            else "SYNTHETIC_WORKER_FAILURE",
            started_at=start,
            completed_at=datetime.now(TIAF_TIMEZONE),
            elapsed_seconds=time.monotonic() - tick,
            timeout_seconds=timeout_seconds,
        )
    return persist_training(store, request, spec, job)
