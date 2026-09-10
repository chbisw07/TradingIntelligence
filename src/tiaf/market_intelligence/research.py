"""Composable research outputs with enforced epistemic discipline."""

from typing import Literal, Self

from pydantic import Field, model_validator

from tiaf.agents import AgentOpinionV2
from tiaf.contracts import ContractModel, DataQuality, FreshnessState, Horizon
from tiaf.contracts.common import NonEmptyStr, Symbol, TiafDateTime

from .enums import EpistemicKind, PointInTimeQuality, ResearchDepth, ResearchStatus


class ResearchAssertion(ContractModel):
    assertion_id: NonEmptyStr
    kind: EpistemicKind
    statement: NonEmptyStr
    evidence_ids: tuple[NonEmptyStr, ...] = ()
    supporting_assertion_ids: tuple[NonEmptyStr, ...] = ()
    reasoning: NonEmptyStr | None = None
    assumptions: tuple[NonEmptyStr, ...] = ()
    invalidation_conditions: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_epistemic_discipline(self) -> Self:
        if self.kind is EpistemicKind.FACT:
            if not self.evidence_ids:
                raise ValueError("FACT assertion requires cited evidence")
            if self.supporting_assertion_ids:
                raise ValueError("FACT assertion cannot be promoted from another assertion")
            if self.assumptions:
                raise ValueError("FACT assertion cannot depend on assumptions")
        elif self.kind is EpistemicKind.INFERENCE:
            if (
                not self.evidence_ids and not self.supporting_assertion_ids
            ) or self.reasoning is None:
                raise ValueError(
                    "INFERENCE requires supporting evidence/assertions and explicit reasoning"
                )
        elif (
            not self.evidence_ids and not self.supporting_assertion_ids
        ) or not self.assumptions or not self.invalidation_conditions:
            raise ValueError(
                "HYPOTHESIS requires supporting evidence/assertions, assumptions, and "
                "invalidation conditions"
            )
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError("assertion evidence IDs must be unique")
        if len(self.supporting_assertion_ids) != len(set(self.supporting_assertion_ids)):
            raise ValueError("supporting assertion IDs must be unique")
        if self.assertion_id in self.supporting_assertion_ids:
            raise ValueError("assertion cannot support itself")
        return self


class ResearchGap(ContractModel):
    gap_id: NonEmptyStr
    capability: NonEmptyStr
    description: NonEmptyStr
    blocking: bool = False


class ResearchComponent(ContractModel):
    component_id: NonEmptyStr
    subject: Symbol
    as_of: TiafDateTime
    horizon: Horizon
    status: ResearchStatus
    assertions: tuple[ResearchAssertion, ...] = ()
    gaps: tuple[ResearchGap, ...] = ()
    contradiction_ids: tuple[NonEmptyStr, ...] = ()
    missing_evidence_ids: tuple[NonEmptyStr, ...] = ()
    quality: DataQuality
    freshness: FreshnessState
    point_in_time_quality: PointInTimeQuality
    producer_id: NonEmptyStr
    producer_version: NonEmptyStr
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    evidence_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    created_at: TiafDateTime

    @model_validator(mode="after")
    def validate_status(self) -> Self:
        if self.status is ResearchStatus.SUCCESS and not self.assertions:
            raise ValueError("successful research component requires assertions")
        if self.status is ResearchStatus.INSUFFICIENT_EVIDENCE and not self.gaps:
            raise ValueError("insufficient component must state its evidence gaps")
        return self


class BusinessModelAssessment(ResearchComponent):
    component_type: Literal["BUSINESS_MODEL"] = "BUSINESS_MODEL"


class IndustryStructureAssessment(ResearchComponent):
    component_type: Literal["INDUSTRY_STRUCTURE"] = "INDUSTRY_STRUCTURE"


class SupplyChainExposure(ResearchComponent):
    component_type: Literal["SUPPLY_CHAIN_EXPOSURE"] = "SUPPLY_CHAIN_EXPOSURE"


class CustomerExposure(ResearchComponent):
    component_type: Literal["CUSTOMER_EXPOSURE"] = "CUSTOMER_EXPOSURE"


class CompetitivePosition(ResearchComponent):
    component_type: Literal["COMPETITIVE_POSITION"] = "COMPETITIVE_POSITION"


class ManagementEvidence(ResearchComponent):
    component_type: Literal["MANAGEMENT_EVIDENCE"] = "MANAGEMENT_EVIDENCE"


class InternationalExposure(ResearchComponent):
    component_type: Literal["INTERNATIONAL_EXPOSURE"] = "INTERNATIONAL_EXPOSURE"


class PolicyExposure(ResearchComponent):
    component_type: Literal["POLICY_EXPOSURE"] = "POLICY_EXPOSURE"


class RiskRegister(ResearchComponent):
    component_type: Literal["RISK_REGISTER"] = "RISK_REGISTER"


class CatalystRegister(ResearchComponent):
    component_type: Literal["CATALYST_REGISTER"] = "CATALYST_REGISTER"


class ResearchHypothesis(ResearchComponent):
    component_type: Literal["RESEARCH_HYPOTHESIS"] = "RESEARCH_HYPOTHESIS"

    @model_validator(mode="after")
    def require_hypothesis(self) -> Self:
        if self.assertions and not any(
            item.kind is EpistemicKind.HYPOTHESIS for item in self.assertions
        ):
            raise ValueError("research hypothesis requires a HYPOTHESIS assertion")
        return self


class ContradictingEvidence(ResearchComponent):
    component_type: Literal["CONTRADICTING_EVIDENCE"] = "CONTRADICTING_EVIDENCE"

    @model_validator(mode="after")
    def require_contradiction(self) -> Self:
        if not self.contradiction_ids:
            raise ValueError("contradicting evidence component requires contradiction IDs")
        return self


class CompanyResearchProfile(ContractModel):
    profile_id: NonEmptyStr
    subject: Symbol
    as_of: TiafDateTime
    horizon: Horizon
    depth: ResearchDepth
    status: ResearchStatus
    component_ids: tuple[NonEmptyStr, ...]
    evidence_ids: tuple[NonEmptyStr, ...] = ()
    evidence_fingerprint: NonEmptyStr
    prior_opinions: tuple[AgentOpinionV2, ...] = ()
    missing_component_types: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_profile(self) -> Self:
        if not self.component_ids and self.status is ResearchStatus.SUCCESS:
            raise ValueError("successful company profile requires research components")
        if len(self.component_ids) != len(set(self.component_ids)):
            raise ValueError("research component IDs must be unique")
        return self
