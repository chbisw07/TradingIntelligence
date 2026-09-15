"""FF0-17/18/23/25: append safety, closure, rights and recorded reconstruction."""

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from tiaf.evaluation.forecast_contracts import ForecastLedgerSnapshot
from tiaf.evaluation.forecast_linkage import link_forecast_outcome
from tiaf.forecasting.capture import (
    CapturedArtifact,
    ForecastCapture,
    strict_json,
    validate_capture,
)
from tiaf.forecasting.errors import ForecastIntegrityError, ForecastStoreError
from tiaf.forecasting.identity import canonical_json
from tiaf.forecasting.replay import verify_replay
from tiaf.forecasting.store import ForecastCorpusStore, StoreOwner

from ._capture_support import closure, outcome_packet, packet
from ._support import instant


def inventory(root: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()
    }


def writer(root: Path, *, evaluation: bool = False) -> ForecastCorpusStore:
    return ForecastCorpusStore(
        root, as_of=instant(10), owner=StoreOwner.EVALUATION if evaluation else StoreOwner.FORECAST
    )


def test_append_idempotence_modes_and_multiple_simulations(tmp_path: Path) -> None:
    store = writer(tmp_path)
    specimens = [packet(), packet(simulated=True), packet(simulated=True, number=2)]
    for capture, blobs in specimens:
        assert store.append_forecast(capture, blobs) is True
        before = inventory(tmp_path)
        assert store.append_forecast(capture, blobs) is False
        assert inventory(tmp_path) == before
        assert store.get_forecast(capture.result.run_id) == capture
    assert len((tmp_path / "forecast_runs.jsonl").read_text().splitlines()) == 3
    assert len({c.result.observation_id for c, _ in specimens}) == 1
    assert len({c.capture_id for c, _ in specimens}) == 3
    assert not (tmp_path / "outcome_records.jsonl").exists()


@pytest.mark.parametrize("field", ["recorded_at", "result_id", "probability"])
def test_conflicting_run_rejects_before_any_new_bytes(tmp_path: Path, field: str) -> None:
    capture, blobs = packet()
    store = writer(tmp_path)
    store.append_forecast(capture, blobs)
    data = capture.model_dump(mode="json", exclude={"capture_id"})
    data["result"].pop("replay_fingerprint")
    if field == "recorded_at":
        data["recorded_at"] = instant(4, 16, 9)
    elif field == "probability":
        data["result"]["output"]["probability"] = 0.4
    else:
        data["result"]["result_id"] = "result:other"
    changed = ForecastCapture.model_validate(data)
    before = inventory(tmp_path)
    with pytest.raises(ForecastIntegrityError, match="CONFLICT"):
        store.append_forecast(changed, blobs)
    assert inventory(tmp_path) == before


def test_existing_result_identity_cannot_be_reused_under_new_run(tmp_path: Path) -> None:
    capture, blobs = packet()
    store = writer(tmp_path)
    store.append_forecast(capture, blobs)
    data = capture.model_dump(mode="json", exclude={"capture_id"})
    data["result"].pop("replay_fingerprint")
    data["result"]["run_id"] = "run:different"
    with pytest.raises(ForecastIntegrityError, match="RESULT_ID_CONFLICT"):
        store.append_forecast(ForecastCapture.model_validate(data), blobs)


def test_outcome_and_link_writes_are_independent_of_forecasts(tmp_path: Path) -> None:
    capture, blobs = packet()
    outcome, outcome_blobs = outcome_packet(capture, blobs)
    evaluation = writer(tmp_path, evaluation=True)
    assert evaluation.append_outcome(outcome, outcome_blobs)
    assert not (tmp_path / "forecast_runs.jsonl").exists()
    assert evaluation.get_outcome(outcome.entry_id) == outcome
    assert not evaluation.append_outcome(outcome, outcome_blobs)
    with pytest.raises(ForecastStoreError, match="OWNER_DENIED"):
        evaluation.append_forecast(capture, blobs)
    forecasting = writer(tmp_path)
    with pytest.raises(ForecastStoreError, match="OWNER_DENIED"):
        forecasting.append_outcome(outcome, outcome_blobs)
    forecasting.append_forecast(capture, blobs)
    link = link_forecast_outcome(capture, outcome, created_at=instant(9))
    assert evaluation.append_link(link)
    assert not evaluation.append_link(link)
    ledger = ForecastLedgerSnapshot(links=(link,), created_at=instant(9, 17))
    assert evaluation.append_ledger(ledger)
    assert not evaluation.append_ledger(ledger)
    assert evaluation.get_link(link.link_id or "") == link
    assert evaluation.get_ledger(ledger.snapshot_id or "") == ledger


def test_readonly_default_does_not_initialize_or_write(tmp_path: Path) -> None:
    root = tmp_path / "absent"
    store = ForecastCorpusStore(root, as_of=instant(10))
    assert not root.exists()
    with pytest.raises(ForecastStoreError, match="NOT_FOUND"):
        store.get_forecast("run:missing")
    capture, blobs = packet()
    with pytest.raises(ForecastStoreError, match="OWNER_DENIED"):
        store.append_forecast(capture, blobs)
    assert not root.exists()


@pytest.mark.parametrize("kind", ["capture", "outcome", "link", "ledger"])
def test_records_cannot_postdate_trusted_access_clock(tmp_path: Path, kind: str) -> None:
    capture, blobs = packet()
    outcome, outcome_blobs = outcome_packet(capture, blobs)
    link = link_forecast_outcome(capture, outcome, created_at=instant(9))
    ledger = ForecastLedgerSnapshot(links=(link,), created_at=instant(9, 17))
    store = ForecastCorpusStore(
        tmp_path / "future",
        as_of=instant(3),
        owner=StoreOwner.FORECAST if kind == "capture" else StoreOwner.EVALUATION,
    )
    with pytest.raises(ForecastIntegrityError, match="POSTDATES_ACCESS_CLOCK"):
        if kind == "capture":
            store.append_forecast(capture, blobs)
        elif kind == "outcome":
            store.append_outcome(outcome, outcome_blobs)
        elif kind == "link":
            store.append_link(link)
        else:
            store.append_ledger(ledger)
    assert not store.root.exists()


def test_capture_truth_and_ledger_contract_roundtrip_and_collection_immutability() -> None:
    capture, blobs = packet()
    outcome, _ = outcome_packet(capture, blobs)
    link = link_forecast_outcome(capture, outcome, created_at=instant(9))
    ledger = ForecastLedgerSnapshot(links=(link,), created_at=instant(9, 17))
    for model, field in (
        (capture, "closure"),
        (capture.snapshot, "history"),
        (blobs[0], "dependencies"),
        (outcome, "check_evidence"),
        (link, "reasons"),
        (ledger, "links"),
    ):
        payload = model.model_dump(mode="json")
        assert isinstance(payload[field], list)
        assert type(model).model_validate(payload) == model
        assert type(model).model_validate_json(model.model_dump_json()) == model
        collection = getattr(model, field)
        assert isinstance(collection, tuple)
        with pytest.raises(AttributeError):
            getattr(collection, "append")(None)
        with pytest.raises(ValidationError):
            setattr(model, field, ())
    assert "+05:30" in capture.model_dump_json()


def test_capture_golden_manifest_pins_recorded_specimens() -> None:
    manifest = json.loads(
        (Path(__file__).parents[2] / "fixtures/forecasting/ff0/capture_cases.json").read_text()
    )
    assert manifest["kind"] == "SYNTHETIC_TEST_MANIFEST_NOT_REPLAY_CORPUS"
    assert len(manifest["cases"]) == 10
    for mode, simulated in (("actual", False), ("simulated", True)):
        capture, _ = packet(simulated=simulated)
        assert capture.capture_id == manifest["capture_fingerprints"][mode]


def test_read_access_clock_is_not_a_rewritten_historical_clock(tmp_path: Path) -> None:
    capture, blobs = packet()
    writer(tmp_path).append_forecast(capture, blobs)
    before = inventory(tmp_path)
    with pytest.raises(ForecastIntegrityError, match="POSTDATES_ACCESS_CLOCK"):
        verify_replay(ForecastCorpusStore(tmp_path, as_of=instant(3)), capture.result.run_id)
    assert inventory(tmp_path) == before


@pytest.mark.parametrize("mode", [False, True])
def test_replay_preserves_all_original_clocks_and_never_simulates_or_labels(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: bool
) -> None:
    capture, blobs = packet(simulated=mode)
    store = writer(tmp_path)
    store.append_forecast(capture, blobs)
    before = inventory(tmp_path)

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("recorded replay attempted a new operation")

    from tiaf.evaluation import forecast_truth

    monkeypatch.setattr(forecast_truth, "resolve_outcome", forbidden)
    monkeypatch.setattr(ForecastCorpusStore, "append_forecast", forbidden)
    monkeypatch.setattr(ForecastCorpusStore, "append_outcome", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    restored = verify_replay(
        ForecastCorpusStore(tmp_path, as_of=instant(10)), capture.result.run_id
    )
    assert restored == capture
    assert canonical_json(restored) == canonical_json(capture)
    assert restored.result.replay_fingerprint == capture.result.replay_fingerprint
    assert inventory(tmp_path) == before


@pytest.mark.parametrize(
    "fault",
    [
        "payload",
        "missing_hash",
        "schema",
        "mode",
        "duplicate_key",
        "partial",
        "blank",
        "duplicate_row",
    ],
)
def test_journal_corruption_blocks_reads_and_writes_without_repair(
    tmp_path: Path, fault: str
) -> None:
    capture, blobs = packet()
    store = writer(tmp_path)
    store.append_forecast(capture, blobs)
    log = tmp_path / "forecast_runs.jsonl"
    original = log.read_text()
    payload = json.loads(original)
    if fault == "payload":
        payload["result"]["output"]["probability"] = 0.3
    elif fault == "missing_hash":
        payload.pop("capture_id")
    elif fault == "schema":
        payload["schema_version"] = "2.0"
    elif fault == "mode":
        payload["result"]["request"]["realization_mode"] = "SIMULATED_ISSUANCE"
    damaged = json.dumps(payload) + "\n"
    if fault == "duplicate_key":
        damaged = original.replace('"capture_id":', '"capture_id":"duplicate","capture_id":', 1)
    elif fault == "partial":
        damaged = original[:-1]
    elif fault == "blank":
        damaged = original + "\n"
    elif fault == "duplicate_row":
        damaged = original + original
    log.write_text(damaged)
    before = inventory(tmp_path)
    with pytest.raises(ForecastStoreError):
        store.get_forecast(capture.result.run_id)
    with pytest.raises(ForecastStoreError):
        store.append_forecast(capture, blobs)
    assert inventory(tmp_path) == before


@pytest.mark.parametrize("fault", ["missing", "content", "rights", "unknown_schema", "dependency"])
def test_replay_requires_exact_blob_closure(tmp_path: Path, fault: str) -> None:
    capture, blobs = packet()
    store = writer(tmp_path)
    store.append_forecast(capture, blobs)
    blob = blobs[0]
    path = tmp_path / "artifacts" / f"{blob.blob_reference.blob_hash}.json"
    payload = json.loads(path.read_text())
    if fault == "missing":
        path.unlink()
    else:
        if fault == "content":
            payload["content_json"] = "null"
        elif fault == "rights":
            payload["rights"]["replay"] = False
        elif fault == "unknown_schema":
            payload["schema_id"] = "unknown"
        else:
            payload["dependencies"] = [capture.build_ref.model_dump(mode="json")]
        path.write_text(json.dumps(payload))
    before = inventory(tmp_path)
    with pytest.raises(ForecastStoreError):
        verify_replay(store, capture.result.run_id)
    assert inventory(tmp_path) == before


def test_explicit_closure_missing_extra_duplicate_and_bad_snapshot_reject() -> None:
    capture, blobs = packet()
    for altered in (blobs[:-1], (*blobs, blobs[0])):
        with pytest.raises(ForecastIntegrityError):
            validate_capture(capture, altered, as_of=instant(10))
    data = capture.model_dump(mode="json", exclude={"capture_id"})
    data["snapshot"]["history"] = []
    with pytest.raises(ValidationError):
        ForecastCapture.model_validate(data)


@pytest.mark.parametrize("right", ["retain", "replay", "expired"])
def test_rights_are_not_granted_by_having_bytes(tmp_path: Path, right: str) -> None:
    capture, blobs = packet()
    altered = blobs[0].model_dump(mode="json")
    if right == "expired":
        altered["rights"]["read_until"] = instant(9).isoformat()
    else:
        altered["rights"][right] = False
    changed_blobs = (CapturedArtifact.model_validate(altered), *blobs[1:])
    data = capture.model_dump(mode="json", exclude={"capture_id"})
    data["closure"] = closure(changed_blobs)
    revised = ForecastCapture.model_validate(data)
    with pytest.raises(ForecastStoreError, match="RIGHTS"):
        writer(tmp_path).append_forecast(revised, changed_blobs)
    assert inventory(tmp_path) == {}
    if right == "expired":
        historical_access = ForecastCorpusStore(
            tmp_path, as_of=instant(8), owner=StoreOwner.FORECAST
        )
        historical_access.append_forecast(revised, changed_blobs)
        with pytest.raises(ForecastStoreError, match="EXPIRED"):
            writer(tmp_path).get_forecast(revised.result.run_id)


def test_stale_lock_is_not_removed(tmp_path: Path) -> None:
    capture, blobs = packet()
    lock = tmp_path / ".writer.lock"
    lock.write_text("owned-by-other-invocation")
    with pytest.raises(ForecastStoreError, match="WRITER"):
        writer(tmp_path).append_forecast(capture, blobs)
    assert lock.read_text() == "owned-by-other-invocation"


@pytest.mark.parametrize("place", ["root", "artifacts", "journal", "blob"])
def test_symlink_substitution_is_denied(tmp_path: Path, place: str) -> None:
    corpus, outside = tmp_path / "corpus", tmp_path / "outside"
    outside.mkdir()
    capture, blobs = packet()
    if place == "root":
        corpus.symlink_to(outside, target_is_directory=True)
    else:
        writer(corpus).append_forecast(capture, blobs)
        if place == "artifacts":
            path = corpus / "artifacts"
            path.rename(outside / "preserved-artifacts")
            path.symlink_to(outside / "preserved-artifacts", target_is_directory=True)
        else:
            path = (
                corpus / "forecast_runs.jsonl"
                if place == "journal"
                else next((corpus / "artifacts").glob("*.json"))
            )
            target = outside / path.name
            path.rename(target)
            path.symlink_to(target)
    before = inventory(outside)
    with pytest.raises(ForecastStoreError, match="SYMLINK"):
        writer(corpus).append_forecast(capture, blobs)
    assert inventory(outside) == before


@pytest.mark.parametrize("value", ['{"x":1,"x":2}', '{"x":NaN}', '{"api_key":"redacted-fixture"}'])
def test_unsafe_json_rejects_without_echo(value: str) -> None:
    with pytest.raises(ValueError, match="INVALID_CAPTURE_JSON") as error:
        strict_json(value)
    assert "redacted-fixture" not in str(error.value)


@pytest.mark.parametrize("fault", ["before_line", "partial_line"])
def test_failed_append_never_claims_transaction_success_or_repairs_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fault: str
) -> None:
    capture, blobs = packet()
    store = writer(tmp_path)
    original = ForecastCorpusStore._write

    def failing(self: ForecastCorpusStore, path: Path, content: bytes, *, append: bool) -> None:
        if append:
            if fault == "partial_line":
                original(self, path, content[:15], append=True)
            raise ForecastStoreError("INJECTED_WRITE_FAILURE")
        original(self, path, content, append=append)

    monkeypatch.setattr(ForecastCorpusStore, "_write", failing)
    with pytest.raises(ForecastStoreError, match="INJECTED"):
        store.append_forecast(capture, blobs)
    assert not (tmp_path / ".writer.lock").exists()
    assert list((tmp_path / "artifacts").glob("*.json"))  # Orphans are not completed forecasts.
    before = inventory(tmp_path)
    with pytest.raises(ForecastStoreError, match="PARTIAL|NOT_FOUND"):
        store.get_forecast(capture.result.run_id)
    assert inventory(tmp_path) == before
    if fault == "before_line":
        monkeypatch.setattr(ForecastCorpusStore, "_write", original)
        assert store.append_forecast(capture, blobs)  # Explicit retry, no automatic retry.


def test_os_write_failure_is_typed_and_sanitized(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    capture, blobs = packet()

    def failed(*args: object, **kwargs: object) -> int:
        raise OSError("private-path-or-token")

    monkeypatch.setattr(os, "write", failed)
    with pytest.raises(ForecastStoreError, match="WRITE_FAILED") as error:
        writer(tmp_path).append_forecast(capture, blobs)
    assert "private-path-or-token" not in str(error.value)


@pytest.mark.parametrize("bound", ["MAX_RECORD_BYTES", "MAX_CORPUS_BYTES", "MAX_JOURNAL_RECORDS"])
def test_resource_denial_is_preflight_no_truncation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bound: str
) -> None:
    import tiaf.forecasting.store as module

    capture, blobs = packet()
    monkeypatch.setattr(module, bound, 0)
    with pytest.raises(ForecastStoreError, match="LIMIT"):
        writer(tmp_path).append_forecast(capture, blobs)
    assert inventory(tmp_path) == {}


def test_optional_sdk_absence_recorded_replay_in_fresh_process(tmp_path: Path) -> None:
    capture, blobs = packet()
    writer(tmp_path).append_forecast(capture, blobs)
    code = """
import sys
from datetime import datetime
from pathlib import Path
blocked = {"httpx", "mcp", "dotenv", "pydantic_settings", "langgraph", "langsmith",
           "numpy", "pandas", "sklearn", "xgboost", "torch", "tensorflow", "yfinance"}
class Guard:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.partition(".")[0] in blocked or fullname.startswith((
            "tiaf.forecasting.forecasters", "tiaf.forecasting.runtime",
            "tiaf.evaluation.forecast_truth", "tiaf.data.providers.")):
            raise ModuleNotFoundError("forbidden optional or execution import", name=fullname)
sys.meta_path.insert(0, Guard())
from tiaf.forecasting.store import ForecastCorpusStore
from tiaf.forecasting.replay import verify_replay
from tiaf.facade import capability_catalog
store = ForecastCorpusStore(Path(sys.argv[1]),
    as_of=datetime.fromisoformat("2026-02-10T16:00:00+05:30"))
assert verify_replay(store, "ff-run:actual-1").capture_id == sys.argv[2]
assert len(capability_catalog()) == 9
assert not blocked.intersection(sys.modules)
print("RECORDED_REPLAY_ISOLATION_PASS")
"""
    completed = subprocess.run(
        [sys.executable, "-B", "-c", code, str(tmp_path), capture.capture_id or ""],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "RECORDED_REPLAY_ISOLATION_PASS" in completed.stdout
