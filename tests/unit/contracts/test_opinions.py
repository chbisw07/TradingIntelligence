"""Tests for agent opinions and non-executable decision bundles."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from tiaf.contracts import (
    AgentDecisionBundle,
    AgentOpinion,
    FreshnessState,
    Horizon,
    TradeDirection,
)

NOW = datetime(2026, 9, 5, 4, 30, tzinfo=UTC)


def agent_opinion(**changes: object) -> AgentOpinion:
    values: dict[str, object] = {
        "agent_name": "structure-v1",
        "agent_role": "technical_structure",
        "subject_id": "RELIANCE",
        "stance": TradeDirection.BULLISH,
        "confidence": 0.72,
        "summary": "Constructive structure within the requested horizon.",
        "evidence_ids": ["evidence-001"],
        "freshness": FreshnessState.FRESH,
        "produced_at": NOW,
    }
    values.update(changes)
    return AgentOpinion.model_validate(values)


def test_agent_opinion_rejects_invalid_confidence() -> None:
    with pytest.raises(ValidationError):
        agent_opinion(confidence=1.1)


def test_agent_opinion_requires_valid_until_after_produced_at() -> None:
    with pytest.raises(ValidationError, match="later than produced_at"):
        agent_opinion(valid_until=NOW)

    opinion = agent_opinion(valid_until=NOW + timedelta(minutes=15))
    assert opinion.valid_until == NOW + timedelta(minutes=15)


def test_decision_bundle_rejects_disagreement_score_above_100() -> None:
    with pytest.raises(ValidationError):
        AgentDecisionBundle(
            decision_id="decision-001",
            subject_id="RELIANCE",
            horizon=Horizon(label="intraday"),
            opinions=(agent_opinion(),),
            consensus_direction=TradeDirection.BULLISH,
            confidence=0.65,
            disagreement_score=100.01,
            recommendation_summary="Evidence is constructive but not authoritative.",
            created_at=NOW,
        )


def test_decision_bundle_has_no_broker_action() -> None:
    bundle = AgentDecisionBundle(
        decision_id="decision-001",
        subject_id="RELIANCE",
        horizon=Horizon(label="intraday"),
        opinions=(agent_opinion(),),
        consensus_direction=TradeDirection.BULLISH,
        confidence=0.65,
        disagreement_score=20,
        recommendation_summary="Evidence is constructive but not authoritative.",
        created_at=NOW,
    )

    assert not hasattr(bundle, "broker_action")
