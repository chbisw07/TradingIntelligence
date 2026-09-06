"""Small pure calculators proving the A2 deterministic feature boundary."""

from abc import ABC, abstractmethod

from tiaf.context import AnalysisContext, EvidenceDescriptor, EvidenceStatus
from tiaf.contracts import DataQuality
from tiaf.features.definitions import (
    ABSOLUTE_RETURN,
    CURRENT_PRICE,
    HIGH_LOW_RANGE_PERCENT,
    HISTORY_BAR_COUNT,
    HISTORY_FIRST_CLOSE,
    HISTORY_LAST_CLOSE,
    PERCENT_RETURN,
)
from tiaf.features.enums import FeatureStatus
from tiaf.features.errors import FeatureParameterError
from tiaf.features.models import FeatureDefinition, FeatureRequest, FeatureResult, JSONScalar
from tiaf.features.registry import FeatureCalculator

_USABLE_EVIDENCE = {
    EvidenceStatus.AVAILABLE,
    EvidenceStatus.PARTIAL,
    EvidenceStatus.STALE,
}


def _evidence(context: AnalysisContext, name: str) -> EvidenceDescriptor | None:
    return next(
        (item for item in context.evidence if item.evidence_name == name),
        None,
    )


def _source_status(descriptor: EvidenceDescriptor | None) -> FeatureStatus:
    if descriptor is None or descriptor.status is EvidenceStatus.NOT_REQUESTED:
        return FeatureStatus.NOT_APPLICABLE
    if descriptor.status not in _USABLE_EVIDENCE:
        return FeatureStatus.INSUFFICIENT_DATA
    if descriptor.status in {EvidenceStatus.PARTIAL, EvidenceStatus.STALE}:
        return FeatureStatus.PARTIAL
    return FeatureStatus.AVAILABLE


def _quality(
    descriptor: EvidenceDescriptor | None,
    fallback: DataQuality | None = None,
) -> DataQuality:
    if descriptor is not None and descriptor.quality is not None:
        return descriptor.quality
    return fallback or DataQuality.UNAVAILABLE


def _warnings(descriptor: EvidenceDescriptor | None) -> tuple[str, ...]:
    if descriptor is None:
        return ("source evidence descriptor is absent",)
    if descriptor.status is EvidenceStatus.AVAILABLE:
        return ()
    return (f"source evidence {descriptor.evidence_name} is {descriptor.status.value}",)


def _result(
    definition: FeatureDefinition,
    request: FeatureRequest,
    context: AnalysisContext,
    descriptor: EvidenceDescriptor | None,
    *,
    status: FeatureStatus,
    value: float | int | None,
    source_name: str,
    fallback_quality: DataQuality | None = None,
    lookback_bars_used: int | None = None,
    warnings: tuple[str, ...] = (),
) -> FeatureResult:
    source_observed_at = (
        descriptor.source_observed_at if descriptor is not None else None
    )
    return FeatureResult(
        definition=definition,
        request=request,
        status=status,
        value=value,
        unit=definition.unit,
        as_of=source_observed_at or context.created_at,
        source_context_id=context.context_id,
        subject_symbol=context.subject.symbol,
        source_evidence=(source_name,),
        source_observed_at=source_observed_at,
        quality=_quality(descriptor, fallback_quality),
        lookback_bars_used=lookback_bars_used,
        warnings=warnings,
    )


def _require_no_parameters(request: FeatureRequest) -> None:
    if request.parameters:
        raise FeatureParameterError(
            f"feature {request.feature_id!r} does not accept parameters"
        )


def _require_no_interval(request: FeatureRequest) -> None:
    if request.interval is not None:
        raise FeatureParameterError(
            f"feature {request.feature_id!r} does not accept an interval"
        )


def _history_interval(context: AnalysisContext, request: FeatureRequest) -> bool:
    if request.interval is None:
        raise FeatureParameterError(
            f"feature {request.feature_id!r} requires an interval"
        )
    return context.history is not None and context.history.interval == request.interval


def _bars(request: FeatureRequest) -> int:
    if tuple(name for name, _ in request.parameters) != ("bars",):
        raise FeatureParameterError(
            f"feature {request.feature_id!r} requires exactly the bars parameter"
        )
    value: JSONScalar = request.parameter("bars")
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise FeatureParameterError("bars must be a positive integer")
    return value


class _BaseCalculator(ABC):
    _definition: FeatureDefinition

    def definition(self) -> FeatureDefinition:
        return self._definition

    def _validate_request(self, request: FeatureRequest) -> None:
        if request.feature_id != self._definition.feature_id:
            raise FeatureParameterError(
                f"calculator {self._definition.feature_id!r} cannot compute "
                f"{request.feature_id!r}"
            )

    @abstractmethod
    def compute(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
    ) -> FeatureResult:
        """Compute one feature from context only."""


class CurrentPriceCalculator(_BaseCalculator):
    _definition = CURRENT_PRICE

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request)
        _require_no_parameters(request)
        _require_no_interval(request)
        descriptor = _evidence(context, "quote")
        status = _source_status(descriptor)
        quote = context.quote
        if status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL} or quote is None:
            return _result(
                self._definition,
                request,
                context,
                descriptor,
                status=status,
                value=None,
                source_name="quote",
                warnings=_warnings(descriptor),
            )
        return _result(
            self._definition,
            request,
            context,
            descriptor,
            status=status,
            value=float(quote.ltp),
            source_name="quote",
            fallback_quality=quote.quality,
            warnings=_warnings(descriptor),
        )


class _HistoryCalculator(_BaseCalculator):
    def _history_state(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
    ) -> tuple[EvidenceDescriptor | None, FeatureStatus]:
        descriptor = _evidence(context, "history")
        status = _source_status(descriptor)
        if status in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL} and not _history_interval(
            context, request
        ):
            return descriptor, FeatureStatus.NOT_APPLICABLE
        if request.interval is None:
            _history_interval(context, request)
        return descriptor, status

    def _unavailable(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
        descriptor: EvidenceDescriptor | None,
        status: FeatureStatus,
    ) -> FeatureResult:
        warnings = _warnings(descriptor)
        if (
            status is FeatureStatus.NOT_APPLICABLE
            and context.history is not None
            and request.interval is not None
            and context.history.interval != request.interval
        ):
            warnings += (
                f"requested interval {request.interval} does not match "
                f"context history interval {context.history.interval}",
            )
        return _result(
            self._definition,
            request,
            context,
            descriptor,
            status=status,
            value=None,
            source_name="history",
            fallback_quality=(
                context.history.quality if context.history is not None else None
            ),
            warnings=warnings,
        )


class HistoryBarCountCalculator(_HistoryCalculator):
    _definition = HISTORY_BAR_COUNT

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request)
        _require_no_parameters(request)
        descriptor, status = self._history_state(context, request)
        if status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
            return self._unavailable(context, request, descriptor, status)
        assert context.history is not None
        count = len(context.history.bars)
        return _result(
            self._definition,
            request,
            context,
            descriptor,
            status=status,
            value=count,
            source_name="history",
            fallback_quality=context.history.quality,
            lookback_bars_used=count,
            warnings=_warnings(descriptor),
        )


class _CloseCalculator(_HistoryCalculator):
    first: bool

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request)
        _require_no_parameters(request)
        descriptor, status = self._history_state(context, request)
        if status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
            return self._unavailable(context, request, descriptor, status)
        assert context.history is not None
        if not context.history.bars:
            return _result(
                self._definition,
                request,
                context,
                descriptor,
                status=FeatureStatus.INSUFFICIENT_DATA,
                value=None,
                source_name="history",
                fallback_quality=context.history.quality,
                warnings=("requires 1 history bar; available 0",),
            )
        bar = context.history.bars[0] if self.first else context.history.bars[-1]
        return _result(
            self._definition,
            request,
            context,
            descriptor,
            status=status,
            value=float(bar.close),
            source_name="history",
            fallback_quality=context.history.quality,
            lookback_bars_used=1,
            warnings=_warnings(descriptor),
        )


class HistoryFirstCloseCalculator(_CloseCalculator):
    _definition = HISTORY_FIRST_CLOSE
    first = True


class HistoryLastCloseCalculator(_CloseCalculator):
    _definition = HISTORY_LAST_CLOSE
    first = False


class _BarsCalculator(_HistoryCalculator):
    def _prepared(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
        *,
        required_count: int,
    ) -> tuple[EvidenceDescriptor | None, FeatureStatus, int, bool]:
        self._validate_request(request)
        bars = _bars(request)
        descriptor, status = self._history_state(context, request)
        if status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
            return descriptor, status, bars, False
        assert context.history is not None
        available = len(context.history.bars)
        needed = bars + required_count
        if available < needed:
            return descriptor, status, bars, False
        return descriptor, status, bars, True

    def _insufficient(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
        descriptor: EvidenceDescriptor | None,
        needed: int,
    ) -> FeatureResult:
        available = len(context.history.bars) if context.history is not None else 0
        return _result(
            self._definition,
            request,
            context,
            descriptor,
            status=FeatureStatus.INSUFFICIENT_DATA,
            value=None,
            source_name="history",
            fallback_quality=(
                context.history.quality if context.history is not None else None
            ),
            warnings=(f"requires {needed} history bars; available {available}",),
        )


class AbsoluteReturnCalculator(_BarsCalculator):
    _definition = ABSOLUTE_RETURN

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        descriptor, status, bars, enough_bars = self._prepared(
            context, request, required_count=1
        )
        if status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
            return self._unavailable(context, request, descriptor, status)
        if not enough_bars:
            return self._insufficient(context, request, descriptor, bars + 1)
        assert context.history is not None
        value = context.history.bars[-1].close - context.history.bars[-1 - bars].close
        return _result(
            self._definition,
            request,
            context,
            descriptor,
            status=status,
            value=float(value),
            source_name="history",
            fallback_quality=context.history.quality,
            lookback_bars_used=bars + 1,
            warnings=_warnings(descriptor),
        )


class PercentReturnCalculator(_BarsCalculator):
    _definition = PERCENT_RETURN

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        descriptor, status, bars, enough_bars = self._prepared(
            context, request, required_count=1
        )
        if status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
            return self._unavailable(context, request, descriptor, status)
        if not enough_bars:
            return self._insufficient(context, request, descriptor, bars + 1)
        assert context.history is not None
        latest = context.history.bars[-1].close
        base = context.history.bars[-1 - bars].close
        if base == 0:
            return _result(
                self._definition,
                request,
                context,
                descriptor,
                status=FeatureStatus.FAILED,
                value=None,
                source_name="history",
                fallback_quality=context.history.quality,
                lookback_bars_used=bars + 1,
                warnings=("percentage return is undefined for zero base close",),
            )
        value = ((latest / base) - 1) * 100
        return _result(
            self._definition,
            request,
            context,
            descriptor,
            status=status,
            value=float(value),
            source_name="history",
            fallback_quality=context.history.quality,
            lookback_bars_used=bars + 1,
            warnings=_warnings(descriptor),
        )


class HighLowRangePercentCalculator(_BarsCalculator):
    _definition = HIGH_LOW_RANGE_PERCENT

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        descriptor, status, bars, enough_bars = self._prepared(
            context, request, required_count=0
        )
        if status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
            return self._unavailable(context, request, descriptor, status)
        if not enough_bars:
            return self._insufficient(context, request, descriptor, bars)
        assert context.history is not None
        window = context.history.bars[-bars:]
        latest_close = context.history.bars[-1].close
        if latest_close == 0:
            return _result(
                self._definition,
                request,
                context,
                descriptor,
                status=FeatureStatus.FAILED,
                value=None,
                source_name="history",
                fallback_quality=context.history.quality,
                lookback_bars_used=bars,
                warnings=("high-low range percentage is undefined for zero latest close",),
            )
        highest = max(bar.high for bar in window)
        lowest = min(bar.low for bar in window)
        value = ((highest - lowest) / latest_close) * 100
        return _result(
            self._definition,
            request,
            context,
            descriptor,
            status=status,
            value=float(value),
            source_name="history",
            fallback_quality=context.history.quality,
            lookback_bars_used=bars,
            warnings=_warnings(descriptor),
        )


BUILTIN_CALCULATORS: tuple[FeatureCalculator, ...] = (
    CurrentPriceCalculator(),
    HistoryBarCountCalculator(),
    HistoryFirstCloseCalculator(),
    HistoryLastCloseCalculator(),
    AbsoluteReturnCalculator(),
    PercentReturnCalculator(),
    HighLowRangePercentCalculator(),
)
