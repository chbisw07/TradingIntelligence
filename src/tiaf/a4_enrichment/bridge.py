"""Narrow A4 semantic-need to A3.8 Planner/workflow application bridge."""

from collections.abc import Callable
from datetime import datetime

from tiaf.a4 import A4EvidenceCapability, A4EvidenceNeed, A4RunRecord
from tiaf.agents import AgentCapability, AgentRegistry, AgentUsage
from tiaf.contracts import EvidenceType
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.planner.digests import digest
from tiaf.planner.models import Intent, OrchestrationRequest
from tiaf.workflows import ControlledServices, run_serial

from .contracts import (
    A4PlannerBridgePlan,
    EvidenceBridgeGrant,
    EvidenceBridgePolicy,
    EvidenceNeedAdmission,
    EvidenceRoundExecution,
)
from .enums import EvidenceNeedAdmissionOutcome, WorkflowAdapter


class PlannerBridgeError(ValueError):
    """The admitted semantic need cannot safely cross the Planner boundary."""


_MAPPING: dict[
    A4EvidenceCapability,
    tuple[tuple[AgentCapability, ...], EvidenceType],
] = {
    A4EvidenceCapability.AUTHORITATIVE_CONFIRMATION: (
        (AgentCapability.READ_FUNDAMENTALS, AgentCapability.READ_FILINGS),
        EvidenceType.FUNDAMENTAL,
    ),
    A4EvidenceCapability.COMPANY_FUNDAMENTALS: (
        (AgentCapability.READ_FUNDAMENTALS, AgentCapability.READ_FILINGS),
        EvidenceType.FUNDAMENTAL,
    ),
    A4EvidenceCapability.EVENT_NEWS_CONTEXT: (
        (AgentCapability.READ_NEWS,),
        EvidenceType.NEWS,
    ),
    A4EvidenceCapability.SECTOR_MACRO_CONTEXT: (
        (AgentCapability.READ_SECTOR_CONTEXT, AgentCapability.READ_MACRO_CONTEXT),
        EvidenceType.SECTOR,
    ),
    A4EvidenceCapability.DERIVATIVES_CONTEXT: (
        (AgentCapability.READ_DERIVATIVES,),
        EvidenceType.DERIVATIVES,
    ),
    A4EvidenceCapability.BOUNDED_DEEP_RESEARCH: (
        (AgentCapability.REQUEST_ADDITIONAL_MARKET_EVIDENCE,),
        EvidenceType.OTHER,
    ),
}


def _plan_fingerprint(plan: A4PlannerBridgePlan) -> str:
    return digest(plan.model_dump(mode="json", exclude={"fingerprint"}))


def build_planner_bridge_plan(
    parent: A4RunRecord,
    need: A4EvidenceNeed,
    admission: EvidenceNeedAdmission,
    grant: EvidenceBridgeGrant,
    template: OrchestrationRequest,
    *,
    execution_as_of: datetime,
    policy: EvidenceBridgePolicy | None = None,
) -> A4PlannerBridgePlan:
    """Translate one admitted semantic capability into a bounded A3.8 request."""
    selected = policy or EvidenceBridgePolicy()
    if admission.outcome is not EvidenceNeedAdmissionOutcome.ADMITTED:
        raise PlannerBridgeError("only an admitted evidence need can be planned")
    if (
        admission.evidence_need_id != need.evidence_need_id
        or admission.parent_a4_run_id != parent.run_id
        or admission.grant_id != grant.grant_id
    ):
        raise PlannerBridgeError("admission lineage mismatch")
    if need.requested_capability not in _MAPPING:
        raise PlannerBridgeError("semantic capability has no Planner mapping")
    if template.subject != need.subject or template.horizon != need.horizon:
        raise PlannerBridgeError("Planner template subject or horizon differs from need")
    if template.purpose.value != need.objective:
        raise PlannerBridgeError("Planner template objective differs from need")
    if (
        template.inventory.a2_pack.deterministic_assessment_id
        != parent.input_projection.parents.a2_assessment_id
        or template.inventory.a2_pack.evidence_fingerprint
        != parent.input_projection.parents.a2_evidence_fingerprint
    ):
        raise PlannerBridgeError("Planner template does not preserve the frozen A2 parent")
    if execution_as_of <= need.original_as_of:
        raise PlannerBridgeError("enrichment execution as-of must advance beyond parent")
    if grant.deadline is not None and execution_as_of >= grant.deadline:
        raise PlannerBridgeError("enrichment execution begins after its deadline")
    child_caps, evidence_type = _MAPPING[need.requested_capability]
    allowed = (AgentCapability.READ_A2_EVIDENCE, *child_caps)
    bounds = template.bounds.model_copy(
        update={
            "max_enrichment_rounds": selected.max_enrichment_rounds,
            "max_replans": selected.max_successor_cycles,
            "max_attempts_per_specialist": 1,
            "max_provider_calls": admission.admitted_provider_calls,
        }
    )
    request = template.model_copy(
        update={
            "request_id": f"a4-need-request:{digest(need.evidence_need_id)[:24]}",
            "run_id": "a4-enrichment-run:"
            + digest((need.evidence_need_id, execution_as_of.isoformat()))[:24],
            "correlation_id": parent.run_id,
            "allowed_capabilities": allowed,
            "budget": admission.admitted_budget,
            "bounds": bounds,
            "permit_confirmation": need.requested_capability
            is A4EvidenceCapability.AUTHORITATIVE_CONFIRMATION,
            "permit_deep_research": need.requested_capability
            is A4EvidenceCapability.BOUNDED_DEEP_RESEARCH,
            "include_macro": need.requested_capability
            is A4EvidenceCapability.SECTOR_MACRO_CONTEXT,
            "as_of": execution_as_of,
            "deadline": grant.deadline,
            "intent": Intent.LIVE if grant.permit_live_read else Intent.CAPTURED,
            "replay_source_run_id": None,
        }
    )
    request = OrchestrationRequest.model_validate(request.model_dump(mode="python"))
    provisional = A4PlannerBridgePlan.model_construct(
        plan_ref="a4-planner-plan:pending",
        evidence_need_id=need.evidence_need_id,
        admission_fingerprint=admission.fingerprint,
        semantic_capability=need.requested_capability,
        planner_capabilities=allowed,
        evidence_type=evidence_type,
        orchestration_request=request,
        bridge_id=selected.bridge_id,
        bridge_version=selected.bridge_version,
        fingerprint="0" * 64,
    )
    identity = digest(
        provisional.model_dump(
            mode="json", exclude={"plan_ref": True, "fingerprint": True}
        )
    )
    provisional = provisional.model_copy(
        update={"plan_ref": f"a4-planner-plan:{identity[:24]}"}
    )
    final = provisional.model_copy(update={"fingerprint": _plan_fingerprint(provisional)})
    return A4PlannerBridgePlan.model_validate(final.model_dump(mode="python"))


def _execution_fingerprint(execution: EvidenceRoundExecution) -> str:
    return digest(execution.model_dump(mode="json", exclude={"fingerprint"}))


def execute_planner_bridge(
    plan: A4PlannerBridgePlan,
    registry: AgentRegistry,
    services: ControlledServices,
    *,
    adapter: WorkflowAdapter = WorkflowAdapter.SERIAL,
    clock: Callable[[], datetime] = lambda: datetime.now(TIAF_TIMEZONE),
) -> EvidenceRoundExecution:
    """Execute exactly one bounded A3.8 workflow; no provider is selected here."""
    started = clock()
    try:
        if adapter is WorkflowAdapter.SERIAL:
            record = run_serial(plan.orchestration_request, registry, services)
        else:
            # Optional infrastructure import remains outside all domain contracts.
            from tiaf.workflows.langgraph_adapter import run_langgraph

            record = run_langgraph(plan.orchestration_request, registry, services)
        if record.request != plan.orchestration_request:
            raise PlannerBridgeError("workflow record request differs from bridge plan")
        if record.result.provider_calls > 1:
            raise PlannerBridgeError("workflow exceeded the one-call provider bound")
        usage = record.result.usage
        if usage.llm_calls or usage.input_tokens or usage.output_tokens:
            raise PlannerBridgeError("workflow used a model in no-model A4.2")
        completed = clock()
        provisional = EvidenceRoundExecution.model_construct(
            execution_id="a4-enrichment-execution:pending",
            plan_ref=plan.plan_ref,
            adapter=adapter,
            workflow_record=record,
            status="COMPLETED",
            usage=usage,
            provider_calls=record.result.provider_calls,
            started_at=started,
            completed_at=completed,
            fingerprint="0" * 64,
        )
    except Exception as exc:
        completed = clock()
        provisional = EvidenceRoundExecution.model_construct(
            execution_id="a4-enrichment-execution:pending",
            plan_ref=plan.plan_ref,
            adapter=adapter,
            status="FAILED",
            failure_codes=(f"WORKFLOW_{type(exc).__name__.upper()}",),
            usage=AgentUsage(metadata={"usage_knowledge": "UNKNOWN"}),
            provider_calls=0,
            started_at=started,
            completed_at=completed,
            fingerprint="0" * 64,
        )
    identity = digest(
        provisional.model_dump(
            mode="json", exclude={"execution_id": True, "fingerprint": True}
        )
    )
    provisional = provisional.model_copy(
        update={"execution_id": f"a4-enrichment-execution:{identity[:24]}"}
    )
    final = provisional.model_copy(
        update={"fingerprint": _execution_fingerprint(provisional)}
    )
    return EvidenceRoundExecution.model_validate(final.model_dump(mode="python"))
