import socket
from datetime import timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from tiaf.facade import capability_catalog
from tiaf.trade_expression import (
    A6ReplayIntegrityError,
    CandidateEligibility,
    ExpiryChainEvidence,
    ExpressionCandidateEvaluation,
    ExpressionDisposition,
    ExpressionPreferences,
    MoneynessLabel,
    TradeExpressionAssessment,
    evaluate_trade_expression,
    validate_trade_expression_assessment,
    verify_trade_expression_replay,
)

from ._a62_support import context, option_capture, option_chain
from ._support import TARGET


def _evaluate(**kwargs: object) -> TradeExpressionAssessment:
    request, a4, evidence, policy, admission = context(**kwargs)  # type: ignore[arg-type]
    return evaluate_trade_expression(request, a4, evidence, policy, admission)


def _preferred(result: TradeExpressionAssessment) -> ExpressionCandidateEvaluation:
    return next(
        item
        for item in result.candidate_evaluations
        if item.candidate.candidate_id == result.preferred_candidate_ref
    )


def test_default_rank_selects_atm_and_retains_all_evaluations() -> None:
    result = _evaluate()
    preferred = _preferred(result)

    assert result.disposition is ExpressionDisposition.EXPRESSION_AVAILABLE
    assert preferred.candidate.moneyness is MoneynessLabel.ATM
    assert len(result.alternative_candidate_refs) == 2
    assert len(result.candidate_evaluations) == 3
    assert result.explanation.preferred_reason_codes == (
        "ALL_HARD_GATES_PASS",
        "LEXICOGRAPHIC_RANK_1",
    )
    assert len(result.explanation.rank_differences) == 2


def test_spread_tier_precedes_moneyness_preference() -> None:
    chain = option_chain(
        bids=(Decimal("99.5"), Decimal("99.49"), Decimal("99.5")),
        asks=(Decimal("100.5"), Decimal("100.51"), Decimal("100.5")),
    )
    result = _evaluate(chains=(chain,))
    assert _preferred(result).candidate.moneyness is MoneynessLabel.ITM1
    assert any(
        difference.decisive_dimension == "SPREAD_TIER"
        for difference in result.explanation.rank_differences
    )


def test_request_moneyness_order_restricts_and_reorders_candidates() -> None:
    preferences = ExpressionPreferences(moneyness_order=(MoneynessLabel.OTM1, MoneynessLabel.ATM))
    result = _evaluate(preferences=preferences)
    assert len(result.candidate_evaluations) == 2
    assert _preferred(result).candidate.moneyness is MoneynessLabel.OTM1


def test_hard_gate_dominates_requested_moneyness_order() -> None:
    chain = option_chain(
        bid_quantities=(Decimal("25"), Decimal("25"), Decimal(0)),
        ask_quantities=(Decimal("25"), Decimal("25"), Decimal(0)),
    )
    preferences = ExpressionPreferences(moneyness_order=(MoneynessLabel.OTM1, MoneynessLabel.ATM))
    result = _evaluate(chains=(chain,), preferences=preferences)
    assert _preferred(result).candidate.moneyness is MoneynessLabel.ATM
    rejected = next(
        item
        for item in result.candidate_evaluations
        if item.candidate.moneyness is MoneynessLabel.OTM1
    )
    assert rejected.eligibility is CandidateEligibility.INELIGIBLE


def test_rank_is_not_cheapest_first() -> None:
    chain = option_chain(
        bids=(Decimal("149.25"), Decimal("99.5"), Decimal("49.75")),
        asks=(Decimal("150.75"), Decimal("100.5"), Decimal("50.25")),
    )
    result = _evaluate(chains=(chain,))
    preferred = _preferred(result)
    assert preferred.candidate.moneyness is MoneynessLabel.ATM
    assert (
        preferred.spread.quote_ref
        != min(
            result.candidate_evaluations,
            key=lambda item: next(
                quote.ask
                for quote in chain.quotes
                if quote.quote_id == item.quote_ref and quote.ask is not None
            ),
        ).spread.quote_ref
    )


def test_rank_uses_smallest_sufficient_cushion_not_longest_expiry() -> None:
    near = option_chain(expiration_at=TARGET + timedelta(days=3))
    far = option_chain(expiration_at=TARGET + timedelta(days=7))
    result = _evaluate(chains=(far, near))
    assert _preferred(result).candidate.contract.expiry_date == near.expiration.expiry_date


def test_full_window_unknown_dominates_a_valid_survivor() -> None:
    chain = option_chain(
        bids=(Decimal("99.5"), Decimal("99.5"), None),
        asks=(Decimal("100.5"), Decimal("100.5"), None),
    )
    result = _evaluate(chains=(chain,))
    assert any(
        item.eligibility is CandidateEligibility.ELIGIBLE for item in result.candidate_evaluations
    )
    assert result.disposition is ExpressionDisposition.INSUFFICIENT_EVIDENCE
    assert result.preferred_candidate_ref is None


def test_list_and_json_round_trip_preserve_immutable_assessment() -> None:
    result = _evaluate()
    payload = result.model_dump(mode="json")
    assert isinstance(payload["candidate_evaluations"], list)
    assert isinstance(payload["alternative_candidate_refs"], list)
    rebuilt = TradeExpressionAssessment.model_validate(payload)
    assert rebuilt == result
    assert isinstance(rebuilt.candidate_evaluations, tuple)
    with pytest.raises(ValidationError):
        rebuilt.disposition = ExpressionDisposition.NO_OPTION_TRADE


def test_input_order_invariance_for_equivalent_captured_rows() -> None:
    chain = option_chain(expiration_at=TARGET + timedelta(days=3))
    later = option_chain(expiration_at=TARGET + timedelta(days=7))
    shuffled = ExpiryChainEvidence.model_validate(
        {**chain.model_dump(mode="python"), "quotes": tuple(reversed(chain.quotes))}
    )
    left_context = context(capture=option_capture((chain, later)))
    right_context = context(capture=option_capture((later, shuffled)))
    left = evaluate_trade_expression(*left_context[:4], left_context[4])
    right = evaluate_trade_expression(*right_context[:4], right_context[4])
    assert left == right
    assert left.semantic_fingerprint == right.semantic_fingerprint


def test_exact_replay_uses_no_network_or_current_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, a4, evidence, policy, admission = context()
    composition_refs = ("composition:a6-test",)
    recorded = evaluate_trade_expression(
        request,
        a4,
        evidence,
        policy,
        admission,
        composition_refs=composition_refs,
    )

    def denied(*args: object, **kwargs: object) -> None:
        pytest.fail("A6.2 replay opened a network socket")

    monkeypatch.setattr(socket.socket, "connect", denied)
    replayed = verify_trade_expression_replay(
        recorded,
        request,
        a4,
        evidence,
        policy,
        admission,
        composition_refs=composition_refs,
    )
    assert replayed == recorded
    assert recorded.composition_refs == composition_refs
    assert validate_trade_expression_assessment(recorded) == recorded


def test_semantic_quote_change_changes_assessment_fingerprint() -> None:
    baseline = _evaluate()
    changed = _evaluate(
        chains=(
            option_chain(
                bids=(Decimal("99.4"),) * 3,
                asks=(Decimal("100.6"),) * 3,
            ),
        )
    )
    assert changed.semantic_fingerprint != baseline.semantic_fingerprint


def test_tampered_assessment_fingerprint_is_rejected() -> None:
    result = _evaluate()
    tampered = result.model_copy(update={"semantic_fingerprint": "0" * 64})
    with pytest.raises(A6ReplayIntegrityError):
        validate_trade_expression_assessment(tampered)


def test_assessment_has_no_execution_authority_or_usage() -> None:
    result = _evaluate()
    fields = set(TradeExpressionAssessment.model_fields)
    assert not fields & {
        "account",
        "capital",
        "final_quantity",
        "order_type",
        "route",
        "execution_consent",
    }
    assert result.executable is False
    assert result.provider_calls == result.model_calls == 0
    assert result.input_tokens == result.output_tokens == result.model_cost_units == 0


def test_a6_3_publishes_expression_capability_without_changing_assessment_shape() -> None:
    capabilities = tuple(item.capability_id for item in capability_catalog())
    assert len(capabilities) == 9
    assert "expression.assess" in capabilities
    assert "score" not in TradeExpressionAssessment.model_fields
