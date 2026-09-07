"""Shared deterministic indicator fixtures."""

from collections.abc import Mapping
from typing import Any

from tiaf.indicators import (
    IndicatorEngine,
    IndicatorRequest,
    IndicatorResult,
    builtin_indicator_registry,
)

from ..features._support import context_with_bars


def request(
    indicator_id: str,
    parameters: Mapping[str, int | float] | None = None,
    *,
    interval: str = "1d",
    required: bool = True,
) -> IndicatorRequest:
    """Build one canonical indicator request."""
    return IndicatorRequest(
        indicator_id=indicator_id,
        parameters=tuple((parameters or {}).items()),
        interval=interval,
        required=required,
    )


def calculate(
    indicator_id: str,
    closes: tuple[float, ...],
    parameters: Mapping[str, int | float] | None = None,
    **context_options: Any,
) -> IndicatorResult:
    """Calculate one built-in against deterministic completed history."""
    return IndicatorEngine(builtin_indicator_registry()).calculate(
        request(indicator_id, parameters),
        context_with_bars(closes, **context_options),
    )
