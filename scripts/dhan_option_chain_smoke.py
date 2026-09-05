"""Read-only Dhan expiry and optional live option-chain inspection."""

import argparse
from datetime import date

from pydantic import ValidationError

from tiaf.data import InstrumentKey, InstrumentNotFoundError, InstrumentType, MarketSegment
from tiaf.data.errors import TIAFDataError
from tiaf.data.providers.dhan import DhanMarketDataProvider

_SEGMENTS = {
    MarketSegment.NSE_EQUITY: ("NSE", InstrumentType.EQUITY),
    MarketSegment.BSE_EQUITY: ("BSE", InstrumentType.EQUITY),
    MarketSegment.NSE_INDEX: ("NSE", InstrumentType.INDEX),
    MarketSegment.BSE_INDEX: ("BSE", InstrumentType.INDEX),
}


def parse_args() -> argparse.Namespace:
    """Parse an explicit underlying identity and optional active expiry."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--segment", required=True, choices=[item.value for item in _SEGMENTS])
    parser.add_argument("--security-id", required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--expiry", type=date.fromisoformat)
    parser.add_argument("--sample-size", type=int, default=5)
    return parser.parse_args()


def _value(value: float | int | None) -> str:
    return "-" if value is None else str(value)


def main() -> int:
    """List expiries and fetch a chain only after an explicit expiry request."""
    args = parse_args()
    exchange, instrument_type = _SEGMENTS[MarketSegment(args.segment)]
    try:
        underlying = InstrumentKey(
            symbol=args.symbol,
            exchange=exchange,
            segment=MarketSegment(args.segment),
            instrument_type=instrument_type,
            provider_instrument_id=args.security_id,
        )
        provider = DhanMarketDataProvider()
        expiries = provider.get_option_expiries(underlying)
        print("Dhan read-only option data inspection; no trading operation is available.")
        print("Active expiries:", ", ".join(item.isoformat() for item in expiries.expiries))
        if args.expiry is None:
            print("Supply --expiry explicitly to retrieve a live option chain.")
            return 0
        if args.expiry not in expiries.expiries:
            raise InstrumentNotFoundError(
                "The requested expiry is not in Dhan's active expiry list",
                provider="DHAN",
            )
        chain = provider.get_option_chain(underlying, args.expiry)
    except (TIAFDataError, ValidationError, ValueError) as exc:
        print(f"Dhan read-only option-chain smoke test failed: {exc}")
        return 2

    print(f"Underlying: {chain.underlying.symbol}")
    print(f"Underlying LTP: {_value(chain.underlying_ltp)}")
    print(f"Expiry: {chain.expiry.isoformat()}")
    print(f"Strikes: {len(chain.strikes)}")
    sample_size = max(args.sample_size, 0)
    nearest = sorted(
        chain.strikes,
        key=lambda item: abs(item.strike - (chain.underlying_ltp or item.strike)),
    )[:sample_size]
    print("Strike | CE LTP | CE IV | CE Delta | CE OI | PE LTP | PE IV | PE Delta | PE OI")
    for item in sorted(nearest, key=lambda value: value.strike):
        call = item.call
        put = item.put
        print(
            " | ".join(
                (
                    _value(item.strike),
                    _value(call.ltp if call else None),
                    _value(call.implied_volatility if call else None),
                    _value(call.greeks.delta if call else None),
                    _value(call.open_interest if call else None),
                    _value(put.ltp if put else None),
                    _value(put.implied_volatility if put else None),
                    _value(put.greeks.delta if put else None),
                    _value(put.open_interest if put else None),
                )
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
