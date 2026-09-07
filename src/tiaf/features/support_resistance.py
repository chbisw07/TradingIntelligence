"""Deterministic prior-boundary levels and signed distance measurements."""

from enum import StrEnum

from tiaf.context import AnalysisContext
from tiaf.contracts.common import Metadata
from tiaf.features._calculation import A22Calculator, positive_int_parameter
from tiaf.features._structure_calculation import prior_range, signed_distance_percent
from tiaf.features.enums import (
    FeatureCategory,
    FeatureSourceKind,
    FeatureStatus,
    FeatureValueType,
)
from tiaf.features.models import FeatureDefinition, FeatureRequest, FeatureResult
from tiaf.features.registry import FeatureCalculator
from tiaf.features.volatility import wilder_atr


def _definition(
    feature_id: str,
    name: str,
    description: str,
    *,
    unit: str,
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
        minimum_history_bars=2,
        metadata=metadata or {},
    )


_PRIOR_WINDOW: Metadata = {
    "bars_semantics": "previous_n_completed_bars_excluding_latest",
}

PRIOR_HIGH = _definition(
    "resistance.prior_high",
    "Prior rolling high boundary",
    "Maximum high of the exact prior bar window, excluding the latest bar.",
    unit="price",
    metadata=_PRIOR_WINDOW,
)
PRIOR_LOW = _definition(
    "support.prior_low",
    "Prior rolling low boundary",
    "Minimum low of the exact prior bar window, excluding the latest bar.",
    unit="price",
    metadata=_PRIOR_WINDOW,
)
RESISTANCE_DISTANCE_PERCENT = _definition(
    "resistance.distance_percent",
    "Close distance from prior high",
    "Signed latest-close distance from the fixed prior high boundary.",
    unit="%",
    metadata=_PRIOR_WINDOW,
)
SUPPORT_DISTANCE_PERCENT = _definition(
    "support.distance_percent",
    "Close distance from prior low",
    "Signed latest-close distance from the fixed prior low boundary.",
    unit="%",
    metadata=_PRIOR_WINDOW,
)
RESISTANCE_DISTANCE_ATR = _definition(
    "resistance.distance_atr",
    "ATR-normalized close distance from prior high",
    "Latest close minus prior high, divided by canonical Wilder ATR.",
    unit="ATR",
    metadata=_PRIOR_WINDOW,
)
SUPPORT_DISTANCE_ATR = _definition(
    "support.distance_atr",
    "ATR-normalized close distance from prior low",
    "Latest close minus prior low, divided by canonical Wilder ATR.",
    unit="ATR",
    metadata=_PRIOR_WINDOW,
)


class _Boundary(StrEnum):
    HIGH = "high"
    LOW = "low"


class PriorBoundaryCalculator(A22Calculator):
    """Return one fixed boundary derived from prior bars only."""

    def __init__(self, definition: FeatureDefinition, boundary: _Boundary) -> None:
        self._definition = definition
        self._boundary = boundary

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
        boundary = prior_range(prepared.history.bars[-bars - 1 : -1])
        value = boundary.high if self._boundary is _Boundary.HIGH else boundary.low
        return self._history_result(
            context,
            request,
            prepared,
            value=value,
            lookback_bars_used=bars + 1,
        )


class BoundaryDistanceCalculator(A22Calculator):
    """Return signed percent or ATR distance from one fixed prior boundary."""

    def __init__(
        self,
        definition: FeatureDefinition,
        boundary: _Boundary,
        *,
        atr_normalized: bool,
    ) -> None:
        self._definition = definition
        self._boundary = boundary
        self._atr_normalized = atr_normalized

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        parameter_names = (
            ("atr_period", "bars") if self._atr_normalized else ("bars",)
        )
        self._validate_request(request, parameter_names=parameter_names)
        bars = positive_int_parameter(request, "bars")
        atr_period = (
            positive_int_parameter(request, "atr_period")
            if self._atr_normalized
            else None
        )
        minimum = max(bars + 1, (atr_period or 0) + 1)
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=minimum
        )
        if failure is not None:
            return failure
        assert prepared is not None
        prior = prior_range(prepared.history.bars[-bars - 1 : -1])
        boundary = prior.high if self._boundary is _Boundary.HIGH else prior.low
        latest_close = prepared.history.bars[-1].close
        if boundary <= 0:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=bars + 1,
                warnings=("boundary distance requires a positive prior boundary",),
            )
        if self._atr_normalized:
            assert atr_period is not None
            atr = wilder_atr(prepared.history.bars, atr_period)
            if atr == 0:
                return self._history_result(
                    context,
                    request,
                    prepared,
                    status=FeatureStatus.FAILED,
                    value=None,
                    lookback_bars_used=len(prepared.history.bars),
                    warnings=("ATR-normalized boundary distance requires nonzero ATR",),
                )
            value = (latest_close - boundary) / atr
            lookback = len(prepared.history.bars)
        else:
            try:
                value = signed_distance_percent(latest_close, boundary)
            except ValueError as exc:
                return self._history_result(
                    context,
                    request,
                    prepared,
                    status=FeatureStatus.FAILED,
                    value=None,
                    lookback_bars_used=bars + 1,
                    warnings=(str(exc),),
                )
            lookback = bars + 1
        return self._history_result(
            context,
            request,
            prepared,
            value=value,
            lookback_bars_used=lookback,
        )


SUPPORT_RESISTANCE_FEATURE_DEFINITIONS = (
    PRIOR_HIGH,
    PRIOR_LOW,
    RESISTANCE_DISTANCE_PERCENT,
    SUPPORT_DISTANCE_PERCENT,
    RESISTANCE_DISTANCE_ATR,
    SUPPORT_DISTANCE_ATR,
)

SUPPORT_RESISTANCE_CALCULATORS: tuple[FeatureCalculator, ...] = (
    PriorBoundaryCalculator(PRIOR_HIGH, _Boundary.HIGH),
    PriorBoundaryCalculator(PRIOR_LOW, _Boundary.LOW),
    BoundaryDistanceCalculator(
        RESISTANCE_DISTANCE_PERCENT, _Boundary.HIGH, atr_normalized=False
    ),
    BoundaryDistanceCalculator(
        SUPPORT_DISTANCE_PERCENT, _Boundary.LOW, atr_normalized=False
    ),
    BoundaryDistanceCalculator(
        RESISTANCE_DISTANCE_ATR, _Boundary.HIGH, atr_normalized=True
    ),
    BoundaryDistanceCalculator(
        SUPPORT_DISTANCE_ATR, _Boundary.LOW, atr_normalized=True
    ),
)
