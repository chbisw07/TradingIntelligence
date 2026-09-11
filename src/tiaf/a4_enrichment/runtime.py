"""Single-round application composition for governed A4 evidence enrichment."""

from collections.abc import Callable
from datetime import datetime

from tiaf.a4 import A4EvidenceNeed, A4RunRecord
from tiaf.agents import AgentRegistry
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.planner.models import OrchestrationRequest
from tiaf.workflows import ControlledServices

from .admission import admit_evidence_need
from .bridge import build_planner_bridge_plan, execute_planner_bridge
from .contracts import (
    A4EnrichmentChain,
    EvidenceBridgeGrant,
    EvidenceBridgePolicy,
    EvidenceRoundExecution,
    SuccessorEvidenceCapture,
)
from .enums import EvidenceNeedAdmissionOutcome, WorkflowAdapter
from .successor import build_successor_outcome, denied_outcome

CapturedEvidenceProjector = Callable[
    [A4EvidenceNeed, EvidenceRoundExecution], SuccessorEvidenceCapture
]


def run_governed_enrichment(
    parent: A4RunRecord,
    need: A4EvidenceNeed,
    grant: EvidenceBridgeGrant,
    template: OrchestrationRequest,
    registry: AgentRegistry,
    services: ControlledServices,
    evidence_projector: CapturedEvidenceProjector,
    *,
    execution_as_of: datetime,
    policy: EvidenceBridgePolicy | None = None,
    adapter: WorkflowAdapter = WorkflowAdapter.SERIAL,
    clock: Callable[[], datetime] = lambda: datetime.now(TIAF_TIMEZONE),
) -> A4EnrichmentChain:
    """Execute at most one workflow round and at most one successor A4 cycle."""
    selected = policy or EvidenceBridgePolicy()
    parent_fingerprint = parent.fingerprint
    admission = admit_evidence_need(
        parent,
        need,
        grant,
        policy=selected,
        decided_at=clock(),
    )
    if admission.outcome is not EvidenceNeedAdmissionOutcome.ADMITTED:
        outcome = denied_outcome(parent, need, admission, completed_at=clock())
    else:
        plan = build_planner_bridge_plan(
            parent,
            need,
            admission,
            grant,
            template,
            execution_as_of=execution_as_of,
            policy=selected,
        )
        execution = execute_planner_bridge(
            plan,
            registry,
            services,
            adapter=adapter,
            clock=clock,
        )
        evidence = (
            evidence_projector(need, execution)
            if execution.status == "COMPLETED"
            else None
        )
        outcome = build_successor_outcome(
            parent,
            need,
            admission,
            plan,
            execution,
            evidence,
            completed_at=clock(),
        )
    if parent.fingerprint != parent_fingerprint:
        raise ValueError("parent A4 run was mutated during enrichment")
    return A4EnrichmentChain.seal(
        parent_run=parent,
        evidence_need=need,
        grant=grant,
        policy=selected,
        outcome=outcome,
    )
