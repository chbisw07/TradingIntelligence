"""A2.3 moving-average, spread, regression, and ATR-extension behavior."""

from typing import Any

import pytest

from tiaf.contracts import DataQuality
from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureParameterError,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    builtin_feature_registry,
)

from ._support import context_with_bars


def _compute(
    feature_id: str,
    closes: tuple[float, ...],
    parameters: tuple[tuple[str, int], ...],
    **context_options: Any,
) -> FeatureResult:
    return DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context_with_bars(closes, **context_options),
        FeatureRequest(
            feature_id=feature_id,
            parameters=parameters,
            interval="1d",
        ),
    )


def test_sma_uses_latest_exact_period() -> None:
    result = _compute("trend.sma", (1.0, 2.0, 3.0, 4.0), (("period", 3),))
    assert result.value == 3.0
    assert result.lookback_bars_used == 3


def test_sma_reports_insufficient_exact_history() -> None:
    result = _compute("trend.sma", (1.0, 2.0), (("period", 3),))
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None


def test_ema_initializes_from_first_period_sma() -> None:
    result = _compute("trend.ema", (1.0, 2.0, 3.0), (("period", 3),))
    assert result.value == 2.0
    assert result.lookback_bars_used == 3


def test_ema_recurses_over_every_subsequent_close() -> None:
    result = _compute("trend.ema", (1.0, 2.0, 3.0, 4.0, 8.0), (("period", 3),))
    assert result.value == 5.5
    assert result.lookback_bars_used == 5


def test_ema_reports_insufficient_warmup() -> None:
    result = _compute("trend.ema", (1.0, 2.0), (("period", 3),))
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


@pytest.mark.parametrize("feature_id", ["trend.sma", "trend.ema"])
def test_moving_average_period_one_is_latest_close(feature_id: str) -> None:
    result = _compute(feature_id, (1.0, 2.0, 7.0), (("period", 1),))
    assert result.value == 7.0


@pytest.mark.parametrize("period", [0, -1])
@pytest.mark.parametrize("feature_id", ["trend.sma", "trend.ema"])
def test_moving_average_rejects_nonpositive_period(
    feature_id: str, period: int
) -> None:
    with pytest.raises(FeatureParameterError, match="positive integer"):
        _compute(feature_id, (1.0, 2.0), (("period", period),))


def test_distance_from_sma_uses_latest_completed_close() -> None:
    result = _compute(
        "trend.distance_from_sma_percent",
        (10.0, 20.0, 30.0),
        (("period", 2),),
        quote_ltp=999.0,
    )
    assert result.value == pytest.approx(20.0)
    assert result.source_evidence == ("history",)


def test_distance_from_ema_uses_canonical_ema() -> None:
    result = _compute(
        "trend.distance_from_ema_percent",
        (10.0, 20.0, 40.0),
        (("period", 2),),
    )
    expected_ema = (2.0 / 3.0 * 40.0) + (1.0 / 3.0 * 15.0)
    assert result.value == pytest.approx(((40.0 / expected_ema) - 1.0) * 100.0)


def test_sma_fast_slow_spread() -> None:
    result = _compute(
        "trend.sma_spread_percent",
        (10.0, 20.0, 30.0, 40.0),
        (("fast_period", 2), ("slow_period", 4)),
    )
    assert result.value == pytest.approx(40.0)
    assert result.lookback_bars_used == 4


def test_ema_fast_slow_spread() -> None:
    closes = (10.0, 20.0, 30.0, 50.0)
    result = _compute(
        "trend.ema_spread_percent",
        closes,
        (("fast_period", 2), ("slow_period", 3)),
    )
    fast = (2.0 / 3.0 * 30.0) + (1.0 / 3.0 * 15.0)
    fast = (2.0 / 3.0 * 50.0) + (1.0 / 3.0 * fast)
    slow = (0.5 * 50.0) + (0.5 * 20.0)
    assert result.value == pytest.approx(((fast / slow) - 1.0) * 100.0)
    assert result.lookback_bars_used == 4


@pytest.mark.parametrize(
    ("fast", "slow"),
    [(2, 2), (3, 2)],
)
@pytest.mark.parametrize(
    "feature_id", ["trend.sma_spread_percent", "trend.ema_spread_percent"]
)
def test_spread_rejects_fast_not_less_than_slow(
    feature_id: str, fast: int, slow: int
) -> None:
    with pytest.raises(FeatureParameterError, match="less than"):
        _compute(
            feature_id,
            (1.0, 2.0, 3.0),
            (("fast_period", fast), ("slow_period", slow)),
        )


@pytest.mark.parametrize(
    "feature_id",
    [
        "trend.distance_from_sma_percent",
        "trend.distance_from_ema_percent",
        "trend.sma_spread_percent",
        "trend.ema_spread_percent",
    ],
)
def test_average_ratio_features_fail_on_zero_denominator(feature_id: str) -> None:
    parameters = (
        (("fast_period", 1), ("slow_period", 2))
        if "spread" in feature_id
        else (("period", 2),)
    )
    result = _compute(feature_id, (0.0, 0.0), parameters)
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


@pytest.mark.parametrize(
    ("closes", "expected"),
    [
        ((1.0, 3.0, 5.0, 7.0), 2.0),
        ((7.0, 5.0, 3.0, 1.0), -2.0),
        ((4.0, 4.0, 4.0, 4.0), 0.0),
    ],
)
def test_linear_slope_known_paths(
    closes: tuple[float, ...], expected: float
) -> None:
    result = _compute("trend.linear_slope", closes, (("bars", 4),))
    assert result.value == pytest.approx(expected)


def test_linear_slope_percent_uses_mean_close_denominator() -> None:
    result = _compute(
        "trend.linear_slope_percent", (10.0, 20.0, 30.0), (("bars", 3),)
    )
    assert result.value == pytest.approx(50.0)


def test_linear_r2_is_one_for_perfect_line_and_constant_series() -> None:
    perfect = _compute("trend.linear_r2", (1.0, 3.0, 5.0), (("bars", 3),))
    constant = _compute("trend.linear_r2", (4.0, 4.0, 4.0), (("bars", 3),))
    assert perfect.value == 1.0
    assert constant.value == 1.0


def test_linear_r2_noisy_path() -> None:
    result = _compute("trend.linear_r2", (1.0, 2.0, 4.0), (("bars", 3),))
    assert result.value == pytest.approx(27.0 / 28.0)


@pytest.mark.parametrize(
    "feature_id",
    ["trend.linear_slope", "trend.linear_slope_percent", "trend.linear_r2"],
)
def test_regression_requires_exact_window(feature_id: str) -> None:
    result = _compute(feature_id, (1.0, 2.0), (("bars", 3),))
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


def test_normalized_slope_fails_on_zero_mean() -> None:
    result = _compute(
        "trend.linear_slope_percent", (0.0, 0.0), (("bars", 2),)
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


def test_regression_rejects_one_bar_window() -> None:
    with pytest.raises(FeatureParameterError, match="at least 2"):
        _compute("trend.linear_slope", (1.0, 2.0), (("bars", 1),))


def test_sma_and_ema_distance_in_wilder_atr_units() -> None:
    options = {
        "highs": (11.0, 13.0, 15.0, 21.0),
        "lows": (9.0, 11.0, 13.0, 19.0),
    }
    parameters = (("atr_period", 2), ("ma_period", 2))
    sma = _compute(
        "trend.distance_from_sma_atr",
        (10.0, 12.0, 14.0, 20.0),
        parameters,
        **options,
    )
    ema = _compute(
        "trend.distance_from_ema_atr",
        (10.0, 12.0, 14.0, 20.0),
        parameters,
        **options,
    )
    assert sma.value == pytest.approx(0.6)
    assert ema.value == pytest.approx(7.0 / 15.0)


@pytest.mark.parametrize(
    "feature_id", ["trend.distance_from_sma_atr", "trend.distance_from_ema_atr"]
)
def test_atr_extension_fails_on_zero_atr(feature_id: str) -> None:
    result = _compute(
        feature_id,
        (10.0, 10.0, 10.0),
        (("atr_period", 2), ("ma_period", 2)),
        highs=(10.0, 10.0, 10.0),
        lows=(10.0, 10.0, 10.0),
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


def test_atr_extension_requires_strict_atr_warmup() -> None:
    result = _compute(
        "trend.distance_from_sma_atr",
        (10.0, 11.0),
        (("atr_period", 2), ("ma_period", 2)),
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


def test_atr_extension_inherits_history_quality_without_upgrade() -> None:
    result = _compute(
        "trend.distance_from_sma_atr",
        (10.0, 11.0, 12.0),
        (("atr_period", 2), ("ma_period", 2)),
        history_quality=DataQuality.DEGRADED,
    )
    assert result.status is FeatureStatus.PARTIAL
    assert result.quality is DataQuality.DEGRADED
    assert result.source_evidence == ("history",)
