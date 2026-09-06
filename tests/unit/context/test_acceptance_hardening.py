"""User-level requirement-role and dual-provenance acceptance regressions."""

from datetime import datetime, timedelta
from typing import cast

from tiaf.context import (
    AnalysisContext,
    AnalysisContextBuilder,
    EvidenceRequirement,
    EvidenceStatus,
)
from tiaf.contracts import FreshnessState
from tiaf.data import MarketDataProvider
from tiaf.data.resolution import InstrumentResolver
from tiaf.data.runtime import DataFetchCoordinator, FetchDisposition

from ._support import (
    NOW,
    FakeDerivativesProvider,
    FakeMarketProvider,
    FakeResolver,
    make_builder,
    quote,
    requirement,
)


def slot(context: AnalysisContext, name: str) -> object:
    return next(item for item in context.evidence if item.evidence_name == name)


def test_optional_requested_failure_exposes_role_and_keeps_complete() -> None:
    derivatives = FakeDerivativesProvider()
    derivatives.chain_error = RuntimeError("failure text is not exposed")
    builder, *_ = make_builder(derivatives=derivatives)
    context = builder.build(
        "RELIANCE",
        requirement(
            include_derivatives=True,
            require_derivatives=False,
            option_expiry="2026-09-29",
            derivatives_freshness=requirement().quote_freshness,
        ),
    )
    descriptor = slot(context, "option_chain")
    assert descriptor.requested  # type: ignore[attr-defined]
    assert not descriptor.required  # type: ignore[attr-defined]
    assert descriptor.requirement_role is EvidenceRequirement.OPTIONAL_REQUESTED  # type: ignore[attr-defined]
    assert descriptor.status is EvidenceStatus.FAILED  # type: ignore[attr-defined]
    assert context.complete
    assert "option_chain: failed" in context.warnings


def test_required_failure_exposes_role_and_makes_partial_context_incomplete() -> None:
    derivatives = FakeDerivativesProvider()
    derivatives.chain_error = RuntimeError("failure")
    builder, *_ = make_builder(derivatives=derivatives)
    context = builder.build(
        "RELIANCE",
        requirement(
            require_derivatives=True,
            option_expiry="2026-09-29",
            derivatives_freshness=requirement().quote_freshness,
        ),
    )
    descriptor = slot(context, "option_chain")
    assert descriptor.requested  # type: ignore[attr-defined]
    assert descriptor.required  # type: ignore[attr-defined]
    assert descriptor.requirement_role is EvidenceRequirement.REQUIRED  # type: ignore[attr-defined]
    assert not context.complete


def test_unrequested_evidence_exposes_explicit_role() -> None:
    builder, *_ = make_builder()
    context = builder.build("RELIANCE", requirement())
    descriptor = slot(context, "option_chain")
    assert not descriptor.requested  # type: ignore[attr-defined]
    assert not descriptor.required  # type: ignore[attr-defined]
    assert descriptor.requirement_role is EvidenceRequirement.NOT_REQUESTED  # type: ignore[attr-defined]


def test_old_market_observation_and_fresh_retrieval_remain_distinct() -> None:
    market = FakeMarketProvider()
    old_observation = NOW - timedelta(days=2)
    market.quote_value = quote(observed_at=old_observation, received_at=NOW)
    builder, *_ = make_builder(market=market)
    context = builder.build("RELIANCE", requirement())
    descriptor = slot(context, "quote")
    assert descriptor.retrieval_freshness is FreshnessState.FRESH  # type: ignore[attr-defined]
    assert descriptor.retrieval_age_seconds == 0  # type: ignore[attr-defined]
    assert descriptor.source_observed_at == old_observation  # type: ignore[attr-defined]
    assert descriptor.observation_age_seconds == 172_800  # type: ignore[attr-defined]
    assert descriptor.source_observed_at != descriptor.received_at  # type: ignore[attr-defined]


def test_cache_hit_age_is_distinct_from_source_observation_age() -> None:
    class Clock:
        value = NOW

        def __call__(self) -> datetime:
            return self.value

    clock = Clock()
    market = FakeMarketProvider()
    source_observed = NOW - timedelta(seconds=1000)
    market.quote_value = quote(observed_at=source_observed, received_at=NOW)
    coordinator = DataFetchCoordinator(wall_clock=clock)
    builder = AnalysisContextBuilder(
        cast(InstrumentResolver, FakeResolver()),
        cast(MarketDataProvider, market),
        coordinator,
        clock=clock,
        context_id_factory=lambda: "context",
    )
    quote_only = requirement(
        include_history=False,
        require_history=False,
        history_interval=None,
        history_lookback_days=None,
    )
    builder.build("RELIANCE", quote_only)
    clock.value = NOW + timedelta(seconds=5)
    second = builder.build("RELIANCE", quote_only)
    descriptor = slot(second, "quote")
    assert descriptor.fetch_disposition is FetchDisposition.CACHE  # type: ignore[attr-defined]
    assert descriptor.retrieval_age_seconds == 5  # type: ignore[attr-defined]
    assert descriptor.observation_age_seconds == 1005  # type: ignore[attr-defined]
    assert descriptor.source_observed_at == source_observed  # type: ignore[attr-defined]


def test_option_chain_observation_semantics_are_explicit() -> None:
    derivatives = FakeDerivativesProvider()
    builder, *_ = make_builder(derivatives=derivatives)
    context = builder.build(
        "RELIANCE",
        requirement(
            include_derivatives=True,
            option_expiry="2026-09-29",
            derivatives_freshness=requirement().quote_freshness,
        ),
    )
    descriptor = slot(context, "option_chain")
    assert (
        descriptor.source_observation_semantics  # type: ignore[attr-defined]
        == "option_chain_acquisition_time_no_authoritative_market_timestamp"
    )


def test_json_round_trip_preserves_both_provenance_dimensions() -> None:
    market = FakeMarketProvider()
    market.quote_value = quote(observed_at=NOW - timedelta(hours=1), received_at=NOW)
    builder, *_ = make_builder(market=market)
    context = builder.build("RELIANCE", requirement())
    restored = AnalysisContext.model_validate_json(context.model_dump_json())
    descriptor = slot(restored, "quote")
    assert descriptor.retrieval_age_seconds == 0  # type: ignore[attr-defined]
    assert descriptor.observation_age_seconds == 3600  # type: ignore[attr-defined]
    assert descriptor.source_observed_at == NOW - timedelta(hours=1)  # type: ignore[attr-defined]
