"""Read-only Dhan quote demo through the provider-neutral A1.6 data runtime."""

import argparse

from pydantic import ValidationError

from tiaf.data import InstrumentQuery, InstrumentType, TIAFDataError
from tiaf.data.providers.dhan import (
    DhanInstrumentResolver,
    DhanMarketDataProvider,
    dhan_rate_policy_registry,
)
from tiaf.data.resolution import InstrumentResolutionError
from tiaf.data.runtime import (
    CacheKey,
    DataFetchCoordinator,
    DataRuntimeError,
    FreshnessRequirement,
    ProviderScheduler,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", default="RELIANCE")
    parser.add_argument("--exchange", type=str.upper, choices=("NSE", "BSE"))
    parser.add_argument("--fresh-for-seconds", type=float, default=5.0)
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="force the second read through the provider gate instead of using cache",
    )
    return parser.parse_args()


def main() -> int:
    """Resolve symbol-first, fetch once, then demonstrate explicit cache reuse."""
    args = parse_args()
    try:
        resolver = DhanInstrumentResolver()
        resolution = resolver.resolve(
            InstrumentQuery(
                symbol=args.symbol,
                exchange=args.exchange,
                instrument_type=InstrumentType.EQUITY,
                provider="dhan",
            )
        )
        if resolution.resolved is None:
            state = "ambiguous" if resolution.ambiguous else "not found"
            raise ValueError(f"symbol resolution was {state}")
        instrument = resolution.resolved.instrument
        provider = DhanMarketDataProvider()
        coordinator = DataFetchCoordinator(
            scheduler=ProviderScheduler(dhan_rate_policy_registry())
        )
        requirement = FreshnessRequirement(
            fresh_for_seconds=args.fresh_for_seconds,
            aging_for_seconds=args.fresh_for_seconds,
            use_stored_at_if_observed_missing=True,
        )
        key = CacheKey(
            namespace="market",
            provider="dhan",
            instrument_identity=(
                f"{instrument.segment.value}:{instrument.provider_instrument_id}"
            ),
            operation="quote",
        )
        first = coordinator.get_or_fetch(
            key,
            requirement,
            lambda: provider.get_quote(instrument),
            "dhan",
            "quote",
            observed_at_getter=lambda quote: quote.received_at,
        )
        second = coordinator.get_or_fetch(
            key,
            requirement,
            lambda: provider.get_quote(instrument),
            "dhan",
            "quote",
            force_refresh=args.force_refresh,
            observed_at_getter=lambda quote: quote.received_at,
        )
    except (
        DataRuntimeError,
        InstrumentResolutionError,
        TIAFDataError,
        ValidationError,
        ValueError,
    ) as exc:
        print(f"Dhan read-only data-runtime smoke failed: {exc}")
        return 2

    print(f"first request: {first.disposition.value}")
    print(f"second request: {second.disposition.value}")
    print(f"freshness: {second.freshness.value}")
    print(f"age_seconds: {second.age_seconds}")
    print(f"source: {second.source_provider}")
    print(coordinator.stats().model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
