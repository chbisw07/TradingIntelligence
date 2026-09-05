"""Evidence and data-snapshot metadata contracts."""

from pydantic import Field

from tiaf.contracts.common import (
    Confidence,
    ContractModel,
    Metadata,
    NonEmptyStr,
    Symbol,
    TiafDateTime,
)
from tiaf.contracts.enums import DataQuality, EvidenceSource, EvidenceType, FreshnessState


class EvidenceItem(ContractModel):
    """A serializable, attributable unit of evidence."""

    evidence_id: NonEmptyStr
    evidence_type: EvidenceType
    source: EvidenceSource
    title: NonEmptyStr
    summary: NonEmptyStr
    observed_at: TiafDateTime
    freshness: FreshnessState
    confidence: Confidence | None = None
    source_ref: NonEmptyStr | None = None
    metadata: Metadata = Field(default_factory=dict)


class DataSnapshot(ContractModel):
    """Metadata describing a coherent data snapshot, without raw time series."""

    snapshot_id: NonEmptyStr
    symbol: Symbol
    observed_at: TiafDateTime
    freshness: FreshnessState
    quality: DataQuality
    providers: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    feature_version: NonEmptyStr | None = None
    metadata: Metadata = Field(default_factory=dict)
