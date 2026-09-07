"""Immutable contracts for the first-class deterministic indicator subsystem."""

import math
import re
from typing import Annotated, Any, Self

from pydantic import (
    BeforeValidator,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    StringConstraints,
    field_validator,
    model_validator,
)

from tiaf.contracts import ContractModel, DataQuality
from tiaf.contracts.common import Metadata, NonEmptyStr, Symbol, TiafDateTime
from tiaf.data.normalization import normalize_interval
from tiaf.features.enums import FeatureSourceKind, FeatureStatus
from tiaf.indicators.enums import IndicatorParameterType

_INDICATOR_ID_PATTERN = r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$"
_FIELD_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
_SENSITIVE_METADATA_PARTS = (
    "access_token",
    "api_key",
    "apikey",
    "authorization",
    "client_id",
    "credential",
    "password",
    "secret",
    "token",
)

IndicatorId = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, pattern=_INDICATOR_ID_PATTERN),
]
NormalizedInterval = Annotated[str, BeforeValidator(normalize_interval)]
type IndicatorParameterValue = StrictStr | StrictInt | StrictFloat | StrictBool | None


def _validate_safe_metadata(value: Metadata) -> Metadata:
    pending: list[Any] = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            for key, item in current.items():
                normalized = key.casefold().replace("-", "_")
                if any(part in normalized for part in _SENSITIVE_METADATA_PARTS):
                    raise ValueError(
                        f"credentials are not permitted in indicator metadata: {key}"
                    )
                pending.append(item)
        elif isinstance(current, list):
            pending.extend(current)
    return value


def _canonical_parameters(
    value: Any,
) -> tuple[tuple[str, IndicatorParameterValue], ...]:
    if value is None:
        return ()
    if isinstance(value, dict):
        raw = tuple(value.items())
    elif isinstance(value, (str, bytes)):
        raise ValueError("parameters must contain name/value pairs")
    else:
        try:
            raw = tuple(value)
        except TypeError as exc:
            raise ValueError("parameters must contain name/value pairs") from exc
    pairs: list[tuple[str, IndicatorParameterValue]] = []
    seen: set[str] = set()
    for item in raw:
        if isinstance(item, (str, bytes)):
            raise ValueError("parameters must contain name/value pairs")
        try:
            name, parameter_value = item
        except (TypeError, ValueError) as exc:
            raise ValueError("parameters must contain name/value pairs") from exc
        normalized_name = str(name).strip()
        if not _FIELD_NAME.fullmatch(normalized_name):
            raise ValueError(f"invalid indicator parameter name: {normalized_name!r}")
        if normalized_name in seen:
            raise ValueError(f"duplicate indicator parameter: {normalized_name}")
        if parameter_value is not None and not isinstance(
            parameter_value, (str, int, float, bool)
        ):
            raise ValueError("indicator parameter values must be JSON scalars")
        if isinstance(parameter_value, float) and not math.isfinite(parameter_value):
            raise ValueError("indicator parameter floats must be finite")
        seen.add(normalized_name)
        pairs.append((normalized_name, parameter_value))
    return tuple(sorted(pairs))


class IndicatorParameterDefinition(ContractModel):
    """Versioned metadata and default for one accepted indicator parameter."""

    name: NonEmptyStr
    value_type: IndicatorParameterType
    required: bool = True
    has_default: bool = False
    default: IndicatorParameterValue = None
    minimum_exclusive: float | None = None
    description: NonEmptyStr

    @model_validator(mode="after")
    def validate_parameter(self) -> Self:
        if not _FIELD_NAME.fullmatch(self.name):
            raise ValueError("parameter name must be canonical snake_case")
        if self.has_default:
            if self.default is None:
                raise ValueError("a declared parameter default cannot be null")
            _validate_parameter_scalar(self, self.default)
        elif self.default is not None:
            raise ValueError("default requires has_default=True")
        return self


class IndicatorOutputDefinition(ContractModel):
    """One named numerical output exposed by an indicator."""

    name: NonEmptyStr
    unit: NonEmptyStr
    description: NonEmptyStr

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not _FIELD_NAME.fullmatch(value):
            raise ValueError("output name must be canonical snake_case")
        return value


class IndicatorStateDefinition(ContractModel):
    """One named deterministic categorical state and its allowed values."""

    name: NonEmptyStr
    allowed_values: tuple[NonEmptyStr, ...]
    description: NonEmptyStr

    @model_validator(mode="after")
    def validate_state(self) -> Self:
        if not _FIELD_NAME.fullmatch(self.name):
            raise ValueError("state name must be canonical snake_case")
        if not self.allowed_values or len(self.allowed_values) != len(
            set(self.allowed_values)
        ):
            raise ValueError("state allowed_values must be non-empty and unique")
        return self


class IndicatorDefinition(ContractModel):
    """Discoverable, provider-neutral definition of one indicator."""

    indicator_id: IndicatorId
    name: NonEmptyStr
    description: NonEmptyStr
    definition_version: NonEmptyStr = "1.0"
    parameter_schema_version: NonEmptyStr = "1.0"
    parameters: tuple[IndicatorParameterDefinition, ...]
    required_sources: tuple[FeatureSourceKind, ...] = (FeatureSourceKind.HISTORY,)
    supported_intervals: tuple[NormalizedInterval, ...] | None = None
    outputs: tuple[IndicatorOutputDefinition, ...]
    states: tuple[IndicatorStateDefinition, ...] = ()
    minimum_history_bars: int = Field(ge=1)
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(_validate_safe_metadata)

    @model_validator(mode="after")
    def validate_definition(self) -> Self:
        parameter_names = tuple(item.name for item in self.parameters)
        output_names = tuple(item.name for item in self.outputs)
        state_names = tuple(item.name for item in self.states)
        if len(parameter_names) != len(set(parameter_names)):
            raise ValueError("indicator parameter names must be unique")
        if not self.outputs or len(output_names) != len(set(output_names)):
            raise ValueError("indicator outputs must be non-empty and unique")
        if len(state_names) != len(set(state_names)):
            raise ValueError("indicator state names must be unique")
        if not self.required_sources or len(self.required_sources) != len(
            set(self.required_sources)
        ):
            raise ValueError("required_sources must be non-empty and unique")
        if self.supported_intervals is not None and (
            not self.supported_intervals
            or len(self.supported_intervals) != len(set(self.supported_intervals))
        ):
            raise ValueError("supported_intervals must be None or non-empty and unique")
        return self


class IndicatorRequest(ContractModel):
    """Canonical immutable request for one registered indicator."""

    indicator_id: IndicatorId
    parameters: tuple[tuple[str, IndicatorParameterValue], ...] = ()
    interval: NormalizedInterval
    required: bool = True

    _ordered_parameters = field_validator("parameters", mode="before")(
        _canonical_parameters
    )

    def parameter(self, name: str) -> IndicatorParameterValue:
        """Return one explicitly supplied parameter, or None when absent."""
        return dict(self.parameters).get(name)


class IndicatorValue(ContractModel):
    """One typed named scalar output."""

    name: NonEmptyStr
    value: StrictInt | StrictFloat
    unit: NonEmptyStr

    @model_validator(mode="after")
    def validate_value(self) -> Self:
        if not _FIELD_NAME.fullmatch(self.name):
            raise ValueError("indicator value name must be canonical snake_case")
        if isinstance(self.value, float) and not math.isfinite(self.value):
            raise ValueError("indicator values must be finite")
        return self


class IndicatorState(ContractModel):
    """One named deterministic state, separate from strategy interpretation."""

    name: NonEmptyStr
    value: NonEmptyStr

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not _FIELD_NAME.fullmatch(value):
            raise ValueError("indicator state name must be canonical snake_case")
        return value


class IndicatorResult(ContractModel):
    """Uniform scalar outputs, state, quality, and provenance for one request."""

    result_id: NonEmptyStr
    indicator_id: IndicatorId
    definition_version: NonEmptyStr
    parameters: tuple[tuple[str, IndicatorParameterValue], ...]
    interval: NormalizedInterval
    required: bool
    status: FeatureStatus
    quality: DataQuality
    as_of: TiafDateTime
    values: tuple[IndicatorValue, ...] = ()
    states: tuple[IndicatorState, ...] = ()
    source_context_id: NonEmptyStr
    subject_symbol: Symbol
    source_evidence: tuple[NonEmptyStr, ...]
    source_observed_at: TiafDateTime | None = None
    lookback_bars_used: int | None = Field(default=None, ge=0)
    warnings: tuple[NonEmptyStr, ...] = ()
    metadata: Metadata = Field(default_factory=dict)

    _ordered_parameters = field_validator("parameters", mode="before")(
        _canonical_parameters
    )
    _safe_metadata = field_validator("metadata")(_validate_safe_metadata)

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        value_names = tuple(item.name for item in self.values)
        state_names = tuple(item.name for item in self.states)
        if len(value_names) != len(set(value_names)):
            raise ValueError("indicator result value names must be unique")
        if len(state_names) != len(set(state_names)):
            raise ValueError("indicator result state names must be unique")
        if not self.source_evidence or len(self.source_evidence) != len(
            set(self.source_evidence)
        ):
            raise ValueError("source_evidence must be non-empty and unique")
        usable = self.status in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
        if usable and not self.values:
            raise ValueError("usable indicator result requires values")
        if not usable and (self.values or self.states):
            raise ValueError("unusable indicator result cannot carry values or states")
        return self

    def value(self, name: str) -> int | float | None:
        """Return a named scalar output, or None when absent."""
        return next((item.value for item in self.values if item.name == name), None)

    def state(self, name: str) -> str | None:
        """Return a named deterministic state, or None when absent."""
        return next((item.value for item in self.states if item.name == name), None)


class IndicatorBundle(ContractModel):
    """Ordered immutable indicator results for one AnalysisContext."""

    bundle_id: NonEmptyStr
    registry_version: NonEmptyStr
    context_id: NonEmptyStr
    subject_symbol: Symbol
    created_at: TiafDateTime
    results: tuple[IndicatorResult, ...]
    overall_quality: DataQuality
    complete: bool
    missing_required_indicators: tuple[IndicatorId, ...] = ()
    warnings: tuple[NonEmptyStr, ...] = ()
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(_validate_safe_metadata)

    @model_validator(mode="after")
    def validate_bundle(self) -> Self:
        if any(result.source_context_id != self.context_id for result in self.results):
            raise ValueError("every result must match bundle context_id")
        if any(result.subject_symbol != self.subject_symbol for result in self.results):
            raise ValueError("every result must match bundle subject_symbol")
        expected = tuple(
            result.indicator_id
            for result in self.results
            if result.required
            and result.status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
        )
        if self.missing_required_indicators != expected:
            raise ValueError("missing_required_indicators must match failed requirements")
        if self.complete != (not expected):
            raise ValueError("complete must agree with missing_required_indicators")
        return self


def _validate_parameter_scalar(
    definition: IndicatorParameterDefinition,
    value: IndicatorParameterValue,
) -> None:
    if definition.value_type is IndicatorParameterType.INTEGER:
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"parameter {definition.name!r} must be an integer")
        numeric = float(value)
    else:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"parameter {definition.name!r} must be numeric")
        numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"parameter {definition.name!r} must be finite")
    if (
        definition.minimum_exclusive is not None
        and numeric <= definition.minimum_exclusive
    ):
        raise ValueError(
            f"parameter {definition.name!r} must be greater than "
            f"{definition.minimum_exclusive}"
        )
