"""INTERNAL FF-1.2: four offline training artifacts; no forecasts or quality metrics."""

import argparse
import json
import platform
import subprocess
import time
from datetime import datetime
from hashlib import sha256
from pathlib import Path

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.identity import canonical_json, semantic_fingerprint
from tiaf.learning.forecast_artifacts import TrainingGrant
from tiaf.learning.forecast_jobs import TrainingRun, TrainingStore, run_fit
from tiaf.learning.forecast_training import load_qualification, prepare_training, read_bounded

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "requirements/ff1-training-linux-py312.lock"
QUALIFICATION = ROOT / "data/ff1/adjusted_qualification_20260921_clock_review/qualification.json"
QUALIFICATION_BLOB = "69333427ebb355672d67e19885ba83a659a0427c8760cce4eac717c49a87d4ca"
PINS = {
    "qualification_fingerprint": "4b021081c3f5ee1afa3ff389f754ce91920fa45a367d4c88064330a0d1999d51",
    "dataset_fingerprint": "d91311cdae0ecec8b3f7c60522e805c6b495e02ea633fdcb63b65476ef0dd6f6",
    "research_profile_fingerprint": (
        "1e616cc7a2f3654d856b916e790d054a6c1ff7f10efe2b316cf0a44835011c45"
    ),
    "feature_schema_fingerprint": (
        "76e63292685ee0b3b41f7ab033407e6bd014fc802d2092a2ed227888bdc71676"
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qualification", type=Path, default=QUALIFICATION)
    parser.add_argument(
        "--dataset", type=Path, default=ROOT / "data/ff1/reliance/reliance_daily_ohlcv.csv"
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="new Git-ignored data/ff1 directory"
    )
    parser.add_argument(
        "--approve-dependency-lock",
        required=True,
        help="reviewer-approved SHA-256 of requirements/ff1-training-linux-py312.lock",
    )
    args = parser.parse_args()
    output = args.output.absolute()
    if (
        output.resolve() != output
        or not output.is_relative_to(ROOT / "data/ff1")
        or output.exists()
    ):
        parser.error(
            "output must be a new non-symlink directory under data/ff1; no retries/overwrite"
        )
    if (
        subprocess.run(
            ["git", "check-ignore", "-q", str(output / "run.json")], cwd=ROOT, check=False
        ).returncode
        != 0
    ):
        parser.error("private artifact location must be Git-ignored")
    lock_hash = sha256(read_bounded(LOCK)).hexdigest()
    if args.approve_dependency_lock != lock_hash or platform.python_version() != "3.12.3":
        parser.error(
            "reviewed dependency lock / CPython 3.12.3 required; no automatic installation"
        )
    code = {
        str(p.relative_to(ROOT)): sha256(read_bounded(p)).hexdigest()
        for p in sorted((ROOT / "src/tiaf/learning").glob("*.py"))
    }
    code["scripts/train_ff1_logistic_candidate.py"] = sha256(
        read_bounded(Path(__file__))
    ).hexdigest()
    protocol = ROOT / "docs/TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md"
    grant = TrainingGrant(
        grant_id="ff1.2:four-development-artifacts",
        basis="QUALIFIED_ADJUSTED_RESEARCH",
        **PINS,
        dependency_lock_fingerprint=lock_hash,
        code_fingerprint=semantic_fingerprint(code),
        protocol_fingerprint=sha256(read_bounded(protocol)).hexdigest(),
        issued_at=datetime.now(TIAF_TIMEZONE),
    )
    tick = time.monotonic()
    try:
        q = load_qualification(
            args.qualification, blob_sha256=QUALIFICATION_BLOB, dataset=args.dataset, grant=grant
        )
        # Admit all four memberships before creating the first worker.
        requests = tuple(prepare_training(q, grant, year) for year in grant.allowed_folds)
        store = TrainingStore(output, grant)
        jobs = []
        for request in requests:
            if time.monotonic() - tick > grant.campaign_timeout_seconds - grant.fit_timeout_seconds:
                break
            store.put("manifest", request.manifest)
            job = run_fit(request)
            store.put("job", job)
            jobs.append(job)
            if job.artifact is None:
                break
            store.put("scaler", job.artifact.reconstruction.scaler)
            store.put("model", job.artifact)
        status = (
            "COMPLETE" if len(jobs) == 4 and all(j.status == "TRAINED" for j in jobs) else "PARTIAL"
        )
        run = TrainingRun(
            grant=grant, jobs=tuple(jobs), created_at=datetime.now(TIAF_TIMEZONE), status=status
        )  # type: ignore[arg-type]
        run_path = store.put("run", run)
        report = {
            "verdict": "FF1_2_ACCEPTED" if status == "COMPLETE" else "HOLD_FF1_2",
            "training_complete": status == "COMPLETE",
            "holdout_status": "SEALED",
            "run_fingerprint": run.fingerprint,
            "run_path": str(run_path.relative_to(ROOT)),
            "grant": grant.model_dump(mode="json"),
            "code_files": code,
            "evaluation_metrics": 0,
            "forecast_records": 0,
            "external_calls": 0,
            "folds": [],
        }
        for job in jobs:
            a = job.artifact
            record = job.model_dump(mode="json", exclude={"artifact"})
            if a is not None:
                record.update(
                    {
                        "audit": a.manifest.audit.model_dump(mode="json"),
                        "train_start": a.manifest.train_start.isoformat(),
                        "train_end": a.manifest.train_end.isoformat(),
                        "fit_cutoff": a.manifest.fit_cutoff.isoformat(),
                        "scaler_fingerprint": a.reconstruction.scaler.fingerprint,
                        "model_fingerprint": a.fingerprint,
                        "scientific_fingerprint": a.scientific_fingerprint,
                        "reconstruction_fingerprint": a.reconstruction.fingerprint,
                        "n_iter": a.n_iter,
                        "converged": a.converged,
                        "reconstruction_max_error": a.reconstruction_max_error,
                        "versions": a.versions.model_dump(mode="json"),
                    }
                )
            report["folds"].append(record)
        report["report_fingerprint"] = semantic_fingerprint(report)
        with (output / "summary.json").open("x", encoding="utf-8") as handle:
            handle.write(canonical_json(report) + "\n")
        print(json.dumps(report, indent=2))
        return 0 if status == "COMPLETE" else 1
    except (ValueError, OSError) as exc:
        print(f"HOLD_FF1_2: {type(exc).__name__}; no usable completion asserted")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
