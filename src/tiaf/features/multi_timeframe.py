"""First-class ordered multi-timeframe context and factual aggregations."""

import math
from collections import Counter
from typing import Any, Self
from uuid import NAMESPACE_URL, uuid5

from pydantic import Field, field_validator, model_validator

from tiaf.contracts import ContractModel, DataQuality
from tiaf.contracts.common import Metadata, NonEmptyStr, Symbol, TiafDateTime
from tiaf.data import normalize_interval
from tiaf.features._calculation import worst_quality
from tiaf.features.enums import (
    FeatureCategory,
    FeatureSourceKind,
    FeatureStatus,
    FeatureValueType,
)
from tiaf.features.errors import FeatureParameterError
from tiaf.features.models import (
    FeatureBundle,
    FeatureDefinition,
    FeatureRequest,
    FeatureResult,
)

_USABLE = {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}


class TimeframeFeatureContext(ContractModel):
    """One requested timeframe and its independently derived feature bundle."""

    interval: NonEmptyStr
    context_id: NonEmptyStr | None = None
    feature_bundle_id: NonEmptyStr | None = None
    status: FeatureStatus
    quality: DataQuality
    as_of: TiafDateTime
    feature_bundle: FeatureBundle | None = None
    warnings: tuple[NonEmptyStr, ...] = ()
    metadata: Metadata = Field(default_factory=dict)

    @field_validator("interval", mode="before")
    @classmethod
    def normalize_timeframe(cls, value: str) -> str:
        return normalize_interval(value)

    @model_validator(mode="after")
    def validate_bundle_reference(self) -> Self:
        usable = self.status in _USABLE
        if usable and self.feature_bundle is None:
            raise ValueError("usable timeframe status requires a feature bundle")
        if self.feature_bundle is not None:
            if self.context_id != self.feature_bundle.context_id:
                raise ValueError("timeframe context_id must match feature bundle")
            if self.feature_bundle_id != self.feature_bundle.bundle_id:
                raise ValueError("timeframe feature_bundle_id must match embedded bundle")
            if self.quality != self.feature_bundle.overall_quality:
                raise ValueError("timeframe quality must match feature bundle")
            if any(
                result.request.interval not in {None, self.interval}
                for result in self.feature_bundle.results
            ):
                raise ValueError("timeframe feature intervals must match the context interval")
        elif self.context_id is not None or self.feature_bundle_id is not None:
            raise ValueError("unavailable timeframe cannot claim context or bundle identity")
        return self


class MultiTimeframeContext(ContractModel):
    """Ordered immutable feature contexts for one subject across intervals."""

    context_id: NonEmptyStr
    subject_symbol: Symbol
    requested_intervals: tuple[NonEmptyStr, ...]
    timeframes: tuple[TimeframeFeatureContext, ...]
    created_at: TiafDateTime
    overall_quality: DataQuality
    complete: bool
    missing_intervals: tuple[NonEmptyStr, ...] = ()
    warnings: tuple[NonEmptyStr, ...] = ()
    metadata: Metadata = Field(default_factory=dict)

    @field_validator("requested_intervals", mode="before")
    @classmethod
    def normalize_intervals(cls, value: Any) -> Any:
        if isinstance(value, (str, bytes)):
            return value
        return tuple(normalize_interval(item) for item in value)

    @model_validator(mode="after")
    def validate_order_and_completeness(self) -> Self:
        if not self.requested_intervals:
            raise ValueError("requested_intervals must not be empty")
        if len(self.requested_intervals) != len(set(self.requested_intervals)):
            raise ValueError("requested_intervals must be unique")
        if tuple(item.interval for item in self.timeframes) != self.requested_intervals:
            raise ValueError("timeframes must exactly preserve requested interval order")
        expected_missing = tuple(
            item.interval for item in self.timeframes if item.status not in _USABLE
        )
        if self.missing_intervals != expected_missing:
            raise ValueError("missing_intervals must match unusable timeframe contexts")
        if self.complete != (not expected_missing):
            raise ValueError("complete must agree with missing_intervals")
        if self.overall_quality != worst_quality(
            *(item.quality for item in self.timeframes)
        ):
            raise ValueError("overall_quality must match the weakest timeframe quality")
        for item in self.timeframes:
            if item.as_of > self.created_at:
                raise ValueError("created_at cannot predate timeframe evidence")
            if item.feature_bundle is not None:
                if item.feature_bundle.subject_symbol != self.subject_symbol:
                    raise ValueError("every timeframe bundle must match subject symbol")
        return self


def timeframe_feature_context(
    interval: str,
    feature_bundle: FeatureBundle,
) -> TimeframeFeatureContext:
    """Reference one completed feature bundle without merging timeframe facts."""
    if not feature_bundle.results:
        raise ValueError("timeframe feature bundle must contain results")
    usable_results = tuple(
        result for result in feature_bundle.results if result.status in _USABLE
    )
    if feature_bundle.complete and feature_bundle.overall_quality is DataQuality.GOOD:
        status = FeatureStatus.AVAILABLE
    elif usable_results:
        status = FeatureStatus.PARTIAL
    else:
        status = FeatureStatus.INSUFFICIENT_DATA
    return TimeframeFeatureContext(
        interval=interval,
        context_id=feature_bundle.context_id,
        feature_bundle_id=feature_bundle.bundle_id,
        status=status,
        quality=feature_bundle.overall_quality,
        as_of=min(result.as_of for result in feature_bundle.results),
        feature_bundle=feature_bundle,
        warnings=feature_bundle.warnings,
    )


def multi_timeframe_context(
    subject_symbol: str,
    timeframes: tuple[TimeframeFeatureContext, ...],
    *,
    created_at: TiafDateTime,
    context_id: str | None = None,
) -> MultiTimeframeContext:
    """Build a deterministic ordered aggregate without collapsing its bundles."""
    if not timeframes:
        raise ValueError("at least one timeframe context is required")
    missing = tuple(item.interval for item in timeframes if item.status not in _USABLE)
    qualities = tuple(item.quality for item in timeframes)
    overall_quality = worst_quality(*qualities)
    identity = "|".join(
        f"{item.interval}:{item.feature_bundle_id or item.status.value}" for item in timeframes
    )
    return MultiTimeframeContext(
        context_id=context_id
        or str(uuid5(NAMESPACE_URL, f"tiaf:multi-timeframe:{subject_symbol}:{identity}")),
        subject_symbol=subject_symbol,
        requested_intervals=tuple(item.interval for item in timeframes),
        timeframes=timeframes,
        created_at=created_at,
        overall_quality=overall_quality,
        complete=not missing,
        missing_intervals=missing,
        warnings=tuple(
            f"{item.interval}: {warning}" for item in timeframes for warning in item.warnings
        ),
    )


def _definition(
    feature_id: str,
    name: str,
    description: str,
    *,
    value_type: FeatureValueType = FeatureValueType.FLOAT,
    unit: str,
    category: FeatureCategory = FeatureCategory.RELATIVE,
) -> FeatureDefinition:
    return FeatureDefinition(
        feature_id=feature_id,
        name=name,
        category=category,
        description=description,
        value_type=value_type,
        unit=unit,
        required_sources=(FeatureSourceKind.DERIVED,),
        metadata={"denominator": "valid_contributing_timeframes"},
    )


REQUESTED_COUNT = _definition(
    "mtf.requested_timeframe_count", "Requested timeframe count",
    "Number of explicitly requested ordered timeframes.", value_type=FeatureValueType.INTEGER,
    unit="timeframes", category=FeatureCategory.META,
)
AVAILABLE_COUNT = _definition(
    "mtf.available_timeframe_count", "Available timeframe count",
    "Number of timeframes carrying usable feature bundles.", value_type=FeatureValueType.INTEGER,
    unit="timeframes", category=FeatureCategory.META,
)
POSITIVE_RETURN_FRACTION = _definition(
    "mtf.positive_return_fraction", "Positive-return timeframe fraction",
    "Fraction of valid timeframe returns greater than zero.", unit="fraction",
)
NEGATIVE_RETURN_FRACTION = _definition(
    "mtf.negative_return_fraction", "Negative-return timeframe fraction",
    "Fraction of valid timeframe returns below zero.", unit="fraction",
)
ABOVE_EMA_FRACTION = _definition(
    "mtf.price_above_ema_fraction", "Price-above-EMA timeframe fraction",
    "Fraction of valid timeframe EMA distances greater than zero.", unit="fraction",
)
BELOW_EMA_FRACTION = _definition(
    "mtf.price_below_ema_fraction", "Price-below-EMA timeframe fraction",
    "Fraction of valid timeframe EMA distances below zero.", unit="fraction",
)
POSITIVE_SLOPE_FRACTION = _definition(
    "mtf.positive_slope_fraction", "Positive-slope timeframe fraction",
    "Fraction of valid timeframe linear slopes greater than zero.", unit="fraction",
)
NEGATIVE_SLOPE_FRACTION = _definition(
    "mtf.negative_slope_fraction", "Negative-slope timeframe fraction",
    "Fraction of valid timeframe linear slopes below zero.", unit="fraction",
)
DIRECTIONAL_AGREEMENT = _definition(
    "mtf.directional_agreement_fraction", "Return-sign agreement fraction",
    "Largest positive, negative, or flat return-sign share among valid timeframes.",
    unit="fraction",
)
DISAGREEMENT = _definition(
    "mtf.disagreement_fraction", "Return-sign disagreement fraction",
    "One minus the largest return-sign share among valid timeframes.", unit="fraction",
)

MULTI_TIMEFRAME_FEATURE_DEFINITIONS = (
    REQUESTED_COUNT,
    AVAILABLE_COUNT,
    POSITIVE_RETURN_FRACTION,
    NEGATIVE_RETURN_FRACTION,
    ABOVE_EMA_FRACTION,
    BELOW_EMA_FRACTION,
    POSITIVE_SLOPE_FRACTION,
    NEGATIVE_SLOPE_FRACTION,
    DIRECTIONAL_AGREEMENT,
    DISAGREEMENT,
)


class MultiTimeframeFeatureEngine:
    """Aggregate exact constituent feature results over valid timeframes."""

    _definitions = {item.feature_id: item for item in MULTI_TIMEFRAME_FEATURE_DEFINITIONS}

    def definitions(self) -> tuple[FeatureDefinition, ...]:
        return tuple(self._definitions[key] for key in sorted(self._definitions))

    def compute_one(
        self, context: MultiTimeframeContext, request: FeatureRequest
    ) -> FeatureResult:
        try:
            definition = self._definitions[request.feature_id]
        except KeyError as exc:
            raise FeatureParameterError(f"feature is not registered: {request.feature_id}") from exc
        if request.interval is not None:
            raise FeatureParameterError("multi-timeframe requests do not accept an interval")
        if request.feature_id in {REQUESTED_COUNT.feature_id, AVAILABLE_COUNT.feature_id}:
            if request.parameters:
                raise FeatureParameterError("timeframe count features do not accept parameters")
            count_value = (
                len(context.timeframes)
                if request.feature_id == REQUESTED_COUNT.feature_id
                else sum(item.status in _USABLE for item in context.timeframes)
            )
            status = FeatureStatus.AVAILABLE if context.complete else FeatureStatus.PARTIAL
            return self._result(
                context, request, definition, status=status, value=count_value,
                quality=context.overall_quality,
                as_of=min(item.as_of for item in context.timeframes),
                contributors=context.timeframes,
            )

        parameter = "period" if request.feature_id in {
            ABOVE_EMA_FRACTION.feature_id, BELOW_EMA_FRACTION.feature_id
        } else "bars"
        if tuple(name for name, _ in request.parameters) != (parameter,):
            raise FeatureParameterError(
                f"feature {request.feature_id!r} requires exactly: {parameter}"
            )
        amount = self._positive_int(request, parameter)
        source_id = self._source_feature(request.feature_id)
        source_parameter = "period" if source_id == "trend.distance_from_ema_percent" else "bars"
        contributors: list[tuple[TimeframeFeatureContext, FeatureResult]] = []
        excluded: list[str] = []
        for timeframe in context.timeframes:
            if timeframe.feature_bundle is None:
                excluded.append(timeframe.interval)
                continue
            matches = tuple(
                result
                for result in timeframe.feature_bundle.results
                if result.request.feature_id == source_id
                and result.request.parameter(source_parameter) == amount
                and result.status in _USABLE
            )
            if (
                len(matches) != 1
                or isinstance(matches[0].value, bool)
                or not isinstance(matches[0].value, (int, float))
            ):
                excluded.append(timeframe.interval)
                continue
            if not math.isfinite(float(matches[0].value)):
                excluded.append(timeframe.interval)
                continue
            contributors.append((timeframe, matches[0]))
        if not contributors:
            return self._result(
                context, request, definition, status=FeatureStatus.INSUFFICIENT_DATA,
                value=None, quality=DataQuality.UNAVAILABLE, as_of=context.created_at,
                contributors=(), excluded=tuple(excluded),
                warnings=("no timeframe has one usable matching constituent feature",),
            )
        values = tuple(float(result.value) for _, result in contributors)  # type: ignore[arg-type]
        value: float
        if request.feature_id in {
            POSITIVE_RETURN_FRACTION.feature_id,
            ABOVE_EMA_FRACTION.feature_id,
            POSITIVE_SLOPE_FRACTION.feature_id,
        }:
            value = sum(item > 0 for item in values) / len(values)
        elif request.feature_id in {
            NEGATIVE_RETURN_FRACTION.feature_id,
            BELOW_EMA_FRACTION.feature_id,
            NEGATIVE_SLOPE_FRACTION.feature_id,
        }:
            value = sum(item < 0 for item in values) / len(values)
        else:
            signs = Counter(1 if item > 0 else -1 if item < 0 else 0 for item in values)
            agreement = max(signs.values()) / len(values)
            value = (
                agreement
                if request.feature_id == DIRECTIONAL_AGREEMENT.feature_id
                else 1 - agreement
            )
        quality = worst_quality(*(result.quality for _, result in contributors))
        status = (
            FeatureStatus.AVAILABLE
            if len(contributors) == len(context.timeframes)
            and all(result.status is FeatureStatus.AVAILABLE for _, result in contributors)
            and quality is DataQuality.GOOD
            else FeatureStatus.PARTIAL
        )
        return self._result(
            context, request, definition, status=status, value=value, quality=quality,
            as_of=min(item.as_of for item, _ in contributors),
            contributors=tuple(item for item, _ in contributors), excluded=tuple(excluded),
            lookback=amount + 1 if source_id != "trend.distance_from_ema_percent" else amount,
        )

    @staticmethod
    def _source_feature(feature_id: str) -> str:
        if feature_id in {ABOVE_EMA_FRACTION.feature_id, BELOW_EMA_FRACTION.feature_id}:
            return "trend.distance_from_ema_percent"
        if feature_id in {POSITIVE_SLOPE_FRACTION.feature_id, NEGATIVE_SLOPE_FRACTION.feature_id}:
            return "trend.linear_slope"
        return "return.percent"

    @staticmethod
    def _positive_int(request: FeatureRequest, name: str) -> int:
        value = request.parameter(name)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise FeatureParameterError(f"{name} must be a positive integer")
        return value

    @staticmethod
    def _result(
        context: MultiTimeframeContext,
        request: FeatureRequest,
        definition: FeatureDefinition,
        *, status: FeatureStatus, value: float | int | None, quality: DataQuality,
        as_of: TiafDateTime, contributors: tuple[TimeframeFeatureContext, ...],
        excluded: tuple[str, ...] = (), warnings: tuple[str, ...] = (),
        lookback: int | None = None,
    ) -> FeatureResult:
        metadata: Metadata = {
            "denominator_semantics": "valid_contributing_timeframes",
            "requested_intervals": list(context.requested_intervals),
            "contributing_intervals": [item.interval for item in contributors],
            "excluded_intervals": list(excluded),
            "feature_bundle_ids": [
                item.feature_bundle_id for item in contributors if item.feature_bundle_id
            ],
            "contributing_as_of": {
                item.interval: item.as_of.isoformat() for item in contributors
            },
            "valid_contributor_count": len(contributors),
            "requested_timeframe_count": len(context.timeframes),
        }
        return FeatureResult(
            definition=definition, request=request, status=status, value=value,
            unit=definition.unit, as_of=as_of, source_context_id=context.context_id,
            subject_symbol=context.subject_symbol, source_evidence=("timeframes",),
            source_observed_at=as_of, quality=quality, lookback_bars_used=lookback,
            warnings=warnings, metadata=metadata,
        )
