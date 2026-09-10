"""Replayable typed detail for the three A3.7 specialists."""

import json
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from tiaf.agents._validation import require_unique
from tiaf.agents.enums import AgentStance
from tiaf.baseline.enums import CandidateClass
from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr, TiafDateTime
from tiaf.data import InstrumentType

from .enums import (
    ConfirmationState,
    CrowdingState,
    DerivativesLiquidityState,
    DerivativesParticipationState,
    DerivativesPositioningState,
    DerivativesReasonCode,
    DerivativesVolatilityState,
    ExpiryProximityState,
    OpportunityMaturityState,
    OpportunityQualityState,
    OpportunityReasonCode,
    OpportunityRiskLevel,
    RemainingRoomQuality,
    RiskReasonCode,
)

UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class ContextContradiction(ContractModel):
    code: NonEmptyStr
    description: NonEmptyStr
    evidence_ids: tuple[NonEmptyStr, ...]

    @model_validator(mode="after")
    def validate_evidence(self) -> Self:
        if not self.evidence_ids:
            raise ValueError("context contradiction requires evidence")
        require_unique(self.evidence_ids, "context contradiction evidence IDs")
        return self


class _ReplayDetail(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    assessment_id: NonEmptyStr
    specialist_version: NonEmptyStr
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    stance: AgentStance
    instrument_type: InstrumentType
    instrument_context: NonEmptyStr
    horizon_context: NonEmptyStr
    evidence_families: tuple[NonEmptyStr, ...]
    contradictions: tuple[ContextContradiction, ...] = ()
    evidence_ids_by_family: tuple[tuple[NonEmptyStr, tuple[NonEmptyStr, ...]], ...]
    internal_agreement: UnitFloat
    confidence_basis: tuple[NonEmptyStr, ...]
    created_at: TiafDateTime

    @model_validator(mode="after")
    def validate_replay_detail(self) -> Self:
        require_unique(self.evidence_families, "evidence families")
        require_unique(tuple(item.code for item in self.contradictions), "contradiction codes")
        require_unique(
            tuple(name for name, _ in self.evidence_ids_by_family), "evidence family names"
        )
        for _, ids in self.evidence_ids_by_family:
            require_unique(ids, "family evidence IDs")
        require_unique(self.confidence_basis, "confidence basis")
        return self

    def canonical_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )


class DerivativesContextAssessment(_ReplayDetail):
    volatility_state: DerivativesVolatilityState
    positioning_state: DerivativesPositioningState
    liquidity_state: DerivativesLiquidityState
    participation_state: DerivativesParticipationState
    crowding_state: CrowdingState
    expiry_proximity: ExpiryProximityState
    underlying_confirmation: ConfirmationState
    reason_codes: tuple[DerivativesReasonCode, ...]

    @model_validator(mode="after")
    def validate_reasons(self) -> Self:
        require_unique(self.reason_codes, "derivatives reason codes")
        return self


class OpportunityQualityAssessment(_ReplayDetail):
    quality_state: OpportunityQualityState
    maturity_state: OpportunityMaturityState
    remaining_room: RemainingRoomQuality
    baseline_candidate_class: CandidateClass | None = None
    supportive_families: tuple[NonEmptyStr, ...] = ()
    adverse_families: tuple[NonEmptyStr, ...] = ()
    reason_codes: tuple[OpportunityReasonCode, ...]

    @model_validator(mode="after")
    def validate_quality(self) -> Self:
        require_unique(self.supportive_families, "supportive families")
        require_unique(self.adverse_families, "adverse families")
        if set(self.supportive_families) & set(self.adverse_families):
            raise ValueError("supportive and adverse families must be disjoint")
        require_unique(self.reason_codes, "opportunity reason codes")
        return self


class OpportunityRiskAssessment(_ReplayDetail):
    risk_level: OpportunityRiskLevel
    active_risk_families: tuple[NonEmptyStr, ...]
    reason_codes: tuple[RiskReasonCode, ...]

    @model_validator(mode="after")
    def validate_risk(self) -> Self:
        require_unique(self.active_risk_families, "active risk families")
        require_unique(self.reason_codes, "risk reason codes")
        return self
