"""Inspect read-only, explicit-benchmark A2.8 relative-strength measurements."""

import argparse
from datetime import datetime

from pydantic import TypeAdapter, ValidationError

from tiaf.context import (
    AnalysisContext,
    AnalysisContextBuilder,
    AnalysisContextError,
    AnalysisContextRequirement,
    AnalysisPurpose,
)
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data import InstrumentQuery, InstrumentType, TIAFDataError
from tiaf.data.providers.dhan import (
    DhanInstrumentResolver,
    DhanMarketDataProvider,
    dhan_rate_policy_registry,
)
from tiaf.data.runtime import DataFetchCoordinator, FreshnessRequirement, ProviderScheduler
from tiaf.features import (
    BenchmarkReference,
    BenchmarkRole,
    FeatureError,
    FeatureRequest,
    FeatureResult,
    RelativeStrengthEngine,
    relative_strength_context,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", default="RELIANCE")
    parser.add_argument("--benchmark", required=True)
    parser.add_argument(
        "--benchmark-role",
        choices=tuple(item.value for item in BenchmarkRole),
        default=BenchmarkRole.MARKET.value,
    )
    parser.add_argument("--subject-exchange", type=str.upper)
    parser.add_argument("--benchmark-exchange", type=str.upper)
    parser.add_argument(
        "--benchmark-type",
        choices=("AUTO", InstrumentType.EQUITY.value, InstrumentType.INDEX.value),
        default="AUTO",
    )
    parser.add_argument("--history-interval", default="1d")
    parser.add_argument("--lookback-days", type=int, default=180)
    parser.add_argument("--bars", type=int, default=20)
    parser.add_argument("--atr-period", type=int, default=14)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.lookback_days <= 0 or args.bars <= 0 or args.atr_period <= 0:
        parser.error("lookback days, bars, and ATR period must be positive")
    return args


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


def _requests(interval: str, bars: int, atr_period: int) -> tuple[FeatureRequest, ...]:
    standard = (("bars", bars),)
    return (
        FeatureRequest(
            feature_id="relative.subject_return_percent",
            parameters=standard,
            interval=interval,
        ),
        FeatureRequest(
            feature_id="relative.benchmark_return_percent",
            parameters=standard,
            interval=interval,
        ),
        FeatureRequest(
            feature_id="relative.return_spread_percent",
            parameters=standard,
            interval=interval,
        ),
        FeatureRequest(
            feature_id="relative.return_ratio",
            parameters=standard,
            interval=interval,
        ),
        FeatureRequest(
            feature_id="relative.excess_move_atr",
            parameters=(("atr_period", atr_period), ("bars", bars)),
            interval=interval,
        ),
        FeatureRequest(
            feature_id="relative.strength_consistency",
            parameters=standard,
            interval=interval,
        ),
    )


def _print_results(
    context: AnalysisContext,
    benchmark_context: AnalysisContext,
    results: tuple[FeatureResult, ...],
) -> None:
    subject_history = context.history
    benchmark_history = benchmark_context.history
    print("TIAF A2.8 EXPLICIT BENCHMARK RELATIVE STRENGTH")
    print("=" * 62)
    print(f"Subject          : {context.subject.symbol}")
    print(f"Benchmark        : {benchmark_context.subject.symbol}")
    print(f"Interval         : {results[0].request.interval}")
    print(f"Subject bars     : {len(subject_history.bars) if subject_history else 0}")
    print(f"Benchmark bars   : {len(benchmark_history.bars) if benchmark_history else 0}")
    if subject_history and benchmark_history and subject_history.bars and benchmark_history.bars:
        print(f"Subject latest   : {subject_history.bars[-1].end_at.isoformat()}")
        print(f"Benchmark latest : {benchmark_history.bars[-1].end_at.isoformat()}")
    print("Alignment        : exact latest common (start_at, end_at) suffix")
    print()
    for result in results:
        rendered = "-" if result.value is None else str(result.value)
        print(f"{result.request.feature_id}: {rendered} {result.unit or ''}".rstrip())
        print(
            f"  status={result.status.value} quality={result.quality.value} "
            f"as_of={result.as_of.isoformat()} lookback={result.lookback_bars_used}"
        )
        if result.warnings:
            print(f"  warnings={'; '.join(result.warnings)}")


def main() -> int:
    """Acquire two factual histories and compare them without trading semantics."""
    args = parse_args()
    try:
        requested_at = datetime.now(TIAF_TIMEZONE)
        provider = DhanMarketDataProvider()
        builder = AnalysisContextBuilder(
            DhanInstrumentResolver(),
            provider,
            DataFetchCoordinator(scheduler=ProviderScheduler(dhan_rate_policy_registry())),
            clock=lambda: requested_at,
        )
        requirement = _requirement(args.history_interval, args.lookback_days)
        subject = builder.build(
            InstrumentQuery(symbol=args.symbol, exchange=args.subject_exchange, provider="dhan"),
            requirement,
            source_system="relative_strength_smoke",
        )
        benchmark_type = (
            None if args.benchmark_type == "AUTO" else InstrumentType(args.benchmark_type)
        )
        benchmark_context = builder.build(
            InstrumentQuery(
                symbol=args.benchmark,
                exchange=args.benchmark_exchange,
                instrument_type=benchmark_type,
                provider="dhan",
            ),
            requirement,
            source_system="relative_strength_smoke",
        )
        benchmark_instrument = benchmark_context.subject.resolved_instrument.instrument
        relative_context = relative_strength_context(
            subject,
            benchmark_context,
            BenchmarkReference(
                symbol=benchmark_context.subject.symbol,
                role=BenchmarkRole(args.benchmark_role),
                exchange=benchmark_instrument.exchange,
            ),
            interval=args.history_interval,
        )
        engine = RelativeStrengthEngine()
        results = tuple(
            engine.compute_one(relative_context, request)
            for request in _requests(args.history_interval, args.bars, args.atr_period)
        )
        if args.json:
            payload = {"context": relative_context, "results": results}
            print(TypeAdapter(dict[str, object]).dump_json(payload, indent=2).decode())
        else:
            _print_results(subject, benchmark_context, results)
    except (AnalysisContextError, FeatureError, TIAFDataError, ValidationError, ValueError) as exc:
        print(f"Read-only relative-strength smoke failed: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
