"""Positive-only close and wick excursions beyond fixed prior boundaries."""

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


def _definition(feature_id: str, name: str, description: str) -> FeatureDefinition:
    metadata: Metadata = {
        "bars_semantics": "previous_n_completed_bars_excluding_latest",
        "no_excursion_value": 0,
    }
    return FeatureDefinition(
        feature_id=feature_id,
        name=name,
        category=FeatureCategory.STRUCTURE,
        description=description,
        value_type=FeatureValueType.FLOAT,
        unit="%",
        required_sources=(FeatureSourceKind.HISTORY,),
        minimum_history_bars=2,
        metadata=metadata,
    )


CLOSE_ABOVE_PRIOR_HIGH = _definition(
    "breakout.above_prior_high_percent",
    "Close excursion above prior high",
    "Positive-only latest-close excursion above the fixed prior high.",
)
CLOSE_BELOW_PRIOR_LOW = _definition(
    "breakdown.below_prior_low_percent",
    "Close excursion below prior low",
    "Positive-only latest-close excursion below the fixed prior low.",
)
HIGH_ABOVE_PRIOR_HIGH = _definition(
    "breakout.high_above_prior_high_percent",
    "High excursion above prior high",
    "Positive-only latest-high excursion above the fixed prior high.",
)
LOW_BELOW_PRIOR_LOW = _definition(
    "breakdown.low_below_prior_low_percent",
    "Low excursion below prior low",
    "Positive-only latest-low excursion below the fixed prior low.",
)


class _ExcursionKind(StrEnum):
    CLOSE_ABOVE = "close_above"
    CLOSE_BELOW = "close_below"
    HIGH_ABOVE = "high_above"
    LOW_BELOW = "low_below"


class BoundaryExcursionCalculator(A22Calculator):
    """Measure an excursion without assigning confirmation or quality."""

    def __init__(
        self, definition: FeatureDefinition, kind: _ExcursionKind
    ) -> None:
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
        history = prepared.history.bars
        boundary = prior_range(history[-bars - 1 : -1])
        latest = history[-1]
        if self._kind in {_ExcursionKind.CLOSE_ABOVE, _ExcursionKind.HIGH_ABOVE}:
            observed = (
                latest.close
                if self._kind is _ExcursionKind.CLOSE_ABOVE
                else latest.high
            )
            reference = boundary.high
            direction = 1.0
        else:
            observed = (
                latest.close
                if self._kind is _ExcursionKind.CLOSE_BELOW
                else latest.low
            )
            reference = boundary.low
            direction = -1.0
        try:
            value = max(0.0, direction * signed_distance_percent(observed, reference))
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
        return self._history_result(
            context,
            request,
            prepared,
            value=value,
            lookback_bars_used=bars + 1,
        )


BREAKOUT_FEATURE_DEFINITIONS = (
    CLOSE_ABOVE_PRIOR_HIGH,
    CLOSE_BELOW_PRIOR_LOW,
    HIGH_ABOVE_PRIOR_HIGH,
    LOW_BELOW_PRIOR_LOW,
)

BREAKOUT_CALCULATORS: tuple[FeatureCalculator, ...] = (
    BoundaryExcursionCalculator(CLOSE_ABOVE_PRIOR_HIGH, _ExcursionKind.CLOSE_ABOVE),
    BoundaryExcursionCalculator(CLOSE_BELOW_PRIOR_LOW, _ExcursionKind.CLOSE_BELOW),
    BoundaryExcursionCalculator(HIGH_ABOVE_PRIOR_HIGH, _ExcursionKind.HIGH_ABOVE),
    BoundaryExcursionCalculator(LOW_BELOW_PRIOR_LOW, _ExcursionKind.LOW_BELOW),
)
