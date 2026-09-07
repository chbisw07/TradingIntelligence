"""Standard completed-bar ATR-band SuperTrend calculation."""

from tiaf.context import AnalysisContext
from tiaf.features.volatility import wilder_atr_series
from tiaf.indicators._calculation import (
    IndicatorCalculatorBase,
    float_value,
    integer_parameter,
    number_parameter,
)
from tiaf.indicators.definitions import SUPERTREND
from tiaf.indicators.enums import SuperTrendBand, SuperTrendRelation
from tiaf.indicators.models import IndicatorRequest, IndicatorResult, IndicatorState


class SuperTrendCalculator(IndicatorCalculatorBase):
    """Calculate recursively constrained bands and their latest relation."""

    def __init__(self) -> None:
        super().__init__(SUPERTREND)

    def calculate(
        self, request: IndicatorRequest, context: AnalysisContext
    ) -> IndicatorResult:
        parameters = self._parameters(request)
        period = integer_parameter(parameters, "period")
        multiplier = number_parameter(parameters, "multiplier")
        prepared, failure = self._prepare_history(
            request, context, parameters, minimum_bars=period + 1
        )
        if failure is not None:
            return failure
        assert prepared is not None
        bars = prepared.history.bars
        atr_values = wilder_atr_series(bars, period)
        final_upper = final_lower = line = 0.0
        basic_upper = basic_lower = 0.0
        upper_active = True
        for offset, atr in enumerate(atr_values):
            index = period + offset
            current = bars[index]
            midpoint = (current.high + current.low) / 2.0
            basic_upper = midpoint + (multiplier * atr)
            basic_lower = midpoint - (multiplier * atr)
            if offset == 0:
                final_upper = basic_upper
                final_lower = basic_lower
                line = final_upper
                upper_active = True
                continue
            previous_close = bars[index - 1].close
            prior_upper = final_upper
            prior_lower = final_lower
            final_upper = (
                basic_upper
                if basic_upper < prior_upper or previous_close > prior_upper
                else prior_upper
            )
            final_lower = (
                basic_lower
                if basic_lower > prior_lower or previous_close < prior_lower
                else prior_lower
            )
            if upper_active:
                upper_active = current.close <= final_upper
            else:
                upper_active = current.close < final_lower
            line = final_upper if upper_active else final_lower

        latest_close = bars[-1].close
        if latest_close > line:
            relation = SuperTrendRelation.ABOVE_LINE
        elif latest_close < line:
            relation = SuperTrendRelation.BELOW_LINE
        else:
            relation = SuperTrendRelation.ON_LINE
        active_band = (
            SuperTrendBand.UPPER_BAND_ACTIVE
            if upper_active
            else SuperTrendBand.LOWER_BAND_ACTIVE
        )
        return self._history_result(
            request,
            context,
            parameters,
            prepared,
            values=(
                float_value("basic_upper_band", basic_upper, "price"),
                float_value("basic_lower_band", basic_lower, "price"),
                float_value("final_upper_band", final_upper, "price"),
                float_value("final_lower_band", final_lower, "price"),
                float_value("line", line, "price"),
            ),
            states=(
                IndicatorState(name="relation", value=relation.value),
                IndicatorState(name="active_band", value=active_band.value),
            ),
            lookback_bars_used=len(bars),
        )
