from datetime import timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from tiaf.contracts import OptionType
from tiaf.trade_expression import (
    AdmittedEvent,
    AdmittedImpliedVolatility,
    CoverageProof,
    CoverageState,
    DerivativesEvidenceCapture,
    EventEvidenceState,
    EventEvidenceWindow,
    EventMateriality,
    EventRelevance,
    ExpirationQualification,
    ExpirationTiming,
    ExpiryChainEvidence,
    FreshnessBasis,
    MarketTimingQualification,
    OptionQuoteEvidence,
    TimingQualification,
    semantic_fingerprint,
)

from ._a62_support import option_chain
from ._support import EXPIRY_DATE, NOW, coverage, derivatives_capture, option_contract, quote


def test_option_identity_distinguishes_side_strike_and_expiry() -> None:
    base = option_contract()
    assert base.identity_fingerprint() == option_contract().identity_fingerprint()
    assert (
        base.identity_fingerprint()
        != option_contract(option_type=OptionType.PE).identity_fingerprint()
    )
    assert base.identity_fingerprint() != option_contract(Decimal("101")).identity_fingerprint()
    later = base.model_copy(
        update={
            "expiry_date": EXPIRY_DATE + timedelta(days=7),
            "expiration": ExpirationTiming(
                expiry_date=EXPIRY_DATE + timedelta(days=7),
                expiration_at=NOW + timedelta(days=35),
                qualification=ExpirationQualification.QUALIFIED_INSTANT,
                qualification_source_ref="source:expiry",
            ),
        }
    )
    assert base.identity_fingerprint() != later.identity_fingerprint()
    different_provider = base.model_copy(
        update={
            "native_instrument_ref": "instrument:different-provider-id",
            "provenance_refs": ("provider:different",),
        }
    )
    assert base.identity_fingerprint() == different_provider.identity_fingerprint()


def test_zero_oi_and_volume_are_facts_missing_book_is_distinct() -> None:
    value = quote()
    assert value.open_interest == 0
    assert value.volume == 0
    missing = value.model_copy(update={"bid": None, "ask": None})
    assert missing.bid is None and missing.ask is None
    assert missing.open_interest == 0


def test_implied_volatility_requires_explicit_units_and_evidence() -> None:
    value = AdmittedImpliedVolatility(
        value=Decimal("17.25"),
        unit_semantics="PROVIDER_PERCENT_POINTS",
        evidence_refs=("observation:iv-fixture",),
    )
    admitted = quote().model_copy(update={"implied_volatility": value})
    assert admitted.implied_volatility == value
    with pytest.raises(ValidationError):
        AdmittedImpliedVolatility(
            value=Decimal("17.25"),
            unit_semantics="PROVIDER_PERCENT_POINTS",
            evidence_refs=(),
        )


def test_crossed_quote_is_invalid_and_zero_depth_is_preserved() -> None:
    payload = quote().model_dump(mode="python")
    payload.update({"bid": Decimal("101"), "ask": Decimal("100")})
    with pytest.raises(ValidationError, match="crossed"):
        OptionQuoteEvidence.model_validate(payload)
    zero_depth = quote().model_copy(
        update={"top_bid_quantity": Decimal(0), "top_ask_quantity": Decimal(0)}
    )
    assert zero_depth.top_bid_quantity == 0
    assert zero_depth.top_ask_quantity == 0


def test_quote_expiration_timing_must_match_its_chain() -> None:
    chain = option_chain()
    quote_value = chain.quotes[0]
    assert quote_value.contract.expiration.expiration_at is not None
    assert quote_value.contract.expiration.trading_cutoff_at is not None
    changed_timing = quote_value.contract.expiration.model_copy(
        update={
            "expiration_at": quote_value.contract.expiration.expiration_at - timedelta(hours=1),
            "trading_cutoff_at": quote_value.contract.expiration.trading_cutoff_at
            - timedelta(hours=1),
        }
    )
    changed_quote = quote_value.model_copy(
        update={"contract": quote_value.contract.model_copy(update={"expiration": changed_timing})}
    )
    with pytest.raises(ValidationError, match="does not belong"):
        ExpiryChainEvidence.model_validate(
            {
                **chain.model_dump(mode="python"),
                "quotes": (changed_quote, *chain.quotes[1:]),
            }
        )


@pytest.mark.parametrize(
    "state,count,complete",
    [
        (CoverageState.PRESENT, 1, True),
        (CoverageState.CONFIRMED_EMPTY, 0, True),
        (CoverageState.PARTIAL, 1, False),
        (CoverageState.UNAVAILABLE, 0, False),
        (CoverageState.UNKNOWN, 0, False),
    ],
)
def test_all_coverage_states_are_explicit(state: CoverageState, count: int, complete: bool) -> None:
    value = coverage(state, count, complete=complete)
    assert value.state is state


def test_empty_response_does_not_prove_confirmed_empty() -> None:
    unknown = coverage(CoverageState.UNKNOWN, 0, complete=False)
    assert unknown.state is not CoverageState.CONFIRMED_EMPTY
    with pytest.raises(ValidationError):
        CoverageProof(
            state=CoverageState.CONFIRMED_EMPTY,
            scope_ref="scope:empty",
            checked_at=NOW,
            observed_item_count=0,
            scope_complete=False,
        )


def test_capture_and_chain_bounds_refuse_over_limit_input() -> None:
    capture = derivatives_capture()
    chain = capture.chains[0]
    with pytest.raises(ValidationError):
        ExpiryChainEvidence.model_validate(
            {**chain.model_dump(mode="python"), "quotes": [quote()] * 513}
        )
    chains = tuple(
        chain.model_copy(
            update={
                "chain_id": f"chain:over-bound-{index}",
                "expiration": chain.expiration.model_copy(
                    update={"expiry_date": EXPIRY_DATE + timedelta(days=index)}
                ),
            }
        )
        for index in range(4)
    )
    with pytest.raises(ValidationError):
        DerivativesEvidenceCapture.model_validate(
            {**capture.model_dump(mode="python"), "chains": chains}
        )


def test_known_event_blocker_and_unknown_event_coverage_remain_distinct() -> None:
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
    blocker = EventEvidenceWindow(
        state=EventEvidenceState.KNOWN_BLOCKER,
        subject="SYNTHETIC",
        window_start=NOW,
        window_end=NOW + timedelta(days=5),
        coverage=coverage(CoverageState.PRESENT, 1, complete=True),
        events=(event,),
        provenance_refs=("source:exchange-filing",),
    )
    assert blocker.state is EventEvidenceState.KNOWN_BLOCKER
    unknown = blocker.model_copy(
        update={
            "state": EventEvidenceState.UNKNOWN,
            "coverage": coverage(CoverageState.UNKNOWN, 1, complete=False),
        }
    )
    assert unknown.state is EventEvidenceState.UNKNOWN


def test_no_event_proof_requires_qualified_confirmed_empty_coverage() -> None:
    valid = EventEvidenceWindow(
        state=EventEvidenceState.QUALIFIED_NO_INTERSECTING_EVENT,
        subject="SYNTHETIC",
        window_start=NOW,
        window_end=NOW + timedelta(days=5),
        coverage=coverage(CoverageState.CONFIRMED_EMPTY, 0, complete=True),
        provenance_refs=("source:event-calendar",),
    )
    assert not valid.events
    with pytest.raises(ValidationError):
        EventEvidenceWindow(
            state=EventEvidenceState.QUALIFIED_NO_INTERSECTING_EVENT,
            subject="SYNTHETIC",
            window_start=NOW,
            window_end=NOW + timedelta(days=5),
            coverage=coverage(CoverageState.UNKNOWN, 0, complete=False),
            provenance_refs=("source:event-calendar",),
        )
    with pytest.raises(ValidationError, match="cannot remain unknown"):
        EventEvidenceWindow(
            state=EventEvidenceState.UNKNOWN,
            subject="SYNTHETIC",
            window_start=NOW,
            window_end=NOW + timedelta(days=5),
            coverage=coverage(CoverageState.CONFIRMED_EMPTY, 0, complete=True),
            provenance_refs=("source:event-calendar",),
        )


def test_acquisition_only_quote_timing_cannot_be_upgraded_by_timezone() -> None:
    value = MarketTimingQualification(
        acquired_at=NOW,
        qualification=TimingQualification.UNQUALIFIED,
        freshness_basis=FreshnessBasis.ACQUISITION_TIME_ONLY,
    )
    assert value.acquired_at.utcoffset() == timedelta(hours=5, minutes=30)
    assert value.authoritative_observed_at is None


def test_irrelevant_reference_order_does_not_change_fingerprint() -> None:
    value = quote()
    reverse = OptionQuoteEvidence.model_validate(
        {
            **value.model_dump(mode="python"),
            "provenance_refs": tuple(reversed(value.provenance_refs)),
        }
    )
    assert value == reverse
    assert semantic_fingerprint(value) == semantic_fingerprint(reverse)
