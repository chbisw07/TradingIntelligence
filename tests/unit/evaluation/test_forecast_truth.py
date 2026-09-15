"""FF0-19–21: independent exact endpoint labels, missingness and immutable revisions."""

from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from tiaf.evaluation.forecast_contracts import OutcomeJournalEntry, QualifiedCloseObservation
from tiaf.evaluation.forecast_truth import resolve_outcome
from tiaf.forecasting.errors import ForecastIntegrityError

from ..forecasting._capture_support import outcome_packet, packet
from ..forecasting._support import instant
from ..forecasting.test_capture_store_replay import inventory, writer


@pytest.mark.parametrize(
    "price,label",
    [("106", 1), ("104", 0), ("105", 0), ("105.000", 0), ("105.00000000000000000001", 1)],
)
def test_exact_independent_up_down_and_tie(price: str, label: int) -> None:
    capture, artifacts = packet()
    outcome, _ = outcome_packet(capture, artifacts, price=Decimal(price))
    assert outcome.label == label
    assert outcome.label_eligibility == "ELIGIBLE"
    assert outcome.window_state == "CLOSED"
    assert outcome.operation_state == "UNKNOWN"
    assert outcome.path_execution_measures == "NOT_APPLICABLE"
    assert outcome.outcome_event_time == instant(5, 15, 30)
    assert outcome.label_available_at is not None
    assert outcome.outcome_event_time <= outcome.label_available_at <= outcome.recorded_at
    assert OutcomeJournalEntry.model_validate_json(outcome.model_dump_json()) == outcome


@pytest.mark.parametrize(
    "day,hour,window,eligibility",
    [
        (5, 10, "OPEN", "PENDING"),
        (5, 16, "CLOSED", "PENDING"),
        (6, 9, "CLOSED", "PENDING"),
        (6, 10, "CENSORED", "INELIGIBLE"),
        (7, 16, "CENSORED", "INELIGIBLE"),
    ],
)
def test_missing_is_pending_then_censored_without_label(
    day: int, hour: int, window: str, eligibility: str
) -> None:
    capture, artifacts = packet()
    outcome, _ = outcome_packet(capture, artifacts, price=None, day=day, evaluated_hour=hour)
    assert outcome.window_state == window and outcome.label_eligibility == eligibility
    assert outcome.label is None
    assert outcome.outcome_event_time is None and outcome.label_available_at is None
    assert outcome.observation_state == "MISSING"


@pytest.mark.parametrize("reason", ["SCHEDULE", "ACTION", "SOURCE"])
def test_explicit_invalidations_do_not_retarget_or_adjust_prices(reason: str) -> None:
    capture, artifacts = packet()
    outcome, _ = outcome_packet(capture, artifacts, invalidation=reason)
    assert outcome.label is None and outcome.label_eligibility == "AMBIGUOUS"
    assert outcome.window == capture.snapshot.window
    assert outcome.window.target_session_id == "session:s21"
    assert outcome.window_state == "UNOBSERVABLE"


@pytest.mark.parametrize("value", [0, -1, True, 105.0, "NaN", "Infinity"])
def test_invalid_terminal_price_cannot_become_label(value: object) -> None:
    capture, artifacts = packet()
    outcome, _ = outcome_packet(capture, artifacts)
    assert outcome.terminal is not None
    data = outcome.terminal.model_dump(mode="json")
    data["value"] = value
    with pytest.raises(ValidationError):
        QualifiedCloseObservation.model_validate(data)


@pytest.mark.parametrize(
    "field,value",
    [
        ("label", 0),
        ("label", True),
        ("outcome_event_time", "2026-02-05T15:29:00+05:30"),
        ("label_available_at", "2026-02-05T15:30:00+05:30"),
        ("recorded_at", "2026-02-04T16:00:00+05:30"),
        ("recorded_at", "2026-02-05T16:01:00"),
        ("schema_version", "2.0"),
        ("operation_state", "NOT_TAKEN"),
        ("revision", 1),
        ("fingerprint", "0" * 64),
    ],
)
def test_outcome_invariants_reject_fabricated_fields(field: str, value: object) -> None:
    capture, artifacts = packet()
    outcome, _ = outcome_packet(capture, artifacts)
    data = outcome.model_dump(mode="json", exclude={"fingerprint"})
    data[field] = value
    with pytest.raises(ValidationError):
        OutcomeJournalEntry.model_validate(data)


def test_revised_truth_keeps_original_bytes_and_exact_revisions(tmp_path: Path) -> None:
    capture, artifacts = packet()
    first, first_blobs = outcome_packet(capture, artifacts)
    second, second_blobs = outcome_packet(
        capture, artifacts, price=Decimal("100"), revision=1, previous=first, day=6
    )
    store = writer(tmp_path, evaluation=True)
    store.append_outcome(first, first_blobs)
    original_line = (tmp_path / "outcome_records.jsonl").read_bytes()
    assert store.append_outcome(second, second_blobs)
    assert (tmp_path / "outcome_records.jsonl").read_bytes().startswith(original_line)
    assert first.key == second.key
    assert first.label == 1 and second.label == 0
    assert second.predecessor == first.reference
    assert store.get_outcome(first.entry_id) == first
    assert store.get_outcome(second.entry_id) == second
    assert not store.append_outcome(first, first_blobs)


def test_late_valid_proof_revises_censored_entry(tmp_path: Path) -> None:
    capture, artifacts = packet()
    absent, absent_blobs = outcome_packet(capture, artifacts, price=None, day=6, evaluated_hour=10)
    late, late_blobs = outcome_packet(capture, artifacts, revision=1, previous=absent, day=7)
    store = writer(tmp_path, evaluation=True)
    store.append_outcome(absent, absent_blobs)
    store.append_outcome(late, late_blobs)
    assert store.get_outcome(absent.entry_id).label is None
    assert store.get_outcome(late.entry_id).label == 1
    assert absent.window.target_resolve_time == late.window.target_resolve_time


@pytest.mark.parametrize("fault", ["gap", "fork", "predecessor", "backdated", "duplicate_id"])
def test_revision_denials_do_not_write_orphan_blobs(tmp_path: Path, fault: str) -> None:
    capture, artifacts = packet()
    first, first_blobs = outcome_packet(capture, artifacts)
    second, second_blobs = outcome_packet(
        capture, artifacts, price=Decimal("100"), revision=1, previous=first, day=6
    )
    store = writer(tmp_path, evaluation=True)
    store.append_outcome(first, first_blobs)
    data = second.model_dump(mode="json", exclude={"fingerprint"})
    if fault == "gap":
        data["revision"] = 2
    elif fault == "fork":
        data.update(revision=0, predecessor=None, revision_reason=None)
    elif fault == "predecessor":
        data["predecessor"]["fingerprint"] = "0" * 64
    elif fault == "duplicate_id":
        data["entry_id"] = first.entry_id
    else:
        first_data = first.model_dump(mode="json", exclude={"fingerprint"})
        first_data["recorded_at"] = instant(8)
        later_recorded = OutcomeJournalEntry.model_validate(first_data)
        # Use a separate corpus so the predecessor really has that recorded timestamp.
        root = tmp_path / "later-recorded"
        store = writer(root, evaluation=True)
        store.append_outcome(later_recorded, first_blobs)
        data["predecessor"] = later_recorded.reference.model_dump(mode="json")
    altered = OutcomeJournalEntry.model_validate(data)
    before = inventory(store.root)
    with pytest.raises(ForecastIntegrityError):
        store.append_outcome(altered, second_blobs)
    assert inventory(store.root) == before


def test_labeler_does_not_accept_forecast_or_generation_inputs() -> None:
    import inspect

    names = set(inspect.signature(resolve_outcome).parameters)
    assert not names.intersection(
        {"forecast", "probability", "forecaster", "run_id", "realization_mode"}
    )


@pytest.mark.parametrize("at_deadline", [False, True])
def test_explicit_missing_terminal_stays_pending_until_exact_deadline(at_deadline: bool) -> None:
    capture, artifacts = packet()
    original, _ = outcome_packet(capture, artifacts)
    assert original.terminal is not None
    data = original.terminal.model_dump(mode="json")
    data.update(value=None, qualification="MISSING", reasons=["EVIDENCE_MISSING"])
    terminal = QualifiedCloseObservation.model_validate(data)
    when = original.window.outcome_due_at if at_deadline else original.evaluated_at
    outcome = resolve_outcome(
        entry_id="outcome:typed-missing",
        target=original.target,
        window=original.window,
        terminal=terminal,
        check_evidence=original.check_evidence,
        evaluated_at=when,
        recorded_at=when,
        closure=original.closure,
    )
    assert outcome.label is None and outcome.outcome_event_time is None
    assert outcome.label_eligibility == ("INELIGIBLE" if at_deadline else "PENDING")
    assert outcome.window_state == ("CENSORED" if at_deadline else "CLOSED")


@pytest.mark.parametrize(
    "facet", ["eligibility", "pending_after_due", "early_censored", "ambiguous"]
)
def test_resealed_contradictory_truth_facets_are_rejected(facet: str) -> None:
    capture, artifacts = packet()
    original, _ = outcome_packet(
        capture, artifacts, price=None if facet != "eligibility" else Decimal("110")
    )
    data = original.model_dump(mode="json", exclude={"fingerprint"})
    if facet == "eligibility":
        data["window"]["schedule"]["sessions"][1]["subject_eligible"] = False
    elif facet == "pending_after_due":
        data.update(evaluated_at=instant(7), recorded_at=instant(7))
    elif facet == "early_censored":
        data.update(window_state="CENSORED", label_eligibility="INELIGIBLE")
    else:
        data["label_eligibility"] = "AMBIGUOUS"
    with pytest.raises(ValidationError):
        OutcomeJournalEntry.model_validate(data)


@pytest.mark.parametrize("endpoint", ["reference", "terminal"])
def test_stored_truth_must_match_captured_bar_before_any_append(
    tmp_path: Path, endpoint: str
) -> None:
    capture, artifacts = packet()
    original, blobs = outcome_packet(capture, artifacts)
    data = original.model_dump(mode="json", exclude={"fingerprint"})
    close = data["window"]["reference"] if endpoint == "reference" else data["terminal"]
    close["value"] = "104" if endpoint == "reference" else "111"
    altered = OutcomeJournalEntry.model_validate(data)  # Label still 1; source bar disagrees.
    with pytest.raises(ForecastIntegrityError, match="CAPTURED_BAR_MISMATCH"):
        writer(tmp_path, evaluation=True).append_outcome(altered, blobs)
    assert inventory(tmp_path) == {}


@pytest.mark.parametrize("invalidation", ["SCHEDULE", "ACTION", "SOURCE"])
def test_material_correction_appends_explicit_invalidation_revision(
    tmp_path: Path, invalidation: str
) -> None:
    capture, artifacts = packet()
    first, blobs = outcome_packet(capture, artifacts)
    revised, revised_blobs = outcome_packet(
        capture, artifacts, revision=1, previous=first, day=6, invalidation=invalidation
    )
    store = writer(tmp_path, evaluation=True)
    store.append_outcome(first, blobs)
    before = (tmp_path / "outcome_records.jsonl").read_bytes()
    store.append_outcome(revised, revised_blobs)
    assert (tmp_path / "outcome_records.jsonl").read_bytes().startswith(before)
    assert store.get_outcome(first.entry_id).label == 1
    assert store.get_outcome(revised.entry_id).label is None
    assert revised.key == first.key and revised.predecessor == first.reference
    assert revised.label_eligibility == "AMBIGUOUS"
