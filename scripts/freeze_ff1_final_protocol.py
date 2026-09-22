"""INTERNAL outcome-blind protocol freeze/replay only. Cannot open or score holdout."""

import argparse
import importlib.abc
import json
import os
import platform
import sys
from datetime import datetime
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
from typing import cast

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.evaluation.forecast_comparison_store import DevelopmentEvaluationStore
from tiaf.evaluation.forecast_final_custody import (
    FinalProtocolStore,
    assemble_protocol,
    final_grid,
    review_handoffs,
)
from tiaf.evaluation.forecast_retrospective_contracts import ResearchCalendar
from tiaf.forecasting.identity import semantic_fingerprint
from tiaf.learning.forecast_artifacts import FifthFoldGrant
from tiaf.learning.forecast_fifth_store import FifthStore

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data/ff1/final_protocol_20260922"
FIFTH = ROOT / "data/ff1/preholdout_fifth_fold_20260922"
DEVELOPMENT = ROOT / "data/ff1/development_evaluation_20260921"
QUALIFICATION = ROOT / "data/ff1/adjusted_qualification_20260921_clock_review/qualification.json"
PROVISIONING_REVIEW = (
    ROOT / "docs/qualification_records/ff1_1a/adjusted_research_review_20260921.json"
)
LOCK = ROOT / "requirements/ff1-training-linux-py312.lock"
PLAN = ROOT / "docs/TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md"
BRIEF = Path(
    "/home/cbiswas/Downloads/"
    "Codex_TIAF_A7_FF1_Final_Holdout_Protocol_Freeze_Review_with_Fifth_Fold_Handoff.md"
)
HANDOFF = "c40148f60e985c83fe8bca027a3722583ed8c1999ecfc86e4959c4fe6166ce54"
LEDGER = "62bc746d90386f3b718bf6fe106f4a80832bfa8206ea3605ec96bbb2e5817246"
EVALUATION = "5f6d4342c61017fecda2196715d707a356ff8728eb0ec1f6996c362723ba19e1"
LOCK_FP = "54e8577800d2a9132df2c8d3721e0d880da9e706a58f6d8b9beba75338e0ac86"


def install_guard() -> None:
    """Permanent process-local guard; qualification has the strict metadata reader only."""

    class NoFit(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path=None, target=None):  # type: ignore[no-untyped-def]
            if fullname.split(".")[0] in {"sklearn", "scipy", "joblib", "threadpoolctl"}:
                raise RuntimeError("FREEZE_REVIEW_FITTING_IMPORT_FORBIDDEN")
            return None

    sys.meta_path.insert(0, NoFit())

    def audit(event: str, args: tuple[object, ...]) -> None:
        if event.startswith("socket.") or event in {"subprocess.Popen", "os.system"}:
            raise RuntimeError("FREEZE_REVIEW_EXTERNAL_OPERATION_FORBIDDEN")
        if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        p = Path(os.fsdecode(args[0])).absolute()
        if not p.is_relative_to(ROOT / "data/ff1"):
            return
        is_output = p.is_relative_to(OUTPUT)
        allowed = (
            is_output
            or p == QUALIFICATION
            or any(p.is_relative_to(base) for base in (FIFTH, DEVELOPMENT))
        )
        flags = args[2]
        writing = isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT)
        if not allowed or (writing and not is_output):
            raise RuntimeError("FREEZE_REVIEW_SOURCE_ACCESS_FORBIDDEN")

    sys.addaudithook(audit)


def source_pins() -> tuple[tuple[str, str], ...]:
    paths = {
        *ROOT.glob("src/tiaf/evaluation/forecast*.py"),
        *ROOT.glob("src/tiaf/forecasting/*.py"),
        *ROOT.glob("src/tiaf/learning/forecast*.py"),
        *ROOT.glob("src/tiaf/features/*.py"),
        Path(__file__).resolve(),
    }
    return tuple(
        sorted((str(p.relative_to(ROOT)), sha256(p.read_bytes()).hexdigest()) for p in paths)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--freeze", action="store_true", help="review safe closures; freeze once")
    mode.add_argument("--verify-protocol", help="exact frozen protocol fingerprint; no execution")
    args = parser.parse_args()
    if not (args.freeze or args.verify_protocol):
        print("Safe: no operation. This script cannot open or evaluate the holdout.")
        return 0
    install_guard()
    try:
        if sha256(LOCK.read_bytes()).hexdigest() != LOCK_FP:
            raise ValueError("FINAL_DEPENDENCY_LOCK_MISMATCH")
        if args.verify_protocol:
            p = FinalProtocolStore(OUTPUT).protocol(args.verify_protocol)
            if (
                p.source_pins
                != tuple(
                    (name, sha256((ROOT / name).read_bytes()).hexdigest())
                    for name, _ in p.source_pins
                )
                or p.dependency_lock_fingerprint != LOCK_FP
                or p.plan_document_fingerprint != sha256(PLAN.read_bytes()).hexdigest()
                or p.provisioning_review_fingerprint
                != sha256(PROVISIONING_REVIEW.read_bytes()).hexdigest()
            ):
                raise ValueError("FINAL_FROZEN_SOURCE_CHANGED")
            print("MATCH; protocol only; no holdout execution")
            return 0
        if OUTPUT.exists():
            raise ValueError("FINAL_PROTOCOL_ALREADY_FROZEN_NO_OVERWRITE")
        versions = {
            "scikit-learn": "1.7.2",
            "numpy": "2.3.3",
            "scipy": "1.16.2",
            "joblib": "1.5.2",
            "threadpoolctl": "3.6.0",
        }
        if platform.python_version() != "3.12.3" or any(
            version(name) != v for name, v in versions.items()
        ):
            raise ValueError("FINAL_DEPENDENCY_VERSIONS")
        fifth = FifthStore(FIFTH)
        before = {
            p: sha256(p.read_bytes()).hexdigest()
            for b in (FIFTH, DEVELOPMENT)
            for p in b.glob("*.json")
        }
        print(
            "Reviewing fifth-fold and DEVELOPMENT_ONLY closures; protected source blocked.",
            flush=True,
        )
        h = review_handoffs(
            fifth, HANDOFF, DevelopmentEvaluationStore(DEVELOPMENT), LEDGER, EVALUATION
        )
        a = cast(FifthFoldGrant, fifth.get("authority", h.authority_fingerprint))
        original_code = [
            *sorted((ROOT / "src/tiaf/learning").glob("*.py")),
            ROOT / "scripts/prepare_ff1_fifth_fold_artifacts.py",
            ROOT / "src/tiaf/evaluation/forecast_research_truth.py",
            ROOT / "src/tiaf/forecasting/logistic_projection.py",
        ]
        if (
            a.dependency_lock_fingerprint != LOCK_FP
            or a.protocol_fingerprint != sha256(PLAN.read_bytes()).hexdigest()
            or a.code_fingerprint
            != semantic_fingerprint(
                {
                    str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                    for p in original_code
                }
            )
        ):
            raise ValueError("FINAL_PREPARATION_SOURCE_CHANGED")
        population = final_grid(QUALIFICATION, a.qualification_blob, a.qualification_fingerprint)
        # Calendar/action review is metadata, not a provider call or market price.
        review = json.loads(PROVISIONING_REVIEW.read_text())
        calendar = ResearchCalendar.model_validate(review["calendar"])
        sessions = calendar.sessions()
        expected = tuple(
            (s[0], sessions[i + 1][0] if i + 1 < len(sessions) else None)
            for i, s in enumerate(sessions)
            if s[0].year == 2025
        )
        if (
            not calendar.qualified
            or tuple((s.reference_date, s.target_date) for s in population.slots) != expected
            or review["expected_files"]["reliance_daily_ohlcv.csv"] != h.dataset_fingerprint
        ):
            raise ValueError("FINAL_POPULATION_CALENDAR_OR_SOURCE_PIN")
        protocol = assemble_protocol(
            h,
            a,
            population,
            ledger_fp=LEDGER,
            evaluation_fp=EVALUATION,
            review_document_fp=sha256(BRIEF.read_bytes()).hexdigest(),
            provisioning_review_fp=sha256(PROVISIONING_REVIEW.read_bytes()).hexdigest(),
            source_pins=source_pins(),
            created_at=datetime.now(TIAF_TIMEZONE),
        )
        if any(sha256(p.read_bytes()).hexdigest() != fp for p, fp in before.items()):
            raise ValueError("FINAL_INPUT_ARTIFACT_CHANGED")
        store = FinalProtocolStore(OUTPUT, create=True)
        fp = store.put("protocol", protocol)
        if FinalProtocolStore(OUTPUT).protocol(fp) != protocol:
            raise ValueError("FINAL_PROTOCOL_RECONSTRUCTION_FAILED")
        print(f"FF1_READY_FOR_FINAL_HOLDOUT; protocol={fp}")
        print(f"Structural slots={len(population.slots)}; population={population.fingerprint}")
        print(f"Safe input blobs unchanged={len(before)}; no execution claim; SEALED; NOT_RUN")
        return 0
    except (ValueError, OSError, LookupError, AssertionError, RuntimeError) as exc:
        print(f"HOLD_FF1_BEFORE_FINAL_HOLDOUT: {type(exc).__name__}; no protected execution")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
