"""Additive capture, provider-free replay and policy comparison for A4 input."""

from datetime import datetime
from typing import Any

from pydantic import ValidationError

from tiaf.a3_hardening import canonical_json, exact_bytes_checksum
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.planner.digests import digest

from .contracts import (
    A4SemanticInputProjection,
    FoundationCapture,
    ProjectionBuildInput,
    ProjectionPolicyComparison,
)
from .projection import ProjectionIntegrityError, build_projection, validate_projection


def _exact_capture_payload(capture: FoundationCapture) -> dict[str, Any]:
    return capture.model_dump(
        mode="json",
        exclude={"exact_capture_checksum": True},
    )


def validate_foundation_capture(capture: FoundationCapture) -> FoundationCapture:
    try:
        capture = FoundationCapture.model_validate_json(capture.model_dump_json())
        if exact_bytes_checksum(capture.build_input_json) != capture.build_input_checksum:
            raise ValueError("foundation build-input checksum mismatch")
        if exact_bytes_checksum(capture.projection_json) != capture.projection_checksum:
            raise ValueError("foundation projection checksum mismatch")
        projection = validate_projection(
            A4SemanticInputProjection.model_validate_json(capture.projection_json)
        )
        if projection.semantic_fingerprint != capture.projection_semantic_fingerprint:
            raise ValueError("foundation projection fingerprint link mismatch")
        if capture.capture_id != f"foundation-capture:{projection.semantic_fingerprint[:24]}":
            raise ValueError("foundation capture ID does not match projection")
        expected = digest(_exact_capture_payload(capture))
        if expected != capture.exact_capture_checksum:
            raise ValueError("foundation capture exact checksum mismatch")
        return capture
    except (TypeError, ValueError, ValidationError) as exc:
        if isinstance(exc, ProjectionIntegrityError):
            raise
        raise ProjectionIntegrityError(str(exc)) from exc


def capture_projection(
    build_input: ProjectionBuildInput,
    *,
    captured_at: datetime | None = None,
) -> FoundationCapture:
    """Capture complete deterministic inputs and output; no external fallback exists."""
    projection = build_projection(build_input)
    input_json = canonical_json(build_input)
    projection_json = canonical_json(projection)
    provisional = FoundationCapture(
        capture_id=f"foundation-capture:{projection.semantic_fingerprint[:24]}",
        build_input_json=input_json,
        build_input_checksum=exact_bytes_checksum(input_json),
        projection_json=projection_json,
        projection_checksum=exact_bytes_checksum(projection_json),
        projection_semantic_fingerprint=projection.semantic_fingerprint,
        exact_capture_checksum="0" * 64,
        captured_at=captured_at or datetime.now(TIAF_TIMEZONE),
    )
    exact = digest(_exact_capture_payload(provisional))
    return validate_foundation_capture(
        provisional.model_copy(update={"exact_capture_checksum": exact})
    )


def capture_json(capture: FoundationCapture, *, indent: int | None = None) -> str:
    capture = validate_foundation_capture(capture)
    if indent is None:
        return canonical_json(capture)
    import json

    return json.dumps(capture.model_dump(mode="json"), sort_keys=True, indent=indent)


def replay_recorded(content: str) -> A4SemanticInputProjection:
    """Rebuild and compare using captured bytes only; no live/provider/model import path."""
    try:
        capture = validate_foundation_capture(FoundationCapture.model_validate_json(content))
        build_input = ProjectionBuildInput.model_validate_json(capture.build_input_json)
        rebuilt = build_projection(build_input)
        recorded = validate_projection(
            A4SemanticInputProjection.model_validate_json(capture.projection_json)
        )
        if rebuilt != recorded:
            raise ValueError("recorded projection differs from deterministic reconstruction")
        return recorded
    except (TypeError, ValueError, ValidationError) as exc:
        if isinstance(exc, ProjectionIntegrityError):
            raise
        raise ProjectionIntegrityError(str(exc)) from exc


def compare_projection_policy(
    capture: FoundationCapture,
    *,
    projection_policy_id: str,
    projection_policy_version: str,
    compared_at: datetime | None = None,
) -> tuple[A4SemanticInputProjection, ProjectionPolicyComparison]:
    """Produce a new projection/record; never relabel changed policy as exact replay."""
    capture = validate_foundation_capture(capture)
    original = replay_recorded(capture_json(capture))
    build_input = ProjectionBuildInput.model_validate_json(capture.build_input_json)
    original_policy = (
        build_input.header.projection_policy_id,
        build_input.header.projection_policy_version,
    )
    compared_policy = (projection_policy_id, projection_policy_version)
    if compared_policy == original_policy:
        raise ProjectionIntegrityError("policy comparison requires a changed policy identity")
    header = build_input.header.model_copy(
        update={
            "projection_policy_id": projection_policy_id,
            "projection_policy_version": projection_policy_version,
        }
    )
    compared = build_projection(build_input.model_copy(update={"header": header}))
    if compared.semantic_fingerprint == original.semantic_fingerprint:
        raise ProjectionIntegrityError("changed projection policy did not change semantic identity")
    identity = digest({"old": original.semantic_fingerprint, "new": compared.semantic_fingerprint})
    comparison_id = f"projection-policy-comparison:{identity[:24]}"
    record = ProjectionPolicyComparison(
        comparison_id=comparison_id,
        original_projection_id=original.projection_id,
        compared_projection_id=compared.projection_id,
        original_policy=original_policy,
        compared_policy=compared_policy,
        original_fingerprint=original.semantic_fingerprint,
        compared_fingerprint=compared.semantic_fingerprint,
        created_at=compared_at or datetime.now(TIAF_TIMEZONE),
    )
    return compared, record


def validate_successor(
    parent: A4SemanticInputProjection,
    successor_input: ProjectionBuildInput,
) -> ProjectionBuildInput:
    """Require explicit later cutoff and newly identified captured evidence."""
    parent = validate_projection(parent)
    successor_input = ProjectionBuildInput.model_validate_json(successor_input.model_dump_json())
    if successor_input.parent_projection_id != parent.projection_id:
        raise ProjectionIntegrityError(
            "successor does not reference the supplied parent projection"
        )
    if successor_input.parent_evidence_as_of != parent.header.evidence_as_of:
        raise ProjectionIntegrityError("successor parent cutoff does not match supplied parent")
    if successor_input.header.evidence_as_of <= parent.header.evidence_as_of:
        raise ProjectionIntegrityError("successor cutoff must advance")
    if not successor_input.new_evidence_ids:
        raise ProjectionIntegrityError("successor requires new evidence IDs")
    return successor_input
