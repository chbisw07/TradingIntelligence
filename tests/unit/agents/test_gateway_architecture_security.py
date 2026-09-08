"""Architecture and complete no-LLM acceptance checks for A3.2."""

import ast
from pathlib import Path

from tiaf.agents import (
    A2EvidenceGateway,
    AgentBudget,
    EvidenceGatewayRegistry,
    EvidenceGatewayRuntime,
    EvidenceGatewayStatus,
    ModelTier,
    ReasoningGateway,
    ReasoningGatewayPolicy,
    ReasoningGatewayStatus,
    ReasoningProviderRegistry,
)

from ._gateway_support import a2_entry, evidence_policy, evidence_request, reasoning_request
from ._support import NOW, evidence_pack

GATEWAY_ROOT = Path("src/tiaf/agents/gateways")
FORBIDDEN_IMPORT_PREFIXES = (
    "tiaf.data.providers",
    "dhanhq",
    "openai",
    "anthropic",
    "langgraph",
    "requests",
    "httpx",
    "subprocess",
)
FORBIDDEN_CALLS = {"open", "exec", "eval", "compile", "system", "popen"}


def _imports(path: Path) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(item.name for item in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return tuple(names)


def test_gateway_layer_has_no_broker_http_vendor_langgraph_or_subprocess_imports() -> None:
    for path in GATEWAY_ROOT.glob("*.py"):
        for imported in _imports(path):
            assert not imported.startswith(FORBIDDEN_IMPORT_PREFIXES), (path, imported)


def test_gateway_layer_has_no_arbitrary_file_shell_or_code_execution_calls() -> None:
    for path in GATEWAY_ROOT.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        assert not calls & FORBIDDEN_CALLS, (path, calls & FORBIDDEN_CALLS)


def test_no_wildcard_capability_exists() -> None:
    from tiaf.agents import AgentCapability

    assert "ALL_ACCESS" not in {item.value for item in AgentCapability}
    assert all("WILDCARD" not in item.value for item in AgentCapability)


def test_evidence_request_contract_has_no_transport_escape_fields() -> None:
    fields = set(type(evidence_request()).model_fields)
    assert not fields & {"url", "uri", "shell", "command", "sql", "query", "headers"}


def test_reasoning_request_has_no_credentials_or_unrestricted_tools() -> None:
    fields = set(type(reasoning_request()).model_fields)
    assert not fields & {
        "credentials",
        "access_token",
        "authorization",
        "broker_account",
        "tools",
        "url",
    }


def test_no_llm_workflow_retrieves_a2_audits_and_preserves_baseline() -> None:
    baseline = evidence_pack()
    before = baseline.model_dump(mode="json")
    evidence_runtime = EvidenceGatewayRuntime(
        EvidenceGatewayRegistry((A2EvidenceGateway((a2_entry(pack=baseline),)),)),
        evidence_policy(),
        wall_clock=lambda: NOW,
        elapsed_clock=lambda: 0.0,
    )
    evidence_run = evidence_runtime.fetch(evidence_request())
    reasoning = ReasoningGateway(
        ReasoningProviderRegistry(),
        ReasoningGatewayPolicy(
            enabled=False,
            default_model_tier=ModelTier.NONE,
            max_model_tier=ModelTier.NONE,
            allowed_model_tiers=(ModelTier.NONE,),
            budget=AgentBudget(),
        ),
        wall_clock=lambda: NOW,
        elapsed_clock=lambda: 0.0,
    ).reason(reasoning_request())
    assert evidence_run.result.status is EvidenceGatewayStatus.SUCCESS
    assert evidence_run.audit.evidence_fingerprint == baseline.evidence_fingerprint
    assert reasoning.result.status is ReasoningGatewayStatus.MODEL_DISABLED
    assert reasoning.result.usage.llm_calls == 0
    assert reasoning.result.usage.input_tokens == 0
    assert reasoning.result.usage.output_tokens == 0
    assert reasoning.result.usage.cost_units == 0
    assert baseline.model_dump(mode="json") == before


def test_gateway_runtime_uses_registry_resolution_not_capability_branching() -> None:
    source = Path("src/tiaf/agents/gateways/runtime.py").read_text(encoding="utf-8")
    assert "self._registry.resolve" in source
    assert "READ_A2_EVIDENCE" not in source
