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
from tiaf.features.price import PRICE_FEATURE_DEFINITIONS
from tiaf.features.registry import FeatureCalculator, FeatureRegistry
from tiaf.features.returns import RETURN_FEATURE_DEFINITIONS, LogReturnCalculator
from tiaf.features.structure import STRUCTURE_FEATURE_DEFINITIONS
from tiaf.features.summaries import summarize_feature_bundle
from tiaf.features.trend import TREND_FEATURE_DEFINITIONS
from tiaf.features.volatility import (
    VOLATILITY_FEATURE_DEFINITIONS,
    MoveOverAtrCalculator,
    RealizedVolatilityCalculator,
)

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
    "PRICE_FEATURE_DEFINITIONS",
    "RETURN_FEATURE_DEFINITIONS",
    "STRUCTURE_FEATURE_DEFINITIONS",
    "TREND_FEATURE_DEFINITIONS",
    "LogReturnCalculator",
    "MoveOverAtrCalculator",
    "RealizedVolatilityCalculator",
    "VOLATILITY_FEATURE_DEFINITIONS",
    "builtin_feature_registry",
    "summarize_feature_bundle",
]
