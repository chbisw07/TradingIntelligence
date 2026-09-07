"""Deterministic completed-history volume participation measurements."""

from enum import StrEnum

from tiaf.context import AnalysisContext
from tiaf.contracts.common import Metadata
from tiaf.features._calculation import A22Calculator, positive_int_parameter
from tiaf.features._volume_calculation import (
    InvalidVolumeError,
    MissingVolumeError,
    participation_totals,
    pearson_correlation,
    volume_values,
)
from tiaf.features.enums import (
    FeatureCategory,
    FeatureSourceKind,
    FeatureStatus,
    FeatureValueType,
)
from tiaf.features.errors import FeatureParameterError
from tiaf.features.models import FeatureDefinition, FeatureRequest, FeatureResult
from tiaf.features.registry import FeatureCalculator
from tiaf.features.volatility import bar_range_percent


def _definition(
    feature_id: str,
    name: str,
    description: str,
    *,
    minimum_bars: int,
    metadata: Metadata,
) -> FeatureDefinition:
    return FeatureDefinition(
        feature_id=feature_id,
        name=name,
        category=FeatureCategory.VOLUME,
        description=description,
        value_type=FeatureValueType.FLOAT,
        unit="correlation" if "alignment" in feature_id else "ratio",
        required_sources=(FeatureSourceKind.HISTORY,),
        minimum_history_bars=minimum_bars,
        metadata=metadata,
    )


_TRANSITION_METADATA: Metadata = {
    "bars_semantics": "n_transitions_requires_n_plus_one_bars",
    "volume_assignment": "destination_bar",
}

UP_VOLUME_FRACTION = _definition(
    "participation.up_volume_fraction",
    "Up-transition volume fraction",
    "Destination volume on rising closes divided by all destination volume.",
    minimum_bars=2,
    metadata=_TRANSITION_METADATA,
)
DOWN_VOLUME_FRACTION = _definition(
    "participation.down_volume_fraction",
    "Down-transition volume fraction",
    "Destination volume on falling closes divided by all destination volume.",
    minimum_bars=2,
    metadata=_TRANSITION_METADATA,
)
FLAT_VOLUME_FRACTION = _definition(
    "participation.flat_volume_fraction",
    "Flat-transition volume fraction",
    "Destination volume on equal closes divided by all destination volume.",
    minimum_bars=2,
    metadata=_TRANSITION_METADATA,
)
SIGNED_VOLUME_BALANCE = _definition(
    "participation.signed_volume_balance",
    "Signed volume balance",
    "Signed destination volume divided by all destination volume.",
    minimum_bars=2,
    metadata=_TRANSITION_METADATA,
)
RETURN_VOLUME_ALIGNMENT = _definition(
    "participation.return_volume_alignment",
    "Absolute-return and volume alignment",
    "Pearson correlation of absolute close returns and destination volume.",
    minimum_bars=3,
    metadata={
        **_TRANSITION_METADATA,
        "zero_variance": "not_applicable",
    },
)
RANGE_VOLUME_ALIGNMENT = _definition(
    "participation.range_volume_alignment",
    "Bar-range and volume alignment",
    "Pearson correlation of bar range percentage and volume.",
    minimum_bars=2,
    metadata={
        "bars_semantics": "latest_n_bars",
        "range": "high_low_divided_by_close_percent",
        "zero_variance": "not_applicable",
    },
)


class _FractionKind(StrEnum):
    UP = "up"
    DOWN = "down"
    FLAT = "flat"


class ParticipationFractionCalculator(A22Calculator):
    """Calculate one destination-volume transition fraction."""

    def __init__(self, definition: FeatureDefinition, kind: _FractionKind) -> None:
        self._definition = definition
        self._kind = kind

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request, parameter_names=("bars",))
        bars = positive_int_parameter(request, "bars")
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=bars + 1
        )
        if failure is not None:
            return failure
        assert prepared is not None
        window = prepared.history.bars[-bars - 1 :]
        try:
            totals = participation_totals(window)
        except MissingVolumeError as exc:
            return self._history_result(
                context, request, prepared, status=FeatureStatus.INSUFFICIENT_DATA,
                value=None, lookback_bars_used=bars + 1, warnings=(str(exc),)
            )
        except InvalidVolumeError as exc:
            return self._history_result(
                context, request, prepared, status=FeatureStatus.FAILED,
                value=None, lookback_bars_used=bars + 1, warnings=(str(exc),)
            )
        if totals.total == 0:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=bars + 1,
                warnings=("participation fraction requires nonzero destination volume",),
            )
        numerator = {
            _FractionKind.UP: totals.up,
            _FractionKind.DOWN: totals.down,
            _FractionKind.FLAT: totals.flat,
        }[self._kind]
        return self._history_result(
            context,
            request,
            prepared,
            value=numerator / totals.total,
            lookback_bars_used=bars + 1,
        )


class SignedVolumeBalanceCalculator(A22Calculator):
    """Calculate signed transition volume divided by total transition volume."""

    _definition = SIGNED_VOLUME_BALANCE

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request, parameter_names=("bars",))
        bars = positive_int_parameter(request, "bars")
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=bars + 1
        )
        if failure is not None:
            return failure
        assert prepared is not None
        try:
            totals = participation_totals(prepared.history.bars[-bars - 1 :])
        except MissingVolumeError as exc:
            return self._history_result(
                context, request, prepared, status=FeatureStatus.INSUFFICIENT_DATA,
                value=None, lookback_bars_used=bars + 1, warnings=(str(exc),)
            )
        except InvalidVolumeError as exc:
            return self._history_result(
                context, request, prepared, status=FeatureStatus.FAILED,
                value=None, lookback_bars_used=bars + 1, warnings=(str(exc),)
            )
        if totals.total == 0:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=bars + 1,
                warnings=("signed volume balance requires nonzero destination volume",),
            )
        return self._history_result(
            context,
            request,
            prepared,
            value=(totals.up - totals.down) / totals.total,
            lookback_bars_used=bars + 1,
        )


class ReturnVolumeAlignmentCalculator(A22Calculator):
    """Correlate absolute close returns with aligned destination volumes."""

    _definition = RETURN_VOLUME_ALIGNMENT

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request, parameter_names=("bars",))
        bars = positive_int_parameter(request, "bars")
        if bars < 2:
            raise FeatureParameterError("return/volume correlation bars must be at least 2")
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=bars + 1
        )
        if failure is not None:
            return failure
        assert prepared is not None
        window = prepared.history.bars[-bars - 1 :]
        try:
            volumes = volume_values(window[1:])
        except MissingVolumeError as exc:
            return self._history_result(
                context, request, prepared, status=FeatureStatus.INSUFFICIENT_DATA,
                value=None, lookback_bars_used=bars + 1, warnings=(str(exc),)
            )
        except InvalidVolumeError as exc:
            return self._history_result(
                context, request, prepared, status=FeatureStatus.FAILED,
                value=None, lookback_bars_used=bars + 1, warnings=(str(exc),)
            )
        if any(bar.close <= 0 for bar in window[:-1]):
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=bars + 1,
                warnings=("return/volume alignment requires positive base closes",),
            )
        returns = tuple(
            abs((window[index].close / window[index - 1].close) - 1.0)
            for index in range(1, len(window))
        )
        correlation = pearson_correlation(
            returns, tuple(float(volume) for volume in volumes)
        )
        if correlation is None:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.NOT_APPLICABLE,
                value=None,
                lookback_bars_used=bars + 1,
                warnings=("correlation is undefined when either series is constant",),
            )
        return self._history_result(
            context,
            request,
            prepared,
            value=correlation,
            lookback_bars_used=bars + 1,
        )


class RangeVolumeAlignmentCalculator(A22Calculator):
    """Correlate exact-bar range percentages with aligned volumes."""

    _definition = RANGE_VOLUME_ALIGNMENT

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request, parameter_names=("bars",))
        bars = positive_int_parameter(request, "bars")
        if bars < 2:
            raise FeatureParameterError("range/volume correlation bars must be at least 2")
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=bars
        )
        if failure is not None:
            return failure
        assert prepared is not None
        window = prepared.history.bars[-bars:]
        try:
            volumes = volume_values(window)
            ranges = tuple(bar_range_percent(bar) for bar in window)
        except MissingVolumeError as exc:
            return self._history_result(
                context, request, prepared, status=FeatureStatus.INSUFFICIENT_DATA,
                value=None, lookback_bars_used=bars, warnings=(str(exc),)
            )
        except InvalidVolumeError as exc:
            return self._history_result(
                context, request, prepared, status=FeatureStatus.FAILED,
                value=None, lookback_bars_used=bars, warnings=(str(exc),)
            )
        except ValueError as exc:
            return self._history_result(
                context, request, prepared, status=FeatureStatus.FAILED,
                value=None, lookback_bars_used=bars, warnings=(str(exc),)
            )
        correlation = pearson_correlation(
            ranges, tuple(float(volume) for volume in volumes)
        )
        if correlation is None:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.NOT_APPLICABLE,
                value=None,
                lookback_bars_used=bars,
                warnings=("correlation is undefined when either series is constant",),
            )
        return self._history_result(
            context,
            request,
            prepared,
            value=correlation,
            lookback_bars_used=bars,
        )


PARTICIPATION_FEATURE_DEFINITIONS = (
    UP_VOLUME_FRACTION,
    DOWN_VOLUME_FRACTION,
    FLAT_VOLUME_FRACTION,
    SIGNED_VOLUME_BALANCE,
    RETURN_VOLUME_ALIGNMENT,
    RANGE_VOLUME_ALIGNMENT,
)

PARTICIPATION_CALCULATORS: tuple[FeatureCalculator, ...] = (
    ParticipationFractionCalculator(UP_VOLUME_FRACTION, _FractionKind.UP),
    ParticipationFractionCalculator(DOWN_VOLUME_FRACTION, _FractionKind.DOWN),
    ParticipationFractionCalculator(FLAT_VOLUME_FRACTION, _FractionKind.FLAT),
    SignedVolumeBalanceCalculator(),
    ReturnVolumeAlignmentCalculator(),
    RangeVolumeAlignmentCalculator(),
)
