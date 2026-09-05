"""Public provider-neutral market-data foundation."""

from tiaf.data.enums import (
    DataFailureKind,
    InstrumentType,
    MarketSegment,
    ProviderCapability,
    QuoteFieldAvailability,
)
from tiaf.data.errors import (
    InstrumentNotFoundError,
    PartialDataError,
    ProviderAuthError,
    ProviderBadResponseError,
    ProviderError,
    ProviderNetworkError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    StaleDataError,
    TIAFDataError,
    UnsupportedCapabilityError,
)
from tiaf.data.models import (
    HistoricalSeries,
    InstrumentKey,
    InstrumentRecord,
    OHLCVBar,
    QuoteSnapshot,
)
from tiaf.data.normalization import (
    age_seconds,
    classify_freshness,
    normalize_datetime_to_ist,
    normalize_exchange,
    normalize_interval,
    normalize_provider_name,
    normalize_symbol,
)
from tiaf.data.provider import MarketDataProvider

__all__ = [
    "DataFailureKind",
    "HistoricalSeries",
    "InstrumentKey",
    "InstrumentNotFoundError",
    "InstrumentRecord",
    "InstrumentType",
    "MarketDataProvider",
    "MarketSegment",
    "OHLCVBar",
    "PartialDataError",
    "ProviderAuthError",
    "ProviderBadResponseError",
    "ProviderCapability",
    "ProviderError",
    "ProviderNetworkError",
    "ProviderRateLimitError",
    "ProviderTimeoutError",
    "QuoteFieldAvailability",
    "QuoteSnapshot",
    "StaleDataError",
    "TIAFDataError",
    "UnsupportedCapabilityError",
    "age_seconds",
    "classify_freshness",
    "normalize_datetime_to_ist",
    "normalize_exchange",
    "normalize_interval",
    "normalize_provider_name",
    "normalize_symbol",
]
