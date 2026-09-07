"""A2.5 registry, provenance, safety, and subsystem boundaries."""

import math
import runpy
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from tiaf.contracts import DataQuality
from tiaf.features import (
    PARTICIPATION_FEATURE_DEFINITIONS,
    VOLUME_FEATURE_DEFINITIONS,
    DeterministicFeatureEngine,
    FeatureCategory,
    FeatureRequest,
    FeatureStatus,
    builtin_feature_registry,
    summarize_feature_bundle,
)

from ._support import context_with_bars, context_with_failed_history


def _request(feature_id: str, *, bars: int | None = None) -> FeatureRequest:
    return FeatureRequest(
        feature_id=feature_id,
        parameters=() if bars is None else (("bars", bars),),
        interval="1d",
    )


def test_registry_contains_all_a25_definitions_in_stable_order() -> None:
    definitions = builtin_feature_registry().definitions()
    a25 = (*VOLUME_FEATURE_DEFINITIONS, *PARTICIPATION_FEATURE_DEFINITIONS)
    assert len(a25) == 17
    assert len(definitions) == 124
    assert len({item.feature_id for item in definitions}) == 124
    assert tuple(item.feature_id for item in definitions) == tuple(
        sorted(item.feature_id for item in definitions)
    )
    assert {item.feature_id for item in a25} <= {
        item.feature_id for item in definitions
    }
    assert all(item.category is FeatureCategory.VOLUME for item in a25)
    assert all(
        tuple(source.value for source in item.required_sources) == ("HISTORY",)
        for item in a25
    )


@pytest.mark.parametrize(
    "quality", (DataQuality.PARTIAL, DataQuality.DEGRADED)
)
def test_a25_never_upgrades_history_quality(quality: DataQuality) -> None:
    context = context_with_bars(
        (100.0, 101.0, 102.0), volumes=(100, 200, 300), history_quality=quality
    )
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context, _request("volume.average", bars=3)
    )
    assert result.status is FeatureStatus.PARTIAL
    assert result.quality is quality


def test_failed_history_is_not_treated_as_volume_evidence() -> None:
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context_with_failed_history(), _request("volume.current")
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.quality is DataQuality.UNAVAILABLE


def test_a25_is_independent_of_context_clock_and_quote() -> None:
    first_context = context_with_bars(
        (100.0, 110.0, 132.0), volumes=(100, 200, 300), quote_ltp=1.0
    )
    second_context = first_context.model_copy(
        update={
            "created_at": first_context.created_at + timedelta(hours=4),
            "quote": first_context.quote.model_copy(update={"ltp": 99_999.0})
            if first_context.quote is not None
            else None,
        }
    )
    request = _request("participation.return_volume_alignment", bars=2)
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    first = engine.compute_one(first_context, request)
    second = engine.compute_one(second_context, request)
    assert first.value == second.value
    assert first.as_of == second.as_of


@pytest.mark.parametrize("bad_value", (float("nan"), float("inf"), -1.0))
def test_malformed_volume_cannot_escape_as_a_value(bad_value: float) -> None:
    context = context_with_bars((100.0,), volumes=(10,))
    assert context.history is not None
    bad_bar = context.history.bars[0].model_copy(update={"volume": bad_value})
    history = context.history.model_copy(update={"bars": (bad_bar,)})
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context.model_copy(update={"history": history}), _request("volume.current")
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


def test_malformed_range_fails_safely() -> None:
    context = context_with_bars((100.0, 100.0), volumes=(100, 200))
    assert context.history is not None
    bad_bar = context.history.bars[-1].model_copy(update={"high": 1.0})
    history = context.history.model_copy(
        update={"bars": (context.history.bars[0], bad_bar)}
    )
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context.model_copy(update={"history": history}),
        _request("participation.range_volume_alignment", bars=2),
    )
    assert result.status is FeatureStatus.FAILED


@pytest.mark.parametrize("mutation", ("duplicate", "reversed"))
def test_duplicate_and_out_of_order_history_fail_safely(mutation: str) -> None:
    context = context_with_bars(
        (100.0, 101.0, 102.0), volumes=(100, 200, 300)
    )
    assert context.history is not None
    bars = context.history.bars
    mutated = (bars[0], bars[0], bars[2]) if mutation == "duplicate" else tuple(reversed(bars))
    history = context.history.model_copy(update={"bars": mutated})
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context.model_copy(update={"history": history}),
        _request("volume.average", bars=3),
    )
    assert result.status is FeatureStatus.FAILED


def test_a25_available_numbers_are_finite() -> None:
    context = context_with_bars(
        (100.0, 110.0, 132.0, 171.6), volumes=(50, 100, 200, 300)
    )
    requests = (
        _request("volume.relative", bars=3),
        _request("volume.linear_slope_percent", bars=3),
        _request("participation.signed_volume_balance", bars=3),
        _request("participation.return_volume_alignment", bars=3),
    )
    results = DeterministicFeatureEngine(builtin_feature_registry()).compute(
        context, requests
    ).results
    assert all(result.value is not None for result in results)
    assert all(isinstance(result.value, (int, float)) for result in results)
    assert all(
        math.isfinite(result.value)
        for result in results
        if isinstance(result.value, (int, float))
    )


def test_a25_summary_is_factual_and_has_no_interpretive_vocabulary() -> None:
    context = context_with_bars(
        (100.0, 110.0, 132.0), volumes=(100, 200, 300)
    )
    bundle = DeterministicFeatureEngine(builtin_feature_registry()).compute(
        context,
        (
            _request("volume.relative", bars=2),
            _request("participation.up_volume_fraction", bars=2),
        ),
    )
    summary = summarize_feature_bundle(bundle).casefold()
    forbidden = (
        "recommend",
        "buy",
        "sell",
        "bullish",
        "bearish",
        "smart money",
        "institutional activity",
        "breakout confirmed",
    )
    assert all(word not in summary for word in forbidden)


def test_a25_modules_have_only_deterministic_feature_dependencies() -> None:
    source = "\n".join(
        Path(path).read_text(encoding="utf-8")
        for path in (
            "src/tiaf/features/_volume_calculation.py",
            "src/tiaf/features/volume.py",
            "src/tiaf/features/participation.py",
        )
    ).casefold()
    forbidden = (
        "tiaf.data.providers",
        "dhan",
        "httpx",
        "requests.",
        "get_quote(",
        "instrumentresolver",
        "datafetchcoordinator",
        "providerscheduler",
        "datetime.now",
        "time.sleep",
        "option_chain",
        "historical_options",
        "indicatorengine",
        "langgraph",
        "openai",
        "agent",
        "broker",
        "trade",
    )
    assert all(token not in source for token in forbidden)


def test_volume_smoke_request_inventory_is_deterministic() -> None:
    namespace: dict[str, Any] = runpy.run_path(
        "scripts/feature_engine_smoke.py", run_name="feature_smoke"
    )
    requests = namespace["_volume_requests"]("1d")
    assert len(requests) == 18
    assert requests == namespace["_volume_requests"]("1d")
    assert requests[0] == _request("volume.current")
    assert {request.feature_id for request in requests} == {
        definition.feature_id
        for definition in (*VOLUME_FEATURE_DEFINITIONS, *PARTICIPATION_FEATURE_DEFINITIONS)
    }


def test_accepted_a21_through_a24_values_remain_available() -> None:
    context = context_with_bars(
        tuple(float(value) for value in range(100, 161)),
        volumes=tuple(range(100, 161)),
        quote_ltp=161.0,
    )
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    requests = (
        _request("return.percent", bars=1),
        FeatureRequest(
            feature_id="volatility.atr", parameters=(("period", 14),), interval="1d"
        ),
        FeatureRequest(
            feature_id="trend.sma", parameters=(("period", 20),), interval="1d"
        ),
    )
    results = engine.compute(context, requests).results
    assert results[0].value == pytest.approx(100 / 159)
    assert all(result.status is FeatureStatus.AVAILABLE for result in results)
