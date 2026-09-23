"""FF-2.3 denial/custody review; authored metadata only, no market p/q/y."""

import json
import socket
import subprocess
from datetime import UTC, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tiaf.forecasting.identity import ArtifactReference, semantic_fingerprint
from tiaf.learning.empirical_authority import (
    DevelopmentCustodyMetadata,
    EmpiricalAuthorityResolution,
    EmpiricalSourcePins,
    require_empirical_development_authority,
    review_development_metadata,
)

ROOT = Path(__file__).resolve().parents[3]
RECORD = ROOT / "docs/qualification_records/ff2_3/authority_resolution.json"


def resolution() -> EmpiricalAuthorityResolution:
    return EmpiricalAuthorityResolution.model_validate_json(RECORD.read_bytes())


def ref(name: str) -> ArtifactReference:
    return ArtifactReference(
        artifact_id=f"test-only:{name}",
        artifact_version="1.0",
        fingerprint=semantic_fingerprint(name),
    )


def row(**updates: Any) -> DevelopmentCustodyMetadata:
    authority = resolution()
    values: dict[str, Any] = {
        "observation_id": "test-only:origin-one",
        "experiment_id": authority.experiment_id,
        "subject": authority.source.subject,
        "target": authority.source.target,
        "horizon": "NEXT_SESSION_CLOSE",
        "purpose": "CALIBRATION",
        "exposure": "KNOWN_DEVELOPMENT",
        "source": authority.source,
        "origin": "2022-06-01T15:30:00+05:30",
        "information_cutoff": "2022-06-01T16:00:00+05:30",
        "target_open": "2022-06-02T09:15:00+05:30",
        "target_close": "2022-06-02T15:30:00+05:30",
        "feature_available_as_of": "2022-06-01T15:45:00+05:30",
        "feature_dependency_clocks": ["2022-05-31T15:30:00+05:30"],
        "feature_capture": ref("features"),
        "raw_capture": ref("raw"),
        "generated_at": "2026-09-23T12:00:00+05:30",
        "persisted_at": "2026-09-23T12:01:00+05:30",
        "generation_code": semantic_fingerprint("test-only:code"),
        "expected_generation_code": semantic_fingerprint("test-only:code"),
        "journal_entry": ref("truth"),
        "expected_journal_entry": ref("truth"),
        "journal_revision": 1,
        "expected_journal_revision": 1,
        "truth_observation_id": "test-only:origin-one",
        "truth_subject": authority.source.subject,
        "truth_target": authority.source.target,
        "truth_target_open": "2022-06-02T09:15:00+05:30",
        "truth_target_close": "2022-06-02T15:30:00+05:30",
        "truth_available_as_of": "2022-06-02T16:00:00+05:30",
        "truth_recorded_at": "2026-09-23T12:00:00+05:30",
        "assessed_at": "2026-09-23T13:00:00+05:30",
    }
    values.update(updates)
    return DevelopmentCustodyMetadata.model_validate(values)


def test_sealed_resolution_not_a_grant() -> None:
    value = resolution()
    assert value.fingerprint == "15a8fb667ad5ec793c737de929cebea5de0c281687c83316fa1e5bfef4ceb8ec"
    assert EmpiricalAuthorityResolution.model_validate_json(value.model_dump_json()) == value
    assert value.empirical_grant is None
    assert value.max_executions_now == 0
    assert value.calibration_2022 == value.validation_2023_2024 == "UNVERIFIABLE"
    assert value.reasons and not value.empirical_execution_allowed
    assert (
        sha256(
            (ROOT / "docs/TIAF_A7_FF2_0_CALIBRATED_LOGISTIC_RESEARCH_PROTOCOL.md").read_bytes()
        ).hexdigest()
        == value.protocol_bytes
    )
    parent = json.loads(
        (ROOT / "docs/qualification_records/ff2_1/data_use_authority.json").read_text()
    )
    assert parent["fingerprint"] == value.parent_authority
    assert parent["source_model"]["model_fingerprint"] == value.source.model
    assert parent["source_model"]["scaler_fingerprint"] == value.source.scaler
    assert parent["source_model"]["feature_schema_fingerprint"] == value.source.feature_schema
    assert parent["source"]["csv_sha256"] == value.source.dataset_bytes


def test_consistent_metadata_is_still_denied() -> None:
    reviewed = review_development_metadata(resolution(), (row(),))
    assert reviewed.reasons == (
        "FF2_EMPIRICAL_AUTHORITY_NOT_GRANTED",
        "ARTIFACT_DERIVED_QUALIFICATION_REQUIRED",
    )
    assert not reviewed.admitted and not reviewed.numeric_access_allowed
    with pytest.raises(ValueError, match="FF2_EMPIRICAL_AUTHORITY_NOT_GRANTED"):
        require_empirical_development_authority(resolution())


@pytest.mark.parametrize("year", [2023, 2024])
def test_known_validation_metadata_also_denied(year: int) -> None:
    data = row().model_dump(exclude={"fingerprint"})
    for key in (
        "origin",
        "information_cutoff",
        "target_open",
        "target_close",
        "feature_available_as_of",
        "truth_target_open",
        "truth_target_close",
        "truth_available_as_of",
    ):
        data[key] = data[key].replace(year=year)
    data["feature_dependency_clocks"] = [data["origin"] - timedelta(days=1)]
    data["purpose"] = "VALIDATION"
    result = review_development_metadata(resolution(), (DevelopmentCustodyMetadata(**data),))
    assert len(result.reasons) == 2
    assert not result.admitted


@pytest.mark.parametrize(
    "field,value",
    [
        ("calibration_2022", "GRANTED"),
        ("validation_2023_2024", "GRANTED"),
        ("empirical_grant", ref("grant")),
        ("empirical_execution_allowed", True),
        ("prospective_collection_allowed", True),
        ("protected_evaluation_allowed", True),
        ("promotion_allowed", True),
        ("max_executions_now", 1),
    ],
)
def test_no_self_authorization(field: str, value: object) -> None:
    forged = resolution().model_copy(update={field: value, "fingerprint": None})
    with pytest.raises(ValidationError):
        require_empirical_development_authority(forged)


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("experiment_id", "test-only:wrong", "EXPERIMENT_MISMATCH"),
        ("target", "test-only:wrong", "SUBJECT_TARGET_HORIZON_MISMATCH"),
        ("subject", "OTHER", "SUBJECT_TARGET_HORIZON_MISMATCH"),
        ("horizon", "FIVE_SESSIONS", "SUBJECT_TARGET_HORIZON_MISMATCH"),
        ("purpose", "PROTECTED", "WRONG_PERIOD_OR_PURPOSE"),
        ("purpose", "VALIDATION", "WRONG_PERIOD_OR_PURPOSE"),
        ("exposure", "CONSUMED", "PROTECTED_OR_UNKNOWN_EXPOSURE"),
        ("exposure", "PROSPECTIVE", "PROTECTED_OR_UNKNOWN_EXPOSURE"),
        ("exposure", "UNKNOWN", "PROTECTED_OR_UNKNOWN_EXPOSURE"),
        ("origin", "2021-06-01T15:30:00+05:30", "TRAINING_OR_SCALER_OVERLAP"),
        ("origin", "2025-06-01T15:30:00+05:30", "PROHIBITED_HISTORICAL_DEPENDENCY"),
        ("origin", "2026-01-01T15:30:00+05:30", "PROHIBITED_HISTORICAL_DEPENDENCY"),
        ("origin", "2027-06-01T15:30:00+05:30", "WRONG_PERIOD_OR_PURPOSE"),
        ("target_close", "2025-01-01T15:30:00+05:30", "PROHIBITED_HISTORICAL_DEPENDENCY"),
        (
            "feature_dependency_clocks",
            ["2025-01-01T15:30:00+05:30"],
            "PROHIBITED_HISTORICAL_DEPENDENCY",
        ),
        (
            "support_dependency_clocks",
            ["2026-01-01T15:30:00+05:30"],
            "PROHIBITED_HISTORICAL_DEPENDENCY",
        ),
        ("feature_dependency_clocks", ["2022-06-02T15:30:00+05:30"], "FEATURE_OR_TEMPORAL_LEAKAGE"),
        ("feature_available_as_of", "2022-06-03T15:30:00+05:30", "FEATURE_OR_TEMPORAL_LEAKAGE"),
        (
            "truth_available_as_of",
            "2022-12-30T09:15:00+05:30",
            "CALIBRATION_EMBARGO_OR_LABEL_LEAKAGE",
        ),
        ("truth_available_as_of", "2022-06-01T15:30:00+05:30", "IMMATURE_TRUTH"),
        ("generated_at", "2022-06-01T16:00:00+05:30", "BACKDATED_ACTUAL_CLOCK"),
        ("truth_recorded_at", "2022-06-02T16:00:00+05:30", "BACKDATED_ACTUAL_CLOCK"),
        ("truth_observation_id", "test-only:wrong", "GROUND_TRUTH_JOIN_MISMATCH"),
        ("truth_subject", "OTHER", "GROUND_TRUTH_JOIN_MISMATCH"),
        ("truth_target", "test-only:wrong", "GROUND_TRUTH_JOIN_MISMATCH"),
        ("truth_target_close", "2022-06-03T15:30:00+05:30", "GROUND_TRUTH_JOIN_MISMATCH"),
        ("journal_revision", 2, "JOURNAL_REVISION_MISMATCH"),
        ("journal_entry", ref("changed-truth"), "JOURNAL_REVISION_MISMATCH"),
        ("regenerated_capture", ref("changed-raw"), "REGENERATION_IDENTITY_MISMATCH"),
        ("generation_code", semantic_fingerprint("changed-code"), "REGENERATION_IDENTITY_MISMATCH"),
        ("qualification_status", "REJECTED", "CUSTODY_STATUS_REJECTED"),
    ],
)
def test_metadata_rejection(field: str, value: object, reason: str) -> None:
    result = review_development_metadata(resolution(), (row(**{field: value}),))
    assert reason in result.reasons
    assert not result.admitted


@pytest.mark.parametrize(
    "field",
    [
        "model",
        "model_bytes",
        "scaler",
        "scaler_bytes",
        "feature_schema",
        "training_run",
        "training_manifest",
        "dataset_bytes",
        "qualification",
        "qualification_bytes",
        "profile",
        "source_manifest",
    ],
)
def test_source_pin_substitution(field: str) -> None:
    changed = resolution().source.model_dump(exclude={"fingerprint"})
    changed[field] = semantic_fingerprint("substitution")
    result = review_development_metadata(
        resolution(), (row(source=EmpiricalSourcePins(**changed)),)
    )
    assert "SOURCE_IDENTITY_OR_BYTES_MISMATCH" in result.reasons


@pytest.mark.parametrize("rename", [False, True])
def test_duplicate_admission_and_relabel(rename: bool) -> None:
    second = (
        row(observation_id="test-only:renamed", truth_observation_id="test-only:renamed")
        if rename
        else row()
    )
    result = review_development_metadata(resolution(), (row(), second))
    assert "DUPLICATE_OBSERVATION_OR_CAPTURE" in result.reasons


def test_forged_and_tampered_records_revalidated() -> None:
    forged = row().model_copy(update={"target": "test-only:tampered"})
    with pytest.raises(ValidationError, match="FINGERPRINT_MISMATCH"):
        review_development_metadata(resolution(), (forged,))
    data = json.loads(RECORD.read_text())
    data["source"]["model"] = "0" * 64
    with pytest.raises(ValidationError, match="FINGERPRINT_MISMATCH"):
        EmpiricalAuthorityResolution.model_validate(data)


def test_cannot_smuggle_probability_label_or_grant_into_metadata() -> None:
    for key in ("raw_probability", "label", "empirical_grant", "verified"):
        with pytest.raises(ValidationError):
            row(**{key: 1})


def test_immutable_json_and_timezone() -> None:
    value = row()
    assert isinstance(value.feature_dependency_clocks, tuple)
    dumped = value.model_dump(mode="json")
    assert isinstance(dumped["feature_dependency_clocks"], list)
    assert dumped["origin"].endswith("+05:30")
    assert DevelopmentCustodyMetadata.model_validate(dumped) == value
    assert row(origin=value.origin.astimezone(UTC)) == value
    with pytest.raises(ValidationError):
        value.origin = value.origin + timedelta(days=1)
    with pytest.raises(AttributeError):
        getattr(value.feature_dependency_clocks, "append")(value.origin)
    with pytest.raises(ValidationError):
        row(origin=value.origin.replace(tzinfo=None))


@pytest.mark.parametrize("n", [0, 4097])
def test_bounded_review(n: int) -> None:
    with pytest.raises(ValueError, match="RECORD_BOUND"):
        review_development_metadata(resolution(), (row(),) * n)


def test_review_and_denial_need_no_numeric_or_external_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authority, proposal = resolution(), row()

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("forbidden side effect")

    monkeypatch.setattr("builtins.open", forbidden)
    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    first = review_development_metadata(authority, (proposal,))
    assert review_development_metadata(authority, (proposal,)) == first
    with pytest.raises(ValueError, match="FF2_EMPIRICAL_AUTHORITY_NOT_GRANTED"):
        require_empirical_development_authority(authority)
