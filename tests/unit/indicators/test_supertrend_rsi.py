"""SuperTrend and RSI deterministic fixtures and boundary behavior."""

import pytest

from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureRequest,
    FeatureStatus,
    builtin_feature_registry,
)
from tiaf.indicators import IndicatorEngine, IndicatorParameterError, builtin_indicator_registry
from tiaf.indicators.library.rsi import wilder_rsi

from ..features._support import context_with_bars
from ._support import calculate, request


def test_supertrend_known_band_transition_fixture() -> None:
    result = calculate(
        "supertrend",
        (10.0, 11.0, 12.0, 11.0, 16.0),
        {"period": 2, "multiplier": 2.0},
        highs=(11.0, 12.0, 13.0, 12.0, 16.0),
        lows=(9.0, 10.0, 11.0, 10.0, 14.0),
    )
    assert result.value("basic_upper_band") == pytest.approx(22.0)
    assert result.value("basic_lower_band") == pytest.approx(8.0)
    assert result.value("final_upper_band") == pytest.approx(15.0)
    assert result.value("final_lower_band") == pytest.approx(8.0)
    assert result.value("line") == pytest.approx(8.0)
    assert result.state("relation") == "ABOVE_LINE"
    assert result.state("active_band") == "LOWER_BAND_ACTIVE"


def test_supertrend_below_and_on_line_states() -> None:
    below = calculate(
        "supertrend",
        (10.0, 10.0, 10.0),
        {"period": 2, "multiplier": 2.0},
        highs=(11.0, 11.0, 11.0),
        lows=(9.0, 9.0, 9.0),
    )
    on_line = calculate(
        "supertrend",
        (10.0, 10.0, 10.0),
        {"period": 2, "multiplier": 2.0},
        highs=(10.0, 10.0, 10.0),
        lows=(10.0, 10.0, 10.0),
    )
    assert below.state("relation") == "BELOW_LINE"
    assert below.state("active_band") == "UPPER_BAND_ACTIVE"
    assert on_line.value("line") == 10.0
    assert on_line.state("relation") == "ON_LINE"


def test_supertrend_atr_reconciles_with_accepted_feature() -> None:
    context = context_with_bars(
        (10.0, 11.0, 12.0, 11.0, 16.0),
        highs=(11.0, 12.0, 13.0, 12.0, 16.0),
        lows=(9.0, 10.0, 11.0, 10.0, 14.0),
    )
    feature = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(
            feature_id="volatility.atr",
            parameters=(("period", 2),),
            interval="1d",
        ),
    )
    indicator = IndicatorEngine(builtin_indicator_registry()).calculate(
        request("supertrend", {"period": 2, "multiplier": 2.0}), context
    )
    latest_midpoint = (16.0 + 14.0) / 2.0
    assert isinstance(feature.value, (int, float))
    assert feature.value == pytest.approx(3.5)
    assert indicator.value("basic_upper_band") == pytest.approx(
        latest_midpoint + (2.0 * feature.value)
    )


def test_supertrend_requires_strict_wilder_warmup() -> None:
    result = calculate(
        "supertrend", (10.0, 11.0), {"period": 2, "multiplier": 3.0}
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


@pytest.mark.parametrize(
    "parameters",
    [
        {"period": 0, "multiplier": 3.0},
        {"period": -1, "multiplier": 3.0},
        {"period": 2, "multiplier": 0.0},
        {"period": 2, "multiplier": -1.0},
    ],
)
def test_supertrend_rejects_nonpositive_parameters(
    parameters: dict[str, int | float],
) -> None:
    with pytest.raises(IndicatorParameterError, match="greater than"):
        calculate("supertrend", (10.0, 11.0, 12.0), parameters)


def test_rsi_exact_initialization_fixture() -> None:
    result = calculate("rsi", (10.0, 11.0, 13.0, 12.0), {"period": 3})
    assert result.value("rsi") == pytest.approx(75.0)
    assert result.lookback_bars_used == 4


def test_rsi_recursive_wilder_smoothing() -> None:
    closes = (10.0, 11.0, 13.0, 12.0, 15.0)
    result = calculate("rsi", closes, {"period": 3})
    assert result.value("rsi") == pytest.approx(88.23529411764706)
    assert result.value("rsi") == wilder_rsi(closes, 3)


@pytest.mark.parametrize(
    ("closes", "expected"),
    [
        ((10.0, 11.0, 12.0, 13.0), 100.0),
        ((13.0, 12.0, 11.0, 10.0), 0.0),
        ((10.0, 10.0, 10.0, 10.0), 50.0),
    ],
)
def test_rsi_zero_gain_loss_conventions(
    closes: tuple[float, ...], expected: float
) -> None:
    result = calculate("rsi", closes, {"period": 3})
    value = result.value("rsi")
    assert value == expected
    assert value is not None
    assert 0.0 <= value <= 100.0


def test_rsi_insufficient_and_invalid_period() -> None:
    result = calculate("rsi", (10.0, 11.0, 12.0), {"period": 3})
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    with pytest.raises(IndicatorParameterError):
        calculate("rsi", (10.0, 11.0), {"period": 0})
