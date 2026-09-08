"""Transparent generic policy for deterministic company-quality interpretation."""

from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, model_validator

from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr


class FundamentalInterpretationPolicy(ContractModel):
    """Generic engineering thresholds; not a fitted return model."""

    schema_version: Literal["1.0"] = "1.0"
    policy_id: NonEmptyStr = "tiaf.fundamental-specialist"
    policy_version: NonEmptyStr = "1.0"
    growth_strong_percent: float = 20.0
    growth_healthy_percent: float = 10.0
    growth_moderate_percent: float = 2.0
    growth_declining_percent: float = -2.0
    growth_volatile_spread_percent: float = 30.0
    margin_strong_percent: float = 15.0
    margin_healthy_percent: float = 8.0
    margin_change_material_pp: float = 1.0
    return_strong_percent: float = 20.0
    return_healthy_percent: float = 12.0
    return_weak_percent: float = 6.0
    leverage_low: float = 0.5
    leverage_high: float = 1.5
    leverage_distressed: float = 3.0
    interest_coverage_weak: float = 2.0
    interest_coverage_strong: float = 5.0
    cash_conversion_healthy: float = 0.8
    cash_conversion_weak: float = 0.5
    consistency_high: float = 0.8
    consistency_low: float = 0.4
    valuation_cheap_percentile: float = 20.0
    valuation_reasonable_percentile: float = 45.0
    valuation_expensive_percentile: float = 75.0
    valuation_very_expensive_percentile: float = 90.0
    promoter_pledge_elevated_percent: float = 20.0
    dilution_elevated_percent: float = 5.0
    financial_sector_applicability: float = Field(default=0.6, ge=0, le=1)
    day_horizon_relevance: float = Field(default=0.25, ge=0, le=1)
    positional_horizon_relevance: float = Field(default=0.7, ge=0, le=1)
    medium_horizon_relevance: float = Field(default=0.9, ge=0, le=1)
    long_horizon_relevance: float = Field(default=1.0, ge=0, le=1)

    @model_validator(mode="after")
    def validate_policy(self) -> Self:
        if not (
            self.growth_declining_percent
            < self.growth_moderate_percent
            < self.growth_healthy_percent
            < self.growth_strong_percent
        ):
            raise ValueError("growth thresholds must increase")
        if not self.return_weak_percent < self.return_healthy_percent < self.return_strong_percent:
            raise ValueError("return thresholds must increase")
        if not self.leverage_low < self.leverage_high < self.leverage_distressed:
            raise ValueError("leverage thresholds must increase")
        if not (
            self.valuation_cheap_percentile
            < self.valuation_reasonable_percentile
            < self.valuation_expensive_percentile
            < self.valuation_very_expensive_percentile
        ):
            raise ValueError("valuation percentile thresholds must increase")
        return self


@lru_cache(maxsize=1)
def default_fundamental_policy() -> FundamentalInterpretationPolicy:
    """Return immutable policy 1.0."""
    return FundamentalInterpretationPolicy()

