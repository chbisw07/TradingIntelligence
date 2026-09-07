"""Small filesystem JSON/JSONL replay corpus with append-only decision logs."""

import json
from pathlib import Path

from pydantic import ValidationError

from .errors import CorpusError
from .models import BaselineOutcome, BaselineRunRecord, CapturedBaselineCase, EvidenceSnapshot
from .snapshot import load_snapshot_json, snapshot_json, validate_no_secrets


def case_json(case: CapturedBaselineCase, *, indent: int | None = 2) -> str:
    """Serialize an evidence/decision envelope deterministically."""
    payload = case.model_dump(mode="json")
    validate_no_secrets(payload)
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":") if indent is None else None,
        indent=indent,
        ensure_ascii=False,
    )


def load_case_json(value: str) -> CapturedBaselineCase:
    """Load a captured case and validate snapshot integrity and links."""
    try:
        payload = json.loads(value)
        validate_no_secrets(payload)
        return CapturedBaselineCase.model_validate(payload)
    except (ValueError, TypeError, ValidationError) as exc:
        raise CorpusError(str(exc)) from exc


def save_case(path: Path, case: CapturedBaselineCase, *, overwrite: bool = False) -> None:
    """Write one portable capture, refusing replacement unless explicitly requested."""
    if path.exists() and not overwrite:
        raise CorpusError(f"capture already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(case_json(case) + "\n", encoding="utf-8")


def load_case(path: Path) -> CapturedBaselineCase:
    """Load one portable capture with clear missing-file behavior."""
    if not path.is_file():
        raise CorpusError(f"capture does not exist: {path}")
    return load_case_json(path.read_text(encoding="utf-8"))


class ReplayCorpusStore:
    """Filesystem-friendly snapshots plus append-only decision/outcome JSONL logs."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.snapshot_directory = root / "snapshots"
        self.decision_log = root / "decision_records.jsonl"
        self.outcome_log = root / "outcome_records.jsonl"

    def initialize(self) -> None:
        """Create only the small explicit corpus directory structure."""
        self.snapshot_directory.mkdir(parents=True, exist_ok=True)

    def save_snapshot(self, snapshot: EvidenceSnapshot) -> Path:
        """Persist content-addressed evidence; identical repeats are idempotent."""
        self.initialize()
        path = self.snapshot_directory / f"{snapshot.snapshot_id}.json"
        serialized = snapshot_json(snapshot) + "\n"
        if path.exists():
            if path.read_text(encoding="utf-8") != serialized:
                raise CorpusError("existing snapshot path has different content")
            return path
        path.write_text(serialized, encoding="utf-8")
        return path

    def load_snapshot(self, snapshot_id: str) -> EvidenceSnapshot:
        """Load a named content-addressed snapshot."""
        path = self.snapshot_directory / f"{snapshot_id}.json"
        if not path.is_file():
            raise CorpusError(f"snapshot does not exist: {snapshot_id}")
        return load_snapshot_json(path.read_text(encoding="utf-8"))

    @staticmethod
    def _append_unique(path: Path, identifier: str, payload: dict[str, object]) -> None:
        existing_ids: set[str] = set()
        if path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    decoded = json.loads(line)
                    for key in ("run_id", "baseline_outcome_id"):
                        if key in decoded:
                            existing_ids.add(str(decoded[key]))
        if identifier in existing_ids:
            raise CorpusError(f"append-only record already exists: {identifier}")
        path.parent.mkdir(parents=True, exist_ok=True)
        validate_no_secrets(payload)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")))
            handle.write("\n")

    def append_run(self, run: BaselineRunRecord) -> None:
        """Append a decision row; never update or replace an earlier row."""
        self._append_unique(self.decision_log, run.run_id, run.model_dump(mode="json"))

    def append_outcome(self, outcome: BaselineOutcome) -> None:
        """Append an outcome row referencing an immutable decision row."""
        self._append_unique(
            self.outcome_log,
            outcome.baseline_outcome_id,
            outcome.model_dump(mode="json"),
        )

    def runs(self) -> tuple[BaselineRunRecord, ...]:
        """Enumerate decision rows in append order with full validation."""
        if not self.decision_log.is_file():
            return ()
        try:
            return tuple(
                BaselineRunRecord.model_validate_json(line)
                for line in self.decision_log.read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        except (ValueError, ValidationError) as exc:
            raise CorpusError(f"invalid decision log: {exc}") from exc

    def cases(self) -> tuple[CapturedBaselineCase, ...]:
        """Associate every decision row with its immutable snapshot."""
        runs = self.runs()
        if not runs:
            raise CorpusError("replay corpus contains no decision records")
        return tuple(
            CapturedBaselineCase(
                snapshot=self.load_snapshot(run.evidence_snapshot_id),
                run_record=run,
            )
            for run in runs
        )
