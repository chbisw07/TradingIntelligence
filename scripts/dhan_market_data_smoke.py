"""Read-only one-quote smoke test for the Dhan A1.2 adapter."""

import argparse

from pydantic import ValidationError

from tiaf.contracts import OptionType
from tiaf.data import InstrumentType, MarketSegment, TIAFDataError
from tiaf.data.providers.dhan import (
    DhanMarketDataProvider,
    resolve_dhan_diagnostic_instrument,
)


def parse_args() -> argparse.Namespace:
    """Parse explicit instrument identity without accepting trading inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--segment", choices=[item.value for item in MarketSegment])
    parser.add_argument("--security-id")
    parser.add_argument("--symbol")
    parser.add_argument("--exchange", type=str.upper, choices=("NSE", "BSE"))
    parser.add_argument(
        "--instrument-type",
        default=InstrumentType.EQUITY.value,
        choices=[item.value for item in InstrumentType],
    )
    parser.add_argument("--option-type", choices=[item.value for item in OptionType])
    return parser.parse_args()


def main() -> int:
    """Fetch and print exactly one normalized quote without exposing secrets."""
    args = parse_args()
    try:
        instrument = resolve_dhan_diagnostic_instrument(
            symbol=args.symbol,
            security_id=args.security_id,
            exchange=args.exchange,
            segment=MarketSegment(args.segment) if args.segment else None,
            instrument_type=InstrumentType(args.instrument_type),
        )
        if args.option_type and instrument.option_type is not OptionType(args.option_type):
            raise ValueError("resolved instrument does not match --option-type")
        provider = DhanMarketDataProvider()
        quote = provider.get_quote(instrument)
    except (TIAFDataError, ValidationError, ValueError) as exc:
        print(f"Dhan read-only smoke test failed: {exc}")
        return 2

    print(quote.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
