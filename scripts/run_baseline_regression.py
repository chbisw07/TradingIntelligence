"""Run exact A2.9 replay checks over captured files or a filesystem corpus."""

import argparse
from datetime import datetime
from pathlib import Path

from tiaf.baseline import BaselinePolicy, default_policy
from tiaf.contracts import TradeStyle
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.evaluation import (
    CorpusError,
    ReplayCorpusStore,
    load_case,
    run_regression,
    summarize_regression,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        action="append",
        default=[],
        help="captured snapshot/run file (repeatable)",
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        help=(
            "replay corpus directory containing persisted snapshots and "
            "decision_records.jsonl"
        ),
    )
    args = parser.parse_args()
    if not args.input and args.corpus is None:
        parser.error("supply at least one --input or --corpus")
    return args


def main() -> int:
    """Replay a corpus without importing any provider or resolver module."""
    args = parse_args()
    try:
        cases = tuple(load_case(path) for path in args.input)
        if args.corpus is not None:
            cases = (*cases, *ReplayCorpusStore(args.corpus).cases())

        def resolve(policy_id: str, policy_version: str) -> BaselinePolicy:
            policies = tuple(default_policy(style) for style in TradeStyle)
            match = next(
                (
                    policy
                    for policy in policies
                    if policy.policy_id == policy_id and policy.policy_version == policy_version
                ),
                None,
            )
            if match is None:
                raise ValueError(f"unsupported policy: {policy_id}/{policy_version}")
            return match

        report = run_regression(
            cases,
            resolve,
            replay_time=datetime.now(TIAF_TIMEZONE),
        )
        print(summarize_regression(report))
        return 0 if report.fail_count == 0 else 1
    except (CorpusError, ValueError) as exc:
        print(f"Regression run failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
