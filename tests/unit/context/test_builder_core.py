"""Resolution, quote/history, quality, freshness, and failure behavior."""

from datetime import timedelta

import pytest

from tiaf.context import (
    AnalysisContextBuildError,
    AnalysisContextResolutionError,
    EvidenceStatus,
    RequiredEvidenceUnavailableError,
)
from tiaf.contracts import DataQuality, FreshnessState
from tiaf.data import InstrumentQuery, ProviderNetworkError
from tiaf.data.resolution import ResolutionResult
from tiaf.data.runtime import FreshnessRequirement

from ._support import (
    NOW,
    FakeMarketProvider,
    FakeResolver,
    make_builder,
    quote,
    requirement,
    resolved,
)


def descriptor(context: object, name: str) -> object:
    return next(item for item in context.evidence if item.evidence_name == name)  # type: ignore[attr-defined]


def test_symbol_resolution_success_and_identity_preserved() -> None:
    builder, resolver, *_ = make_builder()
    context = builder.build("reliance", requirement())
    assert resolver.queries[0].symbol == "RELIANCE"
    assert context.subject.resolved_instrument.provider_instrument_id == "2885"
    assert context.subject.symbol == "RELIANCE"


def test_explicit_query_is_preserved_for_resolution() -> None:
    builder, resolver, *_ = make_builder()
    query = InstrumentQuery(symbol="RELIANCE", exchange="NSE")
    builder.build(query, requirement())
    assert resolver.queries == [query]


def test_missing_freshness_configuration_is_a_build_error() -> None:
    builder, *_ = make_builder()
    with pytest.raises(AnalysisContextBuildError, match="freshness policy"):
        builder.build("RELIANCE", requirement(quote_freshness=None))


def test_ambiguous_resolution_raises_typed_error() -> None:
    query = InstrumentQuery(symbol="DUAL")
    first = resolved("DUAL", "1")
    second = resolved("DUAL", "2")
    outcome = ResolutionResult(
        query=query,
        matches=(first, second),
        ambiguous=True,
        observed_at=NOW,
    )
    builder, *_ = make_builder(resolver_value=FakeResolver({"DUAL": outcome}))
    with pytest.raises(AnalysisContextResolutionError, match="ambiguous"):
        builder.build("DUAL", requirement())


def test_not_found_resolution_raises_typed_error() -> None:
    query = InstrumentQuery(symbol="MISSING")
    outcome = ResolutionResult(query=query, matches=(), not_found=True, observed_at=NOW)
    builder, *_ = make_builder(resolver_value=FakeResolver({"MISSING": outcome}))
    with pytest.raises(AnalysisContextResolutionError, match="not found"):
        builder.build("MISSING", requirement())


def test_required_quote_and_history_are_fetched_through_runtime() -> None:
    builder, _, market, *_ = make_builder()
    context = builder.build("RELIANCE", requirement())
    assert market.quote_calls == 1
    assert len(market.history_calls) == 1
    assert context.quote is not None
    assert context.history is not None
    assert descriptor(context, "quote").fetch_disposition.value == "PROVIDER"  # type: ignore[attr-defined]


def test_history_range_uses_explicit_calendar_days_and_requested_time() -> None:
    builder, _, market, *_ = make_builder()
    context = builder.build("RELIANCE", requirement(history_lookback_days=90))
    interval, start_at, end_at = market.history_calls[0]
    assert interval == "1d"
    assert start_at == NOW - timedelta(days=90)
    assert end_at == NOW
    assert context.history is not None
    assert context.history.interval == "1d"
    assert len(context.history.bars) == 1


def test_all_required_good_is_complete_good_and_fresh() -> None:
    builder, *_ = make_builder()
    context = builder.build("RELIANCE", requirement())
    assert context.complete
    assert context.overall_quality is DataQuality.GOOD
    assert context.overall_retrieval_freshness is FreshnessState.FRESH
    assert context.missing_required_evidence == ()


def test_optional_not_requested_does_not_reduce_completeness_or_quality() -> None:
    builder, *_ = make_builder()
    context = builder.build("RELIANCE", requirement())
    option_evidence = descriptor(context, "option_chain")
    assert option_evidence.status is EvidenceStatus.NOT_REQUESTED  # type: ignore[attr-defined]
    assert context.complete
    assert context.overall_quality is DataQuality.GOOD


def test_optional_quote_failure_returns_complete_partial_context() -> None:
    market = FakeMarketProvider()
    market.quote_error = ProviderNetworkError("offline", provider="test")
    builder, *_ = make_builder(market=market)
    context = builder.build("RELIANCE", requirement(require_quote=False))
    assert context.quote is None
    assert descriptor(context, "quote").status is EvidenceStatus.FAILED  # type: ignore[attr-defined]
    assert context.complete
    assert context.overall_quality is DataQuality.PARTIAL
    assert context.warnings


def test_required_quote_failure_with_partial_allowed_returns_unavailable_context() -> None:
    market = FakeMarketProvider()
    market.quote_error = ProviderNetworkError("offline", provider="test")
    builder, *_ = make_builder(market=market)
    context = builder.build("RELIANCE", requirement(allow_partial=True))
    assert not context.complete
    assert context.overall_quality is DataQuality.UNAVAILABLE
    assert context.missing_required_evidence == ("quote",)


def test_required_quote_failure_with_partial_denied_raises() -> None:
    market = FakeMarketProvider()
    market.quote_error = ProviderNetworkError("offline", provider="test")
    builder, *_ = make_builder(market=market)
    with pytest.raises(RequiredEvidenceUnavailableError, match="quote"):
        builder.build("RELIANCE", requirement(allow_partial=False))


def test_history_failure_with_partial_allowed_is_visible() -> None:
    market = FakeMarketProvider()
    market.history_error = ProviderNetworkError("offline", provider="test")
    builder, *_ = make_builder(market=market)
    context = builder.build("RELIANCE", requirement())
    assert descriptor(context, "history").status is EvidenceStatus.FAILED  # type: ignore[attr-defined]
    assert context.history is None
    assert not context.complete


def test_required_partial_evidence_is_acceptable_only_when_partial_allowed() -> None:
    market = FakeMarketProvider()
    market.quote_value = quote(quality=DataQuality.PARTIAL)
    builder, *_ = make_builder(market=market)
    partial = builder.build("RELIANCE", requirement(allow_partial=True))
    assert partial.complete
    assert partial.overall_quality is DataQuality.PARTIAL

    strict_builder, *_ = make_builder(market=market)
    with pytest.raises(RequiredEvidenceUnavailableError):
        strict_builder.build("RELIANCE", requirement(allow_partial=False))


@pytest.mark.parametrize(
    ("age", "freshness"),
    [
        (1, FreshnessState.FRESH),
        (90, FreshnessState.AGING),
        (180, FreshnessState.STALE),
    ],
)
def test_required_freshness_aggregation(age: int, freshness: FreshnessState) -> None:
    market = FakeMarketProvider()
    market.quote_value = quote(
        observed_at=NOW - timedelta(seconds=age),
        received_at=NOW - timedelta(seconds=age),
    )
    requirement_value = requirement(
        quote_freshness=FreshnessRequirement(
            fresh_for_seconds=60,
            aging_for_seconds=120,
            max_stale_seconds=300,
            allow_stale=True,
        )
    )
    builder, *_ = make_builder(market=market)
    context = builder.build("RELIANCE", requirement_value)
    assert context.overall_retrieval_freshness is freshness


def test_optional_stale_does_not_affect_required_freshness() -> None:
    market = FakeMarketProvider()
    market.quote_value = quote(
        observed_at=NOW - timedelta(seconds=180),
        received_at=NOW - timedelta(seconds=180),
    )
    builder, *_ = make_builder(market=market)
    context = builder.build(
        "RELIANCE",
        requirement(
            require_quote=False,
            quote_freshness=FreshnessRequirement(
                fresh_for_seconds=10,
                aging_for_seconds=20,
                max_stale_seconds=300,
                allow_stale=True,
            ),
        ),
    )
    assert descriptor(context, "quote").retrieval_freshness is FreshnessState.STALE  # type: ignore[attr-defined]
    assert context.overall_retrieval_freshness is FreshnessState.FRESH
