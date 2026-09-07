"""A2.6 registry, provenance, safety, smoke, and architecture boundaries."""

import math
import runpy
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from tiaf.contracts import DataQuality
from tiaf.features import (
    BREAKOUT_FEATURE_DEFINITIONS,
    COMPRESSION_FEATURE_DEFINITIONS,
    SUPPORT_RESISTANCE_FEATURE_DEFINITIONS,
    DeterministicFeatureEngine,
    FeatureCategory,
    FeatureRequest,
    FeatureStatus,
    builtin_feature_registry,
    summarize_feature_bundle,
)

from ..context._support import NOW
from ._support import context_with_bars, context_with_failed_history


def _request(
    feature_id: str,
    parameters: tuple[tuple[str, int], ...] = (("bars", 2),),
) -> FeatureRequest:
    return FeatureRequest(feature_id=feature_id, parameters=parameters, interval="1d")


def test_registry_contains_all_a26_definitions_in_stable_order() -> None:
    definitions = builtin_feature_registry().definitions()
    a26 = (
        *SUPPORT_RESISTANCE_FEATURE_DEFINITIONS,
        *BREAKOUT_FEATURE_DEFINITIONS,
        *COMPRESSION_FEATURE_DEFINITIONS,
    )
    assert len(a26) == 15
    assert len(definitions) == 85
    assert len({definition.feature_id for definition in definitions}) == 85
    assert tuple(definition.feature_id for definition in definitions) == tuple(
        sorted(definition.feature_id for definition in definitions)
    )
    assert {definition.feature_id for definition in a26} <= {
        definition.feature_id for definition in definitions
    }
    assert all(definition.category is FeatureCategory.STRUCTURE for definition in a26)
    assert all(
        tuple(source.value for source in definition.required_sources) == ("HISTORY",)
        for definition in a26
    )


@pytest.mark.parametrize(
    ("quality", "expected_status"),
    (
        (DataQuality.GOOD, FeatureStatus.AVAILABLE),
        (DataQuality.PARTIAL, FeatureStatus.PARTIAL),
        (DataQuality.DEGRADED, FeatureStatus.PARTIAL),
    ),
)
def test_a26_preserves_history_quality(
    quality: DataQuality, expected_status: FeatureStatus
) -> None:
    context = context_with_bars(
        (7.0, 8.0, 9.0),
        highs=(10.0, 9.0, 11.0),
        lows=(5.0, 6.0, 7.0),
        history_quality=quality,
    )
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context, _request("resistance.prior_high")
    )
    assert result.status is expected_status
    assert result.quality is quality


def test_failed_history_produces_no_level() -> None:
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context_with_failed_history(), _request("resistance.prior_high")
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None
    assert result.quality is DataQuality.UNAVAILABLE


def test_a26_uses_latest_bar_market_time_not_acquisition_time() -> None:
    latest_end = NOW - timedelta(days=1)
    context = context_with_bars(
        (7.0, 8.0, 9.0),
        highs=(10.0, 9.0, 11.0),
        lows=(5.0, 6.0, 7.0),
        history_observed_at=NOW,
        latest_bar_end_at=latest_end,
    )
    assert context.history is not None
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context, _request("resistance.prior_high")
    )
    assert result.as_of == latest_end
    assert result.source_observed_at == latest_end
    assert result.metadata["history_acquired_at"] == NOW.isoformat()


def test_a26_is_independent_of_context_clock_and_live_quote() -> None:
    first_context = context_with_bars(
        (7.0, 8.0, 9.0),
        highs=(10.0, 9.0, 11.0),
        lows=(5.0, 6.0, 7.0),
        quote_ltp=1.0,
    )
    assert first_context.quote is not None
    second_context = first_context.model_copy(
        update={
            "created_at": first_context.created_at + timedelta(hours=8),
            "quote": first_context.quote.model_copy(update={"ltp": 99_999.0}),
        }
    )
    request = _request("breakout.above_prior_high_percent")
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    first = engine.compute_one(first_context, request)
    second = engine.compute_one(second_context, request)
    assert first.value == second.value
    assert first.as_of == second.as_of
    assert first.source_evidence == second.source_evidence == ("history",)


def test_exact_prior_window_ignores_older_bars() -> None:
    first = context_with_bars(
        (100.0, 7.0, 8.0, 9.0),
        highs=(1_000.0, 10.0, 9.0, 11.0),
        lows=(1.0, 5.0, 6.0, 7.0),
    )
    second = context_with_bars(
        (6.0, 7.0, 8.0, 9.0),
        highs=(7.0, 10.0, 9.0, 11.0),
        lows=(5.0, 5.0, 6.0, 7.0),
    )
    request = _request("resistance.prior_high")
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    assert engine.compute_one(first, request).value == 10.0
    assert engine.compute_one(second, request).value == 10.0


@pytest.mark.parametrize("bad_value", (float("nan"), float("inf"), -1.0))
def test_malformed_ohlc_cannot_escape_a26_results(bad_value: float) -> None:
    context = context_with_bars(
        (7.0, 8.0, 9.0),
        highs=(10.0, 9.0, 11.0),
        lows=(5.0, 6.0, 7.0),
    )
    assert context.history is not None
    bad_bar = context.history.bars[-1].model_copy(update={"close": bad_value})
    history = context.history.model_copy(
        update={"bars": (*context.history.bars[:-1], bad_bar)}
    )
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context.model_copy(update={"history": history}),
        _request("resistance.distance_percent"),
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


def test_malformed_high_low_envelope_fails_safely() -> None:
    context = context_with_bars((7.0, 8.0, 9.0))
    assert context.history is not None
    bad_bar = context.history.bars[-1].model_copy(update={"high": 1.0})
    history = context.history.model_copy(
        update={"bars": (*context.history.bars[:-1], bad_bar)}
    )
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context.model_copy(update={"history": history}),
        _request("breakout.high_above_prior_high_percent"),
    )
    assert result.status is FeatureStatus.FAILED


@pytest.mark.parametrize("mutation", ("duplicate", "reversed"))
def test_duplicate_and_out_of_order_history_fail_safely(mutation: str) -> None:
    context = context_with_bars((7.0, 8.0, 9.0))
    assert context.history is not None
    bars = context.history.bars
    mutated = (bars[0], bars[0], bars[2]) if mutation == "duplicate" else tuple(reversed(bars))
    history = context.history.model_copy(update={"bars": mutated})
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context.model_copy(update={"history": history}),
        _request("support.prior_low"),
    )
    assert result.status is FeatureStatus.FAILED


def test_available_a26_values_are_finite() -> None:
    context = context_with_bars(
        (7.0, 8.0, 9.0), highs=(10.0, 9.0, 11.0), lows=(5.0, 6.0, 7.0)
    )
    requests = (
        _request("resistance.prior_high"),
        _request("resistance.distance_percent"),
        _request("breakout.above_prior_high_percent"),
        _request("structure.position_vs_prior_range"),
    )
    results = DeterministicFeatureEngine(builtin_feature_registry()).compute(
        context, requests
    ).results
    assert all(isinstance(result.value, (int, float)) for result in results)
    assert all(
        math.isfinite(result.value)
        for result in results
        if isinstance(result.value, (int, float))
    )


def test_a26_summary_is_factual_without_recommendation_language() -> None:
    context = context_with_bars(
        (7.0, 8.0, 12.0), highs=(10.0, 9.0, 13.0), lows=(5.0, 6.0, 7.0)
    )
    bundle = DeterministicFeatureEngine(builtin_feature_registry()).compute(
        context,
        (
            _request("resistance.distance_percent"),
            _request("breakout.above_prior_high_percent"),
        ),
    )
    summary = summarize_feature_bundle(bundle).casefold()
    forbidden = (
        "recommend",
        "buy",
        "sell",
        "enter",
        "confirmed breakout",
        "false breakout",
        "high-probability",
        "target",
        "stop-loss",
    )
    assert all(term not in summary for term in forbidden)


def test_a26_modules_have_only_deterministic_feature_dependencies() -> None:
    source = "\n".join(
        Path(path).read_text(encoding="utf-8")
        for path in (
            "src/tiaf/features/_structure_calculation.py",
            "src/tiaf/features/support_resistance.py",
            "src/tiaf/features/breakout.py",
            "src/tiaf/features/compression.py",
        )
    ).casefold()
    forbidden = (
        "tiaf.data.providers",
        "dhan",
        "httpx",
        "requests.",
        "instrumentresolver",
        "datafetchcoordinator",
        "providerscheduler",
        "datetime.now",
        "time.sleep",
        "featureengine",
        "indicatorengine",
        "option_chain",
        "langgraph",
        "openai",
        "broker",
        "volume.relative",
        "confirmed breakout",
        "smart money",
    )
    assert all(token not in source for token in forbidden)


def test_no_hindsight_pivot_or_subjective_persistence_feature_registered() -> None:
    ids = {definition.feature_id for definition in builtin_feature_registry().definitions()}
    forbidden_parts = ("pivot", "fractal", "touch", "confirmed", "false", "quality")
    assert all(part not in feature_id for feature_id in ids for part in forbidden_parts)


def test_levels_smoke_request_inventory_is_deterministic() -> None:
    namespace: dict[str, Any] = runpy.run_path(
        "scripts/feature_engine_smoke.py", run_name="feature_smoke"
    )
    requests = namespace["_levels_requests"]("1d")
    assert len(requests) == 17
    assert requests == namespace["_levels_requests"]("1d")
    assert {request.feature_id for request in requests} == {
        definition.feature_id
        for definition in (
            *SUPPORT_RESISTANCE_FEATURE_DEFINITIONS,
            *BREAKOUT_FEATURE_DEFINITIONS,
            *COMPRESSION_FEATURE_DEFINITIONS,
        )
    }


def test_accepted_a21_through_a25_values_remain_unchanged() -> None:
    context = context_with_bars(
        (100.0, 110.0, 121.0), volumes=(100, 200, 400), quote_ltp=122.0
    )
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    old_return = engine.compute_one(context, _request("return.percent", (("bars", 1),)))
    old_relative_volume = engine.compute_one(
        context, _request("volume.relative", (("bars", 2),))
    )
    assert old_return.value == pytest.approx(10.0)
    assert old_relative_volume.value == pytest.approx(400 / 150)
