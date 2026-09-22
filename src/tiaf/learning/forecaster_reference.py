"""Bounded synthetic FLC-2 trainer adapter over the existing isolated worker.

Not a general fit endpoint: no caller-supplied observations, empirical input,
optimizer, retries, scientific evaluation, lifecycle transition or activation.
The native RELIANCE labels/schema are codec compatibility, NOT market data.
"""

import os
from datetime import date, datetime, timedelta
from typing import cast

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.identity import ForecastDateTime, canonical_json, semantic_fingerprint

from .forecast_artifacts import (
    FoldManifest,
    PopulationAudit,
    TrainingGrant,
    TrainingInput,
    TrainingRow,
)
from .forecast_jobs import run_fit
from .forecaster_authority import TrainingAttempt, TrainingAuthorization, admit_training
from .forecaster_custody import ForecasterStore, persist_training
from .forecaster_training import TrainingBundle, TrainingIdentity, logistic_request, reference

RECIPE = "flc2.synthetic.integer-patterns.600.v1"


def synthetic_input(
    *,
    issued_at: ForecastDateTime,
    dependency_lock_fingerprint: str,
    code_fingerprint: str,
) -> TrainingInput:
    """Fresh authored engineering data only. Pins/clocks are explicit, not ambient."""
    rows = tuple(
        TrainingRow(
            observation_id=f"ff1-adjusted:RELIANCE:{date(2018, 1, 1) + timedelta(days=i)}",
            reference_date=date(2018, 1, 1) + timedelta(days=i),
            target_date=date(2018, 1, 2) + timedelta(days=i),
            label_available_at=datetime(2018, 1, 2, 16, tzinfo=TIAF_TIMEZONE) + timedelta(days=i),
            values=(float(i % 3), float(i % 5), float(i % 7), float(i % 11), 7.0),
            label=i % 2,
        )
        for i in range(600)
    )
    grant = TrainingGrant(
        grant_id="flc2.synthetic.reference",
        basis="SYNTHETIC_ENGINEERING",
        qualification_fingerprint=semantic_fingerprint((RECIPE, "SYNTHETIC_NOT_EMPIRICAL")),
        dataset_fingerprint=semantic_fingerprint(rows),
        research_profile_fingerprint=semantic_fingerprint(RECIPE),
        feature_schema_fingerprint=semantic_fingerprint((RECIPE, "five-integer-patterns")),
        protocol_fingerprint=semantic_fingerprint((RECIPE, "one-fit-no-evaluation")),
        dependency_lock_fingerprint=dependency_lock_fingerprint,
        code_fingerprint=code_fingerprint,
        issued_at=issued_at,
    )
    ids = tuple(r.observation_id for r in rows)
    manifest = FoldManifest(
        grant=grant,
        fold_id=2021,
        fit_cutoff=datetime(2020, 12, 31, 9, 15, tzinfo=TIAF_TIMEZONE),
        embargo_date=date(2020, 12, 31),
        train_start=rows[0].reference_date,
        train_end=rows[-1].reference_date,
        observation_ids=ids,
        observation_order_fingerprint=semantic_fingerprint(ids),
        training_values_fingerprint=semantic_fingerprint(rows),
        audit=PopulationAudit(
            requested=600,
            train=600,
            positive=300,
            zero=300,
            ineligible=0,
            purge_only=0,
            embargo=0,
            sealed=0,
            later_unsealed=0,
        ),
    )
    return TrainingInput(manifest=manifest, rows=rows)


def execute_synthetic_once(
    store: ForecasterStore,
    request: TrainingIdentity,
    authorization: TrainingAuthorization,
) -> TrainingBundle:
    """Consume exact external authority before worker launch, even on failure/crash.

    Caller owns the new attempt store; reopening is read-only. A different store,
    candidate, version or input requires new external experiment/authority pins.
    """
    if not store.writable or tuple(store.root.glob("attempt-*.json")):
        raise ValueError("TRAINING_ATTEMPT_CONSUMED_OR_READ_ONLY")
    # No input argument exists: only the versioned synthetic recipe can reach fit.
    data = synthetic_input(
        issued_at=request.created_at,
        dependency_lock_fingerprint=request.dependency_lock_fingerprint,
        code_fingerprint=request.implementation_fingerprint,
    )
    at = datetime.now(TIAF_TIMEZONE)
    admit_training(
        request,
        authorization,
        input_fingerprint=semantic_fingerprint(data),
        root=store.root,
        at=at,
    )
    if request != logistic_request(
        data.manifest,
        request.experiment,
        created_at=request.created_at,
        purpose="SYNTHETIC_ENGINEERING",
    ):
        raise ValueError("ONLY_COMPILED_SYNTHETIC_RECIPE_ALLOWED")
    store.put("authorization", authorization)
    store.put("request", request)
    attempt = TrainingAttempt(
        grant_reference=reference("authorization", authorization),
        request_reference=reference("request", request),
    )
    # Existing fifth-fold exclusive-claim pattern; idempotent put is NOT a claim.
    raw = (canonical_json(attempt) + "\n").encode()
    if store.bytes + len(raw) > 2 * 1024**3 or store.count + 1 > 65536:
        raise ValueError("RESEARCH_CORPUS_LIMIT")
    path = store._path("attempt", cast(str, attempt.fingerprint))
    with path.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    store.bytes += len(raw)
    store.count += 1
    if store.get("attempt", cast(str, attempt.fingerprint)) != attempt:
        raise ValueError("ATTEMPT_PERSISTENCE_MISMATCH")
    job = run_fit(data)
    return persist_training(store, request, data.manifest, job)
