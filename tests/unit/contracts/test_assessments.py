"""Tests for opportunity and position assessments."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from tiaf.contracts import (
    ActionStrength,
    Horizon,
    OpportunityAction,
    OpportunityAssessment,
    PositionAction,
    PositionAssessment,
    TradeDirection,
)

NOW = datetime(2026, 9, 5, 4, 30, tzinfo=UTC)


def opportunity_assessment(**changes: object) -> OpportunityAssessment:
    values: dict[str, object] = {
        "assessment_id": "assessment-001",
        "request_id": "request-001",
        "symbol": "RELIANCE",
        "direction": TradeDirection.NEUTRAL,
        "action": OpportunityAction.NO_TRADE,
        "horizon": Horizon(label="intraday"),
        "opportunity_score": 10,
        "confidence": 0.8,
        "summary": "Evidence does not support an entry.",
        "created_at": NOW,
    }
    values.update(changes)
    return OpportunityAssessment.model_validate(values)


def test_no_trade_with_neutral_direction_is_valid() -> None:
    assessment = opportunity_assessment()

    assert assessment.action is OpportunityAction.NO_TRADE
    assert assessment.direction is TradeDirection.NEUTRAL


def test_opportunity_rejects_score_above_100() -> None:
    with pytest.raises(ValidationError):
        opportunity_assessment(opportunity_score=100.1)


def test_opportunity_rejects_reversed_expected_move_range() -> None:
    with pytest.raises(ValidationError, match="expected_move_max_pct"):
        opportunity_assessment(expected_move_min_pct=4.5, expected_move_max_pct=2.0)


def test_opportunity_rejects_invalid_validity_window() -> None:
    with pytest.raises(ValidationError, match="later than created_at"):
        opportunity_assessment(valid_until=NOW)


def test_position_exit_urgent_is_valid_without_entry_thesis() -> None:
    assessment = PositionAssessment(
        assessment_id="assessment-002",
        request_id="request-002",
        position_id="position-001",
        underlying=" reliance ",
        action=PositionAction.EXIT,
        strength=ActionStrength.URGENT,
        confidence=0.91,
        forward_view="Current conditions no longer support retaining the position.",
        reasons=("Material forward risk increased.",),
        created_at=NOW,
    )

    assert assessment.underlying == "RELIANCE"
    assert assessment.action is PositionAction.EXIT
    assert assessment.strength is ActionStrength.URGENT
    assert not hasattr(assessment, "entry_thesis")
