"""Authored synthetic facts; neither exchange-source proof nor historical deployment."""

from datetime import datetime
from decimal import Decimal

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data.enums import InstrumentType, MarketSegment
from tiaf.data.models import InstrumentKey, OHLCVBar
from tiaf.evaluation.forecast_contracts import (
    EvidenceReference,
    ForecastTargetSpec,
    ForecastWindow,
    QualifiedCloseObservation,
    QualifiedSessionSchedule,
    SessionRecord,
)
from tiaf.forecasting.contracts import (
    BinaryProbabilityOutput,
    ForecastArtifactIdentity,
    ForecastComposition,
    ForecastNode,
    ForecastRequest,
    ForecastResult,
    ForecastRoot,
)
from tiaf.forecasting.enums import (
    DataBasis,
    ForecastRealizationMode,
    ForecastStatus,
    KnowledgeBasis,
    QualificationStatus,
)
from tiaf.forecasting.identity import ArtifactReference, semantic_fingerprint


def instant(day: int = 4, hour: int = 16, minute: int = 0) -> datetime:
    return datetime(2026, 2, day, hour, minute, tzinfo=TIAF_TIMEZONE)


def ref(name: str) -> ArtifactReference:
    return ArtifactReference(
        artifact_id=f"fixture:{name}",
        artifact_version="1.0",
        fingerprint=semantic_fingerprint({"synthetic_fixture": name}),
    )


def subject() -> InstrumentKey:
    return InstrumentKey(
        symbol="RELIANCE",
        exchange="NSE",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
    )


def source(name: str, day: int = 3) -> EvidenceReference:
    return EvidenceReference(
        artifact=ref(name),
        source_id="source:synthetic",
        origin_id="origin:synthetic",
        document_version_id=f"document:{name}",
        data_basis=DataBasis.SYNTHETIC_FIXTURE,
        observed_at=instant(day, 15, 30),
        published_at=instant(day, 15, 34),
        available_at=instant(day, 15, 35),
        acquired_at=instant(day, 15, 35),
        admitted_at=instant(day, 15, 36),
    )


def bar() -> OHLCVBar:
    return OHLCVBar(
        instrument=subject(),
        interval="1d",
        start_at=instant(4, 9, 15),
        end_at=instant(4, 15, 30),
        open=105.0,
        high=106.0,
        low=104.0,
        close=105.0,
        source_provider="synthetic",
        volume=0,
    )


def window() -> ForecastWindow:
    schedule = QualifiedSessionSchedule(
        calendar_ref=ref("calendar-v1"),
        coverage_start=instant(4, 9, 15),
        coverage_end=instant(6, 15, 30),
        complete=True,
        qualification=QualificationStatus.QUALIFIED,
        qualification_policy_ref=ref("schedule-policy"),
        source=source("schedule"),
        sessions=tuple(
            SessionRecord(
                session_id=f"session:s{day + 16}",
                opens_at=instant(day, 9, 15),
                closes_at=instant(day, 15, 30),
                subject_eligible=True,
            )
            for day in (4, 5, 6)
        ),
    )
    close = QualifiedCloseObservation(
        observation_id="observation:reference-close",
        subject=subject(),
        session_id="session:s20",
        observed_at=instant(4, 15, 30),
        value=Decimal("105.000"),
        source=source("close", 4),
        bar_ref=ArtifactReference(
            artifact_id="fixture:bar",
            artifact_version="1.0",
            fingerprint=semantic_fingerprint(bar()),
        ),
        qualification=QualificationStatus.QUALIFIED,
        final=True,
        precision="SOURCE_DECIMAL",
        action_coverage="UNAFFECTED",
        action_coverage_ref=source("action-coverage"),
    )
    return ForecastWindow(
        schedule=schedule,
        reference=close,
        target_session_id="session:s21",
        target_open_time=instant(5, 9, 15),
        target_resolve_time=instant(5, 15, 30),
        outcome_due_at=instant(6, 9, 15),
        maturation_policy_ref=ref("maturation-policy"),
    )


def request(*, simulated: bool = False) -> ForecastRequest:
    return ForecastRequest(
        request_id="ff-request:synthetic",
        target=ForecastTargetSpec(
            subject=subject(),
            labeler_ref=ref("labeler-v1"),
            qualification_policy_ref=ref("price-policy"),
        ),
        window=window(),
        realization_mode=(
            ForecastRealizationMode.SIMULATED_ISSUANCE
            if simulated
            else ForecastRealizationMode.ACTUAL_ISSUANCE
        ),
        information_cutoff=instant(),
        as_of=instant(4, 16, 5),
        knowledge_basis=KnowledgeBasis.CAPTURED_AS_KNOWN,
        evidence_ref=ref("input-capture"),
        evidence=(source("prior-labels"),),
        profile_ref=ref("engineering-profile"),
        configuration_ref=ref("cold-config"),
        simulation_profile_ref=ref("simulation-profile") if simulated else None,
    )


def result(*, simulated: bool = False, probability: float = 0.6) -> ForecastResult:
    req = request(simulated=simulated)
    artifact = ForecastArtifactIdentity(
        artifact=ref("baserate-artifact"),
        configuration_ref=ref("baserate-config"),
        code_ref=ref("implementation-code"),
        fit_knowledge_cutoff=instant(4, 15, 45),
        prepared_at=instant(4, 15, 50),
        fit_evidence=(source("fit-labels"),),
    )
    composition = ForecastComposition(
        composition_id="composition:synthetic-singleton",
        nodes=(
            ForecastNode(
                node_id="node:baserate",
                artifact_ref=artifact.artifact,
                realization_mode=req.realization_mode,
            ),
        ),
        roots=(ForecastRoot(root_id="root:benchmark", node_id="node:baserate"),),
        policy_ref=ref("singleton-policy"),
    )
    return ForecastResult(
        result_id="ff-result:synthetic",
        run_id="ff-run:synthetic",
        request=req,
        composition=composition,
        artifact_identity=artifact,
        binding_ref=ref("synthetic-binding"),
        binding_available_at=instant(4, 15, 55),
        status=ForecastStatus.GENERATED,
        output=BinaryProbabilityOutput(probability=probability),
        computed_at=instant(7, 12) if simulated else instant(4, 16, 6),
        issued_at=None if simulated else instant(4, 16, 7),
        limitations=("limitation:synthetic-only",),
    )


def result_payload(*, simulated: bool = False) -> dict[str, object]:
    return result(simulated=simulated).model_dump(mode="json", exclude={"replay_fingerprint"})
