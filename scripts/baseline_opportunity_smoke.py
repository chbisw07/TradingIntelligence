"""Acquire factual evidence, then inspect the deterministic A2.9 benchmark."""

import argparse
from datetime import datetime
from uuid import NAMESPACE_URL, uuid5

from pydantic import TypeAdapter, ValidationError

from tiaf.baseline import (
    BaselineEngine,
    BaselineError,
    BaselineEvidenceSource,
    BaselinePolicy,
    DeterministicBaselineRequest,
    EvidenceFreshness,
    OpportunityAssessment,
    default_policy,
    rank_opportunities,
    summarize_assessment,
    summarize_ranking,
)
from tiaf.context import (
    AnalysisContext,
    AnalysisContextBuilder,
    AnalysisContextError,
    AnalysisContextRequirement,
    AnalysisPurpose,
)
from tiaf.contracts import DataQuality, FreshnessState, Horizon, TradeStyle
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data import InstrumentQuery, TIAFDataError, normalize_interval, normalize_symbol
from tiaf.data.providers.dhan import (
    DhanInstrumentResolver,
    DhanMarketDataProvider,
    dhan_rate_policy_registry,
)
from tiaf.data.runtime import DataFetchCoordinator, FreshnessRequirement, ProviderScheduler
from tiaf.features import (
    BenchmarkReference,
    BenchmarkRole,
    DeterministicFeatureEngine,
    FeatureBundle,
    FeatureError,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    MultiTimeframeFeatureEngine,
    TimeframeFeatureContext,
    builtin_feature_registry,
    multi_timeframe_context,
    relative_strength_context,
    timeframe_feature_context,
)
from tiaf.features.models import JSONScalar
from tiaf.features.relative import RelativeStrengthEngine
from tiaf.indicators import (
    IndicatorBundle,
    IndicatorEngine,
    IndicatorError,
    IndicatorRequest,
    builtin_indicator_registry,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    symbols = parser.add_mutually_exclusive_group()
    symbols.add_argument("--symbol")
    symbols.add_argument("--symbols")
    parser.add_argument(
        "--horizon", choices=tuple(item.value for item in TradeStyle), required=True
    )
    parser.add_argument("--benchmark")
    parser.add_argument(
        "--benchmark-map",
        action="append",
        default=[],
        metavar="SYMBOL=BENCHMARK",
        help="Explicit per-subject mapping; overrides --benchmark.",
    )
    parser.add_argument("--timeframes", default="1d,1h,15m")
    parser.add_argument("--lookback-days", type=int, default=180)
    parser.add_argument("--top-n", type=int)
    parser.add_argument("--rank", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    selected = args.symbols or args.symbol or "RELIANCE"
    args.symbols = tuple(
        dict.fromkeys(normalize_symbol(item) for item in selected.split(",") if item.strip())
    )
    if not args.symbols:
        parser.error("at least one symbol is required")
    args.timeframes = tuple(
        dict.fromkeys(
            normalize_interval(item) for item in args.timeframes.split(",") if item.strip()
        )
    )
    if not args.timeframes:
        parser.error("at least one timeframe is required")
    if args.lookback_days <= 0 or (args.top_n is not None and args.top_n <= 0):
        parser.error("lookback-days and top-n must be positive")
    mapping: dict[str, str] = {}
    for item in args.benchmark_map:
        if "=" not in item:
            parser.error("--benchmark-map entries must be SYMBOL=BENCHMARK")
        subject, benchmark = item.split("=", 1)
        mapping[normalize_symbol(subject)] = normalize_symbol(benchmark)
    args.benchmark_map = mapping
    args.horizon = TradeStyle(args.horizon)
    return args


def _requirement(interval: str, days: int) -> AnalysisContextRequirement:
    effective_days = days if interval == "1d" else min(days, 90)
    return AnalysisContextRequirement(
        purpose=AnalysisPurpose.SCREENING,
        include_quote=False,
        require_quote=False,
        include_history=True,
        require_history=True,
        history_interval=interval,
        history_lookback_days=effective_days,
        history_freshness=FreshnessRequirement(
            fresh_for_seconds=3600,
            aging_for_seconds=86_400,
        ),
    )


def _requests(
    policy: BaselinePolicy,
    source: BaselineEvidenceSource,
    interval: str | None,
) -> tuple[FeatureRequest, ...]:
    selected: dict[tuple[str, tuple[tuple[str, JSONScalar], ...]], bool] = {}
    for rule in policy.evidence_rules:
        if rule.selector.source is source:
            key = (rule.selector.evidence_id, rule.selector.parameters)
            selected[key] = selected.get(key, False) or rule.required
    return tuple(
        FeatureRequest(
            feature_id=feature_id,
            parameters=parameters,
            interval=interval,
            required=required,
        )
        for (feature_id, parameters), required in selected.items()
    )


def _quality(results: tuple[FeatureResult, ...]) -> DataQuality:
    usable = tuple(
        item for item in results if item.status in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
    )
    if not usable:
        return DataQuality.UNAVAILABLE
    if any(item.quality in {DataQuality.DEGRADED, DataQuality.UNAVAILABLE} for item in usable):
        return DataQuality.DEGRADED
    if any(
        item.status is FeatureStatus.PARTIAL or item.quality is DataQuality.PARTIAL
        for item in usable
    ):
        return DataQuality.PARTIAL
    return DataQuality.GOOD


def _indicator_requests(
    policy: BaselinePolicy,
    interval: str,
) -> tuple[IndicatorRequest, ...]:
    selected: dict[tuple[str, tuple[tuple[str, JSONScalar], ...]], bool] = {}
    for rule in policy.evidence_rules:
        if rule.selector.source is BaselineEvidenceSource.INDICATOR:
            key = (rule.selector.evidence_id, rule.selector.parameters)
            selected[key] = selected.get(key, False) or rule.required
    return tuple(
        IndicatorRequest(
            indicator_id=indicator_id,
            parameters=parameters,
            interval=interval,
            required=required,
        )
        for (indicator_id, parameters), required in selected.items()
    )


def _bundle(
    context_id: str,
    symbol: str,
    created_at: datetime,
    results: tuple[FeatureResult, ...],
    identity: str,
) -> FeatureBundle:
    missing = tuple(
        item.request.feature_id
        for item in results
        if item.request.required
        and item.status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
    )
    return FeatureBundle(
        bundle_id=str(uuid5(NAMESPACE_URL, f"tiaf:a2.9-smoke:{identity}")),
        context_id=context_id,
        subject_symbol=symbol,
        created_at=created_at,
        results=results,
        overall_quality=_quality(results),
        complete=not missing,
        missing_required_features=missing,
        warnings=tuple(
            f"{item.request.feature_id}: {warning}" for item in results for warning in item.warnings
        ),
    )


def _history_freshness(context: AnalysisContext | None) -> FreshnessState:
    if context is None:
        return FreshnessState.UNKNOWN
    descriptor = next((item for item in context.evidence if item.evidence_name == "history"), None)
    return (
        descriptor.retrieval_freshness
        if descriptor is not None and descriptor.retrieval_freshness is not None
        else FreshnessState.UNKNOWN
    )


def _unavailable_timeframe(interval: str, now: datetime, warning: str) -> TimeframeFeatureContext:
    return TimeframeFeatureContext(
        interval=interval,
        status=FeatureStatus.INSUFFICIENT_DATA,
        quality=DataQuality.UNAVAILABLE,
        as_of=now,
        warnings=(warning,),
    )


def _acquire_context(
    builder: AnalysisContextBuilder,
    symbol: str,
    interval: str,
    days: int,
) -> AnalysisContext:
    return builder.build(
        InstrumentQuery(symbol=symbol, provider="dhan"),
        _requirement(interval, days),
        source_system="baseline_opportunity_smoke",
    )


def _assess_symbol(
    builder: AnalysisContextBuilder,
    symbol: str,
    benchmark_symbol: str | None,
    intervals: tuple[str, ...],
    lookback_days: int,
    trade_style: TradeStyle,
    requested_at: datetime,
) -> OpportunityAssessment:
    policy = default_policy(trade_style)
    feature_engine = DeterministicFeatureEngine(builtin_feature_registry())
    contexts: dict[str, AnalysisContext] = {}
    timeframes: list[TimeframeFeatureContext] = []
    primary_bundle: FeatureBundle | None = None
    for interval in intervals:
        try:
            context = _acquire_context(builder, symbol, interval, lookback_days)
            contexts[interval] = context
            bundle = feature_engine.compute(
                context, _requests(policy, BaselineEvidenceSource.PRIMARY, interval)
            )
            if interval == intervals[0]:
                primary_bundle = bundle
            timeframes.append(timeframe_feature_context(interval, bundle))
        except (
            AnalysisContextError,
            FeatureError,
            TIAFDataError,
            ValidationError,
            ValueError,
        ) as exc:
            timeframes.append(_unavailable_timeframe(interval, requested_at, str(exc)))
    if primary_bundle is None:
        primary_bundle = _bundle(
            f"missing-{symbol}-{intervals[0]}",
            symbol,
            requested_at,
            (),
            f"missing:{symbol}:{intervals[0]}:{requested_at.isoformat()}",
        )
    mtf_context = multi_timeframe_context(symbol, tuple(timeframes), created_at=requested_at)
    mtf_engine = MultiTimeframeFeatureEngine()
    mtf_results = tuple(
        mtf_engine.compute_one(mtf_context, request)
        for request in _requests(policy, BaselineEvidenceSource.MULTI_TIMEFRAME, None)
    )
    mtf_bundle = _bundle(
        mtf_context.context_id,
        symbol,
        requested_at,
        mtf_results,
        f"mtf:{mtf_context.context_id}",
    )
    relative_bundle: FeatureBundle | None = None
    indicator_bundle: IndicatorBundle | None = None
    benchmark_context: AnalysisContext | None = None
    subject_context = contexts.get(intervals[0])
    if subject_context is not None:
        try:
            indicator_bundle = IndicatorEngine(builtin_indicator_registry()).calculate_many(
                _indicator_requests(policy, intervals[0]),
                subject_context,
            )
        except (IndicatorError, ValidationError, ValueError):
            indicator_bundle = None
    if benchmark_symbol is not None and subject_context is not None:
        try:
            benchmark_context = _acquire_context(
                builder, benchmark_symbol, intervals[0], lookback_days
            )
            relative_context = relative_strength_context(
                subject_context,
                benchmark_context,
                BenchmarkReference(symbol=benchmark_symbol, role=BenchmarkRole.CUSTOM),
                interval=intervals[0],
            )
            relative_engine = RelativeStrengthEngine()
            relative_results = tuple(
                relative_engine.compute_one(relative_context, request)
                for request in _requests(policy, BaselineEvidenceSource.RELATIVE, intervals[0])
            )
            relative_bundle = _bundle(
                relative_context.context_id,
                symbol,
                relative_context.created_at,
                relative_results,
                f"relative:{relative_context.context_id}",
            )
        except (AnalysisContextError, FeatureError, TIAFDataError, ValidationError, ValueError):
            relative_bundle = None
    freshness = [
        EvidenceFreshness(
            source=BaselineEvidenceSource.PRIMARY,
            state=_history_freshness(subject_context),
        ),
        EvidenceFreshness(
            source=BaselineEvidenceSource.MULTI_TIMEFRAME,
            state=min(
                (_history_freshness(context) for context in contexts.values()),
                default=FreshnessState.UNKNOWN,
                key=lambda item: {
                    FreshnessState.STALE: 0,
                    FreshnessState.UNKNOWN: 1,
                    FreshnessState.AGING: 2,
                    FreshnessState.FRESH: 3,
                }[item],
            ),
        ),
    ]
    if relative_bundle is not None:
        relative_states = (
            _history_freshness(subject_context),
            _history_freshness(benchmark_context),
        )
        freshness.append(
            EvidenceFreshness(
                source=BaselineEvidenceSource.RELATIVE,
                state=min(
                    relative_states,
                    key=lambda item: {
                        FreshnessState.STALE: 0,
                        FreshnessState.UNKNOWN: 1,
                        FreshnessState.AGING: 2,
                        FreshnessState.FRESH: 3,
                    }[item],
                ),
            )
        )
    if indicator_bundle is not None:
        freshness.append(
            EvidenceFreshness(
                source=BaselineEvidenceSource.INDICATOR,
                state=_history_freshness(subject_context),
            )
        )
    request = DeterministicBaselineRequest(
        request_id=str(
            uuid5(NAMESPACE_URL, f"tiaf:a2.9-request:{symbol}:{requested_at.isoformat()}")
        ),
        subject=symbol,
        trade_style=trade_style,
        horizon=Horizon(label=trade_style.value.casefold()),
        primary_timeframe=intervals[0],
        supporting_timeframes=intervals[1:],
        primary_features=primary_bundle,
        indicators=indicator_bundle,
        relative_features=relative_bundle,
        multi_timeframe_context=mtf_context,
        multi_timeframe_features=mtf_bundle,
        evidence_freshness=tuple(freshness),
        policy_version=policy.policy_version,
        requested_at=requested_at,
        metadata={"benchmark_symbol": benchmark_symbol},
    )
    return BaselineEngine((policy,)).assess(request)


def main() -> int:
    """Run a read-only single or batch evidence acquisition and baseline assessment."""
    args = parse_args()
    requested_at = datetime.now(TIAF_TIMEZONE)
    try:
        builder = AnalysisContextBuilder(
            DhanInstrumentResolver(),
            DhanMarketDataProvider(),
            DataFetchCoordinator(scheduler=ProviderScheduler(dhan_rate_policy_registry())),
            clock=lambda: requested_at,
        )
        assessments = tuple(
            _assess_symbol(
                builder,
                symbol,
                args.benchmark_map.get(symbol, args.benchmark),
                args.timeframes,
                args.lookback_days,
                args.horizon,
                requested_at,
            )
            for symbol in args.symbols
        )
        ranking = (
            rank_opportunities(assessments, top_n=args.top_n)
            if args.rank or len(assessments) > 1
            else None
        )
        if args.json:
            payload: dict[str, object] = {
                "assessments": assessments,
                "ranking": ranking,
            }
            print(TypeAdapter(dict[str, object]).dump_json(payload, indent=2).decode())
        else:
            print("\n\n".join(summarize_assessment(item) for item in assessments))
            if ranking is not None:
                print("\n\n" + summarize_ranking(ranking))
    except (BaselineError, TIAFDataError, ValidationError, ValueError) as exc:
        print(f"Read-only deterministic-baseline smoke failed: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
