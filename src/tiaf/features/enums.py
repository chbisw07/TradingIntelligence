"""Provider-neutral deterministic feature classifications."""

from enum import StrEnum


class FeatureStatus(StrEnum):
    """Availability state of one deterministic feature result."""

    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    FAILED = "FAILED"


class FeatureValueType(StrEnum):
    """Public representation of a feature value."""

    FLOAT = "FLOAT"
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    CATEGORY = "CATEGORY"
    LEVEL = "LEVEL"
    SERIES = "SERIES"


class FeatureSourceKind(StrEnum):
    """Provider-neutral factual input category required by a feature."""

    QUOTE = "QUOTE"
    HISTORY = "HISTORY"
    OPTION_CHAIN = "OPTION_CHAIN"
    HISTORICAL_OPTIONS = "HISTORICAL_OPTIONS"
    CONTEXT = "CONTEXT"
    DERIVED = "DERIVED"


class FeatureCategory(StrEnum):
    """Descriptive feature family without directional judgment."""

    PRICE = "PRICE"
    RETURN = "RETURN"
    TREND = "TREND"
    VOLATILITY = "VOLATILITY"
    VOLUME = "VOLUME"
    STRUCTURE = "STRUCTURE"
    DERIVATIVES = "DERIVATIVES"
    LIQUIDITY = "LIQUIDITY"
    RELATIVE = "RELATIVE"
    META = "META"
