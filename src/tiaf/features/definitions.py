"""Stable A2.1 built-in feature definitions."""

from tiaf.features.enums import (
    FeatureCategory,
    FeatureSourceKind,
    FeatureValueType,
)
from tiaf.features.models import FeatureDefinition

CURRENT_PRICE = FeatureDefinition(
    feature_id="price.current",
    name="Current price",
    category=FeatureCategory.PRICE,
    description="Normalized quote last-traded price from the source context.",
    value_type=FeatureValueType.FLOAT,
    unit="price",
    required_sources=(FeatureSourceKind.QUOTE,),
)

HISTORY_BAR_COUNT = FeatureDefinition(
    feature_id="history.bar_count",
    name="History bar count",
    category=FeatureCategory.META,
    description="Number of chronological bars in the requested historical series.",
    value_type=FeatureValueType.INTEGER,
    unit="bars",
    required_sources=(FeatureSourceKind.HISTORY,),
    minimum_history_bars=0,
)

HISTORY_FIRST_CLOSE = FeatureDefinition(
    feature_id="history.first_close",
    name="History first close",
    category=FeatureCategory.PRICE,
    description="Close of the earliest bar in the supplied historical series.",
    value_type=FeatureValueType.FLOAT,
    unit="price",
    required_sources=(FeatureSourceKind.HISTORY,),
    minimum_history_bars=1,
)

HISTORY_LAST_CLOSE = FeatureDefinition(
    feature_id="history.last_close",
    name="History last close",
    category=FeatureCategory.PRICE,
    description="Close of the latest bar in the supplied historical series.",
    value_type=FeatureValueType.FLOAT,
    unit="price",
    required_sources=(FeatureSourceKind.HISTORY,),
    minimum_history_bars=1,
)

ABSOLUTE_RETURN = FeatureDefinition(
    feature_id="return.absolute",
    name="Absolute return",
    category=FeatureCategory.RETURN,
    description="Latest close minus the close the requested intervals earlier.",
    value_type=FeatureValueType.FLOAT,
    unit="price",
    required_sources=(FeatureSourceKind.HISTORY,),
    minimum_history_bars=2,
    metadata={"bars_semantics": "intervals_back_requires_bars_plus_one"},
)

PERCENT_RETURN = FeatureDefinition(
    feature_id="return.percent",
    name="Percentage return",
    category=FeatureCategory.RETURN,
    description="Percentage change from the close N intervals earlier to latest close.",
    value_type=FeatureValueType.FLOAT,
    unit="%",
    required_sources=(FeatureSourceKind.HISTORY,),
    minimum_history_bars=2,
    metadata={"bars_semantics": "intervals_back_requires_bars_plus_one"},
)

HIGH_LOW_RANGE_PERCENT = FeatureDefinition(
    feature_id="range.high_low_percent",
    name="High-low range percentage",
    category=FeatureCategory.STRUCTURE,
    description="Latest N-bar high-low range divided by the latest close.",
    value_type=FeatureValueType.FLOAT,
    unit="%",
    required_sources=(FeatureSourceKind.HISTORY,),
    minimum_history_bars=1,
    metadata={"denominator": "latest_close", "bars_semantics": "latest_n_bars"},
)

BUILTIN_FEATURE_DEFINITIONS = (
    CURRENT_PRICE,
    HISTORY_BAR_COUNT,
    HISTORY_FIRST_CLOSE,
    HISTORY_LAST_CLOSE,
    ABSOLUTE_RETURN,
    PERCENT_RETURN,
    HIGH_LOW_RANGE_PERCENT,
)
