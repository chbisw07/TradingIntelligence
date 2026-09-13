from datetime import timedelta
from decimal import Decimal

from tiaf.contracts import OptionType
from tiaf.trade_expression import (
    CandidateEligibility,
    ExpirationQualification,
    ExpirationTiming,
    ExpressionDirection,
    ExpressionDisposition,
    MoneynessLabel,
    evaluate_trade_expression,
)

from ._a62_support import context, option_capture, option_chain
from ._support import TARGET


def test_bullish_builds_only_long_ce_listed_candidates() -> None:
    request, a4, evidence, policy, admission = context()
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)

    assert result.disposition is ExpressionDisposition.EXPRESSION_AVAILABLE
    assert len(result.candidate_evaluations) == 3
    assert {item.candidate.contract.option_type for item in result.candidate_evaluations} == {
        OptionType.CE
    }
    assert {item.candidate.position_side for item in result.candidate_evaluations} == {"LONG"}
    assert all(
        item.eligibility is CandidateEligibility.ELIGIBLE for item in result.candidate_evaluations
    )


def test_bearish_builds_only_long_pe_with_correct_geometry() -> None:
    request, a4, evidence, policy, admission = context(direction=ExpressionDirection.BEARISH)
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)
    by_label = {
        item.candidate.moneyness: item.candidate.contract.strike
        for item in result.candidate_evaluations
    }

    assert {item.candidate.contract.option_type for item in result.candidate_evaluations} == {
        OptionType.PE
    }
    assert by_label == {
        MoneynessLabel.ATM: Decimal("100"),
        MoneynessLabel.ITM1: Decimal("110"),
        MoneynessLabel.OTM1: Decimal("90"),
    }


def test_three_expiries_are_bounded_to_nine_evaluations() -> None:
    chains = tuple(option_chain(expiration_at=TARGET + timedelta(days=days)) for days in (3, 5, 7))
    request, a4, evidence, policy, admission = context(chains=chains)
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)

    assert len(evidence.derivatives.chains) == 3
    assert len(result.candidate_evaluations) == policy.max_evaluated_candidates == 9


def test_missing_listed_neighbor_creates_no_fabricated_candidate() -> None:
    chain = option_chain(strikes=(Decimal("100"), Decimal("110")))
    request, a4, evidence, policy, admission = context(chains=(chain,))
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)

    labels = {item.candidate.moneyness for item in result.candidate_evaluations}
    assert labels == {MoneynessLabel.ATM, MoneynessLabel.OTM1}
    assert all(
        item.candidate.contract.strike in {Decimal("100"), Decimal("110")}
        for item in result.candidate_evaluations
    )


def test_exact_atm_midpoint_tie_uses_lower_listed_strike() -> None:
    chain = option_chain(strikes=(Decimal("100"), Decimal("102")))
    request, a4, evidence, policy, admission = context(chains=(chain,))
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)
    atm = next(
        item
        for item in result.candidate_evaluations
        if item.candidate.moneyness is MoneynessLabel.ATM
    )
    assert atm.candidate.contract.strike == Decimal("100")


def test_insufficient_residual_life_is_complete_no_option_trade() -> None:
    chain = option_chain(expiration_at=TARGET + timedelta(days=2))
    request, a4, evidence, policy, admission = context(chains=(chain,))
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)

    assert result.disposition is ExpressionDisposition.NO_OPTION_TRADE
    assert result.preferred_candidate_ref is None
    assert all(
        "INSUFFICIENT_RESIDUAL_LIFE" in item.rejection_reason_codes
        for item in result.candidate_evaluations
    )


def test_residual_life_equality_is_eligible() -> None:
    chain = option_chain(expiration_at=TARGET + timedelta(days=3))
    request, a4, evidence, policy, admission = context(chains=(chain,))
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)
    assert result.disposition is ExpressionDisposition.EXPRESSION_AVAILABLE
    assert all(
        item.ranking_facts is not None and item.ranking_facts.expiry_cushion_excess_seconds == 0
        for item in result.candidate_evaluations
    )


def test_date_only_expiry_maps_admission_to_insufficient_without_candidates() -> None:
    chain = option_chain()
    timing = ExpirationTiming(
        expiry_date=chain.expiration.expiry_date,
        qualification=ExpirationQualification.DATE_ONLY,
    )
    quotes = tuple(
        quote.model_copy(
            update={"contract": quote.contract.model_copy(update={"expiration": timing})}
        )
        for quote in chain.quotes
    )
    changed_chain = chain.model_copy(update={"expiration": timing, "quotes": quotes})
    capture = option_capture((changed_chain,))
    request, a4, evidence, policy, admission = context(capture=capture)
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)

    assert result.disposition is ExpressionDisposition.INSUFFICIENT_EVIDENCE
    assert result.candidate_evaluations == ()
    assert result.gaps == ("EXPIRATION_INSTANT_UNQUALIFIED",)
