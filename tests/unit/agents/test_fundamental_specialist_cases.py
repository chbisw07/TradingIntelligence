"""A3.4 deterministic company archetypes and contradiction behavior."""

from typing import Any

from tiaf.agents import AgentOpinionV2, AgentRunStatus, AgentStance
from tiaf.agents.specialists.fundamental import (
    BalanceSheetState,
    CapitalEfficiencyState,
    CashFlowState,
    CompanyQualityState,
    FundamentalAssessment,
    FundamentalSpecialist,
    GrowthState,
    MarginState,
    OwnershipEvidenceState,
    ProfitabilityState,
    ValuationState,
    fundamental_assessment_from_opinion,
)
from tiaf.contracts import DataQuality, FreshnessState
from tiaf.fundamentals import FundamentalMetric

from ._fundamental_support import fundamental_agent_request, fundamental_pack


def analyze(**changes: Any) -> tuple[AgentOpinionV2, FundamentalAssessment]:
    pack = fundamental_pack(**changes)
    opinion = FundamentalSpecialist().analyze(fundamental_agent_request(pack), pack)
    return opinion, fundamental_assessment_from_opinion(opinion)


def test_high_quality_profitable_growth_is_positive_and_dimensional() -> None:
    opinion, detail = analyze()

    assert opinion.stance is AgentStance.POSITIVE
    assert opinion.status is AgentRunStatus.SUCCESS
    assert detail.growth_state is GrowthState.STRONG_GROWTH
    assert detail.profitability_state is ProfitabilityState.STRONG
    assert detail.balance_sheet_state is BalanceSheetState.VERY_STRONG
    assert detail.cash_flow_state is CashFlowState.STRONG
    assert detail.company_quality is CompanyQualityState.HIGH_QUALITY
    assert detail.ownership_governance_evidence_state is OwnershipEvidenceState.AVAILABLE


def test_strong_growth_and_extreme_valuation_remain_a_visible_conflict() -> None:
    opinion, detail = analyze(
        overrides={FundamentalMetric.VALUATION_HISTORY_PERCENTILE: 96.0}
    )

    assert opinion.stance is AgentStance.MIXED
    assert detail.valuation_state is ValuationState.VERY_EXPENSIVE
    assert any(item.code == "QUALITY_VALUATION_CONFLICT" for item in detail.contradictions)
    assert "VALUATION_ELEVATED" in opinion.reason_codes


def test_low_growth_and_cheap_valuation_are_reported_without_threshold_fitting() -> None:
    opinion, detail = analyze(
        overrides={
            FundamentalMetric.REVENUE_GROWTH_YOY: 0.0,
            FundamentalMetric.PROFIT_GROWTH_YOY: 0.0,
            FundamentalMetric.REVENUE_CAGR_3Y: 0.0,
            FundamentalMetric.PROFIT_CAGR_3Y: 0.0,
            FundamentalMetric.VALUATION_HISTORY_PERCENTILE: 10.0,
        }
    )

    assert detail.growth_state is GrowthState.STAGNANT
    assert detail.valuation_state is ValuationState.CHEAP
    assert opinion.stance is AgentStance.POSITIVE


def test_leveraged_but_improving_company_is_not_flattened_to_positive() -> None:
    opinion, detail = analyze(
        overrides={FundamentalMetric.DEBT_EQUITY: 1.8}
    )

    assert detail.balance_sheet_state is BalanceSheetState.LEVERAGED
    assert detail.capital_efficiency_state is CapitalEfficiencyState.LEVERAGE_DRIVEN
    assert detail.company_quality is CompanyQualityState.MIXED
    assert opinion.stance is AgentStance.MIXED


def test_deteriorating_margins_conflict_with_growth() -> None:
    opinion, detail = analyze(
        overrides={FundamentalMetric.MARGIN_CHANGE_PP: -3.0}
    )

    assert detail.margin_state is MarginState.CONTRACTING
    assert detail.profitability_state is ProfitabilityState.DETERIORATING
    assert any(item.code == "GROWTH_MARGIN_DIVERGENCE" for item in detail.contradictions)
    assert opinion.stance is AgentStance.MIXED


def test_accounting_profit_with_weak_cash_flow_is_explicitly_negative() -> None:
    opinion, detail = analyze(
        overrides={
            FundamentalMetric.CASH_CONVERSION: 0.25,
            FundamentalMetric.FREE_CASH_FLOW: -20.0,
            FundamentalMetric.FCF_POSITIVE_FRACTION: 0.2,
        }
    )

    assert detail.cash_flow_state is CashFlowState.WEAK
    assert detail.company_quality is CompanyQualityState.DETERIORATING
    assert any("PROFIT_CASHFLOW" in item.code for item in detail.contradictions)
    assert opinion.stance is AgentStance.NEGATIVE


def test_strong_roce_with_high_leverage_is_not_rewarded_blindly() -> None:
    opinion, detail = analyze(
        overrides={
            FundamentalMetric.ROCE: 28.0,
            FundamentalMetric.ROE: 28.0,
            FundamentalMetric.DEBT_EQUITY: 2.0,
        }
    )

    assert detail.capital_efficiency_state is CapitalEfficiencyState.LEVERAGE_DRIVEN
    assert any(item.code == "RETURN_LEVERAGE_CONFLICT" for item in detail.contradictions)
    assert opinion.stance is AgentStance.MIXED


def test_loss_making_growth_company_uses_not_meaningful_valuation() -> None:
    opinion, detail = analyze(
        overrides={
            FundamentalMetric.NET_INCOME: -10.0,
            FundamentalMetric.NET_MARGIN: -8.0,
        }
    )

    assert detail.profitability_state is ProfitabilityState.WEAK
    assert detail.valuation_state is ValuationState.NOT_MEANINGFUL
    assert opinion.stance is AgentStance.MIXED


def test_insufficient_core_evidence_produces_no_directional_opinion() -> None:
    opinion, detail = analyze(
        omit=(
            FundamentalMetric.REVENUE_GROWTH_YOY,
            FundamentalMetric.PROFIT_GROWTH_YOY,
            FundamentalMetric.REVENUE_CAGR_3Y,
            FundamentalMetric.PROFIT_CAGR_3Y,
            FundamentalMetric.NET_MARGIN,
            FundamentalMetric.ROE,
            FundamentalMetric.ROCE,
            FundamentalMetric.DEBT_EQUITY,
            FundamentalMetric.INTEREST_COVERAGE,
            FundamentalMetric.OPERATING_CASH_FLOW,
            FundamentalMetric.FREE_CASH_FLOW,
            FundamentalMetric.CASH_CONVERSION,
            FundamentalMetric.FCF_POSITIVE_FRACTION,
        )
    )

    assert opinion.stance is AgentStance.INSUFFICIENT_EVIDENCE
    assert opinion.status is AgentRunStatus.INSUFFICIENT_EVIDENCE
    assert detail.growth_state is GrowthState.INSUFFICIENT_EVIDENCE
    assert opinion.missing_evidence


def test_stale_reporting_data_is_never_upgraded() -> None:
    opinion, _ = analyze(
        quality=DataQuality.PARTIAL,
        freshness=FreshnessState.STALE,
    )

    assert opinion.status is AgentRunStatus.PARTIAL
    assert opinion.evidence_quality is DataQuality.PARTIAL
    assert opinion.evidence_freshness is FreshnessState.STALE
    assert "FUNDAMENTAL_EVIDENCE_STALE" in opinion.reason_codes


def test_conflicting_equal_quality_sources_remain_cited_and_mixed() -> None:
    opinion, detail = analyze(source_conflict=True)

    conflict = next(item for item in detail.contradictions if "SOURCE_CONFLICT_ROE" in item.code)
    assert len(conflict.evidence_ids) == 2
    assert opinion.stance is AgentStance.MIXED
    assert "FUNDAMENTAL_CONFLICT" in opinion.reason_codes


def test_missing_annual_family_is_explicitly_partial() -> None:
    opinion, _ = analyze(
        omit=(
            FundamentalMetric.REVENUE_GROWTH_YOY,
            FundamentalMetric.PROFIT_GROWTH_YOY,
            FundamentalMetric.REVENUE_CAGR_3Y,
            FundamentalMetric.PROFIT_CAGR_3Y,
            FundamentalMetric.NET_INCOME,
        )
    )

    assert opinion.status is AgentRunStatus.INSUFFICIENT_EVIDENCE
    assert any(
        "INCOME" in item.reason or "GROWTH" in item.reason
        for item in opinion.missing_evidence
    )


def test_bank_requires_sector_policy_and_abstains_from_industrial_rules() -> None:
    pack = fundamental_pack(financial=True)
    opinion = FundamentalSpecialist().analyze(fundamental_agent_request(pack), pack)
    detail = fundamental_assessment_from_opinion(opinion)

    assert opinion.stance is AgentStance.ABSTAIN
    assert opinion.status is AgentRunStatus.ABSTAINED
    assert detail.balance_sheet_state is BalanceSheetState.SECTOR_POLICY_REQUIRED
    assert detail.capital_efficiency_state is CapitalEfficiencyState.SECTOR_POLICY_REQUIRED
    assert detail.valuation_state is ValuationState.SECTOR_POLICY_REQUIRED
    assert detail.company_quality is CompanyQualityState.SECTOR_POLICY_REQUIRED
    assert "SECTOR_POLICY_REQUIRED" in opinion.reason_codes
