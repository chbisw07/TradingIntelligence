"""Shared pure preparation and numerical guards for A2 feature calculators."""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from tiaf.context import AnalysisContext, EvidenceDescriptor, EvidenceStatus
from tiaf.contracts import DataQuality
from tiaf.contracts.common import Metadata
from tiaf.data import HistoricalSeries, OHLCVBar, QuoteSnapshot
from tiaf.features.enums import FeatureStatus
from tiaf.features.errors import FeatureParameterError
from tiaf.features.models import (
    FeatureDefinition,
    FeatureRequest,
    FeatureResult,
    JSONScalar,
)

_USABLE_EVIDENCE = {
    EvidenceStatus.AVAILABLE,
    EvidenceStatus.PARTIAL,
    EvidenceStatus.STALE,
}
_QUALITY_RANK = {
    DataQuality.GOOD: 0,
    DataQuality.PARTIAL: 1,
    DataQuality.DEGRADED: 2,
    DataQuality.UNAVAILABLE: 3,
}


@dataclass(frozen=True)
class HistoryInput:
    """Validated history and its market-time provenance."""

    history: HistoricalSeries
    descriptor: EvidenceDescriptor
    status: FeatureStatus
    quality: DataQuality
    as_of: datetime
    metadata: Metadata
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class MixedInput:
    """Validated quote/history input with limiting-time provenance."""

    quote: QuoteSnapshot
    history: HistoricalSeries
    status: FeatureStatus
    quality: DataQuality
    as_of: datetime
    metadata: Metadata
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class PreviousCloseInput:
    """Canonical previous-session close resolution and actual provenance."""

    value: float | None
    quote: QuoteSnapshot | None
    status: FeatureStatus
    quality: DataQuality
    as_of: datetime
    source_evidence: tuple[str, ...]
    lookback_bars_used: int | None
    metadata: Metadata
    warnings: tuple[str, ...]


def evidence(context: AnalysisContext, name: str) -> EvidenceDescriptor | None:
    """Return one named A1 evidence descriptor without acquiring anything."""
    return next((item for item in context.evidence if item.evidence_name == name), None)


def evidence_status(
    descriptor: EvidenceDescriptor | None,
    fallback_quality: DataQuality | None = None,
) -> FeatureStatus:
    """Translate A1 evidence availability without upgrading source quality."""
    if descriptor is None or descriptor.status is EvidenceStatus.NOT_REQUESTED:
        return FeatureStatus.NOT_APPLICABLE
    if descriptor.status not in _USABLE_EVIDENCE:
        return FeatureStatus.INSUFFICIENT_DATA
    quality = source_quality(descriptor, fallback_quality)
    if quality is DataQuality.UNAVAILABLE:
        return FeatureStatus.INSUFFICIENT_DATA
    if descriptor.status in {EvidenceStatus.PARTIAL, EvidenceStatus.STALE}:
        return FeatureStatus.PARTIAL
    if quality is not DataQuality.GOOD:
        return FeatureStatus.PARTIAL
    return FeatureStatus.AVAILABLE


def source_quality(
    descriptor: EvidenceDescriptor | None,
    fallback: DataQuality | None = None,
) -> DataQuality:
    """Select explicit evidence quality before nested factual quality."""
    if descriptor is not None and descriptor.quality is not None:
        return descriptor.quality
    return fallback or DataQuality.UNAVAILABLE


def worst_quality(*qualities: DataQuality) -> DataQuality:
    """Return the deterministic least-usable source quality."""
    return max(qualities, key=_QUALITY_RANK.__getitem__)


def evidence_warnings(descriptor: EvidenceDescriptor | None) -> tuple[str, ...]:
    """Expose non-available evidence state without provider payloads."""
    if descriptor is None:
        return ("source evidence descriptor is absent",)
    if descriptor.status is EvidenceStatus.AVAILABLE:
        return ()
    return (f"source evidence {descriptor.evidence_name} is {descriptor.status.value}",)


def validate_bars(bars: tuple[OHLCVBar, ...]) -> str | None:
    """Defend calculations if an invalid model was constructed without validation."""
    starts = tuple(bar.start_at for bar in bars)
    if len(starts) != len(set(starts)):
        return "history contains duplicate bar timestamps"
    if starts != tuple(sorted(starts)):
        return "history bars are not chronological"
    for bar in bars:
        prices = (bar.open, bar.high, bar.low, bar.close)
        if any(not math.isfinite(value) or value < 0 for value in prices):
            return "history contains non-finite or negative OHLC values"
        if bar.high < max(bar.open, bar.close, bar.low):
            return "history contains malformed OHLC high envelope"
        if bar.low > min(bar.open, bar.close, bar.high):
            return "history contains malformed OHLC low envelope"
    return None


def resolve_previous_close(
    context: AnalysisContext,
    request: FeatureRequest,
) -> PreviousCloseInput:
    """Resolve previous session close from quote, then a session-aware daily fallback."""
    quote_descriptor = evidence(context, "quote")
    quote_quality = source_quality(
        quote_descriptor,
        context.quote.quality if context.quote is not None else None,
    )
    quote_status = evidence_status(
        quote_descriptor,
        context.quote.quality if context.quote is not None else None,
    )
    if request.interval != "1d":
        return PreviousCloseInput(
            value=None,
            quote=context.quote,
            status=FeatureStatus.NOT_APPLICABLE,
            quality=quote_quality,
            as_of=context.quote.observed_at if context.quote else context.created_at,
            source_evidence=("quote",),
            lookback_bars_used=None,
            metadata={"previous_close_source": "unresolved"},
            warnings=("previous-session close requires interval 1d",),
        )
    if (
        quote_status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
        or context.quote is None
    ):
        return PreviousCloseInput(
            value=None,
            quote=context.quote,
            status=quote_status,
            quality=quote_quality,
            as_of=(
                quote_descriptor.source_observed_at
                if quote_descriptor is not None
                and quote_descriptor.source_observed_at is not None
                else context.created_at
            ),
            source_evidence=("quote",),
            lookback_bars_used=None,
            metadata={"previous_close_source": "unresolved"},
            warnings=evidence_warnings(quote_descriptor),
        )

    previous_close = context.quote.previous_close
    if (
        previous_close is not None
        and math.isfinite(previous_close)
        and previous_close > 0
    ):
        return PreviousCloseInput(
            value=float(previous_close),
            quote=context.quote,
            status=quote_status,
            quality=quote_quality,
            as_of=context.quote.observed_at,
            source_evidence=("quote",),
            lookback_bars_used=None,
            metadata={
                "previous_close_source": "quote.previous_close",
                "source_time_semantics": "quote_market_observation",
                "quote_observed_at": context.quote.observed_at.isoformat(),
            },
            warnings=evidence_warnings(quote_descriptor),
        )

    if context.quote.metadata.get("observed_at_source") == "retrieval_time":
        return PreviousCloseInput(
            value=None,
            quote=context.quote,
            status=FeatureStatus.INSUFFICIENT_DATA,
            quality=quote_quality,
            as_of=context.quote.observed_at,
            source_evidence=("quote",),
            lookback_bars_used=None,
            metadata={
                "previous_close_source": "unresolved",
                "source_time_semantics": "quote_retrieval_time",
                "quote_observed_at": context.quote.observed_at.isoformat(),
            },
            warnings=(
                "quote previous_close is unavailable or invalid and retrieval-time "
                "observation cannot identify the represented trading session",
            ),
        )

    history_descriptor = evidence(context, "history")
    history_quality = source_quality(
        history_descriptor,
        context.history.quality if context.history is not None else None,
    )
    quality = worst_quality(quote_quality, history_quality)
    history_status = evidence_status(
        history_descriptor,
        context.history.quality if context.history is not None else None,
    )
    fallback_prefix = (
        "quote previous_close is unavailable or invalid; "
        "daily history fallback was required"
    )
    if (
        history_status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
        or context.history is None
    ):
        return PreviousCloseInput(
            value=None,
            quote=context.quote,
            status=FeatureStatus.INSUFFICIENT_DATA,
            quality=quality,
            as_of=context.quote.observed_at,
            source_evidence=("quote", "history"),
            lookback_bars_used=None,
            metadata={
                "previous_close_source": "unresolved",
                "quote_observed_at": context.quote.observed_at.isoformat(),
            },
            warnings=(fallback_prefix,) + evidence_warnings(history_descriptor),
        )
    if context.history.interval != "1d":
        return PreviousCloseInput(
            value=None,
            quote=context.quote,
            status=FeatureStatus.INSUFFICIENT_DATA,
            quality=quality,
            as_of=min(context.quote.observed_at, context.history.observed_at),
            source_evidence=("quote", "history"),
            lookback_bars_used=None,
            metadata={"previous_close_source": "unresolved"},
            warnings=(fallback_prefix, "historical fallback requires daily history"),
        )
    bars = context.history.bars
    malformed = validate_bars(bars)
    if malformed is not None:
        return PreviousCloseInput(
            value=None,
            quote=context.quote,
            status=FeatureStatus.FAILED,
            quality=quality,
            as_of=context.quote.observed_at,
            source_evidence=("quote", "history"),
            lookback_bars_used=None,
            metadata={"previous_close_source": "unresolved"},
            warnings=(fallback_prefix, malformed),
        )
    if not bars:
        return PreviousCloseInput(
            value=None,
            quote=context.quote,
            status=FeatureStatus.INSUFFICIENT_DATA,
            quality=quality,
            as_of=context.quote.observed_at,
            source_evidence=("quote", "history"),
            lookback_bars_used=None,
            metadata={"previous_close_source": "unresolved"},
            warnings=(fallback_prefix, "daily history contains no bars"),
        )

    quote_session_date = context.quote.observed_at.date()
    latest_session_date = bars[-1].start_at.date()
    if latest_session_date > quote_session_date:
        return PreviousCloseInput(
            value=None,
            quote=context.quote,
            status=FeatureStatus.FAILED,
            quality=quality,
            as_of=context.quote.observed_at,
            source_evidence=("quote", "history"),
            lookback_bars_used=None,
            metadata={"previous_close_source": "unresolved"},
            warnings=(fallback_prefix, "daily history is later than quote observation"),
        )
    includes_quote_session = latest_session_date == quote_session_date
    if includes_quote_session and len(bars) < 2:
        return PreviousCloseInput(
            value=None,
            quote=context.quote,
            status=FeatureStatus.INSUFFICIENT_DATA,
            quality=quality,
            as_of=min(context.quote.observed_at, bars[-1].end_at),
            source_evidence=("quote", "history"),
            lookback_bars_used=1,
            metadata={"previous_close_source": "unresolved"},
            warnings=(
                fallback_prefix,
                "daily history includes the quote session but no preceding bar",
            ),
        )
    selected_index = -2 if includes_quote_session else -1
    selected = bars[selected_index]
    lookback = 2 if includes_quote_session else 1
    if selected.close <= 0:
        return PreviousCloseInput(
            value=None,
            quote=context.quote,
            status=FeatureStatus.FAILED,
            quality=quality,
            as_of=min(context.quote.observed_at, selected.end_at),
            source_evidence=("quote", "history"),
            lookback_bars_used=lookback,
            metadata={"previous_close_source": "history_session_fallback"},
            warnings=(fallback_prefix, "historical fallback close must be positive"),
        )
    status = (
        FeatureStatus.PARTIAL
        if FeatureStatus.PARTIAL in {quote_status, history_status}
        or quality is not DataQuality.GOOD
        else FeatureStatus.AVAILABLE
    )
    as_of = min(context.quote.observed_at, selected.end_at)
    metadata: Metadata = {
        "previous_close_source": "history_session_fallback",
        "source_time_semantics": "previous_daily_session_close",
        "quote_observed_at": context.quote.observed_at.isoformat(),
        "history_selected_bar_start_at": selected.start_at.isoformat(),
        "history_selected_bar_end_at": selected.end_at.isoformat(),
        "history_includes_quote_session": includes_quote_session,
    }
    if history_descriptor is not None and history_descriptor.source_observed_at:
        metadata["history_acquired_at"] = (
            history_descriptor.source_observed_at.isoformat()
        )
    return PreviousCloseInput(
        value=float(selected.close),
        quote=context.quote,
        status=status,
        quality=quality,
        as_of=as_of,
        source_evidence=("quote", "history"),
        lookback_bars_used=lookback,
        metadata=metadata,
        warnings=(
            "quote previous_close unavailable; used session-aware daily history fallback",
        )
        + evidence_warnings(quote_descriptor)
        + evidence_warnings(history_descriptor),
    )


def positive_int_parameter(request: FeatureRequest, name: str) -> int:
    """Read one strictly positive integer parameter."""
    value: JSONScalar = request.parameter(name)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise FeatureParameterError(f"{name} must be a positive integer")
    return value


def positive_number_parameter(request: FeatureRequest, name: str) -> float:
    """Read one finite strictly positive numeric parameter."""
    value: JSONScalar = request.parameter(name)
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise FeatureParameterError(f"{name} must be a positive finite number")
    return float(value)


class A22Calculator(ABC):
    """Base for A2.2 calculators with stable request and result handling."""

    _definition: FeatureDefinition

    def definition(self) -> FeatureDefinition:
        return self._definition

    def _validate_request(
        self,
        request: FeatureRequest,
        *,
        parameter_names: tuple[str, ...] = (),
    ) -> None:
        if request.feature_id != self._definition.feature_id:
            raise FeatureParameterError(
                f"calculator {self._definition.feature_id!r} cannot compute "
                f"{request.feature_id!r}"
            )
        actual = tuple(name for name, _ in request.parameters)
        if actual != tuple(sorted(parameter_names)):
            if parameter_names:
                joined = ", ".join(parameter_names)
                raise FeatureParameterError(
                    f"feature {request.feature_id!r} requires exactly: {joined}"
                )
            raise FeatureParameterError(
                f"feature {request.feature_id!r} does not accept parameters"
            )

    def _result(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
        *,
        status: FeatureStatus,
        value: int | float | None,
        quality: DataQuality,
        as_of: datetime,
        source_evidence: tuple[str, ...],
        source_observed_at: datetime | None,
        lookback_bars_used: int | None = None,
        warnings: tuple[str, ...] = (),
        metadata: Metadata | None = None,
    ) -> FeatureResult:
        if value is not None and not math.isfinite(value):
            status = FeatureStatus.FAILED
            value = None
            warnings += ("calculation produced a non-finite value",)
        return FeatureResult(
            definition=self._definition,
            request=request,
            status=status,
            value=value,
            unit=self._definition.unit,
            as_of=as_of,
            source_context_id=context.context_id,
            subject_symbol=context.subject.symbol,
            source_evidence=source_evidence,
            source_observed_at=source_observed_at,
            quality=quality,
            lookback_bars_used=lookback_bars_used,
            warnings=warnings,
            metadata=metadata or {},
        )

    def _history_result(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
        prepared: HistoryInput,
        *,
        status: FeatureStatus | None = None,
        value: int | float | None,
        lookback_bars_used: int | None = None,
        warnings: tuple[str, ...] = (),
    ) -> FeatureResult:
        return self._result(
            context,
            request,
            status=status or prepared.status,
            value=value,
            quality=prepared.quality,
            as_of=prepared.as_of,
            source_evidence=("history",),
            source_observed_at=prepared.as_of,
            lookback_bars_used=lookback_bars_used,
            warnings=prepared.warnings + warnings,
            metadata=prepared.metadata,
        )

    def _mixed_result(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
        prepared: MixedInput,
        *,
        status: FeatureStatus | None = None,
        value: int | float | None,
        lookback_bars_used: int | None = None,
        warnings: tuple[str, ...] = (),
    ) -> FeatureResult:
        return self._result(
            context,
            request,
            status=status or prepared.status,
            value=value,
            quality=prepared.quality,
            as_of=prepared.as_of,
            source_evidence=("quote", "history"),
            source_observed_at=prepared.as_of,
            lookback_bars_used=lookback_bars_used,
            warnings=prepared.warnings + warnings,
            metadata=prepared.metadata,
        )

    def _prepare_history(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
        *,
        minimum_bars: int,
    ) -> tuple[HistoryInput | None, FeatureResult | None]:
        if request.interval is None:
            raise FeatureParameterError(
                f"feature {request.feature_id!r} requires an interval"
            )
        descriptor = evidence(context, "history")
        fallback_quality = context.history.quality if context.history is not None else None
        quality = source_quality(descriptor, fallback_quality)
        status = evidence_status(descriptor, fallback_quality)
        if status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
            return None, self._result(
                context,
                request,
                status=status,
                value=None,
                quality=quality,
                as_of=(
                    descriptor.source_observed_at
                    if descriptor is not None and descriptor.source_observed_at is not None
                    else context.created_at
                ),
                source_evidence=("history",),
                source_observed_at=(
                    descriptor.source_observed_at if descriptor is not None else None
                ),
                warnings=evidence_warnings(descriptor),
            )
        assert context.history is not None
        bars = context.history.bars
        market_as_of = bars[-1].end_at if bars else context.history.observed_at
        market_metadata: Metadata = {
            "source_time_semantics": "latest_history_bar_end",
        }
        if bars:
            market_metadata.update(
                {
                    "latest_bar_start_at": bars[-1].start_at.isoformat(),
                    "latest_bar_end_at": bars[-1].end_at.isoformat(),
                }
            )
        if descriptor is not None and descriptor.source_observed_at is not None:
            market_metadata["history_acquired_at"] = (
                descriptor.source_observed_at.isoformat()
            )
        if context.history.interval != request.interval:
            warning = (
                f"requested interval {request.interval} does not match "
                f"context history interval {context.history.interval}"
            )
            return None, self._result(
                context,
                request,
                status=FeatureStatus.NOT_APPLICABLE,
                value=None,
                quality=quality,
                as_of=market_as_of,
                source_evidence=("history",),
                source_observed_at=market_as_of,
                warnings=(warning,),
                metadata=market_metadata,
            )
        if (
            self._definition.supported_intervals is not None
            and request.interval not in self._definition.supported_intervals
        ):
            return None, self._result(
                context,
                request,
                status=FeatureStatus.NOT_APPLICABLE,
                value=None,
                quality=quality,
                as_of=market_as_of,
                source_evidence=("history",),
                source_observed_at=market_as_of,
                warnings=(f"interval {request.interval} is not supported",),
                metadata=market_metadata,
            )
        if len(bars) < minimum_bars:
            return None, self._result(
                context,
                request,
                status=FeatureStatus.INSUFFICIENT_DATA,
                value=None,
                quality=quality,
                as_of=market_as_of,
                source_evidence=("history",),
                source_observed_at=market_as_of,
                warnings=(
                    f"requires {minimum_bars} history bars; available {len(bars)}",
                ),
                metadata=market_metadata,
            )
        malformed = validate_bars(bars)
        if malformed is not None:
            return None, self._result(
                context,
                request,
                status=FeatureStatus.FAILED,
                value=None,
                quality=quality,
                as_of=market_as_of,
                source_evidence=("history",),
                source_observed_at=market_as_of,
                warnings=(malformed,),
                metadata=market_metadata,
            )
        assert descriptor is not None
        latest = bars[-1]
        return (
            HistoryInput(
                history=context.history,
                descriptor=descriptor,
                status=status,
                quality=quality,
                as_of=latest.end_at,
                metadata=market_metadata,
                warnings=evidence_warnings(descriptor),
            ),
            None,
        )

    def _prepare_mixed(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
        *,
        minimum_history_bars: int,
    ) -> tuple[MixedInput | None, FeatureResult | None]:
        quote_descriptor = evidence(context, "quote")
        quote_quality = source_quality(
            quote_descriptor,
            context.quote.quality if context.quote is not None else None,
        )
        quote_status = evidence_status(
            quote_descriptor,
            context.quote.quality if context.quote is not None else None,
        )
        history_input, failure = self._prepare_history(
            context,
            request,
            minimum_bars=minimum_history_bars,
        )
        if failure is not None:
            combined_status = (
                FeatureStatus.NOT_APPLICABLE
                if FeatureStatus.NOT_APPLICABLE in {quote_status, failure.status}
                else failure.status
            )
            mixed_as_of = (
                min(context.quote.observed_at, failure.as_of)
                if context.quote is not None
                else failure.as_of
            )
            metadata = dict(failure.metadata)
            if context.quote is not None:
                metadata["quote_observed_at"] = context.quote.observed_at.isoformat()
            return None, failure.model_copy(
                update={
                    "status": combined_status,
                    "quality": worst_quality(quote_quality, failure.quality),
                    "as_of": mixed_as_of,
                    "source_evidence": ("quote", "history"),
                    "source_observed_at": mixed_as_of,
                    "warnings": evidence_warnings(quote_descriptor) + failure.warnings,
                    "metadata": metadata,
                }
            )
        assert history_input is not None
        quality = worst_quality(quote_quality, history_input.quality)
        if quote_status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
            mixed_as_of = (
                min(context.quote.observed_at, history_input.as_of)
                if context.quote is not None
                else history_input.as_of
            )
            metadata = dict(history_input.metadata)
            if context.quote is not None:
                metadata.update(
                    {
                        "source_time_semantics": "oldest_mixed_market_observation",
                        "quote_observed_at": context.quote.observed_at.isoformat(),
                        "history_latest_bar_end_at": history_input.as_of.isoformat(),
                    }
                )
            return None, self._result(
                context,
                request,
                status=quote_status,
                value=None,
                quality=quality,
                as_of=mixed_as_of,
                source_evidence=("quote", "history"),
                source_observed_at=mixed_as_of,
                warnings=evidence_warnings(quote_descriptor) + history_input.warnings,
                metadata=metadata,
            )
        assert context.quote is not None
        limiting_time = min(context.quote.observed_at, history_input.as_of)
        metadata = {
            **history_input.metadata,
            "source_time_semantics": "oldest_mixed_market_observation",
            "quote_observed_at": context.quote.observed_at.isoformat(),
            "history_latest_bar_end_at": history_input.as_of.isoformat(),
        }
        if not math.isfinite(context.quote.ltp) or context.quote.ltp < 0:
            return None, self._result(
                context,
                request,
                status=FeatureStatus.FAILED,
                value=None,
                quality=quality,
                as_of=limiting_time,
                source_evidence=("quote", "history"),
                source_observed_at=limiting_time,
                warnings=("quote contains a non-finite or negative current price",),
                metadata=metadata,
            )
        status = (
            FeatureStatus.PARTIAL
            if FeatureStatus.PARTIAL in {quote_status, history_input.status}
            or quality is not DataQuality.GOOD
            else FeatureStatus.AVAILABLE
        )
        return (
            MixedInput(
                quote=context.quote,
                history=history_input.history,
                status=status,
                quality=quality,
                as_of=limiting_time,
                metadata=metadata,
                warnings=(
                    evidence_warnings(quote_descriptor) + history_input.warnings
                ),
            ),
            None,
        )

    @abstractmethod
    def compute(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
    ) -> FeatureResult:
        """Compute one deterministic feature from the supplied context."""
