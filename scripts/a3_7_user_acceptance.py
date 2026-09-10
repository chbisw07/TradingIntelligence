"""Run bounded deterministic user-level acceptance for all three A3.7 specialists."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from tiaf.agents import (
    AgentBudget,
    AgentCapability,
    AgentEvidencePack,
    AgentEvidenceReference,
    AgentRequest,
    AgentRunRecord,
    AgentRunStatus,
    AgentStance,
    AnalysisMode,
    BaselineAgreement,
    EvidenceFact,
    EvidenceFactKind,
    EvidenceImportance,
    MissingEvidenceRequest,
    SpecialistId,
    agent_record_json,
    load_agent_record_json,
)
from tiaf.agents.registry import AgentRegistry
from tiaf.agents.runtime import AgentRuntime
from tiaf.agents.specialists import (
    DerivativesContextSpecialist,
    DerivativesReasonCode,
    OpportunityQualitySpecialist,
    OpportunityReasonCode,
    OpportunityRiskSpecialist,
    RiskReasonCode,
    derivatives_context_assessment_from_opinion,
    opportunity_quality_assessment_from_opinion,
    opportunity_risk_assessment_from_opinion,
)
from tiaf.baseline import CandidateClass
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

FIXTURE_TIME = datetime(2026, 9, 10, 15, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
_SPECIALISTS = (
    SpecialistId.DERIVATIVES_CONTEXT,
    SpecialistId.OPPORTUNITY_QUALITY,
    SpecialistId.OPPORTUNITY_RISK,
)
_FORBIDDEN_KEYS = {
    "action",
    "calibrated_success_probability",
    "expiry_selection",
    "lot",
    "lot_size",
    "option_type",
    "quantity",
    "stop",
    "stop_loss",
    "strike",
    "target",
}
_FORBIDDEN_ACTION_VALUES = {"HOLD", "BOOK", "EXIT", "PROTECT", "PARTIAL_BOOK"}


@dataclass(frozen=True)
class FactSpec:
    metric: str
    value: str | int | float | bool


@dataclass(frozen=True)
class ReferenceSpec:
    evidence_id: str
    evidence_type: EvidenceType
    facts: tuple[FactSpec, ...]
    freshness: FreshnessState = FreshnessState.FRESH


@dataclass(frozen=True)
class Scenario:
    code: str
    title: str
    symbol: str
    instrument_type: InstrumentType
    horizon: Horizon
    trade_style: TradeStyle
    references: tuple[ReferenceSpec, ...]
    expected_derivatives: frozenset[str]
    expected_quality: frozenset[str]
    expected_risk: frozenset[str]
    required_reasons: frozenset[str]
    expect_contradiction: bool = False
    expect_missing: bool = False
    coverage: float = 1.0


@dataclass(frozen=True)
class AcceptanceResult:
    scenario: Scenario
    records: tuple[AgentRunRecord, ...]
    derivatives: str
    quality: str
    risk: str
    reasons: tuple[str, ...]
    contradictions: int
    missing: int
    confidence: tuple[str, ...]
    confidence_basis: tuple[str, ...]
    baseline_agreement: tuple[str, ...]


def _baseline(candidate: CandidateClass, direction: str) -> ReferenceSpec:
    return ReferenceSpec(
        "baseline",
        EvidenceType.OTHER,
        (
            FactSpec("baseline.candidate_class", candidate.value),
            FactSpec("baseline.direction", direction),
            FactSpec("baseline.opportunity_score", 70.0),
        ),
    )


def _technical(
    *,
    stance: str,
    extension: str,
    room: str,
    participation: str,
    volatility: str,
) -> ReferenceSpec:
    return ReferenceSpec(
        "technical",
        EvidenceType.TECHNICAL,
        (
            FactSpec("technical.stance", stance),
            FactSpec("technical.extension_state", extension),
            FactSpec("technical.remaining_room", room),
            FactSpec("technical.participation_state", participation),
            FactSpec("technical.volatility_state", volatility),
        ),
    )


def _derivatives(
    *,
    iv: float,
    oi_pcr: float,
    volume_pcr: float,
    spread: float,
    concentration: float,
    dte: int,
    volume: int = 10_000,
    freshness: FreshnessState = FreshnessState.FRESH,
) -> ReferenceSpec:
    return ReferenceSpec(
        "derivatives",
        EvidenceType.DERIVATIVES,
        (
            FactSpec("derivatives.atm_mean_iv", iv),
            FactSpec("derivatives.oi_put_call_ratio", oi_pcr),
            FactSpec("derivatives.volume_put_call_ratio", volume_pcr),
            FactSpec("derivatives.atm_ce_bid_ask_spread_percent", spread),
            FactSpec("derivatives.atm_pe_bid_ask_spread_percent", spread),
            FactSpec("derivatives.ce_volume_total", volume),
            FactSpec("derivatives.pe_volume_total", volume),
            FactSpec("derivatives.ce_oi_top1_fraction", concentration),
            FactSpec("derivatives.pe_oi_top1_fraction", concentration),
            FactSpec("derivatives.days_to_expiry", dte),
        ),
        freshness,
    )


def _context(
    evidence_id: str,
    evidence_type: EvidenceType,
    metric: str,
    value: str,
) -> ReferenceSpec:
    return ReferenceSpec(evidence_id, evidence_type, (FactSpec(metric, value),))


def scenarios() -> tuple[Scenario, ...]:
    """Return six immutable realistic acceptance profiles."""
    positional = Horizon(label="POSITIONAL", min_days=2, max_days=20)
    return (
        Scenario(
            code="A",
            title="Supportive positional opportunity",
            symbol="RELIANCE",
            instrument_type=InstrumentType.EQUITY,
            horizon=positional,
            trade_style=TradeStyle.POSITIONAL,
            references=(
                _baseline(CandidateClass.EARLY_OPPORTUNITY, "POSITIVE"),
                _technical(
                    stance="POSITIVE",
                    extension="NOT_EXTENDED",
                    room="SUFFICIENT",
                    participation="PRESENT",
                    volatility="MODERATE",
                ),
                _derivatives(
                    iv=22.0,
                    oi_pcr=1.3,
                    volume_pcr=1.1,
                    spread=1.5,
                    concentration=0.25,
                    dte=7,
                ),
                _context("relative", EvidenceType.RELATIVE_STRENGTH, "relative.stance", "POSITIVE"),
                _context("sector", EvidenceType.SECTOR, "sector.stance", "SUPPORTIVE"),
                _context("event", EvidenceType.NEWS, "event.proximity", "NONE"),
                _context(
                    "derivatives-opinion",
                    EvidenceType.DERIVATIVES,
                    "derivatives_context.stance",
                    "SUPPORTIVE",
                ),
            ),
            expected_derivatives=frozenset({"POSITIVE"}),
            expected_quality=frozenset({"STRONG", "GOOD"}),
            expected_risk=frozenset({"LOW", "MODERATE"}),
            required_reasons=frozenset(
                {
                    DerivativesReasonCode.DERIVATIVES_OI_SUPPORTIVE_CONTEXT.value,
                    OpportunityReasonCode.OPPORTUNITY_EARLY.value,
                }
            ),
        ),
        Scenario(
            code="B",
            title="Overextended / avoid-chase",
            symbol="HDFCBANK",
            instrument_type=InstrumentType.EQUITY,
            horizon=positional,
            trade_style=TradeStyle.POSITIONAL,
            references=(
                _baseline(CandidateClass.MATURE_AVOID_CHASE, "POSITIVE"),
                _technical(
                    stance="POSITIVE",
                    extension="EXTENDED",
                    room="LIMITED",
                    participation="PRESENT",
                    volatility="MODERATE",
                ),
                _derivatives(
                    iv=24.0,
                    oi_pcr=1.25,
                    volume_pcr=1.05,
                    spread=1.8,
                    concentration=0.3,
                    dte=8,
                ),
                _context(
                    "fundamental",
                    EvidenceType.FUNDAMENTAL,
                    "fundamental.stance",
                    "STRONG",
                ),
            ),
            expected_derivatives=frozenset({"POSITIVE"}),
            expected_quality=frozenset({"MIXED", "WEAK"}),
            expected_risk=frozenset({"HIGH", "CRITICAL"}),
            required_reasons=frozenset(
                {
                    OpportunityReasonCode.OPPORTUNITY_MATURE.value,
                    OpportunityReasonCode.OPPORTUNITY_EXTENDED.value,
                    RiskReasonCode.RISK_OVEREXTENDED.value,
                    RiskReasonCode.RISK_ROOM_LIMITED.value,
                }
            ),
        ),
        Scenario(
            code="C",
            title="High-IV event risk",
            symbol="KAYNES",
            instrument_type=InstrumentType.EQUITY,
            horizon=Horizon(label="DAY", min_days=0, max_days=1),
            trade_style=TradeStyle.DAY,
            references=(
                _baseline(CandidateClass.NO_TRADE, "CONFLICTED"),
                _technical(
                    stance="MIXED",
                    extension="NOT_EXTENDED",
                    room="SUFFICIENT",
                    participation="PRESENT",
                    volatility="ELEVATED",
                ),
                _derivatives(
                    iv=48.0,
                    oi_pcr=1.5,
                    volume_pcr=0.6,
                    spread=2.0,
                    concentration=0.35,
                    dte=1,
                ),
                _context("event", EvidenceType.NEWS, "event.proximity", "IMMINENT"),
                _context("event-type", EvidenceType.NEWS, "event.type", "EARNINGS"),
            ),
            expected_derivatives=frozenset({"MIXED", "NEUTRAL"}),
            expected_quality=frozenset({"MIXED", "WEAK"}),
            expected_risk=frozenset({"HIGH", "CRITICAL"}),
            required_reasons=frozenset(
                {
                    DerivativesReasonCode.DERIVATIVES_IV_ELEVATED.value,
                    RiskReasonCode.RISK_EVENT_GAP.value,
                }
            ),
            expect_contradiction=True,
        ),
        Scenario(
            code="D",
            title="Bullish underlying, conflicting derivatives",
            symbol="NIFTY",
            instrument_type=InstrumentType.INDEX,
            horizon=positional,
            trade_style=TradeStyle.POSITIONAL,
            references=(
                _baseline(CandidateClass.EARLY_OPPORTUNITY, "POSITIVE"),
                _technical(
                    stance="POSITIVE",
                    extension="NOT_EXTENDED",
                    room="LIMITED",
                    participation="PRESENT",
                    volatility="MODERATE",
                ),
                _derivatives(
                    iv=21.0,
                    oi_pcr=1.55,
                    volume_pcr=0.6,
                    spread=2.5,
                    concentration=0.68,
                    dte=4,
                ),
                _context("relative", EvidenceType.RELATIVE_STRENGTH, "relative.stance", "POSITIVE"),
                _context(
                    "derivatives-opinion",
                    EvidenceType.DERIVATIVES,
                    "derivatives_context.stance",
                    "ADVERSE",
                ),
                _context(
                    "contradiction",
                    EvidenceType.RISK,
                    "contradiction.derivatives",
                    "CONFLICTED",
                ),
            ),
            expected_derivatives=frozenset({"MIXED"}),
            expected_quality=frozenset({"MIXED", "WEAK"}),
            expected_risk=frozenset({"HIGH", "CRITICAL"}),
            required_reasons=frozenset(
                {
                    DerivativesReasonCode.DERIVATIVES_CONFLICTED.value,
                    OpportunityReasonCode.OPPORTUNITY_CROSS_DOMAIN_CONFLICT.value,
                    RiskReasonCode.CONTRADICTION_HIGH.value,
                }
            ),
            expect_contradiction=True,
        ),
        Scenario(
            code="E",
            title="Insufficient derivatives evidence",
            symbol="RELIANCE",
            instrument_type=InstrumentType.EQUITY,
            horizon=positional,
            trade_style=TradeStyle.POSITIONAL,
            references=(
                _baseline(CandidateClass.NO_TRADE, "NEUTRAL"),
                _technical(
                    stance="INSUFFICIENT_EVIDENCE",
                    extension="UNKNOWN",
                    room="UNKNOWN",
                    participation="UNKNOWN",
                    volatility="UNKNOWN",
                ),
                ReferenceSpec(
                    "derivatives",
                    EvidenceType.DERIVATIVES,
                    (FactSpec("derivatives.strike_count", 0),),
                    FreshnessState.STALE,
                ),
            ),
            expected_derivatives=frozenset(
                {AgentStance.INSUFFICIENT_EVIDENCE.value, AgentStance.ABSTAIN.value}
            ),
            expected_quality=frozenset({"INSUFFICIENT_EVIDENCE"}),
            expected_risk=frozenset({"INSUFFICIENT_EVIDENCE"}),
            required_reasons=frozenset(
                {DerivativesReasonCode.DERIVATIVES_EVIDENCE_INSUFFICIENT.value}
            ),
            expect_missing=True,
            coverage=0.25,
        ),
        Scenario(
            code="F",
            title="Plain equity without derivatives chain",
            symbol="ATHERENERG",
            instrument_type=InstrumentType.EQUITY,
            horizon=positional,
            trade_style=TradeStyle.POSITIONAL,
            references=(
                _baseline(CandidateClass.EARLY_OPPORTUNITY, "POSITIVE"),
                _technical(
                    stance="POSITIVE",
                    extension="NOT_EXTENDED",
                    room="SUFFICIENT",
                    participation="PRESENT",
                    volatility="MODERATE",
                ),
                _context("relative", EvidenceType.RELATIVE_STRENGTH, "relative.stance", "POSITIVE"),
            ),
            expected_derivatives=frozenset({AgentRunStatus.INSUFFICIENT_EVIDENCE.value}),
            expected_quality=frozenset({"GOOD", "STRONG"}),
            expected_risk=frozenset({"LOW", "MODERATE"}),
            required_reasons=frozenset({OpportunityReasonCode.OPPORTUNITY_EARLY.value}),
            expect_missing=True,
            coverage=0.7,
        ),
    )


def _fact(spec: FactSpec, reference_id: str, freshness: FreshnessState) -> EvidenceFact:
    return EvidenceFact(
        fact_id=f"{reference_id}:{spec.metric}",
        kind=EvidenceFactKind.FEATURE,
        metric_id=spec.metric,
        value=spec.value,
        as_of=FIXTURE_TIME,
        quality=DataQuality.GOOD,
        freshness=freshness,
        source_evidence=(f"fixture:{reference_id}",),
    )


def _reference(spec: ReferenceSpec, symbol: str) -> AgentEvidenceReference:
    facts = tuple(_fact(item, spec.evidence_id, spec.freshness) for item in spec.facts)
    payload = json.dumps(
        [item.model_dump(mode="json") for item in facts],
        sort_keys=True,
        separators=(",", ":"),
    )
    return AgentEvidenceReference(
        evidence_id=spec.evidence_id,
        evidence_type=spec.evidence_type,
        subject=symbol,
        producer_id="tiaf.a3-7.acceptance-fixture",
        producer_version="1.0",
        source=EvidenceSource.DERIVED,
        availability=(
            EvidenceStatus.STALE
            if spec.freshness is FreshnessState.STALE
            else EvidenceStatus.AVAILABLE
        ),
        quality=DataQuality.GOOD,
        freshness=spec.freshness,
        observed_at=FIXTURE_TIME,
        acquired_at=FIXTURE_TIME,
        checksum=hashlib.sha256(payload.encode()).hexdigest(),
        source_reference=f"a3.7-user-acceptance:{spec.evidence_id}",
        facts=facts,
    )


def _fingerprint(scenario: Scenario, references: tuple[AgentEvidenceReference, ...]) -> str:
    payload = {
        "code": scenario.code,
        "symbol": scenario.symbol,
        "instrument_type": scenario.instrument_type.value,
        "horizon": scenario.horizon.model_dump(mode="json"),
        "references": [item.model_dump(mode="json") for item in references],
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _request_and_pack(
    scenario: Scenario, specialist: SpecialistId
) -> tuple[AgentRequest, AgentEvidencePack]:
    references = tuple(_reference(item, scenario.symbol) for item in scenario.references)
    fingerprint = _fingerprint(scenario, references)
    request_id = f"a3.7-acceptance:{scenario.code}:{specialist.value.lower()}"
    missing = (
        (
            MissingEvidenceRequest(
                missing_request_id=f"{request_id}:missing:derivatives-chain",
                evidence_type=EvidenceType.DERIVATIVES,
                capability=AgentCapability.READ_DERIVATIVES,
                subject=scenario.symbol,
                reason="No complete fresh option-chain evidence is available",
                # The other specialists may still interpret bounded cash evidence.
                # A3.8 will later own cross-specialist missing-evidence orchestration.
                importance=EvidenceImportance.MATERIAL,
                requested_at=FIXTURE_TIME,
            ),
        )
        if scenario.expect_missing
        else ()
    )
    overall_freshness = (
        FreshnessState.STALE
        if any(item.freshness is FreshnessState.STALE for item in references)
        else FreshnessState.FRESH
    )
    baseline_id = f"a2.9:{scenario.code}:assessment"
    pack = AgentEvidencePack(
        pack_id=f"{request_id}:pack",
        request_id=request_id,
        subject=scenario.symbol,
        evidence_fingerprint=fingerprint,
        references=references,
        analysis_context_ids=(f"a2:{scenario.code}:context",),
        derivatives_evidence_ids=tuple(
            item.evidence_id
            for item in references
            if item.evidence_type is EvidenceType.DERIVATIVES
        ),
        deterministic_assessment_id=baseline_id,
        overall_quality=DataQuality.GOOD,
        overall_freshness=overall_freshness,
        evidence_coverage=scenario.coverage,
        missing_evidence=missing,
        created_at=FIXTURE_TIME,
    )
    request = AgentRequest(
        request_id=request_id,
        run_id=f"{request_id}:run",
        subject=scenario.symbol,
        instrument_type=scenario.instrument_type,
        horizon=scenario.horizon,
        specialist=specialist,
        purpose=AnalysisPurpose.OPPORTUNITY,
        trade_style=scenario.trade_style,
        analysis_mode=AnalysisMode.DETERMINISTIC_ONLY,
        task="Produce bounded A3.7 user-level interpretation from supplied evidence.",
        a2_context_ids=pack.analysis_context_ids,
        a2_evidence_ids=tuple(item.evidence_id for item in references),
        deterministic_baseline_reference=baseline_id,
        evidence_fingerprint=fingerprint,
        allowed_capabilities=(
            AgentCapability.READ_A2_EVIDENCE,
            AgentCapability.READ_DERIVATIVES,
        ),
        budget=AgentBudget(),
        created_at=FIXTURE_TIME,
    )
    return request, pack


def _structured_forbidden_values(value: Any, path: str = "root") -> tuple[str, ...]:
    violations: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).casefold().replace("-", "_")
            if normalized in _FORBIDDEN_KEYS:
                violations.append(f"{path}.{key}")
            violations.extend(_structured_forbidden_values(item, f"{path}.{key}"))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            violations.extend(_structured_forbidden_values(item, f"{path}[{index}]"))
    elif isinstance(value, str) and value.upper() in _FORBIDDEN_ACTION_VALUES:
        violations.append(f"{path}={value}")
    return tuple(violations)


def _opinion_state(record: AgentRunRecord) -> str:
    return record.opinion.stance.value if record.opinion is not None else record.status.value


def _run_scenario(runtime: AgentRuntime, scenario: Scenario) -> AcceptanceResult:
    records: list[AgentRunRecord] = []
    for specialist in _SPECIALISTS:
        request, pack = _request_and_pack(scenario, specialist)
        record = runtime.run(request, pack)
        replayed = load_agent_record_json(agent_record_json(record))
        assert replayed == record, f"{scenario.code}: record replay changed semantics"
        assert record.request.evidence_fingerprint == record.evidence_pack.evidence_fingerprint
        assert record.usage.llm_calls == 0
        assert record.usage.input_tokens == record.usage.output_tokens == 0
        assert record.usage.cost_units == 0
        assert _structured_forbidden_values(record.model_dump(mode="json")) == ()
        if record.opinion is not None:
            assert record.opinion.model_identity is None
            assert record.opinion.evidence_fingerprint == record.request.evidence_fingerprint
            assert record.opinion.confidence.policy_derived is not None
            assert all(claim.citations for claim in record.opinion.evidence_claims)
        records.append(record)

    derivatives_record, quality_record, risk_record = records
    derivatives = _opinion_state(derivatives_record)
    derivatives_detail = None
    if derivatives_record.opinion is not None:
        derivatives_detail = derivatives_context_assessment_from_opinion(derivatives_record.opinion)
        derivatives = derivatives_detail.stance.value
    assert quality_record.opinion is not None
    assert risk_record.opinion is not None
    quality_detail = opportunity_quality_assessment_from_opinion(quality_record.opinion)
    risk_detail = opportunity_risk_assessment_from_opinion(risk_record.opinion)
    details = (
        *((derivatives_detail,) if derivatives_detail is not None else ()),
        quality_detail,
        risk_detail,
    )
    assert all(
        "confidence_is_not_success_probability" in detail.confidence_basis
        and any("grouped" in item for item in detail.confidence_basis)
        for detail in details
    )

    assert derivatives in scenario.expected_derivatives
    assert quality_detail.quality_state.value in scenario.expected_quality
    assert risk_detail.risk_level.value in scenario.expected_risk
    reasons = tuple(
        dict.fromkeys(
            item
            for record in records
            if record.opinion is not None
            for item in record.opinion.reason_codes
        )
    )
    assert scenario.required_reasons <= set(reasons)
    contradictions = sum(len(detail.contradictions) for detail in details)
    missing = sum(
        len(record.opinion.missing_evidence)
        if record.opinion is not None
        else len(record.evidence_pack.missing_evidence)
        for record in records
    )
    assert (contradictions > 0) is scenario.expect_contradiction
    assert (missing > 0) is scenario.expect_missing
    confidence = tuple(
        (
            f"{record.specialist.value}={record.opinion.confidence.policy_derived.value:.4f}"
            if record.opinion is not None and record.opinion.confidence.policy_derived is not None
            else f"{record.specialist.value}=N/A"
        )
        for record in records
    )
    agreements = tuple(
        record.opinion.baseline_agreement.value
        if record.opinion is not None
        else BaselineAgreement.NOT_COMPARABLE.value
        for record in records
    )
    confidence_basis = tuple(
        dict.fromkeys(item for detail in details for item in detail.confidence_basis)
    )
    return AcceptanceResult(
        scenario=scenario,
        records=tuple(records),
        derivatives=derivatives,
        quality=quality_detail.quality_state.value,
        risk=risk_detail.risk_level.value,
        reasons=reasons,
        contradictions=contradictions,
        missing=missing,
        confidence=confidence,
        confidence_basis=confidence_basis,
        baseline_agreement=agreements,
    )


def run_acceptance() -> tuple[AcceptanceResult, ...]:
    """Run all scenarios through the public registry/runtime composition."""
    registry = AgentRegistry(
        (
            DerivativesContextSpecialist(),
            OpportunityQualitySpecialist(),
            OpportunityRiskSpecialist(),
        )
    )
    runtime = AgentRuntime(
        registry,
        wall_clock=lambda: FIXTURE_TIME,
        elapsed_clock=lambda: 0.0,
    )
    results: list[AcceptanceResult] = []
    for scenario in scenarios():
        try:
            results.append(_run_scenario(runtime, scenario))
        except AssertionError as exc:
            raise AssertionError(f"scenario {scenario.code}: {exc}") from exc
    return tuple(results)


def _print_results(results: tuple[AcceptanceResult, ...]) -> None:
    print("A3.7 deterministic user-level acceptance; no external or trading calls.")
    print("Case | Symbol | Instrument | Horizon | Derivatives | Quality | Risk | Result")
    for result in results:
        scenario = result.scenario
        print(
            " | ".join(
                (
                    scenario.code,
                    scenario.symbol,
                    scenario.instrument_type.value,
                    scenario.horizon.label or "-",
                    result.derivatives,
                    result.quality,
                    result.risk,
                    "PASS",
                )
            )
        )
        print(f"  reasons: {', '.join(result.reasons[:6]) or 'none'}")
        print(
            f"  contradictions/missing: {result.contradictions}/{result.missing}; "
            f"confidence: {', '.join(result.confidence)}"
        )
        print(f"  confidence basis: {', '.join(result.confidence_basis)}")
        print(f"  A2 agreement [derivatives/quality/risk]: {', '.join(result.baseline_agreement)}")
    print("Forbidden structured fields/actions: NONE")
    print("LLM calls/tokens/cost units: 0 / 0 / 0")
    print("Exact offline record replay and fingerprint preservation: PASS")
    print(f"Scenarios passed: {len(results)} / {len(scenarios())}")


def main() -> int:
    """Run, assert, and report the bounded deterministic acceptance suite."""
    try:
        results = run_acceptance()
    except (AssertionError, ValueError) as exc:
        print(f"A3.7 user-level acceptance failed: {exc}")
        return 2
    _print_results(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
