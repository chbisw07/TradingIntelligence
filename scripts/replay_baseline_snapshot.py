"""Replay a captured A2.9 snapshot entirely offline and compare exact output."""

import argparse
from datetime import datetime
from pathlib import Path

from tiaf.baseline import default_policy
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.evaluation import (
    CorpusError,
    EvaluationError,
    ReplayRequest,
    load_case,
    replay,
    summarize_replay,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    """Load normalized JSON and invoke only provider-neutral replay code."""
    try:
        case = load_case(parse_args().input)
        policy = default_policy(case.snapshot.trade_style)
        result = replay(
            ReplayRequest(
                snapshot=case.snapshot,
                policy=policy,
                expected_assessment=case.run_record.assessment,
                replay_time=datetime.now(TIAF_TIMEZONE),
            )
        )
        original = case.run_record.assessment
        print("ORIGINAL")
        print(f"Direction                   : {original.market_state.direction.value}")
        print(f"Opportunity                 : {original.opportunity_score}")
        print(f"Class                       : {original.candidate_class.value}")
        print(f"Assessment ID               : {original.assessment_id}")
        print()
        print(summarize_replay(result))
        return 0 if result.exact_match else 1
    except (CorpusError, EvaluationError, ValueError) as exc:
        print(f"Offline replay failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
