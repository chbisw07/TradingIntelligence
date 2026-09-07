"""Canonical SMA-seeded EMA MACD over completed closes."""

from tiaf.context import AnalysisContext
from tiaf.features._trend_calculation import exponential_moving_average_series
from tiaf.indicators._calculation import (
    IndicatorCalculatorBase,
    float_value,
    integer_parameter,
)
from tiaf.indicators.definitions import MACD
from tiaf.indicators.errors import IndicatorParameterError
from tiaf.indicators.models import IndicatorRequest, IndicatorResult


def macd_values(
    closes: tuple[float, ...],
    fast_period: int,
    slow_period: int,
    signal_period: int,
) -> tuple[float, float, float]:
    """Return latest MACD, signal EMA, and their difference."""
    fast = exponential_moving_average_series(closes, fast_period)
    slow = exponential_moving_average_series(closes, slow_period)
    macd_series = tuple(
        fast[index - (fast_period - 1)] - slow[index - (slow_period - 1)]
        for index in range(slow_period - 1, len(closes))
    )
    signal = exponential_moving_average_series(macd_series, signal_period)[-1]
    macd = macd_series[-1]
    return macd, signal, macd - signal


class MacdCalculator(IndicatorCalculatorBase):
    """Calculate raw MACD outputs without crossover interpretation."""

    def __init__(self) -> None:
        super().__init__(MACD)

    def calculate(
        self, request: IndicatorRequest, context: AnalysisContext
    ) -> IndicatorResult:
        parameters = self._parameters(request)
        fast_period = integer_parameter(parameters, "fast_period")
        slow_period = integer_parameter(parameters, "slow_period")
        signal_period = integer_parameter(parameters, "signal_period")
        if fast_period >= slow_period:
            raise IndicatorParameterError(
                "fast_period must be less than slow_period"
            )
        minimum = slow_period + signal_period - 1
        prepared, failure = self._prepare_history(
            request, context, parameters, minimum_bars=minimum
        )
        if failure is not None:
            return failure
        assert prepared is not None
        closes = tuple(bar.close for bar in prepared.history.bars)
        macd, signal, histogram = macd_values(
            closes, fast_period, slow_period, signal_period
        )
        return self._history_result(
            request,
            context,
            parameters,
            prepared,
            values=(
                float_value("macd", macd, "price"),
                float_value("signal", signal, "price"),
                float_value("histogram", histogram, "price"),
            ),
            lookback_bars_used=len(closes),
        )
