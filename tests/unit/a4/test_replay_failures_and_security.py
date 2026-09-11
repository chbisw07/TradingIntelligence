"""A4 benchmark replay, failure, and forbidden-boundary acceptance."""

import ast
import json
import socket
from pathlib import Path

import pytest

import tiaf.a4.evaluation as evaluation_module
from tiaf.a4 import (
    A4Disposition,
    A4EvaluationError,
    A4InputIntegrityError,
    A4OutputIntegrityError,
    A4ReplayIntegrityError,
    A4RunRecord,
    ChallengerError,
    UnsupportedA4PolicyError,
    capture_json,
    capture_run,
    compare_policy,
    deterministic_policy,
    evaluate_projection,
    replay_recorded,
    validate_capture,
    validate_result,
    verify_deterministic,
)

from ._support import clean_projection


def record() -> A4RunRecord:
    projection = clean_projection()
    return evaluate_projection(projection, evaluated_at=projection.header.evidence_as_of)


def test_unchanged_deterministic_rerun_has_identical_semantic_fingerprint() -> None:
    first = record()
    second = evaluate_projection(first.input_projection)
    assert first.result.semantic_fingerprint == second.result.semantic_fingerprint
    assert first.fingerprint == second.fingerprint


def test_policy_version_change_creates_explicit_non_replay_comparison() -> None:
    original = record()
    capture = capture_run(original, captured_at=original.evaluated_at)
    comparison = compare_policy(
        capture,
        deterministic_policy(version="1.1-comparison"),
        compared_at=original.evaluated_at,
    )
    assert comparison.original_policy != comparison.candidate_policy
    assert comparison.original_run_fingerprint != comparison.candidate_run_fingerprint
    assert comparison.exact_match is False
    assert comparison.original_disposition is comparison.candidate_disposition


def test_recorded_replay_and_verification_are_offline_and_exact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = record()
    capture = capture_run(original, captured_at=original.evaluated_at)
    encoded = capture_json(capture)

    def reject_network(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("A4 replay attempted network access")

    monkeypatch.setattr(socket.socket, "connect", reject_network)
    replay = replay_recorded(encoded, replayed_at=original.evaluated_at)
    verification = verify_deterministic(encoded, verified_at=original.evaluated_at)
    assert replay.record == original
    assert replay.provider_calls == replay.model_calls == 0
    assert verification.exact_match
    assert verification.provider_calls == verification.model_calls == 0


def test_corrupt_capture_and_parent_projection_fail_closed() -> None:
    original = record()
    capture = capture_run(original, captured_at=original.evaluated_at)
    corrupt_capture = capture.model_copy(update={"run_checksum": "f" * 64})
    with pytest.raises(A4ReplayIntegrityError, match="checksum"):
        validate_capture(corrupt_capture)
    corrupt_projection = original.input_projection.model_copy(
        update={"semantic_fingerprint": "f" * 64}
    )
    with pytest.raises(A4InputIntegrityError, match="fingerprint"):
        evaluate_projection(corrupt_projection)


def test_unsupported_policy_is_explicit() -> None:
    unsupported = deterministic_policy().model_copy(update={"policy_version": "9.0"})
    with pytest.raises(UnsupportedA4PolicyError, match="unsupported"):
        evaluate_projection(clean_projection(), policy=unsupported)


def test_challenger_failure_is_partial_abstain_never_favorable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise ChallengerError("synthetic challenger failure")

    monkeypatch.setattr(evaluation_module, "generate_challenges", fail)
    result = evaluate_projection(clean_projection()).result
    assert result.disposition is A4Disposition.ABSTAIN
    assert result.execution_status.value == "PARTIAL"
    assert result.failures[0].code.value == "CHALLENGER_FAILED"


def test_arbitrator_failure_has_no_valid_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise ValueError("synthetic arbitrator failure")

    monkeypatch.setattr(evaluation_module, "arbitrate", fail)
    with pytest.raises(A4EvaluationError, match="arbitration failed"):
        evaluate_projection(clean_projection())


def test_thesis_construction_failure_has_no_valid_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise ValueError("synthetic thesis failure")

    monkeypatch.setattr(evaluation_module, "build_theses", fail)
    with pytest.raises(A4EvaluationError, match="thesis construction failed"):
        evaluate_projection(clean_projection())


def test_output_fingerprint_corruption_is_rejected() -> None:
    original = record()
    corrupt = original.result.model_copy(update={"semantic_fingerprint": "f" * 64})
    with pytest.raises(A4OutputIntegrityError, match="fingerprint"):
        validate_result(corrupt, original.input_projection, original.policy)


def test_a4_has_no_model_provider_broker_remote_or_future_layer_imports() -> None:
    banned_imports = {
        "aiohttp",
        "boto3",
        "fastapi",
        "grpc",
        "httpx",
        "openai",
        "redis",
        "requests",
        "sqlalchemy",
    }
    banned_classes = {
        "Broker",
        "Order",
        "PositionManager",
        "OptionSelector",
        "ForecastModel",
    }
    imported: set[str] = set()
    classes: set[str] = set()
    for path in Path("src/tiaf/a4").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(item.name.split(".", 1)[0] for item in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.ClassDef):
                classes.add(node.name)
    assert not imported & banned_imports
    assert not classes & banned_classes
    assert "provider" not in imported
    assert "model" not in imported


def test_capture_json_contains_no_credentials_or_execution_fields() -> None:
    payload = json.loads(capture_json(capture_run(record())))
    encoded = json.dumps(payload).casefold()
    assert "access_token" not in encoded
    assert "api_key" not in encoded
    assert "broker" not in encoded
    assert "execution_approval" not in encoded
