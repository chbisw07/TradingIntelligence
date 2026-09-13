"""Traceable A6.4 public-path goldens and replay hardening."""

import csv
import json
import os
import subprocess
import sys
from importlib import import_module
from pathlib import Path
from typing import Any, cast

import pytest

from tiaf.facade import (
    ExpressionAssessInput,
    ExpressionAssessResult,
    RecordedReplayResult,
    TrustedArtifact,
)
from tiaf.shell import ShellRuntime
from tiaf.trade_expression import A6ReplayIntegrityError, verify_trade_expression_replay

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = Path(__file__).with_name("corpus_manifest.csv")
GOLDENS = Path(__file__).with_name("golden_public_results.json")


def _manifest() -> list[dict[str, str]]:
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _goldens() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(GOLDENS.read_text(encoding="utf-8")))


def _captured_artifacts() -> tuple[TrustedArtifact, ...]:
    support = import_module("tests.unit.facade._support")
    return cast(tuple[TrustedArtifact, ...], support.captured_artifacts())


def _expression_runtime(root: Path, ref: str) -> ShellRuntime:
    support = import_module("tests.unit.shell._support")
    return cast(ShellRuntime, support.expression_runtime(root, ref))


def _capture(ref: str) -> ExpressionAssessInput:
    artifact = next(item for item in _captured_artifacts() if item.artifact_ref == ref)
    return ExpressionAssessInput.model_validate_json(artifact.content)


def test_manifest_has_all_93_explicit_traceable_cases() -> None:
    rows = _manifest()
    expected_fields = {
        "corpus_case_id",
        "scenario",
        "expected_result",
        "policy_profile",
        "fixture_artifact",
        "test_location",
        "coverage_category",
    }
    assert len(rows) == 93
    assert [row["corpus_case_id"] for row in rows] == [
        f"A6C-{index:03d}" for index in range(1, 94)
    ]
    assert all(set(row) == expected_fields and all(row.values()) for row in rows)
    assert {row["coverage_category"] for row in rows} == {
        "UPSTREAM_ADMISSION",
        "TIMING_FRESHNESS",
        "COVERAGE",
        "CANDIDATE_GEOMETRY",
        "LIQUIDITY_QUOTE_QUALITY",
        "PREMIUM",
        "EVENTS",
        "RANKING",
        "DISPOSITIONS",
        "ALTERNATIVES",
        "REPLAY_INTEGRITY",
        "PUBLIC_SURFACE",
    }
    for row in rows:
        relative_path, test_name = row["test_location"].split("::", maxsplit=1)
        source = ROOT / relative_path
        assert source.is_file(), row["corpus_case_id"]
        assert f"def {test_name}(" in source.read_text(encoding="utf-8"), row[
            "corpus_case_id"
        ]


@pytest.mark.parametrize(
    "golden",
    _goldens()["cases"],
    ids=lambda item: item["disposition"].lower(),
)
def test_public_golden_expression_cases(tmp_path: Path, golden: dict[str, Any]) -> None:
    ref = golden["artifact_ref"]
    shell = _expression_runtime(tmp_path, ref)
    human = shell.execute_tokens(["expression", "assess", "--input", ref])
    assert human.exit_code == 0 and human.outcome is not None
    result = human.outcome.facade_result
    assert isinstance(result, ExpressionAssessResult)
    assessment = result.assessment
    recorded = _capture(ref).recorded_assessment
    assert recorded is not None
    assert assessment == recorded
    assert assessment.disposition.value == golden["disposition"]
    assert assessment.preferred_candidate_ref == golden["preferred_candidate_ref"]
    assert list(assessment.alternative_candidate_refs) == golden[
        "alternative_candidate_refs"
    ]
    assert list(assessment.explanation.disposition_reason_codes) == golden[
        "disposition_reason_codes"
    ]
    assert sorted(
        {item.decisive_dimension for item in assessment.explanation.rank_differences}
    ) == golden["rank_difference_dimensions"]
    rejection_reasons = {
        reason
        for item in assessment.candidate_evaluations
        for reason in item.rejection_reason_codes
    }
    assert set(golden["required_candidate_rejection_reasons"]).issubset(
        rejection_reasons
    )
    assert list(assessment.blockers) == golden["blockers"]
    assert set(golden["required_gaps"]).issubset(assessment.gaps)
    assert set(_goldens()["required_invalidation_conditions"]) == set(
        assessment.invalidation_conditions
    )
    assert assessment.semantic_fingerprint == recorded.semantic_fingerprint
    assert result.authority_statement == "ADVISORY_ONLY_TM_RETAINS_ACTION_AUTHORITY"
    assert result.metadata.usage.model_calls == result.metadata.usage.tool_calls == 0
    assert f"Disposition: {golden['disposition']}" in human.stdout
    assert "Interpretation:" in human.stdout
    assert "Policy Refs:" in human.stdout
    assert "Invalidation Conditions:" in human.stdout
    assert "ADVISORY_ONLY_TM_RETAINS_ACTION_AUTHORITY" in human.stdout
    if golden["rank_difference_dimensions"]:
        assert "Rank Differences:" in human.stdout
        assert all(
            dimension in human.stdout
            for dimension in golden["rank_difference_dimensions"]
        )

    json_result = _expression_runtime(tmp_path, ref).execute_tokens(
        ["--output", "json", "expression", "assess", "--input", ref]
    )
    assert json_result.outcome is not None
    payload = json.loads(json_result.stdout)
    rebuilt = ExpressionAssessResult.model_validate(payload["result"])
    assert rebuilt.assessment == assessment
    assert rebuilt == json_result.outcome.facade_result

    explained = shell.execute_tokens(["--output", "json", "explain", "last"])
    traced = shell.execute_tokens(["--output", "json", "trace", "last"])
    explanation = json.loads(explained.stdout)
    trace = json.loads(traced.stdout)
    assert explanation["candidate_evaluations"] == [
        item.model_dump(mode="json") for item in assessment.candidate_evaluations
    ]
    assert explanation["invalidation_conditions"] == list(
        assessment.invalidation_conditions
    )
    assert trace["request_fingerprint"] == assessment.request_fingerprint
    assert trace["admission_fingerprint"] == assessment.admission_fingerprint
    assert trace["a4_result_fingerprint"] == assessment.a4_result_fingerprint
    assert trace["evidence_fingerprint"] == assessment.evidence_fingerprint
    assert trace["composition_refs"] == list(assessment.composition_refs)
    assert trace["semantic_fingerprint"] == assessment.semantic_fingerprint


@pytest.mark.parametrize(
    "ref",
    [item["artifact_ref"] for item in _goldens()["cases"]],
)
def test_public_recorded_replay_matches_golden(tmp_path: Path, ref: str) -> None:
    replayed = _expression_runtime(tmp_path, ref).execute_tokens(
        ["replay", "recorded", "--artifact-ref", ref]
    )
    assert replayed.exit_code == 0 and replayed.outcome is not None
    result = replayed.outcome.facade_result
    assert isinstance(result, RecordedReplayResult)
    assert result.kind.value == "A6_RECORDED"
    assert result.a6_assessment == _capture(ref).recorded_assessment
    assert result.metadata.usage.model_calls == result.metadata.usage.tool_calls == 0


def test_composition_pin_mismatch_fails_exact_replay() -> None:
    capture = _capture("artifact:a6-available")
    assert capture.recorded_assessment is not None
    with pytest.raises(A6ReplayIntegrityError):
        verify_trade_expression_replay(
            capture.recorded_assessment,
            capture.request,
            capture.a4_result,
            capture.evidence,
            capture.policy,
            capture.admission,
            composition_refs=("composition:changed-after-capture",),
        )


def test_fixed_capture_replay_is_hash_seed_and_environment_independent(
    tmp_path: Path,
) -> None:
    artifact = next(
        item
        for item in _captured_artifacts()
        if item.artifact_ref == "artifact:a6-available"
    )
    capture_path = tmp_path / "fixed-capture.json"
    capture_path.write_text(artifact.content, encoding="utf-8")
    program = """
from pathlib import Path
import sys
from tiaf.facade import ExpressionAssessInput
from tiaf.trade_expression import verify_trade_expression_replay

capture = ExpressionAssessInput.model_validate_json(Path(sys.argv[1]).read_text())
assert capture.recorded_assessment is not None
result = verify_trade_expression_replay(
    capture.recorded_assessment,
    capture.request,
    capture.a4_result,
    capture.evidence,
    capture.policy,
    capture.admission,
    composition_refs=capture.composition_refs,
)
print(result.semantic_fingerprint)
"""
    fingerprints: set[str] = set()
    for seed in ("1", "2", "8675309"):
        environment = {
            **os.environ,
            "PYTHONHASHSEED": seed,
            "TIAF_A6_POLICY_VERSION": "unsupported-current-environment-value",
            "TIAF_A6_REGISTRY_EXPANSION": "future-capability:ignored",
            "TZ": "UTC",
        }
        completed = subprocess.run(
            [sys.executable, "-c", program, str(capture_path)],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert completed.returncode == 0, completed.stderr
        fingerprints.add(completed.stdout.strip())
    expected = _capture("artifact:a6-available").recorded_assessment
    assert expected is not None
    assert fingerprints == {expected.semantic_fingerprint}
