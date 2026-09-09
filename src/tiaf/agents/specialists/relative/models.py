"""Replayable A3.6 Relative Strength specialist detail."""

import json
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from tiaf.agents._validation import require_unique
from tiaf.agents.enums import AgentStance
from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr, Symbol, TiafDateTime
from tiaf.features.relative import BenchmarkRole

from .enums import (
    RelativeConsistencyState,
    RelativeExtremeState,
    RelativeLeadershipState,
    RelativeMtfState,
    RelativeReasonCode,
    RelativeStrengthState,
)

UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class RelativeContradiction(ContractModel):
    code: NonEmptyStr
    description: NonEmptyStr
    evidence_ids: tuple[NonEmptyStr, ...]

    @model_validator(mode="after")
    def validate_evidence(self) -> Self:
        if not self.evidence_ids:
            raise ValueError("relative contradiction requires evidence")
        require_unique(self.evidence_ids, "relative contradiction evidence IDs")
        return self


class RelativeAssessment(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    assessment_id: NonEmptyStr
    specialist_version: NonEmptyStr
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    stance: AgentStance
    benchmark_symbol: Symbol | None = None
    benchmark_role: BenchmarkRole | None = None
    relative_strength: RelativeStrengthState
    relative_consistency: RelativeConsistencyState
    mtf_alignment: RelativeMtfState
    leadership_state: RelativeLeadershipState
    extreme_state: RelativeExtremeState
    subject_return_percent: float | None = Field(default=None, allow_inf_nan=False)
    benchmark_return_percent: float | None = Field(default=None, allow_inf_nan=False)
    excess_return_percent: float | None = Field(default=None, allow_inf_nan=False)
    excess_move_atr: float | None = Field(default=None, allow_inf_nan=False)
    contradictions: tuple[RelativeContradiction, ...] = ()
    evidence_ids_by_dimension: tuple[tuple[NonEmptyStr, tuple[NonEmptyStr, ...]], ...]
    evidence_coverage: UnitFloat
    internal_agreement: UnitFloat
    confidence_basis: tuple[NonEmptyStr, ...]
    reason_codes: tuple[RelativeReasonCode, ...]
    created_at: TiafDateTime

    @model_validator(mode="after")
    def validate_assessment(self) -> Self:
        if (self.benchmark_symbol is None) != (self.benchmark_role is None):
            raise ValueError("benchmark identity and role must appear together")
        require_unique(
            tuple(item.code for item in self.contradictions), "relative contradiction codes"
        )
        require_unique(
            tuple(name for name, _ in self.evidence_ids_by_dimension), "relative dimensions"
        )
        for _, ids in self.evidence_ids_by_dimension:
            require_unique(ids, "relative dimension evidence IDs")
        require_unique(self.confidence_basis, "relative confidence basis")
        require_unique(self.reason_codes, "relative reason codes")
        return self

    def canonical_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
