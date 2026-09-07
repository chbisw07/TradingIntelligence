"""Explicit-benchmark relative-strength contexts and deterministic features."""

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import NAMESPACE_URL, uuid5

from pydantic import Field, field_validator, model_validator

from tiaf.context import AnalysisContext
from tiaf.contracts import ContractModel, DataQuality
from tiaf.contracts.common import Metadata, NonEmptyStr, Symbol, TiafDateTime
from tiaf.data import HistoricalSeries, OHLCVBar
from tiaf.features._calculation import (
    evidence,
    evidence_status,
    source_quality,
    validate_bars,
    worst_quality,
)
from tiaf.features.enums import FeatureCategory, FeatureSourceKind, FeatureStatus, FeatureValueType
from tiaf.features.errors import FeatureParameterError
from tiaf.features.models import FeatureDefinition, FeatureRequest, FeatureResult
from tiaf.features.volatility import wilder_atr


class BenchmarkRole(StrEnum):
    """Caller-declared factual role of an explicit comparison instrument."""

    MARKET = "MARKET"
    SECTOR = "SECTOR"
    PEER = "PEER"
    CUSTOM = "CUSTOM"


class BenchmarkReference(ContractModel):
    """Provider-neutral explicit benchmark identity and caller-owned role."""

    symbol: Symbol
    role: BenchmarkRole
    exchange: NonEmptyStr | None = None
    metadata: Metadata = Field(default_factory=dict)


class RelativeStrengthContext(ContractModel):
    """Two immutable A1 contexts selected for one interval comparison."""

    context_id: NonEmptyStr
    subject_context: AnalysisContext
    benchmark_context: AnalysisContext | None
    benchmark: BenchmarkReference
    interval: NonEmptyStr
    created_at: TiafDateTime
    metadata: Metadata = Field(default_factory=dict)

    @field_validator("interval", mode="before")
    @classmethod
    def normalize_interval(cls, value: str) -> str:
        from tiaf.data import normalize_interval

        return normalize_interval(value)

    @model_validator(mode="after")
    def validate_contexts(self) -> Self:
        if self.subject_context.subject.symbol == self.benchmark.symbol:
            raise ValueError("benchmark must differ from subject")
        if self.subject_context.created_at > self.created_at:
            raise ValueError("created_at cannot predate the subject context")
        if self.benchmark_context is not None:
            if self.benchmark_context.subject.symbol != self.benchmark.symbol:
                raise ValueError("benchmark reference must match benchmark context")
            benchmark_exchange = (
                self.benchmark_context.subject.resolved_instrument.instrument.exchange
            )
            if self.benchmark.exchange is not None:
                if self.benchmark.exchange.casefold() != benchmark_exchange.casefold():
                    raise ValueError("benchmark exchange must match benchmark context")
            if self.benchmark_context.created_at > self.created_at:
                raise ValueError("created_at cannot predate the benchmark context")
        for name, context in (
            ("subject", self.subject_context),
            ("benchmark", self.benchmark_context),
        ):
            if context is not None and context.history is not None:
                if context.history.interval != self.interval:
                    raise ValueError(f"{name} history interval must match relative context")
        return self


def relative_strength_context(
    subject: AnalysisContext,
    benchmark_context: AnalysisContext | None,
    benchmark: BenchmarkReference,
    *,
    interval: str,
    context_id: str | None = None,
) -> RelativeStrengthContext:
    """Build one deterministic explicit-benchmark comparison context."""
    from tiaf.data import normalize_interval

    normalized_interval = normalize_interval(interval)
    identity = (
        f"{subject.context_id}:"
        f"{benchmark_context.context_id if benchmark_context is not None else 'missing'}:"
        f"{benchmark.symbol}:{benchmark.role.value}:{normalized_interval}"
    )
    created_at = (
        max(subject.created_at, benchmark_context.created_at)
        if benchmark_context is not None
        else subject.created_at
    )
    return RelativeStrengthContext(
        context_id=context_id or str(uuid5(NAMESPACE_URL, f"tiaf:relative:{identity}")),
        subject_context=subject,
        benchmark_context=benchmark_context,
        benchmark=benchmark,
        interval=normalized_interval,
        created_at=created_at,
    )


def _definition(
    feature_id: str,
    name: str,
    description: str,
    *,
    unit: str,
    minimum_bars: int = 2,
) -> FeatureDefinition:
    return FeatureDefinition(
        feature_id=feature_id,
        name=name,
        category=FeatureCategory.RELATIVE,
        description=description,
        value_type=FeatureValueType.FLOAT,
        unit=unit,
        required_sources=(FeatureSourceKind.HISTORY,),
        minimum_history_bars=minimum_bars,
        metadata={
            "comparison": "explicit_subject_and_benchmark",
            "alignment": "exact_latest_common_timestamp_suffix",
        },
    )


SUBJECT_RETURN = _definition(
    "relative.subject_return_percent",
    "Aligned subject return",
    "Subject percentage return over the latest exact aligned bar transitions.",
    unit="%",
)
BENCHMARK_RETURN = _definition(
    "relative.benchmark_return_percent",
    "Aligned benchmark return",
    "Benchmark percentage return over the latest exact aligned bar transitions.",
    unit="%",
)
RETURN_SPREAD = _definition(
    "relative.return_spread_percent",
    "Subject-minus-benchmark return spread",
    "Aligned subject percentage return minus aligned benchmark percentage return.",
    unit="percentage points",
)
RETURN_RATIO = _definition(
    "relative.return_ratio",
    "Subject-to-benchmark return ratio",
    "Aligned subject percentage return divided by aligned benchmark percentage return.",
    unit="ratio",
)
EXCESS_MOVE_ATR = _definition(
    "relative.excess_move_atr",
    "Return spread over subject ATR percentage",
    "Aligned return spread divided by subject Wilder ATR as a percentage of close.",
    unit="ATR",
)
STRENGTH_CONSISTENCY = _definition(
    "relative.strength_consistency",
    "Subject outperformance transition fraction",
    "Fraction of aligned transitions whose subject return exceeds benchmark return.",
    unit="fraction",
)

RELATIVE_FEATURE_DEFINITIONS = (
    SUBJECT_RETURN,
    BENCHMARK_RETURN,
    RETURN_SPREAD,
    RETURN_RATIO,
    EXCESS_MOVE_ATR,
    STRENGTH_CONSISTENCY,
)


@dataclass(frozen=True)
class _AlignedInput:
    subject: tuple[OHLCVBar, ...]
    benchmark: tuple[OHLCVBar, ...]
    subject_history: HistoricalSeries
    benchmark_history: HistoricalSeries
    status: FeatureStatus
    quality: DataQuality
    as_of: TiafDateTime
    metadata: Metadata
    warnings: tuple[str, ...]


def _bar_key(bar: OHLCVBar) -> tuple[TiafDateTime, TiafDateTime]:
    return bar.start_at, bar.end_at


def _aligned_suffix(
    subject: tuple[OHLCVBar, ...],
    benchmark: tuple[OHLCVBar, ...],
) -> tuple[tuple[OHLCVBar, ...], tuple[OHLCVBar, ...]]:
    pairs: list[tuple[OHLCVBar, OHLCVBar]] = []
    subject_index = len(subject) - 1
    benchmark_index = len(benchmark) - 1
    while subject_index >= 0 and benchmark_index >= 0:
        subject_bar = subject[subject_index]
        benchmark_bar = benchmark[benchmark_index]
        if _bar_key(subject_bar) != _bar_key(benchmark_bar):
            break
        pairs.append((subject_bar, benchmark_bar))
        subject_index -= 1
        benchmark_index -= 1
    pairs.reverse()
    return tuple(item[0] for item in pairs), tuple(item[1] for item in pairs)


def _positive_return(bars: tuple[OHLCVBar, ...]) -> float:
    base = bars[0].close
    if base <= 0:
        raise ValueError("aligned base close must be positive")
    return (bars[-1].close / base - 1) * 100


class RelativeStrengthEngine:
    """Pure deterministic calculator over a caller-built relative context."""

    _definitions = {item.feature_id: item for item in RELATIVE_FEATURE_DEFINITIONS}

    def definitions(self) -> tuple[FeatureDefinition, ...]:
        return tuple(self._definitions[key] for key in sorted(self._definitions))

    def compute_one(
        self,
        context: RelativeStrengthContext,
        request: FeatureRequest,
    ) -> FeatureResult:
        try:
            definition = self._definitions[request.feature_id]
        except KeyError as exc:
            raise FeatureParameterError(f"feature is not registered: {request.feature_id}") from exc
        if request.interval != context.interval:
            raise FeatureParameterError("relative request interval must match relative context")
        expected = (
            ("atr_period", "bars")
            if request.feature_id == EXCESS_MOVE_ATR.feature_id
            else ("bars",)
        )
        if tuple(name for name, _ in request.parameters) != expected:
            raise FeatureParameterError(
                f"feature {request.feature_id!r} requires exactly: {', '.join(expected)}"
            )
        bars = self._positive_int(request, "bars")
        atr_period = (
            self._positive_int(request, "atr_period")
            if request.feature_id == EXCESS_MOVE_ATR.feature_id
            else None
        )
        prepared, failure = self._prepare(context, request, definition, bars)
        if failure is not None:
            return failure
        assert prepared is not None
        selected_subject = prepared.subject[-(bars + 1) :]
        selected_benchmark = prepared.benchmark[-(bars + 1) :]
        try:
            subject_return = _positive_return(selected_subject)
            benchmark_return = _positive_return(selected_benchmark)
            spread = subject_return - benchmark_return
            if request.feature_id == SUBJECT_RETURN.feature_id:
                value = subject_return
            elif request.feature_id == BENCHMARK_RETURN.feature_id:
                value = benchmark_return
            elif request.feature_id == RETURN_SPREAD.feature_id:
                value = spread
            elif request.feature_id == RETURN_RATIO.feature_id:
                if benchmark_return == 0:
                    raise ZeroDivisionError("return ratio is undefined for zero benchmark return")
                value = subject_return / benchmark_return
            elif request.feature_id == STRENGTH_CONSISTENCY.feature_id:
                wins = sum(
                    (subject_bar.close / previous_subject.close - 1)
                    > (benchmark_bar.close / previous_benchmark.close - 1)
                    for previous_subject, subject_bar, previous_benchmark, benchmark_bar in zip(
                        selected_subject[:-1],
                        selected_subject[1:],
                        selected_benchmark[:-1],
                        selected_benchmark[1:],
                        strict=True,
                    )
                    if previous_subject.close > 0 and previous_benchmark.close > 0
                )
                if any(
                    bar.close <= 0
                    for bar in (*selected_subject[:-1], *selected_benchmark[:-1])
                ):
                    raise ValueError("transition base closes must be positive")
                value = wins / bars
            else:
                assert atr_period is not None
                subject_bars = prepared.subject_history.bars
                if len(subject_bars) < atr_period + 1:
                    return self._result(
                        context,
                        request,
                        definition,
                        status=FeatureStatus.INSUFFICIENT_DATA,
                        quality=prepared.quality,
                        as_of=prepared.as_of,
                        warnings=(
                            f"subject ATR requires {atr_period + 1} bars; "
                            f"available {len(subject_bars)}",
                        ),
                        metadata=prepared.metadata,
                    )
                atr = wilder_atr(subject_bars, atr_period)
                latest_close = selected_subject[-1].close
                atr_percent = atr / latest_close * 100 if latest_close > 0 else 0
                if atr_percent == 0:
                    raise ZeroDivisionError("excess move is undefined for zero subject ATR percent")
                value = spread / atr_percent
        except ZeroDivisionError as exc:
            return self._result(
                context,
                request,
                definition,
                status=FeatureStatus.FAILED,
                quality=prepared.quality,
                as_of=prepared.as_of,
                warnings=(str(exc),),
                metadata=prepared.metadata,
            )
        except ValueError as exc:
            return self._result(
                context,
                request,
                definition,
                status=FeatureStatus.FAILED,
                quality=prepared.quality,
                as_of=prepared.as_of,
                warnings=(str(exc),),
                metadata=prepared.metadata,
            )
        if not math.isfinite(value):
            return self._result(
                context,
                request,
                definition,
                status=FeatureStatus.FAILED,
                quality=prepared.quality,
                as_of=prepared.as_of,
                warnings=("relative calculation produced a non-finite value",),
                metadata=prepared.metadata,
            )
        return self._result(
            context,
            request,
            definition,
            status=prepared.status,
            value=float(value),
            quality=prepared.quality,
            as_of=prepared.as_of,
            lookback=bars + 1,
            metadata=prepared.metadata,
        )

    @staticmethod
    def _positive_int(request: FeatureRequest, name: str) -> int:
        value = request.parameter(name)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise FeatureParameterError(f"{name} must be a positive integer")
        return value

    def _prepare(
        self,
        context: RelativeStrengthContext,
        request: FeatureRequest,
        definition: FeatureDefinition,
        bars: int,
    ) -> tuple[_AlignedInput | None, FeatureResult | None]:
        subject = context.subject_context
        benchmark = context.benchmark_context
        if benchmark is None:
            return None, self._result(
                context,
                request,
                definition,
                status=FeatureStatus.INSUFFICIENT_DATA,
                quality=DataQuality.UNAVAILABLE,
                as_of=context.created_at,
                warnings=("benchmark context is unavailable",),
            )
        subject_descriptor = evidence(subject, "history")
        benchmark_descriptor = evidence(benchmark, "history")
        subject_status = evidence_status(
            subject_descriptor,
            subject.history.quality if subject.history is not None else None,
        )
        benchmark_status = evidence_status(
            benchmark_descriptor,
            benchmark.history.quality if benchmark.history is not None else None,
        )
        quality = worst_quality(
            source_quality(
                subject_descriptor,
                subject.history.quality if subject.history is not None else None,
            ),
            source_quality(
                benchmark_descriptor,
                benchmark.history.quality if benchmark.history is not None else None,
            ),
        )
        as_of = min(subject.created_at, benchmark.created_at)
        metadata = self._metadata(context, None, None)
        if subject_status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
            return None, self._result(
                context, request, definition, status=subject_status, quality=quality,
                as_of=as_of, warnings=("subject history is unavailable",), metadata=metadata,
            )
        if benchmark_status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
            return None, self._result(
                context, request, definition, status=benchmark_status, quality=quality,
                as_of=as_of, warnings=("benchmark history is unavailable",), metadata=metadata,
            )
        assert subject.history is not None and benchmark.history is not None
        for label, history in (("subject", subject.history), ("benchmark", benchmark.history)):
            malformed = validate_bars(history.bars)
            if malformed is not None:
                return None, self._result(
                    context, request, definition, status=FeatureStatus.FAILED,
                    quality=quality, as_of=as_of,
                    warnings=(f"{label} {malformed}",), metadata=metadata,
                )
        aligned_subject, aligned_benchmark = _aligned_suffix(
            subject.history.bars, benchmark.history.bars
        )
        if len(aligned_subject) < bars + 1:
            latest_subject = (
                subject.history.bars[-1].end_at
                if subject.history.bars
                else subject.created_at
            )
            latest_benchmark = (
                benchmark.history.bars[-1].end_at
                if benchmark.history.bars
                else benchmark.created_at
            )
            return None, self._result(
                context, request, definition, status=FeatureStatus.INSUFFICIENT_DATA,
                quality=quality, as_of=min(latest_subject, latest_benchmark),
                warnings=(
                    f"requires {bars + 1} exact aligned suffix bars; "
                    f"available {len(aligned_subject)}",
                ), metadata=self._metadata(context, latest_subject, latest_benchmark),
            )
        as_of = aligned_subject[-1].end_at
        status = (
            FeatureStatus.PARTIAL
            if FeatureStatus.PARTIAL in {subject_status, benchmark_status}
            or quality is not DataQuality.GOOD
            else FeatureStatus.AVAILABLE
        )
        return _AlignedInput(
            subject=aligned_subject,
            benchmark=aligned_benchmark,
            subject_history=subject.history,
            benchmark_history=benchmark.history,
            status=status,
            quality=quality,
            as_of=as_of,
            metadata=self._metadata(context, as_of, as_of),
            warnings=(),
        ), None

    @staticmethod
    def _metadata(
        context: RelativeStrengthContext,
        subject_as_of: TiafDateTime | None,
        benchmark_as_of: TiafDateTime | None,
    ) -> Metadata:
        return {
            "subject_context_id": context.subject_context.context_id,
            "subject_symbol": context.subject_context.subject.symbol,
            "benchmark_context_id": (
                context.benchmark_context.context_id
                if context.benchmark_context is not None
                else None
            ),
            "benchmark_symbol": context.benchmark.symbol,
            "benchmark_role": context.benchmark.role.value,
            "benchmark_exchange": context.benchmark.exchange,
            "interval": context.interval,
            "alignment_semantics": "exact_latest_common_timestamp_suffix",
            "subject_as_of": subject_as_of.isoformat() if subject_as_of else None,
            "benchmark_as_of": benchmark_as_of.isoformat() if benchmark_as_of else None,
        }

    @staticmethod
    def _result(
        context: RelativeStrengthContext,
        request: FeatureRequest,
        definition: FeatureDefinition,
        *,
        status: FeatureStatus,
        quality: DataQuality,
        as_of: TiafDateTime,
        value: float | None = None,
        warnings: tuple[str, ...] = (),
        lookback: int | None = None,
        metadata: Metadata | None = None,
    ) -> FeatureResult:
        return FeatureResult(
            definition=definition,
            request=request,
            status=status,
            value=value,
            unit=definition.unit,
            as_of=as_of,
            source_context_id=context.context_id,
            subject_symbol=context.subject_context.subject.symbol,
            source_evidence=("subject_history", "benchmark_history"),
            source_observed_at=as_of,
            quality=quality,
            lookback_bars_used=lookback,
            warnings=warnings,
            metadata=metadata or RelativeStrengthEngine._metadata(context, None, None),
        )
