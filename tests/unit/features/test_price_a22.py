"""A2.2 price location, change, and rolling-extrema calculations."""

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


def _compute(
    context: AnalysisContext,
    feature_id: str,
    *,
    bars: int | None = None,
) -> FeatureResult:
    parameters = () if bars is None else (("bars", bars),)
    return DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(
            feature_id=feature_id,
            parameters=parameters,
            interval="1d",
        ),
    )


def test_current_session_price_fields_come_from_quote_not_history() -> None:
    context = context_with_bars(
        (100.0, 110.0),
        opens=(98.0, 105.0),
        highs=(102.0, 120.0),
        lows=(95.0, 100.0),
        quote_open=1300.0,
        quote_high=1330.0,
        quote_low=1290.0,
        quote_previous_close=1302.5,
    )
    values = {
        feature_id: _compute(context, feature_id).value
        for feature_id in (
            "price.previous_close",
            "price.open",
            "price.high",
            "price.low",
        )
    }
    assert values == {
        "price.previous_close": 1302.5,
        "price.open": 1300.0,
        "price.high": 1330.0,
        "price.low": 1290.0,
    }
    assert context.quote is not None
    for feature_id in ("price.previous_close", "price.open", "price.high", "price.low"):
        result = _compute(context, feature_id)
        assert result.source_evidence == ("quote",)
        assert result.as_of == context.quote.observed_at


def test_current_price_change_absolute_and_percent_use_quote_previous_close() -> None:
    context = context_with_bars(
        (100.0, 110.0),
        highs=(101.0, 120.0),
        lows=(99.0, 100.0),
        quote_ltp=115.0,
        quote_previous_close=110.0,
    )
    absolute = _compute(context, "price.change_absolute")
    percent = _compute(context, "price.change_percent")
    assert absolute.value == 5.0
    assert percent.value == pytest.approx(((115.0 / 110.0) - 1) * 100)
    assert absolute.source_evidence == ("quote",)
    assert absolute.metadata["previous_close_source"] == "quote.previous_close"


def test_price_change_percent_safely_rejects_zero_reference_close() -> None:
    result = _compute(
        context_with_bars((0.0,), highs=(1.0,), lows=(0.0,), quote_ltp=1.0),
        "price.change_percent",
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None
    assert "positive" in result.warnings[-1]


def test_position_in_day_range_is_exact_and_not_clamped() -> None:
    within = _compute(
        context_with_bars(
            (110.0,),
            opens=(105.0,),
            highs=(120.0,),
            lows=(100.0,),
            quote_ltp=115.0,
            quote_high=120.0,
            quote_low=100.0,
        ),
        "price.position_in_day_range",
    )
    outside = _compute(
        context_with_bars(
            (110.0,),
            opens=(105.0,),
            highs=(120.0,),
            lows=(100.0,),
            quote_ltp=125.0,
            quote_high=120.0,
            quote_low=100.0,
        ),
        "price.position_in_day_range",
    )
    assert within.value == 75.0
    assert outside.value == 125.0
    assert "outside" in outside.warnings[-1]


def test_flat_day_range_is_insufficient_without_fabricated_value() -> None:
    result = _compute(
        context_with_bars(
            (110.0,),
            opens=(110.0,),
            highs=(110.0,),
            lows=(110.0,),
            quote_ltp=110.0,
            quote_high=110.0,
            quote_low=110.0,
        ),
        "price.position_in_day_range",
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None


def test_position_in_day_range_is_not_applicable_to_intraday_history() -> None:
    context = context_with_bars(
        (110.0,),
        opens=(105.0,),
        highs=(120.0,),
        lows=(100.0,),
        interval="1h",
        quote_ltp=115.0,
    )
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(feature_id="price.position_in_day_range", interval="1h"),
    )
    assert result.status is FeatureStatus.NOT_APPLICABLE
    assert "requires interval 1d" in result.warnings[-1]


@pytest.mark.parametrize(
    ("history_quality", "quote_quality", "expected_status", "expected_quality"),
    [
        (
            DataQuality.GOOD,
            DataQuality.PARTIAL,
            FeatureStatus.PARTIAL,
            DataQuality.PARTIAL,
        ),
        (
            DataQuality.DEGRADED,
            DataQuality.GOOD,
            FeatureStatus.AVAILABLE,
            DataQuality.GOOD,
        ),
    ],
)
def test_quote_previous_close_quality_ignores_unused_history(
    history_quality: DataQuality,
    quote_quality: DataQuality,
    expected_status: FeatureStatus,
    expected_quality: DataQuality,
) -> None:
    result = _compute(
        context_with_bars(
            quote_ltp=115.0,
            quote_previous_close=110.0,
            history_quality=history_quality,
            quote_quality=quote_quality,
        ),
        "price.change_absolute",
    )
    assert result.status is expected_status
    assert result.quality is expected_quality
    assert result.source_evidence == ("quote",)


@pytest.mark.parametrize(
    ("feature_id", "expected"),
    [
        ("price.rolling_high", 130.0),
        ("price.rolling_low", 90.0),
        ("price.distance_from_rolling_high_percent", ((110.0 / 130.0) - 1) * 100),
        ("price.distance_from_rolling_low_percent", ((110.0 / 90.0) - 1) * 100),
    ],
)
def test_rolling_extrema_use_only_latest_exact_window(
    feature_id: str, expected: float
) -> None:
    context = context_with_bars(
        (100.0, 105.0, 110.0),
        highs=(500.0, 120.0, 130.0),
        lows=(10.0, 90.0, 100.0),
    )
    result = _compute(context, feature_id, bars=2)
    assert result.value == pytest.approx(expected)
    assert result.lookback_bars_used == 2


def test_rolling_extrema_do_not_shorten_insufficient_window() -> None:
    result = _compute(
        context_with_bars((100.0, 110.0)), "price.rolling_high", bars=3
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.warnings == ("requires 3 history bars; available 2",)


def test_zero_rolling_denominators_fail_safely() -> None:
    context = context_with_bars((0.0,), highs=(0.0,), lows=(0.0,))
    high = _compute(context, "price.distance_from_rolling_high_percent", bars=1)
    low = _compute(context, "price.distance_from_rolling_low_percent", bars=1)
    assert high.status is FeatureStatus.FAILED
    assert low.status is FeatureStatus.FAILED
