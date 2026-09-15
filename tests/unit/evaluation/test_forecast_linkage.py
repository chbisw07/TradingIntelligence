"""FF0-22: exact backward links and immutable joined views, no scoring or pooling."""

from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from tiaf.evaluation.forecast_contracts import (
    EvaluationLink,
    ForecastLedgerSnapshot,
    OutcomeJournalEntry,
)
from tiaf.evaluation.forecast_linkage import link_forecast_outcome
from tiaf.forecasting.capture import ForecastCapture
from tiaf.forecasting.errors import ForecastIntegrityError

from ..forecasting._capture_support import outcome_packet, packet
from ..forecasting._support import instant
from ..forecasting.test_capture_store_replay import inventory, writer


def test_actual_and_two_simulations_link_one_outcome_without_pooling(tmp_path: Path) -> None:
    specimens = [packet(), packet(simulated=True), packet(simulated=True, number=2)]
    outcome, outcome_blobs = outcome_packet(*specimens[0])
    evaluation = writer(tmp_path, evaluation=True)
    evaluation.append_outcome(outcome, outcome_blobs)
    links = []
    for capture, blobs in specimens:
        writer(tmp_path).append_forecast(capture, blobs)
        link = link_forecast_outcome(capture, outcome, created_at=instant(9))
        evaluation.append_link(link)
        assert link.eligibility == "ENGINEERING_LINK_ELIGIBLE"
        assert link.comparison_authority == "NO_METRICS_NO_POOLING"
        assert link.realization_mode == capture.result.request.realization_mode
        links.append(link)
    assert len({link.outcome_key for link in links}) == 1
    assert len({link.observation_id for link in links}) == 1
    assert len({link.link_id for link in links}) == 3
    assert len((tmp_path / "outcome_records.jsonl").read_text().splitlines()) == 1


@pytest.mark.parametrize(
    "fault", ["target_version", "subject", "session", "reference", "basis", "link_time"]
)
def test_incompatible_truth_never_links(fault: str) -> None:
    capture, artifacts = packet()
    outcome, _ = outcome_packet(capture, artifacts)
    data = outcome.model_dump(mode="json", exclude={"fingerprint"})
    if fault == "target_version":
        data["target"]["target_version"] = "2.0"
    elif fault == "subject":
        data["target"]["subject"]["symbol"] = "HDFCBANK"
    elif fault == "session":
        data["window"]["target_session_id"] = "session:s22"
    elif fault == "reference":
        data["window"]["reference"]["source"]["document_version_id"] = "document:revised"
    elif fault == "basis":
        data["window"]["reference"]["price_basis"] = "ADJUSTED"
    with pytest.raises((ValidationError, ForecastIntegrityError)):
        other = OutcomeJournalEntry.model_validate(data)
        link_forecast_outcome(
            capture, other, created_at=instant(4) if fault == "link_time" else instant(9)
        )


@pytest.mark.parametrize(
    "status,reason",
    [
        ("UNAVAILABLE", "EVIDENCE_MISSING"),
        ("ABSTAINED", "POLICY_ABSTENTION"),
        ("FAILED", "INTERNAL_EXECUTION_FAILURE"),
        ("UNSUPPORTED", "SCOPE_UNSUPPORTED"),
    ],
)
def test_absent_forecasts_are_retained_not_evaluable(status: str, reason: str) -> None:
    capture, artifacts = packet()
    outcome, _ = outcome_packet(capture, artifacts)
    data = capture.model_dump(mode="json", exclude={"capture_id"})
    result = data["result"]
    result.pop("replay_fingerprint")
    result.update(status=status, issued_at=None, output={"kind": "ABSENCE", "reasons": [reason]})
    absent = ForecastCapture.model_validate(data)
    link = link_forecast_outcome(absent, outcome, created_at=instant(9))
    assert link.eligibility == "NOT_EVALUABLE" and "link:forecast-absent" in link.reasons


def test_missing_outcome_link_and_old_ledger_are_immutable_after_revision(tmp_path: Path) -> None:
    capture, artifacts = packet()
    missing, missing_blobs = outcome_packet(capture, artifacts, price=None)
    corrected, corrected_blobs = outcome_packet(
        capture, artifacts, price=Decimal("105"), revision=1, previous=missing, day=6
    )
    writer(tmp_path).append_forecast(capture, artifacts)
    store = writer(tmp_path, evaluation=True)
    store.append_outcome(missing, missing_blobs)
    first_link = link_forecast_outcome(capture, missing, created_at=instant(5, 17))
    assert first_link.eligibility == "NOT_EVALUABLE"
    store.append_link(first_link)
    first = ForecastLedgerSnapshot(links=(first_link,), created_at=instant(5, 18))
    store.append_ledger(first)
    before = inventory(tmp_path)
    store.append_outcome(corrected, corrected_blobs)
    new_link = link_forecast_outcome(capture, corrected, created_at=instant(6, 17))
    store.append_link(new_link)
    second = ForecastLedgerSnapshot(
        links=(new_link,), created_at=instant(6, 18), predecessor=first.reference
    )
    store.append_ledger(second)
    assert store.get_ledger(first.snapshot_id or "") == first
    assert store.get_ledger(second.snapshot_id or "") == second
    assert store.get_link(first_link.link_id or "").outcome_ref == missing.reference
    assert store.get_link(new_link.link_id or "").outcome_ref == corrected.reference
    assert (tmp_path / "ledger_snapshots" / f"{first.snapshot_id}.json").read_bytes() == before[
        f"ledger_snapshots/{first.snapshot_id}.json"
    ]


@pytest.mark.parametrize(
    "fault", ["outcome_ref", "capture_ref", "result_id", "mode", "eligibility"]
)
def test_store_rejects_forged_link_relations_even_with_new_hash(tmp_path: Path, fault: str) -> None:
    capture, blobs = packet()
    missing, missing_blobs = outcome_packet(capture, blobs, price=None)
    writer(tmp_path).append_forecast(capture, blobs)
    store = writer(tmp_path, evaluation=True)
    store.append_outcome(missing, missing_blobs)
    link = link_forecast_outcome(capture, missing, created_at=instant(9))
    data = link.model_dump(mode="json", exclude={"link_id"})
    if fault.endswith("ref"):
        data[fault]["fingerprint"] = "0" * 64
    elif fault == "result_id":
        data[fault] = "result:unknown"
    elif fault == "mode":
        data["realization_mode"] = "SIMULATED_ISSUANCE"
    else:
        data["eligibility"] = "ENGINEERING_LINK_ELIGIBLE"
    before = inventory(tmp_path)
    with pytest.raises(ForecastIntegrityError):
        store.append_link(EvaluationLink.model_validate(data))
    assert inventory(tmp_path) == before
