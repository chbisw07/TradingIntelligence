"""Evidence-resolution guardrails; no private prices, live calls or model fitting."""

import json
from datetime import datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from tiaf.evaluation.snapshot import validate_no_secrets
from tiaf.forecasting.identity import canonical_json, exact_decimal, semantic_fingerprint
from tiaf.forecasting.research_contracts import FF1FeatureSchema

ROOT = Path(__file__).resolve().parents[3]
DIRECTORY = ROOT / "docs/qualification_records/ff1_1a"
RECORD = DIRECTORY / "evidence_resolution_20260921.json"
PREVIOUS = "f30caf330ce5192a235d85d18629770d34b3b1547fac9f3dfdfdf5870210a2ed"
SEAL = "0e6d8036f8429238a97859c65772b706aac108c0b80f4e58c30517abe5c2d2b8"


def audit() -> dict[str, Any]:
    return json.loads(RECORD.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def test_resolution_seal_roundtrip_and_no_secret_fields() -> None:
    record = audit()
    validate_no_secrets(record)
    assert record.pop("evidence_resolution_fingerprint") == SEAL
    assert semantic_fingerprint(record) == SEAL
    assert semantic_fingerprint(json.loads(canonical_json(record))) == SEAL


@pytest.mark.parametrize("section", [
    "vintage_policy_proposal", "calendar_evidence", "historical_identity",
])
def test_each_versioned_assessment_has_an_independent_pin(section: str) -> None:
    value = audit()[section]
    fingerprint = value.pop("fingerprint")
    assert value["version"] == "1.0"
    assert semantic_fingerprint(value) == fingerprint


def test_fresh_vintage_proposal_is_not_current_ff1_or_operational_admission() -> None:
    policy = audit()["vintage_policy_proposal"]
    assert policy["adoption_status"] == "NOT_ADOPTED_FOR_CURRENT_FF1"
    assert policy["source_vintage"] == "FRESH_HISTORICAL_DOWNLOAD"
    assert policy["historical_capture_claim"] == "NONE"
    assert policy["realization_mode"] == "SIMULATED"
    assert policy["revised_history_exploration"] == "CONDITIONAL_SEPARATE_PROFILE_ONLY"
    assert not any(policy[field] for field in (
        "runtime_enabled", "operational_replay_eligible", "historical_pit_qualified",
        "current_ff1_training_eligible", "current_ff1_evaluation_eligible",
        "empirical_fitting_authorized",
    ))


@pytest.mark.parametrize("field,value", [
    ("historical_capture_claim", "CAPTURED_AS_KNOWN"),
    ("runtime_enabled", True),
    ("availability_evidence", "OBSERVED"),
    ("information_cutoff_offset_minutes", 0),
    ("current_ff1_training_eligible", True),
])
def test_scope_or_assumption_change_cannot_reuse_policy_fingerprint(
    field: str, value: object,
) -> None:
    policy = audit()["vintage_policy_proposal"]
    fingerprint = policy.pop("fingerprint")
    policy[field] = value
    assert semantic_fingerprint(policy) != fingerprint


@pytest.mark.parametrize("policy", ["FRESH_HISTORICAL_DOWNLOAD", "CONSERVATIVE_EOD_SIMULATION"])
def test_proposal_does_not_silently_change_native_knowledge_policy(policy: str) -> None:
    schema = FF1FeatureSchema()
    assert schema.knowledge_policy == "CAPTURED_AS_KNOWN"
    previous = json.loads((DIRECTORY / f"qualification_attempt_{PREVIOUS}.json").read_text())
    assert schema.fingerprint == previous["feature_derivation"]["schema_fingerprint"]
    with pytest.raises(ValidationError):
        FF1FeatureSchema.model_validate({**schema.model_dump(), "knowledge_policy": policy})


def test_assumed_availability_does_not_backdate_actual_acquisition() -> None:
    record = audit()
    policy = record["vintage_policy_proposal"]
    assert policy["availability_evidence"] == "ASSUMED_CONSERVATIVE_POLICY"
    assert not policy["provider_publication_sla_verified"]
    assert policy["information_cutoff_offset_minutes"] == 30
    assert policy["simulated_as_of_offset_minutes"] == 5
    assert policy["simulated_as_of_must_precede_next_target_open"]
    assert policy["actual_acquisition_must_be_preserved"]
    acquired = datetime.fromisoformat(record["dataset"]["acquired_at"])
    assert acquired.year == 2026
    assert acquired == acquired.astimezone(ZoneInfo("Asia/Kolkata"))
    assert acquired.utcoffset() == timedelta(hours=5, minutes=30)


def test_exact_decimal_companion_pattern_preserves_value_without_float() -> None:
    # Illustrative transport bytes, NOT a recovery of the empirical source.
    raw = '{"close":[100.0000000000000001,100.0000000000000002]}'
    values = json.loads(raw, parse_float=Decimal)["close"]
    assert values == [exact_decimal("100.0000000000000001"),
                      exact_decimal("100.0000000000000002")]
    assert semantic_fingerprint(values[0]) != semantic_fingerprint(values[1])
    assert json.loads(canonical_json(values)) == [
        "100.0000000000000001", "100.0000000000000002",
    ]


def test_float_roundtrip_is_not_a_general_invariance_proof() -> None:
    # A synthetic counterexample only; no empirical labels/features are inspected.
    first = "100.0000000000000001"
    second = "100.0000000000000002"
    assert Decimal(first) < Decimal(second)
    assert float(first) == float(second)
    assert sha256(first.encode()).digest() != sha256(second.encode()).digest()
    decimal = audit()["decimal"]
    assert not decimal["invariance_proven"] and not decimal["tolerance_route_used"]
    assert decimal["new_decimal_artifact"] is None


@pytest.mark.parametrize("value", [100.1, True, float("nan")])
def test_normalized_values_cannot_claim_native_source_decimal_authority(value: object) -> None:
    with pytest.raises(ValueError):
        exact_decimal(value)


@pytest.mark.parametrize("holiday", ["2018-01-26", "2024-01-26"])
def test_known_holidays_preserved_in_scoped_evidence(holiday: str) -> None:
    calendar = audit()["calendar_evidence"]
    assert holiday in calendar["declared_closed_dates"]
    assert calendar["date_only_check"]["supplied_on_declared_closed_dates"] == []


@pytest.mark.parametrize("special", ["2018-11-07", "2024-11-01"])
def test_muhurat_session_is_not_misclassified_as_a_full_day_closure(special: str) -> None:
    calendar = audit()["calendar_evidence"]
    fact = next(f for f in calendar["special_session_facts"] if f["date"] == special)
    assert special not in calendar["declared_closed_dates"]
    assert fact["supplied"] and fact["open_at"] is None and fact["close_at"] is None


@pytest.mark.parametrize("field", [
    "expected_sessions_full_range", "missing_sessions_full_range", "extra_sessions_full_range",
])
def test_unmeasured_calendar_totals_are_null_not_zero(field: str) -> None:
    calendar = audit()["calendar_evidence"]
    assert not calendar["complete"]
    assert calendar["date_only_check"][field] is None
    assert not calendar["date_only_check"]["known_subset_pass_is_full_calendar_pass"]


def test_weekend_rows_remain_unresolved_not_automatically_extra() -> None:
    calendar = audit()["calendar_evidence"]
    assert len(calendar["unresolved_weekend_row_dates"]) == 8
    assert "2024-01-20" in calendar["unresolved_weekend_row_dates"]
    assert calendar["january_2024_crosscheck"]["supplied_january_20"]
    assert not calendar["january_2024_crosscheck"]["supplied_january_22"]


def test_documented_adjusted_basis_does_not_change_unadjusted_target() -> None:
    actions = audit()["corporate_actions"]
    assert actions["price_basis_verdict"] == "ADJUSTED"
    assert actions["accepted_target_basis"] == "UNADJUSTED_COMPLETED_CLOSE"
    assert actions["strategy"] == "C_HOLD"
    assert not actions["accepted_target_compatible"] and not actions["actions_complete"]
    assert actions["active_exclusion_policy"] is None and actions["exclusions_applied"] == 0
    bonus = next(a for a in actions["actions"] if a["kind"] == "BONUS")
    assert bonus["record_date"] == "2024-10-28" and bonus["ex_date"] is None


def test_identity_checkpoints_do_not_invent_effective_provider_mapping() -> None:
    identity = audit()["historical_identity"]
    assert identity["isin"] == "INE002A01018"
    assert identity["checkpoint_consistency"] == "CORROBORATED"
    assert identity["continuity_verdict"].startswith("HOLD_")
    assert identity["qualified_historical_effective_from"] is None
    assert identity["qualified_historical_effective_until"] is None
    mapping = identity["provider_security_ids"][0]
    assert mapping["id"] == "2885" and mapping["historical_effective_from"] is None


def test_holdout_is_sealed_and_only_dates_were_checked() -> None:
    holdout = audit()["holdout"]
    assert holdout["year"] == 2025 and holdout["status"] == "SEALED"
    assert holdout["date_only_operations"] and not holdout["outcomes_opened"]
    assert not holdout["feature_label_or_performance_inspection"]


def test_resolution_hold_is_not_qualification_or_fitting_authority() -> None:
    record = audit()
    assert record["process_verdict"] == "HOLD_EVIDENCE_RESOLUTION"
    assert not record["ready_for_empirical_qualification_rerun"]
    assert not record["empirical_fitting_authorized"] and not record["runtime_contract"]
    assert all(value == 0 for value in record["execution"].values())
    gates = {gate["gate"]: gate for gate in record["gates"]}
    assert not gates["rights_admission"]["blocking"]
    assert not gates["dataset_integrity"]["blocking"]
    assert sum(gate["blocking"] for gate in gates.values()) == 6


def test_sources_distinguish_local_byte_pins_from_web_only_excerpts() -> None:
    record = audit()
    sources = {s["id"]: s for s in record["sources"]}
    assert len(sources) == len(record["sources"])
    retained = [s for s in sources.values() if s["local_path"] is not None]
    assert len(retained) == record["source_retention"]["byte_pinned_local_blobs"] == 3
    for source in sources.values():
        assert source["url"].startswith("https://")
        assert (source["sha256"] is None) == (source["local_path"] is None)
    for action in record["corporate_actions"]["actions"]:
        assert action["source_ref"] in sources


def test_previous_qualification_is_preserved_not_rewritten_by_new_basis_evidence() -> None:
    previous = json.loads((DIRECTORY / f"qualification_attempt_{PREVIOUS}.json").read_text())
    assert previous.pop("qualification_fingerprint") == PREVIOUS
    assert semantic_fingerprint(previous) == PREVIOUS
    assert previous["dataset"]["price_basis"] == "UNKNOWN"
    assert previous["process_verdict"] == "HOLD_FF1_1A_QUALIFICATION"
    assert audit()["previous_qualification_fingerprint"] == PREVIOUS
