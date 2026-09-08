"""Deterministic metric period/window and arithmetic safety tests."""

from datetime import date

import pytest

from tiaf.fundamentals import (
    FundamentalFamily,
    FundamentalMetric,
    MetricResultStatus,
    ReportingPeriod,
    ReportingPeriodKind,
    compound_annual_growth_rate,
    growth_rate,
    metric_result_to_fact,
    ratio_metric,
    trailing_twelve_months,
)

from ._support import fact


def annual(fiscal_year: str, start_year: int) -> ReportingPeriod:
    return ReportingPeriod(
        period_id=fiscal_year,
        kind=ReportingPeriodKind.FISCAL_YEAR,
        start_date=date(start_year, 4, 1),
        end_date=date(start_year + 1, 3, 31),
        fiscal_year=fiscal_year,
    )


def quarter(
    period_id: str,
    fiscal_year: str,
    fiscal_quarter: int,
    start: date,
    end: date,
) -> ReportingPeriod:
    return ReportingPeriod(
        period_id=period_id,
        kind=ReportingPeriodKind.FISCAL_QUARTER,
        start_date=start,
        end_date=end,
        fiscal_year=fiscal_year,
        fiscal_quarter=fiscal_quarter,
    )


def test_annual_and_same_quarter_yoy_are_exact() -> None:
    prior_year = fact(FundamentalMetric.REVENUE, 100.0, period=annual("FY2025", 2024))
    current_year = fact(FundamentalMetric.REVENUE, 120.0, period=annual("FY2026", 2025))
    annual_result = growth_rate(
        current_year,
        prior_year,
        FundamentalMetric.REVENUE_GROWTH_YOY,
        mode="YOY",
    )
    prior_q = fact(
        FundamentalMetric.REVENUE,
        25.0,
        period=quarter(
            "FY2025-Q1", "FY2025", 1, date(2024, 4, 1), date(2024, 6, 30)
        ),
    )
    current_q = fact(
        FundamentalMetric.REVENUE,
        30.0,
        period=quarter(
            "FY2026-Q1", "FY2026", 1, date(2025, 4, 1), date(2025, 6, 30)
        ),
    )
    quarter_result = growth_rate(
        current_q,
        prior_q,
        FundamentalMetric.REVENUE_GROWTH_YOY,
        mode="YOY",
    )

    assert annual_result.status is MetricResultStatus.AVAILABLE
    assert annual_result.value == pytest.approx(20.0)
    assert quarter_result.status is MetricResultStatus.AVAILABLE
    assert quarter_result.value == pytest.approx(20.0)


def test_quarter_over_quarter_crosses_fiscal_year_without_calendar_assumption() -> None:
    q4 = fact(
        FundamentalMetric.REVENUE,
        40.0,
        period=quarter(
            "FY2025-Q4", "FY2025", 4, date(2025, 1, 1), date(2025, 3, 31)
        ),
    )
    q1 = fact(
        FundamentalMetric.REVENUE,
        44.0,
        period=quarter(
            "FY2026-Q1", "FY2026", 1, date(2025, 4, 1), date(2025, 6, 30)
        ),
    )
    result = growth_rate(
        q1,
        q4,
        FundamentalMetric.REVENUE_GROWTH_QOQ,
        mode="QOQ",
    )
    assert result.status is MetricResultStatus.AVAILABLE
    assert result.value == pytest.approx(10.0)


def test_period_mixing_and_zero_comparison_are_not_meaningful_outputs() -> None:
    annual_fact = fact(FundamentalMetric.REVENUE, 100.0, period=annual("FY2026", 2025))
    quarter_fact = fact(
        FundamentalMetric.REVENUE,
        20.0,
        period=quarter(
            "FY2026-Q4", "FY2026", 4, date(2026, 1, 1), date(2026, 3, 31)
        ),
    )
    mixed = growth_rate(
        annual_fact,
        quarter_fact,
        FundamentalMetric.REVENUE_GROWTH_YOY,
        mode="YOY",
    )
    zero = growth_rate(
        annual_fact,
        fact(FundamentalMetric.REVENUE, 0.0, period=annual("FY2025", 2024)),
        FundamentalMetric.REVENUE_GROWTH_YOY,
        mode="YOY",
    )

    assert mixed.status is MetricResultStatus.INSUFFICIENT_DATA
    assert mixed.value is None
    assert zero.status is MetricResultStatus.NOT_MEANINGFUL
    assert zero.value is None


def test_ttm_requires_exactly_four_contiguous_quarters() -> None:
    periods = (
        quarter("FY2026-Q1", "FY2026", 1, date(2025, 4, 1), date(2025, 6, 30)),
        quarter("FY2026-Q2", "FY2026", 2, date(2025, 7, 1), date(2025, 9, 30)),
        quarter("FY2026-Q3", "FY2026", 3, date(2025, 10, 1), date(2025, 12, 31)),
        quarter("FY2026-Q4", "FY2026", 4, date(2026, 1, 1), date(2026, 3, 31)),
    )
    quarters = tuple(
        fact(FundamentalMetric.REVENUE, value, period=period)
        for value, period in zip((10.0, 20.0, 30.0, 40.0), periods, strict=True)
    )
    result = trailing_twelve_months(
        quarters, output_metric=FundamentalMetric.REVENUE
    )
    insufficient = trailing_twelve_months(
        quarters[:3], output_metric=FundamentalMetric.REVENUE
    )
    gap_period = quarter(
        "FY2026-Q4-gap", "FY2026", 4, date(2026, 1, 2), date(2026, 3, 31)
    )
    missing_quarter = trailing_twelve_months(
        (*quarters[:3], fact(FundamentalMetric.REVENUE, 40.0, period=gap_period)),
        output_metric=FundamentalMetric.REVENUE,
    )

    assert result.status is MetricResultStatus.AVAILABLE
    assert result.value == 1_000_000_000.0
    assert result.period is not None
    assert result.period.kind is ReportingPeriodKind.TTM
    assert result.period.constituent_period_ids == tuple(item.period.period_id for item in quarters)
    assert insufficient.status is MetricResultStatus.INSUFFICIENT_DATA
    assert missing_quarter.status is MetricResultStatus.INSUFFICIENT_DATA


def test_cagr_requires_exact_window_and_rejects_missing_year() -> None:
    sequence = tuple(
        fact(
            FundamentalMetric.REVENUE,
            value,
            period=annual(f"FY{year + 1}", year),
        )
        for year, value in ((2022, 100.0), (2023, 110.0), (2024, 121.0), (2025, 133.1))
    )
    valid = compound_annual_growth_rate(
        sequence,
        years=3,
        output_metric=FundamentalMetric.REVENUE_CAGR_3Y,
    )
    insufficient = compound_annual_growth_rate(
        sequence[-3:],
        years=3,
        output_metric=FundamentalMetric.REVENUE_CAGR_3Y,
    )
    missing_year = compound_annual_growth_rate(
        (sequence[0], sequence[1], sequence[3]),
        years=2,
        output_metric=FundamentalMetric.REVENUE_CAGR_3Y,
    )

    assert valid.status is MetricResultStatus.AVAILABLE
    assert valid.value == pytest.approx(10.0)
    assert insufficient.status is MetricResultStatus.INSUFFICIENT_DATA
    assert insufficient.requested_window == "3Y"
    assert missing_year.status is MetricResultStatus.INSUFFICIENT_DATA


def test_ratio_rejects_currency_period_and_zero_denominator_mismatch() -> None:
    period = annual("FY2026", 2025)
    numerator = fact(FundamentalMetric.NET_INCOME, 20.0, period=period)
    denominator = fact(FundamentalMetric.REVENUE, 100.0, period=period)
    valid = ratio_metric(
        numerator,
        denominator,
        output_metric=FundamentalMetric.NET_MARGIN,
        family=FundamentalFamily.MARGINS,
        as_percent=True,
    )
    currency_mismatch = ratio_metric(
        numerator,
        denominator.model_copy(update={"currency": "USD"}),
        output_metric=FundamentalMetric.NET_MARGIN,
        family=FundamentalFamily.MARGINS,
        as_percent=True,
    )
    zero = ratio_metric(
        numerator,
        denominator.model_copy(update={"value": 0.0}),
        output_metric=FundamentalMetric.NET_MARGIN,
        family=FundamentalFamily.MARGINS,
        as_percent=True,
    )

    assert valid.value == pytest.approx(20.0)
    assert currency_mismatch.status is MetricResultStatus.INSUFFICIENT_DATA
    assert zero.status is MetricResultStatus.NOT_MEANINGFUL


def test_available_metric_becomes_auditable_derived_fact() -> None:
    prior = fact(FundamentalMetric.REVENUE, 100.0, period=annual("FY2025", 2024))
    current = fact(FundamentalMetric.REVENUE, 120.0, period=annual("FY2026", 2025))
    result = growth_rate(
        current,
        prior,
        FundamentalMetric.REVENUE_GROWTH_YOY,
        mode="YOY",
    )
    derived = metric_result_to_fact(
        result,
        fact_id="derived:revenue-growth-yoy",
        source_facts=(prior, current),
    )

    assert derived.basis.value == "DERIVED"
    assert derived.derivation is not None
    assert derived.derivation.source_fact_ids == (prior.fact_id, current.fact_id)
    assert derived.value == pytest.approx(20.0)
