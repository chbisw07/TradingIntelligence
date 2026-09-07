"""A2.5 exact-window raw and relative volume behavior."""

import math

import pytest

from tiaf.contracts import DataQuality
from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureParameterError,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    builtin_feature_registry,
)
from tiaf.features._trend_calculation import linear_regression

from ._support import context_with_bars


def _result(
    feature_id: str,
    volumes: tuple[int | None, ...],
    *,
    bars: int | None = None,
    closes: tuple[float, ...] | None = None,
    history_quality: DataQuality = DataQuality.GOOD,
) -> FeatureResult:
    context = context_with_bars(
        closes or tuple(100.0 + index for index in range(len(volumes))),
        volumes=volumes,
        history_quality=history_quality,
    )
    parameters = () if bars is None else (("bars", bars),)
    return DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(
            feature_id=feature_id,
            parameters=parameters,
            interval="1d",
        ),
    )


@pytest.mark.parametrize("volume", (0, 1, 12_345))
def test_current_volume_preserves_nonnegative_integer(volume: int) -> None:
    result = _result("volume.current", (7, volume))
    assert result.status is FeatureStatus.AVAILABLE
    assert result.quality is DataQuality.GOOD
    assert result.value == volume
    assert isinstance(result.value, int)
    assert result.lookback_bars_used == 1


@pytest.mark.parametrize(
    ("feature_id", "expected"),
    (("volume.average", 20.0), ("volume.median", 20.0)),
)
def test_average_and_median_use_latest_exact_window(
    feature_id: str, expected: float
) -> None:
    result = _result(feature_id, (999, 10, 20, 30), bars=3)
    assert result.value == pytest.approx(expected)
    assert result.lookback_bars_used == 3


def test_even_window_median_is_deterministic() -> None:
    assert _result("volume.median", (10, 20, 30, 100), bars=4).value == 25.0


@pytest.mark.parametrize("feature_id", ("volume.average", "volume.median"))
def test_window_statistic_reports_insufficient_bars(feature_id: str) -> None:
    result = _result(feature_id, (10, 20), bars=3)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None


def test_relative_volume_excludes_latest_from_prior_baseline() -> None:
    result = _result("volume.relative", (9_999, 100, 100, 200), bars=2)
    assert result.value == pytest.approx(2.0)
    assert result.lookback_bars_used == 3


def test_relative_volume_requires_n_plus_one_bars() -> None:
    result = _result("volume.relative", (100, 200), bars=2)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


def test_relative_volume_zero_baseline_is_failed() -> None:
    result = _result("volume.relative", (0, 0, 10), bars=2)
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


@pytest.mark.parametrize(
    ("volumes", "expected"), (((100, 200), 100.0), ((200, 100), -50.0))
)
def test_one_bar_volume_change(
    volumes: tuple[int, int], expected: float
) -> None:
    assert _result("volume.change_percent", volumes).value == pytest.approx(expected)


def test_one_bar_volume_change_rejects_zero_denominator() -> None:
    result = _result("volume.change_percent", (0, 100))
    assert result.status is FeatureStatus.FAILED


@pytest.mark.parametrize(
    ("volumes", "expected"),
    (((10, 20, 30), 100.0), ((30, 20, 10), 0.0), ((10, 30, 20), 50.0)),
)
def test_position_in_volume_range(
    volumes: tuple[int, ...], expected: float
) -> None:
    assert _result("volume.position_in_range", volumes, bars=3).value == expected


def test_position_in_flat_volume_range_is_insufficient() -> None:
    result = _result("volume.position_in_range", (10, 10, 10), bars=3)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


def test_volume_coefficient_of_variation_uses_population_stddev() -> None:
    result = _result("volume.coefficient_of_variation_percent", (100, 200, 300), bars=3)
    expected = math.sqrt(20_000 / 3) / 200 * 100
    assert result.value == pytest.approx(expected)


def test_volume_coefficient_of_variation_rejects_zero_mean() -> None:
    result = _result("volume.coefficient_of_variation_percent", (0, 0), bars=2)
    assert result.status is FeatureStatus.FAILED


@pytest.mark.parametrize(
    ("feature_id", "expected"),
    (("volume.linear_slope", 100.0), ("volume.linear_slope_percent", 50.0)),
)
def test_volume_regression_uses_a23_ols(
    feature_id: str, expected: float
) -> None:
    result = _result(feature_id, (100, 200, 300), bars=3)
    assert result.value == pytest.approx(expected)
    assert linear_regression((100.0, 200.0, 300.0)).slope == 100.0


@pytest.mark.parametrize(
    ("volumes", "expected"), (((300, 200, 100), -100.0), ((100, 100, 100), 0.0))
)
def test_volume_slope_handles_negative_and_flat_paths(
    volumes: tuple[int, ...], expected: float
) -> None:
    assert _result("volume.linear_slope", volumes, bars=3).value == expected


def test_volume_slope_does_not_shorten_requested_window() -> None:
    result = _result("volume.linear_slope", (100, 200), bars=3)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


@pytest.mark.parametrize("feature_id", ("volume.linear_slope", "volume.linear_slope_percent"))
def test_volume_regression_requires_two_requested_bars(feature_id: str) -> None:
    with pytest.raises(FeatureParameterError, match="at least 2"):
        _result(feature_id, (100,), bars=1)


def test_normalized_volume_slope_rejects_zero_mean() -> None:
    result = _result("volume.linear_slope_percent", (0, 0), bars=2)
    assert result.status is FeatureStatus.FAILED


@pytest.mark.parametrize(
    ("feature_id", "volumes", "expected", "lookback"),
    (
        ("volume.consecutive_increases", (10, 20, 30), 2, 3),
        ("volume.consecutive_increases", (10, 20, 20), 0, 2),
        ("volume.consecutive_decreases", (30, 20, 10), 2, 3),
        ("volume.consecutive_decreases", (30, 20, 20), 0, 2),
        ("volume.consecutive_increases", (10,), 0, 1),
    ),
)
def test_consecutive_volume_runs(
    feature_id: str,
    volumes: tuple[int, ...],
    expected: int,
    lookback: int,
) -> None:
    result = _result(feature_id, volumes)
    assert result.value == expected
    assert result.lookback_bars_used == lookback


@pytest.mark.parametrize(
    "feature_id",
    (
        "volume.current",
        "volume.average",
        "volume.relative",
        "volume.change_percent",
        "volume.consecutive_increases",
    ),
)
def test_missing_required_volume_is_insufficient(feature_id: str) -> None:
    volumes: tuple[int | None, ...] = (10, 20, None)
    bars = 2 if feature_id in {"volume.average", "volume.relative"} else None
    result = _result(feature_id, volumes, bars=bars)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None


def test_defensive_negative_volume_is_failed() -> None:
    context = context_with_bars((100.0,), volumes=(10,))
    assert context.history is not None
    bad_bar = context.history.bars[0].model_copy(update={"volume": -1})
    bad_history = context.history.model_copy(update={"bars": (bad_bar,)})
    context = context.model_copy(update={"history": bad_history})
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(feature_id="volume.current", interval="1d"),
    )
    assert result.status is FeatureStatus.FAILED


def test_volume_feature_preserves_degraded_source_quality_and_market_time() -> None:
    context = context_with_bars(
        (100.0, 101.0), volumes=(10, 20), history_quality=DataQuality.DEGRADED
    )
    assert context.history is not None
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(feature_id="volume.current", interval="1d"),
    )
    assert result.status is FeatureStatus.PARTIAL
    assert result.quality is DataQuality.DEGRADED
    assert result.as_of == context.history.bars[-1].end_at
    assert result.source_observed_at == context.history.bars[-1].end_at
    assert result.metadata["history_acquired_at"] == context.history.observed_at.isoformat()
