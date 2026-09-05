"""Mocked Dhan expiry-list and complete option-chain tests."""

from datetime import date
from typing import Any

import pytest

from tiaf.contracts import DataQuality, OptionType
from tiaf.data import (
    DerivativesDataProvider,
    InstrumentNotFoundError,
    MarketSegment,
    ProviderBadResponseError,
    ProviderCapability,
    UnsupportedCapabilityError,
)
from tiaf.data.providers.dhan import DhanMarketDataProvider

from ._support import (
    FIXED_NOW,
    OPTION_EXPIRY,
    RecordingTransport,
    dhan_config,
    equity,
    index,
    option_chain_response,
    option_side,
)


def provider_returning(
    response: dict[str, Any],
) -> tuple[DhanMarketDataProvider, RecordingTransport]:
    transport = RecordingTransport(lambda path, body: response)
    provider = DhanMarketDataProvider(
        dhan_config(),
        transport=transport,
        clock=lambda: FIXED_NOW,
    )
    return provider, transport


def test_provider_advertises_derivatives_and_satisfies_segregated_protocol() -> None:
    provider, _ = provider_returning({})
    assert isinstance(provider, DerivativesDataProvider)
    assert provider.capabilities() == frozenset(
        {
            ProviderCapability.QUOTES,
            ProviderCapability.HISTORICAL_OHLCV,
            ProviderCapability.DERIVATIVES_METADATA,
            ProviderCapability.OPTION_CHAIN,
            ProviderCapability.HISTORICAL_OPTIONS,
        }
    )


@pytest.mark.parametrize(
    ("underlying", "expected_segment"),
    [(equity(), "NSE_EQ"), (index(), "IDX_I")],
)
def test_expiry_request_mapping_and_iso_parsing(underlying: Any, expected_segment: str) -> None:
    provider, transport = provider_returning(
        {"status": "success", "data": ["2026-10-01", "2026-09-24"]}
    )
    result = provider.get_option_expiries(underlying)
    assert transport.calls == [
        (
            "/optionchain/expirylist",
            {
                "UnderlyingScrip": int(underlying.provider_instrument_id),
                "UnderlyingSeg": expected_segment,
            },
        )
    ]
    assert result.expiries == (date(2026, 9, 24), date(2026, 10, 1))
    assert result.observed_at == result.received_at
    assert result.observed_at.isoformat().endswith("+05:30")


@pytest.mark.parametrize(
    "response",
    [
        {"status": "failure", "data": []},
        {"status": "success", "data": "2026-09-24"},
        {"status": "success", "data": []},
        {"status": "success", "data": ["24-09-2026"]},
        {"status": "success", "data": ["2026-09-24", "2026-09-24"]},
    ],
)
def test_malformed_expiry_response_is_rejected(response: dict[str, Any]) -> None:
    provider, _ = provider_returning(response)
    with pytest.raises(ProviderBadResponseError):
        provider.get_option_expiries(equity())


def test_option_chain_request_body_and_full_normalization() -> None:
    provider, transport = provider_returning(option_chain_response())
    chain = provider.get_option_chain(equity(), OPTION_EXPIRY)

    assert transport.calls == [
        (
            "/optionchain",
            {
                "UnderlyingScrip": 1333,
                "UnderlyingSeg": "NSE_EQ",
                "Expiry": "2026-09-24",
            },
        )
    ]
    assert chain.underlying_ltp == 3005.5
    assert chain.expiry == OPTION_EXPIRY
    assert chain.observed_at == chain.received_at
    assert chain.quality is DataQuality.GOOD
    strike = chain.strikes[0]
    assert strike.call is not None and strike.put is not None
    call = strike.call
    assert call.option_type is OptionType.CE
    assert call.security_id == "49081"
    assert call.instrument.provider_instrument_id == "49081"
    assert call.instrument.provider_instrument_id != chain.underlying.provider_instrument_id
    assert call.instrument.trading_symbol is None
    assert call.ltp == 146.99
    assert call.previous_close == 141.5
    assert call.average_price == 140.25
    assert call.open_interest == 123456
    assert call.previous_open_interest == 120000
    assert call.volume == 55000
    assert call.previous_volume == 50000
    assert call.implied_volatility == 18.5
    assert call.greeks.model_dump(exclude={"schema_version"}) == {
        "delta": 0.53871,
        "gamma": 0.0012,
        "theta": -12.4,
        "vega": 8.7,
    }
    assert (call.bid, call.bid_quantity, call.ask, call.ask_quantity) == (
        146.8,
        75,
        147.2,
        100,
    )


@pytest.mark.parametrize(("key", "expected_side"), [("ce", "call"), ("pe", "put")])
def test_one_sided_strikes_are_accepted(key: str, expected_side: str) -> None:
    provider, _ = provider_returning(
        option_chain_response(strikes={"3000": {key: option_side()}})
    )
    strike = provider.get_option_chain(equity(), OPTION_EXPIRY).strikes[0]
    assert getattr(strike, expected_side) is not None
    assert (strike.call is None) is (key == "pe")
    assert (strike.put is None) is (key == "ce")


def test_missing_greek_and_depth_produce_partial_data() -> None:
    value = option_side()
    del value["top_bid_price"]
    del value["top_bid_quantity"]
    value["greeks"] = {"delta": 0.5, "gamma": 0.01, "theta": -3.0}
    provider, _ = provider_returning(option_chain_response(strikes={"3000": {"ce": value}}))
    chain = provider.get_option_chain(equity(), OPTION_EXPIRY)
    assert chain.quality is DataQuality.PARTIAL
    assert chain.strikes[0].call is not None
    assert chain.strikes[0].call.greeks.vega is None
    assert chain.strikes[0].call.bid is None


def test_zero_bid_and_ask_are_normalized_to_absence() -> None:
    value = option_side()
    value.update(
        {
            "top_bid_price": 0,
            "top_bid_quantity": 99,
            "top_ask_price": 0,
            "top_ask_quantity": 101,
        }
    )
    provider, _ = provider_returning(option_chain_response(strikes={"3000": {"pe": value}}))
    put = provider.get_option_chain(equity(), OPTION_EXPIRY).strikes[0].put
    assert put is not None
    assert (put.bid, put.bid_quantity, put.ask, put.ask_quantity) == (None, None, None, None)


def test_strikes_are_sorted_and_duplicate_normalization_is_rejected() -> None:
    provider, _ = provider_returning(
        option_chain_response(
            strikes={"3100": {"ce": option_side()}, "3000": {"pe": option_side()}}
        )
    )
    chain = provider.get_option_chain(equity(), OPTION_EXPIRY)
    assert tuple(item.strike for item in chain.strikes) == (
        3000,
        3100,
    )

    duplicate_provider, _ = provider_returning(
        option_chain_response(
            strikes={"3000": {"ce": option_side()}, "3000.0": {"pe": option_side()}}
        )
    )
    with pytest.raises(ProviderBadResponseError, match="validation"):
        duplicate_provider.get_option_chain(equity(), OPTION_EXPIRY)


@pytest.mark.parametrize(
    "response",
    [
        {"status": "failure", "data": {}},
        {"status": "success", "data": {"last_price": 1, "oc": {}}},
        option_chain_response(strikes={"not-a-strike": {"ce": option_side()}}),
        option_chain_response(strikes={"3000": {}}),
        option_chain_response(strikes={"3000": {"ce": {"last_price": "bad"}}}),
        option_chain_response(
            strikes={"3000": {"ce": {"last_price": 1, "greeks": {"delta": "bad"}}}}
        ),
        option_chain_response(strikes={"3000": {"ce": {"security_id": "invalid"}}}),
    ],
)
def test_malformed_option_chain_is_rejected(response: dict[str, Any]) -> None:
    provider, _ = provider_returning(response)
    with pytest.raises(ProviderBadResponseError):
        provider.get_option_chain(equity(), OPTION_EXPIRY)


def test_chain_json_round_trip_and_tuple_immutability() -> None:
    provider, _ = provider_returning(option_chain_response())
    chain = provider.get_option_chain(equity(), OPTION_EXPIRY)
    dumped = chain.model_dump(mode="json")
    assert isinstance(dumped["strikes"], list)
    assert type(chain).model_validate(dumped) == chain
    with pytest.raises(AttributeError):
        chain.strikes.append(chain.strikes[0])  # type: ignore[attr-defined]


def test_invalid_underlying_id_and_unsupported_segment_fail_before_transport() -> None:
    provider, transport = provider_returning(option_chain_response())
    with pytest.raises(InstrumentNotFoundError):
        provider.get_option_chain(equity(security_id="not-numeric"), OPTION_EXPIRY)
    with pytest.raises(UnsupportedCapabilityError):
        provider.get_option_chain(
            equity(segment=MarketSegment.NSE_FNO),
            OPTION_EXPIRY,
        )
    assert transport.calls == []
