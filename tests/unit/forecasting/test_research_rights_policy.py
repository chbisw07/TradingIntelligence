"""FF-1.1A policy evolution: authored evidence only, never an empirical grant."""

import hashlib
import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from pydantic import ValidationError

from tiaf.evaluation.forecast_qualification import ResearchQualificationRuntime, qualify_dataset
from tiaf.evaluation.forecast_research_contracts import (
    EmpiricalDataset,
    EmpiricalDatasetQualification,
    ResearchRightsConfig,
)
from tiaf.evaluation.forecast_research_contracts import QualificationReason as R
from tiaf.evaluation.forecast_research_contracts import RightsAdmissionResult as A
from tiaf.evaluation.forecast_research_contracts import RightsEnforcementPolicy as P
from tiaf.evaluation.forecast_research_contracts import RightsEvidenceStatus as E
from tiaf.forecasting.identity import canonical_json, semantic_fingerprint

from ._research_support import ASSESSMENT, dataset, payload, repin_rights
from .test_research_qualification import report


@pytest.mark.parametrize(
    "policy,status,expected",
    [
        (P.ENFORCE, E.VERIFIED_ALLOWED, A.ADMITTED),
        (P.ENFORCE, E.UNVERIFIED, A.HOLD),
        (P.ENFORCE, E.AMBIGUOUS, A.HOLD),
        (P.ENFORCE, E.VERIFIED_DENIED, A.HOLD),
        (P.WARN_ONLY, E.VERIFIED_ALLOWED, A.ADMITTED),
        (P.WARN_ONLY, E.UNVERIFIED, A.ADMITTED_WITH_WARNING),
        (P.WARN_ONLY, E.AMBIGUOUS, A.ADMITTED_WITH_WARNING),
        (P.WARN_ONLY, E.VERIFIED_DENIED, A.HOLD),
        (P.DISABLED, E.VERIFIED_ALLOWED, A.NOT_ENFORCED),
        (P.DISABLED, E.UNVERIFIED, A.NOT_ENFORCED),
        (P.DISABLED, E.AMBIGUOUS, A.NOT_ENFORCED),
        (P.DISABLED, E.VERIFIED_DENIED, A.HOLD),
    ],
)
def test_admission_matrix_and_offline_reconstruction(policy: P, status: E, expected: A) -> None:
    data = payload()
    data["rights"]["model_training"] = status.value
    repin_rights(data)
    supplied = EmpiricalDataset.model_validate(data)
    before = supplied.fingerprint
    result = report(data, enforcement=policy)
    assert result.rights_evidence_status is status
    assert result.rights_enforcement_policy is policy
    assert result.rights_admission_result is expected
    assert bool(result.rights_warnings) == (expected is not A.ADMITTED)
    assert result.eligible_observations == (0 if expected is A.HOLD else 11)
    assert (R.RIGHTS_UNQUALIFIED in result.reasons) == (expected is A.HOLD)
    assert not result.empirical_fitting_authorized
    assert result.rights_ref == supplied.rights.reference
    assert supplied.fingerprint == before
    replay = EmpiricalDatasetQualification.model_validate_json(canonical_json(result))
    assert replay == result and replay.fingerprint == result.fingerprint
    assert isinstance(result.rights_warnings, tuple)
    assert isinstance(result.model_dump(mode="json")["rights_warnings"], list)


@pytest.mark.parametrize(
    "legacy,expected", [("UNKNOWN", E.UNVERIFIED), ("NOT_QUALIFIED", E.AMBIGUOUS)]
)
def test_legacy_assertions_are_preserved_not_relabelled_as_permission_or_denial(
    legacy: str, expected: E
) -> None:
    data = payload()
    data["rights"]["local_research"] = legacy
    repin_rights(data)
    supplied = EmpiricalDataset.model_validate(data)
    result = qualify_dataset(supplied, assessed_at=ASSESSMENT)
    assert supplied.rights.local_research.value == legacy
    assert result.rights_evidence_status is expected
    assert result.rights_admission_result is A.ADMITTED_WITH_WARNING
    assert result.eligible_observations == 11


@pytest.mark.parametrize("fault", ["missing_basis", "expired", "scope", "future_assessment"])
def test_unsubstantiated_legacy_allowed_claim_never_becomes_verified(fault: str) -> None:
    data = payload()
    if fault == "missing_basis":
        data["rights"]["basis_refs"] = []
    elif fault == "expired":
        data["rights"]["valid_until"] = "2022-01-01T00:00:00+05:30"
    elif fault == "scope":
        data["rights"]["coverage_start"] = "2021-02-01"
    else:
        data["rights"]["assessed_at"] = "2027-01-01T00:00:00+05:30"
    repin_rights(data)
    result = report(data)
    assert result.rights_evidence_status is not E.VERIFIED_ALLOWED
    assert result.rights_admission_result is A.ADMITTED_WITH_WARNING


@pytest.mark.parametrize("status", [E.VERIFIED_ALLOWED, E.VERIFIED_DENIED])
def test_explicit_verified_assertion_requires_referenced_basis(status: E) -> None:
    data = payload()
    data["rights"].update(model_training=status.value, basis_refs=[])
    with pytest.raises(ValidationError, match="VERIFIED_RIGHTS_BASIS_REQUIRED"):
        EmpiricalDataset.model_validate(data)


@pytest.mark.parametrize("fault", ["pin", "capture", "subject"])
@pytest.mark.parametrize("policy", [P.WARN_ONLY, P.DISABLED])
def test_rights_policy_cannot_bypass_evidence_identity(fault: str, policy: P) -> None:
    data = payload()
    if fault == "pin":
        data["source"]["rights_ref"]["fingerprint"] = "0" * 64
    else:
        if fault == "capture":
            data["rights"]["source_artifact"]["fingerprint"] = "0" * 64
        else:
            data["rights"]["subject"]["symbol"] = "HDFCBANK"
        repin_rights(data)
    result = report(data, enforcement=policy)
    assert R.PROVENANCE_UNQUALIFIED in result.reasons
    assert result.eligible_observations == 0


@pytest.mark.parametrize("policy", [P.WARN_ONLY, P.DISABLED])
@pytest.mark.parametrize("fault", ["provenance", "calendar", "security", "actions", "pit", "bar"])
def test_nonblocking_rights_cannot_bypass_scientific_gate(policy: P, fault: str) -> None:
    data = payload()
    data["rights"]["model_training"] = "UNKNOWN"
    repin_rights(data)
    if fault == "provenance":
        data["source"]["provenance_ref"] = None
    elif fault in ("calendar", "security"):
        data[fault]["state"] = "UNKNOWN"
    elif fault == "actions":
        data["actions"] = []
    elif fault == "bar":
        data["rows"][20]["close"] = "0"
    else:
        data["rows"][20]["provenance"]["admitted_at"] = ASSESSMENT.isoformat()
    result = report(data, enforcement=policy)
    assert result.rights_admission_result is not A.HOLD
    assert not result.observations[20].eligible
    assert result.reasons and R.RIGHTS_UNQUALIFIED not in result.reasons
    assert not result.empirical_fitting_authorized


def test_cold_default_frozen_owner_policy_identity_and_no_environment_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RIGHTS_ENFORCEMENT_POLICY", "ENFORCE")
    monkeypatch.setenv("TIAF_RIGHTS_ENFORCEMENT_POLICY", "DISABLED")
    config = ResearchRightsConfig()
    owner = ResearchQualificationRuntime(config)
    assert owner.config == config and owner.config is not config
    assert config.rights_enforcement_policy is P.WARN_ONLY
    with pytest.raises(ValidationError):
        config.rights_enforcement_policy = P.DISABLED
    with pytest.raises(FrozenInstanceError):
        owner.config = ResearchRightsConfig()  # type: ignore[misc]
    with pytest.raises(TypeError):
        owner.qualify(dataset(), assessed_at=ASSESSMENT, policy=P.DISABLED)  # type: ignore[call-arg]
    before = owner.qualify(dataset(), assessed_at=ASSESSMENT)
    with pytest.raises(ValidationError):
        before.rights_enforcement_policy = P.DISABLED
    assert owner.qualify(dataset(), assessed_at=ASSESSMENT) == before
    reports = [report(enforcement=p) for p in P]
    assert len({r.fingerprint for r in reports}) == 3
    assert len({r.rights_configuration_fingerprint for r in reports}) == 3
    # Rights policy cannot retune scientific values or create a different target.
    assert len({r.feature_set_fingerprint for r in reports}) == 1
    assert len({r.dataset_fingerprint for r in reports}) == 1
    forged = config.model_copy(update={"rights_enforcement_policy": "HOT"})
    with pytest.warns(UserWarning, match="serializer warnings"), pytest.raises(ValidationError):
        ResearchQualificationRuntime(forged)


@pytest.mark.parametrize(
    "field,value",
    [
        ("rights_enforcement_policy", "DISABLED"),
        ("rights_admission_result", "HOLD"),
        ("rights_warnings", []),
        ("rights_configuration_fingerprint", "0" * 64),
    ],
)
def test_reconstruction_checks_policy_even_without_outer_seal(field: str, value: object) -> None:
    data = payload()
    data["rights"]["model_training"] = "UNKNOWN"
    repin_rights(data)
    serialized = report(data).model_dump(mode="json")
    serialized.pop("fingerprint")
    serialized[field] = value
    with pytest.raises(ValidationError, match="RIGHTS_POLICY_MISMATCH"):
        EmpiricalDatasetQualification.model_validate(serialized)


def test_dataset_cannot_select_policy() -> None:
    data = payload()
    data["rights_enforcement_policy"] = "DISABLED"
    with pytest.raises(ValidationError):
        EmpiricalDataset.model_validate(data)


def test_prior_enforced_hold_is_byte_identical_and_sealed() -> None:
    docs = Path(__file__).resolve().parents[3] / "docs"
    fingerprint = "4f6d2a998b241ca04e99757791545315482606381af170ff61d1c948c977b833"
    audit = docs / "qualification_records" / "ff1_1a" / f"qualification_attempt_{fingerprint}.json"
    assert hashlib.sha256(audit.read_bytes()).hexdigest() == (
        "59be5223fc06dcdfb203f1e3a6ce0bfbd6d433804b31685ad9de2813cf54acee"
    )
    record = json.loads(audit.read_text(encoding="utf-8"))
    assert record.pop("qualification_fingerprint") == fingerprint
    assert semantic_fingerprint(record) == fingerprint
    prior_doc = docs / "TIAF_A7_FF1_1A_EMPIRICAL_DATA_RIGHTS_QUALIFICATION_EXECUTION.md"
    assert hashlib.sha256(prior_doc.read_bytes()).hexdigest() == (
        "4b65f4c88665f1198535e837d70aa199443e08e4ebb337260ae499cce7839c79"
    )
