"""Provider-neutral classifications for deterministic indicators."""

from enum import StrEnum

from tiaf.features.enums import FeatureStatus

# Indicator availability has exactly the accepted feature-result meaning.
IndicatorStatus = FeatureStatus


class IndicatorParameterType(StrEnum):
    """Supported public parameter scalar types."""

    INTEGER = "INTEGER"
    FLOAT = "FLOAT"


class SuperTrendRelation(StrEnum):
    """Latest completed close location relative to the SuperTrend line."""

    ABOVE_LINE = "ABOVE_LINE"
    BELOW_LINE = "BELOW_LINE"
    ON_LINE = "ON_LINE"


class SuperTrendBand(StrEnum):
    """Band supplying the latest SuperTrend line."""

    UPPER_BAND_ACTIVE = "UPPER_BAND_ACTIVE"
    LOWER_BAND_ACTIVE = "LOWER_BAND_ACTIVE"
