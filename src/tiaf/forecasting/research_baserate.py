"""Research binding 2.0, unchanged BaseRatePolicy/1.0 unsmoothed arithmetic."""

from datetime import datetime, timedelta
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from tiaf.evaluation.forecast_research_truth import ResearchOutcomeEntry, ResearchTruthJournal
from tiaf.forecasting.contracts import BinaryProbabilityOutput
from tiaf.forecasting.identity import ForecastDateTime
from tiaf.forecasting.logistic_forecasts import Fold, ResearchForecastRequest
from tiaf.forecasting.support import BaseRatePolicy
from tiaf.learning.forecast_artifacts import SealedResearch
from tiaf.planner.models import Sha256


class ResearchBaseRateArtifact(SealedResearch):
    forecaster_id: Literal["forecaster:historical-base-rate"] = "forecaster:historical-base-rate"
    implementation_version: Literal["2.0"] = "2.0"
    role: Literal["BENCHMARK"] = "BENCHMARK"
    mode: Literal["SIMULATED_RESEARCH"] = "SIMULATED_RESEARCH"
    fold: Fold
    fit_cutoff: ForecastDateTime
    policy: BaseRatePolicy = Field(default_factory=BaseRatePolicy)
    scheduled_ids: tuple[str, ...] = Field(max_length=20)
    support: tuple[ResearchOutcomeEntry, ...] = Field(max_length=20)
    output: BinaryProbabilityOutput | None

    @model_validator(mode="after")
    def coherent(self) -> Self:
        eligible = tuple(
            e
            for e in self.support
            if e.label is not None
            and e.assumed_label_available_at is not None
            and e.assumed_label_available_at < self.fit_cutoff
            and e.target_closes_at < self.fit_cutoff
        )
        p = None if len(eligible) != 20 else sum(cast(int, e.label) for e in eligible) / 20
        if (
            self.fit_cutoff.year != self.fold - 1
            or self.scheduled_ids != tuple(e.observation_id for e in self.support)
            or tuple(e.reference_date for e in self.support)
            != tuple(sorted({e.reference_date for e in self.support}))
            or (None if self.output is None else self.output.probability) != p
        ):
            raise ValueError("BASERATE_SUPPORT_OR_PROBABILITY_MISMATCH")
        return self


def freeze_baseline(
    journal: ResearchTruthJournal, fold: Fold, fit_cutoff: datetime
) -> ResearchBaseRateArtifact:
    ids = dict(journal.baseline_support)[fold]
    mapping = {e.observation_id: e for e in journal.entries}
    # Missing journal members fail explicitly, never backfill or silently drop.
    selected = tuple(mapping[oid] for oid in ids)
    last = tuple(
        e.observation_id
        for e in journal.entries
        if e.target_closes_at + timedelta(minutes=30) < fit_cutoff
    )[-20:]
    if ids != last:
        raise ValueError("BASERATE_NOT_LAST_SCHEDULED_TRANSITIONS")
    if any(e.target_closes_at + timedelta(minutes=30) >= fit_cutoff for e in selected):
        raise ValueError("BASERATE_TARGET_LEAKAGE")
    eligible = tuple(
        e
        for e in selected
        if e.label is not None
        and e.assumed_label_available_at is not None
        and e.assumed_label_available_at < fit_cutoff
    )
    output = (
        None
        if len(eligible) != 20
        else BinaryProbabilityOutput(probability=sum(cast(int, e.label) for e in eligible) / 20)
    )
    return ResearchBaseRateArtifact(
        fold=fold, fit_cutoff=fit_cutoff, scheduled_ids=ids, support=selected, output=output
    )


class ResearchBaseRateForecast(SealedResearch):
    forecaster_id: Literal["forecaster:historical-base-rate"] = "forecaster:historical-base-rate"
    implementation_version: Literal["2.0"] = "2.0"
    role: Literal["BENCHMARK"] = "BENCHMARK"
    mode: Literal["SIMULATED"] = "SIMULATED"
    # The common Logistic request supplies exact observation/mode/clock/lineage,
    # not the benchmark composition; the benchmark artifact is separately pinned.
    common_request_fingerprint: Sha256
    observation_id: str
    baseline_artifact_fingerprint: Sha256
    output: BinaryProbabilityOutput | None
    computed_at: ForecastDateTime


def baseline_forecast(
    artifact: ResearchBaseRateArtifact, request: ResearchForecastRequest, computed_at: datetime
) -> ResearchBaseRateForecast:
    if (
        request.origin.protected
        or request.fold_id != artifact.fold
        or artifact.fit_cutoff >= request.origin.information_cutoff
        or computed_at <= request.origin.simulation_as_of
    ):
        raise ValueError("BASERATE_REQUEST_NOT_ADMITTED")
    return ResearchBaseRateForecast(
        common_request_fingerprint=cast(str, request.fingerprint),
        observation_id=request.origin.observation_id,
        baseline_artifact_fingerprint=cast(str, artifact.fingerprint),
        output=artifact.output,
        computed_at=computed_at,
    )
