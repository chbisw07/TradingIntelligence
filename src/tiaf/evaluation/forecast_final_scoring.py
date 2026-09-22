"""Final-scope envelope over the frozen metric, sampler and decision kernels."""

import math
from collections import Counter
from datetime import datetime
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from tiaf.evaluation.forecast_comparison_metrics import ArmMetrics, arm_metrics, bootstrap, losses
from tiaf.evaluation.forecast_final_outcomes import FinalOutcome
from tiaf.evaluation.forecast_final_protocol import (
    FinalDecision,
    FinalEvidence,
    FinalProtocol,
    final_decision,
)
from tiaf.forecasting.final_inputs import FinalForecast, FinalInput
from tiaf.forecasting.identity import ForecastDateTime, semantic_fingerprint
from tiaf.forecasting.research_contracts import ResearchContract, ResearchDate
from tiaf.learning.forecast_artifacts import Finite, SealedResearch
from tiaf.planner.models import Sha256


class FinalPair(SealedResearch):
    observation_id: str
    reference_date: ResearchDate
    target_date: ResearchDate
    common_request_fingerprint: Sha256
    protocol_fingerprint: Sha256
    execution_fingerprint: Sha256
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
        b, ll = losses(self.baseline_probability, self.y)
        c, cll = losses(self.logistic_probability, self.y)
        if (
            self.reference_date.year != 2025
            or self.target_date <= self.reference_date
            or (
                self.baseline_brier,
                self.logistic_brier,
                self.brier_difference,
                self.baseline_logloss,
                self.logistic_logloss,
                self.logloss_difference,
            )
            != (b, c, c - b, ll, cll, cll - ll)
        ):
            raise ValueError("FINAL_PAIR_LOSS_OR_SCOPE_MISMATCH")
        return self


class FinalDisposition(ResearchContract):
    observation_id: str
    logistic_available: bool
    baserate_available: bool
    truth_available: bool
    paired: bool
    primary_reason: str
    facets: tuple[str, ...]
    unevaluated_checks: tuple[str, ...]
    decisions: tuple[tuple[str, str, str, str], ...]


def pair_final(
    protocol: FinalProtocol,
    request: FinalInput,
    logistic: FinalForecast,
    baseline: FinalForecast,
    truth: FinalOutcome,
    at: datetime,
) -> tuple[FinalPair | None, FinalDisposition]:
    """An identity mismatch fails the experiment; it is never an exclusion."""
    if (
        request.slot not in protocol.population.slots
        or request.protocol_fingerprint != protocol.fingerprint
        or any(
            r.common_request_fingerprint != request.fingerprint
            or r.protocol_fingerprint != protocol.fingerprint
            or r.execution_fingerprint != request.execution_fingerprint
            for r in (logistic, baseline, truth)
        )
        or logistic.arm != "LOGISTIC"
        or baseline.arm != "BASERATE"
        or logistic.artifact_fingerprint != protocol.model_fingerprint
        or logistic.scaler_fingerprint != protocol.scaler_fingerprint
        or baseline.artifact_fingerprint != protocol.baserate_state_fingerprint
        or at < max(logistic.computed_at, baseline.computed_at, truth.evaluation_as_known)
    ):
        raise ValueError("FINAL_PAIR_INTEGRITY_MISMATCH")
    la, ba, ta = (
        logistic.probability is not None,
        baseline.probability is not None,
        truth.label is not None,
    )
    # Frozen precedence: qualification/action/precision facets, absence, truth.
    facets = list(logistic.reasons)
    if "LABEL_UNSUPPORTED_ACTION" in truth.reasons:
        facets.append("LABEL_UNSUPPORTED_ACTION")
    if not la:
        facets.append("LOGISTIC_ABSENT")
    if not ba:
        facets.extend((*baseline.reasons, "BASERATE_SUPPORT_INSUFFICIENT"))
    facets.extend(r for r in truth.reasons if r != "LABEL_UNSUPPORTED_ACTION")
    if not ta:
        facets.append("GROUND_TRUTH_UNAVAILABLE")
    included = la and ba and ta and not facets
    disposition = FinalDisposition(
        observation_id=request.slot.observation_id,
        logistic_available=la,
        baserate_available=ba,
        truth_available=ta,
        paired=included,
        primary_reason="INCLUDED" if included else facets[0],
        facets=tuple(facets),
        unevaluated_checks=() if included else ("METRICS",),
        decisions=tuple(
            (
                arm,
                metric,
                "INCLUDED" if included else "EXCLUDED",
                "INCLUDED" if included else facets[0],
            )
            for arm in ("BENCHMARK", "CHALLENGER")
            for metric in ("BRIER", "LOG_LOSS")
        ),
    )
    if not included:
        return None, disposition
    assert logistic.probability is not None and baseline.probability is not None
    assert truth.label is not None and request.slot.target_date is not None
    lp, bp, y = logistic.probability, baseline.probability, truth.label
    b, ll = losses(bp, y)
    c, cll = losses(lp, y)
    return FinalPair(
        observation_id=request.slot.observation_id,
        reference_date=request.slot.reference_date,
        target_date=request.slot.target_date,
        common_request_fingerprint=cast(str, request.fingerprint),
        protocol_fingerprint=protocol.fingerprint,
        execution_fingerprint=request.execution_fingerprint,
        ground_truth_fingerprint=cast(str, truth.fingerprint),
        baseline_forecast_fingerprint=cast(str, baseline.fingerprint),
        logistic_forecast_fingerprint=cast(str, logistic.fingerprint),
        y=cast(Literal[0, 1], y),
        baseline_probability=bp,
        logistic_probability=lp,
        baseline_brier=b,
        logistic_brier=c,
        brier_difference=c - b,
        baseline_logloss=ll,
        logistic_logloss=cll,
        logloss_difference=cll - ll,
    ), disposition


class FinalBootstrap(ResearchContract):
    # Numeric fields from the unchanged sampler, without its development label.
    scope: Literal["FINAL_HOLDOUT"] = "FINAL_HOLDOUT"
    status: Literal["ESTIMATED", "NOT_ESTIMABLE"]
    effective_n: int
    point: tuple[Finite, Finite] | None
    bootstrap_mean: tuple[Finite, Finite] | None
    brier_interval: tuple[Finite, Finite] | None
    logloss_interval: tuple[Finite, Finite] | None
    zero_pair_replicates: int
    seed: Literal[1729] = 1729
    block_length: Literal[5] = 5
    replicates: Literal[5000] = 5000
    sampled_indices_fingerprint: Sha256


class FinalSummary(ResearchContract):
    candidate: int
    logistic_available: int
    baserate_available: int
    truth_available: int
    paired_eligible: int
    paired_evaluated: int
    exclusions: tuple[tuple[str, int], ...]
    exclusion_facets: tuple[tuple[str, int], ...]
    n: int
    positive: int
    zero: int
    prevalence: Finite | None
    coverage: Finite
    complete_blocks: int
    baseline: ArmMetrics | None
    logistic: ArmMetrics | None
    fixed_half_diagnostic: ArmMetrics | None
    brier_difference: Finite | None
    logloss_difference: Finite | None
    opposite_sides: int
    mean_absolute_probability_difference: Finite | None
    largest_disagreements: tuple[tuple[str, Finite], ...]
    bootstrap: FinalBootstrap


def summarize_final(
    protocol: FinalProtocol,
    pairs: tuple[FinalPair, ...],
    dispositions: tuple[FinalDisposition, ...],
) -> FinalSummary:
    expected = tuple(s.observation_id for s in protocol.population.slots)
    lookup = {p.observation_id: p for p in pairs}
    if (
        tuple(d.observation_id for d in dispositions) != expected
        or tuple(p.observation_id for p in pairs)
        != tuple(d.observation_id for d in dispositions if d.paired)
        or len(lookup) != len(pairs)
    ):
        raise ValueError("FINAL_POPULATION_MISMATCH")
    grid = tuple(
        None
        if not d.paired
        else (
            lookup[d.observation_id].brier_difference,
            lookup[d.observation_id].logloss_difference,
        )
        for d in dispositions
    )
    n = len(pairs)
    return FinalSummary(
        candidate=len(dispositions),
        logistic_available=sum(d.logistic_available for d in dispositions),
        baserate_available=sum(d.baserate_available for d in dispositions),
        truth_available=sum(d.truth_available for d in dispositions),
        paired_eligible=sum(d.paired for d in dispositions),
        paired_evaluated=n,
        exclusions=tuple(
            sorted(Counter(d.primary_reason for d in dispositions if not d.paired).items())
        ),
        exclusion_facets=tuple(sorted(Counter(f for d in dispositions for f in d.facets).items())),
        n=n,
        positive=sum(p.y for p in pairs),
        zero=sum(1 - p.y for p in pairs),
        prevalence=None if not n else sum(p.y for p in pairs) / n,
        coverage=n / len(dispositions),
        complete_blocks=sum(
            all(r is not None for r in grid[i : i + 5]) for i in range(0, len(grid) - 4, 5)
        ),
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
        bootstrap=FinalBootstrap.model_validate(bootstrap((grid,)).model_dump(exclude={"scope"})),
    )


def summary_evidence(summary: FinalSummary) -> FinalEvidence:
    s = summary
    return FinalEvidence(
        intended=s.candidate,
        paired=s.n,
        positive=s.positive,
        zero=s.zero,
        complete_blocks=s.complete_blocks,
        integrity_passed=True,
        replay_passed=True,
        methodology_valid=True,
        metrics_evaluable=s.baseline is not None and s.logistic is not None,
        intervals_estimable=s.bootstrap.status == "ESTIMATED",
        brier_interval=s.bootstrap.brier_interval,
        logloss_interval=s.bootstrap.logloss_interval,
    )


class FinalEvaluation(SealedResearch):
    evaluation_version: Literal["ff1.final_holdout.evaluation/1.0"] = (
        "ff1.final_holdout.evaluation/1.0"
    )
    protocol: FinalProtocol
    execution_fingerprint: Sha256
    opening_fingerprint: Sha256
    holdout_consumed_at: ForecastDateTime
    source_fingerprint: Sha256
    ground_truth_fingerprint: Sha256
    paired_population_fingerprint: Sha256
    forecast_population_fingerprint: Sha256
    summary: FinalSummary
    decision: FinalDecision
    one_shot_consumed: Literal[True] = True
    executions_used: Literal[1] = 1
    post_holdout_refit_allowed: Literal[False] = False
    automatic_promotion: Literal[False] = False
    holdout_status: Literal["CONSUMED"] = "CONSUMED"
    final_evidence: Literal["COMPLETE"] = "COMPLETE"
    created_at: ForecastDateTime

    @model_validator(mode="after")
    def fixed_decision(self) -> Self:
        if (
            self.decision != final_decision(summary_evidence(self.summary))
            or self.created_at < self.holdout_consumed_at
        ):
            raise ValueError("FINAL_DECISION_OR_CLOCK_MISMATCH")
        return self


class FinalTable(SealedResearch):
    """Human-readable JSON table and complete original-grid exclusion ledger."""

    pairs: tuple[FinalPair, ...] = Field(max_length=4096)
    dispositions: tuple[FinalDisposition, ...] = Field(min_length=5, max_length=4096)

    @property
    def population_fingerprint(self) -> str:
        return semantic_fingerprint(
            tuple((p.common_request_fingerprint, p.ground_truth_fingerprint) for p in self.pairs)
        )
