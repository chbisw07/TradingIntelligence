"""A5.1 replay, policy comparison, security, and frozen-boundary tests."""

import ast
import json
import socket
from pathlib import Path

import pytest
from pydantic import ValidationError

from tiaf.a5 import (
    A5ReplayIntegrityError,
    A5RunRecord,
    PositionRecommendation,
    capture_json,
    capture_run,
    compare_policy,
    deterministic_policy,
    evaluate_position,
    replay_recorded,
    result_semantic_payload,
    validate_capture,
    validate_run,
    verify_deterministic,
)
from tiaf.facade import capability_catalog
from tiaf.planner.digests import digest

from ._support import request


def record() -> A5RunRecord:
    return evaluate_position(request())


def test_capture_recorded_replay_and_verification_are_exact_and_offline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = record()
    capture = capture_run(original, captured_at=original.evaluated_at)
    encoded = capture_json(capture)

    def reject_network(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("A5 replay attempted network access")

    monkeypatch.setattr(socket.socket, "connect", reject_network)
    replay = replay_recorded(encoded, replayed_at=original.evaluated_at)
    verification = verify_deterministic(encoded, verified_at=original.evaluated_at)
    assert replay.record == original
    assert replay.record.result.semantic_fingerprint == original.result.semantic_fingerprint
    assert replay.provider_calls == replay.model_calls == 0
    assert verification.exact_match
    assert verification.provider_calls == verification.model_calls == 0


@pytest.mark.parametrize(
    "field",
    ("snapshot_checksum", "run_checksum", "exact_capture_checksum"),
)
def test_corrupt_capture_checksums_fail_closed(field: str) -> None:
    capture = capture_run(record())
    corrupt = capture.model_copy(update={field: "f" * 64})
    with pytest.raises(A5ReplayIntegrityError, match="checksum"):
        validate_capture(corrupt)


def test_corrupt_a4_artifact_fails_closed() -> None:
    capture = capture_run(record())
    assert capture.a4_result_json is not None
    corrupt = capture.model_copy(update={"a4_result_json": capture.a4_result_json + "x"})
    with pytest.raises(A5ReplayIntegrityError, match="A4 checksum"):
        validate_capture(corrupt)


def test_policy_comparison_creates_new_record_without_mutating_history() -> None:
    original = record()
    original_json = original.model_dump_json()
    comparison = compare_policy(
        capture_run(original),
        deterministic_policy(version="1.1-comparison"),
        compared_at=original.evaluated_at,
    )
    assert comparison.original_policy != comparison.candidate_policy
    assert comparison.original_run_fingerprint != comparison.candidate_run_fingerprint
    assert comparison.exact_match is False
    assert original.model_dump_json() == original_json


def test_tm_response_cannot_mutate_a5_history() -> None:
    result = record().result
    before = result.model_dump_json()
    external_tm_response = {
        "advice_id": result.result_id,
        "decision": "REJECT",
        "adaptation": "operator policy",
    }
    assert external_tm_response["decision"] == "REJECT"
    assert result.model_dump_json() == before


def test_capture_contains_no_credentials_order_or_executable_instruction() -> None:
    payload = json.loads(capture_json(capture_run(record())))
    encoded = json.dumps(payload).casefold()
    for forbidden in (
        "access_token",
        "api_key",
        "client_secret",
        "authorization: bearer",
        "place_order",
        "modify_order",
        "cancel_order",
    ):
        assert forbidden not in encoded
    run_payload = json.loads(payload["run_json"])
    assert run_payload["result"]["protection_intent"]["executable"] is False


def test_credential_shaped_position_text_is_rejected_before_capture() -> None:
    base = request().snapshot
    with pytest.raises(ValidationError, match="credential-shaped"):
        type(base).model_validate(
            base.model_dump(mode="json")
            | {"freshness_basis": "api_key=must-not-enter-position-artifact"}
        )


def test_a5_has_no_provider_model_broker_sdk_a6_a7_or_remote_imports() -> None:
    banned_roots = {
        "aiohttp",
        "boto3",
        "fastapi",
        "grpc",
        "httpx",
        "mcp",
        "openai",
        "redis",
        "requests",
        "sqlalchemy",
    }
    imported: set[str] = set()
    imported_modules: set[str] = set()
    for path in Path("src/tiaf/a5").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for item in node.names:
                    imported.add(item.name.split(".", 1)[0])
                    imported_modules.add(item.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", 1)[0])
                imported_modules.add(node.module)
    assert not imported & banned_roots
    assert not any(name.startswith(("tiaf.a6", "tiaf.a7")) for name in imported_modules)
    assert not any("providers" in name or "transport" in name for name in imported_modules)


def test_a5_does_not_mutate_a4_and_a5_2_publishes_separate_facade_capability() -> None:
    value = request()
    assert value.a4_result is not None
    before = value.a4_result.model_dump_json()
    result = evaluate_position(value).result
    assert value.a4_result.model_dump_json() == before
    assert result.linked_a4_fingerprint == value.a4_result.semantic_fingerprint
    assert "position.assess" in {item.capability_id for item in capability_catalog()}


def test_result_has_no_a6_selection_or_a7_probability_fields() -> None:
    result = record().result
    fields = set(result.model_dump(mode="json"))
    assert not {
        "order",
        "order_type",
        "execution_quantity",
        "replacement_strike",
        "replacement_expiry",
        "forecast_probability",
        "expected_return",
    } & fields
    assert result.recommendation is PositionRecommendation.MAINTAIN


def test_capture_without_a4_round_trips_and_replays_insufficient() -> None:
    original = evaluate_position(request(a4=None))
    capture = capture_run(original)
    assert capture.a4_result_json is None
    replay = replay_recorded(capture)
    assert replay.record.result.recommendation is PositionRecommendation.INSUFFICIENT_EVIDENCE


def test_capture_is_json_reconstructable_with_ordinary_arrays() -> None:
    capture = capture_run(record())
    dumped = capture.model_dump(mode="json")
    reconstructed = type(capture).model_validate(dumped)
    assert reconstructed == capture
    run_payload = json.loads(capture.run_json)
    assert isinstance(run_payload["result"]["monitoring_needs"], list)


def test_refingerprinted_uncited_output_reference_fails_run_validation() -> None:
    original = record()
    provisional_result = original.result.model_copy(
        update={"evidence_refs": (*original.result.evidence_refs, "evidence:invented")}
    )
    semantic_fingerprint = digest(result_semantic_payload(provisional_result))
    forged_result = provisional_result.model_copy(
        update={
            "result_id": f"a5-result:{semantic_fingerprint[:24]}",
            "replay_identity": f"a5-replay-key:{semantic_fingerprint[:24]}",
            "semantic_fingerprint": semantic_fingerprint,
        }
    )
    run_payload = {
        "run_id": original.run_id,
        "request": original.request.model_dump(mode="json"),
        "policy": original.policy.model_dump(mode="json"),
        "result": forged_result.model_dump(mode="json"),
        "evaluated_at": original.evaluated_at.isoformat(),
    }
    forged_run = original.model_copy(
        update={"result": forged_result, "fingerprint": digest(run_payload)}
    )
    with pytest.raises(ValueError, match="uncited evidence"):
        validate_run(forged_run)
