"""Public provider-neutral deterministic feature foundation."""

from tiaf.features.calculators import (
    AbsoluteReturnCalculator,
    CurrentPriceCalculator,
    HighLowRangePercentCalculator,
    HistoryBarCountCalculator,
    HistoryFirstCloseCalculator,
    HistoryLastCloseCalculator,
    PercentReturnCalculator,
)
from tiaf.features.definitions import BUILTIN_FEATURE_DEFINITIONS
from tiaf.features.engine import DeterministicFeatureEngine, builtin_feature_registry
from tiaf.features.enums import (
    FeatureCategory,
    FeatureSourceKind,
    FeatureStatus,
    FeatureValueType,
)
from tiaf.features.errors import (
    FeatureComputationError,
    FeatureDefinitionError,
    FeatureError,
    FeatureNotRegisteredError,
    FeatureParameterError,
)
from tiaf.features.models import (
    FeatureBundle,
    FeatureDefinition,
    FeatureRequest,
    FeatureResult,
)
from tiaf.features.registry import FeatureCalculator, FeatureRegistry
from tiaf.features.summaries import summarize_feature_bundle

__all__ = [
    "AbsoluteReturnCalculator",
    "BUILTIN_FEATURE_DEFINITIONS",
    "CurrentPriceCalculator",
    "DeterministicFeatureEngine",
    "FeatureBundle",
    "FeatureCalculator",
    "FeatureCategory",
    "FeatureComputationError",
    "FeatureDefinition",
    "FeatureDefinitionError",
    "FeatureError",
    "FeatureNotRegisteredError",
    "FeatureParameterError",
    "FeatureRegistry",
    "FeatureRequest",
    "FeatureResult",
    "FeatureSourceKind",
    "FeatureStatus",
    "FeatureValueType",
    "HighLowRangePercentCalculator",
    "HistoryBarCountCalculator",
    "HistoryFirstCloseCalculator",
    "HistoryLastCloseCalculator",
    "PercentReturnCalculator",
    "builtin_feature_registry",
    "summarize_feature_bundle",
]
