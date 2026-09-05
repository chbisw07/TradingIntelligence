"""Tests for the public Dhan adapter package."""

import tiaf.data.providers as providers
import tiaf.data.providers.dhan as dhan


def test_dhan_provider_exports_are_available() -> None:
    assert providers.DhanMarketDataProvider is dhan.DhanMarketDataProvider
    assert {
        "DhanConfig",
        "DhanIdentityMismatchError",
        "DhanInstrumentResolver",
        "DhanInstrumentType",
        "DhanMarketDataProvider",
        "DhanTransport",
        "HttpxDhanTransport",
        "plan_rolling_option_chunks",
        "resolve_dhan_diagnostic_instrument",
        "to_dhan_instrument_type",
        "to_dhan_segment",
    } <= set(dhan.__all__)
