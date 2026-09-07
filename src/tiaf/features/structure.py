"""Deterministic adjacent-bar and rolling-range structure measurements."""

from enum import StrEnum

from tiaf.context import AnalysisContext
from tiaf.features._calculation import A22Calculator, positive_int_parameter
from tiaf.features._trend_calculation import adjacent_structure_counts
from tiaf.features.enums import (
    FeatureCategory,
    FeatureSourceKind,
    FeatureStatus,
    FeatureValueType,
)
from tiaf.features.models import FeatureDefinition, FeatureRequest, FeatureResult
from tiaf.features.registry import FeatureCalculator


def _structure_fraction_definition(
    feature_id: str, name: str, description: str
) -> FeatureDefinition:
    return FeatureDefinition(
        feature_id=feature_id,
        name=name,
        category=FeatureCategory.STRUCTURE,
        description=description,
        value_type=FeatureValueType.FLOAT,
        unit="ratio",
        required_sources=(FeatureSourceKind.HISTORY,),
        minimum_history_bars=2,
        metadata={
            "bars_semantics": "transitions_requires_bars_plus_one",
            "equality_semantics": "neither_strict_direction",
        },
    )


HIGHER_HIGH_FRACTION = _structure_fraction_definition(
    "structure.higher_high_fraction",
    "Higher-high fraction",
    "Fraction of latest exact adjacent comparisons with a strictly higher high.",
)
LOWER_HIGH_FRACTION = _structure_fraction_definition(
    "structure.lower_high_fraction",
    "Lower-high fraction",
    "Fraction of latest exact adjacent comparisons with a strictly lower high.",
)
HIGHER_LOW_FRACTION = _structure_fraction_definition(
    "structure.higher_low_fraction",
    "Higher-low fraction",
    "Fraction of latest exact adjacent comparisons with a strictly higher low.",
)
LOWER_LOW_FRACTION = _structure_fraction_definition(
    "structure.lower_low_fraction",
    "Lower-low fraction",
    "Fraction of latest exact adjacent comparisons with a strictly lower low.",
)
POSITION_IN_ROLLING_RANGE = FeatureDefinition(
    feature_id="structure.position_in_rolling_range",
    name="Position in rolling range",
    category=FeatureCategory.STRUCTURE,
    description="Latest completed close position within the latest exact high-low range.",
    value_type=FeatureValueType.FLOAT,
    unit="%",
    required_sources=(FeatureSourceKind.HISTORY,),
    minimum_history_bars=1,
    metadata={"bars_semantics": "latest_n_bars"},
)


class _StructureKind(StrEnum):
    HIGHER_HIGH = "higher_high"
    LOWER_HIGH = "lower_high"
    HIGHER_LOW = "higher_low"
    LOWER_LOW = "lower_low"


class StructureFractionCalculator(A22Calculator):
    """Calculate one strict adjacent high/low comparison fraction."""

    def __init__(
        self, definition: FeatureDefinition, kind: _StructureKind
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
        window = prepared.history.bars[-bars - 1 :]
        counts = adjacent_structure_counts(window)
        numerator = {
            _StructureKind.HIGHER_HIGH: counts.higher_high,
            _StructureKind.LOWER_HIGH: counts.lower_high,
            _StructureKind.HIGHER_LOW: counts.higher_low,
            _StructureKind.LOWER_LOW: counts.lower_low,
        }[self._kind]
        return self._history_result(
            context,
            request,
            prepared,
            value=numerator / bars,
            lookback_bars_used=bars + 1,
        )


class PositionInRollingRangeCalculator(A22Calculator):
    """Calculate latest completed-close location within an exact bar range."""

    _definition = POSITION_IN_ROLLING_RANGE

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
        rolling_range = rolling_high - rolling_low
        if rolling_range == 0:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.INSUFFICIENT_DATA,
                value=None,
                lookback_bars_used=bars,
                warnings=("rolling-range position is undefined for a flat range",),
            )
        value = ((window[-1].close - rolling_low) / rolling_range) * 100.0
        return self._history_result(
            context,
            request,
            prepared,
            value=value,
            lookback_bars_used=bars,
        )


STRUCTURE_FEATURE_DEFINITIONS = (
    HIGHER_HIGH_FRACTION,
    LOWER_HIGH_FRACTION,
    HIGHER_LOW_FRACTION,
    LOWER_LOW_FRACTION,
    POSITION_IN_ROLLING_RANGE,
)

STRUCTURE_CALCULATORS: tuple[FeatureCalculator, ...] = (
    StructureFractionCalculator(HIGHER_HIGH_FRACTION, _StructureKind.HIGHER_HIGH),
    StructureFractionCalculator(LOWER_HIGH_FRACTION, _StructureKind.LOWER_HIGH),
    StructureFractionCalculator(HIGHER_LOW_FRACTION, _StructureKind.HIGHER_LOW),
    StructureFractionCalculator(LOWER_LOW_FRACTION, _StructureKind.LOWER_LOW),
    PositionInRollingRangeCalculator(),
)
