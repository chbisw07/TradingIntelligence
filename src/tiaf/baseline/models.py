"""Immutable public contracts for the deterministic A2.9 benchmark."""

import math
from typing import Annotated, Any, Self

from pydantic import Field, field_validator, model_validator

from tiaf.contracts import ContractModel, DataQuality, FreshnessState, Horizon, TradeStyle
from tiaf.contracts.common import Metadata, NonEmptyStr, Score, Symbol, TiafDateTime
from tiaf.data import normalize_interval
from tiaf.features import FeatureBundle, MultiTimeframeContext
from tiaf.features.models import JSONScalar
from tiaf.indicators import IndicatorBundle

from .enums import (
    BaselineDirection,
    BaselineEvidenceSource,
    CandidateClass,
    ComponentName,
    ExplanationCode,
    RuleRole,
    ScoreSemantics,
    TransformKind,
)

FiniteFloat = Annotated[float, Field(allow_inf_nan=False)]
NonNegativeFiniteFloat = Annotated[float, Field(ge=0, allow_inf_nan=False)]
UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
SignedUnitFloat = Annotated[float, Field(ge=-1, le=1, allow_inf_nan=False)]


class EvidenceFreshness(ContractModel):
    """Caller-supplied replayable freshness for one supplied evidence slot."""

    source: BaselineEvidenceSource
    state: FreshnessState


class EvidenceSelector(ContractModel):
    """Exact feature or indicator value selected by a policy rule."""

    source: BaselineEvidenceSource
    evidence_id: NonEmptyStr
    parameters: tuple[tuple[NonEmptyStr, JSONScalar], ...] = ()
    output_name: NonEmptyStr | None = None

    @field_validator("parameters", mode="before")
    @classmethod
    def canonical_parameters(cls, value: Any) -> Any:
        if value is None:
            return ()
        if isinstance(value, dict):
            value = tuple(value.items())
        if isinstance(value, (str, bytes)):
            raise ValueError("parameters must contain name/value pairs")
        pairs = tuple((str(name).strip(), item) for name, item in value)
        if any(not name for name, _ in pairs):
            raise ValueError("parameter names must not be empty")
        if len(pairs) != len({name for name, _ in pairs}):
            raise ValueError("parameter names must be unique")
        if any(isinstance(item, float) and not math.isfinite(item) for _, item in pairs):
            raise ValueError("selector parameter floats must be finite")
        return tuple(sorted(pairs))

    @model_validator(mode="after")
    def validate_source_shape(self) -> Self:
        if self.source is BaselineEvidenceSource.INDICATOR:
            if self.output_name is None:
                raise ValueError("indicator selector requires output_name")
        elif self.output_name is not None:
            raise ValueError("feature selector cannot declare output_name")
        return self


class EvidenceRule(ContractModel):
    """One fully explicit policy-owned evidence transformation."""

    rule_id: NonEmptyStr
    component: ComponentName
    selector: EvidenceSelector
    role: RuleRole
    transform: TransformKind
    weight: NonNegativeFiniteFloat
    required: bool = False
    orientation: int = Field(default=1, ge=-1, le=1)
    scale: NonNegativeFiniteFloat | None = None
    center: FiniteFloat | None = None
    floor: FiniteFloat | None = None
    target: FiniteFloat | None = None
    ceiling: FiniteFloat | None = None
    post_boundary_credit: UnitFloat = 0.0
    code_threshold: UnitFloat = 0.0
    positive_code: ExplanationCode | None = None
    negative_code: ExplanationCode | None = None

    @model_validator(mode="after")
    def validate_transform(self) -> Self:
        if self.weight <= 0:
            raise ValueError("evidence rule weight must be positive")
        if self.orientation not in {-1, 1}:
            raise ValueError("orientation must be -1 or 1")
        if self.transform is TransformKind.SIGNED_LINEAR:
            if self.scale is None or self.scale <= 0:
                raise ValueError("SIGNED_LINEAR requires positive scale")
        elif self.transform is TransformKind.CENTERED_LINEAR:
            if self.scale is None or self.scale <= 0 or self.center is None:
                raise ValueError("CENTERED_LINEAR requires center and positive scale")
        elif self.transform in {
            TransformKind.UNSIGNED_LINEAR,
            TransformKind.LOWER_BETTER,
        }:
            if self.floor is None or self.ceiling is None or self.ceiling <= self.floor:
                raise ValueError(f"{self.transform.value} requires floor < ceiling")
        elif self.transform is TransformKind.TRIANGLE:
            if (
                self.floor is None
                or self.target is None
                or self.ceiling is None
                or not self.floor < self.target < self.ceiling
            ):
                raise ValueError("TRIANGLE requires floor < target < ceiling")
        elif self.transform in {TransformKind.POSITIVE_ROOM, TransformKind.NEGATIVE_ROOM}:
            if self.scale is None or self.scale <= 0 or self.ceiling is None:
                raise ValueError("room transforms require positive scale and ceiling")
            if self.ceiling <= 0:
                raise ValueError("room boundary ceiling must be positive")
        if self.role is RuleRole.DIRECTIONAL and self.transform in {
            TransformKind.TRIANGLE,
            TransformKind.LOWER_BETTER,
            TransformKind.POSITIVE_ROOM,
            TransformKind.NEGATIVE_ROOM,
        }:
            raise ValueError("directional rules require a signed-capable transform")
        return self


class ComponentWeight(ContractModel):
    """Policy weights kept separate from calculator code."""

    component: ComponentName
    direction_weight: NonNegativeFiniteFloat = 0.0
    opportunity_weight: NonNegativeFiniteFloat = 0.0
    required: bool = False


class DirectionThresholds(ContractModel):
    minimum_score: Score
    minimum_margin: NonNegativeFiniteFloat
    conflict_score: Score
    component_conflict_score: Score


class ClassificationThresholds(ContractModel):
    minimum_alignment: Score
    minimum_opportunity_score: Score
    early_opportunity_score: Score
    top_mover_momentum: Score
    top_mover_participation: Score
    mature_extension: Score
    mature_room: Score


class PenaltyPolicy(ContractModel):
    """Maximum point deductions from the weighted opportunity base."""

    extension_points: NonNegativeFiniteFloat
    conflict_points: NonNegativeFiniteFloat
    partial_quality_points: NonNegativeFiniteFloat
    degraded_quality_points: NonNegativeFiniteFloat
    unavailable_quality_points: NonNegativeFiniteFloat
    aging_freshness_points: NonNegativeFiniteFloat
    unknown_freshness_points: NonNegativeFiniteFloat


class QualityFactor(ContractModel):
    """Multiplicative evidence-quality treatment owned by policy."""

    quality: DataQuality
    factor: UnitFloat


class BaselinePolicy(ContractModel):
    """Serializable versioned source of every A2.9 weight and threshold."""

    policy_id: NonEmptyStr
    policy_version: NonEmptyStr = "1.0"
    trade_style: TradeStyle
    component_weights: tuple[ComponentWeight, ...]
    evidence_rules: tuple[EvidenceRule, ...]
    direction_thresholds: DirectionThresholds
    classification_thresholds: ClassificationThresholds
    penalties: PenaltyPolicy
    quality_factors: tuple[QualityFactor, ...]
    critical_freshness_sources: tuple[BaselineEvidenceSource, ...]
    rounding_digits: int = Field(ge=0, le=12)
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_policy(self) -> Self:
        components = tuple(item.component for item in self.component_weights)
        rule_ids = tuple(item.rule_id for item in self.evidence_rules)
        if len(components) != len(set(components)):
            raise ValueError("component weights must be unique")
        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError("evidence rule IDs must be unique")
        if not self.evidence_rules:
            raise ValueError("policy requires evidence rules")
        if set(components) != set(ComponentName):
            raise ValueError("component weights must define every component exactly once")
        rule_components = {rule.component for rule in self.evidence_rules}
        if rule_components != set(components):
            raise ValueError("every component requires at least one evidence rule")
        direction_total = sum(item.direction_weight for item in self.component_weights)
        opportunity_total = sum(item.opportunity_weight for item in self.component_weights)
        if not math.isclose(direction_total, 1.0, rel_tol=0.0, abs_tol=1e-9):
            raise ValueError("directional component weights must sum to one")
        if not math.isclose(opportunity_total, 1.0, rel_tol=0.0, abs_tol=1e-9):
            raise ValueError("opportunity component weights must sum to one")
        if len(self.critical_freshness_sources) != len(set(self.critical_freshness_sources)):
            raise ValueError("critical freshness sources must be unique")
        qualities = tuple(item.quality for item in self.quality_factors)
        if set(qualities) != set(DataQuality) or len(qualities) != len(set(qualities)):
            raise ValueError("quality factors must define every DataQuality exactly once")
        thresholds = self.classification_thresholds
        if thresholds.early_opportunity_score < thresholds.minimum_opportunity_score:
            raise ValueError("early threshold cannot be below minimum opportunity threshold")
        if self.direction_thresholds.minimum_margin > 100:
            raise ValueError("direction margin cannot exceed 100")
        return self

    def weight(self, component: ComponentName) -> ComponentWeight:
        """Return the explicitly configured weights for one component."""
        return next(item for item in self.component_weights if item.component is component)

    def quality_factor(self, quality: DataQuality) -> float:
        """Return the explicit multiplicative quality factor."""
        return next(item.factor for item in self.quality_factors if item.quality is quality)


class DeterministicBaselineRequest(ContractModel):
    """Provider-neutral immutable evidence request for one candidate."""

    request_id: NonEmptyStr
    subject: Symbol
    trade_style: TradeStyle
    horizon: Horizon
    primary_timeframe: NonEmptyStr
    supporting_timeframes: tuple[NonEmptyStr, ...] = ()
    primary_features: FeatureBundle
    indicators: IndicatorBundle | None = None
    relative_features: FeatureBundle | None = None
    multi_timeframe_context: MultiTimeframeContext | None = None
    multi_timeframe_features: FeatureBundle | None = None
    derivatives_features: FeatureBundle | None = None
    evidence_freshness: tuple[EvidenceFreshness, ...]
    policy_version: NonEmptyStr
    requested_at: TiafDateTime
    metadata: Metadata = Field(default_factory=dict)

    @field_validator("primary_timeframe", mode="before")
    @classmethod
    def normalize_primary_timeframe(cls, value: str) -> str:
        return normalize_interval(value)

    @field_validator("supporting_timeframes", mode="before")
    @classmethod
    def normalize_supporting_timeframes(cls, value: Any) -> Any:
        if isinstance(value, (str, bytes)):
            return value
        return tuple(normalize_interval(item) for item in value)

    @field_validator("evidence_freshness", mode="before")
    @classmethod
    def canonical_evidence_freshness(cls, value: Any) -> Any:
        """Canonicalize this semantically unordered source map for stable identity."""
        if isinstance(value, (str, bytes)):
            return value
        return tuple(
            sorted(
                value,
                key=lambda item: (
                    item.source.value if isinstance(item, EvidenceFreshness) else item["source"]
                ),
            )
        )

    @model_validator(mode="after")
    def validate_evidence(self) -> Self:
        if self.primary_timeframe in self.supporting_timeframes:
            raise ValueError("supporting timeframes must exclude the primary timeframe")
        if len(self.supporting_timeframes) != len(set(self.supporting_timeframes)):
            raise ValueError("supporting timeframes must be unique")
        supplied: set[BaselineEvidenceSource] = {BaselineEvidenceSource.PRIMARY}
        bundle_pairs = (
            (BaselineEvidenceSource.INDICATOR, self.indicators),
            (BaselineEvidenceSource.RELATIVE, self.relative_features),
            (BaselineEvidenceSource.DERIVATIVES, self.derivatives_features),
        )
        for source, bundle in bundle_pairs:
            if bundle is not None:
                supplied.add(source)
                if bundle.subject_symbol != self.subject:
                    raise ValueError(f"{source.value} evidence subject must match request")
        if self.primary_features.subject_symbol != self.subject:
            raise ValueError("primary evidence subject must match request")
        if any(
            result.request.interval not in {None, self.primary_timeframe}
            for result in self.primary_features.results
        ):
            raise ValueError("primary feature intervals must match primary timeframe")
        if (
            self.indicators is not None
            and self.indicators.context_id != self.primary_features.context_id
        ):
            raise ValueError("indicator and primary feature contexts must match")
        has_mtf = (
            self.multi_timeframe_context is not None or self.multi_timeframe_features is not None
        )
        if has_mtf:
            if self.multi_timeframe_context is None or self.multi_timeframe_features is None:
                raise ValueError("multi-timeframe context and features must be supplied together")
            supplied.add(BaselineEvidenceSource.MULTI_TIMEFRAME)
            expected = (self.primary_timeframe, *self.supporting_timeframes)
            if self.multi_timeframe_context.subject_symbol != self.subject:
                raise ValueError("multi-timeframe subject must match request")
            if self.multi_timeframe_context.requested_intervals != expected:
                raise ValueError(
                    "multi-timeframe order must match primary then supporting timeframes"
                )
            if self.multi_timeframe_features.context_id != self.multi_timeframe_context.context_id:
                raise ValueError("multi-timeframe feature context identity must match")
            if self.multi_timeframe_features.subject_symbol != self.subject:
                raise ValueError("multi-timeframe feature subject must match request")
        freshness_sources = tuple(item.source for item in self.evidence_freshness)
        if len(freshness_sources) != len(set(freshness_sources)):
            raise ValueError("evidence freshness sources must be unique")
        if set(freshness_sources) != supplied:
            raise ValueError("freshness must be explicit for every supplied evidence source")
        evidence_times = [self.primary_features.created_at]
        evidence_times.extend(
            bundle.created_at
            for bundle in (
                self.indicators,
                self.relative_features,
                self.multi_timeframe_features,
                self.derivatives_features,
            )
            if bundle is not None
        )
        if self.multi_timeframe_context is not None:
            evidence_times.append(self.multi_timeframe_context.created_at)
        if any(item > self.requested_at for item in evidence_times):
            raise ValueError("requested_at cannot predate supplied evidence")
        return self


class EvidenceContribution(ContractModel):
    """One retained factual input and its bounded policy transform."""

    rule_id: NonEmptyStr
    component: ComponentName
    source: BaselineEvidenceSource
    evidence_id: NonEmptyStr
    source_context_id: NonEmptyStr
    source_evidence: tuple[NonEmptyStr, ...]
    as_of: TiafDateTime
    raw_value: FiniteFloat
    normalized_signal: SignedUnitFloat
    weighted_signal: FiniteFloat
    quality: DataQuality
    freshness: FreshnessState
    explanation_codes: tuple[ExplanationCode, ...] = ()
    warnings: tuple[NonEmptyStr, ...] = ()
    metadata: Metadata = Field(default_factory=dict)


class ScoreComponent(ContractModel):
    """Decomposable component with score basis and factual evidence kept separate."""

    component: ComponentName
    semantics: ScoreSemantics
    available: bool
    score: Score | None
    score_basis_direction: BaselineDirection | None = None
    positive_score: Score | None = None
    negative_score: Score | None = None
    quality: DataQuality
    contributions: tuple[EvidenceContribution, ...] = ()
    missing_evidence: tuple[NonEmptyStr, ...] = ()
    score_explanation_codes: tuple[ExplanationCode, ...] = ()
    explanation_codes: tuple[ExplanationCode, ...] = ()

    @model_validator(mode="after")
    def validate_availability(self) -> Self:
        if self.available != (self.score is not None):
            raise ValueError("component availability must agree with score presence")
        if self.available and not self.contributions:
            raise ValueError("available component requires contributions")
        expects_direction = self.available and self.semantics is ScoreSemantics.DIRECTIONAL_SUPPORT
        if expects_direction != (self.score_basis_direction is not None):
            raise ValueError("score basis direction must agree with component semantics")
        return self


class MarketStateAssessment(ContractModel):
    """Directional state with conflict and availability left visible."""

    direction: BaselineDirection
    positive_direction_score: Score
    negative_direction_score: Score
    directional_margin: FiniteFloat
    evidence_alignment_score: Score
    conflicting_component_count: int = Field(ge=0)
    unavailable_component_count: int = Field(ge=0)
    quality: DataQuality
    components: tuple[ScoreComponent, ...]
    explanation_codes: tuple[ExplanationCode, ...] = ()
    warnings: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_components(self) -> Self:
        names = tuple(item.component for item in self.components)
        if set(names) != set(ComponentName) or len(names) != len(set(names)):
            raise ValueError("market state must contain every component exactly once")
        if self.unavailable_component_count != sum(not item.available for item in self.components):
            raise ValueError("unavailable component count must match components")
        return self


class OpportunityAssessment(ContractModel):
    """Replayable A2.9 benchmark output, distinct from final A0 intelligence."""

    assessment_id: NonEmptyStr
    request_id: NonEmptyStr
    subject: Symbol
    trade_style: TradeStyle
    horizon: Horizon
    primary_timeframe: NonEmptyStr
    supporting_timeframes: tuple[NonEmptyStr, ...]
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    market_state: MarketStateAssessment
    opportunity_score: Score
    maturity_score: Score
    chase_risk_score: Score
    candidate_class: CandidateClass
    eligible: bool
    evidence_context_ids: tuple[NonEmptyStr, ...]
    evidence_bundle_ids: tuple[NonEmptyStr, ...]
    evidence_freshness: tuple[EvidenceFreshness, ...]
    created_at: TiafDateTime
    explanation_codes: tuple[ExplanationCode, ...] = ()
    warnings: tuple[NonEmptyStr, ...] = ()
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_eligibility(self) -> Self:
        expected = self.candidate_class is not CandidateClass.NO_TRADE
        if self.eligible != expected:
            raise ValueError("eligibility must agree with candidate class")
        return self


class OpportunityRankingItem(ContractModel):
    """Compact stable ranked projection of one eligible assessment."""

    rank: int = Field(ge=1)
    subject: Symbol
    assessment_id: NonEmptyStr
    opportunity_score: Score
    candidate_class: CandidateClass
    direction: BaselineDirection
    evidence_quality: DataQuality
    component_scores: tuple[tuple[ComponentName, Score], ...]
    reasons: tuple[ExplanationCode, ...]
    warnings: tuple[NonEmptyStr, ...]


class OpportunityRanking(ContractModel):
    """Eligible-only ranking plus all original assessments for audit."""

    ranking_id: NonEmptyStr
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr
    trade_style: TradeStyle
    horizon: Horizon
    requested_top_n: int | None = Field(default=None, ge=1)
    input_universe: tuple[Symbol, ...]
    items: tuple[OpportunityRankingItem, ...]
    assessments: tuple[OpportunityAssessment, ...]
    excluded_no_trade: tuple[Symbol, ...]
    created_at: TiafDateTime

    @model_validator(mode="after")
    def validate_ranking(self) -> Self:
        if tuple(item.rank for item in self.items) != tuple(range(1, len(self.items) + 1)):
            raise ValueError("ranking item ranks must be consecutive from one")
        if any(item.candidate_class is CandidateClass.NO_TRADE for item in self.items):
            raise ValueError("ranking items cannot contain NO_TRADE")
        assessment_ids = {item.assessment_id for item in self.assessments}
        if any(item.assessment_id not in assessment_ids for item in self.items):
            raise ValueError("ranking items must reference retained assessments")
        if (
            len(self.input_universe) != len(set(self.input_universe))
            or set(self.input_universe) != {item.subject for item in self.assessments}
        ):
            raise ValueError("input_universe must match retained assessment subjects")
        expected_excluded = tuple(
            item.subject
            for item in self.assessments
            if item.candidate_class is CandidateClass.NO_TRADE
        )
        if self.excluded_no_trade != expected_excluded:
            raise ValueError("excluded_no_trade must match retained assessments")
        return self


def worst_quality(values: tuple[DataQuality, ...]) -> DataQuality:
    """Return the weakest quality using the accepted explicit order."""
    if not values:
        return DataQuality.UNAVAILABLE
    order = {
        DataQuality.GOOD: 0,
        DataQuality.PARTIAL: 1,
        DataQuality.DEGRADED: 2,
        DataQuality.UNAVAILABLE: 3,
    }
    return max(values, key=order.__getitem__)


def finite(value: float) -> float:
    """Reject accidental non-finite internal arithmetic."""
    if not math.isfinite(value):
        raise ValueError("baseline calculation produced a non-finite value")
    return value
