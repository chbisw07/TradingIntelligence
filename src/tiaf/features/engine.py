"""Deterministic orchestration over registered pure feature calculators."""

from uuid import NAMESPACE_URL, uuid5

from tiaf.context import AnalysisContext, EvidenceStatus
from tiaf.contracts import DataQuality
from tiaf.features.calculators import BUILTIN_CALCULATORS
from tiaf.features.enums import FeatureSourceKind, FeatureStatus
from tiaf.features.errors import (
    FeatureComputationError,
    FeatureError,
    FeatureParameterError,
)
from tiaf.features.models import (
    FeatureBundle,
    FeatureDefinition,
    FeatureRequest,
    FeatureResult,
)
from tiaf.features.registry import FeatureCalculator, FeatureRegistry

_SOURCE_EVIDENCE_NAMES = {
    FeatureSourceKind.QUOTE: "quote",
    FeatureSourceKind.HISTORY: "history",
    FeatureSourceKind.OPTION_CHAIN: "option_chain",
    FeatureSourceKind.HISTORICAL_OPTIONS: "historical_options",
    FeatureSourceKind.CONTEXT: "context",
    FeatureSourceKind.DERIVED: "derived",
}


def builtin_feature_registry() -> FeatureRegistry:
    """Create an explicit registry containing only the A2.1 built-ins."""
    return FeatureRegistry(BUILTIN_CALCULATORS)


class DeterministicFeatureEngine:
    """Compute ordered features from one immutable AnalysisContext only."""

    def __init__(self, registry: FeatureRegistry) -> None:
        self._registry = registry

    def definitions(self) -> tuple[FeatureDefinition, ...]:
        """Return the registry's deterministic immutable definition snapshot."""
        return self._registry.definitions()

    def compute_one(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
    ) -> FeatureResult:
        """Compute one feature, surfacing typed registry/parameter failures."""
        self._validate_context(context)
        calculator = self._registry.get_calculator(request.feature_id)
        return self._compute_checked(calculator, context, request)

    def compute(
        self,
        context: AnalysisContext,
        requests: tuple[FeatureRequest, ...],
        *,
        bundle_id: str | None = None,
    ) -> FeatureBundle:
        """Compute each known feature independently and preserve request order."""
        self._validate_context(context)
        if not requests:
            raise FeatureParameterError("at least one feature request is required")
        calculators = tuple(
            self._registry.get_calculator(request.feature_id) for request in requests
        )
        results: list[FeatureResult] = []
        for calculator, request in zip(calculators, requests, strict=True):
            try:
                result = self._compute_checked(calculator, context, request)
            except FeatureError as exc:
                result = self._failed_result(
                    calculator.definition(), context, request, str(exc)
                )
            results.append(result)

        frozen_results = tuple(results)
        missing_required = tuple(
            result.request.feature_id
            for result in frozen_results
            if result.request.required
            and result.status
            not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
        )
        warnings = tuple(
            f"{result.request.feature_id}: {warning}"
            for result in frozen_results
            for warning in result.warnings
        )
        return FeatureBundle(
            bundle_id=bundle_id or self._deterministic_bundle_id(context, requests),
            context_id=context.context_id,
            subject_symbol=context.subject.symbol,
            created_at=context.created_at,
            results=frozen_results,
            overall_quality=self._aggregate_quality(frozen_results, missing_required),
            complete=not missing_required,
            missing_required_features=missing_required,
            warnings=warnings,
        )

    @staticmethod
    def _validate_context(context: AnalysisContext) -> None:
        if context.subject.symbol != context.subject.resolved_instrument.instrument.symbol:
            raise FeatureComputationError("AnalysisContext identity is inconsistent")
        if any(item.status is EvidenceStatus.DEFERRED for item in context.evidence):
            raise FeatureComputationError(
                "deferred AnalysisContext evidence must be completed before feature computation"
            )

    @staticmethod
    def _compute_checked(
        calculator: FeatureCalculator,
        context: AnalysisContext,
        request: FeatureRequest,
    ) -> FeatureResult:
        definition = calculator.definition()
        try:
            result = calculator.compute(context, request)
        except FeatureError:
            raise
        except Exception as exc:
            raise FeatureComputationError(
                f"calculator {definition.feature_id!r} failed with {type(exc).__name__}"
            ) from exc
        if result.definition != definition:
            raise FeatureComputationError("calculator returned a different definition")
        if result.request != request:
            raise FeatureComputationError("calculator returned a different request")
        if result.source_context_id != context.context_id:
            raise FeatureComputationError("calculator returned a different context ID")
        if result.subject_symbol != context.subject.symbol:
            raise FeatureComputationError("calculator returned a different subject symbol")
        return result

    @staticmethod
    def _failed_result(
        definition: FeatureDefinition,
        context: AnalysisContext,
        request: FeatureRequest,
        warning: str,
    ) -> FeatureResult:
        source_evidence = tuple(
            _SOURCE_EVIDENCE_NAMES[source] for source in definition.required_sources
        )
        return FeatureResult(
            definition=definition,
            request=request,
            status=FeatureStatus.FAILED,
            value=None,
            unit=definition.unit,
            as_of=context.created_at,
            source_context_id=context.context_id,
            subject_symbol=context.subject.symbol,
            source_evidence=source_evidence,
            quality=DataQuality.UNAVAILABLE,
            warnings=(warning,),
        )

    @staticmethod
    def _aggregate_quality(
        results: tuple[FeatureResult, ...],
        missing_required: tuple[str, ...],
    ) -> DataQuality:
        usable = tuple(
            result
            for result in results
            if result.status in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
        )
        if not usable:
            return DataQuality.UNAVAILABLE
        if missing_required or any(
            result.quality is DataQuality.DEGRADED for result in usable
        ):
            return DataQuality.DEGRADED
        if any(
            result.status is not FeatureStatus.AVAILABLE
            or result.quality in {DataQuality.PARTIAL, DataQuality.UNAVAILABLE}
            for result in results
        ):
            return DataQuality.PARTIAL
        return DataQuality.GOOD

    @staticmethod
    def _deterministic_bundle_id(
        context: AnalysisContext,
        requests: tuple[FeatureRequest, ...],
    ) -> str:
        request_identity = "|".join(request.model_dump_json() for request in requests)
        return str(
            uuid5(
                NAMESPACE_URL,
                f"tiaf:features:{context.context_id}:{request_identity}",
            )
        )
