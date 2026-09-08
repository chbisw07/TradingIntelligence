"""A3.4 runtime, replay, citation, confidence, and authority acceptance."""

import ast
from pathlib import Path

from tiaf.agents import (
    AgentOpinionV2,
    AgentRegistry,
    AgentRunStatus,
    AgentRuntime,
    BaselineAgreement,
    SpecialistId,
    agent_record_json,
    load_agent_record_json,
)
from tiaf.agents.specialists.fundamental import (
    FUNDAMENTAL_DETAIL_SCHEMA,
    FundamentalAssessment,
    FundamentalSpecialist,
    fundamental_assessment_from_opinion,
)
from tiaf.contracts import DataQuality, FreshnessState, TradeStyle

from ._fundamental_support import fundamental_agent_request, fundamental_pack


def test_registry_runtime_runs_complete_no_llm_fundamental_flow() -> None:
    pack = fundamental_pack()
    request = fundamental_agent_request(pack)
    before = pack.model_dump(mode="json")
    record = AgentRuntime(
        AgentRegistry((FundamentalSpecialist(),)),
        wall_clock=lambda: request.created_at,
        elapsed_clock=lambda: 0.0,
    ).run(request, pack)

    assert record.status is AgentRunStatus.SUCCESS
    assert record.opinion is not None
    assert record.opinion.specialist is SpecialistId.FUNDAMENTAL
    assert record.opinion.baseline_agreement is BaselineAgreement.NOT_COMPARABLE
    assert record.opinion.deterministic_baseline_reference == "a2-assessment"
    assert record.opinion.evidence_fingerprint == pack.evidence_fingerprint
    assert record.usage.llm_calls == 0
    assert record.usage.input_tokens == 0
    assert record.usage.output_tokens == 0
    assert record.usage.cost_units == 0
    assert record.opinion.model_identity is None
    assert pack.model_dump(mode="json") == before
    assert load_agent_record_json(agent_record_json(record)) == record


def test_specialist_detail_round_trips_inside_standard_opinion() -> None:
    pack = fundamental_pack()
    opinion = FundamentalSpecialist().analyze(fundamental_agent_request(pack), pack)
    detail = fundamental_assessment_from_opinion(opinion)
    reconstructed = AgentOpinionV2.model_validate(opinion.model_dump(mode="json"))

    assert opinion.specialist_detail_schema_id == FUNDAMENTAL_DETAIL_SCHEMA
    assert fundamental_assessment_from_opinion(reconstructed) == detail
    assert FundamentalAssessment.model_validate(
        detail.model_dump(mode="json")
    ) == detail


def test_every_interpretive_claim_cites_exact_supplied_fundamental_fact() -> None:
    pack = fundamental_pack()
    opinion = FundamentalSpecialist().analyze(fundamental_agent_request(pack), pack)
    supplied = {item.evidence_id: item for item in pack.references}

    assert opinion.evidence_claims
    for claim in opinion.evidence_claims:
        assert claim.citations
        for citation in claim.citations:
            reference = supplied[citation.evidence_id]
            assert citation.locator in {item.fact_id for item in reference.facts}
            assert claim.evidence_type is reference.evidence_type


def test_confidence_degrades_for_quality_freshness_horizon_and_sector() -> None:
    specialist = FundamentalSpecialist()
    full_pack = fundamental_pack()
    partial_pack = fundamental_pack(quality=DataQuality.PARTIAL)
    stale_pack = fundamental_pack(freshness=FreshnessState.STALE)
    financial_pack = fundamental_pack(financial=True)

    full = specialist.analyze(fundamental_agent_request(full_pack), full_pack)
    partial = specialist.analyze(
        fundamental_agent_request(partial_pack), partial_pack
    )
    stale = specialist.analyze(fundamental_agent_request(stale_pack), stale_pack)
    day = specialist.analyze(
        fundamental_agent_request(full_pack, trade_style=TradeStyle.DAY), full_pack
    )
    financial = specialist.analyze(
        fundamental_agent_request(financial_pack), financial_pack
    )

    values: list[float] = []
    for item in (full, partial, stale, day, financial):
        assert item.confidence.policy_derived is not None
        values.append(item.confidence.policy_derived.value)
    assert values[0] > values[1]
    assert values[0] > values[2]
    assert values[0] > values[3]
    assert values[0] > values[4]
    assert day.stance.value == "ABSTAIN"


def test_capability_is_equity_only_low_cost_and_no_llm() -> None:
    capability = FundamentalSpecialist().capability()

    assert capability.specialist is SpecialistId.FUNDAMENTAL
    assert capability.supports_no_llm
    assert capability.cost_tier.value == "LOW"
    assert tuple(item.value for item in capability.allowed_capabilities) == (
        "READ_A2_EVIDENCE",
        "READ_FUNDAMENTALS",
    )


def test_fundamental_specialist_has_no_forbidden_authority_or_calculator_imports() -> None:
    root = Path("src/tiaf/agents/specialists/fundamental")
    forbidden_imports = (
        "dhan",
        "httpx",
        "requests",
        "subprocess",
        "browser",
        "orders",
        "positions",
        "trade_monitor",
        "openai",
        "anthropic",
        "tiaf.features",
        "tiaf.data.providers",
    )
    imported: set[str] = set()
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.casefold() for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.casefold())

    assert not any(term in module for term in forbidden_imports for module in imported)


def test_specialist_source_has_no_execution_or_recommendation_vocabulary() -> None:
    source = Path(
        "src/tiaf/agents/specialists/fundamental/specialist.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert not calls & {"open", "exec", "eval", "compile", "system", "popen"}
    string_constants = {
        node.value.upper()
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    assert "datetime.now" not in source
    assert not {"BUY", "SELL", "HOLD", "EXIT", "CE", "PE"} & string_constants

    pack = fundamental_pack()
    opinion = FundamentalSpecialist().analyze(fundamental_agent_request(pack), pack)
    output = opinion.model_dump_json().casefold()
    assert all(
        phrase not in output
        for phrase in (
            "management is excellent",
            "has a moat",
            "promoters are trustworthy",
            "target price",
            "return probability",
        )
    )
