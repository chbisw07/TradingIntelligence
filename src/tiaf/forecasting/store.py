"""Bounded single-writer JSON/JSONL corpus; no database or cross-file transaction."""

import os
import re
import stat
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import TypeAdapter

from tiaf.data.models import OHLCVBar
from tiaf.evaluation.forecast_contracts import (
    EvaluationLink,
    ForecastLedgerSnapshot,
    OutcomeJournalEntry,
)
from tiaf.evaluation.forecast_linkage import link_forecast_outcome

from .capture import (
    MAX_CORPUS_BYTES,
    MAX_JOURNAL_RECORDS,
    MAX_RECORD_BYTES,
    CapturedArtifact,
    ForecastCapture,
    references,
    strict_json,
    validate_capture,
    validate_closure,
)
from .enums import QualificationStatus
from .errors import ForecastIntegrityError, ForecastStoreError
from .evidence import validate_reference_bar
from .identity import (
    ArtifactReference,
    CapturedBlobReference,
    ForecastContract,
    ForecastDateTime,
    LogicalId,
    canonical_json,
)


class StoreOwner(StrEnum):
    READ_ONLY = "READ_ONLY"
    FORECAST = "FORECAST"
    EVALUATION = "EVALUATION"


@dataclass
class _Index:
    artifacts: dict[str, CapturedArtifact] = field(default_factory=dict)
    forecasts: dict[str, ForecastCapture] = field(default_factory=dict)
    outcomes: dict[str, OutcomeJournalEntry] = field(default_factory=dict)
    links: dict[str, EvaluationLink] = field(default_factory=dict)
    ledgers: dict[str, ForecastLedgerSnapshot] = field(default_factory=dict)
    size: int = 0


Record = ForecastCapture | OutcomeJournalEntry | EvaluationLink | ForecastLedgerSnapshot
_HASH = re.compile(r"^[a-f0-9]{64}$")
_FILES = {"forecast_runs.jsonl", "outcome_records.jsonl", "evaluation_links.jsonl"}


def outcome_roots(entry: OutcomeJournalEntry) -> tuple[ArtifactReference, ...]:
    return references(
        entry.model_dump(mode="json", exclude={"closure", "fingerprint", "predecessor"})
    )


def _decoded[T: ForecastContract](kind: type[T], raw: bytes, required_hash: str | None = None) -> T:
    try:
        payload = strict_json(raw.decode("utf-8"))
        if required_hash is not None and (
            not isinstance(payload, dict) or not payload.get(required_hash)
        ):
            raise ValueError("MISSING_RECORDED_HASH")
        return kind.model_validate(payload)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ForecastIntegrityError("INVALID_RECORDED_ARTIFACT") from exc


@dataclass(frozen=True)
class ForecastCorpusStore:
    """Explicit trusted local ownership/read-as-of; construction performs no I/O.

    The caller supplies the actual access clock (injectable in synthetic tests).
    This is not R5 startup authority, a clock source or an execution runtime.
    """

    root: Path
    as_of: datetime
    owner: StoreOwner = StoreOwner.READ_ONLY

    def __post_init__(self) -> None:
        if not isinstance(self.root, Path) or not self.root.is_absolute():
            raise ForecastStoreError("EXPLICIT_ABSOLUTE_CORPUS_ROOT_REQUIRED")
        if self.root == Path("/") or ".." in self.root.parts:
            raise ForecastStoreError("UNSAFE_CORPUS_ROOT")
        if not isinstance(self.owner, StoreOwner):
            raise ForecastStoreError("TYPED_STORE_OWNER_REQUIRED")
        normalized = TypeAdapter(ForecastDateTime).validate_python(self.as_of)
        object.__setattr__(self, "as_of", normalized)

    def _safe(self, path: Path) -> None:
        if not path.is_relative_to(self.root):
            raise ForecastStoreError("CORPUS_PATH_ESCAPE")
        for part in (path, *path.parents):
            if part.is_symlink():
                raise ForecastStoreError("CORPUS_SYMLINK_DENIED")

    def _check_access_clock(self, record: Record) -> None:
        when = (
            record.recorded_at
            if isinstance(record, (ForecastCapture, OutcomeJournalEntry))
            else record.created_at
        )
        if when > self.as_of:
            raise ForecastIntegrityError("RECORD_POSTDATES_ACCESS_CLOCK")

    def _read(self, path: Path, *, journal: bool = False) -> bytes:
        self._safe(path)
        limit = MAX_CORPUS_BYTES if journal else MAX_RECORD_BYTES
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, "rb") as handle:
                info = os.fstat(handle.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise ForecastStoreError("CORPUS_REQUIRES_UNLINKED_REGULAR_FILES")
                if info.st_size > limit:
                    raise ForecastStoreError("RECORD_SIZE_LIMIT")
                data = handle.read(limit + 1)
            if len(data) > limit:
                raise ForecastStoreError("RECORD_SIZE_LIMIT")
            return data
        except OSError as exc:
            raise ForecastStoreError("CORPUS_READ_FAILED") from exc

    def _lines(self, name: str) -> tuple[bytes, ...]:
        path = self.root / name
        self._safe(path)
        if not path.exists():
            return ()
        content = self._read(path, journal=True)
        if content and not content.endswith(b"\n"):
            raise ForecastIntegrityError("PARTIAL_JOURNAL_LINE")
        lines = tuple(content.splitlines())
        if len(lines) > MAX_JOURNAL_RECORDS:
            raise ForecastStoreError("JOURNAL_RECORD_LIMIT")
        if any(not line.strip() or len(line) > MAX_RECORD_BYTES for line in lines):
            raise ForecastIntegrityError("INVALID_JOURNAL_LINE")
        return lines

    def _blobs(
        self, refs: tuple[CapturedBlobReference, ...], index: _Index
    ) -> tuple[CapturedArtifact, ...]:
        try:
            return tuple(index.artifacts[ref.blob_hash] for ref in refs)
        except KeyError as exc:
            raise ForecastIntegrityError("MISSING_CAPTURE_CLOSURE") from exc

    def _check_outcome(self, entry: OutcomeJournalEntry, index: _Index, *, now: datetime) -> None:
        blobs = self._blobs(entry.closure, index)
        validate_closure(outcome_roots(entry), entry.closure, blobs, as_of=now)
        by_ref = {blob.reference: blob for blob in blobs}
        for close in (entry.window.reference, entry.terminal):
            if close is not None and close.qualification is QualificationStatus.QUALIFIED:
                try:
                    bar = OHLCVBar.model_validate(strict_json(by_ref[close.bar_ref].content_json))
                    validate_reference_bar(close, bar)
                except ValueError as exc:
                    raise ForecastIntegrityError("OUTCOME_CAPTURED_BAR_MISMATCH") from exc

    def _add_outcome(self, entry: OutcomeJournalEntry, index: _Index) -> None:
        self._check_access_clock(entry)
        if entry.entry_id in index.outcomes:
            raise ForecastIntegrityError("DUPLICATE_OUTCOME_ID")
        chain = [old for old in index.outcomes.values() if old.key == entry.key]
        if entry.revision != len(chain):
            raise ForecastIntegrityError("OUTCOME_REVISION_GAP_OR_FORK")
        if chain:
            previous = chain[-1]
            if entry.predecessor != previous.reference:
                raise ForecastIntegrityError("OUTCOME_PREDECESSOR_MISMATCH")
            if entry.recorded_at < previous.recorded_at or (
                entry.qualification_available_at < previous.qualification_available_at
            ):
                raise ForecastIntegrityError("OUTCOME_REVISION_BACKDATED")
        self._check_outcome(entry, index, now=entry.recorded_at)
        index.outcomes[entry.entry_id] = entry

    @staticmethod
    def _check_link(link: EvaluationLink, index: _Index) -> None:
        capture = index.forecasts.get(link.run_id)
        outcome = index.outcomes.get(link.outcome_ref.artifact_id)
        if capture is None or outcome is None:
            raise ForecastIntegrityError("LINK_RECORD_MISSING")
        if link != link_forecast_outcome(capture, outcome, created_at=link.created_at):
            raise ForecastIntegrityError("LINK_IDENTITY_OR_ELIGIBILITY_MISMATCH")

    @staticmethod
    def _check_ledger(ledger: ForecastLedgerSnapshot, index: _Index) -> None:
        if any(index.links.get(link.link_id or "") != link for link in ledger.links):
            raise ForecastIntegrityError("LEDGER_LINK_MISMATCH")
        if ledger.predecessor is not None:
            previous = index.ledgers.get(ledger.predecessor.fingerprint)
            if previous is None or ledger.predecessor != previous.reference:
                raise ForecastIntegrityError("LEDGER_PREDECESSOR_MISSING")
            if previous.created_at > ledger.created_at:
                raise ForecastIntegrityError("LEDGER_BACKDATED")

    def _load(self, *, locked: bool = False) -> _Index:
        self._safe(self.root)
        if not self.root.exists():
            raise ForecastStoreError("CORPUS_NOT_FOUND")
        lock = self.root / ".writer.lock"
        self._safe(lock)
        if lock.exists() and not locked:
            raise ForecastStoreError("CORPUS_WRITER_ACTIVE_OR_STALE")
        index = _Index()
        try:
            for path in self.root.iterdir():
                self._safe(path)
                if path.name not in _FILES | {"artifacts", "ledger_snapshots", ".writer.lock"}:
                    raise ForecastIntegrityError("UNKNOWN_CORPUS_ENTRY")
                if path.name in {"artifacts", "ledger_snapshots"}:
                    if not path.is_dir():
                        raise ForecastIntegrityError("INVALID_CORPUS_DIRECTORY")
                    for child in path.iterdir():
                        self._safe(child)
                        if child.suffix != ".json" or not _HASH.fullmatch(child.stem):
                            raise ForecastIntegrityError("INVALID_ARTIFACT_FILENAME")
                        index.size += child.stat().st_size
                else:
                    index.size += path.stat().st_size
            if index.size > MAX_CORPUS_BYTES:
                raise ForecastStoreError("CORPUS_SIZE_LIMIT")
            directory = self.root / "artifacts"
            by_id: dict[str, str] = {}
            for path in sorted(directory.glob("*.json")):
                artifact = _decoded(CapturedArtifact, self._read(path))
                if artifact.blob_reference.blob_hash != path.stem:
                    raise ForecastIntegrityError("BLOB_FILENAME_HASH_MISMATCH")
                key = artifact.reference.artifact_id
                if key in by_id and by_id[key] != path.stem:
                    raise ForecastIntegrityError("CONFLICTING_ARTIFACT_ID")
                by_id[key] = path.stem
                index.artifacts[path.stem] = artifact
            result_ids: set[str] = set()
            for raw in self._lines("forecast_runs.jsonl"):
                capture = _decoded(ForecastCapture, raw, "capture_id")
                self._check_access_clock(capture)
                run = capture.result.run_id
                if run in index.forecasts or capture.result.result_id in result_ids:
                    raise ForecastIntegrityError("DUPLICATE_FORECAST_ID")
                validate_capture(
                    capture, self._blobs(capture.closure, index), as_of=capture.recorded_at
                )
                index.forecasts[run] = capture
                result_ids.add(capture.result.result_id)
            for raw in self._lines("outcome_records.jsonl"):
                self._add_outcome(_decoded(OutcomeJournalEntry, raw, "fingerprint"), index)
            for raw in self._lines("evaluation_links.jsonl"):
                link = _decoded(EvaluationLink, raw, "link_id")
                self._check_access_clock(link)
                assert link.link_id is not None
                if link.link_id in index.links:
                    raise ForecastIntegrityError("DUPLICATE_LINK_ID")
                self._check_link(link, index)
                index.links[link.link_id] = link
            directory = self.root / "ledger_snapshots"
            for path in sorted(directory.glob("*.json")):
                ledger = _decoded(ForecastLedgerSnapshot, self._read(path), "snapshot_id")
                self._check_access_clock(ledger)
                if ledger.snapshot_id != path.stem:
                    raise ForecastIntegrityError("LEDGER_FILENAME_HASH_MISMATCH")
                index.ledgers[path.stem] = ledger
            for ledger in index.ledgers.values():
                self._check_ledger(ledger, index)
            return index
        except OSError as exc:
            raise ForecastStoreError("CORPUS_READ_FAILED") from exc

    @contextmanager
    def _writer(self, owner: StoreOwner) -> Iterator[None]:
        if self.owner is not owner:
            raise ForecastStoreError("STORE_WRITE_OWNER_DENIED")
        self._safe(self.root)
        lock = self.root / ".writer.lock"
        self._safe(lock)
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        except FileExistsError as exc:
            raise ForecastStoreError("CORPUS_WRITER_ACTIVE_OR_STALE") from exc
        except OSError as exc:
            raise ForecastStoreError("CORPUS_WRITE_FAILED") from exc
        owned = os.fstat(fd)
        os.close(fd)
        try:
            yield
        finally:
            try:
                current = lock.lstat()
                if (current.st_dev, current.st_ino) != (owned.st_dev, owned.st_ino):
                    raise ForecastStoreError("WRITER_LOCK_REPLACED")
                lock.unlink()  # Only this invocation's exclusively created lock, never stale locks.
            except OSError as exc:
                raise ForecastStoreError("WRITER_LOCK_RELEASE_FAILED") from exc

    def _write(self, path: Path, content: bytes, *, append: bool) -> None:
        self._safe(path)
        flags = os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW
        flags |= os.O_APPEND if append else os.O_EXCL
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(path, flags, 0o600)
            try:
                info = os.fstat(fd)
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise ForecastStoreError("CORPUS_REQUIRES_UNLINKED_REGULAR_FILES")
                if os.write(fd, content) != len(content):
                    raise ForecastStoreError("PARTIAL_WRITE_NO_COMMIT_CLAIM")
                os.fsync(fd)
            finally:
                os.close(fd)
        except OSError as exc:
            raise ForecastStoreError("CORPUS_WRITE_FAILED_NO_COMMIT_CLAIM") from exc

    def _commit(
        self,
        path: Path,
        record: Record,
        artifacts: tuple[CapturedArtifact, ...],
        index: _Index,
        *,
        append: bool,
    ) -> None:
        additions: list[tuple[Path, bytes]] = []
        by_id = {a.reference.artifact_id: a for a in index.artifacts.values()}
        for artifact in artifacts:
            old = by_id.get(artifact.reference.artifact_id)
            if old is not None and old != artifact:
                raise ForecastIntegrityError("ARTIFACT_ID_CONFLICT")
            digest = artifact.blob_reference.blob_hash
            if digest not in index.artifacts:
                additions.append(
                    (
                        self.root / "artifacts" / f"{digest}.json",
                        (canonical_json(artifact) + "\n").encode("utf-8"),
                    )
                )
        encoded = (canonical_json(record) + "\n").encode("utf-8")
        if (
            any(len(data) > MAX_RECORD_BYTES for _, data in additions)
            or len(encoded) > MAX_RECORD_BYTES
        ):
            raise ForecastStoreError("RECORD_SIZE_LIMIT")
        if index.size + sum(len(data) for _, data in additions) + len(encoded) > MAX_CORPUS_BYTES:
            raise ForecastStoreError("CORPUS_SIZE_LIMIT")
        if append and len(self._lines(path.name)) >= MAX_JOURNAL_RECORDS:
            raise ForecastStoreError("JOURNAL_RECORD_LIMIT")
        for destination, data in additions:
            self._write(destination, data, append=False)
        # Single complete line is the logical commit. Earlier orphan blobs are not a run.
        self._write(path, encoded, append=append)

    def append_forecast(
        self, capture: ForecastCapture, artifacts: tuple[CapturedArtifact, ...]
    ) -> bool:
        capture = validate_capture(capture, artifacts, as_of=self.as_of, retaining=True)
        self._check_access_clock(capture)
        with self._writer(StoreOwner.FORECAST):
            index = self._load(locked=True)
            old = index.forecasts.get(capture.result.run_id)
            if old is not None:
                if old != capture:
                    raise ForecastIntegrityError("FORECAST_RUN_ID_CONFLICT")
                return False
            if any(
                c.result.result_id == capture.result.result_id for c in index.forecasts.values()
            ):
                raise ForecastIntegrityError("FORECAST_RESULT_ID_CONFLICT")
            self._commit(self.root / "forecast_runs.jsonl", capture, artifacts, index, append=True)
            return True

    def append_outcome(
        self, entry: OutcomeJournalEntry, artifacts: tuple[CapturedArtifact, ...]
    ) -> bool:
        entry = OutcomeJournalEntry.model_validate(entry)
        self._check_access_clock(entry)
        validate_closure(
            outcome_roots(entry), entry.closure, artifacts, as_of=self.as_of, retaining=True
        )
        with self._writer(StoreOwner.EVALUATION):
            index = self._load(locked=True)
            old = index.outcomes.get(entry.entry_id)
            if old is not None:
                if old != entry:
                    raise ForecastIntegrityError("OUTCOME_ENTRY_ID_CONFLICT")
                return False
            validation_index = _Index(
                artifacts={**index.artifacts, **{a.blob_reference.blob_hash: a for a in artifacts}},
                outcomes=dict(index.outcomes),
            )
            self._add_outcome(entry, validation_index)
            self._commit(self.root / "outcome_records.jsonl", entry, artifacts, index, append=True)
            return True

    def append_link(self, link: EvaluationLink) -> bool:
        link = EvaluationLink.model_validate(link)
        self._check_access_clock(link)
        assert link.link_id is not None
        with self._writer(StoreOwner.EVALUATION):
            index = self._load(locked=True)
            self._check_link(link, index)
            self._check_link_rights(link, index)
            if link.link_id in index.links:
                return False
            self._commit(self.root / "evaluation_links.jsonl", link, (), index, append=True)
            return True

    def append_ledger(self, ledger: ForecastLedgerSnapshot) -> bool:
        ledger = ForecastLedgerSnapshot.model_validate(ledger)
        self._check_access_clock(ledger)
        assert ledger.snapshot_id is not None
        with self._writer(StoreOwner.EVALUATION):
            index = self._load(locked=True)
            self._check_ledger(ledger, index)
            for link in ledger.links:
                self._check_link_rights(link, index)
            if ledger.snapshot_id in index.ledgers:
                return False
            self._commit(
                self.root / "ledger_snapshots" / f"{ledger.snapshot_id}.json",
                ledger,
                (),
                index,
                append=False,
            )
            return True

    def _check_link_rights(self, link: EvaluationLink, index: _Index) -> None:
        capture = index.forecasts[link.run_id]
        validate_capture(capture, self._blobs(capture.closure, index), as_of=self.as_of)
        self._check_outcome(index.outcomes[link.outcome_ref.artifact_id], index, now=self.as_of)

    def get_forecast(self, run_id: str) -> ForecastCapture:
        TypeAdapter(LogicalId).validate_python(run_id)
        index = self._load()
        if run_id not in index.forecasts:
            raise ForecastIntegrityError("FORECAST_NOT_FOUND")
        capture = index.forecasts[run_id]
        return validate_capture(capture, self._blobs(capture.closure, index), as_of=self.as_of)

    def get_outcome(self, entry_id: str) -> OutcomeJournalEntry:
        TypeAdapter(LogicalId).validate_python(entry_id)
        index = self._load()
        if entry_id not in index.outcomes:
            raise ForecastIntegrityError("OUTCOME_NOT_FOUND")
        entry = index.outcomes[entry_id]
        self._check_outcome(entry, index, now=self.as_of)
        return entry

    def get_link(self, link_id: str) -> EvaluationLink:
        index = self._load()
        if link_id not in index.links:
            raise ForecastIntegrityError("LINK_NOT_FOUND")
        link = index.links[link_id]
        self._check_link_rights(link, index)
        return link

    def get_ledger(self, snapshot_id: str) -> ForecastLedgerSnapshot:
        index = self._load()
        if snapshot_id not in index.ledgers:
            raise ForecastIntegrityError("LEDGER_NOT_FOUND")
        snapshot = index.ledgers[snapshot_id]
        for link in snapshot.links:
            self._check_link_rights(link, index)
        return snapshot
