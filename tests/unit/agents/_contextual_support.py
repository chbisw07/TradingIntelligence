"""Shared explicit evidence fixtures for A3.6 specialist tests."""

from collections.abc import Mapping
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import JsonValue

from tiaf.agents import (
    AgentBudget,
    AgentCapability,
    AgentEvidencePack,
    AgentEvidenceReference,
    AgentRequest,
    AnalysisMode,
    EvidenceFact,
    EvidenceFactKind,
    EvidenceFactParameter,
    SpecialistId,
)
from tiaf.context import AnalysisPurpose, EvidenceStatus
from tiaf.contracts import (
    DataQuality,
    EvidenceSource,
    EvidenceType,
    FreshnessState,
    Horizon,
    TradeStyle,
)
from tiaf.data import InstrumentType

NOW = datetime(2026, 9, 9, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
FINGERPRINT = "c" * 64
BASELINE_ID = "a2-context-baseline"


def fact(
    metric: str,
    value: str | int | float | bool,
    *,
    fact_id: str | None = None,
    interval: str | None = None,
    unit: str | None = None,
    parameters: tuple[EvidenceFactParameter, ...] = (),
) -> EvidenceFact:
    return EvidenceFact(
        fact_id=fact_id or f"fact:{metric}:{interval or 'none'}",
        kind=EvidenceFactKind.FEATURE,
        metric_id=metric,
        value=value,
        unit=unit,
        parameters=parameters,
        interval=interval,
        as_of=NOW,
        quality=DataQuality.GOOD,
        freshness=FreshnessState.FRESH,
        source_evidence=(f"source:{metric}",),
    )


def reference(
    evidence_id: str,
    evidence_type: EvidenceType,
    facts: tuple[EvidenceFact, ...],
    *,
    metadata: Mapping[str, JsonValue] | None = None,
) -> AgentEvidenceReference:
    return AgentEvidenceReference(
        evidence_id=evidence_id,
        evidence_type=evidence_type,
        subject="RELIANCE",
        producer_id="test.context",
        producer_version="1.0",
        source=EvidenceSource.DERIVED,
        availability=EvidenceStatus.AVAILABLE,
        quality=DataQuality.GOOD,
        freshness=FreshnessState.FRESH,
        observed_at=NOW,
        acquired_at=NOW,
        checksum=f"checksum:{evidence_id}",
        source_reference=f"fixture:{evidence_id}",
        facts=facts,
        metadata=dict(metadata or {}),
    )


def pack(
    references: tuple[AgentEvidenceReference, ...],
    *,
    coverage: float = 1.0,
    freshness: FreshnessState = FreshnessState.FRESH,
    quality: DataQuality = DataQuality.GOOD,
) -> AgentEvidencePack:
    return AgentEvidencePack(
        pack_id="context-pack",
        request_id="context-request",
        subject="RELIANCE",
        evidence_fingerprint=FINGERPRINT,
        references=references,
        analysis_context_ids=("a2-context",),
        deterministic_assessment_id=BASELINE_ID,
        overall_quality=quality,
        overall_freshness=freshness,
        evidence_coverage=coverage,
        created_at=NOW,
    )


def request(specialist: SpecialistId) -> AgentRequest:
    capability = {
        SpecialistId.RELATIVE_STRENGTH: (AgentCapability.READ_A2_EVIDENCE,),
        SpecialistId.SECTOR: (
            AgentCapability.READ_A2_EVIDENCE,
            AgentCapability.READ_SECTOR_CONTEXT,
        ),
        SpecialistId.MACRO: (AgentCapability.READ_A2_EVIDENCE, AgentCapability.READ_MACRO_CONTEXT),
    }[specialist]
    return AgentRequest(
        request_id="context-request",
        run_id=f"run:{specialist.value.lower()}",
        subject="RELIANCE",
        instrument_type=InstrumentType.EQUITY,
        horizon=Horizon(label="POSITIONAL", min_days=2, max_days=20),
        specialist=specialist,
        purpose=AnalysisPurpose.OPPORTUNITY,
        trade_style=TradeStyle.POSITIONAL,
        analysis_mode=AnalysisMode.DETERMINISTIC_ONLY,
        task="Interpret supplied contextual evidence.",
        a2_context_ids=("a2-context",),
        a2_evidence_ids=("a2-evidence",),
        deterministic_baseline_reference=BASELINE_ID,
        evidence_fingerprint=FINGERPRINT,
        allowed_capabilities=capability,
        budget=AgentBudget(),
        created_at=NOW,
    )
