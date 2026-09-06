"""Enums describing factual analysis-context purpose and evidence state."""

from enum import StrEnum


class AnalysisPurpose(StrEnum):
    """Why factual context is being assembled, not a trading decision."""

    OPPORTUNITY = "OPPORTUNITY"
    POSITION = "POSITION"
    RESEARCH = "RESEARCH"
    SCREENING = "SCREENING"
    OPTION_EXPRESSION = "OPTION_EXPRESSION"


class EvidenceStatus(StrEnum):
    """Availability state of one requested or unrequested evidence slot."""

    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    STALE = "STALE"
    MISSING = "MISSING"
    FAILED = "FAILED"
    DEFERRED = "DEFERRED"
    NOT_REQUESTED = "NOT_REQUESTED"


class EvidenceRequirement(StrEnum):
    """Whether an evidence slot was requested and whether it is required."""

    NOT_REQUESTED = "NOT_REQUESTED"
    OPTIONAL_REQUESTED = "OPTIONAL_REQUESTED"
    REQUIRED = "REQUIRED"


class BatchItemStatus(StrEnum):
    """Truthful outcome of one ordered AnalysisContext batch item."""

    COMPLETE_CONTEXT = "COMPLETE_CONTEXT"
    PARTIAL_CONTEXT = "PARTIAL_CONTEXT"
    DEFERRED = "DEFERRED"
    ERROR = "ERROR"
