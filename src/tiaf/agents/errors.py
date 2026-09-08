"""Typed failures for the provider-neutral A3.1 Agent foundation."""


class AgentError(Exception):
    """Base error for Agent contracts, registry, and runtime."""


class AgentNotRegisteredError(AgentError):
    """A requested specialist identity is absent from the registry."""

    def __init__(self, specialist_id: str) -> None:
        self.specialist_id = specialist_id
        super().__init__(f"specialist {specialist_id!r} is not registered")


class AgentEvidenceError(AgentError):
    """Supplied evidence or capability authorization is inconsistent."""


class AgentBudgetExceededError(AgentError):
    """Reported or observed usage exceeds the request budget."""


class AgentTimeoutError(AgentError):
    """A bounded specialist or future reasoning operation timed out."""


class AgentOutputValidationError(AgentError):
    """A specialist returned an opinion that violates its request/evidence."""


class ReasoningProviderError(AgentError):
    """A future reasoning provider failed without producing a valid response."""
