"""Stable provider-neutral sector and macro evidence vocabulary."""

from enum import StrEnum


class ContextObservationKind(StrEnum):
    """Whether an observation describes a persistent state or a discrete event."""

    STATE = "STATE"
    EVENT = "EVENT"


class SectorEvidenceFamily(StrEnum):
    IDENTITY = "IDENTITY"
    ABSOLUTE_TREND = "ABSOLUTE_TREND"
    RELATIVE_TREND = "RELATIVE_TREND"
    BREADTH = "BREADTH"
    PARTICIPATION = "PARTICIPATION"
    VOLATILITY = "VOLATILITY"
    SUBJECT_RELATIVE = "SUBJECT_RELATIVE"
    EVENT = "EVENT"


class MacroEvidenceFamily(StrEnum):
    MARKET_INDEX = "MARKET_INDEX"
    VOLATILITY = "VOLATILITY"
    INTEREST_RATES = "INTEREST_RATES"
    BOND_YIELDS = "BOND_YIELDS"
    INFLATION = "INFLATION"
    CURRENCY = "CURRENCY"
    COMMODITIES = "COMMODITIES"
    CENTRAL_BANK = "CENTRAL_BANK"
    FISCAL_POLICY = "FISCAL_POLICY"
    LIQUIDITY = "LIQUIDITY"
    ECONOMIC_GROWTH = "ECONOMIC_GROWTH"
    GEOPOLITICAL = "GEOPOLITICAL"
    GLOBAL_RISK = "GLOBAL_RISK"
    OTHER = "OTHER"


class MappingQuality(StrEnum):
    VERIFIED = "VERIFIED"
    DECLARED = "DECLARED"
    AMBIGUOUS = "AMBIGUOUS"
    UNKNOWN = "UNKNOWN"


class SensitivityDirection(StrEnum):
    """Explicit subject response to a rise in the named macro driver."""

    BENEFITS_FROM_RISE = "BENEFITS_FROM_RISE"
    HARMED_BY_RISE = "HARMED_BY_RISE"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"
