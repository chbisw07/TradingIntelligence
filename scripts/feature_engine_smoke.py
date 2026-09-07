"""Build one read-only A1 context and inspect deterministic A2 features."""

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
    parser.add_argument(
        "--extended",
        action="store_true",
        help="include the A2.2 price, return, range, and volatility feature set",
    )
    parser.add_argument(
        "--trend",
        action="store_true",
        help="include completed-history A2.3 trend and structure features",
    )
    parser.add_argument(
        "--annualization-factor",
        type=float,
        help="explicit realized-volatility factor; defaults to 252 only for 1d",
    )
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


def _extended_requests(
    interval: str,
    annualization_factor: float | None = None,
) -> tuple[FeatureRequest, ...]:
    normalized_interval = FeatureRequest(
        feature_id="history.bar_count", interval=interval
    ).interval
    factor = annualization_factor
    if factor is None:
        if normalized_interval != "1d":
            raise ValueError(
                "--annualization-factor is required for extended intraday features"
            )
        factor = 252.0
    return (
        FeatureRequest(feature_id="price.current"),
        FeatureRequest(feature_id="price.previous_close", interval=interval),
        FeatureRequest(feature_id="price.change_percent", interval=interval),
        FeatureRequest(feature_id="price.position_in_day_range", interval=interval),
        *(
            FeatureRequest(
                feature_id="return.percent",
                parameters=(("bars", bars),),
                interval=interval,
            )
            for bars in (1, 5, 20)
        ),
        FeatureRequest(feature_id="range.bar_percent", interval=interval),
        FeatureRequest(feature_id="range.body_percent", interval=interval),
        FeatureRequest(feature_id="range.true_range", interval=interval),
        FeatureRequest(
            feature_id="volatility.atr",
            parameters=(("period", 14),),
            interval=interval,
        ),
        FeatureRequest(
            feature_id="volatility.atr_percent",
            parameters=(("period", 14),),
            interval=interval,
        ),
        FeatureRequest(
            feature_id="volatility.realized",
            parameters=(("bars", 20), ("annualization_factor", factor)),
            interval=interval,
        ),
        *(
            FeatureRequest(
                feature_id=feature_id,
                parameters=(("bars", 20),),
                interval=interval,
            )
            for feature_id in (
                "price.rolling_high",
                "price.rolling_low",
                "price.distance_from_rolling_high_percent",
                "price.distance_from_rolling_low_percent",
                "return.max_drawdown_percent",
                "return.max_runup_percent",
            )
        ),
        FeatureRequest(
            feature_id="range.move_over_atr",
            parameters=(("atr_period", 14),),
            interval=interval,
        ),
    )


def _trend_requests(interval: str) -> tuple[FeatureRequest, ...]:
    return (
        *(
            FeatureRequest(
                feature_id=feature_id,
                parameters=(("period", period),),
                interval=interval,
            )
            for feature_id in ("trend.sma", "trend.ema")
            for period in (10, 20, 50)
        ),
        *(
            FeatureRequest(
                feature_id=feature_id,
                parameters=(("period", 20),),
                interval=interval,
            )
            for feature_id in (
                "trend.distance_from_sma_percent",
                "trend.distance_from_ema_percent",
            )
        ),
        *(
            FeatureRequest(
                feature_id=feature_id,
                parameters=(("fast_period", 10), ("slow_period", 20)),
                interval=interval,
            )
            for feature_id in (
                "trend.sma_spread_percent",
                "trend.ema_spread_percent",
            )
        ),
        *(
            FeatureRequest(
                feature_id=feature_id,
                parameters=(("bars", 20),),
                interval=interval,
            )
            for feature_id in (
                "trend.linear_slope",
                "trend.linear_slope_percent",
                "trend.linear_r2",
                "trend.directional_efficiency",
                "trend.signed_efficiency",
                "trend.up_close_fraction",
                "trend.down_close_fraction",
                "trend.flat_close_fraction",
                "structure.higher_high_fraction",
                "structure.higher_low_fraction",
                "structure.lower_high_fraction",
                "structure.lower_low_fraction",
                "structure.position_in_rolling_range",
            )
        ),
        FeatureRequest(feature_id="trend.consecutive_up_closes", interval=interval),
        FeatureRequest(feature_id="trend.consecutive_down_closes", interval=interval),
        *(
            FeatureRequest(
                feature_id=feature_id,
                parameters=(("atr_period", 14), ("ma_period", 20)),
                interval=interval,
            )
            for feature_id in (
                "trend.distance_from_sma_atr",
                "trend.distance_from_ema_atr",
            )
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
    """Acquire factual context through A1, then derive deterministic A2 features."""
    args = parse_args()
    try:
        base_requests = (
            _extended_requests(
                args.history_interval,
                annualization_factor=args.annualization_factor,
            )
            if args.extended
            else _requests(args.history_interval)
        )
        requests = (
            (*base_requests, *_trend_requests(args.history_interval))
            if args.trend
            else base_requests
        )
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
