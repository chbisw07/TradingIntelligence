"""Exact-window Donchian Channel over completed bars."""

from tiaf.context import AnalysisContext
from tiaf.features.enums import FeatureStatus
from tiaf.indicators._calculation import (
    IndicatorCalculatorBase,
    float_value,
    integer_parameter,
)
from tiaf.indicators.definitions import DONCHIAN
from tiaf.indicators.models import IndicatorRequest, IndicatorResult


class DonchianCalculator(IndicatorCalculatorBase):
    """Calculate channel levels and latest completed-close position."""

    def __init__(self) -> None:
        super().__init__(DONCHIAN)

    def calculate(
        self, request: IndicatorRequest, context: AnalysisContext
    ) -> IndicatorResult:
        parameters = self._parameters(request)
        period = integer_parameter(parameters, "period")
        prepared, failure = self._prepare_history(
            request, context, parameters, minimum_bars=period
        )
        if failure is not None:
            return failure
        assert prepared is not None
        window = prepared.history.bars[-period:]
        upper = max(bar.high for bar in window)
        lower = min(bar.low for bar in window)
        width = upper - lower
        if width == 0:
            return self._history_result(
                request,
                context,
                parameters,
                prepared,
                status=FeatureStatus.INSUFFICIENT_DATA,
                lookback_bars_used=period,
                warnings=("Donchian position is undefined for a flat channel",),
            )
        middle = (upper + lower) / 2.0
        position = (window[-1].close - lower) / width * 100.0
        return self._history_result(
            request,
            context,
            parameters,
            prepared,
            values=(
                float_value("upper", upper, "price"),
                float_value("lower", lower, "price"),
                float_value("middle", middle, "price"),
                float_value("position_percent", position, "%"),
            ),
            lookback_bars_used=period,
        )
