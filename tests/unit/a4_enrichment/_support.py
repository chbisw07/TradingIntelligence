"""Captured, attributable A4.2 fixtures; no live providers or models."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import lru_cache

from scripts._a3_8_fixtures import (
    financial_services,
)
from scripts._a3_8_fixtures import (
    request as workflow_request,
)

from tiaf.a3_hardening import PortableA3ReplayPackage
from tiaf.a4 import A4EvidenceNeed, A4RunRecord, evaluate_projection
from tiaf.a4_enrichment import (
    A4PlannerBridgePlan,
    EvidenceBridgeGrant,
    EvidenceCaptureStatus,
    EvidenceChangeKind,
    EvidenceRoundExecution,
    SuccessorEvidenceCapture,
    admit_evidence_need,
    build_planner_bridge_plan,
    capture_successor_evidence,
    execute_planner_bridge,
)
from tiaf.agents import AgentBudget
from tiaf.source_semantics import (
    ExcludedEvidence,
    Missingness,
    ProjectionBuildInput,
    ProjectionGap,
    SourceEntityRole,
    build_projection,
)
from tiaf.workflows import ControlledServices, default_registry

from ..a3_hardening._support import package_for
from ..source_semantics._support import LATER, NOW, assertion, build_input, occurrence


@dataclass(frozen=True)
class ParentCase:
    package: PortableA3ReplayPackage
    run: A4RunRecord
    need: A4EvidenceNeed


@lru_cache(maxsize=1)
def parent_case() -> ParentCase:
    package = package_for()
    gap = ProjectionGap(
        gap_id="gap:a4-required-evidence",
        missingness=Missingness.REQUIRED,
        code="REQUIRED_EVIDENCE_UNAVAILABLE",
        affected_reference="proposition:revenue",
        reason="captured A4.2 fixture",
    )
    excluded = ExcludedEvidence(
        evidence_id="evidence:outside-cutoff",
        reason="POINT_IN_TIME_INELIGIBLE",
    )
    projection = build_projection(
        build_input(package=package).model_copy(
            update={"gaps": (gap,), "excluded_evidence": (excluded,)}
        )
    )
    run = evaluate_projection(projection, evaluated_at=NOW)
    return ParentCase(package=package, run=run, need=run.result.evidence_needs[0])


def grant(
    case: ParentCase | None = None,
    *,
    tool_calls: int = 1,
    provider_calls: int = 1,
    authority: bool = True,
    deadline: datetime = LATER + timedelta(days=1),
    dedupe: bool = False,
    resolved: bool = False,
) -> EvidenceBridgeGrant:
    case = case or parent_case()
    projection = case.run.input_projection
    return EvidenceBridgeGrant(
        grant_id="grant:a4-enrichment-fixture",
        authority_refs=(projection.header.authority_ref,) if authority else ("authority:other",),
        source_roles=(SourceEntityRole.ISSUER,),
        capabilities=(case.need.requested_capability,),
        entitlement_refs=("entitlement:captured-research",),
        profile_refs=(projection.header.profile_ref,),
        budget_refs=(projection.header.budget_ref,),
        budget=AgentBudget(
            max_tool_calls=tool_calls,
            max_cost_units=float(tool_calls),
            max_elapsed_seconds=30,
        ),
        max_provider_calls=provider_calls,
        deadline=deadline,
        processed_dedupe_keys=(case.need.dedupe_key,) if dedupe else (),
        resolved_need_ids=(case.need.evidence_need_id,) if resolved else (),
    )


@lru_cache(maxsize=1)
def plan_and_execution() -> tuple[A4PlannerBridgePlan, EvidenceRoundExecution]:
    case = parent_case()
    permission = grant(case)
    admission = admit_evidence_need(case.run, case.need, permission, decided_at=NOW)
    template = workflow_request(symbol="SYNTHETIC", calls=1, financials=False)
    plan = build_planner_bridge_plan(
        case.run,
        case.need,
        admission,
        permission,
        template,
        execution_as_of=LATER,
    )
    base_services = financial_services(template)
    acquisition = base_services.acquisitions[0]
    acquisition_request = acquisition.request.model_copy(
        update={
            "allowed_authorities": plan.planner_capabilities,
            "as_of": LATER,
        }
    )
    services = ControlledServices(
        router=base_services.router,
        acquisitions=(
            acquisition.model_copy(
                update={"request": acquisition_request, "material": True}
            ),
        ),
    )
    execution = execute_planner_bridge(
        plan,
        default_registry(),
        services,
        clock=lambda: LATER,
    )
    assert execution.status == "COMPLETED"
    return plan, execution


def successor_input(
    case: ParentCase | None = None,
    *,
    new_value: float = 101.0,
) -> ProjectionBuildInput:
    case = case or parent_case()
    value = build_input(
        package=case.package,
        occurrence_items=(
            occurrence(),
            occurrence(
                "occurrence:two",
                evidence_id="evidence:new",
                acquired_at=LATER,
            ),
        ),
        assertion_items=(
            assertion("assertion:one", 100.0),
            assertion(
                "assertion:two",
                new_value,
                occurrence_id="occurrence:two",
            ),
        ),
        as_of=LATER,
        parent_projection_id=case.run.input_projection.projection_id,
        parent_as_of=case.run.input_projection.header.evidence_as_of,
        new_evidence_ids=("evidence:new",),
    )
    return value.model_copy(
        update={"excluded_evidence": case.run.input_projection.excluded_evidence}
    )


def workflow_new_reference(execution: EvidenceRoundExecution) -> str:
    assert execution.workflow_record is not None
    initial = {
        ref.evidence_id
        for ref in execution.workflow_record.request.inventory.all_references()
    }
    produced = {
        ref.evidence_id
        for inventory in execution.workflow_record.inventories
        for ref in inventory.all_references()
    } - initial
    assert produced
    return sorted(produced)[0]


def captured_new_evidence(
    *,
    change_kind: EvidenceChangeKind = EvidenceChangeKind.SAFE_CONTEXT,
    status: EvidenceCaptureStatus = EvidenceCaptureStatus.NEW_INFORMATION,
    relevant: bool = True,
    live: bool = True,
    affected: tuple[str, ...] | None = None,
) -> SuccessorEvidenceCapture:
    case = parent_case()
    _, execution = plan_and_execution()
    workflow_ref = workflow_new_reference(execution)
    return capture_successor_evidence(
        case.need,
        execution,
        status=status,
        change_kind=change_kind,
        successor_input=successor_input(case),
        new_evidence_ids=("evidence:new",),
        affected_challenge_refs=affected or case.need.challenge_refs,
        resolved_gap_ids=("gap:a4-required-evidence",),
        workflow_evidence_crosswalk=((workflow_ref, "evidence:new"),),
        genuinely_new=True,
        independent=True,
        relevant=relevant,
        live_acquisition=live,
        acquired_at=LATER,
    )
