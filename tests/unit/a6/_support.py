"""Synthetic A6.1 captures over accepted deterministic A4 results."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from tiaf.a4 import A4Result, evaluate_projection
from tiaf.contracts import OptionType
from tiaf.trade_expression import (
    CoverageProof,
    CoverageState,
    DerivativesEvidenceCapture,
    ExpirationQualification,
    ExpirationTiming,
    ExpiryChainEvidence,
    ExpressionDirection,
    ExpressionEvidenceBundle,
    ExpressionHorizon,
    ExpressionHorizonClass,
    FreshnessBasis,
    MarketTimingQualification,
    OptionContractIdentity,
    OptionQuoteEvidence,
    PolicySelection,
    SubjectClass,
    TimingQualification,
    TradeExpressionRequest,
    UpstreamA4Evidence,
    deterministic_policy,
)

from ..a4._support import clean_projection

IST = ZoneInfo("Asia/Kolkata")
NOW = datetime(2026, 9, 10, 12, tzinfo=IST)
TARGET = NOW + timedelta(days=21)
EXPIRY_DATE = date(2026, 10, 8)
EXPIRATION = datetime(2026, 10, 8, 15, 30, tzinfo=IST)


def a4_result() -> A4Result:
    projection = clean_projection()
    return evaluate_projection(projection, evaluated_at=projection.header.evidence_as_of).result


def qualified_market_timing(
    observed_at: datetime = NOW - timedelta(seconds=10),
) -> MarketTimingQualification:
    return MarketTimingQualification(
        observed_at=observed_at,
        acquired_at=observed_at + timedelta(seconds=2),
        qualification=TimingQualification.QUALIFIED,
        freshness_basis=FreshnessBasis.MARKET_OBSERVATION_TIME,
        qualification_source_ref="timing-source:nse-capture",
    )


def expiration() -> ExpirationTiming:
    return ExpirationTiming(
        expiry_date=EXPIRY_DATE,
        expiration_at=EXPIRATION,
        qualification=ExpirationQualification.QUALIFIED_INSTANT,
        qualification_source_ref="expiry-source:nse-contract-master",
        trading_cutoff_at=EXPIRATION,
        trading_cutoff_source_ref="cutoff-source:nse-contract-master",
    )


def option_contract(
    strike: Decimal = Decimal("100"),
    option_type: OptionType = OptionType.CE,
) -> OptionContractIdentity:
    return OptionContractIdentity(
        subject="SYNTHETIC",
        subject_class=SubjectClass.EQUITY,
        option_type=option_type,
        strike=strike,
        expiry_date=EXPIRY_DATE,
        expiration=expiration(),
        native_instrument_ref=f"instrument:{strike}-{option_type.value}",
        lot_size=25,
        provenance_refs=("provider:nse-fixture",),
    )


def quote(
    strike: Decimal = Decimal("100"),
    option_type: OptionType = OptionType.CE,
) -> OptionQuoteEvidence:
    return OptionQuoteEvidence(
        quote_id=f"quote:{strike}-{option_type.value}",
        contract=option_contract(strike, option_type),
        bid=Decimal("99.5"),
        ask=Decimal("100.5"),
        top_bid_quantity=Decimal("25"),
        top_ask_quantity=Decimal("50"),
        quantity_unit="CONTRACTS",
        timing=qualified_market_timing(),
        ltp=Decimal("100"),
        open_interest=0,
        volume=0,
        implied_volatility=None,
        provenance_refs=("provider:nse-fixture", "observation:quote-fixture"),
    )


def coverage(
    state: CoverageState,
    count: int,
    *,
    complete: bool,
) -> CoverageProof:
    qualified = state in {CoverageState.PRESENT, CoverageState.CONFIRMED_EMPTY}
    return CoverageProof(
        state=state,
        scope_ref=f"scope:{state.value.lower()}",
        checked_at=NOW,
        observed_item_count=count,
        expected_item_count=count if complete else None,
        scope_complete=complete,
        qualification_source_ref="coverage-source:nse-fixture" if qualified else None,
        evidence_refs=("coverage-evidence:nse-fixture",) if qualified else (),
    )


def derivatives_capture(
    *,
    capture_coverage: CoverageState = CoverageState.PRESENT,
) -> DerivativesEvidenceCapture:
    if capture_coverage is CoverageState.CONFIRMED_EMPTY:
        chains: tuple[ExpiryChainEvidence, ...] = ()
        proof = coverage(CoverageState.CONFIRMED_EMPTY, 0, complete=True)
    else:
        quotes = (
            quote(Decimal("90")),
            quote(Decimal("100")),
            quote(Decimal("110")),
        )
        chain = ExpiryChainEvidence(
            chain_id="chain:synthetic-2026-10-08",
            subject="SYNTHETIC",
            subject_class=SubjectClass.EQUITY,
            expiration=expiration(),
            underlying_price=Decimal("101"),
            underlying_timing=qualified_market_timing(),
            quotes=quotes,
            coverage=coverage(CoverageState.PRESENT, 3, complete=True),
            provenance_refs=("provider:nse-fixture",),
        )
        chains = (chain,)
        proof = coverage(
            capture_coverage,
            1,
            complete=capture_coverage is CoverageState.PRESENT,
        )
    return DerivativesEvidenceCapture(
        capture_id="derivatives-capture:synthetic-one",
        subject="SYNTHETIC",
        subject_class=SubjectClass.EQUITY,
        captured_as_of=NOW,
        chains=chains,
        coverage=proof,
        provenance_refs=("provider:nse-fixture",),
    )


def bundle(
    result: A4Result | None = None,
    *,
    capture: DerivativesEvidenceCapture | None = None,
) -> ExpressionEvidenceBundle:
    a4 = result or a4_result()
    derivative_evidence = capture or derivatives_capture()
    return ExpressionEvidenceBundle(
        bundle_id="a6-evidence:synthetic-one",
        subject="SYNTHETIC",
        subject_class=SubjectClass.EQUITY,
        evaluation_cutoff=NOW,
        upstream_a4=UpstreamA4Evidence(
            a4_result_ref=a4.result_id,
            a4_result_fingerprint=a4.semantic_fingerprint,
            evidence_as_of=NOW,
            acquired_at=NOW,
            qualification_source_ref="capture:a4-run",
        ),
        derivatives=derivative_evidence,
        provenance_refs=("capture:a4-run", "provider:nse-fixture"),
    )


def request(
    result: A4Result | None = None,
    *,
    evidence: ExpressionEvidenceBundle | None = None,
    direction: ExpressionDirection = ExpressionDirection.BULLISH,
) -> TradeExpressionRequest:
    a4 = result or a4_result()
    supplied = evidence or bundle(a4)
    policy = deterministic_policy()
    return TradeExpressionRequest(
        request_id="a6-request:synthetic-one",
        run_id="a6-run:synthetic-one",
        subject="SYNTHETIC",
        subject_class=SubjectClass.EQUITY,
        objective="OPPORTUNITY",
        direction=direction,
        horizon=ExpressionHorizon(
            horizon_class=ExpressionHorizonClass.POSITIONAL,
            target_end_at=TARGET,
            exact_duration_seconds=Decimal(21 * 24 * 60 * 60),
        ),
        evaluation_cutoff=NOW,
        a4_result_ref=a4.result_id,
        a4_result_fingerprint=a4.semantic_fingerprint,
        derivatives_capture_ref=supplied.derivatives.capture_id,
        derivatives_capture_fingerprint=supplied.derivatives.fingerprint(),
        policy=PolicySelection(
            policy_id=policy.policy_id,
            policy_version=policy.policy_version,
            profile_id=policy.profile_id,
            policy_fingerprint=policy.fingerprint(),
            evaluator_id=policy.evaluator_id,
            evaluator_version=policy.evaluator_version,
            normalizer_id=policy.normalizer_id,
            normalizer_version=policy.normalizer_version,
        ),
        authority_refs=("authority:a6-admission",),
    )
