"""Stable provider-neutral enums for A3 specialist intelligence."""

from enum import StrEnum


class SpecialistId(StrEnum):
    """Bounded specialist domains accepted by the A3 architecture."""

    TECHNICAL = "TECHNICAL"
    FUNDAMENTAL = "FUNDAMENTAL"
    NEWS_EVENT = "NEWS_EVENT"
    RELATIVE_STRENGTH = "RELATIVE_STRENGTH"
    SECTOR = "SECTOR"
    MACRO = "MACRO"
    DERIVATIVES_CONTEXT = "DERIVATIVES_CONTEXT"
    OPPORTUNITY_QUALITY = "OPPORTUNITY_QUALITY"
    OPPORTUNITY_RISK = "OPPORTUNITY_RISK"
    CONTRARIAN_HYPOTHESIS = "CONTRARIAN_HYPOTHESIS"
    FORECAST_INTERPRETATION = "FORECAST_INTERPRETATION"


class AgentCapability(StrEnum):
    """Least-privilege capability identities; A3.1 implements no tools."""

    READ_A2_EVIDENCE = "READ_A2_EVIDENCE"
    READ_FUNDAMENTALS = "READ_FUNDAMENTALS"
    READ_FILINGS = "READ_FILINGS"
    READ_NEWS = "READ_NEWS"
    READ_SECTOR_CONTEXT = "READ_SECTOR_CONTEXT"
    READ_MACRO_CONTEXT = "READ_MACRO_CONTEXT"
    READ_DERIVATIVES = "READ_DERIVATIVES"
    READ_FORECAST = "READ_FORECAST"
    REQUEST_ADDITIONAL_MARKET_EVIDENCE = "REQUEST_ADDITIONAL_MARKET_EVIDENCE"


class AgentStance(StrEnum):
    """Specialist interpretation, deliberately separate from trading actions."""

    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    ABSTAIN = "ABSTAIN"


class AnalysisMode(StrEnum):
    """Budgeted reasoning depth; none implies an external model call."""

    DETERMINISTIC_ONLY = "DETERMINISTIC_ONLY"
    RULE_POLICY = "RULE_POLICY"
    LIGHTWEIGHT_REASONING = "LIGHTWEIGHT_REASONING"
    FULL_SPECIALIST = "FULL_SPECIALIST"
    DEEP_ANALYSIS = "DEEP_ANALYSIS"


class BaselineAgreement(StrEnum):
    """Explicit relationship between A3 interpretation and the A2 benchmark."""

    AGREES = "AGREES"
    PARTIALLY_AGREES = "PARTIALLY_AGREES"
    DISAGREES = "DISAGREES"
    NOT_COMPARABLE = "NOT_COMPARABLE"


class CitationRole(StrEnum):
    """How an evidence reference relates to one claim."""

    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"


class ClaimKind(StrEnum):
    """Distinguish factual attribution from bounded interpretation."""

    FACTUAL = "FACTUAL"
    INTERPRETIVE = "INTERPRETIVE"
    FORECAST_INTERPRETATION = "FORECAST_INTERPRETATION"


class EvidenceImportance(StrEnum):
    """Specialist-declared importance of unavailable evidence."""

    OPTIONAL = "OPTIONAL"
    MATERIAL = "MATERIAL"
    REQUIRED = "REQUIRED"


class AgentRunStatus(StrEnum):
    """Typed outcome of one bounded specialist run."""

    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    ABSTAINED = "ABSTAINED"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    TIMEOUT = "TIMEOUT"
    FAILED = "FAILED"


class SpecialistCostTier(StrEnum):
    """Vendor-neutral relative cost class used by future planning policy."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CalibrationStatus(StrEnum):
    """Whether numerical forecast evidence has empirical calibration."""

    CALIBRATED = "CALIBRATED"
    NOT_CALIBRATED = "NOT_CALIBRATED"
    UNKNOWN = "UNKNOWN"


class ReasoningStatus(StrEnum):
    """Provider-neutral structured-reasoning result status."""

    SUCCESS = "SUCCESS"
    TIMEOUT = "TIMEOUT"
    FAILED = "FAILED"
