"""Projection, capture, replay, policy and as-of semantics."""

import json

import pytest
from pydantic import ValidationError

from tiaf.source_semantics import (
    Missingness,
    ProjectionBuildInput,
    ProjectionGap,
    ProjectionIntegrityError,
    build_projection,
    capture_json,
    capture_projection,
    compare_projection_policy,
    replay_recorded,
    validate_successor,
)

from ._support import LATER, NOW, assertion, build_input, occurrence


def test_projection_preserves_frozen_a2_a3_identity_and_is_order_stable() -> None:
    value = build_input()
    first = build_projection(value)
    reordered = value.model_copy(
        update={
            "sources": tuple(reversed(value.sources)),
            "assertions": tuple(reversed(value.assertions)),
        }
    )
    second = build_projection(reordered)
    manifest = value.package.manifest
    assert first == second
    assert first.parents.a3_package_exact_checksum == manifest.exact_package_checksum
    assert first.parents.a2_assessment_id == manifest.a2_assessment_id
    assert first.parents.a2_evidence_fingerprint == manifest.a2_evidence_fingerprint
    assert first.opportunity.a39_state
    assert first.header.model_policy_ref == "model-policy:no-llm"
    assert first.usage_cost_knowledge == (("provider/model calls", "KNOWN_ZERO"),)


def test_projection_requires_mandatory_references_but_records_optional_gaps() -> None:
    value = build_input()
    missing = value.model_copy(update={"occurrences": ()})
    with pytest.raises(ProjectionIntegrityError, match="occurrence"):
        build_projection(missing)
    gap = ProjectionGap(
        gap_id="gap:optional-source-detail",
        missingness=Missingness.OPTIONAL,
        code="OPTIONAL_SOURCE_DETAIL_UNAVAILABLE",
        affected_reference="source:ril",
        reason="not included in captured parent",
    )
    projected = build_projection(value.model_copy(update={"gaps": (gap,)}))
    assert projected.gaps == (gap,)


def test_missing_or_corrupt_parent_artifact_digest_fails_closed() -> None:
    value = build_input()
    with pytest.raises(ProjectionIntegrityError, match="mandatory referenced artifact"):
        build_projection(value.model_copy(update={"referenced_artifact_digests": ()}))
    corrupt = tuple(
        (name, "f" * 64 if name == "a39-capture" else checksum)
        for name, checksum in value.referenced_artifact_digests
    )
    with pytest.raises(ProjectionIntegrityError, match="mandatory referenced artifact"):
        build_projection(value.model_copy(update={"referenced_artifact_digests": corrupt}))


def test_projection_only_capture_rejects_full_a2_assertion_claim() -> None:
    value = build_input()
    assert value.package.manifest.a2_capture.mode.value == "ORIGINAL_A38_PROJECTION"
    with pytest.raises(ProjectionIntegrityError, match="projection-only"):
        build_projection(
            value.model_copy(update={"requires_full_a2_assertion_ids": ("assertion:one",)})
        )


def test_capture_round_trip_is_exact_and_corruption_fails_closed() -> None:
    capture = capture_projection(build_input(), captured_at=NOW)
    encoded = capture_json(capture)
    replayed = replay_recorded(encoded)
    assert replayed.semantic_fingerprint == capture.projection_semantic_fingerprint
    assert replayed == build_projection(
        ProjectionBuildInput.model_validate_json(capture.build_input_json)
    )
    payload = json.loads(encoded)
    payload["projection_checksum"] = "f" * 64
    with pytest.raises(ProjectionIntegrityError, match="checksum"):
        replay_recorded(json.dumps(payload))


def test_policy_change_is_comparison_not_exact_replay() -> None:
    capture = capture_projection(build_input(), captured_at=NOW)
    compared, record = compare_projection_policy(
        capture,
        projection_policy_id="projection-policy:alternative",
        projection_policy_version="2.0",
        compared_at=LATER,
    )
    original = replay_recorded(capture_json(capture))
    assert compared.projection_id != original.projection_id
    assert record.original_projection_id == original.projection_id
    assert record.compared_projection_id == compared.projection_id


def test_successor_requires_later_cutoff_and_new_captured_evidence() -> None:
    parent_input = build_input()
    parent = build_projection(parent_input)
    second_occurrence = occurrence(
        "occurrence:two", evidence_id="evidence:two", acquired_at=LATER
    )
    second_assertion = assertion(
        "assertion:two", 101, occurrence_id=second_occurrence.occurrence_id
    )
    successor = build_input(
        assertion_items=(parent_input.assertions[0], second_assertion),
        occurrence_items=(parent_input.occurrences[0], second_occurrence),
        as_of=LATER,
        parent_projection_id=parent.projection_id,
        parent_as_of=NOW,
        new_evidence_ids=("evidence:two",),
        package=parent_input.package,
    )
    assert validate_successor(parent, successor) == successor
    projected = build_projection(successor)
    assert projected.parent_projection_id == parent.projection_id
    assert projected.parent_evidence_as_of == parent.header.evidence_as_of
    assert projected.new_evidence_ids == ("evidence:two",)
    assert projected.parents == parent.parents
    backdated = successor.model_copy(
        update={"new_evidence_ids": (parent_input.occurrences[0].evidence_id,)}
    )
    with pytest.raises(ProjectionIntegrityError, match="after parent cutoff"):
        build_projection(backdated)
    with pytest.raises(ValidationError, match="successor"):
        ProjectionBuildInput.model_validate(
            successor.model_dump() | {"new_evidence_ids": []}
        )


def test_json_uses_arrays_and_kolkata_offsets_and_models_are_frozen() -> None:
    projected = build_projection(build_input())
    dumped = projected.model_dump(mode="json")
    assert isinstance(dumped["sources"], list)
    assert dumped["header"]["evidence_as_of"].endswith("+05:30")
    rebuilt = type(projected).model_validate(dumped)
    assert rebuilt == projected
    with pytest.raises(ValidationError):
        projected.assertions = ()


def test_source_semantics_has_no_provider_model_or_a4_reasoning_exports() -> None:
    import tiaf.source_semantics as module

    exported = set(module.__all__)
    assert "SourceScore" not in exported
    assert not {name for name in exported if name.startswith("A4") and "Projection" not in name}


def test_recorded_replay_does_not_open_network(monkeypatch: pytest.MonkeyPatch) -> None:
    import socket

    capture = capture_projection(build_input(), captured_at=NOW)

    def reject_network(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("replay attempted network access")

    monkeypatch.setattr(socket.socket, "connect", reject_network)
    assert replay_recorded(capture_json(capture)).projection_id.startswith("a4-input:")
