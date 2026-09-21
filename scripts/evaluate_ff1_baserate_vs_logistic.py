"""INTERNAL FF-1.4 development-only evaluation. No final holdout or promotion."""

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
from tiaf.evaluation.forecast_comparison import DevelopmentEvaluation
from tiaf.evaluation.forecast_comparison_metrics import DevelopmentPolicy
from tiaf.evaluation.forecast_comparison_store import (
    DevelopmentEvaluationStore,
    EvaluationLedger,
    EvaluationManifest,
    capture_logistic,
    persist_evaluation,
    verify_evaluation,
    write_truth,
)
from tiaf.evaluation.forecast_research_truth import load_research_truth
from tiaf.forecasting.identity import canonical_json, semantic_fingerprint
from tiaf.forecasting.logistic_store import ResearchForecastStore, recorded_replay
from tiaf.forecasting.research_baserate import baseline_forecast, freeze_baseline

ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION = ROOT / "data/ff1/adjusted_qualification_20260921_clock_review/qualification.json"
QUALIFICATION_BLOB = "69333427ebb355672d67e19885ba83a659a0427c8760cce4eac717c49a87d4ca"
LOCK_SHA = "54e8577800d2a9132df2c8d3721e0d880da9e706a58f6d8b9beba75338e0ac86"
LOGISTIC_FP = "4dc2adb6f2bb9977bf3a06c2c5903065223cfc6e2c6a58898c0cb65090197812"
LOGISTIC_CORPUS = ROOT / "data/ff1/logistic_forecasts_20260921"
BRIEF = Path(
    "/home/cbiswas/Downloads/"
    "Codex_TIAF_A7_FF1_4_Development_Only_Paired_Evaluation_with_Sealed_Holdout.md"
)


def check_dependencies() -> None:
    approved = {
        "scikit-learn": "1.7.2",
        "numpy": "2.3.3",
        "scipy": "1.16.2",
        "joblib": "1.5.2",
        "threadpoolctl": "3.6.0",
    }
    try:
        installed = {name: version(name) for name in approved}
    except PackageNotFoundError as exc:
        raise ValueError("DEPENDENCY_MISSING_NO_INSTALLATION") from exc
    if (
        installed != approved
        or platform.python_version() != "3.12.3"
        or sha256((ROOT / "requirements/ff1-training-linux-py312.lock").read_bytes()).hexdigest()
        != LOCK_SHA
    ):
        raise ValueError("DEPENDENCY_LOCK_MISMATCH")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new private data/ff1 directory; no overwrite")
    parser.add_argument("--corpus", type=Path, help="existing evaluation corpus for offline replay")
    parser.add_argument(
        "--verify-ledger", help="exact ledger fingerprint; no original source needed"
    )
    args = parser.parse_args()
    try:
        check_dependencies()
        if args.verify_ledger:
            if args.corpus is None or args.output is not None:
                parser.error("verification requires --corpus, forbids --output")
            result = verify_evaluation(
                DevelopmentEvaluationStore(args.corpus.absolute()), args.verify_ledger
            )
            print(result)
            return 0 if result == "MATCH" else 1
        if args.output is None or args.corpus is not None:
            parser.error("generation requires --output; replay requires --corpus --verify-ledger")
        output = args.output.absolute()
        if (
            output.exists()
            or output.resolve() != output
            or not output.is_relative_to(ROOT / "data/ff1")
            or subprocess.run(
                ["git", "check-ignore", "-q", str(output / "ledger.json")], cwd=ROOT, check=False
            ).returncode
        ):
            raise ValueError("NEW_PRIVATE_OUTPUT_REQUIRED")
        start = time.monotonic()
        store = DevelopmentEvaluationStore(output, create=True)
        policy = DevelopmentPolicy()
        policy_fp = store.put("policy", policy)
        print("Preregistered development-only policy:", policy_fp, flush=True)
        source = ResearchForecastStore(LOGISTIC_CORPUS)
        capture_logistic(source, store, LOGISTIC_FP)
        _, records, training = recorded_replay(store, LOGISTIC_FP)
        journal = load_research_truth(QUALIFICATION, QUALIFICATION_BLOB, training)
        truth_index = write_truth(store, journal)
        artifacts = {}
        for job in training.jobs:
            assert job.artifact is not None
            artifacts[job.fold_id] = freeze_baseline(
                journal, job.fold_id, job.artifact.manifest.fit_cutoff
            )
        evaluated_at = datetime.now(TIAF_TIMEZONE)
        forecasts = tuple(
            baseline_forecast(artifacts[r.request.fold_id], r.request, evaluated_at)
            for r in records
            if not r.request.origin.protected
        )
        code_paths = [
            *sorted((ROOT / "src/tiaf/evaluation").glob("forecast_comparison*.py")),
            ROOT / "src/tiaf/evaluation/forecast_research_truth.py",
            ROOT / "src/tiaf/forecasting/research_baserate.py",
            Path(__file__).resolve(),
        ]
        manifest = EvaluationManifest(
            logistic_run=LOGISTIC_FP,
            truth_index=truth_index,
            baseline_artifacts=tuple(store.put("baseline", a) for a in artifacts.values()),
            baseline_forecasts=tuple(store.put("baselineforecast", f) for f in forecasts),
            policy_fingerprint=policy_fp,
            protocol_document_sha256=sha256(
                (
                    ROOT / "docs/TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md"
                ).read_bytes()
            ).hexdigest(),
            clarification_document_sha256=sha256(BRIEF.read_bytes()).hexdigest(),
            implementation_sha256=semantic_fingerprint(
                {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in code_paths}
            ),
            evaluated_at=evaluated_at,
        )
        ledger_fp = persist_evaluation(store, manifest)
        status = verify_evaluation(DevelopmentEvaluationStore(output), ledger_fp)
        if time.monotonic() - start > 600:
            raise ValueError("CAMPAIGN_TIMEOUT")
        ledger = cast(EvaluationLedger, store.get("ledger", ledger_fp))
        report = cast(DevelopmentEvaluation, store.get("evaluation", ledger.report))
        print(
            canonical_json(
                {
                    "verdict": "FF1_4_ACCEPTED" if status == "MATCH" else "HOLD_FF1_4",
                    "classification": report.decision.classification,
                    "holdout": "SEALED",
                    "final_holdout_evidence": "NOT_RUN",
                    "evaluation_fingerprint": report.fingerprint,
                    "ledger_fingerprint": ledger_fp,
                    "paired_population_fingerprint": report.paired_population_fingerprint,
                    "ground_truth_fingerprint": report.ground_truth_fingerprint,
                    "policy_fingerprint": policy.fingerprint,
                    "replay": status,
                    "decision": report.decision,
                    "summaries": report.summaries,
                    "elapsed_seconds": time.monotonic() - start,
                }
            )
        )
        return 0 if status == "MATCH" else 1
    except (ValueError, OSError, LookupError, AssertionError) as exc:
        print(f"HOLD_FF1_4: {type(exc).__name__}; no final-support decision permitted")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
