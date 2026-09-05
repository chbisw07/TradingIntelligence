"""Read-only one-quote smoke test for the Dhan A1.2 adapter."""

import argparse

from pydantic import ValidationError

from tiaf.contracts import OptionType
from tiaf.data import InstrumentKey, InstrumentType, MarketSegment, TIAFDataError
from tiaf.data.providers.dhan import DhanMarketDataProvider


def parse_args() -> argparse.Namespace:
    """Parse explicit instrument identity without accepting trading inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--segment", required=True, choices=[item.value for item in MarketSegment])
    parser.add_argument("--security-id", required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--exchange", default="NSE")
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
        instrument = InstrumentKey(
            symbol=args.symbol,
            exchange=args.exchange,
            segment=MarketSegment(args.segment),
            instrument_type=InstrumentType(args.instrument_type),
            option_type=OptionType(args.option_type) if args.option_type else None,
            provider_instrument_id=args.security_id,
        )
        provider = DhanMarketDataProvider()
        quote = provider.get_quote(instrument)
    except (TIAFDataError, ValidationError, ValueError) as exc:
        print(f"Dhan read-only smoke test failed: {exc}")
        return 2

    print(quote.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
