"""Transparent generic relative-context policy; no fitted symbol thresholds."""

from functools import lru_cache
from typing import Literal

from pydantic import Field

from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr


class RelativeInterpretationPolicy(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    policy_id: NonEmptyStr = "tiaf.relative-specialist"
    policy_version: NonEmptyStr = "1.0"
    inline_spread_percent: float = Field(default=0.5, ge=0)
    outperform_spread_percent: float = Field(default=2.0, gt=0)
    strong_spread_percent: float = Field(default=5.0, gt=0)
    consistent_fraction: float = Field(default=0.65, ge=0.5, le=1)
    weak_consistency_fraction: float = Field(default=0.35, ge=0, le=0.5)
    extreme_atr: float = Field(default=2.5, gt=0)


@lru_cache(maxsize=1)
def default_relative_policy() -> RelativeInterpretationPolicy:
    return RelativeInterpretationPolicy()
