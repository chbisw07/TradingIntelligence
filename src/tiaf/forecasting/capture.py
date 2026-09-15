"""Immutable capture closure and validation, with no I/O or forecast execution."""

import json
from datetime import datetime
from typing import Literal, Self

from pydantic import Field, StrictBool, model_validator

from tiaf.data.models import OHLCVBar
from tiaf.evaluation.forecast_contracts import EvidenceReference, ForecastWindow
from tiaf.evaluation.snapshot import validate_no_secrets
from tiaf.planner.models import Sha256

from .contracts import ForecastResult
from .enums import DataBasis
from .errors import ForecastIntegrityError, ForecastStoreError
from .evidence import validate_knowledge, validate_reference_bar, window_evidence
from .identity import (
    ArtifactReference,
    CapturedBlobReference,
    ForecastContract,
    ForecastDateTime,
    canonical_json,
    semantic_fingerprint,
)

MAX_RECORD_BYTES = 1_048_576
MAX_JOURNAL_RECORDS = 256
MAX_CORPUS_BYTES = 33_554_432
MAX_ARTIFACTS = 256


def strict_json(value: str) -> object:
    """Reject duplicate keys/nonfinite values; never execute encoded content."""

    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, item in items:
            if key in result:
                raise ValueError("DUPLICATE_JSON_KEY")
            result[key] = item
        return result

    def nonfinite(value: str) -> None:
        raise ValueError("NONFINITE_JSON")

    if len(value.encode("utf-8")) > MAX_RECORD_BYTES:
        raise ValueError("RECORD_TOO_LARGE")
    try:
        decoded: object = json.loads(value, object_pairs_hook=pairs, parse_constant=nonfinite)
        validate_no_secrets(decoded)
        canonical_json(decoded)
        return decoded
    except (ValueError, RecursionError) as exc:
        raise ValueError("INVALID_CAPTURE_JSON") from exc


def references(value: object) -> tuple[ArtifactReference, ...]:
    """Collect explicit native references, not URLs or incidental text."""
    if isinstance(value, ForecastContract):
        value = value.model_dump(mode="json")
    found: dict[tuple[str, str], ArtifactReference] = {}
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            if {"artifact_id", "artifact_version", "fingerprint"} <= item.keys():
                ref = ArtifactReference.model_validate(item)
                key = (ref.artifact_id, ref.artifact_version)
                if key in found and found[key] != ref:
                    raise ValueError("CONFLICTING_ARTIFACT_REFERENCE")
                found[key] = ref
            else:
                pending.extend(item.values())
        elif isinstance(item, (list, tuple)):
            pending.extend(item)
    return tuple(found[key] for key in sorted(found))


class CaptureRights(ForecastContract):
    policy: Literal["SYNTHETIC_FIXTURE_ONLY_V1"] = "SYNTHETIC_FIXTURE_ONLY_V1"
    retain: StrictBool = True
    replay: StrictBool = True
    read_until: ForecastDateTime | None = None


class CapturedArtifact(ForecastContract):
    schema_id: Literal["tiaf.ff.captured-artifact"] = "tiaf.ff.captured-artifact"
    reference: ArtifactReference
    content_json: str
    dependencies: tuple[ArtifactReference, ...] = ()
    rights: CaptureRights

    @model_validator(mode="after")
    def content_integrity(self) -> Self:
        payload = strict_json(self.content_json)
        if self.content_json != canonical_json(payload):
            raise ValueError("ARTIFACT_CONTENT_NOT_CANONICAL")
        if semantic_fingerprint(payload) != self.reference.fingerprint:
            raise ValueError("ARTIFACT_CONTENT_HASH_MISMATCH")
        if self.dependencies != references(payload):
            raise ValueError("ARTIFACT_DEPENDENCY_CLOSURE_MISMATCH")
        return self

    @property
    def blob_reference(self) -> CapturedBlobReference:
        return CapturedBlobReference(artifact=self.reference, blob_hash=semantic_fingerprint(self))


def capture_artifact(
    artifact_id: str,
    payload: object,
    *,
    artifact_version: str = "1.0",
    rights: CaptureRights | None = None,
) -> CapturedArtifact:
    encoded = canonical_json(payload)
    decoded = strict_json(encoded)
    return CapturedArtifact(
        reference=ArtifactReference(
            artifact_id=artifact_id,
            artifact_version=artifact_version,
            fingerprint=semantic_fingerprint(decoded),
        ),
        content_json=encoded,
        dependencies=references(decoded),
        rights=rights or CaptureRights(),
    )


class ForecastEvidenceSnapshot(ForecastContract):
    schema_id: Literal["tiaf.ff.evidence-snapshot"] = "tiaf.ff.evidence-snapshot"
    window: ForecastWindow
    history: tuple[OHLCVBar, ...] = Field(max_length=64)
    sources: tuple[EvidenceReference, ...]
    data_basis: Literal["SYNTHETIC_FIXTURE"] = "SYNTHETIC_FIXTURE"

    @model_validator(mode="after")
    def history_identity(self) -> Self:
        times = [bar.end_at for bar in self.history]
        if times != sorted(set(times)):
            raise ValueError("HISTORY_NOT_ORDERED_UNIQUE")
        for bar in self.history:
            if bar.instrument != self.window.reference.subject or bar.interval != "1d":
                raise ValueError("HISTORY_SCOPE_MISMATCH")
            if bar.end_at > self.window.reference.observed_at:
                raise ValueError("TARGET_OUTCOME_IN_FORECAST_INPUT")
        if self.window.reference.value is not None:
            matching = [
                bar for bar in self.history if bar.end_at == self.window.reference.observed_at
            ]
            if len(matching) != 1:
                raise ValueError("REFERENCE_BAR_MISSING")
            validate_reference_bar(self.window.reference, matching[0])
        return self


class ForecastCapture(ForecastContract):
    schema_id: Literal["tiaf.ff.capture"] = "tiaf.ff.capture"
    serializer_profile: Literal["tiaf.ff.canonical-json/1.0"] = "tiaf.ff.canonical-json/1.0"
    result: ForecastResult
    snapshot: ForecastEvidenceSnapshot
    build_ref: ArtifactReference
    dependency_versions_ref: ArtifactReference
    closure: tuple[CapturedBlobReference, ...] = Field(min_length=1, max_length=MAX_ARTIFACTS)
    recorded_at: ForecastDateTime
    capture_id: Sha256 | None = None

    @model_validator(mode="after")
    def capture_integrity(self) -> Self:
        result, request = self.result, self.result.request
        if self.snapshot.window != request.window or self.snapshot.sources != request.evidence:
            raise ValueError("CAPTURE_REQUEST_EVIDENCE_MISMATCH")
        if semantic_fingerprint(self.snapshot) != request.evidence_ref.fingerprint:
            raise ValueError("CAPTURE_SNAPSHOT_HASH_MISMATCH")
        completion = result.issued_at or result.computed_at or request.as_of
        if self.recorded_at < completion:
            raise ValueError("CAPTURE_RECORDING_PREDATES_RESULT")
        validate_knowledge(
            self.snapshot.sources,
            request.information_cutoff,
            request.realization_mode,
            request.knowledge_basis,
        )
        hashes = [ref.blob_hash for ref in self.closure]
        if hashes != sorted(set(hashes)):
            raise ValueError("CAPTURE_CLOSURE_NOT_CANONICAL_UNIQUE")
        expected = semantic_fingerprint(self.model_dump(mode="python", exclude={"capture_id"}))
        if self.capture_id is not None and self.capture_id != expected:
            raise ValueError("CAPTURE_HASH_MISMATCH")
        object.__setattr__(self, "capture_id", expected)
        return self

    @property
    def reference(self) -> ArtifactReference:
        assert self.capture_id is not None
        return ArtifactReference(
            artifact_id="ff-capture:" + self.capture_id,
            artifact_version="1.0",
            fingerprint=self.capture_id,
        )


def validate_closure(
    roots: tuple[ArtifactReference, ...],
    closure: tuple[CapturedBlobReference, ...],
    artifacts: tuple[CapturedArtifact, ...],
    *,
    as_of: datetime,
    retaining: bool = False,
) -> None:
    """Verify exact transitive bytes/rights; no source/model resolver participates."""
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("AS_OF_MUST_BE_AWARE")
    if len(artifacts) > MAX_ARTIFACTS:
        raise ForecastStoreError("ARTIFACT_LIMIT")
    by_ref: dict[ArtifactReference, CapturedArtifact] = {}
    by_id: dict[str, CapturedArtifact] = {}
    for artifact in artifacts:
        artifact = CapturedArtifact.model_validate(artifact)
        key = artifact.reference.artifact_id
        if key in by_id:
            raise ForecastIntegrityError("DUPLICATE_ARTIFACT_ID")
        by_ref[artifact.reference] = artifact
        by_id[key] = artifact
        rights = artifact.rights
        if not rights.replay or (retaining and not rights.retain):
            raise ForecastStoreError("ARTIFACT_RIGHTS_DENIED")
        if rights.read_until is not None and as_of > rights.read_until:
            raise ForecastStoreError("ARTIFACT_RIGHTS_EXPIRED")
    actual = tuple(sorted((a.blob_reference for a in artifacts), key=lambda r: r.blob_hash))
    if closure != actual:
        raise ForecastIntegrityError("BLOB_CLOSURE_MISMATCH")
    visited: set[ArtifactReference] = set()
    active: set[ArtifactReference] = set()

    def visit(ref: ArtifactReference) -> None:
        if ref in active:
            raise ForecastIntegrityError("ARTIFACT_REFERENCE_CYCLE")
        if ref in visited:
            return
        if ref not in by_ref:
            raise ForecastIntegrityError("ARTIFACT_REFERENCE_MISSING")
        active.add(ref)
        for dependency in by_ref[ref].dependencies:
            visit(dependency)
        active.remove(ref)
        visited.add(ref)

    for root in roots:
        visit(root)
    if visited != set(by_ref):
        raise ForecastIntegrityError("UNREFERENCED_ARTIFACT_IN_CLOSURE")


def capture_roots(capture: ForecastCapture) -> tuple[ArtifactReference, ...]:
    return references(
        {
            "result": capture.result.model_dump(mode="json"),
            "snapshot": capture.snapshot.model_dump(mode="json"),
            "build": capture.build_ref.model_dump(mode="json"),
            "versions": capture.dependency_versions_ref.model_dump(mode="json"),
        }
    )


def select_artifacts(
    roots: tuple[ArtifactReference, ...], artifacts: tuple[CapturedArtifact, ...]
) -> tuple[CapturedArtifact, ...]:
    """Select exact transitive pins from a bounded supplied shelf; never fetch anything."""
    if len(artifacts) > MAX_ARTIFACTS:
        raise ForecastStoreError("ARTIFACT_LIMIT")
    by_ref: dict[ArtifactReference, CapturedArtifact] = {}
    by_id: dict[str, CapturedArtifact] = {}
    for item in artifacts:
        item = CapturedArtifact.model_validate(item)
        old = by_id.get(item.reference.artifact_id)
        if old is not None and old != item:
            raise ForecastIntegrityError("CONFLICTING_ARTIFACT_REFERENCE")
        by_id[item.reference.artifact_id] = item
        by_ref[item.reference] = item
    selected: dict[ArtifactReference, CapturedArtifact] = {}
    active: set[ArtifactReference] = set()

    def visit(ref: ArtifactReference) -> None:
        if ref in active:
            raise ForecastIntegrityError("ARTIFACT_REFERENCE_CYCLE")
        if ref in selected:
            return
        if ref not in by_ref:
            raise ForecastIntegrityError("ARTIFACT_REFERENCE_MISSING")
        active.add(ref)
        for child in by_ref[ref].dependencies:
            visit(child)
        active.remove(ref)
        selected[ref] = by_ref[ref]

    for ref in roots:
        visit(ref)
    return tuple(sorted(selected.values(), key=lambda item: item.blob_reference.blob_hash))


def validate_capture(
    capture: ForecastCapture,
    artifacts: tuple[CapturedArtifact, ...],
    *,
    as_of: datetime,
    retaining: bool = False,
) -> ForecastCapture:
    capture = ForecastCapture.model_validate(capture)
    validate_closure(
        capture_roots(capture), capture.closure, artifacts, as_of=as_of, retaining=retaining
    )
    for source in (*window_evidence(capture.snapshot.window), *capture.snapshot.sources):
        if source.data_basis is not DataBasis.SYNTHETIC_FIXTURE:
            raise ForecastIntegrityError("NON_SYNTHETIC_CAPTURE")
    snapshot_blob = next(a for a in artifacts if a.reference == capture.result.request.evidence_ref)
    if snapshot_blob.content_json != canonical_json(capture.snapshot):
        raise ForecastIntegrityError("SNAPSHOT_BYTES_MISMATCH")
    return capture
