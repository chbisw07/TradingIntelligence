"""A2.9 policy and immutable-contract acceptance tests."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from tiaf.baseline import (
    BaselineEvidenceSource,
    BaselinePolicy,
    DeterministicBaselineRequest,
    EvidenceFreshness,
    default_policy,
    summarize_policy,
)
from tiaf.contracts import FreshnessState, TradeStyle

from ._support import baseline_request


@pytest.mark.parametrize("style", tuple(TradeStyle))
def test_policy_is_versioned_and_json_round_trips(style: TradeStyle) -> None:
    policy = default_policy(style)
    assert policy.policy_version == "1.0"
    assert BaselinePolicy.model_validate(policy.model_dump(mode="json")) == policy
    with pytest.raises(ValidationError):
        policy.policy_version = "2.0"


def test_policy_declares_every_rule_weight_transform_and_threshold() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    assert len(policy.evidence_rules) == 31
    assert all(rule.weight > 0 and rule.transform for rule in policy.evidence_rules)
    assert sum(item.direction_weight for item in policy.component_weights) == pytest.approx(1.0)
    assert sum(item.opportunity_weight for item in policy.component_weights) == pytest.approx(1.0)
    assert policy.metadata["status"] == "generic_engineering_baseline_not_fitted"


@pytest.mark.parametrize("style", tuple(TradeStyle))
def test_policy_inspection_exposes_all_rules_weights_and_thresholds(style: TradeStyle) -> None:
    policy = default_policy(style)
    rendered = summarize_policy(policy)
    assert all(rendered.count(f"    {rule.rule_id}\n") == 1 for rule in policy.evidence_rules)
    assert rendered.count("max points:") == 31
    assert "CONFLICTED: positive >= 42 and negative >= 42" in rendered
    assert "NEUTRAL: max(positive, negative) < 52" in rendered
    assert "TOP_MOVER: momentum >= 70 and participation >= 52" in rendered
    assert "Effective maxima are full-evidence GOOD-quality points" in rendered


def test_invalid_policy_weights_and_thresholds_are_rejected() -> None:
    policy = default_policy(TradeStyle.DAY).model_dump(mode="python")
    policy["component_weights"] = []
    with pytest.raises(ValidationError, match="component weights"):
        BaselinePolicy.model_validate(policy)
    policy = default_policy(TradeStyle.DAY).model_dump(mode="python")
    policy["classification_thresholds"]["early_opportunity_score"] = 1
    with pytest.raises(ValidationError, match="early threshold"):
        BaselinePolicy.model_validate(policy)


def test_request_requires_horizon_and_explicit_freshness() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    payload = baseline_request(policy).model_dump(mode="python")
    payload.pop("horizon")
    with pytest.raises(ValidationError):
        DeterministicBaselineRequest.model_validate(payload)
    payload = baseline_request(policy).model_dump(mode="python")
    payload["evidence_freshness"] = ()
    with pytest.raises(ValidationError, match="freshness"):
        DeterministicBaselineRequest.model_validate(payload)


def test_request_is_immutable_accepts_lists_and_serializes_arrays() -> None:
    request = baseline_request(default_policy(TradeStyle.POSITIONAL))
    payload = request.model_dump(mode="json")
    payload["supporting_timeframes"] = ["1H", "15m"]
    payload["evidence_freshness"] = list(payload["evidence_freshness"])
    rebuilt = DeterministicBaselineRequest.model_validate(payload)
    assert rebuilt.supporting_timeframes == ("1h", "15m")
    assert isinstance(rebuilt.model_dump(mode="json")["supporting_timeframes"], list)
    with pytest.raises(ValidationError):
        rebuilt.subject = "OTHER"


def test_request_normalizes_utc_timestamp_to_kolkata_and_rejects_naive() -> None:
    request = baseline_request(default_policy(TradeStyle.DAY))
    payload = request.model_dump(mode="python")
    payload["requested_at"] = datetime(2026, 9, 7, 6, 30, tzinfo=UTC)
    rebuilt = DeterministicBaselineRequest.model_validate(payload)
    assert rebuilt.requested_at.isoformat().endswith("+05:30")
    payload["requested_at"] = datetime(2026, 9, 7, 12, 0)
    with pytest.raises(ValidationError, match="timezone-aware"):
        DeterministicBaselineRequest.model_validate(payload)


def test_request_rejects_freshness_for_unsupplied_source() -> None:
    request = baseline_request(default_policy(TradeStyle.DAY), include_relative=False)
    payload = request.model_dump(mode="python")
    payload["evidence_freshness"] = (
        *request.evidence_freshness,
        EvidenceFreshness(
            source=BaselineEvidenceSource.RELATIVE,
            state=FreshnessState.FRESH,
        ),
    )
    with pytest.raises(ValidationError, match="every supplied"):
        DeterministicBaselineRequest.model_validate(payload)
