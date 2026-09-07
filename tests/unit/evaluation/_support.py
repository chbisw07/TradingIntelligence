"""Synthetic frozen evidence, decision, and outcome helpers."""

from datetime import timedelta

from tiaf import __version__
from tiaf.baseline import BaselineEngine, BaselinePolicy, default_policy
from tiaf.contracts import DataQuality, FreshnessState, TradeStyle
from tiaf.evaluation import (
    BaselineRunRecord,
    EvidenceSnapshot,
    OutcomeObservation,
    OutcomePath,
    OutcomeWindow,
    create_evidence_snapshot,
    create_outcome_path,
    create_run_record,
)
from tiaf.features import FeatureStatus

from ..baseline._support import NOW, baseline_request


def frozen_case(
    *,
    profile: str = "positive",
    subject: str = "RELIANCE",
    policy: BaselinePolicy | None = None,
    include_relative: bool = True,
    quality: DataQuality = DataQuality.GOOD,
    status: FeatureStatus = FeatureStatus.AVAILABLE,
    primary_freshness: FreshnessState = FreshnessState.FRESH,
    values: dict[str, float] | None = None,
) -> tuple[EvidenceSnapshot, BaselineRunRecord]:
    selected = policy or default_policy(TradeStyle.POSITIONAL)
    request = baseline_request(
        selected,
        profile=profile,
        subject=subject,
        include_relative=include_relative,
        quality=quality,
        status=status,
        primary_freshness=primary_freshness,
        values=values,
    )
    snapshot = create_evidence_snapshot(
        request,
        policy_id=selected.policy_id,
        producer_version=__version__,
        benchmark_symbol="NIFTY" if include_relative else None,
        snapshot_created_at=NOW,
    )
    assessment = BaselineEngine((selected,)).assess(snapshot.decision_request)
    return snapshot, create_run_record(snapshot, assessment, recorded_at=NOW)


def future_path(run: BaselineRunRecord) -> OutcomePath:
    window = OutcomeWindow(
        start_at=NOW + timedelta(days=1),
        end_at=NOW + timedelta(days=3),
        source_interval="1d",
    )
    observations = (
        OutcomeObservation(
            start_at=NOW + timedelta(days=1),
            end_at=NOW + timedelta(days=2),
            high=105.0,
            low=98.0,
            close=104.0,
        ),
        OutcomeObservation(
            start_at=NOW + timedelta(days=2),
            end_at=NOW + timedelta(days=3),
            high=108.0,
            low=96.0,
            close=102.0,
        ),
    )
    return create_outcome_path(
        run,
        assessment_reference_price=100.0,
        window=window,
        observations=observations,
        quality=DataQuality.GOOD,
        complete=True,
        captured_at=NOW + timedelta(days=3),
    )
