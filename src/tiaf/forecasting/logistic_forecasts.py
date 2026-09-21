"""Additive v2 SIMULATED Logistic requests/results; no truth or fitting API."""

from collections import Counter
from datetime import datetime
from typing import Annotated, Literal, Self, cast

from pydantic import Field, StrictInt, model_validator

from tiaf.forecasting.contracts import BinaryProbabilityOutput
from tiaf.forecasting.identity import ForecastDateTime, semantic_fingerprint
from tiaf.forecasting.logistic_projection import ForecastOrigin, ForecastProjection
from tiaf.forecasting.research_contracts import ResearchContract
from tiaf.learning.forecast_artifacts import Five, LogisticArtifact, SealedResearch, reconstruct
from tiaf.learning.forecast_jobs import TrainingRun
from tiaf.planner.models import Sha256

Fold = Literal[2021, 2022, 2023, 2024]
Count = Annotated[StrictInt, Field(ge=0, le=4096)]


class LogisticComposition(SealedResearch):
    composition_id: Literal["ff1.logistic_singleton/1.0"] = "ff1.logistic_singleton/1.0"
    forecaster_id: Literal["forecaster:logistic-regression"] = "forecaster:logistic-regression"
    forecaster_version: Literal["1.0"] = "1.0"
    role: Literal["CHALLENGER"] = "CHALLENGER"
    lifecycle: Literal["EXPERIMENTAL"] = "EXPERIMENTAL"
    model_fingerprint: Sha256
    scaler_fingerprint: Sha256
    model_scientific_fingerprint: Sha256


class ResearchForecastRequest(SealedResearch):
    subject: Literal["RELIANCE:NSE:NSE_EQUITY:EQUITY"] = "RELIANCE:NSE:NSE_EQUITY:EQUITY"
    target_id: Literal["equity.next_session_close.return_gt_zero/1.0"] = (
        "equity.next_session_close.return_gt_zero/1.0"
    )
    mode: Literal["SIMULATED"] = "SIMULATED"
    purpose: Literal["SIMULATED_RESEARCH"] = "SIMULATED_RESEARCH"
    feature_schema_id: Literal["ff1.reliance.a2_daily_five/1.0"] = "ff1.reliance.a2_daily_five/1.0"
    feature_schema_fingerprint: Sha256
    feature_vector_fingerprint: Sha256 | None
    fold_id: Fold
    origin: ForecastOrigin
    composition: LogisticComposition
    training_run_fingerprint: Sha256
    qualification_blob: Sha256
    qualification_fingerprint: Sha256
    dataset_fingerprint: Sha256
    research_profile_fingerprint: Sha256
    dependency_lock_fingerprint: Sha256
    price_series_basis: Literal["CORPORATE_ACTION_ADJUSTED"] = "CORPORATE_ACTION_ADJUSTED"

    @model_validator(mode="after")
    def lineage(self) -> Self:
        f = self.origin.features
        if (
            self.fold_id != self.origin.reference_date.year
            or self.research_profile_fingerprint != self.origin.profile_fingerprint
            or self.feature_vector_fingerprint != (None if f is None else f.fingerprint)
            or (f is not None and f.feature_schema.fingerprint != self.feature_schema_fingerprint)
        ):
            raise ValueError("FORECAST_REQUEST_LINEAGE_MISMATCH")
        return self

    @property
    def scientific_fingerprint(self) -> str:
        # Full FeatureResults and qualification/model captures have real audit
        # clocks. Keep those in request.fingerprint, not scientific identity.
        o = self.origin
        return semantic_fingerprint(
            {
                "subject": self.subject,
                "target": self.target_id,
                "fold": self.fold_id,
                "reference": o.reference_date.isoformat(),
                "target_session": None if o.target_date is None else o.target_date.isoformat(),
                "cutoff": o.information_cutoff,
                "as_of": o.simulation_as_of,
                "target_open": o.target_opens_at,
                "mode": self.mode,
                "values": None if o.features is None else o.features.values,
                "reasons": o.reasons,
                "profile": self.research_profile_fingerprint,
                "dataset": self.dataset_fingerprint,
                "schema": self.feature_schema_fingerprint,
                "model": self.composition.model_scientific_fingerprint,
                "composition": self.composition.composition_id,
            }
        )


class ResearchForecastResult(SealedResearch):
    forecast_id: str = Field(pattern=r"^ff1-logistic:[0-9a-f]{64}$")
    request: ResearchForecastRequest
    computed_at: ForecastDateTime
    status: Literal["GENERATED", "UNAVAILABLE", "EXCLUDED", "PROTECTED"]
    output: BinaryProbabilityOutput | None
    reasons: tuple[str, ...]

    @model_validator(mode="after")
    def valid(self) -> Self:
        expected, reasons = eligibility(self.request.origin)
        if (
            self.forecast_id != "ff1-logistic:" + self.request.scientific_fingerprint
            or self.computed_at <= self.request.origin.simulation_as_of
            or self.status != expected
            or self.reasons != reasons
            or (self.output is not None) != (self.status == "GENERATED")
        ):
            raise ValueError("FORECAST_RESULT_SEMANTICS_MISMATCH")
        return self


def eligibility(
    origin: ForecastOrigin,
) -> tuple[Literal["GENERATED", "UNAVAILABLE", "EXCLUDED", "PROTECTED"], tuple[str, ...]]:
    if origin.protected:
        return "PROTECTED", ("TARGET_HOLDOUT_SEALED",)
    if origin.reasons:
        return "EXCLUDED", origin.reasons
    if origin.features is None or origin.target_date is None:
        return "UNAVAILABLE", ("MISSING_FEATURES_OR_TARGET_SESSION",)
    return "GENERATED", ()


def validate_handoff(run: TrainingRun) -> None:
    if run.status != "COMPLETE" or run.grant.basis != "QUALIFIED_ADJUSTED_RESEARCH":
        raise ValueError("COMPLETE_EMPIRICAL_TRAINING_REQUIRED")
    if any(j.artifact is None or j.artifact.versions.python != "3.12.3" for j in run.jobs):
        raise ValueError("TRAINING_ARTIFACT_OR_VERSION_MISSING")


def model_for(run: TrainingRun, fold: int) -> LogisticArtifact:
    validate_handoff(run)
    for job in run.jobs:
        if job.fold_id == fold and job.artifact is not None:
            return job.artifact
    raise ValueError("FOLD_MODEL_UNAVAILABLE")


def generate(
    origin: ForecastOrigin, source: ForecastProjection, run: TrainingRun, computed_at: datetime
) -> ResearchForecastResult:
    model = model_for(run, origin.reference_date.year)
    grant = run.grant
    if (
        source.qualification_fingerprint != grant.qualification_fingerprint
        or source.dataset_fingerprint != grant.dataset_fingerprint
        or source.profile.fingerprint != grant.research_profile_fingerprint
        or source.feature_schema.fingerprint != grant.feature_schema_fingerprint
        or origin not in source.origins
        or model.manifest.fit_cutoff >= origin.information_cutoff
        or computed_at < run.created_at
    ):
        raise ValueError("FORECAST_HANDOFF_OR_CLOCK_MISMATCH")
    request = ResearchForecastRequest(
        fold_id=model.manifest.fold_id,
        origin=origin,
        composition=LogisticComposition(
            model_fingerprint=cast(str, model.fingerprint),
            scaler_fingerprint=cast(str, model.reconstruction.scaler.fingerprint),
            model_scientific_fingerprint=model.scientific_fingerprint,
        ),
        training_run_fingerprint=cast(str, run.fingerprint),
        qualification_blob=source.qualification_blob,
        qualification_fingerprint=source.qualification_fingerprint,
        dataset_fingerprint=source.dataset_fingerprint,
        research_profile_fingerprint=source.profile.fingerprint,
        dependency_lock_fingerprint=grant.dependency_lock_fingerprint,
        feature_schema_fingerprint=source.feature_schema.fingerprint,
        feature_vector_fingerprint=None if origin.features is None else origin.features.fingerprint,
    )
    status, reasons = eligibility(origin)
    output = None
    if status == "GENERATED":
        assert origin.features is not None
        probability = reconstruct(model.reconstruction, cast(Five, origin.features.values))
        output = BinaryProbabilityOutput(probability=probability)
    return ResearchForecastResult(
        forecast_id="ff1-logistic:" + request.scientific_fingerprint,
        request=request,
        computed_at=computed_at,
        status=status,
        output=output,
        reasons=reasons,
    )


class FoldPopulation(ResearchContract):
    fold_id: Fold
    candidate: Count
    eligible: Count
    generated: Count
    unavailable: Count
    excluded: Count
    protected: Count
    reason_counts: tuple[tuple[str, Count], ...]

    @model_validator(mode="after")
    def reconcile(self) -> Self:
        if (
            self.candidate != self.generated + self.unavailable + self.excluded + self.protected
            or self.eligible != self.generated
        ):
            raise ValueError("FORECAST_POPULATION_MISMATCH")
        return self


def population(fold: Fold, records: tuple[ResearchForecastResult, ...]) -> FoldPopulation:
    rows = tuple(r for r in records if r.request.fold_id == fold)
    counts = Counter(r.status for r in rows)
    reasons = Counter(reason for r in rows for reason in r.reasons)
    return FoldPopulation(
        fold_id=fold,
        candidate=len(rows),
        eligible=counts["GENERATED"],
        generated=counts["GENERATED"],
        unavailable=counts["UNAVAILABLE"],
        excluded=counts["EXCLUDED"],
        protected=counts["PROTECTED"],
        reason_counts=tuple(sorted(reasons.items())),
    )


class ForecastShard(SealedResearch):
    """Ordered append-safe capture references; separate from future truth ledger."""

    captures: tuple[Sha256, ...] = Field(min_length=1, max_length=64)


class LogisticForecastRun(SealedResearch):
    run_version: Literal["ff1.3/1.0"] = "ff1.3/1.0"
    forecaster_id: Literal["forecaster:logistic-regression"] = "forecaster:logistic-regression"
    role: Literal["CHALLENGER"] = "CHALLENGER"
    lifecycle: Literal["EXPERIMENTAL"] = "EXPERIMENTAL"
    mode: Literal["SIMULATED"] = "SIMULATED"
    qualification_blob: Sha256
    qualification_fingerprint: Sha256
    dataset_fingerprint: Sha256
    research_profile_fingerprint: Sha256
    feature_schema_fingerprint: Sha256
    training_run_fingerprint: Sha256
    dependency_lock_fingerprint: Sha256
    shards: tuple[Sha256, ...] = Field(min_length=1, max_length=64)
    populations: tuple[FoldPopulation, FoldPopulation, FoldPopulation, FoldPopulation]
    verification_matches: Count
    verification_mismatches: Literal[0] = 0
    verification_tolerance: Annotated[float, Field(strict=True, ge=1e-12, le=1e-12)] = 1e-12
    holdout_status: Literal["SEALED"] = "SEALED"
    created_at: ForecastDateTime

    @model_validator(mode="after")
    def complete(self) -> Self:
        if (
            tuple(p.fold_id for p in self.populations) != (2021, 2022, 2023, 2024)
            or sum(p.candidate for p in self.populations) != self.verification_matches
            or any(p.candidate == 0 for p in self.populations)
        ):
            raise ValueError("FORECAST_RUN_INCOMPLETE")
        return self
