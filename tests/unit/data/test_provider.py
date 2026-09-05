"""Tests for the synchronous provider protocol shape."""

from datetime import UTC, datetime

import pytest

from tiaf.contracts import DataQuality, FreshnessState
from tiaf.data import (
    HistoricalSeries,
    InstrumentKey,
    InstrumentRecord,
    InstrumentType,
    MarketDataProvider,
    MarketSegment,
    ProviderCapability,
    QuoteFieldAvailability,
    QuoteSnapshot,
    UnsupportedCapabilityError,
)

NOW = datetime(2026, 9, 5, 4, 30, tzinfo=UTC)


class FakeQuoteProvider:
    """Small deterministic provider used only to verify protocol semantics."""

    def provider_name(self) -> str:
        return "fake"

    def capabilities(self) -> frozenset[ProviderCapability]:
        return frozenset({ProviderCapability.QUOTES})

    def get_quote(self, instrument: InstrumentKey) -> QuoteSnapshot:
        return QuoteSnapshot(
            instrument=instrument,
            ltp=100,
            observed_at=NOW,
            received_at=NOW,
            source_provider=self.provider_name(),
            freshness=FreshnessState.FRESH,
            quality=DataQuality.GOOD,
            availability=QuoteFieldAvailability.PARTIAL,
        )

    def get_quotes(
        self,
        instruments: tuple[InstrumentKey, ...],
    ) -> tuple[QuoteSnapshot, ...]:
        return tuple(self.get_quote(instrument) for instrument in instruments)

    def get_historical(
        self,
        instrument: InstrumentKey,
        interval: str,
        start_at: datetime,
        end_at: datetime,
    ) -> HistoricalSeries:
        del instrument, interval, start_at, end_at
        raise UnsupportedCapabilityError(
            ProviderCapability.HISTORICAL_OHLCV,
            provider=self.provider_name(),
        )

    def search_instruments(self, query: str) -> tuple[InstrumentRecord, ...]:
        del query
        raise UnsupportedCapabilityError(
            ProviderCapability.INSTRUMENT_MASTER,
            provider=self.provider_name(),
        )


def equity(symbol: str) -> InstrumentKey:
    return InstrumentKey(
        symbol=symbol,
        exchange="NSE",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
    )


def test_fake_provider_satisfies_protocol_and_preserves_batch_order() -> None:
    provider = FakeQuoteProvider()
    instruments = (equity("RELIANCE"), equity("TCS"))

    assert isinstance(provider, MarketDataProvider)
    assert provider.capabilities() == frozenset({ProviderCapability.QUOTES})
    assert tuple(quote.instrument for quote in provider.get_quotes(instruments)) == instruments


def test_unsupported_provider_capability_raises_typed_error() -> None:
    provider = FakeQuoteProvider()

    with pytest.raises(UnsupportedCapabilityError) as captured:
        provider.get_historical(equity("RELIANCE"), "1m", NOW, NOW)

    assert captured.value.capability is ProviderCapability.HISTORICAL_OHLCV
