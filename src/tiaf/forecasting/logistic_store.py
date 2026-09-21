"""Explicit research-v2 Capture Store profile; FF-0 store/rights remain unchanged.

Single-writer, exclusive content-addressed writes, <=64 references/shard, <=1 MiB
per record, <=65,536 blobs and <=2 GiB. No mutable alias, outcome store, pickle,
database or cross-file atomicity claim. A crash cannot create a COMPLETE parent.
"""

import os
import re
import stat
from collections import Counter
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Annotated, Literal, cast

from pydantic import Field

from tiaf.forecasting.capture import strict_json
from tiaf.forecasting.identity import canonical_json
from tiaf.forecasting.logistic_forecasts import (
    FoldPopulation,
    ForecastShard,
    LogisticForecastRun,
    ResearchForecastResult,
    model_for,
    validate_handoff,
)
from tiaf.forecasting.research_contracts import ResearchContract
from tiaf.learning.forecast_artifacts import (
    Five,
    LogisticArtifact,
    ScalerArtifact,
    SealedResearch,
    reconstruct,
)
from tiaf.learning.forecast_jobs import TrainingRun
from tiaf.learning.forecast_training import read_bounded

_KINDS: dict[str, type[SealedResearch]] = {
    "training": TrainingRun,
    "model": LogisticArtifact,
    "scaler": ScalerArtifact,
    "capture": ResearchForecastResult,
    "shard": ForecastShard,
    "run": LogisticForecastRun,
}


class ResearchForecastStore:
    def __init__(self, root: Path, *, create: bool = False) -> None:
        if (
            not root.is_absolute()
            or root == Path("/")
            or ".." in root.parts
            or any(p.is_symlink() for p in (root, *root.parents))
        ):
            raise ValueError("UNSAFE_RESEARCH_CORPUS_ROOT")
        if create:
            root.mkdir(parents=True, exist_ok=False)
        if not root.is_dir():
            raise ValueError("RESEARCH_CORPUS_MISSING")
        self.root = root
        self.writable = create
        self.bytes = 0
        self.count = 0
        self._forecast_ids: dict[str, str] = {}
        for path in root.iterdir():
            if (
                path.is_symlink()
                or not stat.S_ISREG(path.stat().st_mode)
                or not re.fullmatch(r"[a-z]+-[a-f0-9]{64}\.json", path.name)
            ):
                raise ValueError("UNSAFE_RESEARCH_CORPUS_ENTRY")
            size = path.stat().st_size
            if size > 1024 * 1024:
                raise ValueError("RESEARCH_RECORD_LIMIT")
            self.bytes += size
            self.count += 1
            self._bounds()

    def _bounds(self) -> None:
        if self.bytes > 2 * 1024**3 or self.count > 65536:
            raise ValueError("RESEARCH_CORPUS_LIMIT")

    def _path(self, kind: str, fingerprint: str) -> Path:
        if kind not in _KINDS or not re.fullmatch(r"[a-f0-9]{64}", fingerprint):
            raise ValueError("INVALID_RESEARCH_REFERENCE")
        if any(p.is_symlink() for p in (self.root, *self.root.parents)):
            raise ValueError("UNSAFE_RESEARCH_CORPUS_ROOT")
        return self.root / f"{kind}-{fingerprint}.json"

    def put(self, kind: str, value: SealedResearch) -> str:
        if not self.writable:
            raise ValueError("READ_ONLY_RESEARCH_CORPUS")
        if kind not in _KINDS or type(value) is not _KINDS[kind]:
            raise ValueError("RESEARCH_RECORD_KIND_MISMATCH")
        value = type(value).model_validate(value.model_dump())
        fp = cast(str, value.fingerprint)
        if isinstance(value, ResearchForecastResult):
            previous = self._forecast_ids.get(value.forecast_id)
            if previous is not None and previous != fp:
                raise ValueError("DUPLICATE_SCIENTIFIC_FORECAST_ID")
        raw = (canonical_json(value) + "\n").encode()
        if len(raw) > 1024 * 1024:
            raise ValueError("RESEARCH_RECORD_LIMIT")
        path = self._path(kind, fp)
        if path.exists():
            if self.get(kind, fp) != value:
                raise ValueError("RESEARCH_DUPLICATE_CONFLICT")
            return fp
        if self.bytes + len(raw) > 2 * 1024**3 or self.count + 1 > 65536:
            raise ValueError("RESEARCH_CORPUS_LIMIT")
        with path.open("xb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        self.bytes += len(raw)
        self.count += 1
        if isinstance(value, ResearchForecastResult):
            self._forecast_ids[value.forecast_id] = fp
        if self.get(kind, fp) != value:
            raise ValueError("RESEARCH_CAPTURE_ROUND_TRIP_MISMATCH")
        return fp

    def get(self, kind: str, fingerprint: str) -> SealedResearch:
        path = self._path(kind, fingerprint)
        raw = read_bounded(path, limit=1024 * 1024)
        payload = strict_json(raw.decode())
        if not isinstance(payload, dict) or payload.get("fingerprint") != fingerprint:
            raise ValueError("RESEARCH_RECORDED_SEAL_MISSING")
        value = _KINDS[kind].model_validate(payload)
        if raw != (canonical_json(value) + "\n").encode():
            raise ValueError("RESEARCH_BLOB_NOT_CANONICAL")
        return value


def capture_training(store: ResearchForecastStore, run: TrainingRun) -> None:
    validate_handoff(run)
    store.put("training", run)
    for fold in run.grant.allowed_folds:
        model = model_for(run, fold)
        store.put("model", model)
        store.put("scaler", model.reconstruction.scaler)


class Verification(ResearchContract):
    status: Literal["MATCH", "MISMATCH"]
    matches: int
    mismatches: int
    tolerance: Annotated[float, Field(strict=True, ge=1e-12, le=1e-12)] = 1e-12
    reason: str


def verify_records(
    store: ResearchForecastStore, records: Iterable[ResearchForecastResult], training: TrainingRun
) -> None:
    """Data-only pinned verification; never imports an estimator or reads truth."""
    validate_handoff(training)
    models = {}
    for fold in training.grant.allowed_folds:
        expected = model_for(training, fold)
        model = store.get("model", cast(str, expected.fingerprint))
        scaler = store.get("scaler", cast(str, expected.reconstruction.scaler.fingerprint))
        if model != expected or scaler != expected.reconstruction.scaler:
            raise ValueError("REPLAY_MODEL_SCALER_MISMATCH")
        models[fold] = expected
    seen: set[str] = set()
    for r in records:
        # Reconstruct, do not trust model_copy/construct to preserve seals.
        r = ResearchForecastResult.model_validate(r.model_dump())
        q = r.request
        m = models[q.fold_id]
        g = training.grant
        if (
            r.forecast_id in seen
            or q.training_run_fingerprint != training.fingerprint
            or q.composition.model_fingerprint != m.fingerprint
            or q.composition.scaler_fingerprint != m.reconstruction.scaler.fingerprint
            or q.composition.model_scientific_fingerprint != m.scientific_fingerprint
            or q.qualification_fingerprint != g.qualification_fingerprint
            or q.dataset_fingerprint != g.dataset_fingerprint
            or q.research_profile_fingerprint != g.research_profile_fingerprint
            or q.feature_schema_fingerprint != g.feature_schema_fingerprint
            or q.dependency_lock_fingerprint != g.dependency_lock_fingerprint
            or m.manifest.fit_cutoff >= q.origin.information_cutoff
            or r.computed_at < training.created_at
        ):
            raise ValueError("REPLAY_LINEAGE_MISMATCH")
        seen.add(r.forecast_id)
        if r.output is not None:
            assert q.origin.features is not None
            expected_p = reconstruct(m.reconstruction, cast(Five, q.origin.features.values))
            if abs(expected_p - r.output.probability) > 1e-12:
                raise ValueError("REPLAY_PROBABILITY_MISMATCH")


def _records(
    store: ResearchForecastStore, parent: LogisticForecastRun
) -> Iterator[ResearchForecastResult]:
    count = 0
    for shard_fp in parent.shards:
        shard = cast(ForecastShard, store.get("shard", shard_fp))
        for fp in shard.captures:
            count += 1
            if count > 4096:
                raise ValueError("REPLAY_POPULATION_LIMIT")
            yield cast(ResearchForecastResult, store.get("capture", fp))


def recorded_replay(
    store: ResearchForecastStore, fingerprint: str
) -> tuple[LogisticForecastRun, tuple[ResearchForecastResult, ...], TrainingRun]:
    """Bounded materialized convenience view; pinned verification streams instead."""
    parent = cast(LogisticForecastRun, store.get("run", fingerprint))
    training = cast(TrainingRun, store.get("training", parent.training_run_fingerprint))
    return parent, tuple(_records(store, parent)), training


def verify_run(store: ResearchForecastStore, fingerprint: str) -> Verification:
    try:
        parent = cast(LogisticForecastRun, store.get("run", fingerprint))
        training = cast(TrainingRun, store.get("training", parent.training_run_fingerprint))
        counts: Counter[tuple[int, str]] = Counter()
        reasons: dict[int, Counter[str]] = {f: Counter() for f in training.grant.allowed_folds}

        def checked_rows() -> Iterator[ResearchForecastResult]:
            previous = None
            for r in _records(store, parent):
                day = r.request.origin.reference_date
                if (
                    (previous is not None and day <= previous)
                    or r.computed_at > parent.created_at
                    or any(
                        getattr(parent, key) != getattr(r.request, key)
                        for key in (
                            "qualification_blob",
                            "qualification_fingerprint",
                            "dataset_fingerprint",
                            "research_profile_fingerprint",
                            "feature_schema_fingerprint",
                            "dependency_lock_fingerprint",
                            "training_run_fingerprint",
                        )
                    )
                ):
                    raise ValueError("REPLAY_PARENT_LINEAGE_OR_ORDER_MISMATCH")
                previous = day
                counts[r.request.fold_id, r.status] += 1
                counts[r.request.fold_id, "CANDIDATE"] += 1
                reasons[r.request.fold_id].update(r.reasons)
                yield r

        # Only one row/shard plus the four pinned models is materialized at once.
        verify_records(store, checked_rows(), training)
        expected = tuple(
            FoldPopulation(
                fold_id=f,
                candidate=counts[f, "CANDIDATE"],
                eligible=counts[f, "GENERATED"],
                generated=counts[f, "GENERATED"],
                unavailable=counts[f, "UNAVAILABLE"],
                excluded=counts[f, "EXCLUDED"],
                protected=counts[f, "PROTECTED"],
                reason_counts=tuple(sorted(reasons[f].items())),
            )
            for f in training.grant.allowed_folds
        )
        total = sum(p.candidate for p in expected)
        if expected != parent.populations or total != parent.verification_matches:
            raise ValueError("REPLAY_PARENT_POPULATION_MISMATCH")
        return Verification(status="MATCH", matches=total, mismatches=0, reason="VERIFIED")
    except (ValueError, OSError, KeyError, AssertionError):
        return Verification(
            status="MISMATCH",
            matches=0,
            mismatches=1,
            reason="CORPUS_INTEGRITY_OR_PINNED_RECONSTRUCTION_FAILED",
        )
