"""A6.4 edge hardening for requirements not isolated by earlier A6 slices."""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from tiaf.contracts import OptionType
from tiaf.trade_expression import (
    AdmittedEvent,
    CandidateRankingFacts,
    CoverageState,
    EventEvidenceState,
    EventEvidenceWindow,
    EventMateriality,
    EventRelevance,
    ExpiryChainEvidence,
    ExpressionDirection,
    ExpressionDisposition,
    ExpressionPreferences,
    MoneynessLabel,
    SpreadEligibility,
    TimingQualification,
    TradeExpressionAssessment,
    assess_spread,
    deterministic_policy,
    evaluate_trade_expression,
)
from tiaf.trade_expression.evaluation import _rank_key

from ._a62_support import context, option_chain
from ._support import NOW, TARGET, coverage


def _evaluate(**kwargs: object) -> TradeExpressionAssessment:
    request, a4, evidence, policy, admission = context(**kwargs)  # type: ignore[arg-type]
    return evaluate_trade_expression(request, a4, evidence, policy, admission)


@pytest.mark.parametrize(
    ("event_at", "expected"),
    (
        (NOW - timedelta(seconds=1), ExpressionDisposition.EXPRESSION_AVAILABLE),
        (NOW, ExpressionDisposition.EXPRESSION_AVAILABLE),
        (TARGET, ExpressionDisposition.WAIT_FOR_EXPRESSION),
        (TARGET + timedelta(seconds=1), ExpressionDisposition.EXPRESSION_AVAILABLE),
    ),
)
def test_event_holding_window_boundaries_are_explicit(
    event_at: datetime,
    expected: ExpressionDisposition,
) -> None:
    event = AdmittedEvent(
        event_id="event:a64-boundary",
        subject="SYNTHETIC",
        event_at=event_at,
        acquired_at=NOW,
        timing_qualification=TimingQualification.QUALIFIED,
        materiality=EventMateriality.MATERIAL,
        relevance=EventRelevance.RELEVANT,
        provenance_refs=("source:a64-boundary",),
    )
    window = EventEvidenceWindow(
        state=EventEvidenceState.KNOWN_BLOCKER,
        subject="SYNTHETIC",
        window_start=NOW - timedelta(days=1),
        window_end=TARGET + timedelta(days=1),
        coverage=coverage(CoverageState.PRESENT, 1, complete=True),
        events=(event,),
        provenance_refs=("source:a64-boundary",),
    )
    result = _evaluate(event_evidence=window)
    assert result.disposition is expected


def test_spread_just_over_hard_limit_is_exactly_ineligible() -> None:
    result = assess_spread(
        quote_ref="quote:a64-501bps",
        bid=Decimal("97.495"),
        ask=Decimal("102.505"),
        top_bid_quantity=Decimal(1),
        top_ask_quantity=Decimal(1),
        policy=deterministic_policy(),
    )
    assert result.relative_spread_bps == Decimal(501)
    assert result.eligibility is SpreadEligibility.INELIGIBLE
    assert result.reason_code == "SPREAD_ABOVE_HARD_LIMIT"


@pytest.mark.parametrize(
    ("bid_quantity", "ask_quantity"),
    ((Decimal(0), Decimal(1)), (Decimal(1), Decimal(0))),
)
def test_each_zero_top_depth_side_is_a_factual_rejection(
    bid_quantity: Decimal,
    ask_quantity: Decimal,
) -> None:
    result = _evaluate(
        chains=(
            option_chain(
                bid_quantities=(bid_quantity,) * 3,
                ask_quantities=(ask_quantity,) * 3,
            ),
        )
    )
    assert result.disposition is ExpressionDisposition.NO_OPTION_TRADE
    assert result.blockers == ("NON_POSITIVE_TOP_QUANTITY",)


def test_missing_optional_oi_and_volume_do_not_become_a_hidden_gate() -> None:
    chain = option_chain()
    quotes = tuple(
        quote.model_copy(update={"open_interest": None, "volume": None})
        for quote in chain.quotes
    )
    changed = ExpiryChainEvidence.model_validate(
        {**chain.model_dump(mode="python"), "quotes": quotes}
    )
    result = _evaluate(chains=(changed,))
    assert result.disposition is ExpressionDisposition.EXPRESSION_AVAILABLE


@pytest.mark.parametrize(
    ("direction", "option_type", "expected_labels"),
    (
        (
            ExpressionDirection.BULLISH,
            OptionType.CE,
            {MoneynessLabel.ATM, MoneynessLabel.OTM1},
        ),
        (
            ExpressionDirection.BEARISH,
            OptionType.PE,
            {MoneynessLabel.ATM, MoneynessLabel.ITM1},
        ),
    ),
)
def test_missing_itm_and_otm_neighbors_are_not_fabricated(
    direction: ExpressionDirection,
    option_type: OptionType,
    expected_labels: set[MoneynessLabel],
) -> None:
    result = _evaluate(
        direction=direction,
        chains=(
            option_chain(
                option_type=option_type,
                strikes=(Decimal("100"), Decimal("110")),
            ),
        ),
    )
    assert {item.candidate.moneyness for item in result.candidate_evaluations} == (
        expected_labels
    )


def test_duplicate_contract_identity_is_rejected_even_with_distinct_quote_ids() -> None:
    chain = option_chain()
    duplicate = chain.quotes[0].model_copy(update={"quote_id": "quote:a64-duplicate"})
    with pytest.raises(ValidationError, match="identities must be unique"):
        ExpiryChainEvidence.model_validate(
            {
                **chain.model_dump(mode="python"),
                "quotes": (*chain.quotes, duplicate),
                "coverage": chain.coverage.model_copy(
                    update={
                        "observed_item_count": 4,
                        "expected_item_count": 4,
                    }
                ),
            }
        )


@pytest.mark.parametrize(
    ("order", "expected_evaluations", "expected_alternatives"),
    (
        ((MoneynessLabel.ATM,), 1, 0),
        ((MoneynessLabel.ATM, MoneynessLabel.ITM1), 2, 1),
        (
            (MoneynessLabel.ATM, MoneynessLabel.ITM1, MoneynessLabel.OTM1),
            3,
            2,
        ),
    ),
)
def test_survivor_counts_preserve_one_preferred_and_at_most_two_alternatives(
    order: tuple[MoneynessLabel, ...],
    expected_evaluations: int,
    expected_alternatives: int,
) -> None:
    result = _evaluate(preferences=ExpressionPreferences(moneyness_order=order))
    assert len(result.candidate_evaluations) == expected_evaluations
    assert result.preferred_candidate_ref is not None
    assert len(result.alternative_candidate_refs) == expected_alternatives


def test_final_rank_dimensions_total_order_engineered_ties() -> None:
    result = _evaluate()
    left, right, third = result.candidate_evaluations
    assert left.ranking_facts is not None
    common = left.ranking_facts.model_dump(mode="python")
    exact_left = left.model_copy(
        update={
            "ranking_facts": CandidateRankingFacts.model_validate(
                {**common, "exact_spread_bps": Decimal(100)}
            )
        }
    )
    exact_right = right.model_copy(
        update={
            "ranking_facts": CandidateRankingFacts.model_validate(
                {**common, "exact_spread_bps": Decimal(101)}
            )
        }
    )
    assert _rank_key(exact_left) < _rank_key(exact_right)

    key_left = left.model_copy(
        update={
            "ranking_facts": CandidateRankingFacts.model_validate(
                {**common, "canonical_contract_key": ("A", "A", "A", "A", "A")}
            )
        }
    )
    key_right = third.model_copy(
        update={
            "ranking_facts": CandidateRankingFacts.model_validate(
                {**common, "canonical_contract_key": ("B", "A", "A", "A", "A")}
            )
        }
    )
    assert _rank_key(key_left) < _rank_key(key_right)
