"""Opportunity and forward-looking position assessment contracts."""

from typing import Self

from pydantic import Field, model_validator

from tiaf.contracts.common import (
    Confidence,
    ContractModel,
    Horizon,
    Metadata,
    NonEmptyStr,
    Score,
    Symbol,
    TiafDateTime,
)
from tiaf.contracts.enums import (
    ActionStrength,
    OpportunityAction,
    PositionAction,
    TradeDirection,
)


class OpportunityAssessment(ContractModel):
    """Timestamped forward opportunity intelligence for one underlying."""

    assessment_id: NonEmptyStr
    request_id: NonEmptyStr
    symbol: Symbol
    direction: TradeDirection
    action: OpportunityAction
    horizon: Horizon
    opportunity_score: Score
    confidence: Confidence
    summary: NonEmptyStr
    created_at: TiafDateTime
    expected_move_min_pct: float | None = None
    expected_move_max_pct: float | None = None
    preferred_entry_state: NonEmptyStr | None = None
    invalidation: NonEmptyStr | None = None
    evidence_ids: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    decision_bundle_id: NonEmptyStr | None = None
    valid_until: TiafDateTime | None = None
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_assessment(self) -> Self:
        """Validate expected-move bounds and the assessment validity window."""
        if (
            self.expected_move_min_pct is not None
            and self.expected_move_max_pct is not None
            and self.expected_move_max_pct < self.expected_move_min_pct
        ):
            raise ValueError(
                "expected_move_max_pct must be greater than or equal to expected_move_min_pct"
            )
        if self.valid_until is not None and self.valid_until <= self.created_at:
            raise ValueError("valid_until must be later than created_at")
        return self


class PositionAssessment(ContractModel):
    """Forward-looking intelligence for an existing or adopted position."""

    assessment_id: NonEmptyStr
    request_id: NonEmptyStr
    position_id: NonEmptyStr
    underlying: Symbol
    action: PositionAction
    strength: ActionStrength
    confidence: Confidence
    forward_view: NonEmptyStr
    created_at: TiafDateTime
    current_pnl: float | None = None
    current_pnl_pct: float | None = None
    changed_since_previous: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    reasons: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    evidence_ids: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    decision_bundle_id: NonEmptyStr | None = None
    valid_until: TiafDateTime | None = None
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_validity_window(self) -> Self:
        """Ensure an assessment expires strictly after it is created."""
        if self.valid_until is not None and self.valid_until <= self.created_at:
            raise ValueError("valid_until must be later than created_at")
        return self
