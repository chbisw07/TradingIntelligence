"""Deterministic, cited Fundamental / Company-Quality specialist."""

from dataclasses import dataclass
from enum import StrEnum

from tiaf.agents import (
    AgentCapability,
    AgentConfidence,
    AgentEvidencePack,
    AgentOpinionV2,
    AgentRequest,
    AgentRunStatus,
    AgentStance,
    AgentUsage,
    BaselineAgreement,
    CitationRole,
    ClaimKind,
    EvidenceCitation,
    EvidenceClaim,
    EvidenceImportance,
    MissingEvidenceRequest,
    PolicyDerivedConfidence,
    SpecialistCapability,
    SpecialistCostTier,
    SpecialistId,
)
from tiaf.contracts import DataQuality, EvidenceType, FreshnessState, TradeStyle
from tiaf.data import InstrumentType
from tiaf.fundamentals import FundamentalMetric
from tiaf.fundamentals.quality import weakest_freshness, weakest_quality

from .enums import (
    BalanceSheetState,
    CapitalEfficiencyState,
    CashFlowState,
    CompanyQualityState,
    EarningsQualityState,
    FundamentalMomentumState,
    FundamentalReasonCode,
    GrowthState,
    MarginState,
    OwnershipEvidenceState,
    ProfitabilityState,
    StabilityState,
    ValuationState,
)
from .evidence import FundamentalFactBook, FundamentalFactRecord
from .models import FundamentalAssessment, FundamentalContradiction
from .policy import FundamentalInterpretationPolicy, default_fundamental_policy

SPECIALIST_VERSION = "1.0"
FUNDAMENTAL_DETAIL_SCHEMA = "tiaf.fundamental-assessment/1.0"


@dataclass(frozen=True)
class _Dimension:
    name: str
    state: StrEnum
    sign: int
    records: tuple[FundamentalFactRecord, ...]


class FundamentalSpecialist:
    """Interpret supplied normalized financial facts without provider access."""

    def __init__(
        self,
        policy: FundamentalInterpretationPolicy | None = None,
    ) -> None:
        self._policy = policy or default_fundamental_policy()

    def capability(self) -> SpecialistCapability:
        return SpecialistCapability(
            specialist=SpecialistId.FUNDAMENTAL,
            specialist_version=SPECIALIST_VERSION,
            display_name="Fundamental / Company-Quality Specialist",
            description="Cited deterministic interpretation of normalized company evidence",
            supported_instrument_types=(InstrumentType.EQUITY,),
            required_evidence_types=(EvidenceType.FUNDAMENTAL,),
            allowed_capabilities=(
                AgentCapability.READ_A2_EVIDENCE,
                AgentCapability.READ_FUNDAMENTALS,
            ),
            supports_no_llm=True,
            cost_tier=SpecialistCostTier.LOW,
            prohibitions=(
                "provider acquisition",
                "qualitative moat or management claims without sourced documents",
                "target price or return probability",
                "trading or option action",
                "broker or execution operation",
            ),
        )

    def analyze(
        self,
        request: AgentRequest,
        evidence: AgentEvidencePack,
    ) -> AgentOpinionV2:
        self._validate_identity(request, evidence)
        facts = FundamentalFactBook(evidence)
        financial = self._is_financial(evidence)
        growth = self._growth(facts)
        profitability = self._profitability(facts)
        margins = self._margins(facts)
        capital = self._capital_efficiency(facts, financial)
        balance = self._balance_sheet(facts, financial)
        cash = self._cash_flow(facts)
        earnings = self._earnings_quality(facts)
        valuation = self._valuation(facts, financial)
        stability = self._stability(facts)
        ownership = self._ownership(facts)
        momentum = self._momentum(facts)
        dimensions = (
            growth,
            profitability,
            margins,
            capital,
            balance,
            cash,
            earnings,
            valuation,
            stability,
            ownership,
            momentum,
        )
        contradictions = self._contradictions(facts, dimensions)
        company_quality = self._company_quality(dimensions, contradictions, financial)
        core_complete = all(
            (
                growth.state is not GrowthState.INSUFFICIENT_EVIDENCE,
                profitability.state is not ProfitabilityState.INSUFFICIENT_EVIDENCE,
                cash.state is not CashFlowState.INSUFFICIENT_EVIDENCE,
                balance.state is not BalanceSheetState.UNKNOWN,
            )
        )
        horizon_relevance = self._horizon_relevance(request)
        stance = self._stance(
            request,
            company_quality,
            FundamentalMomentumState(momentum.state),
            ValuationState(valuation.state),
            contradictions,
            core_complete,
            financial,
        )
        missing = self._missing(request, evidence, dimensions, core_complete)
        agreement = self._internal_agreement(dimensions)
        sector_applicability = (
            self._policy.financial_sector_applicability if financial else 1.0
        )
        confidence = self._confidence(
            evidence,
            agreement,
            sector_applicability,
            horizon_relevance,
            core_complete,
        )
        reasons = self._reasons(
            facts,
            dimensions,
            contradictions,
            evidence,
            financial,
            core_complete,
        )
        assessment = FundamentalAssessment(
            assessment_id=f"{request.run_id}:fundamental-assessment",
            specialist_version=SPECIALIST_VERSION,
            policy_id=self._policy.policy_id,
            policy_version=self._policy.policy_version,
            stance=stance,
            growth_state=GrowthState(growth.state),
            profitability_state=ProfitabilityState(profitability.state),
            margin_state=MarginState(margins.state),
            capital_efficiency_state=CapitalEfficiencyState(capital.state),
            balance_sheet_state=BalanceSheetState(balance.state),
            cash_flow_state=CashFlowState(cash.state),
            earnings_quality_state=EarningsQualityState(earnings.state),
            valuation_state=ValuationState(valuation.state),
            stability_state=StabilityState(stability.state),
            ownership_governance_evidence_state=OwnershipEvidenceState(
                ownership.state
            ),
            fundamental_momentum=FundamentalMomentumState(momentum.state),
            company_quality=company_quality,
            contradictions=contradictions,
            evidence_ids_by_dimension=tuple(
                (item.name, _reference_ids(item.records)) for item in dimensions
            ),
            evidence_coverage=evidence.evidence_coverage,
            internal_agreement=agreement,
            sector_policy_applicability=sector_applicability,
            horizon_relevance=horizon_relevance,
            confidence_basis=(
                "evidence_coverage_quality_and_freshness",
                "dimension_group_agreement",
                "sector_policy_applicability",
                "horizon_relevance",
                "not_probability_of_market_success",
            ),
            reason_codes=reasons,
            created_at=request.created_at,
        )
        claims = self._claims(dimensions, company_quality, contradictions)
        supporting_ids = tuple(
            dict.fromkeys(
                citation.evidence_id
                for claim in claims
                for citation in claim.citations
            )
        )
        status = self._status(stance, evidence, missing)
        risks = tuple(item.description for item in contradictions)
        limitation = evidence.metadata.get("point_in_time_limitation")
        caveats = tuple(
            item
            for item in (
                "Generic industrial ratios are not applied to financial companies"
                if financial
                else None,
                limitation if isinstance(limitation, str) else None,
                "Fundamental evidence is background context for DAY horizon"
                if request.trade_style is TradeStyle.DAY
                else None,
            )
            if item is not None
        )
        return AgentOpinionV2(
            opinion_id=f"{request.run_id}:fundamental-opinion",
            request_id=request.request_id,
            run_id=request.run_id,
            specialist=SpecialistId.FUNDAMENTAL,
            specialist_version=SPECIALIST_VERSION,
            subject=request.subject,
            horizon=request.horizon,
            stance=stance,
            status=status,
            confidence=AgentConfidence(
                evidence_coverage=evidence.evidence_coverage,
                evidence_quality=evidence.overall_quality,
                policy_derived=PolicyDerivedConfidence(
                    value=confidence,
                    policy_id=self._policy.policy_id,
                    policy_version=self._policy.policy_version,
                ),
            ),
            summary=(
                f"Deterministic financial quality is {company_quality.value}; "
                f"fundamental momentum is {momentum.state}."
            ),
            reason_codes=tuple(item.value for item in reasons),
            evidence_claims=claims,
            supporting_evidence_ids=supporting_ids,
            missing_evidence=missing,
            risks=risks,
            caveats=caveats,
            deterministic_baseline_reference=request.deterministic_baseline_reference,
            baseline_agreement=BaselineAgreement.NOT_COMPARABLE,
            evidence_fingerprint=request.evidence_fingerprint,
            evidence_quality=evidence.overall_quality,
            evidence_freshness=evidence.overall_freshness,
            policy_version=self._policy.policy_version,
            usage=AgentUsage(),
            produced_at=request.created_at,
            specialist_detail_schema_id=FUNDAMENTAL_DETAIL_SCHEMA,
            specialist_detail_json=assessment.canonical_json(),
        )

    def _growth(self, facts: FundamentalFactBook) -> _Dimension:
        metrics = (
            FundamentalMetric.REVENUE_GROWTH_YOY,
            FundamentalMetric.PROFIT_GROWTH_YOY,
            FundamentalMetric.REVENUE_CAGR_3Y,
            FundamentalMetric.PROFIT_CAGR_3Y,
        )
        records = _latest_records(facts, metrics)
        values = _numbers(facts, metrics)
        if not values:
            return _Dimension("GROWTH", GrowthState.INSUFFICIENT_EVIDENCE, 0, records)
        positives = [item for item in values if item >= self._policy.growth_moderate_percent]
        negatives = [item for item in values if item <= self._policy.growth_declining_percent]
        spread = max(values) - min(values)
        average = sum(values) / len(values)
        if positives and negatives:
            state, sign = GrowthState.MIXED, 0
        elif len(values) >= 2 and spread >= self._policy.growth_volatile_spread_percent:
            state, sign = GrowthState.VOLATILE, 0
        elif average >= self._policy.growth_strong_percent and len(values) >= 2:
            state, sign = GrowthState.STRONG_GROWTH, 1
        elif average >= self._policy.growth_healthy_percent:
            state, sign = GrowthState.HEALTHY_GROWTH, 1
        elif average >= self._policy.growth_moderate_percent:
            state, sign = GrowthState.MODERATE_GROWTH, 1
        elif average <= self._policy.growth_declining_percent:
            state, sign = GrowthState.DECLINING, -1
        else:
            state, sign = GrowthState.STAGNANT, 0
        return _Dimension("GROWTH", state, sign, records)

    def _profitability(self, facts: FundamentalFactBook) -> _Dimension:
        metrics = (
            FundamentalMetric.NET_MARGIN,
            FundamentalMetric.ROE,
            FundamentalMetric.ROCE,
        )
        records = _latest_records(facts, metrics)
        values = _numbers(facts, metrics)
        if not values:
            return _Dimension(
                "PROFITABILITY", ProfitabilityState.INSUFFICIENT_EVIDENCE, 0, records
            )
        margin_change = facts.number(FundamentalMetric.MARGIN_CHANGE_PP)
        average = sum(values) / len(values)
        if margin_change is not None and margin_change <= -self._policy.margin_change_material_pp:
            state, sign = ProfitabilityState.DETERIORATING, -1
        elif min(values) < 0:
            state, sign = ProfitabilityState.WEAK, -1
        elif average >= self._policy.return_strong_percent:
            state, sign = ProfitabilityState.STRONG, 1
        elif average >= self._policy.return_healthy_percent:
            state, sign = ProfitabilityState.HEALTHY, 1
        elif average >= self._policy.return_weak_percent:
            state, sign = ProfitabilityState.AVERAGE, 0
        else:
            state, sign = ProfitabilityState.WEAK, -1
        return _Dimension("PROFITABILITY", state, sign, records)

    def _margins(self, facts: FundamentalFactBook) -> _Dimension:
        metrics = (
            FundamentalMetric.OPERATING_MARGIN,
            FundamentalMetric.EBITDA_MARGIN,
            FundamentalMetric.NET_MARGIN,
            FundamentalMetric.MARGIN_CHANGE_PP,
        )
        records = _latest_records(facts, metrics)
        margins = _numbers(
            facts,
            (
                FundamentalMetric.OPERATING_MARGIN,
                FundamentalMetric.EBITDA_MARGIN,
                FundamentalMetric.NET_MARGIN,
            ),
        )
        change = facts.number(FundamentalMetric.MARGIN_CHANGE_PP)
        if not margins and change is None:
            return _Dimension("MARGINS", MarginState.INSUFFICIENT_EVIDENCE, 0, records)
        if change is not None and change >= self._policy.margin_change_material_pp:
            state, sign = MarginState.EXPANDING, 1
        elif change is not None and change <= -self._policy.margin_change_material_pp:
            state, sign = MarginState.CONTRACTING, -1
        elif margins and min(margins) < 0:
            state, sign = MarginState.NEGATIVE, -1
        elif margins and sum(margins) / len(margins) >= self._policy.margin_strong_percent:
            state, sign = MarginState.STRONG, 1
        elif margins and sum(margins) / len(margins) >= self._policy.margin_healthy_percent:
            state, sign = MarginState.HEALTHY, 1
        else:
            state, sign = MarginState.STABLE, 0
        return _Dimension("MARGINS", state, sign, records)

    def _capital_efficiency(
        self,
        facts: FundamentalFactBook,
        financial: bool,
    ) -> _Dimension:
        metrics = (FundamentalMetric.ROE, FundamentalMetric.ROCE, FundamentalMetric.ROA)
        records = _latest_records(facts, metrics)
        if financial:
            return _Dimension(
                "CAPITAL_EFFICIENCY",
                CapitalEfficiencyState.SECTOR_POLICY_REQUIRED,
                0,
                records,
            )
        values = _numbers(facts, metrics)
        if not values:
            return _Dimension(
                "CAPITAL_EFFICIENCY",
                CapitalEfficiencyState.INSUFFICIENT_EVIDENCE,
                0,
                records,
            )
        debt_equity = facts.number(FundamentalMetric.DEBT_EQUITY)
        average = sum(values) / len(values)
        change = facts.number(FundamentalMetric.ROCE_CHANGE_PP)
        if debt_equity is not None and debt_equity >= self._policy.leverage_high:
            state, sign = CapitalEfficiencyState.LEVERAGE_DRIVEN, 0
        elif change is not None and change <= -self._policy.margin_change_material_pp:
            state, sign = CapitalEfficiencyState.DETERIORATING, -1
        elif average >= self._policy.return_strong_percent:
            state, sign = CapitalEfficiencyState.STRONG, 1
        elif average >= self._policy.return_healthy_percent:
            state, sign = CapitalEfficiencyState.HEALTHY, 1
        elif average >= self._policy.return_weak_percent:
            state, sign = CapitalEfficiencyState.AVERAGE, 0
        else:
            state, sign = CapitalEfficiencyState.WEAK, -1
        return _Dimension("CAPITAL_EFFICIENCY", state, sign, records)

    def _balance_sheet(self, facts: FundamentalFactBook, financial: bool) -> _Dimension:
        metrics = (
            FundamentalMetric.DEBT_EQUITY,
            FundamentalMetric.NET_DEBT_EBITDA,
            FundamentalMetric.INTEREST_COVERAGE,
            FundamentalMetric.CASH,
            FundamentalMetric.TOTAL_DEBT,
        )
        records = _latest_records(facts, metrics)
        if financial:
            return _Dimension(
                "BALANCE_SHEET",
                BalanceSheetState.SECTOR_POLICY_REQUIRED,
                0,
                records,
            )
        debt_equity = facts.number(FundamentalMetric.DEBT_EQUITY)
        coverage = facts.number(FundamentalMetric.INTEREST_COVERAGE)
        if debt_equity is None and coverage is None:
            return _Dimension("BALANCE_SHEET", BalanceSheetState.UNKNOWN, 0, records)
        if (
            debt_equity is not None
            and debt_equity >= self._policy.leverage_distressed
            and coverage is not None
            and coverage < 1.0
        ):
            state, sign = BalanceSheetState.DISTRESSED_RISK, -1
        elif debt_equity is not None and debt_equity >= self._policy.leverage_high:
            state, sign = BalanceSheetState.LEVERAGED, -1
        elif coverage is not None and coverage < self._policy.interest_coverage_weak:
            state, sign = BalanceSheetState.WEAK, -1
        elif (
            debt_equity is not None
            and debt_equity <= self._policy.leverage_low
            and (coverage is None or coverage >= self._policy.interest_coverage_strong)
        ):
            state, sign = BalanceSheetState.VERY_STRONG, 1
        elif coverage is not None and coverage >= self._policy.interest_coverage_strong:
            state, sign = BalanceSheetState.STRONG, 1
        else:
            state, sign = BalanceSheetState.ADEQUATE, 0
        return _Dimension("BALANCE_SHEET", state, sign, records)

    def _cash_flow(self, facts: FundamentalFactBook) -> _Dimension:
        metrics = (
            FundamentalMetric.CASH_CONVERSION,
            FundamentalMetric.FCF_POSITIVE_FRACTION,
            FundamentalMetric.OPERATING_CASH_FLOW,
            FundamentalMetric.FREE_CASH_FLOW,
        )
        records = _latest_records(facts, metrics)
        conversion = facts.number(FundamentalMetric.CASH_CONVERSION)
        consistency = facts.number(FundamentalMetric.FCF_POSITIVE_FRACTION)
        fcf = facts.number(FundamentalMetric.FREE_CASH_FLOW)
        if conversion is None and consistency is None and fcf is None:
            return _Dimension(
                "CASH_FLOW_QUALITY", CashFlowState.INSUFFICIENT_EVIDENCE, 0, records
            )
        if fcf is not None and fcf < 0 and (conversion is None or conversion < 0):
            state, sign = CashFlowState.NEGATIVE, -1
        elif conversion is not None and conversion < self._policy.cash_conversion_weak:
            state, sign = CashFlowState.WEAK, -1
        elif consistency is not None and consistency < self._policy.consistency_low:
            state, sign = CashFlowState.VOLATILE, -1
        elif (
            conversion is not None
            and conversion >= 1.0
            and (consistency is None or consistency >= self._policy.consistency_high)
        ):
            state, sign = CashFlowState.STRONG, 1
        elif conversion is not None and conversion >= self._policy.cash_conversion_healthy:
            state, sign = CashFlowState.HEALTHY, 1
        else:
            state, sign = CashFlowState.ADEQUATE, 0
        return _Dimension("CASH_FLOW_QUALITY", state, sign, records)

    def _earnings_quality(self, facts: FundamentalFactBook) -> _Dimension:
        metrics = (
            FundamentalMetric.PROFIT_GROWTH_YOY,
            FundamentalMetric.CASH_CONVERSION,
            FundamentalMetric.FCF_POSITIVE_FRACTION,
            FundamentalMetric.NET_MARGIN,
        )
        records = _latest_records(facts, metrics)
        profit_growth = facts.number(FundamentalMetric.PROFIT_GROWTH_YOY)
        conversion = facts.number(FundamentalMetric.CASH_CONVERSION)
        consistency = facts.number(FundamentalMetric.FCF_POSITIVE_FRACTION)
        if conversion is None and consistency is None:
            return _Dimension(
                "EARNINGS_QUALITY",
                EarningsQualityState.INSUFFICIENT_EVIDENCE,
                0,
                records,
            )
        if (
            profit_growth is not None
            and profit_growth > self._policy.growth_moderate_percent
            and conversion is not None
            and conversion < self._policy.cash_conversion_weak
        ):
            state, sign = EarningsQualityState.PROFIT_CASHFLOW_DIVERGENCE, -1
        elif conversion is not None and conversion >= 1.0 and (
            consistency is None or consistency >= self._policy.consistency_high
        ):
            state, sign = EarningsQualityState.HIGH, 1
        elif conversion is not None and conversion >= self._policy.cash_conversion_healthy:
            state, sign = EarningsQualityState.GOOD, 1
        elif conversion is not None and conversion < self._policy.cash_conversion_weak:
            state, sign = EarningsQualityState.WEAK, -1
        else:
            state, sign = EarningsQualityState.ADEQUATE, 0
        return _Dimension("EARNINGS_QUALITY", state, sign, records)

    def _valuation(self, facts: FundamentalFactBook, financial: bool) -> _Dimension:
        metrics = (
            FundamentalMetric.VALUATION_HISTORY_PERCENTILE,
            FundamentalMetric.PE,
            FundamentalMetric.PB,
            FundamentalMetric.EV_EBITDA,
            FundamentalMetric.NET_INCOME,
        )
        records = _latest_records(facts, metrics)
        if financial:
            return _Dimension(
                "VALUATION", ValuationState.SECTOR_POLICY_REQUIRED, 0, records
            )
        net_income = facts.number(FundamentalMetric.NET_INCOME)
        if net_income is not None and net_income <= 0:
            return _Dimension("VALUATION", ValuationState.NOT_MEANINGFUL, 0, records)
        percentile = facts.number(FundamentalMetric.VALUATION_HISTORY_PERCENTILE)
        if percentile is None:
            return _Dimension("VALUATION", ValuationState.UNKNOWN, 0, records)
        if percentile >= self._policy.valuation_very_expensive_percentile:
            state, sign = ValuationState.VERY_EXPENSIVE, -1
        elif percentile >= self._policy.valuation_expensive_percentile:
            state, sign = ValuationState.EXPENSIVE, -1
        elif percentile <= self._policy.valuation_cheap_percentile:
            state, sign = ValuationState.CHEAP, 1
        elif percentile <= self._policy.valuation_reasonable_percentile:
            state, sign = ValuationState.REASONABLE, 1
        else:
            state, sign = ValuationState.FAIR, 0
        return _Dimension("VALUATION", state, sign, records)

    def _stability(self, facts: FundamentalFactBook) -> _Dimension:
        metrics = (
            FundamentalMetric.EARNINGS_STABILITY,
            FundamentalMetric.FCF_POSITIVE_FRACTION,
        )
        records = _latest_records(facts, metrics)
        values = _numbers(facts, metrics)
        if not values:
            return _Dimension("STABILITY", StabilityState.UNKNOWN, 0, records)
        average = sum(values) / len(values)
        if average >= self._policy.consistency_high:
            state, sign = StabilityState.HIGH, 1
        elif average >= 0.6:
            state, sign = StabilityState.STABLE, 1
        elif average < self._policy.consistency_low:
            state, sign = StabilityState.VOLATILE, -1
        else:
            state, sign = StabilityState.VARIABLE, 0
        return _Dimension("STABILITY", state, sign, records)

    def _momentum(self, facts: FundamentalFactBook) -> _Dimension:
        metrics = (
            FundamentalMetric.REVENUE_GROWTH_YOY,
            FundamentalMetric.PROFIT_GROWTH_YOY,
            FundamentalMetric.MARGIN_CHANGE_PP,
            FundamentalMetric.ROCE_CHANGE_PP,
        )
        records = _latest_records(facts, metrics)
        values = _numbers(facts, metrics)
        if not values:
            return _Dimension(
                "FUNDAMENTAL_MOMENTUM", FundamentalMomentumState.UNKNOWN, 0, records
            )
        positive = sum(value > self._policy.growth_moderate_percent for value in values)
        negative = sum(value < self._policy.growth_declining_percent for value in values)
        if positive and negative:
            state, sign = FundamentalMomentumState.MIXED, 0
        elif positive:
            state, sign = FundamentalMomentumState.IMPROVING, 1
        elif negative:
            state, sign = FundamentalMomentumState.DETERIORATING, -1
        else:
            state, sign = FundamentalMomentumState.STABLE, 0
        return _Dimension("FUNDAMENTAL_MOMENTUM", state, sign, records)

    def _ownership(self, facts: FundamentalFactBook) -> _Dimension:
        metrics = (
            FundamentalMetric.PROMOTER_OWNERSHIP,
            FundamentalMetric.PROMOTER_PLEDGE,
            FundamentalMetric.INSTITUTIONAL_OWNERSHIP,
            FundamentalMetric.SHARE_DILUTION_PERCENT,
        )
        records = _latest_records(facts, metrics)
        if not records:
            return _Dimension(
                "OWNERSHIP_GOVERNANCE_EVIDENCE",
                OwnershipEvidenceState.INSUFFICIENT_EVIDENCE,
                0,
                records,
            )
        pledge = facts.number(FundamentalMetric.PROMOTER_PLEDGE)
        dilution = facts.number(FundamentalMetric.SHARE_DILUTION_PERCENT)
        if (
            pledge is not None
            and pledge >= self._policy.promoter_pledge_elevated_percent
        ) or (
            dilution is not None
            and dilution >= self._policy.dilution_elevated_percent
        ):
            state, sign = OwnershipEvidenceState.ELEVATED_DISCLOSED_RISK, -1
        elif len(records) >= 2:
            state, sign = OwnershipEvidenceState.AVAILABLE, 0
        else:
            state, sign = OwnershipEvidenceState.PARTIAL, 0
        return _Dimension("OWNERSHIP_GOVERNANCE_EVIDENCE", state, sign, records)

    def _company_quality(
        self,
        dimensions: tuple[_Dimension, ...],
        contradictions: tuple[FundamentalContradiction, ...],
        financial: bool,
    ) -> CompanyQualityState:
        values = {item.name: item for item in dimensions}
        if financial:
            return CompanyQualityState.SECTOR_POLICY_REQUIRED
        if any("PROFIT_CASHFLOW" in item.code for item in contradictions):
            return CompanyQualityState.DETERIORATING
        signs = tuple(
            values[name].sign
            for name in (
                "GROWTH",
                "PROFITABILITY",
                "CAPITAL_EFFICIENCY",
                "BALANCE_SHEET",
                "CASH_FLOW_QUALITY",
                "EARNINGS_QUALITY",
                "STABILITY",
            )
            if values[name].records
        )
        if len(signs) < 4:
            return CompanyQualityState.INSUFFICIENT_EVIDENCE
        positive, negative = signs.count(1), signs.count(-1)
        if negative >= 3:
            return CompanyQualityState.DETERIORATING
        if negative >= 2:
            return CompanyQualityState.WEAK
        if positive >= 6 and negative == 0:
            return CompanyQualityState.HIGH_QUALITY
        if positive >= 4 and negative == 0:
            return CompanyQualityState.GOOD_QUALITY
        if positive and negative:
            return CompanyQualityState.MIXED
        return CompanyQualityState.AVERAGE

    @staticmethod
    def _stance(
        request: AgentRequest,
        quality: CompanyQualityState,
        momentum: FundamentalMomentumState,
        valuation: ValuationState,
        contradictions: tuple[FundamentalContradiction, ...],
        core_complete: bool,
        financial: bool,
    ) -> AgentStance:
        if not core_complete:
            return AgentStance.INSUFFICIENT_EVIDENCE
        if request.trade_style is TradeStyle.DAY or financial:
            return AgentStance.ABSTAIN
        if quality in {CompanyQualityState.HIGH_QUALITY, CompanyQualityState.GOOD_QUALITY}:
            if valuation is ValuationState.VERY_EXPENSIVE or contradictions:
                return AgentStance.MIXED
            return AgentStance.POSITIVE
        if quality in {CompanyQualityState.WEAK, CompanyQualityState.DETERIORATING}:
            return AgentStance.NEGATIVE
        if quality is CompanyQualityState.MIXED or momentum is FundamentalMomentumState.MIXED:
            return AgentStance.MIXED
        return AgentStance.NEUTRAL

    def _contradictions(
        self,
        facts: FundamentalFactBook,
        dimensions: tuple[_Dimension, ...],
    ) -> tuple[FundamentalContradiction, ...]:
        by_name = {item.name: item for item in dimensions}
        contradictions: list[FundamentalContradiction] = []
        if by_name["GROWTH"].sign > 0 and by_name["MARGINS"].sign < 0:
            contradictions.append(
                _contradiction(
                    "GROWTH_MARGIN_DIVERGENCE",
                    "Positive growth coexists with contracting or negative margins",
                    (*by_name["GROWTH"].records, *by_name["MARGINS"].records),
                )
            )
        if by_name["GROWTH"].sign > 0 and by_name["CASH_FLOW_QUALITY"].sign < 0:
            contradictions.append(
                _contradiction(
                    "PROFIT_CASHFLOW_DIVERGENCE",
                    "Growth/profit evidence coexists with weak cash conversion",
                    (*by_name["GROWTH"].records, *by_name["CASH_FLOW_QUALITY"].records),
                )
            )
        if (
            by_name["GROWTH"].sign > 0
            and by_name["PROFITABILITY"].sign > 0
            and by_name["VALUATION"].state is ValuationState.VERY_EXPENSIVE
        ):
            contradictions.append(
                _contradiction(
                    "QUALITY_VALUATION_CONFLICT",
                    "Positive growth and profitability coexist with extreme valuation",
                    (
                        *by_name["GROWTH"].records,
                        *by_name["PROFITABILITY"].records,
                        *by_name["VALUATION"].records,
                    ),
                )
            )
        roe = facts.number(FundamentalMetric.ROE)
        leverage = facts.number(FundamentalMetric.DEBT_EQUITY)
        if (
            roe is not None
            and roe >= self._policy.return_strong_percent
            and leverage is not None
            and leverage >= self._policy.leverage_high
        ):
            contradictions.append(
                _contradiction(
                    "RETURN_LEVERAGE_CONFLICT",
                    "Strong supplied return on equity coexists with high leverage",
                    (
                        *facts.latest(FundamentalMetric.ROE),
                        *facts.latest(FundamentalMetric.DEBT_EQUITY),
                    ),
                )
            )
        for metric in FundamentalMetric:
            if facts.has_conflict(metric):
                contradictions.append(
                    _contradiction(
                        f"SOURCE_CONFLICT_{metric.name}",
                        f"Equally preferred sources disagree for {metric.value}",
                        facts.latest(metric),
                    )
                )
        return tuple(contradictions)

    def _reasons(
        self,
        facts: FundamentalFactBook,
        dimensions: tuple[_Dimension, ...],
        contradictions: tuple[FundamentalContradiction, ...],
        evidence: AgentEvidencePack,
        financial: bool,
        core_complete: bool,
    ) -> tuple[FundamentalReasonCode, ...]:
        values = {item.name: item.state for item in dimensions}
        reasons: list[FundamentalReasonCode] = []
        if values["GROWTH"] is GrowthState.STRONG_GROWTH:
            reasons.extend(
                (
                    FundamentalReasonCode.REVENUE_GROWTH_STRONG,
                    FundamentalReasonCode.PROFIT_GROWTH_STRONG,
                )
            )
        if values["GROWTH"] is GrowthState.DECLINING:
            reasons.append(FundamentalReasonCode.PROFIT_DECLINING)
        if values["MARGINS"] is MarginState.EXPANDING:
            reasons.append(FundamentalReasonCode.MARGIN_EXPANDING)
        if values["MARGINS"] is MarginState.CONTRACTING:
            reasons.append(FundamentalReasonCode.MARGIN_CONTRACTING)
        if values["CAPITAL_EFFICIENCY"] is CapitalEfficiencyState.STRONG:
            reasons.append(FundamentalReasonCode.ROCE_STRONG)
        leverage = facts.number(FundamentalMetric.DEBT_EQUITY)
        if leverage is not None and leverage <= self._policy.leverage_low:
            reasons.append(FundamentalReasonCode.LEVERAGE_LOW)
        elif leverage is not None and leverage >= self._policy.leverage_high:
            reasons.append(FundamentalReasonCode.LEVERAGE_HIGH)
        coverage = facts.number(FundamentalMetric.INTEREST_COVERAGE)
        if coverage is not None and coverage < self._policy.interest_coverage_weak:
            reasons.append(FundamentalReasonCode.INTEREST_COVERAGE_WEAK)
        if values["CASH_FLOW_QUALITY"] is CashFlowState.STRONG:
            reasons.append(FundamentalReasonCode.OPERATING_CASH_FLOW_STRONG)
        fcf_consistency = facts.number(FundamentalMetric.FCF_POSITIVE_FRACTION)
        if (
            fcf_consistency is not None
            and fcf_consistency >= self._policy.consistency_high
        ):
            reasons.append(FundamentalReasonCode.FCF_CONSISTENT)
        if values["VALUATION"] in {ValuationState.EXPENSIVE, ValuationState.VERY_EXPENSIVE}:
            reasons.append(FundamentalReasonCode.VALUATION_ELEVATED)
        if values["VALUATION"] in {ValuationState.CHEAP, ValuationState.REASONABLE}:
            reasons.append(FundamentalReasonCode.VALUATION_REASONABLE)
        pledge = facts.number(FundamentalMetric.PROMOTER_PLEDGE)
        if pledge is not None and pledge >= self._policy.promoter_pledge_elevated_percent:
            reasons.append(FundamentalReasonCode.PROMOTER_PLEDGE_ELEVATED)
        dilution = facts.number(FundamentalMetric.SHARE_DILUTION_PERCENT)
        if dilution is not None and dilution >= self._policy.dilution_elevated_percent:
            reasons.append(FundamentalReasonCode.DILUTION_RISK)
        if contradictions:
            reasons.append(FundamentalReasonCode.FUNDAMENTAL_CONFLICT)
        if any("PROFIT_CASHFLOW" in item.code for item in contradictions):
            reasons.append(FundamentalReasonCode.PROFIT_CASHFLOW_DIVERGENCE)
        if financial:
            reasons.append(FundamentalReasonCode.SECTOR_POLICY_REQUIRED)
        if evidence.overall_quality is not DataQuality.GOOD or evidence.missing_evidence:
            reasons.append(FundamentalReasonCode.FUNDAMENTAL_EVIDENCE_PARTIAL)
        if evidence.overall_freshness is FreshnessState.STALE:
            reasons.append(FundamentalReasonCode.FUNDAMENTAL_EVIDENCE_STALE)
        if not core_complete:
            reasons.append(FundamentalReasonCode.FUNDAMENTAL_EVIDENCE_INSUFFICIENT)
        return tuple(dict.fromkeys(reasons))

    def _claims(
        self,
        dimensions: tuple[_Dimension, ...],
        company_quality: CompanyQualityState,
        contradictions: tuple[FundamentalContradiction, ...],
    ) -> tuple[EvidenceClaim, ...]:
        claims: list[EvidenceClaim] = []
        for dimension in dimensions:
            if not dimension.records:
                continue
            unique_records = tuple(
                {
                    item.reference.evidence_id: item
                    for item in dimension.records
                }.values()
            )
            claims.append(
                EvidenceClaim(
                    claim_id=f"fundamental:{dimension.name.casefold()}",
                    kind=ClaimKind.INTERPRETIVE,
                    statement=f"{dimension.name} evidence is interpreted as {dimension.state}.",
                    evidence_type=EvidenceType.FUNDAMENTAL,
                    citations=tuple(
                        EvidenceCitation(
                            evidence_id=item.reference.evidence_id,
                            role=CitationRole.SUPPORTS,
                            locator=item.fact.fact_id,
                        )
                        for item in unique_records
                    ),
                    as_of=max(item.fact.as_of for item in unique_records),
                    provenance=f"{self._policy.policy_id}/{self._policy.policy_version}",
                    quality=weakest_quality(
                        tuple(
                            item.reference.quality
                            for item in unique_records
                            if item.reference.quality is not None
                        )
                    ),
                    freshness=weakest_freshness(
                        tuple(
                            item.reference.freshness
                            for item in unique_records
                            if item.reference.freshness is not None
                        )
                    ),
                )
            )
        all_records = tuple(item for dimension in dimensions for item in dimension.records)
        if all_records:
            claims.append(
                self._aggregate_claim(
                    claim_id="fundamental:company_quality",
                    statement=(
                        "Supplied dimensions synthesize to deterministic financial "
                        f"quality {company_quality.value}."
                    ),
                    records=all_records,
                )
            )
        by_evidence = {item.reference.evidence_id: item for item in all_records}
        for contradiction in contradictions:
            records = tuple(
                by_evidence[evidence_id]
                for evidence_id in contradiction.evidence_ids
                if evidence_id in by_evidence
            )
            if records:
                claims.append(
                    self._aggregate_claim(
                        claim_id=f"fundamental:contradiction:{contradiction.code.casefold()}",
                        statement=contradiction.description,
                        records=records,
                    )
                )
        return tuple(claims)

    def _aggregate_claim(
        self,
        *,
        claim_id: str,
        statement: str,
        records: tuple[FundamentalFactRecord, ...],
    ) -> EvidenceClaim:
        unique_records = tuple(
            {item.reference.evidence_id: item for item in records}.values()
        )
        return EvidenceClaim(
            claim_id=claim_id,
            kind=ClaimKind.INTERPRETIVE,
            statement=statement,
            evidence_type=EvidenceType.FUNDAMENTAL,
            citations=tuple(
                EvidenceCitation(
                    evidence_id=item.reference.evidence_id,
                    role=CitationRole.SUPPORTS,
                    locator=item.fact.fact_id,
                )
                for item in unique_records
            ),
            as_of=max(item.fact.as_of for item in unique_records),
            provenance=f"{self._policy.policy_id}/{self._policy.policy_version}",
            quality=weakest_quality(
                tuple(
                    item.reference.quality
                    for item in unique_records
                    if item.reference.quality is not None
                )
            ),
            freshness=weakest_freshness(
                tuple(
                    item.reference.freshness
                    for item in unique_records
                    if item.reference.freshness is not None
                )
            ),
        )

    def _missing(
        self,
        request: AgentRequest,
        evidence: AgentEvidencePack,
        dimensions: tuple[_Dimension, ...],
        core_complete: bool,
    ) -> tuple[MissingEvidenceRequest, ...]:
        missing = list(evidence.missing_evidence)
        for dimension in dimensions:
            if dimension.records:
                continue
            missing.append(
                MissingEvidenceRequest(
                    missing_request_id=f"{request.request_id}:missing:{dimension.name}",
                    evidence_type=EvidenceType.FUNDAMENTAL,
                    capability=AgentCapability.READ_FUNDAMENTALS,
                    subject=request.subject,
                    reason=f"No usable normalized facts for {dimension.name}",
                    importance=(
                        EvidenceImportance.REQUIRED
                        if dimension.name
                        in {
                            "GROWTH",
                            "PROFITABILITY",
                            "BALANCE_SHEET",
                            "CASH_FLOW_QUALITY",
                        }
                        else EvidenceImportance.OPTIONAL
                    ),
                    required_freshness=FreshnessState.FRESH,
                    requested_at=request.created_at,
                )
            )
        if not core_complete and not any(
            item.importance is EvidenceImportance.REQUIRED for item in missing
        ):
            missing.append(
                MissingEvidenceRequest(
                    missing_request_id=f"{request.request_id}:missing:CORE",
                    evidence_type=EvidenceType.FUNDAMENTAL,
                    capability=AgentCapability.READ_FUNDAMENTALS,
                    subject=request.subject,
                    reason="Minimum company-quality evidence is incomplete",
                    importance=EvidenceImportance.REQUIRED,
                    required_freshness=FreshnessState.FRESH,
                    requested_at=request.created_at,
                )
            )
        return tuple({item.missing_request_id: item for item in missing}.values())

    @staticmethod
    def _internal_agreement(dimensions: tuple[_Dimension, ...]) -> float:
        signs = tuple(item.sign for item in dimensions if item.records and item.name != "VALUATION")
        if not signs:
            return 0.0
        return round(max(signs.count(1), signs.count(-1), signs.count(0)) / len(signs), 4)

    def _confidence(
        self,
        evidence: AgentEvidencePack,
        agreement: float,
        sector_applicability: float,
        horizon_relevance: float,
        core_complete: bool,
    ) -> float:
        if not core_complete:
            return 0.0
        quality = {
            DataQuality.GOOD: 1.0,
            DataQuality.PARTIAL: 0.8,
            DataQuality.DEGRADED: 0.6,
            DataQuality.UNAVAILABLE: 0.0,
        }[evidence.overall_quality]
        freshness = {
            FreshnessState.FRESH: 1.0,
            FreshnessState.AGING: 0.8,
            FreshnessState.STALE: 0.5,
            FreshnessState.UNKNOWN: 0.6,
        }[evidence.overall_freshness]
        return round(
            evidence.evidence_coverage
            * agreement
            * quality
            * freshness
            * sector_applicability
            * horizon_relevance,
            4,
        )

    def _horizon_relevance(self, request: AgentRequest) -> float:
        if request.trade_style is TradeStyle.DAY:
            return self._policy.day_horizon_relevance
        days = request.horizon.max_days or request.horizon.min_days or 0
        if days >= 180:
            return self._policy.long_horizon_relevance
        if days >= 90:
            return self._policy.medium_horizon_relevance
        return self._policy.positional_horizon_relevance

    @staticmethod
    def _status(
        stance: AgentStance,
        evidence: AgentEvidencePack,
        missing: tuple[MissingEvidenceRequest, ...],
    ) -> AgentRunStatus:
        if stance is AgentStance.INSUFFICIENT_EVIDENCE:
            return AgentRunStatus.INSUFFICIENT_EVIDENCE
        if stance is AgentStance.ABSTAIN:
            return AgentRunStatus.ABSTAINED
        if (
            missing
            or evidence.overall_quality is not DataQuality.GOOD
            or evidence.overall_freshness is not FreshnessState.FRESH
        ):
            return AgentRunStatus.PARTIAL
        return AgentRunStatus.SUCCESS

    @staticmethod
    def _is_financial(evidence: AgentEvidencePack) -> bool:
        text = " ".join(
            str(evidence.metadata.get(key, "")).casefold()
            for key in ("sector", "industry")
        )
        return any(term in text for term in ("bank", "nbfc", "financial services", "insurance"))

    @staticmethod
    def _validate_identity(request: AgentRequest, evidence: AgentEvidencePack) -> None:
        if request.specialist is not SpecialistId.FUNDAMENTAL:
            raise ValueError("FundamentalSpecialist requires FUNDAMENTAL request identity")
        if AgentCapability.READ_FUNDAMENTALS not in request.allowed_capabilities:
            raise ValueError("FundamentalSpecialist requires READ_FUNDAMENTALS authorization")
        if request.instrument_type is not InstrumentType.EQUITY:
            raise ValueError("FundamentalSpecialist supports company equities only")
        if (
            evidence.request_id != request.request_id
            or evidence.subject != request.subject
            or evidence.evidence_fingerprint != request.evidence_fingerprint
            or evidence.deterministic_assessment_id != request.deterministic_baseline_reference
        ):
            raise ValueError("fundamental evidence does not preserve request/A2 identity")


def fundamental_assessment_from_opinion(opinion: AgentOpinionV2) -> FundamentalAssessment:
    """Reconstruct typed A3.4 detail from a standard Agent opinion."""
    if (
        opinion.specialist_detail_schema_id != FUNDAMENTAL_DETAIL_SCHEMA
        or opinion.specialist_detail_json is None
    ):
        raise ValueError("opinion does not contain A3.4 fundamental detail")
    return FundamentalAssessment.model_validate_json(opinion.specialist_detail_json)


def _latest_records(
    facts: FundamentalFactBook,
    metrics: tuple[FundamentalMetric, ...],
) -> tuple[FundamentalFactRecord, ...]:
    return tuple(item for metric in metrics for item in facts.latest(metric))


def _numbers(
    facts: FundamentalFactBook,
    metrics: tuple[FundamentalMetric, ...],
) -> tuple[float, ...]:
    return tuple(value for metric in metrics if (value := facts.number(metric)) is not None)


def _reference_ids(records: tuple[FundamentalFactRecord, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item.reference.evidence_id for item in records))


def _contradiction(
    code: str,
    description: str,
    records: tuple[FundamentalFactRecord, ...],
) -> FundamentalContradiction:
    return FundamentalContradiction(
        code=code,
        description=description,
        evidence_ids=_reference_ids(records),
        fact_ids=tuple(dict.fromkeys(item.fact.fact_id for item in records)),
    )
