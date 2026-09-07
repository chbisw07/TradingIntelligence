"""Same-evidence alternate-policy comparison tests."""

import pytest

from tiaf.baseline import BaselinePolicy, ComponentName, default_policy
from tiaf.contracts import TradeStyle
from tiaf.evaluation import compare_policies

from ._support import frozen_case


def test_same_policy_comparison_has_no_deltas() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    snapshot, _ = frozen_case(policy=policy)
    comparison = compare_policies(snapshot, policy, policy)
    assert comparison.old_assessment == comparison.new_assessment
    assert comparison.opportunity_delta == 0.0
    assert all(item.delta in {None, 0.0} for item in comparison.component_deltas)
    assert comparison.added_reasons == comparison.removed_reasons == ()


def test_synthetic_policy_change_has_exact_deltas_without_mutating_evidence() -> None:
    old_policy = default_policy(TradeStyle.POSITIONAL)
    snapshot, _ = frozen_case(policy=old_policy)
    before = snapshot.model_dump_json()
    rules = tuple(
        rule.model_copy(update={"scale": 12.0})
        if rule.rule_id == "momentum.return_5"
        else rule
        for rule in old_policy.evidence_rules
    )
    new_policy = BaselinePolicy.model_validate(
        old_policy.model_copy(
            update={
                "policy_id": "synthetic-test-policy",
                "policy_version": "test-1.1",
                "evidence_rules": rules,
            }
        ).model_dump()
    )
    comparison = compare_policies(snapshot, old_policy, new_policy)
    momentum = next(
        item
        for item in comparison.component_deltas
        if item.component is ComponentName.MOMENTUM
    )
    assert momentum.delta is not None
    assert momentum.new_score is not None and momentum.old_score is not None
    assert momentum.delta == pytest.approx(momentum.new_score - momentum.old_score)
    assert comparison.opportunity_delta == pytest.approx(
        comparison.new_opportunity_score - comparison.old_opportunity_score
    )
    assert snapshot.model_dump_json() == before
    assert comparison.old_policy_version == "1.0"
    assert comparison.new_policy_version == "test-1.1"
