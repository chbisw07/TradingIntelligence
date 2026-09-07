"""Deterministic completed-history raw and relative volume features."""

import statistics
from enum import StrEnum

from tiaf.context import AnalysisContext
from tiaf.contracts.common import Metadata
from tiaf.features._calculation import A22Calculator, positive_int_parameter
from tiaf.features._trend_calculation import linear_regression
from tiaf.features._volume_calculation import (
    InvalidVolumeError,
    MissingVolumeError,
    arithmetic_mean,
    consecutive_volume_run,
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


def _definition(
    feature_id: str,
    name: str,
    description: str,
    *,
    unit: str,
    minimum_bars: int,
    value_type: FeatureValueType = FeatureValueType.FLOAT,
    metadata: Metadata | None = None,
) -> FeatureDefinition:
    return FeatureDefinition(
        feature_id=feature_id,
        name=name,
        category=FeatureCategory.VOLUME,
        description=description,
        value_type=value_type,
        unit=unit,
        required_sources=(FeatureSourceKind.HISTORY,),
        minimum_history_bars=minimum_bars,
        metadata=metadata or {},
    )


CURRENT_VOLUME = _definition(
    "volume.current",
    "Latest completed volume",
    "Reported volume of the latest completed historical bar.",
    unit="volume",
    minimum_bars=1,
    value_type=FeatureValueType.INTEGER,
)
AVERAGE_VOLUME = _definition(
    "volume.average",
    "Average volume",
    "Arithmetic mean volume over the latest exact bar window.",
    unit="volume",
    minimum_bars=1,
    metadata={"bars_semantics": "latest_n_bars"},
)
MEDIAN_VOLUME = _definition(
    "volume.median",
    "Median volume",
    "Deterministic median volume over the latest exact bar window.",
    unit="volume",
    minimum_bars=1,
    metadata={"bars_semantics": "latest_n_bars"},
)
RELATIVE_VOLUME = _definition(
    "volume.relative",
    "Relative volume",
    "Latest volume divided by mean volume of the preceding exact comparison window.",
    unit="ratio",
    minimum_bars=2,
    metadata={"bars_semantics": "latest_excluded_from_previous_n_baseline"},
)
VOLUME_CHANGE_PERCENT = _definition(
    "volume.change_percent",
    "One-bar volume change",
    "Percentage change from previous completed-bar volume to latest volume.",
    unit="%",
    minimum_bars=2,
)
VOLUME_POSITION = _definition(
    "volume.position_in_range",
    "Volume position in range",
    "Latest volume position inside the latest exact rolling volume range.",
    unit="%",
    minimum_bars=1,
    metadata={"bars_semantics": "latest_n_bars"},
)
VOLUME_CV = _definition(
    "volume.coefficient_of_variation_percent",
    "Volume coefficient of variation",
    "Population volume standard deviation divided by mean volume.",
    unit="%",
    minimum_bars=1,
    metadata={"dispersion": "population_standard_deviation"},
)
VOLUME_SLOPE = _definition(
    "volume.linear_slope",
    "Linear volume slope",
    "OLS slope over the latest exact volume window.",
    unit="volume/bar",
    minimum_bars=2,
)
VOLUME_SLOPE_PERCENT = _definition(
    "volume.linear_slope_percent",
    "Mean-normalized linear volume slope",
    "OLS volume slope divided by mean volume and expressed per bar as a percentage.",
    unit="%/bar",
    minimum_bars=2,
)
CONSECUTIVE_VOLUME_INCREASES = _definition(
    "volume.consecutive_increases",
    "Consecutive volume increases",
    "Number of immediately consecutive latest strict volume increases.",
    unit="transitions",
    minimum_bars=1,
    value_type=FeatureValueType.INTEGER,
)
CONSECUTIVE_VOLUME_DECREASES = _definition(
    "volume.consecutive_decreases",
    "Consecutive volume decreases",
    "Number of immediately consecutive latest strict volume decreases.",
    unit="transitions",
    minimum_bars=1,
    value_type=FeatureValueType.INTEGER,
)


class CurrentVolumeCalculator(A22Calculator):
    """Return latest completed-bar volume without current-quote mixing."""

    _definition = CURRENT_VOLUME

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request)
        prepared, failure = self._prepare_history(context, request, minimum_bars=1)
        if failure is not None:
            return failure
        assert prepared is not None
        try:
            value = volume_values(prepared.history.bars[-1:])[0]
        except MissingVolumeError as exc:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.INSUFFICIENT_DATA,
                value=None,
                lookback_bars_used=1,
                warnings=(str(exc),),
            )
        except InvalidVolumeError as exc:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=1,
                warnings=(str(exc),),
            )
        return self._history_result(
            context, request, prepared, value=value, lookback_bars_used=1
        )


class _WindowOutput(StrEnum):
    AVERAGE = "average"
    MEDIAN = "median"
    POSITION = "position"
    CV = "cv"
    SLOPE = "slope"
    SLOPE_PERCENT = "slope_percent"


class VolumeWindowCalculator(A22Calculator):
    """Calculate one exact-window volume statistic."""

    def __init__(self, definition: FeatureDefinition, output: _WindowOutput) -> None:
        self._definition = definition
        self._output = output

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request, parameter_names=("bars",))
        bars = positive_int_parameter(request, "bars")
        if self._output in {_WindowOutput.SLOPE, _WindowOutput.SLOPE_PERCENT} and bars < 2:
            raise FeatureParameterError("volume regression bars must be at least 2")
        prepared, failure = self._prepare_history(
            context, request, minimum_bars=bars
        )
        if failure is not None:
            return failure
        assert prepared is not None
        try:
            values = volume_values(prepared.history.bars[-bars:])
        except MissingVolumeError as exc:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.INSUFFICIENT_DATA,
                value=None,
                lookback_bars_used=bars,
                warnings=(str(exc),),
            )
        except InvalidVolumeError as exc:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=bars,
                warnings=(str(exc),),
            )
        mean = arithmetic_mean(values)
        if self._output is _WindowOutput.AVERAGE:
            value = mean
        elif self._output is _WindowOutput.MEDIAN:
            value = float(statistics.median(values))
        elif self._output is _WindowOutput.POSITION:
            low = min(values)
            high = max(values)
            if high == low:
                return self._history_result(
                    context,
                    request,
                    prepared,
                    status=FeatureStatus.INSUFFICIENT_DATA,
                    value=None,
                    lookback_bars_used=bars,
                    warnings=("volume range position is undefined for a flat window",),
                )
            value = (values[-1] - low) / (high - low) * 100.0
        elif self._output is _WindowOutput.CV:
            if mean == 0:
                return self._history_result(
                    context,
                    request,
                    prepared,
                    status=FeatureStatus.FAILED,
                    value=None,
                    lookback_bars_used=bars,
                    warnings=("volume coefficient of variation requires nonzero mean",),
                )
            value = statistics.pstdev(values) / mean * 100.0
        else:
            regression = linear_regression(tuple(float(item) for item in values))
            value = regression.slope
            if self._output is _WindowOutput.SLOPE_PERCENT:
                if regression.mean_close == 0:
                    return self._history_result(
                        context,
                        request,
                        prepared,
                        status=FeatureStatus.FAILED,
                        value=None,
                        lookback_bars_used=bars,
                        warnings=("normalized volume slope requires nonzero mean",),
                    )
                value = value / regression.mean_close * 100.0
        return self._history_result(
            context,
            request,
            prepared,
            value=value,
            lookback_bars_used=bars,
        )


class RelativeVolumeCalculator(A22Calculator):
    """Compare latest volume with the preceding exact baseline only."""

    _definition = RELATIVE_VOLUME

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
            values = volume_values(prepared.history.bars[-bars - 1 :])
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
        baseline = arithmetic_mean(values[:-1])
        if baseline == 0:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=bars + 1,
                warnings=("relative volume baseline is zero",),
            )
        return self._history_result(
            context,
            request,
            prepared,
            value=values[-1] / baseline,
            lookback_bars_used=bars + 1,
        )


class VolumeChangeCalculator(A22Calculator):
    """Calculate latest completed volume change from the preceding bar."""

    _definition = VOLUME_CHANGE_PERCENT

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request)
        prepared, failure = self._prepare_history(context, request, minimum_bars=2)
        if failure is not None:
            return failure
        assert prepared is not None
        try:
            previous, latest = volume_values(prepared.history.bars[-2:])
        except MissingVolumeError as exc:
            return self._history_result(
                context, request, prepared, status=FeatureStatus.INSUFFICIENT_DATA,
                value=None, lookback_bars_used=2, warnings=(str(exc),)
            )
        except InvalidVolumeError as exc:
            return self._history_result(
                context, request, prepared, status=FeatureStatus.FAILED,
                value=None, lookback_bars_used=2, warnings=(str(exc),)
            )
        if previous == 0:
            return self._history_result(
                context,
                request,
                prepared,
                status=FeatureStatus.FAILED,
                value=None,
                lookback_bars_used=2,
                warnings=("volume change is undefined from zero previous volume",),
            )
        return self._history_result(
            context,
            request,
            prepared,
            value=((latest / previous) - 1.0) * 100.0,
            lookback_bars_used=2,
        )


class ConsecutiveVolumeCalculator(A22Calculator):
    """Count immediately trailing strict volume changes."""

    def __init__(self, definition: FeatureDefinition, *, increasing: bool) -> None:
        self._definition = definition
        self._increasing = increasing

    def compute(
        self, context: AnalysisContext, request: FeatureRequest
    ) -> FeatureResult:
        self._validate_request(request)
        prepared, failure = self._prepare_history(context, request, minimum_bars=1)
        if failure is not None:
            return failure
        assert prepared is not None
        try:
            values = volume_values(prepared.history.bars)
        except MissingVolumeError as exc:
            return self._history_result(
                context, request, prepared, status=FeatureStatus.INSUFFICIENT_DATA,
                value=None, warnings=(str(exc),)
            )
        except InvalidVolumeError as exc:
            return self._history_result(
                context, request, prepared, status=FeatureStatus.FAILED,
                value=None, warnings=(str(exc),)
            )
        value, lookback = consecutive_volume_run(
            values, increasing=self._increasing
        )
        return self._history_result(
            context,
            request,
            prepared,
            value=value,
            lookback_bars_used=lookback,
        )


VOLUME_FEATURE_DEFINITIONS = (
    CURRENT_VOLUME,
    AVERAGE_VOLUME,
    MEDIAN_VOLUME,
    RELATIVE_VOLUME,
    VOLUME_CHANGE_PERCENT,
    VOLUME_POSITION,
    VOLUME_CV,
    VOLUME_SLOPE,
    VOLUME_SLOPE_PERCENT,
    CONSECUTIVE_VOLUME_INCREASES,
    CONSECUTIVE_VOLUME_DECREASES,
)

VOLUME_CALCULATORS: tuple[FeatureCalculator, ...] = (
    CurrentVolumeCalculator(),
    VolumeWindowCalculator(AVERAGE_VOLUME, _WindowOutput.AVERAGE),
    VolumeWindowCalculator(MEDIAN_VOLUME, _WindowOutput.MEDIAN),
    RelativeVolumeCalculator(),
    VolumeChangeCalculator(),
    VolumeWindowCalculator(VOLUME_POSITION, _WindowOutput.POSITION),
    VolumeWindowCalculator(VOLUME_CV, _WindowOutput.CV),
    VolumeWindowCalculator(VOLUME_SLOPE, _WindowOutput.SLOPE),
    VolumeWindowCalculator(VOLUME_SLOPE_PERCENT, _WindowOutput.SLOPE_PERCENT),
    ConsecutiveVolumeCalculator(CONSECUTIVE_VOLUME_INCREASES, increasing=True),
    ConsecutiveVolumeCalculator(CONSECUTIVE_VOLUME_DECREASES, increasing=False),
)
