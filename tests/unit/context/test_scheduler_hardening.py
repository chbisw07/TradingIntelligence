"""Truthful AnalysisContext scheduling deferral and batch semantics."""

import inspect
from typing import cast

import pytest

from tiaf.context import (
    AnalysisContextBuilder,
    AnalysisContextDeferredError,
    BatchItemStatus,
    EvidenceStatus,
)
from tiaf.contracts import DataQuality, FreshnessState
from tiaf.data import InstrumentQuery, MarketDataProvider, ProviderNetworkError
from tiaf.data.providers.dhan import DhanMarketDataProvider
from tiaf.data.resolution import InstrumentResolver, ResolutionResult
from tiaf.data.runtime import (
    DataFetchCoordinator,
    ProviderGateState,
    ProviderScheduler,
    RatePolicy,
    RatePolicyRegistry,
)

from ._support import (
    NOW,
    FakeMarketProvider,
    FakeResolver,
    make_builder,
    requirement,
    resolved,
)


def _outcome(symbol: str, provider_id: str) -> ResolutionResult:
    query = InstrumentQuery(symbol=symbol)
    match = resolved(symbol, provider_id)
    return ResolutionResult(
        query=query,
        matches=(match,),
        resolved=match,
        observed_at=NOW,
        source_provider="test",
    )


def _batch_resolver() -> FakeResolver:
    return FakeResolver(
        {
            "HDFCBANK": _outcome("HDFCBANK", "1333"),
            "KAYNES": _outcome("KAYNES", "12092"),
        }
    )


def _rate_gated_builder() -> tuple[AnalysisContextBuilder, FakeMarketProvider]:
    scheduler = ProviderScheduler(
        RatePolicyRegistry(
            (
                RatePolicy(
                    provider="test",
                    operation="quote",
                    minimum_interval_seconds=2,
                ),
            )
        ),
        monotonic_clock=lambda: 100.0,
        wall_clock=lambda: NOW,
    )
    market = FakeMarketProvider()
    builder = AnalysisContextBuilder(
        cast(InstrumentResolver, _batch_resolver()),
        cast(MarketDataProvider, market),
        DataFetchCoordinator(scheduler=scheduler, wall_clock=lambda: NOW),
        clock=lambda: NOW,
        context_id_factory=lambda: "context-id",
    )
    return builder, market


def _evidence(item: object, name: str) -> object:
    return next(
        descriptor
        for descriptor in item.context.evidence  # type: ignore[attr-defined]
        if descriptor.evidence_name == name
    )


def test_single_build_preserves_typed_scheduler_deferral() -> None:
    builder, market = _rate_gated_builder()
    builder.build("RELIANCE", requirement())

    with pytest.raises(AnalysisContextDeferredError) as caught:
        builder.build("HDFCBANK", requirement(), correlation_id="batch-correlation")

    deferred = caught.value
    assert deferred.provider == "test"
    assert deferred.operation == "quote"
    assert deferred.retry_after_seconds == 2
    assert deferred.gate_state is ProviderGateState.RATE_LIMITED
    assert deferred.reason == "configured provider rate policy"
    assert deferred.partial_context.subject.symbol == "HDFCBANK"
    assert deferred.partial_context.subject.correlation_id == "batch-correlation"
    assert market.quote_calls == 1


def test_rate_gated_fixture_batch_returns_one_complete_and_two_deferred() -> None:
    builder, market = _rate_gated_builder()
    results = builder.build_many(
        ("RELIANCE", "HDFCBANK", "KAYNES"),
        requirement(),
        correlation_id="batch-correlation",
    )

    assert tuple(item.symbol for item in results) == (
        "RELIANCE",
        "HDFCBANK",
        "KAYNES",
    )
    assert tuple(item.status for item in results) == (
        BatchItemStatus.COMPLETE_CONTEXT,
        BatchItemStatus.DEFERRED,
        BatchItemStatus.DEFERRED,
    )
    assert results[0].context is not None
    assert results[0].context.complete
    for item in results[1:]:
        assert item.error_type == "ProviderScheduleBlockedError"
        assert item.reason == "configured provider rate policy"
        assert item.provider == "test"
        assert item.operation == "quote"
        assert item.retry_after_seconds == 2
        assert item.gate_state is ProviderGateState.RATE_LIMITED
        assert item.correlation_id == "batch-correlation"
        assert item.context is not None
        assert item.context.overall_retrieval_freshness is FreshnessState.UNKNOWN
        assert item.context.overall_quality is DataQuality.PARTIAL
        quote_descriptor = _evidence(item, "quote")
        assert quote_descriptor.status is EvidenceStatus.DEFERRED  # type: ignore[attr-defined]
        assert quote_descriptor.quality is None  # type: ignore[attr-defined]
        assert quote_descriptor.retrieval_freshness is None  # type: ignore[attr-defined]
        assert item.context.history is not None
    assert market.quote_calls == 1
    assert len(market.history_calls) == 3


def test_provider_failure_is_partial_failed_context_not_deferred() -> None:
    class SymbolFailureMarket(FakeMarketProvider):
        def get_quote(self, requested: object) -> object:  # type: ignore[override]
            if requested.symbol == "HDFCBANK":  # type: ignore[attr-defined]
                raise ProviderNetworkError("offline", provider="test")
            return super().get_quote(requested)  # type: ignore[arg-type]

    builder = AnalysisContextBuilder(
        cast(InstrumentResolver, _batch_resolver()),
        cast(MarketDataProvider, SymbolFailureMarket()),
        DataFetchCoordinator(wall_clock=lambda: NOW),
        clock=lambda: NOW,
        context_id_factory=lambda: "context-id",
    )
    results = builder.build_many(("RELIANCE", "HDFCBANK", "KAYNES"), requirement())

    assert tuple(item.status for item in results) == (
        BatchItemStatus.COMPLETE_CONTEXT,
        BatchItemStatus.PARTIAL_CONTEXT,
        BatchItemStatus.COMPLETE_CONTEXT,
    )
    assert _evidence(results[1], "quote").status is EvidenceStatus.FAILED  # type: ignore[attr-defined]
    assert results[1].context is not None
    assert results[1].context.overall_quality is DataQuality.UNAVAILABLE


def test_instrument_not_found_remains_error_and_later_symbol_is_retained() -> None:
    missing_query = InstrumentQuery(symbol="HDFCBANK")
    missing = ResolutionResult(
        query=missing_query,
        matches=(),
        not_found=True,
        observed_at=NOW,
    )
    builder, *_ = make_builder(
        resolver_value=FakeResolver(
            {
                "HDFCBANK": missing,
                "KAYNES": _outcome("KAYNES", "12092"),
            }
        )
    )
    results = builder.build_many(("RELIANCE", "HDFCBANK", "KAYNES"), requirement())

    assert results[1].status is BatchItemStatus.ERROR
    assert results[1].error_type == "AnalysisContextResolutionError"
    assert results[1].context is None
    assert results[2].status is BatchItemStatus.COMPLETE_CONTEXT
    assert results[2].context is not None


def test_builder_coordinator_and_scheduler_do_not_sleep() -> None:
    sources = (
        inspect.getsource(AnalysisContextBuilder),
        inspect.getsource(DataFetchCoordinator),
        inspect.getsource(ProviderScheduler),
        inspect.getsource(DhanMarketDataProvider),
    )
    assert all("sleep(" not in source for source in sources)
