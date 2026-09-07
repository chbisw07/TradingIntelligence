"""Inspect ordered read-only A2.8 feature evidence across explicit timeframes."""

import argparse
from datetime import datetime

from pydantic import TypeAdapter, ValidationError

from tiaf.context import (
    AnalysisContextBuilder,
    AnalysisContextError,
    AnalysisContextRequirement,
    AnalysisPurpose,
)
from tiaf.contracts import DataQuality
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data import InstrumentQuery, TIAFDataError, normalize_interval, normalize_symbol
from tiaf.data.providers.dhan import (
    DhanInstrumentResolver,
    DhanMarketDataProvider,
    dhan_rate_policy_registry,
)
from tiaf.data.runtime import DataFetchCoordinator, FreshnessRequirement, ProviderScheduler
from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureError,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    MultiTimeframeContext,
    MultiTimeframeFeatureEngine,
    TimeframeFeatureContext,
    builtin_feature_registry,
    multi_timeframe_context,
    timeframe_feature_context,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", default="RELIANCE")
    parser.add_argument("--exchange", type=str.upper)
    parser.add_argument("--timeframes", default="1d,1h,15m")
    parser.add_argument("--lookback-days", type=int, default=180)
    parser.add_argument("--bars", type=int, default=20)
    parser.add_argument("--ema-period", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.lookback_days <= 0 or args.bars <= 0 or args.ema_period <= 0:
        parser.error("lookback days, bars, and EMA period must be positive")
    intervals = tuple(
        normalize_interval(item) for item in args.timeframes.split(",") if item.strip()
    )
    if not intervals:
        parser.error("--timeframes requires at least one interval")
    if len(intervals) != len(set(intervals)):
        parser.error("--timeframes must not contain duplicate normalized intervals")
    args.timeframes = intervals
    return args


def _effective_lookback(interval: str, requested_days: int) -> int:
    # The accepted Dhan A1 adapter exposes its intraday single-request ceiling.
    return requested_days if interval == "1d" else min(requested_days, 90)


def _requirement(interval: str, lookback_days: int) -> AnalysisContextRequirement:
    return AnalysisContextRequirement(
        purpose=AnalysisPurpose.RESEARCH,
        include_quote=False,
        require_quote=False,
        include_history=True,
        require_history=True,
        history_interval=interval,
        history_lookback_days=lookback_days,
        history_freshness=FreshnessRequirement(
            fresh_for_seconds=3600,
            aging_for_seconds=86_400,
        ),
    )


def _constituent_requests(
    interval: str, bars: int, ema_period: int
) -> tuple[FeatureRequest, ...]:
    return (
        FeatureRequest(
            feature_id="return.percent",
            parameters=(("bars", bars),),
            interval=interval,
        ),
        FeatureRequest(
            feature_id="trend.distance_from_ema_percent",
            parameters=(("period", ema_period),),
            interval=interval,
        ),
        FeatureRequest(
            feature_id="trend.linear_slope",
            parameters=(("bars", bars),),
            interval=interval,
        ),
    )


def _aggregate_requests(bars: int, ema_period: int) -> tuple[FeatureRequest, ...]:
    return (
        FeatureRequest(feature_id="mtf.requested_timeframe_count"),
        FeatureRequest(feature_id="mtf.available_timeframe_count"),
        *(
            FeatureRequest(feature_id=feature_id, parameters=(("bars", bars),))
            for feature_id in (
                "mtf.positive_return_fraction",
                "mtf.negative_return_fraction",
                "mtf.positive_slope_fraction",
                "mtf.negative_slope_fraction",
                "mtf.directional_agreement_fraction",
                "mtf.disagreement_fraction",
            )
        ),
        *(
            FeatureRequest(feature_id=feature_id, parameters=(("period", ema_period),))
            for feature_id in (
                "mtf.price_above_ema_fraction",
                "mtf.price_below_ema_fraction",
            )
        ),
    )


def _unavailable(interval: str, requested_at: datetime, reason: str) -> TimeframeFeatureContext:
    return TimeframeFeatureContext(
        interval=interval,
        status=FeatureStatus.INSUFFICIENT_DATA,
        quality=DataQuality.UNAVAILABLE,
        as_of=requested_at,
        warnings=(reason,),
    )


def _print_results(
    context: MultiTimeframeContext,
    results: tuple[FeatureResult, ...],
    lookbacks: tuple[tuple[str, int], ...],
) -> None:
    print("TIAF A2.8 ORDERED MULTI-TIMEFRAME CONTEXT")
    print("=" * 58)
    print(f"Subject          : {context.subject_symbol}")
    print(f"Requested order  : {', '.join(context.requested_intervals)}")
    print(f"Complete         : {context.complete}")
    print(f"Overall quality  : {context.overall_quality.value}")
    for timeframe, (_, lookback) in zip(context.timeframes, lookbacks, strict=True):
        print(
            f"  {timeframe.interval}: status={timeframe.status.value} "
            f"quality={timeframe.quality.value} lookback_days={lookback} "
            f"as_of={timeframe.as_of.isoformat()} bundle={timeframe.feature_bundle_id or '-'}"
        )
        if timeframe.warnings:
            print(f"    warnings={'; '.join(timeframe.warnings)}")
    print("Denominator      : valid contributing timeframes (missing is excluded)")
    print()
    for result in results:
        rendered = "-" if result.value is None else str(result.value)
        print(f"{result.request.feature_id}: {rendered} {result.unit or ''}".rstrip())
        print(
            f"  status={result.status.value} quality={result.quality.value} "
            f"as_of={result.as_of.isoformat()} "
            f"contributors={result.metadata['contributing_intervals']}"
        )


def main() -> int:
    """Acquire each timeframe independently and aggregate factual bundle outputs."""
    args = parse_args()
    requested_at = datetime.now(TIAF_TIMEZONE)
    lookbacks = tuple(
        (interval, _effective_lookback(interval, args.lookback_days))
        for interval in args.timeframes
    )
    try:
        provider = DhanMarketDataProvider()
        builder = AnalysisContextBuilder(
            DhanInstrumentResolver(),
            provider,
            DataFetchCoordinator(scheduler=ProviderScheduler(dhan_rate_policy_registry())),
            clock=lambda: requested_at,
        )
        feature_engine = DeterministicFeatureEngine(builtin_feature_registry())
        timeframes: list[TimeframeFeatureContext] = []
        for interval, lookback in lookbacks:
            try:
                context = builder.build(
                    InstrumentQuery(
                        symbol=args.symbol,
                        exchange=args.exchange,
                        provider="dhan",
                    ),
                    _requirement(interval, lookback),
                    source_system="multi_timeframe_smoke",
                )
                bundle = feature_engine.compute(
                    context,
                    _constituent_requests(interval, args.bars, args.ema_period),
                )
                timeframes.append(timeframe_feature_context(interval, bundle))
            except (
                AnalysisContextError,
                FeatureError,
                TIAFDataError,
                ValidationError,
                ValueError,
            ) as exc:
                timeframes.append(_unavailable(interval, requested_at, str(exc)))
        aggregate_context = multi_timeframe_context(
            normalize_symbol(args.symbol),
            tuple(timeframes),
            created_at=requested_at,
        )
        aggregate_engine = MultiTimeframeFeatureEngine()
        results = tuple(
            aggregate_engine.compute_one(aggregate_context, request)
            for request in _aggregate_requests(args.bars, args.ema_period)
        )
        if args.json:
            payload = {"context": aggregate_context, "results": results}
            print(TypeAdapter(dict[str, object]).dump_json(payload, indent=2).decode())
        else:
            if any(
                interval != "1d" and lookback < args.lookback_days
                for interval, lookback in lookbacks
            ):
                print(
                    "Dhan intraday lookback is capped at the accepted 90-day "
                    "single-request limit; effective values are shown below.\n"
                )
            _print_results(aggregate_context, results, lookbacks)
    except (FeatureError, TIAFDataError, ValidationError, ValueError) as exc:
        print(f"Read-only multi-timeframe smoke failed: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
