"""Versioned generic engineering policy for deterministic technical interpretation."""

from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, model_validator

from tiaf.agents._validation import require_unique
from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr


class TechnicalInterpretationPolicy(ContractModel):
    """Transparent thresholds; dimension votes prevent correlated-feature inflation."""

    schema_version: Literal["1.0"] = "1.0"
    policy_id: NonEmptyStr = "tiaf.technical-specialist"
    policy_version: NonEmptyStr = "1.0"
    day_interval_priority: tuple[NonEmptyStr, ...] = ("15m", "1h", "1d")
    positional_interval_priority: tuple[NonEmptyStr, ...] = ("1d", "1h", "15m")
    slope_direction_threshold: float = Field(default=0.05, ge=0)
    efficiency_strength_threshold: float = Field(default=0.30, ge=0, le=1)
    trend_r2_strength_threshold: float = Field(default=0.60, ge=0, le=1)
    structure_margin: float = Field(default=0.10, ge=0, le=1)
    rsi_positive: float = Field(default=55.0, ge=0, le=100)
    rsi_negative: float = Field(default=45.0, ge=0, le=100)
    participation_threshold: float = Field(default=0.10, ge=0, le=1)
    unusual_relative_volume_high: float = Field(default=1.50, gt=0)
    unusual_relative_volume_low: float = Field(default=0.60, gt=0)
    atr_low_percent: float = Field(default=1.0, ge=0)
    atr_elevated_percent: float = Field(default=3.0, ge=0)
    atr_extreme_percent: float = Field(default=5.0, ge=0)
    compression_ratio: float = Field(default=0.80, gt=0)
    expansion_ratio: float = Field(default=1.25, gt=0)
    mtf_alignment_fraction: float = Field(default=0.67, ge=0, le=1)
    mtf_conflict_fraction: float = Field(default=0.50, ge=0, le=1)
    mature_move_atr: float = Field(default=1.50, ge=0)
    extended_move_atr: float = Field(default=2.50, ge=0)
    exhaustion_move_atr: float = Field(default=3.00, ge=0)
    room_large_atr: float = Field(default=2.00, ge=0)
    room_moderate_atr: float = Field(default=1.00, ge=0)
    room_minimal_atr: float = Field(default=0.25, ge=0)

    @model_validator(mode="after")
    def validate_policy(self) -> Self:
        require_unique(self.day_interval_priority, "day interval priority")
        require_unique(self.positional_interval_priority, "positional interval priority")
        if self.rsi_negative >= self.rsi_positive:
            raise ValueError("RSI negative threshold must be below positive threshold")
        if not self.atr_low_percent < self.atr_elevated_percent < self.atr_extreme_percent:
            raise ValueError("ATR percent thresholds must increase")
        if not self.mature_move_atr < self.extended_move_atr <= self.exhaustion_move_atr:
            raise ValueError("extension thresholds must increase")
        if not self.room_minimal_atr < self.room_moderate_atr < self.room_large_atr:
            raise ValueError("remaining-room thresholds must increase")
        return self


@lru_cache(maxsize=1)
def default_technical_policy() -> TechnicalInterpretationPolicy:
    """Return the immutable A3.3 generic baseline policy."""
    return TechnicalInterpretationPolicy()
