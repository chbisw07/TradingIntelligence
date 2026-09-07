"""Bollinger and Donchian exact-window deterministic behavior."""

import math

import pytest

from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureRequest,
    FeatureStatus,
    builtin_feature_registry,
)
from tiaf.indicators import IndicatorEngine, IndicatorParameterError, builtin_indicator_registry

from ..features._support import context_with_bars
from ._support import calculate, request


def test_bollinger_population_fixture_and_sma_reconciliation() -> None:
    closes = (10.0, 11.0, 12.0, 13.0)
    context = context_with_bars(closes)
    result = IndicatorEngine(builtin_indicator_registry()).calculate(
        request("bollinger", {"period": 4, "stddev_multiplier": 2.0}), context
    )
    feature = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(
            feature_id="trend.sma", parameters=(("period", 4),), interval="1d"
        ),
    )
    deviation = math.sqrt(1.25)
    assert result.value("middle") == feature.value == 11.5
    assert result.value("upper") == pytest.approx(11.5 + (2.0 * deviation))
    assert result.value("lower") == pytest.approx(11.5 - (2.0 * deviation))
    assert result.value("bandwidth_percent") == pytest.approx(
        (4.0 * deviation) / 11.5 * 100.0
    )
    assert result.value("percent_b") == pytest.approx(
        (13.0 - (11.5 - 2.0 * deviation)) / (4.0 * deviation)
    )


def test_bollinger_uses_latest_exact_period() -> None:
    first = calculate(
        "bollinger",
        (999.0, 10.0, 11.0, 12.0),
        {"period": 3, "stddev_multiplier": 2.0},
    )
    second = calculate(
        "bollinger",
        (10.0, 11.0, 12.0),
        {"period": 3, "stddev_multiplier": 2.0},
    )
    assert first.values == second.values
    assert first.lookback_bars_used == 3


def test_bollinger_flat_positive_series_is_centered() -> None:
    result = calculate(
        "bollinger",
        (10.0,) * 4,
        {"period": 4, "stddev_multiplier": 2.0},
    )
    assert result.value("upper") == result.value("middle") == result.value("lower")
    assert result.value("bandwidth_percent") == 0.0
    assert result.value("percent_b") == 0.5


def test_bollinger_insufficient_and_invalid_period() -> None:
    insufficient = calculate(
        "bollinger", (10.0, 11.0), {"period": 3, "stddev_multiplier": 2.0}
    )
    assert insufficient.status is FeatureStatus.INSUFFICIENT_DATA
    with pytest.raises(IndicatorParameterError, match="greater than 1"):
        calculate(
            "bollinger", (10.0, 11.0), {"period": 1, "stddev_multiplier": 2.0}
        )
    zero_middle = calculate(
        "bollinger",
        (0.0, 0.0),
        {"period": 2, "stddev_multiplier": 2.0},
        highs=(0.0, 0.0),
        lows=(0.0, 0.0),
    )
    assert zero_middle.status is FeatureStatus.FAILED
    assert zero_middle.values == ()


@pytest.mark.parametrize(
    ("close", "expected"),
    [(10.0, 0.0), (15.0, 50.0), (20.0, 100.0)],
)
def test_donchian_position_fixture(close: float, expected: float) -> None:
    result = calculate(
        "donchian",
        (12.0, 14.0, close),
        {"period": 3},
        highs=(15.0, 18.0, 20.0),
        lows=(10.0, 11.0, 10.0),
    )
    assert result.value("upper") == 20.0
    assert result.value("lower") == 10.0
    assert result.value("middle") == 15.0
    assert result.value("position_percent") == expected


def test_donchian_uses_latest_exact_window() -> None:
    result = calculate(
        "donchian",
        (50.0, 10.0, 12.0, 14.0),
        {"period": 3},
        highs=(100.0, 15.0, 16.0, 20.0),
        lows=(1.0, 8.0, 10.0, 12.0),
    )
    assert result.value("upper") == 20.0
    assert result.value("lower") == 8.0
    assert result.lookback_bars_used == 3


def test_donchian_flat_channel_and_insufficient_history() -> None:
    flat = calculate(
        "donchian",
        (10.0, 10.0),
        {"period": 2},
        highs=(10.0, 10.0),
        lows=(10.0, 10.0),
    )
    insufficient = calculate("donchian", (10.0,), {"period": 2})
    assert flat.status is FeatureStatus.INSUFFICIENT_DATA
    assert flat.values == ()
    assert insufficient.status is FeatureStatus.INSUFFICIENT_DATA
    with pytest.raises(IndicatorParameterError):
        calculate("donchian", (10.0,), {"period": 0})


def test_indicator_rejects_zero_nonfinite_malformed_and_out_of_order_ohlc() -> None:
    engine = IndicatorEngine(builtin_indicator_registry())
    context = context_with_bars((10.0, 11.0, 12.0))
    assert context.history is not None
    last = context.history.bars[-1]
    variants = (
        last.model_copy(update={"close": 0.0, "low": 0.0}),
        last.model_copy(update={"close": float("inf"), "high": float("inf")}),
        last.model_copy(update={"high": 1.0}),
    )
    for invalid in variants:
        history = context.history.model_copy(
            update={"bars": (*context.history.bars[:-1], invalid)}
        )
        result = engine.calculate(
            request("donchian", {"period": 2}),
            context.model_copy(update={"history": history}),
        )
        assert result.status is FeatureStatus.FAILED
        assert result.values == ()
    reversed_history = context.history.model_copy(
        update={"bars": tuple(reversed(context.history.bars))}
    )
    reversed_result = engine.calculate(
        request("donchian", {"period": 2}),
        context.model_copy(update={"history": reversed_history}),
    )
    assert reversed_result.status is FeatureStatus.FAILED
    duplicate = context.history.bars[-1].model_copy(
        update={"start_at": context.history.bars[-2].start_at}
    )
    duplicate_history = context.history.model_copy(
        update={"bars": (*context.history.bars[:-1], duplicate)}
    )
    duplicate_result = engine.calculate(
        request("donchian", {"period": 2}),
        context.model_copy(update={"history": duplicate_history}),
    )
    assert duplicate_result.status is FeatureStatus.FAILED
