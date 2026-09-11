"""Successor capture, projection, and bounded A4 re-evaluation semantics."""

from datetime import datetime
from typing import Any, cast

from tiaf.a4 import A4EvidenceNeed, A4RunRecord, ChallengeFinding, evaluate_projection
from tiaf.agents import AgentUsage
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.planner.digests import digest
from tiaf.source_semantics import ProjectionBuildInput, build_projection, validate_successor

from .contracts import (
    A4EnrichmentOutcome,
    A4PlannerBridgePlan,
    EvidenceNeedAdmission,
    EvidenceRoundExecution,
    FindingLineage,
    SuccessorEvidenceCapture,
)
from .enums import (
    EnrichmentStopReason,
    EvidenceCaptureStatus,
    EvidenceChangeKind,
    EvidenceNeedAdmissionOutcome,
    FindingLineageState,
)


class SuccessorProjectionError(ValueError):
    """Captured enrichment cannot safely form an A4 successor."""


def _disposition_value(run: A4RunRecord) -> str:
    disposition = run.result.disposition
    if disposition is None:
        raise SuccessorProjectionError("failed A4 run has no enrichable disposition")
    return disposition.value


def _capture_fingerprint(capture: SuccessorEvidenceCapture) -> str:
    return digest(capture.model_dump(mode="json", exclude={"fingerprint"}))


def capture_successor_evidence(
    need: A4EvidenceNeed,
    execution: EvidenceRoundExecution,
    *,
    status: EvidenceCaptureStatus,
    change_kind: EvidenceChangeKind,
    successor_input: ProjectionBuildInput | None = None,
    new_evidence_ids: tuple[str, ...] = (),
    reused_evidence_ids: tuple[str, ...] = (),
    affected_challenge_refs: tuple[str, ...] = (),
    resolved_gap_ids: tuple[str, ...] = (),
    workflow_evidence_crosswalk: tuple[tuple[str, str], ...] = (),
    genuinely_new: bool,
    independent: bool | None,
    relevant: bool,
    live_acquisition: bool,
    acquired_at: datetime,
    failure_codes: tuple[str, ...] = (),
) -> SuccessorEvidenceCapture:
    """Seal already-normalized source-semantic evidence from the workflow side."""
    typed_input = (
        ProjectionBuildInput.model_validate(successor_input)
        if successor_input is not None
        else None
    )
    if execution.status != "COMPLETED" and status is not EvidenceCaptureStatus.FAILED:
        raise SuccessorProjectionError("failed execution cannot yield evidence")
    if execution.workflow_record is None:
        known_workflow_ids: set[str] = set()
        new_workflow_ids: set[str] = set()
        workflow_fingerprint = "0" * 64
    else:
        workflow_fingerprint = execution.workflow_record.fingerprint
        initial_workflow_ids = {
            ref.evidence_id
            for ref in execution.workflow_record.request.inventory.all_references()
        }
        known_workflow_ids = {
            ref.evidence_id
            for inventory in execution.workflow_record.inventories
            for ref in inventory.all_references()
        } | {item.artifact_id for item in execution.workflow_record.artifacts}
        new_workflow_ids = known_workflow_ids - initial_workflow_ids
    if any(left not in known_workflow_ids for left, _ in workflow_evidence_crosswalk):
        raise SuccessorProjectionError("successor evidence crosswalk has unknown workflow input")
    if genuinely_new and any(
        left not in new_workflow_ids for left, _ in workflow_evidence_crosswalk
    ):
        raise SuccessorProjectionError(
            "genuinely new evidence must crosswalk from workflow-produced output"
        )
    if new_evidence_ids and set(new_evidence_ids) != {
        right for _, right in workflow_evidence_crosswalk
    }:
        raise SuccessorProjectionError("every new semantic evidence ID requires a crosswalk")
    information = digest(
        {
            "new": tuple(sorted(new_evidence_ids)),
            "reused": tuple(sorted(reused_evidence_ids)),
            "change": change_kind,
            "relevant": relevant,
            "successor": typed_input.model_dump(mode="json") if typed_input else None,
        }
    )
    provisional = SuccessorEvidenceCapture.model_construct(
        capture_id="a4-successor-evidence:pending",
        evidence_need_id=need.evidence_need_id,
        workflow_run_fingerprint=workflow_fingerprint,
        status=status,
        change_kind=change_kind,
        successor_input=typed_input,
        new_evidence_ids=tuple(sorted(new_evidence_ids)),
        reused_evidence_ids=tuple(sorted(reused_evidence_ids)),
        affected_challenge_refs=tuple(sorted(affected_challenge_refs)),
        resolved_gap_ids=tuple(sorted(resolved_gap_ids)),
        workflow_evidence_crosswalk=tuple(sorted(workflow_evidence_crosswalk)),
        genuinely_new=genuinely_new,
        independent=independent,
        relevant=relevant,
        live_acquisition=live_acquisition,
        acquired_at=acquired_at,
        usage=execution.usage,
        failure_codes=failure_codes,
        information_fingerprint=information,
        fingerprint="0" * 64,
    )
    identity = digest(
        provisional.model_dump(
            mode="json", exclude={"capture_id": True, "fingerprint": True}
        )
    )
    provisional = provisional.model_copy(
        update={"capture_id": f"a4-successor-evidence:{identity[:24]}"}
    )
    final = provisional.model_copy(update={"fingerprint": _capture_fingerprint(provisional)})
    return SuccessorEvidenceCapture.model_validate(final.model_dump(mode="python"))


def _finding_key(finding: ChallengeFinding) -> tuple[object, ...]:
    return (
        finding.family,
        finding.reason_code,
        finding.materiality,
        finding.status,
        finding.dispute_refs,
    )


def _lineage(
    parent: A4RunRecord,
    successor: A4RunRecord,
    affected: set[str],
) -> tuple[FindingLineage, ...]:
    remaining = list(successor.result.challenge_findings)
    lineage: list[FindingLineage] = []
    for old in parent.result.challenge_findings:
        match = next((item for item in remaining if _finding_key(item) == _finding_key(old)), None)
        if match is not None:
            remaining.remove(match)
        state = (
            FindingLineageState.RECOMPUTED
            if old.finding_id in affected
            else FindingLineageState.PRESERVED
            if match is not None
            else FindingLineageState.RESOLVED
        )
        lineage.append(
            FindingLineage(
                parent_finding_ref=old.finding_id,
                successor_finding_ref=match.finding_id if match else None,
                family=old.family.value,
                reason_code=old.reason_code,
                state=state,
            )
        )
    lineage.extend(
        FindingLineage(
            successor_finding_ref=item.finding_id,
            family=item.family.value,
            reason_code=item.reason_code,
            state=FindingLineageState.NEW,
        )
        for item in remaining
    )
    return tuple(lineage)


def _seal_outcome(**values: object) -> A4EnrichmentOutcome:
    provisional = A4EnrichmentOutcome.model_construct(
        **cast(Any, values),
        outcome_id="a4-enrichment-outcome:pending",
        fingerprint="0" * 64,
    )
    identity = digest(
        provisional.model_dump(
            mode="json", exclude={"outcome_id": True, "fingerprint": True}
        )
    )
    provisional = provisional.model_copy(
        update={"outcome_id": f"a4-enrichment-outcome:{identity[:24]}"}
    )
    fingerprint = digest(provisional.model_dump(mode="json", exclude={"fingerprint"}))
    final = provisional.model_copy(update={"fingerprint": fingerprint})
    return A4EnrichmentOutcome.model_validate(final.model_dump(mode="python"))


def denied_outcome(
    parent: A4RunRecord,
    need: A4EvidenceNeed,
    admission: EvidenceNeedAdmission,
    *,
    completed_at: datetime | None = None,
) -> A4EnrichmentOutcome:
    if admission.outcome is EvidenceNeedAdmissionOutcome.ADMITTED:
        raise SuccessorProjectionError("admitted need is not a denied outcome")
    disposition = _disposition_value(parent)
    return _seal_outcome(
        parent_a4_run_id=parent.run_id,
        parent_a4_result_id=parent.result.result_id,
        parent_projection_id=parent.input_projection.projection_id,
        evidence_need_id=need.evidence_need_id,
        admission=admission,
        stop_reason=EnrichmentStopReason.ADMISSION_DENIED,
        original_disposition=disposition,
        final_disposition=disposition,
        enrichment_rounds=0,
        successor_cycles=0,
        provider_calls=0,
        usage=AgentUsage(),
        failure_codes=(admission.reason_code,),
        completed_at=completed_at or datetime.now(TIAF_TIMEZONE),
    )


def build_successor_outcome(
    parent: A4RunRecord,
    need: A4EvidenceNeed,
    admission: EvidenceNeedAdmission,
    plan: A4PlannerBridgePlan,
    execution: EvidenceRoundExecution,
    capture: SuccessorEvidenceCapture | None,
    *,
    completed_at: datetime | None = None,
) -> A4EnrichmentOutcome:
    """Stop or build one successor; the parent projection/result are never changed."""
    when = completed_at or datetime.now(TIAF_TIMEZONE)
    original = _disposition_value(parent)
    common: dict[str, object] = {
        "parent_a4_run_id": parent.run_id,
        "parent_a4_result_id": parent.result.result_id,
        "parent_projection_id": parent.input_projection.projection_id,
        "evidence_need_id": need.evidence_need_id,
        "admission": admission,
        "bridge_plan": plan,
        "execution": execution,
        "evidence_capture": capture,
        "original_disposition": original,
        "final_disposition": original,
        "enrichment_rounds": 1,
        "successor_cycles": 0,
        "provider_calls": execution.provider_calls,
        "usage": execution.usage,
        "completed_at": when,
    }
    if execution.status == "FAILED":
        return _seal_outcome(
            **common,
            stop_reason=EnrichmentStopReason.ACQUISITION_FAILED,
            failure_codes=execution.failure_codes,
        )
    if capture is None:
        raise SuccessorProjectionError("completed execution requires an evidence capture")
    workflow_record = execution.workflow_record
    if workflow_record is None:
        raise SuccessorProjectionError("completed execution is missing its workflow record")
    if capture.workflow_run_fingerprint != workflow_record.fingerprint:
        raise SuccessorProjectionError("evidence capture workflow lineage mismatch")
    if capture.status is EvidenceCaptureStatus.FAILED:
        return _seal_outcome(
            **common,
            stop_reason=EnrichmentStopReason.ACQUISITION_FAILED,
            failure_codes=capture.failure_codes,
        )
    if (
        capture.status is EvidenceCaptureStatus.NO_NEW_INFORMATION
        or not capture.relevant
        or capture.change_kind in {EvidenceChangeKind.EQUIVALENT, EvidenceChangeKind.IRRELEVANT}
    ):
        return _seal_outcome(
            **common,
            stop_reason=EnrichmentStopReason.NO_NEW_INFORMATION,
            failure_codes=("NO_NEW_INFORMATION",),
        )
    if capture.change_kind in {
        EvidenceChangeKind.PRICE_OR_MARKET_STATE,
        EvidenceChangeKind.SPECIALIST_INPUT,
    }:
        return _seal_outcome(
            **common,
            stop_reason=EnrichmentStopReason.UPSTREAM_REFRESH_REQUIRED,
            failure_codes=("LOWER_LAYER_RECOMPUTATION_REQUIRED",),
        )
    if capture.successor_input is None:
        raise SuccessorProjectionError("new safe evidence requires a successor build input")
    if not set(capture.affected_challenge_refs) <= {
        item.finding_id for item in parent.result.challenge_findings
    }:
        raise SuccessorProjectionError("affected challenge reference is unresolved")
    try:
        successor_input = validate_successor(parent.input_projection, capture.successor_input)
        successor_projection = build_projection(successor_input)
        if successor_projection.parents != parent.input_projection.parents:
            raise SuccessorProjectionError("A2/A3 frozen parent identity changed")
        if capture.live_acquisition and (
            successor_projection.header.evidence_as_of
            <= parent.input_projection.header.evidence_as_of
            or successor_projection.header.evidence_as_of != capture.acquired_at
        ):
            raise SuccessorProjectionError("live successor acquisition/as-of is not truthful")
    except Exception as exc:
        return _seal_outcome(
            **common,
            stop_reason=EnrichmentStopReason.SUCCESSOR_FAILED,
            failure_codes=(f"SUCCESSOR_{type(exc).__name__.upper()}",),
        )
    try:
        successor_run = evaluate_projection(
            successor_projection,
            policy=parent.policy,
            evaluated_at=when,
        )
    except Exception as exc:
        return _seal_outcome(
            **common,
            stop_reason=EnrichmentStopReason.REEVALUATION_FAILED,
            failure_codes=(f"REEVALUATION_{type(exc).__name__.upper()}",),
        )
    lineage = _lineage(parent, successor_run, set(capture.affected_challenge_refs))
    unresolved = {
        item.finding_id
        for item in successor_run.result.challenge_findings
        if item.evidence_need_ref is not None
    }
    resolved_requested = all(
        item.successor_finding_ref not in unresolved
        for item in lineage
        if item.parent_finding_ref in set(capture.affected_challenge_refs)
    )
    final_values = {
        **common,
        "successor_projection": successor_projection,
        "successor_a4_run": successor_run,
        "finding_lineage": lineage,
        "stop_reason": (
            EnrichmentStopReason.RESOLVED
            if resolved_requested
            else EnrichmentStopReason.ROUND_LIMIT
        ),
        "final_disposition": _disposition_value(successor_run),
        "successor_cycles": 1,
        "failure_codes": ("ENRICHMENT_ROUND_LIMIT_REACHED",)
        if not resolved_requested
        else (),
    }
    return _seal_outcome(**final_values)
