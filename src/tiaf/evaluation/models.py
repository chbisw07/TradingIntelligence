"""Immutable contracts for evidence, decisions, replay, and later outcomes."""

from typing import Annotated, Self

from pydantic import Field, JsonValue, model_validator

from tiaf.baseline import (
    BaselineDirection,
    BaselinePolicy,
    CandidateClass,
    ComponentName,
    DeterministicBaselineRequest,
    ExplanationCode,
    OpportunityAssessment,
)
from tiaf.contracts import ContractModel, DataQuality, Horizon, TradeStyle
from tiaf.contracts.common import Metadata, NonEmptyStr, Symbol, TiafDateTime

from .enums import ProducerType, RegressionStatus

FiniteFloat = Annotated[float, Field(allow_inf_nan=False)]
NonNegativeFiniteFloat = Annotated[float, Field(ge=0, allow_inf_nan=False)]
PositiveFiniteFloat = Annotated[float, Field(gt=0, allow_inf_nan=False)]


class SnapshotContextReference(ContractModel):
    """Normalized context identity retained without requiring provider access."""

    context_id: NonEmptyStr
    role: NonEmptyStr
    subject: Symbol
    interval: NonEmptyStr | None = None
    created_at: TiafDateTime
    source_as_of: TiafDateTime | None = None


class EvidenceSnapshot(ContractModel):
    """Self-contained normalized decision-time evidence sufficient for A2.9 replay."""

    snapshot_id: NonEmptyStr
    fingerprint: NonEmptyStr
    fingerprint_algorithm: NonEmptyStr = "sha256"
    fingerprint_schema_version: NonEmptyStr = "1.0"
    producer_type: ProducerType = ProducerType.DETERMINISTIC_BASELINE
    producer_id: NonEmptyStr = "tiaf.baseline"
    producer_version: NonEmptyStr
    subject: Symbol
    benchmark_symbol: Symbol | None = None
    trade_style: TradeStyle
    horizon: Horizon
    requested_timeframes: tuple[NonEmptyStr, ...]
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    decision_time: TiafDateTime
    snapshot_created_at: TiafDateTime
    context_references: tuple[SnapshotContextReference, ...]
    decision_request: DeterministicBaselineRequest
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        request = self.decision_request
        if self.fingerprint_algorithm != "sha256":
            raise ValueError("only sha256 evidence fingerprints are supported")
        if self.producer_type is not ProducerType.DETERMINISTIC_BASELINE:
            raise ValueError("A2.10 snapshot capture supports deterministic baseline only")
        if (
            self.subject != request.subject
            or self.trade_style is not request.trade_style
            or self.horizon != request.horizon
            or self.policy_version != request.policy_version
            or self.decision_time != request.requested_at
        ):
            raise ValueError("snapshot identity must match decision request")
        if self.requested_timeframes != (
            request.primary_timeframe,
            *request.supporting_timeframes,
        ):
            raise ValueError("snapshot timeframes must match decision request")
        if self.snapshot_created_at < self.decision_time:
            raise ValueError("snapshot_created_at cannot predate decision_time")
        from .snapshot import (
            context_references,
            expected_snapshot_id,
            semantic_fingerprint,
            validate_no_secrets,
        )

        validate_no_secrets(self.model_dump(mode="json"))
        if self.context_references != context_references(request):
            raise ValueError("snapshot context references must match embedded evidence")
        expected = semantic_fingerprint(
            request,
            policy_id=self.policy_id,
            producer_id=self.producer_id,
            producer_version=self.producer_version,
            benchmark_symbol=self.benchmark_symbol,
            context_references=self.context_references,
            fingerprint_schema_version=self.fingerprint_schema_version,
        )
        if self.fingerprint != expected:
            raise ValueError("snapshot fingerprint does not match semantic evidence")
        if self.snapshot_id != expected_snapshot_id(expected):
            raise ValueError("snapshot_id does not match evidence fingerprint")
        return self


class RankingContext(ContractModel):
    """Original batch placement retained without allowing hindsight re-ranking."""

    ranking_id: NonEmptyStr
    original_rank: int | None = Field(default=None, ge=1)
    requested_top_n: int | None = Field(default=None, ge=1)
    input_universe: tuple[Symbol, ...]


class ComponentScoreRecord(ContractModel):
    """Frozen projection of a decision-time component score."""

    component: ComponentName
    score: NonNegativeFiniteFloat | None


class BaselineRunRecord(ContractModel):
    """Append-only decision record; outcomes reference but never modify it."""

    run_id: NonEmptyStr
    producer_type: ProducerType = ProducerType.DETERMINISTIC_BASELINE
    producer_id: NonEmptyStr
    producer_version: NonEmptyStr
    evidence_snapshot_id: NonEmptyStr
    evidence_fingerprint: NonEmptyStr
    subject: Symbol
    horizon: Horizon
    trade_style: TradeStyle
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    assessment: OpportunityAssessment
    candidate_class: CandidateClass
    direction: BaselineDirection
    opportunity_score: NonNegativeFiniteFloat
    component_scores: tuple[ComponentScoreRecord, ...]
    reasons: tuple[ExplanationCode, ...]
    quality: DataQuality
    warnings: tuple[NonEmptyStr, ...]
    ranking_context: RankingContext | None = None
    decision_at: TiafDateTime
    recorded_at: TiafDateTime
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_projection(self) -> Self:
        assessment = self.assessment
        expected_scores = tuple(
            ComponentScoreRecord(component=item.component, score=item.score)
            for item in assessment.market_state.components
        )
        if (
            self.subject != assessment.subject
            or self.horizon != assessment.horizon
            or self.trade_style is not assessment.trade_style
            or self.policy_id != assessment.policy_id
            or self.policy_version != assessment.policy_version
            or self.candidate_class is not assessment.candidate_class
            or self.direction is not assessment.market_state.direction
            or self.opportunity_score != assessment.opportunity_score
            or self.component_scores != expected_scores
            or self.reasons != assessment.explanation_codes
            or self.quality is not assessment.market_state.quality
            or self.warnings != assessment.warnings
            or self.decision_at != assessment.created_at
        ):
            raise ValueError("run record projection must exactly match assessment")
        if self.recorded_at < self.decision_at:
            raise ValueError("recorded_at cannot predate decision_at")
        if self.producer_type is not ProducerType.DETERMINISTIC_BASELINE:
            raise ValueError("A2.10 records deterministic baseline runs only")
        return self


class CapturedBaselineCase(ContractModel):
    """Filesystem envelope preserving separate evidence and decision objects."""

    snapshot: EvidenceSnapshot
    run_record: BaselineRunRecord

    @model_validator(mode="after")
    def validate_link(self) -> Self:
        if (
            self.run_record.evidence_snapshot_id != self.snapshot.snapshot_id
            or self.run_record.evidence_fingerprint != self.snapshot.fingerprint
        ):
            raise ValueError("captured run must reference captured evidence")
        return self


class ReplayRequest(ContractModel):
    """Explicit offline replay inputs, including non-semantic replay time."""

    snapshot: EvidenceSnapshot
    policy: BaselinePolicy
    expected_assessment: OpportunityAssessment | None = None
    replay_time: TiafDateTime


class FieldDifference(ContractModel):
    """One deterministic field-level mismatch."""

    path: NonEmptyStr
    expected: JsonValue
    actual: JsonValue


class ReplayResult(ContractModel):
    """Offline assessment plus exact expected-output comparison when supplied."""

    replay_id: NonEmptyStr
    snapshot_id: NonEmptyStr
    evidence_fingerprint: NonEmptyStr
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    assessment: OpportunityAssessment
    exact_match: bool | None
    differences: tuple[FieldDifference, ...] = ()
    replay_time: TiafDateTime


class ComponentDelta(ContractModel):
    """Exact new-minus-old component comparison for one evidence snapshot."""

    component: ComponentName
    old_score: NonNegativeFiniteFloat | None
    new_score: NonNegativeFiniteFloat | None
    delta: FiniteFloat | None


class BaselineComparison(ContractModel):
    """Two immutable policy assessments over the same frozen evidence."""

    comparison_id: NonEmptyStr
    snapshot_id: NonEmptyStr
    evidence_fingerprint: NonEmptyStr
    old_policy_id: NonEmptyStr
    old_policy_version: NonEmptyStr
    new_policy_id: NonEmptyStr
    new_policy_version: NonEmptyStr
    old_assessment: OpportunityAssessment
    new_assessment: OpportunityAssessment
    old_direction: BaselineDirection
    new_direction: BaselineDirection
    old_opportunity_score: NonNegativeFiniteFloat
    new_opportunity_score: NonNegativeFiniteFloat
    opportunity_delta: FiniteFloat
    old_candidate_class: CandidateClass
    new_candidate_class: CandidateClass
    component_deltas: tuple[ComponentDelta, ...]
    added_reasons: tuple[ExplanationCode, ...]
    removed_reasons: tuple[ExplanationCode, ...]


class OutcomeWindow(ContractModel):
    """Explicit subsequent observation window, never a decision-time input."""

    start_at: TiafDateTime
    end_at: TiafDateTime
    source_interval: NonEmptyStr

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.end_at <= self.start_at:
            raise ValueError("outcome window end must be after start")
        return self


class OutcomeObservation(ContractModel):
    """One normalized future bar used only after the decision is frozen."""

    start_at: TiafDateTime
    end_at: TiafDateTime
    high: PositiveFiniteFloat
    low: PositiveFiniteFloat
    close: PositiveFiniteFloat

    @model_validator(mode="after")
    def validate_bar(self) -> Self:
        if self.end_at <= self.start_at:
            raise ValueError("outcome observation end must be after start")
        if self.high < max(self.low, self.close) or self.low > self.close:
            raise ValueError("outcome OHLC bounds are inconsistent")
        return self


class OutcomePath(ContractModel):
    """Later factual path attached by identity, not inserted into the assessment."""

    outcome_path_id: NonEmptyStr
    run_id: NonEmptyStr
    assessment_id: NonEmptyStr
    evidence_fingerprint: NonEmptyStr
    subject: Symbol
    assessment_reference_price: PositiveFiniteFloat
    window: OutcomeWindow
    observations: tuple[OutcomeObservation, ...]
    quality: DataQuality
    complete: bool
    captured_at: TiafDateTime
    warnings: tuple[NonEmptyStr, ...] = ()
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_observations(self) -> Self:
        if not self.observations:
            raise ValueError("outcome path requires observations")
        if tuple(sorted(self.observations, key=lambda item: item.start_at)) != self.observations:
            raise ValueError("outcome observations must be chronologically ordered")
        if any(
            item.start_at < self.window.start_at or item.end_at > self.window.end_at
            for item in self.observations
        ):
            raise ValueError("outcome observations must lie inside the explicit window")
        if any(
            current.start_at < previous.end_at
            for previous, current in zip(self.observations, self.observations[1:])
        ):
            raise ValueError("outcome observations must not overlap")
        if self.captured_at < self.observations[-1].end_at:
            raise ValueError("captured_at cannot predate observed outcome data")
        return self


class ExcursionMetrics(ContractModel):
    """Raw path movement and optional direction-relative excursions."""

    ending_return_percent: FiniteFloat
    maximum_upside_excursion_percent: NonNegativeFiniteFloat
    maximum_downside_excursion_percent: FiniteFloat
    mfe_percent: NonNegativeFiniteFloat | None
    mae_percent: FiniteFloat | None
    realized_range_percent: NonNegativeFiniteFloat
    bars_observed: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_signs(self) -> Self:
        if self.maximum_downside_excursion_percent > 0:
            raise ValueError("maximum downside excursion must be non-positive")
        if self.mae_percent is not None and self.mae_percent > 0:
            raise ValueError("MAE must be non-positive")
        if (self.mfe_percent is None) != (self.mae_percent is None):
            raise ValueError("directional MFE and MAE must be present together")
        return self


class BaselineOutcome(ContractModel):
    """Outcome evaluation referencing an unchanged decision-time run."""

    baseline_outcome_id: NonEmptyStr
    run_id: NonEmptyStr
    assessment_id: NonEmptyStr
    evidence_fingerprint: NonEmptyStr
    subject: Symbol
    original_direction: BaselineDirection
    original_candidate_class: CandidateClass
    path: OutcomePath
    metrics: ExcursionMetrics
    evaluated_at: TiafDateTime

    @model_validator(mode="after")
    def validate_path_link(self) -> Self:
        if (
            self.run_id != self.path.run_id
            or self.assessment_id != self.path.assessment_id
            or self.evidence_fingerprint != self.path.evidence_fingerprint
            or self.subject != self.path.subject
        ):
            raise ValueError("baseline outcome identity must match outcome path")
        if self.evaluated_at < self.path.captured_at:
            raise ValueError("evaluated_at cannot predate outcome capture")
        return self


class ObservedStatistics(ContractModel):
    """Descriptive observed averages with no execution or alpha claim."""

    count: int = Field(ge=0)
    average_ending_return_percent: FiniteFloat | None = None
    average_mfe_percent: NonNegativeFiniteFloat | None = None
    average_mae_percent: FiniteFloat | None = None


class RankingOutcomeItem(ContractModel):
    """Original rank association and later factual metrics."""

    subject: Symbol
    assessment_id: NonEmptyStr
    original_rank: int | None = Field(default=None, ge=1)
    original_candidate_class: CandidateClass
    originally_eligible: bool
    metrics: ExcursionMetrics


class RankingEvaluation(ContractModel):
    """Observed outcomes keyed to the frozen ranking without hindsight reordering."""

    ranking_evaluation_id: NonEmptyStr
    ranking_id: NonEmptyStr
    evidence_fingerprints: tuple[NonEmptyStr, ...]
    items: tuple[RankingOutcomeItem, ...]
    top_1: ObservedStatistics
    top_n: ObservedStatistics
    eligible_population: ObservedStatistics
    no_trade_population: ObservedStatistics
    evaluated_at: TiafDateTime


class EvaluationMetrics(ContractModel):
    """Corpus-level descriptive counts and outcome averages."""

    runs_evaluated: int = Field(ge=0)
    replay_pass_count: int = Field(ge=0)
    replay_fail_count: int = Field(ge=0)
    direction_counts: tuple[tuple[BaselineDirection, int], ...]
    class_counts: tuple[tuple[CandidateClass, int], ...]
    quality_counts: tuple[tuple[DataQuality, int], ...]
    observed_outcomes: ObservedStatistics


class RegressionCheckResult(ContractModel):
    """One expected-versus-replayed assessment check."""

    check_id: NonEmptyStr
    status: RegressionStatus
    snapshot_id: NonEmptyStr
    run_id: NonEmptyStr
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    evidence_fingerprint: NonEmptyStr
    differences: tuple[FieldDifference, ...] = ()


class RegressionReport(ContractModel):
    """Stable corpus regression summary."""

    report_id: NonEmptyStr
    results: tuple[RegressionCheckResult, ...]
    pass_count: int = Field(ge=0)
    fail_count: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_counts(self) -> Self:
        if self.pass_count != sum(item.status is RegressionStatus.PASS for item in self.results):
            raise ValueError("pass_count must match regression results")
        if self.fail_count != sum(item.status is RegressionStatus.FAIL for item in self.results):
            raise ValueError("fail_count must match regression results")
        return self
