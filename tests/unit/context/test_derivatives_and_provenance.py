"""Derivatives, historical-options, provenance, batching, and summaries."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from threading import Event
from typing import cast

import pytest

from tiaf.context import (
    AnalysisContextBuilder,
    BatchItemStatus,
    EvidenceStatus,
    HistoricalOptionRequirement,
    RequiredEvidenceUnavailableError,
    summarize_context,
)
from tiaf.contracts import DataQuality, FreshnessState, OptionType
from tiaf.data import (
    ExpiryFlag,
    HistoricalOptionExpiryCode,
    InstrumentQuery,
    MarketDataProvider,
    ProviderNetworkError,
    RelativeStrike,
)
from tiaf.data.resolution import InstrumentResolver, ResolutionResult
from tiaf.data.runtime import (
    CacheEntry,
    CacheKey,
    DataFetchCoordinator,
    FetchDisposition,
    FreshnessRequirement,
    InMemoryCacheBackend,
)

from ._support import (
    EXPIRY,
    FRESH,
    NOW,
    FakeDerivativesProvider,
    FakeHistoricalOptionsProvider,
    FakeMarketProvider,
    FakeResolver,
    make_builder,
    quote,
    requirement,
)


def evidence(context: object, name: str) -> object:
    return next(item for item in context.evidence if item.evidence_name == name)  # type: ignore[attr-defined]


def derivatives_requirement(**changes: object) -> object:
    values: dict[str, object] = {
        "include_derivatives": True,
        "option_expiry": EXPIRY,
        "derivatives_freshness": FRESH,
    }
    values.update(changes)
    return requirement(**values)


def historical_requirement(**changes: object) -> object:
    request = HistoricalOptionRequirement(
        interval="15m",
        expiry_flag=ExpiryFlag.MONTH,
        expiry_code=HistoricalOptionExpiryCode.NEAR,
        relative_strike=RelativeStrike("ATM"),
        option_type=OptionType.CE,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 7),
    )
    values: dict[str, object] = {
        "include_historical_options": True,
        "historical_option_requests": (request,),
        "historical_options_freshness": FRESH,
    }
    values.update(changes)
    return requirement(**values)


def test_explicit_option_chain_expiry_is_fetched_and_preserved() -> None:
    derivatives = FakeDerivativesProvider()
    builder, *_ = make_builder(derivatives=derivatives)
    context = builder.build("RELIANCE", derivatives_requirement())  # type: ignore[arg-type]
    assert derivatives.calls[0][1] == EXPIRY
    assert context.option_chain is not None
    assert context.option_chain.expiry == EXPIRY
    assert len(context.option_chain.strikes) == 1
    assert evidence(context, "option_chain").fetch_disposition is FetchDisposition.PROVIDER  # type: ignore[attr-defined]


def test_optional_option_chain_failure_keeps_context_complete() -> None:
    derivatives = FakeDerivativesProvider()
    derivatives.chain_error = ProviderNetworkError("offline", provider="test")
    builder, *_ = make_builder(derivatives=derivatives)
    context = builder.build("RELIANCE", derivatives_requirement())  # type: ignore[arg-type]
    assert context.option_chain is None
    assert evidence(context, "option_chain").status is EvidenceStatus.FAILED  # type: ignore[attr-defined]
    assert context.complete
    assert context.overall_quality is DataQuality.PARTIAL


def test_required_option_chain_failure_returns_degraded_partial_context() -> None:
    derivatives = FakeDerivativesProvider()
    derivatives.chain_error = ProviderNetworkError("offline", provider="test")
    builder, *_ = make_builder(derivatives=derivatives)
    context = builder.build(
        "RELIANCE", derivatives_requirement(require_derivatives=True)  # type: ignore[arg-type]
    )
    assert not context.complete
    assert context.overall_quality is DataQuality.DEGRADED
    assert context.missing_required_evidence == ("option_chain",)


def test_required_option_chain_failure_is_strict_when_partial_denied() -> None:
    derivatives = FakeDerivativesProvider()
    derivatives.chain_error = ProviderNetworkError("offline", provider="test")
    builder, *_ = make_builder(derivatives=derivatives)
    with pytest.raises(RequiredEvidenceUnavailableError, match="option_chain"):
        builder.build(
            "RELIANCE",
            derivatives_requirement(  # type: ignore[arg-type]
                require_derivatives=True, allow_partial=False
            ),
        )


def test_missing_optional_derivatives_dependency_is_visible() -> None:
    builder, *_ = make_builder()
    context = builder.build("RELIANCE", derivatives_requirement())  # type: ignore[arg-type]
    descriptor = evidence(context, "option_chain")
    assert descriptor.status is EvidenceStatus.FAILED  # type: ignore[attr-defined]
    assert descriptor.error_type == "AnalysisContextBuildError"  # type: ignore[attr-defined]


def test_historical_options_are_only_fetched_when_requested() -> None:
    historical = FakeHistoricalOptionsProvider()
    builder, *_ = make_builder(historical=historical)
    context = builder.build("RELIANCE", requirement())
    assert historical.calls == []
    assert context.historical_options is None
    assert evidence(context, "historical_options").status is EvidenceStatus.NOT_REQUESTED  # type: ignore[attr-defined]


def test_historical_options_exact_specification_and_series_are_preserved() -> None:
    historical = FakeHistoricalOptionsProvider()
    builder, *_ = make_builder(historical=historical)
    context = builder.build("RELIANCE", historical_requirement())  # type: ignore[arg-type]
    call = historical.calls[0]
    assert call[1:] == (
        "15m",
        ExpiryFlag.MONTH,
        HistoricalOptionExpiryCode.NEAR,
        RelativeStrike("ATM"),
        OptionType.CE,
        date(2026, 9, 1),
        date(2026, 9, 7),
    )
    assert context.historical_options is not None
    assert len(context.historical_options) == 1


def test_historical_options_failure_semantics() -> None:
    historical = FakeHistoricalOptionsProvider()
    historical.error = ProviderNetworkError("offline", provider="test")
    builder, *_ = make_builder(historical=historical)
    context = builder.build(
        "RELIANCE",
        historical_requirement(require_historical_options=True),  # type: ignore[arg-type]
    )
    assert not context.complete
    assert context.historical_options == ()
    assert evidence(context, "historical_options[0]").status is EvidenceStatus.FAILED  # type: ignore[attr-defined]


def test_repeated_build_preserves_provider_then_cache_provenance() -> None:
    builder, _, market, *_ = make_builder()
    first = builder.build("RELIANCE", requirement())
    second = builder.build("RELIANCE", requirement())
    assert market.quote_calls == 1
    assert len(market.history_calls) == 1
    assert evidence(first, "quote").fetch_disposition is FetchDisposition.PROVIDER  # type: ignore[attr-defined]
    assert evidence(second, "quote").fetch_disposition is FetchDisposition.CACHE  # type: ignore[attr-defined]
    assert evidence(second, "quote").cache_disposition.value == "HIT_FRESH"  # type: ignore[attr-defined]


def test_stale_fallback_and_age_are_preserved_in_evidence() -> None:
    market = FakeMarketProvider()
    market.quote_error = ProviderNetworkError("offline", provider="test")
    cache = InMemoryCacheBackend()
    key = CacheKey(
        namespace="market",
        provider="test",
        instrument_identity="NSE_EQUITY:2885",
        operation="quote",
    )
    stale_quote = quote(observed_at=NOW - timedelta(seconds=100))
    cache.put(
        key,
        CacheEntry(
            key=key,
            value=stale_quote,
            stored_at=NOW - timedelta(seconds=100),
            observed_at=NOW - timedelta(seconds=100),
            source_provider="test",
        ),
    )
    coordinator = DataFetchCoordinator(cache, wall_clock=lambda: NOW)
    builder = AnalysisContextBuilder(
        cast(InstrumentResolver, FakeResolver()),
        cast(MarketDataProvider, market),
        coordinator,
        clock=lambda: NOW,
        context_id_factory=lambda: "stale",
    )
    freshness = FreshnessRequirement(
        fresh_for_seconds=10,
        aging_for_seconds=20,
        max_stale_seconds=200,
    )
    context = builder.build(
        "RELIANCE",
        requirement(
            include_history=False,
            require_history=False,
            history_interval=None,
            history_lookback_days=None,
            quote_freshness=freshness,
            allow_stale_on_error=True,
        ),
    )
    descriptor = evidence(context, "quote")
    assert descriptor.stale_fallback_used  # type: ignore[attr-defined]
    assert descriptor.retrieval_age_seconds == 100  # type: ignore[attr-defined]
    assert context.overall_retrieval_freshness is FreshnessState.STALE


def test_simultaneous_contexts_preserve_coalesced_provenance() -> None:
    started = Event()
    release = Event()

    class BlockingMarket(FakeMarketProvider):
        def get_quote(self, requested: object) -> object:  # type: ignore[override]
            self.quote_calls += 1
            started.set()
            assert release.wait(2)
            return self.quote_value

    market = BlockingMarket()
    builder, *_ = make_builder(market=market)
    quote_only = requirement(
        include_history=False,
        require_history=False,
        history_interval=None,
        history_lookback_days=None,
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(builder.build, "RELIANCE", quote_only)
        assert started.wait(2)
        second = pool.submit(builder.build, "RELIANCE", quote_only)
        release.set()
        contexts = (first.result(timeout=2), second.result(timeout=2))
    dispositions = {evidence(item, "quote").fetch_disposition for item in contexts}  # type: ignore[attr-defined]
    assert dispositions == {FetchDisposition.PROVIDER, FetchDisposition.COALESCED}
    assert market.quote_calls == 1


def test_build_many_preserves_order_and_explicit_errors() -> None:
    missing = InstrumentQuery(symbol="MISSING")
    outcome = ResolutionResult(query=missing, matches=(), not_found=True, observed_at=NOW)
    resolver = FakeResolver({"MISSING": outcome})
    builder, *_ = make_builder(resolver_value=resolver)
    results = builder.build_many(("RELIANCE", "MISSING", "OTHER"), requirement())
    assert tuple(item.symbol for item in results) == ("RELIANCE", "MISSING", "OTHER")
    assert results[0].status is BatchItemStatus.COMPLETE_CONTEXT
    assert results[0].context is not None
    assert results[1].status is BatchItemStatus.ERROR
    assert results[1].context is None
    assert results[1].error_type == "AnalysisContextResolutionError"
    assert results[2].context is not None


def test_summary_contains_counts_and_no_intelligence_fields() -> None:
    derivatives = FakeDerivativesProvider()
    builder, *_ = make_builder(derivatives=derivatives)
    context = builder.build("RELIANCE", derivatives_requirement())  # type: ignore[arg-type]
    summary = summarize_context(context)
    dumped = summary.model_dump()
    assert summary.quote_ltp == 1400
    assert summary.history_bar_count == 1
    assert summary.option_chain_strike_count == 1
    assert summary.option_expiry == EXPIRY
    assert not {"buy", "sell", "ce", "pe", "recommendation", "score"} & set(dumped)


def test_builder_has_no_dhan_dependency() -> None:
    import inspect

    source = inspect.getsource(AnalysisContextBuilder)
    assert "Dhan" not in source
    assert "get_quote(" in source
    assert "_coordinator.get_or_fetch" in source
