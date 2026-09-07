"""MACD and Wilder ADX deterministic fixtures and warm-up semantics."""

import pytest

from tiaf.features import FeatureStatus
from tiaf.features._trend_calculation import exponential_moving_average_series
from tiaf.indicators import IndicatorParameterError
from tiaf.indicators.library.adx import directional_movement

from ..features._support import context_with_bars
from ._support import calculate


def test_macd_known_fixture_and_histogram_identity() -> None:
    result = calculate(
        "macd",
        (10.0, 11.0, 12.0, 13.0),
        {"fast_period": 2, "slow_period": 3, "signal_period": 2},
    )
    assert result.value("macd") == pytest.approx(0.5)
    assert result.value("signal") == pytest.approx(0.5)
    assert result.value("histogram") == pytest.approx(0.0)
    macd = result.value("macd")
    signal = result.value("signal")
    assert macd is not None and signal is not None
    assert result.value("histogram") == pytest.approx(macd - signal)


def test_macd_reconciles_with_canonical_ema_series() -> None:
    closes = (10.0, 11.0, 13.0, 17.0, 25.0, 21.0)
    result = calculate(
        "macd",
        closes,
        {"fast_period": 2, "slow_period": 3, "signal_period": 2},
    )
    fast = exponential_moving_average_series(closes, 2)
    slow = exponential_moving_average_series(closes, 3)
    series = tuple(fast[index - 1] - slow[index - 2] for index in range(2, 6))
    expected_signal = exponential_moving_average_series(series, 2)[-1]
    assert result.value("macd") == pytest.approx(series[-1])
    assert result.value("signal") == pytest.approx(expected_signal)


def test_macd_constant_series_is_zero() -> None:
    result = calculate(
        "macd",
        (10.0,) * 8,
        {"fast_period": 2, "slow_period": 4, "signal_period": 3},
    )
    assert tuple(value.value for value in result.values) == (0.0, 0.0, 0.0)


@pytest.mark.parametrize("count", [2, 3])
def test_macd_requires_slow_and_signal_warmup(count: int) -> None:
    result = calculate(
        "macd",
        tuple(float(value) for value in range(10, 10 + count)),
        {"fast_period": 2, "slow_period": 3, "signal_period": 2},
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


@pytest.mark.parametrize(
    "parameters",
    [
        {"fast_period": 3, "slow_period": 3, "signal_period": 2},
        {"fast_period": 4, "slow_period": 3, "signal_period": 2},
        {"fast_period": 0, "slow_period": 3, "signal_period": 2},
    ],
)
def test_macd_rejects_invalid_periods(parameters: dict[str, int]) -> None:
    with pytest.raises(IndicatorParameterError):
        calculate("macd", (10.0, 11.0, 12.0, 13.0), parameters)


def test_directional_movement_strict_wilder_semantics() -> None:
    context = context_with_bars(
        (10.0, 11.0), highs=(11.0, 13.0), lows=(9.0, 10.0)
    )
    assert context.history is not None
    plus_dm, minus_dm = directional_movement(
        context.history.bars[1], context.history.bars[0]
    )
    assert plus_dm == 2.0
    assert minus_dm == 0.0


def test_directional_movement_tie_contributes_zero_to_both_sides() -> None:
    context = context_with_bars(
        (10.0, 10.0), highs=(11.0, 12.0), lows=(9.0, 8.0)
    )
    assert context.history is not None
    assert directional_movement(
        context.history.bars[1], context.history.bars[0]
    ) == (0.0, 0.0)


def test_adx_known_increasing_and_decreasing_fixtures() -> None:
    increasing = calculate(
        "adx",
        (10.0, 11.0, 12.0, 13.0),
        {"period": 2},
        highs=(11.0, 12.0, 13.0, 14.0),
        lows=(9.0, 10.0, 11.0, 12.0),
    )
    decreasing = calculate(
        "adx",
        (13.0, 12.0, 11.0, 10.0),
        {"period": 2},
        highs=(14.0, 13.0, 12.0, 11.0),
        lows=(12.0, 11.0, 10.0, 9.0),
    )
    assert increasing.value("adx") == 100.0
    assert increasing.value("plus_di") == 50.0
    assert increasing.value("minus_di") == 0.0
    assert decreasing.value("adx") == 100.0
    assert decreasing.value("plus_di") == 0.0
    assert decreasing.value("minus_di") == 50.0


def test_adx_wilder_initialization_and_recursive_update_fixture() -> None:
    result = calculate(
        "adx",
        (10.0, 12.0, 11.0, 14.0, 13.0),
        {"period": 2},
        highs=(11.0, 13.0, 12.0, 15.0, 14.0),
        lows=(9.0, 11.0, 10.0, 13.0, 12.0),
    )
    assert result.value("adx") == pytest.approx(39.31623931623932)
    assert result.value("plus_di") == pytest.approx(38.095238095238095)
    assert result.value("minus_di") == pytest.approx(23.80952380952381)


def test_adx_constant_market_convention_is_zero() -> None:
    result = calculate(
        "adx",
        (10.0,) * 6,
        {"period": 3},
        highs=(10.0,) * 6,
        lows=(10.0,) * 6,
    )
    assert tuple(value.value for value in result.values) == (0.0, 0.0, 0.0)


def test_adx_exact_warmup_and_invalid_period() -> None:
    insufficient = calculate("adx", (10.0, 11.0, 12.0), {"period": 2})
    assert insufficient.status is FeatureStatus.INSUFFICIENT_DATA
    with pytest.raises(IndicatorParameterError):
        calculate("adx", (10.0, 11.0), {"period": -1})
