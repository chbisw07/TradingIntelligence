"""Typed failures for factual AnalysisContext construction."""

from typing import TYPE_CHECKING

from tiaf.data.runtime import ProviderGateState

if TYPE_CHECKING:
    from tiaf.context.models import AnalysisContext


class AnalysisContextError(Exception):
    """Base error for context validation and assembly failures."""


class AnalysisContextResolutionError(AnalysisContextError):
    """A canonical analysis subject could not be resolved uniquely."""


class AnalysisContextBuildError(AnalysisContextError):
    """A context could not be built under the caller's strict policy."""


class AnalysisContextDeferredError(AnalysisContextBuildError):
    """Context assembly was deferred by the provider scheduler, not failed."""

    def __init__(
        self,
        evidence_name: str,
        provider: str,
        operation: str,
        retry_after_seconds: float | None,
        reason: str,
        gate_state: ProviderGateState,
        partial_context: "AnalysisContext",
    ) -> None:
        self.evidence_name = evidence_name
        self.provider = provider
        self.operation = operation
        self.retry_after_seconds = retry_after_seconds
        self.reason = reason
        self.gate_state = gate_state
        self.partial_context = partial_context
        retry = (
            "unknown"
            if retry_after_seconds is None
            else f"{retry_after_seconds:.6f}s"
        )
        super().__init__(
            f"evidence {evidence_name!r} deferred by provider {provider!r} "
            f"operation {operation!r} in gate state {gate_state.value}: {reason}; "
            f"retry after {retry}"
        )


class RequiredEvidenceUnavailableError(AnalysisContextBuildError):
    """Required factual evidence was unavailable or unacceptable."""

    def __init__(self, evidence_name: str, reason: str) -> None:
        self.evidence_name = evidence_name
        self.reason = reason
        super().__init__(f"required evidence {evidence_name!r} is unavailable: {reason}")
