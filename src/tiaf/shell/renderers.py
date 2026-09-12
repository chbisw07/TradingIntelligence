"""Allowlisted human and JSON projections for accepted facade results."""

import json
from collections.abc import Mapping
from typing import Any

from tiaf.facade import (
    A4EvaluateResult,
    A4InputProjectResult,
    BaselineAssessResult,
    CapabilityDescriptor,
    CapabilityListResult,
    OpportunityAssembleResult,
    PositionAssessResult,
    RecordedReplayResult,
    ReplayVerifyResult,
)

from .commands import ExplainLastCommand, LastView, ShowLastCommand, TraceLastCommand, TraceView
from .dispatcher import DispatchOutcome
from .errors import ShellError, ShellErrorCode, shell_error
from .session import SessionDefaults, ShellFacadeResult, SuccessfulInvocation


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _facade_envelope(invocation: SuccessfulInvocation) -> dict[str, Any]:
    result = invocation.result
    return {
        "schema_id": "tiaf.shell.result-envelope",
        "schema_version": "1.0",
        "grammar_version": "0.1",
        "shell_invocation_id": invocation.record.shell_invocation_id,
        "parent_shell_invocation_id": invocation.record.parent_shell_invocation_id,
        "command_name": invocation.record.command_name,
        "capability_id": result.metadata.capability_id,
        "capability_version": result.metadata.capability_version,
        "request_id": result.metadata.request_id,
        "correlation_id": result.metadata.correlation_id,
        "facade_run_id": result.metadata.run_id,
        "status": result.metadata.status.value,
        "effect": result.metadata.effect.value,
        "result_schema_id": result.schema_id,
        "result_schema_version": result.schema_version,
        "result": result.model_dump(mode="json"),
    }


def _context_payload(defaults: SessionDefaults) -> dict[str, Any]:
    return {
        "schema_id": "tiaf.shell.context",
        "schema_version": "1.0",
        "context": defaults.model_dump(mode="json"),
        "authority_note": "requested defaults do not grant authority",
    }


def _summary(result: ShellFacadeResult) -> dict[str, Any]:
    metadata = result.metadata
    base: dict[str, Any] = {
        "capability": metadata.capability_id,
        "status": metadata.status.value,
        "effect": metadata.effect.value,
        "run_id": metadata.run_id,
        "subject": metadata.subject,
        "objective": metadata.objective.value if metadata.objective is not None else None,
        "horizon": metadata.horizon.model_dump(mode="json") if metadata.horizon else None,
        "as_of": metadata.as_of.isoformat() if metadata.as_of else None,
        "warnings": list(metadata.warnings),
        "gaps": list(metadata.gaps),
        "usage": metadata.usage.model_dump(mode="json"),
    }
    if isinstance(result, CapabilityListResult):
        base["capabilities"] = [item.capability_id for item in result.capabilities]
    elif isinstance(result, BaselineAssessResult):
        assessment = result.assessment
        base.update(
            direction=assessment.market_state.direction.value,
            candidate_class=assessment.candidate_class.value,
            opportunity_score=assessment.opportunity_score,
            maturity_score=assessment.maturity_score,
            chase_risk_score=assessment.chase_risk_score,
            eligible=assessment.eligible,
            reasons=[item.value for item in assessment.explanation_codes],
            warnings=[*base["warnings"], *assessment.warnings],
        )
    elif isinstance(result, OpportunityAssembleResult):
        intelligence = result.intelligence
        base.update(
            state=intelligence.summary.state.value,
            headline=intelligence.summary.bias.headline.value,
            price_direction=intelligence.summary.bias.price_direction.value,
            reasons=[item.code for item in intelligence.reasons],
            contradictions=[item.code for item in intelligence.contradictions],
            completeness_gaps=list(intelligence.completeness.gaps),
            run_fingerprint=result.run_fingerprint,
        )
    elif isinstance(result, A4InputProjectResult):
        projection = result.projection
        base.update(
            projection_id=projection.projection_id,
            projection_fingerprint=projection.semantic_fingerprint,
            disputes=[item.dispute_id for item in projection.disputes],
            projection_gaps=[item.code for item in projection.gaps],
        )
    elif isinstance(result, A4EvaluateResult):
        evaluation = result.evaluation
        base.update(
            execution_status=evaluation.execution_status.value,
            disposition=evaluation.disposition.value if evaluation.disposition else None,
            primary_thesis=evaluation.primary_thesis.thesis_id,
            counter_thesis=(
                evaluation.counter_thesis.thesis_id if evaluation.counter_thesis else None
            ),
            surviving_theses=list(evaluation.surviving_thesis_refs),
            residual_uncertainties=len(evaluation.residual_uncertainties),
            evidence_needs=len(evaluation.evidence_needs),
            run_fingerprint=result.run_fingerprint,
            semantic_fingerprint=evaluation.semantic_fingerprint,
        )
    elif isinstance(result, PositionAssessResult):
        position_assessment = result.assessment
        expression_note = None
        if (
            position_assessment.protection_intent.kind.value
            == "EXPRESSION_REFRESH_REQUIRED"
        ):
            expression_note = "expression refresh required; no replacement selected"
        base.update(
            position_id=position_assessment.position_id,
            snapshot_id=position_assessment.snapshot_id,
            snapshot_at=position_assessment.snapshot_at.isoformat(),
            freshness=position_assessment.effective_freshness.value,
            execution_status=position_assessment.status.value,
            posture=position_assessment.posture.value,
            thesis_health=position_assessment.thesis_health.value,
            recommendation=position_assessment.recommendation.value,
            protection_intent=position_assessment.protection_intent.kind.value,
            remaining_opportunity=position_assessment.remaining_opportunity.value,
            monitoring_needs=[
                item.need_id for item in position_assessment.monitoring_needs
            ],
            monitoring_statement=result.monitoring_statement,
            reasons=list(position_assessment.reason_codes),
            result_gaps=list(position_assessment.gaps),
            linked_a4_result_id=position_assessment.linked_a4_result_id,
            run_fingerprint=result.run_fingerprint,
            semantic_fingerprint=position_assessment.semantic_fingerprint,
            replay_identity=position_assessment.replay_identity,
            authority_statement=position_assessment.authority_statement,
            expression_refresh_note=expression_note,
        )
    elif isinstance(result, RecordedReplayResult):
        base["replay_kind"] = result.kind.value
        if result.a3_replay is not None:
            base.update(
                replay_id=result.a3_replay.replay_id,
                semantic_match=result.a3_replay.semantic_match,
                replay_fingerprint=result.a3_replay.fingerprint,
            )
        if result.foundation_projection is not None:
            base.update(
                projection_id=result.foundation_projection.projection_id,
                replay_fingerprint=result.foundation_projection.semantic_fingerprint,
            )
        if result.a5_replay is not None:
            base.update(
                replay_id=result.a5_replay.replay_id,
                replay_fingerprint=result.a5_replay.fingerprint,
                position_semantic_fingerprint=(
                    result.a5_replay.record.result.semantic_fingerprint
                ),
            )
    elif isinstance(result, ReplayVerifyResult):
        base["verification"] = result.verification.model_dump(mode="json")
    return base


def _reasons(result: ShellFacadeResult) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "warnings": list(result.metadata.warnings),
        "gaps": list(result.metadata.gaps),
    }
    if isinstance(result, BaselineAssessResult):
        payload.update(
            assessment_reasons=[item.value for item in result.assessment.explanation_codes],
            market_state_reasons=[
                item.value for item in result.assessment.market_state.explanation_codes
            ],
            component_reasons={
                item.component.value: [code.value for code in item.explanation_codes]
                for item in result.assessment.market_state.components
            },
        )
    elif isinstance(result, OpportunityAssembleResult):
        payload["reasons"] = [item.model_dump(mode="json") for item in result.intelligence.reasons]
    elif isinstance(result, A4InputProjectResult):
        payload["projection_gaps"] = [
            item.model_dump(mode="json") for item in result.projection.gaps
        ]
    elif isinstance(result, A4EvaluateResult):
        evaluation = result.evaluation
        payload.update(
            primary_conclusion=evaluation.primary_thesis.conclusion_relation,
            primary_gaps=list(evaluation.primary_thesis.gaps),
            primary_risks=list(evaluation.primary_thesis.risks),
            challenge_reason_codes=[item.reason_code for item in evaluation.challenge_findings],
            arbitration_reason_codes=[
                item.reason_code for item in evaluation.arbitration_findings
            ],
        )
    elif isinstance(result, PositionAssessResult):
        payload.update(
            reason_codes=list(result.assessment.reason_codes),
            freshness_reasons=list(result.assessment.freshness_reasons),
            protection_reason_codes=list(
                result.assessment.protection_intent.reason_codes
            ),
            monitoring_reason_codes=[
                item.reason_code for item in result.assessment.monitoring_needs
            ],
        )
    return payload


def _gaps(result: ShellFacadeResult) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "metadata_gaps": list(result.metadata.gaps),
        "warnings": list(result.metadata.warnings),
    }
    if isinstance(result, BaselineAssessResult):
        payload.update(
            unavailable_components=[
                item.component.value
                for item in result.assessment.market_state.components
                if not item.available
            ],
            evidence_warnings=list(result.assessment.warnings),
        )
    elif isinstance(result, OpportunityAssembleResult):
        payload.update(
            completeness_gaps=list(result.intelligence.completeness.gaps),
            prerequisites=[
                item.model_dump(mode="json") for item in result.intelligence.prerequisites
            ],
        )
    elif isinstance(result, A4InputProjectResult):
        payload.update(
            projection_gaps=[item.model_dump(mode="json") for item in result.projection.gaps],
            excluded_evidence=[
                item.model_dump(mode="json") for item in result.projection.excluded_evidence
            ],
        )
    elif isinstance(result, A4EvaluateResult):
        evaluation = result.evaluation
        payload.update(
            primary_gaps=list(evaluation.primary_thesis.gaps),
            counter_gaps=(
                list(evaluation.counter_thesis.gaps) if evaluation.counter_thesis else []
            ),
            residual_uncertainties=[
                item.model_dump(mode="json") for item in evaluation.residual_uncertainties
            ],
            evidence_needs=[item.model_dump(mode="json") for item in evaluation.evidence_needs],
            failures=[item.model_dump(mode="json") for item in evaluation.failures],
        )
    elif isinstance(result, PositionAssessResult):
        payload.update(
            position_gaps=list(result.assessment.gaps),
            failure_codes=[item.value for item in result.assessment.failure_codes],
        )
    return payload


def _contradictions(result: ShellFacadeResult) -> dict[str, Any]:
    values: list[Any]
    if isinstance(result, OpportunityAssembleResult):
        values = [item.model_dump(mode="json") for item in result.intelligence.contradictions]
    elif isinstance(result, A4InputProjectResult):
        values = [item.model_dump(mode="json") for item in result.projection.disputes]
    elif isinstance(result, A4EvaluateResult):
        evaluation = result.evaluation
        values = [
            {
                "counter_thesis": (
                    evaluation.counter_thesis.model_dump(mode="json")
                    if evaluation.counter_thesis
                    else None
                ),
                "challenge_findings": [
                    item.model_dump(mode="json") for item in evaluation.challenge_findings
                ],
                "arbitration_dissent": [
                    list(item.dissent_refs) for item in evaluation.arbitration_findings
                ],
            }
        ]
    elif isinstance(result, PositionAssessResult):
        values = list(result.assessment.contradictions)
    else:
        values = []
    return {"contradictions": values}


def _evidence(result: ShellFacadeResult) -> dict[str, Any]:
    if isinstance(result, BaselineAssessResult):
        return {
            "context_ids": list(result.assessment.evidence_context_ids),
            "bundle_ids": list(result.assessment.evidence_bundle_ids),
            "freshness": [
                item.model_dump(mode="json") for item in result.assessment.evidence_freshness
            ],
        }
    if isinstance(result, OpportunityAssembleResult):
        return {
            "reason_sources": [
                source.model_dump(mode="json")
                for reason in result.intelligence.reasons
                for source in reason.sources
            ],
            "lineages": [item.model_dump(mode="json") for item in result.intelligence.lineages],
            "baseline_evidence_ids": list(result.intelligence.baseline.evidence_ids),
        }
    if isinstance(result, A4InputProjectResult):
        return {
            "sources": [item.model_dump(mode="json") for item in result.projection.sources],
            "occurrences": [
                item.model_dump(mode="json") for item in result.projection.occurrences
            ],
            "assertions": [
                item.model_dump(mode="json") for item in result.projection.assertions
            ],
            "admissions": [
                item.model_dump(mode="json") for item in result.projection.admissions
            ],
        }
    if isinstance(result, A4EvaluateResult):
        evaluation = result.evaluation
        return {
            "premises": [item.model_dump(mode="json") for item in evaluation.premises],
            "challenge_refs": [
                {
                    "support": list(item.cited_support_refs),
                    "opposition": list(item.cited_opposition_refs),
                    "disputes": list(item.dispute_refs),
                }
                for item in evaluation.challenge_findings
            ],
            "decisive_evidence_refs": [
                list(item.decisive_evidence_refs) for item in evaluation.arbitration_findings
            ],
            "invalidation_conditions": [
                item.model_dump(mode="json") for item in evaluation.invalidation_conditions
            ],
        }
    if isinstance(result, PositionAssessResult):
        return {
            "evidence_refs": list(result.assessment.evidence_refs),
            "linked_a4_result_id": result.assessment.linked_a4_result_id,
            "linked_a4_fingerprint": result.assessment.linked_a4_fingerprint,
            "linked_thesis_refs": list(result.assessment.linked_thesis_refs),
            "invalidation_condition_refs": list(
                result.assessment.invalidation_condition_refs
            ),
        }
    return {"admitted_artifact_refs": list(result.metadata.admitted_artifact_refs)}


def _last_view(result: ShellFacadeResult, view: LastView) -> dict[str, Any]:
    if view is LastView.REASONS:
        return _reasons(result)
    if view is LastView.GAPS:
        return _gaps(result)
    if view is LastView.CONTRADICTIONS:
        return _contradictions(result)
    if view is LastView.EVIDENCE:
        return _evidence(result)
    return _summary(result)


def _explain(result: ShellFacadeResult) -> dict[str, Any]:
    if isinstance(result, BaselineAssessResult):
        return {
            "schema_id": "tiaf.shell.explanation",
            "schema_version": "1.0",
            "capability_id": result.metadata.capability_id,
            "summary": _summary(result),
            "reasons": _reasons(result),
            "evidence": _evidence(result),
        }
    if isinstance(result, OpportunityAssembleResult):
        return {
            "schema_id": "tiaf.shell.explanation",
            "schema_version": "1.0",
            "capability_id": result.metadata.capability_id,
            "summary": _summary(result),
            "reasons": _reasons(result),
            "gaps": _gaps(result),
            "contradictions": _contradictions(result),
            "evidence": _evidence(result),
        }
    if isinstance(result, A4InputProjectResult):
        return {
            "schema_id": "tiaf.shell.explanation",
            "schema_version": "1.0",
            "capability_id": result.metadata.capability_id,
            "summary": _summary(result),
            "gaps": _gaps(result),
            "contradictions": _contradictions(result),
            "evidence": _evidence(result),
        }
    if isinstance(result, A4EvaluateResult):
        evaluation = result.evaluation
        return {
            "schema_id": "tiaf.shell.explanation",
            "schema_version": "1.0",
            "capability_id": result.metadata.capability_id,
            "summary": _summary(result),
            "primary_thesis": evaluation.primary_thesis.model_dump(mode="json"),
            "counter_thesis": (
                evaluation.counter_thesis.model_dump(mode="json")
                if evaluation.counter_thesis
                else None
            ),
            "challenge_findings": [
                item.model_dump(mode="json") for item in evaluation.challenge_findings
            ],
            "arbitration_findings": [
                item.model_dump(mode="json") for item in evaluation.arbitration_findings
            ],
            "residual_uncertainties": [
                item.model_dump(mode="json") for item in evaluation.residual_uncertainties
            ],
            "evidence_needs": [item.model_dump(mode="json") for item in evaluation.evidence_needs],
            "invalidation_conditions": [
                item.model_dump(mode="json") for item in evaluation.invalidation_conditions
            ],
            "evidence": _evidence(result),
        }
    if isinstance(result, PositionAssessResult):
        assessment = result.assessment
        return {
            "schema_id": "tiaf.shell.explanation",
            "schema_version": "1.0",
            "capability_id": result.metadata.capability_id,
            "summary": _summary(result),
            "reasons": _reasons(result),
            "gaps": _gaps(result),
            "contradictions": _contradictions(result),
            "evidence": _evidence(result),
            "protection_intent": assessment.protection_intent.model_dump(mode="json"),
            "monitoring_needs": [
                item.model_dump(mode="json") for item in assessment.monitoring_needs
            ],
            "monitoring_statement": result.monitoring_statement,
            "invalidation_condition_refs": list(
                assessment.invalidation_condition_refs
            ),
            "authority_statement": assessment.authority_statement,
        }
    raise shell_error(
        ShellErrorCode.EXPLANATION_UNAVAILABLE,
        "structured explanation is unavailable for this result type",
        command_name="explain last",
    )


def _trace(invocation: SuccessfulInvocation, view: TraceView) -> dict[str, Any]:
    metadata = invocation.result.metadata
    common: dict[str, Any] = {
        "schema_id": "tiaf.shell.trace",
        "schema_version": "1.0",
        "shell_invocation_id": invocation.record.shell_invocation_id,
        "parent_shell_invocation_id": invocation.record.parent_shell_invocation_id,
        "capability_id": metadata.capability_id,
        "capability_version": metadata.capability_version,
        "request_id": metadata.request_id,
        "run_id": metadata.run_id,
        "correlation_id": metadata.correlation_id,
        "status": metadata.status.value,
        "effect": metadata.effect.value,
    }
    if view in {TraceView.ALL, TraceView.COST}:
        common["usage"] = metadata.usage.model_dump(mode="json")
        common["budget_ref"] = metadata.budget_ref
        common["model_policy_ref"] = metadata.model_policy_ref
    if view in {TraceView.ALL, TraceView.EVIDENCE}:
        common["admitted_artifact_refs"] = list(metadata.admitted_artifact_refs)
        common["policy_refs"] = [list(item) for item in metadata.policy_refs]
        common["warnings"] = list(metadata.warnings)
        common["gaps"] = list(metadata.gaps)
        if isinstance(invocation.result, PositionAssessResult):
            assessment = invocation.result.assessment
            common.update(
                position_request_ref=metadata.position_context_ref,
                snapshot_id=assessment.snapshot_id,
                linked_a4_result_id=assessment.linked_a4_result_id,
                linked_a4_fingerprint=assessment.linked_a4_fingerprint,
                a5_run_fingerprint=invocation.result.run_fingerprint,
                semantic_fingerprint=assessment.semantic_fingerprint,
                replay_identity=assessment.replay_identity,
            )
    if view in {TraceView.ALL, TraceView.TIMING}:
        common["created_at"] = metadata.created_at.isoformat()
        common["started_at"] = metadata.started_at.isoformat()
        common["completed_at"] = metadata.completed_at.isoformat()
        common["elapsed_seconds"] = metadata.usage.elapsed_seconds
    return common


def _descriptor(descriptor: CapabilityDescriptor) -> dict[str, Any]:
    return {
        "capability_id": descriptor.capability_id,
        "capability_version": descriptor.capability_version,
        "interface_level": descriptor.interface_level.value,
        "request_schema_id": descriptor.request_schema_id,
        "request_schema_version": descriptor.request_schema_version,
        "result_schema_id": descriptor.result_schema_id,
        "result_schema_version": descriptor.result_schema_version,
        "effect": descriptor.effect.value,
        "deterministic": descriptor.deterministic,
        "model_supported": descriptor.model_supported,
        "replay_support": descriptor.replay_support.value,
        "required_authority_scope": descriptor.required_authority_scope.value,
        "cost_knowledge": descriptor.cost_knowledge.value,
        "availability": descriptor.availability.value,
        "deprecated": descriptor.deprecated,
        "replacement_capability_id": descriptor.replacement_capability_id,
    }


def render_json(outcome: DispatchOutcome) -> str:
    if isinstance(outcome.command, ExplainLastCommand):
        assert isinstance(outcome.value, SuccessfulInvocation)
        return _json(_explain(outcome.value.result))
    if isinstance(outcome.command, TraceLastCommand):
        assert isinstance(outcome.value, SuccessfulInvocation)
        return _json(_trace(outcome.value, outcome.command.view))
    if isinstance(outcome.command, ShowLastCommand):
        assert isinstance(outcome.value, SuccessfulInvocation)
        if outcome.command.view is LastView.SUMMARY:
            return _json(_facade_envelope(outcome.value))
        return _json(
            {
                "schema_id": "tiaf.shell.result-view",
                "schema_version": "1.0",
                "capability_id": outcome.value.result.metadata.capability_id,
                "view": outcome.command.view.value,
                "projection": _last_view(outcome.value.result, outcome.command.view),
            }
        )
    if outcome.invocation is not None:
        payload = _facade_envelope(outcome.invocation)
        if isinstance(outcome.value, CapabilityDescriptor):
            payload["selected_descriptor"] = _descriptor(outcome.value)
        return _json(payload)
    if isinstance(outcome.value, SessionDefaults):
        return _json(_context_payload(outcome.value))
    return _json(
        {
            "schema_id": "tiaf.shell.local-result",
            "schema_version": "1.0",
            "command": outcome.command_name,
            "message": str(outcome.value),
        }
    )


def _human_mapping(payload: Mapping[str, Any]) -> str:
    lines = []
    for key, value in payload.items():
        if value is None or value == [] or value == {}:
            continue
        rendered = value if isinstance(value, str | int | float | bool) else _json(value)
        lines.append(f"{key.replace('_', ' ').title()}: {rendered}")
    return "\n".join(lines) or "No applicable data."


def render_human(outcome: DispatchOutcome) -> str:
    if isinstance(outcome.command, ExplainLastCommand):
        assert isinstance(outcome.value, SuccessfulInvocation)
        return _human_mapping(_explain(outcome.value.result))
    if isinstance(outcome.command, TraceLastCommand):
        assert isinstance(outcome.value, SuccessfulInvocation)
        return _human_mapping(_trace(outcome.value, outcome.command.view))
    if isinstance(outcome.command, ShowLastCommand):
        assert isinstance(outcome.value, SuccessfulInvocation)
        return _human_mapping(_last_view(outcome.value.result, outcome.command.view))
    if isinstance(outcome.value, CapabilityDescriptor):
        return _human_mapping(_descriptor(outcome.value))
    if isinstance(outcome.value, SessionDefaults):
        return _human_mapping(outcome.value.model_dump(mode="json"))
    if outcome.facade_result is not None:
        return _human_mapping(_summary(outcome.facade_result))
    return str(outcome.value).rstrip()


def render(outcome: DispatchOutcome) -> str:
    return render_json(outcome) if outcome.output_mode.value == "json" else render_human(outcome)


def render_error(error: ShellError, *, json_mode: bool) -> str:
    if json_mode:
        return _json(error.record.model_dump(mode="json"))
    return f"{error.record.code.value}: {error.record.message}"
