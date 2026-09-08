"""Public A3.2 controlled evidence and optional reasoning gateways."""

from .cache import InMemoryEvidenceGatewayCache, evidence_cache_key, reasoning_cache_key
from .contracts import (
    EvidenceGatewayAuditRecord,
    EvidenceGatewayContext,
    EvidenceGatewayRequest,
    EvidenceGatewayResult,
    EvidenceGatewayRun,
    GatewayIdentity,
    ReasoningGatewayAuditRecord,
    ReasoningGatewayRequest,
    ReasoningGatewayResult,
    ReasoningGatewayRun,
)
from .enums import (
    AuthorizationDecision,
    DowngradePolicy,
    EvidenceGatewayStatus,
    GatewayCacheStatus,
    ModelCapability,
    ModelTier,
    ReasoningGatewayStatus,
)
from .errors import (
    GatewayAuthorizationError,
    GatewayError,
    GatewayNotFoundError,
    GatewayOutputValidationError,
    GatewayRegistrationError,
)
from .evidence import A2EvidenceEntry, A2EvidenceGateway
from .policy import (
    EvidenceGatewayPolicy,
    ModelTierMapping,
    ReasoningGatewayPolicy,
    budget_within,
)
from .protocols import EvidenceGateway
from .reasoning import ReasoningGateway
from .registry import (
    EvidenceGatewayRegistry,
    ReasoningProviderRegistration,
    ReasoningProviderRegistry,
)
from .runtime import EvidenceGatewayRuntime

__all__ = [
    "A2EvidenceEntry",
    "A2EvidenceGateway",
    "AuthorizationDecision",
    "DowngradePolicy",
    "EvidenceGateway",
    "EvidenceGatewayAuditRecord",
    "EvidenceGatewayContext",
    "EvidenceGatewayPolicy",
    "EvidenceGatewayRegistry",
    "EvidenceGatewayRequest",
    "EvidenceGatewayResult",
    "EvidenceGatewayRun",
    "EvidenceGatewayRuntime",
    "EvidenceGatewayStatus",
    "GatewayAuthorizationError",
    "GatewayCacheStatus",
    "GatewayError",
    "GatewayIdentity",
    "GatewayNotFoundError",
    "GatewayOutputValidationError",
    "GatewayRegistrationError",
    "InMemoryEvidenceGatewayCache",
    "ModelCapability",
    "ModelTier",
    "ModelTierMapping",
    "ReasoningGateway",
    "ReasoningGatewayAuditRecord",
    "ReasoningGatewayPolicy",
    "ReasoningGatewayRequest",
    "ReasoningGatewayResult",
    "ReasoningGatewayRun",
    "ReasoningGatewayStatus",
    "ReasoningProviderRegistration",
    "ReasoningProviderRegistry",
    "budget_within",
    "evidence_cache_key",
    "reasoning_cache_key",
]
