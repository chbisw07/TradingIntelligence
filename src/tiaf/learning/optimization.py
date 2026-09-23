"""Bounded orchestration over FLC-2 training, independent Evaluation and custody.

Recorded replay consumes persisted objectives, never fitting or scoring. Hashes
provide integrity against a caller-pinned root, not reviewer authentication.
"""

import math
import os
import time
from datetime import datetime
from types import MappingProxyType
from typing import Literal, TypedDict, cast

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.evaluation import optimization_evaluation as evaluation
from tiaf.forecasting.identity import ArtifactReference, canonical_json, semantic_fingerprint

from . import forecaster_reference as training
from .forecaster_authority import TrainingAttempt, admit_training
from .forecaster_custody import ForecasterStore, restore_training
from .forecaster_training import ModelArtifactIdentity, reference
from .optimization_contracts import (
    CandidateScore,
    OptimizationClaim,
    OptimizationGrant,
    OptimizationRequest,
    OptimizationResult,
    TrialDefinition,
    TrialPlan,
    TrialRecord,
    plan_trials,
)
from .synthetic_trials import SyntheticModel, code_pin, dependency_pin, development_rows


class OptimizationStore(ForecasterStore):
    """Codecs only; FLC-2's existing store remains the sole I/O owner."""

    record_types = MappingProxyType(
        {
            **ForecasterStore.record_types,
            "optrequest": OptimizationRequest,
            "optplan": TrialPlan,
            "optgrant": OptimizationGrant,
            "optclaim": OptimizationClaim,
            "trialdef": TrialDefinition,
            "trialrecord": TrialRecord,
            "devevaluation": evaluation.DevelopmentTrialEvaluation,
            "optresult": OptimizationResult,
        }
    )


class _TrialCommon(TypedDict):
    definition_reference: ArtifactReference
    trial_id: str


class _TrialLineage(TypedDict):
    bundle_reference: ArtifactReference
    model_identity: ModelArtifactIdentity | None


def _grant_links(request: OptimizationRequest, plan: TrialPlan, grant: OptimizationGrant) -> None:
    if (
        grant.request_reference != reference("optrequest", request)
        or grant.plan_reference != reference("optplan", plan)
        or len(grant.training_grants) != len(plan.trials)
    ):
        raise ValueError("EXACT_OPTIMIZATION_GRANT_REQUIRED")
    for trial, permission in zip(plan.trials, grant.training_grants, strict=True):
        if (
            permission.request_reference != reference("request", trial.training)
            or permission.experiment != trial.training.experiment
            or permission.input_fingerprint != semantic_fingerprint(trial.spec)
            or permission.authority_reference != request.training_authority_reference
            or permission.qualification_reference.fingerprint != request.qualification_fingerprint
            or permission.experiment_status != "OPEN"
            or permission.holdout_status != "NONE"
        ):
            raise ValueError("EXACT_DEVELOPMENT_TRAINING_GRANT_REQUIRED")


def select_candidate(
    request: OptimizationRequest, plan: TrialPlan, records: tuple[TrialRecord, ...]
) -> tuple[tuple[CandidateScore, ...], TrialRecord | None]:
    """Aggregate recorded objectives only; two complete folds, stable identity tie."""
    if len(records) != len(plan.trials):
        raise ValueError("INCOMPLETE_TRIAL_ACCOUNTING")
    groups: dict[str, list[TrialRecord]] = {}
    for definition, record in zip(plan.trials, records, strict=True):
        if (
            record.definition_reference != reference("trialdef", definition)
            or record.trial_id != definition.trial_id
        ):
            raise ValueError("TRIAL_ORDER_MISMATCH")
        groups.setdefault(definition.candidate_id, []).append(record)
    scores = []
    for candidate, folds in groups.items():
        if len(folds) == 2 and all(r.status == "EVALUATED" for r in folds):
            score = math.fsum(cast(float, r.objective_value) for r in folds) / 2
            scores.append(
                CandidateScore(
                    candidate_id=candidate,
                    trial_ids=(folds[0].trial_id, folds[1].trial_id),
                    value=score,
                )
            )
    sign = 1 if request.objective.direction == "MINIMIZE" else -1
    ordered = tuple(sorted(scores, key=lambda s: (sign * s.value, s.candidate_id)))
    return ordered, groups[ordered[0].candidate_id][-1] if ordered else None


def execute_optimization(
    store: OptimizationStore, request: OptimizationRequest, grant: OptimizationGrant
) -> OptimizationResult:
    tick = time.monotonic()
    request = OptimizationRequest.model_validate(request.model_dump())
    grant = OptimizationGrant.model_validate(grant.model_dump())
    plan = plan_trials(request)
    _grant_links(request, plan, grant)
    if (
        not store.writable
        or request.implementation_fingerprint != code_pin()
        or request.dependency_lock_fingerprint != dependency_pin()
    ):
        raise ValueError("OPTIMIZATION_CUSTODY_OR_IMPLEMENTATION_MISMATCH")
    now = datetime.now(TIAF_TIMEZONE)
    for definition, permission in zip(plan.trials, grant.training_grants, strict=True):
        admit_training(
            definition.training,
            permission,
            input_fingerprint=semantic_fingerprint(definition.spec),
            root=store.root,
            at=now,
        )
    # Existing custody is single-writer. One campaign per dedicated root; a crash
    # cannot silently resume/refit, even with a differently named grant.
    if any(store.root.glob("optclaim-*.json")):
        raise ValueError("OPTIMIZATION_ALREADY_CONSUMED")
    for kind, value in (("optrequest", request), ("optplan", plan), ("optgrant", grant)):
        store.put(kind, value)
    for definition in plan.trials:
        store.put("trialdef", definition)
    claim = OptimizationClaim(
        request_reference=reference("optrequest", request),
        grant_reference=reference("optgrant", grant),
    )
    raw = (canonical_json(claim) + "\n").encode()
    if store.bytes + len(raw) > 2 * 1024**3 or store.count + 1 > 65536:
        raise ValueError("RESEARCH_CORPUS_LIMIT")
    with store._path("optclaim", cast(str, claim.fingerprint)).open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    store.bytes += len(raw)
    store.count += 1
    if store.resolve(reference("optclaim", claim)) != claim:
        raise ValueError("OPTIMIZATION_CLAIM_NOT_PERSISTED")
    deadline = tick + request.budget.max_wall_seconds
    records = []
    for definition, permission in zip(plan.trials, grant.training_grants, strict=True):
        started = time.monotonic()
        remaining = deadline - started
        common = _TrialCommon(
            definition_reference=reference("trialdef", definition), trial_id=definition.trial_id
        )
        if remaining <= 0:
            record = TrialRecord(
                **common,
                status="BUDGET_EXCEEDED",
                reason="WALL_BUDGET_EXHAUSTED",
                elapsed_seconds=0.0,
            )
        else:
            bundle = training.execute_synthetic_once(
                store,
                definition.training,
                permission,
                trial=definition.spec,
                timeout_seconds=min(remaining, request.budget.per_trial_seconds),
            )
            lineage = _TrialLineage(
                bundle_reference=reference("bundle", bundle),
                model_identity=bundle.result.model_identity,
            )
            if bundle.result.status != "TRAINED":
                record = TrialRecord(
                    **common,
                    **lineage,
                    status="TRAINING_FAILED",
                    reason=bundle.result.failure_reason,
                    elapsed_seconds=time.monotonic() - started,
                )
            elif time.monotonic() >= deadline:
                record = TrialRecord(
                    **common,
                    **lineage,
                    status="BUDGET_EXCEEDED",
                    reason="WALL_BUDGET_EXHAUSTED",
                    elapsed_seconds=time.monotonic() - started,
                )
            else:
                assert bundle.result.model_identity is not None
                model = store.resolve(bundle.result.model_identity.artifact)
                if not isinstance(model, SyntheticModel):
                    raise ValueError("SYNTHETIC_ARTIFACT_REQUIRED")
                try:
                    report = evaluation.evaluate_trial(
                        model,
                        bundle.result.model_identity,
                        request.objective.metric_id,
                        datetime.now(TIAF_TIMEZONE),
                    )
                except ValueError:
                    record = TrialRecord(
                        **common,
                        **lineage,
                        status="EVALUATION_FAILED",
                        reason="DEVELOPMENT_EVALUATION_FAILURE",
                        elapsed_seconds=time.monotonic() - started,
                    )
                else:
                    if time.monotonic() >= deadline:
                        record = TrialRecord(
                            **common,
                            **lineage,
                            status="BUDGET_EXCEEDED",
                            reason="WALL_BUDGET_EXHAUSTED",
                            elapsed_seconds=time.monotonic() - started,
                        )
                    else:
                        store.put("devevaluation", report)
                        record = TrialRecord(
                            **common,
                            **lineage,
                            status="EVALUATED",
                            evaluation_reference=reference("devevaluation", report),
                            objective_value=report.objective_value,
                            elapsed_seconds=time.monotonic() - started,
                        )
        store.put("trialrecord", record)
        records.append(record)
    scores, selected = select_candidate(request, plan, tuple(records))
    result = OptimizationResult(
        request_reference=reference("optrequest", request),
        plan_reference=reference("optplan", plan),
        grant_reference=reference("optgrant", grant),
        trial_references=tuple(reference("trialrecord", r) for r in records),
        scores=scores,
        selected_trial_id=selected.trial_id if selected else None,
        selected_model_identity=selected.model_identity if selected else None,
        status="SELECTED" if selected else "NO_VALID_TRIAL",
        selection_rule=request.selection_rule,
        elapsed_seconds=time.monotonic() - tick,
        failed_trial_count=sum(r.status != "EVALUATED" for r in records),
        budget_exceeded=any(r.status == "BUDGET_EXCEEDED" for r in records),
    )
    store.put("optresult", result)
    return result


def replay_optimization(
    store: OptimizationStore, result_reference: ArtifactReference
) -> Literal["MATCH", "MISMATCH"]:
    """Read-only closure/selection verification. Never reevaluate or refit."""
    try:
        result = store.resolve(result_reference)
        if not isinstance(result, OptimizationResult):
            raise ValueError("OPTIMIZATION_RESULT_REQUIRED")
        request, plan, grant = (
            store.resolve(r)
            for r in (result.request_reference, result.plan_reference, result.grant_reference)
        )
        if (
            not isinstance(request, OptimizationRequest)
            or not isinstance(plan, TrialPlan)
            or not isinstance(grant, OptimizationGrant)
        ):
            raise ValueError("OPTIMIZATION_LINEAGE_REQUIRED")
        if plan != plan_trials(request):
            raise ValueError("PLAN_MISMATCH")
        _grant_links(request, plan, grant)
        claim = OptimizationClaim(
            request_reference=result.request_reference, grant_reference=result.grant_reference
        )
        if store.resolve(reference("optclaim", claim)) != claim:
            raise ValueError("CLAIM_MISMATCH")
        records = []
        for ref, definition, permission in zip(
            result.trial_references, plan.trials, grant.training_grants, strict=True
        ):
            if store.resolve(reference("trialdef", definition)) != definition:
                raise ValueError("DEFINITION_MISMATCH")
            record = store.resolve(ref)
            if not isinstance(record, TrialRecord):
                raise ValueError("TRIAL_REQUIRED")
            if record.bundle_reference is not None:
                bundle = restore_training(store, record.bundle_reference)
                attempt = TrainingAttempt(
                    grant_reference=reference("authorization", permission),
                    request_reference=reference("request", definition.training),
                )
                if (
                    store.resolve(reference("attempt", attempt)) != attempt
                    or store.resolve(reference("authorization", permission)) != permission
                ):
                    raise ValueError("TRAINING_AUTHORITY_LINEAGE_MISMATCH")
                if (
                    bundle.request != definition.training
                    or record.model_identity != bundle.result.model_identity
                ):
                    raise ValueError("TRAINING_LINEAGE_MISMATCH")
                if record.status == "TRAINING_FAILED" and (
                    bundle.result.status == "TRAINED"
                    or record.reason != bundle.result.failure_reason
                ):
                    raise ValueError("TRAINING_FAILURE_MISMATCH")
                if (
                    record.status in ("EVALUATED", "EVALUATION_FAILED")
                    and bundle.result.status != "TRAINED"
                ):
                    raise ValueError("TRAINED_MODEL_REQUIRED")
            elif record.status != "BUDGET_EXCEEDED":
                raise ValueError("TRAINING_ATTEMPT_MISSING")
            if record.evaluation_reference is not None:
                report = store.resolve(record.evaluation_reference)
                if (
                    not isinstance(report, evaluation.DevelopmentTrialEvaluation)
                    or record.model_identity is None
                ):
                    raise ValueError("EVALUATION_REQUIRED")
                if (
                    report.model_identity_reference
                    != reference("modelidentity", record.model_identity)
                    or report.spec_reference != reference("trialspec", definition.spec)
                    or report.population_fingerprint
                    != semantic_fingerprint(development_rows(definition.spec))
                    or report.metric_id != request.objective.metric_id
                    or report.objective_value != record.objective_value
                ):
                    raise ValueError("EVALUATION_LINEAGE_MISMATCH")
            records.append(record)
        scores, selected = select_candidate(request, plan, tuple(records))
        if (
            result.scores != scores
            or result.selection_rule != request.selection_rule
            or result.selected_trial_id != (selected.trial_id if selected else None)
            or result.selected_model_identity != (selected.model_identity if selected else None)
            or result.failed_trial_count != sum(r.status != "EVALUATED" for r in records)
            or result.budget_exceeded != any(r.status == "BUDGET_EXCEEDED" for r in records)
        ):
            raise ValueError("SELECTION_MISMATCH")
        return "MATCH"
    except (ValueError, OSError):
        return "MISMATCH"
