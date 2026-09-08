"""Typed A3.2 gateway failures used at enforcement boundaries."""

from tiaf.agents.errors import AgentError


class GatewayError(AgentError):
    """Base error for evidence and reasoning gateway infrastructure."""


class GatewayRegistrationError(GatewayError):
    """A gateway/provider registry declaration is invalid or ambiguous."""


class GatewayNotFoundError(GatewayError):
    """No registered gateway/provider satisfies an explicit lookup."""


class GatewayAuthorizationError(GatewayError):
    """A request attempted a capability it was not granted."""


class GatewayOutputValidationError(GatewayError):
    """A gateway/provider returned a malformed or mismatched result."""
