"""FF0-18/22–24/26: new generation, old recording, independent truth and pinned checks."""

import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from tiaf.evaluation.forecast_contracts import ForecastLedgerSnapshot
from tiaf.evaluation.forecast_linkage import link_forecast_outcome
from tiaf.forecasting.capture import ForecastCapture
from tiaf.forecasting.contracts import ForecastResult
from tiaf.forecasting.errors import ForecastIntegrityError
from tiaf.forecasting.forecasters import HistoricalBaseRateForecaster
from tiaf.forecasting.replay import verify_pinned, verify_replay
from tiaf.forecasting.store import ForecastCorpusStore, StoreOwner

from ._capture_support import outcome_packet, packet
from ._runtime_support import FixedClock, fixture
from ._support import instant
from .test_baserate_runtime import owner
from .test_capture_store_replay import inventory


@pytest.mark.parametrize("simulated", [False, True])
def test_generate_capture_recorded_replay_and_pinned_verification_are_distinct(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, simulated: bool
) -> None:
    f = fixture(simulated=simulated)
    captured = owner(f, tmp_path).run(f.request, f.snapshot, f.blobs)
    store = ForecastCorpusStore(tmp_path, as_of=instant(10))
    before = inventory(tmp_path)
    original = HistoricalBaseRateForecaster.forecast

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("recorded replay invoked a forecaster/provider")

    monkeypatch.setattr(HistoricalBaseRateForecaster, "forecast", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    assert verify_replay(store, captured.result.run_id) == captured
    assert inventory(tmp_path) == before
    monkeypatch.setattr(HistoricalBaseRateForecaster, "forecast", original)
    verified = verify_pinned(store, captured.result.run_id, _clock=FixedClock(instant(10)))
    assert verified.status == "VERIFIED" and verified.usage.attempts == 1
    assert verified.original_result_fingerprint == verified.reconstructed_result_fingerprint
    assert verified.usage.local_cost == "UNPRICED"
    assert captured.result.inference is not None
    assert verified.usage.attempt_id != captured.result.inference.usage.attempt_id
    assert verified.usage.completed_at != captured.result.computed_at
    assert inventory(tmp_path) == before


def test_new_actual_and_simulations_share_independent_truth_without_extra_observations(
    tmp_path: Path,
) -> None:
    actual, simulated = fixture(simulated=False), fixture()
    first = owner(actual, tmp_path).run(actual.request, actual.snapshot, actual.blobs)
    runtime = owner(simulated, tmp_path)
    second = runtime.run(simulated.request, simulated.snapshot, simulated.blobs)
    third = runtime.run(simulated.request, simulated.snapshot, simulated.blobs)
    evaluation = ForecastCorpusStore(tmp_path, as_of=instant(10), owner=StoreOwner.EVALUATION)
    blobs = evaluation.get_forecast_artifacts(first.result.run_id)
    truth, truth_blobs = outcome_packet(first, blobs)
    assert evaluation.append_outcome(truth, truth_blobs)
    links = tuple(
        link_forecast_outcome(capture, truth, created_at=instant(10))
        for capture in (first, second, third)
    )
    for link in links:
        assert evaluation.append_link(link)
    ledger = ForecastLedgerSnapshot(links=links, created_at=instant(10))
    assert evaluation.append_ledger(ledger)
    assert len({link.observation_id for link in links}) == 1
    assert len({link.outcome_key for link in links}) == 1
    assert len({link.run_id for link in links}) == 3
    assert all(link.eligibility == "ENGINEERING_LINK_ELIGIBLE" for link in links)
    assert evaluation.get_ledger(ledger.snapshot_id or "") == ledger


@pytest.mark.parametrize("n", [0, 19, 20])
def test_support_absence_and_boundary_generation_verify_exactly(tmp_path: Path, n: int) -> None:
    f = fixture(included=n)
    capture = owner(f, tmp_path).run(f.request, f.snapshot, f.blobs)
    report = verify_pinned(
        ForecastCorpusStore(tmp_path, as_of=instant(10)),
        capture.result.run_id,
        _clock=FixedClock(instant(10)),
    )
    assert report.status == "VERIFIED"


@pytest.mark.parametrize("fault", ["probability", "support", "profile"])
def test_resealed_material_mismatch_fails_pinned_verification(tmp_path: Path, fault: str) -> None:
    f = fixture()
    original = owner(f, tmp_path / "original").run(f.request, f.snapshot, f.blobs)
    store = ForecastCorpusStore(tmp_path / "original", as_of=instant(10))
    blobs = store.get_forecast_artifacts(original.result.run_id)
    data = original.result.model_dump(mode="json", exclude={"replay_fingerprint"})
    if fault == "probability":
        data["output"]["probability"] = 0.7
    elif fault == "support":
        data["inference"]["support"]["positive_count"] = 11
    else:
        data["binding_available_at"] = instant(8)
    altered = ForecastResult.model_validate(data)
    packet_data = original.model_dump(mode="json", exclude={"capture_id"})
    packet_data["result"] = altered.model_dump(mode="json")
    capture = ForecastCapture.model_validate(packet_data)
    target = ForecastCorpusStore(
        tmp_path / "resealed", as_of=instant(10), owner=StoreOwner.FORECAST
    )
    target.append_forecast(capture, blobs)
    assert verify_replay(target, capture.result.run_id) == capture
    before = inventory(target.root)
    assert (
        verify_pinned(target, capture.result.run_id, _clock=FixedClock(instant(10))).status
        == "MISMATCH"
    )
    assert inventory(target.root) == before


@pytest.mark.parametrize("fault", ["missing", "different_descriptor", "exception", "deadline"])
def test_unavailable_verifier_never_falls_back_or_mutates_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fault: str
) -> None:
    from tiaf.forecasting import forecasters

    f = fixture()
    capture = owner(f, tmp_path).run(f.request, f.snapshot, f.blobs)
    before = inventory(tmp_path)
    if fault == "missing":

        def missing(*args: object, **kwargs: object) -> None:
            raise ForecastIntegrityError("MISSING_EXACT_VERIFIER")

        monkeypatch.setattr(forecasters, "resolve_forecaster", missing)
    elif fault == "different_descriptor":
        original = HistoricalBaseRateForecaster.descriptor

        def different(self: HistoricalBaseRateForecaster) -> object:
            return original(self).model_copy(update={"required_evidence": "different"})

        monkeypatch.setattr(HistoricalBaseRateForecaster, "descriptor", different)
    elif fault == "exception":

        def failed(*args: object, **kwargs: object) -> None:
            raise RuntimeError("private-payload")

        monkeypatch.setattr(HistoricalBaseRateForecaster, "forecast", failed)
    store = ForecastCorpusStore(tmp_path, as_of=instant(10))
    report = verify_pinned(
        store,
        capture.result.run_id,
        _clock=FixedClock(instant(10), step=1.1 if fault == "deadline" else 0.01),
    )
    assert report.status == "UNVERIFIABLE" and "private-payload" not in report.model_dump_json()
    assert verify_replay(store, capture.result.run_id) == capture
    assert inventory(tmp_path) == before


def test_legacy_specimens_remain_replayable_but_not_claimed_executed(tmp_path: Path) -> None:
    captured, blobs = packet()
    store = ForecastCorpusStore(tmp_path, as_of=instant(10), owner=StoreOwner.FORECAST)
    store.append_forecast(captured, blobs)
    assert verify_replay(store, captured.result.run_id) == captured
    report = verify_pinned(store, captured.result.run_id, _clock=FixedClock(instant(10)))
    assert report.status == "UNVERIFIABLE" and report.usage.attempts == 0
    assert "inference" not in captured.result.model_dump(mode="json")


def test_fresh_process_recorded_replay_needs_no_inference_or_optional_imports(
    tmp_path: Path,
) -> None:
    f = fixture()
    capture = owner(f, tmp_path).run(f.request, f.snapshot, f.blobs)
    code = r"""
import importlib.abc
import socket
import sys
from datetime import datetime
from pathlib import Path
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        forbidden = ('numpy','sklearn','torch','tensorflow','xgboost','mcp','httpx','requests',
                     'tiaf.forecasting.forecasters','tiaf.forecasting.runtime',
                     'tiaf.forecasting.support','tiaf.evaluation.forecast_truth')
        if any(fullname == name or fullname.startswith(name + '.') for name in forbidden):
            raise AssertionError('forbidden import: ' + fullname)
sys.meta_path.insert(0, Block())
def denied(*args, **kwargs): raise AssertionError('live access')
socket.create_connection = denied
from tiaf.forecasting.replay import verify_replay
from tiaf.forecasting.store import ForecastCorpusStore
from tiaf.facade.capabilities import capability_discovery_catalog
result = verify_replay(ForecastCorpusStore(Path(sys.argv[1]),
    as_of=datetime.fromisoformat('2026-02-10T16:00:00+05:30')), sys.argv[2])
assert result.result.inference.usage.attempts == 1
assert len(capability_discovery_catalog()) == 9
print('PASS')
"""
    completed = subprocess.run(
        [sys.executable, "-B", "-c", code, str(tmp_path), capture.result.run_id],
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "PASS"
