"""A3.2 optional reasoning, mapping, validation, timeout, and budget tests."""

from time import sleep

import pytest
from pydantic import ValidationError

from tiaf.agents import (
    AgentBudget,
    AgentUsage,
    DowngradePolicy,
    ModelTier,
    ReasoningField,
    ReasoningGateway,
    ReasoningGatewayPolicy,
    ReasoningGatewayRequest,
    ReasoningGatewayStatus,
    ReasoningProviderRegistry,
    ReasoningRequest,
    ReasoningResponse,
    ReasoningStatus,
)

from ._gateway_support import (
    FakeReasoningProvider,
    gateway_budget,
    model_mapping,
    reasoning_policy,
    reasoning_request,
    summary_validator,
)
from ._support import NOW


def configured_gateway(
    provider: FakeReasoningProvider | None = None,
    *,
    policy: ReasoningGatewayPolicy | None = None,
) -> tuple[ReasoningGateway, FakeReasoningProvider]:
    selected = provider or FakeReasoningProvider()
    registry = ReasoningProviderRegistry()
    registry.register(
        selected,
        supported_tiers=(ModelTier.LIGHTWEIGHT, ModelTier.STANDARD),
    )
    return (
        ReasoningGateway(
            registry,
            policy or reasoning_policy(),
            output_validators={"test.summary.v1": summary_validator},
            wall_clock=lambda: NOW,
            elapsed_clock=lambda: 0.0,
        ),
        selected,
    )


def test_no_llm_tier_returns_explicit_disabled_result_and_zero_usage() -> None:
    gateway, provider = configured_gateway()
    run = gateway.reason(reasoning_request(requested_model_tier=ModelTier.NONE))
    assert run.result.status is ReasoningGatewayStatus.MODEL_DISABLED
    assert run.result.actual_model_tier is ModelTier.NONE
    assert run.result.usage == AgentUsage()
    assert provider.calls == 0


def test_globally_disabled_reasoning_makes_zero_model_calls() -> None:
    policy = ReasoningGatewayPolicy(
        enabled=False,
        default_model_tier=ModelTier.NONE,
        max_model_tier=ModelTier.NONE,
        allowed_model_tiers=(ModelTier.NONE,),
        budget=AgentBudget(),
    )
    gateway, provider = configured_gateway(policy=policy)
    run = gateway.reason(reasoning_request())
    assert run.result.status is ReasoningGatewayStatus.MODEL_DISABLED
    assert run.result.downgrade_reason == "reasoning is globally disabled"
    assert provider.calls == 0
    assert run.audit.usage.input_tokens == 0
    assert run.audit.usage.cost_units == 0


def test_enabled_reasoning_preserves_structured_output_and_version_identity() -> None:
    gateway, provider = configured_gateway()
    request = reasoning_request()
    run = gateway.reason(request)
    assert run.result.status is ReasoningGatewayStatus.SUCCESS
    assert run.result.fields == (ReasoningField(name="summary", value="structured"),)
    assert run.result.provider_identity == provider.identity()
    assert run.result.requested_model_tier is ModelTier.LIGHTWEIGHT
    assert run.result.actual_model_tier is ModelTier.LIGHTWEIGHT
    assert run.result.prompt_version == "technical-prompt-1"
    assert run.result.policy_version == "reasoning-policy-1"
    assert run.result.specialist_version == "1.0"
    assert run.result.finish_reason == "STOP"
    assert run.result.cache_key is not None
    assert provider.calls == 1
    assert provider.last_request is not None
    assert provider.last_request.structured_instructions == request.instructions
    assert run.audit.gateway_identity.gateway_id == "tiaf.reasoning-gateway"


def test_reasoning_request_is_frozen_round_trips_and_json_collections_are_arrays() -> None:
    request = reasoning_request()
    payload = request.model_dump(mode="json")
    assert isinstance(payload["instructions"], list)
    assert isinstance(payload["evidence_references"], list)
    assert payload["created_at"].endswith("+05:30")
    assert ReasoningGatewayRequest.model_validate(payload) == request
    with pytest.raises(ValidationError, match="frozen"):
        request.task = "changed"


def test_reasoning_request_rejects_credential_shaped_structured_input() -> None:
    with pytest.raises(ValidationError, match="secret-bearing"):
        reasoning_request(
            instructions=(ReasoningField(name="purpose", value={"password": "x"}),)
        )


def test_reasoning_request_rejects_credential_shaped_text_value() -> None:
    with pytest.raises(ValidationError, match="credential-shaped text"):
        reasoning_request(
            instructions=(
                ReasoningField(name="purpose", value="Authorization: Bearer unsafe"),
            )
        )


def test_reasoning_capability_is_least_privilege_and_prompt_cannot_escalate() -> None:
    gateway, provider = configured_gateway()
    run = gateway.reason(reasoning_request(allowed_model_capabilities=()))
    assert run.result.status is ReasoningGatewayStatus.UNAUTHORIZED_CAPABILITY
    assert provider.calls == 0


def test_request_budget_cannot_exceed_global_policy() -> None:
    gateway, provider = configured_gateway()
    run = gateway.reason(
        reasoning_request(budget=gateway_budget(max_cost_units=6.0))
    )
    assert run.result.status is ReasoningGatewayStatus.INVALID_REQUEST
    assert provider.calls == 0


@pytest.mark.parametrize(
    ("budget", "expected_detail"),
    [
        (gateway_budget(max_llm_calls=0), "LLM call budget"),
        (gateway_budget(max_input_tokens=10, max_total_tokens=50), "estimated input"),
        (gateway_budget(max_output_tokens=0), "output-token budget"),
        (
            gateway_budget(max_input_tokens=100, max_total_tokens=20),
            "total-token budget",
        ),
        (gateway_budget(max_elapsed_seconds=0.5), "timeout"),
    ],
)
def test_budget_precheck_rejects_before_provider(
    budget: AgentBudget,
    expected_detail: str,
) -> None:
    gateway, provider = configured_gateway()
    run = gateway.reason(reasoning_request(budget=budget))
    assert run.result.status is ReasoningGatewayStatus.BUDGET_EXCEEDED
    assert run.result.failure is not None
    assert expected_detail in run.result.failure.detail
    assert provider.calls == 0


@pytest.mark.parametrize(
    ("usage", "violation"),
    [
        (AgentUsage(llm_calls=2), "llm_calls"),
        (AgentUsage(llm_calls=1, input_tokens=101), "input_tokens"),
        (AgentUsage(llm_calls=1, output_tokens=41), "output_tokens"),
        (AgentUsage(llm_calls=1, input_tokens=90, output_tokens=60), "total_tokens"),
        (AgentUsage(llm_calls=1, cost_units=5.1), "cost_units"),
        (AgentUsage(llm_calls=1, elapsed_seconds=2.1), "elapsed_seconds"),
    ],
)
def test_post_run_budget_overrun_preserves_true_usage(
    usage: AgentUsage,
    violation: str,
) -> None:
    response = ReasoningResponse(
        response_id="provider-response-1",
        reasoning_request_id="reasoning-request-1",
        provider_id="fake-provider",
        model_id="fake-model",
        status=ReasoningStatus.SUCCESS,
        fields=(ReasoningField(name="summary", value="structured"),),
        usage=usage,
        completed_at=NOW,
    )
    gateway, _ = configured_gateway(FakeReasoningProvider(response=response))
    run = gateway.reason(reasoning_request())
    expected = (
        ReasoningGatewayStatus.TIMEOUT
        if violation == "elapsed_seconds"
        else ReasoningGatewayStatus.BUDGET_EXCEEDED
    )
    assert run.result.status is expected
    assert run.result.usage == usage
    assert run.result.failure is not None
    assert violation in run.result.failure.detail


def test_invalid_structured_output_records_usage_but_rejects_fields() -> None:
    response = ReasoningResponse(
        response_id="provider-response-1",
        reasoning_request_id="reasoning-request-1",
        provider_id="fake-provider",
        model_id="fake-model",
        status=ReasoningStatus.SUCCESS,
        fields=(ReasoningField(name="unexpected", value="prose"),),
        usage=AgentUsage(llm_calls=1, input_tokens=5, output_tokens=2, cost_units=0.1),
        completed_at=NOW,
    )
    gateway, _ = configured_gateway(FakeReasoningProvider(response=response))
    run = gateway.reason(reasoning_request())
    assert run.result.status is ReasoningGatewayStatus.MODEL_OUTPUT_INVALID
    assert run.result.fields == ()
    assert run.result.usage.cost_units == 0.1


def test_provider_failure_is_not_a_market_stance() -> None:
    gateway, _ = configured_gateway(
        FakeReasoningProvider(error=RuntimeError("vendor internals"))
    )
    run = gateway.reason(reasoning_request())
    assert run.result.status is ReasoningGatewayStatus.PROVIDER_FAILURE
    assert run.result.failure is not None
    assert run.result.failure.detail == "provider raised unexpected RuntimeError"


def test_reasoning_timeout_is_explicit() -> None:
    class SlowProvider(FakeReasoningProvider):
        def reason(self, request: ReasoningRequest) -> ReasoningResponse:
            sleep(0.05)
            return super().reason(request)

    gateway, _ = configured_gateway(SlowProvider())
    run = gateway.reason(reasoning_request(timeout_seconds=0.001))
    assert run.result.status is ReasoningGatewayStatus.TIMEOUT
    assert run.result.fields == ()


def test_unregistered_schema_rejects_before_model_call() -> None:
    gateway, provider = configured_gateway()
    run = gateway.reason(reasoning_request(output_schema_id="unknown.schema"))
    assert run.result.status is ReasoningGatewayStatus.INVALID_REQUEST
    assert provider.calls == 0


def test_explicit_downgrade_preserves_requested_actual_tier_and_reason() -> None:
    policy = reasoning_policy(
        max_model_tier=ModelTier.LIGHTWEIGHT,
        allowed_model_tiers=(ModelTier.NONE, ModelTier.LIGHTWEIGHT),
        model_mappings=(model_mapping(),),
        downgrade_policy=DowngradePolicy.DOWNGRADE,
    )
    gateway, _ = configured_gateway(policy=policy)
    run = gateway.reason(reasoning_request(requested_model_tier=ModelTier.DEEP))
    assert run.result.status is ReasoningGatewayStatus.SUCCESS
    assert run.result.requested_model_tier is ModelTier.DEEP
    assert run.result.actual_model_tier is ModelTier.LIGHTWEIGHT
    assert "downgraded" in (run.result.downgrade_reason or "")


def test_no_llm_fallback_is_explicit_when_tier_unavailable() -> None:
    policy = reasoning_policy(downgrade_policy=DowngradePolicy.NO_LLM_FALLBACK)
    gateway, provider = configured_gateway(policy=policy)
    run = gateway.reason(reasoning_request(requested_model_tier=ModelTier.DEEP))
    assert run.result.status is ReasoningGatewayStatus.MODEL_DISABLED
    assert run.result.actual_model_tier is ModelTier.NONE
    assert run.result.downgrade_reason is not None
    assert provider.calls == 0


def test_fail_policy_does_not_silently_downgrade() -> None:
    gateway, provider = configured_gateway()
    run = gateway.reason(reasoning_request(requested_model_tier=ModelTier.DEEP))
    assert run.result.status is ReasoningGatewayStatus.UNAVAILABLE
    assert run.result.actual_model_tier is ModelTier.DEEP
    assert run.result.downgrade_reason is None
    assert provider.calls == 0


def test_changed_model_mapping_requires_no_request_or_specialist_change() -> None:
    request = reasoning_request(requested_model_tier=ModelTier.STANDARD)
    gateway, _ = configured_gateway()
    run = gateway.reason(request)
    assert run.result.actual_model_tier is ModelTier.STANDARD
    assert run.result.provider_identity is not None
    assert run.result.provider_identity.model_id == "fake-model"
