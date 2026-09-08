"""Stable provider-neutral identities for fundamental evidence."""

from enum import StrEnum


class FundamentalFamily(StrEnum):
    """Broad financial evidence families requested through the gateway."""

    INCOME = "INCOME"
    MARGINS = "MARGINS"
    CAPITAL_EFFICIENCY = "CAPITAL_EFFICIENCY"
    CASH_FLOW = "CASH_FLOW"
    BALANCE_SHEET = "BALANCE_SHEET"
    WORKING_CAPITAL = "WORKING_CAPITAL"
    VALUATION = "VALUATION"
    OWNERSHIP = "OWNERSHIP"
    STABILITY = "STABILITY"


class FundamentalMetric(StrEnum):
    """Canonical raw and deterministic derived company metrics."""

    REVENUE = "fundamental.revenue"
    EBITDA = "fundamental.ebitda"
    EBIT = "fundamental.ebit"
    NET_INCOME = "fundamental.net_income"
    EPS = "fundamental.eps"
    OPERATING_MARGIN = "fundamental.operating_margin"
    EBITDA_MARGIN = "fundamental.ebitda_margin"
    NET_MARGIN = "fundamental.net_margin"
    ROE = "fundamental.roe"
    ROCE = "fundamental.roce"
    ROA = "fundamental.roa"
    OPERATING_CASH_FLOW = "fundamental.operating_cash_flow"
    FREE_CASH_FLOW = "fundamental.free_cash_flow"
    CAPEX = "fundamental.capex"
    CASH = "fundamental.cash"
    TOTAL_DEBT = "fundamental.total_debt"
    NET_DEBT = "fundamental.net_debt"
    EQUITY = "fundamental.equity"
    ASSETS = "fundamental.assets"
    LIABILITIES = "fundamental.liabilities"
    RECEIVABLES = "fundamental.receivables"
    INVENTORY = "fundamental.inventory"
    PAYABLES = "fundamental.payables"
    MARKET_CAP = "fundamental.market_cap"
    ENTERPRISE_VALUE = "fundamental.enterprise_value"
    PE = "fundamental.pe"
    PB = "fundamental.pb"
    EV_EBITDA = "fundamental.ev_ebitda"
    PRICE_SALES = "fundamental.price_sales"
    DIVIDEND_YIELD = "fundamental.dividend_yield"
    EARNINGS_YIELD = "fundamental.earnings_yield"
    PROMOTER_OWNERSHIP = "fundamental.promoter_ownership"
    PROMOTER_PLEDGE = "fundamental.promoter_pledge"
    INSTITUTIONAL_OWNERSHIP = "fundamental.institutional_ownership"
    SHARES_OUTSTANDING = "fundamental.shares_outstanding"
    REVENUE_GROWTH_YOY = "fundamental.revenue_growth_yoy"
    REVENUE_GROWTH_QOQ = "fundamental.revenue_growth_qoq"
    PROFIT_GROWTH_YOY = "fundamental.profit_growth_yoy"
    PROFIT_GROWTH_QOQ = "fundamental.profit_growth_qoq"
    REVENUE_CAGR_3Y = "fundamental.revenue_cagr_3y"
    REVENUE_CAGR_5Y = "fundamental.revenue_cagr_5y"
    PROFIT_CAGR_3Y = "fundamental.profit_cagr_3y"
    PROFIT_CAGR_5Y = "fundamental.profit_cagr_5y"
    MARGIN_CHANGE_PP = "fundamental.margin_change_pp"
    ROCE_CHANGE_PP = "fundamental.roce_change_pp"
    DEBT_EQUITY = "fundamental.debt_equity"
    NET_DEBT_EBITDA = "fundamental.net_debt_ebitda"
    INTEREST_COVERAGE = "fundamental.interest_coverage"
    CASH_CONVERSION = "fundamental.cash_conversion"
    FCF_POSITIVE_FRACTION = "fundamental.fcf_positive_fraction"
    EARNINGS_STABILITY = "fundamental.earnings_stability"
    VALUATION_HISTORY_PERCENTILE = "fundamental.valuation_history_percentile"
    SHARE_DILUTION_PERCENT = "fundamental.share_dilution_percent"


class ReportingPeriodKind(StrEnum):
    """Non-interchangeable financial reporting period types."""

    FISCAL_QUARTER = "FISCAL_QUARTER"
    FISCAL_YEAR = "FISCAL_YEAR"
    TTM = "TTM"
    INSTANT = "INSTANT"


class FundamentalUnit(StrEnum):
    """Semantic units; scale and currency remain separate."""

    CURRENCY = "CURRENCY"
    PERCENT = "PERCENT"
    RATIO = "RATIO"
    PER_SHARE = "PER_SHARE"
    COUNT = "COUNT"


class ValueScale(StrEnum):
    """Explicit source scaling for numeric normalization."""

    ONES = "ONES"
    THOUSANDS = "THOUSANDS"
    MILLIONS = "MILLIONS"
    BILLIONS = "BILLIONS"
    LAKHS = "LAKHS"
    CRORES = "CRORES"


class FactBasis(StrEnum):
    """Whether a value was reported by a source or deterministically derived."""

    REPORTED = "REPORTED"
    DERIVED = "DERIVED"


class FundamentalSourceQuality(StrEnum):
    """Categorical provenance strength without an invented credibility score."""

    PRIMARY_FILED = "PRIMARY_FILED"
    EXCHANGE_FILED = "EXCHANGE_FILED"
    REGULATORY = "REGULATORY"
    COMPANY_REPORTED = "COMPANY_REPORTED"
    DERIVED_FROM_PRIMARY = "DERIVED_FROM_PRIMARY"
    TRUSTED_AGGREGATOR = "TRUSTED_AGGREGATOR"
    UNKNOWN = "UNKNOWN"


class MetricResultStatus(StrEnum):
    """Outcome of one deterministic metric request."""

    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    CONFLICTING_DATA = "CONFLICTING_DATA"
    NOT_MEANINGFUL = "NOT_MEANINGFUL"
    SECTOR_POLICY_REQUIRED = "SECTOR_POLICY_REQUIRED"

