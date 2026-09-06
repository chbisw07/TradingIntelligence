"""Build one read-only A1 context and inspect deterministic A2.1 features."""

import argparse
from datetime import datetime

from pydantic import ValidationError

from tiaf.context import (
    AnalysisContextBuilder,
    AnalysisContextError,
    AnalysisContextRequirement,
    AnalysisPurpose,
)
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data import TIAFDataError
from tiaf.data.providers.dhan import (
    DhanInstrumentResolver,
    DhanMarketDataProvider,
    dhan_rate_policy_registry,
)
from tiaf.data.runtime import DataFetchCoordinator, FreshnessRequirement, ProviderScheduler
from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureBundle,
    FeatureError,
    FeatureRequest,
    builtin_feature_registry,
    summarize_feature_bundle,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", default="RELIANCE")
    parser.add_argument("--history-interval", default="1d")
    parser.add_argument("--lookback-days", type=int, default=90)
    parser.add_argument("--repeat", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _requests(interval: str) -> tuple[FeatureRequest, ...]:
    return (
        FeatureRequest(feature_id="price.current"),
        FeatureRequest(feature_id="history.bar_count", interval=interval),
        FeatureRequest(
            feature_id="return.percent",
            parameters=(("bars", 1),),
            interval=interval,
        ),
        FeatureRequest(
            feature_id="return.percent",
            parameters=(("bars", 5),),
            interval=interval,
        ),
        FeatureRequest(
            feature_id="return.percent",
            parameters=(("bars", 20),),
            interval=interval,
        ),
        FeatureRequest(
            feature_id="range.high_low_percent",
            parameters=(("bars", 20),),
            interval=interval,
        ),
    )


def _print_bundle(
    bundle: FeatureBundle, *, as_json: bool, label: str | None = None
) -> None:
    if label is not None:
        print(label)
    if as_json:
        print(bundle.model_dump_json(indent=2))
    else:
        print(summarize_feature_bundle(bundle))


def main() -> int:
    """Acquire factual context through A1, then derive A2.1 features."""
    args = parse_args()
    try:
        requested_at = datetime.now(TIAF_TIMEZONE)
        provider = DhanMarketDataProvider()
        builder = AnalysisContextBuilder(
            DhanInstrumentResolver(),
            provider,
            DataFetchCoordinator(
                scheduler=ProviderScheduler(dhan_rate_policy_registry())
            ),
            clock=lambda: requested_at,
        )
        requirements = AnalysisContextRequirement(
            purpose=AnalysisPurpose.RESEARCH,
            history_interval=args.history_interval,
            history_lookback_days=args.lookback_days,
            quote_freshness=FreshnessRequirement(
                fresh_for_seconds=5,
                aging_for_seconds=30,
            ),
            history_freshness=FreshnessRequirement(
                fresh_for_seconds=3600,
                aging_for_seconds=86_400,
            ),
        )
        engine = DeterministicFeatureEngine(builtin_feature_registry())
        requests = _requests(args.history_interval)
        first_context = builder.build(
            args.symbol,
            requirements,
            source_system="feature_engine_smoke",
        )
        first = engine.compute(first_context, requests)
        _print_bundle(
            first,
            as_json=args.json,
            label="FIRST FEATURE BUILD" if args.repeat else None,
        )
        if args.repeat:
            second_context = builder.build(
                args.symbol,
                requirements,
                source_system="feature_engine_smoke",
            )
            second = engine.compute(second_context, requests)
            print()
            _print_bundle(second, as_json=args.json, label="SECOND FEATURE BUILD")
    except (AnalysisContextError, FeatureError, TIAFDataError, ValidationError, ValueError) as exc:
        print(f"Read-only feature smoke failed: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
