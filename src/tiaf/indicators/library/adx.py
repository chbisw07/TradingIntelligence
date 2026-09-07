"""Wilder ADX and directional movement over completed OHLC bars."""

import math

from tiaf.context import AnalysisContext
from tiaf.data import OHLCVBar
from tiaf.features.volatility import true_range
from tiaf.indicators._calculation import (
    IndicatorCalculatorBase,
    float_value,
    integer_parameter,
)
from tiaf.indicators.definitions import ADX
from tiaf.indicators.models import IndicatorRequest, IndicatorResult


def directional_movement(
    current: OHLCVBar, previous: OHLCVBar
) -> tuple[float, float]:
    """Return Wilder positive and negative directional movement."""
    up_move = current.high - previous.high
    down_move = previous.low - current.low
    plus_dm = up_move if up_move > down_move and up_move > 0 else 0.0
    minus_dm = down_move if down_move > up_move and down_move > 0 else 0.0
    return plus_dm, minus_dm


def _directional_values(
    smoothed_tr: float,
    smoothed_plus: float,
    smoothed_minus: float,
) -> tuple[float, float, float]:
    if smoothed_tr == 0:
        return 0.0, 0.0, 0.0
    plus_di = 100.0 * smoothed_plus / smoothed_tr
    minus_di = 100.0 * smoothed_minus / smoothed_tr
    total = plus_di + minus_di
    dx = 0.0 if total == 0 else 100.0 * abs(plus_di - minus_di) / total
    return plus_di, minus_di, dx


def wilder_adx(
    bars: tuple[OHLCVBar, ...], period: int
) -> tuple[float, float, float]:
    """Return latest ADX, +DI, and -DI using a two-period warm-up."""
    ranges: list[float] = []
    plus_movements: list[float] = []
    minus_movements: list[float] = []
    for index in range(1, len(bars)):
        ranges.append(true_range(bars[index], bars[index - 1].close))
        plus_dm, minus_dm = directional_movement(bars[index], bars[index - 1])
        plus_movements.append(plus_dm)
        minus_movements.append(minus_dm)

    smoothed_tr = math.fsum(ranges[:period])
    smoothed_plus = math.fsum(plus_movements[:period])
    smoothed_minus = math.fsum(minus_movements[:period])
    plus_di, minus_di, first_dx = _directional_values(
        smoothed_tr, smoothed_plus, smoothed_minus
    )
    dx_values = [first_dx]
    for index in range(period, len(ranges)):
        smoothed_tr = smoothed_tr - (smoothed_tr / period) + ranges[index]
        smoothed_plus = (
            smoothed_plus - (smoothed_plus / period) + plus_movements[index]
        )
        smoothed_minus = (
            smoothed_minus - (smoothed_minus / period) + minus_movements[index]
        )
        plus_di, minus_di, dx = _directional_values(
            smoothed_tr, smoothed_plus, smoothed_minus
        )
        dx_values.append(dx)

    adx = math.fsum(dx_values[:period]) / period
    for dx in dx_values[period:]:
        adx = ((adx * (period - 1)) + dx) / period
    return adx, plus_di, minus_di


class AdxCalculator(IndicatorCalculatorBase):
    """Calculate raw Wilder directional-strength measurements."""

    def __init__(self) -> None:
        super().__init__(ADX)

    def calculate(
        self, request: IndicatorRequest, context: AnalysisContext
    ) -> IndicatorResult:
        parameters = self._parameters(request)
        period = integer_parameter(parameters, "period")
        prepared, failure = self._prepare_history(
            request, context, parameters, minimum_bars=2 * period
        )
        if failure is not None:
            return failure
        assert prepared is not None
        adx, plus_di, minus_di = wilder_adx(prepared.history.bars, period)
        return self._history_result(
            request,
            context,
            parameters,
            prepared,
            values=(
                float_value("adx", adx, "index_0_100"),
                float_value("plus_di", plus_di, "index_0_100"),
                float_value("minus_di", minus_di, "index_0_100"),
            ),
            lookback_bars_used=len(prepared.history.bars),
        )
