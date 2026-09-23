"""Finite, data-only optimization contracts. Selection is not approval."""

import itertools
import math
import re
from typing import Annotated, Literal, Self

from pydantic import Field, StrictBool, StrictFloat, StrictInt, StrictStr, model_validator

from tiaf.forecasting.forecaster_seams import ForecasterKey
from tiaf.forecasting.identity import (
    ArtifactReference,
    ForecastDateTime,
    LogicalId,
    semantic_fingerprint,
)
from tiaf.planner.models import Sha256

from .forecast_artifacts import Finite, SealedResearch
from .forecaster_authority import TrainingAuthorization
from .forecaster_training import (
    ExperimentIdentity,
    ModelArtifactIdentity,
    TrainingIdentity,
    reference,
)
from .synthetic_trials import (
    DATASET,
    FEATURES,
    KEY,
    PROFILE,
    QUALIFICATION,
    TARGET,
    SyntheticConfig,
    SyntheticSpec,
    training_request,
)

Value = StrictBool | StrictInt | StrictFloat | StrictStr


class Domain(SealedResearch):
    name: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]{0,39}$")
    kind: Literal["CATEGORICAL", "INTEGER", "FLOAT", "BOOLEAN"]
    values: tuple[Value, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def finite_values(self) -> Self:
        expected = {"CATEGORICAL": str, "INTEGER": int, "FLOAT": float, "BOOLEAN": bool}[self.kind]
        if any(type(v) is not expected for v in self.values):
            raise ValueError("DOMAIN_TYPE_MISMATCH")
        if len({semantic_fingerprint(v) for v in self.values}) != len(self.values):
            raise ValueError("DUPLICATE_DOMAIN_VALUE")
        if any(isinstance(v, float) and not math.isfinite(v) for v in self.values):
            raise ValueError("NONFINITE_DOMAIN")
        if any(
            isinstance(v, str) and not re.fullmatch(r"[A-Za-z0-9_.:-]{1,64}", v)
            for v in self.values
        ):
            raise ValueError("EXECUTABLE_DOMAIN_FORBIDDEN")
        return self


class SearchSpace(SealedResearch):
    domains: tuple[Domain, ...] = Field(min_length=1, max_length=3)

    @model_validator(mode="after")
    def unique(self) -> Self:
        if len({d.name for d in self.domains}) != len(self.domains):
            raise ValueError("DUPLICATE_PARAMETER")
        return self


class Objective(SealedResearch):
    metric_id: Literal["metric:brier", "metric:log-loss", "metric:accuracy"]
    direction: Literal["MINIMIZE", "MAXIMIZE"]
    population_fingerprint: Sha256
    aggregation: Literal["EQUAL_MEAN_OF_TWO_TEMPORAL_FOLDS"] = "EQUAL_MEAN_OF_TWO_TEMPORAL_FOLDS"


class OptimizationBudget(SealedResearch):
    max_trials: Literal[2, 4, 6] = 6
    max_wall_seconds: Annotated[StrictFloat, Field(gt=0, le=360)] = 360.0
    per_trial_seconds: Annotated[StrictFloat, Field(gt=0, le=60)] = 60.0
    max_memory_mib: Literal[512] = 512
    max_training_observations: Literal[640] = 640
    max_features: Literal[5] = 5
    max_parallelism: Literal[1] = 1


DEVELOPMENT_POPULATION = semantic_fingerprint((DATASET, ((600, 640), (640, 680))))


class OptimizationRequest(SealedResearch):
    request_version: Literal["flc3.optimization.1"] = "flc3.optimization.1"
    optimization_request_id: LogicalId
    family: Literal["LOGISTIC_REGRESSION"] = "LOGISTIC_REGRESSION"
    forecaster: ForecasterKey = KEY
    experiment_id: LogicalId
    search: SearchSpace
    objective: Objective
    budget: OptimizationBudget
    training_authority_reference: ArtifactReference
    dependency_lock_fingerprint: Sha256
    implementation_fingerprint: Sha256
    qualification_fingerprint: Sha256 = QUALIFICATION
    dataset_fingerprint: Sha256 = DATASET
    research_profile_fingerprint: Sha256 = PROFILE
    target_id: Literal["synthetic:positive-label"] = TARGET
    feature_schema_id: Literal["synthetic:five-patterns-v1"] = FEATURES
    seed: Literal[1729] = 1729
    selection_rule: Literal[
        "PRIMARY_THEN_STABLE_CANDIDATE_ID;LAST_INNER_FOLD_ARTIFACT;NO_REFIT"
    ] = "PRIMARY_THEN_STABLE_CANDIDATE_ID;LAST_INNER_FOLD_ARTIFACT;NO_REFIT"
    evidence_scope: Literal["DEVELOPMENT_ONLY"] = "DEVELOPMENT_ONLY"
    protected_evidence_allowed: Literal[False] = False
    consumed_holdout_allowed: Literal[False] = False
    experiment_status: Literal["OPEN"] = "OPEN"
    holdout_status: Literal["NONE"] = "NONE"
    created_at: ForecastDateTime

    @model_validator(mode="after")
    def scope(self) -> Self:
        if self.forecaster != KEY:
            raise ValueError("EXACT_SYNTHETIC_IMPLEMENTATION_REQUIRED")
        if (
            self.qualification_fingerprint,
            self.dataset_fingerprint,
            self.research_profile_fingerprint,
        ) != (QUALIFICATION, DATASET, PROFILE):
            raise ValueError("ONLY_AUTHORED_SYNTHETIC_DATA_QUALIFIED")
        if self.objective.population_fingerprint != DEVELOPMENT_POPULATION:
            raise ValueError("EXACT_DEVELOPMENT_POPULATION_REQUIRED")
        return self


class Assignment(SealedResearch):
    values: tuple[tuple[str, Value], ...]


class TrialDefinition(SealedResearch):
    trial_id: LogicalId
    candidate_id: LogicalId
    index: int = Field(ge=0, lt=6)
    optimization_reference: ArtifactReference
    assignment: Assignment
    spec: SyntheticSpec
    training: TrainingIdentity


class TrialPlan(SealedResearch):
    request_reference: ArtifactReference
    trials: tuple[TrialDefinition, ...] = Field(min_length=2, max_length=6)


def plan_trials(request: OptimizationRequest) -> TrialPlan:
    request = OptimizationRequest.model_validate(request.model_dump())
    domains = request.search.domains
    if {d.name for d in domains} != {"C", "fit_intercept"}:
        raise ValueError("UNSUPPORTED_SYNTHETIC_PARAMETER")
    trials: list[TrialDefinition] = []
    products = tuple(itertools.product(*(d.values for d in domains)))
    # Validate the entire declared grid, including the unexecuted bounded suffix.
    for values in products:
        SyntheticConfig.model_validate(dict(zip((d.name for d in domains), values, strict=True)))
    for values in products[: request.budget.max_trials // 2]:
        assignment = Assignment(
            values=tuple((d.name, v) for d, v in zip(domains, values, strict=True))
        )
        config = SyntheticConfig.model_validate(dict(assignment.values))
        candidate = f"flc3:candidate-{assignment.fingerprint}"
        experiment_key = semantic_fingerprint(
            (request.experiment_id, request.fingerprint, candidate)
        )
        experiment = ExperimentIdentity(
            experiment_id=f"flc3:experiment-{experiment_key}",
            candidate_id=candidate,
            forecaster=KEY,
            design_reference=reference("optrequest", request),
        )
        for fold in (0, 1):
            spec = SyntheticSpec(
                config=config,
                fold=fold,
                created_at=request.created_at,
                dependency_lock_fingerprint=request.dependency_lock_fingerprint,
                implementation_fingerprint=request.implementation_fingerprint,
            )
            trial_key = semantic_fingerprint((request.fingerprint, candidate, fold))
            trial = TrialDefinition(
                trial_id=f"flc3:trial-{trial_key}",
                candidate_id=candidate,
                index=len(trials),
                optimization_reference=reference("optrequest", request),
                assignment=assignment,
                spec=spec,
                training=training_request(spec, experiment, request.training_authority_reference),
            )
            trials.append(trial)
    return TrialPlan(request_reference=reference("optrequest", request), trials=tuple(trials))


class OptimizationGrant(SealedResearch):
    request_reference: ArtifactReference
    plan_reference: ArtifactReference
    training_grants: tuple[TrainingAuthorization, ...] = Field(min_length=2, max_length=6)
    evidence_scope: Literal["DEVELOPMENT_ONLY"] = "DEVELOPMENT_ONLY"
    protected_evidence_allowed: Literal[False] = False
    consumed_holdout_allowed: Literal[False] = False
    experiment_status: Literal["OPEN"] = "OPEN"
    holdout_status: Literal["NONE"] = "NONE"


class OptimizationClaim(SealedResearch):
    request_reference: ArtifactReference
    grant_reference: ArtifactReference
    consumed_before_trials: Literal[True] = True


class TrialRecord(SealedResearch):
    definition_reference: ArtifactReference
    trial_id: LogicalId
    status: Literal["EVALUATED", "TRAINING_FAILED", "EVALUATION_FAILED", "BUDGET_EXCEEDED"]
    bundle_reference: ArtifactReference | None = None
    evaluation_reference: ArtifactReference | None = None
    model_identity: ModelArtifactIdentity | None = None
    objective_value: Finite | None = None
    reason: str | None = None
    elapsed_seconds: Finite = Field(ge=0)

    @model_validator(mode="after")
    def state(self) -> Self:
        evaluated = self.status == "EVALUATED"
        if (
            evaluated != (self.evaluation_reference is not None)
            or evaluated != (self.objective_value is not None)
            or evaluated != (self.reason is None)
        ):
            raise ValueError("TRIAL_OUTCOME_MISMATCH")
        if evaluated and (self.bundle_reference is None or self.model_identity is None):
            raise ValueError("TRIAL_LINEAGE_MISSING")
        return self


class CandidateScore(SealedResearch):
    candidate_id: LogicalId
    trial_ids: tuple[LogicalId, LogicalId]
    value: Finite


class OptimizationResult(SealedResearch):
    request_reference: ArtifactReference
    plan_reference: ArtifactReference
    grant_reference: ArtifactReference
    trial_references: tuple[ArtifactReference, ...]
    scores: tuple[CandidateScore, ...]
    selected_trial_id: LogicalId | None
    selected_model_identity: ModelArtifactIdentity | None
    status: Literal["SELECTED", "NO_VALID_TRIAL"]
    selection_rule: str
    elapsed_seconds: Finite = Field(ge=0)
    failed_trial_count: int = Field(ge=0, le=6)
    budget_exceeded: bool
    evidence_scope: Literal["DEVELOPMENT_ONLY"] = "DEVELOPMENT_ONLY"
    lifecycle: Literal["EXPERIMENTAL"] = "EXPERIMENTAL"
    approval: None = None
    activation: Literal[False] = False
    promotion: Literal[False] = False

    @model_validator(mode="after")
    def outcome(self) -> Self:
        selected = self.status == "SELECTED"
        if (
            selected != (self.selected_trial_id is not None)
            or selected != (self.selected_model_identity is not None)
            or selected != bool(self.scores)
        ):
            raise ValueError("OPTIMIZATION_OUTCOME_MISMATCH")
        return self
