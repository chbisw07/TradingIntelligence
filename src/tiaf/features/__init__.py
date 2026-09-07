"""Public provider-neutral deterministic feature foundation."""

from tiaf.features.breakout import BREAKOUT_FEATURE_DEFINITIONS
from tiaf.features.calculators import (
    AbsoluteReturnCalculator,
    CurrentPriceCalculator,
    HighLowRangePercentCalculator,
    HistoryBarCountCalculator,
    HistoryFirstCloseCalculator,
    HistoryLastCloseCalculator,
    PercentReturnCalculator,
)
from tiaf.features.compression import COMPRESSION_FEATURE_DEFINITIONS
from tiaf.features.definitions import BUILTIN_FEATURE_DEFINITIONS
from tiaf.features.derivatives import DERIVATIVES_FEATURE_DEFINITIONS
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
from tiaf.features.multi_timeframe import (
    MULTI_TIMEFRAME_FEATURE_DEFINITIONS,
    MultiTimeframeContext,
    MultiTimeframeFeatureEngine,
    TimeframeFeatureContext,
    multi_timeframe_context,
    timeframe_feature_context,
)
from tiaf.features.participation import PARTICIPATION_FEATURE_DEFINITIONS
from tiaf.features.price import PRICE_FEATURE_DEFINITIONS
from tiaf.features.registry import FeatureCalculator, FeatureRegistry
from tiaf.features.relative import (
    RELATIVE_FEATURE_DEFINITIONS,
    BenchmarkReference,
    BenchmarkRole,
    RelativeStrengthContext,
    RelativeStrengthEngine,
    relative_strength_context,
)
from tiaf.features.returns import RETURN_FEATURE_DEFINITIONS, LogReturnCalculator
from tiaf.features.structure import STRUCTURE_FEATURE_DEFINITIONS
from tiaf.features.summaries import summarize_feature_bundle
from tiaf.features.support_resistance import SUPPORT_RESISTANCE_FEATURE_DEFINITIONS
from tiaf.features.trend import TREND_FEATURE_DEFINITIONS
from tiaf.features.volatility import (
    VOLATILITY_FEATURE_DEFINITIONS,
    MoveOverAtrCalculator,
    RealizedVolatilityCalculator,
)
from tiaf.features.volume import VOLUME_FEATURE_DEFINITIONS

__all__ = [
    "AbsoluteReturnCalculator",
    "BREAKOUT_FEATURE_DEFINITIONS",
    "BenchmarkReference",
    "BenchmarkRole",
    "BUILTIN_FEATURE_DEFINITIONS",
    "CurrentPriceCalculator",
    "COMPRESSION_FEATURE_DEFINITIONS",
    "DeterministicFeatureEngine",
    "DERIVATIVES_FEATURE_DEFINITIONS",
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
    "MULTI_TIMEFRAME_FEATURE_DEFINITIONS",
    "MultiTimeframeContext",
    "MultiTimeframeFeatureEngine",
    "PercentReturnCalculator",
    "PARTICIPATION_FEATURE_DEFINITIONS",
    "PRICE_FEATURE_DEFINITIONS",
    "RELATIVE_FEATURE_DEFINITIONS",
    "RETURN_FEATURE_DEFINITIONS",
    "RelativeStrengthContext",
    "RelativeStrengthEngine",
    "STRUCTURE_FEATURE_DEFINITIONS",
    "SUPPORT_RESISTANCE_FEATURE_DEFINITIONS",
    "TREND_FEATURE_DEFINITIONS",
    "TimeframeFeatureContext",
    "LogReturnCalculator",
    "MoveOverAtrCalculator",
    "RealizedVolatilityCalculator",
    "VOLATILITY_FEATURE_DEFINITIONS",
    "VOLUME_FEATURE_DEFINITIONS",
    "builtin_feature_registry",
    "multi_timeframe_context",
    "relative_strength_context",
    "timeframe_feature_context",
    "summarize_feature_bundle",
]
