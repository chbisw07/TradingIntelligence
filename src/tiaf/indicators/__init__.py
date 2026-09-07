"""Public first-class deterministic indicator framework."""

from tiaf.indicators.definitions import BUILTIN_INDICATOR_DEFINITIONS
from tiaf.indicators.engine import IndicatorEngine
from tiaf.indicators.enums import (
    IndicatorParameterType,
    IndicatorStatus,
    SuperTrendBand,
    SuperTrendRelation,
)
from tiaf.indicators.errors import (
    IndicatorComputationError,
    IndicatorDefinitionError,
    IndicatorError,
    IndicatorNotRegisteredError,
    IndicatorParameterError,
)
from tiaf.indicators.library import BUILTIN_INDICATOR_CALCULATORS
from tiaf.indicators.models import (
    IndicatorBundle,
    IndicatorDefinition,
    IndicatorOutputDefinition,
    IndicatorParameterDefinition,
    IndicatorRequest,
    IndicatorResult,
    IndicatorState,
    IndicatorStateDefinition,
    IndicatorValue,
)
from tiaf.indicators.registry import IndicatorCalculator, IndicatorRegistry
from tiaf.indicators.summaries import summarize_indicator_bundle


def builtin_indicator_registry() -> IndicatorRegistry:
    """Create the explicitly populated initial indicator registry."""
    return IndicatorRegistry(BUILTIN_INDICATOR_CALCULATORS)


__all__ = [
    "BUILTIN_INDICATOR_DEFINITIONS",
    "IndicatorBundle",
    "IndicatorCalculator",
    "IndicatorComputationError",
    "IndicatorDefinition",
    "IndicatorDefinitionError",
    "IndicatorEngine",
    "IndicatorError",
    "IndicatorNotRegisteredError",
    "IndicatorOutputDefinition",
    "IndicatorParameterDefinition",
    "IndicatorParameterError",
    "IndicatorParameterType",
    "IndicatorRegistry",
    "IndicatorRequest",
    "IndicatorResult",
    "IndicatorState",
    "IndicatorStateDefinition",
    "IndicatorStatus",
    "IndicatorValue",
    "SuperTrendBand",
    "SuperTrendRelation",
    "builtin_indicator_registry",
    "summarize_indicator_bundle",
]
