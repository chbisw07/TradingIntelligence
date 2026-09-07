"""Capture one live normalized A2.9 evidence snapshot and immutable decision record."""

import argparse
from datetime import datetime
from pathlib import Path

from baseline_opportunity_smoke import _build_request
from pydantic import ValidationError

from tiaf import __version__
from tiaf.baseline import BaselineEngine, BaselineError, default_policy
from tiaf.context import AnalysisContextBuilder, AnalysisContextError
from tiaf.contracts import TradeStyle
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data import TIAFDataError, normalize_interval, normalize_symbol
from tiaf.data.providers.dhan import (
    DhanInstrumentResolver,
    DhanMarketDataProvider,
    dhan_rate_policy_registry,
)
from tiaf.data.runtime import DataFetchCoordinator, ProviderScheduler
from tiaf.evaluation import (
    CapturedBaselineCase,
    CorpusError,
    create_evidence_snapshot,
    create_run_record,
    save_case,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", required=True)
    parser.add_argument(
        "--horizon",
        choices=tuple(item.value for item in TradeStyle),
        required=True,
    )
    parser.add_argument("--benchmark")
    parser.add_argument("--timeframes", default="1d,1h,15m")
    parser.add_argument("--lookback-days", type=int, default=180)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    args.symbol = normalize_symbol(args.symbol)
    args.benchmark = normalize_symbol(args.benchmark) if args.benchmark else None
    args.horizon = TradeStyle(args.horizon)
    args.timeframes = tuple(
        dict.fromkeys(
            normalize_interval(item) for item in args.timeframes.split(",") if item.strip()
        )
    )
    if not args.timeframes or args.lookback_days <= 0:
        parser.error("timeframes must be non-empty and lookback-days must be positive")
    return args


def main() -> int:
    """Acquire once, freeze normalized evidence, assess, and write separate objects."""
    args = parse_args()
    decision_time = datetime.now(TIAF_TIMEZONE)
    try:
        builder = AnalysisContextBuilder(
            DhanInstrumentResolver(),
            DhanMarketDataProvider(),
            DataFetchCoordinator(scheduler=ProviderScheduler(dhan_rate_policy_registry())),
            clock=lambda: decision_time,
        )
        request = _build_request(
            builder,
            args.symbol,
            args.benchmark,
            args.timeframes,
            args.lookback_days,
            args.horizon,
            decision_time,
        )
        policy = default_policy(args.horizon)
        snapshot = create_evidence_snapshot(
            request,
            policy_id=policy.policy_id,
            producer_version=__version__,
            benchmark_symbol=args.benchmark,
            snapshot_created_at=decision_time,
        )
        assessment = BaselineEngine((policy,)).assess(snapshot.decision_request)
        run = create_run_record(snapshot, assessment, recorded_at=decision_time)
        save_case(
            args.output,
            CapturedBaselineCase(snapshot=snapshot, run_record=run),
            overwrite=args.overwrite,
        )
        print(f"Captured                    : {args.output}")
        print(f"Direction                   : {assessment.market_state.direction.value}")
        print(f"Opportunity                 : {assessment.opportunity_score}")
        print(f"Class                       : {assessment.candidate_class.value}")
        print(f"Assessment ID               : {assessment.assessment_id}")
        print(f"Evidence fingerprint        : {snapshot.fingerprint}")
    except (
        AnalysisContextError,
        BaselineError,
        CorpusError,
        TIAFDataError,
        ValidationError,
        ValueError,
    ) as exc:
        print(f"Read-only snapshot capture failed: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
