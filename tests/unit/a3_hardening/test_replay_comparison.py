"""Offline replay, verification dispositions and closed observational mappings."""

import socket
from typing import Any

import pytest
from pydantic import ValidationError

from tiaf.a3_hardening import (
    DirectionAxis,
    DisagreementClass,
    OpportunityAxis,
    PolicyComparisonError,
    VerificationDisposition,
    compare_a2_a3,
    compare_a3_policy,
    direction_axis,
    opportunity_axis,
    replay_a3_package,
    verify_a3_package,
)
from tiaf.agents import AgentRuntime, AgentStance
from tiaf.baseline import BaselineDirection, CandidateClass
from tiaf.market_intelligence import MarketIntelligenceRouter
from tiaf.service.opportunity_intelligence import OpportunityState, default_policy
from tiaf.workflows import OrchestrationCoordinator

from ._support import full_a2_package, operational_variant, package_for


@pytest.mark.parametrize(
    ("a2", "a3", "comparable", "expected"),
    [
        (BaselineDirection.POSITIVE, AgentStance.POSITIVE, True, DirectionAxis.ALIGNED),
        (BaselineDirection.POSITIVE, AgentStance.NEGATIVE, True, DirectionAxis.OPPOSED),
        (
            BaselineDirection.POSITIVE,
            AgentStance.INSUFFICIENT_EVIDENCE,
            True,
            DirectionAxis.A3_INSUFFICIENT,
        ),
        (
            BaselineDirection.NEUTRAL,
            AgentStance.POSITIVE,
            True,
            DirectionAxis.A3_DIRECTIONAL_A2_NEUTRAL,
        ),
        (
            BaselineDirection.CONFLICTED,
            AgentStance.MIXED,
            True,
            DirectionAxis.A2_CONFLICTED,
        ),
        (None, AgentStance.POSITIVE, True, DirectionAxis.NON_COMPARABLE),
        (BaselineDirection.POSITIVE, AgentStance.POSITIVE, False, DirectionAxis.NON_COMPARABLE),
    ],
)
def test_direction_axis_is_closed(
    a2: BaselineDirection | None,
    a3: AgentStance,
    comparable: bool,
    expected: DirectionAxis,
) -> None:
    assert direction_axis(a2, a3, comparable=comparable) is expected


@pytest.mark.parametrize(
    ("a2", "a3", "comparable", "expected"),
    [
        (
            CandidateClass.EARLY_OPPORTUNITY,
            OpportunityState.OPPORTUNITY,
            True,
            OpportunityAxis.ALIGNED_OPPORTUNITY,
        ),
        (
            CandidateClass.MATURE_AVOID_CHASE,
            OpportunityState.WAIT,
            True,
            OpportunityAxis.ALIGNED_TIMING_CAUTION,
        ),
        (
            CandidateClass.NO_TRADE,
            OpportunityState.WATCH,
            True,
            OpportunityAxis.BASELINE_NO_TRADE_WATCH,
        ),
        (
            CandidateClass.NO_TRADE,
            OpportunityState.NO_TRADE,
            True,
            OpportunityAxis.BASELINE_NO_TRADE_PRESERVED,
        ),
        (
            CandidateClass.EARLY_OPPORTUNITY,
            OpportunityState.WAIT,
            True,
            OpportunityAxis.A3_RESTRICTION_ADDED,
        ),
        (
            CandidateClass.EARLY_OPPORTUNITY,
            OpportunityState.INSUFFICIENT_EVIDENCE,
            True,
            OpportunityAxis.A3_EVIDENCE_INSUFFICIENT,
        ),
        (
            CandidateClass.MATURE_AVOID_CHASE,
            OpportunityState.AVOID,
            True,
            OpportunityAxis.SEMANTIC_DIVERGENCE,
        ),
        (None, OpportunityState.WATCH, False, OpportunityAxis.NON_COMPARABLE),
    ],
)
def test_opportunity_axis_is_closed(
    a2: CandidateClass | None,
    a3: OpportunityState,
    comparable: bool,
    expected: OpportunityAxis,
) -> None:
    assert opportunity_axis(a2, a3, comparable=comparable) is expected


def test_recorded_replay_reconstructs_children_and_consumes_no_market_resources() -> None:
    replay = replay_a3_package(package_for())
    assert replay.semantic_match
    assert replay.replay_usage.llm_calls == replay.replay_usage.tool_calls == 0
    assert replay.replay_usage.input_tokens == replay.replay_usage.output_tokens == 0
    assert replay.replay_usage.cost_units == 0


def test_recorded_replay_and_comparison_cannot_execute_upstream(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def denied(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("external/upstream execution forbidden")

    monkeypatch.setattr(AgentRuntime, "run", denied)
    monkeypatch.setattr(MarketIntelligenceRouter, "execute", denied)
    monkeypatch.setattr(OrchestrationCoordinator, "invoke", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)
    package = package_for()
    assert replay_a3_package(package).semantic_match
    assert compare_a2_a3(package).a3.intelligence_id


def test_verification_distinguishes_full_projection_and_recorded_only() -> None:
    projected = verify_a3_package(package_for())
    full = verify_a3_package(full_a2_package())
    assert projected.components[0].disposition is VerificationDisposition.NOT_APPLICABLE
    assert full.components[0].disposition is VerificationDisposition.REEXECUTED_DETERMINISTIC
    assert projected.components[1].disposition is VerificationDisposition.RECORDED_ONLY
    assert projected.components[2].disposition is VerificationDisposition.REEXECUTED_DETERMINISTIC
    assert projected.passed and full.passed


def test_policy_comparison_is_new_record_and_unsupported_policy_is_explicit() -> None:
    package = package_for()
    same = compare_a3_policy(package, default_policy())
    assert same.exact_match and not same.differences
    unsupported = default_policy().model_copy(update={"version": "99.0"})
    with pytest.raises(PolicyComparisonError, match="candidate"):
        compare_a3_policy(package, unsupported)


@pytest.mark.parametrize(
    ("case", "opportunity"),
    [
        ("aligned", OpportunityAxis.ALIGNED_OPPORTUNITY),
        ("baseline_watch", OpportunityAxis.BASELINE_NO_TRADE_WATCH),
        ("baseline_no_trade", OpportunityAxis.BASELINE_NO_TRADE_PRESERVED),
        ("poor_timing", OpportunityAxis.A3_RESTRICTION_ADDED),
        ("sparse_kaynes", OpportunityAxis.A3_EVIDENCE_INSUFFICIENT),
    ],
)
def test_comparison_preserves_both_sides_and_observes_divergence(
    case: str, opportunity: OpportunityAxis
) -> None:
    comparison = compare_a2_a3(package_for(case))
    assert comparison.a2.assessment_id and comparison.a2.evidence_fingerprint
    assert comparison.a3.intelligence_id and comparison.a3.fingerprint
    assert comparison.opportunity_axis is opportunity
    assert not {
        "winner",
        "better",
        "alpha",
        "confidence_boost",
        "merged_score",
    } & set(comparison.model_dump())


def test_no_trade_watch_retains_eligibility_basis_and_coexisting_labels() -> None:
    comparison = compare_a2_a3(package_for("baseline_watch"))
    assert comparison.a2.candidate_class is CandidateClass.NO_TRADE
    assert comparison.a2.eligibility_basis == "NOT_CAPTURED"
    assert DisagreementClass.A3_MORE_PERMISSIVE in comparison.disagreements
    assert DisagreementClass.BASELINE_NO_TRADE_PRESERVED in comparison.disagreements


def test_information_additions_are_attributed_statuses_not_superiority_claims() -> None:
    comparison = compare_a2_a3(package_for("poor_timing"))
    assert all(
        item.status.value in {"PRESENT", "ABSENT", "UNKNOWN"}
        for item in comparison.information_additions
    )
    serialized = comparison.model_dump_json().lower()
    assert not any(term in serialized for term in ("better", "profit", "superior", "winner"))


def test_operational_adapter_parity_preserves_comparison_semantics() -> None:
    serial, graph = operational_variant()
    left, right = compare_a2_a3(serial), compare_a2_a3(graph)
    assert left.fingerprint == right.fingerprint
    assert left.a2 == right.a2 and left.a3 == right.a3


def test_comparison_record_rejects_semantic_tampering() -> None:
    comparison = compare_a2_a3(package_for())
    with pytest.raises(ValidationError, match="fingerprint"):
        comparison.__class__.model_validate(
            comparison.model_dump() | {"opportunity_axis": OpportunityAxis.SEMANTIC_DIVERGENCE}
        )
