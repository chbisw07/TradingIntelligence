"""Shared immutable fixtures and dummy specialists for A3.1 tests."""

from datetime import datetime
from typing import cast
from zoneinfo import ZoneInfo

from tiaf.agents import (
    AgentBudget,
    AgentCapability,
    AgentConfidence,
    AgentEvidencePack,
    AgentEvidenceReference,
    AgentOpinionV2,
    AgentRequest,
    AgentRunStatus,
    AgentStance,
    AgentUsage,
    AnalysisMode,
    BaselineAgreement,
    CitationRole,
    ClaimKind,
    EvidenceCitation,
    EvidenceClaim,
    ReasoningModelIdentity,
    SpecialistCapability,
    SpecialistCostTier,
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

NOW = datetime(2026, 9, 8, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
FINGERPRINT = "a" * 64
BASELINE_ID = "a2-assessment-1"
EVIDENCE_ID = "a2-technical-1"


def agent_request(
    *,
    budget: AgentBudget | None = None,
    specialist: SpecialistId = SpecialistId.TECHNICAL,
    allowed_capabilities: tuple[AgentCapability, ...] = (
        AgentCapability.READ_A2_EVIDENCE,
    ),
) -> AgentRequest:
    return AgentRequest(
        request_id="request-1",
        run_id="run-1",
        subject="RELIANCE",
        instrument_type=InstrumentType.EQUITY,
        horizon=Horizon(label="positional", min_days=2, max_days=20),
        specialist=specialist,
        purpose=AnalysisPurpose.OPPORTUNITY,
        trade_style=TradeStyle.POSITIONAL,
        analysis_mode=AnalysisMode.DETERMINISTIC_ONLY,
        task="Interpret supplied deterministic structure.",
        a2_context_ids=("context-1",),
        a2_evidence_ids=(EVIDENCE_ID,),
        deterministic_baseline_reference=BASELINE_ID,
        evidence_fingerprint=FINGERPRINT,
        allowed_capabilities=allowed_capabilities,
        budget=budget or AgentBudget(),
        correlation_id="correlation-1",
        created_at=NOW,
    )


def evidence_reference(
    *,
    evidence_id: str = EVIDENCE_ID,
    evidence_type: EvidenceType = EvidenceType.TECHNICAL,
    availability: EvidenceStatus = EvidenceStatus.AVAILABLE,
) -> AgentEvidenceReference:
    factual = availability in {
        EvidenceStatus.AVAILABLE,
        EvidenceStatus.PARTIAL,
        EvidenceStatus.STALE,
    }
    return AgentEvidenceReference(
        evidence_id=evidence_id,
        evidence_type=evidence_type,
        subject="RELIANCE",
        producer_id="tiaf.baseline",
        producer_version="1.0",
        source=EvidenceSource.DERIVED,
        availability=availability,
        quality=DataQuality.GOOD if factual else None,
        freshness=(
            FreshnessState.STALE
            if availability is EvidenceStatus.STALE
            else FreshnessState.FRESH if factual else None
        ),
        observed_at=NOW if factual else None,
        acquired_at=NOW,
        checksum="evidence-checksum" if factual else None,
        failure_code="EVIDENCE_FAILED" if availability is EvidenceStatus.FAILED else None,
        failure_detail="Evidence source failed" if availability is EvidenceStatus.FAILED else None,
    )


def evidence_pack(
    *,
    reference: AgentEvidenceReference | None = None,
    request_id: str = "request-1",
    fingerprint: str = FINGERPRINT,
    baseline_id: str = BASELINE_ID,
) -> AgentEvidencePack:
    selected = reference or evidence_reference()
    factual = selected.availability in {
        EvidenceStatus.AVAILABLE,
        EvidenceStatus.PARTIAL,
        EvidenceStatus.STALE,
    }
    return AgentEvidencePack(
        pack_id="pack-1",
        request_id=request_id,
        subject="RELIANCE",
        evidence_fingerprint=fingerprint,
        references=(selected,),
        analysis_context_ids=("context-1",),
        feature_bundle_ids=("feature-bundle-1",),
        deterministic_assessment_id=baseline_id,
        overall_quality=DataQuality.GOOD if factual else DataQuality.UNAVAILABLE,
        overall_freshness=FreshnessState.FRESH if factual else FreshnessState.UNKNOWN,
        evidence_coverage=1.0 if factual else 0.0,
        created_at=NOW,
    )


def capability(
    *,
    specialist: SpecialistId = SpecialistId.TECHNICAL,
    required_evidence_types: tuple[EvidenceType, ...] = (EvidenceType.TECHNICAL,),
    allowed_capabilities: tuple[AgentCapability, ...] = (
        AgentCapability.READ_A2_EVIDENCE,
    ),
) -> SpecialistCapability:
    return SpecialistCapability(
        specialist=specialist,
        specialist_version="1.0",
        display_name="Technical structure",
        description="Interprets supplied deterministic structure.",
        supported_instrument_types=(InstrumentType.EQUITY, InstrumentType.INDEX),
        required_evidence_types=required_evidence_types,
        allowed_capabilities=allowed_capabilities,
        supports_no_llm=True,
        cost_tier=SpecialistCostTier.LOW,
        prohibitions=("NO_EXECUTION", "NO_A2_RECOMPUTATION"),
    )


def evidence_claim() -> EvidenceClaim:
    return EvidenceClaim(
        claim_id="claim-1",
        kind=ClaimKind.INTERPRETIVE,
        statement="The supplied deterministic structure is constructive.",
        evidence_type=EvidenceType.TECHNICAL,
        citations=(
            EvidenceCitation(
                evidence_id=EVIDENCE_ID,
                role=CitationRole.SUPPORTS,
            ),
        ),
        as_of=NOW,
        provenance="TIAF A2 deterministic evidence",
        quality=DataQuality.GOOD,
        freshness=FreshnessState.FRESH,
    )


def agent_opinion(
    *,
    status: AgentRunStatus = AgentRunStatus.SUCCESS,
    stance: AgentStance = AgentStance.POSITIVE,
    usage: AgentUsage | None = None,
    request: AgentRequest | None = None,
) -> AgentOpinionV2:
    selected_request = request or agent_request()
    selected_usage = usage or AgentUsage()
    return AgentOpinionV2(
        opinion_id="opinion-1",
        request_id=selected_request.request_id,
        run_id=selected_request.run_id,
        specialist=selected_request.specialist,
        specialist_version="1.0",
        subject=selected_request.subject,
        horizon=selected_request.horizon,
        stance=stance,
        status=status,
        confidence=AgentConfidence(
            evidence_coverage=1.0,
            evidence_quality=DataQuality.GOOD,
        ),
        summary="Constructive interpretation of supplied evidence.",
        reason_codes=("STRUCTURE_CONSTRUCTIVE",),
        evidence_claims=(evidence_claim(),),
        supporting_evidence_ids=(EVIDENCE_ID,),
        deterministic_baseline_reference=BASELINE_ID,
        baseline_agreement=BaselineAgreement.PARTIALLY_AGREES,
        evidence_fingerprint=FINGERPRINT,
        evidence_quality=DataQuality.GOOD,
        evidence_freshness=FreshnessState.FRESH,
        model_identity=(
            ReasoningModelIdentity(
                provider_id="fake-provider",
                model_id="fake-model",
                model_version="1",
                configuration_id="test-config",
            )
            if selected_usage.llm_calls
            else None
        ),
        prompt_version="test-prompt-1" if selected_usage.llm_calls else None,
        policy_version="1.0",
        usage=selected_usage,
        produced_at=NOW,
    )


class DummySpecialist:
    def __init__(
        self,
        *,
        definition: SpecialistCapability | None = None,
        opinion: AgentOpinionV2 | None = None,
        error: Exception | None = None,
        invalid_output: bool = False,
    ) -> None:
        self._definition = definition or capability()
        self._opinion = opinion or agent_opinion()
        self._error = error
        self._invalid_output = invalid_output
        self.calls = 0

    def capability(self) -> SpecialistCapability:
        return self._definition

    def analyze(
        self,
        request: AgentRequest,
        evidence: AgentEvidencePack,
    ) -> AgentOpinionV2:
        del request, evidence
        self.calls += 1
        if self._error is not None:
            raise self._error
        if self._invalid_output:
            return cast(AgentOpinionV2, object())
        return self._opinion


class StepClock:
    def __init__(self, *values: float) -> None:
        self._values = iter(values)

    def __call__(self) -> float:
        return next(self._values)
