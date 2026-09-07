"""A2.3 directional efficiency, transition fractions, and run behavior."""

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
    closes: tuple[float, ...],
    *,
    bars: int | None = None,
) -> FeatureResult:
    parameters = () if bars is None else (("bars", bars),)
    return DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context_with_bars(closes),
        FeatureRequest(
            feature_id=feature_id,
            parameters=parameters,
            interval="1d",
        ),
    )


def test_perfectly_increasing_path_has_unit_efficiency() -> None:
    unsigned = _compute("trend.directional_efficiency", (1.0, 2.0, 3.0, 4.0), bars=3)
    signed = _compute("trend.signed_efficiency", (1.0, 2.0, 3.0, 4.0), bars=3)
    assert unsigned.value == 1.0
    assert signed.value == 1.0
    assert unsigned.lookback_bars_used == 4


def test_perfectly_decreasing_path_has_negative_signed_efficiency() -> None:
    unsigned = _compute("trend.directional_efficiency", (4.0, 3.0, 2.0, 1.0), bars=3)
    signed = _compute("trend.signed_efficiency", (4.0, 3.0, 2.0, 1.0), bars=3)
    assert unsigned.value == 1.0
    assert signed.value == -1.0


def test_oscillating_path_has_lower_efficiency() -> None:
    unsigned = _compute("trend.directional_efficiency", (1.0, 2.0, 1.0, 2.0), bars=3)
    signed = _compute("trend.signed_efficiency", (1.0, 2.0, 1.0, 2.0), bars=3)
    assert unsigned.value == pytest.approx(1.0 / 3.0)
    assert signed.value == pytest.approx(1.0 / 3.0)


@pytest.mark.parametrize(
    "feature_id", ["trend.directional_efficiency", "trend.signed_efficiency"]
)
def test_flat_path_has_deterministic_zero_efficiency(feature_id: str) -> None:
    result = _compute(feature_id, (2.0, 2.0, 2.0, 2.0), bars=3)
    assert result.value == 0.0


@pytest.mark.parametrize(
    "feature_id", ["trend.directional_efficiency", "trend.signed_efficiency"]
)
def test_efficiency_requires_n_plus_one_observations(feature_id: str) -> None:
    result = _compute(feature_id, (1.0, 2.0, 3.0), bars=3)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None


def test_up_down_flat_fractions_form_exact_distribution() -> None:
    closes = (1.0, 2.0, 2.0, 1.0)
    up = _compute("trend.up_close_fraction", closes, bars=3)
    down = _compute("trend.down_close_fraction", closes, bars=3)
    flat = _compute("trend.flat_close_fraction", closes, bars=3)
    assert up.value == pytest.approx(1.0 / 3.0)
    assert down.value == pytest.approx(1.0 / 3.0)
    assert flat.value == pytest.approx(1.0 / 3.0)
    assert isinstance(up.value, (int, float))
    assert isinstance(down.value, (int, float))
    assert isinstance(flat.value, (int, float))
    assert up.value + down.value + flat.value == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("feature_id", "closes", "expected"),
    [
        ("trend.up_close_fraction", (1.0, 2.0, 3.0), 1.0),
        ("trend.down_close_fraction", (3.0, 2.0, 1.0), 1.0),
        ("trend.flat_close_fraction", (2.0, 2.0, 2.0), 1.0),
        ("trend.up_close_fraction", (3.0, 2.0, 1.0), 0.0),
        ("trend.down_close_fraction", (1.0, 2.0, 3.0), 0.0),
    ],
)
def test_close_fraction_known_paths(
    feature_id: str, closes: tuple[float, ...], expected: float
) -> None:
    assert _compute(feature_id, closes, bars=2).value == expected


@pytest.mark.parametrize(
    "feature_id",
    [
        "trend.up_close_fraction",
        "trend.down_close_fraction",
        "trend.flat_close_fraction",
    ],
)
def test_close_fractions_do_not_shorten_transition_window(feature_id: str) -> None:
    result = _compute(feature_id, (1.0, 2.0), bars=2)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


def test_close_fraction_uses_only_latest_requested_transitions() -> None:
    result = _compute("trend.up_close_fraction", (100.0, 1.0, 2.0, 3.0), bars=2)
    assert result.value == 1.0
    assert result.lookback_bars_used == 3


@pytest.mark.parametrize(
    ("feature_id", "closes", "expected"),
    [
        ("trend.consecutive_up_closes", (100.0, 101.0, 102.0, 103.0), 3),
        ("trend.consecutive_down_closes", (100.0, 101.0, 99.0, 98.0), 2),
        ("trend.consecutive_up_closes", (100.0, 99.0), 0),
        ("trend.consecutive_down_closes", (100.0, 101.0), 0),
        ("trend.consecutive_up_closes", (100.0, 101.0, 101.0), 0),
        ("trend.consecutive_down_closes", (100.0, 99.0, 99.0), 0),
    ],
)
def test_consecutive_latest_close_runs(
    feature_id: str, closes: tuple[float, ...], expected: int
) -> None:
    result = _compute(feature_id, closes)
    assert result.value == expected
    assert type(result.value) is int


@pytest.mark.parametrize(
    "feature_id", ["trend.consecutive_up_closes", "trend.consecutive_down_closes"]
)
def test_consecutive_run_requires_one_transition(feature_id: str) -> None:
    result = _compute(feature_id, (100.0,))
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None
