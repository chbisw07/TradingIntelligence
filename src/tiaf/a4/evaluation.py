"""Deterministic A4 evaluation pipeline over one validated semantic projection."""

from datetime import datetime

from pydantic import ValidationError

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.planner.digests import digest
from tiaf.source_semantics import A4SemanticInputProjection, ProjectionIntegrityError
from tiaf.source_semantics import validate_projection as validate_input_projection

from .arbitration import ArbitrationError, arbitrate
from .challenges import ChallengerError, generate_challenges
from .contracts import (
    A4DeterministicPolicy,
    A4EvidenceNeed,
    A4Failure,
    A4Result,
    A4RunRecord,
    A4Usage,
    ArbitrationFinding,
    ArgumentPremise,
    ChallengeFinding,
    InvestmentThesis,
    ResidualUncertainty,
)
from .enums import (
    A4Disposition,
    A4ExecutionStatus,
    A4FailureCode,
    ArbitrationDisposition,
    ChallengeStatus,
    FailureStage,
    Materiality,
    UncertaintyKind,
)
from .policy import deterministic_policy, require_supported_policy
from .thesis import ThesisConstructionError, build_theses, validate_premises


class A4EvaluationError(ValueError):
    """Base error for deterministic A4 evaluation and output integrity."""


class A4InputIntegrityError(A4EvaluationError):
    """Input projection failed closed before reasoning."""


class A4OutputIntegrityError(A4EvaluationError):
    """Generated A4 graph or semantic fingerprint is inconsistent."""


def _admitted_basis_refs(projection: A4SemanticInputProjection) -> set[str]:
    """Return only identities/reasons explicitly present in the input projection."""
    return {
        projection.projection_id,
        projection.parents.a2_assessment_id,
        projection.parents.a3_package_id,
        f"a39-state:{projection.opportunity.a39_state}",
        *(
            (f"a2-class:{projection.opportunity.original_a2_candidate_class}",)
            if projection.opportunity.original_a2_candidate_class
            else ()
        ),
        *(
            (f"a2-direction:{projection.opportunity.original_a2_direction}",)
            if projection.opportunity.original_a2_direction
            else ()
        ),
        *projection.opportunity.a39_reason_ids,
        *projection.opportunity.a39_gap_ids,
        *projection.opportunity.active_opinion_ids,
        *projection.opportunity.superseded_opinion_ids,
        *(item.source_id for item in projection.sources),
        *(item.provider_id for item in projection.providers),
        *(item.origin_id for item in projection.origins),
        *(item.family_id for item in projection.document_families),
        *(item.document_version_id for item in projection.document_versions),
        *(item.occurrence_id for item in projection.occurrences),
        *(item.evidence_id for item in projection.occurrences),
        *(item.assertion_id for item in projection.assertions),
        *(item.proposition.proposition_id for item in projection.assertions),
        *(ref for item in projection.assertions for ref in item.original_claim_ids),
        *(item.admission_id for item in projection.admissions),
        *(item.assessment_id for item in projection.authority_assessments),
        *(value for item in projection.authority_assessments for value in item.limitations),
        *(item.comparison_id for item in projection.comparisons),
        *(value for item in projection.comparisons for value in item.reasons),
        *(item.dispute_id for item in projection.disputes),
        *(event.event_id for item in projection.disputes for event in item.events),
        *(
            evidence_id
            for item in projection.disputes
            for event in item.events
            for evidence_id in event.evidence_ids
        ),
        *(item.assessment_id for item in projection.independence),
        *(item.left_occurrence_id for item in projection.independence),
        *(item.right_occurrence_id for item in projection.independence),
        *(value for item in projection.independence for value in item.basis),
        *(item.evidence_id for item in projection.evidence_qualifications),
        *(item.gap_id for item in projection.gaps),
        *(item.code for item in projection.gaps),
        *(item.affected_reference for item in projection.gaps),
        *(item.evidence_id for item in projection.excluded_evidence),
        *(item.reason for item in projection.excluded_evidence),
    }


def result_semantic_payload(result: A4Result) -> dict[str, object]:
    return result.model_dump(
        mode="json",
        exclude={"result_id": True, "semantic_fingerprint": True},
    )


def _result(
    *,
    projection: A4SemanticInputProjection,
    policy: A4DeterministicPolicy,
    primary: InvestmentThesis,
    counter: InvestmentThesis | None,
    premises: tuple[ArgumentPremise, ...],
    challenge_findings: tuple[ChallengeFinding, ...],
    arbitration_findings: tuple[ArbitrationFinding, ...],
    uncertainties: tuple[ResidualUncertainty, ...],
    evidence_needs: tuple[A4EvidenceNeed, ...],
    disposition: A4Disposition,
    execution_status: A4ExecutionStatus,
    failures: tuple[A4Failure, ...] = (),
    surviving: tuple[str, ...] = (),
) -> A4Result:
    primary_thesis = InvestmentThesis.model_validate(primary)
    counter_thesis = (
        InvestmentThesis.model_validate(counter) if counter is not None else None
    )
    premise_items = tuple(ArgumentPremise.model_validate(item) for item in premises)
    challenge_items = tuple(
        ChallengeFinding.model_validate(item) for item in challenge_findings
    )
    arbitration_items = tuple(
        ArbitrationFinding.model_validate(item) for item in arbitration_findings
    )
    uncertainty_items = tuple(
        ResidualUncertainty.model_validate(item) for item in uncertainties
    )
    provisional = A4Result(
        result_id="a4-result:pending",
        input_projection_id=projection.projection_id,
        input_projection_fingerprint=projection.semantic_fingerprint,
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
        challenge_policy_id=policy.challenge_policy_id,
        challenge_policy_version=policy.challenge_policy_version,
        arbitration_policy_id=policy.arbitration_policy_id,
        arbitration_policy_version=policy.arbitration_policy_version,
        primary_thesis=primary_thesis,
        counter_thesis=counter_thesis,
        surviving_thesis_refs=surviving,
        premises=premise_items,
        challenge_findings=challenge_items,
        arbitration_findings=arbitration_items,
        residual_uncertainties=uncertainty_items,
        evidence_needs=evidence_needs,
        disposition=disposition,
        execution_status=execution_status,
        original_a2_assessment_ref=projection.parents.a2_assessment_id,
        original_a2_evidence_fingerprint=projection.parents.a2_evidence_fingerprint,
        original_a3_package_ref=projection.parents.a3_package_id,
        original_a3_semantic_fingerprint=projection.parents.a3_package_semantic_fingerprint,
        invalidation_conditions=tuple(
            condition
            for thesis in (primary_thesis, counter_thesis)
            if thesis is not None
            for condition in thesis.invalidation_conditions
        ),
        usage=A4Usage(
            parent_usage_refs=(projection.parents.a3_package_id,),
            parent_cost_knowledge=projection.usage_cost_knowledge,
        ),
        failures=failures,
        semantic_fingerprint="0" * 64,
    )
    fingerprint = digest(result_semantic_payload(provisional))
    return provisional.model_copy(
        update={
            "result_id": f"a4-result:{fingerprint[:24]}",
            "semantic_fingerprint": fingerprint,
        }
    )


def validate_result(
    result: A4Result,
    projection: A4SemanticInputProjection,
    policy: A4DeterministicPolicy,
) -> A4Result:
    try:
        result = A4Result.model_validate_json(result.model_dump_json())
        validate_input_projection(projection)
        require_supported_policy(policy)
        if (
            result.input_projection_id != projection.projection_id
            or result.input_projection_fingerprint != projection.semantic_fingerprint
            or (result.policy_id, result.policy_version)
            != (policy.policy_id, policy.policy_version)
            or result.challenge_policy_id != policy.challenge_policy_id
            or result.challenge_policy_version != policy.challenge_policy_version
            or result.arbitration_policy_id != policy.arbitration_policy_id
            or result.arbitration_policy_version != policy.arbitration_policy_version
        ):
            raise ValueError("A4 result input or policy identity mismatch")
        validate_premises(result.premises, projection)
        basis_refs = _admitted_basis_refs(projection)
        thesis_ids = {result.primary_thesis.thesis_id}
        if result.counter_thesis is not None:
            thesis_ids.add(result.counter_thesis.thesis_id)
        premise_ids = {item.premise_id for item in result.premises}
        if result.primary_thesis.role.value != "PRIMARY" or (
            result.counter_thesis is not None
            and result.counter_thesis.role.value != "COUNTER"
        ):
            raise ValueError("A4 result thesis role mismatch")
        for thesis in (result.primary_thesis, result.counter_thesis):
            if thesis is None:
                continue
            if (
                thesis.parent_a2_assessment_ref != projection.parents.a2_assessment_id
                or thesis.parent_a3_package_ref != projection.parents.a3_package_id
                or thesis.parent_a39_fingerprint_ref
                != projection.parents.a39_semantic_fingerprint
                or thesis.subject != projection.header.subject
                or thesis.objective != projection.header.objective
                or thesis.horizon != projection.header.horizon
                or thesis.conclusion_policy_id != policy.policy_id
            ):
                raise ValueError("A4 thesis input or policy identity mismatch")
            if not (
                set(thesis.support_refs)
                | set(thesis.opposition_refs)
                | set(thesis.gaps)
                | set(thesis.risks)
            ) <= basis_refs:
                raise ValueError("A4 thesis contains an unadmitted basis reference")
            for condition in thesis.invalidation_conditions:
                if (
                    condition.premise_ref not in thesis.premise_refs
                    or not set(condition.cited_refs) <= basis_refs
                ):
                    raise ValueError("A4 invalidation condition is unresolved")
        expected_conditions = tuple(
            condition
            for thesis in (result.primary_thesis, result.counter_thesis)
            if thesis is not None
            for condition in thesis.invalidation_conditions
        )
        if result.invalidation_conditions != expected_conditions:
            raise ValueError("A4 result invalidation conditions do not match theses")
        if (
            result.original_a2_assessment_ref != projection.parents.a2_assessment_id
            or result.original_a2_evidence_fingerprint
            != projection.parents.a2_evidence_fingerprint
            or result.original_a3_package_ref != projection.parents.a3_package_id
            or result.original_a3_semantic_fingerprint
            != projection.parents.a3_package_semantic_fingerprint
            or result.usage.parent_usage_refs != (projection.parents.a3_package_id,)
            or result.usage.parent_cost_knowledge != projection.usage_cost_knowledge
        ):
            raise ValueError("A4 result parent identity or usage mismatch")
        challenge_ids = {item.finding_id for item in result.challenge_findings}
        dispute_ids = {item.dispute_id for item in projection.disputes}
        need_ids = {item.need_id for item in result.evidence_needs}
        if any(
            item.challenged_thesis_ref not in thesis_ids
            or (
                item.challenged_premise_ref is not None
                and item.challenged_premise_ref not in premise_ids
            )
            or not set(item.dispute_refs) <= dispute_ids
            or (
                item.evidence_need_ref is not None
                and item.evidence_need_ref not in need_ids
            )
            or not (
                set(item.cited_support_refs) | set(item.cited_opposition_refs)
            )
            <= basis_refs
            for item in result.challenge_findings
        ):
            raise ValueError("A4 challenge reference is unresolved")
        if any(
            not set(item.finding_refs) <= challenge_ids
            or not set(item.dispute_refs) <= dispute_ids
            or item.subject != projection.header.subject
            or item.horizon != projection.header.horizon
            or item.evidence_cutoff != projection.header.evidence_as_of
            or item.permitted_scope_ref != projection.header.authority_ref
            or item.remaining_budget_ref != projection.header.budget_ref
            for item in result.evidence_needs
        ):
            raise ValueError("A4 evidence need finding is unresolved")
        failure_ids = {item.failure_id for item in result.failures}
        valid_issue_refs = challenge_ids | failure_ids | {
            item.issue_ref
            for item in result.arbitration_findings
            if item.issue_ref.startswith("a4-issue:")
        }
        if any(
            item.issue_ref not in valid_issue_refs
            or not set(item.thesis_refs) <= thesis_ids
            or not set(item.argument_refs) <= premise_ids
            or not set(item.decisive_evidence_refs) <= basis_refs
            or not set(item.dissent_refs) <= basis_refs
            or not set(item.decisive_condition_refs)
            <= {condition.condition_id for condition in expected_conditions}
            for item in result.arbitration_findings
        ):
            raise ValueError("A4 arbitration reference is unresolved")
        if any(
            item.affected_thesis_ref not in thesis_ids
            or (
                item.affected_premise_ref is not None
                and item.affected_premise_ref not in premise_ids
            )
            or not set(item.evidence_need_refs) <= need_ids
            for item in result.residual_uncertainties
        ):
            raise ValueError("A4 uncertainty reference is unresolved")
        expected = digest(result_semantic_payload(result))
        if result.semantic_fingerprint != expected:
            raise ValueError("A4 result semantic fingerprint mismatch")
        if result.result_id != f"a4-result:{expected[:24]}":
            raise ValueError("A4 result ID does not match fingerprint")
        return result
    except (TypeError, ValueError, ValidationError) as exc:
        if isinstance(exc, A4OutputIntegrityError):
            raise
        raise A4OutputIntegrityError(str(exc)) from exc


def record_fingerprint(record: A4RunRecord) -> str:
    return digest(
        {
            "input_projection_fingerprint": record.input_projection.semantic_fingerprint,
            "policy": record.policy.model_dump(mode="json"),
            "result_fingerprint": record.result.semantic_fingerprint,
        }
    )


def validate_run(record: A4RunRecord) -> A4RunRecord:
    try:
        record = A4RunRecord.model_validate_json(record.model_dump_json())
        projection = validate_input_projection(record.input_projection)
        policy = require_supported_policy(record.policy)
        validate_result(record.result, projection, policy)
        if record.fingerprint != record_fingerprint(record):
            raise ValueError("A4 run fingerprint mismatch")
        return record
    except (TypeError, ValueError, ValidationError) as exc:
        if isinstance(exc, A4EvaluationError):
            raise
        raise A4OutputIntegrityError(str(exc)) from exc


def _challenger_failure_result(
    projection: A4SemanticInputProjection,
    policy: A4DeterministicPolicy,
    premises: tuple[ArgumentPremise, ...],
    primary: InvestmentThesis,
    counter: InvestmentThesis | None,
    exc: ChallengerError,
) -> A4Result:
    failure = A4Failure(
        failure_id=f"a4-failure:{digest(('challenger', type(exc).__name__))[:24]}",
        stage=FailureStage.CHALLENGER,
        code=A4FailureCode.CHALLENGER_FAILED,
        reason_code="REQUIRED_DETERMINISTIC_CHALLENGE_INCOMPLETE",
        child_codes=(type(exc).__name__,),
    )
    uncertainty = ResidualUncertainty(
        uncertainty_id=f"a4-uncertainty:{digest(failure.failure_id)[:24]}",
        affected_thesis_ref=primary.thesis_id,
        kind=UncertaintyKind.UNKNOWN,
        materiality=Materiality.MATERIAL,
        consequence_code="CHALLENGE_COVERAGE_INCOMPLETE",
        resolution_requirement="RERUN_DETERMINISTIC_CHALLENGER",
    )
    arbitration_finding = ArbitrationFinding(
        finding_id=f"a4-arbitration-finding:{digest(failure.failure_id)[:24]}",
        issue_ref=failure.failure_id,
        thesis_refs=(primary.thesis_id,),
        disposition=ArbitrationDisposition.UNRESOLVED,
        rule_id="a4-rule:incomplete-review",
        policy_id=policy.arbitration_policy_id,
        reason_code="CHALLENGER_FAILURE_PREVENTS_SUPPORT",
    )
    return _result(
        projection=projection,
        policy=policy,
        primary=primary,
        counter=counter,
        premises=premises,
        challenge_findings=(),
        arbitration_findings=(arbitration_finding,),
        uncertainties=(uncertainty,),
        evidence_needs=(),
        disposition=A4Disposition.ABSTAIN,
        execution_status=A4ExecutionStatus.PARTIAL,
        failures=(failure,),
    )


def evaluate_projection(
    projection: A4SemanticInputProjection,
    *,
    policy: A4DeterministicPolicy | None = None,
    evaluated_at: datetime | None = None,
) -> A4RunRecord:
    """Run the no-LLM A4 benchmark; no acquisition or fallback path exists."""
    selected = policy or deterministic_policy()
    try:
        projection = validate_input_projection(projection)
    except (ProjectionIntegrityError, ValueError, ValidationError) as exc:
        raise A4InputIntegrityError(str(exc)) from exc
    selected = require_supported_policy(selected)
    try:
        premises, primary, counter = build_theses(projection, selected)
    except (ThesisConstructionError, TypeError, ValueError, ValidationError) as exc:
        raise A4EvaluationError("deterministic thesis construction failed") from exc
    try:
        challenges, needs, uncertainties = generate_challenges(
            projection, selected, premises, primary, counter
        )
    except ChallengerError as exc:
        result = _challenger_failure_result(
            projection, selected, premises, primary, counter, exc
        )
    else:
        try:
            disposition, arbitration_findings, surviving = arbitrate(
                projection, selected, primary, counter, challenges
            )
        except (ArbitrationError, TypeError, ValueError, ValidationError) as exc:
            raise A4EvaluationError("deterministic arbitration failed") from exc
        unresolved_required_rule = any(
            item.status is ChallengeStatus.UNEVALUATED
            and item.materiality in {Materiality.MATERIAL, Materiality.HARD_CONSTRAINT}
            for item in challenges
        )
        failures = (
            (
                A4Failure(
                    failure_id=f"a4-failure:{digest(('arbitration', 'unresolved-rule'))[:24]}",
                    stage=FailureStage.ARBITRATION,
                    code=A4FailureCode.UNRESOLVED_REQUIRED_RULE,
                    reason_code="MATERIAL_ISSUE_OUTSIDE_DECLARED_POLICY",
                ),
            )
            if unresolved_required_rule
            else ()
        )
        result = _result(
            projection=projection,
            policy=selected,
            primary=primary,
            counter=counter,
            premises=premises,
            challenge_findings=challenges,
            arbitration_findings=arbitration_findings,
            uncertainties=uncertainties,
            evidence_needs=needs,
            disposition=disposition,
            execution_status=(
                A4ExecutionStatus.PARTIAL
                if unresolved_required_rule
                else A4ExecutionStatus.COMPLETE
            ),
            failures=failures,
            surviving=surviving,
        )
    result = validate_result(result, projection, selected)
    provisional = A4RunRecord(
        input_projection=projection,
        policy=selected,
        result=result,
        evaluated_at=evaluated_at or datetime.now(TIAF_TIMEZONE),
        fingerprint="0" * 64,
    )
    return validate_run(
        provisional.model_copy(update={"fingerprint": record_fingerprint(provisional)})
    )
