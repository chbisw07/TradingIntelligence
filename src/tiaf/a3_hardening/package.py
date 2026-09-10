"""Content-addressed A3 replay packages over accepted child captures."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.evaluation.store import load_case_json
from tiaf.planner.digests import digest, semantic
from tiaf.service.opportunity_intelligence import replay_intelligence
from tiaf.workflows.replay import replay_recorded

from .contracts import (
    A2CaptureDescriptor,
    A2CaptureMode,
    A2ProjectionCapture,
    A3ReplayPackageManifest,
    BlobKind,
    BlobReference,
    CaptureCompleteness,
    CapturedBlob,
    CaptureOrigin,
    CaptureStatus,
    PackageIntegrityError,
    PortableA3ReplayPackage,
)


def exact_bytes_checksum(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _blob(kind: BlobKind, schema_id: str, content: str) -> CapturedBlob:
    checksum = exact_bytes_checksum(content)
    return CapturedBlob(
        reference=BlobReference(
            kind=kind,
            schema_id=schema_id,
            content_schema_version="1.0",
            checksum=checksum,
            byte_length=len(content.encode("utf-8")),
            relative_path=f"blobs/sha256/{checksum}.json",
        ),
        content=content,
    )


def _semantic_payload(manifest: A3ReplayPackageManifest) -> dict[str, Any]:
    return manifest.model_dump(
        mode="json",
        exclude={
            "package_id": True,
            "package_semantic_fingerprint": True,
            "exact_package_checksum": True,
            "created_at": True,
            "a38_capture": True,
            "a39_capture": True,
            "a38_exact_checksum": True,
            "a39_exact_checksum": True,
            "a2_capture": {"blob"},
        },
    )


def _package_checksum(manifest: A3ReplayPackageManifest, blobs: tuple[CapturedBlob, ...]) -> str:
    manifest_payload = manifest.model_dump(mode="json", exclude={"exact_package_checksum"})
    blob_payload = tuple(
        (b.reference.kind.value, b.reference.checksum, b.content)
        for b in sorted(blobs, key=lambda b: b.reference.kind.value)
    )
    return digest({"manifest": manifest_payload, "blobs": blob_payload})


def capture_a3_package(
    a38_capture: str,
    a39_capture: str,
    a2_capture: str | None = None,
    *,
    origin: CaptureOrigin = CaptureOrigin.CAPTURED_UNKNOWN,
    source_reference: str = "caller-supplied-captured-records",
    fixture_builder_version: str | None = None,
    created_at: datetime | None = None,
) -> PortableA3ReplayPackage:
    """Compose completed records only; this function cannot acquire missing evidence."""
    try:
        a38 = replay_recorded(a38_capture)
        a39 = replay_intelligence(a39_capture)
        if a39.request.capture_json != a38_capture:
            raise ValueError("A3.9 does not embed the supplied exact A3.8 capture")
        if (
            a39.result.subject != a38.request.subject
            or a39.result.horizon != a38.request.horizon
            or a39.result.as_of != a38.request.as_of
            or a39.result.audit.semantic_fingerprint != a38.fingerprint
        ):
            raise ValueError("A3.8/A3.9 subject, horizon, as-of or fingerprint mismatch")

        a38_blob = _blob(BlobKind.A38_CAPTURE, "tiaf.a3.8.orchestration-capture", a38_capture)
        a39_blob = _blob(BlobKind.A39_CAPTURE, "tiaf.a3.9.intelligence-capture", a39_capture)
        if a2_capture is None:
            projection = A2ProjectionCapture(
                a2_pack=a38.request.inventory.a2_pack,
                baseline=a39.result.baseline,
            )
            a2_content = canonical_json(projection)
            a2_blob = _blob(BlobKind.A2_CAPTURE, "tiaf.a3.10.a2-original-projection", a2_content)
            a2_mode = A2CaptureMode.ORIGINAL_A38_PROJECTION
        else:
            baseline_case = load_case_json(a2_capture)
            if (
                baseline_case.snapshot.subject != a38.request.subject
                or baseline_case.snapshot.horizon != a38.request.horizon
                or baseline_case.snapshot.decision_time > a38.request.as_of
                or baseline_case.run_record.assessment.assessment_id != a38.result.a2_reference
                or baseline_case.snapshot.fingerprint != a38.result.a2_fingerprint
            ):
                raise ValueError("full A2 capture does not match the A3 source")
            a2_content = a2_capture
            a2_blob = _blob(BlobKind.A2_CAPTURE, "tiaf.a2.10.captured-baseline-case", a2_content)
            a2_mode = A2CaptureMode.FULL_BASELINE_CASE

        outer38, outer39 = json.loads(a38_capture), json.loads(a39_capture)
        model_outputs = tuple(
            sorted(o.opinion_id for o in a38.result.opinions if o.usage.llm_calls > 0)
        )
        nonreplayable = tuple(
            sorted(
                o.opinion_id
                for o in a38.result.opinions
                if o.usage.llm_calls > 0 and (o.model_identity is None or o.prompt_version is None)
            )
        )
        capture_status = (
            CaptureStatus.NON_REPLAYABLE
            if nonreplayable
            else CaptureStatus.PARTIAL_RECORDED_ONLY
            if model_outputs
            else CaptureStatus.COMPLETE
        )
        completeness_reasons = (
            tuple(f"INCOMPLETE_MODEL_PROVENANCE:{item}" for item in nonreplayable)
            if nonreplayable
            else tuple(f"MODEL_OUTPUT_RECORDED_ONLY:{item}" for item in model_outputs)
        )
        completeness = CaptureCompleteness(
            status=capture_status,
            required_kinds=(BlobKind.A2_CAPTURE, BlobKind.A38_CAPTURE, BlobKind.A39_CAPTURE),
            present_kinds=(BlobKind.A2_CAPTURE, BlobKind.A38_CAPTURE, BlobKind.A39_CAPTURE),
            reasons=completeness_reasons,
        )
        attempts = tuple(a for a in a38.attempts if a.record is not None)
        version_snapshots = (
            ("a3.8.record_schema", a38.schema_version),
            ("a3.8.planner", a38.plans[-1].planner_version),
            ("a3.8.policy", a38.plans[-1].policy_version),
            ("a3.9.record_schema", a39.schema_version),
            ("a3.9.policy", a39.result.policy_version),
        )
        provisional = A3ReplayPackageManifest.model_construct(
            package_id="pending",
            subject=a38.request.subject,
            instrument_type=a39.result.instrument_type,
            horizon=a38.request.horizon,
            as_of=a38.request.as_of,
            purpose=a38.request.purpose,
            a2_capture=A2CaptureDescriptor(
                mode=a2_mode,
                blob=a2_blob.reference,
                assessment_id=a38.result.a2_reference,
                evidence_fingerprint=a38.result.a2_fingerprint,
                eligibility_captured=a39.result.baseline.eligible is not None,
            ),
            a38_capture=a38_blob.reference,
            a39_capture=a39_blob.reference,
            version_snapshots=version_snapshots,
            plan_versions=tuple(p.version for p in a38.plans),
            registry_snapshots=tuple(
                sorted(
                    (s.capability.specialist.value, s.capability.specialist_version)
                    for s in a38.plans[-1].registry
                )
            ),
            admitted_evidence_ids=tuple(
                sorted({item for a in a38.attempts for item in a.consumed_ids})
            ),
            active_opinion_ids=tuple(sorted(o.opinion_id for o in a38.result.opinions)),
            superseded_opinion_ids=tuple(
                sorted(
                    a.record.opinion.opinion_id
                    for a in a38.attempts
                    if a.superseded and a.record and a.record.opinion
                )
            ),
            specialist_input_digests=tuple(
                sorted((a.record.record_id, a.input_digest) for a in attempts if a.record)
            ),
            specialist_output_fingerprints=tuple(
                sorted(
                    (a.record.opinion.opinion_id, digest(semantic(a.record.opinion)))
                    for a in attempts
                    if a.record and a.record.opinion
                )
            ),
            artifact_ids=tuple(sorted(a.artifact_id for a in a38.artifacts)),
            projection_digests=tuple(sorted(p.field_digest() for p in a38.projections)),
            reservation_ids=tuple(sorted(r.accounting_id for r in a38.reservations)),
            outcome_statuses=tuple(
                sorted((o.node_id, o.status.value) for o in a38.result.outcomes)
            ),
            stop_reasons=tuple(s.value for s in a38.result.stop_reasons),
            a2_evidence_fingerprint=a38.result.a2_fingerprint,
            a2_assessment_id=a38.result.a2_reference,
            a38_semantic_fingerprint=a38.fingerprint,
            a38_exact_checksum=outer38["checksum"],
            a39_semantic_fingerprint=a39.fingerprint,
            a39_exact_checksum=outer39["checksum"],
            completeness=completeness,
            origin=origin,
            source_reference=source_reference,
            fixture_builder_version=fixture_builder_version,
            package_semantic_fingerprint="0" * 64,
            exact_package_checksum="0" * 64,
            created_at=created_at or datetime.now(TIAF_TIMEZONE),
        )
        semantic_fingerprint = digest(_semantic_payload(provisional))
        package_id = f"a3-package:{semantic_fingerprint[:24]}"
        manifest = A3ReplayPackageManifest.model_validate(
            provisional.model_dump()
            | {
                "package_id": package_id,
                "package_semantic_fingerprint": semantic_fingerprint,
            }
        )
        blobs = (a2_blob, a38_blob, a39_blob)
        exact = _package_checksum(manifest, blobs)
        manifest = manifest.model_copy(update={"exact_package_checksum": exact})
        package = PortableA3ReplayPackage(manifest=manifest, blobs=blobs)
        return validate_package(package)
    except (ValueError, TypeError, KeyError, ValidationError) as exc:
        if isinstance(exc, PackageIntegrityError):
            raise
        raise PackageIntegrityError(str(exc)) from exc


def validate_package(package: PortableA3ReplayPackage) -> PortableA3ReplayPackage:
    """Validate exact bytes, semantic manifest and every accepted child link."""
    try:
        package = PortableA3ReplayPackage.model_validate_json(package.model_dump_json())
        manifest = package.manifest
        by_kind: dict[BlobKind, CapturedBlob] = {}
        for blob in package.blobs:
            ref = blob.reference
            if ref.kind in by_kind:
                raise ValueError(f"duplicate blob kind: {ref.kind}")
            if exact_bytes_checksum(blob.content) != ref.checksum:
                raise ValueError("blob exact-byte checksum mismatch")
            if len(blob.content.encode("utf-8")) != ref.byte_length:
                raise ValueError("blob byte length mismatch")
            by_kind[ref.kind] = blob
        expected_refs = {
            BlobKind.A2_CAPTURE: manifest.a2_capture.blob,
            BlobKind.A38_CAPTURE: manifest.a38_capture,
            BlobKind.A39_CAPTURE: manifest.a39_capture,
        }
        if set(by_kind) != set(expected_refs):
            raise ValueError("missing required package blob")
        if any(by_kind[k].reference != v for k, v in expected_refs.items()):
            raise ValueError("manifest/blob reference mismatch")
        if digest(_semantic_payload(manifest)) != manifest.package_semantic_fingerprint:
            raise ValueError("package semantic fingerprint mismatch")
        if manifest.package_id != f"a3-package:{manifest.package_semantic_fingerprint[:24]}":
            raise ValueError("package ID does not match semantic fingerprint")
        if (
            _package_checksum(
                manifest.model_copy(update={"exact_package_checksum": "0" * 64}), package.blobs
            )
            != manifest.exact_package_checksum
        ):
            raise ValueError("complete package checksum mismatch")

        a38_content = by_kind[BlobKind.A38_CAPTURE].content
        a39_content = by_kind[BlobKind.A39_CAPTURE].content
        a38 = replay_recorded(a38_content)
        a39 = replay_intelligence(a39_content)
        if a39.request.capture_json != a38_content:
            raise ValueError("broken embedded A3.8 reference")
        if (
            a38.fingerprint != manifest.a38_semantic_fingerprint
            or a39.fingerprint != manifest.a39_semantic_fingerprint
            or a38.result.a2_reference != manifest.a2_assessment_id
            or a38.result.a2_fingerprint != manifest.a2_evidence_fingerprint
            or (a38.request.subject, a38.request.horizon, a38.request.as_of)
            != (manifest.subject, manifest.horizon, manifest.as_of)
        ):
            raise ValueError("package child identity mismatch")
        a2_content = by_kind[BlobKind.A2_CAPTURE].content
        if manifest.a2_capture.mode is A2CaptureMode.FULL_BASELINE_CASE:
            case = load_case_json(a2_content)
            if (
                case.snapshot.fingerprint != manifest.a2_evidence_fingerprint
                or case.run_record.assessment.assessment_id != manifest.a2_assessment_id
            ):
                raise ValueError("full A2 capture identity mismatch")
        else:
            projection = A2ProjectionCapture.model_validate_json(a2_content)
            if (
                projection.baseline.evidence_fingerprint != manifest.a2_evidence_fingerprint
                or projection.baseline.assessment_id != manifest.a2_assessment_id
                or projection.a2_pack != a38.request.inventory.a2_pack
                or projection.baseline != a39.result.baseline
            ):
                raise ValueError("original A2 projection was mutated")
        return package
    except (ValueError, TypeError, KeyError, ValidationError) as exc:
        raise PackageIntegrityError(str(exc)) from exc


def package_json(package: PortableA3ReplayPackage, *, indent: int | None = None) -> str:
    package = validate_package(package)
    return json.dumps(
        package.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":") if indent is None else None,
        indent=indent,
        ensure_ascii=False,
    )


def load_package_json(content: str) -> PortableA3ReplayPackage:
    try:
        return validate_package(PortableA3ReplayPackage.model_validate_json(content))
    except (ValueError, TypeError, ValidationError) as exc:
        if isinstance(exc, PackageIntegrityError):
            raise
        raise PackageIntegrityError(str(exc)) from exc


def package_blob(package: PortableA3ReplayPackage, kind: BlobKind) -> CapturedBlob:
    return next(blob for blob in validate_package(package).blobs if blob.reference.kind is kind)


def resolve_blob_path(root: Path, reference: BlobReference) -> Path:
    """Resolve only the fixed content-addressed relative layout."""
    path = root / reference.relative_path
    if path.resolve().parent != (root / "blobs" / "sha256").resolve():
        raise PackageIntegrityError("blob path escapes content-addressed store")
    return path
