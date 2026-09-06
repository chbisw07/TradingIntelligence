"""Typed errors for feature definitions, registration, and computation."""


class FeatureError(Exception):
    """Base error for the deterministic feature layer."""


class FeatureDefinitionError(FeatureError):
    """A feature definition or registry entry is invalid."""


class FeatureNotRegisteredError(FeatureError):
    """A requested feature ID has no registered calculator."""

    def __init__(self, feature_id: str) -> None:
        self.feature_id = feature_id
        super().__init__(f"feature {feature_id!r} is not registered")


class FeatureParameterError(FeatureError):
    """Feature-specific request parameters are invalid."""


class FeatureComputationError(FeatureError):
    """A calculator violated its contract or failed unexpectedly."""
