"""Deterministic A3.4 company facts and gateway requests."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from tiaf.agents import AgentBudget, AgentCapability, EvidenceGatewayRequest, SpecialistId
from tiaf.context import AnalysisPurpose
from tiaf.contracts import DataQuality, EvidenceType, FreshnessState, Horizon
from tiaf.data import InstrumentKey, InstrumentType, MarketSegment
from tiaf.fundamentals import (
    CompanyIdentity,
    FactBasis,
    FundamentalDerivation,
    FundamentalFact,
    FundamentalFamily,
    FundamentalMetric,
    FundamentalRequest,
    FundamentalSourceQuality,
    FundamentalUnit,
    PeriodRequirement,
    ReportingPeriod,
    ReportingPeriodKind,
    ValueScale,
    fundamental_gateway_attributes,
)

NOW = datetime(2026, 9, 8, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
PUBLISHED = datetime(2026, 5, 15, 18, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
ACQUIRED = datetime(2026, 5, 16, 9, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
FY2026 = ReportingPeriod(
    period_id="FY2026",
    kind=ReportingPeriodKind.FISCAL_YEAR,
    start_date=date(2025, 4, 1),
    end_date=date(2026, 3, 31),
    fiscal_year="FY2026",
)

DEFAULT_VALUES: dict[FundamentalMetric, float] = {
    FundamentalMetric.REVENUE_GROWTH_YOY: 22.0,
    FundamentalMetric.PROFIT_GROWTH_YOY: 25.0,
    FundamentalMetric.REVENUE_CAGR_3Y: 18.0,
    FundamentalMetric.PROFIT_CAGR_3Y: 20.0,
    FundamentalMetric.OPERATING_MARGIN: 18.0,
    FundamentalMetric.NET_MARGIN: 16.0,
    FundamentalMetric.MARGIN_CHANGE_PP: 2.0,
    FundamentalMetric.ROE: 22.0,
    FundamentalMetric.ROCE: 24.0,
    FundamentalMetric.ROCE_CHANGE_PP: 2.0,
    FundamentalMetric.DEBT_EQUITY: 0.3,
    FundamentalMetric.INTEREST_COVERAGE: 8.0,
    FundamentalMetric.RECEIVABLES: 25.0,
    FundamentalMetric.OPERATING_CASH_FLOW: 120.0,
    FundamentalMetric.FREE_CASH_FLOW: 80.0,
    FundamentalMetric.CASH_CONVERSION: 1.05,
    FundamentalMetric.FCF_POSITIVE_FRACTION: 0.9,
    FundamentalMetric.NET_INCOME: 100.0,
    FundamentalMetric.VALUATION_HISTORY_PERCENTILE: 40.0,
    FundamentalMetric.EARNINGS_STABILITY: 0.9,
    FundamentalMetric.PROMOTER_OWNERSHIP: 51.0,
    FundamentalMetric.PROMOTER_PLEDGE: 0.0,
    FundamentalMetric.SHARE_DILUTION_PERCENT: 0.0,
}

_FAMILIES = {
    FundamentalMetric.REVENUE_GROWTH_YOY: FundamentalFamily.INCOME,
    FundamentalMetric.PROFIT_GROWTH_YOY: FundamentalFamily.INCOME,
    FundamentalMetric.REVENUE_CAGR_3Y: FundamentalFamily.INCOME,
    FundamentalMetric.PROFIT_CAGR_3Y: FundamentalFamily.INCOME,
    FundamentalMetric.NET_INCOME: FundamentalFamily.INCOME,
    FundamentalMetric.OPERATING_MARGIN: FundamentalFamily.MARGINS,
    FundamentalMetric.NET_MARGIN: FundamentalFamily.MARGINS,
    FundamentalMetric.MARGIN_CHANGE_PP: FundamentalFamily.MARGINS,
    FundamentalMetric.ROE: FundamentalFamily.CAPITAL_EFFICIENCY,
    FundamentalMetric.ROCE: FundamentalFamily.CAPITAL_EFFICIENCY,
    FundamentalMetric.ROCE_CHANGE_PP: FundamentalFamily.CAPITAL_EFFICIENCY,
    FundamentalMetric.DEBT_EQUITY: FundamentalFamily.BALANCE_SHEET,
    FundamentalMetric.INTEREST_COVERAGE: FundamentalFamily.BALANCE_SHEET,
    FundamentalMetric.RECEIVABLES: FundamentalFamily.WORKING_CAPITAL,
    FundamentalMetric.OPERATING_CASH_FLOW: FundamentalFamily.CASH_FLOW,
    FundamentalMetric.FREE_CASH_FLOW: FundamentalFamily.CASH_FLOW,
    FundamentalMetric.CASH_CONVERSION: FundamentalFamily.CASH_FLOW,
    FundamentalMetric.FCF_POSITIVE_FRACTION: FundamentalFamily.CASH_FLOW,
    FundamentalMetric.VALUATION_HISTORY_PERCENTILE: FundamentalFamily.VALUATION,
    FundamentalMetric.EARNINGS_STABILITY: FundamentalFamily.STABILITY,
    FundamentalMetric.PROMOTER_OWNERSHIP: FundamentalFamily.OWNERSHIP,
    FundamentalMetric.PROMOTER_PLEDGE: FundamentalFamily.OWNERSHIP,
    FundamentalMetric.SHARE_DILUTION_PERCENT: FundamentalFamily.OWNERSHIP,
}

_CURRENCY_METRICS = {
    FundamentalMetric.REVENUE,
    FundamentalMetric.EBITDA,
    FundamentalMetric.EBIT,
    FundamentalMetric.NET_INCOME,
    FundamentalMetric.OPERATING_CASH_FLOW,
    FundamentalMetric.FREE_CASH_FLOW,
    FundamentalMetric.CAPEX,
    FundamentalMetric.CASH,
    FundamentalMetric.TOTAL_DEBT,
    FundamentalMetric.NET_DEBT,
    FundamentalMetric.EQUITY,
    FundamentalMetric.ASSETS,
    FundamentalMetric.LIABILITIES,
    FundamentalMetric.RECEIVABLES,
    FundamentalMetric.INVENTORY,
    FundamentalMetric.PAYABLES,
    FundamentalMetric.MARKET_CAP,
    FundamentalMetric.ENTERPRISE_VALUE,
}


def company(*, financial: bool = False) -> CompanyIdentity:
    symbol = "HDFCBANK" if financial else "RELIANCE"
    return CompanyIdentity(
        symbol=symbol,
        listing=InstrumentKey(
            symbol=symbol,
            exchange="NSE",
            segment=MarketSegment.NSE_EQUITY,
            instrument_type=InstrumentType.EQUITY,
        ),
        legal_name="HDFC Bank Limited" if financial else "Reliance Industries Limited",
        sector="Banking" if financial else "Energy",
        industry="Private sector bank" if financial else "Diversified industrial",
        provider_entity_id=f"NSE:{symbol}",
    )


def fact(
    metric: FundamentalMetric,
    value: float,
    *,
    company_identity: CompanyIdentity | None = None,
    period: ReportingPeriod = FY2026,
    suffix: str = "primary",
    published_at: datetime = PUBLISHED,
    acquired_at: datetime = ACQUIRED,
    source_provider: str = "fixture.exchange",
    source_quality: FundamentalSourceQuality = FundamentalSourceQuality.EXCHANGE_FILED,
    revision: int = 0,
    revision_id: str | None = None,
    replaces_fact_id: str | None = None,
    quality: DataQuality = DataQuality.GOOD,
    freshness: FreshnessState = FreshnessState.FRESH,
) -> FundamentalFact:
    monetary = metric in _CURRENCY_METRICS
    return FundamentalFact(
        fact_id=f"fact:{metric.name.casefold()}:{period.period_id}:{suffix}",
        company=company_identity or company(),
        metric=metric,
        family=_FAMILIES.get(metric, FundamentalFamily.INCOME),
        value=value,
        unit=(
            FundamentalUnit.CURRENCY
            if monetary
            else FundamentalUnit.PERCENT
            if metric.value.endswith(("percentile", "_yoy", "_3y", "_pp"))
            or metric
            in {
                FundamentalMetric.OPERATING_MARGIN,
                FundamentalMetric.NET_MARGIN,
                FundamentalMetric.ROE,
                FundamentalMetric.ROCE,
                FundamentalMetric.PROMOTER_OWNERSHIP,
                FundamentalMetric.PROMOTER_PLEDGE,
                FundamentalMetric.SHARE_DILUTION_PERCENT,
            }
            else FundamentalUnit.RATIO
        ),
        scale=ValueScale.CRORES if monetary else ValueScale.ONES,
        currency="INR" if monetary else None,
        period=period,
        basis=FactBasis.REPORTED,
        source_quality=source_quality,
        source_provider=source_provider,
        source_reference=f"fixture://{metric.value}/{period.period_id}/{suffix}",
        published_at=published_at,
        acquired_at=acquired_at,
        revision=revision,
        revision_id=revision_id,
        replaces_fact_id=replaces_fact_id,
        quality=quality,
        freshness=freshness,
    )


def derived_fact(
    metric: FundamentalMetric,
    value: float,
    *,
    source_fact_ids: tuple[str, ...] = ("source:prior", "source:current"),
) -> FundamentalFact:
    base = fact(metric, value)
    return base.model_copy(
        update={
            "basis": FactBasis.DERIVED,
            "source_quality": FundamentalSourceQuality.DERIVED_FROM_PRIMARY,
            "derivation": FundamentalDerivation(
                formula_id="fixture.formula",
                formula_version="1.0",
                source_fact_ids=source_fact_ids,
                requested_window="EXACT",
            ),
        }
    )


def facts(
    *,
    overrides: dict[FundamentalMetric, float] | None = None,
    omit: tuple[FundamentalMetric, ...] = (),
    financial: bool = False,
    quality: DataQuality = DataQuality.GOOD,
    freshness: FreshnessState = FreshnessState.FRESH,
) -> tuple[FundamentalFact, ...]:
    values = {**DEFAULT_VALUES, **(overrides or {})}
    identity = company(financial=financial)
    return tuple(
        fact(
            metric,
            value,
            company_identity=identity,
            quality=quality,
            freshness=freshness,
        )
        for metric, value in values.items()
        if metric not in omit
    )


def fundamental_request(*, financial: bool = False) -> FundamentalRequest:
    return FundamentalRequest(
        request_id="fundamental-read",
        company=company(financial=financial),
        as_of=NOW,
        horizon=Horizon(label="six-month", min_days=90, max_days=180),
        families=tuple(FundamentalFamily),
        periods=(PeriodRequirement(kind=ReportingPeriodKind.FISCAL_YEAR, count=1),),
        required_freshness=FreshnessState.FRESH,
    )


def gateway_request(*, financial: bool = False) -> EvidenceGatewayRequest:
    typed = fundamental_request(financial=financial)
    return EvidenceGatewayRequest(
        request_id=typed.request_id,
        capability=AgentCapability.READ_FUNDAMENTALS,
        allowed_capabilities=(AgentCapability.READ_FUNDAMENTALS,),
        subject=typed.company.symbol,
        instrument_type=InstrumentType.EQUITY,
        horizon=typed.horizon,
        purpose=AnalysisPurpose.OPPORTUNITY,
        evidence_type=EvidenceType.FUNDAMENTAL,
        requested_attributes=fundamental_gateway_attributes(typed),
        as_of=typed.as_of,
        required_freshness=typed.required_freshness,
        context_references=("a2-context",),
        evidence_fingerprint="a" * 64,
        deterministic_baseline_reference="a2-assessment",
        requesting_specialist=SpecialistId.FUNDAMENTAL,
        budget=AgentBudget(max_tool_calls=1),
        timeout_seconds=2.0,
    )
