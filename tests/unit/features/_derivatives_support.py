"""Rich provider-neutral option-chain fixtures for A2.7 tests."""

from datetime import date, datetime

from tiaf.context import AnalysisContext, EvidenceStatus
from tiaf.contracts import DataQuality, FreshnessState, OptionType
from tiaf.data import (
    InstrumentKey,
    InstrumentType,
    MarketSegment,
    OptionChainSnapshot,
    OptionGreeks,
    OptionMarketSnapshot,
    OptionStrikeSnapshot,
)

from ..context._support import (
    EXPIRY,
    FRESH,
    NOW,
    FakeDerivativesProvider,
    make_builder,
    requirement,
)

STRIKES = (1300.0, 1350.0, 1400.0, 1450.0, 1500.0)


def _option(
    underlying: InstrumentKey,
    strike: float,
    option_type: OptionType,
    index: int,
    *,
    expiry: date,
    observed_at: datetime,
) -> OptionMarketSnapshot:
    is_call = option_type is OptionType.CE
    ltp = float((5 - index) * 10 if is_call else (index + 1) * 10)
    provider_id = f"{1 if is_call else 2}{index:03d}"
    instrument = InstrumentKey(
        symbol=underlying.symbol,
        exchange=underlying.exchange,
        segment=MarketSegment.NSE_FNO,
        instrument_type=(
            InstrumentType.CALL_OPTION if is_call else InstrumentType.PUT_OPTION
        ),
        expiry=expiry,
        strike=strike,
        option_type=option_type,
        provider_instrument_id=provider_id,
    )
    return OptionMarketSnapshot(
        instrument=instrument,
        option_type=option_type,
        strike=strike,
        expiry=expiry,
        security_id=provider_id,
        ltp=ltp,
        bid=ltp - 1,
        ask=ltp + 1,
        volume=(index + 1 if is_call else 5 - index),
        open_interest=((index + 1) * 10 if is_call else (5 - index) * 10),
        implied_volatility=(10.125 + index if is_call else 20.875 + index),
        greeks=OptionGreeks(
            delta=(0.7 - index * 0.1 if is_call else -0.3 - index * 0.1),
            gamma=0.01 + index * 0.001,
            theta=-1.0 - index * 0.1,
            vega=2.0 + index * 0.1,
        ),
        observed_at=observed_at,
        source_provider="test",
        freshness=FreshnessState.FRESH,
        quality=DataQuality.GOOD,
    )


def option_chain(
    *,
    spot: float | None = 1400.0,
    expiry: date = EXPIRY,
    observed_at: datetime = NOW,
    quality: DataQuality = DataQuality.GOOD,
) -> OptionChainSnapshot:
    """Return five fully populated strikes centered on 1400."""
    builder, *_ = make_builder()
    base = builder.build("RELIANCE", requirement(), context_id="fixture-subject")
    underlying = base.subject.resolved_instrument.instrument
    strikes = tuple(
        OptionStrikeSnapshot(
            strike=strike,
            call=_option(
                underlying,
                strike,
                OptionType.CE,
                index,
                expiry=expiry,
                observed_at=observed_at,
            ),
            put=_option(
                underlying,
                strike,
                OptionType.PE,
                index,
                expiry=expiry,
                observed_at=observed_at,
            ),
        )
        for index, strike in enumerate(STRIKES)
    )
    return OptionChainSnapshot(
        underlying=underlying,
        expiry=expiry,
        underlying_ltp=spot,
        strikes=strikes,
        observed_at=observed_at,
        received_at=observed_at,
        source_provider="test",
        freshness=FreshnessState.FRESH,
        quality=quality,
        snapshot_id="chain-a27",
        metadata={"observed_at_source": "retrieval_time"},
    )


def context_with_option_chain(
    chain: OptionChainSnapshot | None = None,
    *,
    quality: DataQuality = DataQuality.GOOD,
) -> AnalysisContext:
    """Build coherent requested option evidence and install a rich snapshot."""
    derivatives = FakeDerivativesProvider()
    builder, *_ = make_builder(derivatives=derivatives)
    context = builder.build(
        "RELIANCE",
        requirement(
            include_derivatives=True,
            require_derivatives=True,
            option_expiry=EXPIRY,
            derivatives_freshness=FRESH,
        ),
        context_id="ctx-derivatives-features",
    )
    selected = chain or option_chain(quality=quality)
    evidence = tuple(
        item.model_copy(update={"quality": quality})
        if item.evidence_name == "option_chain"
        else item
        for item in context.evidence
    )
    return context.model_copy(update={"option_chain": selected, "evidence": evidence})


def context_without_option_chain_request() -> AnalysisContext:
    """Build context where derivative evidence is explicitly not requested."""
    builder, *_ = make_builder()
    return builder.build("RELIANCE", requirement(), context_id="ctx-no-derivatives")


def context_with_failed_option_chain() -> AnalysisContext:
    """Build optional requested derivative evidence whose acquisition failed."""
    derivatives = FakeDerivativesProvider()
    derivatives.chain_error = RuntimeError("offline")
    builder, *_ = make_builder(derivatives=derivatives)
    context = builder.build(
        "RELIANCE",
        requirement(
            include_derivatives=True,
            require_derivatives=False,
            option_expiry=EXPIRY,
            derivatives_freshness=FRESH,
        ),
        context_id="ctx-failed-derivatives",
    )
    assert next(
        item for item in context.evidence if item.evidence_name == "option_chain"
    ).status is EvidenceStatus.FAILED
    return context
