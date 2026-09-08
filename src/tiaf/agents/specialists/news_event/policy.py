"""Transparent generic A3.5 interpretation policy; no learned sentiment."""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field

from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr

UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class NewsEventInterpretationPolicy(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    policy_id: NonEmptyStr = "tiaf.news-event-specialist"
    policy_version: NonEmptyStr = "1.0"
    primary_source_weight: UnitFloat = 1.0
    official_source_weight: UnitFloat = 0.85
    trusted_secondary_weight: UnitFloat = 0.65
    other_source_weight: UnitFloat = 0.35
    unknown_source_weight: UnitFloat = 0.15
    direct_relevance_weight: UnitFloat = 1.0
    high_relevance_weight: UnitFloat = 0.8
    moderate_relevance_weight: UnitFloat = 0.55
    low_relevance_weight: UnitFloat = 0.25
    incidental_relevance_weight: UnitFloat = 0.1
    unknown_relevance_weight: UnitFloat = 0.0
    fresh_weight: UnitFloat = 1.0
    aging_weight: UnitFloat = 0.65
    stale_weight: UnitFloat = 0.25
    unknown_freshness_weight: UnitFloat = 0.2
    source_conflict_consistency_weight: UnitFloat = 0.35
    unknown_materiality_weight: UnitFloat = 0.4
    horizon_mismatch_weight: UnitFloat = 0.25


@lru_cache(maxsize=1)
def default_news_event_policy() -> NewsEventInterpretationPolicy:
    return NewsEventInterpretationPolicy()
