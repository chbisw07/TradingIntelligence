"""Immutable contracts for deterministic feature definitions and results."""

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
from tiaf.features.enums import (
    FeatureCategory,
    FeatureSourceKind,
    FeatureStatus,
    FeatureValueType,
)

_FEATURE_ID_PATTERN = r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$"
_PARAMETER_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
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

FeatureId = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        pattern=_FEATURE_ID_PATTERN,
    ),
]
NormalizedInterval = Annotated[str, BeforeValidator(normalize_interval)]
type JSONScalar = StrictStr | StrictInt | StrictFloat | StrictBool | None
type FeatureValue = JSONScalar | tuple[JSONScalar, ...]


def _validate_safe_metadata(value: Metadata) -> Metadata:
    pending: list[Any] = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            for key, item in current.items():
                normalized = key.casefold().replace("-", "_")
                if any(part in normalized for part in _SENSITIVE_METADATA_PARTS):
                    raise ValueError(
                        f"credentials are not permitted in feature metadata: {key}"
                    )
                pending.append(item)
        elif isinstance(current, list):
            pending.extend(current)
    return value


def _canonical_parameters(value: Any) -> tuple[tuple[str, JSONScalar], ...]:
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
    pairs: list[tuple[str, JSONScalar]] = []
    seen: set[str] = set()
    for item in raw:
        if isinstance(item, (str, bytes)):
            raise ValueError("parameters must contain name/value pairs")
        try:
            name, parameter_value = item
        except (TypeError, ValueError) as exc:
            raise ValueError("parameters must contain name/value pairs") from exc
        normalized_name = str(name).strip()
        if not _PARAMETER_NAME.fullmatch(normalized_name):
            raise ValueError(f"invalid feature parameter name: {normalized_name!r}")
        if normalized_name in seen:
            raise ValueError(f"duplicate feature parameter: {normalized_name}")
        if parameter_value is not None and not isinstance(
            parameter_value, (str, int, float, bool)
        ):
            raise ValueError("feature parameter values must be JSON scalars")
        if isinstance(parameter_value, float) and not math.isfinite(parameter_value):
            raise ValueError("feature parameter floats must be finite")
        seen.add(normalized_name)
        pairs.append((normalized_name, parameter_value))
    return tuple(sorted(pairs, key=lambda pair: pair[0]))


class FeatureDefinition(ContractModel):
    """Versioned machine-readable definition of one deterministic feature."""

    feature_id: FeatureId
    name: NonEmptyStr
    category: FeatureCategory
    description: NonEmptyStr
    value_type: FeatureValueType
    unit: NonEmptyStr | None = None
    required_sources: tuple[FeatureSourceKind, ...]
    minimum_history_bars: int | None = Field(default=None, ge=0)
    supported_intervals: tuple[NormalizedInterval, ...] | None = None
    parameters_schema_version: NonEmptyStr = "1.0"
    definition_version: NonEmptyStr = "1.0"
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(_validate_safe_metadata)

    @model_validator(mode="after")
    def validate_definition(self) -> Self:
        if not self.required_sources:
            raise ValueError("required_sources must not be empty")
        if len(self.required_sources) != len(set(self.required_sources)):
            raise ValueError("required_sources must be unique")
        if self.supported_intervals is not None:
            if not self.supported_intervals:
                raise ValueError("supported_intervals must be None or non-empty")
            if len(self.supported_intervals) != len(set(self.supported_intervals)):
                raise ValueError("supported_intervals must be unique")
        return self


class FeatureRequest(ContractModel):
    """Canonical request for one registered feature calculation."""

    feature_id: FeatureId
    parameters: tuple[tuple[str, JSONScalar], ...] = ()
    interval: NormalizedInterval | None = None
    required: bool = True

    _ordered_parameters = field_validator("parameters", mode="before")(
        _canonical_parameters
    )

    def parameter(self, name: str) -> JSONScalar:
        """Return one canonical parameter or None when it is absent."""
        return dict(self.parameters).get(name)


class FeatureResult(ContractModel):
    """One deterministic value with source identity, quality, and provenance."""

    definition: FeatureDefinition
    request: FeatureRequest
    status: FeatureStatus
    value: FeatureValue = None
    unit: NonEmptyStr | None = None
    as_of: TiafDateTime
    source_context_id: NonEmptyStr
    subject_symbol: Symbol
    source_evidence: tuple[NonEmptyStr, ...]
    source_observed_at: TiafDateTime | None = None
    quality: DataQuality
    lookback_bars_used: int | None = Field(default=None, ge=0)
    warnings: tuple[NonEmptyStr, ...] = ()
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(_validate_safe_metadata)

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if self.definition.feature_id != self.request.feature_id:
            raise ValueError("definition and request feature IDs must match")
        if self.unit != self.definition.unit:
            raise ValueError("result unit must match the feature definition")
        if not self.source_evidence:
            raise ValueError("source_evidence must not be empty")
        if len(self.source_evidence) != len(set(self.source_evidence)):
            raise ValueError("source_evidence must be unique")
        usable = self.status in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
        if usable and self.value is None:
            raise ValueError("AVAILABLE or PARTIAL feature result requires a value")
        if not usable and self.value is not None:
            raise ValueError(f"{self.status.value} feature result cannot carry a value")
        if usable:
            self._validate_value_type()
            values = self.value if isinstance(self.value, tuple) else (self.value,)
            if any(isinstance(item, float) and not math.isfinite(item) for item in values):
                raise ValueError("feature result floats must be finite")
        return self

    def _validate_value_type(self) -> None:
        value = self.value
        expected = self.definition.value_type
        if expected in {FeatureValueType.FLOAT, FeatureValueType.LEVEL}:
            valid = isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected is FeatureValueType.INTEGER:
            valid = isinstance(value, int) and not isinstance(value, bool)
        elif expected is FeatureValueType.BOOLEAN:
            valid = isinstance(value, bool)
        elif expected is FeatureValueType.CATEGORY:
            valid = isinstance(value, str)
        else:
            valid = isinstance(value, tuple)
        if not valid:
            raise ValueError(
                f"feature value does not match {self.definition.value_type.value}"
            )


class FeatureBundle(ContractModel):
    """Ordered immutable results derived from one AnalysisContext."""

    bundle_id: NonEmptyStr
    context_id: NonEmptyStr
    subject_symbol: Symbol
    created_at: TiafDateTime
    results: tuple[FeatureResult, ...]
    overall_quality: DataQuality
    complete: bool
    missing_required_features: tuple[FeatureId, ...] = ()
    warnings: tuple[NonEmptyStr, ...] = ()
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(_validate_safe_metadata)

    @model_validator(mode="after")
    def validate_bundle(self) -> Self:
        if any(result.source_context_id != self.context_id for result in self.results):
            raise ValueError("every result must match the bundle context_id")
        if any(result.subject_symbol != self.subject_symbol for result in self.results):
            raise ValueError("every result must match the bundle subject_symbol")
        expected_missing = tuple(
            result.request.feature_id
            for result in self.results
            if result.request.required
            and result.status
            not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
        )
        if self.missing_required_features != expected_missing:
            raise ValueError(
                "missing_required_features must match unacceptable required results"
            )
        if self.complete != (not expected_missing):
            raise ValueError("complete must agree with missing_required_features")
        return self
