"""Deterministic A2.2 price-location and rolling-extrema features."""

import math
from enum import StrEnum

from tiaf.context import AnalysisContext
from tiaf.contracts.common import Metadata
from tiaf.features._calculation import (
    A22Calculator,
    evidence,
    evidence_status,
    evidence_warnings,
    positive_int_parameter,
    resolve_previous_close,
    source_quality,
)
from tiaf.features.enums import FeatureCategory, FeatureSourceKind, FeatureStatus, FeatureValueType
from tiaf.features.models import FeatureDefinition, FeatureRequest, FeatureResult
from tiaf.features.registry import FeatureCalculator


def _price_definition(
    feature_id: str,
    name: str,
    description: str,
    *,
    sources: tuple[FeatureSourceKind, ...] = (FeatureSourceKind.HISTORY,),
    unit: str = "price",
    minimum_bars: int | None = 1,
    supported_intervals: tuple[str, ...] | None = None,
    metadata: Metadata | None = None,
) -> FeatureDefinition:
    return FeatureDefinition(
        feature_id=feature_id,
        name=name,
        category=FeatureCategory.PRICE,
        description=description,
        value_type=FeatureValueType.FLOAT,
        unit=unit,
        required_sources=sources,
        minimum_history_bars=minimum_bars,
        supported_intervals=supported_intervals,
        metadata=metadata or {},
    )


PREVIOUS_CLOSE = _price_definition(
    "price.previous_close",
    "Previous close",
    "Factual previous trading-session close, preferring normalized quote data.",
    sources=(FeatureSourceKind.QUOTE,),
    minimum_bars=None,
    supported_intervals=("1d",),
    metadata={"source_semantics": "quote_previous_close_then_daily_history_fallback"},
)
SESSION_OPEN = _price_definition(
    "price.open",
    "Current session open",
    "Current trading-session open from the normalized quote.",
    sources=(FeatureSourceKind.QUOTE,),
    minimum_bars=None,
    supported_intervals=("1d",),
)
SESSION_HIGH = _price_definition(
    "price.high",
    "Current session high",
    "Current trading-session high from the normalized quote.",
    sources=(FeatureSourceKind.QUOTE,),
    minimum_bars=None,
    supported_intervals=("1d",),
)
SESSION_LOW = _price_definition(
    "price.low",
    "Current session low",
    "Current trading-session low from the normalized quote.",
    sources=(FeatureSourceKind.QUOTE,),
    minimum_bars=None,
    supported_intervals=("1d",),
)
PRICE_CHANGE_ABSOLUTE = _price_definition(
    "price.change_absolute",
    "Current price change",
    "Quote LTP minus the canonical previous trading-session close.",
    sources=(FeatureSourceKind.QUOTE,),
    minimum_bars=None,
    supported_intervals=("1d",),
    metadata={"reference": "canonical_previous_session_close"},
)
PRICE_CHANGE_PERCENT = _price_definition(
    "price.change_percent",
    "Current price change percentage",
    "Percentage change from canonical previous trading-session close to quote LTP.",
    sources=(FeatureSourceKind.QUOTE,),
    unit="%",
    minimum_bars=None,
    supported_intervals=("1d",),
    metadata={"reference": "canonical_previous_session_close"},
)
POSITION_IN_DAY_RANGE = _price_definition(
    "price.position_in_day_range",
    "Position in day range",
    "Quote LTP position within normalized current-session quote high and low.",
    sources=(FeatureSourceKind.QUOTE,),
    unit="%",
    minimum_bars=None,
    supported_intervals=("1d",),
    metadata={"range_semantics": "quote_current_session_high_low"},
)
ROLLING_HIGH = _price_definition(
    "price.rolling_high",
    "Rolling high",
    "Maximum high over the latest N historical bars.",
    metadata={"bars_semantics": "latest_n_bars"},
)
ROLLING_LOW = _price_definition(
    "price.rolling_low",
    "Rolling low",
    "Minimum low over the latest N historical bars.",
    metadata={"bars_semantics": "latest_n_bars"},
)
DISTANCE_FROM_ROLLING_HIGH_PERCENT = _price_definition(
    "price.distance_from_rolling_high_percent",
    "Distance from rolling high",
    "Latest close divided by latest N-bar high, minus one, as a percentage.",
    unit="%",
    metadata={"bars_semantics": "latest_n_bars"},
)
DISTANCE_FROM_ROLLING_LOW_PERCENT = _price_definition(
    "price.distance_from_rolling_low_percent",
    "Distance from rolling low",
    "Latest close divided by latest N-bar low, minus one, as a percentage.",
    unit="%",
    metadata={"bars_semantics": "latest_n_bars"},
)


class _QuoteField(StrEnum):
    OPEN = "open"
    HIGH = "high"
    LOW = "low"


class QuoteSessionPriceCalculator(A22Calculator):
    """Return one current-session field from normalized quote evidence."""

    def __init__(self, definition: FeatureDefinition, field: _QuoteField) -> None:
        self._definition = definition
        self._field = field

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request)
        descriptor = evidence(context, "quote")
        quality = source_quality(
            descriptor, context.quote.quality if context.quote is not None else None
        )
        status = evidence_status(
            descriptor, context.quote.quality if context.quote is not None else None
        )
        as_of = context.quote.observed_at if context.quote else context.created_at
        if request.interval != "1d":
            return self._result(
                context,
                request,
                status=FeatureStatus.NOT_APPLICABLE,
                value=None,
                quality=quality,
                as_of=as_of,
                source_evidence=("quote",),
                source_observed_at=as_of,
                warnings=("current-session price feature requires interval 1d",),
            )
        if status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
            return self._result(
                context,
                request,
                status=status,
                value=None,
                quality=quality,
                as_of=as_of,
                source_evidence=("quote",),
                source_observed_at=(as_of if context.quote else None),
                warnings=evidence_warnings(descriptor),
            )
        assert context.quote is not None
        value = getattr(context.quote, self._field.value)
        if value is None:
            return self._result(
                context,
                request,
                status=FeatureStatus.INSUFFICIENT_DATA,
                value=None,
                quality=quality,
                as_of=as_of,
                source_evidence=("quote",),
                source_observed_at=as_of,
                warnings=(f"quote {self._field.value} is unavailable",),
            )
        if not math.isfinite(value) or value < 0:
            return self._result(
                context,
                request,
                status=FeatureStatus.FAILED,
                value=None,
                quality=quality,
                as_of=as_of,
                source_evidence=("quote",),
                source_observed_at=as_of,
                warnings=(f"quote {self._field.value} is invalid",),
            )
        return self._result(
            context,
            request,
            status=status,
            value=float(value),
            quality=quality,
            as_of=as_of,
            source_evidence=("quote",),
            source_observed_at=as_of,
            warnings=evidence_warnings(descriptor),
            metadata={
                "price_source": f"quote.{self._field.value}",
                "source_time_semantics": "quote_market_observation",
            },
        )


class _ChangeMode(StrEnum):
    ABSOLUTE = "absolute"
    PERCENT = "percent"


class PreviousCloseCalculator(A22Calculator):
    _definition = PREVIOUS_CLOSE

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request)
        resolved = resolve_previous_close(context, request)
        return self._result(
            context,
            request,
            status=resolved.status,
            value=resolved.value,
            quality=resolved.quality,
            as_of=resolved.as_of,
            source_evidence=resolved.source_evidence,
            source_observed_at=resolved.as_of,
            lookback_bars_used=resolved.lookback_bars_used,
            warnings=resolved.warnings,
            metadata=resolved.metadata,
        )


class PriceChangeCalculator(A22Calculator):
    """Calculate quote change from the shared canonical previous close."""

    def __init__(self, definition: FeatureDefinition, mode: _ChangeMode) -> None:
        self._definition = definition
        self._mode = mode

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request)
        resolved = resolve_previous_close(context, request)
        if resolved.value is None or resolved.quote is None:
            return self._result(
                context,
                request,
                status=resolved.status,
                value=None,
                quality=resolved.quality,
                as_of=resolved.as_of,
                source_evidence=resolved.source_evidence,
                source_observed_at=resolved.as_of,
                lookback_bars_used=resolved.lookback_bars_used,
                warnings=resolved.warnings,
                metadata=resolved.metadata,
            )
        current = resolved.quote.ltp
        if not math.isfinite(current) or current < 0:
            return self._result(
                context,
                request,
                status=FeatureStatus.FAILED,
                value=None,
                quality=resolved.quality,
                as_of=resolved.as_of,
                source_evidence=resolved.source_evidence,
                source_observed_at=resolved.as_of,
                warnings=("quote current price is invalid",),
                metadata=resolved.metadata,
            )
        if self._mode is _ChangeMode.ABSOLUTE:
            value = current - resolved.value
        else:
            value = ((current / resolved.value) - 1) * 100
        return self._result(
            context,
            request,
            status=resolved.status,
            value=float(value),
            quality=resolved.quality,
            as_of=resolved.as_of,
            source_evidence=resolved.source_evidence,
            source_observed_at=resolved.as_of,
            lookback_bars_used=resolved.lookback_bars_used,
            warnings=resolved.warnings,
            metadata=resolved.metadata,
        )


class PositionInDayRangeCalculator(A22Calculator):
    _definition = POSITION_IN_DAY_RANGE

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request)
        descriptor = evidence(context, "quote")
        quality = source_quality(
            descriptor, context.quote.quality if context.quote is not None else None
        )
        status = evidence_status(
            descriptor, context.quote.quality if context.quote is not None else None
        )
        as_of = context.quote.observed_at if context.quote else context.created_at
        if request.interval != "1d":
            return self._result(
                context,
                request,
                status=FeatureStatus.NOT_APPLICABLE,
                value=None,
                quality=quality,
                as_of=as_of,
                source_evidence=("quote",),
                source_observed_at=(as_of if context.quote else None),
                warnings=("position in day range requires interval 1d",),
            )
        if status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
            return self._result(
                context,
                request,
                status=status,
                value=None,
                quality=quality,
                as_of=as_of,
                source_evidence=("quote",),
                source_observed_at=(as_of if context.quote else None),
                warnings=evidence_warnings(descriptor),
            )
        assert context.quote is not None
        current, high, low = context.quote.ltp, context.quote.high, context.quote.low
        if high is None or low is None:
            return self._result(
                context,
                request,
                status=FeatureStatus.INSUFFICIENT_DATA,
                value=None,
                quality=quality,
                as_of=as_of,
                source_evidence=("quote",),
                source_observed_at=as_of,
                warnings=("quote current-session high or low is unavailable",),
            )
        values = (current, high, low)
        if any(not math.isfinite(value) or value < 0 for value in values) or high < low:
            return self._result(
                context,
                request,
                status=FeatureStatus.FAILED,
                value=None,
                quality=quality,
                as_of=as_of,
                source_evidence=("quote",),
                source_observed_at=as_of,
                warnings=("quote current-session range is invalid",),
            )
        day_range = high - low
        if day_range == 0:
            return self._result(
                context,
                request,
                status=FeatureStatus.INSUFFICIENT_DATA,
                value=None,
                quality=quality,
                as_of=as_of,
                source_evidence=("quote",),
                source_observed_at=as_of,
                warnings=("position in day range is undefined for a flat range",),
            )
        value = ((current - low) / day_range) * 100
        warnings = evidence_warnings(descriptor)
        if current < low or current > high:
            warnings += ("current price is outside the reported quote session range",)
        return self._result(
            context,
            request,
            status=status,
            value=value,
            quality=quality,
            as_of=as_of,
            source_evidence=("quote",),
            source_observed_at=as_of,
            warnings=warnings,
            metadata={
                "range_source": "quote.high_low",
                "source_time_semantics": "quote_market_observation",
            },
        )


class _RollingMode(StrEnum):
    HIGH = "high"
    LOW = "low"
    DISTANCE_HIGH = "distance_high"
    DISTANCE_LOW = "distance_low"


class RollingPriceCalculator(A22Calculator):
    """Calculate exact-window extrema or distance from those extrema."""

    def __init__(self, definition: FeatureDefinition, mode: _RollingMode) -> None:
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
        window = prepared.history.bars[-bars:]
        rolling_high = max(bar.high for bar in window)
        rolling_low = min(bar.low for bar in window)
        if self._mode is _RollingMode.HIGH:
            value = rolling_high
        elif self._mode is _RollingMode.LOW:
            value = rolling_low
        elif self._mode is _RollingMode.DISTANCE_HIGH:
            if rolling_high == 0:
                return self._history_result(
                    context,
                    request,
                    prepared,
                    status=FeatureStatus.FAILED,
                    value=None,
                    lookback_bars_used=bars,
                    warnings=("distance from rolling high is undefined for zero high",),
                )
            value = ((window[-1].close / rolling_high) - 1) * 100
        else:
            if rolling_low == 0:
                return self._history_result(
                    context,
                    request,
                    prepared,
                    status=FeatureStatus.FAILED,
                    value=None,
                    lookback_bars_used=bars,
                    warnings=("distance from rolling low is undefined for zero low",),
                )
            value = ((window[-1].close / rolling_low) - 1) * 100
        return self._history_result(
            context,
            request,
            prepared,
            value=float(value),
            lookback_bars_used=bars,
        )


PRICE_FEATURE_DEFINITIONS = (
    PREVIOUS_CLOSE,
    SESSION_OPEN,
    SESSION_HIGH,
    SESSION_LOW,
    PRICE_CHANGE_ABSOLUTE,
    PRICE_CHANGE_PERCENT,
    POSITION_IN_DAY_RANGE,
    ROLLING_HIGH,
    ROLLING_LOW,
    DISTANCE_FROM_ROLLING_HIGH_PERCENT,
    DISTANCE_FROM_ROLLING_LOW_PERCENT,
)

PRICE_CALCULATORS: tuple[FeatureCalculator, ...] = (
    PreviousCloseCalculator(),
    QuoteSessionPriceCalculator(SESSION_OPEN, _QuoteField.OPEN),
    QuoteSessionPriceCalculator(SESSION_HIGH, _QuoteField.HIGH),
    QuoteSessionPriceCalculator(SESSION_LOW, _QuoteField.LOW),
    PriceChangeCalculator(PRICE_CHANGE_ABSOLUTE, _ChangeMode.ABSOLUTE),
    PriceChangeCalculator(PRICE_CHANGE_PERCENT, _ChangeMode.PERCENT),
    PositionInDayRangeCalculator(),
    RollingPriceCalculator(ROLLING_HIGH, _RollingMode.HIGH),
    RollingPriceCalculator(ROLLING_LOW, _RollingMode.LOW),
    RollingPriceCalculator(
        DISTANCE_FROM_ROLLING_HIGH_PERCENT, _RollingMode.DISTANCE_HIGH
    ),
    RollingPriceCalculator(
        DISTANCE_FROM_ROLLING_LOW_PERCENT, _RollingMode.DISTANCE_LOW
    ),
)
