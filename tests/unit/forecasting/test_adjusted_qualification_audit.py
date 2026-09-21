"""Sanitized empirical result seals; private prices and holdout outcomes not required."""

import json
from pathlib import Path
from typing import Any

import pytest

from tiaf.evaluation.snapshot import validate_no_secrets
from tiaf.forecasting.identity import semantic_fingerprint
from tiaf.forecasting.research_contracts import AdjustedFF1FeatureSchema, AdjustedResearchProfile

DIRECTORY = Path(__file__).resolve().parents[3] / "docs/qualification_records/ff1_1a"
SEAL = "2432d79c8892c8942f0f35dfd13dee8a461cefd1622dc16d53d91908339ece72"


def audit() -> dict[str, Any]:
    return json.loads((DIRECTORY / "adjusted_qualification_20260921.json").read_text())  # type: ignore[no-any-return]


def test_empirical_summary_sealed_and_private_market_rows_absent() -> None:
    record = audit()
    assert record.pop("report_fingerprint") == SEAL
    assert semantic_fingerprint(record) == SEAL
    assert "observations" not in record and "rows" not in record
    validate_no_secrets(record)
    assert record["qualification_fingerprint"] == (
        "4b021081c3f5ee1afa3ff389f754ce91920fa45a367d4c88064330a0d1999d51"
    )


def test_review_and_profile_exactly_bound() -> None:
    record = audit()
    review = json.loads((DIRECTORY / "adjusted_research_review_20260921.json").read_text())
    assert semantic_fingerprint(review) == record["review_fingerprint"]
    profile = AdjustedResearchProfile.model_validate(record["profile"])
    assert profile.fingerprint == record["profile_fingerprint"]
    assert (
        AdjustedFF1FeatureSchema(profile=profile).fingerprint
        == record["feature_schema_fingerprint"]
    )
    assert record["dataset_fingerprint"] == review["expected_files"]["reliance_daily_ohlcv.csv"]


def test_empirical_population_accounting_does_not_treat_sealed_as_negative() -> None:
    summary = audit()["audit"]
    assert (
        summary["requested"]
        == 1983
        == summary["unsealed_requested"] + summary["holdout_structural"]
    )
    assert summary["unsealed_requested"] == 1734
    assert summary["feature_eligible"] == 1694
    assert summary["label_eligible"] == 1731 == summary["positive"] + summary["zero"]
    assert (summary["positive"], summary["zero"]) == (900, 831)
    assert summary["paired_ready_potential"] == 1691
    assert summary["label_unavailable"] == 2
    assert summary["label_sealed"] == 250  # 249 holdout origins plus final 2024 target.
    assert (
        summary["label_eligible"] + summary["label_unavailable"] + summary["label_sealed"] == 1983
    )


@pytest.mark.parametrize(
    "year,train,test,paired",
    [
        (2021, 720, 248, 248),
        (2022, 968, 248, 248),
        (2023, 1216, 246, 225),
        (2024, 1441, 249, 248),
        (2025, 1690, 249, None),
    ],
)
def test_empirical_fold_summary(year: int, train: int, test: int, paired: int | None) -> None:
    fold = next(f for f in audit()["folds"] if f["test_year"] == year)
    assert (fold["train_count"], fold["test_count"], fold["paired_potential_count"]) == (
        train,
        test,
        paired,
    )
    assert fold["train_positive"] + fold["train_zero"] == train
    assert fold["purge_count"] == 2 and fold["baseline_support_eligible"] == 20
    assert not fold["blocking_reasons"]
    if year == 2025:
        assert all(
            fold[name] is None
            for name in (
                "test_positive",
                "test_zero",
                "test_feature_complete",
                "test_label_complete",
                "complete_five_session_blocks",
            )
        )


def test_numeric_and_replay_boundaries_not_overclaimed() -> None:
    record = audit()
    summary = record["audit"]
    assert summary["maximum_feature_perturbation"] < 1e-8
    assert summary["minimum_gap_over_perturbation_envelope"] > 5e9
    assert summary["equal_normalized_close_labels"] == 1
    assert summary["feature_nonfinite"] == 0
    assert not record["profile"]["source_forensic_eligible"]
    assert not record["profile"]["operational_replay_eligible"]
    assert summary["rights_status"] == "UNVERIFIED"
    assert summary["rights_policy"] == "WARN_ONLY"
    assert summary["rights_admission"] == "ADMITTED_WITH_WARNING"
    assert record["empirical_fitting_authorized"] is True
    assert all(
        summary[name] == 0 for name in ("fits", "scaler_fits", "forecasts", "paired_metrics")
    )
