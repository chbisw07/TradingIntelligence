"""Typed A6.1 configuration and integrity errors."""

from .enums import A6ErrorCode


class A6ContractError(ValueError):
    """Malformed A6 contract or configuration, not a normal domain outcome."""

    def __init__(self, code: A6ErrorCode, message: str) -> None:
        self.code = code
        super().__init__(message)


class UnsupportedA6PolicyError(A6ContractError):
    """The requested policy identity or content is not supported."""


class A6ReplayIntegrityError(A6ContractError):
    """A replay result differs from its captured deterministic result."""
