"""Explicit adjusted research contexts; no reinterpretation of FF-0 contracts."""

from datetime import date, datetime, time, timedelta
from typing import Annotated, Any, Literal, Self

from pydantic import Field, StrictBool, model_validator

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data.models import OHLCVBar
from tiaf.data.resolution import ResolvedInstrument
from tiaf.evaluation.forecast_research_contracts import RightsEvidenceStatus
from tiaf.forecasting.identity import ForecastDateTime, semantic_fingerprint
from tiaf.forecasting.research_contracts import (
    AdjustedFF1FeatureSchema,
    AdjustedResearchProfile,
    FeatureVector,
    ResearchContract,
    ResearchDate,
)
from tiaf.planner.models import Sha256


class ResearchSpecialSession(ResearchContract):
    session_date: ResearchDate
    opens: str = Field(pattern=r"^\d{2}:\d{2}$")
    closes: str = Field(pattern=r"^\d{2}:\d{2}$")
    reason: str = Field(min_length=1)
    source_url: str = Field(pattern=r"^https://")

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if time.fromisoformat(self.opens) >= time.fromisoformat(self.closes):
            raise ValueError("SESSION_CLOCK_ORDER")
        return self


class ResearchCalendar(ResearchContract):
    """Reviewed daily research scope, not an operational scheduling service."""

    policy_id: Literal["ff1.nse_daily_research/1.0"] = "ff1.nse_daily_research/1.0"
    start: ResearchDate
    end: ResearchDate
    closed_dates: tuple[ResearchDate, ...]
    special_sessions: tuple[ResearchSpecialSession, ...]
    source_urls: tuple[str, ...] = Field(min_length=1)
    reviewed_at: ForecastDateTime
    qualified: StrictBool
    limitations: tuple[str, ...]

    @model_validator(mode="after")
    def unique_scope(self) -> Self:
        special = [s.session_date for s in self.special_sessions]
        if (
            self.end < self.start
            or (self.end - self.start).days > 4000
            or len(special) != len(set(special))
            or len(self.closed_dates) != len(set(self.closed_dates))
            or set(special).intersection(self.closed_dates)
            or any(not self.start <= d <= self.end for d in (*special, *self.closed_dates))
        ):
            raise ValueError("CALENDAR_SCOPE_CONFLICT")
        return self

    def sessions(self) -> tuple[tuple[date, datetime, datetime], ...]:
        special = {s.session_date: s for s in self.special_sessions}
        closed = set(self.closed_dates)
        result: list[tuple[date, datetime, datetime]] = []
        day = self.start
        while day <= self.end:
            if day in special or (day.weekday() < 5 and day not in closed):
                override = special.get(day)
                opens = time(9, 15) if override is None else time.fromisoformat(override.opens)
                closes = time(15, 30) if override is None else time.fromisoformat(override.closes)
                result.append(
                    (
                        day,
                        datetime.combine(day, opens, TIAF_TIMEZONE),
                        datetime.combine(day, closes, TIAF_TIMEZONE),
                    )
                )
            day += timedelta(days=1)
        return tuple(result)


class ResearchAction(ResearchContract):
    boundary: ResearchDate
    kind: Literal["SPLIT", "BONUS", "RIGHTS", "DEMERGER", "EXTRAORDINARY_DISTRIBUTION"]
    provider_adjustment_supported: StrictBool
    source_url: str = Field(pattern=r"^https://")

    @model_validator(mode="after")
    def documented_coverage_only(self) -> Self:
        if self.provider_adjustment_supported and self.kind not in ("SPLIT", "BONUS"):
            raise ValueError("ACTION_CLASS_NOT_DOCUMENTED_AS_ADJUSTED")
        return self


class RetrospectiveRow(ResearchContract):
    session_date: ResearchDate
    price_series_basis: Literal["CORPORATE_ACTION_ADJUSTED"] = "CORPORATE_ACTION_ADJUSTED"
    bar: OHLCVBar | None
    protected: StrictBool

    @model_validator(mode="after")
    def sealed_values_absent(self) -> Self:
        if self.protected != (self.session_date.year >= 2025):
            raise ValueError("PROTECTED_YEAR_MISMATCH")
        if self.protected != (self.bar is None):
            raise ValueError("PROTECTED_VALUES_MUST_BE_ABSENT")
        if self.bar is not None and self.bar.end_at.date() != self.session_date:
            raise ValueError("ROW_DATE_MISMATCH")
        return self


class RetrospectiveDataset(ResearchContract):
    dataset_id: str = Field(min_length=1)
    dataset_sha256: Sha256
    source_manifest_fingerprint: Sha256
    acquired_at: ForecastDateTime
    resolved: ResolvedInstrument
    rights_status: RightsEvidenceStatus
    rights_basis_fingerprint: Sha256
    identity_evidence_fingerprint: Sha256
    identity_qualified: StrictBool
    adjustment_evidence_fingerprint: Sha256
    adjustment_qualified: StrictBool
    action_review_qualified: StrictBool
    calendar: ResearchCalendar
    actions: tuple[ResearchAction, ...]
    rows: tuple[RetrospectiveRow, ...] = Field(min_length=1, max_length=8192)
    reference_start: ResearchDate = date(2018, 1, 1)
    reference_end: ResearchDate = date(2025, 12, 31)
    warnings: tuple[str, ...]

    @model_validator(mode="after")
    def bounded(self) -> Self:
        if self.reference_end < self.reference_start:
            raise ValueError("REVERSED_REFERENCE_SCOPE")
        if self.reference_end.year > 2025 or self.reference_start < date(2018, 1, 1):
            raise ValueError("REFERENCE_SCOPE_NOT_FF1")
        instrument = self.resolved.instrument
        if (
            instrument.symbol != "RELIANCE"
            or instrument.exchange != "NSE"
            or instrument.segment != "NSE_EQUITY"
            or instrument.instrument_type != "EQUITY"
        ):
            raise ValueError("RETROSPECTIVE_SUBJECT_MISMATCH")
        return self


class RetrospectiveObservation(ResearchContract):
    observation_id: str
    reference_date: ResearchDate
    target_date: ResearchDate | None
    profile_fingerprint: Sha256
    input_fingerprint: Sha256
    price_series_basis: Literal["CORPORATE_ACTION_ADJUSTED"] = "CORPORATE_ACTION_ADJUSTED"
    reference_closes_at: ForecastDateTime
    information_cutoff: ForecastDateTime
    simulation_as_of: ForecastDateTime
    target_opens_at: ForecastDateTime | None
    target_closes_at: ForecastDateTime | None
    assumed_label_available_at: ForecastDateTime | None
    feature_window_dates: tuple[ResearchDate, ...]
    features: FeatureVector | None
    label: Literal[0, 1] | None
    label_state: Literal["ELIGIBLE", "UNAVAILABLE", "SEALED"]
    reasons: tuple[str, ...]
    precision_feature_drift: Annotated[float, Field(ge=0, allow_inf_nan=False)] | None = None

    @model_validator(mode="after")
    def coherent(self) -> Self:
        if self.information_cutoff != self.reference_closes_at + timedelta(minutes=30):
            raise ValueError("RESEARCH_CUTOFF_ORDER")
        if self.reference_closes_at.date() != self.reference_date:
            raise ValueError("REFERENCE_CLOCK_DATE")
        if self.simulation_as_of != self.information_cutoff + timedelta(minutes=5):
            raise ValueError("RESEARCH_AS_OF_ORDER")
        if self.target_opens_at is not None and self.simulation_as_of >= self.target_opens_at:
            raise ValueError("AS_OF_NOT_BEFORE_TARGET_OPEN")
        if self.target_date is not None and self.target_date <= self.reference_date:
            raise ValueError("TARGET_DATE_ORDER")
        if any(day > self.reference_date for day in self.feature_window_dates):
            raise ValueError("FEATURE_FUTURE_ROW")
        if self.label is not None and (
            self.target_closes_at is None
            or self.assumed_label_available_at != self.target_closes_at + timedelta(minutes=30)
        ):
            raise ValueError("RESEARCH_LABEL_CLOCK")
        if (self.label is not None) != (self.label_state == "ELIGIBLE"):
            raise ValueError("LABEL_STATE_MISMATCH")
        if self.reference_date.year >= 2025 and (
            self.features is not None or self.label is not None
        ):
            raise ValueError("HOLDOUT_OPENED")
        if (
            self.target_date is not None
            and self.target_date.year >= 2025
            and self.label is not None
        ):
            raise ValueError("HOLDOUT_TARGET_OPENED")
        if self.features is not None and (
            not isinstance(self.features.feature_schema, AdjustedFF1FeatureSchema)
            or self.features.feature_schema.profile.fingerprint != self.profile_fingerprint
            or self.features.input_fingerprint != self.input_fingerprint
            or len(self.feature_window_dates) != 21
            or self.feature_window_dates[-1] != self.reference_date
            or tuple(sorted(set(self.feature_window_dates))) != self.feature_window_dates
        ):
            raise ValueError("RESEARCH_FEATURE_PROFILE_MISMATCH")
        return self


class RetrospectiveFold(ResearchContract):
    test_year: int = Field(ge=2021, le=2025)
    fit_cutoff: ForecastDateTime
    embargo_date: ResearchDate
    train_ids: tuple[str, ...]
    purged_ids: tuple[str, ...]
    test_ids: tuple[str, ...]
    paired_potential_ids: tuple[str, ...]
    baseline_support_ids: tuple[str, ...]
    baseline_support_eligible: int = Field(ge=0, le=20)
    train_positive: int = Field(ge=0)
    train_zero: int = Field(ge=0)
    test_feature_complete: int | None
    test_label_complete: int | None
    test_positive: int | None
    test_zero: int | None
    complete_five_session_blocks: int | None
    structural_holdout_slots: int | None
    test_outcomes_sealed: StrictBool
    blocking_reasons: tuple[str, ...]

    @model_validator(mode="after")
    def consistent(self) -> Self:
        if len(self.train_ids) != self.train_positive + self.train_zero:
            raise ValueError("FOLD_TRAIN_DENOMINATOR")
        if self.test_outcomes_sealed != (self.test_year == 2025):
            raise ValueError("FOLD_HOLDOUT_MISMATCH")
        if self.test_outcomes_sealed and (
            self.paired_potential_ids
            or self.test_feature_complete is not None
            or self.test_label_complete is not None
            or self.test_positive is not None
            or self.test_zero is not None
            or self.complete_five_session_blocks is not None
        ):
            raise ValueError("FOLD_HOLDOUT_OPENED")
        if set(self.train_ids).intersection((*self.test_ids, *self.purged_ids)):
            raise ValueError("FOLD_MEMBERSHIP_OVERLAP")
        return self


class RetrospectiveQualification(ResearchContract):
    policy_id: Literal["FF1_1A_ADJUSTED_QUALIFICATION_1.0"] = "FF1_1A_ADJUSTED_QUALIFICATION_1.0"
    profile: AdjustedResearchProfile
    assessed_at: ForecastDateTime
    dataset_fingerprint: Sha256
    context_fingerprint: Sha256
    feature_schema: AdjustedFF1FeatureSchema
    observations: tuple[RetrospectiveObservation, ...]
    folds: tuple[RetrospectiveFold, ...]
    # Sanitized extensible audit details; finalized memberships live in observations.
    audit: dict[str, Any]
    blocking_reasons: tuple[str, ...]
    empirical_fitting_authorized: StrictBool
    fingerprint: Sha256 | None = None

    @model_validator(mode="after")
    def sealed(self) -> Self:
        if self.feature_schema.profile != self.profile:
            raise ValueError("QUALIFICATION_PROFILE_MISMATCH")
        if any(o.profile_fingerprint != self.profile.fingerprint for o in self.observations):
            raise ValueError("OBSERVATION_PROFILE_MISMATCH")
        if self.empirical_fitting_authorized and (
            tuple(f.test_year for f in self.folds) != (2021, 2022, 2023, 2024, 2025)
            or any(f.blocking_reasons for f in self.folds)
        ):
            raise ValueError("FOLD_QUALIFICATION_INCOMPLETE")
        if self.empirical_fitting_authorized != (not self.blocking_reasons):
            raise ValueError("QUALIFICATION_AUTHORITY_MISMATCH")
        if self.empirical_fitting_authorized and not any(
            o.label is not None for o in self.observations
        ):
            raise ValueError("EMPTY_QUALIFICATION")
        fingerprint = semantic_fingerprint(self.model_dump(exclude={"fingerprint"}))
        if self.fingerprint is not None and self.fingerprint != fingerprint:
            raise ValueError("RETROSPECTIVE_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", fingerprint)
        return self
