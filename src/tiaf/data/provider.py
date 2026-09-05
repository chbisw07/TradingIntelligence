"""Synchronous provider-neutral market-data interface."""

from datetime import datetime
from typing import Protocol, runtime_checkable

from tiaf.data.enums import ProviderCapability
from tiaf.data.models import HistoricalSeries, InstrumentKey, InstrumentRecord, QuoteSnapshot


@runtime_checkable
class MarketDataProvider(Protocol):
    """Stable interface implemented by future market-data adapters."""

    def provider_name(self) -> str:
        """Return the adapter's normalized provider name."""
        ...

    def capabilities(self) -> frozenset[ProviderCapability]:
        """Return the factual capabilities supported by this adapter."""
        ...

    def get_quote(self, instrument: InstrumentKey) -> QuoteSnapshot:
        """Return one normalized quote or raise a typed provider error."""
        ...

    def get_quotes(
        self,
        instruments: tuple[InstrumentKey, ...],
    ) -> tuple[QuoteSnapshot, ...]:
        """Return normalized quotes, preserving input order where practical."""
        ...

    def get_historical(
        self,
        instrument: InstrumentKey,
        interval: str,
        start_at: datetime,
        end_at: datetime,
    ) -> HistoricalSeries:
        """Return a normalized historical series for the requested window."""
        ...

    def search_instruments(self, query: str) -> tuple[InstrumentRecord, ...]:
        """Search the provider's instrument master and return normalized records."""
        ...
