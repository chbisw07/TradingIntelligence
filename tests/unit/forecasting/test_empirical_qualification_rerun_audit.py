"""Sanitized empirical gate audit; never load the private CSV or open holdout labels."""

import json
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tiaf.data.resolution import ResolutionResult
from tiaf.evaluation.forecast_research_contracts import (
    ResearchRightsConfig,
    RightsEvidenceStatus,
    SessionCalendarQualification,
    rights_admission,
)
from tiaf.evaluation.snapshot import validate_no_secrets
from tiaf.forecasting.identity import canonical_json, semantic_fingerprint
from tiaf.forecasting.research_contracts import FF1FeatureSchema

ROOT = Path(__file__).resolve().parents[3]
SEAL = "f30caf330ce5192a235d85d18629770d34b3b1547fac9f3dfdfdf5870210a2ed"
RECORD = ROOT / "docs/qualification_records/ff1_1a" / f"qualification_attempt_{SEAL}.json"


def audit() -> dict[str, Any]:
    return json.loads(RECORD.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def test_audit_seal_roundtrip_and_no_secret_fields() -> None:
    record = audit()
    validate_no_secrets(record)
    assert record["qualification_fingerprint"] == SEAL
    body = {k: v for k, v in record.items() if k != "qualification_fingerprint"}
    assert semantic_fingerprint(body) == SEAL
    assert semantic_fingerprint(json.loads(canonical_json(body))) == SEAL
    body["empirical_fitting_authorized"] = True
    assert semantic_fingerprint(body) != SEAL


def test_audit_is_hold_not_a_fabricated_native_qualification() -> None:
    record = audit()
    assert record["process_verdict"] == "HOLD_FF1_1A_QUALIFICATION"
    assert not record["empirical_fitting_authorized"]
    assert not record["runtime_contract"] and not record["qualification_executed"]
    assert record["no_fitting"]["native_empirical_qualifier_invocations"] == 0
    assert all(
        record["no_fitting"][field] == 0
        for field in (
            "logistic_fits", "scaler_fits", "model_artifacts", "learned_forecasts",
            "paired_metrics", "calibration", "provider_calls", "broker_calls",
        )
    )
    gates = {gate["gate"]: gate for gate in record["gates"]}
    assert not gates["rights_admission"]["blocking"]
    assert gates["pit_availability"]["blocking"]
    assert gates["calendar"]["blocking"]
    assert gates["corporate_actions_price_basis"]["blocking"]


def test_numeric_counts_are_not_scientific_observation_counts() -> None:
    record = audit()
    quality, population = record["bar_quality"], record["population"]
    assert quality["raw_rows"] == quality["valid_rows"] + quality["invalid_rows"] == 2045
    assert quality["invalid_rows"] == quality["duplicates"] == 0
    assert quality["invalid_reason_counts"] == {}
    assert population["supplied_reference_date_slots"] == 1983
    assert sum(population["raw_date_counts_by_year"].values()) == quality["raw_rows"]
    assert population["supplied_date_slots_blocked"] == 1983
    assert set(population["slot_reason_counts"].values()) == {1983}
    assert record["feature_derivation"]["feature_set_fingerprint"] is None
    assert record["leakage_audit"]["status"] == "HOLD"


@pytest.mark.parametrize(
    "field",
    [
        "qualified_rows", "requested_observations", "feature_eligible", "label_eligible",
        "paired_ready_observations", "excluded_observations", "positive_labels",
        "zero_labels", "unavailable_labels",
    ],
)
def test_unmeasured_populations_are_null_not_zero(field: str) -> None:
    assert audit()["population"][field] is None


def test_pinned_rights_and_current_identity_reconstruct_without_provider() -> None:
    record = audit()
    config = ResearchRightsConfig()
    admission, warnings = rights_admission(
        RightsEvidenceStatus.UNVERIFIED, config.rights_enforcement_policy
    )
    rights = record["rights"]
    assert rights["configuration_fingerprint"] == config.fingerprint
    assert rights["admission_result"] == admission.value == "ADMITTED_WITH_WARNING"
    assert rights["warnings"] == list(warnings)
    resolution = ResolutionResult.model_validate(record["security"]["current_resolution"])
    assert resolution.resolved is not None
    assert resolution.resolved.provider_instrument_id == "2885"
    assert resolution.resolved.instrument.symbol == "RELIANCE"
    assert resolution.observed_at.utcoffset() == timedelta(hours=5, minutes=30)
    assert semantic_fingerprint(resolution) == record["security"]["current_resolution_fingerprint"]
    assert record["security"]["historical_mapping"] == "UNKNOWN"


def test_holdout_and_fold_support_remain_unopened() -> None:
    record = audit()
    assert record["holdout"]["status"] == "SEALED"
    assert not record["holdout"]["outcomes_opened"]
    assert not record["holdout"]["price_return_or_class_summaries"]
    assert record["holdout"]["supplied_date_rows"] == 249
    for fold in record["fold_feasibility"]["folds"]:
        for field in (
            "training_observations", "test_observations", "purge_exclusions",
            "embargo_exclusions", "feature_complete", "label_complete",
            "paired_ready_potential", "baserate_support", "minimum_support_met",
        ):
            assert fold[field] is None
    assert record["labels"]["labels_constructed"] == 0


def test_missing_native_calendar_cannot_be_replaced_with_empty_schedule() -> None:
    with pytest.raises(ValidationError):
        SessionCalendarQualification.model_validate(
            {"state": "UNKNOWN", "schedules": [], "authority_refs": []}
        )
    schema = FF1FeatureSchema()
    assert schema.knowledge_policy == "CAPTURED_AS_KNOWN"
    assert schema.fingerprint == audit()["feature_derivation"]["schema_fingerprint"]
    assert not audit()["pit_policy"]["alternative_profile_adopted"]
