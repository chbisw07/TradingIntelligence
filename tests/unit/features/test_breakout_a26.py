"""A2.6 close/wick excursion and prior-range position semantics."""

import pytest

from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    builtin_feature_registry,
)

from ._support import context_with_bars


def _compute(
    feature_id: str,
    *,
    latest_close: float,
    latest_high: float | None = None,
    latest_low: float | None = None,
    prior_high: float = 10.0,
    prior_low: float = 5.0,
    bars: int = 2,
) -> FeatureResult:
    closes = (7.0, 8.0, latest_close)
    highs = (prior_high, 9.0, latest_high if latest_high is not None else max(9.0, latest_close))
    lows = (prior_low, 6.0, latest_low if latest_low is not None else min(6.0, latest_close))
    context = context_with_bars(closes, highs=highs, lows=lows)
    return DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(
            feature_id=feature_id,
            parameters=(("bars", bars),),
            interval="1d",
        ),
    )


@pytest.mark.parametrize(
    ("feature_id", "latest", "expected"),
    (
        ("breakout.above_prior_high_percent", 9.0, 0.0),
        ("breakout.above_prior_high_percent", 10.0, 0.0),
        ("breakout.above_prior_high_percent", 12.0, 20.0),
        ("breakdown.below_prior_low_percent", 6.0, 0.0),
        ("breakdown.below_prior_low_percent", 5.0, 0.0),
        ("breakdown.below_prior_low_percent", 4.0, 20.0),
    ),
)
def test_close_excursion_is_positive_only(
    feature_id: str, latest: float, expected: float
) -> None:
    assert _compute(feature_id, latest_close=latest).value == pytest.approx(expected)


def test_close_excursion_reconciles_with_signed_distance() -> None:
    context = context_with_bars(
        (7.0, 8.0, 12.0),
        highs=(10.0, 9.0, 13.0),
        lows=(5.0, 6.0, 7.0),
    )
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    requests = tuple(
        FeatureRequest(feature_id=feature_id, parameters=(("bars", 2),), interval="1d")
        for feature_id in (
            "resistance.distance_percent",
            "breakout.above_prior_high_percent",
        )
    )
    signed, excursion = engine.compute(context, requests).results
    assert signed.value == excursion.value == pytest.approx(20.0)


def test_high_wick_can_cross_while_close_remains_below() -> None:
    close_result = _compute(
        "breakout.above_prior_high_percent", latest_close=9.0, latest_high=12.0
    )
    wick_result = _compute(
        "breakout.high_above_prior_high_percent", latest_close=9.0, latest_high=12.0
    )
    assert close_result.value == 0.0
    assert wick_result.value == pytest.approx(20.0)


def test_low_wick_can_cross_while_close_remains_above() -> None:
    close_result = _compute(
        "breakdown.below_prior_low_percent", latest_close=6.0, latest_low=2.0
    )
    wick_result = _compute(
        "breakdown.low_below_prior_low_percent", latest_close=6.0, latest_low=2.0
    )
    assert close_result.value == 0.0
    assert wick_result.value == pytest.approx(60.0)


@pytest.mark.parametrize(
    ("feature_id", "latest_close", "latest_high", "latest_low"),
    (
        ("breakout.high_above_prior_high_percent", 9.0, 9.5, 6.0),
        ("breakdown.low_below_prior_low_percent", 6.0, 9.0, 5.5),
        ("breakout.high_above_prior_high_percent", 9.0, 10.0, 6.0),
        ("breakdown.low_below_prior_low_percent", 6.0, 9.0, 5.0),
    ),
)
def test_no_wick_excursion_and_exact_touch_are_zero(
    feature_id: str,
    latest_close: float,
    latest_high: float,
    latest_low: float,
) -> None:
    assert _compute(
        feature_id,
        latest_close=latest_close,
        latest_high=latest_high,
        latest_low=latest_low,
    ).value == 0.0


@pytest.mark.parametrize(
    ("latest", "expected"),
    ((10.0, 50.0), (5.0, 0.0), (15.0, 100.0), (20.0, 150.0), (4.0, -10.0)),
)
def test_prior_range_position_is_unclamped(latest: float, expected: float) -> None:
    result = _compute(
        "structure.position_vs_prior_range",
        latest_close=latest,
        latest_high=max(15.0, latest),
        latest_low=min(5.0, latest),
        prior_high=15.0,
        prior_low=5.0,
    )
    assert result.value == pytest.approx(expected)


def test_prior_range_position_zero_width_is_insufficient() -> None:
    context = context_with_bars(
        (10.0, 10.0, 10.0),
        highs=(10.0, 10.0, 10.0),
        lows=(10.0, 10.0, 10.0),
    )
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(
            feature_id="structure.position_vs_prior_range",
            parameters=(("bars", 2),),
            interval="1d",
        ),
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None


def test_current_bar_cannot_change_fixed_prior_range() -> None:
    low_current = _compute(
        "resistance.prior_high", latest_close=9.0, latest_high=9.0
    )
    extreme_current = _compute(
        "resistance.prior_high", latest_close=20.0, latest_high=100.0
    )
    assert low_current.value == extreme_current.value == 10.0
