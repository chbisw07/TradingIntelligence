"""Build read-only history and inspect first-class deterministic indicators."""

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
from tiaf.indicators import (
    IndicatorBundle,
    IndicatorEngine,
    IndicatorError,
    IndicatorRequest,
    builtin_indicator_registry,
    summarize_indicator_bundle,
)

_DEFAULT_PARAMETERS: dict[str, dict[str, int | float]] = {
    "supertrend": {"period": 10, "multiplier": 3.0},
    "rsi": {"period": 14},
    "macd": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
    "adx": {"period": 14},
    "bollinger": {"period": 20, "stddev_multiplier": 2.0},
    "donchian": {"period": 20},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", default="RELIANCE")
    parser.add_argument("--history-interval", default="1d")
    parser.add_argument("--lookback-days", type=int, default=180)
    parser.add_argument(
        "--indicator",
        action="append",
        help="indicator ID or comma-separated IDs; repeatable",
    )
    parser.add_argument("--all", action="store_true", help="run the default indicator pack")
    parser.add_argument("--repeat", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _selected_ids(raw: list[str] | None, *, all_indicators: bool) -> tuple[str, ...]:
    if all_indicators or not raw:
        return tuple(_DEFAULT_PARAMETERS)
    selected = tuple(
        item.strip().casefold()
        for group in raw
        for item in group.split(",")
        if item.strip()
    )
    unknown = tuple(item for item in selected if item not in _DEFAULT_PARAMETERS)
    if unknown:
        raise ValueError(f"unknown indicator selection: {', '.join(unknown)}")
    if not selected:
        raise ValueError("at least one indicator must be selected")
    return selected


def _requests(
    interval: str,
    selected: tuple[str, ...],
) -> tuple[IndicatorRequest, ...]:
    return tuple(
        IndicatorRequest(
            indicator_id=indicator_id,
            parameters=tuple(_DEFAULT_PARAMETERS[indicator_id].items()),
            interval=interval,
        )
        for indicator_id in selected
    )


def _print_bundle(
    bundle: IndicatorBundle, *, as_json: bool, label: str | None = None
) -> None:
    if label is not None:
        print(label)
    print(
        bundle.model_dump_json(indent=2)
        if as_json
        else summarize_indicator_bundle(bundle)
    )


def main() -> int:
    """Acquire completed history through A1, then calculate indicators."""
    args = parse_args()
    try:
        selected = _selected_ids(args.indicator, all_indicators=args.all)
        requests = _requests(args.history_interval, selected)
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
            include_quote=False,
            require_quote=False,
            history_interval=args.history_interval,
            history_lookback_days=args.lookback_days,
            history_freshness=FreshnessRequirement(
                fresh_for_seconds=3600,
                aging_for_seconds=86_400,
            ),
        )
        engine = IndicatorEngine(builtin_indicator_registry())
        first_context = builder.build(
            args.symbol,
            requirements,
            source_system="indicator_engine_smoke",
        )
        first = engine.calculate_many(requests, first_context)
        _print_bundle(
            first,
            as_json=args.json,
            label="FIRST INDICATOR BUILD" if args.repeat else None,
        )
        if args.repeat:
            second_context = builder.build(
                args.symbol,
                requirements,
                source_system="indicator_engine_smoke",
            )
            second = engine.calculate_many(requests, second_context)
            print()
            _print_bundle(second, as_json=args.json, label="SECOND INDICATOR BUILD")
    except (
        AnalysisContextError,
        IndicatorError,
        TIAFDataError,
        ValidationError,
        ValueError,
    ) as exc:
        print(f"Read-only indicator smoke failed: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
