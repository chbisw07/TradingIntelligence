"""Offline recorded replay and deterministic policy/specialist verification."""

import json

from tiaf.agents import AgentRegistry, AgentRunRecord, AgentRuntime
from tiaf.contracts import ContractModel
from tiaf.market_intelligence import (
    AuthoritativeConfirmationResult,
    DeepResearchResult,
    MarketIntelligenceRun,
    SparseEvidenceGraph,
)
from tiaf.planner.digests import digest, semantic
from tiaf.planner.policy import build_plan, consumption_digest, dependencies, invocation_digest
from tiaf.planner.projection import project_opinion

from .ledger import ReservationLedger
from .records import OrchestrationRunRecord


def capture_json(record: OrchestrationRunRecord) -> str:
    record = OrchestrationRunRecord.model_validate_json(record.model_dump_json())
    payload = record.model_dump(mode="json")
    return json.dumps({"record": payload, "checksum": digest(payload)}, sort_keys=True)


def replay_recorded(content: str) -> OrchestrationRunRecord:
    captured = json.loads(content)
    if digest(captured["record"]) != captured["checksum"]:
        raise ValueError("capture checksum mismatch")
    record = OrchestrationRunRecord.model_validate(captured["record"])
    validators: dict[str, type[ContractModel]] = {
        "MarketIntelligenceRun": MarketIntelligenceRun,
        "AuthoritativeConfirmationResult": AuthoritativeConfirmationResult,
        "DeepResearchResult": DeepResearchResult,
        "SparseEvidenceGraph": SparseEvidenceGraph,
        "AgentRunRecord": AgentRunRecord,
    }
    for artifact in record.artifacts:
        validator = validators.get(artifact.kind)
        if validator is None:
            raise ValueError(f"unknown captured artifact schema: {artifact.kind}")
        validator.model_validate_json(artifact.canonical_json)
    artifact_ids = {a.artifact_id for a in record.artifacts}
    external_refs = (
        *record.request.inventory.normalized_run_ids,
        *record.request.inventory.confirmation_ids,
        *record.request.inventory.graph_ids,
        *record.request.inventory.prior_run_ids,
    )
    if not set(external_refs) <= artifact_ids:
        raise ValueError("missing captured external inventory reference")
    for decision in record.decisions:
        if (
            decision.action in {"ACQUIRE", "CONFIRM", "RESEARCH"}
            and not set(decision.trigger_ids) <= artifact_ids
        ):
            raise ValueError("missing captured child record")
    return record


def verify_deterministic(content: str, registry: AgentRegistry) -> OrchestrationRunRecord:
    record = replay_recorded(content)
    specs = dependencies(registry)
    ledger = ReservationLedger(record.request.budget, record.request.bounds.max_provider_calls)
    for entry in record.reservations:
        if not ledger.reserve(entry.accounting_id, entry.budget, entry.provider_calls):
            raise ValueError("recorded work could not have been reserved within aggregate budget")
        if entry.state != "OUTSTANDING":
            ledger.settle(entry.accounting_id, entry.actual, entry.actual_provider_calls)
    if ledger.entries() != record.reservations:
        raise ValueError("reservation reconciliation mismatch")
    for plan in record.plans:
        if plan != build_plan(record.request, specs, version=plan.version):
            raise ValueError("planner/dependency version or deterministic plan mismatch")
    for attempt in record.attempts:
        captured = attempt.record
        if captured is None:
            continue  # Recorded denial/timeout; do not invent or re-execute missing work.
        spec = next(s for s in specs if s.capability.specialist == captured.specialist)
        expected = invocation_digest(record.request, spec, captured.evidence_pack.references)
        if expected != attempt.input_digest or expected != captured.request.evidence_fingerprint:
            raise ValueError("invocation input digest mismatch")
        if (
            consumption_digest(record.request, spec, captured.evidence_pack.references)
            != attempt.consumed_digest
        ):
            raise ValueError("consumed dependency digest mismatch")
        ticks = iter((0.0, captured.usage.elapsed_seconds))
        runtime = AgentRuntime(
            registry,
            wall_clock=lambda: record.request.as_of,
            elapsed_clock=lambda: next(ticks, captured.usage.elapsed_seconds),
        )
        actual = runtime.run(captured.request, captured.evidence_pack)
        if semantic(actual) != semantic(captured):
            raise ValueError(
                f"deterministic specialist verification mismatch: {captured.specialist}"
            )
    for projection in record.projections:
        if project_opinion(projection.source_opinion) != projection:
            raise ValueError("typed projection verification mismatch")
    return record
