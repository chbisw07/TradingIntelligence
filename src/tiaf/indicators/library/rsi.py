"""Wilder Relative Strength Index over completed closes."""

import math

from tiaf.context import AnalysisContext
from tiaf.indicators._calculation import (
    IndicatorCalculatorBase,
    float_value,
    integer_parameter,
)
from tiaf.indicators.definitions import RSI
from tiaf.indicators.models import IndicatorRequest, IndicatorResult


def wilder_rsi(closes: tuple[float, ...], period: int) -> float:
    """Return Wilder RSI with deterministic gain/loss zero conventions."""
    changes = tuple(
        closes[index] - closes[index - 1] for index in range(1, len(closes))
    )
    gains = tuple(max(change, 0.0) for change in changes)
    losses = tuple(max(-change, 0.0) for change in changes)
    average_gain = math.fsum(gains[:period]) / period
    average_loss = math.fsum(losses[:period]) / period
    for gain, loss in zip(gains[period:], losses[period:], strict=True):
        average_gain = ((average_gain * (period - 1)) + gain) / period
        average_loss = ((average_loss * (period - 1)) + loss) / period
    if average_gain == 0 and average_loss == 0:
        return 50.0
    if average_loss == 0:
        return 100.0
    if average_gain == 0:
        return 0.0
    relative_strength = average_gain / average_loss
    return 100.0 - (100.0 / (1.0 + relative_strength))


class RsiCalculator(IndicatorCalculatorBase):
    """Calculate latest Wilder RSI without interpretive thresholds."""

    def __init__(self) -> None:
        super().__init__(RSI)

    def calculate(
        self, request: IndicatorRequest, context: AnalysisContext
    ) -> IndicatorResult:
        parameters = self._parameters(request)
        period = integer_parameter(parameters, "period")
        prepared, failure = self._prepare_history(
            request, context, parameters, minimum_bars=period + 1
        )
        if failure is not None:
            return failure
        assert prepared is not None
        closes = tuple(bar.close for bar in prepared.history.bars)
        return self._history_result(
            request,
            context,
            parameters,
            prepared,
            values=(float_value("rsi", wilder_rsi(closes, period), "index_0_100"),),
            lookback_bars_used=len(closes),
        )
