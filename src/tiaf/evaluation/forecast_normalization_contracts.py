"""FLC-6 immutable contracts for Evaluation-owned normalized evidence.

These contracts describe evaluation inputs and evidence.  They grant no training,
selection, calibration, diagnostic, approval, promotion, or activation authority.
"""

from collections import Counter
from typing import Annotated, Literal, Self

from pydantic import Field, StrictBool, StrictInt, model_validator

from tiaf.forecasting.enums import ForecastRealizationMode, PopulationDisposition
from tiaf.forecasting.forecaster_seams import ForecasterKey
from tiaf.forecasting.identity import (
    ArtifactReference,
    ForecastDateTime,
    LogicalId,
    semantic_fingerprint,
)
from tiaf.learning.forecast_artifacts import Finite, SealedResearch
from tiaf.planner.models import Sha256

Probability = Annotated[Finite, Field(ge=0.0, le=1.0)]
Count = Annotated[StrictInt, Field(ge=0)]


def synthetic_reference(name: str) -> ArtifactReference:
    """Stable FLC-6 engineering pin; it is not an empirical evidence claim."""
    return ArtifactReference(
        artifact_id=f"flc6:{name}",
        artifact_version="flc6.synthetic.1",
        fingerprint=semantic_fingerprint(("flc6.synthetic.1", name)),
    )


class EvaluationTargetIdentity(SealedResearch):
    target_id: LogicalId
    target_version: str = Field(min_length=1, max_length=40)
    horizon: LogicalId
    event: LogicalId
    cutoff_policy: ArtifactReference
    output_semantics: Literal["BINARY_PROBABILITY"] = "BINARY_PROBABILITY"
    label_semantics: Literal["BINARY_ZERO_ONE"] = "BINARY_ZERO_ONE"


class GroundTruthIdentity(SealedResearch):
    authority_id: LogicalId
    journal_ref: ArtifactReference
    target: EvaluationTargetIdentity
    label_version: str = Field(min_length=1, max_length=40)
    resolution_policy: ArtifactReference
    ownership: Literal["EXTERNAL_EVALUATION_OUTCOME_JOURNAL"] = (
        "EXTERNAL_EVALUATION_OUTCOME_JOURNAL"
    )


class EvaluationPopulation(SealedResearch):
    population_id: LogicalId
    population_version: str = Field(min_length=1, max_length=40)
    subject: LogicalId
    universe: tuple[LogicalId, ...] = Field(min_length=1, max_length=64)
    window_start: ForecastDateTime
    window_end: ForecastDateTime
    observation_ids: tuple[LogicalId, ...] = Field(min_length=1, max_length=4096)
    eligibility_rule: ArtifactReference
    exclusion_rule: ArtifactReference
    split_ref: ArtifactReference
    protection_state: Literal["SYNTHETIC_REFERENCE", "DEVELOPMENT_KNOWN", "CONSUMED_HISTORICAL"]
    coverage_policy: Literal["FULL_DENOMINATOR_RETAIN_ABSENCE"] = "FULL_DENOMINATOR_RETAIN_ABSENCE"
    complete: StrictBool

    @model_validator(mode="after")
    def population_closure(self) -> Self:
        if self.window_start >= self.window_end:
            raise ValueError("EVALUATION_POPULATION_WINDOW_INVALID")
        if len(self.observation_ids) != len(set(self.observation_ids)):
            raise ValueError("EVALUATION_POPULATION_DUPLICATE_OBSERVATION")
        if len(self.universe) != len(set(self.universe)):
            raise ValueError("EVALUATION_POPULATION_DUPLICATE_UNIVERSE_MEMBER")
        return self


class EvidenceUseDeclaration(SealedResearch):
    evidence_ref: ArtifactReference
    source_experiment_id: LogicalId
    requesting_experiment_id: LogicalId
    source_state: Literal["SYNTHETIC_REFERENCE", "CONSUMED_HISTORICAL"]
    use_classification: Literal[
        "SYNTHETIC_REFERENCE", "HISTORICAL_REPLAY_ONLY", "DEVELOPMENT_KNOWN"
    ]
    unseen_claim: Literal[False] = False
    protected_claim: Literal[False] = False
    evaluation_execution_authorized: StrictBool

    @model_validator(mode="after")
    def evidence_boundary(self) -> Self:
        if self.source_state == "SYNTHETIC_REFERENCE":
            if (
                self.use_classification != "SYNTHETIC_REFERENCE"
                or not self.evaluation_execution_authorized
            ):
                raise ValueError("SYNTHETIC_REFERENCE_EVALUATION_DECLARATION_INVALID")
            return self
        expected = (
            "HISTORICAL_REPLAY_ONLY"
            if self.source_experiment_id == self.requesting_experiment_id
            else "DEVELOPMENT_KNOWN"
        )
        if self.use_classification != expected or self.evaluation_execution_authorized:
            raise ValueError("CONSUMED_EVIDENCE_CANNOT_AUTHORIZE_NEW_EVALUATION")
        return self


class EvaluationParticipant(SealedResearch):
    participant_id: LogicalId
    form: Literal[
        "PRIMITIVE_FORECASTER",
        "ARTIFACT_BACKED_FORECASTER",
        "CALIBRATED_COMPOSITION",
        "FUTURE_COMPOSITE",
    ]
    report_role: Literal["BENCHMARK", "CHALLENGER", "SUBJECT"]
    forecast_or_composition: ArtifactReference
    forecaster: ForecasterKey | None = None
    target: EvaluationTargetIdentity
    population_fingerprint: Sha256
    realization_mode: ForecastRealizationMode
    cutoff_policy: ArtifactReference
    output_semantics: Literal["BINARY_PROBABILITY"] = "BINARY_PROBABILITY"


class PairingIdentity(SealedResearch):
    comparison_id: LogicalId
    comparison_version: str = Field(min_length=1, max_length=40)
    mode: Literal["SINGLE_PARTICIPANT", "PAIRED_COMPARISON"]
    participant_ids: tuple[LogicalId, ...] = Field(min_length=1, max_length=2)
    join_rule: Literal["EXACT_OBSERVATION_ID"] = "EXACT_OBSERVATION_ID"
    missing_policy: Literal["EXPLICIT_EXCLUSION_RETAIN_DENOMINATOR"] = (
        "EXPLICIT_EXCLUSION_RETAIN_DENOMINATOR"
    )
    difference_direction: Literal["SECOND_MINUS_FIRST"] = "SECOND_MINUS_FIRST"

    @model_validator(mode="after")
    def cardinality(self) -> Self:
        expected = 1 if self.mode == "SINGLE_PARTICIPANT" else 2
        if len(self.participant_ids) != expected or len(set(self.participant_ids)) != expected:
            raise ValueError("EVALUATION_PAIRING_CARDINALITY_MISMATCH")
        return self


class MetricDefinition(SealedResearch):
    metric_id: Literal["BRIER", "NATURAL_LOG_LOSS", "ACCURACY", "ECE_FIXED_10"]
    metric_version: Literal["1.0"] = "1.0"
    tier: Literal["PRIMARY", "SECONDARY_DESCRIPTIVE", "DIAGNOSTIC_ONLY"]
    direction: Literal["LOWER_IS_BETTER", "HIGHER_IS_BETTER", "DESCRIPTIVE_ONLY"]
    denominator: Literal["EVALUATED_OBSERVATIONS"] = "EVALUATED_OBSERVATIONS"
    numeric_policy: ArtifactReference


class MetricSetIdentity(SealedResearch):
    metric_set_id: LogicalId
    metric_set_version: str = Field(min_length=1, max_length=40)
    metrics: tuple[MetricDefinition, ...] = Field(min_length=1, max_length=16)
    weighting: Literal["UNIFORM_UNIQUE_OBSERVATIONS"] = "UNIFORM_UNIQUE_OBSERVATIONS"

    @model_validator(mode="after")
    def unique_metrics(self) -> Self:
        ids = tuple(metric.metric_id for metric in self.metrics)
        if len(ids) != len(set(ids)):
            raise ValueError("EVALUATION_METRIC_ID_DUPLICATE")
        if not any(metric.tier == "PRIMARY" for metric in self.metrics):
            raise ValueError("EVALUATION_PRIMARY_METRIC_REQUIRED")
        return self


class StatisticalPolicy(SealedResearch):
    policy_id: LogicalId
    policy_version: str = Field(min_length=1, max_length=40)
    method: Literal["PAIRED_NONCIRCULAR_MOVING_BLOCK"] = "PAIRED_NONCIRCULAR_MOVING_BLOCK"
    paired: Literal[True] = True
    block_length: Literal[5] = 5
    replicate_count: Literal[5000] = 5000
    seed: Literal[1729] = 1729
    confidence_level: Literal["0.975_TWO_SIDED_PERCENTILE"] = "0.975_TWO_SIDED_PERCENTILE"
    quantiles: tuple[Literal["0.0125"], Literal["0.9875"]] = ("0.0125", "0.9875")
    minimum_support: Annotated[StrictInt, Field(ge=1, le=4096)]
    ordering_policy: Literal["POPULATION_OBSERVATION_ORDER"] = "POPULATION_OBSERVATION_ORDER"
    terminal_block_policy: Literal["NONCIRCULAR_CONCATENATE_TRUNCATE"] = (
        "NONCIRCULAR_CONCATENATE_TRUNCATE"
    )
    zero_pair_policy: Literal["NOT_ESTIMABLE_NO_REDRAW"] = "NOT_ESTIMABLE_NO_REDRAW"


class EvaluationIdentity(SealedResearch):
    evaluation_id: LogicalId
    evaluation_version: str = Field(min_length=1, max_length=40)
    subject: LogicalId
    universe: tuple[LogicalId, ...] = Field(min_length=1, max_length=64)
    target: EvaluationTargetIdentity
    realization_mode: ForecastRealizationMode
    population_fingerprint: Sha256
    split_ref: ArtifactReference
    ground_truth_fingerprint: Sha256
    metric_set_fingerprint: Sha256
    comparison_fingerprint: Sha256
    statistical_policy_fingerprint: Sha256
    policy_ref: ArtifactReference
    created_at: ForecastDateTime


class EvaluationRequest(SealedResearch):
    request_id: LogicalId
    identity: EvaluationIdentity
    participants: tuple[EvaluationParticipant, ...] = Field(min_length=1, max_length=2)
    population: EvaluationPopulation
    ground_truth: GroundTruthIdentity
    pairing: PairingIdentity
    metric_set: MetricSetIdentity
    statistics: StatisticalPolicy
    evidence_use: EvidenceUseDeclaration
    decision_policy_ref: ArtifactReference
    created_at: ForecastDateTime
    scope: Literal["INTERNAL_SYNTHETIC_RESEARCH"] = "INTERNAL_SYNTHETIC_RESEARCH"
    trains_models: Literal[False] = False
    selects_optimizer_candidate: Literal[False] = False
    fits_or_applies_calibration: Literal[False] = False
    runs_diagnostics: Literal[False] = False
    grants_approval: Literal[False] = False
    grants_promotion: Literal[False] = False
    grants_activation: Literal[False] = False

    @model_validator(mode="after")
    def exact_request(self) -> Self:
        population_fp = str(self.population.fingerprint)
        truth_fp = str(self.ground_truth.fingerprint)
        metric_fp = str(self.metric_set.fingerprint)
        pairing_fp = str(self.pairing.fingerprint)
        statistics_fp = str(self.statistics.fingerprint)
        participant_ids = tuple(participant.participant_id for participant in self.participants)
        if (
            not self.population.complete
            or self.population.protection_state != "SYNTHETIC_REFERENCE"
            or not self.evidence_use.evaluation_execution_authorized
            or participant_ids != self.pairing.participant_ids
            or len(participant_ids) != len(set(participant_ids))
            or self.identity.subject != self.population.subject
            or self.identity.universe != self.population.universe
            or self.identity.population_fingerprint != population_fp
            or self.identity.split_ref != self.population.split_ref
            or self.identity.ground_truth_fingerprint != truth_fp
            or self.identity.metric_set_fingerprint != metric_fp
            or self.identity.comparison_fingerprint != pairing_fp
            or self.identity.statistical_policy_fingerprint != statistics_fp
            or self.identity.target != self.ground_truth.target
            or self.created_at < self.identity.created_at
        ):
            raise ValueError("EVALUATION_REQUEST_IDENTITY_MISMATCH")
        if any(
            participant.target != self.identity.target
            or participant.population_fingerprint != population_fp
            or participant.realization_mode != self.identity.realization_mode
            or participant.cutoff_policy != self.identity.target.cutoff_policy
            for participant in self.participants
        ):
            raise ValueError("EVALUATION_PARTICIPANT_INCOMPATIBLE")
        return self


class ForecastObservation(SealedResearch):
    observation_id: LogicalId
    participant_id: LogicalId
    forecast_ref: ArtifactReference | None
    probability: Probability | None
    status: Literal["AVAILABLE", "MISSING", "FAILED", "UNSUPPORTED"]
    reason: LogicalId

    @model_validator(mode="after")
    def availability(self) -> Self:
        available = self.status == "AVAILABLE"
        if available != (self.forecast_ref is not None and self.probability is not None):
            raise ValueError("EVALUATION_FORECAST_AVAILABILITY_MISMATCH")
        if not available and (self.forecast_ref is not None or self.probability is not None):
            raise ValueError("EVALUATION_ABSENT_FORECAST_HAS_VALUE")
        return self


class ParticipantForecastSet(SealedResearch):
    participant: EvaluationParticipant
    population_fingerprint: Sha256
    observations: tuple[ForecastObservation, ...] = Field(min_length=1, max_length=4096)

    @model_validator(mode="after")
    def exact_participant(self) -> Self:
        ids = tuple(row.observation_id for row in self.observations)
        if (
            len(ids) != len(set(ids))
            or any(
                row.participant_id != self.participant.participant_id for row in self.observations
            )
            or self.population_fingerprint != self.participant.population_fingerprint
        ):
            raise ValueError("EVALUATION_FORECAST_SET_IDENTITY_MISMATCH")
        return self


class GroundTruthObservation(SealedResearch):
    observation_id: LogicalId
    journal_entry_ref: ArtifactReference | None
    label: Annotated[StrictInt, Field(ge=0, le=1)] | None
    status: Literal["AVAILABLE", "MISSING", "INELIGIBLE", "AMBIGUOUS"]
    reason: LogicalId

    @model_validator(mode="after")
    def availability(self) -> Self:
        available = self.status == "AVAILABLE"
        if available != (self.journal_entry_ref is not None and self.label is not None):
            raise ValueError("EVALUATION_TRUTH_AVAILABILITY_MISMATCH")
        if not available and (self.journal_entry_ref is not None or self.label is not None):
            raise ValueError("EVALUATION_ABSENT_TRUTH_HAS_LABEL")
        return self


class GroundTruthSet(SealedResearch):
    identity: GroundTruthIdentity
    population_fingerprint: Sha256
    observations: tuple[GroundTruthObservation, ...] = Field(min_length=1, max_length=4096)
    labels_supplied_externally: Literal[True] = True

    @model_validator(mode="after")
    def unique_truth(self) -> Self:
        ids = tuple(row.observation_id for row in self.observations)
        if len(ids) != len(set(ids)):
            raise ValueError("EVALUATION_TRUTH_DUPLICATE_OBSERVATION")
        return self


class EvaluationInput(SealedResearch):
    request: EvaluationRequest
    forecast_sets: tuple[ParticipantForecastSet, ...] = Field(min_length=1, max_length=2)
    ground_truth: GroundTruthSet
    captured_at: ForecastDateTime
    data_scope: Literal["AUTHORED_SYNTHETIC_REFERENCE_ONLY"] = "AUTHORED_SYNTHETIC_REFERENCE_ONLY"

    @model_validator(mode="after")
    def complete_grid(self) -> Self:
        expected_ids = self.request.population.observation_ids
        participants = tuple(row.participant for row in self.forecast_sets)
        if (
            participants != self.request.participants
            or self.ground_truth.identity != self.request.ground_truth
            or self.ground_truth.population_fingerprint != self.request.population.fingerprint
            or tuple(row.observation_id for row in self.ground_truth.observations) != expected_ids
            or self.captured_at < self.request.created_at
        ):
            raise ValueError("EVALUATION_INPUT_CLOSURE_MISMATCH")
        if any(
            row.population_fingerprint != self.request.population.fingerprint
            or tuple(item.observation_id for item in row.observations) != expected_ids
            for row in self.forecast_sets
        ):
            raise ValueError("EVALUATION_INPUT_POPULATION_MISMATCH")
        return self


class KnownCount(SealedResearch):
    status: Literal["KNOWN", "UNKNOWN"]
    value: Count | None

    @model_validator(mode="after")
    def known_value(self) -> Self:
        if (self.status == "KNOWN") != (self.value is not None):
            raise ValueError("UNKNOWN_EVALUATION_COUNT_IS_NOT_ZERO")
        return self


class ParticipantAvailability(SealedResearch):
    participant_id: LogicalId
    available: KnownCount


class EvaluationDisposition(SealedResearch):
    observation_id: LogicalId
    available_participant_ids: tuple[LogicalId, ...]
    truth_available: StrictBool
    disposition: PopulationDisposition
    reasons: tuple[LogicalId, ...] = Field(min_length=1)


class CoverageAccounting(SealedResearch):
    requested: KnownCount
    participant_availability: tuple[ParticipantAvailability, ...] = Field(min_length=1)
    ground_truth_available: KnownCount
    paired_eligible: KnownCount
    evaluated: KnownCount
    protected_excluded: KnownCount
    consumed_excluded: KnownCount
    exclusions_by_reason: tuple[tuple[LogicalId, Count], ...]
    dispositions: tuple[EvaluationDisposition, ...] = Field(min_length=1, max_length=4096)
    coverage: Probability | None

    @model_validator(mode="after")
    def counts_match(self) -> Self:
        if any(
            count.status != "KNOWN"
            for count in (
                self.requested,
                self.ground_truth_available,
                self.paired_eligible,
                self.evaluated,
                self.protected_excluded,
                self.consumed_excluded,
            )
        ) or any(item.available.status != "KNOWN" for item in self.participant_availability):
            if self.coverage is not None:
                raise ValueError("UNKNOWN_DENOMINATOR_CANNOT_REPORT_COVERAGE")
            return self
        requested = self.requested.value
        evaluated = self.evaluated.value
        paired = self.paired_eligible.value
        truth = self.ground_truth_available.value
        protected = self.protected_excluded.value
        consumed = self.consumed_excluded.value
        assert None not in (requested, evaluated, paired, truth, protected, consumed)
        included = sum(
            row.disposition is PopulationDisposition.INCLUDED for row in self.dispositions
        )
        if (
            requested != len(self.dispositions)
            or evaluated != included
            or paired != included
            or evaluated > requested
            or truth != sum(row.truth_available for row in self.dispositions)
            or protected != 0
            or consumed != 0
        ):
            raise ValueError("EVALUATION_COVERAGE_COUNT_MISMATCH")
        availability = dict(
            (item.participant_id, item.available.value) for item in self.participant_availability
        )
        if len(availability) != len(self.participant_availability) or any(
            availability[participant_id]
            != sum(participant_id in row.available_participant_ids for row in self.dispositions)
            for participant_id in availability
        ):
            raise ValueError("EVALUATION_PARTICIPANT_AVAILABILITY_COUNT_MISMATCH")
        actual_reasons = Counter(
            reason
            for row in self.dispositions
            if row.disposition is not PopulationDisposition.INCLUDED
            for reason in row.reasons
        )
        if self.exclusions_by_reason != tuple(sorted(actual_reasons.items())):
            raise ValueError("EVALUATION_EXCLUSION_ACCOUNTING_MISMATCH")
        expected = evaluated / requested if requested else None
        if self.coverage != expected:
            raise ValueError("EVALUATION_COVERAGE_VALUE_MISMATCH")
        return self


class MetricValue(SealedResearch):
    participant_id: LogicalId
    metric_id: Literal["BRIER", "NATURAL_LOG_LOSS", "ACCURACY", "ECE_FIXED_10"]
    metric_version: str
    tier: Literal["PRIMARY", "SECONDARY_DESCRIPTIVE", "DIAGNOSTIC_ONLY"]
    status: Literal["COMPUTED", "UNDEFINED"]
    value: Finite | None
    evaluated_count: Count
    reason: LogicalId

    @model_validator(mode="after")
    def result_value(self) -> Self:
        if (self.status == "COMPUTED") != (self.value is not None):
            raise ValueError("EVALUATION_METRIC_STATUS_MISMATCH")
        return self


class MetricBundle(SealedResearch):
    metric_set: MetricSetIdentity
    values: tuple[MetricValue, ...]

    @model_validator(mode="after")
    def unique_grid(self) -> Self:
        keys = tuple((value.participant_id, value.metric_id) for value in self.values)
        if len(keys) != len(set(keys)):
            raise ValueError("EVALUATION_METRIC_RESULT_DUPLICATE")
        return self


class PairedLossObservation(SealedResearch):
    observation_id: LogicalId
    ground_truth_ref: ArtifactReference
    first_forecast_ref: ArtifactReference
    second_forecast_ref: ArtifactReference
    label: Literal[0, 1]
    first_probability: Probability
    second_probability: Probability
    first_brier: Finite
    second_brier: Finite
    brier_difference: Finite
    first_log_loss: Finite
    second_log_loss: Finite
    log_loss_difference: Finite

    @model_validator(mode="after")
    def exact_losses(self) -> Self:
        from tiaf.evaluation.forecast_comparison_metrics import losses

        first = losses(self.first_probability, self.label)
        second = losses(self.second_probability, self.label)
        if (
            self.first_brier,
            self.second_brier,
            self.brier_difference,
            self.first_log_loss,
            self.second_log_loss,
            self.log_loss_difference,
        ) != (
            first[0],
            second[0],
            second[0] - first[0],
            first[1],
            second[1],
            second[1] - first[1],
        ):
            raise ValueError("NORMALIZED_PAIRED_LOSS_MISMATCH")
        return self


class PairedTable(SealedResearch):
    pairing: PairingIdentity
    population_fingerprint: Sha256
    rows: tuple[PairedLossObservation, ...] = Field(max_length=4096)

    @model_validator(mode="after")
    def exact_pairing(self) -> Self:
        ids = tuple(row.observation_id for row in self.rows)
        if self.pairing.mode != "PAIRED_COMPARISON" or len(ids) != len(set(ids)):
            raise ValueError("NORMALIZED_PAIRED_TABLE_IDENTITY_MISMATCH")
        return self


class StatisticalSummary(SealedResearch):
    policy: StatisticalPolicy
    status: Literal["ESTIMATED", "NOT_ESTIMABLE", "NOT_APPLICABLE"]
    effective_n: Count
    brier_difference: Finite | None
    log_loss_difference: Finite | None
    brier_interval: tuple[Finite, Finite] | None
    log_loss_interval: tuple[Finite, Finite] | None
    sampled_indices_fingerprint: Sha256 | None
    interpretation: Literal["EVIDENCE_ONLY_NO_DECISION"] = "EVIDENCE_ONLY_NO_DECISION"

    @model_validator(mode="after")
    def status_shape(self) -> Self:
        if self.status == "ESTIMATED" and any(
            item is None
            for item in (
                self.brier_difference,
                self.log_loss_difference,
                self.brier_interval,
                self.log_loss_interval,
                self.sampled_indices_fingerprint,
            )
        ):
            raise ValueError("NORMALIZED_STATISTICAL_SUMMARY_STATUS_MISMATCH")
        if self.status == "NOT_ESTIMABLE" and (
            self.brier_interval is not None or self.log_loss_interval is not None
        ):
            raise ValueError("NORMALIZED_STATISTICAL_INTERVAL_NOT_ESTIMABLE")
        if self.status == "NOT_APPLICABLE" and any(
            item is not None
            for item in (
                self.brier_difference,
                self.log_loss_difference,
                self.brier_interval,
                self.log_loss_interval,
                self.sampled_indices_fingerprint,
            )
        ):
            raise ValueError("NORMALIZED_STATISTICAL_ABSENCE_HAS_VALUES")
        return self


class NormalizedEvaluationResult(SealedResearch):
    request: EvaluationRequest
    input_reference: ArtifactReference
    status: Literal["GENERATED", "INSUFFICIENT_SUPPORT"]
    population_fingerprint: Sha256
    ground_truth_fingerprint: Sha256
    coverage: CoverageAccounting
    metrics: MetricBundle
    paired_table: PairedTable | None
    statistics: StatisticalSummary
    limitations: tuple[LogicalId, ...]
    created_at: ForecastDateTime
    scientific_decision: Literal["NOT_OWNED_BY_EVALUATOR"] = "NOT_OWNED_BY_EVALUATOR"
    optimizer_selection: Literal[False] = False
    approval: Literal[False] = False
    promotion: Literal[False] = False
    activation: Literal[False] = False

    @model_validator(mode="after")
    def authority_and_shape(self) -> Self:
        paired = self.request.pairing.mode == "PAIRED_COMPARISON"
        if paired != (self.paired_table is not None):
            raise ValueError("EVALUATION_RESULT_PAIRING_SHAPE_MISMATCH")
        if (
            self.population_fingerprint != self.request.population.fingerprint
            or self.ground_truth_fingerprint != self.request.ground_truth.fingerprint
            or self.metrics.metric_set != self.request.metric_set
            or self.statistics.policy != self.request.statistics
            or self.created_at < self.request.created_at
        ):
            raise ValueError("EVALUATION_RESULT_IDENTITY_MISMATCH")
        participant_ids = tuple(item.participant_id for item in self.request.participants)
        metric_ids = tuple(item.metric_id for item in self.request.metric_set.metrics)
        actual_metric_grid = tuple(
            (item.participant_id, item.metric_id) for item in self.metrics.values
        )
        expected_metric_grid = tuple(
            (participant_id, metric_id)
            for participant_id in participant_ids
            for metric_id in metric_ids
        )
        if (
            actual_metric_grid != expected_metric_grid
            or tuple(item.participant_id for item in self.coverage.participant_availability)
            != participant_ids
            or tuple(item.observation_id for item in self.coverage.dispositions)
            != self.request.population.observation_ids
        ):
            raise ValueError("EVALUATION_RESULT_GRID_MISMATCH")
        if self.paired_table is not None and (
            self.paired_table.pairing != self.request.pairing
            or self.paired_table.population_fingerprint != self.request.population.fingerprint
        ):
            raise ValueError("EVALUATION_RESULT_PAIRED_IDENTITY_MISMATCH")
        return self


class NormalizedEvaluationLedger(SealedResearch):
    request: ArtifactReference
    population: ArtifactReference
    evaluation_input: ArtifactReference
    paired_table: ArtifactReference | None
    metrics: ArtifactReference
    statistics: ArtifactReference
    result: ArtifactReference
    completed_at: ForecastDateTime
    replay: Literal["MATCH"] = "MATCH"


class LegacyFF1EvaluationView(SealedResearch):
    adapter_version: Literal["flc6.ff1-final-readonly.1"] = "flc6.ff1-final-readonly.1"
    protocol_fingerprint: Sha256
    execution_fingerprint: Sha256
    evaluation_fingerprint: Sha256
    ledger_fingerprint: Sha256
    paired_population_fingerprint: Sha256
    ground_truth_fingerprint: Sha256
    metric_policy_fingerprint: Sha256
    classification: Literal["INSUFFICIENT_EVIDENCE"]
    scientific_reason: Literal["CONFIDENCE_NONDECISIVE"]
    benchmark_role: Literal["BASERATE_BENCHMARK"] = "BASERATE_BENCHMARK"
    challenger_role: Literal["LOGISTIC_CHALLENGER_EXPERIMENTAL"] = (
        "LOGISTIC_CHALLENGER_EXPERIMENTAL"
    )
    evidence_state: Literal["HISTORICAL_ACCEPTED_CONSUMED"] = "HISTORICAL_ACCEPTED_CONSUMED"
    executions_used: Literal[1] = 1
    post_holdout_refit_allowed: Literal[False] = False
    automatic_promotion: Literal[False] = False
    reclassified_as_unseen: Literal[False] = False
    evaluation_reexecuted: Literal[False] = False
    semantics: Literal["READ_ONLY_VIEW_NO_METRIC_RECOMPUTATION"] = (
        "READ_ONLY_VIEW_NO_METRIC_RECOMPUTATION"
    )
    created_at: ForecastDateTime
