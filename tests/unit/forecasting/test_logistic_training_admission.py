"""Reuse native synthetic adjusted qualification; never read private empirical rows."""

from datetime import timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest

from tiaf.evaluation.forecast_qualification import ResearchQualificationRuntime
from tiaf.evaluation.forecast_retrospective_contracts import RetrospectiveQualification
from tiaf.forecasting.research_contracts import AdjustedResearchProfile
from tiaf.learning.forecast_artifacts import TrainingGrant
from tiaf.learning.forecast_training import (
    load_qualification,
    prepare_training,
    validate_qualification,
)

from .test_adjusted_retrospective_research import AT, dataset
from .test_logistic_training import grant


@pytest.fixture(scope="module")
def qualification() -> RetrospectiveQualification:
    return ResearchQualificationRuntime(
        retrospective_profile=AdjustedResearchProfile()
    ).qualify_retrospective(dataset(full=True), assessed_at=AT)


def bound(q: RetrospectiveQualification, **updates: Any) -> TrainingGrant:
    return TrainingGrant.model_validate(
        {
            **grant().model_dump(exclude={"fingerprint"}),
            "qualification_fingerprint": q.fingerprint,
            "dataset_fingerprint": q.dataset_fingerprint,
            "research_profile_fingerprint": q.profile.fingerprint,
            "feature_schema_fingerprint": q.feature_schema.fingerprint,
            "issued_at": AT,
            **updates,
        }
    )


@pytest.mark.parametrize(
    "pin,reason",
    [
        ("qualification_fingerprint", "QUALIFICATION_STALE_OR_MISMATCH"),
        ("dataset_fingerprint", "DATASET_FINGERPRINT_MISMATCH"),
        ("research_profile_fingerprint", "RESEARCH_PROFILE_MISMATCH"),
        ("feature_schema_fingerprint", "FEATURE_SCHEMA_MISMATCH"),
    ],
)
def test_pinned_admission(qualification: RetrospectiveQualification, pin: str, reason: str) -> None:
    with pytest.raises(ValueError, match=reason):
        validate_qualification(qualification, bound(qualification, **{pin: "0" * 64}))


def test_authorization_required(qualification: RetrospectiveQualification) -> None:
    q = RetrospectiveQualification.model_validate(
        {
            **qualification.model_dump(exclude={"fingerprint"}),
            "empirical_fitting_authorized": False,
            "blocking_reasons": ["TEST_NOT_AUTHORIZED"],
        }
    )
    with pytest.raises(ValueError, match="EMPIRICAL_FITTING_NOT_AUTHORIZED"):
        prepare_training(q, bound(q), 2021)


@pytest.mark.parametrize("year", [2021, 2022, 2023, 2024])
def test_exact_fold_and_exclusion_accounting(
    qualification: RetrospectiveQualification, year: int
) -> None:
    request = prepare_training(qualification, bound(qualification), year)
    fold = next(f for f in qualification.folds if f.test_year == year)
    assert request.manifest.observation_ids == fold.train_ids
    assert request.manifest.audit.train == len(fold.train_ids)
    assert request.manifest.audit.positive == fold.train_positive
    assert request.manifest.audit.purge_only + request.manifest.audit.embargo == len(
        fold.purged_ids
    )
    assert request.manifest.audit.embargo == 1
    assert request.manifest.audit.sealed == 250
    assert not set(request.manifest.observation_ids).intersection(fold.test_ids)
    assert all(
        r.target_date.year < 2025 and r.label_available_at < fold.fit_cutoff for r in request.rows
    )
    assert all(r.reference_date < fold.embargo_date for r in request.rows)
    assert "ff1-adjusted:RELIANCE:2024-12-31" not in request.manifest.observation_ids


def test_no_holdout_fit(qualification: RetrospectiveQualification) -> None:
    with pytest.raises(ValueError, match="HOLDOUT_NOT_AUTHORIZED"):
        prepare_training(qualification, bound(qualification), 2025)


def test_guard_mutated_seal_and_unsealed_protected_row(
    qualification: RetrospectiveQualification,
) -> None:
    dump = qualification.model_dump(exclude={"fingerprint"})
    dump["audit"] = {**dump["audit"], "holdout_status": "OPEN"}
    changed = RetrospectiveQualification.model_validate(dump)
    with pytest.raises(ValueError, match="HOLDOUT_POLICY_MISMATCH"):
        validate_qualification(changed, bound(changed))
    dump = qualification.model_dump(exclude={"fingerprint"})
    # Contradictory protected status, without fabricating any protected outcome.
    dump["observations"][-1]["label_state"] = "UNAVAILABLE"
    changed = RetrospectiveQualification.model_validate(dump)
    with pytest.raises(ValueError, match="HOLDOUT_NOT_AUTHORIZED"):
        validate_qualification(changed, bound(changed))


def test_only_train_values_enter_worker(qualification: RetrospectiveQualification) -> None:
    original = prepare_training(qualification, bound(qualification), 2021)
    # A later unsealed feature being unavailable cannot affect earlier training.
    dump = qualification.model_dump(exclude={"fingerprint"})
    next(o for o in dump["observations"] if o["reference_date"] == "2023-01-03")["features"] = None
    changed = RetrospectiveQualification.model_validate(dump)
    later = prepare_training(changed, bound(changed), 2021)
    assert original.rows == later.rows
    assert original.manifest.scientific_fingerprint == later.manifest.scientific_fingerprint


def test_grant_cannot_predate_qualification(qualification: RetrospectiveQualification) -> None:
    with pytest.raises(ValueError, match="QUALIFICATION_POSTDATES_GRANT"):
        validate_qualification(
            qualification, bound(qualification, issued_at=AT - timedelta(days=1))
        )


def test_loader_verifies_bytes_before_decode(tmp_path: Path) -> None:
    path = tmp_path / "qualification.json"
    path.write_bytes(b"MUST_NOT_DECODE_UNAPPROVED_BYTES")
    with pytest.raises(ValueError, match="QUALIFICATION_BLOB_MISMATCH"):
        load_qualification(path, blob_sha256="0" * 64, dataset=path, grant=grant())
    with pytest.raises(ValueError, match="DATASET_FINGERPRINT_MISMATCH"):
        load_qualification(
            path, blob_sha256=sha256(path.read_bytes()).hexdigest(), dataset=path, grant=grant()
        )


def test_loader_missing_or_symlink_refused(tmp_path: Path) -> None:
    missing = tmp_path / "absent"
    with pytest.raises(ValueError, match="REGULAR_LOCAL_ARTIFACT_REQUIRED"):
        load_qualification(missing, blob_sha256="0" * 64, dataset=missing, grant=grant())
    link = tmp_path / "link"
    link.symlink_to(missing)
    with pytest.raises(ValueError, match="REGULAR_LOCAL_ARTIFACT_REQUIRED"):
        load_qualification(link, blob_sha256="0" * 64, dataset=missing, grant=grant())
