"""Adjusted research is additive; no fitting, live access or historical backdating."""

import json
import math
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.evaluation.forecast_qualification import ResearchQualificationRuntime
from tiaf.evaluation.forecast_research_contracts import (
    ResearchRightsConfig,
    RightsEnforcementPolicy,
)
from tiaf.evaluation.forecast_retrospective import _folds, research_direction
from tiaf.evaluation.forecast_retrospective_contracts import (
    ResearchCalendar,
    RetrospectiveDataset,
    RetrospectiveObservation,
    RetrospectiveQualification,
)
from tiaf.forecasting.identity import semantic_fingerprint
from tiaf.forecasting.research_contracts import (
    AdjustedFF1FeatureSchema,
    AdjustedResearchProfile,
    FF1FeatureSchema,
)

ROOT = Path(__file__).resolve().parents[3]
PROFILE = AdjustedResearchProfile()
AT = datetime(2026, 9, 21, 16, tzinfo=TIAF_TIMEZONE)


def revised(model: Any, **updates: Any) -> Any:
    return type(model).model_validate({**model.model_dump(), **updates})


def dataset(*, full: bool = False) -> RetrospectiveDataset:
    if full:
        review = json.loads(
            (
                ROOT / "docs/qualification_records/ff1_1a/adjusted_research_review_20260921.json"
            ).read_text()
        )
        calendar = ResearchCalendar.model_validate(review["calendar"])
        actions = review["actions"]
    else:
        calendar = ResearchCalendar(
            start=date(2017, 11, 1),
            end=date(2018, 1, 31),
            closed_dates=(),
            special_sessions=(),
            source_urls=("https://example.test/calendar",),
            reviewed_at=AT,
            qualified=True,
            limitations=("SYNTHETIC_TEST_CALENDAR",),
        )
        actions = []
    instrument = {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "segment": "NSE_EQUITY",
        "instrument_type": "EQUITY",
    }
    rows = []
    for index, (day, opens, closes) in enumerate(calendar.sessions()):
        protected = day.year >= 2025
        close = 100 + index * 0.002 + math.sin(index) if not protected else None
        bar = (
            None
            if close is None
            else {
                "instrument": instrument,
                "interval": "1d",
                "start_at": opens,
                "end_at": closes,
                "open": close,
                "high": close + 1,
                "low": close - 1,
                "close": close,
                "volume": 1000 + index % 20,
                "source_provider": "test",
            }
        )
        rows.append({"session_date": day, "protected": protected, "bar": bar})
    return RetrospectiveDataset.model_validate(
        {
            "dataset_id": "synthetic-adjusted",
            "dataset_sha256": "a" * 64,
            "source_manifest_fingerprint": "b" * 64,
            "acquired_at": AT,
            "resolved": {
                "instrument": instrument,
                "provider_name": "test",
                "provider_instrument_id": "test-id",
                "source_record_id": "synthetic",
                "source_observed_at": AT,
                "resolution_kind": "EXACT",
                "quality": "GOOD",
            },
            "rights_status": "UNVERIFIED",
            "rights_basis_fingerprint": "c" * 64,
            "identity_evidence_fingerprint": "d" * 64,
            "identity_qualified": True,
            "adjustment_evidence_fingerprint": "e" * 64,
            "adjustment_qualified": True,
            "action_review_qualified": True,
            "calendar": calendar,
            "actions": actions,
            "rows": rows,
            "reference_end": calendar.end if not full else date(2025, 12, 31),
            "warnings": ("SYNTHETIC_VALUES_NOT_EMPIRICAL_DATA",),
        }
    )


def qualify(value: RetrospectiveDataset) -> RetrospectiveQualification:
    return ResearchQualificationRuntime(retrospective_profile=PROFILE).qualify_retrospective(
        value, assessed_at=AT
    )


@pytest.fixture(scope="module")
def full_result() -> RetrospectiveQualification:
    return qualify(dataset(full=True))


def test_adjusted_profile_requires_explicit_cold_owner() -> None:
    with pytest.raises(ValueError, match="NOT_INSTALLED"):
        ResearchQualificationRuntime().qualify_retrospective(dataset(), assessed_at=AT)
    owner = ResearchQualificationRuntime(retrospective_profile=PROFILE)
    with pytest.raises(AttributeError):
        owner.retrospective_profile = None  # type: ignore[misc]


@pytest.mark.parametrize(
    "field,value",
    [
        ("research_mode", "CAPTURED_AS_KNOWN"),
        ("source_vintage", "HISTORICAL_CAPTURE"),
        ("price_series_basis", "UNADJUSTED"),
        ("operational_replay_eligible", True),
        ("historical_capture_claim", "AVAILABLE_AS_KNOWN"),
        ("production_eligible", True),
        ("feature_absolute_tolerance", 1.0),
        ("cutoff_minutes_after_close", 0),
        ("holdout_year", 2026),
        ("target_family", "other"),
    ],
)
def test_policy_cannot_silently_change(field: str, value: Any) -> None:
    with pytest.raises(ValidationError):
        revised(PROFILE, **{field: value})


def test_fixed_five_formulas_old_profile_unchanged_and_new_basis_sealed() -> None:
    original = FF1FeatureSchema()
    adjusted = AdjustedFF1FeatureSchema(profile=PROFILE)
    assert (
        original.fingerprint == "521337f10dd977b523ad6a2bd073ba9f11351f8948c87beff6ec710b4e4b217a"
    )
    assert original.features == adjusted.features
    assert original.feature_schema_id == adjusted.feature_schema_id
    assert original.feature_schema_version == adjusted.feature_schema_version == "1.0"
    assert adjusted.fingerprint != original.fingerprint
    assert PROFILE.fingerprint != semantic_fingerprint(
        {**PROFILE.model_dump(), "price_series_basis": "UNADJUSTED"}
    )
    with pytest.raises(ValidationError):
        FF1FeatureSchema.model_validate(adjusted.model_dump())
    with pytest.raises(ValidationError):
        revised(adjusted, features=adjusted.features[:-1])


@pytest.mark.parametrize(
    "current,next_close,expected", [(100.0, 101.0, 1), (100.0, 99.0, 0), (100.0, 100.0, 0)]
)
def test_shared_ground_truth_direction(current: float, next_close: float, expected: int) -> None:
    assert (
        research_direction(
            current,
            next_close,
            reference_basis=PROFILE.price_series_basis,
            terminal_basis=PROFILE.price_series_basis,
            profile=PROFILE,
        )
        == expected
    )


@pytest.mark.parametrize(
    "current,target",
    [(math.nan, 100.0), (100.0, math.inf), (0.0, 100.0), (100.0, math.nextafter(100.0, math.inf))],
)
def test_material_numeric_ambiguity_is_not_negative_label(current: float, target: float) -> None:
    with pytest.raises(ValueError):
        research_direction(
            current,
            target,
            reference_basis=PROFILE.price_series_basis,
            terminal_basis=PROFILE.price_series_basis,
            profile=PROFILE,
        )


def test_mixed_endpoint_and_window_basis_rejected() -> None:
    with pytest.raises(ValueError, match="BASIS_MISMATCH"):
        research_direction(
            100.0,
            101.0,
            reference_basis="UNADJUSTED",
            terminal_basis=PROFILE.price_series_basis,
            profile=PROFILE,
        )
    original = dataset()
    with pytest.raises(ValidationError):
        revised(original.rows[0], price_series_basis="UNADJUSTED")


@pytest.mark.parametrize(
    "field", ["identity_qualified", "adjustment_qualified", "action_review_qualified"]
)
def test_reviewed_scientific_evidence_required(field: str) -> None:
    result = qualify(revised(dataset(), **{field: False}))
    assert not result.empirical_fitting_authorized
    assert not any(o.features or o.label is not None for o in result.observations)


def test_denied_rights_fail_even_with_warning_policy() -> None:
    result = qualify(revised(dataset(), rights_status="VERIFIED_DENIED"))
    assert "RIGHTS_HOLD" in result.blocking_reasons
    owner = ResearchQualificationRuntime(
        config=ResearchRightsConfig(rights_enforcement_policy=RightsEnforcementPolicy.ENFORCE),
        retrospective_profile=PROFILE,
    )
    assert "RIGHTS_HOLD" in owner.qualify_retrospective(dataset(), assessed_at=AT).blocking_reasons


def test_calendar_has_all_eight_actual_weekend_exceptions_and_clocks() -> None:
    data = dataset(full=True)
    weekends = tuple(
        (d.isoformat(), a.strftime("%H:%M"), b.strftime("%H:%M"))
        for d, a, b in data.calendar.sessions()
        if d.weekday() >= 5
    )
    assert weekends == (
        ("2019-10-27", "18:15", "19:15"),
        ("2020-02-01", "09:15", "15:30"),
        ("2020-11-14", "18:15", "19:15"),
        ("2023-11-12", "18:15", "19:15"),
        ("2024-01-20", "09:15", "15:30"),
        ("2024-03-02", "09:15", "12:30"),
        ("2024-05-18", "09:15", "12:30"),
        ("2025-02-01", "09:15", "15:30"),
    )
    assert len(data.rows) == 2045
    assert len(data.calendar.sessions()) == 2045


def test_unexplained_session_and_missing_rows_do_not_backfill() -> None:
    data = dataset()
    modified = revised(data.calendar, closed_dates=(data.rows[-2].session_date,))
    result = qualify(revised(data, calendar=modified))
    assert "UNEXPLAINED_NON_SESSION_ROW" in result.blocking_reasons
    missing = qualify(revised(data, rows=data.rows[:-2] + data.rows[-1:]))
    assert "MISSING_SCHEDULED_BAR" in missing.blocking_reasons
    assert not missing.empirical_fitting_authorized


def test_full_synthetic_qualification_passes_without_learning(
    full_result: RetrospectiveQualification,
) -> None:
    assert full_result.empirical_fitting_authorized
    assert not full_result.blocking_reasons
    assert full_result.audit["rights_status"] == "UNVERIFIED"
    assert full_result.audit["rights_admission"] == "ADMITTED_WITH_WARNING"
    assert all(
        full_result.audit[key] == 0
        for key in ("fits", "scaler_fits", "forecasts", "paired_metrics")
    )
    assert full_result.audit["maximum_feature_perturbation"] <= PROFILE.feature_absolute_tolerance
    assert not PROFILE.source_forensic_eligible


def test_actions_exclude_only_unsupported_dependency_intersections(
    full_result: RetrospectiveQualification,
) -> None:
    by_date = {o.reference_date: o for o in full_result.observations}
    assert "LABEL_UNSUPPORTED_ACTION" in by_date[date(2020, 5, 12)].reasons
    assert "FEATURE_ACTION_RIGHTS" in by_date[date(2020, 5, 13)].reasons
    assert "FEATURE_ACTION_DEMERGER" in by_date[date(2023, 7, 20)].reasons
    assert by_date[date(2024, 10, 28)].features is not None
    assert by_date[date(2024, 10, 25)].label is not None
    assert by_date[date(2020, 6, 11)].features is not None


def test_all_feature_windows_and_simulated_clocks_are_causal(
    full_result: RetrospectiveQualification,
) -> None:
    for row in full_result.observations:
        assert all(day <= row.reference_date for day in row.feature_window_dates)
        assert row.target_date not in row.feature_window_dates
        assert row.simulation_as_of == row.information_cutoff + timedelta(minutes=5)
        assert row.target_opens_at is not None and row.simulation_as_of < row.target_opens_at
    for field, value in (("simulation_as_of", AT), ("feature_window_dates", [date(2026, 1, 1)])):
        with pytest.raises(ValidationError):
            revised(full_result.observations[0], **{field: value})
    with pytest.raises(ValidationError):
        revised(full_result, assessed_at=datetime(2026, 9, 21))


def test_holdout_cannot_carry_numeric_rows_features_or_labels(
    full_result: RetrospectiveQualification,
) -> None:
    data = dataset(full=True)
    protected = next(row for row in data.rows if row.protected)
    with pytest.raises(ValidationError):
        revised(protected, bar=data.rows[0].bar)
    reference = next(o for o in full_result.observations if o.reference_date.year == 2025)
    with pytest.raises(ValidationError):
        revised(reference, label=0, label_state="ELIGIBLE")
    assert all(
        o.features is None and o.label is None and o.label_state == "SEALED"
        for o in full_result.observations
        if o.reference_date.year == 2025
    )
    last_dev = next(o for o in full_result.observations if o.reference_date == date(2024, 12, 31))
    assert last_dev.label_state == "SEALED" and last_dev.label is None
    assert full_result.folds[-1].test_positive is None
    assert full_result.folds[-1].test_feature_complete is None
    assert full_result.folds[-1].paired_potential_ids == ()


def test_fold_memberships_are_cutoff_safe_and_gap_is_purged(
    full_result: RetrospectiveQualification,
) -> None:
    by_id = {o.observation_id: o for o in full_result.observations}
    for fold in full_result.folds:
        assert len(fold.purged_ids) == 2
        assert fold.baseline_support_eligible == len(fold.baseline_support_ids) == 20
        for name in fold.train_ids:
            row = by_id[name]
            assert row.features is not None and row.label is not None
            assert row.assumed_label_available_at is not None
            assert row.assumed_label_available_at < fold.fit_cutoff
            assert row.reference_date.year < fold.test_year
        assert not set(fold.train_ids).intersection(fold.test_ids)


def test_baseline_does_not_backfill_invalid_last_twenty(
    full_result: RetrospectiveQualification,
) -> None:
    remove = full_result.folds[0].baseline_support_ids[-1]
    rows = tuple(
        revised(o, label=None, label_state="UNAVAILABLE", assumed_label_available_at=None)
        if o.observation_id == remove
        else o
        for o in full_result.observations
    )
    folds = _folds(rows, dataset(full=True).calendar.sessions())
    assert folds[0].baseline_support_eligible == 19
    assert folds[0].baseline_support_ids == full_result.folds[0].baseline_support_ids
    assert "BASERATE_SUPPORT" in folds[0].blocking_reasons


def test_round_trip_frozen_collections_and_tamper_rejection(
    full_result: RetrospectiveQualification,
) -> None:
    rebuilt = RetrospectiveQualification.model_validate_json(full_result.model_dump_json())
    assert rebuilt == full_result
    assert isinstance(rebuilt.observations, tuple)
    assert isinstance(rebuilt.model_dump(mode="json")["observations"], list)
    with pytest.raises(ValidationError):
        revised(rebuilt, dataset_fingerprint="f" * 64)
    with pytest.raises(ValidationError):
        rebuilt.empirical_fitting_authorized = False
    with pytest.raises(AttributeError):
        rebuilt.observations.append(rebuilt.observations[0])  # type: ignore[attr-defined]


def test_target_missing_is_unavailable_not_zero() -> None:
    result = qualify(dataset())
    row = result.observations[-1]
    assert row.label is None and row.label_state == "UNAVAILABLE"
    assert "TARGET_UNAVAILABLE" in row.reasons


def test_observation_reconstructs_from_json_arrays(full_result: RetrospectiveQualification) -> None:
    row = full_result.observations[0]
    rebuilt = RetrospectiveObservation.model_validate(row.model_dump(mode="json"))
    assert rebuilt == row
    assert rebuilt.features is not None
    assert rebuilt.features.feature_schema.features == FF1FeatureSchema().features


def test_cutoff_must_be_close_plus_thirty(full_result: RetrospectiveQualification) -> None:
    row = full_result.observations[0]
    with pytest.raises(ValidationError, match="RESEARCH_CUTOFF_ORDER"):
        revised(
            row,
            information_cutoff=row.information_cutoff - timedelta(minutes=1),
            simulation_as_of=row.simulation_as_of - timedelta(minutes=1),
        )


def test_weekday_outage_extension_uses_actual_final_close(
    full_result: RetrospectiveQualification,
) -> None:
    row = next(o for o in full_result.observations if o.reference_date == date(2021, 2, 24))
    assert row.reference_closes_at.strftime("%H:%M") == "17:00"
    assert row.information_cutoff.strftime("%H:%M") == "17:30"
    assert row.simulation_as_of.strftime("%H:%M") == "17:35"


def test_future_price_changes_cannot_change_earlier_feature_values() -> None:
    data = dataset()
    before = qualify(data)
    last = data.rows[-1]
    assert last.bar is not None
    bar = revised(last.bar, high=10001.0, close=10000.0)
    after = qualify(revised(data, rows=(*data.rows[:-1], revised(last, bar=bar))))
    for original, changed in zip(before.observations[:-1], after.observations[:-1], strict=True):
        assert original.features is not None and changed.features is not None
        assert original.features.values == changed.features.values
