from pathlib import Path
from typing import cast

import pytest
from scripts._a3_8_fixtures import request as workflow_request

from tiaf.a4 import A4Disposition, A4EvidenceNeed, evaluate_projection
from tiaf.a4_enrichment import (
    A4EnrichmentChain,
    A4EnrichmentReplayError,
    EnrichmentStopReason,
    EvidenceBridgePolicy,
    EvidenceCaptureStatus,
    EvidenceChangeKind,
    EvidenceRoundExecution,
    SuccessorEvidenceCapture,
    WorkflowAdapter,
    admit_evidence_need,
    build_planner_bridge_plan,
    build_successor_outcome,
    capture_chain,
    capture_successor_evidence,
    compare_policy,
    execute_planner_bridge,
    replay_recorded,
    run_governed_enrichment,
    verify_deterministic,
)
from tiaf.agents import AgentRegistry
from tiaf.planner.digests import digest
from tiaf.workflows import ControlledServices, default_registry

from ..a4._support import reseal
from ..source_semantics._support import LATER, NOW
from ._support import (
    captured_new_evidence,
    grant,
    parent_case,
    plan_and_execution,
)


def _chain() -> A4EnrichmentChain:
    case = parent_case()
    permission = grant(case)
    admission = admit_evidence_need(case.run, case.need, permission, decided_at=NOW)
    plan, execution = plan_and_execution()
    outcome = build_successor_outcome(
        case.run,
        case.need,
        admission,
        plan,
        execution,
        captured_new_evidence(),
        completed_at=LATER,
    )
    return A4EnrichmentChain.seal(
        parent_run=case.run,
        evidence_need=case.need,
        grant=permission,
        policy=EvidenceBridgePolicy(),
        outcome=outcome,
    )


def test_recorded_replay_is_exact_and_zero_live_or_model_calls() -> None:
    chain = _chain()
    replay = replay_recorded(capture_chain(chain, captured_at=LATER), replayed_at=LATER)
    assert replay.chain == chain
    assert replay.provider_calls == 0
    assert replay.model_calls == 0


def test_deterministic_verification_rebuilds_exact_chain_offline() -> None:
    result = verify_deterministic(
        capture_chain(_chain(), captured_at=LATER),
        verified_at=LATER,
    )
    assert result.exact_match
    assert result.provider_calls == 0
    assert result.model_calls == 0


def test_missing_or_corrupt_replay_artifact_fails_closed() -> None:
    capture = capture_chain(_chain(), captured_at=LATER)
    corrupt = capture.model_copy(update={"chain_json": capture.chain_json[:-1]})
    with pytest.raises(A4EnrichmentReplayError):
        replay_recorded(corrupt, replayed_at=LATER)


def test_policy_change_has_distinct_comparison_and_admission_identity() -> None:
    chain = _chain()
    candidate = EvidenceBridgePolicy(
        policy_id="a4-enrichment-policy:comparison",
        policy_version="2.0",
    )
    comparison = compare_policy(chain, candidate, compared_at=LATER)
    assert comparison.original_policy != comparison.candidate_policy
    assert comparison.original_admission_fingerprint != (
        comparison.candidate_admission_fingerprint
    )
    assert not comparison.exact_match


def test_governed_runtime_executes_exactly_one_round_then_stops_no_information() -> None:
    case = parent_case()
    calls = 0

    def projector(
        need: A4EvidenceNeed,
        execution: EvidenceRoundExecution,
    ) -> SuccessorEvidenceCapture:
        nonlocal calls
        calls += 1
        return capture_successor_evidence(
            need,
            execution,
            status=EvidenceCaptureStatus.NO_NEW_INFORMATION,
            change_kind=EvidenceChangeKind.EQUIVALENT,
            reused_evidence_ids=("evidence:one",),
            genuinely_new=False,
            independent=None,
            relevant=True,
            live_acquisition=False,
            acquired_at=LATER,
        )

    chain = run_governed_enrichment(
        case.run,
        case.need,
        grant(case),
        workflow_request(symbol="SYNTHETIC", calls=1),
        default_registry(),
        ControlledServices(),
        projector,
        execution_as_of=LATER,
        clock=lambda: LATER,
    )
    assert calls == 1
    assert chain.outcome.enrichment_rounds == 1
    assert chain.outcome.successor_cycles == 0
    assert chain.outcome.stop_reason is EnrichmentStopReason.NO_NEW_INFORMATION


def test_denied_runtime_never_invokes_workflow_or_projector() -> None:
    case = parent_case()

    def forbidden_projector(
        need: A4EvidenceNeed,
        execution: EvidenceRoundExecution,
    ) -> SuccessorEvidenceCapture:
        raise AssertionError("projector must not run after admission denial")

    chain = run_governed_enrichment(
        case.run,
        case.need,
        grant(case, tool_calls=0),
        workflow_request(symbol="SYNTHETIC", calls=1),
        cast(AgentRegistry, None),
        ControlledServices(),
        forbidden_projector,
        execution_as_of=LATER,
        clock=lambda: LATER,
    )
    assert chain.outcome.stop_reason is EnrichmentStopReason.ADMISSION_DENIED
    assert chain.outcome.execution is None
    assert chain.outcome.provider_calls == 0


def test_serial_and_langgraph_have_same_semantic_successor_when_available() -> None:
    pytest.importorskip("langgraph")
    case = parent_case()
    permission = grant(case)
    admission = admit_evidence_need(case.run, case.need, permission, decided_at=NOW)
    plan = build_planner_bridge_plan(
        case.run,
        case.need,
        admission,
        permission,
        workflow_request(symbol="SYNTHETIC", calls=1),
        execution_as_of=LATER,
    )
    serial = execute_planner_bridge(
        plan,
        default_registry(),
        ControlledServices(),
        adapter=WorkflowAdapter.SERIAL,
        clock=lambda: LATER,
    )
    graph = execute_planner_bridge(
        plan,
        default_registry(),
        ControlledServices(),
        adapter=WorkflowAdapter.LANGGRAPH,
        clock=lambda: LATER,
    )
    assert serial.status == graph.status == "COMPLETED"
    assert serial.workflow_record is not None
    assert graph.workflow_record is not None
    assert serial.workflow_record.semantic_payload() == graph.workflow_record.semantic_payload()
    assert serial.provider_calls == graph.provider_calls
    assert serial.usage.model_dump(exclude={"elapsed_seconds"}) == graph.usage.model_dump(
        exclude={"elapsed_seconds"}
    )


def test_hard_no_trade_remains_visible_and_blocks_irrelevant_acquisition() -> None:
    case = parent_case()
    opportunity = case.run.input_projection.opportunity.model_copy(
        update={"original_a2_candidate_class": "NO_TRADE"}
    )
    projection = reseal(case.run.input_projection, opportunity=opportunity)
    run = evaluate_projection(projection, evaluated_at=NOW)
    assert run.result.disposition is A4Disposition.NO_TRADE
    assert any(
        item.reason_code == "A2_NO_TRADE_HARD_GATE"
        for item in run.result.challenge_findings
    )
    need = run.result.evidence_needs[0]
    permission = grant(case).model_copy(
        update={
            "capabilities": (need.requested_capability,),
            "processed_dedupe_keys": (),
            "resolved_need_ids": (),
        }
    )
    decision = admit_evidence_need(run, need, permission, decided_at=NOW)
    assert decision.reason_code == "DECISIVE_HARD_STOP_MAKES_ENRICHMENT_IRRELEVANT"


def test_domain_and_facade_import_boundaries_remain_clean() -> None:
    roots = (
        Path("src/tiaf/a4/contracts.py"),
        Path("src/tiaf/source_semantics/contracts.py"),
        Path("src/tiaf/facade/contracts.py"),
    )
    contents = "\n".join(path.read_text() for path in roots)
    assert "langgraph" not in contents.lower()
    assert "langchain" not in contents.lower()
    assert "Provider" not in Path("src/tiaf/a4/contracts.py").read_text()
    facade_init = Path("src/tiaf/facade/__init__.py").read_text()
    assert "run_governed_enrichment" not in facade_init


def test_no_langchain_dependency_no_broker_authority_and_no_future_phase_leakage() -> None:
    dependency_files = (Path("pyproject.toml"), Path("uv.lock"))
    assert all("langchain" not in path.read_text().lower() for path in dependency_files)
    need_json = parent_case().need.model_dump_json().lower()
    assert all(word not in need_json for word in ("broker", "order", "trade"))
    application_source = "\n".join(
        path.read_text() for path in Path("src/tiaf/a4_enrichment").glob("*.py")
    )
    assert all(f"tiaf.a{phase}" not in application_source for phase in (5, 6, 7))
    assert parent_case().run.result.usage.model_calls == 0


def test_chain_tampering_breaks_semantic_fingerprint() -> None:
    chain = _chain()
    with pytest.raises(ValueError, match="fingerprint"):
        A4EnrichmentChain.model_validate(
            chain.model_dump(mode="python")
            | {"fingerprint": digest("tampered")}
        )
