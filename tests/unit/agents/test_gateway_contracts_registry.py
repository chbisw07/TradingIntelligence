"""A3.2 contract, registry, immutability, and cache-key tests."""

from datetime import UTC, datetime
from typing import cast

import pytest
from pydantic import ValidationError

from tiaf.agents import (
    A2EvidenceGateway,
    AgentCapability,
    EvidenceGateway,
    EvidenceGatewayRegistry,
    EvidenceGatewayRequest,
    GatewayRegistrationError,
    ModelTier,
    ModelTierMapping,
    ReasoningField,
    ReasoningProviderRegistry,
    evidence_cache_key,
    reasoning_cache_key,
)

from ._gateway_support import (
    FakeReasoningProvider,
    a2_entry,
    evidence_request,
    model_mapping,
)


def test_gateway_request_is_frozen_and_semantic_collections_are_tuples() -> None:
    request = evidence_request(
        allowed_capabilities=["READ_A2_EVIDENCE"],
        requested_attributes=["market_structure"],
    )
    assert request.allowed_capabilities == (AgentCapability.READ_A2_EVIDENCE,)
    assert request.requested_attributes == ("market_structure",)
    with pytest.raises(ValidationError, match="frozen"):
        request.subject = "HDFCBANK"
    with pytest.raises(AttributeError):
        request.requested_attributes.append("rsi")  # type: ignore[attr-defined]


def test_gateway_request_json_round_trip_uses_arrays_and_kolkata_time() -> None:
    request = evidence_request(as_of=datetime(2026, 9, 8, 6, 30, tzinfo=UTC))
    payload = request.model_dump(mode="json")
    assert isinstance(payload["allowed_capabilities"], list)
    assert payload["as_of"].endswith("+05:30")
    assert EvidenceGatewayRequest.model_validate(payload) == request


@pytest.mark.parametrize("field", ["start_at", "end_at"])
def test_gateway_request_requires_complete_time_range(field: str) -> None:
    with pytest.raises(ValidationError, match="both bounds"):
        evidence_request(**{field: datetime(2026, 9, 7, tzinfo=UTC)})


def test_evidence_registry_registers_discovers_and_resolves() -> None:
    gateway = A2EvidenceGateway((a2_entry(),))
    registry = EvidenceGatewayRegistry((gateway,))
    assert isinstance(gateway, EvidenceGateway)
    assert registry.identities() == (gateway.identity(),)
    assert registry.capabilities() == (AgentCapability.READ_A2_EVIDENCE,)
    assert registry.resolve(evidence_request()) is gateway


def test_evidence_registry_rejects_duplicate_gateway_id() -> None:
    registry = EvidenceGatewayRegistry((A2EvidenceGateway((a2_entry(),)),))
    with pytest.raises(GatewayRegistrationError, match="duplicate gateway ID"):
        registry.register(A2EvidenceGateway((a2_entry(),)))


def test_evidence_registry_requires_explicit_conflict_resolution() -> None:
    first = A2EvidenceGateway((a2_entry(),), gateway_id="a")
    second = A2EvidenceGateway((a2_entry(),), gateway_id="b")
    registry = EvidenceGatewayRegistry((first, second))
    with pytest.raises(GatewayRegistrationError, match="ambiguous"):
        registry.resolve(evidence_request())
    assert registry.resolve(evidence_request(), gateway_id="b") is second


def test_test_only_gateway_proves_registry_extensibility_without_runtime_change() -> None:
    gateway = A2EvidenceGateway(
        (a2_entry(),), gateway_id="custom-test-gateway", gateway_version="9"
    )
    registry = EvidenceGatewayRegistry()
    registry.register(cast(EvidenceGateway, gateway))
    assert registry.get("custom-test-gateway") is gateway


def test_reasoning_provider_registry_is_deterministic_and_rejects_duplicates() -> None:
    provider = FakeReasoningProvider()
    registry = ReasoningProviderRegistry()
    registry.register(provider, supported_tiers=(ModelTier.LIGHTWEIGHT,))
    assert registry.registrations()[0].identity.provider_id == "fake-provider"
    with pytest.raises(GatewayRegistrationError, match="duplicate"):
        registry.register(provider, supported_tiers=(ModelTier.LIGHTWEIGHT,))


def test_model_mapping_rejects_none_and_mutable_configuration_input_becomes_tuple() -> None:
    mapping = model_mapping()
    assert isinstance(mapping.configuration, tuple)
    with pytest.raises(ValidationError, match="NONE"):
        ModelTierMapping(
            tier=ModelTier.NONE,
            provider_id="fake",
            model_id="none",
            configuration_id="none",
        )


def test_evidence_cache_key_ignores_request_bookkeeping_not_semantics() -> None:
    original = evidence_request()
    same = evidence_request(
        request_id="gateway-request-2",
        correlation_id="different",
        budget=original.budget.model_copy(update={"max_tool_calls": 2}),
    )
    changed = evidence_request(subject="HDFCBANK")
    assert evidence_cache_key(original) == evidence_cache_key(same)
    assert evidence_cache_key(original) != evidence_cache_key(changed)


def test_reasoning_cache_key_changes_with_replay_relevant_identity() -> None:
    mapping = model_mapping()
    identity = FakeReasoningProvider().identity()
    first = reasoning_cache_key(
        task="task",
        evidence_fingerprint="a" * 64,
        model_identity=identity,
        model_tier=ModelTier.LIGHTWEIGHT,
        prompt_version="p1",
        policy_version="policy1",
        specialist_version="s1",
        output_schema_id="schema1",
        model_configuration=mapping.configuration,
    )
    second = reasoning_cache_key(
        task="task",
        evidence_fingerprint="b" * 64,
        model_identity=identity,
        model_tier=ModelTier.LIGHTWEIGHT,
        prompt_version="p1",
        policy_version="policy1",
        specialist_version="s1",
        output_schema_id="schema1",
        model_configuration=mapping.configuration,
    )
    assert first != second


@pytest.mark.parametrize("secret_key", ["access_token", "authorization", "api_key"])
def test_gateway_contracts_reject_credential_shaped_metadata(secret_key: str) -> None:
    with pytest.raises(ValidationError, match="secret-bearing"):
        evidence_request(metadata={secret_key: "must-not-enter"})


def test_model_configuration_rejects_credential_shaped_field() -> None:
    with pytest.raises(ValidationError, match="secret-bearing"):
        model_mapping().model_copy(
            update={"configuration": (ReasoningField(name="api_key", value="x"),)}
        )
