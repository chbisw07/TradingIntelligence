"""Public A3.6 Relative Strength specialist API."""

from .enums import (
    RelativeConsistencyState,
    RelativeExtremeState,
    RelativeLeadershipState,
    RelativeMtfState,
    RelativeReasonCode,
    RelativeStrengthState,
)
from .evidence import relative_evidence_reference, relative_feature_facts
from .models import RelativeAssessment, RelativeContradiction
from .policy import RelativeInterpretationPolicy, default_relative_policy
from .specialist import (
    RELATIVE_DETAIL_SCHEMA,
    SPECIALIST_VERSION,
    RelativeStrengthSpecialist,
    relative_assessment_from_opinion,
)

RelativeSpecialist = RelativeStrengthSpecialist

__all__ = [
    "RELATIVE_DETAIL_SCHEMA",
    "SPECIALIST_VERSION",
    "RelativeAssessment",
    "RelativeConsistencyState",
    "RelativeContradiction",
    "RelativeExtremeState",
    "RelativeInterpretationPolicy",
    "RelativeLeadershipState",
    "RelativeMtfState",
    "RelativeReasonCode",
    "RelativeSpecialist",
    "RelativeStrengthSpecialist",
    "RelativeStrengthState",
    "default_relative_policy",
    "relative_assessment_from_opinion",
    "relative_evidence_reference",
    "relative_feature_facts",
]
