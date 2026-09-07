"""A2.2 engine compatibility, time semantics, and numerical boundaries."""

import runpy
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from tiaf.features import (
    PRICE_FEATURE_DEFINITIONS,
    RETURN_FEATURE_DEFINITIONS,
    VOLATILITY_FEATURE_DEFINITIONS,
    DeterministicFeatureEngine,
    FeatureRequest,
    FeatureStatus,
    builtin_feature_registry,
    summarize_feature_bundle,
)

from ..context._support import NOW
from ._support import context_with_bars


def _load_smoke() -> dict[str, Any]:
    return runpy.run_path("scripts/feature_engine_smoke.py", run_name="feature_smoke")


def test_registry_contains_all_new_definitions_in_deterministic_order() -> None:
    registry = builtin_feature_registry()
    definitions = registry.definitions()
    new_definitions = (
        *PRICE_FEATURE_DEFINITIONS,
        *RETURN_FEATURE_DEFINITIONS,
        *VOLATILITY_FEATURE_DEFINITIONS,
    )
    assert len(definitions) == 53
    assert tuple(item.feature_id for item in definitions) == tuple(
        sorted(item.feature_id for item in definitions)
    )
    assert {item.feature_id for item in new_definitions} <= {
        item.feature_id for item in definitions
    }


def test_a21_feature_calculations_and_acquisition_time_semantics_are_unchanged() -> None:
    context = context_with_bars(
        (100.0, 110.0),
        history_observed_at=NOW,
        latest_bar_end_at=NOW - timedelta(days=1),
    )
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    price = engine.compute_one(context, FeatureRequest(feature_id="price.current"))
    old_return = engine.compute_one(
        context,
        FeatureRequest(
            feature_id="return.percent",
            parameters=(("bars", 1),),
            interval="1d",
        ),
    )
    assert price.value == 1400.0
    assert old_return.value == pytest.approx(10.0)
    assert old_return.as_of == NOW


def test_new_history_feature_as_of_is_latest_bar_market_time() -> None:
    bar_end = NOW - timedelta(days=1)
    context = context_with_bars(
        (100.0, 110.0),
        history_observed_at=NOW,
        latest_bar_end_at=bar_end,
    )
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(
            feature_id="return.log",
            parameters=(("bars", 1),),
            interval="1d",
        ),
    )
    assert result.as_of == bar_end
    assert result.source_observed_at == bar_end
    assert result.metadata["history_acquired_at"] == NOW.isoformat()
    assert result.metadata["source_time_semantics"] == "latest_history_bar_end"


def test_quote_previous_close_feature_as_of_follows_quote_observation() -> None:
    quote_time = NOW - timedelta(days=2)
    bar_end = NOW - timedelta(days=1)
    context = context_with_bars(
        (100.0, 110.0),
        quote_ltp=115.0,
        quote_previous_close=110.0,
        quote_observed_at=quote_time,
        latest_bar_end_at=bar_end,
    )
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context,
        FeatureRequest(feature_id="price.change_absolute", interval="1d"),
    )
    assert result.as_of == quote_time
    assert result.metadata["quote_observed_at"] == quote_time.isoformat()
    assert "history_latest_bar_end_at" not in result.metadata
    assert result.metadata["source_time_semantics"] == "quote_market_observation"


def test_extended_request_order_is_deterministic() -> None:
    namespace = _load_smoke()
    requests = namespace["_extended_requests"]("1d")
    context = context_with_bars(
        tuple(float(value) for value in range(100, 121)), quote_ltp=121.0
    )
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    first = engine.compute(context, requests)
    second = engine.compute(context, requests)
    assert first == second
    assert tuple(result.request for result in first.results) == requests


def test_extended_intraday_smoke_requests_require_explicit_annualization() -> None:
    namespace = _load_smoke()
    with pytest.raises(ValueError, match="annualization-factor"):
        namespace["_extended_requests"]("1h")
    requests = namespace["_extended_requests"]("1h", 1638.0)
    realized = next(
        request for request in requests if request.feature_id == "volatility.realized"
    )
    assert realized.parameter("annualization_factor") == 1638.0


def test_one_insufficient_extended_feature_does_not_suppress_others() -> None:
    context = context_with_bars((100.0, 110.0), quote_ltp=112.0)
    bundle = DeterministicFeatureEngine(builtin_feature_registry()).compute(
        context,
        (
            FeatureRequest(feature_id="price.change_absolute", interval="1d"),
            FeatureRequest(
                feature_id="volatility.atr",
                parameters=(("period", 14),),
                interval="1d",
            ),
            FeatureRequest(feature_id="range.bar_percent", interval="1d"),
        ),
    )
    assert tuple(result.status for result in bundle.results) == (
        FeatureStatus.AVAILABLE,
        FeatureStatus.INSUFFICIENT_DATA,
        FeatureStatus.AVAILABLE,
    )
    assert not bundle.complete


def test_optional_extended_insufficiency_retains_bundle_completeness() -> None:
    context = context_with_bars((100.0, 110.0))
    bundle = DeterministicFeatureEngine(builtin_feature_registry()).compute(
        context,
        (
            FeatureRequest(feature_id="range.bar_percent", interval="1d"),
            FeatureRequest(
                feature_id="volatility.atr",
                parameters=(("period", 14),),
                interval="1d",
                required=False,
            ),
        ),
    )
    assert bundle.complete
    assert bundle.missing_required_features == ()


@pytest.mark.parametrize("bad_value", [float("nan"), float("inf")])
def test_nonfinite_ohlc_cannot_escape_as_a_feature_value(bad_value: float) -> None:
    context = context_with_bars((100.0,))
    assert context.history is not None
    bad_bar = context.history.bars[0].model_copy(update={"high": bad_value})
    bad_history = context.history.model_copy(update={"bars": (bad_bar,)})
    bad_context = context.model_copy(update={"history": bad_history})
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        bad_context,
        FeatureRequest(
            feature_id="price.rolling_high",
            parameters=(("bars", 1),),
            interval="1d",
        ),
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


def test_malformed_ohlc_and_duplicate_timestamp_are_safely_detected() -> None:
    context = context_with_bars((100.0, 110.0))
    assert context.history is not None
    malformed_bar = context.history.bars[-1].model_copy(
        update={"high": 90.0, "low": 120.0}
    )
    malformed_history = context.history.model_copy(
        update={"bars": (context.history.bars[0], malformed_bar)}
    )
    malformed_context = context.model_copy(update={"history": malformed_history})
    malformed = DeterministicFeatureEngine(
        builtin_feature_registry()
    ).compute_one(
        malformed_context, FeatureRequest(feature_id="range.bar_percent", interval="1d")
    )
    duplicate_bar = context.history.bars[-1].model_copy(
        update={"start_at": context.history.bars[0].start_at}
    )
    duplicate_history = context.history.model_copy(
        update={"bars": (context.history.bars[0], duplicate_bar)}
    )
    duplicate_context = context.model_copy(update={"history": duplicate_history})
    duplicate = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        duplicate_context,
        FeatureRequest(feature_id="range.true_range", interval="1d"),
    )
    assert malformed.status is FeatureStatus.FAILED
    assert duplicate.status is FeatureStatus.FAILED


def test_negative_price_bypassing_a1_validation_is_safely_detected() -> None:
    context = context_with_bars((100.0,))
    assert context.history is not None
    bad_bar = context.history.bars[0].model_copy(update={"low": -1.0})
    bad_history = context.history.model_copy(update={"bars": (bad_bar,)})
    bad_context = context.model_copy(update={"history": bad_history})
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        bad_context, FeatureRequest(feature_id="range.bar_percent", interval="1d")
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None


def test_extended_summary_contains_measurements_without_opinion_language() -> None:
    context = context_with_bars((100.0, 110.0), quote_ltp=112.0)
    bundle = DeterministicFeatureEngine(builtin_feature_registry()).compute(
        context,
        (
            FeatureRequest(feature_id="price.change_percent", interval="1d"),
            FeatureRequest(feature_id="range.bar_percent", interval="1d"),
        ),
    )
    summary = summarize_feature_bundle(bundle).casefold()
    forbidden = (
        "bullish",
        "bearish",
        "buy",
        "sell",
        "opportunity",
        "support",
        "resistance",
    )
    assert all(word not in summary for word in forbidden)


def test_feature_calculators_have_no_external_io_or_wall_clock_dependency() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(Path("src/tiaf/features").glob("*.py"))
    ).casefold()
    forbidden = (
        "tiaf.data.providers",
        "dhan",
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
    )
    assert all(token not in source for token in forbidden)
