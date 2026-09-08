"""Typed A3.4 specialist detail attached to the standard Agent opinion."""

import json
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from tiaf.agents._validation import require_unique
from tiaf.agents.enums import AgentStance
from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr, TiafDateTime

from .enums import (
    BalanceSheetState,
    CapitalEfficiencyState,
    CashFlowState,
    CompanyQualityState,
    EarningsQualityState,
    FundamentalMomentumState,
    FundamentalReasonCode,
    GrowthState,
    MarginState,
    OwnershipEvidenceState,
    ProfitabilityState,
    StabilityState,
    ValuationState,
)

UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class FundamentalContradiction(ContractModel):
    """Visible cross-dimension or cross-source financial conflict."""

    code: NonEmptyStr
    description: NonEmptyStr
    evidence_ids: tuple[NonEmptyStr, ...]
    fact_ids: tuple[NonEmptyStr, ...]

    @model_validator(mode="after")
    def validate_evidence(self) -> Self:
        if not self.evidence_ids or not self.fact_ids:
            raise ValueError("fundamental contradiction requires evidence and facts")
        require_unique(self.evidence_ids, "fundamental contradiction evidence IDs")
        require_unique(self.fact_ids, "fundamental contradiction fact IDs")
        return self


class FundamentalAssessment(ContractModel):
    """Versioned dimensional company-quality interpretation."""

    schema_version: Literal["1.0"] = "1.0"
    assessment_id: NonEmptyStr
    specialist_version: NonEmptyStr
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    stance: AgentStance
    growth_state: GrowthState
    profitability_state: ProfitabilityState
    margin_state: MarginState
    capital_efficiency_state: CapitalEfficiencyState
    balance_sheet_state: BalanceSheetState
    cash_flow_state: CashFlowState
    earnings_quality_state: EarningsQualityState
    valuation_state: ValuationState
    stability_state: StabilityState
    ownership_governance_evidence_state: OwnershipEvidenceState
    fundamental_momentum: FundamentalMomentumState
    company_quality: CompanyQualityState
    contradictions: tuple[FundamentalContradiction, ...] = ()
    evidence_ids_by_dimension: tuple[tuple[NonEmptyStr, tuple[NonEmptyStr, ...]], ...]
    evidence_coverage: UnitFloat
    internal_agreement: UnitFloat
    sector_policy_applicability: UnitFloat
    horizon_relevance: UnitFloat
    confidence_basis: tuple[NonEmptyStr, ...]
    reason_codes: tuple[FundamentalReasonCode, ...]
    created_at: TiafDateTime

    @model_validator(mode="after")
    def validate_assessment(self) -> Self:
        require_unique(
            tuple(item.code for item in self.contradictions),
            "fundamental contradiction codes",
        )
        dimensions = tuple(name for name, _ in self.evidence_ids_by_dimension)
        require_unique(dimensions, "fundamental dimension names")
        for _, evidence_ids in self.evidence_ids_by_dimension:
            require_unique(evidence_ids, "fundamental dimension evidence IDs")
        require_unique(self.confidence_basis, "fundamental confidence basis")
        require_unique(self.reason_codes, "fundamental reason codes")
        return self

    def canonical_json(self) -> str:
        """Return stable specialist detail for replay."""
        return json.dumps(
            self.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
