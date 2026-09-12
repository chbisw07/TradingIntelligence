"""Content-addressed A5.1 capture, offline replay, and policy comparison."""

from datetime import datetime
from typing import Any

from pydantic import ValidationError

from tiaf.a3_hardening import canonical_json, exact_bytes_checksum
from tiaf.a4 import A4Result
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.planner.digests import digest

from .contracts import (
    A5Capture,
    A5DeterministicPolicy,
    A5PolicyComparison,
    A5ReplayResult,
    A5RunRecord,
    A5VerificationResult,
    PositionSnapshot,
)
from .errors import A5ReplayIntegrityError
from .evaluation import evaluate_position, validate_run
from .policy import require_supported_policy


def _exact_capture_payload(capture: A5Capture) -> dict[str, Any]:
    return capture.model_dump(mode="json", exclude={"exact_capture_checksum": True})


def validate_capture(capture: A5Capture) -> A5Capture:
    try:
        capture = A5Capture.model_validate_json(capture.model_dump_json())
        if exact_bytes_checksum(capture.snapshot_json) != capture.snapshot_checksum:
            raise ValueError("A5 capture snapshot checksum mismatch")
        if exact_bytes_checksum(capture.run_json) != capture.run_checksum:
            raise ValueError("A5 capture run checksum mismatch")
        snapshot = PositionSnapshot.model_validate_json(capture.snapshot_json)
        record = validate_run(A5RunRecord.model_validate_json(capture.run_json))
        if snapshot != record.request.snapshot:
            raise ValueError("A5 capture snapshot and run input differ")
        if digest(snapshot) != capture.snapshot_fingerprint:
            raise ValueError("A5 capture snapshot fingerprint mismatch")
        current_a4 = record.request.successor_a4_result or record.request.a4_result
        if current_a4 is None:
            if any(
                value is not None
                for value in (
                    capture.a4_result_json,
                    capture.a4_result_checksum,
                    capture.a4_result_fingerprint,
                )
            ):
                raise ValueError("A5 capture has unexpected linked A4 artifact")
        else:
            if (
                capture.a4_result_json is None
                or capture.a4_result_checksum is None
                or capture.a4_result_fingerprint is None
            ):
                raise ValueError("A5 capture is missing linked A4 artifact")
            if exact_bytes_checksum(capture.a4_result_json) != capture.a4_result_checksum:
                raise ValueError("A5 capture A4 checksum mismatch")
            captured_a4 = A4Result.model_validate_json(capture.a4_result_json)
            if captured_a4 != current_a4:
                raise ValueError("A5 capture A4 result and run input differ")
            if captured_a4.semantic_fingerprint != capture.a4_result_fingerprint:
                raise ValueError("A5 capture A4 fingerprint mismatch")
        if record.fingerprint != capture.run_fingerprint:
            raise ValueError("A5 capture run fingerprint mismatch")
        if capture.capture_id != f"a5-capture:{record.fingerprint[:24]}":
            raise ValueError("A5 capture identity does not match run")
        if digest(_exact_capture_payload(capture)) != capture.exact_capture_checksum:
            raise ValueError("A5 capture exact checksum mismatch")
        return capture
    except (TypeError, ValueError, ValidationError) as exc:
        if isinstance(exc, A5ReplayIntegrityError):
            raise
        raise A5ReplayIntegrityError(str(exc)) from exc


def capture_run(
    record: A5RunRecord,
    *,
    captured_at: datetime | None = None,
) -> A5Capture:
    record = validate_run(record)
    snapshot_json = canonical_json(record.request.snapshot)
    current_a4 = record.request.successor_a4_result or record.request.a4_result
    a4_json = canonical_json(current_a4) if current_a4 is not None else None
    run_json = canonical_json(record)
    provisional = A5Capture(
        capture_id=f"a5-capture:{record.fingerprint[:24]}",
        snapshot_json=snapshot_json,
        snapshot_checksum=exact_bytes_checksum(snapshot_json),
        snapshot_fingerprint=digest(record.request.snapshot),
        a4_result_json=a4_json,
        a4_result_checksum=exact_bytes_checksum(a4_json) if a4_json is not None else None,
        a4_result_fingerprint=(
            current_a4.semantic_fingerprint if current_a4 is not None else None
        ),
        run_json=run_json,
        run_checksum=exact_bytes_checksum(run_json),
        run_fingerprint=record.fingerprint,
        exact_capture_checksum="0" * 64,
        captured_at=captured_at or datetime.now(TIAF_TIMEZONE),
    )
    return validate_capture(
        provisional.model_copy(
            update={"exact_capture_checksum": digest(_exact_capture_payload(provisional))}
        )
    )


def capture_json(capture: A5Capture, *, indent: int | None = None) -> str:
    capture = validate_capture(capture)
    if indent is None:
        return canonical_json(capture)
    import json

    return json.dumps(capture.model_dump(mode="json"), sort_keys=True, indent=indent)


def replay_recorded(
    capture: A5Capture | str,
    *,
    replayed_at: datetime | None = None,
) -> A5ReplayResult:
    """Return the exact recorded A5 run without live repair."""
    try:
        value = A5Capture.model_validate_json(capture) if isinstance(capture, str) else capture
        value = validate_capture(value)
        record = validate_run(A5RunRecord.model_validate_json(value.run_json))
        payload = {
            "mode": "RECORDED",
            "capture": value.capture_id,
            "run": record.fingerprint,
        }
        fingerprint = digest(payload)
        return A5ReplayResult(
            replay_id=f"a5-replay:{fingerprint[:24]}",
            record=record,
            replayed_at=replayed_at or datetime.now(TIAF_TIMEZONE),
            fingerprint=fingerprint,
        )
    except (TypeError, ValueError, ValidationError) as exc:
        if isinstance(exc, A5ReplayIntegrityError):
            raise
        raise A5ReplayIntegrityError(str(exc)) from exc


def verify_deterministic(
    capture: A5Capture | str,
    *,
    verified_at: datetime | None = None,
) -> A5VerificationResult:
    value = A5Capture.model_validate_json(capture) if isinstance(capture, str) else capture
    value = validate_capture(value)
    recorded = validate_run(A5RunRecord.model_validate_json(value.run_json))
    verified = evaluate_position(
        recorded.request,
        policy=require_supported_policy(recorded.policy),
        evaluated_at=recorded.evaluated_at,
    )
    exact = (
        recorded.fingerprint == verified.fingerprint
        and recorded.result.semantic_fingerprint == verified.result.semantic_fingerprint
    )
    payload = {
        "mode": "DETERMINISTIC_VERIFICATION",
        "recorded": recorded.fingerprint,
        "verified": verified.fingerprint,
        "exact": exact,
    }
    fingerprint = digest(payload)
    return A5VerificationResult(
        verification_id=f"a5-verification:{fingerprint[:24]}",
        recorded_run_fingerprint=recorded.fingerprint,
        verified_run_fingerprint=verified.fingerprint,
        recorded_semantic_fingerprint=recorded.result.semantic_fingerprint,
        verified_semantic_fingerprint=verified.result.semantic_fingerprint,
        exact_match=exact,
        verified_at=verified_at or datetime.now(TIAF_TIMEZONE),
        fingerprint=fingerprint,
    )


def compare_policy(
    capture: A5Capture | str,
    candidate_policy: A5DeterministicPolicy,
    *,
    compared_at: datetime | None = None,
) -> A5PolicyComparison:
    value = A5Capture.model_validate_json(capture) if isinstance(capture, str) else capture
    value = validate_capture(value)
    original = validate_run(A5RunRecord.model_validate_json(value.run_json))
    candidate_policy = require_supported_policy(candidate_policy)
    candidate_request = original.request.model_copy(
        update={
            "policy_id": candidate_policy.policy_id,
            "policy_version": candidate_policy.policy_version,
            "monitoring_policy_ref": candidate_policy.monitoring_policy_ref,
        }
    )
    candidate = evaluate_position(
        candidate_request,
        policy=candidate_policy,
        evaluated_at=original.evaluated_at,
    )
    payload = {
        "mode": "POLICY_COMPARISON",
        "original_policy": (original.policy.policy_id, original.policy.policy_version),
        "candidate_policy": (candidate.policy.policy_id, candidate.policy.policy_version),
        "original": original.fingerprint,
        "candidate": candidate.fingerprint,
        "original_recommendation": original.result.recommendation,
        "candidate_recommendation": candidate.result.recommendation,
        "original_posture": original.result.posture,
        "candidate_posture": candidate.result.posture,
    }
    fingerprint = digest(payload)
    return A5PolicyComparison(
        comparison_id=f"a5-policy-comparison:{fingerprint[:24]}",
        original_policy=(original.policy.policy_id, original.policy.policy_version),
        candidate_policy=(candidate.policy.policy_id, candidate.policy.policy_version),
        original_run_fingerprint=original.fingerprint,
        candidate_run_fingerprint=candidate.fingerprint,
        original_recommendation=original.result.recommendation,
        candidate_recommendation=candidate.result.recommendation,
        original_posture=original.result.posture,
        candidate_posture=candidate.result.posture,
        exact_match=original.fingerprint == candidate.fingerprint,
        compared_at=compared_at or datetime.now(TIAF_TIMEZONE),
        fingerprint=fingerprint,
    )
