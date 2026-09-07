"""A2.2 logarithmic return, drawdown, and run-up calculations."""

import math

import pytest

from tiaf.context import AnalysisContext
from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    builtin_feature_registry,
)

from ._support import context_with_bars


def _compute(context: AnalysisContext, feature_id: str, bars: int) -> FeatureResult:
    return DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(
            feature_id=feature_id,
            parameters=(("bars", bars),),
            interval="1d",
        ),
    )


def test_log_return_uses_exact_intervals_back() -> None:
    result = _compute(context_with_bars((100.0, 105.0, 110.0)), "return.log", 2)
    assert result.value == pytest.approx(math.log(110.0) - math.log(100.0))
    assert result.lookback_bars_used == 3


@pytest.mark.parametrize("closes", [(0.0, 1.0), (1.0, 0.0)])
def test_log_return_requires_positive_prices(closes: tuple[float, ...]) -> None:
    result = _compute(context_with_bars(closes), "return.log", 1)
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


def test_log_return_does_not_shorten_window() -> None:
    result = _compute(context_with_bars((100.0, 110.0)), "return.log", 2)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.warnings == ("requires 3 history bars; available 2",)


def test_monotonic_up_series_has_zero_max_drawdown() -> None:
    result = _compute(
        context_with_bars((100.0, 110.0, 120.0, 130.0)),
        "return.max_drawdown_percent",
        4,
    )
    assert result.value == 0.0


def test_monotonic_down_series_has_zero_max_runup() -> None:
    result = _compute(
        context_with_bars((130.0, 120.0, 110.0, 100.0)),
        "return.max_runup_percent",
        4,
    )
    assert result.value == 0.0


def test_max_drawdown_is_the_most_negative_peak_to_later_close() -> None:
    result = _compute(
        context_with_bars((100.0, 120.0, 90.0, 110.0, 80.0)),
        "return.max_drawdown_percent",
        5,
    )
    assert result.value == pytest.approx(((80.0 / 120.0) - 1) * 100)
    assert isinstance(result.value, (int, float)) and result.value < 0


def test_max_runup_is_largest_trough_to_later_close() -> None:
    result = _compute(
        context_with_bars((100.0, 80.0, 120.0, 90.0, 135.0)),
        "return.max_runup_percent",
        5,
    )
    assert result.value == pytest.approx(((135.0 / 80.0) - 1) * 100)
    assert isinstance(result.value, (int, float)) and result.value > 0


@pytest.mark.parametrize(
    "feature_id",
    ["return.max_drawdown_percent", "return.max_runup_percent"],
)
def test_one_bar_path_window_is_zero(feature_id: str) -> None:
    result = _compute(context_with_bars((100.0,)), feature_id, 1)
    assert result.value == 0.0


def test_path_measure_requires_the_exact_requested_window() -> None:
    result = _compute(
        context_with_bars((100.0, 90.0)), "return.max_drawdown_percent", 3
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None


def test_runup_from_zero_trough_fails_without_infinity() -> None:
    result = _compute(
        context_with_bars((0.0, 10.0)), "return.max_runup_percent", 2
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None
    assert "zero trough" in result.warnings[-1]
