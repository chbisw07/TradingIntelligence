"""Immutable structured detail produced inside the standard AgentOpinionV2."""

import json
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from tiaf.agents._validation import require_unique
from tiaf.agents.enums import AgentStance
from tiaf.baseline.enums import BaselineDirection, CandidateClass
from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr, TiafDateTime

from .enums import (
    BreakoutState,
    ExtensionState,
    MomentumState,
    MultiTimeframeState,
    ParticipationState,
    RemainingRoomState,
    StructureState,
    TechnicalReasonCode,
    TrendState,
    VolatilityState,
)

UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class TechnicalInvalidation(ContractModel):
    """Evidence-linked technical invalidation concept, never an order."""

    condition: NonEmptyStr
    evidence_id: NonEmptyStr
    fact_id: NonEmptyStr
    supplied_level: float | None = Field(default=None, allow_inf_nan=False)


class TechnicalContradiction(ContractModel):
    """One visible within-domain conflict between grouped dimensions."""

    code: NonEmptyStr
    description: NonEmptyStr
    evidence_ids: tuple[NonEmptyStr, ...]

    @model_validator(mode="after")
    def validate_evidence(self) -> Self:
        if not self.evidence_ids:
            raise ValueError("technical contradiction requires evidence")
        require_unique(self.evidence_ids, "contradiction evidence IDs")
        return self


class TechnicalAssessment(ContractModel):
    """A3.3 dimension-level interpretation attached to AgentOpinionV2."""

    schema_version: Literal["1.0"] = "1.0"
    assessment_id: NonEmptyStr
    specialist_version: NonEmptyStr
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    stance: AgentStance
    trend_state: TrendState
    momentum_state: MomentumState
    structure_state: StructureState
    breakout_state: BreakoutState
    participation_state: ParticipationState
    volatility_state: VolatilityState
    mtf_state: MultiTimeframeState
    extension_state: ExtensionState
    remaining_room: RemainingRoomState
    invalidations: tuple[TechnicalInvalidation, ...] = ()
    contradictions: tuple[TechnicalContradiction, ...] = ()
    positive_timeframes: tuple[NonEmptyStr, ...] = ()
    negative_timeframes: tuple[NonEmptyStr, ...] = ()
    evidence_ids_by_dimension: tuple[tuple[NonEmptyStr, tuple[NonEmptyStr, ...]], ...]
    evidence_coverage: UnitFloat
    internal_agreement: UnitFloat
    confidence_basis: tuple[NonEmptyStr, ...]
    reason_codes: tuple[TechnicalReasonCode, ...]
    baseline_direction: BaselineDirection | None = None
    baseline_opportunity_score: float | None = Field(default=None, ge=0, le=100)
    baseline_candidate_class: CandidateClass | None = None
    created_at: TiafDateTime

    @model_validator(mode="after")
    def validate_assessment(self) -> Self:
        require_unique(
            tuple(item.fact_id for item in self.invalidations),
            "technical invalidation facts",
        )
        require_unique(
            tuple(item.code for item in self.contradictions),
            "technical contradiction codes",
        )
        dimensions = tuple(name for name, _ in self.evidence_ids_by_dimension)
        require_unique(dimensions, "technical dimension names")
        for _, evidence_ids in self.evidence_ids_by_dimension:
            require_unique(evidence_ids, "technical dimension evidence IDs")
        require_unique(self.positive_timeframes, "positive timeframes")
        require_unique(self.negative_timeframes, "negative timeframes")
        require_unique(self.confidence_basis, "confidence basis")
        require_unique(self.reason_codes, "technical reason codes")
        baseline_values = (
            self.baseline_direction,
            self.baseline_opportunity_score,
            self.baseline_candidate_class,
        )
        if any(item is None for item in baseline_values) and any(
            item is not None for item in baseline_values
        ):
            raise ValueError("A2 baseline projection must be complete or absent")
        return self

    def canonical_json(self) -> str:
        """Return stable immutable specialist detail for opinion replay."""
        return json.dumps(
            self.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
