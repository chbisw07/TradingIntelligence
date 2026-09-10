"""A3.10 immutable contracts, capture modes, checksums and local store."""

from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from tiaf.a3_hardening import (
    A2CaptureMode,
    A3CorpusStoreError,
    A3ReplayCorpusStore,
    CaptureOrigin,
    CorpusCase,
    EvidenceStatus,
    MilestoneEvidence,
    PackageIntegrityError,
    PortableA3ReplayPackage,
    corpus_manifest,
    load_package_json,
    package_json,
    validate_package,
)

from ._support import BUILDER, NOW, full_a2_package, operational_variant, package_for


def test_contracts_are_frozen_and_json_lists_round_trip_to_tuples() -> None:
    package = package_for()
    payload = package.model_dump(mode="json")
    assert isinstance(payload["manifest"]["active_opinion_ids"], list)
    rebuilt = PortableA3ReplayPackage.model_validate(payload)
    assert isinstance(rebuilt.manifest.active_opinion_ids, tuple)
    with pytest.raises(ValidationError, match="frozen"):
        rebuilt.manifest.package_id = "changed"
    with pytest.raises(AttributeError):
        rebuilt.manifest.active_opinion_ids.append("changed")  # type: ignore[attr-defined]


def test_timestamp_contracts_normalize_aware_utc_and_reject_naive() -> None:
    item = MilestoneEvidence(
        evidence_id="utc",
        category="TEST",
        status=EvidenceStatus.PASS,
        required=True,
        artifact_refs=("test",),
        observed_at=datetime(2026, 9, 10, tzinfo=UTC),
        note="aware UTC input",
    )
    offset = item.observed_at.utcoffset()
    assert offset is not None
    assert offset.total_seconds() == 19_800
    assert "+05:30" in item.model_dump_json()
    with pytest.raises(ValidationError, match="timezone-aware"):
        item.model_copy(update={"observed_at": datetime(2026, 9, 10)}).__class__.model_validate(
            item.model_dump() | {"observed_at": datetime(2026, 9, 10)}
        )


def test_projection_and_full_a2_capture_modes_are_honest() -> None:
    projection = package_for()
    full = full_a2_package()
    assert projection.manifest.a2_capture.mode is A2CaptureMode.ORIGINAL_A38_PROJECTION
    assert full.manifest.a2_capture.mode is A2CaptureMode.FULL_BASELINE_CASE
    assert not projection.manifest.a2_capture.eligibility_captured
    assert full.manifest.a2_capture.assessment_id


def test_package_envelope_round_trip_preserves_semantic_and_exact_identity() -> None:
    package = package_for()
    rebuilt = load_package_json(package_json(package))
    assert rebuilt == package
    assert (
        rebuilt.manifest.package_semantic_fingerprint
        == package.manifest.package_semantic_fingerprint
    )
    assert rebuilt.manifest.exact_package_checksum == package.manifest.exact_package_checksum


def test_operational_variants_share_semantics_but_not_exact_checksums() -> None:
    serial, graph = operational_variant()
    assert serial.manifest.package_id == graph.manifest.package_id
    assert (
        serial.manifest.package_semantic_fingerprint == graph.manifest.package_semantic_fingerprint
    )
    assert serial.manifest.exact_package_checksum != graph.manifest.exact_package_checksum
    assert serial.manifest.a38_exact_checksum != graph.manifest.a38_exact_checksum


@pytest.mark.parametrize("mutation", ["content", "missing", "manifest_identity"])
def test_tampered_missing_or_reidentified_packages_fail_before_replay(mutation: str) -> None:
    package = package_for()
    if mutation == "content":
        first = package.blobs[0].model_copy(update={"content": package.blobs[0].content + " "})
        changed = package.model_copy(update={"blobs": (first, *package.blobs[1:])})
    elif mutation == "missing":
        changed = package.model_copy(update={"blobs": package.blobs[:-1]})
    else:
        manifest = package.manifest.model_copy(update={"subject": "ALTERED"})
        changed = package.model_copy(update={"manifest": manifest})
    with pytest.raises(PackageIntegrityError):
        validate_package(changed)


def test_synthetic_origin_requires_builder_and_live_cannot_claim_synthetic_source() -> None:
    package = package_for()
    fields = package.manifest.model_dump()
    with pytest.raises(ValidationError, match="fixture-builder"):
        package.manifest.__class__.model_validate(fields | {"fixture_builder_version": None})
    with pytest.raises(ValidationError, match="synthetic source"):
        package.manifest.__class__.model_validate(
            fields | {"origin": CaptureOrigin.LIVE, "source_reference": "synthetic:bad"}
        )


def test_content_addressed_store_is_idempotent_append_only_and_portable(
    tmp_path: Path,
) -> None:
    package = package_for()
    store = A3ReplayCorpusStore(tmp_path / "corpus")
    path = store.save_package(package)
    assert store.save_package(package) == path
    assert store.load_package(package.manifest.package_id) == package
    case = CorpusCase(
        case_id="A",
        package_id=package.manifest.package_id,
        origin=CaptureOrigin.SYNTHETIC,
        strata=("replay", "aligned"),
        fixture_builder_version=BUILDER,
        source_reference="synthetic:a3.9/aligned",
    )
    store.append_case(case)
    with pytest.raises(A3CorpusStoreError, match="already exists"):
        store.append_case(case)
    assert store.manifest(corpus_id="a3.10", created_at=NOW).cases == (case,)


def test_content_address_conflict_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "same"
    A3ReplayCorpusStore._write_idempotent(path, "one")
    with pytest.raises(A3CorpusStoreError, match="conflicts"):
        A3ReplayCorpusStore._write_idempotent(path, "two")


def test_corpus_manifest_is_fingerprinted_and_rejects_mutation() -> None:
    package = package_for()
    case = CorpusCase(
        case_id="A",
        package_id=package.manifest.package_id,
        origin=CaptureOrigin.SYNTHETIC,
        strata=("replay",),
        fixture_builder_version=BUILDER,
        source_reference="synthetic:a3.9/aligned",
    )
    manifest = corpus_manifest("a3.10", (case,), created_at=NOW)
    with pytest.raises(ValidationError, match="fingerprint"):
        manifest.__class__.model_validate(
            manifest.model_dump() | {"cases": [case.model_copy(update={"case_id": "B"})]}
        )
