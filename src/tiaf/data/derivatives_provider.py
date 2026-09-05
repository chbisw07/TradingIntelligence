"""Segregated provider-neutral interface for live derivatives data."""

from datetime import date
from typing import Protocol, runtime_checkable

from tiaf.data.derivatives import ExpiryListSnapshot, OptionChainSnapshot
from tiaf.data.enums import ProviderCapability
from tiaf.data.models import InstrumentKey


@runtime_checkable
class DerivativesDataProvider(Protocol):
    """Read-only expiry discovery and complete option-chain interface."""

    def provider_name(self) -> str:
        """Return the adapter's normalized provider name."""
        ...

    def capabilities(self) -> frozenset[ProviderCapability]:
        """Return the factual capabilities supported by this adapter."""
        ...

    def get_option_expiries(self, underlying: InstrumentKey) -> ExpiryListSnapshot:
        """Return active expiries for an explicitly identified underlying."""
        ...

    def get_option_chain(self, underlying: InstrumentKey, expiry: date) -> OptionChainSnapshot:
        """Return a normalized live chain for one underlying and expiry."""
        ...
