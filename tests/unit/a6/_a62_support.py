"""Synthetic A6.2 option universes over accepted A6.1 artifacts."""

from datetime import datetime, timedelta
from decimal import Decimal

from tiaf.a4 import A4Result, evaluate_projection
from tiaf.contracts import OptionType
from tiaf.trade_expression import (
    AdmissionResult,
    CoverageProof,
    CoverageState,
    DerivativesEvidenceCapture,
    EventEvidenceWindow,
    ExpirationQualification,
    ExpirationTiming,
    ExpiryChainEvidence,
    ExpressionDirection,
    ExpressionEvidenceBundle,
    ExpressionPreferences,
    MarketTimingQualification,
    OptionContractIdentity,
    OptionQuoteEvidence,
    SubjectClass,
    TradeExpressionPolicy,
    TradeExpressionRequest,
    admit_request,
    deterministic_policy,
)

from ..a4._support import with_state
from ._support import NOW, TARGET, a4_result, bundle, qualified_market_timing, request


def directional_a4(direction: ExpressionDirection) -> A4Result:
    if direction is ExpressionDirection.BULLISH:
        return a4_result()
    projection = with_state("OPPORTUNITY", a2_direction="NEGATIVE")
    return evaluate_projection(projection, evaluated_at=projection.header.evidence_as_of).result


def option_quote(
    *,
    expiration_at: datetime,
    strike: Decimal,
    option_type: OptionType,
    bid: Decimal | None = Decimal("99.5"),
    ask: Decimal | None = Decimal("100.5"),
    bid_quantity: Decimal | None = Decimal("25"),
    ask_quantity: Decimal | None = Decimal("50"),
    timing: MarketTimingQualification | None = None,
) -> OptionQuoteEvidence:
    suffix = f"{expiration_at.date()}-{strike}-{option_type.value}"
    expiration = ExpirationTiming(
        expiry_date=expiration_at.date(),
        expiration_at=expiration_at,
        qualification=ExpirationQualification.QUALIFIED_INSTANT,
        qualification_source_ref="expiry-source:nse-contract-master",
        trading_cutoff_at=expiration_at,
        trading_cutoff_source_ref="cutoff-source:nse-contract-master",
    )
    contract = OptionContractIdentity(
        subject="SYNTHETIC",
        subject_class=SubjectClass.EQUITY,
        option_type=option_type,
        strike=strike,
        expiry_date=expiration_at.date(),
        expiration=expiration,
        native_instrument_ref=f"instrument:{suffix}",
        lot_size=25,
        provenance_refs=("provider:nse-fixture",),
    )
    return OptionQuoteEvidence(
        quote_id=f"quote:{suffix}",
        contract=contract,
        bid=bid,
        ask=ask,
        top_bid_quantity=bid_quantity,
        top_ask_quantity=ask_quantity,
        quantity_unit="CONTRACTS",
        timing=timing or qualified_market_timing(),
        ltp=Decimal("100"),
        open_interest=0,
        volume=0,
        provenance_refs=("observation:quote-fixture", "provider:nse-fixture"),
    )


def option_chain(
    *,
    expiration_at: datetime = TARGET + timedelta(days=7),
    option_type: OptionType = OptionType.CE,
    strikes: tuple[Decimal, ...] = (Decimal("90"), Decimal("100"), Decimal("110")),
    bids: tuple[Decimal | None, ...] | None = None,
    asks: tuple[Decimal | None, ...] | None = None,
    bid_quantities: tuple[Decimal | None, ...] | None = None,
    ask_quantities: tuple[Decimal | None, ...] | None = None,
    timing: MarketTimingQualification | None = None,
) -> ExpiryChainEvidence:
    count = len(strikes)
    supplied_bids = bids or (Decimal("99.5"),) * count
    supplied_asks = asks or (Decimal("100.5"),) * count
    supplied_bid_quantities = bid_quantities or (Decimal("25"),) * count
    supplied_ask_quantities = ask_quantities or (Decimal("50"),) * count
    quotes = tuple(
        option_quote(
            expiration_at=expiration_at,
            strike=strike,
            option_type=option_type,
            bid=supplied_bids[index],
            ask=supplied_asks[index],
            bid_quantity=supplied_bid_quantities[index],
            ask_quantity=supplied_ask_quantities[index],
            timing=timing,
        )
        for index, strike in enumerate(strikes)
    )
    coverage = CoverageProof(
        state=CoverageState.PRESENT,
        scope_ref=f"scope:chain-{expiration_at.date()}",
        checked_at=NOW,
        observed_item_count=count,
        expected_item_count=count,
        scope_complete=True,
        qualification_source_ref="coverage-source:nse-fixture",
        evidence_refs=("coverage-evidence:nse-fixture",),
    )
    expiration = quotes[0].contract.expiration
    return ExpiryChainEvidence(
        chain_id=f"chain:synthetic-{expiration_at.date()}",
        subject="SYNTHETIC",
        subject_class=SubjectClass.EQUITY,
        expiration=expiration,
        underlying_price=Decimal("101"),
        underlying_timing=timing or qualified_market_timing(),
        quotes=quotes,
        coverage=coverage,
        provenance_refs=("provider:nse-fixture",),
    )


def option_capture(
    chains: tuple[ExpiryChainEvidence, ...],
    *,
    state: CoverageState = CoverageState.PRESENT,
) -> DerivativesEvidenceCapture:
    complete = state in {CoverageState.PRESENT, CoverageState.CONFIRMED_EMPTY}
    proof = CoverageProof(
        state=state,
        scope_ref=f"scope:capture-{state.value.lower()}",
        checked_at=NOW,
        observed_item_count=len(chains),
        expected_item_count=len(chains) if complete else None,
        scope_complete=complete,
        qualification_source_ref="coverage-source:nse-fixture" if complete else None,
        evidence_refs=("coverage-evidence:nse-fixture",) if complete else (),
    )
    return DerivativesEvidenceCapture(
        capture_id=f"derivatives-capture:a62-{state.value.lower()}",
        subject="SYNTHETIC",
        subject_class=SubjectClass.EQUITY,
        captured_as_of=NOW,
        chains=chains,
        coverage=proof,
        provenance_refs=("provider:nse-fixture",),
    )


def context(
    *,
    direction: ExpressionDirection = ExpressionDirection.BULLISH,
    a4: A4Result | None = None,
    chains: tuple[ExpiryChainEvidence, ...] | None = None,
    capture: DerivativesEvidenceCapture | None = None,
    preferences: ExpressionPreferences | None = None,
    event_evidence: EventEvidenceWindow | None = None,
) -> tuple[
    TradeExpressionRequest,
    A4Result,
    ExpressionEvidenceBundle,
    TradeExpressionPolicy,
    AdmissionResult,
]:
    selected_a4 = a4 or directional_a4(direction)
    selected_capture = capture or option_capture(
        chains
        or (
            option_chain(
                option_type=OptionType.CE
                if direction is ExpressionDirection.BULLISH
                else OptionType.PE
            ),
        )
    )
    evidence = bundle(selected_a4, capture=selected_capture)
    if event_evidence is not None:
        evidence = ExpressionEvidenceBundle.model_validate(
            {**evidence.model_dump(mode="python"), "event_evidence": event_evidence}
        )
    value = request(selected_a4, evidence=evidence, direction=direction)
    if preferences is not None:
        value = TradeExpressionRequest.model_validate(
            {**value.model_dump(mode="python"), "preferences": preferences}
        )
    policy = deterministic_policy()
    admission = admit_request(value, selected_a4, evidence, policy)
    return value, selected_a4, evidence, policy, admission
