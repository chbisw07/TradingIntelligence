"""Typed failures for provider-neutral evaluation operations."""


class EvaluationError(Exception):
    """Base error for A2.10 validation and replay."""


class SnapshotIntegrityError(EvaluationError):
    """Serialized evidence does not match its semantic fingerprint."""


class ReplayError(EvaluationError):
    """A snapshot cannot be replayed with the supplied policy."""


class OutcomeEvaluationError(EvaluationError):
    """A subsequent outcome cannot be associated or measured safely."""


class CorpusError(EvaluationError):
    """A replay corpus is absent, malformed, or internally inconsistent."""
