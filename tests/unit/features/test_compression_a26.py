"""A2.6 prior-range width, compression, and latest-range comparison tests."""

import pytest

from tiaf.context import AnalysisContext
from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureParameterError,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    builtin_feature_registry,
)
from tiaf.features.volatility import wilder_atr

from ._support import context_with_bars


def _context_from_ranges(
    ranges: tuple[tuple[float, float], ...],
) -> AnalysisContext:
    lows = tuple(item[0] for item in ranges)
    highs = tuple(item[1] for item in ranges)
    closes = tuple((low + high) / 2 for low, high in ranges)
    return context_with_bars(closes, highs=highs, lows=lows)


def _compute(
    feature_id: str,
    ranges: tuple[tuple[float, float], ...],
    parameters: tuple[tuple[str, int], ...],
) -> FeatureResult:
    return DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        _context_from_ranges(ranges),
        FeatureRequest(feature_id=feature_id, parameters=parameters, interval="1d"),
    )


def test_prior_range_percent_uses_midpoint_formula() -> None:
    result = _compute(
        "structure.prior_range_percent",
        ((5.0, 15.0), (6.0, 12.0), (9.0, 11.0)),
        (("bars", 2),),
    )
    assert result.value == pytest.approx(100.0)


def test_prior_range_width_excludes_latest_bar() -> None:
    ordinary = _compute(
        "structure.prior_range_percent",
        ((5.0, 15.0), (6.0, 12.0), (9.0, 11.0)),
        (("bars", 2),),
    )
    extreme = _compute(
        "structure.prior_range_percent",
        ((5.0, 15.0), (6.0, 12.0), (0.0, 100.0)),
        (("bars", 2),),
    )
    assert ordinary.value == extreme.value == pytest.approx(100.0)


def test_prior_range_atr_reconciles_with_shared_wilder_helper() -> None:
    context = _context_from_ranges(
        ((5.0, 15.0), (6.0, 12.0), (7.0, 13.0), (8.0, 14.0))
    )
    assert context.history is not None
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(
            feature_id="structure.prior_range_atr",
            parameters=(("atr_period", 2), ("bars", 3)),
            interval="1d",
        ),
    )
    assert result.value == pytest.approx(10.0 / wilder_atr(context.history.bars, 2))


def test_prior_range_atr_zero_atr_fails() -> None:
    result = _compute(
        "structure.prior_range_atr",
        ((10.0, 10.0), (10.0, 10.0), (10.0, 10.0)),
        (("atr_period", 2), ("bars", 2)),
    )
    assert result.status is FeatureStatus.FAILED


def test_prior_range_percent_rejects_zero_midpoint() -> None:
    result = _compute(
        "structure.prior_range_percent",
        ((0.0, 0.0), (0.0, 0.0)),
        (("bars", 1),),
    )
    assert result.status is FeatureStatus.FAILED


def test_prior_range_requires_n_plus_one_bars() -> None:
    result = _compute(
        "structure.prior_range_percent",
        ((5.0, 15.0), (6.0, 12.0)),
        (("bars", 2),),
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


@pytest.mark.parametrize(
    ("ranges", "expected"),
    (
        (((0.0, 20.0), (2.0, 18.0), (8.0, 12.0), (8.0, 12.0), (9.0, 11.0)), 0.2),
        (((5.0, 15.0), (5.0, 15.0), (5.0, 15.0), (5.0, 15.0), (9.0, 11.0)), 1.0),
    ),
)
def test_nested_prior_range_ratio(
    ranges: tuple[tuple[float, float], ...], expected: float
) -> None:
    result = _compute(
        "structure.range_compression_ratio",
        ranges,
        (("long_bars", 4), ("short_bars", 2)),
    )
    assert result.value == pytest.approx(expected)


def test_nested_short_range_cannot_exceed_its_long_range() -> None:
    result = _compute(
        "structure.range_compression_ratio",
        ((1.0, 30.0), (2.0, 25.0), (5.0, 20.0), (7.0, 18.0), (9.0, 11.0)),
        (("long_bars", 4), ("short_bars", 2)),
    )
    assert isinstance(result.value, float)
    assert 0.0 <= result.value <= 1.0


@pytest.mark.parametrize(
    "parameters",
    (
        (("long_bars", 2), ("short_bars", 2)),
        (("long_bars", 2), ("short_bars", 3)),
        (("long_bars", 3), ("short_bars", 1)),
    ),
)
def test_compression_rejects_invalid_window_relationships(
    parameters: tuple[tuple[str, int], ...]
) -> None:
    with pytest.raises(FeatureParameterError):
        _compute(
            "structure.range_compression_ratio",
            ((5.0, 15.0),) * 5,
            parameters,
        )


def test_compression_zero_long_range_fails() -> None:
    result = _compute(
        "structure.range_compression_ratio",
        ((10.0, 10.0),) * 5,
        (("long_bars", 4), ("short_bars", 2)),
    )
    assert result.status is FeatureStatus.FAILED


def test_compression_excludes_latest_extreme() -> None:
    base_prior = ((0.0, 20.0), (2.0, 18.0), (8.0, 12.0), (8.0, 12.0))
    first = _compute(
        "structure.range_compression_ratio",
        (*base_prior, (9.0, 11.0)),
        (("long_bars", 4), ("short_bars", 2)),
    )
    second = _compute(
        "structure.range_compression_ratio",
        (*base_prior, (0.0, 100.0)),
        (("long_bars", 4), ("short_bars", 2)),
    )
    assert first.value == second.value


@pytest.mark.parametrize(
    ("latest_range", "expected"), ((4.0, 2.0), (2.0, 1.0), (1.0, 0.5))
)
def test_latest_bar_range_versus_prior_average(
    latest_range: float, expected: float
) -> None:
    half = latest_range / 2
    result = _compute(
        "structure.latest_bar_range_vs_average",
        ((9.0, 11.0), (9.0, 11.0), (10.0 - half, 10.0 + half)),
        (("bars", 2),),
    )
    assert result.value == pytest.approx(expected)


def test_latest_range_is_excluded_from_baseline() -> None:
    result = _compute(
        "structure.latest_bar_range_vs_average",
        ((9.0, 11.0), (9.0, 11.0), (0.0, 100.0)),
        (("bars", 2),),
    )
    assert result.value == pytest.approx(50.0)


def test_latest_range_zero_baseline_fails() -> None:
    result = _compute(
        "structure.latest_bar_range_vs_average",
        ((10.0, 10.0), (10.0, 10.0), (9.0, 11.0)),
        (("bars", 2),),
    )
    assert result.status is FeatureStatus.FAILED


def test_latest_range_requires_n_plus_one_bars() -> None:
    result = _compute(
        "structure.latest_bar_range_vs_average",
        ((9.0, 11.0), (9.0, 11.0)),
        (("bars", 2),),
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
