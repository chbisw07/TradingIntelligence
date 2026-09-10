"""Transparent generic A3.7 interpretation policy; no symbol-fitted values."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator

from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr


class OpportunityInterpretationPolicy(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    policy_id: NonEmptyStr = "tiaf.a3-7-opportunity-context"
    policy_version: NonEmptyStr = "1.0"
    compressed_iv: float = Field(default=12.0, ge=0)
    elevated_iv: float = Field(default=30.0, gt=0)
    balanced_pcr_low: float = Field(default=0.8, gt=0)
    balanced_pcr_high: float = Field(default=1.2, gt=0)
    concentrated_oi_fraction: float = Field(default=0.45, ge=0, le=1)
    adequate_spread_percent: float = Field(default=3.0, ge=0)
    weak_spread_percent: float = Field(default=5.0, gt=0)
    imminent_expiry_days: int = Field(default=1, ge=0)
    near_expiry_days: int = Field(default=3, ge=1)
    minimum_core_families: int = Field(default=2, ge=1)
    minimum_quality_families: int = Field(default=3, ge=1)

    @model_validator(mode="after")
    def validate_ordering(self) -> "OpportunityInterpretationPolicy":
        if self.elevated_iv <= self.compressed_iv:
            raise ValueError("elevated IV must exceed compressed IV")
        if self.balanced_pcr_high <= self.balanced_pcr_low:
            raise ValueError("PCR upper boundary must exceed lower boundary")
        if self.weak_spread_percent <= self.adequate_spread_percent:
            raise ValueError("weak spread must exceed adequate spread")
        if self.near_expiry_days <= self.imminent_expiry_days:
            raise ValueError("near expiry must exceed imminent expiry")
        return self


@lru_cache(maxsize=1)
def default_opportunity_policy() -> OpportunityInterpretationPolicy:
    return OpportunityInterpretationPolicy()
