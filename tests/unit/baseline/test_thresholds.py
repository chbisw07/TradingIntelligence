"""Exact A2.9 transform and threshold-boundary tests."""

from typing import Any

import pytest

from tiaf.baseline import (
    BaselineDirection,
    BaselineEvidenceSource,
    ComponentName,
    EvidenceRule,
    EvidenceSelector,
    RuleRole,
    TransformKind,
    default_policy,
)
from tiaf.baseline.scoring import _market_direction, _transform
from tiaf.contracts import TradeStyle


def _rule(transform: TransformKind, **values: Any) -> EvidenceRule:
    return EvidenceRule(
        rule_id="boundary.rule",
        component=ComponentName.VOLATILITY_SUITABILITY,
        selector=EvidenceSelector(
            source=BaselineEvidenceSource.PRIMARY,
            evidence_id="boundary.value",
        ),
        role=RuleRole.SUITABILITY,
        transform=transform,
        weight=1.0,
        **values,
    )


def test_direction_threshold_boundaries_are_inclusive() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    assert _market_direction(policy, 51.999999, 0.0) is BaselineDirection.NEUTRAL
    assert _market_direction(policy, 52.0, 0.0) is BaselineDirection.POSITIVE
    assert _market_direction(policy, 0.0, 52.0) is BaselineDirection.NEGATIVE
    assert _market_direction(policy, 42.0, 42.0) is BaselineDirection.CONFLICTED


def test_direction_absolute_floor_precedes_margin_decision() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    assert _market_direction(policy, 15.319647, 43.604477) is BaselineDirection.NEUTRAL
    assert _market_direction(policy, 15.319647, 52.0) is BaselineDirection.NEGATIVE


def test_direction_conflict_precedes_absolute_floor_and_margin() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    assert _market_direction(policy, 42.0, 42.0) is BaselineDirection.CONFLICTED
    assert _market_direction(policy, 60.0, 53.0) is BaselineDirection.CONFLICTED
    assert _market_direction(policy, 60.0, 52.0) is BaselineDirection.CONFLICTED


def test_triangle_transform_has_exact_floor_target_and_ceiling() -> None:
    rule = _rule(TransformKind.TRIANGLE, floor=1.0, target=2.0, ceiling=4.0)
    assert _transform(rule, 1.0) == 0.0
    assert _transform(rule, 2.0) == 1.0
    assert _transform(rule, 4.0) == 0.0
    assert _transform(rule, 3.0) == pytest.approx(0.5)


def test_room_transform_keeps_bounded_post_breakout_credit() -> None:
    rule = _rule(
        TransformKind.POSITIVE_ROOM,
        scale=3.0,
        ceiling=1.5,
        post_boundary_credit=0.2,
    )
    assert _transform(rule, -3.0) == 1.0
    assert _transform(rule, 0.0) == 0.0
    assert _transform(rule, 0.75) == pytest.approx(0.1)
    assert _transform(rule, 1.5) == 0.0
