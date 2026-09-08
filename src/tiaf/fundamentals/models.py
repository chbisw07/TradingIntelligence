"""Immutable provider-neutral contracts for point-in-time company evidence."""

import hashlib
import json
import math
from datetime import date, datetime
from typing import Annotated, Self

from pydantic import Field, StringConstraints, field_validator, model_validator

from tiaf.agents._validation import require_unique, validate_safe_metadata
from tiaf.contracts import ContractModel, DataQuality, FreshnessState, Horizon
from tiaf.contracts.common import Metadata, NonEmptyStr, Symbol, TiafDateTime
from tiaf.data import InstrumentKey, InstrumentType

from .enums import (
    FactBasis,
    FundamentalFamily,
    FundamentalMetric,
    FundamentalSourceQuality,
    FundamentalUnit,
    MetricResultStatus,
    ReportingPeriodKind,
    ValueScale,
)
from .quality import weakest_freshness, weakest_quality

CurrencyCode = Annotated[
    str,
    StringConstraints(strip_whitespace=True, to_upper=True, pattern=r"^[A-Z]{3}$"),
]
FiniteFloat = Annotated[float, Field(allow_inf_nan=False)]
UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]

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
_PERCENT_METRICS = {
    FundamentalMetric.OPERATING_MARGIN,
    FundamentalMetric.EBITDA_MARGIN,
    FundamentalMetric.NET_MARGIN,
    FundamentalMetric.ROE,
    FundamentalMetric.ROCE,
    FundamentalMetric.ROA,
    FundamentalMetric.DIVIDEND_YIELD,
    FundamentalMetric.EARNINGS_YIELD,
    FundamentalMetric.PROMOTER_OWNERSHIP,
    FundamentalMetric.PROMOTER_PLEDGE,
    FundamentalMetric.INSTITUTIONAL_OWNERSHIP,
    FundamentalMetric.REVENUE_GROWTH_YOY,
    FundamentalMetric.REVENUE_GROWTH_QOQ,
    FundamentalMetric.PROFIT_GROWTH_YOY,
    FundamentalMetric.PROFIT_GROWTH_QOQ,
    FundamentalMetric.REVENUE_CAGR_3Y,
    FundamentalMetric.REVENUE_CAGR_5Y,
    FundamentalMetric.PROFIT_CAGR_3Y,
    FundamentalMetric.PROFIT_CAGR_5Y,
    FundamentalMetric.MARGIN_CHANGE_PP,
    FundamentalMetric.ROCE_CHANGE_PP,
    FundamentalMetric.VALUATION_HISTORY_PERCENTILE,
    FundamentalMetric.SHARE_DILUTION_PERCENT,
}
_RATIO_METRICS = {
    FundamentalMetric.PE,
    FundamentalMetric.PB,
    FundamentalMetric.EV_EBITDA,
    FundamentalMetric.PRICE_SALES,
    FundamentalMetric.DEBT_EQUITY,
    FundamentalMetric.NET_DEBT_EBITDA,
    FundamentalMetric.INTEREST_COVERAGE,
    FundamentalMetric.CASH_CONVERSION,
    FundamentalMetric.FCF_POSITIVE_FRACTION,
    FundamentalMetric.EARNINGS_STABILITY,
}
_METRIC_FAMILIES = {
    **{
        metric: FundamentalFamily.INCOME
        for metric in {
            FundamentalMetric.REVENUE,
            FundamentalMetric.EBITDA,
            FundamentalMetric.EBIT,
            FundamentalMetric.NET_INCOME,
            FundamentalMetric.EPS,
            FundamentalMetric.REVENUE_GROWTH_YOY,
            FundamentalMetric.REVENUE_GROWTH_QOQ,
            FundamentalMetric.PROFIT_GROWTH_YOY,
            FundamentalMetric.PROFIT_GROWTH_QOQ,
            FundamentalMetric.REVENUE_CAGR_3Y,
            FundamentalMetric.REVENUE_CAGR_5Y,
            FundamentalMetric.PROFIT_CAGR_3Y,
            FundamentalMetric.PROFIT_CAGR_5Y,
        }
    },
    **{
        metric: FundamentalFamily.MARGINS
        for metric in {
            FundamentalMetric.OPERATING_MARGIN,
            FundamentalMetric.EBITDA_MARGIN,
            FundamentalMetric.NET_MARGIN,
            FundamentalMetric.MARGIN_CHANGE_PP,
        }
    },
    **{
        metric: FundamentalFamily.CAPITAL_EFFICIENCY
        for metric in {
            FundamentalMetric.ROE,
            FundamentalMetric.ROCE,
            FundamentalMetric.ROA,
            FundamentalMetric.ROCE_CHANGE_PP,
        }
    },
    **{
        metric: FundamentalFamily.CASH_FLOW
        for metric in {
            FundamentalMetric.OPERATING_CASH_FLOW,
            FundamentalMetric.FREE_CASH_FLOW,
            FundamentalMetric.CAPEX,
            FundamentalMetric.CASH_CONVERSION,
            FundamentalMetric.FCF_POSITIVE_FRACTION,
        }
    },
    **{
        metric: FundamentalFamily.BALANCE_SHEET
        for metric in {
            FundamentalMetric.CASH,
            FundamentalMetric.TOTAL_DEBT,
            FundamentalMetric.NET_DEBT,
            FundamentalMetric.EQUITY,
            FundamentalMetric.ASSETS,
            FundamentalMetric.LIABILITIES,
            FundamentalMetric.DEBT_EQUITY,
            FundamentalMetric.NET_DEBT_EBITDA,
            FundamentalMetric.INTEREST_COVERAGE,
        }
    },
    **{
        metric: FundamentalFamily.WORKING_CAPITAL
        for metric in {
            FundamentalMetric.RECEIVABLES,
            FundamentalMetric.INVENTORY,
            FundamentalMetric.PAYABLES,
        }
    },
    **{
        metric: FundamentalFamily.VALUATION
        for metric in {
            FundamentalMetric.MARKET_CAP,
            FundamentalMetric.ENTERPRISE_VALUE,
            FundamentalMetric.PE,
            FundamentalMetric.PB,
            FundamentalMetric.EV_EBITDA,
            FundamentalMetric.PRICE_SALES,
            FundamentalMetric.DIVIDEND_YIELD,
            FundamentalMetric.EARNINGS_YIELD,
            FundamentalMetric.VALUATION_HISTORY_PERCENTILE,
        }
    },
    **{
        metric: FundamentalFamily.OWNERSHIP
        for metric in {
            FundamentalMetric.PROMOTER_OWNERSHIP,
            FundamentalMetric.PROMOTER_PLEDGE,
            FundamentalMetric.INSTITUTIONAL_OWNERSHIP,
            FundamentalMetric.SHARES_OUTSTANDING,
            FundamentalMetric.SHARE_DILUTION_PERCENT,
        }
    },
    FundamentalMetric.EARNINGS_STABILITY: FundamentalFamily.STABILITY,
}


class CompanyIdentity(ContractModel):
    """Stable company identity reusing the accepted listed-instrument identity."""

    symbol: Symbol
    listing: InstrumentKey
    legal_name: NonEmptyStr | None = None
    sector: NonEmptyStr | None = None
    industry: NonEmptyStr | None = None
    provider_entity_id: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_listing(self) -> Self:
        if self.listing.instrument_type is not InstrumentType.EQUITY:
            raise ValueError("fundamental company identity requires an equity listing")
        if self.listing.symbol != self.symbol:
            raise ValueError("company symbol must match listing symbol")
        return self


class ReportingPeriod(ContractModel):
    """Exact fiscal/reporting interval; different periodicities never compare silently."""

    period_id: NonEmptyStr
    kind: ReportingPeriodKind
    start_date: date
    end_date: date
    fiscal_year: NonEmptyStr | None = None
    fiscal_quarter: int | None = Field(default=None, ge=1, le=4)
    constituent_period_ids: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_period(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError("reporting period end_date cannot predate start_date")
        require_unique(self.constituent_period_ids, "constituent period IDs")
        if self.kind is ReportingPeriodKind.FISCAL_QUARTER:
            if self.fiscal_year is None or self.fiscal_quarter is None:
                raise ValueError("fiscal quarter requires year and quarter identity")
            if self.constituent_period_ids:
                raise ValueError("reported quarter cannot contain constituent periods")
        elif self.kind is ReportingPeriodKind.FISCAL_YEAR:
            if self.fiscal_year is None or self.fiscal_quarter is not None:
                raise ValueError("fiscal year requires year identity and no quarter")
            if self.constituent_period_ids:
                raise ValueError("reported year cannot contain constituent periods")
        elif self.kind is ReportingPeriodKind.TTM:
            if self.fiscal_quarter is not None or len(self.constituent_period_ids) != 4:
                raise ValueError("TTM requires exactly four constituent quarters")
        elif self.kind is ReportingPeriodKind.INSTANT:
            if self.start_date != self.end_date:
                raise ValueError("instant period requires equal start and end dates")
            if self.fiscal_quarter is not None or self.constituent_period_ids:
                raise ValueError("instant period cannot claim quarter constituents")
        return self


class FundamentalDerivation(ContractModel):
    """Auditable deterministic derivation identity."""

    formula_id: NonEmptyStr
    formula_version: NonEmptyStr
    source_fact_ids: tuple[NonEmptyStr, ...]
    requested_window: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_sources(self) -> Self:
        if not self.source_fact_ids:
            raise ValueError("derivation requires source facts")
        require_unique(self.source_fact_ids, "derivation source fact IDs")
        return self


class FundamentalFact(ContractModel):
    """One reported or derived numeric fact with full point-in-time provenance."""

    fact_id: NonEmptyStr
    company: CompanyIdentity
    metric: FundamentalMetric
    family: FundamentalFamily
    value: FiniteFloat
    unit: FundamentalUnit
    scale: ValueScale = ValueScale.ONES
    currency: CurrencyCode | None = None
    period: ReportingPeriod
    basis: FactBasis
    source_quality: FundamentalSourceQuality
    source_provider: NonEmptyStr
    source_reference: NonEmptyStr
    published_at: TiafDateTime
    acquired_at: TiafDateTime
    revision: int = Field(default=0, ge=0)
    revision_id: NonEmptyStr | None = None
    replaces_fact_id: NonEmptyStr | None = None
    derivation: FundamentalDerivation | None = None
    quality: DataQuality
    freshness: FreshnessState
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_fact(self) -> Self:
        if not math.isfinite(self.value):
            raise ValueError("fundamental fact value must be finite")
        monetary = self.unit in {FundamentalUnit.CURRENCY, FundamentalUnit.PER_SHARE}
        if monetary != (self.currency is not None):
            raise ValueError("currency is required only for monetary/per-share facts")
        if not monetary and self.scale is not ValueScale.ONES:
            raise ValueError("non-monetary facts must use ONES scale")
        expected_unit = (
            FundamentalUnit.CURRENCY
            if self.metric in _CURRENCY_METRICS
            else FundamentalUnit.PER_SHARE
            if self.metric is FundamentalMetric.EPS
            else FundamentalUnit.COUNT
            if self.metric is FundamentalMetric.SHARES_OUTSTANDING
            else FundamentalUnit.PERCENT
            if self.metric in _PERCENT_METRICS
            else FundamentalUnit.RATIO
            if self.metric in _RATIO_METRICS
            else None
        )
        if expected_unit is None or self.unit is not expected_unit:
            raise ValueError(f"{self.metric.value} requires {expected_unit} unit")
        if self.family is not _METRIC_FAMILIES[self.metric]:
            raise ValueError(
                f"{self.metric.value} requires {_METRIC_FAMILIES[self.metric]} family"
            )
        if self.acquired_at < self.published_at:
            raise ValueError("fundamental acquisition cannot predate publication")
        if self.basis is FactBasis.DERIVED:
            if self.derivation is None:
                raise ValueError("derived fact requires derivation metadata")
        elif self.derivation is not None:
            raise ValueError("reported fact cannot claim deterministic derivation")
        if self.revision == 0 and any(
            value is not None for value in (self.revision_id, self.replaces_fact_id)
        ):
            raise ValueError("revision metadata requires a positive revision")
        if self.revision > 0 and self.revision_id is None:
            raise ValueError("positive revision requires revision_id")
        return self


class PeriodRequirement(ContractModel):
    """Exact requested reporting-history depth; no silent shortening is allowed."""

    kind: ReportingPeriodKind
    count: int = Field(gt=0)


class FundamentalRequest(ContractModel):
    """Typed bounded read request with no arbitrary URL or query field."""

    request_id: NonEmptyStr
    company: CompanyIdentity
    as_of: TiafDateTime
    horizon: Horizon
    families: tuple[FundamentalFamily, ...]
    periods: tuple[PeriodRequirement, ...]
    required_freshness: FreshnessState

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        if not self.families or not self.periods:
            raise ValueError("fundamental request requires families and period depth")
        require_unique(self.families, "fundamental families")
        require_unique(tuple(item.kind for item in self.periods), "period requirement kinds")
        return self


class FundamentalMetricResult(ContractModel):
    """One deterministic preprocessing result with exact formula/source identity."""

    result_id: NonEmptyStr
    metric: FundamentalMetric
    family: FundamentalFamily
    status: MetricResultStatus
    value: FiniteFloat | None = None
    unit: FundamentalUnit | None = None
    currency: CurrencyCode | None = None
    period: ReportingPeriod | None = None
    source_fact_ids: tuple[NonEmptyStr, ...] = ()
    formula_id: NonEmptyStr
    formula_version: NonEmptyStr
    requested_window: NonEmptyStr | None = None
    reason: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        require_unique(self.source_fact_ids, "metric result source fact IDs")
        if self.status is MetricResultStatus.AVAILABLE:
            if (
                self.value is None
                or self.unit is None
                or self.period is None
                or not self.source_fact_ids
                or self.reason is not None
            ):
                raise ValueError("available metric result requires complete output")
        elif self.value is not None or self.period is not None:
            raise ValueError("unavailable metric result cannot expose a value/period")
        return self


class FundamentalDataset(ContractModel):
    """Point-in-time normalized facts returned by one provider invocation."""

    dataset_id: NonEmptyStr
    company: CompanyIdentity
    provider_id: NonEmptyStr
    provider_version: NonEmptyStr
    requested_as_of: TiafDateTime
    acquired_at: TiafDateTime
    valid_until: TiafDateTime
    facts: tuple[FundamentalFact, ...]
    missing_families: tuple[FundamentalFamily, ...] = ()
    missing_periods: tuple[PeriodRequirement, ...] = ()
    quality: DataQuality
    freshness: FreshnessState
    point_in_time_limitation: NonEmptyStr | None = None
    fingerprint: NonEmptyStr

    @model_validator(mode="after")
    def validate_dataset(self) -> Self:
        if self.valid_until <= self.acquired_at:
            raise ValueError("fundamental valid_until must follow acquisition")
        require_unique(tuple(item.fact_id for item in self.facts), "fundamental fact IDs")
        require_unique(self.missing_families, "missing fundamental families")
        require_unique(
            tuple(item.kind for item in self.missing_periods),
            "missing fundamental period kinds",
        )
        if any(item.company != self.company for item in self.facts):
            raise ValueError("all fundamental facts must match exact dataset company identity")
        if {item.family for item in self.facts} & set(self.missing_families):
            raise ValueError("present fundamental family cannot also be marked missing")
        for requirement in self.missing_periods:
            available = len(
                {
                    item.period.period_id
                    for item in self.facts
                    if item.period.kind is requirement.kind
                }
            )
            if available >= requirement.count:
                raise ValueError("satisfied reporting-period depth cannot be marked missing")
        if self.quality is not weakest_quality(tuple(item.quality for item in self.facts)):
            raise ValueError("dataset quality must equal weakest fact quality")
        if self.freshness is not weakest_freshness(
            tuple(item.freshness for item in self.facts)
        ):
            raise ValueError("dataset freshness must equal weakest fact freshness")
        if any(
            item.published_at > self.requested_as_of
            or item.acquired_at > self.requested_as_of
            for item in self.facts
        ):
            raise ValueError("dataset cannot contain facts unavailable at requested as-of")
        if self.fingerprint != fundamental_fingerprint(
            self.company,
            self.provider_id,
            self.provider_version,
            self.requested_as_of,
            self.facts,
            self.missing_families,
            self.missing_periods,
            self.point_in_time_limitation,
        ):
            raise ValueError("fundamental dataset fingerprint does not match content")
        return self


def fundamental_fingerprint(
    company: CompanyIdentity,
    provider_id: str,
    provider_version: str,
    requested_as_of: datetime,
    facts: tuple[FundamentalFact, ...],
    missing_families: tuple[FundamentalFamily, ...],
    missing_periods: tuple[PeriodRequirement, ...] = (),
    point_in_time_limitation: str | None = None,
) -> str:
    """Return stable SHA-256 identity for decision-visible fundamental content."""
    payload = {
        "company": company.model_dump(mode="json"),
        "provider_id": provider_id,
        "provider_version": provider_version,
        "requested_as_of": requested_as_of.isoformat(),
        "facts": [item.model_dump(mode="json") for item in facts],
        "missing_families": [item.value for item in missing_families],
        "missing_periods": [item.model_dump(mode="json") for item in missing_periods],
        "point_in_time_limitation": point_in_time_limitation,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode()).hexdigest()
