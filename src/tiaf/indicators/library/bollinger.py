"""Population-standard-deviation Bollinger Bands over completed closes."""

import statistics

from tiaf.context import AnalysisContext
from tiaf.features._trend_calculation import simple_moving_average
from tiaf.features.enums import FeatureStatus
from tiaf.indicators._calculation import (
    IndicatorCalculatorBase,
    float_value,
    integer_parameter,
    number_parameter,
)
from tiaf.indicators.definitions import BOLLINGER
from tiaf.indicators.errors import IndicatorParameterError
from tiaf.indicators.models import IndicatorRequest, IndicatorResult


class BollingerCalculator(IndicatorCalculatorBase):
    """Calculate exact-window Bollinger levels and normalized positions."""

    def __init__(self) -> None:
        super().__init__(BOLLINGER)

    def calculate(
        self, request: IndicatorRequest, context: AnalysisContext
    ) -> IndicatorResult:
        parameters = self._parameters(request)
        period = integer_parameter(parameters, "period")
        multiplier = number_parameter(parameters, "stddev_multiplier")
        if period <= 1:
            raise IndicatorParameterError("Bollinger period must be greater than 1")
        prepared, failure = self._prepare_history(
            request, context, parameters, minimum_bars=period
        )
        if failure is not None:
            return failure
        assert prepared is not None
        closes = tuple(bar.close for bar in prepared.history.bars)
        window = closes[-period:]
        middle = simple_moving_average(closes, period)
        if middle == 0:
            return self._history_result(
                request,
                context,
                parameters,
                prepared,
                status=FeatureStatus.FAILED,
                lookback_bars_used=period,
                warnings=("Bollinger bandwidth is undefined for zero middle",),
            )
        deviation = statistics.pstdev(window)
        upper = middle + (multiplier * deviation)
        lower = middle - (multiplier * deviation)
        width = upper - lower
        percent_b = 0.5 if width == 0 else (closes[-1] - lower) / width
        return self._history_result(
            request,
            context,
            parameters,
            prepared,
            values=(
                float_value("middle", middle, "price"),
                float_value("upper", upper, "price"),
                float_value("lower", lower, "price"),
                float_value("bandwidth_percent", width / middle * 100.0, "%"),
                float_value("percent_b", percent_b, "ratio"),
            ),
            lookback_bars_used=period,
        )
