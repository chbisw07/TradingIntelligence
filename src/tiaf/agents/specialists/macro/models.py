"""Replayable A3.6 Macro Context specialist detail."""

import json
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from tiaf.agents._validation import require_unique
from tiaf.agents.enums import AgentStance
from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr, TiafDateTime

from .enums import (
    CommodityContextState,
    CurrencyState,
    MacroReasonCode,
    MacroVolatilityRegime,
    MarketRiskRegime,
    RateRegime,
    SubjectSensitivityState,
)

UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class MacroContradiction(ContractModel):
    code: NonEmptyStr
    description: NonEmptyStr
    evidence_ids: tuple[NonEmptyStr, ...]

    @model_validator(mode="after")
    def validate_evidence(self) -> Self:
        if not self.evidence_ids:
            raise ValueError("macro contradiction requires evidence")
        require_unique(self.evidence_ids, "macro contradiction evidence IDs")
        return self


class MacroAssessment(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    assessment_id: NonEmptyStr
    specialist_version: NonEmptyStr
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    stance: AgentStance
    market: NonEmptyStr | None = None
    market_risk_regime: MarketRiskRegime
    volatility_regime: MacroVolatilityRegime
    rate_regime: RateRegime
    currency_context: CurrencyState
    commodity_context: CommodityContextState
    growth_context: NonEmptyStr | None = None
    policy_context: NonEmptyStr | None = None
    geopolitical_risk: NonEmptyStr | None = None
    subject_sensitivity: SubjectSensitivityState
    horizon_relevance: UnitFloat
    contradictions: tuple[MacroContradiction, ...] = ()
    evidence_ids_by_dimension: tuple[tuple[NonEmptyStr, tuple[NonEmptyStr, ...]], ...]
    evidence_coverage: UnitFloat
    internal_agreement: UnitFloat
    confidence_basis: tuple[NonEmptyStr, ...]
    reason_codes: tuple[MacroReasonCode, ...]
    created_at: TiafDateTime

    @model_validator(mode="after")
    def validate_assessment(self) -> Self:
        require_unique(
            tuple(item.code for item in self.contradictions), "macro contradiction codes"
        )
        require_unique(
            tuple(name for name, _ in self.evidence_ids_by_dimension), "macro dimensions"
        )
        for _, ids in self.evidence_ids_by_dimension:
            require_unique(ids, "macro dimension evidence IDs")
        require_unique(self.confidence_basis, "macro confidence basis")
        require_unique(self.reason_codes, "macro reason codes")
        return self

    def canonical_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
