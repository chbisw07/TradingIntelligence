"""Deterministic factual fixtures for AnalysisContext unit tests."""

from datetime import date, datetime, timedelta
from typing import cast
from zoneinfo import ZoneInfo

from tiaf.context import AnalysisContextBuilder, AnalysisContextRequirement, AnalysisPurpose
from tiaf.contracts import DataQuality, FreshnessState, OptionType
from tiaf.data import (
    DerivativesDataProvider,
    ExpiryFlag,
    HistoricalOptionBar,
    HistoricalOptionExpiryCode,
    HistoricalOptionsDataProvider,
    HistoricalOptionSeries,
    HistoricalSeries,
    InstrumentKey,
    InstrumentQuery,
    InstrumentType,
    MarketDataProvider,
    MarketSegment,
    OHLCVBar,
    OptionChainSnapshot,
    OptionMarketSnapshot,
    OptionStrikeSnapshot,
    QuoteFieldAvailability,
    QuoteSnapshot,
    RelativeStrike,
)
from tiaf.data.resolution import (
    InstrumentResolver,
    ResolutionKind,
    ResolutionResult,
    ResolvedInstrument,
)
from tiaf.data.runtime import DataFetchCoordinator, FreshnessRequirement

IST = ZoneInfo("Asia/Kolkata")
NOW = datetime(2026, 9, 6, 10, 30, tzinfo=IST)
EXPIRY = date(2026, 9, 29)
FRESH = FreshnessRequirement(
    fresh_for_seconds=60,
    aging_for_seconds=120,
    max_stale_seconds=300,
)


def instrument(symbol: str = "RELIANCE", provider_id: str = "2885") -> InstrumentKey:
    return InstrumentKey(
        symbol=symbol,
        exchange="NSE",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
        provider_instrument_id=provider_id,
        trading_symbol=symbol,
    )


def resolved(symbol: str = "RELIANCE", provider_id: str = "2885") -> ResolvedInstrument:
    return ResolvedInstrument(
        instrument=instrument(symbol, provider_id),
        provider_name="test",
        provider_instrument_id=provider_id,
        source_record_id=f"test:NSE_EQUITY:{provider_id}",
        source_observed_at=NOW,
        resolution_kind=ResolutionKind.EXACT,
        quality=DataQuality.GOOD,
    )


def quote(
    subject: InstrumentKey | None = None,
    *,
    quality: DataQuality = DataQuality.GOOD,
    observed_at: datetime = NOW,
    received_at: datetime = NOW,
) -> QuoteSnapshot:
    return QuoteSnapshot(
        instrument=subject or instrument(),
        ltp=1400,
        observed_at=observed_at,
        received_at=received_at,
        source_provider="test",
        freshness=FreshnessState.FRESH,
        quality=quality,
        availability=QuoteFieldAvailability.AVAILABLE,
    )


def history(
    subject: InstrumentKey | None = None,
    *,
    quality: DataQuality = DataQuality.GOOD,
) -> HistoricalSeries:
    selected = subject or instrument()
    bar = OHLCVBar(
        instrument=selected,
        interval="1d",
        start_at=NOW - timedelta(days=2),
        end_at=NOW - timedelta(days=1),
        open=100,
        high=110,
        low=90,
        close=105,
        volume=1000,
        source_provider="test",
    )
    return HistoricalSeries(
        instrument=selected,
        interval="1d",
        bars=(bar,),
        source_provider="test",
        observed_at=NOW,
        freshness=FreshnessState.FRESH,
        quality=quality,
        requested_from=NOW - timedelta(days=90),
        requested_to=NOW,
    )


def option_chain(subject: InstrumentKey | None = None) -> OptionChainSnapshot:
    selected = subject or instrument()
    option_instrument = InstrumentKey(
        symbol=selected.symbol,
        exchange=selected.exchange,
        segment=MarketSegment.NSE_FNO,
        instrument_type=InstrumentType.CALL_OPTION,
        expiry=EXPIRY,
        strike=1400,
        option_type=OptionType.CE,
        provider_instrument_id="9001",
    )
    call = OptionMarketSnapshot(
        instrument=option_instrument,
        option_type=OptionType.CE,
        strike=1400,
        expiry=EXPIRY,
        security_id="9001",
        ltp=50,
        observed_at=NOW,
        source_provider="test",
        freshness=FreshnessState.FRESH,
        quality=DataQuality.GOOD,
    )
    return OptionChainSnapshot(
        underlying=selected,
        expiry=EXPIRY,
        underlying_ltp=1400,
        strikes=(OptionStrikeSnapshot(strike=1400, call=call),),
        observed_at=NOW,
        received_at=NOW,
        source_provider="test",
        freshness=FreshnessState.FRESH,
        quality=DataQuality.GOOD,
    )


def historical_options(subject: InstrumentKey | None = None) -> HistoricalOptionSeries:
    selected = subject or instrument()
    bar = HistoricalOptionBar(
        underlying=selected,
        option_type=OptionType.CE,
        expiry_flag=ExpiryFlag.MONTH,
        expiry_code=HistoricalOptionExpiryCode.NEAR,
        relative_strike=RelativeStrike("ATM"),
        start_at=NOW - timedelta(days=2),
        open=20,
        high=25,
        low=18,
        close=22,
        source_provider="test",
        quality=DataQuality.GOOD,
    )
    return HistoricalOptionSeries(
        underlying=selected,
        option_type=OptionType.CE,
        expiry_flag=ExpiryFlag.MONTH,
        expiry_code=HistoricalOptionExpiryCode.NEAR,
        relative_strike=RelativeStrike("ATM"),
        interval="15m",
        bars=(bar,),
        requested_from=date(2026, 9, 1),
        requested_to=date(2026, 9, 7),
        observed_at=NOW,
        source_provider="test",
        quality=DataQuality.GOOD,
    )


class FakeResolver:
    def __init__(self, outcomes: dict[str, ResolutionResult] | None = None) -> None:
        self.outcomes = outcomes or {}
        self.queries: list[InstrumentQuery] = []

    def resolve(self, query: InstrumentQuery) -> ResolutionResult:
        self.queries.append(query)
        symbol = query.symbol or ""
        if symbol in self.outcomes:
            return self.outcomes[symbol]
        match = resolved(symbol or "RELIANCE", "2885" if symbol == "RELIANCE" else "1")
        return ResolutionResult(
            query=query,
            matches=(match,),
            resolved=match,
            observed_at=NOW,
            source_provider="test",
        )


class FakeMarketProvider:
    def __init__(self) -> None:
        self.quote_value = quote()
        self.history_value = history()
        self.quote_error: Exception | None = None
        self.history_error: Exception | None = None
        self.quote_calls = 0
        self.history_calls: list[tuple[str, datetime, datetime]] = []

    def provider_name(self) -> str:
        return "test"

    def get_quote(self, requested: InstrumentKey) -> QuoteSnapshot:
        self.quote_calls += 1
        if self.quote_error is not None:
            raise self.quote_error
        return self.quote_value.model_copy(update={"instrument": requested})

    def get_historical(
        self,
        requested: InstrumentKey,
        interval: str,
        start_at: datetime,
        end_at: datetime,
    ) -> HistoricalSeries:
        self.history_calls.append((interval, start_at, end_at))
        if self.history_error is not None:
            raise self.history_error
        value = history(requested, quality=self.history_value.quality)
        return value.model_copy(
            update={
                "interval": interval,
                "bars": tuple(
                    bar.model_copy(update={"interval": interval}) for bar in value.bars
                ),
                "requested_from": start_at,
                "requested_to": end_at,
                "observed_at": self.history_value.observed_at,
            }
        )


class FakeDerivativesProvider:
    def __init__(self) -> None:
        self.chain_error: Exception | None = None
        self.calls: list[tuple[InstrumentKey, date]] = []

    def provider_name(self) -> str:
        return "test"

    def get_option_chain(
        self, requested: InstrumentKey, expiry: date
    ) -> OptionChainSnapshot:
        self.calls.append((requested, expiry))
        if self.chain_error is not None:
            raise self.chain_error
        return option_chain(requested)


class FakeHistoricalOptionsProvider:
    def __init__(self) -> None:
        self.error: Exception | None = None
        self.calls: list[tuple[object, ...]] = []

    def provider_name(self) -> str:
        return "test"

    def get_historical_options(
        self,
        underlying: InstrumentKey,
        interval: str,
        expiry_flag: ExpiryFlag,
        expiry_code: HistoricalOptionExpiryCode | int,
        relative_strike: RelativeStrike,
        option_type: OptionType,
        start_date: date,
        end_date: date,
    ) -> HistoricalOptionSeries:
        self.calls.append(
            (
                underlying,
                interval,
                expiry_flag,
                expiry_code,
                relative_strike,
                option_type,
                start_date,
                end_date,
            )
        )
        if self.error is not None:
            raise self.error
        return historical_options(underlying)


def requirement(**changes: object) -> AnalysisContextRequirement:
    values: dict[str, object] = {
        "purpose": AnalysisPurpose.RESEARCH,
        "include_quote": True,
        "include_history": True,
        "require_quote": True,
        "require_history": True,
        "history_interval": "1d",
        "history_lookback_days": 90,
        "quote_freshness": FRESH,
        "history_freshness": FRESH,
    }
    values.update(changes)
    return AnalysisContextRequirement.model_validate(values)


def make_builder(
    *,
    resolver_value: FakeResolver | None = None,
    market: FakeMarketProvider | None = None,
    derivatives: FakeDerivativesProvider | None = None,
    historical: FakeHistoricalOptionsProvider | None = None,
) -> tuple[
    AnalysisContextBuilder,
    FakeResolver,
    FakeMarketProvider,
    FakeDerivativesProvider | None,
    FakeHistoricalOptionsProvider | None,
]:
    selected_resolver = resolver_value or FakeResolver()
    selected_market = market or FakeMarketProvider()
    coordinator = DataFetchCoordinator(wall_clock=lambda: NOW)
    builder = AnalysisContextBuilder(
        cast(InstrumentResolver, selected_resolver),
        cast(MarketDataProvider, selected_market),
        coordinator,
        derivatives_provider=cast(DerivativesDataProvider, derivatives),
        historical_options_provider=cast(HistoricalOptionsDataProvider, historical),
        clock=lambda: NOW,
        context_id_factory=lambda: "ctx-test",
    )
    return builder, selected_resolver, selected_market, derivatives, historical
