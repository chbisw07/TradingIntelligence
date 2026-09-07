"""Indicator-agnostic deterministic orchestration over registered calculators."""

from uuid import NAMESPACE_URL, uuid5

from tiaf.context import AnalysisContext, EvidenceStatus
from tiaf.contracts import DataQuality
from tiaf.features.enums import FeatureSourceKind, FeatureStatus
from tiaf.indicators.errors import (
    IndicatorComputationError,
    IndicatorError,
    IndicatorParameterError,
)
from tiaf.indicators.models import (
    IndicatorBundle,
    IndicatorDefinition,
    IndicatorRequest,
    IndicatorResult,
)
from tiaf.indicators.registry import IndicatorCalculator, IndicatorRegistry

_SOURCE_NAMES = {
    FeatureSourceKind.QUOTE: "quote",
    FeatureSourceKind.HISTORY: "history",
    FeatureSourceKind.OPTION_CHAIN: "option_chain",
    FeatureSourceKind.HISTORICAL_OPTIONS: "historical_options",
    FeatureSourceKind.CONTEXT: "context",
    FeatureSourceKind.DERIVED: "derived",
}


class IndicatorEngine:
    """Calculate registered indicators uniformly from one immutable context."""

    def __init__(self, registry: IndicatorRegistry) -> None:
        self._registry = registry

    def definitions(self) -> tuple[IndicatorDefinition, ...]:
        """Return stable discoverable definitions."""
        return self._registry.definitions()

    @property
    def registry_version(self) -> str:
        """Return the explicit registry version used by this engine."""
        return self._registry.version

    def calculate(
        self,
        request: IndicatorRequest,
        context: AnalysisContext,
    ) -> IndicatorResult:
        """Calculate one indicator, surfacing typed request errors."""
        self._validate_context(context)
        calculator = self._registry.get_calculator(request.indicator_id)
        return self._calculate_checked(calculator, request, context)

    def calculate_many(
        self,
        requests: tuple[IndicatorRequest, ...],
        context: AnalysisContext,
        *,
        bundle_id: str | None = None,
    ) -> IndicatorBundle:
        """Preserve request order while isolating known calculator failures."""
        self._validate_context(context)
        if not requests:
            raise IndicatorParameterError("at least one indicator request is required")
        calculators = tuple(
            self._registry.get_calculator(request.indicator_id) for request in requests
        )
        results: list[IndicatorResult] = []
        for calculator, request in zip(calculators, requests, strict=True):
            try:
                result = self._calculate_checked(calculator, request, context)
            except IndicatorError as exc:
                result = self._failed_result(
                    calculator.definition(), request, context, str(exc)
                )
            results.append(result)
        frozen_results = tuple(results)
        missing = tuple(
            result.indicator_id
            for result in frozen_results
            if result.required
            and result.status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
        )
        warnings = tuple(
            f"{result.indicator_id}: {warning}"
            for result in frozen_results
            for warning in result.warnings
        )
        return IndicatorBundle(
            bundle_id=bundle_id
            or self._deterministic_bundle_id(context, frozen_results),
            registry_version=self._registry.version,
            context_id=context.context_id,
            subject_symbol=context.subject.symbol,
            created_at=context.created_at,
            results=frozen_results,
            overall_quality=self._aggregate_quality(frozen_results, missing),
            complete=not missing,
            missing_required_indicators=missing,
            warnings=warnings,
        )

    @staticmethod
    def _validate_context(context: AnalysisContext) -> None:
        if context.subject.symbol != context.subject.resolved_instrument.instrument.symbol:
            raise IndicatorComputationError("AnalysisContext identity is inconsistent")
        if any(item.status is EvidenceStatus.DEFERRED for item in context.evidence):
            raise IndicatorComputationError(
                "deferred AnalysisContext evidence must complete before indicators"
            )

    @staticmethod
    def _calculate_checked(
        calculator: IndicatorCalculator,
        request: IndicatorRequest,
        context: AnalysisContext,
    ) -> IndicatorResult:
        definition = calculator.definition()
        try:
            result = calculator.calculate(request, context)
        except IndicatorError:
            raise
        except Exception as exc:
            raise IndicatorComputationError(
                f"calculator {definition.indicator_id!r} failed with {type(exc).__name__}"
            ) from exc
        if result.indicator_id != definition.indicator_id:
            raise IndicatorComputationError("calculator returned a different indicator ID")
        if result.definition_version != definition.definition_version:
            raise IndicatorComputationError("calculator returned a different definition version")
        if result.interval != request.interval or result.required != request.required:
            raise IndicatorComputationError("calculator returned different request semantics")
        if result.source_context_id != context.context_id:
            raise IndicatorComputationError("calculator returned a different context ID")
        if result.subject_symbol != context.subject.symbol:
            raise IndicatorComputationError("calculator returned a different subject symbol")
        expected_outputs = {item.name: item.unit for item in definition.outputs}
        if any(expected_outputs.get(item.name) != item.unit for item in result.values):
            raise IndicatorComputationError("calculator returned an undeclared output")
        expected_states = {
            item.name: set(item.allowed_values) for item in definition.states
        }
        if any(
            item.name not in expected_states
            or item.value not in expected_states[item.name]
            for item in result.states
        ):
            raise IndicatorComputationError("calculator returned an undeclared state")
        return result

    @staticmethod
    def _failed_result(
        definition: IndicatorDefinition,
        request: IndicatorRequest,
        context: AnalysisContext,
        warning: str,
    ) -> IndicatorResult:
        identity = "|".join(f"{name}={value!r}" for name, value in request.parameters)
        return IndicatorResult(
            result_id=str(
                uuid5(
                    NAMESPACE_URL,
                    f"tiaf:indicator:{context.context_id}:{request.indicator_id}:"
                    f"{definition.definition_version}:{request.interval}:"
                    f"required={request.required}:{identity}",
                )
            ),
            indicator_id=definition.indicator_id,
            definition_version=definition.definition_version,
            parameters=request.parameters,
            interval=request.interval,
            required=request.required,
            status=FeatureStatus.FAILED,
            quality=DataQuality.UNAVAILABLE,
            as_of=context.created_at,
            source_context_id=context.context_id,
            subject_symbol=context.subject.symbol,
            source_evidence=tuple(
                _SOURCE_NAMES[source] for source in definition.required_sources
            ),
            warnings=(warning,),
        )

    @staticmethod
    def _aggregate_quality(
        results: tuple[IndicatorResult, ...],
        missing: tuple[str, ...],
    ) -> DataQuality:
        usable = tuple(
            result
            for result in results
            if result.status in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
        )
        if not usable:
            return DataQuality.UNAVAILABLE
        if missing or any(result.quality is DataQuality.DEGRADED for result in usable):
            return DataQuality.DEGRADED
        if any(
            result.status is not FeatureStatus.AVAILABLE
            or result.quality in {DataQuality.PARTIAL, DataQuality.UNAVAILABLE}
            for result in results
        ):
            return DataQuality.PARTIAL
        return DataQuality.GOOD

    def _deterministic_bundle_id(
        self,
        context: AnalysisContext,
        results: tuple[IndicatorResult, ...],
    ) -> str:
        identity = "|".join(result.result_id for result in results)
        return str(
            uuid5(
                NAMESPACE_URL,
                f"tiaf:indicators:{self._registry.version}:"
                f"{context.context_id}:{identity}",
            )
        )
