"""Registry and deterministic orchestration behavior."""

from pathlib import Path

import pytest

from tiaf.context import AnalysisContext
from tiaf.contracts import DataQuality
from tiaf.features import (
    CurrentPriceCalculator,
    DeterministicFeatureEngine,
    FeatureCategory,
    FeatureComputationError,
    FeatureDefinition,
    FeatureDefinitionError,
    FeatureNotRegisteredError,
    FeatureParameterError,
    FeatureRegistry,
    FeatureRequest,
    FeatureResult,
    FeatureSourceKind,
    FeatureStatus,
    FeatureValueType,
    builtin_feature_registry,
)
from tiaf.features import __all__ as public_feature_exports

from ._support import context_with_bars

FAILURE_DEFINITION = FeatureDefinition(
    feature_id="test.failure",
    name="Test failure",
    category=FeatureCategory.META,
    description="Test-only calculator failure.",
    value_type=FeatureValueType.FLOAT,
    unit="count",
    required_sources=(FeatureSourceKind.CONTEXT,),
)


class FailingCalculator:
    def definition(self) -> FeatureDefinition:
        return FAILURE_DEFINITION

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        del context, request
        raise FeatureParameterError("deliberate isolated failure")


class UnexpectedFailingCalculator:
    def definition(self) -> FeatureDefinition:
        return FAILURE_DEFINITION

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        del context, request
        raise RuntimeError("sensitive detail must not escape")


def test_registry_rejects_duplicates_and_unknown_features_with_typed_errors() -> None:
    registry = FeatureRegistry()
    registry.register(CurrentPriceCalculator())
    with pytest.raises(FeatureDefinitionError, match="duplicate feature ID"):
        registry.register(CurrentPriceCalculator())
    with pytest.raises(FeatureNotRegisteredError) as caught:
        registry.get_definition("missing.feature")
    assert caught.value.feature_id == "missing.feature"


def test_registry_definition_snapshot_is_sorted_and_immutable() -> None:
    definitions = builtin_feature_registry().definitions()
    assert isinstance(definitions, tuple)
    assert tuple(item.feature_id for item in definitions) == tuple(
        sorted(item.feature_id for item in definitions)
    )


def test_engine_preserves_request_order_and_is_deterministic() -> None:
    context = context_with_bars(tuple(float(value) for value in range(100, 121)))
    requests = (
        FeatureRequest(feature_id="history.last_close", interval="1d"),
        FeatureRequest(feature_id="price.current"),
        FeatureRequest(
            feature_id="return.percent",
            parameters=(("bars", 5),),
            interval="1d",
        ),
    )
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    first = engine.compute(context, requests)
    second = engine.compute(context, requests)
    assert tuple(item.request for item in first.results) == requests
    assert first == second
    assert first.bundle_id == second.bundle_id
    assert first.created_at == context.created_at
    assert first.complete


def test_unknown_feature_is_rejected_before_partial_bundle_construction() -> None:
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    with pytest.raises(FeatureNotRegisteredError, match="unknown.feature"):
        engine.compute(
            context_with_bars(),
            (
                FeatureRequest(feature_id="price.current"),
                FeatureRequest(feature_id="unknown.feature"),
            ),
        )


def test_empty_request_batch_is_rejected() -> None:
    with pytest.raises(FeatureParameterError, match="at least one"):
        DeterministicFeatureEngine(builtin_feature_registry()).compute(
            context_with_bars(), ()
        )


def test_one_calculator_failure_does_not_suppress_other_results() -> None:
    registry = FeatureRegistry((FailingCalculator(), CurrentPriceCalculator()))
    bundle = DeterministicFeatureEngine(registry).compute(
        context_with_bars(),
        (
            FeatureRequest(feature_id="test.failure", required=False),
            FeatureRequest(feature_id="price.current"),
        ),
    )
    assert tuple(item.status for item in bundle.results) == (
        FeatureStatus.FAILED,
        FeatureStatus.AVAILABLE,
    )
    assert bundle.results[0].warnings == ("deliberate isolated failure",)
    assert bundle.complete
    assert bundle.overall_quality is DataQuality.PARTIAL


def test_unexpected_calculator_failure_is_sanitized_and_typed_for_compute_one() -> None:
    engine = DeterministicFeatureEngine(
        FeatureRegistry((UnexpectedFailingCalculator(),))
    )
    with pytest.raises(FeatureComputationError) as caught:
        engine.compute_one(
            context_with_bars(), FeatureRequest(feature_id="test.failure")
        )
    assert "RuntimeError" in str(caught.value)
    assert "sensitive detail" not in str(caught.value)


def test_required_and_optional_failures_have_explicit_completeness_semantics() -> None:
    context = context_with_bars((100.0,))
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    required = engine.compute(
        context,
        (
            FeatureRequest(
                feature_id="return.percent",
                parameters=(("bars", 1),),
                interval="1d",
            ),
        ),
    )
    optional = engine.compute(
        context,
        (
            FeatureRequest(
                feature_id="return.percent",
                parameters=(("bars", 1),),
                interval="1d",
                required=False,
            ),
        ),
    )
    assert not required.complete
    assert required.missing_required_features == ("return.percent",)
    assert optional.complete
    assert optional.missing_required_features == ()


def test_feature_package_has_no_external_io_or_trading_dependencies() -> None:
    feature_root = Path("src/tiaf/features")
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(feature_root.glob("*.py"))
    ).casefold()
    forbidden = (
        "tiaf.data.providers",
        "dhan",
        "httpx",
        "langgraph",
        "openai",
        "datetime.now",
        "time.sleep",
        "get_quote(",
        "get_historical(",
        "instrumentresolver",
        "datafetchcoordinator",
        "providerscheduler",
        "broker",
        "langchain",
    )
    assert all(token not in source for token in forbidden)


def test_public_feature_contracts_and_engine_are_exported() -> None:
    expected = {
        "FeatureDefinition",
        "FeatureRequest",
        "FeatureResult",
        "FeatureBundle",
        "FeatureRegistry",
        "FeatureCalculator",
        "DeterministicFeatureEngine",
        "builtin_feature_registry",
        "summarize_feature_bundle",
    }
    assert expected <= set(public_feature_exports)
