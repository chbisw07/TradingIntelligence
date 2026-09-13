from datetime import timedelta
from decimal import Decimal

import pytest

from tiaf.a4 import evaluate_projection
from tiaf.trade_expression import (
    AdmittedEvent,
    CoverageState,
    EventEvidenceState,
    EventEvidenceWindow,
    EventMateriality,
    EventRelevance,
    ExpiryChainEvidence,
    ExpressionDisposition,
    ExpressionPreferences,
    FreshnessBasis,
    MarketTimingQualification,
    TimingQualification,
    TradeExpressionAssessment,
    TradeExpressionRequest,
    admit_request,
    evaluate_trade_expression,
)

from ..a4._support import with_state, with_unresolved_conflict
from ._a62_support import context, option_capture, option_chain
from ._support import NOW, TARGET, coverage, qualified_market_timing


def _result_for_chain(
    chain: ExpiryChainEvidence,
    *,
    preferences: ExpressionPreferences | None = None,
) -> TradeExpressionAssessment:
    request, a4, evidence, policy, admission = context(
        chains=(chain,),
        preferences=preferences,
    )
    return evaluate_trade_expression(request, a4, evidence, policy, admission)


def test_missing_book_is_insufficient_not_illiquid() -> None:
    result = _result_for_chain(option_chain(bids=(None, None, None), asks=(None, None, None)))
    assert result.disposition is ExpressionDisposition.INSUFFICIENT_EVIDENCE
    assert "MISSING_BID_OR_ASK" in result.gaps


def test_crossed_book_is_known_rejection() -> None:
    chain = option_chain()
    first = chain.quotes[0].model_copy(update={"bid": Decimal("101"), "ask": Decimal("100")})
    chain = chain.model_copy(update={"quotes": (first, *chain.quotes[1:])})
    result = _result_for_chain(chain)
    assert result.disposition is ExpressionDisposition.EXPRESSION_AVAILABLE
    rejected = next(
        item for item in result.candidate_evaluations if item.quote_ref == first.quote_id
    )
    assert "INVALID_OR_CROSSED_ASK" in rejected.rejection_reason_codes


def test_zero_depth_and_over_limit_spread_are_complete_rejections() -> None:
    zero_depth = _result_for_chain(
        option_chain(
            bid_quantities=(Decimal(0),) * 3,
            ask_quantities=(Decimal(0),) * 3,
        )
    )
    wide = _result_for_chain(
        option_chain(
            bids=(Decimal("90"),) * 3,
            asks=(Decimal("110"),) * 3,
        )
    )
    assert zero_depth.disposition is ExpressionDisposition.NO_OPTION_TRADE
    assert wide.disposition is ExpressionDisposition.NO_OPTION_TRADE
    assert "NON_POSITIVE_TOP_QUANTITY" in zero_depth.blockers
    assert "SPREAD_ABOVE_HARD_LIMIT" in wide.blockers


@pytest.mark.parametrize(
    "timing",
    [
        qualified_market_timing(NOW - timedelta(seconds=61)),
        MarketTimingQualification(
            acquired_at=NOW,
            qualification=TimingQualification.UNQUALIFIED,
            freshness_basis=FreshnessBasis.ACQUISITION_TIME_ONLY,
        ),
    ],
)
def test_stale_or_acquisition_only_timing_fails_closed(
    timing: MarketTimingQualification,
) -> None:
    request, a4, evidence, policy, admission = context(chains=(option_chain(timing=timing),))
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)
    assert result.disposition is ExpressionDisposition.INSUFFICIENT_EVIDENCE
    assert result.candidate_evaluations == ()


@pytest.mark.parametrize(
    "cap,expected",
    [
        (Decimal("101"), ExpressionDisposition.EXPRESSION_AVAILABLE),
        (Decimal("100.5"), ExpressionDisposition.EXPRESSION_AVAILABLE),
        (Decimal("100"), ExpressionDisposition.NO_OPTION_TRADE),
    ],
)
def test_premium_cap_uses_captured_ask_per_unit(
    cap: Decimal,
    expected: ExpressionDisposition,
) -> None:
    preferences = ExpressionPreferences(premium_cap=cap, premium_currency="INR")
    result = _result_for_chain(option_chain(), preferences=preferences)
    assert result.disposition is expected
    assert all(
        gate.measured_unit == "INR_PER_UNIT"
        for item in result.candidate_evaluations
        for gate in item.gates
        if gate.gate_id.value == "PREMIUM_CAP"
    )


def test_missing_ask_for_requested_cap_is_insufficient() -> None:
    preferences = ExpressionPreferences(premium_cap=Decimal("200"), premium_currency="INR")
    result = _result_for_chain(
        option_chain(asks=(None, None, None)),
        preferences=preferences,
    )
    assert result.disposition is ExpressionDisposition.INSUFFICIENT_EVIDENCE
    assert "ASK_MISSING_FOR_PREMIUM_CAP" in result.gaps


@pytest.mark.parametrize(
    "state",
    [CoverageState.PARTIAL, CoverageState.UNAVAILABLE, CoverageState.UNKNOWN],
)
def test_nonqualified_capture_coverage_never_becomes_no_trade(state: CoverageState) -> None:
    chains = (option_chain(),) if state is CoverageState.PARTIAL else ()
    capture = option_capture(chains, state=state)
    request, a4, evidence, policy, admission = context(capture=capture)
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)
    assert result.disposition is ExpressionDisposition.INSUFFICIENT_EVIDENCE


def test_confirmed_empty_scope_proves_no_listed_expiries() -> None:
    capture = option_capture((), state=CoverageState.CONFIRMED_EMPTY)
    request, a4, evidence, policy, admission = context(capture=capture)
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)
    assert result.disposition is ExpressionDisposition.NO_OPTION_TRADE
    assert result.explanation.disposition_reason_codes == ("NO_LISTED_EXPIRIES_IN_SCOPE",)


def _event_window(state: EventEvidenceState) -> EventEvidenceWindow:
    if state is EventEvidenceState.KNOWN_BLOCKER:
        event = AdmittedEvent(
            event_id="event:earnings",
            subject="SYNTHETIC",
            event_at=NOW + timedelta(days=2),
            acquired_at=NOW,
            timing_qualification=TimingQualification.QUALIFIED,
            materiality=EventMateriality.MATERIAL,
            relevance=EventRelevance.RELEVANT,
            provenance_refs=("source:exchange-filing",),
        )
        return EventEvidenceWindow(
            state=state,
            subject="SYNTHETIC",
            window_start=NOW,
            window_end=TARGET,
            coverage=coverage(CoverageState.PRESENT, 1, complete=True),
            events=(event,),
            provenance_refs=("source:exchange-filing",),
        )
    return EventEvidenceWindow(
        state=state,
        subject="SYNTHETIC",
        window_start=NOW,
        window_end=TARGET,
        coverage=coverage(
            CoverageState.CONFIRMED_EMPTY
            if state is EventEvidenceState.QUALIFIED_NO_INTERSECTING_EVENT
            else CoverageState.UNKNOWN,
            0,
            complete=state is EventEvidenceState.QUALIFIED_NO_INTERSECTING_EVENT,
        ),
        provenance_refs=("source:event-calendar",),
    )


def test_known_event_is_wait_even_when_quote_scope_is_stale() -> None:
    request, a4, evidence, policy, admission = context(
        chains=(option_chain(timing=qualified_market_timing(NOW - timedelta(seconds=61))),),
        event_evidence=_event_window(EventEvidenceState.KNOWN_BLOCKER),
    )
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)
    assert result.disposition is ExpressionDisposition.WAIT_FOR_EXPRESSION
    assert result.candidate_evaluations == ()


def test_qualified_event_clear_proceeds_and_unknown_is_optional_by_default() -> None:
    clear_context = context(
        event_evidence=_event_window(EventEvidenceState.QUALIFIED_NO_INTERSECTING_EVENT)
    )
    clear = evaluate_trade_expression(*clear_context[:4], clear_context[4])
    unknown_context = context(event_evidence=_event_window(EventEvidenceState.UNKNOWN))
    unknown = evaluate_trade_expression(*unknown_context[:4], unknown_context[4])
    assert clear.disposition is ExpressionDisposition.EXPRESSION_AVAILABLE
    assert unknown.disposition is ExpressionDisposition.EXPRESSION_AVAILABLE
    assert "EVENT_COVERAGE_UNKNOWN_OPTIONAL" in unknown.gaps


def test_event_clear_preference_with_unknown_coverage_is_insufficient() -> None:
    request, a4, evidence, policy, admission = context(
        preferences=ExpressionPreferences(require_event_clear=True),
        event_evidence=_event_window(EventEvidenceState.UNKNOWN),
    )
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)
    assert result.disposition is ExpressionDisposition.INSUFFICIENT_EVIDENCE


def test_event_clear_preference_requires_full_holding_window() -> None:
    window = EventEvidenceWindow(
        state=EventEvidenceState.QUALIFIED_NO_INTERSECTING_EVENT,
        subject="SYNTHETIC",
        window_start=NOW,
        window_end=NOW + timedelta(days=1),
        coverage=coverage(CoverageState.CONFIRMED_EMPTY, 0, complete=True),
        provenance_refs=("source:event-calendar",),
    )
    request, a4, evidence, policy, admission = context(
        preferences=ExpressionPreferences(require_event_clear=True),
        event_evidence=window,
    )
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)
    assert result.disposition is ExpressionDisposition.INSUFFICIENT_EVIDENCE
    assert result.gaps == ("EVENT_CLEARANCE_WINDOW_INCOMPLETE",)


def test_ambiguous_relevant_event_is_insufficient_even_without_clear_preference() -> None:
    event = AdmittedEvent(
        event_id="event:timing-unknown",
        subject="SYNTHETIC",
        acquired_at=NOW,
        timing_qualification=TimingQualification.UNKNOWN,
        materiality=EventMateriality.MATERIAL,
        relevance=EventRelevance.RELEVANT,
        provenance_refs=("source:exchange-filing",),
    )
    window = EventEvidenceWindow(
        state=EventEvidenceState.UNKNOWN,
        subject="SYNTHETIC",
        window_start=NOW,
        window_end=TARGET,
        coverage=coverage(CoverageState.PRESENT, 1, complete=True),
        events=(event,),
        provenance_refs=("source:exchange-filing",),
    )
    request, a4, evidence, policy, admission = context(event_evidence=window)
    result = evaluate_trade_expression(request, a4, evidence, policy, admission)
    assert result.disposition is ExpressionDisposition.INSUFFICIENT_EVIDENCE
    assert result.gaps == ("EVENT_STATE_UNRESOLVED",)


def test_upstream_no_trade_and_conflict_preserve_precedence() -> None:
    no_trade_a4 = evaluate_projection(
        with_state("OPPORTUNITY", a2_class="NO_TRADE"),
        evaluated_at=with_state("OPPORTUNITY", a2_class="NO_TRADE").header.evidence_as_of,
    ).result
    no_trade_context = context(a4=no_trade_a4)
    no_trade = evaluate_trade_expression(*no_trade_context[:4], no_trade_context[4])
    conflict_projection = with_unresolved_conflict()
    conflict_a4 = evaluate_projection(
        conflict_projection,
        evaluated_at=conflict_projection.header.evidence_as_of,
    ).result
    conflict_context = context(a4=conflict_a4)
    conflict = evaluate_trade_expression(*conflict_context[:4], conflict_context[4])
    assert no_trade.disposition is ExpressionDisposition.NO_OPTION_TRADE
    assert conflict.disposition is ExpressionDisposition.WAIT_FOR_EXPRESSION
    assert no_trade.candidate_evaluations == conflict.candidate_evaluations == ()


def test_outside_v1_horizon_maps_to_unsupported() -> None:
    request, a4, evidence, policy, _ = context()
    changed = request.model_dump(mode="python")
    changed["horizon"] = {
        **request.horizon.model_dump(mode="python"),
        "target_end_at": NOW + timedelta(days=91),
        "exact_duration_seconds": 91 * 24 * 60 * 60,
    }
    outside = TradeExpressionRequest.model_validate(changed)
    admission = admit_request(outside, a4, evidence, policy)
    result = evaluate_trade_expression(outside, a4, evidence, policy, admission)
    assert result.disposition is ExpressionDisposition.UNSUPPORTED
