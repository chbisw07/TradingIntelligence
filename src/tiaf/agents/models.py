"""Immutable framework-independent contracts for A3 specialist intelligence."""

import json
from typing import Annotated, Literal, Self

from pydantic import Field, JsonValue, StringConstraints, field_validator, model_validator

from tiaf.context import AnalysisPurpose
from tiaf.contracts import AgentOpinion as AgentOpinionV1
from tiaf.contracts import (
    ContractModel,
    DataQuality,
    EvidenceType,
    FreshnessState,
    Horizon,
    TradeStyle,
)
from tiaf.contracts.common import Metadata, NonEmptyStr, Symbol, TiafDateTime
from tiaf.data import InstrumentType

from ._validation import require_unique, validate_no_secrets, validate_safe_metadata
from .budget import AgentBudget, AgentUsage
from .enums import (
    AgentCapability,
    AgentRunStatus,
    AgentStance,
    AnalysisMode,
    BaselineAgreement,
    CalibrationStatus,
    CitationRole,
    ReasoningStatus,
    SpecialistCostTier,
    SpecialistId,
)
from .evidence import AgentEvidencePack, EvidenceClaim, MissingEvidenceRequest

UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
FiniteFloat = Annotated[float, Field(allow_inf_nan=False)]
PositiveFiniteFloat = Annotated[float, Field(gt=0, allow_inf_nan=False)]
Sha256Fingerprint = Annotated[
    str,
    StringConstraints(pattern=r"^[0-9a-f]{64}$"),
]


class AgentRequest(ContractModel):
    """One bounded request for exactly one named specialist."""

    request_id: NonEmptyStr
    run_id: NonEmptyStr
    subject: Symbol
    instrument_type: InstrumentType
    horizon: Horizon
    specialist: SpecialistId
    purpose: AnalysisPurpose
    trade_style: TradeStyle | None = None
    analysis_mode: AnalysisMode
    task: NonEmptyStr
    a2_context_ids: tuple[NonEmptyStr, ...]
    a2_evidence_ids: tuple[NonEmptyStr, ...]
    deterministic_baseline_reference: NonEmptyStr
    evidence_fingerprint: Sha256Fingerprint
    allowed_capabilities: tuple[AgentCapability, ...]
    budget: AgentBudget
    correlation_id: NonEmptyStr | None = None
    created_at: TiafDateTime
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        if not self.a2_context_ids or not self.a2_evidence_ids:
            raise ValueError("Agent request requires explicit A2 context and evidence IDs")
        require_unique(self.a2_context_ids, "A2 context IDs")
        require_unique(self.a2_evidence_ids, "A2 evidence IDs")
        if not self.allowed_capabilities:
            raise ValueError("Agent request requires allowed capabilities")
        require_unique(self.allowed_capabilities, "allowed capabilities")
        if AgentCapability.READ_A2_EVIDENCE not in self.allowed_capabilities:
            raise ValueError("Agent request must allow READ_A2_EVIDENCE")
        return self


class PolicyDerivedConfidence(ContractModel):
    """A deterministic confidence value whose policy is explicitly identified."""

    value: UnitFloat
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr


class EmpiricallyCalibratedConfidence(ContractModel):
    """A held-out empirical confidence estimate, not model self-confidence."""

    value: UnitFloat
    calibration_id: NonEmptyStr
    method: NonEmptyStr
    cohort: NonEmptyStr
    sample_size: int = Field(gt=0)
    evaluated_at: TiafDateTime


class AgentConfidence(ContractModel):
    """Separate confidence dimensions; unavailable values remain absent."""

    evidence_coverage: UnitFloat
    evidence_quality: DataQuality
    self_reported: UnitFloat | None = None
    self_reported_basis: NonEmptyStr | None = None
    policy_derived: PolicyDerivedConfidence | None = None
    empirically_calibrated: EmpiricallyCalibratedConfidence | None = None

    @model_validator(mode="after")
    def validate_self_reported_basis(self) -> Self:
        if (self.self_reported is None) != (self.self_reported_basis is None):
            raise ValueError("self-reported confidence and basis must appear together")
        return self


class ReasoningModelIdentity(ContractModel):
    """Provider/model/config identity retained without importing an SDK."""

    provider_id: NonEmptyStr
    model_id: NonEmptyStr
    model_version: NonEmptyStr | None = None
    configuration_id: NonEmptyStr


class ForecastQuantile(ContractModel):
    """One externally produced return and/or price distribution quantile."""

    probability: UnitFloat
    return_pct: FiniteFloat | None = None
    price: PositiveFiniteFloat | None = None

    @model_validator(mode="after")
    def validate_value(self) -> Self:
        if self.return_pct is None and self.price is None:
            raise ValueError("forecast quantile requires return_pct or price")
        return self


class ForecastThresholdProbability(ContractModel):
    """Calibrated probability that return reaches an explicit threshold."""

    threshold_return_pct: FiniteFloat
    probability: UnitFloat


class ForecastValidationMetric(ContractModel):
    """Named held-out validation metric supplied by a future forecast system."""

    name: NonEmptyStr
    value: FiniteFloat


class ForecastEvidence(ContractModel):
    """Consumer seam for external forecasts; A3.1 produces none."""

    forecast_id: NonEmptyStr
    subject: Symbol
    horizon: Horizon
    reference_price: PositiveFiniteFloat
    return_quantiles: tuple[ForecastQuantile, ...] = ()
    price_quantiles: tuple[ForecastQuantile, ...] = ()
    threshold_probabilities: tuple[ForecastThresholdProbability, ...] = ()
    expected_return_pct: FiniteFloat | None = None
    median_return_pct: FiniteFloat | None = None
    model_id: NonEmptyStr
    model_version: NonEmptyStr
    training_window_start: TiafDateTime
    training_window_end: TiafDateTime
    calibration_status: CalibrationStatus
    calibration_id: NonEmptyStr | None = None
    calibration_method: NonEmptyStr | None = None
    calibration_sample_size: int | None = Field(default=None, gt=0)
    validation_metrics: tuple[ForecastValidationMetric, ...] = ()
    regime_applicability: NonEmptyStr
    evidence_snapshot_reference: NonEmptyStr
    created_at: TiafDateTime
    valid_until: TiafDateTime
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_forecast(self) -> Self:
        if self.training_window_end <= self.training_window_start:
            raise ValueError("forecast training window must increase")
        if self.valid_until <= self.created_at:
            raise ValueError("forecast valid_until must follow created_at")
        if not (
            self.return_quantiles
            or self.price_quantiles
            or self.threshold_probabilities
            or self.expected_return_pct is not None
            or self.median_return_pct is not None
        ):
            raise ValueError("forecast evidence requires at least one numerical output")
        for values, label in (
            (self.return_quantiles, "return quantile probabilities"),
            (self.price_quantiles, "price quantile probabilities"),
        ):
            probabilities = tuple(item.probability for item in values)
            if probabilities != tuple(sorted(probabilities)):
                raise ValueError(f"{label} must be sorted")
            require_unique(probabilities, label)
        calibrated_fields = (
            self.calibration_id,
            self.calibration_method,
            self.calibration_sample_size,
        )
        if self.calibration_status is CalibrationStatus.CALIBRATED:
            if any(value is None for value in calibrated_fields):
                raise ValueError("calibrated forecast requires calibration metadata")
            if not self.validation_metrics:
                raise ValueError("calibrated forecast requires validation metrics")
        elif any(value is not None for value in calibrated_fields):
            raise ValueError("uncalibrated forecast cannot claim calibration metadata")
        return self


class SpecialistCapability(ContractModel):
    """Discoverable versioned declaration for one specialist implementation."""

    specialist: SpecialistId
    specialist_version: NonEmptyStr
    display_name: NonEmptyStr
    description: NonEmptyStr
    supported_instrument_types: tuple[InstrumentType, ...]
    required_evidence_types: tuple[EvidenceType, ...]
    optional_evidence_types: tuple[EvidenceType, ...] = ()
    allowed_capabilities: tuple[AgentCapability, ...]
    supports_no_llm: bool
    cost_tier: SpecialistCostTier
    prohibitions: tuple[NonEmptyStr, ...]
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_capability(self) -> Self:
        if not self.supported_instrument_types:
            raise ValueError("specialist requires supported instrument types")
        if not self.required_evidence_types:
            raise ValueError("specialist requires at least one evidence type")
        if not self.allowed_capabilities:
            raise ValueError("specialist requires allowed capabilities")
        if AgentCapability.READ_A2_EVIDENCE not in self.allowed_capabilities:
            raise ValueError("every A3.1 specialist must consume A2 evidence")
        if not self.prohibitions:
            raise ValueError("specialist must declare prohibited responsibilities")
        for values, label in (
            (self.supported_instrument_types, "supported instrument types"),
            (self.required_evidence_types, "required evidence types"),
            (self.optional_evidence_types, "optional evidence types"),
            (self.allowed_capabilities, "specialist capabilities"),
            (self.prohibitions, "specialist prohibitions"),
        ):
            require_unique(values, label)
        if set(self.required_evidence_types) & set(self.optional_evidence_types):
            raise ValueError("required and optional evidence types must be disjoint")
        return self


class AgentOpinionV2(ContractModel):
    """A3 specialist opinion with no execution or consensus semantics."""

    schema_version: Literal["2.0"] = "2.0"
    opinion_id: NonEmptyStr
    request_id: NonEmptyStr
    run_id: NonEmptyStr
    specialist: SpecialistId
    specialist_version: NonEmptyStr
    subject: Symbol
    horizon: Horizon
    stance: AgentStance
    status: AgentRunStatus
    confidence: AgentConfidence
    summary: NonEmptyStr
    reason_codes: tuple[NonEmptyStr, ...] = ()
    evidence_claims: tuple[EvidenceClaim, ...]
    supporting_evidence_ids: tuple[NonEmptyStr, ...] = ()
    contradictory_evidence_ids: tuple[NonEmptyStr, ...] = ()
    missing_evidence: tuple[MissingEvidenceRequest, ...] = ()
    risks: tuple[NonEmptyStr, ...] = ()
    caveats: tuple[NonEmptyStr, ...] = ()
    deterministic_baseline_reference: NonEmptyStr
    baseline_agreement: BaselineAgreement
    evidence_fingerprint: Sha256Fingerprint
    evidence_quality: DataQuality
    evidence_freshness: FreshnessState
    model_identity: ReasoningModelIdentity | None = None
    prompt_version: NonEmptyStr | None = None
    policy_version: NonEmptyStr
    usage: AgentUsage
    produced_at: TiafDateTime
    valid_until: TiafDateTime | None = None
    legacy_opinion: AgentOpinionV1 | None = None
    specialist_detail_schema_id: NonEmptyStr | None = None
    specialist_detail_json: NonEmptyStr | None = None
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_opinion(self) -> Self:
        if (self.specialist_detail_schema_id is None) != (
            self.specialist_detail_json is None
        ):
            raise ValueError("specialist detail schema and JSON must appear together")
        if self.specialist_detail_json is not None:
            try:
                detail = json.loads(self.specialist_detail_json)
            except json.JSONDecodeError as exc:
                raise ValueError("specialist detail must be valid JSON") from exc
            if not isinstance(detail, dict):
                raise ValueError("specialist detail JSON must contain an object")
            validate_no_secrets(detail)
        if self.status in {
            AgentRunStatus.BUDGET_EXCEEDED,
            AgentRunStatus.TIMEOUT,
            AgentRunStatus.FAILED,
        }:
            raise ValueError("infrastructure failures cannot be Agent opinions")
        expected = {
            AgentStance.INSUFFICIENT_EVIDENCE: AgentRunStatus.INSUFFICIENT_EVIDENCE,
            AgentStance.ABSTAIN: AgentRunStatus.ABSTAINED,
        }
        if self.stance in expected:
            if self.status is not expected[self.stance]:
                raise ValueError("opinion status must agree with non-directional stance")
        elif self.status not in {AgentRunStatus.SUCCESS, AgentRunStatus.PARTIAL}:
            raise ValueError("market stance requires SUCCESS or PARTIAL status")
        if self.valid_until is not None and self.valid_until <= self.produced_at:
            raise ValueError("opinion valid_until must follow produced_at")
        if self.confidence.evidence_quality is not self.evidence_quality:
            raise ValueError("confidence and opinion evidence quality must agree")
        collections = (
            (self.reason_codes, "reason codes"),
            (self.supporting_evidence_ids, "supporting evidence IDs"),
            (self.contradictory_evidence_ids, "contradictory evidence IDs"),
            (tuple(item.claim_id for item in self.evidence_claims), "claim IDs"),
            (
                tuple(item.missing_request_id for item in self.missing_evidence),
                "missing-evidence request IDs",
            ),
        )
        for values, label in collections:
            require_unique(values, label)
        if set(self.supporting_evidence_ids) & set(self.contradictory_evidence_ids):
            raise ValueError("supporting and contradictory evidence must be disjoint")
        allowed_ids = set(self.supporting_evidence_ids) | set(
            self.contradictory_evidence_ids
        )
        for claim in self.evidence_claims:
            for citation in claim.citations:
                if citation.evidence_id not in allowed_ids:
                    raise ValueError("claim citation is absent from opinion evidence IDs")
                if (
                    citation.role is CitationRole.SUPPORTS
                    and citation.evidence_id not in self.supporting_evidence_ids
                ):
                    raise ValueError("support citation must reference supporting evidence")
                if (
                    citation.role is CitationRole.CONTRADICTS
                    and citation.evidence_id not in self.contradictory_evidence_ids
                ):
                    raise ValueError(
                        "contradicting citation must reference contradictory evidence"
                    )
        if self.usage.llm_calls > 0 and self.model_identity is None:
            raise ValueError("LLM usage requires model identity")
        if self.usage.llm_calls == 0 and self.model_identity is not None:
            raise ValueError("model identity requires recorded LLM usage")
        if self.prompt_version is not None and self.model_identity is None:
            raise ValueError("prompt version requires model identity")
        if (
            self.status in {AgentRunStatus.SUCCESS, AgentRunStatus.PARTIAL}
            and not self.evidence_claims
            and self.legacy_opinion is None
        ):
            raise ValueError("successful A3 opinion requires evidence claims")
        return self


class AgentFailure(ContractModel):
    """Sanitized typed failure retained without inventing an opinion."""

    error_type: NonEmptyStr
    detail: NonEmptyStr
    retryable: bool = False


class AgentRunRecord(ContractModel):
    """Immutable audit record for exactly one specialist invocation."""

    record_id: NonEmptyStr
    request: AgentRequest
    evidence_pack: AgentEvidencePack
    specialist: SpecialistId
    specialist_version: NonEmptyStr
    status: AgentRunStatus
    opinion: AgentOpinionV2 | None = None
    failure: AgentFailure | None = None
    usage: AgentUsage
    started_at: TiafDateTime
    completed_at: TiafDateTime
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_record(self) -> Self:
        if self.completed_at < self.started_at:
            raise ValueError("completed_at cannot predate started_at")
        if self.specialist is not self.request.specialist:
            raise ValueError("run specialist must match request")
        infrastructure_failure = self.status in {
            AgentRunStatus.BUDGET_EXCEEDED,
            AgentRunStatus.TIMEOUT,
            AgentRunStatus.FAILED,
        }
        if infrastructure_failure:
            if self.failure is None or self.opinion is not None:
                raise ValueError("infrastructure failure requires failure and no opinion")
        elif self.failure is not None:
            raise ValueError("non-failure status cannot carry infrastructure failure")
        evidence_matches = (
            self.evidence_pack.request_id == self.request.request_id
            and self.evidence_pack.subject == self.request.subject
            and self.evidence_pack.evidence_fingerprint == self.request.evidence_fingerprint
            and self.evidence_pack.deterministic_assessment_id
            == self.request.deterministic_baseline_reference
        )
        is_evidence_failure = (
            self.status is AgentRunStatus.FAILED
            and self.failure is not None
            and self.failure.error_type == "AgentEvidenceError"
        )
        if not evidence_matches and not is_evidence_failure:
            raise ValueError("run evidence pack must preserve request and A2 identity")
        if self.status in {
            AgentRunStatus.SUCCESS,
            AgentRunStatus.PARTIAL,
            AgentRunStatus.ABSTAINED,
        }:
            if self.opinion is None:
                raise ValueError("successful/partial/abstained run requires an opinion")
        if self.opinion is not None:
            opinion = self.opinion
            if (
                opinion.request_id != self.request.request_id
                or opinion.run_id != self.request.run_id
                or opinion.specialist is not self.specialist
                or opinion.specialist_version != self.specialist_version
                or opinion.subject != self.request.subject
                or opinion.horizon != self.request.horizon
                or opinion.deterministic_baseline_reference
                != self.request.deterministic_baseline_reference
                or opinion.evidence_fingerprint != self.request.evidence_fingerprint
                or opinion.status is not self.status
                or opinion.usage != self.usage
            ):
                raise ValueError("run opinion projection must match request and record")
            supplied_ids = {item.evidence_id for item in self.evidence_pack.references}
            opinion_ids = set(opinion.supporting_evidence_ids) | set(
                opinion.contradictory_evidence_ids
            )
            cited_ids = {
                citation.evidence_id
                for claim in opinion.evidence_claims
                for citation in claim.citations
            }
            if not opinion_ids <= supplied_ids or not cited_ids <= supplied_ids:
                raise ValueError("run opinion evidence must exist in embedded pack")
            if (
                opinion.evidence_quality is not self.evidence_pack.overall_quality
                or opinion.evidence_freshness is not self.evidence_pack.overall_freshness
                or opinion.confidence.evidence_coverage
                != self.evidence_pack.evidence_coverage
            ):
                raise ValueError("run opinion must preserve pack quality and coverage")
            if any(
                item.capability not in self.request.allowed_capabilities
                for item in opinion.missing_evidence
            ):
                raise ValueError("run opinion contains unauthorized evidence request")
        if not infrastructure_failure and self.request.budget.violations(self.usage):
            raise ValueError("non-failure run usage must remain within request budget")
        return self


class ReasoningRequest(ContractModel):
    """Structured provider invocation assembled only by the A3.2 gateway."""

    reasoning_request_id: NonEmptyStr
    run_id: NonEmptyStr
    specialist: SpecialistId
    model_identity: ReasoningModelIdentity
    prompt_version: NonEmptyStr
    evidence_fingerprint: Sha256Fingerprint
    output_schema_id: NonEmptyStr
    max_input_tokens: int = Field(ge=0)
    max_output_tokens: int = Field(ge=0)
    timeout_seconds: PositiveFiniteFloat
    created_at: TiafDateTime
    subject: Symbol | None = None
    horizon: Horizon | None = None
    task: NonEmptyStr | None = None
    structured_instructions: tuple["ReasoningField", ...] = ()
    model_tier: NonEmptyStr | None = None
    allowed_model_capabilities: tuple[NonEmptyStr, ...] = ()
    policy_version: NonEmptyStr | None = None
    specialist_version: NonEmptyStr | None = None
    temperature: FiniteFloat | None = None
    correlation_id: NonEmptyStr | None = None


class ReasoningField(ContractModel):
    """One named structured response field."""

    name: NonEmptyStr
    value: JsonValue

    @model_validator(mode="after")
    def reject_secret_fields(self) -> Self:
        validate_no_secrets({self.name: self.value})
        return self


class ReasoningResponse(ContractModel):
    """SDK-neutral structured response and exact usage/failure state."""

    response_id: NonEmptyStr
    reasoning_request_id: NonEmptyStr
    provider_id: NonEmptyStr
    model_id: NonEmptyStr
    status: ReasoningStatus
    fields: tuple[ReasoningField, ...] = ()
    usage: AgentUsage
    completed_at: TiafDateTime
    finish_reason: NonEmptyStr | None = None
    failure: AgentFailure | None = None

    @model_validator(mode="after")
    def validate_response(self) -> Self:
        names = tuple(item.name for item in self.fields)
        require_unique(names, "reasoning response field names")
        if self.status is ReasoningStatus.SUCCESS:
            if not self.fields or self.failure is not None:
                raise ValueError("successful reasoning requires fields and no failure")
        elif self.failure is None or self.fields:
            raise ValueError("failed reasoning requires failure and no output fields")
        return self
