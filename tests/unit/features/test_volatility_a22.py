"""A2.2 candle range, ATR, realized volatility, and normalized movement."""

import math
import statistics

import pytest

from tiaf.context import AnalysisContext
from tiaf.contracts import DataQuality
from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureParameterError,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    builtin_feature_registry,
)

from ._support import context_with_bars


def _request(
    feature_id: str,
    parameters: tuple[tuple[str, int], ...] = (),
    *,
    interval: str = "1d",
) -> FeatureRequest:
    return FeatureRequest(
        feature_id=feature_id,
        parameters=parameters,
        interval=interval,
    )


def _compute(context: AnalysisContext, request: FeatureRequest) -> FeatureResult:
    return DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context, request
    )


@pytest.mark.parametrize(
    ("closes", "highs", "lows", "expected"),
    [
        ((100.0, 100.0), (101.0, 110.0), (99.0, 90.0), 20.0),
        ((100.0, 122.0), (101.0, 125.0), (99.0, 118.0), 25.0),
        ((100.0, 78.0), (101.0, 82.0), (99.0, 75.0), 25.0),
    ],
)
def test_true_range_selects_high_low_or_gap_extreme(
    closes: tuple[float, ...],
    highs: tuple[float, ...],
    lows: tuple[float, ...],
    expected: float,
) -> None:
    result = _compute(
        context_with_bars(closes, highs=highs, lows=lows),
        _request("range.true_range"),
    )
    assert result.value == expected


@pytest.mark.parametrize(
    ("feature_id", "expected"),
    [
        ("range.bar_percent", ((115.0 - 90.0) / 110.0) * 100),
        ("range.body_percent", (abs(110.0 - 100.0) / 110.0) * 100),
        ("range.upper_wick_percent", ((115.0 - 110.0) / 110.0) * 100),
        ("range.lower_wick_percent", ((100.0 - 90.0) / 110.0) * 100),
    ],
)
def test_latest_candle_percentages_are_exact(feature_id: str, expected: float) -> None:
    context = context_with_bars(
        (110.0,), opens=(100.0,), highs=(115.0,), lows=(90.0,)
    )
    result = _compute(context, _request(feature_id))
    assert result.value == pytest.approx(expected)


@pytest.mark.parametrize(
    "feature_id",
    [
        "range.bar_percent",
        "range.body_percent",
        "range.upper_wick_percent",
        "range.lower_wick_percent",
    ],
)
def test_candle_percentage_zero_close_fails_safely(feature_id: str) -> None:
    context = context_with_bars(
        (0.0,), opens=(1.0,), highs=(2.0,), lows=(0.0,)
    )
    result = _compute(context, _request(feature_id))
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


def test_atr_period_14_known_constant_range_fixture() -> None:
    context = context_with_bars(
        (100.0,) * 15,
        highs=(102.0,) * 15,
        lows=(98.0,) * 15,
    )
    result = _compute(
        context, _request("volatility.atr", (("period", 14),))
    )
    assert result.value == 4.0
    assert result.lookback_bars_used == 15


def test_atr_exact_wilder_initialization() -> None:
    context = context_with_bars(
        (10.0, 12.0, 14.0, 17.0),
        highs=(11.0, 13.0, 15.0, 18.0),
        lows=(9.0, 9.0, 11.0, 13.0),
    )
    result = _compute(context, _request("volatility.atr", (("period", 3),)))
    assert result.value == pytest.approx((4.0 + 4.0 + 5.0) / 3.0)


def test_atr_applies_recursive_wilder_smoothing_after_initialization() -> None:
    context = context_with_bars(
        (10.0, 12.0, 14.0, 17.0, 15.0),
        highs=(11.0, 13.0, 15.0, 18.0, 17.0),
        lows=(9.0, 9.0, 11.0, 13.0, 14.0),
    )
    result = _compute(context, _request("volatility.atr", (("period", 3),)))
    initial = (4.0 + 4.0 + 5.0) / 3.0
    assert result.value == pytest.approx(((initial * 2) + 3.0) / 3.0)


def test_atr_requires_period_plus_one_bars() -> None:
    result = _compute(
        context_with_bars((100.0,) * 14),
        _request("volatility.atr", (("period", 14),)),
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.warnings == ("requires 15 history bars; available 14",)


@pytest.mark.parametrize(
    ("feature_id", "parameter_name"),
    [("volatility.atr", "period"), ("range.move_over_atr", "atr_period")],
)
def test_atr_period_parameters_must_be_positive(
    feature_id: str, parameter_name: str
) -> None:
    with pytest.raises(FeatureParameterError, match="positive integer"):
        _compute(
            context_with_bars((100.0, 101.0)),
            _request(feature_id, ((parameter_name, 0),)),
        )


def test_atr_percent_divides_latest_atr_by_latest_close() -> None:
    context = context_with_bars(
        (100.0,) * 15,
        highs=(102.0,) * 15,
        lows=(98.0,) * 15,
    )
    result = _compute(
        context, _request("volatility.atr_percent", (("period", 14),))
    )
    assert result.value == 4.0


def test_atr_percent_rejects_zero_latest_close() -> None:
    result = _compute(
        context_with_bars(
            (1.0, 1.0, 0.0),
            highs=(1.0, 1.0, 1.0),
            lows=(1.0, 1.0, 0.0),
        ),
        _request("volatility.atr_percent", (("period", 2),)),
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


def test_constant_price_series_has_zero_atr() -> None:
    result = _compute(
        context_with_bars(
            (100.0,) * 15,
            highs=(100.0,) * 15,
            lows=(100.0,) * 15,
        ),
        _request("volatility.atr", (("period", 14),)),
    )
    assert result.value == 0.0


def test_realized_volatility_matches_known_log_return_fixture() -> None:
    closes = (100.0, 110.0, 99.0)
    factor = 252
    result = _compute(
        context_with_bars(closes),
        _request(
            "volatility.realized",
            (("bars", 2), ("annualization_factor", factor)),
        ),
    )
    log_returns = (
        math.log(110.0) - math.log(100.0),
        math.log(99.0) - math.log(110.0),
    )
    expected = statistics.stdev(log_returns) * math.sqrt(factor) * 100
    assert result.value == pytest.approx(expected)


def test_realized_volatility_constant_series_is_zero() -> None:
    result = _compute(
        context_with_bars((100.0,) * 6),
        _request(
            "volatility.realized",
            (("bars", 5), ("annualization_factor", 252)),
        ),
    )
    assert result.value == 0.0


def test_realized_volatility_requires_exact_observations() -> None:
    result = _compute(
        context_with_bars((100.0,) * 5),
        _request(
            "volatility.realized",
            (("bars", 5), ("annualization_factor", 252)),
        ),
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.warnings == ("requires 6 history bars; available 5",)


def test_realized_volatility_requires_two_log_returns_for_sample_stdev() -> None:
    result = _compute(
        context_with_bars((100.0, 101.0)),
        _request(
            "volatility.realized",
            (("bars", 1), ("annualization_factor", 252)),
        ),
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert "at least 2 log returns" in result.warnings[-1]


def test_realized_volatility_requires_explicit_annualization_for_every_interval() -> None:
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    for interval in ("1d", "1h"):
        context = context_with_bars((100.0, 101.0, 102.0), interval=interval)
        with pytest.raises(FeatureParameterError, match="annualization_factor"):
            engine.compute_one(
                context,
                FeatureRequest(
                    feature_id="volatility.realized",
                    parameters=(("bars", 2),),
                    interval=interval,
                ),
            )


def test_realized_volatility_rejects_nonpositive_annualization() -> None:
    with pytest.raises(FeatureParameterError, match="positive finite"):
        _compute(
            context_with_bars((100.0, 101.0, 102.0)),
            _request(
                "volatility.realized",
                (("bars", 2), ("annualization_factor", 0)),
            ),
        )


def test_intraday_realized_volatility_accepts_caller_explicit_factor() -> None:
    context = context_with_bars((100.0, 101.0, 102.0), interval="1h")
    result = _compute(
        context,
        _request(
            "volatility.realized",
            (("bars", 2), ("annualization_factor", 1638)),
            interval="1h",
        ),
    )
    assert result.status is FeatureStatus.AVAILABLE


@pytest.mark.parametrize(("quote_ltp", "expected"), [(104.0, 1.0), (96.0, -1.0)])
def test_signed_move_over_atr(quote_ltp: float, expected: float) -> None:
    context = context_with_bars(
        (100.0,) * 15,
        highs=(102.0,) * 15,
        lows=(98.0,) * 15,
        quote_ltp=quote_ltp,
    )
    result = _compute(
        context, _request("range.move_over_atr", (("atr_period", 14),))
    )
    assert result.value == expected


def test_move_over_zero_atr_fails_safely() -> None:
    context = context_with_bars(
        (100.0,) * 15,
        highs=(100.0,) * 15,
        lows=(100.0,) * 15,
        quote_ltp=101.0,
    )
    result = _compute(
        context, _request("range.move_over_atr", (("atr_period", 14),))
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


@pytest.mark.parametrize(
    ("history_quality", "quote_quality", "expected"),
    [
        (DataQuality.GOOD, DataQuality.PARTIAL, DataQuality.PARTIAL),
        (DataQuality.DEGRADED, DataQuality.GOOD, DataQuality.DEGRADED),
    ],
)
def test_move_over_atr_uses_worst_source_quality(
    history_quality: DataQuality,
    quote_quality: DataQuality,
    expected: DataQuality,
) -> None:
    context = context_with_bars(
        (100.0,) * 15,
        highs=(102.0,) * 15,
        lows=(98.0,) * 15,
        quote_ltp=104.0,
        history_quality=history_quality,
        quote_quality=quote_quality,
    )
    result = _compute(
        context, _request("range.move_over_atr", (("atr_period", 14),))
    )
    assert result.status is FeatureStatus.PARTIAL
    assert result.quality is expected
