"""Deterministic human-readable formatting for baseline outputs."""

from .models import OpportunityAssessment, OpportunityRanking


def summarize_assessment(assessment: OpportunityAssessment) -> str:
    """Render fixed labels without recommendation, target, or contract language."""
    state = assessment.market_state
    component_lines: list[str] = []
    for item in state.components:
        score = item.score if item.score is not None else "-"
        basis = (
            item.score_basis_direction.value
            if item.score_basis_direction
            else "NOT_DIRECTIONAL"
        )
        positive = item.positive_score if item.positive_score is not None else "-"
        negative = item.negative_score if item.negative_score is not None else "-"
        score_reasons = ",".join(code.value for code in item.score_explanation_codes) or "-"
        evidence_facts = ",".join(code.value for code in item.explanation_codes) or "-"
        component_lines.extend(
            (
                f"{item.component.value:<28}: {score} ({item.semantics.value})",
                f"  Score Basis / Sides         : {basis}; positive={positive}; "
                f"negative={negative}",
                f"  Score Reasons               : {score_reasons}",
                f"  Evidence Facts              : {evidence_facts}",
            )
        )
    warnings = "; ".join(assessment.warnings) or "-"
    reasons = ", ".join(item.value for item in assessment.explanation_codes) or "-"
    return "\n".join(
        (
            f"{assessment.subject} DETERMINISTIC BASELINE",
            "=" * 56,
            f"Direction                   : {state.direction.value}",
            f"Positive Score              : {state.positive_direction_score}",
            f"Negative Score              : {state.negative_direction_score}",
            f"Directional Margin          : {state.directional_margin}",
            *tuple(component_lines),
            f"Evidence Alignment          : {state.evidence_alignment_score}",
            f"Opportunity Score           : {assessment.opportunity_score}",
            f"Maturity / Chase Risk       : {assessment.chase_risk_score}",
            f"Candidate Class             : {assessment.candidate_class.value}",
            f"Quality                     : {state.quality.value}",
            f"Warnings                    : {warnings}",
            f"Reasons                     : {reasons}",
        )
    )


def summarize_ranking(ranking: OpportunityRanking) -> str:
    """Render an eligible-only ranking, including a valid empty result."""
    heading = "TIAF A2.9 DETERMINISTIC OPPORTUNITY RANKING\n" + "=" * 56
    if not ranking.items:
        return f"{heading}\nNo eligible opportunities; NO_TRADE is preserved."
    rows = tuple(
        f"{item.rank:>2}. {item.subject:<16} {item.opportunity_score:>9.3f}  "
        f"{item.candidate_class.value}  {item.direction.value}"
        for item in ranking.items
    )
    return "\n".join((heading, *rows))
