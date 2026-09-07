"""Deterministic A2.9 synthesis benchmark over accepted factual evidence."""

from .engine import BaselineEngine
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
from .errors import BaselineError, BaselinePolicyError, BaselineRankingError
from .inspection import summarize_policy
from .models import (
    BaselinePolicy,
    ClassificationThresholds,
    ComponentWeight,
    DeterministicBaselineRequest,
    DirectionThresholds,
    EvidenceContribution,
    EvidenceFreshness,
    EvidenceRule,
    EvidenceSelector,
    MarketStateAssessment,
    OpportunityAssessment,
    OpportunityRanking,
    OpportunityRankingItem,
    PenaltyPolicy,
    QualityFactor,
    ScoreComponent,
)
from .policy import default_policy
from .ranking import rank_opportunities
from .scoring import score_request
from .summaries import summarize_assessment, summarize_ranking

__all__ = [
    "BaselineDirection",
    "BaselineEngine",
    "BaselineError",
    "BaselineEvidenceSource",
    "BaselinePolicy",
    "BaselinePolicyError",
    "BaselineRankingError",
    "CandidateClass",
    "ClassificationThresholds",
    "ComponentName",
    "ComponentWeight",
    "DeterministicBaselineRequest",
    "DirectionThresholds",
    "EvidenceContribution",
    "EvidenceFreshness",
    "EvidenceRule",
    "EvidenceSelector",
    "ExplanationCode",
    "MarketStateAssessment",
    "OpportunityAssessment",
    "OpportunityRanking",
    "OpportunityRankingItem",
    "PenaltyPolicy",
    "QualityFactor",
    "RuleRole",
    "ScoreComponent",
    "ScoreSemantics",
    "TransformKind",
    "default_policy",
    "rank_opportunities",
    "score_request",
    "summarize_assessment",
    "summarize_policy",
    "summarize_ranking",
]
