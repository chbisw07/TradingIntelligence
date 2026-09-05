"""Deterministic Dhan test helpers with no network behavior."""

from collections.abc import Callable, Mapping
from datetime import UTC, date, datetime
from typing import Any

from tiaf.contracts import OptionType
from tiaf.data import InstrumentKey, InstrumentType, MarketSegment
from tiaf.data.providers.dhan import DhanConfig

FIXED_NOW = datetime(2026, 9, 5, 4, 31, tzinfo=UTC)
ResponseHandler = Callable[[str, Mapping[str, Any]], dict[str, Any]]


def dhan_config(token: str = "test-token-value") -> DhanConfig:
    """Build secret-safe fake credentials for isolated unit tests."""
    return DhanConfig.model_validate(
        {
            "client_id": "test-client-id",
            "access_token": token,
            "base_url": "https://api.dhan.co/v2",
        }
    )


def equity(
    symbol: str = "RELIANCE",
    security_id: str = "1333",
    *,
    segment: MarketSegment = MarketSegment.NSE_EQUITY,
) -> InstrumentKey:
    """Build an equity identity carrying an explicit Dhan security ID."""
    exchange = "BSE" if segment is MarketSegment.BSE_EQUITY else "NSE"
    return InstrumentKey(
        symbol=symbol,
        exchange=exchange,
        segment=segment,
        instrument_type=InstrumentType.EQUITY,
        provider_instrument_id=security_id,
    )


def index(
    symbol: str = "NIFTY",
    security_id: str = "13",
    *,
    segment: MarketSegment = MarketSegment.NSE_INDEX,
) -> InstrumentKey:
    """Build an index identity carrying an explicit Dhan security ID."""
    exchange = "BSE" if segment is MarketSegment.BSE_INDEX else "NSE"
    return InstrumentKey(
        symbol=symbol,
        exchange=exchange,
        segment=segment,
        instrument_type=InstrumentType.INDEX,
        provider_instrument_id=security_id,
    )


def option_side(
    security_id: int = 49081,
    *,
    last_price: float = 146.99,
) -> dict[str, Any]:
    """Return a complete documented Dhan option-side response."""
    return {
        "average_price": 140.25,
        "greeks": {"delta": 0.53871, "theta": -12.4, "gamma": 0.0012, "vega": 8.7},
        "implied_volatility": 18.5,
        "last_price": last_price,
        "oi": 123456,
        "previous_close_price": 141.5,
        "previous_oi": 120000,
        "previous_volume": 50000,
        "security_id": security_id,
        "top_ask_price": 147.2,
        "top_ask_quantity": 100,
        "top_bid_price": 146.8,
        "top_bid_quantity": 75,
        "volume": 55000,
    }


def option_chain_response(
    *,
    strikes: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return a deterministic complete live option-chain fixture."""
    return {
        "status": "success",
        "data": {
            "last_price": 3005.5,
            "oc": strikes
            or {
                "3000.000000": {
                    "ce": option_side(49081),
                    "pe": option_side(49082, last_price=138.2),
                }
            },
        },
    }


OPTION_EXPIRY = date(2026, 9, 24)


def rolling_option_side(timestamps: list[int] | None = None) -> dict[str, list[Any]]:
    """Return aligned arrays matching Dhan's rolling expired-option response."""
    epochs = timestamps or [1785555900, 1785556800]
    size = len(epochs)
    return {
        "timestamp": epochs,
        "open": [100.0 + index for index in range(size)],
        "high": [105.0 + index for index in range(size)],
        "low": [98.0 + index for index in range(size)],
        "close": [103.0 + index for index in range(size)],
        "iv": [18.5 + index for index in range(size)],
        "volume": [1000 + index for index in range(size)],
        "strike": [3000.0 for _ in range(size)],
        "oi": [5000 + index for index in range(size)],
        "spot": [3005.0 + index for index in range(size)],
    }


def rolling_option_response(
    *,
    side: str = "ce",
    values: dict[str, list[Any]] | None = None,
) -> dict[str, Any]:
    """Return one requested side with the opposite side explicitly unavailable."""
    data: dict[str, Any] = {"ce": None, "pe": None}
    data[side] = values or rolling_option_side()
    return {"data": data}


def call_option(
    symbol: str = "RELIANCE",
    security_id: str = "49081",
) -> InstrumentKey:
    """Build an F&O option identity carrying an explicit Dhan security ID."""
    return InstrumentKey(
        symbol=symbol,
        exchange="NSE",
        segment=MarketSegment.NSE_FNO,
        instrument_type=InstrumentType.CALL_OPTION,
        strike=3000,
        option_type=OptionType.CE,
        provider_instrument_id=security_id,
    )


def quote_entry(
    *,
    last_price: float = 3010.5,
    include_depth: bool = True,
    include_oi: bool = False,
) -> dict[str, Any]:
    """Return a fixture matching Dhan's documented full-quote shape."""
    entry: dict[str, Any] = {
        "last_price": last_price,
        "last_trade_time": "05/09/2026 10:00:00",
        "ohlc": {"open": 2990, "high": 3020, "low": 2980, "close": 2985},
        "volume": 1000,
    }
    if include_depth:
        entry["depth"] = {
            "buy": [
                {"price": 3009.0, "quantity": 10, "orders": 1},
                {"price": 3010.0, "quantity": 20, "orders": 2},
            ],
            "sell": [
                {"price": 3012.0, "quantity": 10, "orders": 1},
                {"price": 3011.0, "quantity": 20, "orders": 2},
            ],
        }
    if include_oi:
        entry["oi"] = 500
    return entry


def quote_response(
    request_body: Mapping[str, Any],
    *,
    include_depth: bool = True,
    include_oi: bool = False,
) -> dict[str, Any]:
    """Build a complete quote response for every requested security ID."""
    data: dict[str, dict[str, Any]] = {}
    for segment, ids_value in request_body.items():
        ids = tuple(ids_value)
        data[segment] = {
            str(security_id): quote_entry(
                last_price=float(security_id),
                include_depth=include_depth,
                include_oi=include_oi,
            )
            for security_id in reversed(ids)
        }
    return {"status": "success", "data": data}


class RecordingTransport:
    """Injected transport that records calls and delegates to a local handler."""

    def __init__(self, handler: ResponseHandler) -> None:
        self.handler = handler
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def post(self, path: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        copied = dict(payload)
        self.calls.append((path, copied))
        return self.handler(path, copied)
