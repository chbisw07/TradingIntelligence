"""Learning admission over immutable Evaluation outputs; no acquisition or A2 recalculation."""

from datetime import date, timedelta
from hashlib import sha256
from pathlib import Path

from pydantic import TypeAdapter

from tiaf.evaluation.forecast_retrospective_contracts import RetrospectiveQualification
from tiaf.forecasting.identity import semantic_fingerprint

from .forecast_artifacts import (
    Five,
    FoldManifest,
    PopulationAudit,
    TrainingGrant,
    TrainingInput,
    TrainingRow,
)


def read_bounded(path: Path, limit: int = 32 * 1024 * 1024) -> bytes:
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError("REGULAR_LOCAL_ARTIFACT_REQUIRED")
    with path.open("rb") as handle:
        raw = handle.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("ARTIFACT_SIZE_LIMIT")
    return raw


def load_qualification(
    path: Path, *, blob_sha256: str, dataset: Path, grant: TrainingGrant
) -> RetrospectiveQualification:
    """Verify approved bytes BEFORE decoding. Never parse the raw price dataset."""
    raw = read_bounded(path)
    if sha256(raw).hexdigest() != blob_sha256:
        raise ValueError("QUALIFICATION_BLOB_MISMATCH")
    if sha256(read_bounded(dataset)).hexdigest() != grant.dataset_fingerprint:
        raise ValueError("DATASET_FINGERPRINT_MISMATCH")
    # This is the already pinned native FF-1.1A qualification (up to 32 MiB),
    # NOT a v1 FF-0 captured record. Its approved byte hash is checked first;
    # do not widen or silently bypass FF-0's separate 1 MiB record contract.
    result = RetrospectiveQualification.model_validate_json(raw)
    validate_qualification(result, grant)
    return result


def validate_qualification(q: RetrospectiveQualification, grant: TrainingGrant) -> None:
    # Revalidate mutable audit metadata, seals and any model_construct/model_copy bypass.
    q = RetrospectiveQualification.model_validate(q.model_dump())
    TrainingGrant.model_validate(grant.model_dump())
    if not q.empirical_fitting_authorized:
        raise ValueError("EMPIRICAL_FITTING_NOT_AUTHORIZED")
    for actual, expected, reason in (
        (q.fingerprint, grant.qualification_fingerprint, "QUALIFICATION_STALE_OR_MISMATCH"),
        (q.dataset_fingerprint, grant.dataset_fingerprint, "DATASET_FINGERPRINT_MISMATCH"),
        (q.profile.fingerprint, grant.research_profile_fingerprint, "RESEARCH_PROFILE_MISMATCH"),
        (q.feature_schema.fingerprint, grant.feature_schema_fingerprint, "FEATURE_SCHEMA_MISMATCH"),
    ):
        if actual != expected:
            raise ValueError(reason)
    if q.assessed_at > grant.issued_at:
        raise ValueError("QUALIFICATION_POSTDATES_GRANT")
    ids = tuple(o.observation_id for o in q.observations)
    dates = tuple(o.reference_date for o in q.observations)
    if len(ids) != len(set(ids)) or dates != tuple(sorted(set(dates))) or len(ids) > 4096:
        raise ValueError("INVALID_QUALIFIED_POPULATION")
    if q.audit.get("holdout_status") != "SEALED" or q.profile.holdout_year != 2025:
        raise ValueError("HOLDOUT_POLICY_MISMATCH")
    for o in q.observations:
        protected = o.reference_date.year >= 2025 or (
            o.target_date is not None and o.target_date.year >= 2025
        )
        if protected and (o.label_state != "SEALED" or o.label is not None):
            raise ValueError("HOLDOUT_NOT_AUTHORIZED")


def prepare_training(
    q: RetrospectiveQualification, grant: TrainingGrant, year: int
) -> TrainingInput:
    validate_qualification(q, grant)
    if year not in grant.allowed_folds:
        raise ValueError("HOLDOUT_NOT_AUTHORIZED")
    fold = next(f for f in q.folds if f.test_year == year)
    requested = len(q.observations)
    buckets = {
        k: 0 for k in ("train", "ineligible", "purge_only", "embargo", "sealed", "later_unsealed")
    }
    rows: list[TrainingRow] = []
    purged: list[str] = []
    for o in q.observations:
        # Date/state guard precedes ANY access to features or labels.
        if (
            o.reference_date.year >= 2025
            or (o.target_date is not None and o.target_date.year >= 2025)
            or o.label_state == "SEALED"
        ):
            buckets["sealed"] += 1
            continue
        if o.reference_date.year >= year:
            buckets["later_unsealed"] += 1
            continue
        if o.reference_date < date(2018, 1, 1):
            raise ValueError("TRAINING_SCOPE_MISMATCH")
        if o.target_closes_at is None or o.target_opens_at is None:
            raise ValueError("TRAINING_TARGET_CLOCK_MISSING")
        # Availability includes even an ineligible label's conservative scheduled clock.
        if o.target_closes_at + timedelta(minutes=30) >= fold.fit_cutoff:
            purged.append(o.observation_id)
            bucket = "embargo" if o.reference_date == fold.embargo_date else "purge_only"
            buckets[bucket] += 1
            continue
        if o.features is None or o.label is None:
            buckets["ineligible"] += 1
            continue
        if (
            o.information_cutoff >= fold.fit_cutoff
            or o.assumed_label_available_at is None
            or o.assumed_label_available_at >= fold.fit_cutoff
            or o.target_date is None
            or o.features.feature_schema != q.feature_schema
        ):
            raise ValueError("TRAINING_LEAKAGE_OR_SCHEMA_MISMATCH")
        rows.append(
            TrainingRow(
                observation_id=o.observation_id,
                reference_date=o.reference_date,
                target_date=o.target_date,
                label_available_at=o.assumed_label_available_at,
                values=TypeAdapter(Five).validate_python(o.features.values),
                label=o.label,
            )
        )
        buckets["train"] += 1
    ids = tuple(r.observation_id for r in rows)
    positive = sum(r.label for r in rows)
    if (
        ids != fold.train_ids
        or tuple(purged) != fold.purged_ids
        or (positive != fold.train_positive or len(rows) - positive != fold.train_zero)
    ):
        raise ValueError("QUALIFIED_FOLD_MEMBERSHIP_MISMATCH")
    if not rows:
        raise ValueError("INSUFFICIENT_TRAINING_DATA")
    manifest = FoldManifest(
        grant=grant,
        fold_id=year,
        fit_cutoff=fold.fit_cutoff,
        embargo_date=fold.embargo_date,
        train_start=rows[0].reference_date,
        train_end=rows[-1].reference_date,
        observation_ids=ids,
        observation_order_fingerprint=semantic_fingerprint(ids),
        training_values_fingerprint=semantic_fingerprint(tuple(rows)),
        audit=PopulationAudit.model_validate(
            {
                "requested": requested,
                "positive": positive,
                "zero": len(rows) - positive,
                **buckets,
            }
        ),
    )
    return TrainingInput(manifest=manifest, rows=tuple(rows))
