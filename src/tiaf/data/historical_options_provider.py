"""Segregated provider-neutral historical-options interface."""

from datetime import date
from typing import Protocol, runtime_checkable

from tiaf.contracts import OptionType
from tiaf.data.enums import ProviderCapability
from tiaf.data.historical_options import (
    ExpiryFlag,
    HistoricalOptionExpiryCode,
    HistoricalOptionSeries,
    RelativeStrike,
)
from tiaf.data.models import InstrumentKey


@runtime_checkable
class HistoricalOptionsDataProvider(Protocol):
    """Read-only rolling historical-options data interface."""

    def provider_name(self) -> str:
        """Return the adapter's normalized provider name."""
        ...

    def capabilities(self) -> frozenset[ProviderCapability]:
        """Return the factual capabilities supported by this adapter."""
        ...

    def get_historical_options(
        self,
        underlying: InstrumentKey,
        interval: str,
        expiry_flag: ExpiryFlag,
        expiry_code: HistoricalOptionExpiryCode | int,
        relative_strike: RelativeStrike,
        option_type: OptionType,
        start_date: date,
        end_date: date,
    ) -> HistoricalOptionSeries:
        """Return factual rolling option history for a half-open date range."""
        ...
