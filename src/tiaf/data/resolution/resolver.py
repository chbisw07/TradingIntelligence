"""Synchronous provider-neutral instrument resolver interface."""

from typing import Protocol, runtime_checkable

from tiaf.data.resolution.models import InstrumentQuery, ResolutionResult, ResolvedInstrument


@runtime_checkable
class InstrumentResolver(Protocol):
    """Resolve explicit queries without recommendations or silent tie-breaking."""

    def resolve(self, query: InstrumentQuery) -> ResolutionResult:
        """Return a unique, ambiguous, or not-found outcome."""
        ...

    def search(self, query: InstrumentQuery) -> tuple[ResolvedInstrument, ...]:
        """Return every exact filtered master match in deterministic order."""
        ...

    def resolve_many(self, queries: tuple[InstrumentQuery, ...]) -> tuple[ResolutionResult, ...]:
        """Resolve independently while preserving query order."""
        ...
