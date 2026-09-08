"""Stable provider-neutral statuses and policy choices for A3.2 gateways."""

from enum import StrEnum


class EvidenceGatewayStatus(StrEnum):
    """Infrastructure outcome of one evidence gateway request."""

    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNAVAILABLE = "UNAVAILABLE"
    STALE = "STALE"
    DEFERRED = "DEFERRED"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    TIMEOUT = "TIMEOUT"
    UNAUTHORIZED_CAPABILITY = "UNAUTHORIZED_CAPABILITY"
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_OUTPUT = "INVALID_OUTPUT"
    FAILED = "FAILED"


class ReasoningGatewayStatus(StrEnum):
    """Infrastructure outcome of one optional reasoning request."""

    SUCCESS = "SUCCESS"
    MODEL_DISABLED = "MODEL_DISABLED"
    UNAVAILABLE = "UNAVAILABLE"
    DEFERRED = "DEFERRED"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    TIMEOUT = "TIMEOUT"
    UNAUTHORIZED_CAPABILITY = "UNAUTHORIZED_CAPABILITY"
    INVALID_REQUEST = "INVALID_REQUEST"
    MODEL_OUTPUT_INVALID = "MODEL_OUTPUT_INVALID"
    PROVIDER_FAILURE = "PROVIDER_FAILURE"
    FAILED = "FAILED"


class GatewayCacheStatus(StrEnum):
    """Whether a result was reused by the A3 gateway cache."""

    HIT = "HIT"
    MISS = "MISS"
    NOT_CACHEABLE = "NOT_CACHEABLE"


class AuthorizationDecision(StrEnum):
    """Explicit least-privilege authorization decision."""

    ALLOWED = "ALLOWED"
    DENIED = "DENIED"


class ModelTier(StrEnum):
    """Vendor-neutral increasing reasoning depth/cost tier."""

    NONE = "NONE"
    DETERMINISTIC = "DETERMINISTIC"
    LIGHTWEIGHT = "LIGHTWEIGHT"
    STANDARD = "STANDARD"
    DEEP = "DEEP"


_MODEL_TIER_ORDER = {
    ModelTier.NONE: 0,
    ModelTier.DETERMINISTIC: 1,
    ModelTier.LIGHTWEIGHT: 2,
    ModelTier.STANDARD: 3,
    ModelTier.DEEP: 4,
}


def model_tier_rank(tier: ModelTier) -> int:
    """Return stable policy ordering without encoding a vendor."""
    return _MODEL_TIER_ORDER[tier]


class ModelCapability(StrEnum):
    """Bounded model operations; none grants evidence or tool authority."""

    STRUCTURED_REASONING = "STRUCTURED_REASONING"


class DowngradePolicy(StrEnum):
    """Explicit behavior when the requested tier cannot be honored."""

    FAIL = "FAIL"
    DOWNGRADE = "DOWNGRADE"
    NO_LLM_FALLBACK = "NO_LLM_FALLBACK"
