"""Tests for the public data-package surface."""

import tiaf.data as data


def test_expected_data_foundation_symbols_are_public() -> None:
    expected = {
        "DerivativesDataProvider",
        "ExpiryListSnapshot",
        "HistoricalSeries",
        "HistoricalOptionBar",
        "HistoricalOptionExpiryCode",
        "HistoricalOptionSeries",
        "HistoricalOptionsDataProvider",
        "InstrumentKey",
        "InstrumentMasterParseError",
        "InstrumentQuery",
        "InstrumentRecord",
        "InstrumentResolver",
        "MarketDataProvider",
        "OHLCVBar",
        "OptionChainSnapshot",
        "OptionGreeks",
        "OptionMarketSnapshot",
        "OptionStrikeSnapshot",
        "ProviderCapability",
        "QuoteSnapshot",
        "RelativeStrike",
        "ResolutionResult",
        "ResolutionPolicy",
        "ResolvedInstrument",
        "TIAFDataError",
        "UnsupportedCapabilityError",
        "age_seconds",
        "classify_freshness",
        "normalize_datetime_to_ist",
        "normalize_interval",
    }

    assert expected <= set(data.__all__)
    assert all(getattr(data, name) is not None for name in expected)
