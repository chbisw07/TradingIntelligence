"""Acceptance tests for immutable semantic contract collections."""

import json
import operator
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from tiaf.contracts import (
    ActionStrength,
    AgentDecisionBundle,
    AgentOpinion,
    ContractModel,
    DataQuality,
    DataSnapshot,
    DirectionPolicy,
    FreshnessState,
    OpportunityAction,
    OpportunityAssessment,
    OpportunityRequest,
    PositionAction,
    PositionAssessment,
    TradeDirection,
    TradeStyle,
)

NOW = datetime(2026, 9, 5, 4, 30, tzinfo=UTC)


def semantic_collection_models() -> list[tuple[ContractModel, tuple[str, ...]]]:
    """Build every contract containing finalized semantic sequences from lists."""
    request = OpportunityRequest.model_validate(
        {
            "universe": ["reliance", "TCS", "RELIANCE"],
            "trade_style": TradeStyle.DAY,
            "horizon": {"label": "intraday"},
            "direction_policy": DirectionPolicy.BOTH,
            "top_n": 5,
            "requested_at": NOW,
        }
    )
    snapshot = DataSnapshot.model_validate(
        {
            "snapshot_id": "snapshot-001",
            "symbol": "RELIANCE",
            "observed_at": NOW,
            "freshness": FreshnessState.FRESH,
            "quality": DataQuality.GOOD,
            "providers": ["provider-a", "provider-b"],
        }
    )
    opinion = AgentOpinion.model_validate(
        {
            "agent_name": "structure-v1",
            "agent_role": "technical_structure",
            "subject_id": "RELIANCE",
            "stance": TradeDirection.BULLISH,
            "confidence": 0.72,
            "summary": "Constructive structure.",
            "evidence_ids": ["evidence-001"],
            "concerns": ["Nearby resistance."],
            "supporting_factors": ["Relative strength."],
            "freshness": FreshnessState.FRESH,
            "produced_at": NOW,
        }
    )
    bundle = AgentDecisionBundle.model_validate(
        {
            "decision_id": "decision-001",
            "subject_id": "RELIANCE",
            "horizon": {"label": "intraday"},
            "opinions": [opinion.model_dump(mode="json")],
            "consensus_direction": TradeDirection.BULLISH,
            "confidence": 0.68,
            "disagreement_score": 20,
            "recommendation_summary": "Constructive but bounded view.",
            "evidence_ids": ["evidence-001"],
            "created_at": NOW,
        }
    )
    opportunity = OpportunityAssessment.model_validate(
        {
            "assessment_id": "assessment-001",
            "request_id": "request-001",
            "symbol": "RELIANCE",
            "direction": TradeDirection.NEUTRAL,
            "action": OpportunityAction.NO_TRADE,
            "horizon": {"label": "intraday"},
            "opportunity_score": 20,
            "confidence": 0.8,
            "summary": "Insufficient entry quality.",
            "evidence_ids": ["evidence-001"],
            "created_at": NOW,
        }
    )
    position = PositionAssessment.model_validate(
        {
            "assessment_id": "assessment-002",
            "request_id": "request-002",
            "position_id": "position-001",
            "underlying": "RELIANCE",
            "action": PositionAction.HOLD,
            "strength": ActionStrength.MODERATE,
            "confidence": 0.7,
            "forward_view": "The forward view remains constructive.",
            "changed_since_previous": ["Volatility declined."],
            "reasons": ["Structure remains intact."],
            "evidence_ids": ["evidence-001"],
            "created_at": NOW,
        }
    )
    return [
        (request, ("universe",)),
        (snapshot, ("providers",)),
        (opinion, ("evidence_ids", "concerns", "supporting_factors")),
        (bundle, ("opinions", "evidence_ids")),
        (opportunity, ("evidence_ids",)),
        (position, ("changed_since_previous", "reasons", "evidence_ids")),
    ]


def test_list_input_becomes_immutable_semantic_tuples() -> None:
    for model, fields in semantic_collection_models():
        for field in fields:
            collection = getattr(model, field)
            assert isinstance(collection, tuple)
            assert not hasattr(collection, "append")
            assert not hasattr(collection, "remove")


def test_tuple_in_place_addition_does_not_mutate_contract_collection() -> None:
    request = semantic_collection_models()[0][0]
    assert isinstance(request, OpportunityRequest)
    original = request.universe
    combined = operator.iadd(original, ("INFY",))

    assert request.universe is original
    assert request.universe == ("RELIANCE", "TCS")
    assert combined == ("RELIANCE", "TCS", "INFY")


def test_frozen_model_rejects_semantic_collection_replacement() -> None:
    request = semantic_collection_models()[0][0]

    with pytest.raises(ValidationError, match="frozen"):
        setattr(request, "universe", ("INFY",))


def test_semantic_tuples_dump_as_json_arrays_and_round_trip() -> None:
    for model, fields in semantic_collection_models():
        json_mode = model.model_dump(mode="json")
        json_text = json.loads(model.model_dump_json())
        restored = type(model).model_validate_json(model.model_dump_json())

        assert restored == model
        for field in fields:
            assert isinstance(json_mode[field], list)
            assert isinstance(json_text[field], list)
            assert isinstance(getattr(restored, field), tuple)
