"""Prior-range geometry and completed-bar range comparison features."""

import math
from enum import StrEnum

from tiaf.context import AnalysisContext
from tiaf.contracts.common import Metadata
from tiaf.features._calculation import A22Calculator, positive_int_parameter
from tiaf.features._structure_calculation import midpoint_range_percent, prior_range
from tiaf.features.enums import (
    FeatureCategory,
    FeatureSourceKind,
    FeatureStatus,
    FeatureValueType,
)
from tiaf.features.errors import FeatureParameterError
from tiaf.features.models import FeatureDefinition, FeatureRequest, FeatureResult
from tiaf.features.registry import FeatureCalculator
from tiaf.features.volatility import bar_range, wilder_atr


def _definition(
    feature_id: str,
    name: str,
    description: str,
    *,
    unit: str,
    minimum_bars: int = 2,
    metadata: Metadata | None = None,
) -> FeatureDefinition:
    return FeatureDefinition(
        feature_id=feature_id,
        name=name,
        category=FeatureCategory.STRUCTURE,
        description=description,
        value_type=FeatureValueType.FLOAT,
        unit=unit,
        required_sources=(FeatureSourceKind.HISTORY,),
        minimum_history_bars=minimum_bars,
        metadata=metadata or {},
    )


_PRIOR_WINDOW: Metadata = {
    "bars_semantics": "previous_n_completed_bars_excluding_latest",
}

POSITION_VS_PRIOR_RANGE = _definition(
    "structure.position_vs_prior_range",
    "Close position versus prior range",
    "Unclamped latest-close position against the fixed prior high/low range.",
    unit="%",
    metadata={**_PRIOR_WINDOW, "clamped": False},
)
PRIOR_RANGE_PERCENT = _definition(
    "structure.prior_range_percent",
    "Prior range width percentage",
    "Prior high-low width divided by the prior range midpoint.",
    unit="%",
    metadata={**_PRIOR_WINDOW, "normalization": "prior_range_midpoint"},
)
PRIOR_RANGE_ATR = _definition(
    "structure.prior_range_atr",
    "ATR-normalized prior range width",
    "Prior high-low width divided by canonical Wilder ATR.",
    unit="ATR",
    metadata=_PRIOR_WINDOW,
)
RANGE_COMPRESSION_RATIO = _definition(
    "structure.range_compression_ratio",
    "Prior range width ratio",
    "Short prior midpoint-normalized range divided by long prior range.",
    unit="ratio",
    minimum_bars=4,
    metadata={
        "bars_semantics": "nested_prior_windows_excluding_latest",
        "normalization": "prior_range_midpoint",
    },
)
LATEST_RANGE_VS_AVERAGE = _definition(
    "structure.latest_bar_range_vs_average",
    "Latest bar range versus prior average",
    "Latest raw high-low range divided by the mean raw range of prior bars.",
    unit="ratio",
    metadata=_PRIOR_WINDOW,
)


class _RangeOutput(StrEnum):
    POSITION = "position"
    WIDTH_PERCENT = "width_percent"
    WIDTH_ATR = "width_atr"


class PriorRangeGeometryCalculator(A22Calculator):
    """Calculate position or width from one exact prior window."""

    def __init__(self, definition: FeatureDefinition, output: _RangeOutput) -> None:
        self._definition = definition
        self._output = output

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        parameter_names = (
            ("atr_period", "bars")
            if self._output is _RangeOutput.WIDTH_ATR
            else ("bars",)
        )
        self._validate_request(request, parameter_names=parameter_names)
        bars = positive_int_parameter(request, "bars")
        atr_period = (
            positive_int_parameter(request, "atr_period")
            if self._output is _RangeOutput.WIDTH_ATR
            else None
        )
        minimum = max(bars + 1, (atr_period or 0) + 1)
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=minimum
        )
        if failure is not None:
            return failure
        assert prepared is not None
        history = prepared.history.bars
        value_range = prior_range(history[-bars - 1 : -1])
        lookback = bars + 1
        if self._output is _RangeOutput.POSITION:
            if value_range.width == 0:
                return self._history_result(
                    context,
                    request,
                    prepared,
                    status=FeatureStatus.INSUFFICIENT_DATA,
                    value=None,
                    lookback_bars_used=lookback,
                    warnings=("position versus prior range requires nonzero width",),
                )
            value = (history[-1].close - value_range.low) / value_range.width * 100
        elif self._output is _RangeOutput.WIDTH_PERCENT:
            try:
                value = midpoint_range_percent(value_range)
            except ValueError as exc:
                return self._history_result(
                    context,
                    request,
                    prepared,
                    status=FeatureStatus.FAILED,
                    value=None,
                    lookback_bars_used=lookback,
                    warnings=(str(exc),),
                )
        else:
            assert atr_period is not None
            atr = wilder_atr(history, atr_period)
            lookback = len(history)
            if atr == 0:
                return self._history_result(
                    context,
                    request,
                    prepared,
                    status=FeatureStatus.FAILED,
                    value=None,
                    lookback_bars_used=lookback,
                    warnings=("ATR-normalized prior range requires nonzero ATR",),
                )
            value = value_range.width / atr
        return self._history_result(
            context,
            request,
            prepared,
            value=value,
            lookback_bars_used=lookback,
        )


class RangeCompressionCalculator(A22Calculator):
    """Compare midpoint-normalized nested prior ranges without interpretation."""

    _definition = RANGE_COMPRESSION_RATIO

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(
            request, parameter_names=("long_bars", "short_bars")
        )
        short_bars = positive_int_parameter(request, "short_bars")
        long_bars = positive_int_parameter(request, "long_bars")
        if short_bars <= 1 or long_bars <= 1:
            raise FeatureParameterError("range windows must both exceed 1 bar")
        if short_bars >= long_bars:
            raise FeatureParameterError("short_bars must be less than long_bars")
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=long_bars + 1
        )
        if failure is not None:
            return failure
        assert prepared is not None
        history = prepared.history.bars
        short_range = prior_range(history[-short_bars - 1 : -1])
        long_range = prior_range(history[-long_bars - 1 : -1])
        try:
            short_percent = midpoint_range_percent(short_range)
            long_percent = midpoint_range_percent(long_range)
        except ValueError as exc:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=long_bars + 1,
                warnings=(str(exc),),
            )
        if long_percent == 0:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=long_bars + 1,
                warnings=("range width ratio requires nonzero long-window range",),
            )
        return self._history_result(
            context,
            request,
            prepared,
            value=short_percent / long_percent,
            lookback_bars_used=long_bars + 1,
        )


class LatestRangeExpansionCalculator(A22Calculator):
    """Compare latest raw bar range with the preceding exact baseline."""

    _definition = LATEST_RANGE_VS_AVERAGE

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
        window = prepared.history.bars[-bars - 1 :]
        baseline = math.fsum(bar_range(bar) for bar in window[:-1]) / bars
        if baseline == 0:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=bars + 1,
                warnings=("latest range comparison requires nonzero prior average",),
            )
        return self._history_result(
            context,
            request,
            prepared,
            value=bar_range(window[-1]) / baseline,
            lookback_bars_used=bars + 1,
        )


COMPRESSION_FEATURE_DEFINITIONS = (
    POSITION_VS_PRIOR_RANGE,
    PRIOR_RANGE_PERCENT,
    PRIOR_RANGE_ATR,
    RANGE_COMPRESSION_RATIO,
    LATEST_RANGE_VS_AVERAGE,
)

COMPRESSION_CALCULATORS: tuple[FeatureCalculator, ...] = (
    PriorRangeGeometryCalculator(POSITION_VS_PRIOR_RANGE, _RangeOutput.POSITION),
    PriorRangeGeometryCalculator(PRIOR_RANGE_PERCENT, _RangeOutput.WIDTH_PERCENT),
    PriorRangeGeometryCalculator(PRIOR_RANGE_ATR, _RangeOutput.WIDTH_ATR),
    RangeCompressionCalculator(),
    LatestRangeExpansionCalculator(),
)
