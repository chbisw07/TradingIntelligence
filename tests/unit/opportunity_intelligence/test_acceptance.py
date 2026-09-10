"""Public captured-input cases and policy invariants; no live acquisition."""

import json
from dataclasses import FrozenInstanceError
from functools import lru_cache

import pytest
from pydantic import ValidationError
from scripts._a3_9_cases import CASES, load_case

from tiaf.agents import AgentStance, SpecialistId
from tiaf.service.opportunity_intelligence import (
    IntelligenceRunRecord,
    OpportunityIntelligenceRequest,
    OpportunityState,
    StructuredOpportunityIntelligence,
    Truth,
    assemble_opportunity_intelligence,
    capture_intelligence,
    default_policy,
    replay_intelligence,
    request_from_capture,
    verify_intelligence,
)
from tiaf.service.opportunity_intelligence.policy import conjunction, disjunction


@lru_cache
def result(name: str = "aligned") -> IntelligenceRunRecord:
    return assemble_opportunity_intelligence(
        request_from_capture(load_case(name), request_id=name, policy=default_policy())
    )


@pytest.mark.parametrize("name,expected", CASES)
def test_public_state_cases_and_replay(name: str, expected: str) -> None:
    run = result(name)
    assert run.result.summary.state.value == expected
    assert replay_intelligence(capture_intelligence(run)) == run
    assert verify_intelligence(capture_intelligence(run)).exact_match
    assert run.assembly_usage.tool_calls == run.assembly_usage.llm_calls == 0
    assert run.assembly_usage.input_tokens == run.assembly_usage.output_tokens == 0
    assert run.assembly_usage.cost_units == 0
    source = json.loads(load_case(name))["record"]
    assert run.result.baseline.evidence_fingerprint == source["result"]["a2_fingerprint"]
    assert json.loads(run.request.capture_json) == json.loads(load_case(name))


def test_all_seven_states_are_exercised() -> None:
    assert {result(name).result.summary.state for name, _ in CASES} == set(OpportunityState)


def test_frozen_tuples_json_lists_and_reconstruction() -> None:
    run = result()
    assert isinstance(run.result, StructuredOpportunityIntelligence)
    dumped = run.model_dump(mode="json")
    assert isinstance(dumped["result"]["contributions"], list)
    assert type(run).model_validate(dumped) == run
    assert isinstance(run.result.contributions, tuple)
    with pytest.raises((ValidationError, FrozenInstanceError)):
        run.result.subject = "CHANGED"
    with pytest.raises(AttributeError):
        run.result.contributions.append(None)  # type: ignore[attr-defined]


def test_timestamp_policy_rejects_naive_and_normalizes_utc() -> None:
    run = result()
    raw = run.result.model_dump(mode="json")
    raw["as_of"] = "2026-09-10T12:00:00"
    with pytest.raises(ValidationError):
        type(run.result).model_validate(raw)
    raw["as_of"] = "2026-09-10T06:30:00+00:00"
    restored = type(run.result).model_validate(raw)
    assert restored.as_of == run.result.as_of
    assert restored.model_dump(mode="json")["as_of"].endswith("+05:30")


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (Truth.TRUE, Truth.UNKNOWN, Truth.UNKNOWN),
        (Truth.FALSE, Truth.UNKNOWN, Truth.FALSE),
        (Truth.TRUE, Truth.TRUE, Truth.TRUE),
        (Truth.UNKNOWN, Truth.UNKNOWN, Truth.UNKNOWN),
    ],
)
def test_three_valued_conjunction(a: Truth, b: Truth, expected: Truth) -> None:
    assert conjunction(a, b) is expected
    assert disjunction(a, b) is (Truth.TRUE if Truth.TRUE in (a, b) else Truth.UNKNOWN)


def test_ordered_rules_record_overlaps_and_precedence() -> None:
    run = result("disputed_event")
    assert run.result.summary.primary_rule == "UNRESOLVED_CONFLICT"
    assert "TIMING_RESTRICTION" in run.result.summary.matched_rules
    assert tuple(r.rule_id for r in run.rules) == default_policy().rule_order
    assert all(p.sources and p.reason_codes for p in run.predicates)


def test_no_trade_row5_gates_and_benchmark_preservation() -> None:
    watch = result("baseline_watch")
    no_trade = result("baseline_no_trade")
    assert watch.result.summary.state is OpportunityState.WATCH
    assert no_trade.result.summary.state is OpportunityState.NO_TRADE
    assert (
        watch.result.baseline.candidate_class
        == no_trade.result.baseline.candidate_class
        == "NO_TRADE"
    )
    assert (
        watch.result.baseline.opportunity_score == no_trade.result.baseline.opportunity_score == 30
    )
    assert not any(
        r.value is Truth.TRUE and r.state is OpportunityState.OPPORTUNITY for r in watch.rules
    )


def test_no_relative_or_company_vote_over_negative_price_bias() -> None:
    run = result("negative")
    assert run.result.summary.bias.headline is AgentStance.NEGATIVE
    assert (
        dict(run.result.summary.bias.domain_views)[SpecialistId.FUNDAMENTAL] is AgentStance.POSITIVE
    )
    assert all(s.specialist is SpecialistId.TECHNICAL for s in run.result.summary.bias.sources)


def test_company_tension_is_not_same_proposition_or_price_sign() -> None:
    run = result("weak_company")
    assert run.result.summary.bias.headline is AgentStance.MIXED
    assert run.result.summary.bias.price_direction is AgentStance.POSITIVE
    assert any(c.kind == "CROSS_DOMAIN_TENSION" for c in run.result.contradictions)
    assert not any(c.kind == "SAME_PROPOSITION" for c in run.result.contradictions)


def test_valuation_alone_does_not_invent_critical_risk() -> None:
    run = result("valuation")
    assert run.result.summary.state is OpportunityState.WATCH
    assert run.result.summary.risk and run.result.summary.risk.value == "MODERATE"


def test_applicability_denominators_keep_unknown_distinct() -> None:
    cash = result("non_fno").result.completeness
    unknown = result("unknown_fno").result.completeness
    assert SpecialistId.DERIVATIVES_CONTEXT in cash.not_applicable
    assert cash.numerator == cash.denominator == 7
    assert SpecialistId.DERIVATIVES_CONTEXT in unknown.unknown_applicability
    assert result("unknown_fno").result.summary.state is not OpportunityState.OPPORTUNITY
    assert SpecialistId.FUNDAMENTAL in result("index").result.completeness.not_applicable


def test_lineage_deduplicates_downstream_repetition_without_independence_claim() -> None:
    run = result()
    roots = [root for g in run.result.lineages for root in g.roots]
    assert len(roots) == len(set(roots))
    assert any(len(g.opinion_ids) >= 3 for g in run.result.lineages)
    assert all(g.independence == "UNKNOWN" for g in run.result.lineages)
    assert all(
        c.role == "DOWNSTREAM_SUMMARY"
        for c in run.result.contributions
        if c.specialist in {SpecialistId.OPPORTUNITY_QUALITY, SpecialistId.OPPORTUNITY_RISK}
    )
    assert not hasattr(run.result, "confidence")
    assert all(c.confidence is not None for c in run.result.contributions if c.opinion_id)


def test_reasons_are_cited_stable_and_no_prose_inference() -> None:
    run = result()
    assert run.result.reasons == tuple(
        sorted(run.result.reasons, key=lambda r: (r.category, r.code, r.reason_id))
    )
    for reason in run.result.reasons:
        assert reason.sources and reason.rule_ids
        if reason.epistemic == "INFERENCE":
            assert all(
                s.opinion_id and s.schema_id and s.field and s.evidence_ids for s in reason.sources
            )


def test_sparse_kaynes_keeps_gaps_and_unknown_core() -> None:
    run = result("sparse_kaynes")
    assert run.result.subject == "KAYNES"
    assert run.result.summary.state is OpportunityState.INSUFFICIENT_EVIDENCE
    assert run.result.prerequisites
    assert run.result.baseline.candidate_class == "NO_TRADE"
    assert run.result.completeness.numerator < run.result.completeness.denominator


def test_no_side_channel_or_metadata_policy_escape() -> None:
    raw = result().request.model_dump()
    for key in ("opinions", "metadata", "horizon", "provider", "winner"):
        with pytest.raises(ValidationError):
            OpportunityIntelligenceRequest.model_validate(raw | {key: {"action": "ENTER"}})
