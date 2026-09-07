"""Deterministic completed-history moving-average and close-path features."""

from enum import StrEnum

from tiaf.context import AnalysisContext
from tiaf.contracts.common import Metadata
from tiaf.features._calculation import A22Calculator, positive_int_parameter
from tiaf.features._trend_calculation import (
    close_direction_counts,
    consecutive_close_run,
    directional_efficiency,
    exponential_moving_average,
    linear_regression,
    simple_moving_average,
)
from tiaf.features.enums import (
    FeatureCategory,
    FeatureSourceKind,
    FeatureStatus,
    FeatureValueType,
)
from tiaf.features.errors import FeatureParameterError
from tiaf.features.models import FeatureDefinition, FeatureRequest, FeatureResult
from tiaf.features.registry import FeatureCalculator
from tiaf.features.volatility import wilder_atr


def _trend_definition(
    feature_id: str,
    name: str,
    description: str,
    *,
    unit: str,
    minimum_bars: int,
    value_type: FeatureValueType = FeatureValueType.FLOAT,
    metadata: Metadata | None = None,
) -> FeatureDefinition:
    return FeatureDefinition(
        feature_id=feature_id,
        name=name,
        category=FeatureCategory.TREND,
        description=description,
        value_type=value_type,
        unit=unit,
        required_sources=(FeatureSourceKind.HISTORY,),
        minimum_history_bars=minimum_bars,
        metadata=metadata or {},
    )


SMA = _trend_definition(
    "trend.sma",
    "Simple moving average",
    "Arithmetic mean of the latest exact period completed closes.",
    unit="price",
    minimum_bars=1,
    metadata={"initialization": "latest_period_arithmetic_mean"},
)
EMA = _trend_definition(
    "trend.ema",
    "Exponential moving average",
    "EMA seeded by the first period-close SMA and updated through supplied history.",
    unit="price",
    minimum_bars=1,
    metadata={"initialization": "first_period_sma", "alpha": "2/(period+1)"},
)
DISTANCE_FROM_SMA_PERCENT = _trend_definition(
    "trend.distance_from_sma_percent",
    "Distance from simple moving average",
    "Latest completed close distance from SMA as a percentage of SMA.",
    unit="%",
    minimum_bars=1,
)
DISTANCE_FROM_EMA_PERCENT = _trend_definition(
    "trend.distance_from_ema_percent",
    "Distance from exponential moving average",
    "Latest completed close distance from EMA as a percentage of EMA.",
    unit="%",
    minimum_bars=1,
)
SMA_SPREAD_PERCENT = _trend_definition(
    "trend.sma_spread_percent",
    "Simple moving-average spread",
    "Fast SMA distance from slow SMA as a percentage of slow SMA.",
    unit="%",
    minimum_bars=2,
)
EMA_SPREAD_PERCENT = _trend_definition(
    "trend.ema_spread_percent",
    "Exponential moving-average spread",
    "Fast EMA distance from slow EMA as a percentage of slow EMA.",
    unit="%",
    minimum_bars=2,
)
LINEAR_SLOPE = _trend_definition(
    "trend.linear_slope",
    "Linear close slope",
    "Ordinary least-squares slope of the latest exact close window.",
    unit="price/bar",
    minimum_bars=2,
)
LINEAR_SLOPE_PERCENT = _trend_definition(
    "trend.linear_slope_percent",
    "Mean-normalized linear close slope",
    "OLS close slope divided by mean close and expressed per bar as a percentage.",
    unit="%/bar",
    minimum_bars=2,
)
LINEAR_R2 = _trend_definition(
    "trend.linear_r2",
    "Linear close coefficient of determination",
    "Coefficient of determination for the latest exact close window.",
    unit="ratio",
    minimum_bars=2,
    metadata={"constant_series_r_squared": 1.0},
)
DIRECTIONAL_EFFICIENCY = _trend_definition(
    "trend.directional_efficiency",
    "Directional efficiency",
    "Absolute net close displacement divided by close-path length.",
    unit="ratio",
    minimum_bars=2,
    metadata={"bars_semantics": "transitions_requires_bars_plus_one"},
)
SIGNED_EFFICIENCY = _trend_definition(
    "trend.signed_efficiency",
    "Signed directional efficiency",
    "Signed net close displacement divided by close-path length.",
    unit="ratio",
    minimum_bars=2,
    metadata={"bars_semantics": "transitions_requires_bars_plus_one"},
)
UP_CLOSE_FRACTION = _trend_definition(
    "trend.up_close_fraction",
    "Up-close fraction",
    "Fraction of latest exact close transitions that increased.",
    unit="ratio",
    minimum_bars=2,
    metadata={"bars_semantics": "transitions_requires_bars_plus_one"},
)
DOWN_CLOSE_FRACTION = _trend_definition(
    "trend.down_close_fraction",
    "Down-close fraction",
    "Fraction of latest exact close transitions that decreased.",
    unit="ratio",
    minimum_bars=2,
    metadata={"bars_semantics": "transitions_requires_bars_plus_one"},
)
FLAT_CLOSE_FRACTION = _trend_definition(
    "trend.flat_close_fraction",
    "Flat-close fraction",
    "Fraction of latest exact close transitions that were equal.",
    unit="ratio",
    minimum_bars=2,
    metadata={"bars_semantics": "transitions_requires_bars_plus_one"},
)
CONSECUTIVE_UP_CLOSES = _trend_definition(
    "trend.consecutive_up_closes",
    "Consecutive latest up closes",
    "Number of immediately consecutive latest close increases.",
    unit="transitions",
    minimum_bars=2,
    value_type=FeatureValueType.INTEGER,
)
CONSECUTIVE_DOWN_CLOSES = _trend_definition(
    "trend.consecutive_down_closes",
    "Consecutive latest down closes",
    "Number of immediately consecutive latest close decreases.",
    unit="transitions",
    minimum_bars=2,
    value_type=FeatureValueType.INTEGER,
)
DISTANCE_FROM_SMA_ATR = _trend_definition(
    "trend.distance_from_sma_atr",
    "Distance from simple moving average in ATR units",
    "Latest completed close minus SMA, divided by Wilder ATR.",
    unit="atr_multiple",
    minimum_bars=2,
)
DISTANCE_FROM_EMA_ATR = _trend_definition(
    "trend.distance_from_ema_atr",
    "Distance from exponential moving average in ATR units",
    "Latest completed close minus EMA, divided by Wilder ATR.",
    unit="atr_multiple",
    minimum_bars=2,
)


class _AverageKind(StrEnum):
    SMA = "sma"
    EMA = "ema"


class _AverageOutput(StrEnum):
    VALUE = "value"
    DISTANCE_PERCENT = "distance_percent"


def _average(closes: tuple[float, ...], period: int, kind: _AverageKind) -> float:
    if kind is _AverageKind.SMA:
        return simple_moving_average(closes, period)
    return exponential_moving_average(closes, period)


def _average_lookback(
    closes: tuple[float, ...], period: int, kind: _AverageKind
) -> int:
    return period if kind is _AverageKind.SMA else len(closes)


class MovingAverageCalculator(A22Calculator):
    """Calculate an average or completed-close distance from that average."""

    def __init__(
        self,
        definition: FeatureDefinition,
        kind: _AverageKind,
        output: _AverageOutput,
    ) -> None:
        self._definition = definition
        self._kind = kind
        self._output = output

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request, parameter_names=("period",))
        period = positive_int_parameter(request, "period")
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=period
        )
        if failure is not None:
            return failure
        assert prepared is not None
        closes = tuple(bar.close for bar in prepared.history.bars)
        average = _average(closes, period, self._kind)
        lookback = _average_lookback(closes, period, self._kind)
        if self._output is _AverageOutput.VALUE:
            value = average
        else:
            if average <= 0:
                return self._history_result(
                    context,
                    request,
                    prepared,
                    status=FeatureStatus.FAILED,
                    value=None,
                    lookback_bars_used=lookback,
                    warnings=("moving-average distance requires a positive average",),
                )
            value = ((closes[-1] / average) - 1.0) * 100.0
        return self._history_result(
            context,
            request,
            prepared,
            value=value,
            lookback_bars_used=lookback,
        )


class MovingAverageSpreadCalculator(A22Calculator):
    """Calculate fast-average distance from a slower average."""

    def __init__(self, definition: FeatureDefinition, kind: _AverageKind) -> None:
        self._definition = definition
        self._kind = kind

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(
            request, parameter_names=("fast_period", "slow_period")
        )
        fast = positive_int_parameter(request, "fast_period")
        slow = positive_int_parameter(request, "slow_period")
        if fast >= slow:
            raise FeatureParameterError("fast_period must be less than slow_period")
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=slow
        )
        if failure is not None:
            return failure
        assert prepared is not None
        closes = tuple(bar.close for bar in prepared.history.bars)
        fast_average = _average(closes, fast, self._kind)
        slow_average = _average(closes, slow, self._kind)
        lookback = _average_lookback(closes, slow, self._kind)
        if slow_average <= 0:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=lookback,
                warnings=("moving-average spread requires a positive slow average",),
            )
        return self._history_result(
            context,
            request,
            prepared,
            value=((fast_average / slow_average) - 1.0) * 100.0,
            lookback_bars_used=lookback,
        )


class _RegressionOutput(StrEnum):
    SLOPE = "slope"
    SLOPE_PERCENT = "slope_percent"
    R2 = "r2"


class LinearRegressionCalculator(A22Calculator):
    """Calculate close OLS slope, normalized slope, or R-squared."""

    def __init__(
        self, definition: FeatureDefinition, output: _RegressionOutput
    ) -> None:
        self._definition = definition
        self._output = output

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request, parameter_names=("bars",))
        bars = positive_int_parameter(request, "bars")
        if bars < 2:
            raise FeatureParameterError("bars must be at least 2 for linear regression")
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=bars
        )
        if failure is not None:
            return failure
        assert prepared is not None
        closes = tuple(bar.close for bar in prepared.history.bars[-bars:])
        regression = linear_regression(closes)
        if self._output is _RegressionOutput.SLOPE:
            value = regression.slope
        elif self._output is _RegressionOutput.R2:
            value = regression.r_squared
        else:
            if regression.mean_close <= 0:
                return self._history_result(
                    context,
                    request,
                    prepared,
                    status=FeatureStatus.FAILED,
                    value=None,
                    lookback_bars_used=bars,
                    warnings=("normalized slope requires a positive mean close",),
                )
            value = (regression.slope / regression.mean_close) * 100.0
        return self._history_result(
            context,
            request,
            prepared,
            value=value,
            lookback_bars_used=bars,
        )


class EfficiencyCalculator(A22Calculator):
    """Calculate unsigned or signed efficiency across exact transitions."""

    def __init__(self, definition: FeatureDefinition, *, signed: bool) -> None:
        self._definition = definition
        self._signed = signed

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request, parameter_names=("bars",))
        bars = positive_int_parameter(request, "bars")
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=bars + 1
        )
        if failure is not None:
            return failure
        assert prepared is not None
        closes = tuple(bar.close for bar in prepared.history.bars[-bars - 1 :])
        unsigned, signed = directional_efficiency(closes)
        return self._history_result(
            context,
            request,
            prepared,
            value=signed if self._signed else unsigned,
            lookback_bars_used=bars + 1,
        )


class _FractionKind(StrEnum):
    UP = "up"
    DOWN = "down"
    FLAT = "flat"


class CloseFractionCalculator(A22Calculator):
    """Calculate one member of the exact close-transition distribution."""

    def __init__(self, definition: FeatureDefinition, kind: _FractionKind) -> None:
        self._definition = definition
        self._kind = kind

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request, parameter_names=("bars",))
        bars = positive_int_parameter(request, "bars")
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=bars + 1
        )
        if failure is not None:
            return failure
        assert prepared is not None
        closes = tuple(bar.close for bar in prepared.history.bars[-bars - 1 :])
        counts = close_direction_counts(closes)
        numerator = {
            _FractionKind.UP: counts.up,
            _FractionKind.DOWN: counts.down,
            _FractionKind.FLAT: counts.flat,
        }[self._kind]
        return self._history_result(
            context,
            request,
            prepared,
            value=numerator / bars,
            lookback_bars_used=bars + 1,
        )


class ConsecutiveCloseCalculator(A22Calculator):
    """Count immediately consecutive increases or decreases at history end."""

    def __init__(self, definition: FeatureDefinition, *, increasing: bool) -> None:
        self._definition = definition
        self._increasing = increasing

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request)
        prepared, failure = self._prepare_history(context, request, minimum_bars=2)
        if failure is not None:
            return failure
        assert prepared is not None
        closes = tuple(bar.close for bar in prepared.history.bars)
        value, lookback = consecutive_close_run(
            closes, increasing=self._increasing
        )
        return self._history_result(
            context,
            request,
            prepared,
            value=value,
            lookback_bars_used=lookback,
        )


class MovingAverageAtrDistanceCalculator(A22Calculator):
    """Normalize completed-close distance from one average by Wilder ATR."""

    def __init__(self, definition: FeatureDefinition, kind: _AverageKind) -> None:
        self._definition = definition
        self._kind = kind

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(
            request, parameter_names=("atr_period", "ma_period")
        )
        atr_period = positive_int_parameter(request, "atr_period")
        ma_period = positive_int_parameter(request, "ma_period")
        minimum = max(ma_period, atr_period + 1)
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=minimum
        )
        if failure is not None:
            return failure
        assert prepared is not None
        closes = tuple(bar.close for bar in prepared.history.bars)
        average = _average(closes, ma_period, self._kind)
        atr = wilder_atr(prepared.history.bars, atr_period)
        if atr == 0:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=len(closes),
                warnings=("moving-average ATR distance is undefined for zero ATR",),
            )
        return self._history_result(
            context,
            request,
            prepared,
            value=(closes[-1] - average) / atr,
            lookback_bars_used=len(closes),
        )


TREND_FEATURE_DEFINITIONS = (
    SMA,
    EMA,
    DISTANCE_FROM_SMA_PERCENT,
    DISTANCE_FROM_EMA_PERCENT,
    SMA_SPREAD_PERCENT,
    EMA_SPREAD_PERCENT,
    LINEAR_SLOPE,
    LINEAR_SLOPE_PERCENT,
    LINEAR_R2,
    DIRECTIONAL_EFFICIENCY,
    SIGNED_EFFICIENCY,
    UP_CLOSE_FRACTION,
    DOWN_CLOSE_FRACTION,
    FLAT_CLOSE_FRACTION,
    CONSECUTIVE_UP_CLOSES,
    CONSECUTIVE_DOWN_CLOSES,
    DISTANCE_FROM_SMA_ATR,
    DISTANCE_FROM_EMA_ATR,
)

TREND_CALCULATORS: tuple[FeatureCalculator, ...] = (
    MovingAverageCalculator(SMA, _AverageKind.SMA, _AverageOutput.VALUE),
    MovingAverageCalculator(EMA, _AverageKind.EMA, _AverageOutput.VALUE),
    MovingAverageCalculator(
        DISTANCE_FROM_SMA_PERCENT,
        _AverageKind.SMA,
        _AverageOutput.DISTANCE_PERCENT,
    ),
    MovingAverageCalculator(
        DISTANCE_FROM_EMA_PERCENT,
        _AverageKind.EMA,
        _AverageOutput.DISTANCE_PERCENT,
    ),
    MovingAverageSpreadCalculator(SMA_SPREAD_PERCENT, _AverageKind.SMA),
    MovingAverageSpreadCalculator(EMA_SPREAD_PERCENT, _AverageKind.EMA),
    LinearRegressionCalculator(LINEAR_SLOPE, _RegressionOutput.SLOPE),
    LinearRegressionCalculator(
        LINEAR_SLOPE_PERCENT, _RegressionOutput.SLOPE_PERCENT
    ),
    LinearRegressionCalculator(LINEAR_R2, _RegressionOutput.R2),
    EfficiencyCalculator(DIRECTIONAL_EFFICIENCY, signed=False),
    EfficiencyCalculator(SIGNED_EFFICIENCY, signed=True),
    CloseFractionCalculator(UP_CLOSE_FRACTION, _FractionKind.UP),
    CloseFractionCalculator(DOWN_CLOSE_FRACTION, _FractionKind.DOWN),
    CloseFractionCalculator(FLAT_CLOSE_FRACTION, _FractionKind.FLAT),
    ConsecutiveCloseCalculator(CONSECUTIVE_UP_CLOSES, increasing=True),
    ConsecutiveCloseCalculator(CONSECUTIVE_DOWN_CLOSES, increasing=False),
    MovingAverageAtrDistanceCalculator(DISTANCE_FROM_SMA_ATR, _AverageKind.SMA),
    MovingAverageAtrDistanceCalculator(DISTANCE_FROM_EMA_ATR, _AverageKind.EMA),
)
