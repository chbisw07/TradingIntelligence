"""INTERNAL FF-1.3: four fixed Logistic folds; offline, no outcomes or quality scoring."""

import argparse
import platform
import subprocess
import time
from datetime import datetime
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import cast

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.identity import canonical_json
from tiaf.forecasting.logistic_forecasts import (
    ForecastShard,
    LogisticForecastRun,
    generate,
    population,
    validate_handoff,
)
from tiaf.forecasting.logistic_projection import project_qualification
from tiaf.forecasting.logistic_store import (
    ResearchForecastStore,
    capture_training,
    verify_records,
    verify_run,
)
from tiaf.learning.forecast_artifacts import LogisticArtifact, ScalerArtifact
from tiaf.learning.forecast_jobs import TrainingRun
from tiaf.learning.forecast_training import read_bounded

ROOT = Path(__file__).resolve().parents[1]
LOCK_SHA = "54e8577800d2a9132df2c8d3721e0d880da9e706a58f6d8b9beba75338e0ac86"
QUALIFICATION_BLOB = "69333427ebb355672d67e19885ba83a659a0427c8760cce4eac717c49a87d4ca"
TRAINING_FP = "f26605528584a68449396da9dea1a3e28d6e2295f355a7085887e5adedc94406"
QUALIFICATION = ROOT / "data/ff1/adjusted_qualification_20260921_clock_review/qualification.json"
TRAINING = ROOT / f"data/ff1/logistic_training_20260921/run-{TRAINING_FP}.json"
VERSIONS = {
    "scikit-learn": "1.7.2",
    "numpy": "2.3.3",
    "scipy": "1.16.2",
    "joblib": "1.5.2",
    "threadpoolctl": "3.6.0",
}


def check_dependencies() -> None:
    try:
        installed = {name: version(name) for name in VERSIONS}
    except PackageNotFoundError as exc:
        raise ValueError("DEPENDENCY_MISSING_NO_INSTALLATION") from exc
    if (
        platform.python_version() != "3.12.3"
        or sha256(read_bounded(ROOT / "requirements/ff1-training-linux-py312.lock")).hexdigest()
        != LOCK_SHA
        or installed != VERSIONS
    ):
        raise ValueError("DEPENDENCY_LOCK_MISMATCH_NO_INSTALLATION")


def load_training(path: Path) -> TrainingRun:
    run = TrainingRun.model_validate_json(read_bounded(path))
    if run.fingerprint != TRAINING_FP or run.grant.dependency_lock_fingerprint != LOCK_SHA:
        raise ValueError("ACCEPTED_TRAINING_RUN_PIN_MISMATCH")
    validate_handoff(run)
    for job in run.jobs:
        assert job.artifact is not None
        expected = job.artifact
        actual = LogisticArtifact.model_validate_json(
            read_bounded(path.parent / f"model-{expected.fingerprint}.json")
        )
        scaler = ScalerArtifact.model_validate_json(
            read_bounded(path.parent / f"scaler-{expected.reconstruction.scaler.fingerprint}.json")
        )
        if actual != expected or scaler != expected.reconstruction.scaler:
            raise ValueError("ACCEPTED_MODEL_SCALER_MISMATCH")
    return run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new Git-ignored data/ff1 corpus directory")
    parser.add_argument("--qualification", type=Path, default=QUALIFICATION)
    parser.add_argument("--training-run", type=Path, default=TRAINING)
    parser.add_argument("--corpus", type=Path, help="read-only captured corpus for verification")
    parser.add_argument(
        "--verify-run", help="pinned forecast-run fingerprint; no source/ML required"
    )
    args = parser.parse_args()
    try:
        if args.verify_run:
            if args.corpus is None or args.output is not None:
                parser.error("--verify-run requires --corpus and forbids --output")
            replay_result = verify_run(
                ResearchForecastStore(args.corpus.absolute()), args.verify_run
            )
            print(canonical_json(replay_result))
            return 0 if replay_result.status == "MATCH" else 1
        if args.output is None or args.corpus is not None:
            parser.error("generation requires --output; replay uses --corpus --verify-run")
        check_dependencies()
        training = load_training(args.training_run)
        projection = project_qualification(args.qualification, QUALIFICATION_BLOB, training.grant)
        output = args.output.absolute()
        if (
            output.resolve() != output
            or not output.is_relative_to(ROOT / "data/ff1")
            or output.exists()
            or subprocess.run(
                ["git", "check-ignore", "-q", str(output / "run.json")],
                cwd=ROOT,
                check=False,
            ).returncode
            != 0
        ):
            raise ValueError("NEW_PRIVATE_NON_SYMLINK_CORPUS_REQUIRED")
        start = time.monotonic()
        store = ResearchForecastStore(output, create=True)
        capture_training(store, training)
        records = []
        for origin in projection.origins:
            tick = time.monotonic()
            if tick - start > 600:
                raise ValueError("FORECAST_CAMPAIGN_TIMEOUT")
            result = generate(origin, projection, training, datetime.now(TIAF_TIMEZONE))
            if time.monotonic() - tick > 1:
                raise ValueError("FORECAST_ATTEMPT_TIMEOUT")
            store.put("capture", result)
            records.append(result)
        captured = tuple(records)
        verify_records(store, captured, training)
        shards = tuple(
            store.put(
                "shard",
                ForecastShard(
                    captures=tuple(cast(str, r.fingerprint) for r in captured[i : i + 64])
                ),
            )
            for i in range(0, len(captured), 64)
        )
        populations = tuple(population(fold, captured) for fold in training.grant.allowed_folds)
        parent = LogisticForecastRun(
            qualification_blob=projection.qualification_blob,
            qualification_fingerprint=projection.qualification_fingerprint,
            dataset_fingerprint=projection.dataset_fingerprint,
            research_profile_fingerprint=projection.profile.fingerprint,
            feature_schema_fingerprint=projection.feature_schema.fingerprint,
            training_run_fingerprint=cast(str, training.fingerprint),
            dependency_lock_fingerprint=LOCK_SHA,
            shards=shards,
            populations=populations,  # type: ignore[arg-type]
            verification_matches=len(captured),
            created_at=datetime.now(TIAF_TIMEZONE),
        )
        fp = store.put("run", parent)
        verification = verify_run(ResearchForecastStore(output), fp)
        probabilities = [r.output.probability for r in captured if r.output is not None]
        print(
            canonical_json(
                {
                    "verdict": "FF1_3_ACCEPTED" if verification.status == "MATCH" else "HOLD_FF1_3",
                    "training_run": training.fingerprint,
                    "forecast_run": fp,
                    "corpus": str(output.relative_to(ROOT)),
                    "populations": populations,
                    "generated": len(probabilities),
                    "holdout": "SEALED",
                    "verification": verification,
                    "engineering_probability_min": min(probabilities, default=None),
                    "engineering_probability_max": max(probabilities, default=None),
                    "elapsed_seconds": time.monotonic() - start,
                }
            )
        )
        return 0 if verification.status == "MATCH" else 1
    except (ValueError, OSError, LookupError) as exc:
        # Never echo source data or validation inputs.
        print(f"HOLD_FF1_3: {type(exc).__name__}; no promotion or evaluation performed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
