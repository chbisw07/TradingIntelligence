"""Portable captures: no workflow framework or provider required to deserialize."""

import json
from typing import Any, Self

from pydantic import model_validator

from tiaf.agents import AgentUsage
from tiaf.contracts import ContractModel
from tiaf.contracts.common import TiafDateTime
from tiaf.planner.digests import digest, semantic
from tiaf.planner.models import (
    AnalysisPlan,
    CapturedArtifact,
    EvidenceInventory,
    NodeAttempt,
    OrchestrationRequest,
    OrchestrationResult,
    PlanDecision,
    Reservation,
    Sha256,
)
from tiaf.planner.projection import SpecialistOutputProjection

from .ledger import add_usage, reserved_usage


class OrchestrationRunRecord(ContractModel):
    request: OrchestrationRequest
    plans: tuple[AnalysisPlan, ...]
    inventories: tuple[EvidenceInventory, ...]
    decisions: tuple[PlanDecision, ...]
    attempts: tuple[NodeAttempt, ...]
    projections: tuple[SpecialistOutputProjection, ...]
    reservations: tuple[Reservation, ...]
    artifacts: tuple[CapturedArtifact, ...]
    result: OrchestrationResult
    started_at: TiafDateTime
    completed_at: TiafDateTime
    runtime_adapter: str
    fingerprint: Sha256

    def semantic_payload(self) -> Any:
        data = self.model_dump(mode="json", exclude={"fingerprint"})
        for plan in data["plans"]:
            if plan["policy_version"] == "1.0":
                for skipped in plan["skipped"]:
                    skipped.pop("required", None)
        if data["plans"] and data["plans"][-1]["policy_version"] == "1.0":
            for skipped in data["result"]["skipped"]:
                skipped.pop("required", None)
        data["artifacts"] = [
            {
                "artifact_id": a.artifact_id,
                "kind": a.kind,
                "content": semantic(json.loads(a.canonical_json)),
            }
            for a in self.artifacts
        ]
        return semantic(data)

    @model_validator(mode="after")
    def validate_record(self) -> Self:
        if digest(self.semantic_payload()) != self.fingerprint:
            raise ValueError("orchestration semantic fingerprint mismatch")
        if not self.plans or not self.inventories:
            raise ValueError("missing captured plans/inventory")
        if tuple(p.version for p in self.plans) != tuple(range(1, len(self.plans) + 1)):
            raise ValueError("missing or reordered plan versions")
        if any(
            (plan.planner_version, plan.policy_version)
            != (self.plans[0].planner_version, self.plans[0].policy_version)
            for plan in self.plans
        ):
            raise ValueError("planner/policy version changed within one run")
        if any(p.request_digest != digest(self.request) for p in self.plans):
            raise ValueError("plan/request digest mismatch")
        if any(i.a2_pack != self.request.inventory.a2_pack for i in self.inventories):
            raise ValueError("A2 capture was modified")
        if self.result.a2_fingerprint != self.request.inventory.a2_pack.evidence_fingerprint:
            raise ValueError("A2 fingerprint not preserved")
        expected_opinions = tuple(
            a.record.opinion
            for a in sorted(
                (item for item in self.attempts if not item.superseded),
                key=lambda a: a.node_id,
            )
            if a.record is not None and a.record.opinion is not None
        )
        if self.result.opinions != expected_opinions:
            raise ValueError("active opinion set differs from captured nonsuperseded attempts")
        if self.result.a2_reference != self.request.inventory.a2_pack.deterministic_assessment_id:
            raise ValueError("A2 assessment reference mismatch")
        if self.result.run_id != self.request.run_id:
            raise ValueError("result run identity mismatch")
        if not self.result.stop_reasons or len(set(self.result.stop_reasons)) != len(
            self.result.stop_reasons
        ):
            raise ValueError("invalid stop reason set")
        actuals = tuple(r.actual for r in self.reservations if r.actual is not None)
        usage = AgentUsage(
            tool_calls=sum(u.tool_calls for u in actuals),
            llm_calls=sum(u.llm_calls for u in actuals),
            input_tokens=sum(u.input_tokens for u in actuals),
            output_tokens=sum(u.output_tokens for u in actuals),
            cost_units=sum(u.cost_units for u in actuals),
            elapsed_seconds=self.result.usage.elapsed_seconds,
        )
        if usage != self.result.usage:
            raise ValueError("result usage does not match recorded actual consumption")
        if self.result.provider_calls != sum(
            r.actual_provider_calls or 0 for r in self.reservations
        ):
            raise ValueError("provider-call rollup mismatch")
        if self.result.usage_is_complete != all(r.state == "SETTLED" for r in self.reservations):
            raise ValueError("unreported usage must remain explicit")
        held = tuple(r for r in self.reservations if r.state != "SETTLED")
        if self.result.held_usage != add_usage(tuple(reserved_usage(r.budget) for r in held)):
            raise ValueError("held usage differs from outstanding reservations")
        if self.result.held_provider_calls != sum(r.provider_calls for r in held):
            raise ValueError("held provider-call allowance mismatch")
        if len({r.accounting_id for r in self.reservations}) != len(self.reservations):
            raise ValueError("duplicate operation accounting ID")
        if len({a.artifact_id for a in self.artifacts}) != len(self.artifacts):
            raise ValueError("duplicate artifact identity")
        known_nodes = {n.node_id for n in self.plans[-1].nodes}
        if {o.node_id for o in self.result.outcomes} != known_nodes:
            raise ValueError("missing selected-node outcome")
        if tuple(d.sequence for d in self.decisions) != tuple(range(1, len(self.decisions) + 1)):
            raise ValueError("decision audit sequence mismatch")
        if self.completed_at < self.started_at:
            raise ValueError("invalid run time interval")
        return self

    @classmethod
    def seal(cls, **fields: Any) -> Self:
        provisional = cls.model_construct(fingerprint="0" * 64, **fields)
        data = provisional.model_dump(mode="python")
        data["fingerprint"] = digest(provisional.semantic_payload())
        return cls.model_validate(data)
