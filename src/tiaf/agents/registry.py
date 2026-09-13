"""Caller-populated registry for independently extensible specialists."""

from tiaf.cold_bindings import FrozenBindingsError

from .enums import SpecialistId
from .errors import AgentNotRegisteredError, AgentOutputValidationError
from .models import SpecialistCapability
from .protocols import SpecialistAgent


class AgentRegistry:
    """Register and discover specialists without central runtime branching."""

    def __init__(self, specialists: tuple[SpecialistAgent, ...] = ()) -> None:
        self._frozen = False
        self._specialists: dict[SpecialistId, SpecialistAgent] = {}
        for specialist in specialists:
            self.register(specialist)

    def register(self, specialist: SpecialistAgent) -> None:
        """Register one protocol-conforming specialist and reject duplicates."""
        if self._frozen:
            raise FrozenBindingsError()
        if not isinstance(specialist, SpecialistAgent):
            raise AgentOutputValidationError(
                "specialist does not satisfy SpecialistAgent protocol"
            )
        try:
            capability = specialist.capability()
        except Exception as exc:
            raise AgentOutputValidationError(
                "specialist capability declaration failed"
            ) from exc
        if not isinstance(capability, SpecialistCapability):
            raise AgentOutputValidationError(
                "specialist capability must be SpecialistCapability"
            )
        specialist_id = capability.specialist
        if specialist_id in self._specialists:
            raise AgentOutputValidationError(
                f"duplicate specialist ID: {specialist_id.value}"
            )
        self._specialists[specialist_id] = specialist

    def frozen_copy(self) -> "AgentRegistry":
        """Pin membership without freezing or retaining the caller's binding map."""
        snapshot = AgentRegistry()
        snapshot._specialists = self._specialists.copy()
        snapshot._frozen = True
        return snapshot

    def get(self, specialist_id: SpecialistId) -> SpecialistAgent:
        """Return one specialist or raise a typed lookup error."""
        try:
            return self._specialists[specialist_id]
        except KeyError as exc:
            raise AgentNotRegisteredError(specialist_id.value) from exc

    def capabilities(self) -> tuple[SpecialistCapability, ...]:
        """Return an immutable specialist-ID-sorted capability snapshot."""
        return tuple(
            self._specialists[specialist_id].capability()
            for specialist_id in sorted(self._specialists, key=lambda item: item.value)
        )
