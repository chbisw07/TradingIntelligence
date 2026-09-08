"""A3.1 contract, stance, confidence, and compatibility coverage."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from tiaf.agents import (
    AgentConfidence,
    AgentOpinionV2,
    AgentRunStatus,
    AgentStance,
    AgentUsage,
    BaselineAgreement,
    EmpiricallyCalibratedConfidence,
    PolicyDerivedConfidence,
    agent_opinion_v1_to_v2,
    agent_opinion_v2_to_v1,
)
from tiaf.agents.errors import AgentOutputValidationError
from tiaf.contracts import AgentOpinion as AgentOpinionV1
from tiaf.contracts import DataQuality, FreshnessState, TradeDirection

from ._support import NOW, agent_opinion, agent_request, evidence_pack


def test_request_is_frozen_accepts_lists_and_serializes_tuples_as_arrays() -> None:
    request = agent_request()
    with pytest.raises(ValidationError, match="frozen"):
        request.subject = "TCS"
    payload = request.model_dump(mode="json")
    assert isinstance(payload["a2_context_ids"], list)
    assert isinstance(payload["allowed_capabilities"], list)
    assert payload["created_at"].endswith("+05:30")
    assert type(request).model_validate(payload) == request


def test_request_normalizes_aware_utc_and_rejects_naive_timestamp() -> None:
    payload = agent_request().model_dump(mode="python")
    payload["created_at"] = datetime(2026, 9, 8, 6, 30, tzinfo=UTC)
    request = type(agent_request()).model_validate(payload)
    assert request.created_at.isoformat().endswith("+05:30")
    payload["created_at"] = datetime(2026, 9, 8, 12, 0)
    with pytest.raises(ValidationError, match="timezone-aware"):
        type(request).model_validate(payload)


@pytest.mark.parametrize(
    ("stance", "status"),
    [
        (AgentStance.POSITIVE, AgentRunStatus.SUCCESS),
        (AgentStance.NEGATIVE, AgentRunStatus.SUCCESS),
        (AgentStance.NEUTRAL, AgentRunStatus.SUCCESS),
        (AgentStance.MIXED, AgentRunStatus.PARTIAL),
        (AgentStance.INSUFFICIENT_EVIDENCE, AgentRunStatus.INSUFFICIENT_EVIDENCE),
        (AgentStance.ABSTAIN, AgentRunStatus.ABSTAINED),
    ],
)
def test_every_specialist_stance_has_non_execution_semantics(
    stance: AgentStance,
    status: AgentRunStatus,
) -> None:
    assert agent_opinion(stance=stance, status=status).stance is stance


def test_infrastructure_failure_cannot_be_encoded_as_market_opinion() -> None:
    payload = agent_opinion().model_dump(mode="python")
    payload["status"] = AgentRunStatus.FAILED
    with pytest.raises(ValidationError, match="infrastructure failures"):
        AgentOpinionV2.model_validate(payload)


def test_confidence_dimensions_are_independent_and_optional() -> None:
    confidence = AgentConfidence(
        evidence_coverage=0.75,
        evidence_quality=DataQuality.PARTIAL,
        policy_derived=PolicyDerivedConfidence(
            value=0.6,
            policy_id="policy",
            policy_version="1.0",
        ),
        empirically_calibrated=EmpiricallyCalibratedConfidence(
            value=0.55,
            calibration_id="cal-1",
            method="isotonic-held-out",
            cohort="POSITIONAL",
            sample_size=200,
            evaluated_at=NOW,
        ),
    )
    assert confidence.self_reported is None
    assert confidence.empirically_calibrated is not None
    assert confidence.empirically_calibrated.value == 0.55


def test_self_reported_confidence_requires_an_explicit_basis() -> None:
    with pytest.raises(ValidationError, match="appear together"):
        AgentConfidence(
            evidence_coverage=1.0,
            evidence_quality=DataQuality.GOOD,
            self_reported=0.7,
        )


def test_a0_opinion_remains_schema_1_and_losslessly_round_trips_through_v2() -> None:
    old = AgentOpinionV1.model_validate(
        {
            "agent_name": "Legacy technical",
            "agent_role": "technical",
            "subject_id": "RELIANCE",
            "stance": TradeDirection.BULLISH,
            "confidence": 0.7,
            "summary": "Legacy bounded opinion.",
            "evidence_ids": ["a2-technical-1"],
            "concerns": ["Late extension"],
            "supporting_factors": ["Trend"],
            "freshness": FreshnessState.FRESH,
            "produced_at": NOW,
        }
    )
    converted = agent_opinion_v1_to_v2(
        old,
        request=agent_request(),
        evidence_pack=evidence_pack(),
        opinion_id="v2-opinion",
        specialist_version="1.0",
        policy_version="1.0",
        baseline_agreement=BaselineAgreement.AGREES,
    )
    assert old.schema_version == "1.0"
    assert converted.schema_version == "2.0"
    assert converted.stance is AgentStance.POSITIVE
    assert converted.confidence.self_reported == 0.7
    assert agent_opinion_v2_to_v1(converted) == old


def test_native_v2_opinion_rejects_lossy_v1_conversion() -> None:
    with pytest.raises(AgentOutputValidationError, match="losslessly"):
        agent_opinion_v2_to_v1(agent_opinion())


def test_opinion_collections_are_immutable_json_arrays() -> None:
    opinion = agent_opinion()
    with pytest.raises(AttributeError):
        opinion.reason_codes.append("NEW")  # type: ignore[attr-defined]
    payload = opinion.model_dump(mode="json")
    assert isinstance(payload["evidence_claims"], list)
    assert isinstance(payload["supporting_evidence_ids"], list)
    assert AgentOpinionV2.model_validate(payload) == opinion


def test_confidence_is_not_required_to_claim_probability() -> None:
    opinion = agent_opinion(usage=AgentUsage())
    assert opinion.confidence.self_reported is None
    assert opinion.confidence.empirically_calibrated is None
