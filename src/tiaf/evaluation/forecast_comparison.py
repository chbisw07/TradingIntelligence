"""Development-only pairing, population dispositions and fixed scientific gates."""

import math
from collections import Counter
from datetime import datetime
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from tiaf.evaluation.forecast_comparison_metrics import (
    ArmMetrics,
    BootstrapResult,
    DevelopmentPolicy,
    arm_metrics,
    bootstrap,
    losses,
)
from tiaf.evaluation.forecast_research_truth import ResearchOutcomeEntry
from tiaf.forecasting.identity import ForecastDateTime, semantic_fingerprint
from tiaf.forecasting.logistic_forecasts import Fold, ResearchForecastResult
from tiaf.forecasting.research_baserate import ResearchBaseRateForecast
from tiaf.forecasting.research_contracts import ResearchContract, ResearchDate
from tiaf.learning.forecast_artifacts import Finite, SealedResearch
from tiaf.planner.models import Sha256


class PairedObservation(SealedResearch):
    observation_id: str
    reference_date: ResearchDate
    target_date: ResearchDate
    fold: Fold
    information_cutoff: ForecastDateTime
    simulation_as_of: ForecastDateTime
    common_request_fingerprint: Sha256
    ground_truth_fingerprint: Sha256
    baseline_forecast_fingerprint: Sha256
    logistic_forecast_fingerprint: Sha256
    y: Literal[0, 1]
    baseline_probability: Finite
    logistic_probability: Finite
    baseline_brier: Finite
    logistic_brier: Finite
    brier_difference: Finite
    baseline_logloss: Finite
    logistic_logloss: Finite
    logloss_difference: Finite

    @model_validator(mode="after")
    def valid(self) -> Self:
        if (
            self.reference_date.year != self.fold
            or not self.reference_date < self.target_date
            or self.target_date.year >= 2025
        ):
            raise ValueError("PROTECTED_PAIR_FORBIDDEN")
        b, ll = losses(self.baseline_probability, self.y)
        c, cll = losses(self.logistic_probability, self.y)
        if (
            self.baseline_brier,
            self.logistic_brier,
            self.brier_difference,
            self.baseline_logloss,
            self.logistic_logloss,
            self.logloss_difference,
        ) != (b, c, c - b, ll, cll, cll - ll):
            raise ValueError("PAIR_LOSS_MISMATCH")
        return self


class PopulationDisposition(ResearchContract):
    observation_id: str
    reference_date: ResearchDate
    fold: Fold
    protected: bool
    logistic_available: bool
    baseline_available: bool
    truth_available: bool
    paired: bool
    primary_reason: str
    facets: tuple[str, ...]
    unevaluated_checks: tuple[str, ...]
    decisions: tuple[tuple[str, str, str, str], ...]

    @model_validator(mode="after")
    def development_scope(self) -> Self:
        if self.reference_date.year != self.fold:
            raise ValueError("PROTECTED_DISPOSITION_GRID_FORBIDDEN")
        if self.protected and (
            self.paired
            or self.truth_available
            or self.baseline_available
            or self.logistic_available
        ):
            raise ValueError("PROTECTED_DISPOSITION_VALUES_FORBIDDEN")
        return self


def pair_observation(
    logistic: ResearchForecastResult,
    baseline: ResearchBaseRateForecast | None,
    truth: ResearchOutcomeEntry | None,
    evaluated_at: datetime,
) -> tuple[PairedObservation | None, PopulationDisposition]:
    q, o = logistic.request, logistic.request.origin
    if evaluated_at < logistic.computed_at or (
        baseline is not None and evaluated_at < baseline.computed_at
    ):
        raise ValueError("EVALUATION_BEFORE_FORECAST_CAPTURE")
    if o.protected and (baseline is not None or truth is not None):
        raise ValueError("PROTECTED_PAIR_COMPONENT_FORBIDDEN")
    if baseline is not None and (
        baseline.common_request_fingerprint != q.fingerprint
        or baseline.observation_id != o.observation_id
    ):
        raise ValueError("BASELINE_PAIR_IDENTITY_MISMATCH")
    if truth is not None and (
        any(
            getattr(truth, k) != getattr(o, k)
            for k in (
                "observation_id",
                "reference_date",
                "target_date",
                "reference_closes_at",
                "information_cutoff",
                "simulation_as_of",
                "target_opens_at",
                "input_fingerprint",
                "profile_fingerprint",
                "price_series_basis",
            )
        )
        or truth.subject != q.subject
        or truth.target_id != q.target_id
        or truth.qualification_fingerprint != q.qualification_fingerprint
        or truth.qualification_blob != q.qualification_blob
        or truth.dataset_fingerprint != q.dataset_fingerprint
        or evaluated_at < truth.source_assessed_at
    ):
        raise ValueError("GROUND_TRUTH_PAIR_IDENTITY_MISMATCH")
    la = logistic.output is not None
    ba = baseline is not None and baseline.output is not None
    ta = truth is not None and truth.label is not None
    facets: list[str] = []
    if o.protected:
        facets.append("TARGET_HOLDOUT_SEALED")
    else:
        facets.extend(o.reasons)
        if not la:
            facets.append("LOGISTIC_ABSENT")
        if not ba:
            facets.append("BASERATE_SUPPORT_INSUFFICIENT")
        if not ta:
            facets.append("GROUND_TRUTH_UNAVAILABLE")
    included = not facets and la and ba and ta
    reason = "INCLUDED" if included else facets[0]
    disposition = PopulationDisposition(
        observation_id=o.observation_id,
        reference_date=o.reference_date,
        fold=q.fold_id,
        protected=o.protected,
        logistic_available=la,
        baseline_available=ba,
        truth_available=ta,
        paired=included,
        primary_reason=reason,
        facets=tuple(facets),
        unevaluated_checks=("GROUND_TRUTH", "METRICS") if o.protected else (),
        decisions=tuple(
            (arm, metric, "INCLUDED" if included else "EXCLUDED", reason)
            for arm in ("BENCHMARK", "CHALLENGER")
            for metric in ("BRIER", "LOG_LOSS")
        ),
    )
    if not included:
        return None, disposition
    assert logistic.output is not None and baseline is not None and baseline.output is not None
    assert truth is not None and truth.label is not None and o.target_date is not None
    bp, lp, y = baseline.output.probability, logistic.output.probability, truth.label
    b, ll = losses(bp, y)
    c, cll = losses(lp, y)
    return PairedObservation(
        observation_id=o.observation_id,
        reference_date=o.reference_date,
        target_date=o.target_date,
        fold=q.fold_id,
        information_cutoff=o.information_cutoff,
        simulation_as_of=o.simulation_as_of,
        common_request_fingerprint=cast(str, q.fingerprint),
        ground_truth_fingerprint=cast(str, truth.fingerprint),
        baseline_forecast_fingerprint=cast(str, baseline.fingerprint),
        logistic_forecast_fingerprint=cast(str, logistic.fingerprint),
        y=y,  # type: ignore[arg-type]
        baseline_probability=bp,
        logistic_probability=lp,
        baseline_brier=b,
        logistic_brier=c,
        brier_difference=c - b,
        baseline_logloss=ll,
        logistic_logloss=cll,
        logloss_difference=cll - ll,
    ), disposition


class PopulationAccounting(ResearchContract):
    requested: int
    logistic_forecasts: int
    baseline_forecasts: int
    truth_available: int
    union_forecasts: int
    intersection_forecasts: int
    paired_evaluated: int
    unpaired: int
    protected: int
    primary_exclusions: tuple[tuple[str, int], ...]
    all_exclusion_facets: tuple[tuple[str, int], ...]


def accounting(rows: tuple[PopulationDisposition, ...]) -> PopulationAccounting:
    return PopulationAccounting(
        requested=len(rows),
        logistic_forecasts=sum(r.logistic_available for r in rows),
        baseline_forecasts=sum(r.baseline_available for r in rows),
        truth_available=sum(r.truth_available for r in rows),
        union_forecasts=sum(r.logistic_available or r.baseline_available for r in rows),
        intersection_forecasts=sum(r.logistic_available and r.baseline_available for r in rows),
        paired_evaluated=sum(r.paired for r in rows),
        unpaired=sum(not r.paired for r in rows),
        protected=sum(r.protected for r in rows),
        primary_exclusions=tuple(
            sorted(Counter(r.primary_reason for r in rows if not r.paired).items())
        ),
        all_exclusion_facets=tuple(sorted(Counter(f for r in rows for f in r.facets).items())),
    )


class DevelopmentSummary(ResearchContract):
    name: Literal["2021", "2022", "2023", "2024", "POOLED"]
    population: PopulationAccounting
    n: int
    positive: int
    zero: int
    prevalence: Finite | None
    coverage: Finite
    complete_nonoverlapping_blocks: int
    baseline: ArmMetrics | None
    logistic: ArmMetrics | None
    fixed_half_diagnostic: ArmMetrics | None
    brier_difference: Finite | None
    logloss_difference: Finite | None
    opposite_sides: int
    mean_absolute_probability_difference: Finite | None
    largest_disagreements: tuple[tuple[str, Finite], ...]
    bootstrap: BootstrapResult


def summarize(
    name: str, pairs: tuple[PairedObservation, ...], dispositions: tuple[PopulationDisposition, ...]
) -> DevelopmentSummary:
    dates = tuple(d.reference_date for d in dispositions)
    if dates != tuple(sorted(set(dates))) or len({p.observation_id for p in pairs}) != len(pairs):
        raise ValueError("EVALUATION_DUPLICATE_OR_UNORDERED_POPULATION")
    lookup = {p.observation_id: p for p in pairs}
    if set(lookup) != {d.observation_id for d in dispositions if d.paired}:
        raise ValueError("PAIRED_POPULATION_MISMATCH")
    grids = tuple(
        tuple(
            None
            if not d.paired
            else (
                lookup[d.observation_id].brier_difference,
                lookup[d.observation_id].logloss_difference,
            )
            for d in dispositions
            if d.fold == fold
        )
        for fold in sorted({d.fold for d in dispositions})
    )
    blocks = sum(
        all(row is not None for row in grid[i : i + 5])
        for grid in grids
        for i in range(0, len(grid) - 4, 5)
    )
    n = len(pairs)
    return DevelopmentSummary(
        name=name,  # type: ignore[arg-type]
        population=accounting(dispositions),
        n=n,
        positive=sum(p.y for p in pairs),
        zero=sum(1 - p.y for p in pairs),
        prevalence=None if not n else sum(p.y for p in pairs) / n,
        coverage=n / len(dispositions) if dispositions else 0.0,
        complete_nonoverlapping_blocks=blocks,
        baseline=arm_metrics(tuple((p.baseline_probability, p.y) for p in pairs)),
        logistic=arm_metrics(tuple((p.logistic_probability, p.y) for p in pairs)),
        fixed_half_diagnostic=arm_metrics(tuple((0.5, p.y) for p in pairs)),
        brier_difference=None if not n else math.fsum(p.brier_difference for p in pairs) / n,
        logloss_difference=None if not n else math.fsum(p.logloss_difference for p in pairs) / n,
        opposite_sides=sum(
            (p.baseline_probability >= 0.5) != (p.logistic_probability >= 0.5) for p in pairs
        ),
        mean_absolute_probability_difference=None
        if not n
        else math.fsum(abs(p.logistic_probability - p.baseline_probability) for p in pairs) / n,
        largest_disagreements=tuple(
            sorted(
                (
                    (p.observation_id, abs(p.logistic_probability - p.baseline_probability))
                    for p in pairs
                ),
                key=lambda item: (-item[1], item[0]),
            )[:5]
        ),
        bootstrap=bootstrap(grids),
    )


class DevelopmentDecision(ResearchContract):
    classification: Literal["LOGISTIC_NOT_SUPPORTED", "INSUFFICIENT_EVIDENCE"]
    support_failures: tuple[str, ...]
    stability_failures: tuple[str, ...]
    final_holdout_evidence: Literal["NOT_RUN"] = "NOT_RUN"
    holdout_status: Literal["SEALED"] = "SEALED"


def decide(
    folds: tuple[DevelopmentSummary, ...], pooled: DevelopmentSummary
) -> DevelopmentDecision:
    if tuple(s.name for s in folds) != ("2021", "2022", "2023", "2024"):
        raise ValueError("DEVELOPMENT_FOLDS_REQUIRED")
    support, stability = [], []
    for s in folds:
        if (
            s.n < 150
            or min(s.positive, s.zero) < 30
            or s.coverage < 0.8
            or s.complete_nonoverlapping_blocks < 20
            or s.bootstrap.status != "ESTIMATED"
        ):
            support.append(f"{s.name}:DEVELOPMENT_SUPPORT_OR_INTERVAL_INADEQUATE")
        if s.brier_difference is not None and s.brier_difference > 0.02:
            stability.append(f"{s.name}:BRIER_WORSENING_GT_0.02")
        if s.logloss_difference is not None and s.logloss_difference > 0.05:
            stability.append(f"{s.name}:LOGLOSS_WORSENING_GT_0.05")
    if pooled.n < 600 or pooled.bootstrap.status != "ESTIMATED":
        support.append("POOLED_SUPPORT_OR_INTERVAL_INADEQUATE")
    if sum(s.brier_difference is not None and s.brier_difference < 0 for s in folds) < 3:
        stability.append("FEWER_THAN_THREE_NEGATIVE_DEVELOPMENT_BRIER_FOLDS")
    # Interval sign is deliberately NOT a development rejection criterion.
    return DevelopmentDecision(
        classification="LOGISTIC_NOT_SUPPORTED"
        if stability and not support
        else "INSUFFICIENT_EVIDENCE",
        support_failures=tuple(support),
        stability_failures=tuple(stability),
    )


class DevelopmentEvaluation(SealedResearch):
    evaluation_version: Literal["ff1.4.development/1.0"] = "ff1.4.development/1.0"
    evaluation_scope: Literal["DEVELOPMENT_ONLY"] = "DEVELOPMENT_ONLY"
    subject: Literal["RELIANCE:NSE:NSE_EQUITY:EQUITY"] = "RELIANCE:NSE:NSE_EQUITY:EQUITY"
    target_id: Literal["equity.next_session_close.return_gt_zero/1.0"] = (
        "equity.next_session_close.return_gt_zero/1.0"
    )
    price_series_basis: Literal["CORPORATE_ACTION_ADJUSTED"] = "CORPORATE_ACTION_ADJUSTED"
    mode: Literal["SIMULATED_RESEARCH"] = "SIMULATED_RESEARCH"
    baserate_identity: Literal["forecaster:historical-base-rate/2.0:BENCHMARK"] = (
        "forecaster:historical-base-rate/2.0:BENCHMARK"
    )
    logistic_identity: Literal["forecaster:logistic-regression/1.0:CHALLENGER:EXPERIMENTAL"] = (
        "forecaster:logistic-regression/1.0:CHALLENGER:EXPERIMENTAL"
    )
    policy: DevelopmentPolicy
    input_manifest_fingerprint: Sha256
    paired_population_fingerprint: Sha256
    ground_truth_fingerprint: Sha256
    logistic_run_fingerprint: Sha256
    research_profile_fingerprint: Sha256
    summaries: tuple[DevelopmentSummary, ...] = Field(min_length=5, max_length=5)
    decision: DevelopmentDecision
    created_at: ForecastDateTime

    @model_validator(mode="after")
    def exact_decision(self) -> Self:
        if self.summaries[-1].name != "POOLED" or self.decision != decide(
            self.summaries[:4], self.summaries[-1]
        ):
            raise ValueError("DEVELOPMENT_DECISION_MISMATCH")
        return self


def paired_identity(pairs: tuple[PairedObservation, ...]) -> str:
    # Population identity is independent of capture clocks and model losses.
    return semantic_fingerprint(
        tuple(
            p.model_dump(
                include={
                    "observation_id",
                    "reference_date",
                    "target_date",
                    "fold",
                    "information_cutoff",
                    "simulation_as_of",
                    "ground_truth_fingerprint",
                }
            )
            for p in pairs
        )
    )
