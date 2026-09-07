"""Deterministic A2.2 range, ATR, and realized-volatility features."""

import math
import statistics
from enum import StrEnum

from tiaf.context import AnalysisContext
from tiaf.contracts import DataQuality
from tiaf.contracts.common import Metadata
from tiaf.data import OHLCVBar
from tiaf.features._calculation import (
    A22Calculator,
    positive_int_parameter,
    positive_number_parameter,
    resolve_previous_close,
    worst_quality,
)
from tiaf.features.enums import FeatureCategory, FeatureSourceKind, FeatureStatus, FeatureValueType
from tiaf.features.models import FeatureDefinition, FeatureRequest, FeatureResult
from tiaf.features.registry import FeatureCalculator


def _range_definition(
    feature_id: str,
    name: str,
    description: str,
    *,
    unit: str,
    minimum_bars: int,
    sources: tuple[FeatureSourceKind, ...] = (FeatureSourceKind.HISTORY,),
    category: FeatureCategory = FeatureCategory.STRUCTURE,
    metadata: Metadata | None = None,
) -> FeatureDefinition:
    return FeatureDefinition(
        feature_id=feature_id,
        name=name,
        category=category,
        description=description,
        value_type=FeatureValueType.FLOAT,
        unit=unit,
        required_sources=sources,
        minimum_history_bars=minimum_bars,
        metadata=metadata or {},
    )


TRUE_RANGE = _range_definition(
    "range.true_range",
    "True range",
    "Latest bar true range using its high, low, and the preceding bar close.",
    unit="price",
    minimum_bars=2,
)
BAR_PERCENT = _range_definition(
    "range.bar_percent",
    "Bar range percentage",
    "Latest bar high-low range divided by its close as a percentage.",
    unit="%",
    minimum_bars=1,
)
BODY_PERCENT = _range_definition(
    "range.body_percent",
    "Bar body percentage",
    "Absolute latest bar close-open distance divided by its close.",
    unit="%",
    minimum_bars=1,
)
UPPER_WICK_PERCENT = _range_definition(
    "range.upper_wick_percent",
    "Upper wick percentage",
    "Latest bar high minus the greater of open and close, divided by close.",
    unit="%",
    minimum_bars=1,
)
LOWER_WICK_PERCENT = _range_definition(
    "range.lower_wick_percent",
    "Lower wick percentage",
    "Lesser of latest bar open and close minus low, divided by close.",
    unit="%",
    minimum_bars=1,
)
ATR = _range_definition(
    "volatility.atr",
    "Wilder average true range",
    "Wilder-smoothed true range initialized with an arithmetic mean.",
    unit="price",
    minimum_bars=2,
    category=FeatureCategory.VOLATILITY,
    metadata={"method": "wilder", "warmup": "period_plus_one_bars"},
)
ATR_PERCENT = _range_definition(
    "volatility.atr_percent",
    "Wilder average true range percentage",
    "Wilder ATR divided by latest close as a percentage.",
    unit="%",
    minimum_bars=2,
    category=FeatureCategory.VOLATILITY,
    metadata={"method": "wilder", "warmup": "period_plus_one_bars"},
)
REALIZED_VOLATILITY = _range_definition(
    "volatility.realized",
    "Annualized realized volatility",
    "Sample standard deviation of exact-window log returns, explicitly annualized.",
    unit="%",
    minimum_bars=3,
    category=FeatureCategory.VOLATILITY,
    metadata={
        "return_method": "log",
        "dispersion": "sample_standard_deviation",
        "annualization": "explicit_parameter",
    },
)
MOVE_OVER_ATR = _range_definition(
    "range.move_over_atr",
    "Current move over ATR",
    "Signed quote change from canonical previous-session close divided by Wilder ATR.",
    unit="ATR",
    minimum_bars=2,
    sources=(FeatureSourceKind.QUOTE, FeatureSourceKind.HISTORY),
    metadata={"method": "signed_previous_close_change_over_wilder_atr"},
)


def true_range(current: OHLCVBar, previous_close: float) -> float:
    """Return the canonical true range for one validated bar."""
    return max(
        current.high - current.low,
        abs(current.high - previous_close),
        abs(current.low - previous_close),
    )


def bar_range(bar: OHLCVBar) -> float:
    """Return one validated bar's raw high-low range."""
    return bar.high - bar.low


def bar_range_percent(bar: OHLCVBar) -> float:
    """Return one validated bar's high-low range divided by close."""
    if bar.close == 0:
        raise ValueError("bar range percentage is undefined for zero close")
    return (bar_range(bar) / bar.close) * 100.0


def wilder_atr(bars: tuple[OHLCVBar, ...], period: int) -> float:
    """Calculate latest Wilder ATR from all supplied chronological bars."""
    return wilder_atr_series(bars, period)[-1]


def wilder_atr_series(bars: tuple[OHLCVBar, ...], period: int) -> tuple[float, ...]:
    """Return Wilder ATR values beginning after the strict period warm-up."""
    if period <= 0 or len(bars) < period + 1:
        raise ValueError("Wilder ATR requires period+1 bars")
    ranges = tuple(
        true_range(bars[index], bars[index - 1].close)
        for index in range(1, len(bars))
    )
    atr = sum(ranges[:period]) / period
    values = [atr]
    for value in ranges[period:]:
        atr = ((atr * (period - 1)) + value) / period
        values.append(atr)
    return tuple(values)


class _CandleMode(StrEnum):
    TRUE_RANGE = "true_range"
    BAR_PERCENT = "bar_percent"
    BODY_PERCENT = "body_percent"
    UPPER_WICK_PERCENT = "upper_wick_percent"
    LOWER_WICK_PERCENT = "lower_wick_percent"


class CandleRangeCalculator(A22Calculator):
    """Calculate one factual latest-bar range or candle-shape measure."""

    def __init__(self, definition: FeatureDefinition, mode: _CandleMode) -> None:
        self._definition = definition
        self._mode = mode

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request)
        minimum_bars = 2 if self._mode is _CandleMode.TRUE_RANGE else 1
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=minimum_bars
        )
        if failure is not None:
            return failure
        assert prepared is not None
        current = prepared.history.bars[-1]
        if self._mode is _CandleMode.TRUE_RANGE:
            value = true_range(current, prepared.history.bars[-2].close)
        else:
            if current.close == 0:
                return self._history_result(
                    context,
                    request,
                    prepared,
                    status=FeatureStatus.FAILED,
                    value=None,
                    lookback_bars_used=1,
                    warnings=(f"{request.feature_id} is undefined for zero close",),
                )
            if self._mode is _CandleMode.BAR_PERCENT:
                value = bar_range_percent(current)
            elif self._mode is _CandleMode.BODY_PERCENT:
                value = abs(current.close - current.open) / current.close * 100
            elif self._mode is _CandleMode.UPPER_WICK_PERCENT:
                value = (
                    (current.high - max(current.open, current.close))
                    / current.close
                    * 100
                )
            else:
                value = (
                    (min(current.open, current.close) - current.low)
                    / current.close
                    * 100
                )
        return self._history_result(
            context,
            request,
            prepared,
            value=float(value),
            lookback_bars_used=minimum_bars,
        )


class AtrCalculator(A22Calculator):
    """Calculate Wilder ATR in price or percent units."""

    def __init__(self, definition: FeatureDefinition, *, percent: bool) -> None:
        self._definition = definition
        self._percent = percent

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request, parameter_names=("period",))
        period = positive_int_parameter(request, "period")
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=period + 1
        )
        if failure is not None:
            return failure
        assert prepared is not None
        value = wilder_atr(prepared.history.bars, period)
        if self._percent:
            latest_close = prepared.history.bars[-1].close
            if latest_close == 0:
                return self._history_result(
                    context,
                    request,
                    prepared,
                    status=FeatureStatus.FAILED,
                    value=None,
                    lookback_bars_used=len(prepared.history.bars),
                    warnings=("ATR percentage is undefined for zero latest close",),
                )
            value = (value / latest_close) * 100
        return self._history_result(
            context,
            request,
            prepared,
            value=value,
            lookback_bars_used=len(prepared.history.bars),
        )


class RealizedVolatilityCalculator(A22Calculator):
    _definition = REALIZED_VOLATILITY

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(
            request,
            parameter_names=("bars", "annualization_factor"),
        )
        bars = positive_int_parameter(request, "bars")
        annualization = positive_number_parameter(request, "annualization_factor")
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=bars + 1
        )
        if failure is not None:
            return failure
        assert prepared is not None
        if bars < 2:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.INSUFFICIENT_DATA,
                value=None,
                lookback_bars_used=bars + 1,
                warnings=("sample volatility requires at least 2 log returns",),
            )
        closes = tuple(bar.close for bar in prepared.history.bars[-bars - 1 :])
        if any(close <= 0 for close in closes):
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=bars + 1,
                warnings=("realized volatility requires positive closes",),
            )
        log_returns = tuple(
            math.log(closes[index]) - math.log(closes[index - 1])
            for index in range(1, len(closes))
        )
        value = statistics.stdev(log_returns) * math.sqrt(annualization) * 100
        return self._history_result(
            context,
            request,
            prepared,
            value=value,
            lookback_bars_used=bars + 1,
        )


class MoveOverAtrCalculator(A22Calculator):
    _definition = MOVE_OVER_ATR

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request, parameter_names=("atr_period",))
        period = positive_int_parameter(request, "atr_period")
        previous_close = resolve_previous_close(context, request)
        prepared, failure = self._prepare_mixed(
            context,
            request,
            minimum_history_bars=period + 1,
        )
        if failure is not None:
            return failure
        assert prepared is not None
        if previous_close.value is None:
            return self._result(
                context,
                request,
                status=previous_close.status,
                value=None,
                quality=worst_quality(prepared.quality, previous_close.quality),
                as_of=min(prepared.as_of, previous_close.as_of),
                source_evidence=("quote", "history"),
                source_observed_at=min(prepared.as_of, previous_close.as_of),
                lookback_bars_used=len(prepared.history.bars),
                warnings=tuple(
                    dict.fromkeys(prepared.warnings + previous_close.warnings)
                ),
                metadata={**prepared.metadata, **previous_close.metadata},
            )
        quality = worst_quality(prepared.quality, previous_close.quality)
        status = (
            FeatureStatus.PARTIAL
            if FeatureStatus.PARTIAL in {prepared.status, previous_close.status}
            or quality is not DataQuality.GOOD
            else FeatureStatus.AVAILABLE
        )
        as_of = min(prepared.as_of, previous_close.as_of)
        metadata = {
            **prepared.metadata,
            **previous_close.metadata,
            "source_time_semantics": "oldest_quote_history_market_observation",
        }
        warnings = tuple(
            dict.fromkeys(prepared.warnings + previous_close.warnings)
        )
        atr = wilder_atr(prepared.history.bars, period)
        if atr == 0:
            return self._result(
                context,
                request,
                status=FeatureStatus.FAILED,
                value=None,
                quality=quality,
                as_of=as_of,
                source_evidence=("quote", "history"),
                source_observed_at=as_of,
                lookback_bars_used=len(prepared.history.bars),
                warnings=warnings + ("move over ATR is undefined for zero ATR",),
                metadata=metadata,
            )
        move = prepared.quote.ltp - previous_close.value
        return self._result(
            context,
            request,
            status=status,
            value=move / atr,
            quality=quality,
            as_of=as_of,
            source_evidence=("quote", "history"),
            source_observed_at=as_of,
            lookback_bars_used=len(prepared.history.bars),
            warnings=warnings,
            metadata=metadata,
        )


VOLATILITY_FEATURE_DEFINITIONS = (
    TRUE_RANGE,
    BAR_PERCENT,
    BODY_PERCENT,
    UPPER_WICK_PERCENT,
    LOWER_WICK_PERCENT,
    ATR,
    ATR_PERCENT,
    REALIZED_VOLATILITY,
    MOVE_OVER_ATR,
)

VOLATILITY_CALCULATORS: tuple[FeatureCalculator, ...] = (
    CandleRangeCalculator(TRUE_RANGE, _CandleMode.TRUE_RANGE),
    CandleRangeCalculator(BAR_PERCENT, _CandleMode.BAR_PERCENT),
    CandleRangeCalculator(BODY_PERCENT, _CandleMode.BODY_PERCENT),
    CandleRangeCalculator(UPPER_WICK_PERCENT, _CandleMode.UPPER_WICK_PERCENT),
    CandleRangeCalculator(LOWER_WICK_PERCENT, _CandleMode.LOWER_WICK_PERCENT),
    AtrCalculator(ATR, percent=False),
    AtrCalculator(ATR_PERCENT, percent=True),
    RealizedVolatilityCalculator(),
    MoveOverAtrCalculator(),
)
