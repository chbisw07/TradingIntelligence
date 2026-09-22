"""Bounded serial Learning jobs and append-only local research artifact custody.

No active-model alias/registry service, public runtime binding or FF-0 store change.
Only data-only artifacts are stored; existing qualification is pinned externally.
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.capture import strict_json
from tiaf.forecasting.identity import ForecastDateTime, canonical_json

from .forecast_artifacts import (
    FifthFoldGrant,
    Finite,
    LogisticArtifact,
    SealedResearch,
    TrainingGrant,
    TrainingInput,
)
from .forecast_training import read_bounded


class _TrainingJob(SealedResearch):
    fold_id: int
    grant_fingerprint: str
    manifest_fingerprint: str
    status: Literal["TRAINED", "UNAVAILABLE", "FAILED"]
    reason: str | None = None
    artifact: LogisticArtifact | None = None
    started_at: ForecastDateTime
    completed_at: ForecastDateTime
    elapsed_seconds: Annotated[Finite, Field(ge=0)]
    cpu_seconds: Annotated[Finite, Field(ge=0)] | None = None
    peak_rss_kib: int | None = None
    # Linux lifetime ru_maxrss can include the parent's fork/exec launch high-water.
    # The enforced post-launch worker limits are reported independently.
    address_space_limit_bytes: Literal[536870912] | None = None
    cpu_limit_seconds: Literal[60] | None = None
    monetary_cost: Literal["UNPRICED"] = "UNPRICED"
    attempts: Literal[1] = 1

    @model_validator(mode="after")
    def outcome(self) -> Self:
        if (self.status == "TRAINED") != (self.artifact is not None):
            raise ValueError("JOB_ARTIFACT_STATUS_MISMATCH")
        if (self.status == "TRAINED") != (self.reason is None):
            raise ValueError("JOB_REASON_STATUS_MISMATCH")
        if self.completed_at < self.started_at:
            raise ValueError("JOB_CLOCK_ORDER")
        if self.artifact is not None and (
            self.artifact.manifest.fingerprint != self.manifest_fingerprint
            or self.artifact.manifest.grant.fingerprint != self.grant_fingerprint
            or self.artifact.manifest.fold_id != self.fold_id
            or self.address_space_limit_bytes != 536870912
            or self.cpu_limit_seconds != 60
        ):
            raise ValueError("JOB_ARTIFACT_LINEAGE_MISMATCH")
        return self


class TrainingJob(_TrainingJob):
    fold_id: Literal[2021, 2022, 2023, 2024]


class FifthTrainingJob(_TrainingJob):
    fold_id: Literal[2025] = 2025

    @model_validator(mode="after")
    def fifth_authority(self) -> Self:
        if self.artifact is not None and not isinstance(
            self.artifact.manifest.grant, FifthFoldGrant
        ):
            raise ValueError("FIFTH_AUTHORITY_REQUIRED")
        return self


class TrainingRun(SealedResearch):
    grant: TrainingGrant
    jobs: tuple[TrainingJob, ...] = Field(max_length=4)
    created_at: ForecastDateTime
    status: Literal["COMPLETE", "PARTIAL", "FAILED"]
    holdout_status: Literal["SEALED"] = "SEALED"
    evaluation_metrics: Literal[0] = 0
    forecast_records: Literal[0] = 0
    external_calls: Literal[0] = 0

    @model_validator(mode="after")
    def complete(self) -> Self:
        ids = tuple(j.fold_id for j in self.jobs)
        if ids != self.grant.allowed_folds[: len(ids)] or any(
            j.grant_fingerprint != self.grant.fingerprint for j in self.jobs
        ):
            raise ValueError("RUN_JOB_LINEAGE_MISMATCH")
        done = ids == self.grant.allowed_folds and all(j.status == "TRAINED" for j in self.jobs)
        if done != (self.status == "COMPLETE"):
            raise ValueError("RUN_COMPLETION_MISMATCH")
        return self


def run_fit(request: TrainingInput) -> TrainingJob:
    if not isinstance(request.manifest.grant, TrainingGrant):
        raise ValueError("DEVELOPMENT_GRANT_REQUIRED")
    return _run_fit(request, TrainingJob)


def _run_fit[Job: _TrainingJob](request: TrainingInput, job_type: type[Job]) -> Job:
    request = TrainingInput.model_validate(request.model_dump())
    m = request.manifest
    start = datetime.now(TIAF_TIMEZONE)
    tick = time.monotonic()
    # No inherited .env, credentials, PYTHONPATH or provider configuration.
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
    env["PYTHONHASHSEED"] = "1729"
    env["PATH"] = os.defpath
    result: dict[str, object]
    if len(request.model_dump_json().encode()) > 1024 * 1024:
        result = {"status": "FAILED", "reason": "WORKER_INPUT_LIMIT"}
    else:
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "tiaf.learning.forecast_worker"],
                input=request.model_dump_json(),
                text=True,
                capture_output=True,
                env=env,
                timeout=m.grant.fit_timeout_seconds,
                check=False,
            )
            if completed.returncode != 0:
                result = {"status": "FAILED", "reason": "WORKER_TERMINATED_OR_RESOURCE_LIMIT"}
            elif len(completed.stdout) > 1024 * 1024:
                result = {"status": "FAILED", "reason": "WORKER_OUTPUT_LIMIT"}
            else:
                decoded = strict_json(completed.stdout)
                if not isinstance(decoded, dict):
                    raise ValueError("INVALID_WORKER_RESULT")
                result = decoded
        except subprocess.TimeoutExpired:
            result = {"status": "FAILED", "reason": "RESOURCE_LIMIT_EXCEEDED"}
        except (ValueError, OSError):
            result = {"status": "FAILED", "reason": "INVALID_WORKER_RESULT"}
    fields = dict(
        fold_id=m.fold_id,
        grant_fingerprint=m.grant.fingerprint,
        manifest_fingerprint=m.fingerprint,
        started_at=start,
        completed_at=datetime.now(TIAF_TIMEZONE),
        elapsed_seconds=time.monotonic() - tick,
    )
    try:
        return job_type.model_validate({**fields, **result})
    except ValueError:
        return job_type.model_validate(
            {
                **fields,
                "status": "FAILED",
                "reason": "INVALID_WORKER_ARTIFACT",
            }
        )


class TrainingStore:
    """A new private attempt directory; append-only jobs, content-addressed JSON blobs.

    Strict 1 MiB records/32 MiB total here (well below the research campaign grant).
    No market rows or executable serialization. Crash leaves an explicit incomplete
    attempt: grant/jobs but no COMPLETE run. A new directory requires a new grant.
    """

    def __init__(self, root: Path, grant: TrainingGrant) -> None:
        if (
            not root.is_absolute()
            or root == Path("/")
            or any(p.is_symlink() for p in (root, *root.parents))
        ):
            raise ValueError("UNSAFE_TRAINING_ROOT")
        root.mkdir(parents=True, exist_ok=False)
        self.root = root
        self._bytes = 0
        self.put("grant", grant)

    def put(self, kind: str, value: SealedResearch) -> Path:
        if kind not in {"grant", "manifest", "scaler", "model", "job", "run"}:
            raise ValueError("UNKNOWN_TRAINING_ARTIFACT_KIND")
        # Defensive reconstruction before persistence; never trust a copied seal.
        value = type(value).model_validate(value.model_dump())
        raw = (canonical_json(value) + "\n").encode()
        if len(raw) > 1024 * 1024 or self._bytes + len(raw) > 32 * 1024 * 1024:
            raise ValueError("TRAINING_STORE_LIMIT")
        path = self.root / f"{kind}-{value.fingerprint}.json"
        with path.open("xb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        self._bytes += len(raw)
        replayed = type(value).model_validate(strict_json(read_bounded(path).decode()))
        if replayed != value:
            raise ValueError("TRAINING_ARTIFACT_ROUND_TRIP_MISMATCH")
        return path
