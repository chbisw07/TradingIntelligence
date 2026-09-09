"""A3.6 Macro Context specialist synthetic matrix."""

import pytest

from tiaf.agents import (
    AgentEvidenceReference,
    AgentRunStatus,
    AgentStance,
    EvidenceFactParameter,
    SpecialistId,
)
from tiaf.agents.specialists import (
    CommodityContextState,
    CurrencyState,
    MacroSpecialist,
    MacroVolatilityRegime,
    MarketRiskRegime,
    RateRegime,
    SubjectSensitivityState,
    macro_assessment_from_opinion,
)
from tiaf.contracts import EvidenceType

from ._contextual_support import fact, pack, reference, request


def macro_reference(
    *,
    risk: float = 0.7,
    market_return: float = 2.0,
    volatility: float = 0.4,
    rate_change: float | None = None,
    currency_change: float | None = None,
    commodity_change: float | None = None,
    sensitivity: tuple[str, str] | None = ("commodity.crude", "HARMED_BY_RISE"),
) -> AgentEvidenceReference:
    state = (EvidenceFactParameter(name="context_kind", value="STATE"),)
    values = [
        fact("macro.market_risk.score", risk, parameters=state),
        fact("macro.market_index.return_percent", market_return, unit="%", parameters=state),
        fact("macro.volatility.percentile", volatility, unit="fraction", parameters=state),
    ]
    if rate_change is not None:
        values.append(
            fact(
                "macro.rates.change_bps",
                rate_change,
                parameters=(
                    *state,
                    EvidenceFactParameter(name="driver_id", value="interest_rates.policy"),
                ),
            )
        )
    if currency_change is not None:
        values.append(
            fact(
                "macro.currency.change_percent",
                currency_change,
                parameters=(*state, EvidenceFactParameter(name="driver_id", value="currency.inr")),
            )
        )
    if commodity_change is not None:
        values.append(
            fact(
                "macro.commodity.crude.change_percent",
                commodity_change,
                parameters=(
                    *state,
                    EvidenceFactParameter(name="driver_id", value="commodity.crude"),
                ),
            )
        )
    if sensitivity is not None:
        values.append(
            fact(
                "macro.sensitivity.commodities",
                sensitivity[1],
                fact_id="macro-sensitivity",
                parameters=(EvidenceFactParameter(name="driver_id", value=sensitivity[0]),),
            )
        )
    return reference(
        "macro-evidence", EvidenceType.MACRO, tuple(values), metadata={"market": "INDIA"}
    )


@pytest.mark.parametrize(
    ("risk", "market_return", "stance", "regime"),
    (
        (0.8, 2.0, AgentStance.POSITIVE, MarketRiskRegime.RISK_ON),
        (-0.8, -2.0, AgentStance.NEGATIVE, MarketRiskRegime.RISK_OFF),
        (0.8, -2.0, AgentStance.MIXED, MarketRiskRegime.MIXED),
    ),
)
def test_market_risk_regimes(
    risk: float, market_return: float, stance: AgentStance, regime: MarketRiskRegime
) -> None:
    opinion = MacroSpecialist().analyze(
        request(SpecialistId.MACRO),
        pack((macro_reference(risk=risk, market_return=market_return),)),
    )
    assert macro_assessment_from_opinion(opinion).market_risk_regime is regime
    assert opinion.stance is stance


def test_risk_off_with_extreme_volatility_is_market_stress() -> None:
    opinion = MacroSpecialist().analyze(
        request(SpecialistId.MACRO),
        pack((macro_reference(risk=-0.9, market_return=-3.0, volatility=0.98),)),
    )
    detail = macro_assessment_from_opinion(opinion)
    assert detail.market_risk_regime is MarketRiskRegime.STRESS
    assert detail.volatility_regime is MacroVolatilityRegime.EXTREME
    assert opinion.stance is AgentStance.NEGATIVE


def test_sensitivity_mapping_alone_is_not_macro_state_evidence() -> None:
    state = (EvidenceFactParameter(name="context_kind", value="STATE"),)
    sensitivity_only = reference(
        "macro-mapping-only",
        EvidenceType.MACRO,
        (
            fact(
                "macro.sensitivity.currency",
                "BENEFITS_FROM_RISE",
                parameters=(
                    *state,
                    EvidenceFactParameter(name="driver_id", value="currency.inr"),
                ),
            ),
        ),
    )
    opinion = MacroSpecialist().analyze(
        request(SpecialistId.MACRO), pack((sensitivity_only,))
    )
    assert opinion.status is AgentRunStatus.INSUFFICIENT_EVIDENCE
    assert opinion.stance is AgentStance.INSUFFICIENT_EVIDENCE


@pytest.mark.parametrize(
    ("change", "state"), ((50.0, RateRegime.TIGHTENING), (-50.0, RateRegime.EASING))
)
def test_rate_regime_is_separate_from_subject_impact(change: float, state: RateRegime) -> None:
    opinion = MacroSpecialist().analyze(
        request(SpecialistId.MACRO), pack((macro_reference(rate_change=change),))
    )
    assert macro_assessment_from_opinion(opinion).rate_regime is state


@pytest.mark.parametrize(
    ("change", "state"), ((2.0, CurrencyState.APPRECIATING), (-2.0, CurrencyState.DEPRECIATING))
)
def test_currency_state(change: float, state: CurrencyState) -> None:
    opinion = MacroSpecialist().analyze(
        request(SpecialistId.MACRO), pack((macro_reference(currency_change=change),))
    )
    assert macro_assessment_from_opinion(opinion).currency_context is state


@pytest.mark.parametrize(
    ("sensitivity", "expected"),
    (
        ("HARMED_BY_RISE", CommodityContextState.ADVERSE),
        ("BENEFITS_FROM_RISE", CommodityContextState.FAVORABLE),
    ),
)
def test_commodity_impact_requires_explicit_sensitivity(
    sensitivity: str, expected: CommodityContextState
) -> None:
    opinion = MacroSpecialist().analyze(
        request(SpecialistId.MACRO),
        pack(
            (macro_reference(commodity_change=4.0, sensitivity=("commodity.crude", sensitivity)),)
        ),
    )
    assert macro_assessment_from_opinion(opinion).commodity_context is expected


def test_unknown_subject_sensitivity_is_insufficient_not_neutral() -> None:
    opinion = MacroSpecialist().analyze(
        request(SpecialistId.MACRO),
        pack((macro_reference(commodity_change=4.0, sensitivity=None),)),
    )
    detail = macro_assessment_from_opinion(opinion)
    assert detail.subject_sensitivity is SubjectSensitivityState.MAPPING_REQUIRED
    assert opinion.stance is AgentStance.INSUFFICIENT_EVIDENCE
    assert "MACRO_SENSITIVITY_UNKNOWN" in opinion.reason_codes


def test_conflicting_macro_impacts_are_preserved() -> None:
    opinion = MacroSpecialist().analyze(
        request(SpecialistId.MACRO),
        pack((macro_reference(risk=0.8, market_return=2.0, commodity_change=4.0),)),
    )
    assert opinion.stance is AgentStance.MIXED
    assert macro_assessment_from_opinion(opinion).contradictions
    assert "MACRO_CONFLICT" in opinion.reason_codes


def test_macro_specialist_is_no_llm_and_all_claims_are_cited() -> None:
    evidence = pack((macro_reference(),))
    opinion = MacroSpecialist().analyze(request(SpecialistId.MACRO), evidence)
    assert opinion.usage.llm_calls == opinion.usage.input_tokens == opinion.usage.output_tokens == 0
    assert opinion.usage.cost_units == 0
    supplied = {item.evidence_id for item in evidence.references}
    assert {
        citation.evidence_id for claim in opinion.evidence_claims for citation in claim.citations
    } <= supplied
