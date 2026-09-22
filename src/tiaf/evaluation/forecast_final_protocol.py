"""Pre-open FF-1 protocol and exhaustive decision rules; no outcome loader/scorer.

FinalEvidence is a future aggregate (synthetic in this review), not permission
to read data. Invalid/failed computations must not masquerade as scientific loss.
"""

from datetime import date
from typing import Annotated, Literal, Self

from pydantic import Field, StrictBool, StrictInt, model_validator

from tiaf.forecasting.identity import ForecastDateTime
from tiaf.forecasting.research_contracts import ResearchContract, ResearchDate
from tiaf.learning.forecast_artifacts import FIFTH_CUTOFF, Finite, SealedResearch
from tiaf.planner.models import Sha256


class FinalSlot(ResearchContract):
    observation_id: str
    reference_date: ResearchDate
    target_date: ResearchDate | None

    @model_validator(mode="after")
    def scope(self) -> Self:
        if (
            self.reference_date.year != 2025
            or self.observation_id != f"ff1-adjusted:RELIANCE:{self.reference_date.isoformat()}"
            or (self.target_date is not None and self.target_date <= self.reference_date)
        ):
            raise ValueError("FINAL_REFERENCE_SCOPE")
        return self


class FinalPopulation(SealedResearch):
    """Non-outcome grid; missing slots stay in the denominator and bootstrap mask."""

    qualification_blob: Sha256
    qualification_fingerprint: Sha256
    context_fingerprint: Sha256
    slots: tuple[FinalSlot, ...] = Field(min_length=1, max_length=4096)
    reference_start: ResearchDate = date(2025, 1, 1)
    reference_end: ResearchDate = date(2025, 12, 31)
    target_rule: Literal["NEXT_QUALIFIED_SESSION_INCLUDING_TERMINAL_2026"] = (
        "NEXT_QUALIFIED_SESSION_INCLUDING_TERMINAL_2026"
    )
    excluded_reference_rule: Literal["NO_2024_OR_2026_REFERENCES"] = "NO_2024_OR_2026_REFERENCES"
    missing_target_rule: Literal["UNAVAILABLE_KEEP_GRID_NO_SUBSTITUTION"] = (
        "UNAVAILABLE_KEEP_GRID_NO_SUBSTITUTION"
    )
    feature_rule: Literal["SAME_A2_FIVE_FINITE_AVAILABLE_21_CAUSAL_BARS_NO_IMPUTATION"] = (
        "SAME_A2_FIVE_FINITE_AVAILABLE_21_CAUSAL_BARS_NO_IMPUTATION"
    )
    qualification_rule: Literal["PINNED_FF1_1A_RULES_ONLY_REMOVE_SEAL_AFTER_CONSUMPTION"] = (
        "PINNED_FF1_1A_RULES_ONLY_REMOVE_SEAL_AFTER_CONSUMPTION"
    )
    feature_input_rule: Literal["HASH_ACTUAL_CAUSAL_BARS_NOT_REDACTED_PLACEHOLDERS"] = (
        "HASH_ACTUAL_CAUSAL_BARS_NOT_REDACTED_PLACEHOLDERS"
    )
    truth_rule: Literal["EVALUATION_OWNED_PINNED_SOURCE_ENDPOINT_DIRECTION_REVISION_0"] = (
        "EVALUATION_OWNED_PINNED_SOURCE_ENDPOINT_DIRECTION_REVISION_0"
    )
    truth_clock_rule: Literal["ACTUAL_EXECUTION_AS_KNOWN_SEPARATE_FROM_SIMULATED_ORIGIN"] = (
        "ACTUAL_EXECUTION_AS_KNOWN_SEPARATE_FROM_SIMULATED_ORIGIN"
    )
    pair_key: tuple[str, ...] = (
        "experiment",
        "fold",
        "observation_id",
        "subject",
        "target_version",
        "reference_date",
        "target_date",
        "session_window",
        "basis_unit",
        "information_cutoff",
        "simulation_as_of",
        "realization_mode",
        "feature_input_fingerprint",
        "qualification",
        "dataset",
        "profile",
        "label_policy",
        "truth_revision_fingerprint",
        "evaluation_as_known",
        "weighting",
    )
    disposition_precedence: tuple[str, ...] = (
        "SCOPE",
        "IDENTITY_PIT_BASIS_SESSION_ACTIONS",
        "FORECAST_ABSENCE_FAILURE",
        "TRUTH_ABSENCE",
        "METRIC_APPLICABILITY",
        "INCLUDED",
    )
    mismatch_rule: Literal["FAIL_INTEGRITY_NEVER_SILENTLY_EXCLUDE"] = (
        "FAIL_INTEGRITY_NEVER_SILENTLY_EXCLUDE"
    )
    weighting: Literal["UNIFORM_UNIQUE_PAIRED_OBSERVATIONS"] = "UNIFORM_UNIQUE_PAIRED_OBSERVATIONS"

    @model_validator(mode="after")
    def exact_grid(self) -> Self:
        dates = tuple(s.reference_date for s in self.slots)
        if (
            dates != tuple(sorted(set(dates)))
            or self.reference_start != date(2025, 1, 1)
            or self.reference_end != date(2025, 12, 31)
            or self.pair_key != type(self).model_fields["pair_key"].default
            or self.disposition_precedence
            != type(self).model_fields["disposition_precedence"].default
        ):
            raise ValueError("FINAL_POPULATION_RULE_CHANGED")
        return self


class FinalPolicy(SealedResearch):
    policy_version: Literal["ff1.final_holdout.decision/1.0"] = "ff1.final_holdout.decision/1.0"
    primary_metrics: tuple[Literal["BRIER"], Literal["NATURAL_LOG_LOSS"]] = (
        "BRIER",
        "NATURAL_LOG_LOSS",
    )
    loss_difference: Literal["LOGISTIC_MINUS_BASERATE"] = "LOGISTIC_MINUS_BASERATE"
    epsilon: Literal["1e-15_METRIC_ONLY"] = "1e-15_METRIC_ONLY"
    secondary_diagnostics: tuple[str, ...] = (
        "ACCURACY_P_GE_0.5_TIES_POSITIVE",
        "CONFUSION",
        "MEAN_PROBABILITY",
        "COVERAGE",
        "10_FIXED_WIDTH_RELIABILITY_BINS_LAST_CLOSED_MIN20",
        "PROBABILITY_DISAGREEMENT",
        "FIXED_0.5_SAME_PAIRS",
        "ENDPOINT_AND_CLIPPED_COUNTS",
    )
    bootstrap: Literal["PAIRED_NONCIRCULAR_MOVING_BLOCK_ORIGINAL_GRID_AND_MASK"] = (
        "PAIRED_NONCIRCULAR_MOVING_BLOCK_ORIGINAL_GRID_AND_MASK"
    )
    block_length: Literal[5] = 5
    replicates: Literal[5000] = 5000
    seed: Literal[1729] = 1729
    generator: Literal["numpy.Generator(PCG64)/2.3.3"] = "numpy.Generator(PCG64)/2.3.3"
    ordering: Literal["REFERENCE_SESSION_ASC_FRESH_SEED_REPLICATE_MAJOR"] = (
        "REFERENCE_SESSION_ASC_FRESH_SEED_REPLICATE_MAJOR"
    )
    terminal_blocks: Literal["UNIFORM_STARTS_0_TO_T_MINUS_5_CONCATENATE_TRUNCATE_TO_T"] = (
        "UNIFORM_STARTS_0_TO_T_MINUS_5_CONCATENATE_TRUNCATE_TO_T"
    )
    zero_pair_replicate: Literal["NOT_ESTIMABLE_NO_REDRAW"] = "NOT_ESTIMABLE_NO_REDRAW"
    confidence: Literal["0.975_TWO_SIDED_PERCENTILE"] = "0.975_TWO_SIDED_PERCENTILE"
    quantiles: tuple[Literal["0.0125"], Literal["0.9875"]] = ("0.0125", "0.9875")
    quantile_method: Literal["linear"] = "linear"
    multiplicity: Literal["NOMINAL_BONFERRONI_95_FAMILYWISE_CONDITIONAL_APPROXIMATION"] = (
        "NOMINAL_BONFERRONI_95_FAMILYWISE_CONDITIONAL_APPROXIMATION"
    )
    minimum_pairs: Literal[200] = 200
    minimum_class: Literal[40] = 40
    minimum_coverage: Literal["0.8"] = "0.8"
    minimum_complete_blocks: Literal[20] = 20
    complete_block_rule: Literal["NONOVERLAPPING_FROM_FIRST_GRID_SLOT_DROP_SHORT_TAIL"] = (
        "NONOVERLAPPING_FROM_FIRST_GRID_SLOT_DROP_SHORT_TAIL"
    )
    support_rule: Literal["ADEQUATE_AND_BRIER_UPPER_LT_0_AND_LOGLOSS_UPPER_LE_0.01"] = (
        "ADEQUATE_AND_BRIER_UPPER_LT_0_AND_LOGLOSS_UPPER_LE_0.01"
    )
    rejection_rule: Literal["ADEQUATE_AND_BRIER_LOWER_GE_0_OR_LOGLOSS_LOWER_GT_0.01"] = (
        "ADEQUATE_AND_BRIER_LOWER_GE_0_OR_LOGLOSS_LOWER_GT_0.01"
    )
    precedence: Literal["INADEQUATE_THEN_SUPPORTED_THEN_REJECTED_ELSE_INCONCLUSIVE"] = (
        "INADEQUATE_THEN_SUPPORTED_THEN_REJECTED_ELSE_INCONCLUSIVE"
    )
    dependency_assumptions: Literal["INHERITED_APPROXIMATION_NO_POSTHOC_DIAGNOSTIC_VETO"] = (
        "INHERITED_APPROXIMATION_NO_POSTHOC_DIAGNOSTIC_VETO"
    )
    executions_allowed: Literal[1] = 1
    post_holdout_refit_allowed: Literal[False] = False
    mutation_after_freeze: Literal["FORBIDDEN_NEW_EXPERIMENT_AND_INDEPENDENT_HOLDOUT"] = (
        "FORBIDDEN_NEW_EXPERIMENT_AND_INDEPENDENT_HOLDOUT"
    )
    failure_rule: Literal["ATTEMPT_CONSUMED_FAILED_NO_SCIENTIFIC_VERDICT_NO_RETRY"] = (
        "ATTEMPT_CONSUMED_FAILED_NO_SCIENTIFIC_VERDICT_NO_RETRY"
    )
    replay_rule: Literal["READ_ONLY_CAPTURED_CLOSURE_NO_NEW_SOURCE_INFERENCE_SELECTION"] = (
        "READ_ONLY_CAPTURED_CLOSURE_NO_NEW_SOURCE_INFERENCE_SELECTION"
    )
    promotion_rule: Literal["NONE_CHALLENGER_EXPERIMENTAL_BENCHMARK_UNCHANGED"] = (
        "NONE_CHALLENGER_EXPERIMENTAL_BENCHMARK_UNCHANGED"
    )
    supported_next: Literal["CLOSE_SUPPORTED_INDEPENDENT_CLOSURE_PROMOTION_SEPARATE"] = (
        "CLOSE_SUPPORTED_INDEPENDENT_CLOSURE_PROMOTION_SEPARATE"
    )
    rejected_next: Literal["RETAIN_BASERATE_CLOSE_V1_NEW_EXPERIMENT_FOR_REVISION"] = (
        "RETAIN_BASERATE_CLOSE_V1_NEW_EXPERIMENT_FOR_REVISION"
    )
    insufficient_next: Literal["PRESERVE_UNCERTAINTY_NO_RECYCLE_FUTURE_EVIDENCE_SEPARATE"] = (
        "PRESERVE_UNCERTAINTY_NO_RECYCLE_FUTURE_EVIDENCE_SEPARATE"
    )
    maximum_grid: Literal[4096] = 4096
    evaluation_timeout_seconds: Literal[120] = 120
    campaign_timeout_seconds: Literal[600] = 600
    forecast_attempts_per_arm_per_slot: Literal[1] = 1
    inference_tolerance: Literal["1e-12"] = "1e-12"

    @model_validator(mode="after")
    def fixed_diagnostics(self) -> Self:
        if self.secondary_diagnostics != type(self).model_fields["secondary_diagnostics"].default:
            raise ValueError("FINAL_DIAGNOSTIC_POLICY_CHANGED")
        return self


class FinalProtocol(SealedResearch):
    protocol_version: Literal["ff1.final_holdout.protocol/1.0"] = "ff1.final_holdout.protocol/1.0"
    experiment_id: Literal["ff1.reliance.daily_logistic_vs_b0/1.0"] = (
        "ff1.reliance.daily_logistic_vs_b0/1.0"
    )
    subject: Literal["RELIANCE:NSE:NSE_EQUITY:EQUITY"] = "RELIANCE:NSE:NSE_EQUITY:EQUITY"
    target_id: Literal["equity.next_session_close.return_gt_zero/1.0"] = (
        "equity.next_session_close.return_gt_zero/1.0"
    )
    mode: Literal["SIMULATED_RESEARCH"] = "SIMULATED_RESEARCH"
    price_basis: Literal["CORPORATE_ACTION_ADJUSTED"] = "CORPORATE_ACTION_ADJUSTED"
    development_evaluation_fingerprint: Sha256
    development_ledger_fingerprint: Sha256
    fifth_cutoff: ForecastDateTime = FIFTH_CUTOFF
    fifth_handoff_fingerprint: Sha256
    scaler_fingerprint: Sha256
    model_fingerprint: Sha256
    training_population_fingerprint: Sha256
    authority_fingerprint: Sha256
    baserate_state_fingerprint: Sha256
    baserate_positive: Literal[8] = 8
    baserate_support: Literal[20] = 20
    baserate_rule: Literal["FOLD_FROZEN_LAST_20_SCHEDULED_UNSMOOTHED_NO_BACKFILL_MIN20"] = (
        "FOLD_FROZEN_LAST_20_SCHEDULED_UNSMOOTHED_NO_BACKFILL_MIN20"
    )
    qualification_fingerprint: Sha256
    qualification_blob: Sha256
    dataset_fingerprint: Sha256
    research_profile_fingerprint: Sha256
    feature_schema_fingerprint: Sha256
    dependency_lock_fingerprint: Sha256
    plan_document_fingerprint: Sha256
    review_document_fingerprint: Sha256
    provisioning_review_fingerprint: Sha256
    # Source files pin exact qualification/features/truth and decision arithmetic,
    # not a future runner that has not yet been implemented/reviewed.
    source_pins: tuple[tuple[str, Sha256], ...] = Field(min_length=1)
    population: FinalPopulation
    policy: FinalPolicy = Field(default_factory=FinalPolicy)
    authorized: StrictBool
    holdout_status_at_freeze: Literal["SEALED"] = "SEALED"
    final_evidence_at_freeze: Literal["NOT_RUN"] = "NOT_RUN"
    protected_outcome_access: Literal["NONE"] = "NONE"
    created_at: ForecastDateTime

    @model_validator(mode="after")
    def consistent(self) -> Self:
        paths = tuple(p for p, _ in self.source_pins)
        if (
            self.fifth_cutoff != FIFTH_CUTOFF
            or self.created_at <= self.fifth_cutoff
            or self.population.qualification_fingerprint != self.qualification_fingerprint
            or self.population.qualification_blob != self.qualification_blob
            or paths != tuple(sorted(set(paths)))
            or any(p.startswith("/") or ".." in p.split("/") for p in paths)
        ):
            raise ValueError("FINAL_PROTOCOL_LINEAGE_OR_CUTOFF")
        return self


Count = Annotated[StrictInt, Field(ge=0, le=4096)]


class FinalEvidence(ResearchContract):
    """Future summary only; no such empirical object is constructed during freeze."""

    intended: Count
    paired: Count
    positive: Count
    zero: Count
    complete_blocks: Count
    integrity_passed: StrictBool
    replay_passed: StrictBool
    methodology_valid: StrictBool
    metrics_evaluable: StrictBool
    intervals_estimable: StrictBool
    brier_interval: tuple[Finite, Finite] | None
    logloss_interval: tuple[Finite, Finite] | None

    @model_validator(mode="after")
    def valid(self) -> Self:
        if (
            self.paired != self.positive + self.zero
            or self.paired > self.intended
            or self.complete_blocks > min(self.intended // 5, self.paired // 5)
            or any(
                i is not None and i[0] > i[1] for i in (self.brier_interval, self.logloss_interval)
            )
            or self.intervals_estimable
            != (self.brier_interval is not None and self.logloss_interval is not None)
        ):
            raise ValueError("INVALID_FINAL_EVIDENCE_SUMMARY")
        return self


class FinalDecision(ResearchContract):
    classification: Literal["LOGISTIC_SUPPORTED", "LOGISTIC_NOT_SUPPORTED", "INSUFFICIENT_EVIDENCE"]
    reasons: tuple[str, ...]
    automatic_promotion: Literal[False] = False
    logistic_role: Literal["CHALLENGER_EXPERIMENTAL"] = "CHALLENGER_EXPERIMENTAL"
    baserate_role: Literal["BENCHMARK"] = "BENCHMARK"


def final_decision(evidence: FinalEvidence) -> FinalDecision:
    """Total on valid summaries; inadequate > supported > decisive rejection > uncertain."""
    e = FinalEvidence.model_validate(evidence.model_dump())
    failures = tuple(
        name
        for name, passed in (
            ("INTEGRITY", e.integrity_passed),
            ("REPLAY", e.replay_passed),
            ("METHODOLOGY", e.methodology_valid),
            ("METRICS", e.metrics_evaluable),
            ("INTERVALS", e.intervals_estimable),
            ("PAIRED_N", e.paired >= 200),
            ("CLASS_SUPPORT", min(e.positive, e.zero) >= 40),
            ("COVERAGE", e.intended > 0 and 5 * e.paired >= 4 * e.intended),
            ("COMPLETE_BLOCKS", e.complete_blocks >= 20),
        )
        if not passed
    )
    if failures:
        return FinalDecision(classification="INSUFFICIENT_EVIDENCE", reasons=failures)
    assert e.brier_interval is not None and e.logloss_interval is not None
    if e.brier_interval[1] < 0 and e.logloss_interval[1] <= 0.01:
        return FinalDecision(classification="LOGISTIC_SUPPORTED", reasons=("BOTH_FINAL_BOUNDS",))
    rejected = tuple(
        name
        for name, failed in (
            ("BRIER_LOWER_GE_ZERO", e.brier_interval[0] >= 0),
            ("LOGLOSS_LOWER_GT_0.01", e.logloss_interval[0] > 0.01),
        )
        if failed
    )
    return FinalDecision(
        classification="LOGISTIC_NOT_SUPPORTED" if rejected else "INSUFFICIENT_EVIDENCE",
        reasons=rejected or ("CONFIDENCE_NONDECISIVE",),
    )
