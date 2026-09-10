"""Request, DAG, applicability, authority and pure-policy gates."""

from datetime import UTC, timedelta, timezone

import pytest
from pydantic import ValidationError
from scripts._a3_8_fixtures import NOW, request

from tiaf.agents import AgentCapability, SpecialistId
from tiaf.contracts import TradeStyle
from tiaf.data import InstrumentType
from tiaf.planner import (
    AnalysisPlan,
    Disposition,
    OrchestrationRequest,
    build_plan,
    dependencies,
    missing_disposition,
)
from tiaf.workflows import default_registry


def test_contract_list_json_aware_roundtrip_and_frozen() -> None:
    original = request()
    data = original.model_dump(mode="json")
    assert data["as_of"].endswith("+05:30")
    assert isinstance(data["allowed_capabilities"], list)
    rebuilt = OrchestrationRequest.model_validate(data)
    assert rebuilt == original
    assert isinstance(rebuilt.allowed_capabilities, tuple)
    with pytest.raises(ValidationError):
        rebuilt.run_id = "replace"
    with pytest.raises(AttributeError):
        rebuilt.allowed_capabilities.append(AgentCapability.READ_NEWS)  # type: ignore[attr-defined]


@pytest.mark.parametrize("zone", [UTC, timezone(timedelta(hours=-7))])
def test_normalizes_aware_zones(zone: timezone) -> None:
    data = request().model_dump(mode="python")
    data["as_of"] = NOW.astimezone(zone)
    assert OrchestrationRequest.model_validate(data).as_of == NOW


@pytest.mark.parametrize(
    "mutation", ["naive", "future", "missing_identity", "model", "no_a2", "extra"]
)
def test_rejects_unsafe_request(mutation: str) -> None:
    data = request().model_dump(mode="python")
    if mutation == "naive":
        data["as_of"] = NOW.replace(tzinfo=None)
    elif mutation == "future":
        data["inventory"]["references"][0]["acquired_at"] = NOW + timedelta(days=1)
    elif mutation == "missing_identity":
        data["instrument"]["eligibility_reference"] = "not-captured"
    elif mutation == "model":
        data["no_llm"] = False
    elif mutation == "no_a2":
        data["allowed_capabilities"] = ()
    else:
        data["action"] = "BUY"
    with pytest.raises(ValidationError):
        OrchestrationRequest.model_validate(data)


@pytest.mark.parametrize(
    ("fno", "selected", "reason"),
    [
        (True, True, None),
        (False, False, "ATTRIBUTED_NON_FNO"),
        (None, False, "UNKNOWN_FNO_ELIGIBILITY"),
    ],
)
def test_fno_applicability(fno: bool | None, selected: bool, reason: str | None) -> None:
    plan = build_plan(request(fno=fno), dependencies(default_registry()))
    assert ("DERIVATIVES_CONTEXT" in {n.node_id for n in plan.nodes}) is selected
    if reason:
        assert any(s.reason == reason for s in plan.skipped)


@pytest.mark.parametrize("kind", [InstrumentType.INDEX, InstrumentType.UNKNOWN])
def test_index_company_skip_and_unsupported_instrument(kind: InstrumentType) -> None:
    original = request()
    changed = original.model_copy(
        update={"instrument": original.instrument.model_copy(update={"instrument_type": kind})}
    )
    plan = build_plan(changed, dependencies(default_registry()))
    assert "FUNDAMENTAL" not in {n.node_id for n in plan.nodes}
    if kind is InstrumentType.UNKNOWN:
        assert not plan.nodes


def test_day_and_macro_are_selective_not_automatic() -> None:
    req = request().model_copy(update={"trade_style": TradeStyle.DAY})
    plan = build_plan(req, dependencies(default_registry()))
    assert {s.specialist for s in plan.skipped} >= {SpecialistId.FUNDAMENTAL, SpecialistId.MACRO}


def test_stable_waves_barriers_and_no_placeholder_execution() -> None:
    specs = dependencies(default_registry())
    plan = build_plan(request(), specs)
    assert plan == build_plan(request(), specs)
    assert all(len(w) <= 3 for w in plan.waves)
    risk = next(n for n in plan.nodes if n.node_id == "OPPORTUNITY_RISK")
    assert "OPPORTUNITY_QUALITY" not in risk.dependencies
    assert "TECHNICAL" in risk.dependencies
    assert not any(n.specialist is SpecialistId.CONTRARIAN_HYPOTHESIS for n in plan.nodes)
    assert AnalysisPlan.model_validate_json(plan.model_dump_json()) == plan


@pytest.mark.parametrize(
    "mutation", ["self_cycle", "unknown_dependency", "duplicate_wave", "parent"]
)
def test_invalid_dag_rejected(mutation: str) -> None:
    data = build_plan(request(), dependencies(default_registry())).model_dump(mode="json")
    if mutation == "self_cycle":
        data["nodes"][0]["dependencies"] = [data["nodes"][0]["node_id"]]
    elif mutation == "unknown_dependency":
        data["nodes"][0]["dependencies"] = ["NOT_REGISTERED"]
    elif mutation == "duplicate_wave":
        data["waves"].append(data["waves"][0])
    else:
        data["parent_version"] = 7
    with pytest.raises(ValidationError):
        AnalysisPlan.model_validate(data)


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        ({}, Disposition.RECOVERABLE),
        ({"authorized": False}, Disposition.PERMISSION_DENIED),
        ({"supported": False}, Disposition.UNSUPPORTED),
        ({"pit_usable": False}, Disposition.UNSUPPORTED),
        ({"specific": False}, Disposition.NOT_WORTH_COST),
        ({"repeated": True}, Disposition.NOT_WORTH_COST),
        ({"already_satisfied": True}, Disposition.NOT_WORTH_COST),
        ({"budget_available": False}, Disposition.BUDGET_BLOCKED),
    ],
)
def test_missing_evidence_dispositions(overrides: dict[str, bool], expected: Disposition) -> None:
    args = dict(
        authorized=True, supported=True, specific=True, pit_usable=True, budget_available=True
    )
    args.update(overrides)
    assert missing_disposition(**args) == expected
