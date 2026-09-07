"""A2.3 adjacent high/low and rolling-range structure behavior."""

import pytest

from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    builtin_feature_registry,
)

from ._support import context_with_bars


def _compute_fraction(
    feature_id: str,
    *,
    highs: tuple[float, ...],
    lows: tuple[float, ...],
    bars: int,
) -> FeatureResult:
    closes = tuple((high + low) / 2.0 for high, low in zip(highs, lows, strict=True))
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
    ("feature_id", "highs", "lows", "expected"),
    [
        ("structure.higher_high_fraction", (10.0, 11.0, 12.0), (1.0, 1.0, 1.0), 1.0),
        ("structure.lower_high_fraction", (12.0, 11.0, 10.0), (1.0, 1.0, 1.0), 1.0),
        ("structure.higher_low_fraction", (12.0, 12.0, 12.0), (1.0, 2.0, 3.0), 1.0),
        ("structure.lower_low_fraction", (12.0, 12.0, 12.0), (3.0, 2.0, 1.0), 1.0),
    ],
)
def test_strict_structure_fraction_known_paths(
    feature_id: str,
    highs: tuple[float, ...],
    lows: tuple[float, ...],
    expected: float,
) -> None:
    result = _compute_fraction(feature_id, highs=highs, lows=lows, bars=2)
    assert result.value == expected
    assert result.lookback_bars_used == 3


def test_structure_fractions_share_comparison_counts() -> None:
    highs = (10.0, 12.0, 11.0, 11.0)
    lows = (5.0, 6.0, 4.0, 4.0)
    results = {
        feature_id: _compute_fraction(
            feature_id, highs=highs, lows=lows, bars=3
        ).value
        for feature_id in (
            "structure.higher_high_fraction",
            "structure.lower_high_fraction",
            "structure.higher_low_fraction",
            "structure.lower_low_fraction",
        )
    }
    assert results == {
        "structure.higher_high_fraction": pytest.approx(1.0 / 3.0),
        "structure.lower_high_fraction": pytest.approx(1.0 / 3.0),
        "structure.higher_low_fraction": pytest.approx(1.0 / 3.0),
        "structure.lower_low_fraction": pytest.approx(1.0 / 3.0),
    }


@pytest.mark.parametrize(
    "feature_id",
    [
        "structure.higher_high_fraction",
        "structure.lower_high_fraction",
        "structure.higher_low_fraction",
        "structure.lower_low_fraction",
    ],
)
def test_equal_highs_and_lows_count_as_neither_direction(feature_id: str) -> None:
    result = _compute_fraction(
        feature_id,
        highs=(10.0, 10.0, 10.0),
        lows=(5.0, 5.0, 5.0),
        bars=2,
    )
    assert result.value == 0.0


def test_structure_fraction_uses_exact_latest_transition_window() -> None:
    result = _compute_fraction(
        "structure.higher_high_fraction",
        highs=(100.0, 10.0, 11.0, 12.0),
        lows=(1.0, 1.0, 1.0, 1.0),
        bars=2,
    )
    assert result.value == 1.0
    assert result.lookback_bars_used == 3


@pytest.mark.parametrize(
    "feature_id",
    [
        "structure.higher_high_fraction",
        "structure.lower_high_fraction",
        "structure.higher_low_fraction",
        "structure.lower_low_fraction",
    ],
)
def test_structure_fraction_requires_n_plus_one_bars(feature_id: str) -> None:
    result = _compute_fraction(
        feature_id,
        highs=(10.0, 11.0),
        lows=(5.0, 6.0),
        bars=2,
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None


def _position(
    closes: tuple[float, ...],
    highs: tuple[float, ...],
    lows: tuple[float, ...],
    bars: int,
    *,
    quote_ltp: float = 999.0,
) -> FeatureResult:
    context = context_with_bars(
        closes,
        highs=highs,
        lows=lows,
        quote_ltp=quote_ltp,
    )
    return DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(
            feature_id="structure.position_in_rolling_range",
            parameters=(("bars", bars),),
            interval="1d",
        ),
    )


@pytest.mark.parametrize(
    ("closes", "highs", "lows", "expected"),
    [
        ((5.0, 20.0), (10.0, 20.0), (0.0, 5.0), 100.0),
        ((5.0, 0.0), (10.0, 8.0), (0.0, 0.0), 0.0),
        ((5.0, 10.0), (10.0, 20.0), (0.0, 5.0), 50.0),
    ],
)
def test_position_in_rolling_range_known_locations(
    closes: tuple[float, ...],
    highs: tuple[float, ...],
    lows: tuple[float, ...],
    expected: float,
) -> None:
    result = _position(closes, highs, lows, 2)
    assert result.value == expected
    assert result.source_evidence == ("history",)
    assert result.lookback_bars_used == 2


def test_position_in_rolling_range_ignores_current_quote() -> None:
    first = _position((5.0, 10.0), (10.0, 20.0), (0.0, 5.0), 2, quote_ltp=1.0)
    second = _position(
        (5.0, 10.0), (10.0, 20.0), (0.0, 5.0), 2, quote_ltp=10_000.0
    )
    assert first.value == second.value == 50.0


def test_position_in_flat_rolling_range_is_insufficient() -> None:
    result = _position(
        (10.0, 10.0),
        (10.0, 10.0),
        (10.0, 10.0),
        2,
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None


def test_position_in_rolling_range_requires_exact_window() -> None:
    result = _position((5.0, 10.0), (10.0, 20.0), (0.0, 5.0), 3)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
