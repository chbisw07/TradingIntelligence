"""Framework-independent specialist and reasoning-provider protocols."""

from typing import Protocol, runtime_checkable

from .evidence import AgentEvidencePack
from .models import (
    AgentOpinionV2,
    AgentRequest,
    ReasoningModelIdentity,
    ReasoningRequest,
    ReasoningResponse,
    SpecialistCapability,
)


@runtime_checkable
class SpecialistAgent(Protocol):
    """One bounded specialist with declared evidence and tool requirements."""

    def capability(self) -> SpecialistCapability:
        """Return stable identity, requirements, limits, and prohibitions."""
        ...

    def analyze(
        self,
        request: AgentRequest,
        evidence: AgentEvidencePack,
    ) -> AgentOpinionV2:
        """Interpret supplied evidence without fetching or executing anything."""
        ...


@runtime_checkable
class ReasoningProvider(Protocol):
    """Optional SDK-neutral structured reasoning boundary for future adapters."""

    def identity(self) -> ReasoningModelIdentity:
        """Return stable provider/model/config identity."""
        ...

    def reason(self, request: ReasoningRequest) -> ReasoningResponse:
        """Return schema-bound output and usage or a typed failure response."""
        ...
