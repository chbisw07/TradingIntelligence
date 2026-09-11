"""Required deterministic challenge/arbitration disposition scenarios."""

import pytest

from tiaf.a4 import (
    A4Disposition,
    A4ExecutionStatus,
    A4RunRecord,
    ChallengeFamily,
    ChallengeStatus,
    evaluate_projection,
)
from tiaf.source_semantics import A4SemanticInputProjection

from ._support import (
    clean_projection,
    reseal,
    with_excluded_evidence,
    with_gap,
    with_resolved_scope_mismatch,
    with_source_dependence,
    with_stale_evidence,
    with_state,
    with_unknown_authority,
    with_unresolved_conflict,
    with_unsupported_assumption,
)


def evaluate(projection: A4SemanticInputProjection | None = None) -> A4RunRecord:
    value = projection or clean_projection()
    return evaluate_projection(value, evaluated_at=value.header.evidence_as_of)


def test_clean_opportunity_is_supportive_without_action_semantics() -> None:
    record = evaluate()
    assert record.result.disposition is A4Disposition.SUPPORTIVE
    assert record.result.execution_status is A4ExecutionStatus.COMPLETE
    assert record.result.primary_thesis.thesis_id in record.result.surviving_thesis_refs
    payload = record.result.model_dump(mode="json")
    assert not {"action", "buy", "sell", "entry", "execution_approval"} & set(payload)


@pytest.mark.parametrize(
    ("projection", "family"),
    (
        (with_unknown_authority(), ChallengeFamily.SOURCE_BASIS),
        (with_source_dependence(), ChallengeFamily.SOURCE_BASIS),
    ),
)
def test_critical_source_weakness_and_copy_dependence_downgrade(
    projection: A4SemanticInputProjection, family: ChallengeFamily
) -> None:
    record = evaluate(projection)
    assert record.result.disposition is A4Disposition.INSUFFICIENT_EVIDENCE
    assert any(item.family is family for item in record.result.challenge_findings)
    assert record.result.evidence_needs


def test_stale_catalyst_is_wait_not_factual_conflict() -> None:
    record = evaluate(with_stale_evidence())
    assert record.result.disposition is A4Disposition.WAIT
    assert any(
        item.family is ChallengeFamily.FRESHNESS
        for item in record.result.challenge_findings
    )


def test_point_in_time_excluded_evidence_is_visible_but_never_used_as_support() -> None:
    record = evaluate(with_excluded_evidence())
    finding = next(
        item
        for item in record.result.challenge_findings
        if item.reason_code == "EVIDENCE_EXCLUDED_BY_PROJECTION"
    )
    assert finding.status is ChallengeStatus.QUALIFIED
    assert record.result.disposition is A4Disposition.SUPPORTIVE
    assert "evidence:outside-cutoff" not in record.result.primary_thesis.support_refs
    assert all(
        item.family is not ChallengeFamily.THESIS_TENSION
        for item in record.result.challenge_findings
    )


def test_positive_context_with_poor_timing_is_wait_not_factual_conflict() -> None:
    record = evaluate(with_state("WAIT"))
    assert record.result.disposition is A4Disposition.WAIT
    assert record.result.counter_thesis is not None
    assert record.result.counter_thesis.conclusion_relation == "TIMING_ALTERNATIVE"
    assert all(
        item.family is not ChallengeFamily.THESIS_TENSION
        for item in record.result.challenge_findings
    )


def test_authoritative_comparable_conflict_remains_conflicted() -> None:
    record = evaluate(with_unresolved_conflict())
    assert record.result.disposition is A4Disposition.CONFLICTED
    assert record.result.counter_thesis is not None
    assert len(record.result.surviving_thesis_refs) == 2
    assert any(item.dispute_refs for item in record.result.challenge_findings)


def test_a2_no_trade_cannot_be_overridden_by_a3_contextual_support() -> None:
    record = evaluate(with_state("OPPORTUNITY", a2_class="NO_TRADE"))
    assert record.result.disposition is A4Disposition.NO_TRADE
    premise = next(
        item
        for item in record.result.premises
        if item.premise_id == "a4-premise:captured-a39-observation"
    )
    assert premise.support_state.value == "TRUE"
    assert record.result.original_a2_assessment_ref


def test_matched_a2_a3_directional_divergence_is_visible_not_a_vote() -> None:
    record = evaluate(with_state("OPPORTUNITY", a2_direction="NEGATIVE"))
    assert record.result.disposition is A4Disposition.SUPPORTIVE
    finding = next(
        item
        for item in record.result.challenge_findings
        if item.reason_code == "A2_A3_DIRECTIONAL_DIVERGENCE"
    )
    assert finding.family is ChallengeFamily.BASELINE_DIVERGENCE
    assert finding.status is ChallengeStatus.QUALIFIED


def test_missing_required_evidence_is_insufficient() -> None:
    record = evaluate(with_gap(required=True))
    assert record.result.disposition is A4Disposition.INSUFFICIENT_EVIDENCE
    assert record.result.evidence_needs[0].status.value == "OPEN"


def test_optional_gap_is_preserved_without_blocking_support() -> None:
    record = evaluate(with_gap(required=False))
    assert record.result.disposition is A4Disposition.SUPPORTIVE
    assert record.result.challenge_findings[0].status is ChallengeStatus.QUALIFIED


def test_unsupported_assumption_is_challenged_and_cannot_support() -> None:
    record = evaluate(with_unsupported_assumption())
    assert record.result.disposition is A4Disposition.ABSTAIN
    assert any(
        item.family is ChallengeFamily.ASSUMPTION_SUPPORT
        for item in record.result.challenge_findings
    )


def test_supported_counter_thesis_is_conflicted() -> None:
    record = evaluate(with_state("CONFLICTED"))
    assert record.result.counter_thesis is not None
    assert record.result.disposition is A4Disposition.CONFLICTED


def test_no_supported_thesis_abstains() -> None:
    record = evaluate(with_state("UNEVALUATED"))
    assert record.result.disposition is A4Disposition.ABSTAIN
    assert record.result.execution_status is A4ExecutionStatus.PARTIAL
    assert record.result.failures[0].code.value == "UNRESOLVED_REQUIRED_RULE"


def test_deterministic_risk_veto_avoids_without_sell_instruction() -> None:
    record = evaluate(with_state("AVOID"))
    assert record.result.disposition is A4Disposition.AVOID
    assert record.result.counter_thesis is not None
    assert record.result.counter_thesis.conclusion_relation == "RISK_DOMINANT"
    assert "SELL" not in record.result.model_dump_json()


def test_resolved_scope_mismatch_is_not_conflict() -> None:
    record = evaluate(with_resolved_scope_mismatch())
    assert record.result.disposition is A4Disposition.SUPPORTIVE
    scope_findings = [
        item
        for item in record.result.challenge_findings
        if item.reason_code in {"SCOPE_MISMATCH_RESOLVED", "DISPUTE_RESOLVED_BY_SCOPE"}
    ]
    assert scope_findings
    assert all(item.status is ChallengeStatus.RESOLVED for item in scope_findings)


def test_watch_may_be_qualified_support_only_when_no_blocker_survives() -> None:
    assert evaluate(with_state("WATCH")).result.disposition is A4Disposition.SUPPORTIVE
    weakened = reseal(
        with_state("WATCH"),
        authority_assessments=with_unknown_authority().authority_assessments,
    )
    assert evaluate(weakened).result.disposition is A4Disposition.INSUFFICIENT_EVIDENCE
