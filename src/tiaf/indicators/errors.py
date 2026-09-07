"""Typed indicator definition, registry, parameter, and calculation errors."""


class IndicatorError(Exception):
    """Base error for the deterministic indicator subsystem."""


class IndicatorDefinitionError(IndicatorError):
    """An indicator definition or registry entry is invalid."""


class IndicatorNotRegisteredError(IndicatorError):
    """A requested indicator ID has no registered calculator."""

    def __init__(self, indicator_id: str) -> None:
        self.indicator_id = indicator_id
        super().__init__(f"indicator {indicator_id!r} is not registered")


class IndicatorParameterError(IndicatorError):
    """Indicator request parameters are missing or invalid."""


class IndicatorComputationError(IndicatorError):
    """An indicator calculator violated its contract or failed unexpectedly."""
