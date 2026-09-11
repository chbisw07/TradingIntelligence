from dataclasses import replace
from typing import cast

import pytest
from pydantic import ValidationError
from scripts._a3_8_fixtures import (
    confirmation_services,
)
from scripts._a3_8_fixtures import (
    request as workflow_request,
)

from tiaf.a4 import evaluate_projection
from tiaf.a4_enrichment import (
    EnrichmentStopReason,
    EvidenceCaptureStatus,
    EvidenceChangeKind,
    EvidenceNeedAdmission,
    FindingLineageState,
    PlannerBridgeError,
    SuccessorProjectionError,
    WorkflowAdapter,
    admit_evidence_need,
    build_planner_bridge_plan,
    build_successor_outcome,
    capture_successor_evidence,
    execute_planner_bridge,
)
from tiaf.agents import AgentCapability, AgentRegistry
from tiaf.source_semantics import (
    AuthorityApplicability,
    DisputeEvent,
    DisputeState,
    append_dispute_event,
    build_projection,
    compare_assertions,
    create_dispute,
)
from tiaf.workflows import ControlledServices, default_registry

from ..a3_hardening._support import package_for
from ..source_semantics._support import LATER, NOW, assertion, build_input, occurrence
from ._support import (
    ParentCase,
    captured_new_evidence,
    grant,
    parent_case,
    plan_and_execution,
    successor_input,
    workflow_new_reference,
)


def _admission() -> EvidenceNeedAdmission:
    case = parent_case()
    return admit_evidence_need(case.run, case.need, grant(case), decided_at=NOW)


def test_bridge_preserves_semantic_lineage_and_frozen_a2() -> None:
    case = parent_case()
    plan, _ = plan_and_execution()
    request = plan.orchestration_request
    assert plan.evidence_need_id == case.need.evidence_need_id
    assert request.subject == case.need.subject
    assert request.horizon == case.need.horizon
    assert request.as_of == LATER
    assert request.correlation_id == case.run.run_id
    assert request.inventory.a2_pack.deterministic_assessment_id == (
        case.run.input_projection.parents.a2_assessment_id
    )
    assert request.inventory.a2_pack.evidence_fingerprint == (
        case.run.input_projection.parents.a2_evidence_fingerprint
    )
    assert request.no_llm
    assert request.bounds.max_enrichment_rounds == 1
    assert request.bounds.max_replans == 1
    assert request.bounds.max_provider_calls == 1


def test_bridge_uses_coarse_planner_capability_not_provider_or_tool_name() -> None:
    plan, _ = plan_and_execution()
    assert plan.planner_capabilities == (
        AgentCapability.READ_A2_EVIDENCE,
        AgentCapability.READ_FUNDAMENTALS,
        AgentCapability.READ_FILINGS,
    )
    dumped = plan.model_dump_json().lower()
    assert "endpoint" not in dumped
    assert "browser" not in dumped
    assert "broker" not in dumped


def test_bridge_rejects_backdated_execution() -> None:
    case = parent_case()
    with pytest.raises(PlannerBridgeError, match="advance"):
        build_planner_bridge_plan(
            case.run,
            case.need,
            _admission(),
            grant(case),
            workflow_request(symbol="SYNTHETIC", calls=1),
            execution_as_of=NOW,
        )


def test_serial_workflow_execution_is_real_bounded_a38_and_no_model() -> None:
    plan, execution = plan_and_execution()
    assert execution.adapter is WorkflowAdapter.SERIAL
    assert execution.workflow_record is not None
    assert execution.workflow_record.request == plan.orchestration_request
    assert execution.provider_calls == 1
    assert execution.usage.llm_calls == 0
    assert execution.usage.input_tokens == 0
    assert execution.usage.output_tokens == 0


def test_authoritative_confirmation_need_is_admitted_and_resolved() -> None:
    package = package_for()
    initial = build_input(package=package)
    unknown = initial.authority_assessments[0].model_copy(
        update={"applicability": AuthorityApplicability.UNKNOWN}
    )
    projection = build_projection(
        initial.model_copy(update={"authority_assessments": (unknown,)})
    )
    run = evaluate_projection(projection, evaluated_at=NOW)
    case = ParentCase(package=package, run=run, need=run.result.evidence_needs[0])
    permission = grant(case)
    admission = admit_evidence_need(run, case.need, permission, decided_at=NOW)
    template = workflow_request(symbol="SYNTHETIC", calls=1)
    plan = build_planner_bridge_plan(
        run,
        case.need,
        admission,
        permission,
        template,
        execution_as_of=LATER,
    )
    base_services = confirmation_services(template)
    task = base_services.confirmation_tasks[0]
    task_request = task.request.model_copy(
        update={"as_of": LATER, "allowed_authorities": plan.planner_capabilities}
    )
    services = ControlledServices(
        confirmation_gateway=base_services.confirmation_gateway,
        confirmation_tasks=(replace(task, request=task_request),),
    )
    execution = execute_planner_bridge(
        plan,
        default_registry(),
        services,
        clock=lambda: LATER,
    )
    successor = build_input(
        package=package,
        occurrence_items=(
            occurrence(),
            occurrence("occurrence:two", evidence_id="evidence:new", acquired_at=LATER),
        ),
        assertion_items=(
            assertion("assertion:one", 100.0),
            assertion("assertion:two", 100.0, occurrence_id="occurrence:two"),
        ),
        as_of=LATER,
        parent_projection_id=projection.projection_id,
        parent_as_of=projection.header.evidence_as_of,
        new_evidence_ids=("evidence:new",),
    )
    capture = capture_successor_evidence(
        case.need,
        execution,
        status=EvidenceCaptureStatus.NEW_INFORMATION,
        change_kind=EvidenceChangeKind.CONFIRMATION,
        successor_input=successor,
        new_evidence_ids=("evidence:new",),
        affected_challenge_refs=case.need.challenge_refs,
        workflow_evidence_crosswalk=(
            (workflow_new_reference(execution), "evidence:new"),
        ),
        genuinely_new=True,
        independent=True,
        relevant=True,
        live_acquisition=True,
        acquired_at=LATER,
    )
    outcome = build_successor_outcome(
        run,
        case.need,
        admission,
        plan,
        execution,
        capture,
        completed_at=LATER,
    )
    assert plan.orchestration_request.permit_confirmation
    assert outcome.stop_reason is EnrichmentStopReason.RESOLVED
    assert outcome.final_disposition == "SUPPORTIVE"


def test_confirmation_not_found_is_no_information_and_remains_unresolved() -> None:
    case = parent_case()
    plan, execution = plan_and_execution()
    capture = capture_successor_evidence(
        case.need,
        execution,
        status=EvidenceCaptureStatus.NO_NEW_INFORMATION,
        change_kind=EvidenceChangeKind.EQUIVALENT,
        reused_evidence_ids=("evidence:one",),
        genuinely_new=False,
        independent=None,
        relevant=True,
        live_acquisition=False,
        acquired_at=LATER,
        failure_codes=("CONFIRMATION_NOT_FOUND",),
    )
    outcome = build_successor_outcome(
        case.run,
        case.need,
        _admission(),
        plan,
        execution,
        capture,
        completed_at=LATER,
    )
    assert outcome.stop_reason is EnrichmentStopReason.NO_NEW_INFORMATION
    assert outcome.evidence_capture is not None
    assert outcome.evidence_capture.failure_codes == ("CONFIRMATION_NOT_FOUND",)
    assert outcome.final_disposition == "INSUFFICIENT_EVIDENCE"


def test_safe_new_context_builds_later_successor_without_mutating_parent() -> None:
    case = parent_case()
    parent_json = case.run.model_dump_json()
    plan, execution = plan_and_execution()
    outcome = build_successor_outcome(
        case.run,
        case.need,
        _admission(),
        plan,
        execution,
        captured_new_evidence(),
        completed_at=LATER,
    )
    assert outcome.stop_reason is EnrichmentStopReason.RESOLVED
    assert outcome.successor_projection is not None
    assert outcome.successor_projection.header.evidence_as_of == LATER
    assert outcome.successor_projection.parent_projection_id == (
        case.run.input_projection.projection_id
    )
    assert outcome.successor_projection.parents == case.run.input_projection.parents
    assert outcome.successor_a4_run is not None
    assert outcome.original_disposition == "INSUFFICIENT_EVIDENCE"
    assert outcome.final_disposition == "SUPPORTIVE"
    assert case.run.model_dump_json() == parent_json


def test_successor_a4_reevaluation_failure_is_a_distinct_conservative_stop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = parent_case()
    plan, execution = plan_and_execution()

    def fail_reevaluation(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise RuntimeError("captured deterministic re-evaluation failure")

    monkeypatch.setattr(
        "tiaf.a4_enrichment.successor.evaluate_projection", fail_reevaluation
    )
    outcome = build_successor_outcome(
        case.run,
        case.need,
        _admission(),
        plan,
        execution,
        captured_new_evidence(),
        completed_at=LATER,
    )

    assert outcome.stop_reason is EnrichmentStopReason.REEVALUATION_FAILED
    assert outcome.failure_codes == ("REEVALUATION_RUNTIMEERROR",)
    assert outcome.final_disposition == outcome.original_disposition
    assert outcome.successor_projection is None
    assert outcome.successor_a4_run is None


def test_only_affected_finding_is_recomputed_and_unaffected_is_preserved() -> None:
    case = parent_case()
    plan, execution = plan_and_execution()
    outcome = build_successor_outcome(
        case.run,
        case.need,
        _admission(),
        plan,
        execution,
        captured_new_evidence(),
        completed_at=LATER,
    )
    states = {item.reason_code: item.state for item in outcome.finding_lineage}
    assert states["REQUIRED_EVIDENCE_UNAVAILABLE"] is FindingLineageState.RECOMPUTED
    assert states["EVIDENCE_EXCLUDED_BY_PROJECTION"] is FindingLineageState.PRESERVED


@pytest.mark.parametrize(
    "change_kind",
    [EvidenceChangeKind.PRICE_OR_MARKET_STATE, EvidenceChangeKind.SPECIALIST_INPUT],
)
def test_lower_layer_change_requires_upstream_refresh(change_kind: EvidenceChangeKind) -> None:
    case = parent_case()
    plan, execution = plan_and_execution()
    outcome = build_successor_outcome(
        case.run,
        case.need,
        _admission(),
        plan,
        execution,
        captured_new_evidence(change_kind=change_kind),
        completed_at=LATER,
    )
    assert outcome.stop_reason is EnrichmentStopReason.UPSTREAM_REFRESH_REQUIRED
    assert outcome.successor_projection is None
    assert outcome.successor_a4_run is None
    assert outcome.final_disposition == outcome.original_disposition


def test_duplicate_wrapper_stops_as_no_new_information() -> None:
    case = parent_case()
    plan, execution = plan_and_execution()
    capture = capture_successor_evidence(
        case.need,
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
    outcome = build_successor_outcome(
        case.run,
        case.need,
        _admission(),
        plan,
        execution,
        capture,
        completed_at=LATER,
    )
    assert outcome.stop_reason is EnrichmentStopReason.NO_NEW_INFORMATION
    assert outcome.final_disposition == "INSUFFICIENT_EVIDENCE"
    assert outcome.successor_cycles == 0


def test_no_information_contract_rejects_fabricated_new_ids() -> None:
    case = parent_case()
    _, execution = plan_and_execution()
    with pytest.raises(ValidationError):
        capture_successor_evidence(
            case.need,
            execution,
            status=EvidenceCaptureStatus.NO_NEW_INFORMATION,
            change_kind=EvidenceChangeKind.EQUIVALENT,
            new_evidence_ids=("evidence:new",),
            workflow_evidence_crosswalk=(
                (workflow_new_reference(execution), "evidence:new"),
            ),
            genuinely_new=True,
            independent=None,
            relevant=True,
            live_acquisition=False,
            acquired_at=LATER,
        )


def test_every_new_evidence_id_requires_workflow_crosswalk() -> None:
    case = parent_case()
    _, execution = plan_and_execution()
    with pytest.raises(SuccessorProjectionError, match="crosswalk"):
        capture_successor_evidence(
            case.need,
            execution,
            status=EvidenceCaptureStatus.NEW_INFORMATION,
            change_kind=EvidenceChangeKind.CONFIRMATION,
            successor_input=successor_input(),
            new_evidence_ids=("evidence:new",),
            genuinely_new=True,
            independent=True,
            relevant=True,
            live_acquisition=True,
            acquired_at=LATER,
        )


def test_partial_evidence_remains_explicit_and_bounded() -> None:
    case = parent_case()
    plan, execution = plan_and_execution()
    capture = captured_new_evidence(status=EvidenceCaptureStatus.PARTIAL)
    outcome = build_successor_outcome(
        case.run,
        case.need,
        _admission(),
        plan,
        execution,
        capture,
        completed_at=LATER,
    )
    assert outcome.evidence_capture is not None
    assert outcome.evidence_capture.status is EvidenceCaptureStatus.PARTIAL
    assert outcome.enrichment_rounds == 1
    assert outcome.successor_cycles <= 1


def test_factual_conflict_kind_is_preserved_without_favorable_assumption() -> None:
    case = parent_case()
    plan, execution = plan_and_execution()
    successor = successor_input(case, new_value=120.0)
    left, right = successor.assertions
    comparison = compare_assertions(
        left,
        right,
        comparison_policy_id="comparison-policy:default",
        comparison_policy_version="1.0",
    )
    dispute = create_dispute(
        left,
        right,
        comparison,
        event=DisputeEvent(
            event_id="dispute-event:detected-later",
            state=DisputeState.DETECTED,
            recorded_at=LATER,
            policy_id="dispute-policy:default",
            policy_version="1.0",
            reason="captured incompatible successor values",
        ),
    )
    dispute = append_dispute_event(
        dispute,
        DisputeEvent(
            event_id="dispute-event:unresolved-later",
            state=DisputeState.UNRESOLVED,
            recorded_at=LATER,
            evidence_ids=("evidence:one", "evidence:new"),
            policy_id="dispute-policy:default",
            policy_version="1.0",
            reason="captured factual conflict remains unresolved",
        ),
    )
    successor = successor.model_copy(
        update={"comparisons": (comparison,), "disputes": (dispute,)}
    )
    capture = capture_successor_evidence(
        case.need,
        execution,
        status=EvidenceCaptureStatus.NEW_INFORMATION,
        change_kind=EvidenceChangeKind.FACTUAL_CONFLICT,
        successor_input=successor,
        new_evidence_ids=("evidence:new",),
        affected_challenge_refs=case.need.challenge_refs,
        workflow_evidence_crosswalk=(
            (workflow_new_reference(execution), "evidence:new"),
        ),
        genuinely_new=True,
        independent=False,
        relevant=True,
        live_acquisition=True,
        acquired_at=LATER,
    )
    outcome = build_successor_outcome(
        case.run,
        case.need,
        _admission(),
        plan,
        execution,
        capture,
        completed_at=LATER,
    )
    assert outcome.evidence_capture is not None
    assert outcome.evidence_capture.change_kind is EvidenceChangeKind.FACTUAL_CONFLICT
    assert outcome.successor_projection is not None
    assert outcome.successor_projection.disputes[-1].events[-1].state is DisputeState.UNRESOLVED
    assert outcome.final_disposition != "SUPPORTIVE"
    assert outcome.provider_calls <= 1


def test_acquisition_failure_never_improves_parent_disposition() -> None:
    case = parent_case()
    plan, _ = plan_and_execution()
    failed = execute_planner_bridge(
        plan,
        cast(AgentRegistry, None),
        ControlledServices(),
        clock=lambda: LATER,
    )
    outcome = build_successor_outcome(
        case.run,
        case.need,
        _admission(),
        plan,
        failed,
        None,
        completed_at=LATER,
    )
    assert failed.status == "FAILED"
    assert outcome.stop_reason is EnrichmentStopReason.ACQUISITION_FAILED
    assert outcome.final_disposition == outcome.original_disposition
    assert outcome.successor_cycles == 0
