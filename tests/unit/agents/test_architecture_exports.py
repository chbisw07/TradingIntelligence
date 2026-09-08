"""A3.1 public exports and strict authority-boundary tests."""

import ast
from pathlib import Path

import pytest
from pydantic import ValidationError

import tiaf.agents as agents
from tiaf.agents import AgentCapability, AgentStance, SpecialistId
from tiaf.agents.models import ReasoningField
from tiaf.contracts import AgentOpinion as AgentOpinionV1


def test_all_accepted_specialist_identities_are_stable() -> None:
    assert tuple(item.value for item in SpecialistId) == (
        "TECHNICAL",
        "FUNDAMENTAL",
        "NEWS_EVENT",
        "RELATIVE_STRENGTH",
        "SECTOR",
        "MACRO",
        "DERIVATIVES_CONTEXT",
        "OPPORTUNITY_RISK",
        "CONTRARIAN_HYPOTHESIS",
        "FORECAST_INTERPRETATION",
    )


def test_capabilities_are_only_controlled_read_or_request_contracts() -> None:
    assert tuple(item.value for item in AgentCapability) == (
        "READ_A2_EVIDENCE",
        "READ_FUNDAMENTALS",
        "READ_FILINGS",
        "READ_NEWS",
        "READ_SECTOR_CONTEXT",
        "READ_MACRO_CONTEXT",
        "READ_DERIVATIVES",
        "READ_FORECAST",
        "REQUEST_ADDITIONAL_MARKET_EVIDENCE",
    )
    assert not any(
        forbidden in item.value
        for item in AgentCapability
        for forbidden in ("UNRESTRICTED", "SHELL", "BROKER", "EXECUTION", "ORDER")
    )


def test_agent_stances_contain_no_later_layer_actions() -> None:
    assert set(AgentStance) == {
        AgentStance.POSITIVE,
        AgentStance.NEGATIVE,
        AgentStance.NEUTRAL,
        AgentStance.MIXED,
        AgentStance.INSUFFICIENT_EVIDENCE,
        AgentStance.ABSTAIN,
    }
    assert not set(item.value for item in AgentStance) & {
        "BUY",
        "SELL",
        "CE",
        "PE",
        "HOLD",
        "EXIT",
    }


def test_agent_package_has_no_provider_network_broker_llm_or_langgraph_imports() -> None:
    root = Path("src/tiaf/agents")
    forbidden_roots = {
        "anthropic",
        "httpx",
        "langchain",
        "langgraph",
        "openai",
        "requests",
        "socket",
        "subprocess",
    }
    forbidden_tiaf = {
        "tiaf.contracts.options",
        "tiaf.data.providers",
        "tiaf.providers",
    }
    forbidden_imported_names = {
        "DirectionPolicy",
        "OpportunityAction",
        "OptionExpression",
        "OptionType",
        "PositionAction",
    }
    violations: list[str] = []
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in forbidden_roots:
                        violations.append(f"{path}:{alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.split(".")[0] in forbidden_roots or module in forbidden_tiaf:
                    violations.append(f"{path}:{module}")
                for alias in node.names:
                    if alias.name in forbidden_imported_names:
                        violations.append(f"{path}:{module}.{alias.name}")
    assert violations == []


def test_runtime_has_no_specialist_specific_branching() -> None:
    source = Path("src/tiaf/agents/runtime.py").read_text()
    assert not any(f"SpecialistId.{item.name}" in source for item in SpecialistId)


def test_a0_agent_opinion_public_contract_remains_unchanged() -> None:
    assert agents.AgentOpinionV2.__name__ != AgentOpinionV1.__name__
    assert AgentOpinionV1.model_fields["schema_version"].default == "1.0"
    assert AgentOpinionV1.__module__ == "tiaf.contracts.opinions"


def test_expected_agent_foundation_symbols_are_public() -> None:
    expected = {
        "AgentRequest",
        "AgentEvidencePack",
        "EvidenceClaim",
        "MissingEvidenceRequest",
        "AgentOpinionV2",
        "SpecialistAgent",
        "AgentRegistry",
        "AgentBudget",
        "AgentUsage",
        "ReasoningProvider",
        "AgentRuntime",
        "AgentRunRecord",
        "ForecastEvidence",
    }
    assert expected <= set(agents.__all__)
    assert all(hasattr(agents, name) for name in expected)


def test_agent_structured_fields_and_metadata_reject_credential_keys() -> None:
    with pytest.raises(ValidationError, match="secret-bearing"):
        ReasoningField(name="payload", value={"api_key": "not-allowed"})
    with pytest.raises(ValidationError, match="secret-bearing"):
        agents.AgentBudget(metadata={"nested": {"client_id": "not-allowed"}})
