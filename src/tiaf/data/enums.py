"""Provider-neutral market-data enums."""

from enum import StrEnum


class MarketSegment(StrEnum):
    """Normalized exchange and market segment."""

    NSE_EQUITY = "NSE_EQUITY"
    NSE_FNO = "NSE_FNO"
    NSE_INDEX = "NSE_INDEX"
    BSE_EQUITY = "BSE_EQUITY"
    BSE_FNO = "BSE_FNO"
    BSE_INDEX = "BSE_INDEX"
    UNKNOWN = "UNKNOWN"


class InstrumentType(StrEnum):
    """Normalized instrument classification."""

    EQUITY = "EQUITY"
    INDEX = "INDEX"
    FUTURE = "FUTURE"
    CALL_OPTION = "CALL_OPTION"
    PUT_OPTION = "PUT_OPTION"
    UNKNOWN = "UNKNOWN"


class QuoteFieldAvailability(StrEnum):
    """Availability of optional fields in a normalized quote."""

    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"


class ProviderCapability(StrEnum):
    """A factual data capability advertised by a provider."""

    QUOTES = "QUOTES"
    HISTORICAL_OHLCV = "HISTORICAL_OHLCV"
    INSTRUMENT_MASTER = "INSTRUMENT_MASTER"
    DERIVATIVES_METADATA = "DERIVATIVES_METADATA"
    OPTION_CHAIN = "OPTION_CHAIN"
    MARKET_DEPTH = "MARKET_DEPTH"
    FUNDAMENTALS = "FUNDAMENTALS"
    NEWS = "NEWS"


class DataFailureKind(StrEnum):
    """Stable classification for data and provider failures."""

    AUTH = "AUTH"
    RATE_LIMIT = "RATE_LIMIT"
    TIMEOUT = "TIMEOUT"
    NETWORK = "NETWORK"
    BAD_RESPONSE = "BAD_RESPONSE"
    NOT_FOUND = "NOT_FOUND"
    UNSUPPORTED = "UNSUPPORTED"
    STALE = "STALE"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"
