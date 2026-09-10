"""Concurrency, failure, selective invalidation and portable audit hardening."""

import ast
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from threading import Event, Lock
from time import sleep
from typing import Any

import pytest
from scripts._a3_8_fixtures import confirmation_services, financial_services, reference, request

from tiaf.agents import (
    AgentBudget,
    AgentEvidencePack,
    AgentOpinionV2,
    AgentRegistry,
    AgentRequest,
    AgentRunRecord,
    AgentRunStatus,
    AgentStance,
    AgentUsage,
)
from tiaf.agents.specialists import (
    DerivativesContextSpecialist,
    OpportunityRiskSpecialist,
)
from tiaf.context import EvidenceStatus
from tiaf.contracts import DataQuality, EvidenceType, FreshnessState
from tiaf.market_intelligence import (
    DeepResearchIntegrationController,
    MarketIntelligenceResearchController,
    MarketIntelligenceRouter,
    ResearchDepth,
)
from tiaf.planner import OrchestrationBounds
from tiaf.planner.digests import digest
from tiaf.planner.models import NodeStatus, StopReason
from tiaf.planner.projection import project_opinion
from tiaf.workflows import (
    ControlledServices,
    EvidenceRevision,
    OrchestrationCoordinator,
    capture_json,
    default_registry,
    replay_recorded,
    run_serial,
    verify_deterministic,
)
from tiaf.workflows.langgraph_adapter import run_langgraph
from tiaf.workflows.ledger import ReservationLedger


def test_atomic_reservations_under_competing_workers() -> None:
    ledger = ReservationLedger(AgentBudget(max_tool_calls=2, max_cost_units=2), 2)
    with ThreadPoolExecutor(max_workers=12) as pool:
        accepted = list(
            pool.map(
                lambda n: ledger.reserve(
                    str(n), AgentBudget(max_tool_calls=1, max_cost_units=1), 1
                ),
                range(12),
            )
        )
    assert sum(accepted) == 2
    assert ledger.provider_calls() == 2
    assert ledger.committed_usage().tool_calls == 2


def test_failed_unknown_usage_is_held_and_not_double_debited() -> None:
    ledger = ReservationLedger(AgentBudget(max_tool_calls=1), 1)
    assert ledger.reserve("one", AgentBudget(max_tool_calls=1), 1)
    ledger.settle("one", None)
    assert ledger.entries()[0].state == "UNKNOWN"
    assert not ledger.reserve("two", AgentBudget(max_tool_calls=1), 1)
    with pytest.raises(ValueError):
        ledger.settle("one", AgentUsage())


def test_actual_overrun_stops_admission_even_zero_cost_work() -> None:
    ledger = ReservationLedger(AgentBudget(max_tool_calls=1), 1)
    assert ledger.reserve("one", AgentBudget(), 0)
    ledger.settle("one", AgentUsage(tool_calls=1), 1)
    assert ledger.exceeded
    assert not ledger.reserve("two", AgentBudget())


def test_single_flight_completed_and_inflight(monkeypatch: pytest.MonkeyPatch) -> None:
    services = financial_services(request(financials=False))
    original = MarketIntelligenceRouter.execute
    entered, release = Event(), Event()
    calls: list[int] = []

    def delayed(self: MarketIntelligenceRouter, *args: Any, **kwargs: Any) -> Any:
        calls.append(1)
        entered.set()
        assert release.wait(2)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(MarketIntelligenceRouter, "execute", delayed)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(services.acquire, services.acquisitions[0])
        assert entered.wait(2)
        second = pool.submit(services.acquire, services.acquisitions[0])
        release.set()
        a, b = first.result(), second.result()
    assert a[0] == b[0]
    assert a[1] is False and b[1] is True
    assert len(calls) == 1
    assert services.acquire(services.acquisitions[0])[1] is True


@pytest.mark.parametrize("adapter", [run_serial, run_langgraph])
def test_changed_chain_reruns_only_consumers(adapter: Any) -> None:
    req = request()
    revision = reference(
        req.subject,
        "chain",
        EvidenceType.DERIVATIVES,
        {
            "derivatives.atm_mean_iv": 60.0,
            "derivatives.days_to_expiry": 2,
        },
    )
    services = ControlledServices(
        revisions=(
            EvidenceRevision(after_round=0, references=(revision,), reason="new captured chain"),
        )
    )
    record = adapter(req, default_registry(), services)
    assert len(record.plans) == 2
    repeated = {a.node_id for a in record.attempts if a.plan_version == 2}
    assert repeated == {"DERIVATIVES_CONTEXT", "OPPORTUNITY_QUALITY", "OPPORTUNITY_RISK"}
    assert any(a.superseded for a in record.attempts)
    assert all(
        o.opinion_id
        not in {
            a.record.opinion.opinion_id
            for a in record.attempts
            if a.superseded and a.record and a.record.opinion
        }
        for o in record.result.opinions
    )
    assert verify_deterministic(capture_json(record), default_registry()) == record


def test_irrelevant_identical_revision_does_not_replan() -> None:
    req = request()
    ref = next(r for r in req.inventory.references if r.evidence_id == "chain")
    record = run_serial(
        req,
        default_registry(),
        ControlledServices(
            revisions=(EvidenceRevision(after_round=0, references=(ref,), reason="identical"),)
        ),
    )
    assert len(record.plans) == 1


def test_changed_upstream_input_with_identical_projection_reuses_downstream() -> None:
    class ProjectionOnlyRisk(OpportunityRiskSpecialist):
        def capability(self) -> Any:
            cap = super().capability()
            return cap.model_copy(
                update={
                    "optional_evidence_types": tuple(
                        t for t in cap.optional_evidence_types if t is not EvidenceType.DERIVATIVES
                    ),
                }
            )

    registry = AgentRegistry((DerivativesContextSpecialist(), ProjectionOnlyRisk()))
    req = request()
    old = next(r for r in req.inventory.references if r.evidence_id == "chain")
    extra = old.facts[0].model_copy(
        update={
            "fact_id": "fixture-additional",
            "metric_id": "derivatives.fixture_revision",
            "value": 1,
        }
    )
    updated = old.model_copy(update={"facts": (*old.facts, extra)})
    record = run_serial(
        req,
        registry,
        ControlledServices(
            revisions=(
                EvidenceRevision(
                    after_round=0, references=(updated,), reason="same interpreted state"
                ),
            )
        ),
    )
    assert len(record.plans) == 2
    assert [a.node_id for a in record.attempts if a.plan_version == 2] == ["DERIVATIVES_CONTEXT"]
    projections = [p for p in record.projections if p.reference is not None]
    assert projections[0].reference == projections[-1].reference
    assert verify_deterministic(capture_json(record), registry) == record


def test_quality_and_freshness_changes_invalidate_consumers() -> None:
    req = request()
    old = next(r for r in req.inventory.references if r.evidence_id == "chain")
    changed = old.model_copy(
        update={
            "quality": DataQuality.PARTIAL,
            "freshness": FreshnessState.STALE,
            "availability": EvidenceStatus.STALE,
        }
    )
    record = run_serial(
        req,
        default_registry(),
        ControlledServices(
            revisions=(
                EvidenceRevision(after_round=0, references=(changed,), reason="quality revision"),
            )
        ),
    )
    assert len(record.plans) == 2
    assert {a.node_id for a in record.attempts if a.plan_version == 2} == {
        "DERIVATIVES_CONTEXT",
        "OPPORTUNITY_QUALITY",
        "OPPORTUNITY_RISK",
    }
    assert verify_deterministic(capture_json(record), default_registry()) == record


def test_replan_limit_supersedes_old_evidence_outputs() -> None:
    req = request().model_copy(update={"bounds": OrchestrationBounds(max_replans=0)})
    ref = reference(
        req.subject, "chain", EvidenceType.DERIVATIVES, {"derivatives.atm_mean_iv": 60.0}
    )
    record = run_serial(
        req,
        default_registry(),
        ControlledServices(
            revisions=(EvidenceRevision(after_round=0, references=(ref,), reason="changed"),)
        ),
    )
    assert StopReason.DEPTH_LIMIT in record.result.stop_reasons
    assert record.result.status == "PARTIAL"
    assert not any(
        o.specialist.value in {"DERIVATIVES_CONTEXT", "OPPORTUNITY_QUALITY", "OPPORTUNITY_RISK"}
        for o in record.result.opinions
    )
    assert verify_deterministic(capture_json(record), default_registry()) == record


@pytest.mark.parametrize("permitted", [True, False])
def test_material_confirmation_gate_and_replay(permitted: bool) -> None:
    req = request().model_copy(update={"permit_confirmation": permitted})
    record = run_serial(req, default_registry(), confirmation_services(req))
    assert record.result.provider_calls == int(permitted)
    assert bool(record.result.confirmation_ids) == permitted
    if permitted:
        assert any(d.action == "CONFIRM" for d in record.decisions)
        assert any(a.node_id == "OPPORTUNITY_RISK" and a.plan_version == 2 for a in record.attempts)
    assert verify_deterministic(capture_json(record), default_registry()) == record


@pytest.mark.parametrize("permitted", [True, False])
def test_deep_research_assembles_existing_captured_subset(permitted: bool) -> None:
    req = request(financials=False).model_copy(
        update={
            "permit_deep_research": permitted,
            "research_depth": ResearchDepth.L2_INVESTMENT_RESEARCH,
        }
    )
    services = financial_services(req)
    services.acquisitions = tuple(
        a.model_copy(update={"material": True}) for a in services.acquisitions
    )
    assert services.router is not None
    services.research_controller = DeepResearchIntegrationController(
        MarketIntelligenceResearchController(services.router)
    )
    record = run_serial(req, default_registry(), services)
    assert record.result.provider_calls == 1
    assert bool(record.result.research_ids) == permitted
    assert verify_deterministic(capture_json(record), default_registry()) == record


def test_budget_denial_keeps_completed_specialists() -> None:
    req = request(financials=False, calls=0)
    record = run_serial(req, default_registry(), financial_services(req))
    assert record.result.provider_calls == 0
    assert record.result.status == "PARTIAL"
    assert StopReason.BUDGET_EXHAUSTED in record.result.stop_reasons
    assert any(o.specialist.value == "OPPORTUNITY_RISK" for o in record.result.opinions)


def test_actual_parallelism_and_shuffled_completion_parity(monkeypatch: pytest.MonkeyPatch) -> None:
    original = OrchestrationCoordinator.invoke
    active = peak = 0
    lock = Lock()

    def delayed(self: OrchestrationCoordinator, *args: Any) -> AgentRunRecord:
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
        sleep(0.01 if args[0].node_id == "FUNDAMENTAL" else 0.02)
        try:
            return original(self, *args)
        finally:
            with lock:
                active -= 1

    monkeypatch.setattr(OrchestrationCoordinator, "invoke", delayed)
    req = request()
    serial = run_serial(req, default_registry())
    peak = 0
    parallel = run_langgraph(req, default_registry())
    assert 1 < peak <= 3
    assert parallel.fingerprint == serial.fingerprint


def test_timeout_is_partial_and_keeps_unreported_reservation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = OrchestrationCoordinator.invoke

    def slow(self: OrchestrationCoordinator, *args: Any) -> AgentRunRecord:
        sleep(0.08)
        return original(self, *args)

    monkeypatch.setattr(OrchestrationCoordinator, "invoke", slow)
    req = request().model_copy(update={"budget": AgentBudget(max_elapsed_seconds=0.02)})
    record = run_serial(req, default_registry())
    assert StopReason.DEADLINE_EXCEEDED in record.result.stop_reasons
    assert record.result.status == "PARTIAL"
    assert any(r.state == "UNKNOWN" for r in record.reservations)
    assert any(a.status is NodeStatus.TIMED_OUT for a in record.attempts)
    sleep(0.1)  # Settle fixture threads, not a claim that arbitrary Python was cancelled.


def test_specialist_exception_isolated_with_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    original = OrchestrationCoordinator.invoke

    def broken(self: OrchestrationCoordinator, *args: Any) -> AgentRunRecord:
        if args[0].node_id == "FUNDAMENTAL":
            raise RuntimeError("fixture")
        return original(self, *args)

    monkeypatch.setattr(OrchestrationCoordinator, "invoke", broken)
    record = run_serial(request(), default_registry())
    failed = next(a for a in record.attempts if a.node_id == "FUNDAMENTAL")
    assert failed.reason == "RuntimeError" and failed.status is NodeStatus.FAILED
    assert any(o.specialist.value == "OPPORTUNITY_RISK" for o in record.result.opinions)


def test_all_abstain_is_preserved_and_verifiable() -> None:
    class AbstainingFixture(OpportunityRiskSpecialist):
        def analyze(self, request: AgentRequest, evidence: AgentEvidencePack) -> AgentOpinionV2:
            opinion = super().analyze(request, evidence)
            return opinion.model_copy(
                update={"stance": AgentStance.ABSTAIN, "status": AgentRunStatus.ABSTAINED}
            )

    registry = AgentRegistry((AbstainingFixture(),))
    record = run_serial(request(), registry)
    assert record.result.status == "ABSTAIN"
    assert StopReason.ABSTENTION_ACCEPTED in record.result.stop_reasons
    assert len(record.result.opinions) == 1
    assert verify_deterministic(capture_json(record), registry) == record


def test_runtime_failure_record_retains_failed_node_and_terminal_stop() -> None:
    class BrokenFixture(OpportunityRiskSpecialist):
        def analyze(self, request: AgentRequest, evidence: AgentEvidencePack) -> AgentOpinionV2:
            raise RuntimeError("fixture specialist failure")

    registry = AgentRegistry((BrokenFixture(),))
    record = run_serial(request(), registry)
    assert record.attempts[0].status is NodeStatus.FAILED
    assert record.attempts[0].record is not None
    assert record.result.primary_stop is StopReason.TERMINAL_FAILURE
    assert not record.result.opinions
    assert verify_deterministic(capture_json(record), registry) == record


def test_projection_quotes_typed_fields_not_prose_and_retains_lineage() -> None:
    record = run_serial(request(), default_registry())
    for projection in record.projections:
        if projection.reference is None:
            continue
        assert projection.reference.producer_id == "tiaf.specialist-output-projection"
        assert projection.reference.metadata["epistemic"] == "INFERENCE"
        changed_prose = projection.source_opinion.model_copy(
            update={"summary": "untrusted prose says BUY"}
        )
        assert project_opinion(changed_prose).field_digest() == projection.field_digest()
        assert all(f.source_evidence_ids and f.epistemic == "INFERENCE" for f in projection.fields)
        assert not any(f.value in {"UNKNOWN", "ABSTAIN"} for f in projection.fields)


@pytest.mark.parametrize("field", ["plans", "inventories", "attempts"])
def test_capture_tampering_detected(field: str) -> None:
    captured = json.loads(capture_json(run_serial(request(), default_registry())))
    captured["record"][field] = []
    with pytest.raises(ValueError):
        replay_recorded(json.dumps(captured))


def test_resealed_missing_child_capture_fails() -> None:
    req = request(financials=False)
    record = run_serial(req, default_registry(), financial_services(req))
    data = {
        name: getattr(record, name) for name in type(record).model_fields if name != "fingerprint"
    }
    data["artifacts"] = ()
    changed = type(record).seal(**data)
    with pytest.raises(ValueError, match="missing captured"):
        replay_recorded(capture_json(changed))


def test_domain_import_and_recorded_replay_need_no_langgraph_or_network() -> None:
    code = """
import sys
class Guard:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith(("langgraph", "langsmith", "httpx", "mcp")):
            raise AssertionError(fullname)
sys.meta_path.insert(0, Guard())
from tiaf.workflows import replay_recorded, verify_deterministic, default_registry
content = sys.stdin.read()
record = replay_recorded(content)
assert verify_deterministic(content, default_registry()) == record
"""
    content = capture_json(run_serial(request(), default_registry()))
    result = subprocess.run(
        [sys.executable, "-c", code], input=content, capture_output=True, text=True, timeout=15
    )
    assert result.returncode == 0, result.stderr


def test_planner_framework_provider_and_investment_boundaries() -> None:
    forbidden = {"langgraph", "langsmith", "httpx", "mcp", "subprocess", "openai"}
    for path in Path("src/tiaf/planner").glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not {a.name.split(".")[0] for a in node.names} & forbidden
            elif isinstance(node, ast.ImportFrom):
                assert (node.module or "").split(".")[0] not in forbidden
    policy = Path("src/tiaf/planner/policy.py").read_text().casefold()
    assert re.search(r"\b(tapetide|yahoo|dhan|nse|bse)\b", policy) is None
    from tiaf.planner import OrchestrationResult

    assert not set(OrchestrationResult.model_fields) & {
        "action",
        "recommendation",
        "winner",
        "quantity",
        "strike",
        "target",
        "stop_loss",
        "probability",
    }
    assert digest(request().inventory.a2_pack) == digest(
        run_serial(request(), default_registry()).inventories[-1].a2_pack
    )


def test_complete_workflow_keeps_separate_opinions_and_sufficiency_stop() -> None:
    registry = AgentRegistry(
        (
            DerivativesContextSpecialist(),
            OpportunityRiskSpecialist(),
        )
    )
    record = run_serial(request(), registry)
    assert record.result.status == "COMPLETE"
    assert len(record.result.opinions) == 2
    assert StopReason.EVIDENCE_SUFFICIENT in record.result.stop_reasons
    assert record.result.usage_is_complete


def test_new_unconsumed_evidence_does_not_replan() -> None:
    req = request()
    ref = reference(
        req.subject, "unrelated-identity", EvidenceType.OTHER, {"identity.name": "UNCHANGED"}
    )
    record = run_serial(
        req,
        default_registry(),
        ControlledServices(
            revisions=(
                EvidenceRevision(after_round=0, references=(ref,), reason="unused identity"),
            )
        ),
    )
    assert len(record.inventories) == 2
    assert len(record.plans) == 1


def test_acquisition_timestamp_alone_does_not_reinterpret() -> None:
    req = request()
    original = next(r for r in req.inventory.references if r.evidence_id == "chain")
    facts = tuple(
        f.model_copy(update={"as_of": req.as_of - timedelta(hours=2)}) for f in original.facts
    )
    old = original.model_copy(
        update={
            "facts": facts,
            "observed_at": req.as_of - timedelta(hours=2),
            "acquired_at": req.as_of - timedelta(hours=1),
            "checksum": "old-transport-hash",
        }
    )
    newer = old.model_copy(update={"acquired_at": req.as_of, "checksum": "new-transport-hash"})
    req = req.model_copy(
        update={
            "inventory": req.inventory.model_copy(
                update={
                    "references": tuple(
                        old if r.evidence_id == "chain" else r for r in req.inventory.references
                    ),
                }
            )
        }
    )
    record = run_serial(
        req,
        default_registry(),
        ControlledServices(
            revisions=(
                EvidenceRevision(
                    after_round=0, references=(newer,), reason="transport-only refresh"
                ),
            )
        ),
    )
    assert len(record.inventories) == 2
    assert len(record.plans) == 1
    assert verify_deterministic(capture_json(record), default_registry()) == record


def test_duplicate_semantic_acquisition_ids_share_one_call() -> None:
    req = request(financials=False)
    services = financial_services(req)
    a = services.acquisitions[0]
    b = a.model_copy(
        update={"request": a.request.model_copy(update={"request_id": "other-consumer"})}
    )
    assert a.key() == b.key()
    services.acquisitions = (a, b)
    record = run_serial(req, default_registry(), services)
    assert record.result.provider_calls == 1


def test_deterministic_replay_rejects_changed_registry() -> None:
    record = run_serial(request(), default_registry())
    with pytest.raises(ValueError, match="planner/dependency version"):
        verify_deterministic(capture_json(record), AgentRegistry((OpportunityRiskSpecialist(),)))


@pytest.mark.parametrize(
    "field", ["normalized_run_ids", "prior_run_ids", "confirmation_ids", "graph_ids"]
)
def test_missing_external_capture_reference_fails_preflight(field: str) -> None:
    req = request()
    req = req.model_copy(
        update={"inventory": req.inventory.model_copy(update={field: ("missing",)})}
    )
    with pytest.raises(ValueError, match="missing captured"):
        run_serial(req, default_registry())


def test_prior_independent_specialist_reused_without_restamping() -> None:
    req = request()
    previous = run_serial(req, default_registry())
    prior = next(a.record for a in previous.attempts if a.node_id == "TECHNICAL")
    assert prior is not None
    current = run_serial(req, default_registry(), ControlledServices(prior_runs=(prior,)))
    reused = next(a for a in current.attempts if a.node_id == "TECHNICAL")
    assert reused.status is NodeStatus.REUSED and reused.record == prior
    assert verify_deterministic(capture_json(current), default_registry()) == current


def test_graph_reuse_is_one_hop_asof_bounded_and_relation_filtered() -> None:
    from tiaf.market_intelligence import GraphRelation, SparseEvidenceGraph

    from ..market_intelligence.test_graph_research import _edge, _nodes

    req = request()
    nodes = _nodes()
    nodes = (nodes[0].model_copy(update={"canonical_name": req.subject}), nodes[1])
    graph = SparseEvidenceGraph(graph_id="captured-graph", nodes=nodes, edges=(_edge(),))
    record = run_serial(req, default_registry(), ControlledServices(graph=graph))
    assert record.result.graph_ids == ("captured-graph",)
    restored = SparseEvidenceGraph.model_validate_json(record.artifacts[0].canonical_json)
    assert len(restored.edges) == 1
    blocked = run_serial(
        req, default_registry(), ControlledServices(graph=graph, graph_relations=())
    )
    assert len(blocked.result.graph_ids) == 2
    assert SparseEvidenceGraph.model_validate_json(blocked.artifacts[0].canonical_json) == graph
    assert not SparseEvidenceGraph.model_validate_json(blocked.artifacts[1].canonical_json).edges
    assert verify_deterministic(capture_json(blocked), default_registry()) == blocked
    assert GraphRelation.EXPOSED_TO_COMMODITY == restored.edges[0].relation


def test_public_acceptance_script_exercises_both_adapters() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/a3_8_user_acceptance.py"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "PASS: 14 / FAIL: 0" in completed.stdout
