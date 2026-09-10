"""A3.7 deterministic acceptance scenarios and ownership boundaries."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from pydantic import JsonValue

from tiaf.agents import (
    AgentBudget,
    AgentCapability,
    AgentEvidencePack,
    AgentEvidenceReference,
    AgentRequest,
    AgentRunStatus,
    AgentStance,
    AnalysisMode,
    BaselineAgreement,
    EvidenceFact,
    EvidenceFactKind,
    SpecialistId,
)
from tiaf.agents.registry import AgentRegistry
from tiaf.agents.runtime import AgentRuntime
from tiaf.agents.serialization import agent_record_json, load_agent_record_json
from tiaf.agents.specialists.opportunity import (
    CrowdingState,
    DerivativesContextSpecialist,
    DerivativesPositioningState,
    DerivativesReasonCode,
    DerivativesVolatilityState,
    OpportunityMaturityState,
    OpportunityQualitySpecialist,
    OpportunityQualityState,
    OpportunityRiskLevel,
    OpportunityRiskSpecialist,
    RemainingRoomQuality,
    RiskReasonCode,
    derivatives_context_assessment_from_opinion,
    opportunity_quality_assessment_from_opinion,
    opportunity_risk_assessment_from_opinion,
)
from tiaf.baseline.enums import CandidateClass
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

NOW = datetime(2026, 9, 10, 14, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
FINGERPRINT = "d" * 64
BASELINE_ID = "a2-baseline-a37"


def fact(
    metric: str,
    value: str | int | float | bool,
    *,
    fact_id: str | None = None,
) -> EvidenceFact:
    return EvidenceFact(
        fact_id=fact_id or f"fact:{metric}",
        kind=EvidenceFactKind.FEATURE,
        metric_id=metric,
        value=value,
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
    freshness: FreshnessState = FreshnessState.FRESH,
) -> AgentEvidenceReference:
    return AgentEvidenceReference(
        evidence_id=evidence_id,
        evidence_type=evidence_type,
        subject="RELIANCE",
        producer_id="test.a37",
        producer_version="1.0",
        source=EvidenceSource.DERIVED,
        availability=(
            EvidenceStatus.STALE if freshness is FreshnessState.STALE else EvidenceStatus.AVAILABLE
        ),
        quality=DataQuality.GOOD,
        freshness=freshness,
        observed_at=NOW,
        acquired_at=NOW,
        checksum=f"checksum:{evidence_id}",
        source_reference=f"fixture:{evidence_id}",
        facts=tuple(item.model_copy(update={"freshness": freshness}) for item in facts),
    )


def pack(
    references: tuple[AgentEvidenceReference, ...],
    *,
    freshness: FreshnessState = FreshnessState.FRESH,
    coverage: float = 1.0,
) -> AgentEvidencePack:
    return AgentEvidencePack(
        pack_id="a37-pack",
        request_id="a37-request",
        subject="RELIANCE",
        evidence_fingerprint=FINGERPRINT,
        references=references,
        analysis_context_ids=("a2-context",),
        derivatives_evidence_ids=tuple(
            item.evidence_id
            for item in references
            if item.evidence_type is EvidenceType.DERIVATIVES
        ),
        deterministic_assessment_id=BASELINE_ID,
        overall_quality=DataQuality.GOOD,
        overall_freshness=freshness,
        evidence_coverage=coverage,
        created_at=NOW,
    )


def request(
    specialist: SpecialistId,
    *,
    instrument: InstrumentType = InstrumentType.EQUITY,
    style: TradeStyle = TradeStyle.POSITIONAL,
    horizon: Horizon | None = None,
) -> AgentRequest:
    capabilities: tuple[AgentCapability, ...] = (AgentCapability.READ_A2_EVIDENCE,)
    if specialist is SpecialistId.DERIVATIVES_CONTEXT:
        capabilities = (*capabilities, AgentCapability.READ_DERIVATIVES)
    metadata: dict[str, JsonValue] = {}
    if instrument is InstrumentType.CALL_OPTION:
        metadata["underlying_instrument_type"] = InstrumentType.EQUITY.value
    elif instrument is InstrumentType.PUT_OPTION:
        metadata["underlying_instrument_type"] = InstrumentType.INDEX.value
    return AgentRequest(
        request_id="a37-request",
        run_id=f"run:{specialist.value.lower()}:{instrument.value.lower()}",
        subject="RELIANCE",
        instrument_type=instrument,
        horizon=horizon or Horizon(label="POSITIONAL", min_days=2, max_days=20),
        specialist=specialist,
        purpose=AnalysisPurpose.OPPORTUNITY,
        trade_style=style,
        analysis_mode=AnalysisMode.DETERMINISTIC_ONLY,
        task="Interpret supplied evidence without execution authority.",
        a2_context_ids=("a2-context",),
        a2_evidence_ids=("a2-evidence",),
        deterministic_baseline_reference=BASELINE_ID,
        evidence_fingerprint=FINGERPRINT,
        allowed_capabilities=capabilities,
        budget=AgentBudget(),
        created_at=NOW,
        metadata=metadata,
    )


def derivatives_reference(
    *,
    iv: float = 22.0,
    oi_pcr: float = 1.3,
    volume_pcr: float = 1.1,
    spread: float = 1.5,
    volume: int = 10_000,
    concentration: float = 0.3,
    dte: int = 7,
    extra_iv_fields: int = 0,
    freshness: FreshnessState = FreshnessState.FRESH,
) -> AgentEvidenceReference:
    values = [
        fact("derivatives.atm_mean_iv", iv),
        fact("derivatives.oi_put_call_ratio", oi_pcr),
        fact("derivatives.volume_put_call_ratio", volume_pcr),
        fact("derivatives.atm_ce_bid_ask_spread_percent", spread),
        fact("derivatives.atm_pe_bid_ask_spread_percent", spread),
        fact("derivatives.ce_volume_total", volume),
        fact("derivatives.pe_volume_total", volume),
        fact("derivatives.ce_oi_top1_fraction", concentration),
        fact("derivatives.pe_oi_top1_fraction", concentration),
        fact("derivatives.days_to_expiry", dte),
    ]
    for index in range(extra_iv_fields):
        values.append(
            fact(
                "derivatives.atm_ce_iv" if index % 2 == 0 else "derivatives.atm_pe_iv",
                iv,
                fact_id=f"fact:extra-iv:{index}",
            )
        )
    return reference(
        "derivatives-evidence",
        EvidenceType.DERIVATIVES,
        tuple(values),
        freshness=freshness,
    )


def baseline_reference(
    candidate: CandidateClass = CandidateClass.EARLY_OPPORTUNITY,
    direction: str = "POSITIVE",
) -> AgentEvidenceReference:
    return reference(
        "baseline-evidence",
        EvidenceType.TECHNICAL,
        (
            fact("baseline.candidate_class", candidate.value),
            fact("baseline.direction", direction),
            fact("baseline.opportunity_score", 72.0),
        ),
    )


def context_reference(
    evidence_id: str,
    evidence_type: EvidenceType,
    metric: str,
    value: str,
) -> AgentEvidenceReference:
    return reference(evidence_id, evidence_type, (fact(metric, value),))


def test_scenario_a_supportive_derivatives_context_is_positive_and_cited() -> None:
    evidence = pack((derivatives_reference(), baseline_reference()))
    opinion = DerivativesContextSpecialist().analyze(
        request(SpecialistId.DERIVATIVES_CONTEXT), evidence
    )
    detail = derivatives_context_assessment_from_opinion(opinion)

    assert opinion.stance is AgentStance.POSITIVE
    assert detail.volatility_state is DerivativesVolatilityState.MODERATE
    assert detail.positioning_state is DerivativesPositioningState.SUPPORTIVE_CONTEXT
    assert DerivativesReasonCode.DERIVATIVES_LIQUIDITY_ADEQUATE in detail.reason_codes
    assert opinion.usage.llm_calls == opinion.usage.input_tokens == 0
    assert opinion.usage.output_tokens == 0 and opinion.usage.cost_units == 0
    assert opinion.evidence_claims
    assert all(claim.citations for claim in opinion.evidence_claims)


def test_scenario_b_high_iv_is_risk_context_not_bearish_direction() -> None:
    evidence = pack((derivatives_reference(iv=48.0, dte=1), baseline_reference()))
    opinion = DerivativesContextSpecialist().analyze(
        request(SpecialistId.DERIVATIVES_CONTEXT), evidence
    )
    detail = derivatives_context_assessment_from_opinion(opinion)

    assert detail.volatility_state is DerivativesVolatilityState.ELEVATED
    assert DerivativesReasonCode.DERIVATIVES_IV_ELEVATED in detail.reason_codes
    assert opinion.stance is AgentStance.POSITIVE
    assert "probability" not in opinion.summary.casefold()


def test_scenario_c_pcr_conflict_and_concentration_are_preserved() -> None:
    evidence = pack(
        (
            derivatives_reference(oi_pcr=1.5, volume_pcr=0.6, concentration=0.7, spread=4.0),
            baseline_reference(),
        )
    )
    opinion = DerivativesContextSpecialist().analyze(
        request(SpecialistId.DERIVATIVES_CONTEXT), evidence
    )
    detail = derivatives_context_assessment_from_opinion(opinion)

    assert opinion.stance is AgentStance.MIXED
    assert detail.positioning_state is DerivativesPositioningState.CONFLICTED
    assert detail.crowding_state is CrowdingState.CONCENTRATED
    assert detail.contradictions[0].code == "DERIVATIVES_PCR_CONFLICT"


def test_pcr_without_underlying_direction_is_not_a_directional_oracle() -> None:
    evidence = pack((derivatives_reference(oi_pcr=1.8),))
    opinion = DerivativesContextSpecialist().analyze(
        request(SpecialistId.DERIVATIVES_CONTEXT), evidence
    )
    detail = derivatives_context_assessment_from_opinion(opinion)

    assert detail.positioning_state is DerivativesPositioningState.BALANCED
    assert opinion.stance is AgentStance.NEUTRAL


def test_max_pain_fact_is_context_not_a_price_or_direction_oracle() -> None:
    base = derivatives_reference()
    with_max_pain = base.model_copy(
        update={
            "facts": (
                *base.facts,
                fact("derivatives.max_pain_distance_percent", -18.0),
            )
        }
    )
    opinion = DerivativesContextSpecialist().analyze(
        request(SpecialistId.DERIVATIVES_CONTEXT),
        pack((with_max_pain, baseline_reference())),
    )

    assert opinion.stance is AgentStance.POSITIVE
    assert "oracle" in " ".join(opinion.caveats).casefold()
    assert all("target" not in claim.statement.casefold() for claim in opinion.evidence_claims)


def test_correlated_iv_fields_do_not_inflate_policy_confidence() -> None:
    base = pack((derivatives_reference(extra_iv_fields=0), baseline_reference()))
    expanded = pack((derivatives_reference(extra_iv_fields=8), baseline_reference()))
    specialist = DerivativesContextSpecialist()

    first = specialist.analyze(request(SpecialistId.DERIVATIVES_CONTEXT), base)
    second = specialist.analyze(request(SpecialistId.DERIVATIVES_CONTEXT), expanded)

    assert first.confidence.policy_derived is not None
    assert second.confidence.policy_derived is not None
    assert first.confidence.policy_derived.value == second.confidence.policy_derived.value


def test_scenario_e_missing_and_stale_derivatives_evidence_abstains_or_is_insufficient() -> None:
    sparse = reference(
        "sparse-derivatives",
        EvidenceType.DERIVATIVES,
        (fact("derivatives.atm_ce_bid_ask_spread_percent", 12.0),),
    )
    insufficient = DerivativesContextSpecialist().analyze(
        request(SpecialistId.DERIVATIVES_CONTEXT), pack((sparse,))
    )
    stale_reference = derivatives_reference(freshness=FreshnessState.STALE)
    stale_baseline = baseline_reference().model_copy(
        update={
            "availability": EvidenceStatus.STALE,
            "freshness": FreshnessState.STALE,
            "facts": tuple(
                item.model_copy(update={"freshness": FreshnessState.STALE})
                for item in baseline_reference().facts
            ),
        }
    )
    stale = DerivativesContextSpecialist().analyze(
        request(SpecialistId.DERIVATIVES_CONTEXT),
        pack((stale_reference, stale_baseline), freshness=FreshnessState.STALE),
    )

    assert insufficient.status is AgentRunStatus.INSUFFICIENT_EVIDENCE
    assert insufficient.stance is AgentStance.INSUFFICIENT_EVIDENCE
    assert insufficient.missing_evidence
    assert stale.status is AgentRunStatus.ABSTAINED
    assert stale.stance is AgentStance.ABSTAIN


def test_scenario_d_mature_extended_limited_room_is_weak_without_action() -> None:
    evidence = pack(
        (
            baseline_reference(CandidateClass.MATURE_AVOID_CHASE),
            context_reference(
                "technical-context", EvidenceType.TECHNICAL, "technical.extension_state", "EXTENDED"
            ).model_copy(
                update={
                    "facts": (
                        fact("technical.extension_state", "EXTENDED"),
                        fact("technical.remaining_room", "LIMITED"),
                    )
                }
            ),
            context_reference(
                "relative-context", EvidenceType.RELATIVE_STRENGTH, "relative.stance", "POSITIVE"
            ),
        )
    )
    opinion = OpportunityQualitySpecialist().analyze(
        request(SpecialistId.OPPORTUNITY_QUALITY), evidence
    )
    detail = opportunity_quality_assessment_from_opinion(opinion)

    assert detail.quality_state in {OpportunityQualityState.WEAK, OpportunityQualityState.MIXED}
    assert detail.maturity_state is OpportunityMaturityState.MATURE
    assert detail.remaining_room is RemainingRoomQuality.LIMITED
    serialized = opinion.model_dump_json().casefold()
    assert all(token not in serialized for token in ('"action"', '"strike"', '"quantity"'))


def test_quality_cross_domain_support_and_conflict_are_explicit() -> None:
    evidence = pack(
        (
            baseline_reference(),
            context_reference(
                "technical-context",
                EvidenceType.TECHNICAL,
                "technical.extension_state",
                "NOT_EXTENDED",
            ),
            context_reference(
                "relative-context", EvidenceType.RELATIVE_STRENGTH, "relative.stance", "POSITIVE"
            ),
            context_reference("sector-context", EvidenceType.SECTOR, "sector.stance", "NEGATIVE"),
        )
    )
    opinion = OpportunityQualitySpecialist().analyze(
        request(SpecialistId.OPPORTUNITY_QUALITY), evidence
    )
    detail = opportunity_quality_assessment_from_opinion(opinion)

    assert detail.quality_state is OpportunityQualityState.MIXED
    assert detail.supportive_families == ("RELATIVE",)
    assert detail.adverse_families == ("SECTOR",)
    assert detail.contradictions


def test_early_opportunity_with_broad_support_is_strong_and_agrees_with_a2() -> None:
    evidence = pack(
        (
            baseline_reference(),
            context_reference(
                "technical-context",
                EvidenceType.TECHNICAL,
                "technical.extension_state",
                "NOT_EXTENDED",
            ),
            context_reference(
                "relative-context",
                EvidenceType.RELATIVE_STRENGTH,
                "relative.stance",
                "POSITIVE",
            ),
            context_reference("sector-context", EvidenceType.SECTOR, "sector.stance", "SUPPORTIVE"),
        )
    )
    opinion = OpportunityQualitySpecialist().analyze(
        request(SpecialistId.OPPORTUNITY_QUALITY), evidence
    )
    detail = opportunity_quality_assessment_from_opinion(opinion)

    assert detail.quality_state is OpportunityQualityState.STRONG
    assert detail.maturity_state is OpportunityMaturityState.EARLY
    assert opinion.baseline_agreement is BaselineAgreement.AGREES


def test_opportunity_risk_groups_extension_room_event_and_context() -> None:
    technical = reference(
        "technical-risk",
        EvidenceType.TECHNICAL,
        (
            fact("technical.extension_state", "EXTENDED"),
            fact("technical.remaining_room", "LIMITED"),
            fact("technical.participation_state", "WEAK"),
        ),
    )
    evidence = pack(
        (
            baseline_reference(CandidateClass.MATURE_AVOID_CHASE),
            technical,
            context_reference("event-risk", EvidenceType.NEWS, "event.proximity", "IMMINENT"),
            context_reference("macro-risk", EvidenceType.MACRO, "macro.stance", "RISK_OFF"),
        )
    )
    opinion = OpportunityRiskSpecialist().analyze(request(SpecialistId.OPPORTUNITY_RISK), evidence)
    detail = opportunity_risk_assessment_from_opinion(opinion)

    assert detail.risk_level is OpportunityRiskLevel.CRITICAL
    assert set(detail.active_risk_families) >= {
        "EXTENSION",
        "ROOM",
        "PARTICIPATION",
        "EVENT",
        "SECTOR_MACRO",
    }
    assert RiskReasonCode.RISK_EVENT_GAP in detail.reason_codes
    assert opinion.usage.llm_calls == 0 and opinion.model_identity is None


def test_implicit_mixed_context_cites_the_family_that_exposes_conflict() -> None:
    evidence = pack(
        (
            baseline_reference(CandidateClass.NO_TRADE, direction="CONFLICTED"),
            reference(
                "technical-mixed",
                EvidenceType.TECHNICAL,
                (
                    fact("technical.extension_state", "NOT_EXTENDED"),
                    fact("technical.volatility_state", "MIXED"),
                ),
            ),
            context_reference("event-context", EvidenceType.NEWS, "event.proximity", "NONE"),
        )
    )
    opinion = OpportunityRiskSpecialist().analyze(request(SpecialistId.OPPORTUNITY_RISK), evidence)
    detail = opportunity_risk_assessment_from_opinion(opinion)

    assert detail.contradictions
    assert set(detail.contradictions[0].evidence_ids) == {
        "baseline-evidence",
        "technical-mixed",
    }


def test_unknown_state_placeholders_do_not_count_as_risk_coverage() -> None:
    evidence = pack(
        (
            baseline_reference(CandidateClass.NO_TRADE, direction="NEUTRAL"),
            reference(
                "technical-unknown",
                EvidenceType.TECHNICAL,
                (
                    fact("technical.extension_state", "UNKNOWN"),
                    fact("technical.remaining_room", "UNKNOWN"),
                    fact("technical.participation_state", "UNKNOWN"),
                    fact("technical.volatility_state", "UNKNOWN"),
                ),
            ),
        ),
        coverage=0.25,
    )
    opinion = OpportunityRiskSpecialist().analyze(request(SpecialistId.OPPORTUNITY_RISK), evidence)
    detail = opportunity_risk_assessment_from_opinion(opinion)

    assert opinion.status is AgentRunStatus.INSUFFICIENT_EVIDENCE
    assert detail.risk_level is OpportunityRiskLevel.INSUFFICIENT_EVIDENCE
    assert detail.evidence_families == ("BASELINE",)


def test_horizon_awareness_limits_fundamental_risk_materiality_for_day_style() -> None:
    references = (
        baseline_reference(),
        context_reference(
            "technical-risk", EvidenceType.TECHNICAL, "technical.extension_state", "NOT_EXTENDED"
        ),
        context_reference(
            "fundamental-risk",
            EvidenceType.FUNDAMENTAL,
            "fundamental.balance_sheet",
            "FRAGILE",
        ),
    )
    evidence = pack(references)
    day = OpportunityRiskSpecialist().analyze(
        request(
            SpecialistId.OPPORTUNITY_RISK,
            style=TradeStyle.DAY,
            horizon=Horizon(label="DAY", min_days=0, max_days=1),
        ),
        evidence,
    )
    medium = OpportunityRiskSpecialist().analyze(
        request(
            SpecialistId.OPPORTUNITY_RISK,
            horizon=Horizon(label="MEDIUM", min_days=60, max_days=180),
        ),
        evidence,
    )

    assert "FUNDAMENTAL" not in opportunity_risk_assessment_from_opinion(day).active_risk_families
    assert "FUNDAMENTAL" in opportunity_risk_assessment_from_opinion(medium).active_risk_families


@pytest.mark.parametrize(
    "instrument",
    [
        InstrumentType.EQUITY,
        InstrumentType.INDEX,
        InstrumentType.FUTURE,
        InstrumentType.CALL_OPTION,
        InstrumentType.PUT_OPTION,
    ],
)
def test_scenario_f_instrument_type_is_preserved_without_assuming_equal_fields(
    instrument: InstrumentType,
) -> None:
    evidence = pack((derivatives_reference(), baseline_reference()))
    opinion = DerivativesContextSpecialist().analyze(
        request(SpecialistId.DERIVATIVES_CONTEXT, instrument=instrument), evidence
    )

    detail = derivatives_context_assessment_from_opinion(opinion)
    assert detail.instrument_type is instrument
    if instrument is InstrumentType.CALL_OPTION:
        assert detail.instrument_context == "STOCK_OPTION_UNDERLYING"
    if instrument is InstrumentType.PUT_OPTION:
        assert detail.instrument_context == "INDEX_OPTION_UNDERLYING"


def test_option_context_rejects_missing_underlying_identity() -> None:
    invalid = request(SpecialistId.DERIVATIVES_CONTEXT).model_copy(
        update={"instrument_type": InstrumentType.CALL_OPTION, "metadata": {}}
    )
    with pytest.raises(ValueError, match="explicit EQUITY or INDEX underlying"):
        DerivativesContextSpecialist().analyze(
            invalid, pack((derivatives_reference(), baseline_reference()))
        )


def test_runtime_replay_preserves_fingerprint_opinion_and_zero_usage() -> None:
    evidence = pack((derivatives_reference(), baseline_reference()))
    runtime = AgentRuntime(AgentRegistry((DerivativesContextSpecialist(),)))
    record = runtime.run(request(SpecialistId.DERIVATIVES_CONTEXT), evidence)
    replayed = load_agent_record_json(agent_record_json(record))

    assert replayed == record
    assert replayed.evidence_pack.evidence_fingerprint == FINGERPRINT
    assert replayed.opinion is not None
    assert replayed.opinion.evidence_fingerprint == FINGERPRINT
    assert replayed.usage.llm_calls == 0


def test_specialist_source_has_no_provider_model_or_execution_imports() -> None:
    root = Path("src/tiaf/agents/specialists/opportunity")
    source = "\n".join(path.read_text() for path in root.glob("*.py"))

    assert "tiaf.data.providers" not in source
    assert "OptionExpression" not in source
    assert "PositionAction" not in source
    assert "OpportunityAction" not in source
    assert "ReasoningGateway" not in source
    assert "requests" not in source and "httpx" not in source
