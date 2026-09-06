"""Explicit registry for deterministic feature calculators."""

from typing import Protocol, runtime_checkable

from tiaf.context import AnalysisContext
from tiaf.features.errors import FeatureDefinitionError, FeatureNotRegisteredError
from tiaf.features.models import FeatureDefinition, FeatureRequest, FeatureResult


@runtime_checkable
class FeatureCalculator(Protocol):
    """Pure calculation boundary over an existing AnalysisContext."""

    def definition(self) -> FeatureDefinition:
        """Return this calculator's stable versioned definition."""
        ...

    def compute(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
    ) -> FeatureResult:
        """Derive one deterministic result without external I/O."""
        ...


class FeatureRegistry:
    """Caller-populated calculator registry with deterministic snapshots."""

    def __init__(self, calculators: tuple[FeatureCalculator, ...] = ()) -> None:
        self._calculators: dict[str, FeatureCalculator] = {}
        for calculator in calculators:
            self.register(calculator)

    def register(self, calculator: FeatureCalculator) -> None:
        """Register one calculator and reject duplicate feature IDs."""
        if not isinstance(calculator, FeatureCalculator):
            raise FeatureDefinitionError("calculator does not satisfy FeatureCalculator")
        definition = calculator.definition()
        feature_id = definition.feature_id
        if feature_id in self._calculators:
            raise FeatureDefinitionError(f"duplicate feature ID: {feature_id}")
        self._calculators[feature_id] = calculator

    def get_calculator(self, feature_id: str) -> FeatureCalculator:
        """Return a calculator or raise a typed registry error."""
        try:
            return self._calculators[feature_id]
        except KeyError as exc:
            raise FeatureNotRegisteredError(feature_id) from exc

    def get_definition(self, feature_id: str) -> FeatureDefinition:
        """Return one registered definition."""
        return self.get_calculator(feature_id).definition()

    def definitions(self) -> tuple[FeatureDefinition, ...]:
        """Return an immutable feature-ID-sorted definition snapshot."""
        return tuple(
            self._calculators[feature_id].definition()
            for feature_id in sorted(self._calculators)
        )
