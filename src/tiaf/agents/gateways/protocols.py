"""Framework-independent protocols for controlled A3.2 evidence access."""

from typing import Protocol, runtime_checkable

from tiaf.agents.enums import AgentCapability

from .contracts import (
    EvidenceGatewayContext,
    EvidenceGatewayRequest,
    EvidenceGatewayResult,
    GatewayIdentity,
)


@runtime_checkable
class EvidenceGateway(Protocol):
    """A read-only capability owner with no transport details in its API."""

    def identity(self) -> GatewayIdentity:
        """Return stable gateway identity/version."""
        ...

    def capabilities(self) -> tuple[AgentCapability, ...]:
        """Return the exact allow-listed capabilities owned by this gateway."""
        ...

    def can_handle(self, request: EvidenceGatewayRequest) -> bool:
        """Return whether this gateway can satisfy the semantic request."""
        ...

    def fetch(
        self,
        request: EvidenceGatewayRequest,
        context: EvidenceGatewayContext,
    ) -> EvidenceGatewayResult:
        """Read approved evidence and return a typed result."""
        ...
