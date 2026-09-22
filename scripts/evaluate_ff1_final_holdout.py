"""INTERNAL one-shot protected 2025 evaluation; no fitting, network or promotion.

No arguments is a no-op. --preflight is outcome-blind. --execute requires the
exact accepted protocol and consumes permanent authority BEFORE decoding values.
--verify-ledger reads the captured final corpus only; it is not another execution.
"""

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
from tiaf.evaluation.forecast_final_custody import FinalProtocolStore, final_grid, review_handoffs
from tiaf.evaluation.forecast_final_protocol import FinalProtocol
from tiaf.evaluation.forecast_final_scoring import FinalEvaluation
from tiaf.evaluation.forecast_final_store import (
    FinalExecution,
    FinalLedger,
    FinalStore,
    execute_final,
    validate_artifacts,
    verify_final,
)
from tiaf.evaluation.forecast_research_contracts import ResearchRightsConfig
from tiaf.evaluation.forecast_retrospective_contracts import RetrospectiveDataset
from tiaf.evaluation.forecast_retrospective_io import load_reviewed_dataset
from tiaf.forecasting.identity import semantic_fingerprint
from tiaf.forecasting.research_contracts import AdjustedFF1FeatureSchema, AdjustedResearchProfile
from tiaf.learning.forecast_artifacts import LogisticArtifact
from tiaf.learning.forecast_fifth_preparation import FifthBaseRateState
from tiaf.learning.forecast_fifth_store import FifthHandoff, FifthStore

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814"
CUSTODY = ROOT / "data/ff1/final_protocol_20260922"
OUTPUT = ROOT / "data/ff1/final_holdout_20260922"
FIFTH = ROOT / "data/ff1/preholdout_fifth_fold_20260922"
DEVELOPMENT = ROOT / "data/ff1/development_evaluation_20260921"
QUALIFICATION = ROOT / "data/ff1/adjusted_qualification_20260921_clock_review/qualification.json"
DATASET = ROOT / "data/ff1/reliance"
REVIEW = ROOT / "docs/qualification_records/ff1_1a/adjusted_research_review_20260921.json"
LOCK = ROOT / "requirements/ff1-training-linux-py312.lock"
BRIEF = Path(
    "/home/cbiswas/Downloads/Codex_TIAF_A7_FF1_One_Shot_Protected_2025_Final_Holdout_Evaluation.md"
)


def install_guard(*, execute: bool, replay: bool) -> None:
    """Permanent process-local no-fit/no-network/read-only-source enforcement."""
    forbidden = {"sklearn", "scipy", "joblib", "threadpoolctl"}
    if any(name.split(".")[0] in forbidden for name in sys.modules):
        raise RuntimeError("FINAL_FITTING_LIBRARY_ALREADY_LOADED")

    class NoFit(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path=None, target=None):  # type: ignore[no-untyped-def]
            if fullname.split(".")[0] in forbidden or fullname.startswith("tiaf.data.providers"):
                raise RuntimeError("FINAL_FITTING_OR_PROVIDER_IMPORT_FORBIDDEN")
            return None

    sys.meta_path.insert(0, NoFit())

    def audit(event: str, args: tuple[object, ...]) -> None:
        if event.startswith("socket.") or event in {
            "subprocess.Popen",
            "os.system",
            "os.exec",
            "os.posix_spawn",
            "os.fork",
        }:
            raise RuntimeError("FINAL_EXTERNAL_OPERATION_FORBIDDEN")
        if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        p = Path(os.fsdecode(args[0])).absolute()
        if p.name == ".env":
            raise RuntimeError("FINAL_SECRET_ACCESS_FORBIDDEN")
        if not p.is_relative_to(ROOT / "data"):
            return
        flags = args[2]
        writing = isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT)
        if replay:
            allowed = p.is_relative_to(OUTPUT) and not writing
        else:
            allowed = p == QUALIFICATION or any(
                p.is_relative_to(base) for base in (OUTPUT, CUSTODY, FIFTH, DEVELOPMENT, DATASET)
            )
            if writing:
                allowed = execute and (
                    p.is_relative_to(OUTPUT)
                    or (
                        p.parent == CUSTODY
                        and p.name.startswith("attempt-")
                        and isinstance(flags, int)
                        and bool(flags & os.O_EXCL)
                    )
                )
        if not allowed:
            raise RuntimeError("FINAL_SOURCE_ACCESS_FORBIDDEN")

    sys.addaudithook(audit)


def preflight() -> tuple[
    FinalProtocol, LogisticArtifact, FifthBaseRateState, FifthHandoff, RetrospectiveDataset
]:
    custody = FinalProtocolStore(CUSTODY)
    protocol = custody.protocol(PROTOCOL)
    if tuple(CUSTODY.glob("attempt-*.json")) or OUTPUT.exists():
        raise ValueError("FINAL_ALREADY_CONSUMED_OR_OUTPUT_EXISTS_NO_RETRY")
    if not protocol.authorized or any(
        sha256((ROOT / name).read_bytes()).hexdigest() != fp for name, fp in protocol.source_pins
    ):
        raise ValueError("FINAL_PROTOCOL_OR_FROZEN_SOURCE_CHANGED")
    if (
        sha256(REVIEW.read_bytes()).hexdigest() != protocol.provisioning_review_fingerprint
        or sha256(LOCK.read_bytes()).hexdigest() != protocol.dependency_lock_fingerprint
        or platform.python_version() != "3.12.3"
        or any(
            version(name) != expected
            for name, expected in (
                ("scikit-learn", "1.7.2"),
                ("numpy", "2.3.3"),
                ("scipy", "1.16.2"),
                ("joblib", "1.5.2"),
                ("threadpoolctl", "3.6.0"),
            )
        )
    ):
        raise ValueError("FINAL_REVIEW_OR_DEPENDENCIES_CHANGED")
    fifth = FifthStore(FIFTH)
    handoff = review_handoffs(
        fifth,
        protocol.fifth_handoff_fingerprint,
        DevelopmentEvaluationStore(DEVELOPMENT),
        protocol.development_ledger_fingerprint,
        protocol.development_evaluation_fingerprint,
    )
    model = cast(LogisticArtifact, fifth.get("model", protocol.model_fingerprint))
    baseline = cast(FifthBaseRateState, fifth.get("baseline", protocol.baserate_state_fingerprint))
    validate_artifacts(protocol, model, baseline, handoff, approved=PROTOCOL)
    if (
        final_grid(QUALIFICATION, protocol.qualification_blob, protocol.qualification_fingerprint)
        != protocol.population
    ):
        raise ValueError("FINAL_POPULATION_CHANGED")
    # Unchanged old reader REDACTS every 2025+ numerical field. No label access.
    context = load_reviewed_dataset(DATASET, json.loads(REVIEW.read_text()))
    profile = AdjustedResearchProfile()
    if semantic_fingerprint(
        (context, profile, ResearchRightsConfig(), AdjustedFF1FeatureSchema(profile=profile))
    ) != (protocol.population.context_fingerprint):
        raise ValueError("FINAL_REDACTED_QUALIFICATION_CONTEXT_CHANGED")
    # Only metadata is needed by the A2 projector. No historical TRAIN values are
    # supplied to final inference; preserve one structurally redacted row.
    context = RetrospectiveDataset.model_validate(
        {
            **context.model_dump(),
            "rows": (next(r for r in context.rows if r.protected),),
        }
    )
    return protocol, model, baseline, handoff, context


def implementation_pins() -> tuple[tuple[str, str], ...]:
    names = (
        "src/tiaf/forecasting/final_inputs.py",
        "src/tiaf/evaluation/forecast_final_outcomes.py",
        "src/tiaf/evaluation/forecast_final_scoring.py",
        "src/tiaf/evaluation/forecast_final_store.py",
        "scripts/evaluate_ff1_final_holdout.py",
        "tests/unit/evaluation/test_final_holdout.py",
    )
    return tuple((name, sha256((ROOT / name).read_bytes()).hexdigest()) for name in sorted(names))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", help="outcome-blind checks; no claim")
    mode.add_argument("--execute", action="store_true", help="consume the ONLY authorized attempt")
    mode.add_argument("--verify-ledger", help="captured final ledger fingerprint; read-only replay")
    parser.add_argument(
        "--approved-protocol", help="required exact frozen fingerprint for --execute"
    )
    args = parser.parse_args()
    if not (args.preflight or args.execute or args.verify_ledger):
        print("Safe: no operation. No protected values read and no authority consumed.")
        return 0
    if args.execute and args.approved_protocol != PROTOCOL:
        print("HOLD_FF1_FINAL_HOLDOUT: exact approved protocol required; no opening")
        return 1
    try:
        install_guard(execute=args.execute, replay=bool(args.verify_ledger))
        if args.verify_ledger:
            captured = FinalStore(OUTPUT)
            terminal = cast(FinalLedger, captured.get("ledger", args.verify_ledger))
            frozen = cast(FinalProtocol, captured.get("protocol", terminal.protocol))
            run = cast(FinalExecution, captured.get("execution", terminal.execution))
            if (
                terminal.protocol != PROTOCOL
                or any(
                    sha256((ROOT / name).read_bytes()).hexdigest() != fp
                    for name, fp in (*frozen.source_pins, *run.implementation_pins)
                )
                or sha256(LOCK.read_bytes()).hexdigest() != frozen.dependency_lock_fingerprint
                or version("numpy") != "2.3.3"
                or platform.python_version() != "3.12.3"
            ):
                print("MISMATCH; frozen implementation/dependency identity changed")
                return 1
            result = verify_final(captured, args.verify_ledger)
            print(result + "; captured closure only; no source access, claim, fitting or network")
            return 0 if result == "MATCH" else 1
        print("Preflight: sealed readers / opaque hashes / accepted closures only.", flush=True)
        protocol, model, baseline, handoff, context = preflight()
        print("MATCH; SEALED; executions_used=0; all frozen identities verified", flush=True)
        if args.preflight:
            return 0
        execution = FinalExecution(
            protocol_fingerprint=PROTOCOL,
            authority_document_fingerprint=sha256(BRIEF.read_bytes()).hexdigest(),
            implementation_pins=implementation_pins(),
            created_at=datetime.now(TIAF_TIMEZONE),
        )
        # Fixed directory; no override, force, resume, refit or seed/threshold flags.
        store = FinalStore(OUTPUT, create=True)
        print("Consuming the one-shot claim before protected source decoding.", flush=True)
        ledger_fp = execute_final(
            FinalProtocolStore(CUSTODY),
            store,
            protocol,
            execution,
            model,
            baseline,
            handoff,
            context,
            lambda: (DATASET / "reliance_daily_ohlcv.csv").read_bytes(),
            approved=PROTOCOL,
        )
        if execution.implementation_pins != implementation_pins() or any(
            sha256((ROOT / name).read_bytes()).hexdigest() != fp
            for name, fp in protocol.source_pins
        ):
            raise ValueError("FINAL_CODE_CHANGED_DURING_EXECUTION")
        ledger = cast(FinalLedger, store.get("ledger", ledger_fp))
        report = cast(FinalEvaluation, store.get("evaluation", ledger.evaluation))
        print(f"FF1_FINAL_HOLDOUT_ACCEPTED; {report.decision.classification}")
        print("CONSUMED; COMPLETE; executions_used=1; refit=NO; promotion=NO")
        print(f"ledger={ledger_fp}\nevaluation={report.fingerprint}")
        print(report.summary.model_dump_json(indent=2))
        return 0
    except (ValueError, OSError, LookupError, AssertionError, RuntimeError) as exc:
        print(f"HOLD_FF1_FINAL_HOLDOUT: {type(exc).__name__}: {exc}")
        print("No retry is allowed if the durable attempt was consumed. Do not reset custody.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
