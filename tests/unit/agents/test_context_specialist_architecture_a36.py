"""A3.6 separation, authority, replay, and registry acceptance checks."""

import ast
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tiaf.agents import AgentEvidenceReference, AgentRegistry, AgentRuntime, SpecialistId
from tiaf.agents.specialists import MacroSpecialist, RelativeStrengthSpecialist, SectorSpecialist
from tiaf.market_context import MacroContextRequest, SectorContextRequest

from ._contextual_support import pack, request
from .test_macro_specialist_a36 import macro_reference
from .test_relative_specialist_a36 import relative_reference
from .test_sector_specialist_a36 import sector_reference


def test_three_specialists_are_independently_registered_and_versioned() -> None:
    specialists = (RelativeStrengthSpecialist(), SectorSpecialist(), MacroSpecialist())
    capabilities = AgentRegistry(specialists).capabilities()
    assert tuple(item.specialist for item in capabilities) == (
        SpecialistId.MACRO,
        SpecialistId.RELATIVE_STRENGTH,
        SpecialistId.SECTOR,
    )
    assert {item.specialist_version for item in capabilities} == {"1.0"}
    assert all(item.supports_no_llm for item in capabilities)


@pytest.mark.parametrize(
    ("specialist", "evidence"),
    (
        (RelativeStrengthSpecialist(), relative_reference(("1d", 3.0))),
        (SectorSpecialist(), sector_reference()),
        (MacroSpecialist(), macro_reference()),
    ),
)
def test_runtime_preserves_input_and_records_zero_model_usage(
    specialist: Any, evidence: AgentEvidenceReference
) -> None:
    specialist_id = specialist.capability().specialist
    supplied = pack((evidence,))
    before = supplied.model_dump(mode="json")
    record = AgentRuntime(AgentRegistry((specialist,))).run(request(specialist_id), supplied)
    assert record.opinion is not None
    assert record.usage.llm_calls == 0
    assert record.usage.input_tokens == record.usage.output_tokens == 0
    assert record.usage.cost_units == 0
    assert record.evidence_pack.evidence_fingerprint == supplied.evidence_fingerprint
    assert record.opinion.evidence_fingerprint == supplied.evidence_fingerprint
    assert supplied.model_dump(mode="json") == before


def test_context_specialists_contain_no_network_model_shell_or_broker_imports() -> None:
    forbidden = {
        "anthropic",
        "dhanhq",
        "httpx",
        "langchain",
        "langgraph",
        "openai",
        "requests",
        "socket",
        "subprocess",
    }
    violations: list[tuple[Path, str]] = []
    for package in ("relative", "sector", "macro"):
        for path in Path(f"src/tiaf/agents/specialists/{package}").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports = tuple(item.name for item in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports = (node.module or "",)
                else:
                    continue
                violations.extend(
                    (path, item)
                    for item in imports
                    if item.split(".")[0] in forbidden or item.startswith("tiaf.data.providers")
                )
    assert violations == []


def test_context_gateway_requests_have_no_arbitrary_transport_fields() -> None:
    forbidden = {"url", "uri", "query", "headers", "credentials", "command", "shell"}
    assert not set(SectorContextRequest.model_fields) & forbidden
    assert not set(MacroContextRequest.model_fields) & forbidden


def test_context_detail_and_semantic_collections_are_immutable_json_safe() -> None:
    opinion = RelativeStrengthSpecialist().analyze(
        request(SpecialistId.RELATIVE_STRENGTH),
        pack((relative_reference(("1d", 3.0)),)),
    )
    assert isinstance(opinion.model_dump(mode="json")["evidence_claims"], list)
    with pytest.raises(ValidationError):
        setattr(opinion, "stance", opinion.stance)
    with pytest.raises(AttributeError):
        getattr(opinion.reason_codes, "append")("MUTATE")
