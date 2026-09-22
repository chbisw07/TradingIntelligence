"""Single-attempt fifth-fold custody and non-fitting offline handoff verification."""

import os
from datetime import datetime
from types import MappingProxyType
from typing import Literal, Self, cast

from pydantic import model_validator

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.identity import ForecastDateTime, canonical_json
from tiaf.forecasting.logistic_store import ResearchForecastStore
from tiaf.planner.models import Sha256

from .forecast_artifacts import (
    FIFTH_CUTOFF,
    FifthFoldGrant,
    Five,
    LogisticArtifact,
    ScalerArtifact,
    SealedResearch,
    reconstruct,
)
from .forecast_fifth_preparation import FifthBaseRateState, FifthPreparation
from .forecast_jobs import FifthTrainingJob, _run_fit


class FifthAttempt(SealedResearch):
    authority: Sha256
    preparation: Sha256
    consumed_before_worker: Literal[True] = True
    attempts: Literal[1] = 1


class FifthHandoff(SealedResearch):
    handoff_version: Literal["ff1.pre_holdout.fifth_fold/1.0"] = "ff1.pre_holdout.fifth_fold/1.0"
    fold_id: Literal[2025] = 2025
    cutoff: ForecastDateTime = FIFTH_CUTOFF
    authority_fingerprint: Sha256
    preparation_fingerprint: Sha256
    attempt_fingerprint: Sha256
    job_fingerprint: Sha256
    qualification_fingerprint: Sha256
    dataset_fingerprint: Sha256
    research_profile_fingerprint: Sha256
    feature_schema_id: Literal["ff1.reliance.a2_daily_five/1.0"] = "ff1.reliance.a2_daily_five/1.0"
    training_population_fingerprint: Sha256
    training_values_fingerprint: Sha256
    scaler_fingerprint: Sha256
    model_artifact_fingerprint: Sha256
    baserate_state_fingerprint: Sha256
    dependency_lock_fingerprint: Sha256
    holdout_status: Literal["SEALED"] = "SEALED"
    protected_outcome_access: Literal["NONE"] = "NONE"
    post_holdout_refit_allowed: Literal[False] = False
    forecast_generation: Literal["DEFERRED_TO_ONE_SHOT_EVALUATION"] = (
        "DEFERRED_TO_ONE_SHOT_EVALUATION"
    )
    forecast_records: Literal[0] = 0
    evaluation_metrics: Literal[0] = 0
    final_protocol_frozen: Literal[False] = False
    engineering_probe_probabilities: Five
    created_at: ForecastDateTime

    @model_validator(mode="after")
    def fixed_scope(self) -> Self:
        if self.cutoff != FIFTH_CUTOFF or self.created_at <= self.cutoff:
            raise ValueError("FIFTH_HANDOFF_SCOPE")
        return self


class FifthStore(ResearchForecastStore):
    record_types = MappingProxyType(
        {
            "authority": FifthFoldGrant,
            "preparation": FifthPreparation,
            "attempt": FifthAttempt,
            "job": FifthTrainingJob,
            "model": LogisticArtifact,
            "scaler": ScalerArtifact,
            "baseline": FifthBaseRateState,
            "handoff": FifthHandoff,
        }
    )


def execute_once(store: FifthStore, preparation: FifthPreparation) -> str:
    """Caller supplies a new private store. Any existing attempt is terminal, even failed."""
    if not store.writable or tuple(store.root.glob("attempt-*.json")):
        raise ValueError("FIFTH_ATTEMPT_ALREADY_CONSUMED_OR_READ_ONLY")
    preparation = FifthPreparation.model_validate(preparation.model_dump())
    m = preparation.training.manifest
    assert isinstance(m.grant, FifthFoldGrant)
    if m.audit.train < 500 or min(m.audit.positive, m.audit.zero) < 100:
        raise ValueError("FIFTH_TRAINING_SUPPORT_INSUFFICIENT")
    if preparation.baseline.output is None:
        raise ValueError("FIFTH_BASERATE_SUPPORT_INSUFFICIENT")
    authority = store.put("authority", m.grant)
    prep = store.put("preparation", preparation)
    baseline = store.put("baseline", preparation.baseline)
    attempt = FifthAttempt(authority=authority, preparation=prep)
    # Unlike idempotent put(), exclusive creation is the attempt-consumption boundary.
    # Deterministic claim identity has no fresh timestamp to permit a retry.
    path = store._path("attempt", cast(str, attempt.fingerprint))
    with path.open("xb") as handle:
        handle.write((canonical_json(attempt) + "\n").encode())
        handle.flush()
        os.fsync(handle.fileno())
    if store.get("attempt", cast(str, attempt.fingerprint)) != attempt:
        raise ValueError("FIFTH_ATTEMPT_NOT_PERSISTED")
    job = _run_fit(preparation.training, FifthTrainingJob)
    job_fp = store.put("job", job)
    if job.artifact is None:
        raise ValueError("FIFTH_WORKER_NOT_TRAINED_NO_RETRY")
    model = store.put("model", job.artifact)
    scaler = store.put("scaler", job.artifact.reconstruction.scaler)
    return store.put(
        "handoff",
        FifthHandoff(
            authority_fingerprint=authority,
            preparation_fingerprint=prep,
            attempt_fingerprint=cast(str, attempt.fingerprint),
            job_fingerprint=job_fp,
            qualification_fingerprint=m.grant.qualification_fingerprint,
            dataset_fingerprint=m.grant.dataset_fingerprint,
            research_profile_fingerprint=m.grant.research_profile_fingerprint,
            training_population_fingerprint=m.observation_order_fingerprint,
            training_values_fingerprint=m.training_values_fingerprint,
            scaler_fingerprint=scaler,
            model_artifact_fingerprint=model,
            baserate_state_fingerprint=baseline,
            dependency_lock_fingerprint=m.grant.dependency_lock_fingerprint,
            engineering_probe_probabilities=cast(
                Five,
                tuple(
                    reconstruct(
                        job.artifact.reconstruction,
                        cast(
                            Five,
                            tuple(
                                x + k * s
                                for x, s in zip(
                                    job.artifact.reconstruction.scaler.means,
                                    job.artifact.reconstruction.scaler.scales,
                                    strict=True,
                                )
                            ),
                        ),
                    )
                    for k in (0.0, 1.0, -1.0, 1e6, -1e6)
                ),
            ),
            created_at=datetime.now(TIAF_TIMEZONE),
        ),
    )


def verify_fifth(store: FifthStore, handoff_fp: str) -> str:
    """No worker/NumPy/sklearn, source files, forecast generation or quality metrics."""
    try:
        h = cast(FifthHandoff, store.get("handoff", handoff_fp))
        a = cast(FifthFoldGrant, store.get("authority", h.authority_fingerprint))
        p = cast(FifthPreparation, store.get("preparation", h.preparation_fingerprint))
        claim = cast(FifthAttempt, store.get("attempt", h.attempt_fingerprint))
        job = cast(FifthTrainingJob, store.get("job", h.job_fingerprint))
        model = cast(LogisticArtifact, store.get("model", h.model_artifact_fingerprint))
        scaler = cast(ScalerArtifact, store.get("scaler", h.scaler_fingerprint))
        b = cast(FifthBaseRateState, store.get("baseline", h.baserate_state_fingerprint))
        m = p.training.manifest
        if (
            m.grant != a
            or job.artifact != model
            or model.manifest != m
            or model.reconstruction.scaler != scaler
            or b != p.baseline
            or b.output is None
            or claim.authority != a.fingerprint
            or claim.preparation != p.fingerprint
            or job.started_at < a.issued_at
            or h.created_at < job.completed_at
            or h.qualification_fingerprint != a.qualification_fingerprint
            or h.dataset_fingerprint != a.dataset_fingerprint
            or h.research_profile_fingerprint != a.research_profile_fingerprint
            or h.training_population_fingerprint != m.observation_order_fingerprint
            or h.training_values_fingerprint != m.training_values_fingerprint
            or h.dependency_lock_fingerprint != a.dependency_lock_fingerprint
        ):
            raise ValueError("FIFTH_HANDOFF_LINEAGE_MISMATCH")
        # Reconstruct TRAIN scaler from captured values, no fit/library needed.
        # Same float64 policy; ordinary summation error gets a scale-aware tolerance.
        for i in range(5):
            mean = sum(r.values[i] for r in p.training.rows) / len(p.training.rows)
            variance = sum((r.values[i] - mean) ** 2 for r in p.training.rows) / len(
                p.training.rows
            )
            if abs(mean - scaler.means[i]) > 1e-12 * max(1.0, abs(mean)) or abs(
                variance - scaler.variances[i]
            ) > 1e-12 * max(1.0, abs(variance)):
                raise ValueError("FIFTH_SCALER_RECONSTRUCTION_MISMATCH")
        for index, k in enumerate((0.0, 1.0, -1.0, 1e6, -1e6)):
            values = tuple(x + k * s for x, s in zip(scaler.means, scaler.scales, strict=True))
            probability = reconstruct(model.reconstruction, cast(Five, values))
            if not 0 <= probability <= 1 or probability != h.engineering_probe_probabilities[index]:
                raise ValueError("FIFTH_ENGINEERING_RECONSTRUCTION")
        return "MATCH"
    except (ValueError, OSError, LookupError, AssertionError):
        return "MISMATCH"
