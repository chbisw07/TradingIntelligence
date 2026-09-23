"""Executable FF-2.1 governance specification, NOT a runtime admission service.

Only authored metadata witnesses are exercised. No empirical source is decoded,
no calibration is implemented, and a passing witness grants no execution right.
FF-2.2 must port these obligations to its real captured-artifact admission edge.
"""

import json
from datetime import timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tiaf.forecasting.identity import ForecastDateTime, canonical_json, semantic_fingerprint
from tiaf.learning.forecast_artifacts import SealedResearch

ROOT = Path(__file__).resolve().parents[3]
AUTHORITY = ROOT / "docs/qualification_records/ff2_1/data_use_authority.json"


def authority() -> dict[str, Any]:
    value: dict[str, Any] = json.loads(AUTHORITY.read_text())
    seal = value.pop("fingerprint")
    assert seal == semantic_fingerprint(value)
    return value


class MetadataWitness(SealedResearch):
    """Test-only clock/identity projection; deliberately contains no p, q or y."""

    observation_id: str
    subject: str
    target: str
    candidate: str
    model: str
    scaler: str
    feature_schema: str
    freeze_pin: str
    component_pin: str
    raw_capture: str
    calibrated_capture: str
    benchmark_capture: str
    source_dataset: str
    source_kind: str
    origin: ForecastDateTime
    generated: ForecastDateTime
    persisted: ForecastDateTime
    input_available: ForecastDateTime
    target_open: ForecastDateTime
    target_close: ForecastDateTime
    truth_available: ForecastDateTime | None
    assessed: ForecastDateTime
    passed_proofs: tuple[str, ...]


def witness(**updates: Any) -> MetadataWitness:
    policy = authority()
    source = policy["source_model"]
    data: dict[str, Any] = {
        "observation_id": "test-only:prospective-slot-1",
        "subject": policy["source"]["subject"],
        "target": source["target_id"],
        "candidate": policy["candidate_id"],
        "model": source["model_fingerprint"],
        "scaler": source["scaler_fingerprint"],
        "feature_schema": source["feature_schema_fingerprint"],
        "freeze_pin": "test-only:frozen-closure",
        "component_pin": "test-only:all-components-code-policy-parameters",
        "raw_capture": "test-only:raw-1",
        "calibrated_capture": "test-only:calibrated-1",
        "benchmark_capture": "test-only:benchmark-1",
        "source_dataset": "test-only:authored-future-input",
        "source_kind": "CAPTURED_AS_KNOWN",
        "origin": "2027-01-06T15:30:00+05:30",
        "input_available": "2027-01-06T15:45:00+05:30",
        "generated": "2027-01-06T16:00:00+05:30",
        "persisted": "2027-01-06T16:01:00+05:30",
        "target_open": "2027-01-07T09:15:00+05:30",
        "target_close": "2027-01-07T15:30:00+05:30",
        "truth_available": "2027-01-07T16:00:00+05:30",
        "assessed": "2027-01-14T15:30:00+05:30",
        "passed_proofs": [
            "integrity",
            "recorded_replay",
            "pinned_numeric_verifier",
            "basis",
            "calendar",
            "actions",
            "source_rights",
            "no_early_exposure",
        ],
    }
    data.update(updates)
    return MetadataWitness.model_validate(data)


def specification_reasons(
    row: MetadataWitness, *, previous_slots: tuple[tuple[str, str, str], ...] = ()
) -> tuple[str, ...]:
    """Reference predicates for one explicitly authored schedule, never live authority.

    The real qualifier must derive these fields/proofs from pinned capture bytes
    and external custody, not trust flags supplied by a forecast producer.
    """
    row = MetadataWitness.model_validate(row.model_dump())
    policy = authority()
    expected = witness()
    # Authored freeze/embargo instants, NOT actual FF-2 experiment clocks.
    frozen = expected.origin - timedelta(days=2)
    embargo_end = expected.origin - timedelta(days=1)
    deadline = row.target_close + timedelta(
        days=policy["prospective"]["truth_deadline_calendar_days"]
    )
    slot = (row.subject, row.target, row.origin.isoformat())
    proofs = set(row.passed_proofs)
    checks = {
        "UNIQUE_SLOT": slot not in previous_slots
        and (row.origin, row.target_open, row.target_close)
        == (expected.origin, expected.target_open, expected.target_close),
        "NOT_HISTORICAL": row.source_kind == "CAPTURED_AS_KNOWN"
        and row.source_dataset != policy["source"]["csv_sha256"]
        and row.origin > frozen,
        "EXACT_FREEZE": (row.candidate, row.freeze_pin, row.component_pin, row.subject, row.target)
        == (
            expected.candidate,
            expected.freeze_pin,
            expected.component_pin,
            expected.subject,
            expected.target,
        ),
        "SOURCE_PINS": (row.model, row.scaler, row.feature_schema)
        == (expected.model, expected.scaler, expected.feature_schema),
        "AFTER_FREEZE_EMBARGO": frozen < embargo_end < row.origin < row.generated,
        "TIMELY_CAPTURE": row.generated <= row.persisted < row.target_open < row.target_close,
        "PAST_ONLY_FEATURES": row.origin <= row.input_available <= row.generated,
        "UNKNOWN_TRUTH": row.truth_available is None
        or (
            row.truth_available > max(frozen, row.generated, row.persisted)
            and row.truth_available >= row.target_close
        ),
        "MATURED": row.assessed >= deadline,
        "TRUTH_DEADLINE": row.truth_available is not None
        and row.target_close <= row.truth_available <= deadline,
        "INTEGRITY_REPLAY": {"integrity", "recorded_replay", "pinned_numeric_verifier"} <= proofs
        and len({row.raw_capture, row.calibrated_capture, row.benchmark_capture}) == 3,
        "COMMON_BASIS": {"basis", "calendar", "actions", "source_rights"} <= proofs,
        "NO_EARLY_EXPOSURE": "no_early_exposure" in proofs,
    }
    assert list(checks) == policy["prospective"]["qualification_rule_ids"]
    return tuple(key for key, passed in checks.items() if not passed)


def test_authority_integrity_scope_and_unchanged_protocol() -> None:
    policy = authority()
    assert (
        sha256((ROOT / policy["protocol_path"]).read_bytes()).hexdigest()
        == policy["protocol_sha256"]
    )
    assert policy["record_kind"] == "GOVERNANCE_DESIGN_NOT_EXECUTION_GRANT"
    assert policy["rights"]["ff2_empirical_grant"] is None
    assert policy["rights"]["ff2_rights_admission"] == "NOT_GRANTED"
    assert policy["rights"]["explicit_denial"] == "BLOCK_ALL_POLICIES"
    assert policy["readiness"] == {
        "implementation": "SYNTHETIC_ONLY",
        "empirical_development": False,
        "prospective_collection": False,
        "final_protected_evaluation": False,
        "promotion": False,
        "activation": False,
    }
    assert policy["source_model"]["base_model_fits_allowed"] == 0
    assert policy["source_model"]["scaler_fits_allowed"] == 0
    assert policy["historical_ff1"]["holdout_status"] == "CONSUMED"
    assert policy["historical_ff1"]["executions"] == 1
    assert not policy["historical_ff1"]["post_holdout_refit"]


def test_historical_allocation_does_not_mint_independence_or_a_fit_grant() -> None:
    policy = authority()["historical_use_policy"]
    rows = policy["scientific_allocation"]
    assert sum(row["rows"] for row in rows) == 2045
    assert policy["execution_authority"] == "NONE_PENDING_FF2_SPECIFIC_GRANT"
    assert policy["all_existing_source_rows_prohibited_as_protected"]
    assert rows[-2]["status"] == "CONSUMED_PROTECTED"
    assert all(r["role"] == "HASH_AND_RECORDED_STATUS_ONLY" for r in rows[-2:])
    assert policy["configuration_count"] == 1
    assert policy["max_calibrator_fits_if_separately_granted"] == 1
    assert not policy["post_selection_refit"]
    assert rows[3]["qualified_ff2_count"] is None
    assert rows[3]["target_and_label_strictly_before"] == "2022-12-30T09:15:00+05:30"
    assert policy["historical_target_before"] == "2025-01-01"


def test_selected_source_matches_the_frozen_protocol_not_another_fold() -> None:
    policy = authority()
    protocol = (ROOT / policy["protocol_path"]).read_text()
    source = policy["source_model"]
    assert source["fold"] == 2022
    for key in ("model_fingerprint", "scaler_fingerprint", "training_run_fingerprint"):
        assert source[key] in protocol
    assert source["feature_order"] == [
        "ret_1",
        "ret_5",
        "sma20_distance",
        "realized_vol_20",
        "relative_volume",
    ]


def test_accrual_is_fixed_slots_not_results_or_success_count() -> None:
    policy = authority()["prospective"]
    assert policy["origin_slots"] == 500 and policy["replacement_slots"] == 0
    assert policy["whole_session_embargo"] == 1
    assert policy["stop_rule"] == "ALL_500_PREDECLARED_SLOTS_TERMINAL_AT_FIXED_DEADLINES"
    assert policy["sample_minima_checked"] == (
        "INSIDE_ONE_CONSUMED_FINAL_EVALUATION_NOT_AS_STOPPING_RULE"
    )
    assert (
        policy["minimum_common_pairs"],
        policy["minimum_per_class"],
        policy["minimum_coverage"],
        policy["minimum_complete_five_slot_blocks"],
    ) == (400, 80, 0.8, 40)
    assert policy["halves"] == [[1, 250], [251, 500]]
    assert (policy["minimum_half_pairs"], policy["minimum_half_per_class"]) == (150, 30)
    assert policy["candidate_freeze_reference"] is None and policy["frozen_at"] is None
    assert policy["final_execution"]["maximum"] == 1
    assert not policy["final_execution"]["authorized_now"]
    assert policy["final_execution"]["failure_after_claim"] == "CONSUMED_INCOMPLETE_NO_RETRY"


@pytest.mark.parametrize("field", ["model", "scaler", "feature_schema"])
def test_source_substitution_rejected(field: str) -> None:
    assert "SOURCE_PINS" in specification_reasons(witness(**{field: "substituted"}))


@pytest.mark.parametrize("field", ["candidate", "freeze_pin", "component_pin", "subject", "target"])
def test_freeze_substitution_rejected(field: str) -> None:
    assert "EXACT_FREEZE" in specification_reasons(witness(**{field: "substituted"}))


@pytest.mark.parametrize(
    "updates,reason",
    [
        ({"origin": "2025-06-02T15:30:00+05:30"}, "NOT_HISTORICAL"),
        ({"generated": "2027-01-04T15:30:00+05:30"}, "AFTER_FREEZE_EMBARGO"),
        ({"generated": "2027-01-05T16:00:00+05:30"}, "AFTER_FREEZE_EMBARGO"),
        ({"truth_available": "2027-01-06T16:00:00+05:30"}, "UNKNOWN_TRUTH"),
        ({"truth_available": "2027-01-06T16:01:00+05:30"}, "UNKNOWN_TRUTH"),
        ({"persisted": "2027-01-07T09:15:00+05:30"}, "TIMELY_CAPTURE"),
        ({"persisted": "2027-01-07T16:00:00+05:30"}, "TIMELY_CAPTURE"),
        ({"input_available": "2027-01-06T16:01:00+05:30"}, "PAST_ONLY_FEATURES"),
        ({"assessed": "2027-01-07T10:00:00+05:30"}, "MATURED"),
        ({"truth_available": None}, "TRUTH_DEADLINE"),
        ({"truth_available": "2027-01-14T15:30:01+05:30"}, "TRUTH_DEADLINE"),
        ({"source_kind": "FRESH_HISTORICAL_DOWNLOAD"}, "NOT_HISTORICAL"),
        ({"target_close": "2027-01-08T15:30:00+05:30"}, "UNIQUE_SLOT"),
        ({"calibrated_capture": "test-only:raw-1"}, "INTEGRITY_REPLAY"),
    ],
)
def test_negative_clock_and_provenance_cases(updates: dict[str, Any], reason: str) -> None:
    assert reason in specification_reasons(witness(**updates))


@pytest.mark.parametrize(
    "proof,reason",
    [
        ("integrity", "INTEGRITY_REPLAY"),
        ("recorded_replay", "INTEGRITY_REPLAY"),
        ("pinned_numeric_verifier", "INTEGRITY_REPLAY"),
        ("basis", "COMMON_BASIS"),
        ("calendar", "COMMON_BASIS"),
        ("actions", "COMMON_BASIS"),
        ("source_rights", "COMMON_BASIS"),
        ("no_early_exposure", "NO_EARLY_EXPOSURE"),
    ],
)
def test_missing_independent_proof_fails_closed(proof: str, reason: str) -> None:
    row = witness(passed_proofs=[p for p in witness().passed_proofs if p != proof])
    assert reason in specification_reasons(row)


def test_relabelling_old_source_and_duplicate_identity_do_not_qualify() -> None:
    row = witness(source_dataset=authority()["source"]["csv_sha256"])
    assert "NOT_HISTORICAL" in specification_reasons(row)
    row = witness(observation_id="renamed:observation")
    slots = ((row.subject, row.target, row.origin.isoformat()),)
    assert "UNIQUE_SLOT" in specification_reasons(row, previous_slots=slots)


def test_deterministic_offline_seal_roundtrip_and_aware_clocks() -> None:
    row = witness()
    assert specification_reasons(row) == ()
    restored = MetadataWitness.model_validate_json(canonical_json(row))
    assert restored == row and specification_reasons(restored) == ()
    assert isinstance(row.passed_proofs, tuple)
    assert isinstance(row.model_dump(mode="json")["passed_proofs"], list)
    utc = witness(generated="2027-01-06T10:30:00+00:00")
    assert utc == row and utc.fingerprint == row.fingerprint
    assert row.model_dump(mode="json")["generated"].endswith("+05:30")
    with pytest.raises(ValidationError):
        witness(generated="2027-01-06T16:00:00")
    with pytest.raises(ValidationError):
        row.candidate = "changed"
    bad = row.model_dump()
    bad["model"] = "tampered-without-resealing"
    with pytest.raises(ValidationError):
        MetadataWitness.model_validate(bad)
    with pytest.raises(ValidationError):
        witness(unknown_field="not-admitted")


def test_missing_forecast_record_cannot_be_constructed_as_a_valid_witness() -> None:
    payload = witness().model_dump(exclude={"fingerprint", "persisted"})
    with pytest.raises(ValidationError):
        MetadataWitness.model_validate(payload)
