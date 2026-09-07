"""A2.5 destination-volume participation and correlation behavior."""

import pytest

from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureParameterError,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    builtin_feature_registry,
)

from ._support import context_with_bars


def _result(
    feature_id: str,
    closes: tuple[float, ...],
    volumes: tuple[int | None, ...],
    *,
    bars: int,
    highs: tuple[float, ...] | None = None,
    lows: tuple[float, ...] | None = None,
) -> FeatureResult:
    context = context_with_bars(
        closes, volumes=volumes, highs=highs, lows=lows
    )
    return DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(
            feature_id=feature_id,
            parameters=(("bars", bars),),
            interval="1d",
        ),
    )


@pytest.mark.parametrize(
    ("feature_id", "expected"),
    (
        ("participation.up_volume_fraction", 1 / 6),
        ("participation.down_volume_fraction", 2 / 6),
        ("participation.flat_volume_fraction", 3 / 6),
    ),
)
def test_participation_fractions_use_destination_volume(
    feature_id: str, expected: float
) -> None:
    result = _result(feature_id, (10, 11, 10, 10), (999_999, 100, 200, 300), bars=3)
    assert result.value == pytest.approx(expected)
    assert result.lookback_bars_used == 4


def test_participation_fractions_sum_to_one() -> None:
    values = tuple(
        _result(feature_id, (10, 11, 10, 10), (0, 100, 200, 300), bars=3).value
        for feature_id in (
            "participation.up_volume_fraction",
            "participation.down_volume_fraction",
            "participation.flat_volume_fraction",
        )
    )
    assert all(isinstance(value, (int, float)) for value in values)
    numeric = tuple(value for value in values if isinstance(value, (int, float)))
    assert sum(numeric) == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("feature_id", "closes"),
    (
        ("participation.up_volume_fraction", (10.0, 11.0, 12.0)),
        ("participation.down_volume_fraction", (12.0, 11.0, 10.0)),
    ),
)
def test_all_one_direction_volume_fraction_is_one(
    feature_id: str, closes: tuple[float, ...]
) -> None:
    assert _result(feature_id, closes, (0, 100, 200), bars=2).value == 1.0


def test_first_bar_volume_is_not_assigned_to_a_transition() -> None:
    small = _result("participation.up_volume_fraction", (10, 11), (0, 20), bars=1)
    huge = _result("participation.up_volume_fraction", (10, 11), (999_999, 20), bars=1)
    assert small.value == huge.value == 1.0


def test_transition_feature_requires_n_plus_one_bars() -> None:
    result = _result("participation.up_volume_fraction", (10, 11), (10, 20), bars=2)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


@pytest.mark.parametrize(
    "feature_id",
    (
        "participation.up_volume_fraction",
        "participation.down_volume_fraction",
        "participation.flat_volume_fraction",
        "participation.signed_volume_balance",
    ),
)
def test_zero_destination_volume_is_failed(feature_id: str) -> None:
    result = _result(feature_id, (10, 11, 10), (999, 0, 0), bars=2)
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


@pytest.mark.parametrize(
    ("closes", "volumes", "expected"),
    (
        ((10, 11, 12), (0, 100, 200), 1.0),
        ((12, 11, 10), (0, 100, 200), -1.0),
        ((10, 11, 10, 10), (0, 100, 200, 300), -1 / 6),
        ((10, 10, 10), (0, 100, 200), 0.0),
    ),
)
def test_signed_volume_balance(
    closes: tuple[float, ...], volumes: tuple[int, ...], expected: float
) -> None:
    result = _result(
        "participation.signed_volume_balance",
        closes,
        volumes,
        bars=len(closes) - 1,
    )
    assert result.value == pytest.approx(expected)


@pytest.mark.parametrize(
    ("volumes", "expected"),
    (((0, 100, 200, 300), 1.0), ((0, 300, 200, 100), -1.0)),
)
def test_absolute_return_volume_alignment(
    volumes: tuple[int, ...], expected: float
) -> None:
    result = _result(
        "participation.return_volume_alignment",
        (100.0, 110.0, 132.0, 171.6),
        volumes,
        bars=3,
    )
    assert result.value == pytest.approx(expected)


def test_return_alignment_uses_exact_latest_transition_window() -> None:
    result = _result(
        "participation.return_volume_alignment",
        (1_000.0, 100.0, 110.0, 132.0, 171.6),
        (9_999, 0, 100, 200, 300),
        bars=3,
    )
    assert result.value == pytest.approx(1.0)
    assert result.lookback_bars_used == 4


def test_return_alignment_rejects_zero_base_close() -> None:
    result = _result(
        "participation.return_volume_alignment",
        (0.0, 10.0, 20.0),
        (0, 100, 200),
        bars=2,
    )
    assert result.status is FeatureStatus.FAILED


def test_return_alignment_requires_n_plus_one_bars() -> None:
    result = _result(
        "participation.return_volume_alignment",
        (100.0, 110.0),
        (100, 200),
        bars=2,
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


@pytest.mark.parametrize(
    ("closes", "volumes"),
    (
        ((100.0, 110.0, 121.0), (0, 100, 200)),
        ((100.0, 110.0, 132.0), (0, 100, 100)),
    ),
)
def test_return_alignment_zero_variance_is_not_applicable(
    closes: tuple[float, ...], volumes: tuple[int, ...]
) -> None:
    result = _result(
        "participation.return_volume_alignment", closes, volumes, bars=2
    )
    assert result.status is FeatureStatus.NOT_APPLICABLE
    assert result.value is None


@pytest.mark.parametrize(
    ("volumes", "expected"),
    (((100, 200, 300), 1.0), ((300, 200, 100), -1.0)),
)
def test_range_volume_alignment(
    volumes: tuple[int, ...], expected: float
) -> None:
    result = _result(
        "participation.range_volume_alignment",
        (100.0, 100.0, 100.0),
        volumes,
        bars=3,
        highs=(101.0, 102.0, 103.0),
        lows=(99.0, 98.0, 97.0),
    )
    assert result.value == pytest.approx(expected)


def test_range_alignment_zero_variance_is_not_applicable() -> None:
    result = _result(
        "participation.range_volume_alignment",
        (100.0, 100.0, 100.0),
        (100, 200, 300),
        bars=3,
        highs=(101.0, 101.0, 101.0),
        lows=(99.0, 99.0, 99.0),
    )
    assert result.status is FeatureStatus.NOT_APPLICABLE


@pytest.mark.parametrize(
    "feature_id",
    ("participation.return_volume_alignment", "participation.range_volume_alignment"),
)
def test_correlation_requires_at_least_two_observations(feature_id: str) -> None:
    closes = (100.0, 101.0) if "return" in feature_id else (100.0,)
    volumes = tuple(100 for _ in closes)
    with pytest.raises(FeatureParameterError, match="at least 2"):
        _result(feature_id, closes, volumes, bars=1)


@pytest.mark.parametrize(
    "feature_id",
    (
        "participation.up_volume_fraction",
        "participation.signed_volume_balance",
        "participation.return_volume_alignment",
        "participation.range_volume_alignment",
    ),
)
def test_missing_aligned_volume_is_insufficient(feature_id: str) -> None:
    closes = (100.0, 110.0, 132.0)
    result = _result(feature_id, closes, (0, None, 200), bars=2)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
