"""Frozen-ranking association and descriptive aggregate tests."""

from datetime import timedelta

import pytest

from tiaf.baseline import CandidateClass, default_policy, rank_opportunities
from tiaf.contracts import TradeStyle
from tiaf.evaluation import (
    RegressionCheckResult,
    RegressionStatus,
    aggregate_metrics,
    create_run_record,
    evaluate_outcome,
    evaluate_ranking,
)

from ..baseline._support import NOW
from ._support import frozen_case, future_path


def test_ranking_outcomes_preserve_original_rank_eligibility_and_no_trade() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    captures = (
        frozen_case(subject="AAA", policy=policy),
        frozen_case(subject="BBB", policy=policy),
        frozen_case(subject="CCC", profile="neutral", policy=policy),
    )
    ranking = rank_opportunities(tuple(run.assessment for _, run in captures), top_n=2)
    outcomes = []
    for snapshot, initial_run in captures:
        run = create_run_record(
            snapshot,
            initial_run.assessment,
            recorded_at=NOW,
            ranking=ranking,
        )
        outcomes.append(
            evaluate_outcome(
                run,
                future_path(run),
                evaluated_at=NOW + timedelta(days=3),
            )
        )
    result = evaluate_ranking(
        ranking,
        tuple(outcomes),
        evaluated_at=NOW + timedelta(days=3),
    )
    assert tuple(item.original_rank for item in result.items) == (1, 2, None)
    assert tuple(item.subject for item in result.items) == ("AAA", "BBB", "CCC")
    assert result.top_1.count == 1
    assert result.top_n.count == 2
    assert result.top_n.average_ending_return_percent == pytest.approx(2.0)
    assert result.eligible_population.count == 2
    assert result.no_trade_population.count == 1
    no_trade = result.items[-1]
    assert no_trade.original_candidate_class is CandidateClass.NO_TRADE
    assert not no_trade.originally_eligible
    assert no_trade.metrics.mfe_percent is None
    check = RegressionCheckResult(
        check_id="check",
        status=RegressionStatus.PASS,
        snapshot_id=captures[0][0].snapshot_id,
        run_id=outcomes[0].run_id,
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
        evidence_fingerprint=outcomes[0].evidence_fingerprint,
    )
    aggregate = aggregate_metrics(
        tuple(
            create_run_record(snapshot, run.assessment, recorded_at=NOW)
            for snapshot, run in captures
        ),
        (check,),
        tuple(outcomes),
    )
    assert aggregate.runs_evaluated == 3
    assert aggregate.replay_pass_count == 1
    assert aggregate.observed_outcomes.count == 3
