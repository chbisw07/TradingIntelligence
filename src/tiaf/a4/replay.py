"""Captured deterministic A4 replay, verification and policy comparison."""

from datetime import datetime
from typing import Any

from pydantic import ValidationError

from tiaf.a3_hardening import canonical_json, exact_bytes_checksum
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.planner.digests import digest
from tiaf.source_semantics import A4SemanticInputProjection, validate_projection

from .contracts import (
    A4Capture,
    A4DeterministicPolicy,
    A4PolicyComparison,
    A4ReplayResult,
    A4RunRecord,
    A4VerificationResult,
)
from .evaluation import A4EvaluationError, evaluate_projection, validate_run
from .policy import require_supported_policy


class A4ReplayIntegrityError(A4EvaluationError):
    """Captured A4 bytes, links, policy, or result failed closed."""


def _exact_capture_payload(capture: A4Capture) -> dict[str, Any]:
    return capture.model_dump(mode="json", exclude={"exact_capture_checksum": True})


def validate_capture(capture: A4Capture) -> A4Capture:
    try:
        capture = A4Capture.model_validate_json(capture.model_dump_json())
        if exact_bytes_checksum(capture.projection_json) != capture.projection_checksum:
            raise ValueError("A4 capture projection checksum mismatch")
        if exact_bytes_checksum(capture.run_json) != capture.run_checksum:
            raise ValueError("A4 capture run checksum mismatch")
        projection = validate_projection(
            A4SemanticInputProjection.model_validate_json(capture.projection_json)
        )
        record = validate_run(A4RunRecord.model_validate_json(capture.run_json))
        if projection != record.input_projection:
            raise ValueError("A4 capture projection and run input differ")
        if capture.projection_fingerprint != projection.semantic_fingerprint:
            raise ValueError("A4 capture projection fingerprint link mismatch")
        if capture.run_fingerprint != record.fingerprint:
            raise ValueError("A4 capture run fingerprint link mismatch")
        if capture.capture_id != f"a4-capture:{record.fingerprint[:24]}":
            raise ValueError("A4 capture ID does not match run")
        if digest(_exact_capture_payload(capture)) != capture.exact_capture_checksum:
            raise ValueError("A4 capture exact checksum mismatch")
        return capture
    except (TypeError, ValueError, ValidationError) as exc:
        if isinstance(exc, A4ReplayIntegrityError):
            raise
        raise A4ReplayIntegrityError(str(exc)) from exc


def capture_run(
    record: A4RunRecord,
    *,
    captured_at: datetime | None = None,
) -> A4Capture:
    record = validate_run(record)
    projection_json = canonical_json(record.input_projection)
    run_json = canonical_json(record)
    provisional = A4Capture(
        capture_id=f"a4-capture:{record.fingerprint[:24]}",
        projection_json=projection_json,
        projection_checksum=exact_bytes_checksum(projection_json),
        projection_fingerprint=record.input_projection.semantic_fingerprint,
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


def capture_json(capture: A4Capture, *, indent: int | None = None) -> str:
    capture = validate_capture(capture)
    if indent is None:
        return canonical_json(capture)
    import json

    return json.dumps(capture.model_dump(mode="json"), sort_keys=True, indent=indent)


def replay_recorded(
    capture: A4Capture | str,
    *,
    replayed_at: datetime | None = None,
) -> A4ReplayResult:
    """Reconstruct stored A4 semantics exactly; never invoke live repair."""
    try:
        value = A4Capture.model_validate_json(capture) if isinstance(capture, str) else capture
        value = validate_capture(value)
        record = validate_run(A4RunRecord.model_validate_json(value.run_json))
        when = replayed_at or datetime.now(TIAF_TIMEZONE)
        fingerprint = digest(
            {"mode": "RECORDED", "capture": value.capture_id, "run": record.fingerprint}
        )
        return A4ReplayResult(
            replay_id=f"a4-replay:{fingerprint[:24]}",
            record=record,
            replayed_at=when,
            fingerprint=fingerprint,
        )
    except (TypeError, ValueError, ValidationError) as exc:
        if isinstance(exc, A4ReplayIntegrityError):
            raise
        raise A4ReplayIntegrityError(str(exc)) from exc


def verify_deterministic(
    capture: A4Capture | str,
    *,
    verified_at: datetime | None = None,
) -> A4VerificationResult:
    """Re-execute eligible deterministic logic using the captured policy and input."""
    value = A4Capture.model_validate_json(capture) if isinstance(capture, str) else capture
    value = validate_capture(value)
    recorded = validate_run(A4RunRecord.model_validate_json(value.run_json))
    verified = evaluate_projection(
        recorded.input_projection,
        policy=require_supported_policy(recorded.policy),
        evaluated_at=recorded.evaluated_at,
    )
    exact = recorded.fingerprint == verified.fingerprint
    when = verified_at or datetime.now(TIAF_TIMEZONE)
    payload = {
        "mode": "DETERMINISTIC_VERIFICATION",
        "recorded": recorded.fingerprint,
        "verified": verified.fingerprint,
        "exact_match": exact,
    }
    fingerprint = digest(payload)
    return A4VerificationResult(
        verification_id=f"a4-verification:{fingerprint[:24]}",
        recorded_run_fingerprint=recorded.fingerprint,
        verified_run_fingerprint=verified.fingerprint,
        exact_match=exact,
        verified_at=when,
        fingerprint=fingerprint,
    )


def compare_policy(
    capture: A4Capture | str,
    candidate_policy: A4DeterministicPolicy,
    *,
    compared_at: datetime | None = None,
) -> A4PolicyComparison:
    """Create a successor comparison; never relabel a policy change as replay."""
    value = A4Capture.model_validate_json(capture) if isinstance(capture, str) else capture
    value = validate_capture(value)
    original = validate_run(A4RunRecord.model_validate_json(value.run_json))
    candidate = evaluate_projection(
        original.input_projection,
        policy=require_supported_policy(candidate_policy),
        evaluated_at=original.evaluated_at,
    )
    if original.result.disposition is None or candidate.result.disposition is None:
        raise A4ReplayIntegrityError("policy comparison requires valid dispositions")
    when = compared_at or datetime.now(TIAF_TIMEZONE)
    payload = {
        "mode": "POLICY_COMPARISON",
        "original_policy": (original.policy.policy_id, original.policy.policy_version),
        "candidate_policy": (candidate.policy.policy_id, candidate.policy.policy_version),
        "original": original.fingerprint,
        "candidate": candidate.fingerprint,
        "original_disposition": original.result.disposition,
        "candidate_disposition": candidate.result.disposition,
    }
    fingerprint = digest(payload)
    return A4PolicyComparison(
        comparison_id=f"a4-policy-comparison:{fingerprint[:24]}",
        original_policy=(original.policy.policy_id, original.policy.policy_version),
        candidate_policy=(candidate.policy.policy_id, candidate.policy.policy_version),
        original_run_fingerprint=original.fingerprint,
        candidate_run_fingerprint=candidate.fingerprint,
        original_disposition=original.result.disposition,
        candidate_disposition=candidate.result.disposition,
        exact_match=original.fingerprint == candidate.fingerprint,
        compared_at=when,
        fingerprint=fingerprint,
    )

