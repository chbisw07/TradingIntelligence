"""Capture tampering, original lineage, semantic identity and zero-execution checks."""

import ast
import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from scripts._a3_9_cases import load_case

from tiaf.planner.digests import digest, semantic
from tiaf.service.opportunity_intelligence import (
    CaptureIntegrityError,
    IntelligenceRunRecord,
    assemble_opportunity_intelligence,
    capture_intelligence,
    default_policy,
    replay_intelligence,
    request_from_capture,
    verify_intelligence,
)
from tiaf.service.opportunity_intelligence.handoff import baseline_view
from tiaf.workflows.records import OrchestrationRunRecord
from tiaf.workflows.replay import replay_recorded

from .test_acceptance import result


def reseal(data: dict[str, Any]) -> str:
    payload = {k: v for k, v in data.items() if k != "fingerprint"}
    payload["artifacts"] = [
        {
            "artifact_id": a["artifact_id"],
            "kind": a["kind"],
            "content": semantic(json.loads(a["canonical_json"])),
        }
        for a in data["artifacts"]
    ]
    data["fingerprint"] = digest(semantic(payload))
    return json.dumps({"record": data, "checksum": digest(data)}, sort_keys=True)


def assemble(content: str) -> IntelligenceRunRecord:
    return assemble_opportunity_intelligence(
        request_from_capture(content, request_id="test", policy=default_policy())
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "checksum",
        "identity",
        "schema",
        "citation",
        "pack",
        "outcome",
        "artifact",
        "active",
        "future",
    ],
)
def test_corrupt_captures_are_integrity_errors_not_market_gaps(mutation: str) -> None:
    data = json.loads(load_case("aligned"))["record"]
    if mutation == "checksum":
        content = reseal(data)
        content = content.replace('"checksum": "', '"checksum": "bad', 1)
    else:
        opinion = data["result"]["opinions"][0]
        run = next(
            a["record"]
            for a in data["attempts"]
            if a["record"]["opinion"]["opinion_id"] == opinion["opinion_id"]
        )
        if mutation == "identity":
            data["result"]["run_id"] = "wrong-run"
        elif mutation == "schema":
            opinion["specialist_detail_schema_id"] = "unsupported/99"
            run["opinion"]["specialist_detail_schema_id"] = "unsupported/99"
        elif mutation == "citation":
            for o in (opinion, run["opinion"]):
                o["supporting_evidence_ids"].append("absent")
                o["evidence_claims"][0]["citations"][0]["evidence_id"] = "absent"
        elif mutation == "pack":
            run["evidence_pack"]["references"][0]["facts"][0]["value"] = "CHANGED"
        elif mutation == "outcome":
            data["result"]["outcomes"][0]["run_record_id"] = "other"
        elif mutation == "artifact":
            data["result"]["confirmation_ids"] = ["missing"]
        elif mutation == "active":
            data["result"]["opinions"].append(copy.deepcopy(opinion))
        elif mutation == "future":
            for o in (opinion, run["opinion"]):
                o["evidence_claims"][0]["as_of"] = "2027-01-01T00:00:00+05:30"
        content = reseal(data)
    with pytest.raises(CaptureIntegrityError):
        assemble(content)


def test_mutable_source_summary_or_metadata_does_not_drive_state() -> None:
    data = json.loads(load_case("aligned"))["record"]
    for opinion in data["result"]["opinions"]:
        opinion["summary"] = "SELL BUY probability 99%"
        opinion["metadata"] = {"winner": "FUNDAMENTAL", "action": "EXIT"}
    for attempt in data["attempts"]:
        attempt["record"]["opinion"] = next(
            o
            for o in data["result"]["opinions"]
            if o["specialist"] == attempt["record"]["specialist"]
        )
    for projection in data["projections"]:
        projection["source_opinion"] = next(
            o
            for o in data["result"]["opinions"]
            if o["opinion_id"] == projection["source_opinion"]["opinion_id"]
        )
    run = assemble(reseal(data))
    assert run.result.summary.state.value == "OPPORTUNITY"
    assert not any("99%" in str(r.parameters) for r in run.result.reasons)


def test_baseline_missing_content_and_contradictory_copies() -> None:
    source = replay_recorded(load_case("aligned"))
    pack = source.request.inventory.a2_pack
    ref = pack.references[0]

    def source_with(facts: Any) -> OrchestrationRunRecord:
        changed = pack.model_copy(
            update={"references": (ref.model_copy(update={"facts": facts}), *pack.references[1:])}
        )
        return source.model_copy(
            update={
                "request": source.request.model_copy(
                    update={
                        "inventory": source.request.inventory.model_copy(
                            update={"a2_pack": changed}
                        )
                    }
                )
            }
        )

    view = baseline_view(
        source_with(tuple(f for f in ref.facts if f.metric_id != "baseline.opportunity_score"))
    )
    assert view.availability == "MISSING_CONTENT" and view.candidate_class is None
    extra = ref.facts[0].model_copy(update={"fact_id": "different", "value": "CONFLICTED"})
    with pytest.raises(CaptureIntegrityError, match="contradictory"):
        baseline_view(source_with((*ref.facts, extra)))


def test_no_hidden_policy_snapshot_change() -> None:
    request = result().request
    policy = request.policy.model_copy(update={"directional_fields": ("FUNDAMENTAL.stance",)})
    with pytest.raises(ValueError, match="unsupported synthesis policy"):
        assemble_opportunity_intelligence(request.model_copy(update={"policy": policy}))


def test_operational_adapter_differences_preserve_semantic_identity() -> None:
    original = json.loads(load_case("aligned"))["record"]
    changed = copy.deepcopy(original)
    changed["runtime_adapter"] = "langgraph-1.2.11"
    changed["completed_at"] = "2026-09-10T23:59:59+05:30"
    changed["result"]["usage"]["elapsed_seconds"] = 42
    a, b = assemble(reseal(original)), assemble(reseal(changed))
    assert a.result.audit.capture_checksum != b.result.audit.capture_checksum
    assert a.fingerprint == b.fingerprint
    assert (
        a.result.audit.imported_usage.elapsed_seconds
        != b.result.audit.imported_usage.elapsed_seconds
    )


def test_semantic_change_changes_identity() -> None:
    assert result("aligned").fingerprint != result("extended").fingerprint


def test_recorded_replay_detects_output_tampering() -> None:
    captured = json.loads(capture_intelligence(result()))
    captured["record"]["result"]["summary"]["state"] = "AVOID"
    captured["checksum"] = digest(captured["record"])
    with pytest.raises(CaptureIntegrityError):
        replay_intelligence(json.dumps(captured))


def test_assembly_and_replay_cannot_execute_upstream(monkeypatch: pytest.MonkeyPatch) -> None:
    import socket

    from tiaf.agents import AgentRuntime
    from tiaf.market_intelligence import MarketIntelligenceRouter
    from tiaf.workflows import OrchestrationCoordinator

    def denied(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("upstream execution forbidden")

    monkeypatch.setattr(AgentRuntime, "run", denied)
    monkeypatch.setattr(MarketIntelligenceRouter, "execute", denied)
    monkeypatch.setattr(OrchestrationCoordinator, "invoke", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)
    run = assemble(load_case("aligned"))
    captured = capture_intelligence(run)
    assert replay_intelligence(captured) == run
    assert verify_intelligence(captured).exact_match


def test_framework_and_network_import_isolation_subprocess() -> None:
    code = """
import sys
class Guard:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith(("langgraph", "langsmith", "httpx", "mcp", "openai")):
            raise AssertionError(fullname)
sys.meta_path.insert(0, Guard())
from scripts._a3_9_cases import load_case
from tiaf.service.opportunity_intelligence import *
r=assemble_opportunity_intelligence(request_from_capture(load_case("aligned"),request_id="isolation",policy=default_policy()))
assert verify_intelligence(capture_intelligence(r)).exact_match
"""
    completed = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=20
    )
    assert completed.returncode == 0, completed.stderr


def test_ast_and_schema_ownership_boundaries() -> None:
    from tiaf.contracts import ContractModel
    from tiaf.service.opportunity_intelligence import contracts

    forbidden_fields = {
        "winner",
        "arbitration",
        "action",
        "strike",
        "quantity",
        "target",
        "stop_loss",
        "probability",
        "expected_return",
        "forecast",
        "weights",
        "selected_expiry",
    }
    for value in vars(contracts).values():
        if (
            isinstance(value, type)
            and issubclass(value, ContractModel)
            and value.__module__ == contracts.__name__
        ):
            assert not set(value.model_fields) & forbidden_fields
            assert "metadata" not in value.model_fields
    for path in Path("src/tiaf/service/opportunity_intelligence").glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                assert not (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr in {"analyze", "execute", "invoke", "run_waves"}
                )
            if isinstance(node, ast.ImportFrom):
                assert not any(
                    x.name
                    in {"AgentRuntime", "verify_deterministic", "run_serial", "run_langgraph"}
                    for x in node.names
                )
                assert not (node.module or "").startswith(("langgraph", "httpx", "openai"))


def test_public_acceptance_helper() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/a3_9_user_acceptance.py"],
        capture_output=True,
        text=True,
        timeout=45,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "PASS: 18 / FAIL: 0" in completed.stdout
