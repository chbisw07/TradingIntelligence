"""Immutable point-in-time contracts for reusable sector and macro context."""

import hashlib
import json
import math
import re
from datetime import datetime
from enum import Enum
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    ValidationInfo,
    field_validator,
    model_validator,
)

from tiaf.agents._validation import require_unique
from tiaf.contracts import ContractModel, DataQuality, FreshnessState, Horizon
from tiaf.contracts.common import Metadata, NonEmptyStr, Symbol, TiafDateTime

from .enums import (
    ContextObservationKind,
    MacroEvidenceFamily,
    MappingQuality,
    SectorEvidenceFamily,
    SensitivityDirection,
)

ContextValue = StrictStr | StrictInt | StrictFloat | StrictBool
UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
_METRIC_PATTERN = re.compile(r"^(?:sector|macro)\.[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")


class SectorIdentity(ContractModel):
    """Explicit, versioned classification; never inferred from a company name."""

    sector_id: NonEmptyStr
    sector_name: NonEmptyStr
    benchmark_symbol: Symbol
    mapping_source: NonEmptyStr
    mapping_version: NonEmptyStr
    quality: MappingQuality
    industry_id: NonEmptyStr | None = None
    industry_name: NonEmptyStr | None = None
    effective_from: TiafDateTime
    effective_to: TiafDateTime | None = None

    @model_validator(mode="after")
    def validate_effective_range(self) -> Self:
        if (self.industry_id is None) != (self.industry_name is None):
            raise ValueError("industry identity must be complete or absent")
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError("sector mapping effective_to must follow effective_from")
        return self

    def applies_at(self, as_of: TiafDateTime) -> bool:
        return self.effective_from <= as_of and (
            self.effective_to is None or as_of < self.effective_to
        )


class SubjectMacroSensitivity(ContractModel):
    """Explicit subject/sector exposure mapping, distinct from macro state."""

    sensitivity_id: NonEmptyStr
    subject: Symbol
    family: MacroEvidenceFamily
    driver_id: NonEmptyStr
    direction: SensitivityDirection
    mapping_source: NonEmptyStr
    mapping_version: NonEmptyStr
    quality: MappingQuality
    effective_from: TiafDateTime
    effective_to: TiafDateTime | None = None

    @model_validator(mode="after")
    def validate_effective_range(self) -> Self:
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError("macro sensitivity effective_to must follow effective_from")
        return self

    def applies_at(self, as_of: TiafDateTime) -> bool:
        return self.effective_from <= as_of and (
            self.effective_to is None or as_of < self.effective_to
        )


class ContextObservation(ContractModel):
    """One source-attributed scalar context observation visible at a decision time."""

    observation_id: NonEmptyStr
    metric_id: NonEmptyStr
    value: ContextValue
    family: SectorEvidenceFamily | MacroEvidenceFamily
    kind: ContextObservationKind
    observed_at: TiafDateTime
    available_at: TiafDateTime
    source_id: NonEmptyStr
    source_version: NonEmptyStr
    source_reference: NonEmptyStr
    quality: DataQuality
    freshness: FreshnessState
    unit: NonEmptyStr | None = None
    interval: NonEmptyStr | None = None
    driver_id: NonEmptyStr | None = None
    applicable_horizons: tuple[NonEmptyStr, ...] = ()
    metadata: Metadata = Field(default_factory=dict)

    @field_validator("family", mode="before")
    @classmethod
    def resolve_family_namespace(
        cls, value: object, info: ValidationInfo
    ) -> SectorEvidenceFamily | MacroEvidenceFamily:
        metric_id = info.data.get("metric_id")
        raw = (
            value.value if isinstance(value, (SectorEvidenceFamily, MacroEvidenceFamily)) else value
        )
        if not isinstance(raw, str):
            raise ValueError("context family must be a string enum value")
        if isinstance(metric_id, str) and metric_id.startswith("macro."):
            return MacroEvidenceFamily(raw)
        if isinstance(metric_id, str) and metric_id.startswith("sector."):
            return SectorEvidenceFamily(raw)
        raise ValueError("context metric namespace is required before family")

    @model_validator(mode="after")
    def validate_observation(self) -> Self:
        if not _METRIC_PATTERN.fullmatch(self.metric_id):
            raise ValueError("context metric_id must be a sector.* or macro.* identifier")
        if isinstance(self.value, float) and not math.isfinite(self.value):
            raise ValueError("context value must be finite")
        if self.available_at < self.observed_at:
            raise ValueError("context evidence cannot be available before observation")
        require_unique(self.applicable_horizons, "applicable horizons")
        if isinstance(self.family, SectorEvidenceFamily) != self.metric_id.startswith("sector."):
            raise ValueError("context family must agree with metric namespace")
        return self


class SectorContextRequest(ContractModel):
    request_id: NonEmptyStr
    subject: Symbol
    sector_id: NonEmptyStr
    benchmark_symbol: Symbol
    as_of: TiafDateTime
    horizon: Horizon
    families: tuple[SectorEvidenceFamily, ...]
    required_freshness: FreshnessState

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        if not self.families:
            raise ValueError("sector context request requires evidence families")
        require_unique(self.families, "sector context families")
        return self


class MacroContextRequest(ContractModel):
    request_id: NonEmptyStr
    subject: Symbol
    market: NonEmptyStr
    as_of: TiafDateTime
    horizon: Horizon
    families: tuple[MacroEvidenceFamily, ...]
    required_freshness: FreshnessState

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        if not self.families:
            raise ValueError("macro context request requires evidence families")
        require_unique(self.families, "macro context families")
        return self


class SectorContextSnapshot(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    snapshot_id: NonEmptyStr
    identity: SectorIdentity
    requested_as_of: TiafDateTime
    observations: tuple[ContextObservation, ...]
    missing_families: tuple[SectorEvidenceFamily, ...] = ()
    quality: DataQuality
    freshness: FreshnessState
    acquired_at: TiafDateTime
    valid_until: TiafDateTime
    provider_id: NonEmptyStr
    provider_version: NonEmptyStr
    fingerprint: NonEmptyStr

    @model_validator(mode="after")
    def validate_snapshot(self) -> Self:
        require_unique(tuple(item.observation_id for item in self.observations), "observations")
        require_unique(self.missing_families, "missing sector families")
        if any(not isinstance(item.family, SectorEvidenceFamily) for item in self.observations):
            raise ValueError("sector snapshot accepts only sector observations")
        if any(item.available_at > self.requested_as_of for item in self.observations):
            raise ValueError("sector snapshot cannot contain future evidence")
        if self.valid_until <= self.acquired_at:
            raise ValueError("sector snapshot valid_until must follow acquisition")
        return self


class MacroContextSnapshot(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    snapshot_id: NonEmptyStr
    market: NonEmptyStr
    requested_as_of: TiafDateTime
    observations: tuple[ContextObservation, ...]
    sensitivities: tuple[SubjectMacroSensitivity, ...] = ()
    missing_families: tuple[MacroEvidenceFamily, ...] = ()
    quality: DataQuality
    freshness: FreshnessState
    acquired_at: TiafDateTime
    valid_until: TiafDateTime
    provider_id: NonEmptyStr
    provider_version: NonEmptyStr
    fingerprint: NonEmptyStr

    @model_validator(mode="after")
    def validate_snapshot(self) -> Self:
        require_unique(tuple(item.observation_id for item in self.observations), "observations")
        require_unique(tuple(item.sensitivity_id for item in self.sensitivities), "sensitivities")
        require_unique(self.missing_families, "missing macro families")
        if any(not isinstance(item.family, MacroEvidenceFamily) for item in self.observations):
            raise ValueError("macro snapshot accepts only macro observations")
        if any(item.available_at > self.requested_as_of for item in self.observations):
            raise ValueError("macro snapshot cannot contain future evidence")
        if any(not item.applies_at(self.requested_as_of) for item in self.sensitivities):
            raise ValueError("macro snapshot sensitivity must apply at requested_as_of")
        if self.valid_until <= self.acquired_at:
            raise ValueError("macro snapshot valid_until must follow acquisition")
        return self


def context_fingerprint(payload: object) -> str:
    """Hash normalized context content for cache/replay identity."""

    def encode(value: object) -> object:
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, Enum):
            return value.value
        raise TypeError(f"unsupported context fingerprint value: {type(value).__name__}")

    encoded = json.dumps(
        payload,
        default=encode,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(encoded.encode()).hexdigest()
