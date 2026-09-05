"""Tests for provider-neutral data enum stability."""

import json

from tiaf.data import (
    DataFailureKind,
    InstrumentType,
    MarketSegment,
    ProviderCapability,
    QuoteFieldAvailability,
)


def test_data_enums_serialize_as_explicit_strings() -> None:
    values = [
        MarketSegment.NSE_FNO,
        InstrumentType.CALL_OPTION,
        QuoteFieldAvailability.PARTIAL,
        ProviderCapability.HISTORICAL_OHLCV,
        DataFailureKind.RATE_LIMIT,
    ]

    assert json.loads(json.dumps(values)) == [value.value for value in values]
