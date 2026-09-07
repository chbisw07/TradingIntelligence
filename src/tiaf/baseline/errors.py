"""Typed deterministic-baseline failures."""


class BaselineError(Exception):
    """Base class for A2.9 failures."""


class BaselinePolicyError(BaselineError):
    """Raised when a request cannot resolve its declared policy."""


class BaselineRankingError(BaselineError):
    """Raised for incomparable ranking inputs."""
