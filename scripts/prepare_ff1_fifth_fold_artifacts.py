"""Internal one-attempt fifth-fold preparation; no protected inference or evaluation."""

import argparse
import platform
import subprocess
import time
from datetime import datetime
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
from typing import cast

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.identity import canonical_json, semantic_fingerprint
from tiaf.learning.forecast_artifacts import FifthFoldGrant
from tiaf.learning.forecast_fifth_preparation import prepare_fifth
from tiaf.learning.forecast_fifth_store import FifthHandoff, FifthStore, execute_once, verify_fifth
from tiaf.learning.forecast_worker import VERSIONS

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data/ff1/preholdout_fifth_fold_20260922"
QUALIFICATION = ROOT / "data/ff1/adjusted_qualification_20260921_clock_review/qualification.json"
LOCK = ROOT / "requirements/ff1-training-linux-py312.lock"
LOCK_FP = "54e8577800d2a9132df2c8d3721e0d880da9e706a58f6d8b9beba75338e0ac86"
BRIEF = Path(
    "/home/cbiswas/Downloads/"
    "Codex_TIAF_A7_FF1_PreHoldout_FifthFold_Artifact_Preparation_and_NoRefit_Authority_Reconciliation.md"
)
PINS = {
    "qualification_fingerprint": "4b021081c3f5ee1afa3ff389f754ce91920fa45a367d4c88064330a0d1999d51",
    "qualification_blob": "69333427ebb355672d67e19885ba83a659a0427c8760cce4eac717c49a87d4ca",
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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--preflight", action="store_true", help="TRAIN admission only; no fit or writes"
    )
    mode.add_argument(
        "--prepare", action="store_true", help="one scaler/model fit; fixed new corpus"
    )
    mode.add_argument("--verify-handoff", help="exact fingerprint; offline non-fitting replay")
    parser.add_argument("--corpus", type=Path, help="relocated captured corpus, replay only")
    parser.add_argument("--approve-dependency-lock", help="explicit approved dependency SHA-256")
    args = parser.parse_args()
    if not (args.preflight or args.prepare or args.verify_handoff):
        print("Safe: no operation. Use --preflight, explicitly authorized --prepare, or replay.")
        return 0
    try:
        if args.verify_handoff:
            result = verify_fifth(
                FifthStore((args.corpus or OUTPUT).absolute()), args.verify_handoff
            )
            print(result)
            return 0 if result == "MATCH" else 1
        if args.corpus is not None:
            parser.error("--corpus is replay-only; preparation output is fixed to prevent retries")
        if (
            args.approve_dependency_lock != LOCK_FP
            or sha256(LOCK.read_bytes()).hexdigest() != LOCK_FP
            or platform.python_version() != "3.12.3"
            or any(version(name) != expected for name, expected in VERSIONS.items())
        ):
            raise ValueError("FIFTH_DEPENDENCY_APPROVAL_REQUIRED")
        if args.prepare and OUTPUT.exists():
            raise ValueError("FIFTH_ATTEMPT_ALREADY_EXISTS_NO_RETRY")
        code = [
            *sorted((ROOT / "src/tiaf/learning").glob("*.py")),
            Path(__file__).resolve(),
            ROOT / "src/tiaf/evaluation/forecast_research_truth.py",
            ROOT / "src/tiaf/forecasting/logistic_projection.py",
        ]
        a = FifthFoldGrant(
            basis="QUALIFIED_ADJUSTED_RESEARCH",
            qualification_fingerprint=PINS["qualification_fingerprint"],
            qualification_blob=PINS["qualification_blob"],
            dataset_fingerprint=PINS["dataset_fingerprint"],
            research_profile_fingerprint=PINS["research_profile_fingerprint"],
            feature_schema_fingerprint=PINS["feature_schema_fingerprint"],
            protocol_fingerprint=sha256(
                (
                    ROOT / "docs/TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md"
                ).read_bytes()
            ).hexdigest(),
            authority_document_fingerprint=sha256(BRIEF.read_bytes()).hexdigest(),
            dependency_lock_fingerprint=LOCK_FP,
            code_fingerprint=semantic_fingerprint(
                {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in code}
            ),
            issued_at=datetime.now(TIAF_TIMEZONE),
        )
        started = time.monotonic()
        preparation = prepare_fifth(QUALIFICATION, a)
        print(
            canonical_json(
                {
                    "phase": "TRAIN_ONLY_PREFLIGHT",
                    "authority": a.fingerprint,
                    "cutoff": a.cutoff,
                    "audit": preparation.training.manifest.audit,
                    "train_start": preparation.training.manifest.train_start.isoformat(),
                    "train_end": preparation.training.manifest.train_end.isoformat(),
                    "preparation_bytes": len((canonical_json(preparation) + "\n").encode()),
                    "holdout": "SEALED",
                    "protected_outcome_access": "NONE",
                }
            ),
            flush=True,
        )
        if args.preflight:
            return 0
        if subprocess.run(
            ["git", "check-ignore", "-q", str(OUTPUT / "handoff.json")], cwd=ROOT, check=False
        ).returncode:
            raise ValueError("FIFTH_PRIVATE_OUTPUT_REQUIRED")
        store = FifthStore(OUTPUT, create=True)
        fp = execute_once(store, preparation)
        status = verify_fifth(FifthStore(OUTPUT), fp)
        h = cast(FifthHandoff, store.get("handoff", fp))
        if time.monotonic() - started > 600 or status != "MATCH":
            raise ValueError("FIFTH_REPLAY_OR_CAMPAIGN_LIMIT")
        print(
            canonical_json(
                {
                    "verdict": "FIFTH_FOLD_PREPARATION_COMPLETE",
                    "handoff": h,
                    "reconstruction": status,
                    "elapsed_seconds": time.monotonic() - started,
                }
            )
        )
        return 0
    except (ValueError, OSError, LookupError, AssertionError) as exc:
        print(f"HOLD_FIFTH_FOLD_PREPARATION: {type(exc).__name__}; no retry or holdout opening")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
