"""Deterministic A1 contexts for feature-foundation tests."""

from datetime import timedelta

from tiaf.context import AnalysisContext
from tiaf.contracts import DataQuality
from tiaf.data import OHLCVBar, ProviderNetworkError

from ..context._support import (
    NOW,
    FakeMarketProvider,
    make_builder,
    requirement,
)


def context_with_bars(
    closes: tuple[float, ...] = (100.0, 110.0),
    *,
    highs: tuple[float, ...] | None = None,
    lows: tuple[float, ...] | None = None,
    history_quality: DataQuality = DataQuality.GOOD,
    quote_quality: DataQuality = DataQuality.GOOD,
) -> AnalysisContext:
    """Build a coherent context and replace its history with chronological bars."""
    if highs is not None and len(highs) != len(closes):
        raise ValueError("highs must match closes")
    if lows is not None and len(lows) != len(closes):
        raise ValueError("lows must match closes")

    market = FakeMarketProvider()
    market.history_value = market.history_value.model_copy(
        update={"quality": history_quality}
    )
    market.quote_value = market.quote_value.model_copy(update={"quality": quote_quality})
    builder, *_ = make_builder(market=market)
    context = builder.build("RELIANCE", requirement(), context_id="ctx-features")
    assert context.history is not None

    bars = tuple(
        OHLCVBar(
            instrument=context.history.instrument,
            interval=context.history.interval,
            start_at=NOW - timedelta(days=len(closes) - index),
            end_at=NOW - timedelta(days=len(closes) - index - 1),
            open=close,
            high=(highs[index] if highs is not None else close + 1),
            low=(lows[index] if lows is not None else max(close - 1, 0)),
            close=close,
            volume=index,
            source_provider="test",
        )
        for index, close in enumerate(closes)
    )
    history = context.history.model_copy(update={"bars": bars})
    return context.model_copy(update={"history": history})


def context_without_sources() -> AnalysisContext:
    """Build a context whose quote and history evidence were not requested."""
    builder, *_ = make_builder()
    return builder.build(
        "RELIANCE",
        requirement(
            include_quote=False,
            require_quote=False,
            include_history=False,
            require_history=False,
            history_interval=None,
            history_lookback_days=None,
        ),
        context_id="ctx-no-sources",
    )


def context_with_failed_history() -> AnalysisContext:
    """Build a context with optional history retrieval failure provenance."""
    market = FakeMarketProvider()
    market.history_error = ProviderNetworkError("offline", provider="test")
    builder, *_ = make_builder(market=market)
    return builder.build(
        "RELIANCE",
        requirement(require_history=False),
        context_id="ctx-failed-history",
    )


def context_with_failed_quote() -> AnalysisContext:
    """Build a context with optional quote retrieval failure provenance."""
    market = FakeMarketProvider()
    market.quote_error = ProviderNetworkError("offline", provider="test")
    builder, *_ = make_builder(market=market)
    return builder.build(
        "RELIANCE",
        requirement(require_quote=False),
        context_id="ctx-failed-quote",
    )


def context_with_missing_quote() -> AnalysisContext:
    """Build a context whose requested quote explicitly reports no usable data."""
    market = FakeMarketProvider()
    market.quote_value = market.quote_value.model_copy(
        update={"quality": DataQuality.UNAVAILABLE}
    )
    builder, *_ = make_builder(market=market)
    return builder.build(
        "RELIANCE",
        requirement(require_quote=False),
        context_id="ctx-missing-quote",
    )
