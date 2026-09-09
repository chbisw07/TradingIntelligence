"""Transparent horizon-aware macro interpretation policy."""

from functools import lru_cache
from typing import Literal

from pydantic import Field

from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr


class MacroInterpretationPolicy(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    policy_id: NonEmptyStr = "tiaf.macro-specialist"
    policy_version: NonEmptyStr = "1.0"
    risk_material_score: float = Field(default=0.35, ge=0, le=1)
    risk_strong_score: float = Field(default=0.70, ge=0, le=1)
    volatility_elevated_percentile: float = Field(default=0.70, ge=0, le=1)
    volatility_high_percentile: float = Field(default=0.85, ge=0, le=1)
    volatility_extreme_percentile: float = Field(default=0.95, ge=0, le=1)
    rate_material_bps: float = Field(default=25.0, gt=0)
    currency_material_percent: float = Field(default=1.0, gt=0)
    minimum_risk_dimensions: int = Field(default=2, ge=2)


@lru_cache(maxsize=1)
def default_macro_policy() -> MacroInterpretationPolicy:
    return MacroInterpretationPolicy()
