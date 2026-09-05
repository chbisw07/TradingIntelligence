"""Specialist opinion and decision-bundle contracts."""

from typing import Self

from pydantic import Field, model_validator

from tiaf.contracts.common import (
    Confidence,
    ContractModel,
    Horizon,
    Metadata,
    NonEmptyStr,
    Score,
    TiafDateTime,
)
from tiaf.contracts.enums import FreshnessState, TradeDirection


class AgentOpinion(ContractModel):
    """A bounded, attributable specialist opinion without execution authority."""

    agent_name: NonEmptyStr
    agent_role: NonEmptyStr
    subject_id: NonEmptyStr
    stance: TradeDirection
    confidence: Confidence
    summary: NonEmptyStr
    evidence_ids: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    concerns: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    supporting_factors: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    freshness: FreshnessState
    produced_at: TiafDateTime
    valid_until: TiafDateTime | None = None
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_validity_window(self) -> Self:
        """Ensure an opinion expires strictly after it is produced."""
        if self.valid_until is not None and self.valid_until <= self.produced_at:
            raise ValueError("valid_until must be later than produced_at")
        return self


class AgentDecisionBundle(ContractModel):
    """Aggregated interpretation that deliberately omits broker action."""

    decision_id: NonEmptyStr
    subject_id: NonEmptyStr
    horizon: Horizon
    opinions: tuple[AgentOpinion, ...]
    consensus_direction: TradeDirection
    confidence: Confidence
    disagreement_score: Score
    recommendation_summary: NonEmptyStr
    evidence_ids: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    data_snapshot_id: NonEmptyStr | None = None
    created_at: TiafDateTime
    valid_until: TiafDateTime | None = None
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_validity_window(self) -> Self:
        """Ensure a decision expires strictly after it is created."""
        if self.valid_until is not None and self.valid_until <= self.created_at:
            raise ValueError("valid_until must be later than created_at")
        return self
