"""Deterministic A2.2 logarithmic return and path-measure features."""

import math
from enum import StrEnum

from tiaf.context import AnalysisContext
from tiaf.features._calculation import A22Calculator, positive_int_parameter
from tiaf.features.enums import FeatureCategory, FeatureSourceKind, FeatureStatus, FeatureValueType
from tiaf.features.models import FeatureDefinition, FeatureRequest, FeatureResult
from tiaf.features.registry import FeatureCalculator

LOG_RETURN = FeatureDefinition(
    feature_id="return.log",
    name="Log return",
    category=FeatureCategory.RETURN,
    description="Natural logarithm of latest close divided by close N intervals earlier.",
    value_type=FeatureValueType.FLOAT,
    unit="log_ratio",
    required_sources=(FeatureSourceKind.HISTORY,),
    minimum_history_bars=2,
    metadata={"bars_semantics": "intervals_back_requires_bars_plus_one"},
)
MAX_DRAWDOWN_PERCENT = FeatureDefinition(
    feature_id="return.max_drawdown_percent",
    name="Maximum drawdown percentage",
    category=FeatureCategory.RETURN,
    description="Most negative close decline from a running peak in the latest N bars.",
    value_type=FeatureValueType.FLOAT,
    unit="%",
    required_sources=(FeatureSourceKind.HISTORY,),
    minimum_history_bars=1,
    metadata={"convention": "negative_or_zero", "bars_semantics": "latest_n_bars"},
)
MAX_RUNUP_PERCENT = FeatureDefinition(
    feature_id="return.max_runup_percent",
    name="Maximum run-up percentage",
    category=FeatureCategory.RETURN,
    description="Largest close rise from a running trough in the latest N bars.",
    value_type=FeatureValueType.FLOAT,
    unit="%",
    required_sources=(FeatureSourceKind.HISTORY,),
    minimum_history_bars=1,
    metadata={"convention": "positive_or_zero", "bars_semantics": "latest_n_bars"},
)


class LogReturnCalculator(A22Calculator):
    _definition = LOG_RETURN

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
        latest = prepared.history.bars[-1].close
        base = prepared.history.bars[-1 - bars].close
        if base <= 0 or latest <= 0:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=bars + 1,
                warnings=("log return requires positive base and latest closes",),
            )
        return self._history_result(
            context,
            request,
            prepared,
            value=math.log(latest) - math.log(base),
            lookback_bars_used=bars + 1,
        )


class _PathMode(StrEnum):
    DRAWDOWN = "drawdown"
    RUNUP = "runup"


class PathReturnCalculator(A22Calculator):
    """Calculate close-path drawdown or run-up within an exact latest window."""

    def __init__(self, definition: FeatureDefinition, mode: _PathMode) -> None:
        self._definition = definition
        self._mode = mode

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request, parameter_names=("bars",))
        bars = positive_int_parameter(request, "bars")
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=bars
        )
        if failure is not None:
            return failure
        assert prepared is not None
        closes = tuple(bar.close for bar in prepared.history.bars[-bars:])
        value: float | None
        if self._mode is _PathMode.DRAWDOWN:
            value = self._max_drawdown(closes)
        else:
            value = self._max_runup(closes)
            if value is None:
                return self._history_result(
                    context,
                    request,
                    prepared,
                    status=FeatureStatus.FAILED,
                    value=None,
                    lookback_bars_used=bars,
                    warnings=("run-up percentage is undefined from a zero trough",),
                )
        return self._history_result(
            context,
            request,
            prepared,
            value=value,
            lookback_bars_used=bars,
        )

    @staticmethod
    def _max_drawdown(closes: tuple[float, ...]) -> float:
        peak = closes[0]
        maximum_drawdown = 0.0
        for close in closes:
            peak = max(peak, close)
            drawdown = 0.0 if peak == 0 else ((close / peak) - 1) * 100
            maximum_drawdown = min(maximum_drawdown, drawdown)
        return maximum_drawdown

    @staticmethod
    def _max_runup(closes: tuple[float, ...]) -> float | None:
        trough = closes[0]
        maximum_runup = 0.0
        for close in closes:
            trough = min(trough, close)
            if trough == 0:
                if close > 0:
                    return None
                runup = 0.0
            else:
                runup = ((close / trough) - 1) * 100
            maximum_runup = max(maximum_runup, runup)
        return maximum_runup


RETURN_FEATURE_DEFINITIONS = (
    LOG_RETURN,
    MAX_DRAWDOWN_PERCENT,
    MAX_RUNUP_PERCENT,
)

RETURN_CALCULATORS: tuple[FeatureCalculator, ...] = (
    LogReturnCalculator(),
    PathReturnCalculator(MAX_DRAWDOWN_PERCENT, _PathMode.DRAWDOWN),
    PathReturnCalculator(MAX_RUNUP_PERCENT, _PathMode.RUNUP),
)
