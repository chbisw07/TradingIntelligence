"""Transparent A5.1 recommendation and transition scenarios."""

from datetime import timedelta

import pytest

from tiaf.a5 import (
    A5ExecutionStatus,
    A5InputIntegrityError,
    MonitoringTriggerKind,
    PositionRecommendation,
    PositionRiskPosture,
    PositionSignalKind,
    ProtectionIntentKind,
    ReferenceLevel,
    ReferenceLevelKind,
    RemainingOpportunity,
    ThesisHealth,
    deterministic_policy,
    evaluate_position,
)
from tiaf.data import InstrumentType

from ._support import NOW, a4_result, request, signal, snapshot


def test_fresh_supported_equity_starts_capital_at_risk_and_maintains() -> None:
    result = evaluate_position(request()).result
    assert result.status is A5ExecutionStatus.COMPLETE
    assert result.posture is PositionRiskPosture.CAPITAL_AT_RISK
    assert result.thesis_health is ThesisHealth.INTACT
    assert result.recommendation is PositionRecommendation.MAINTAIN
    assert result.protection_intent.kind is ProtectionIntentKind.NO_PROTECTION_CHANGE


def test_cited_milestone_reduces_risk_and_recommends_protection() -> None:
    item = signal(PositionSignalKind.STRUCTURAL_MILESTONE)
    result = evaluate_position(request(signals=(item,))).result
    assert result.posture is PositionRiskPosture.RISK_REDUCED
    assert result.recommendation is PositionRecommendation.PROTECT
    assert result.protection_intent.kind is ProtectionIntentKind.TIGHTEN_PROTECTION
    assert item.evidence_refs[0] in result.evidence_refs


def test_favorable_continuation_activates_profit_protection_and_trailing() -> None:
    item = signal(PositionSignalKind.FAVORABLE_CONTINUATION)
    result = evaluate_position(request(signals=(item,))).result
    assert result.posture is PositionRiskPosture.PROFIT_PROTECTION_ACTIVE
    assert result.recommendation is PositionRecommendation.TRAIL_PROTECTION
    assert result.protection_intent.kind is ProtectionIntentKind.TRAIL_STRUCTURALLY
    assert "FREE" not in result.model_dump_json()


def test_thesis_weakening_reduces_risk() -> None:
    result = evaluate_position(
        request(signals=(signal(PositionSignalKind.THESIS_WEAKENING),))
    ).result
    assert result.thesis_health is ThesisHealth.WEAKENED
    assert result.recommendation is PositionRecommendation.REDUCE_RISK


def test_cited_a4_invalidation_recommends_exit_without_execution() -> None:
    linked = a4_result()
    invalidation = signal(PositionSignalKind.THESIS_INVALIDATION, a4=linked)
    result = evaluate_position(request(a4=linked, signals=(invalidation,))).result
    assert result.thesis_health is ThesisHealth.INVALIDATED
    assert result.recommendation is PositionRecommendation.EXIT_RECOMMENDED
    assert result.protection_intent.kind is ProtectionIntentKind.EXIT_IF_INVALIDATED
    assert result.authority_statement == "ADVISORY_ONLY_TRADEMONITOR_DECIDES_BROKER_EXECUTION"


def test_unresolved_invalidation_reference_fails_closed() -> None:
    linked = a4_result()
    invalidation = signal(PositionSignalKind.THESIS_INVALIDATION, a4=linked).model_copy(
        update={"condition_ref": "a4-invalidation:unknown"}
    )
    with pytest.raises(A5InputIntegrityError, match="condition"):
        evaluate_position(request(a4=linked, signals=(invalidation,)))


def test_successor_strengthens_and_weakens_without_rewriting_original() -> None:
    original_wait = a4_result("WAIT")
    supportive = a4_result()
    strengthened = evaluate_position(
        request(a4=original_wait, successor=supportive)
    ).result
    assert strengthened.thesis_health is ThesisHealth.STRENGTHENED
    original_supportive_json = supportive.model_dump_json()
    weakened = evaluate_position(
        request(a4=supportive, successor=a4_result("WAIT"))
    ).result
    assert weakened.thesis_health is ThesisHealth.WEAKENED
    assert weakened.recommendation is PositionRecommendation.REDUCE_RISK
    assert supportive.model_dump_json() == original_supportive_json


def test_a4_conflict_and_adverse_dispositions_remain_conservative() -> None:
    conflicted = evaluate_position(request(a4=a4_result("CONFLICTED"))).result
    assert conflicted.recommendation is PositionRecommendation.WAIT_FOR_CONFIRMATION
    assert conflicted.contradictions
    adverse = evaluate_position(request(a4=a4_result("AVOID"))).result
    assert adverse.recommendation is PositionRecommendation.EXIT_RECOMMENDED


def test_expired_derivative_never_maintains_and_near_expiry_is_surfaced() -> None:
    expired = snapshot(
        kind=InstrumentType.CALL_OPTION,
        expiry=NOW.date() - timedelta(days=1),
    )
    expired_result = evaluate_position(request(position_snapshot=expired)).result
    assert expired_result.recommendation is PositionRecommendation.EXIT_RECOMMENDED
    assert expired_result.failure_codes[0].value == "EXPIRED_INSTRUMENT"
    near = snapshot(
        kind=InstrumentType.FUTURE,
        expiry=NOW.date() + timedelta(days=2),
    )
    near_result = evaluate_position(request(position_snapshot=near)).result
    assert near_result.recommendation is PositionRecommendation.WATCH_CLOSELY
    assert any(
        item.trigger_kind is MonitoringTriggerKind.EXPIRY_TIME
        for item in near_result.monitoring_needs
    )


def test_intraday_exit_window_is_advisory_time_risk() -> None:
    from tiaf.a5 import PositionProduct

    near_exit = snapshot(
        product=PositionProduct.INTRADAY,
        mandatory_exit_at=NOW + timedelta(minutes=20),
    )
    near_result = evaluate_position(request(position_snapshot=near_exit)).result
    assert near_result.recommendation is PositionRecommendation.WATCH_CLOSELY
    reached_snapshot = near_exit.model_copy(
        update={
            "snapshot_id": "position-snapshot:intraday-exit-reached",
            "snapshot_at": NOW + timedelta(minutes=24),
        }
    )
    reached = evaluate_position(
        request(
            position_snapshot=reached_snapshot,
            as_of=NOW + timedelta(minutes=25),
        )
    ).result
    assert reached.recommendation is PositionRecommendation.EXIT_RECOMMENDED


@pytest.mark.parametrize(
    ("kind", "expected"),
    (
        (PositionSignalKind.REMAINING_ROOM_STRONG, RemainingOpportunity.STRONG),
        (PositionSignalKind.REMAINING_ROOM_MODERATE, RemainingOpportunity.MODERATE),
        (PositionSignalKind.REMAINING_ROOM_LIMITED, RemainingOpportunity.LIMITED),
        (PositionSignalKind.REMAINING_ROOM_EXHAUSTED, RemainingOpportunity.EXHAUSTED),
    ),
)
def test_remaining_room_is_only_projected_from_cited_signal(
    kind: PositionSignalKind,
    expected: RemainingOpportunity,
) -> None:
    result = evaluate_position(request(signals=(signal(kind),))).result
    assert result.remaining_opportunity is expected


def test_structural_level_is_preserved_only_when_supplied_and_non_executable() -> None:
    level = ReferenceLevel(
        level_id="reference-level:support",
        kind=ReferenceLevelKind.SUPPORT,
        value=98.5,
        evidence_refs=("evidence:support",),
        observed_at=NOW,
    )
    base = snapshot().model_copy(update={"supplied_levels": (level,)})
    supplied = evaluate_position(request(position_snapshot=base)).result
    assert supplied.protection_intent.reference_levels == (level,)
    assert supplied.protection_intent.reference_levels[0].executable is False
    unsupplied = evaluate_position(request()).result
    assert not unsupplied.protection_intent.reference_levels


def test_expression_refresh_seam_selects_no_contract_or_quantity() -> None:
    result = evaluate_position(
        request(signals=(signal(PositionSignalKind.EXPRESSION_UNSUITABLE),))
    ).result
    assert result.protection_intent.kind is ProtectionIntentKind.EXPRESSION_REFRESH_REQUIRED
    payload = result.model_dump(mode="json")
    assert not {"replacement_strike", "replacement_expiry", "order_quantity"} & set(payload)


def test_no_a7_probability_and_known_zero_model_usage() -> None:
    result = evaluate_position(request()).result
    payload = result.model_dump(mode="json")
    assert "probability" not in str(payload).casefold()
    assert result.usage.model_calls == 0
    assert result.usage.input_tokens == result.usage.output_tokens == 0
    assert result.usage.model_cost_knowledge == "KNOWN_ZERO"


def test_identical_input_has_stable_semantic_and_run_fingerprints() -> None:
    value = request()
    first = evaluate_position(value)
    second = evaluate_position(value)
    assert first.result.semantic_fingerprint == second.result.semantic_fingerprint
    assert first.fingerprint == second.fingerprint


def test_previous_result_creates_successor_lineage_and_changed_inputs() -> None:
    original = evaluate_position(request()).result
    successor_snapshot = snapshot(snapshot_at=NOW + timedelta(minutes=4)).model_copy(
        update={"snapshot_id": "position-snapshot:successor"}
    )
    successor = evaluate_position(
        request(
            position_snapshot=successor_snapshot,
            previous=original,
            successor_reason="POSITION_SNAPSHOT_CHANGED",
        )
    ).result
    assert successor.previous_result_ref == original.result_id
    assert successor.previous_posture is original.posture
    assert successor.successor_reason == "POSITION_SNAPSHOT_CHANGED"
    assert successor_snapshot.snapshot_id in successor.changed_input_refs
    assert successor.watch_mandate.predecessor_ref == original.watch_mandate.mandate_id
    assert successor.watch_mandate.revision == 2


def test_policy_identity_mismatch_fails_before_evaluation() -> None:
    value = request().model_copy(update={"policy_version": "other"})
    with pytest.raises(A5InputIntegrityError, match="policy mismatch"):
        evaluate_position(value, policy=deterministic_policy())
