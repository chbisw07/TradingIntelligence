"""A2.6 fixed prior boundaries and signed distance semantics."""

import pytest

from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    builtin_feature_registry,
)
from tiaf.features.volatility import wilder_atr

from ._support import context_with_bars


def _compute(
    feature_id: str,
    closes: tuple[float, ...],
    highs: tuple[float, ...],
    lows: tuple[float, ...],
    *,
    bars: int,
    atr_period: int | None = None,
) -> FeatureResult:
    parameters = [("bars", bars)]
    if atr_period is not None:
        parameters.append(("atr_period", atr_period))
    context = context_with_bars(closes, highs=highs, lows=lows)
    return DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(
            feature_id=feature_id,
            parameters=tuple(parameters),
            interval="1d",
        ),
    )


def test_prior_high_excludes_latest_new_high() -> None:
    result = _compute(
        "resistance.prior_high",
        (7.0, 8.0, 9.0, 20.0),
        (10.0, 12.0, 11.0, 25.0),
        (5.0, 6.0, 7.0, 8.0),
        bars=3,
    )
    assert result.value == 12.0
    assert result.lookback_bars_used == 4


def test_prior_low_excludes_latest_new_low() -> None:
    result = _compute(
        "support.prior_low",
        (7.0, 8.0, 9.0, 2.0),
        (10.0, 12.0, 11.0, 4.0),
        (5.0, 3.0, 6.0, 1.0),
        bars=3,
    )
    assert result.value == 3.0


@pytest.mark.parametrize(
    ("feature_id", "expected"),
    (("resistance.prior_high", 12.0), ("support.prior_low", 3.0)),
)
def test_prior_boundary_known_fixture(feature_id: str, expected: float) -> None:
    result = _compute(
        feature_id,
        (7.0, 8.0, 9.0, 8.0),
        (10.0, 12.0, 11.0, 9.0),
        (5.0, 3.0, 6.0, 7.0),
        bars=3,
    )
    assert result.status is FeatureStatus.AVAILABLE
    assert result.value == expected


@pytest.mark.parametrize("feature_id", ("resistance.prior_high", "support.prior_low"))
def test_prior_boundary_requires_n_plus_one_bars(feature_id: str) -> None:
    result = _compute(
        feature_id,
        (7.0, 8.0, 9.0),
        (10.0, 12.0, 11.0),
        (5.0, 3.0, 6.0),
        bars=3,
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None


@pytest.mark.parametrize(
    ("feature_id", "latest", "expected"),
    (
        ("resistance.distance_percent", 8.0, -20.0),
        ("resistance.distance_percent", 10.0, 0.0),
        ("resistance.distance_percent", 12.0, 20.0),
        ("support.distance_percent", 8.0, 60.0),
        ("support.distance_percent", 5.0, 0.0),
        ("support.distance_percent", 4.0, -20.0),
    ),
)
def test_signed_boundary_distance(
    feature_id: str, latest: float, expected: float
) -> None:
    result = _compute(
        feature_id,
        (7.0, 8.0, latest),
        (10.0, 9.0, max(latest, 8.0)),
        (5.0, 6.0, min(latest, 6.0)),
        bars=2,
    )
    assert result.value == pytest.approx(expected)


@pytest.mark.parametrize(
    ("feature_id", "boundary"),
    (("resistance.distance_atr", 12.0), ("support.distance_atr", 3.0)),
)
def test_atr_distance_reconciles_with_shared_wilder_helper(
    feature_id: str, boundary: float
) -> None:
    context = context_with_bars(
        (7.0, 8.0, 9.0, 10.0),
        highs=(10.0, 12.0, 11.0, 13.0),
        lows=(5.0, 3.0, 6.0, 8.0),
    )
    assert context.history is not None
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(
            feature_id=feature_id,
            parameters=(("atr_period", 2), ("bars", 3)),
            interval="1d",
        ),
    )
    expected = (10.0 - boundary) / wilder_atr(context.history.bars, 2)
    assert result.value == pytest.approx(expected)
    assert result.lookback_bars_used == 4


@pytest.mark.parametrize(
    "feature_id", ("resistance.distance_atr", "support.distance_atr")
)
def test_atr_distance_zero_atr_fails(feature_id: str) -> None:
    result = _compute(
        feature_id,
        (10.0, 10.0, 10.0),
        (10.0, 10.0, 10.0),
        (10.0, 10.0, 10.0),
        bars=2,
        atr_period=2,
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


@pytest.mark.parametrize(
    "feature_id",
    (
        "resistance.distance_percent",
        "support.distance_percent",
        "resistance.distance_atr",
        "support.distance_atr",
    ),
)
def test_zero_boundary_fails_distance(feature_id: str) -> None:
    atr_period = 1 if feature_id.endswith("_atr") else None
    result = _compute(
        feature_id,
        (0.0, 0.0),
        (0.0, 0.0),
        (0.0, 0.0),
        bars=1,
        atr_period=atr_period,
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None
