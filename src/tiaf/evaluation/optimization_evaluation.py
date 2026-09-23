"""Evaluation-owned synthetic adapter; delegates metrics to existing Evaluation.

No fitting, trial search, selection, scientific approval or calibration.
Record validation never recomputes metrics, permitting recorded-only replay.
"""

from typing import Literal

from pydantic import Field

from tiaf.forecasting.identity import ArtifactReference, ForecastDateTime, semantic_fingerprint
from tiaf.learning.forecast_artifacts import Finite, SealedResearch, reconstruct
from tiaf.learning.forecaster_training import ModelArtifactIdentity, reference
from tiaf.learning.synthetic_trials import SyntheticModel, development_rows
from tiaf.planner.models import Sha256

from .forecast_comparison_metrics import arm_metrics


class DevelopmentTrialEvaluation(SealedResearch):
    metric_id: Literal["metric:brier", "metric:log-loss", "metric:accuracy"]
    model_identity_reference: ArtifactReference
    spec_reference: ArtifactReference
    population_fingerprint: Sha256
    probabilities: tuple[Finite, ...] = Field(min_length=40, max_length=40)
    labels: tuple[Literal[0, 1], ...] = Field(min_length=40, max_length=40)
    objective_value: Finite
    evidence_scope: Literal["DEVELOPMENT_ONLY"] = "DEVELOPMENT_ONLY"
    created_at: ForecastDateTime


def evaluate_trial(
    model: SyntheticModel,
    identity: ModelArtifactIdentity,
    metric_id: Literal["metric:brier", "metric:log-loss", "metric:accuracy"],
    at: ForecastDateTime,
) -> DevelopmentTrialEvaluation:
    model = SyntheticModel.model_validate(model.model_dump())
    if identity.artifact != reference("trialmodel", model):
        raise ValueError("EVALUATION_MODEL_IDENTITY_MISMATCH")
    if at < model.created_at:
        raise ValueError("EVALUATION_BEFORE_MODEL")
    rows = development_rows(model.spec)
    values = tuple((reconstruct(model.reconstruction, x), y) for x, y in rows)
    metrics = arm_metrics(values)
    assert metrics is not None
    return DevelopmentTrialEvaluation.model_validate(
        dict(
            metric_id=metric_id,
            model_identity_reference=reference("modelidentity", identity),
            spec_reference=reference("trialspec", model.spec),
            population_fingerprint=semantic_fingerprint(rows),
            probabilities=tuple(p for p, _ in values),
            labels=tuple(y for _, y in values),
            objective_value={
                "metric:brier": metrics.brier,
                "metric:log-loss": metrics.log_loss,
                "metric:accuracy": metrics.accuracy,
            }[metric_id],
            created_at=at,
        )
    )
