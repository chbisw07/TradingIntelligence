"""Mocked Dhan full-quote adapter tests."""

from collections.abc import Mapping
from typing import Any

import pytest

from tiaf.contracts import DataQuality
from tiaf.data import (
    InstrumentNotFoundError,
    MarketDataProvider,
    MarketSegment,
    ProviderBadResponseError,
    ProviderCapability,
    QuoteFieldAvailability,
    QuoteSnapshot,
)
from tiaf.data.providers.dhan import DhanMarketDataProvider

from ._support import (
    FIXED_NOW,
    RecordingTransport,
    call_option,
    dhan_config,
    equity,
    quote_entry,
    quote_response,
)


def provider_with(transport: RecordingTransport) -> DhanMarketDataProvider:
    return DhanMarketDataProvider(
        dhan_config(),
        transport=transport,
        clock=lambda: FIXED_NOW,
    )


def test_single_equity_quote_normalization() -> None:
    transport = RecordingTransport(lambda path, payload: quote_response(payload))
    provider = provider_with(transport)

    snapshot = provider.get_quote(equity())

    assert snapshot.ltp == 1333
    assert snapshot.previous_close == 2985
    assert snapshot.source_provider == "dhan"
    assert snapshot.availability is QuoteFieldAvailability.AVAILABLE
    assert snapshot.quality is DataQuality.GOOD
    assert snapshot.metadata["observed_at_source"] == "last_trade_time"
    assert transport.calls[0][0] == "/marketfeed/quote"


def test_single_fno_quote_normalizes_open_interest() -> None:
    transport = RecordingTransport(
        lambda path, payload: quote_response(payload, include_oi=True)
    )
    snapshot = provider_with(transport).get_quote(call_option())

    assert snapshot.open_interest == 500
    assert snapshot.availability is QuoteFieldAvailability.AVAILABLE


def test_missing_depth_does_not_fabricate_bid_or_ask() -> None:
    transport = RecordingTransport(
        lambda path, payload: quote_response(payload, include_depth=False)
    )
    snapshot = provider_with(transport).get_quote(equity())

    assert snapshot.bid is None
    assert snapshot.ask is None
    assert snapshot.availability is QuoteFieldAvailability.PARTIAL
    assert snapshot.quality is DataQuality.PARTIAL


def test_market_depth_extracts_best_positive_bid_and_ask() -> None:
    transport = RecordingTransport(lambda path, payload: quote_response(payload))
    snapshot = provider_with(transport).get_quote(equity())

    assert snapshot.bid == 3010
    assert snapshot.ask == 3011


def test_batch_groups_segments_in_one_request() -> None:
    transport = RecordingTransport(lambda path, payload: quote_response(payload))
    instruments = (
        equity("RELIANCE", "1333"),
        equity("BSECO", "500001", segment=MarketSegment.BSE_EQUITY),
    )

    provider_with(transport).get_quotes(instruments)

    assert transport.calls == [
        (
            "/marketfeed/quote",
            {"NSE_EQ": [1333], "BSE_EQ": [500001]},
        )
    ]


def test_batch_preserves_caller_order_even_if_response_order_differs() -> None:
    transport = RecordingTransport(lambda path, payload: quote_response(payload))
    instruments = (
        equity("THREE", "3"),
        equity("ONE", "1"),
        equity("TWO", "2"),
    )

    snapshots = provider_with(transport).get_quotes(instruments)

    assert tuple(snapshot.instrument for snapshot in snapshots) == instruments
    assert tuple(snapshot.ltp for snapshot in snapshots) == (3, 1, 2)


def test_quote_requests_over_1000_are_chunked_without_sleeping() -> None:
    transport = RecordingTransport(lambda path, payload: quote_response(payload))
    instruments = tuple(equity(f"SYM{index}", str(index)) for index in range(1, 1002))

    snapshots = provider_with(transport).get_quotes(instruments)

    assert len(transport.calls) == 2
    assert len(transport.calls[0][1]["NSE_EQ"]) == 1000
    assert transport.calls[1][1]["NSE_EQ"] == [1001]
    assert len(snapshots) == 1001


def test_missing_requested_instrument_raises_instead_of_dropping() -> None:
    def missing_one(path: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        del path, payload
        return {
            "status": "success",
            "data": {"NSE_EQ": {"1": quote_entry(last_price=1)}},
        }

    transport = RecordingTransport(missing_one)

    with pytest.raises(InstrumentNotFoundError, match="omitted securityId 2"):
        provider_with(transport).get_quotes((equity("ONE", "1"), equity("TWO", "2")))


@pytest.mark.parametrize(
    "response",
    [
        {},
        {"status": "success", "data": []},
        {"status": "success", "data": {"NSE_EQ": {"1333": {}}}},
    ],
)
def test_malformed_quote_response_is_typed(response: dict[str, Any]) -> None:
    transport = RecordingTransport(lambda path, payload: response)

    with pytest.raises(ProviderBadResponseError):
        provider_with(transport).get_quote(equity())


def test_missing_or_invalid_security_id_is_typed_not_found() -> None:
    transport = RecordingTransport(lambda path, payload: quote_response(payload))

    with pytest.raises(InstrumentNotFoundError, match="securityId"):
        provider_with(transport).get_quote(equity(security_id="missing"))

    assert transport.calls == []


def test_capabilities_and_provider_protocol_are_accurate() -> None:
    provider = provider_with(RecordingTransport(lambda path, payload: quote_response(payload)))

    assert isinstance(provider, MarketDataProvider)
    assert provider.capabilities() == frozenset(
        {
            ProviderCapability.QUOTES,
            ProviderCapability.HISTORICAL_OHLCV,
            ProviderCapability.DERIVATIVES_METADATA,
            ProviderCapability.OPTION_CHAIN,
        }
    )
    assert ProviderCapability.INSTRUMENT_MASTER not in provider.capabilities()


def test_returned_quote_serializes_and_round_trips() -> None:
    transport = RecordingTransport(lambda path, payload: quote_response(payload))
    snapshot = provider_with(transport).get_quote(equity())

    restored = QuoteSnapshot.model_validate_json(snapshot.model_dump_json())

    assert restored == snapshot
    assert snapshot.model_dump(mode="json")["observed_at"].endswith("+05:30")
