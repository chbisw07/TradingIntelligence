"""A2.3 registry, provenance, safety, smoke, and architecture boundaries."""

import runpy
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from tiaf.contracts import DataQuality
from tiaf.features import (
    STRUCTURE_FEATURE_DEFINITIONS,
    TREND_FEATURE_DEFINITIONS,
    DeterministicFeatureEngine,
    FeatureRequest,
    FeatureStatus,
    builtin_feature_registry,
    summarize_feature_bundle,
)

from ..context._support import NOW
from ._support import context_with_bars


def _request(
    feature_id: str,
    parameters: tuple[tuple[str, int], ...] = (),
) -> FeatureRequest:
    return FeatureRequest(
        feature_id=feature_id,
        parameters=parameters,
        interval="1d",
    )


def test_registry_contains_all_a23_definitions_in_stable_order() -> None:
    registry = builtin_feature_registry()
    definitions = registry.definitions()
    a23 = (*TREND_FEATURE_DEFINITIONS, *STRUCTURE_FEATURE_DEFINITIONS)
    assert len(a23) == 23
    assert len(definitions) == 70
    assert tuple(item.feature_id for item in definitions) == tuple(
        sorted(item.feature_id for item in definitions)
    )
    assert {item.feature_id for item in a23} <= {
        item.feature_id for item in definitions
    }
    assert all(
        tuple(source.value for source in item.required_sources) == ("HISTORY",)
        for item in a23
    )


def test_history_quality_and_latest_market_bar_time_are_preserved() -> None:
    bar_end = NOW - timedelta(days=1)
    context = context_with_bars(
        (10.0, 20.0, 30.0),
        history_quality=DataQuality.DEGRADED,
        history_observed_at=NOW,
        latest_bar_end_at=bar_end,
    )
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        _request("trend.linear_slope", (("bars", 3),)),
    )
    assert result.status is FeatureStatus.PARTIAL
    assert result.quality is DataQuality.DEGRADED
    assert result.as_of == bar_end
    assert result.source_observed_at == bar_end
    assert result.source_evidence == ("history",)
    assert result.metadata["history_acquired_at"] == NOW.isoformat()
    assert result.metadata["source_time_semantics"] == "latest_history_bar_end"


def test_a23_calculation_is_independent_of_context_creation_time() -> None:
    first_context = context_with_bars((10.0, 20.0, 30.0))
    second_context = first_context.model_copy(
        update={"created_at": first_context.created_at + timedelta(hours=4)}
    )
    request = _request("trend.sma", (("period", 2),))
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    first = engine.compute_one(first_context, request)
    second = engine.compute_one(second_context, request)
    assert first.value == second.value
    assert first.as_of == second.as_of


@pytest.mark.parametrize("bad_value", [float("nan"), float("inf")])
def test_nonfinite_history_cannot_escape_a23_results(bad_value: float) -> None:
    context = context_with_bars((10.0, 20.0, 30.0))
    assert context.history is not None
    bad_bar = context.history.bars[-1].model_copy(update={"close": bad_value})
    history = context.history.model_copy(
        update={"bars": (*context.history.bars[:-1], bad_bar)}
    )
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context.model_copy(update={"history": history}),
        _request("trend.sma", (("period", 2),)),
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


def test_malformed_and_out_of_order_history_fail_safely() -> None:
    context = context_with_bars((10.0, 20.0, 30.0))
    assert context.history is not None
    malformed = context.history.bars[-1].model_copy(update={"high": 1.0})
    malformed_history = context.history.model_copy(
        update={"bars": (*context.history.bars[:-1], malformed)}
    )
    reversed_history = context.history.model_copy(
        update={"bars": tuple(reversed(context.history.bars))}
    )
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    malformed_result = engine.compute_one(
        context.model_copy(update={"history": malformed_history}),
        _request("structure.position_in_rolling_range", (("bars", 2),)),
    )
    reversed_result = engine.compute_one(
        context.model_copy(update={"history": reversed_history}),
        _request("trend.directional_efficiency", (("bars", 2),)),
    )
    assert malformed_result.status is FeatureStatus.FAILED
    assert reversed_result.status is FeatureStatus.FAILED


def test_trend_smoke_request_inventory_is_deterministic() -> None:
    namespace: dict[str, Any] = runpy.run_path(
        "scripts/feature_engine_smoke.py", run_name="feature_smoke"
    )
    requests = namespace["_trend_requests"]("1d")
    assert len(requests) == 27
    assert requests == namespace["_trend_requests"]("1d")
    assert requests[0] == _request("trend.sma", (("period", 10),))
    assert any(
        request.feature_id == "structure.position_in_rolling_range"
        for request in requests
    )
    assert any(request.feature_id == "trend.distance_from_ema_atr" for request in requests)


def test_a23_summary_contains_measurements_without_recommendation_language() -> None:
    context = context_with_bars(tuple(float(value) for value in range(1, 22)))
    requests = (
        _request("trend.linear_slope_percent", (("bars", 20),)),
        _request("trend.directional_efficiency", (("bars", 20),)),
        _request("structure.higher_high_fraction", (("bars", 20),)),
    )
    bundle = DeterministicFeatureEngine(builtin_feature_registry()).compute(
        context, requests
    )
    summary = summarize_feature_bundle(bundle).casefold()
    forbidden = (
        "bullish",
        "bearish",
        "buy",
        "sell",
        "wait",
        "good trend",
        "opportunity score",
        "recommendation",
        "target",
        "stop loss",
    )
    assert all(term not in summary for term in forbidden)


def test_a23_results_contain_no_provider_payload_metadata() -> None:
    context = context_with_bars((10.0, 20.0, 30.0))
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        _request("trend.sma", (("period", 2),)),
    )
    assert all("dhan" not in key.casefold() for key in result.metadata)


def test_feature_layer_has_no_external_or_interpretive_dependencies() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(Path("src/tiaf/features").glob("*.py"))
    ).casefold()
    forbidden = (
        "tiaf.data.providers",
        "httpx",
        "requests.",
        "get_quote(",
        "get_historical(",
        "instrumentresolver",
        "datafetchcoordinator",
        "providerscheduler",
        "datetime.now",
        "time.sleep",
        "langgraph",
        "openai",
        "broker",
        "strong_bullish",
        "weak_bearish",
        "buy signal",
        "sell signal",
    )
    assert all(token not in source for token in forbidden)


def test_accepted_a21_and_a22_values_remain_unchanged() -> None:
    context = context_with_bars((100.0, 110.0), quote_ltp=112.0)
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    old_return = engine.compute_one(
        context, _request("return.percent", (("bars", 1),))
    )
    a22_log_return = engine.compute_one(
        context, _request("return.log", (("bars", 1),))
    )
    assert old_return.value == pytest.approx(10.0)
    assert a22_log_return.value == pytest.approx(0.09531017980432477)
