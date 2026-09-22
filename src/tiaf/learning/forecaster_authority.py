"""External, request-pinned synthetic job authority. Not a lifecycle approval.

The trusted caller owns issuing experiment/authority identities and their audit
history. Content hashes detect mismatches; they do not authenticate reviewers.
There is no empirical fit route or grant renewal in this additive FLC-2 seam.
"""

from pathlib import Path
from typing import Literal, Self

from pydantic import TypeAdapter, model_validator

from tiaf.forecasting.identity import (
    ArtifactReference,
    ForecastDateTime,
    LogicalId,
    semantic_fingerprint,
)
from tiaf.planner.models import Sha256

from .forecast_artifacts import SealedResearch
from .forecaster_training import ExperimentIdentity, TrainingIdentity, reference


class TrainingAuthorization(SealedResearch):
    grant_id: LogicalId
    authority_reference: ArtifactReference
    experiment: ExperimentIdentity
    request_reference: ArtifactReference
    input_fingerprint: Sha256
    custody_root_fingerprint: Sha256
    experiment_status: Literal["OPEN", "CLOSED"]
    holdout_status: Literal["NONE", "PROTECTED", "CONSUMED"]
    qualification_reference: ArtifactReference
    evidence_policy: Literal["SYNTHETIC_TRAIN_ONLY"]
    issued_at: ForecastDateTime
    expires_at: ForecastDateTime
    maximum_executions: Literal[1] = 1
    empirical_fitting: Literal[False] = False
    post_holdout_refit: Literal[False] = False

    @model_validator(mode="after")
    def clocks(self) -> Self:
        if self.expires_at <= self.issued_at:
            raise ValueError("TRAINING_AUTHORITY_EXPIRY")
        return self


class TrainingAttempt(SealedResearch):
    grant_reference: ArtifactReference
    request_reference: ArtifactReference
    consumed_before_worker: Literal[True] = True


def custody_root_fingerprint(root: Path) -> str:
    # Do not serialize machine-specific/private paths into the lineage records.
    if (
        not root.is_absolute()
        or ".." in root.parts
        or any(p.is_symlink() for p in (root, *root.parents))
    ):
        raise ValueError("UNSAFE_TRAINING_CUSTODY")
    return semantic_fingerprint(str(root))


def admit_training(
    request: TrainingIdentity,
    authorization: TrainingAuthorization,
    *,
    input_fingerprint: str,
    root: Path,
    at: ForecastDateTime,
) -> None:
    request = TrainingIdentity.model_validate(request.model_dump())
    authorization = TrainingAuthorization.model_validate(authorization.model_dump())
    # Reuse aware canonical timestamp validation before comparing any instants.
    at = TypeAdapter(ForecastDateTime).validate_python(at)
    if authorization.experiment_status != "OPEN" or authorization.holdout_status != "NONE":
        raise ValueError("PROTECTED_CONSUMED_OR_CLOSED_EXPERIMENT")
    if request.purpose != "SYNTHETIC_ENGINEERING":
        raise ValueError("LEGACY_REFIT_NOT_AUTHORIZED")
    if (
        authorization.request_reference != reference("request", request)
        or authorization.experiment != request.experiment
        or authorization.input_fingerprint != input_fingerprint
        or authorization.custody_root_fingerprint != custody_root_fingerprint(root)
        or authorization.qualification_reference.fingerprint != request.qualification_fingerprint
        or not request.created_at <= authorization.issued_at <= at < authorization.expires_at
    ):
        raise ValueError("EXACT_TRAINING_AUTHORITY_REQUIRED")
