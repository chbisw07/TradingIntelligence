"""Stable string enums shared by TIAF domain contracts."""

from enum import StrEnum


class TradeStyle(StrEnum):
    """Requested trading cadence."""

    DAY = "DAY"
    POSITIONAL = "POSITIONAL"


class DirectionPolicy(StrEnum):
    """Option directions allowed for an opportunity request."""

    CE = "CE"
    PE = "PE"
    BOTH = "BOTH"


class TradeDirection(StrEnum):
    """Directional market stance."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class OpportunityAction(StrEnum):
    """Action associated with an opportunity assessment."""

    ENTER = "ENTER"
    WAIT = "WAIT"
    NO_TRADE = "NO_TRADE"


class PositionAction(StrEnum):
    """Forward-looking position-management action."""

    HOLD = "HOLD"
    WATCH_CLOSELY = "WATCH_CLOSELY"
    PROTECT = "PROTECT"
    PARTIAL_BOOK = "PARTIAL_BOOK"
    BOOK = "BOOK"
    EXIT = "EXIT"


class ActionStrength(StrEnum):
    """Urgency or conviction of a position action."""

    MILD = "MILD"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    URGENT = "URGENT"


class FreshnessState(StrEnum):
    """Freshness classification for evidence or decisions."""

    FRESH = "FRESH"
    AGING = "AGING"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class EvidenceType(StrEnum):
    """Semantic category of an evidence item."""

    MARKET = "MARKET"
    TECHNICAL = "TECHNICAL"
    VOLUME = "VOLUME"
    RELATIVE_STRENGTH = "RELATIVE_STRENGTH"
    SECTOR = "SECTOR"
    FUNDAMENTAL = "FUNDAMENTAL"
    NEWS = "NEWS"
    MACRO = "MACRO"
    VOLATILITY = "VOLATILITY"
    DERIVATIVES = "DERIVATIVES"
    RISK = "RISK"
    OTHER = "OTHER"


class EvidenceSource(StrEnum):
    """Origin category of an evidence item."""

    USER = "USER"
    DHAN = "DHAN"
    ZERODHA = "ZERODHA"
    WEB = "WEB"
    DERIVED = "DERIVED"
    THIRD_PARTY = "THIRD_PARTY"
    INTERNAL = "INTERNAL"


class ConfidenceBand(StrEnum):
    """Human-readable confidence classification."""

    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class DataQuality(StrEnum):
    """Completeness and usability of a data snapshot."""

    GOOD = "GOOD"
    PARTIAL = "PARTIAL"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


class OptionType(StrEnum):
    """Exchange option type."""

    CE = "CE"
    PE = "PE"
