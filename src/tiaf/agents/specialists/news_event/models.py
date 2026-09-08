"""Typed A3.5 detail attached to a standard AgentOpinionV2."""

import json
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from tiaf.agents._validation import require_unique
from tiaf.agents.enums import AgentStance
from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr, TiafDateTime
from tiaf.events import (
    CatalystDirection,
    CatalystHorizon,
    CatalystStrength,
    ContradictionState,
    EventFamily,
    EventMateriality,
    EventNovelty,
    ExecutionRiskState,
    SourceQualityState,
)

from .enums import NewsEventReasonCode

UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class EventClusterAssessment(ContractModel):
    """One deduplicated event interpretation with all source IDs retained."""

    cluster_id: NonEmptyStr
    event_ids: tuple[NonEmptyStr, ...]
    active_event_ids: tuple[NonEmptyStr, ...]
    dominant_family: EventFamily
    catalyst_direction: CatalystDirection
    catalyst_strength: CatalystStrength
    catalyst_horizon: CatalystHorizon
    materiality: EventMateriality
    novelty: EventNovelty
    source_quality: SourceQualityState
    contradiction_state: ContradictionState
    execution_risk: ExecutionRiskState
    contradiction_fields: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_cluster(self) -> Self:
        for values, label in (
            (self.event_ids, "assessment event IDs"),
            (self.active_event_ids, "assessment active event IDs"),
            (self.contradiction_fields, "assessment contradiction fields"),
        ):
            require_unique(values, label)
        if not self.event_ids or not self.active_event_ids:
            raise ValueError("cluster assessment requires event evidence")
        if not set(self.active_event_ids) <= set(self.event_ids):
            raise ValueError("active assessment events must belong to cluster")
        return self


class NewsEventAssessment(ContractModel):
    """Versioned, replayable event/catalyst interpretation."""

    schema_version: Literal["1.0"] = "1.0"
    assessment_id: NonEmptyStr
    specialist_version: NonEmptyStr
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    stance: AgentStance
    dominant_event_families: tuple[EventFamily, ...]
    catalyst_direction: CatalystDirection
    catalyst_strength: CatalystStrength
    catalyst_horizon: CatalystHorizon
    materiality: EventMateriality
    novelty: EventNovelty
    source_quality: SourceQualityState
    contradiction_state: ContradictionState
    execution_risk: ExecutionRiskState
    clusters: tuple[EventClusterAssessment, ...]
    evidence_coverage: UnitFloat
    confidence_basis: tuple[NonEmptyStr, ...]
    reason_codes: tuple[NewsEventReasonCode, ...]
    created_at: TiafDateTime

    @model_validator(mode="after")
    def validate_assessment(self) -> Self:
        require_unique(self.dominant_event_families, "dominant event families")
        require_unique(tuple(item.cluster_id for item in self.clusters), "assessment clusters")
        require_unique(self.confidence_basis, "event confidence basis")
        require_unique(self.reason_codes, "event reason codes")
        return self

    def canonical_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
