"""Read-only Dhan instrument-master lookup; no credentials or trading operations."""

import argparse
from datetime import date

from pydantic import ValidationError

from tiaf.contracts import OptionType
from tiaf.data import InstrumentQuery, InstrumentType, MarketSegment
from tiaf.data.providers.dhan import DhanInstrumentResolver
from tiaf.data.resolution import InstrumentResolutionError, ResolvedInstrument


def parse_args() -> argparse.Namespace:
    """Parse an explicit lookup or F&O-underlying listing request."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol")
    parser.add_argument("--exchange", type=str.upper, choices=("NSE", "BSE"))
    parser.add_argument("--segment", choices=[item.value for item in MarketSegment])
    parser.add_argument("--instrument-type", choices=[item.value for item in InstrumentType])
    parser.add_argument("--expiry", type=date.fromisoformat)
    parser.add_argument("--strike", type=float)
    parser.add_argument("--option-type", choices=[item.value for item in OptionType])
    parser.add_argument("--trading-symbol")
    parser.add_argument("--provider-instrument-id")
    parser.add_argument("--list-fno-underlyings", action="store_true")
    parser.add_argument(
        "--all-matches",
        action="store_true",
        help="show every exact match, or every F&O underlying instead of the first 20",
    )
    parser.add_argument("--refresh", action="store_true")
    return parser.parse_args()


def _print_instrument(prefix: str, match: ResolvedInstrument) -> None:
    instrument = match.instrument
    print(
        f"{prefix}{instrument.symbol} | {instrument.exchange} | "
        f"{instrument.segment.value} | {instrument.instrument_type.value} | "
        f"securityId={match.provider_instrument_id} | "
        f"tradingSymbol={instrument.trading_symbol or '-'}"
    )


def main() -> int:
    """Inspect deterministic master resolution and print no market recommendation."""
    args = parse_args()
    try:
        resolver = DhanInstrumentResolver()
        if args.refresh:
            resolver.refresh()
        print("Dhan read-only instrument resolver; no market or trading operation is available.")
        if args.list_fno_underlyings:
            fno_exchange = args.exchange or resolver.policy.primary_fno_exchange
            underlyings = resolver.get_fno_underlyings(exchange=fno_exchange)
            print(f"F&O exchange: {fno_exchange}")
            visible = underlyings if args.all_matches else underlyings[:20]
            for match in visible:
                _print_instrument("", match)
            if len(visible) < len(underlyings):
                print(f"... {len(underlyings) - len(visible)} more; use --all-matches to show all")
            print(f"Unique eligible underlying count: {len(underlyings)}")
            return 0
        query = InstrumentQuery(
            symbol=args.symbol,
            exchange=args.exchange,
            segment=args.segment,
            instrument_type=args.instrument_type,
            expiry=args.expiry,
            strike=args.strike,
            option_type=args.option_type,
            trading_symbol=args.trading_symbol,
            provider_instrument_id=args.provider_instrument_id,
            provider="DHAN",
        )
        result = resolver.resolve(query)
        all_matches = resolver.search(query) if args.all_matches else ()
    except (InstrumentResolutionError, ValidationError, ValueError) as exc:
        print(f"Dhan instrument resolver smoke test failed: {exc}")
        return 2

    if result.not_found:
        print("No instrument matched the explicit query.")
        return 1
    if result.ambiguous:
        print(f"Ambiguous query: {len(result.matches)} exact candidates")
        for match in result.matches:
            _print_instrument("- ", match)
        return 1
    assert result.resolved is not None
    print(f"Resolved: {result.resolved.instrument.symbol}")
    print(f"Resolution: {result.resolved.resolution_kind.value}")
    if result.metadata.get("policy_applied") is True:
        print(f"Primary exchange: {result.metadata['preferred_exchange']}")
    _print_instrument("Instrument: ", result.resolved)
    if all_matches:
        print(f"All exact matches before policy: {len(all_matches)}")
        for match in all_matches:
            _print_instrument("- ", match)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
