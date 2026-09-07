"""A2.4 indicator contracts, registry, engine, and architecture."""

import runpy
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tiaf.context import AnalysisContext
from tiaf.contracts import DataQuality
from tiaf.features import FeatureSourceKind, FeatureStatus
from tiaf.indicators import (
    BUILTIN_INDICATOR_DEFINITIONS,
    IndicatorDefinition,
    IndicatorDefinitionError,
    IndicatorEngine,
    IndicatorNotRegisteredError,
    IndicatorOutputDefinition,
    IndicatorParameterDefinition,
    IndicatorParameterError,
    IndicatorParameterType,
    IndicatorRegistry,
    IndicatorRequest,
    IndicatorResult,
    builtin_indicator_registry,
    summarize_indicator_bundle,
)
from tiaf.indicators._calculation import (
    IndicatorCalculatorBase,
    float_value,
    number_parameter,
)

from ..context._support import NOW
from ..features._support import (
    context_with_bars,
    context_with_failed_history,
    context_without_sources,
)
from ._support import request

TEST_DEFINITION = IndicatorDefinition(
    indicator_id="test_indicator",
    name="Test indicator",
    description="Extensibility proof without an engine branch.",
    parameters=(
        IndicatorParameterDefinition(
            name="scale",
            value_type=IndicatorParameterType.FLOAT,
            description="Required test scale.",
        ),
    ),
    required_sources=(FeatureSourceKind.HISTORY,),
    outputs=(
        IndicatorOutputDefinition(
            name="scaled_close", unit="price", description="Scaled close."
        ),
    ),
    minimum_history_bars=1,
)


class TestCalculator(IndicatorCalculatorBase):
    __test__ = False

    def __init__(self) -> None:
        super().__init__(TEST_DEFINITION)

    def calculate(
        self, request: IndicatorRequest, context: AnalysisContext
    ) -> IndicatorResult:
        parameters = self._parameters(request)
        prepared, failure = self._prepare_history(
            request, context, parameters, minimum_bars=1
        )
        if failure is not None:
            return failure
        assert prepared is not None
        scale = number_parameter(parameters, "scale")
        return self._history_result(
            request,
            context,
            parameters,
            prepared,
            values=(
                float_value(
                    "scaled_close", prepared.history.bars[-1].close * scale, "price"
                ),
            ),
            lookback_bars_used=1,
        )


def test_contracts_are_frozen_and_semantic_collections_are_tuples() -> None:
    definition = BUILTIN_INDICATOR_DEFINITIONS[0]
    indicator_request = request("rsi", {"period": 14})
    result = IndicatorEngine(builtin_indicator_registry()).calculate(
        indicator_request,
        context_with_bars(tuple(float(value) for value in range(10, 29))),
    )
    bundle = IndicatorEngine(builtin_indicator_registry()).calculate_many(
        (indicator_request,),
        context_with_bars(tuple(float(value) for value in range(10, 29))),
    )
    assert isinstance(definition.parameters, tuple)
    assert isinstance(indicator_request.parameters, tuple)
    assert isinstance(result.values, tuple)
    assert isinstance(bundle.results, tuple)
    for model, field_name in (
        (definition, "name"),
        (indicator_request, "interval"),
        (result, "status"),
        (bundle, "complete"),
    ):
        with pytest.raises(ValidationError, match="frozen"):
            setattr(model, field_name, "replacement")
    with pytest.raises(AttributeError):
        result.values.append(result.values[0])  # type: ignore[attr-defined]


@pytest.mark.parametrize("model_name", ["request", "definition", "result", "bundle"])
def test_contract_json_round_trip(model_name: str) -> None:
    indicator_request = request("rsi", {"period": 14})
    engine = IndicatorEngine(builtin_indicator_registry())
    context = context_with_bars(tuple(float(value) for value in range(10, 29)))
    result = engine.calculate(indicator_request, context)
    models: dict[str, Any] = {
        "request": indicator_request,
        "definition": engine.definitions()[0],
        "result": result,
        "bundle": engine.calculate_many((indicator_request,), context),
    }
    model = models[model_name]
    rebuilt = type(model).model_validate_json(model.model_dump_json())
    assert rebuilt == model
    assert isinstance(model.model_dump(mode="json").get("parameters", []), list)


def test_request_parameter_order_is_semantically_canonical() -> None:
    first = IndicatorRequest(
        indicator_id="macd",
        parameters=(
            ("signal_period", 9),
            ("fast_period", 12),
            ("slow_period", 26),
        ),
        interval="1d",
    )
    second = IndicatorRequest(
        indicator_id="macd",
        parameters=(("slow_period", 26), ("signal_period", 9), ("fast_period", 12)),
        interval="1d",
    )
    assert first == second
    assert first.parameters == (
        ("fast_period", 12),
        ("signal_period", 9),
        ("slow_period", 26),
    )
    from_mapping = IndicatorRequest.model_validate(
        {
            "indicator_id": "rsi",
            "parameters": {"period": 14},
            "interval": "1d",
        }
    )
    assert from_mapping.parameters == (("period", 14),)


def test_registry_is_sorted_and_rejects_duplicate_or_unknown_ids() -> None:
    registry = IndicatorRegistry((TestCalculator(),))
    assert registry.version == "1.0"
    with pytest.raises(IndicatorDefinitionError, match="duplicate indicator ID"):
        registry.register(TestCalculator())
    with pytest.raises(IndicatorNotRegisteredError, match="missing"):
        registry.get_definition("missing")
    definitions = builtin_indicator_registry().definitions()
    assert tuple(item.indicator_id for item in definitions) == tuple(
        sorted(item.indicator_id for item in definitions)
    )
    assert tuple(item.indicator_id for item in BUILTIN_INDICATOR_DEFINITIONS) == (
        "supertrend",
        "rsi",
        "macd",
        "adx",
        "bollinger",
        "donchian",
    )
    with pytest.raises(IndicatorDefinitionError, match="version"):
        IndicatorRegistry(version=" ")


def test_dummy_registration_proves_engine_extensibility() -> None:
    result = IndicatorEngine(IndicatorRegistry((TestCalculator(),))).calculate(
        request("test_indicator", {"scale": 2.0}), context_with_bars((10.0,))
    )
    assert result.value("scaled_close") == 20.0


def test_unknown_missing_and_misspelled_parameters_are_rejected() -> None:
    engine = IndicatorEngine(builtin_indicator_registry())
    context = context_with_bars(tuple(float(value) for value in range(10, 49)))
    with pytest.raises(IndicatorNotRegisteredError):
        engine.calculate(request("missing"), context)
    with pytest.raises(IndicatorParameterError, match="does not accept"):
        engine.calculate(request("rsi", {"preiod": 14}), context)
    with pytest.raises(IndicatorParameterError, match="requires parameter"):
        IndicatorEngine(IndicatorRegistry((TestCalculator(),))).calculate(
            request("test_indicator"), context
        )


def test_defaults_resolve_to_same_identity_as_explicit_values() -> None:
    context = context_with_bars(tuple(float(value) for value in range(10, 49)))
    engine = IndicatorEngine(builtin_indicator_registry())
    default = engine.calculate(request("rsi"), context)
    explicit = engine.calculate(request("rsi", {"period": 14}), context)
    assert default.parameters == (("period", 14),)
    assert default == explicit
    default_supertrend = engine.calculate(request("supertrend"), context)
    integer_multiplier = engine.calculate(
        request("supertrend", {"period": 10, "multiplier": 3}), context
    )
    assert default_supertrend == integer_multiplier


def test_calculate_many_preserves_order_and_isolates_failure() -> None:
    context = context_with_bars(tuple(float(value) for value in range(10, 59)))
    bundle = IndicatorEngine(builtin_indicator_registry()).calculate_many(
        (
            request("rsi"),
            request("macd", {"fast_period": 26, "slow_period": 12, "signal_period": 9}),
            request("donchian"),
        ),
        context,
    )
    assert tuple(result.indicator_id for result in bundle.results) == (
        "rsi",
        "macd",
        "donchian",
    )
    assert tuple(result.status for result in bundle.results) == (
        FeatureStatus.AVAILABLE,
        FeatureStatus.FAILED,
        FeatureStatus.AVAILABLE,
    )


@pytest.mark.parametrize(
    ("context", "expected"),
    [
        (context_without_sources(), FeatureStatus.NOT_APPLICABLE),
        (context_with_failed_history(), FeatureStatus.INSUFFICIENT_DATA),
    ],
)
def test_unusable_evidence_is_isolated(context: AnalysisContext, expected: FeatureStatus) -> None:
    result = IndicatorEngine(builtin_indicator_registry()).calculate(
        request("rsi"), context
    )
    assert result.status is expected
    assert result.values == ()


def test_quality_as_of_interval_and_quote_independence() -> None:
    context = context_with_bars(
        tuple(float(value) for value in range(10, 29)),
        history_quality=DataQuality.DEGRADED,
        history_observed_at=NOW,
        latest_bar_end_at=NOW,
        quote_ltp=99999.0,
    )
    result = IndicatorEngine(builtin_indicator_registry()).calculate(
        request("rsi"), context
    )
    assert result.status is FeatureStatus.PARTIAL
    assert result.quality is DataQuality.DEGRADED
    assert result.as_of == NOW
    assert result.source_observed_at == NOW
    assert result.source_evidence == ("history",)
    mismatch = IndicatorEngine(builtin_indicator_registry()).calculate(
        request("rsi", interval="1h"), context
    )
    assert mismatch.status is FeatureStatus.NOT_APPLICABLE
    assert context.quote is not None
    different_quote = context.model_copy(
        update={"quote": context.quote.model_copy(update={"ltp": 1.0})}
    )
    assert result.values == IndicatorEngine(builtin_indicator_registry()).calculate(
        request("rsi"), different_quote
    ).values


def test_context_creation_time_does_not_change_indicator_calculation() -> None:
    context = context_with_bars(tuple(float(value) for value in range(10, 49)))
    later = context.model_copy(update={"created_at": NOW.replace(hour=15)})
    engine = IndicatorEngine(builtin_indicator_registry())
    first = engine.calculate(request("macd"), context)
    second = engine.calculate(request("macd"), later)
    assert first.values == second.values
    assert first.as_of == second.as_of


def test_bundle_and_result_identity_are_deterministic() -> None:
    context = context_with_bars(tuple(float(value) for value in range(10, 49)))
    requests = (request("rsi"), request("bollinger"))
    engine = IndicatorEngine(builtin_indicator_registry())
    assert engine.calculate_many(requests, context) == engine.calculate_many(
        requests, context
    )


def test_summary_and_source_tree_have_no_strategy_or_external_dependencies() -> None:
    context = context_with_bars(tuple(float(value) for value in range(10, 49)))
    bundle = IndicatorEngine(builtin_indicator_registry()).calculate_many(
        (request("rsi"), request("macd")), context
    )
    summary = summarize_indicator_bundle(bundle).casefold()
    forbidden_output = ("buy", "sell", "bullish", "bearish", "overbought", "oversold")
    assert all(word not in summary for word in forbidden_output)
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(Path("src/tiaf/indicators").rglob("*.py"))
    ).casefold()
    forbidden_source = (
        "tiaf.data.providers",
        "httpx",
        "requests.",
        "resolver",
        "broker",
        "langgraph",
        "openai",
        "sigmadsl",
        "datetime.now",
        "time.sleep",
        "buy signal",
        "sell signal",
    )
    assert all(term not in source for term in forbidden_source)
    central_engine = Path("src/tiaf/indicators/engine.py").read_text(encoding="utf-8")
    assert all(
        f'"{indicator_id}"' not in central_engine
        for indicator_id in ("supertrend", "rsi", "macd", "adx", "bollinger", "donchian")
    )


def test_smoke_selection_and_request_inventory() -> None:
    namespace: dict[str, Any] = runpy.run_path(
        "scripts/indicator_engine_smoke.py", run_name="indicator_smoke"
    )
    selected = namespace["_selected_ids"](
        ["rsi,macd", "donchian"], all_indicators=False
    )
    requests = namespace["_requests"]("1d", selected)
    assert selected == ("rsi", "macd", "donchian")
    assert tuple(item.indicator_id for item in requests) == selected


def test_halftrend_is_not_falsely_registered() -> None:
    assert "halftrend" not in {
        definition.indicator_id for definition in builtin_indicator_registry().definitions()
    }
