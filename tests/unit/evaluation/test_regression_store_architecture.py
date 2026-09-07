"""Corpus persistence, golden replay, failure diagnostics, and boundaries."""

import json
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import pytest

from tiaf.baseline import BaselinePolicy, CandidateClass, default_policy, rank_opportunities
from tiaf.contracts import DataQuality, FreshnessState, TradeStyle
from tiaf.evaluation import (
    BaselineRunRecord,
    CapturedBaselineCase,
    CorpusError,
    RegressionStatus,
    ReplayCorpusStore,
    SnapshotIntegrityError,
    case_json,
    load_case,
    load_snapshot_json,
    run_regression,
    save_case,
    snapshot_json,
)

from ..baseline._support import NOW, values_for
from ._support import frozen_case


def _resolve(policy_id: str, policy_version: str) -> BaselinePolicy:
    policy = default_policy(TradeStyle.POSITIONAL)
    if (policy_id, policy_version) != (policy.policy_id, policy.policy_version):
        raise ValueError("policy mismatch")
    return policy


def test_golden_manifest_freezes_all_directions_and_core_no_trade() -> None:
    manifest = json.loads(
        Path("tests/fixtures/evaluation/golden_manifest.json").read_text(encoding="utf-8")
    )
    cases = tuple(
        CapturedBaselineCase(snapshot=snapshot, run_record=run)
        for item in manifest["cases"]
        for snapshot, run in (frozen_case(profile=item["profile"]),)
    )
    assert tuple(run.run_record.direction.value for run in cases) == tuple(
        item["direction"] for item in manifest["cases"]
    )
    report = run_regression(cases, _resolve, replay_time=NOW + timedelta(days=100))
    assert report.pass_count == len(cases)
    assert report.fail_count == 0
    assert all(item.status is RegressionStatus.PASS for item in report.results)


def test_golden_corpus_covers_all_classes_quality_absence_stale_and_rankings() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    top_values = values_for("positive")
    top_values.update(
        {
            "momentum.return_5": 20.0,
            "momentum.return_20": 30.0,
            "participation.balance": 1.0,
            "participation.relative_volume": 3.0,
            "extension.ema": 0.1,
            "extension.range": 1.0,
        }
    )
    mature_values = values_for("positive")
    mature_values.update(
        {
            "momentum.return_20": 30.0,
            "extension.ema": 6.0,
            "extension.range": 5.0,
        }
    )
    captures = (
        frozen_case(policy=policy),
        frozen_case(policy=policy, values=top_values, subject="TOP"),
        frozen_case(policy=policy, values=mature_values, subject="MATURE"),
        frozen_case(policy=policy, profile="neutral", subject="NONE"),
        frozen_case(
            policy=policy,
            subject="PARTIAL",
            quality=DataQuality.PARTIAL,
        ),
        frozen_case(policy=policy, subject="NOINDEX", include_relative=False),
        frozen_case(
            policy=policy,
            subject="STALE",
            primary_freshness=FreshnessState.STALE,
        ),
    )
    classes = {run.candidate_class for _, run in captures}
    assert classes == set(CandidateClass)
    assert captures[4][1].quality is DataQuality.PARTIAL
    assert captures[5][0].benchmark_symbol is None
    assert captures[6][1].candidate_class is CandidateClass.NO_TRADE
    golden_cases = tuple(
        CapturedBaselineCase(snapshot=snapshot, run_record=run)
        for snapshot, run in captures
    )
    report = run_regression(
        golden_cases,
        _resolve,
        replay_time=NOW + timedelta(days=365),
    )
    assert report.pass_count == len(captures)
    ranking = rank_opportunities(tuple(run.assessment for _, run in captures[:4]), top_n=3)
    assert ranking.assessments
    all_no_trade = rank_opportunities(
        (captures[3][1].assessment, captures[6][1].assessment),
        top_n=5,
    )
    assert all_no_trade.items == ()


def test_regression_reports_deliberate_field_difference_and_policy_mismatch() -> None:
    snapshot, run = frozen_case()
    changed_assessment = run.assessment.model_copy(
        update={"opportunity_score": run.assessment.opportunity_score + 0.25}
    )
    changed = BaselineRunRecord.model_validate(
        run.model_copy(
            update={
                "assessment": changed_assessment,
                "opportunity_score": changed_assessment.opportunity_score,
            }
        ).model_dump()
    )
    case = CapturedBaselineCase(snapshot=snapshot, run_record=changed)
    report = run_regression((case,), _resolve, replay_time=NOW)
    assert report.fail_count == 1
    assert any(item.path == "opportunity_score" for item in report.results[0].differences)

    mismatch = run_regression(
        (CapturedBaselineCase(snapshot=snapshot, run_record=run),),
        lambda _policy_id, _version: default_policy(TradeStyle.DAY),
        replay_time=NOW,
    )
    assert mismatch.fail_count == 1
    assert mismatch.results[0].differences[0].path == "$replay_error"


def test_content_addressed_store_and_append_only_logs(tmp_path: Path) -> None:
    snapshot, run = frozen_case()
    store = ReplayCorpusStore(tmp_path / "corpus")
    first_path = store.save_snapshot(snapshot)
    assert store.save_snapshot(snapshot) == first_path
    store.append_run(run)
    assert store.runs() == (run,)
    assert store.cases() == (CapturedBaselineCase(snapshot=snapshot, run_record=run),)
    with pytest.raises(CorpusError, match="already exists"):
        store.append_run(run)
    with pytest.raises(CorpusError, match="does not exist"):
        store.load_snapshot("missing")
    with pytest.raises(CorpusError, match="no decision records"):
        ReplayCorpusStore(tmp_path / "empty").cases()


def test_portable_case_and_subprocess_replay_are_exact_and_offline(tmp_path: Path) -> None:
    snapshot, run = frozen_case()
    case = CapturedBaselineCase(snapshot=snapshot, run_record=run)
    path = tmp_path / "case.json"
    save_case(path, case)
    assert load_case(path) == case
    assert case_json(load_case(path)) == case_json(case)
    completed = subprocess.run(
        [sys.executable, "scripts/replay_baseline_snapshot.py", "--input", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Exact Match                : YES" in completed.stdout
    assert "Evidence fingerprint" in completed.stdout


def test_serialized_fingerprint_mismatch_is_detected() -> None:
    snapshot, _ = frozen_case()
    payload = json.loads(snapshot_json(snapshot))
    payload["fingerprint"] = "0" * 64
    with pytest.raises(SnapshotIntegrityError, match="fingerprint"):
        load_snapshot_json(json.dumps(payload))


def test_evaluation_package_has_no_provider_execution_ai_or_optimization_imports() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in Path("src/tiaf/evaluation").glob("*.py")
    )
    forbidden = (
        "tiaf.data.providers",
        "DhanInstrumentResolver",
        "DhanMarketDataProvider",
        "httpx",
        "requests",
        "TradeMonitor",
        "langgraph",
        "openai",
        "tiaf.agents",
        "tiaf.workflows",
        "sklearn",
        "strategy_selector",
        "order_manager",
    )
    assert not any(item in source for item in forbidden)
