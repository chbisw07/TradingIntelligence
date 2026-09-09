"""Replayable A3.6 Sector / Rotation specialist detail."""

import json
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from tiaf.agents._validation import require_unique
from tiaf.agents.enums import AgentStance
from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr, Symbol, TiafDateTime

from .enums import (
    RotationState,
    SectorBreadthState,
    SectorConcentrationState,
    SectorParticipationState,
    SectorReasonCode,
    SectorState,
    SubjectSectorState,
)

UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class SectorContradiction(ContractModel):
    code: NonEmptyStr
    description: NonEmptyStr
    evidence_ids: tuple[NonEmptyStr, ...]

    @model_validator(mode="after")
    def validate_evidence(self) -> Self:
        if not self.evidence_ids:
            raise ValueError("sector contradiction requires evidence")
        require_unique(self.evidence_ids, "sector contradiction evidence IDs")
        return self


class SectorAssessment(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    assessment_id: NonEmptyStr
    specialist_version: NonEmptyStr
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    stance: AgentStance
    sector_id: NonEmptyStr | None = None
    sector_name: NonEmptyStr | None = None
    benchmark_symbol: Symbol | None = None
    mapping_source: NonEmptyStr | None = None
    mapping_version: NonEmptyStr | None = None
    sector_state: SectorState
    rotation_state: RotationState
    subject_vs_sector: SubjectSectorState
    breadth_state: SectorBreadthState
    participation_state: SectorParticipationState
    concentration_state: SectorConcentrationState
    catalyst_context: tuple[NonEmptyStr, ...] = ()
    contradictions: tuple[SectorContradiction, ...] = ()
    evidence_ids_by_dimension: tuple[tuple[NonEmptyStr, tuple[NonEmptyStr, ...]], ...]
    evidence_coverage: UnitFloat
    internal_agreement: UnitFloat
    confidence_basis: tuple[NonEmptyStr, ...]
    reason_codes: tuple[SectorReasonCode, ...]
    created_at: TiafDateTime

    @model_validator(mode="after")
    def validate_assessment(self) -> Self:
        mapping = (
            self.sector_id,
            self.sector_name,
            self.benchmark_symbol,
            self.mapping_source,
            self.mapping_version,
        )
        if any(item is None for item in mapping) and any(item is not None for item in mapping):
            raise ValueError("sector mapping projection must be complete or absent")
        require_unique(self.catalyst_context, "sector catalyst context")
        require_unique(
            tuple(item.code for item in self.contradictions), "sector contradiction codes"
        )
        require_unique(
            tuple(name for name, _ in self.evidence_ids_by_dimension), "sector dimensions"
        )
        for _, ids in self.evidence_ids_by_dimension:
            require_unique(ids, "sector dimension evidence IDs")
        require_unique(self.confidence_basis, "sector confidence basis")
        require_unique(self.reason_codes, "sector reason codes")
        return self

    def canonical_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
