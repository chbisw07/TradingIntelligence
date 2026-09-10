"""Small append-only filesystem store for content-addressed A3 packages."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .contracts import (
    A3ClosureReadinessRecord,
    A3CorpusManifest,
    A3HardeningError,
    A3HardeningResult,
    A3ReplayPackageManifest,
    CapturedBlob,
    CorpusCase,
    PortableA3ReplayPackage,
)
from .package import load_package_json, package_json, resolve_blob_path, validate_package


class A3CorpusStoreError(A3HardeningError):
    """Append-only corpus storage violation."""


class A3ReplayCorpusStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.package_root = root / "packages"
        self.corpus_log = root / "corpus_records.jsonl"
        self.evaluation_log = root / "evaluation_records.jsonl"
        self.closure_log = root / "closure_records.jsonl"

    @staticmethod
    def _write_idempotent(path: Path, content: str) -> None:
        if path.exists():
            if path.read_text(encoding="utf-8") != content:
                raise A3CorpusStoreError(f"content-addressed path conflicts: {path}")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def save_package(self, package: PortableA3ReplayPackage) -> Path:
        package = validate_package(package)
        for blob in package.blobs:
            path = resolve_blob_path(self.root, blob.reference)
            self._write_idempotent(path, blob.content)
        path = self.package_root / package.manifest.package_id / "manifest.json"
        manifest_json = (
            json.dumps(
                package.manifest.model_dump(mode="json"),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
            + "\n"
        )
        self._write_idempotent(path, manifest_json)
        return path

    def load_package(self, package_id: str) -> PortableA3ReplayPackage:
        path = self.package_root / package_id / "manifest.json"
        if not path.is_file():
            raise A3CorpusStoreError(f"package does not exist: {package_id}")
        try:
            manifest = A3ReplayPackageManifest.model_validate_json(path.read_text(encoding="utf-8"))
            blobs = tuple(
                CapturedBlob(
                    reference=ref,
                    content=resolve_blob_path(self.root, ref).read_text(encoding="utf-8"),
                )
                for ref in (
                    manifest.a2_capture.blob,
                    manifest.a38_capture,
                    manifest.a39_capture,
                )
            )
            return load_package_json(
                package_json(PortableA3ReplayPackage(manifest=manifest, blobs=blobs))
            )
        except (OSError, ValueError, ValidationError) as exc:
            raise A3CorpusStoreError(str(exc)) from exc

    @staticmethod
    def _append_unique(path: Path, identifier: str, payload: dict[str, Any]) -> None:
        existing: set[str] = set()
        if path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line:
                    row = json.loads(line)
                    existing.update(
                        str(row[k])
                        for k in (
                            "case_id",
                            "evaluation_id",
                            "closure_record_id",
                        )
                        if k in row
                    )
        if identifier in existing:
            raise A3CorpusStoreError(f"append-only record already exists: {identifier}")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")))
            handle.write("\n")

    def append_case(self, case: CorpusCase) -> None:
        if not (self.package_root / case.package_id / "manifest.json").is_file():
            raise A3CorpusStoreError("corpus case references an absent package")
        self._append_unique(self.corpus_log, case.case_id, case.model_dump(mode="json"))

    def append_evaluation(self, result: A3HardeningResult) -> None:
        self._append_unique(
            self.evaluation_log, result.evaluation_id, result.model_dump(mode="json")
        )

    def append_closure(self, record: A3ClosureReadinessRecord) -> None:
        self._append_unique(
            self.closure_log, record.closure_record_id, record.model_dump(mode="json")
        )

    def manifest(self, *, corpus_id: str, created_at: datetime) -> A3CorpusManifest:
        cases: tuple[CorpusCase, ...] = ()
        if self.corpus_log.is_file():
            cases = tuple(
                CorpusCase.model_validate_json(line)
                for line in self.corpus_log.read_text(encoding="utf-8").splitlines()
                if line
            )
        from .evaluation import corpus_manifest

        return corpus_manifest(corpus_id, cases, created_at=created_at)
