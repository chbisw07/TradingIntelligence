"""Deterministic, period-safe fundamental calculations outside Agent reasoning."""

import math
from datetime import timedelta

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
from .models import (
    FundamentalDerivation,
    FundamentalFact,
    FundamentalMetricResult,
    ReportingPeriod,
)
from .normalization import FundamentalNormalizationError, ensure_compatible_values, normalize_scale
from .quality import weakest_freshness, weakest_quality

FORMULA_VERSION = "1.0"


def growth_rate(
    current: FundamentalFact,
    comparison: FundamentalFact,
    output_metric: FundamentalMetric,
    *,
    mode: str,
) -> FundamentalMetricResult:
    """Calculate period-safe YoY or QoQ growth in percent points."""
    formula_id = f"fundamental.growth.{mode.casefold()}"
    try:
        ensure_compatible_values((current, comparison))
        _validate_growth_periods(current.period, comparison.period, mode)
        current_value = normalize_scale(current).value
        comparison_value = normalize_scale(comparison).value
    except FundamentalNormalizationError as exc:
        return _unavailable(output_metric, current.family, formula_id, str(exc))
    if comparison_value == 0:
        return _unavailable(
            output_metric,
            current.family,
            formula_id,
            "comparison value is zero",
            MetricResultStatus.NOT_MEANINGFUL,
        )
    return _available(
        output_metric,
        current.family,
        (current_value / comparison_value - 1.0) * 100.0,
        FundamentalUnit.PERCENT,
        current.period,
        (comparison, current),
        formula_id,
        mode.upper(),
    )


def compound_annual_growth_rate(
    annual_facts: tuple[FundamentalFact, ...],
    *,
    years: int,
    output_metric: FundamentalMetric,
) -> FundamentalMetricResult:
    """Calculate exact N-year CAGR from N+1 consecutive fiscal-year observations."""
    formula_id = "fundamental.cagr"
    requested = f"{years}Y"
    ordered = tuple(sorted(annual_facts, key=lambda item: item.period.end_date))
    family = ordered[0].family if ordered else FundamentalFamily.INCOME
    if years <= 0 or len(ordered) != years + 1:
        return _unavailable(
            output_metric,
            family,
            formula_id,
            "exact N+1 annual observations required",
            requested_window=requested,
        )
    try:
        ensure_compatible_values(ordered)
        if any(item.period.kind is not ReportingPeriodKind.FISCAL_YEAR for item in ordered):
            raise FundamentalNormalizationError("CAGR requires fiscal-year observations")
        for prior, current in zip(ordered[:-1], ordered[1:], strict=True):
            days = (current.period.end_date - prior.period.end_date).days
            if not 330 <= days <= 400:
                raise FundamentalNormalizationError(
                    "annual history contains a missing fiscal year"
                )
        first, last = normalize_scale(ordered[0]), normalize_scale(ordered[-1])
    except FundamentalNormalizationError as exc:
        return _unavailable(
            output_metric,
            family,
            formula_id,
            str(exc),
            requested_window=requested,
        )
    if first.value <= 0 or last.value <= 0:
        return _unavailable(
            output_metric,
            family,
            formula_id,
            "CAGR endpoints must be positive",
            MetricResultStatus.NOT_MEANINGFUL,
            requested_window=requested,
        )
    value = (math.pow(last.value / first.value, 1.0 / years) - 1.0) * 100.0
    return _available(
        output_metric,
        family,
        value,
        FundamentalUnit.PERCENT,
        last.period,
        ordered,
        formula_id,
        requested,
    )


def trailing_twelve_months(
    quarters: tuple[FundamentalFact, ...],
    *,
    output_metric: FundamentalMetric,
) -> FundamentalMetricResult:
    """Sum exactly four contiguous fiscal quarters without silent gap filling."""
    formula_id = "fundamental.ttm_sum"
    ordered = tuple(sorted(quarters, key=lambda item: item.period.start_date))
    family = ordered[0].family if ordered else FundamentalFamily.INCOME
    if len(ordered) != 4:
        return _unavailable(
            output_metric,
            family,
            formula_id,
            "TTM requires exactly four quarters",
            requested_window="4Q",
        )
    try:
        ensure_compatible_values(ordered)
        if any(item.period.kind is not ReportingPeriodKind.FISCAL_QUARTER for item in ordered):
            raise FundamentalNormalizationError("TTM requires fiscal quarters")
        for prior, current in zip(ordered[:-1], ordered[1:], strict=True):
            if current.period.start_date != prior.period.end_date + timedelta(days=1):
                raise FundamentalNormalizationError("TTM quarters must be contiguous")
        normalized_values = tuple(normalize_scale(item).value for item in ordered)
    except FundamentalNormalizationError as exc:
        return _unavailable(
            output_metric,
            family,
            formula_id,
            str(exc),
            requested_window="4Q",
        )
    period = ReportingPeriod(
        period_id=f"TTM:{ordered[-1].period.end_date.isoformat()}",
        kind=ReportingPeriodKind.TTM,
        start_date=ordered[0].period.start_date,
        end_date=ordered[-1].period.end_date,
        fiscal_year=ordered[-1].period.fiscal_year,
        constituent_period_ids=tuple(item.period.period_id for item in ordered),
    )
    return _available(
        output_metric,
        family,
        sum(normalized_values),
        ordered[0].unit,
        period,
        ordered,
        formula_id,
        "4Q",
        currency=ordered[0].currency,
    )


def ratio_metric(
    numerator: FundamentalFact,
    denominator: FundamentalFact,
    *,
    output_metric: FundamentalMetric,
    family: FundamentalFamily,
    as_percent: bool = False,
) -> FundamentalMetricResult:
    """Calculate a same-period, same-currency deterministic ratio."""
    formula_id = "fundamental.ratio"
    if numerator.company.symbol != denominator.company.symbol:
        return _unavailable(output_metric, family, formula_id, "ratio cannot mix companies")
    if numerator.period != denominator.period:
        return _unavailable(
            output_metric, family, formula_id, "ratio requires identical reporting periods"
        )
    if numerator.currency != denominator.currency or numerator.currency is None:
        return _unavailable(
            output_metric,
            family,
            formula_id,
            "ratio requires identical explicit currency",
        )
    try:
        numerator_value = normalize_scale(numerator).value
        denominator_value = normalize_scale(denominator).value
    except FundamentalNormalizationError as exc:
        return _unavailable(output_metric, family, formula_id, str(exc))
    if denominator_value == 0:
        return _unavailable(
            output_metric,
            family,
            formula_id,
            "ratio denominator is zero",
            MetricResultStatus.NOT_MEANINGFUL,
        )
    value = numerator_value / denominator_value
    if as_percent:
        value *= 100.0
    return _available(
        output_metric,
        family,
        value,
        FundamentalUnit.PERCENT if as_percent else FundamentalUnit.RATIO,
        numerator.period,
        (numerator, denominator),
        formula_id,
        "same-period",
    )


def metric_result_to_fact(
    result: FundamentalMetricResult,
    *,
    fact_id: str,
    source_facts: tuple[FundamentalFact, ...],
) -> FundamentalFact:
    """Convert an available deterministic result into an explicitly derived fact."""
    if (
        result.status is not MetricResultStatus.AVAILABLE
        or result.value is None
        or result.unit is None
        or result.period is None
        or not source_facts
    ):
        raise ValueError("only available metric results can become derived facts")
    template = source_facts[-1]
    if tuple(item.fact_id for item in source_facts) != result.source_fact_ids:
        raise ValueError("derived fact sources must exactly match metric result provenance")
    return FundamentalFact(
        fact_id=fact_id,
        company=template.company,
        metric=result.metric,
        family=result.family,
        value=result.value,
        unit=result.unit,
        scale=ValueScale.ONES,
        currency=result.currency,
        period=result.period,
        basis=FactBasis.DERIVED,
        source_quality=_derived_source_quality(source_facts),
        source_provider="tiaf.fundamentals",
        source_reference=result.result_id,
        published_at=max(item.published_at for item in source_facts),
        acquired_at=max(item.acquired_at for item in source_facts),
        derivation=FundamentalDerivation(
            formula_id=result.formula_id,
            formula_version=result.formula_version,
            source_fact_ids=result.source_fact_ids,
            requested_window=result.requested_window,
        ),
        quality=weakest_quality(tuple(item.quality for item in source_facts)),
        freshness=weakest_freshness(tuple(item.freshness for item in source_facts)),
    )


def _validate_growth_periods(
    current: ReportingPeriod,
    comparison: ReportingPeriod,
    mode: str,
) -> None:
    if current.kind is not comparison.kind:
        raise FundamentalNormalizationError("growth cannot mix reporting periodicities")
    days = (current.end_date - comparison.end_date).days
    if mode == "YOY":
        if current.kind is ReportingPeriodKind.FISCAL_QUARTER:
            if current.fiscal_quarter != comparison.fiscal_quarter or not 330 <= days <= 400:
                raise FundamentalNormalizationError(
                    "quarterly YoY requires same fiscal quarter one year earlier"
                )
        elif current.kind is ReportingPeriodKind.FISCAL_YEAR:
            if not 330 <= days <= 400:
                raise FundamentalNormalizationError(
                    "annual YoY requires consecutive fiscal years"
                )
        else:
            raise FundamentalNormalizationError(
                "YoY requires fiscal quarter or fiscal year"
            )
    elif mode == "QOQ":
        if current.kind is not ReportingPeriodKind.FISCAL_QUARTER:
            raise FundamentalNormalizationError("QoQ requires fiscal quarters")
        if current.start_date != comparison.end_date + timedelta(days=1):
            raise FundamentalNormalizationError("QoQ requires adjacent fiscal quarters")
    else:
        raise FundamentalNormalizationError("growth mode must be YOY or QOQ")


def _available(
    metric: FundamentalMetric,
    family: FundamentalFamily,
    value: float,
    unit: FundamentalUnit,
    period: ReportingPeriod,
    facts: tuple[FundamentalFact, ...],
    formula_id: str,
    requested_window: str,
    *,
    currency: str | None = None,
) -> FundamentalMetricResult:
    if not math.isfinite(value):
        return _unavailable(
            metric,
            family,
            formula_id,
            "derived metric is not finite",
            MetricResultStatus.NOT_MEANINGFUL,
            requested_window=requested_window,
        )
    return FundamentalMetricResult(
        result_id=f"metric:{metric.value}:{period.period_id}:{formula_id}:{requested_window}",
        metric=metric,
        family=family,
        status=MetricResultStatus.AVAILABLE,
        value=value,
        unit=unit,
        currency=currency,
        period=period,
        source_fact_ids=tuple(item.fact_id for item in facts),
        formula_id=formula_id,
        formula_version=FORMULA_VERSION,
        requested_window=requested_window,
    )


def _unavailable(
    metric: FundamentalMetric,
    family: FundamentalFamily,
    formula_id: str,
    reason: str,
    status: MetricResultStatus = MetricResultStatus.INSUFFICIENT_DATA,
    *,
    requested_window: str | None = None,
) -> FundamentalMetricResult:
    return FundamentalMetricResult(
        result_id=f"metric:{metric.value}:{formula_id}:unavailable",
        metric=metric,
        family=family,
        status=status,
        formula_id=formula_id,
        formula_version=FORMULA_VERSION,
        requested_window=requested_window,
        reason=reason,
    )


def _derived_source_quality(
    facts: tuple[FundamentalFact, ...],
) -> FundamentalSourceQuality:
    qualities = {item.source_quality for item in facts}
    primary_classes = {
        FundamentalSourceQuality.PRIMARY_FILED,
        FundamentalSourceQuality.EXCHANGE_FILED,
        FundamentalSourceQuality.REGULATORY,
        FundamentalSourceQuality.COMPANY_REPORTED,
        FundamentalSourceQuality.DERIVED_FROM_PRIMARY,
    }
    if qualities <= primary_classes:
        return FundamentalSourceQuality.DERIVED_FROM_PRIMARY
    if FundamentalSourceQuality.UNKNOWN in qualities:
        return FundamentalSourceQuality.UNKNOWN
    return FundamentalSourceQuality.TRUSTED_AGGREGATOR
