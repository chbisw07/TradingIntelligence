"""Transparent multi-period sector/rotation interpretation policy."""

from functools import lru_cache
from typing import Literal

from pydantic import Field

from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr


class SectorInterpretationPolicy(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    policy_id: NonEmptyStr = "tiaf.sector-specialist"
    policy_version: NonEmptyStr = "1.0"
    relative_material_percent: float = Field(default=1.0, gt=0)
    subject_material_percent: float = Field(default=1.0, gt=0)
    breadth_strong_fraction: float = Field(default=0.65, ge=0.5, le=1)
    breadth_weak_fraction: float = Field(default=0.35, ge=0, le=0.5)
    narrow_concentration_fraction: float = Field(default=0.50, ge=0, le=1)
    minimum_rotation_periods: int = Field(default=2, ge=2)


@lru_cache(maxsize=1)
def default_sector_policy() -> SectorInterpretationPolicy:
    return SectorInterpretationPolicy()
