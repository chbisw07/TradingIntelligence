"""Explicit composition root for the nine implemented specialists."""

from tiaf.agents import AgentRegistry
from tiaf.agents.specialists import (
    DerivativesContextSpecialist,
    FundamentalSpecialist,
    MacroSpecialist,
    NewsEventSpecialist,
    OpportunityQualitySpecialist,
    OpportunityRiskSpecialist,
    RelativeStrengthSpecialist,
    SectorSpecialist,
    TechnicalSpecialist,
)


def default_registry() -> AgentRegistry:
    return AgentRegistry(
        (
            TechnicalSpecialist(),
            FundamentalSpecialist(),
            NewsEventSpecialist(),
            RelativeStrengthSpecialist(),
            SectorSpecialist(),
            MacroSpecialist(),
            DerivativesContextSpecialist(),
            OpportunityQualitySpecialist(),
            OpportunityRiskSpecialist(),
        )
    )
