"""Stable eligible-only watchlist ranking for A2.9 assessments."""

from uuid import NAMESPACE_URL, uuid5

from .enums import CandidateClass
from .errors import BaselineRankingError
from .models import OpportunityAssessment, OpportunityRanking, OpportunityRankingItem

_QUALITY_ORDER = {"GOOD": 0, "PARTIAL": 1, "DEGRADED": 2, "UNAVAILABLE": 3}


def rank_opportunities(
    assessments: tuple[OpportunityAssessment, ...],
    *,
    top_n: int | None = None,
) -> OpportunityRanking:
    """Rank eligible candidates by score, quality, then canonical symbol."""
    if not assessments:
        raise BaselineRankingError("at least one assessment is required")
    if top_n is not None and top_n <= 0:
        raise BaselineRankingError("top_n must be positive")
    canonical = tuple(sorted(assessments, key=lambda item: item.subject))
    if len({item.subject for item in canonical}) != len(canonical):
        raise BaselineRankingError("ranking subjects must be unique")
    first = canonical[0]
    if any(
        item.policy_id != first.policy_id
        or item.policy_version != first.policy_version
        or item.trade_style is not first.trade_style
        or item.horizon != first.horizon
        or item.primary_timeframe != first.primary_timeframe
        or item.supporting_timeframes != first.supporting_timeframes
        for item in canonical[1:]
    ):
        raise BaselineRankingError(
            "assessments must share policy, style, horizon, and timeframe set"
        )
    eligible = tuple(
        sorted(
            (item for item in canonical if item.candidate_class is not CandidateClass.NO_TRADE),
            key=lambda item: (
                -item.opportunity_score,
                _QUALITY_ORDER[item.market_state.quality.value],
                item.subject,
            ),
        )
    )
    selected = eligible if top_n is None else eligible[:top_n]
    items = tuple(
        OpportunityRankingItem(
            rank=index,
            subject=item.subject,
            assessment_id=item.assessment_id,
            opportunity_score=item.opportunity_score,
            candidate_class=item.candidate_class,
            direction=item.market_state.direction,
            evidence_quality=item.market_state.quality,
            component_scores=tuple(
                (component.component, component.score)
                for component in item.market_state.components
                if component.score is not None
            ),
            reasons=item.explanation_codes,
            warnings=item.warnings,
        )
        for index, item in enumerate(selected, start=1)
    )
    identity = "|".join(item.assessment_id for item in canonical)
    ranking_id = str(uuid5(NAMESPACE_URL, f"tiaf:ranking:{identity}:top_n={top_n}"))
    return OpportunityRanking(
        ranking_id=ranking_id,
        policy_id=first.policy_id,
        policy_version=first.policy_version,
        trade_style=first.trade_style,
        horizon=first.horizon,
        requested_top_n=top_n,
        input_universe=tuple(item.subject for item in assessments),
        items=items,
        assessments=canonical,
        excluded_no_trade=tuple(
            item.subject for item in canonical if item.candidate_class is CandidateClass.NO_TRADE
        ),
        created_at=max(item.created_at for item in canonical),
    )
