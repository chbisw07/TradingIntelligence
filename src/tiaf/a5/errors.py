"""Typed fail-closed errors for A5.1."""


class A5EvaluationError(ValueError):
    """Base A5 deterministic evaluation error."""


class A5InputIntegrityError(A5EvaluationError):
    """Supplied position/A4 identity or fingerprint is incoherent."""


class A5OutputIntegrityError(A5EvaluationError):
    """A constructed result or run failed semantic validation."""


class A5ReplayIntegrityError(A5EvaluationError):
    """Captured bytes, checksums, links, or policy failed closed."""


class UnsupportedA5PolicyError(A5EvaluationError):
    """The requested policy identity/version is not executable."""
