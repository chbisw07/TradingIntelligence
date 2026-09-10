"""Accounting, failure lineage, injected faults and closure-readiness truth."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from tiaf.a3_hardening import (
    ClosureReadiness,
    CostKnowledge,
    CostMeasure,
    DegradationStatus,
    EvidenceStatus,
    FailureCategory,
    FailureCode,
    MilestoneEvidence,
    UsageDisposition,
    closure_readiness_record,
    compare_a2_a3,
    evaluate_a3_hardening,
    failure_event,
    summarize_a3_cost,
    summarize_a3_failures,
)

from ._support import (
    NOW,
    budget_exhausted_package,
    fallback_package,
    held_reservation_package,
    operational_variant,
    package_for,
)


def test_cost_knowledge_never_serializes_unknown_or_unpriced_as_zero() -> None:
    for knowledge in (CostKnowledge.UNKNOWN, CostKnowledge.UNPRICED):
        measure = CostMeasure(knowledge=knowledge, source_refs=("attempt",))
        payload = measure.model_dump(mode="json")
        assert payload["amount"] is None and payload["currency"] is None
    with pytest.raises(ValidationError, match="cannot carry"):
        CostMeasure(knowledge=CostKnowledge.UNKNOWN, amount=0, currency="USD")
    with pytest.raises(ValidationError, match="positive"):
        CostMeasure(knowledge=CostKnowledge.KNOWN_NONZERO, amount=0, currency="USD")


def test_leaf_usage_reconciles_once_and_replay_usage_is_separate() -> None:
    summary = summarize_a3_cost(package_for())
    included = tuple(item for item in summary.attributions if item.included_in_original_total)
    assert (
        sum(item.usage.tool_calls for item in included)
        == summary.original_captured_usage.tool_calls
    )
    assert (
        sum(item.usage.llm_calls for item in included) == summary.original_captured_usage.llm_calls
    )
    assert summary.replay_execution_usage.tool_calls == 0
    assert summary.provider_monetary_cost.knowledge is CostKnowledge.KNOWN_ZERO
    assert summary.model_monetary_cost.knowledge is CostKnowledge.KNOWN_ZERO


def test_fallback_attempt_is_charged_separately_and_failure_lineage_survives() -> None:
    package = fallback_package()
    cost = summarize_a3_cost(package)
    failures = summarize_a3_failures(package)
    details = tuple(
        item for item in cost.attributions if item.phase == "MARKET_INTELLIGENCE_PROVIDER_ATTEMPT"
    )
    assert len(details) == 2
    assert [item.provider_id for item in details] == ["tapetide", "yahoo"]
    assert details[1].disposition is UsageDisposition.FALLBACK
    assert cost.fallback_attempts == 1
    assert all(not item.included_in_original_total for item in details)
    assert cost.provider_monetary_cost.knowledge is CostKnowledge.UNPRICED
    event = next(item for item in failures.events if item.code is FailureCode.RATE_LIMITED)
    assert event.provider_id == "tapetide"
    assert event.original_code == "RATE_LIMIT"
    assert event.original_message_ref


def test_budget_denial_and_required_gaps_are_not_hidden() -> None:
    package = budget_exhausted_package()
    failures = summarize_a3_failures(package)
    assert FailureCode.BUDGET_EXHAUSTED in {item.code for item in failures.events}
    assert failures.degradation.status is DegradationStatus.INSUFFICIENT_EVIDENCE
    assert failures.degradation.required_impact
    assert summarize_a3_cost(package).original_captured_usage.tool_calls == 0


def test_unknown_completion_retains_held_reservation_without_double_debit() -> None:
    package = held_reservation_package()
    cost = summarize_a3_cost(package)
    assert cost.original_held_usage.tool_calls == 1
    assert any(not item.included_in_original_total for item in cost.attributions)


@pytest.mark.parametrize(
    ("case", "status"),
    [
        ("aligned", DegradationStatus.NONE),
        ("stale", DegradationStatus.INSUFFICIENT_EVIDENCE),
        ("abstain", DegradationStatus.INSUFFICIENT_EVIDENCE),
        ("unknown_fno", DegradationStatus.PARTIAL),
        ("non_fno", DegradationStatus.NONE),
        ("sparse_kaynes", DegradationStatus.INSUFFICIENT_EVIDENCE),
    ],
)
def test_captured_degradation_is_projected_without_shadow_synthesis(
    case: str, status: DegradationStatus
) -> None:
    package = package_for(case)
    summary = summarize_a3_failures(package)
    comparison = compare_a2_a3(package)
    assert summary.degradation.status is status
    assert summary.degradation.a39_state is comparison.a3.state


def test_fault_matrix_has_22_truthfully_synthetic_typed_cases() -> None:
    data = json.loads(
        Path("tests/fixtures/a3_hardening/fault_matrix.json").read_text(encoding="utf-8")
    )
    assert data["origin"] == "SYNTHETIC"
    assert data["fixture_builder_version"]
    assert len(data["cases"]) == 22
    assert len({item["id"] for item in data["cases"]}) == 22
    events = tuple(
        failure_event(
            category=FailureCategory(item["category"]),
            code=FailureCode(item["code"]),
            phase="DETERMINISTIC_FAULT_INJECTION",
            original_type="SyntheticFault",
            original_code=item["id"],
            original_message=f"synthetic offline fixture: {item['id']}",
            terminal=False,
            affected_capabilities=(item["id"],),
        )
        for item in data["cases"]
    )
    assert all(item.original_message_ref and item.original_code for item in events)


def test_failure_event_retains_unknown_child_identity_as_unclassified() -> None:
    event = failure_event(
        category=FailureCategory.SPECIALIST,
        code=FailureCode.UNCLASSIFIED,
        phase="SPECIALIST_INVOCATION",
        original_type="FutureChildError",
        original_code="FUTURE_77",
        original_message="sanitized future error",
        terminal=False,
    )
    assert event.code is FailureCode.UNCLASSIFIED
    assert event.original_type == "FutureChildError"
    assert event.original_code == "FUTURE_77"


def test_operational_timing_does_not_change_cost_or_failure_semantics() -> None:
    serial, graph = operational_variant()
    assert summarize_a3_cost(serial).fingerprint == summarize_a3_cost(graph).fingerprint
    assert summarize_a3_failures(serial).fingerprint == summarize_a3_failures(graph).fingerprint


def test_hardening_evaluation_composes_children_without_new_intelligence() -> None:
    result = evaluate_a3_hardening(package_for(), evaluated_at=NOW)
    assert result.passed
    assert len(result.checks) == 5
    assert all(item.status is EvidenceStatus.PASS for item in result.checks)


def test_closure_readiness_requires_every_required_item_to_pass() -> None:
    passed = MilestoneEvidence(
        evidence_id="tests",
        category="QUALITY_GATE",
        status=EvidenceStatus.PASS,
        required=True,
        artifact_refs=("pytest",),
        observed_at=NOW,
        note="offline test evidence",
    )
    unknown = passed.model_copy(update={"evidence_id": "live", "status": EvidenceStatus.UNKNOWN})
    ready = closure_readiness_record(
        (passed,),
        unresolved_deferrals=("DEF-049",),
        known_risks=("future model replay",),
        assessed_at=NOW,
    )
    not_ready = closure_readiness_record(
        (passed, unknown), unresolved_deferrals=(), known_risks=(), assessed_at=NOW
    )
    assert ready.readiness is ClosureReadiness.READY_FOR_CLOSURE_REVIEW
    assert not_ready.readiness is ClosureReadiness.NOT_READY
