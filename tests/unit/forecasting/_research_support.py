"""Authored FF-1.1 cases, NOT evidence of exchange sessions or empirical rights."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any

from tiaf.contracts import DataQuality
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data.resolution.enums import ResolutionKind
from tiaf.data.resolution.models import InstrumentQuery, ResolutionResult, ResolvedInstrument
from tiaf.evaluation.forecast_contracts import (
    EvidenceReference,
    ForecastTargetSpec,
    QualifiedSessionSchedule,
    SessionRecord,
)
from tiaf.evaluation.forecast_research_contracts import (
    CorporateActionQualification,
    DailyBarInput,
    DataRightsQualification,
    EmpiricalDataset,
    EmpiricalSourceIdentity,
    OutcomeMaturationInput,
    SecurityIdentityQualification,
    SessionCalendarQualification,
)
from tiaf.evaluation.forecast_research_contracts import (
    QualificationState as Q,
)
from tiaf.forecasting.enums import DataBasis, QualificationStatus

from ._support import ref, subject

ASSESSMENT = datetime(2026, 9, 19, 12, tzinfo=TIAF_TIMEZONE)
PRIOR = datetime(2020, 12, 31, 12, tzinfo=TIAF_TIMEZONE)


def evidence(name: str, observed: datetime = PRIOR) -> EvidenceReference:
    return EvidenceReference(
        artifact=ref(name),
        source_id="source:synthetic",
        origin_id="origin:synthetic",
        document_version_id="document:" + name,
        data_basis=DataBasis.SYNTHETIC_FIXTURE,
        observed_at=observed,
        available_at=observed + timedelta(minutes=5),
        acquired_at=observed + timedelta(minutes=6),
        admitted_at=observed + timedelta(minutes=7),
    )


def dataset() -> EmpiricalDataset:
    # Fixture schedule is explicitly authored. Production never infers weekday sessions.
    dates = [
        date(2021, 1, d)
        for d in (4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29)
    ]
    dates += [date(2021, 2, d) for d in (1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 15, 16)]
    sessions = tuple(
        SessionRecord(
            session_id=f"session:ff1-{i}",
            opens_at=datetime.combine(day, time(9, 15), TIAF_TIMEZONE),
            closes_at=datetime.combine(day, time(15, 30), TIAF_TIMEZONE),
            subject_eligible=True,
        )
        for i, day in enumerate(dates)
    )
    schedule = QualifiedSessionSchedule(
        calendar_ref=ref("calendar"),
        coverage_start=sessions[0].opens_at,
        coverage_end=sessions[-1].closes_at,
        sessions=sessions,
        complete=True,
        qualification=QualificationStatus.QUALIFIED,
        qualification_policy_ref=ref("calendar-policy"),
        source=evidence("calendar"),
    )
    resolved = ResolvedInstrument(
        instrument=subject(),
        provider_name="synthetic",
        provider_instrument_id="synthetic-2885",
        source_record_id="master:reliance",
        source_observed_at=PRIOR,
        resolution_kind=ResolutionKind.EXACT,
        quality=DataQuality.GOOD,
    )
    rights = DataRightsQualification(
        record_id="rights:synthetic",
        source_artifact=ref("capture"),
        subject=subject(),
        coverage_start=dates[0],
        coverage_end=dates[-1],
        local_research=Q.QUALIFIED,
        model_training=Q.QUALIFIED,
        derived_feature_storage=Q.QUALIFIED,
        evaluation_artifact_retention=Q.QUALIFIED,
        replay_evidence_retention=Q.QUALIFIED,
        basis_refs=(ref("authored-not-real-permission"),),
        assessed_at=PRIOR,
    )
    return EmpiricalDataset(
        dataset_id="dataset:ff1-synthetic",
        target=ForecastTargetSpec(
            subject=subject(),
            labeler_ref=ref("labeler"),
            qualification_policy_ref=ref("unadjusted-price-policy"),
        ),
        source=EmpiricalSourceIdentity(
            source_id="source:synthetic",
            provider_id="provider:synthetic",
            origin_id="origin:synthetic",
            capture=ref("capture"),
            source_timezone="Asia/Kolkata",
            data_basis=DataBasis.SYNTHETIC_FIXTURE,
            rights_ref=rights.reference,
            acquisition_at=sessions[-1].closes_at + timedelta(days=1),
            provenance_ref=ref("retained-original-captures"),
        ),
        rights=rights,
        security=SecurityIdentityQualification(
            resolution=ResolutionResult(
                query=InstrumentQuery(symbol="RELIANCE"),
                matches=(resolved,),
                resolved=resolved,
                source_provider="synthetic",
                observed_at=PRIOR,
            ),
            valid_from=dates[0],
            valid_through=dates[-1],
            state=Q.QUALIFIED,
            evidence=evidence("master"),
        ),
        calendar=SessionCalendarQualification(
            schedules=(schedule,),
            state=Q.QUALIFIED,
            authority_refs=(ref("synthetic-calendar-authority"),),
        ),
        actions=(
            CorporateActionQualification(
                subject=subject(),
                from_session=dates[0],
                through_session=dates[-1],
                basis="UNADJUSTED",
                state=Q.QUALIFIED,
                coverage="UNAFFECTED",
                complete=True,
                evidence=evidence("actions"),
            ),
        ),
        maturation=tuple(
            OutcomeMaturationInput(
                target_session_id=s.session_id,
                outcome_due_at=s.closes_at + timedelta(days=1),
                policy_ref=ref("maturation-policy"),
                evidence=evidence("maturation-policy"),
            )
            for s in sessions
        ),
        coverage_start=dates[0],
        coverage_end=dates[-1],
        rows=tuple(
            DailyBarInput(
                row_id=f"bar:ff1-{i}",
                session_id=s.session_id,
                session_date=dates[i],
                instrument=subject(),
                provider_security_id="synthetic-2885",
                open=Decimal(100 + i),
                high=Decimal(101 + i),
                low=Decimal(99 + i),
                close=Decimal(100 + i),
                volume=100 + i,
                provenance=evidence(f"bar-{i}", s.closes_at),
            )
            for i, s in enumerate(sessions)
        ),
        reference_session_ids=tuple(s.session_id for s in sessions),
    )


def payload() -> dict[str, Any]:
    return dataset().model_dump(mode="json")


def repin_rights(data: dict[str, Any]) -> None:
    data["source"]["rights_ref"] = DataRightsQualification.model_validate(
        data["rights"]
    ).reference.model_dump(mode="json")
