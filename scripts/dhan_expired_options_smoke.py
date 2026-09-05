"""Read-only inspection of normalized Dhan rolling expired-option history."""

import argparse
from datetime import date

from pydantic import ValidationError

from tiaf.contracts import OptionType
from tiaf.data import (
    ExpiryFlag,
    HistoricalOptionExpiryCode,
    InstrumentKey,
    InstrumentType,
    MarketSegment,
)
from tiaf.data.errors import TIAFDataError
from tiaf.data.historical_options import RelativeStrike
from tiaf.data.providers.dhan import DhanInstrumentType, DhanMarketDataProvider

_SEGMENTS = (MarketSegment.NSE_FNO, MarketSegment.BSE_FNO)
_INSTRUMENTS = (DhanInstrumentType.OPTSTK, DhanInstrumentType.OPTIDX)


def parse_args() -> argparse.Namespace:
    """Parse explicit factual request parameters without trading inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--segment", required=True, choices=[item.value for item in _SEGMENTS])
    parser.add_argument("--security-id", required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument(
        "--instrument", required=True, choices=[item.value for item in _INSTRUMENTS]
    )
    parser.add_argument("--expiry-flag", required=True, choices=[item.value for item in ExpiryFlag])
    parser.add_argument(
        "--expiry-code",
        required=True,
        type=int,
        choices=[int(item) for item in HistoricalOptionExpiryCode],
    )
    parser.add_argument("--strike", required=True)
    parser.add_argument("--option-type", required=True, choices=[item.value for item in OptionType])
    parser.add_argument("--interval", required=True, choices=("1m", "5m", "15m", "25m", "1h"))
    parser.add_argument("--from-date", required=True, type=date.fromisoformat)
    parser.add_argument("--to-date", required=True, type=date.fromisoformat)
    parser.add_argument("--sample-size", type=int, default=10)
    return parser.parse_args()


def _value(value: float | int | None) -> str:
    return "-" if value is None else str(value)


def main() -> int:
    """Fetch and display factual history from Dhan's read-only data endpoint."""
    args = parse_args()
    segment = MarketSegment(args.segment)
    exchange = "NSE" if segment is MarketSegment.NSE_FNO else "BSE"
    instrument_type = (
        InstrumentType.EQUITY
        if args.instrument == DhanInstrumentType.OPTSTK.value
        else InstrumentType.INDEX
    )
    try:
        underlying = InstrumentKey(
            symbol=args.symbol,
            exchange=exchange,
            segment=segment,
            instrument_type=instrument_type,
            provider_instrument_id=args.security_id,
        )
        provider = DhanMarketDataProvider()
        result = provider.get_historical_options(
            underlying=underlying,
            interval=args.interval,
            expiry_flag=ExpiryFlag(args.expiry_flag),
            expiry_code=args.expiry_code,
            relative_strike=RelativeStrike.model_validate(args.strike),
            option_type=OptionType(args.option_type),
            start_date=args.from_date,
            end_date=args.to_date,
        )
    except (TIAFDataError, ValidationError, ValueError) as exc:
        print(f"Dhan read-only expired-options smoke test failed: {exc}")
        return 2

    print("Dhan read-only historical option data; no trading operation is available.")
    print(f"Underlying: {result.underlying.symbol}")
    print(f"Side: {result.option_type.value}")
    print(f"Expiry flag/code: {result.expiry_flag.value} / {int(result.expiry_code)}")
    print(f"Relative strike: {result.relative_strike}")
    print(f"Range: {result.requested_from} to {result.requested_to} (non-inclusive)")
    print(f"Bars: {len(result.bars)}")
    print("Time | Spot | Strike | O | H | L | C | IV | OI | Volume")
    for bar in result.bars[: max(args.sample_size, 0)]:
        print(
            " | ".join(
                (
                    bar.start_at.isoformat(),
                    _value(bar.spot),
                    _value(bar.actual_strike),
                    _value(bar.open),
                    _value(bar.high),
                    _value(bar.low),
                    _value(bar.close),
                    _value(bar.implied_volatility),
                    _value(bar.open_interest),
                    _value(bar.volume),
                )
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
