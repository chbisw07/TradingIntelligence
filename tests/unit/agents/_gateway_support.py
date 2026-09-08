"""Shared controlled-gateway fixtures and fakes for A3.2 tests."""

from datetime import timedelta

from tiaf.agents import (
    A2EvidenceEntry,
    AgentBudget,
    AgentCapability,
    AgentEvidencePack,
    AgentUsage,
    EvidenceGatewayPolicy,
    EvidenceGatewayRequest,
    ModelCapability,
    ModelTier,
    ModelTierMapping,
    ReasoningField,
    ReasoningGatewayPolicy,
    ReasoningGatewayRequest,
    ReasoningModelIdentity,
    ReasoningRequest,
    ReasoningResponse,
    ReasoningStatus,
    SpecialistId,
)
from tiaf.context import AnalysisPurpose
from tiaf.contracts import EvidenceType, FreshnessState, Horizon
from tiaf.data import InstrumentType

from ._support import FINGERPRINT, NOW, evidence_pack


def gateway_budget(**changes: object) -> AgentBudget:
    payload: dict[str, object] = {
        "max_llm_calls": 1,
        "max_tool_calls": 1,
        "max_input_tokens": 100,
        "max_output_tokens": 40,
        "max_total_tokens": 140,
        "max_cost_units": 5.0,
        "max_elapsed_seconds": 2.0,
    }
    payload.update(changes)
    return AgentBudget.model_validate(payload)


def evidence_request(**changes: object) -> EvidenceGatewayRequest:
    payload: dict[str, object] = {
        "request_id": "gateway-request-1",
        "capability": AgentCapability.READ_A2_EVIDENCE,
        "allowed_capabilities": (AgentCapability.READ_A2_EVIDENCE,),
        "subject": "RELIANCE",
        "instrument_type": InstrumentType.EQUITY,
        "horizon": Horizon(label="positional", min_days=2, max_days=20),
        "purpose": AnalysisPurpose.OPPORTUNITY,
        "evidence_type": EvidenceType.TECHNICAL,
        "requested_attributes": ("market_structure",),
        "as_of": NOW,
        "required_freshness": FreshnessState.FRESH,
        "context_references": ("context-1",),
        "evidence_fingerprint": FINGERPRINT,
        "deterministic_baseline_reference": "a2-assessment-1",
        "requesting_specialist": SpecialistId.TECHNICAL,
        "correlation_id": "correlation-1",
        "budget": gateway_budget(),
        "timeout_seconds": 1.0,
    }
    payload.update(changes)
    return EvidenceGatewayRequest.model_validate(payload)


def a2_entry(*, pack: AgentEvidencePack | None = None) -> A2EvidenceEntry:
    return A2EvidenceEntry(
        evidence_pack=pack or evidence_pack(),
        valid_until=NOW + timedelta(hours=1),
    )


def evidence_policy() -> EvidenceGatewayPolicy:
    return EvidenceGatewayPolicy(
        enabled_capabilities=(AgentCapability.READ_A2_EVIDENCE,)
    )


def model_mapping(
    *,
    tier: ModelTier = ModelTier.LIGHTWEIGHT,
    provider_id: str = "fake-provider",
    model_id: str = "fake-model",
) -> ModelTierMapping:
    return ModelTierMapping(
        tier=tier,
        provider_id=provider_id,
        model_id=model_id,
        model_version="2026-01",
        configuration_id="config-1",
        configuration=(ReasoningField(name="temperature_policy", value="bounded"),),
    )


def reasoning_policy(**changes: object) -> ReasoningGatewayPolicy:
    payload: dict[str, object] = {
        "enabled": True,
        "default_model_tier": ModelTier.LIGHTWEIGHT,
        "max_model_tier": ModelTier.STANDARD,
        "allowed_model_tiers": (
            ModelTier.NONE,
            ModelTier.LIGHTWEIGHT,
            ModelTier.STANDARD,
        ),
        "allowed_model_capabilities": (ModelCapability.STRUCTURED_REASONING,),
        "model_mappings": (
            model_mapping(),
            model_mapping(tier=ModelTier.STANDARD),
        ),
        "budget": gateway_budget(),
    }
    payload.update(changes)
    return ReasoningGatewayPolicy.model_validate(payload)


def reasoning_request(**changes: object) -> ReasoningGatewayRequest:
    payload: dict[str, object] = {
        "reasoning_request_id": "reasoning-request-1",
        "run_id": "run-1",
        "specialist": SpecialistId.TECHNICAL,
        "specialist_version": "1.0",
        "subject": "RELIANCE",
        "horizon": Horizon(label="positional", min_days=2, max_days=20),
        "task": "Interpret only the supplied A2 structure.",
        "instructions": (
            ReasoningField(name="purpose", value="return structured interpretation"),
        ),
        "evidence_references": evidence_pack().references,
        "evidence_fingerprint": FINGERPRINT,
        "requested_model_tier": ModelTier.LIGHTWEIGHT,
        "allowed_model_capabilities": (ModelCapability.STRUCTURED_REASONING,),
        "budget": gateway_budget(),
        "prompt_version": "technical-prompt-1",
        "policy_version": "reasoning-policy-1",
        "output_schema_id": "test.summary.v1",
        "estimated_input_tokens": 20,
        "temperature": 0.0,
        "timeout_seconds": 1.0,
        "correlation_id": "correlation-1",
        "created_at": NOW,
    }
    payload.update(changes)
    return ReasoningGatewayRequest.model_validate(payload)


class FakeReasoningProvider:
    def __init__(
        self,
        *,
        response: ReasoningResponse | None = None,
        error: Exception | None = None,
    ) -> None:
        self.calls = 0
        self.last_request: ReasoningRequest | None = None
        self._response = response
        self._error = error

    def identity(self) -> ReasoningModelIdentity:
        return ReasoningModelIdentity(
            provider_id="fake-provider",
            model_id="fake-model",
            model_version="2026-01",
            configuration_id="config-1",
        )

    def reason(self, request: ReasoningRequest) -> ReasoningResponse:
        self.calls += 1
        self.last_request = request
        if self._error is not None:
            raise self._error
        if self._response is not None:
            return self._response
        return ReasoningResponse(
            response_id="provider-response-1",
            reasoning_request_id="reasoning-request-1",
            provider_id="fake-provider",
            model_id="fake-model",
            status=ReasoningStatus.SUCCESS,
            fields=(ReasoningField(name="summary", value="structured"),),
            usage=AgentUsage(
                llm_calls=1,
                input_tokens=20,
                output_tokens=3,
                cost_units=0.25,
            ),
            completed_at=NOW,
            finish_reason="STOP",
        )


def summary_validator(fields: tuple[ReasoningField, ...]) -> bool:
    return len(fields) == 1 and fields[0].name == "summary"
