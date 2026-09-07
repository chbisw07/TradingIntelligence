"""Explicit deterministic registry for indicator calculators."""

from typing import Protocol, runtime_checkable

from tiaf.context import AnalysisContext
from tiaf.indicators.errors import IndicatorDefinitionError, IndicatorNotRegisteredError
from tiaf.indicators.models import IndicatorDefinition, IndicatorRequest, IndicatorResult


@runtime_checkable
class IndicatorCalculator(Protocol):
    """Pure indicator calculation boundary over an existing AnalysisContext."""

    def definition(self) -> IndicatorDefinition:
        """Return the calculator's stable versioned definition."""
        ...

    def calculate(
        self,
        request: IndicatorRequest,
        context: AnalysisContext,
    ) -> IndicatorResult:
        """Calculate one deterministic completed-history indicator."""
        ...


class IndicatorRegistry:
    """Caller-populated registry with canonical ID-sorted discovery."""

    def __init__(
        self,
        calculators: tuple[IndicatorCalculator, ...] = (),
        *,
        version: str = "1.0",
    ) -> None:
        if not version.strip():
            raise IndicatorDefinitionError("registry version must be non-empty")
        self._version = version.strip()
        self._calculators: dict[str, IndicatorCalculator] = {}
        for calculator in calculators:
            self.register(calculator)

    @property
    def version(self) -> str:
        """Return the explicit registry contract version."""
        return self._version

    def register(self, calculator: IndicatorCalculator) -> None:
        """Register one calculator and reject duplicate IDs."""
        if not isinstance(calculator, IndicatorCalculator):
            raise IndicatorDefinitionError(
                "calculator does not satisfy IndicatorCalculator"
            )
        definition = calculator.definition()
        if definition.indicator_id in self._calculators:
            raise IndicatorDefinitionError(
                f"duplicate indicator ID: {definition.indicator_id}"
            )
        self._calculators[definition.indicator_id] = calculator

    def get_calculator(self, indicator_id: str) -> IndicatorCalculator:
        """Return one calculator or raise a typed lookup error."""
        try:
            return self._calculators[indicator_id]
        except KeyError as exc:
            raise IndicatorNotRegisteredError(indicator_id) from exc

    def get_definition(self, indicator_id: str) -> IndicatorDefinition:
        """Return one registered definition."""
        return self.get_calculator(indicator_id).definition()

    def definitions(self) -> tuple[IndicatorDefinition, ...]:
        """Return an immutable ID-sorted definition snapshot."""
        return tuple(
            self._calculators[indicator_id].definition()
            for indicator_id in sorted(self._calculators)
        )
