"""Shared preparation, parameter, identity, and result guards for indicators."""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import NAMESPACE_URL, uuid5

from tiaf.context import AnalysisContext
from tiaf.contracts import DataQuality
from tiaf.contracts.common import Metadata
from tiaf.data import HistoricalSeries
from tiaf.features._calculation import (
    evidence,
    evidence_status,
    evidence_warnings,
    source_quality,
    validate_bars,
)
from tiaf.features.enums import FeatureStatus
from tiaf.indicators.enums import IndicatorParameterType
from tiaf.indicators.errors import IndicatorParameterError
from tiaf.indicators.models import (
    IndicatorDefinition,
    IndicatorParameterValue,
    IndicatorRequest,
    IndicatorResult,
    IndicatorState,
    IndicatorValue,
    _validate_parameter_scalar,
)


@dataclass(frozen=True)
class PreparedIndicatorHistory:
    """Validated completed history with inherited provenance."""

    history: HistoricalSeries
    status: FeatureStatus
    quality: DataQuality
    as_of: datetime
    metadata: Metadata
    warnings: tuple[str, ...]


def resolve_parameters(
    definition: IndicatorDefinition,
    request: IndicatorRequest,
) -> tuple[tuple[str, IndicatorParameterValue], ...]:
    """Apply versioned defaults and reject unknown, missing, or ill-typed values."""
    supplied = dict(request.parameters)
    definitions = {item.name: item for item in definition.parameters}
    unknown = tuple(sorted(set(supplied) - set(definitions)))
    if unknown:
        raise IndicatorParameterError(
            f"indicator {definition.indicator_id!r} does not accept: {', '.join(unknown)}"
        )
    resolved: list[tuple[str, IndicatorParameterValue]] = []
    for name in sorted(definitions):
        parameter = definitions[name]
        if name in supplied:
            value = supplied[name]
        elif parameter.has_default:
            value = parameter.default
        elif parameter.required:
            raise IndicatorParameterError(
                f"indicator {definition.indicator_id!r} requires parameter {name!r}"
            )
        else:
            continue
        try:
            _validate_parameter_scalar(parameter, value)
        except ValueError as exc:
            raise IndicatorParameterError(str(exc)) from exc
        if parameter.value_type is IndicatorParameterType.FLOAT:
            assert isinstance(value, (int, float)) and not isinstance(value, bool)
            canonical_value: IndicatorParameterValue = float(value)
        else:
            canonical_value = value
        resolved.append((name, canonical_value))
    return tuple(resolved)


def integer_parameter(
    parameters: tuple[tuple[str, IndicatorParameterValue], ...], name: str
) -> int:
    """Return one already-validated integer parameter."""
    value = dict(parameters)[name]
    if not isinstance(value, int) or isinstance(value, bool):
        raise IndicatorParameterError(f"parameter {name!r} must be an integer")
    return value


def number_parameter(
    parameters: tuple[tuple[str, IndicatorParameterValue], ...], name: str
) -> float:
    """Return one already-validated finite numeric parameter."""
    value = dict(parameters)[name]
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise IndicatorParameterError(f"parameter {name!r} must be numeric")
    return float(value)


class IndicatorCalculatorBase(ABC):
    """Common deterministic implementation boundary for history indicators."""

    def __init__(self, definition: IndicatorDefinition) -> None:
        self._definition = definition

    def definition(self) -> IndicatorDefinition:
        """Return the immutable indicator definition."""
        return self._definition

    @abstractmethod
    def calculate(
        self,
        request: IndicatorRequest,
        context: AnalysisContext,
    ) -> IndicatorResult:
        """Calculate one indicator."""

    def _parameters(
        self, request: IndicatorRequest
    ) -> tuple[tuple[str, IndicatorParameterValue], ...]:
        if request.indicator_id != self._definition.indicator_id:
            raise IndicatorParameterError(
                f"calculator {self._definition.indicator_id!r} cannot calculate "
                f"{request.indicator_id!r}"
            )
        return resolve_parameters(self._definition, request)

    def _prepare_history(
        self,
        request: IndicatorRequest,
        context: AnalysisContext,
        parameters: tuple[tuple[str, IndicatorParameterValue], ...],
        *,
        minimum_bars: int,
    ) -> tuple[PreparedIndicatorHistory | None, IndicatorResult | None]:
        descriptor = evidence(context, "history")
        fallback_quality = context.history.quality if context.history is not None else None
        quality = source_quality(descriptor, fallback_quality)
        status = evidence_status(descriptor, fallback_quality)
        if status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
            as_of = (
                descriptor.source_observed_at
                if descriptor is not None and descriptor.source_observed_at is not None
                else context.created_at
            )
            return None, self._result(
                request,
                context,
                parameters,
                status=status,
                quality=quality,
                as_of=as_of,
                warnings=evidence_warnings(descriptor),
            )
        assert context.history is not None
        bars = context.history.bars
        market_as_of = bars[-1].end_at if bars else context.history.observed_at
        metadata: Metadata = {"source_time_semantics": "latest_history_bar_end"}
        if bars:
            metadata.update(
                {
                    "latest_bar_start_at": bars[-1].start_at.isoformat(),
                    "latest_bar_end_at": bars[-1].end_at.isoformat(),
                }
            )
        if descriptor is not None and descriptor.source_observed_at is not None:
            metadata["history_acquired_at"] = descriptor.source_observed_at.isoformat()
        if context.history.interval != request.interval:
            return None, self._result(
                request,
                context,
                parameters,
                status=FeatureStatus.NOT_APPLICABLE,
                quality=quality,
                as_of=market_as_of,
                warnings=(
                    f"requested interval {request.interval} does not match "
                    f"context history interval {context.history.interval}",
                ),
                metadata=metadata,
            )
        if (
            self._definition.supported_intervals is not None
            and request.interval not in self._definition.supported_intervals
        ):
            return None, self._result(
                request,
                context,
                parameters,
                status=FeatureStatus.NOT_APPLICABLE,
                quality=quality,
                as_of=market_as_of,
                warnings=(f"interval {request.interval} is not supported",),
                metadata=metadata,
            )
        if len(bars) < minimum_bars:
            return None, self._result(
                request,
                context,
                parameters,
                status=FeatureStatus.INSUFFICIENT_DATA,
                quality=quality,
                as_of=market_as_of,
                warnings=(
                    f"requires {minimum_bars} history bars; available {len(bars)}",
                ),
                metadata=metadata,
            )
        malformed = validate_bars(bars)
        if malformed is None and any(
            price <= 0
            for bar in bars
            for price in (bar.open, bar.high, bar.low, bar.close)
        ):
            malformed = "indicator history requires strictly positive OHLC values"
        if malformed is not None:
            return None, self._result(
                request,
                context,
                parameters,
                status=FeatureStatus.FAILED,
                quality=quality,
                as_of=market_as_of,
                warnings=(malformed,),
                metadata=metadata,
            )
        return (
            PreparedIndicatorHistory(
                history=context.history,
                status=status,
                quality=quality,
                as_of=bars[-1].end_at,
                metadata=metadata,
                warnings=evidence_warnings(descriptor),
            ),
            None,
        )

    def _history_result(
        self,
        request: IndicatorRequest,
        context: AnalysisContext,
        parameters: tuple[tuple[str, IndicatorParameterValue], ...],
        prepared: PreparedIndicatorHistory,
        *,
        status: FeatureStatus | None = None,
        values: tuple[IndicatorValue, ...] = (),
        states: tuple[IndicatorState, ...] = (),
        lookback_bars_used: int | None = None,
        warnings: tuple[str, ...] = (),
    ) -> IndicatorResult:
        return self._result(
            request,
            context,
            parameters,
            status=status or prepared.status,
            quality=prepared.quality,
            as_of=prepared.as_of,
            values=values,
            states=states,
            lookback_bars_used=lookback_bars_used,
            warnings=prepared.warnings + warnings,
            metadata=prepared.metadata,
        )

    def _result(
        self,
        request: IndicatorRequest,
        context: AnalysisContext,
        parameters: tuple[tuple[str, IndicatorParameterValue], ...],
        *,
        status: FeatureStatus,
        quality: DataQuality,
        as_of: datetime,
        values: tuple[IndicatorValue, ...] = (),
        states: tuple[IndicatorState, ...] = (),
        lookback_bars_used: int | None = None,
        warnings: tuple[str, ...] = (),
        metadata: Metadata | None = None,
    ) -> IndicatorResult:
        if any(
            isinstance(item.value, float) and not math.isfinite(item.value)
            for item in values
        ):
            status = FeatureStatus.FAILED
            values = ()
            states = ()
            warnings += ("indicator calculation produced a non-finite value",)
        identity = "|".join(f"{name}={value!r}" for name, value in parameters)
        result_id = str(
            uuid5(
                NAMESPACE_URL,
                f"tiaf:indicator:{context.context_id}:{self._definition.indicator_id}:"
                f"{self._definition.definition_version}:{request.interval}:"
                f"required={request.required}:{identity}",
            )
        )
        return IndicatorResult(
            result_id=result_id,
            indicator_id=self._definition.indicator_id,
            definition_version=self._definition.definition_version,
            parameters=parameters,
            interval=request.interval,
            required=request.required,
            status=status,
            quality=quality,
            as_of=as_of,
            values=values,
            states=states,
            source_context_id=context.context_id,
            subject_symbol=context.subject.symbol,
            source_evidence=("history",),
            source_observed_at=as_of,
            lookback_bars_used=lookback_bars_used,
            warnings=warnings,
            metadata=metadata or {},
        )


def float_value(name: str, value: float, unit: str) -> IndicatorValue:
    """Build one explicitly floating, finite indicator output."""
    return IndicatorValue(name=name, value=float(value), unit=unit)
