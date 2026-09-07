"""Live-validation regressions for canonical previous-session close semantics."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from tiaf.context import AnalysisContext
from tiaf.contracts import DataQuality
from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    builtin_feature_registry,
)

from ._support import context_with_bars

IST = ZoneInfo("Asia/Kolkata")
FRIDAY_QUOTE = datetime(2026, 9, 4, 15, 30, tzinfo=IST)
FRIDAY_BAR_END = datetime(2026, 9, 5, 0, 0, tzinfo=IST)
THURSDAY_BAR_END = datetime(2026, 9, 4, 0, 0, tzinfo=IST)


def _compute(
    context: AnalysisContext,
    feature_id: str,
    *,
    parameters: tuple[tuple[str, int], ...] = (),
) -> FeatureResult:
    return DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(
            feature_id=feature_id,
            parameters=parameters,
            interval="1d",
        ),
    )


def test_quote_previous_close_is_canonical_and_reconciles_change_features() -> None:
    context = context_with_bars(
        (1300.0,) * 13 + (1302.5, 1322.0),
        highs=(1310.0,) * 13 + (1312.5, 1332.0),
        lows=(1290.0,) * 13 + (1292.5, 1312.0),
        quote_ltp=1322.0,
        quote_previous_close=1302.5,
    )
    current = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context, FeatureRequest(feature_id="price.current")
    )
    previous = _compute(context, "price.previous_close")
    absolute = _compute(context, "price.change_absolute")
    percent = _compute(context, "price.change_percent")
    atr = _compute(context, "volatility.atr", parameters=(("period", 14),))
    move = _compute(context, "range.move_over_atr", parameters=(("atr_period", 14),))

    assert previous.value == 1302.5
    assert isinstance(current.value, (int, float))
    assert isinstance(previous.value, (int, float))
    assert isinstance(absolute.value, (int, float))
    assert isinstance(atr.value, (int, float))
    assert absolute.value == current.value - previous.value
    assert percent.value == pytest.approx(
        ((current.value / previous.value) - 1) * 100
    )
    assert move.value == pytest.approx(absolute.value / atr.value)
    assert previous.source_evidence == ("quote",)
    assert absolute.source_evidence == ("quote",)
    assert move.source_evidence == ("quote", "history")


def test_latest_same_session_history_close_cannot_override_quote_previous_close() -> None:
    context = context_with_bars(
        (1200.0, 1322.0),
        quote_ltp=1322.0,
        quote_previous_close=1302.5,
        quote_observed_at=FRIDAY_QUOTE,
        latest_bar_end_at=FRIDAY_BAR_END,
    )
    previous = _compute(context, "price.previous_close")
    change = _compute(context, "price.change_percent")
    assert previous.value == 1302.5
    assert change.value == pytest.approx(((1322.0 / 1302.5) - 1) * 100)
    assert previous.metadata["previous_close_source"] == "quote.previous_close"
    assert previous.lookback_bars_used is None


def test_weekend_closed_market_fallback_skips_friday_history_bar() -> None:
    context = context_with_bars(
        (1302.5, 1322.0),
        quote_ltp=1322.0,
        quote_previous_close=None,
        quote_observed_at=FRIDAY_QUOTE,
        latest_bar_end_at=FRIDAY_BAR_END,
    )
    previous = _compute(context, "price.previous_close")
    change = _compute(context, "price.change_percent")
    assert context.created_at.date() > FRIDAY_QUOTE.date()
    assert previous.value == 1302.5
    assert change.value == pytest.approx(((1322.0 / 1302.5) - 1) * 100)
    assert previous.metadata["previous_close_source"] == "history_session_fallback"
    assert previous.metadata["history_includes_quote_session"] is True
    assert previous.lookback_bars_used == 2
    assert previous.source_evidence == ("quote", "history")
    assert "session-aware daily history fallback" in previous.warnings[0]


def test_live_session_fallback_uses_latest_bar_when_current_session_is_absent() -> None:
    context = context_with_bars(
        (1280.0, 1302.5),
        quote_ltp=1322.0,
        quote_previous_close=None,
        quote_observed_at=FRIDAY_QUOTE,
        latest_bar_end_at=THURSDAY_BAR_END,
    )
    previous = _compute(context, "price.previous_close")
    assert previous.value == 1302.5
    assert previous.metadata["history_includes_quote_session"] is False
    assert previous.lookback_bars_used == 1


@pytest.mark.parametrize(
    "invalid_previous_close",
    [0.0, -1.0, float("nan"), float("inf")],
)
def test_invalid_quote_previous_close_uses_valid_daily_fallback(
    invalid_previous_close: float,
) -> None:
    context = context_with_bars(
        (1280.0, 1302.5),
        quote_ltp=1322.0,
        quote_previous_close=invalid_previous_close,
        quote_observed_at=FRIDAY_QUOTE,
        latest_bar_end_at=THURSDAY_BAR_END,
    )
    result = _compute(context, "price.previous_close")
    assert result.status is FeatureStatus.AVAILABLE
    assert result.value == 1302.5
    assert result.metadata["previous_close_source"] == "history_session_fallback"


def test_invalid_quote_and_zero_fallback_close_fail_without_fabrication() -> None:
    context = context_with_bars(
        (0.0,),
        highs=(0.0,),
        lows=(0.0,),
        quote_ltp=1.0,
        quote_previous_close=0.0,
        quote_observed_at=FRIDAY_QUOTE,
        latest_bar_end_at=THURSDAY_BAR_END,
    )
    for feature_id in (
        "price.previous_close",
        "price.change_absolute",
        "price.change_percent",
    ):
        result = _compute(context, feature_id)
        assert result.status is FeatureStatus.FAILED
        assert result.value is None
        assert "must be positive" in result.warnings[-1]


def test_retrieval_time_quote_does_not_guess_a_history_session() -> None:
    context = context_with_bars(
        (1302.5, 1322.0),
        quote_ltp=1322.0,
        quote_previous_close=None,
        quote_observed_at=FRIDAY_QUOTE,
        latest_bar_end_at=FRIDAY_BAR_END,
    )
    assert context.quote is not None
    quote = context.quote.model_copy(
        update={"metadata": {"observed_at_source": "retrieval_time"}}
    )

    result = _compute(context.model_copy(update={"quote": quote}), "price.previous_close")

    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None
    assert result.source_evidence == ("quote",)
    assert result.metadata["source_time_semantics"] == "quote_retrieval_time"
    assert "cannot identify the represented trading session" in result.warnings[0]


def test_fallback_quality_and_provenance_use_both_actual_sources() -> None:
    context = context_with_bars(
        (1280.0, 1302.5),
        quote_ltp=1322.0,
        quote_previous_close=None,
        quote_observed_at=FRIDAY_QUOTE,
        latest_bar_end_at=THURSDAY_BAR_END,
        quote_quality=DataQuality.PARTIAL,
        history_quality=DataQuality.DEGRADED,
    )
    result = _compute(context, "price.change_absolute")
    assert result.status is FeatureStatus.PARTIAL
    assert result.quality is DataQuality.DEGRADED
    assert result.source_evidence == ("quote", "history")
    assert result.as_of == THURSDAY_BAR_END


def test_parameterized_return_percent_remains_history_only_and_unchanged() -> None:
    context = context_with_bars(
        (1000.0, 1100.0),
        quote_ltp=1322.0,
        quote_previous_close=1200.0,
    )
    result = _compute(context, "return.percent", parameters=(("bars", 1),))
    assert result.value == pytest.approx(10.0)
    assert result.source_evidence == ("history",)
