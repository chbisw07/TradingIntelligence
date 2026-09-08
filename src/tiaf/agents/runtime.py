"""Minimal single-specialist runtime with bounded failure isolation."""

from collections.abc import Callable
from datetime import datetime
from time import monotonic

from pydantic import ValidationError

from tiaf.context import EvidenceStatus
from tiaf.contracts import EvidenceType
from tiaf.contracts.common import TIAF_TIMEZONE

from .budget import AgentUsage
from .enums import AgentRunStatus
from .errors import (
    AgentBudgetExceededError,
    AgentError,
    AgentEvidenceError,
    AgentOutputValidationError,
    AgentTimeoutError,
)
from .evidence import AgentEvidencePack
from .models import (
    AgentFailure,
    AgentOpinionV2,
    AgentRequest,
    AgentRunRecord,
    SpecialistCapability,
)
from .registry import AgentRegistry

WallClock = Callable[[], datetime]
ElapsedClock = Callable[[], float]


def _now() -> datetime:
    return datetime.now(TIAF_TIMEZONE)


class AgentRuntime:
    """Invoke exactly one registered specialist over already supplied evidence."""

    def __init__(
        self,
        registry: AgentRegistry,
        *,
        wall_clock: WallClock = _now,
        elapsed_clock: ElapsedClock = monotonic,
    ) -> None:
        self._registry = registry
        self._wall_clock = wall_clock
        self._elapsed_clock = elapsed_clock

    def run(
        self,
        request: AgentRequest,
        evidence: AgentEvidencePack,
    ) -> AgentRunRecord:
        """Run one specialist and always isolate post-validation failures."""
        started_at = self._wall_clock()
        elapsed_start = self._elapsed_clock()
        specialist_version = "UNRESOLVED"
        try:
            specialist = self._registry.get(request.specialist)
            definition = specialist.capability()
            specialist_version = definition.specialist_version
            self._validate_evidence_contract(request, evidence, definition)
            if self._missing_required_evidence(evidence, definition.required_evidence_types):
                return self._record(
                    request=request,
                    evidence=evidence,
                    specialist_version=specialist_version,
                    status=AgentRunStatus.INSUFFICIENT_EVIDENCE,
                    usage=self._observed_usage(AgentUsage(), elapsed_start),
                    started_at=started_at,
                )
            raw_opinion = specialist.analyze(request, evidence)
            if not isinstance(raw_opinion, AgentOpinionV2):
                raise AgentOutputValidationError(
                    "specialist must return AgentOpinionV2"
                )
            try:
                opinion = AgentOpinionV2.model_validate(
                    raw_opinion.model_dump(mode="python")
                )
            except ValidationError as exc:
                raise AgentOutputValidationError(
                    "specialist returned an invalid AgentOpinionV2"
                ) from exc
            self._validate_opinion(request, evidence, definition.specialist_version, opinion)
            usage = self._observed_usage(opinion.usage, elapsed_start)
            opinion = opinion.model_copy(update={"usage": usage})
            violations = request.budget.violations(usage)
            if violations:
                if "elapsed_seconds" in violations:
                    error: AgentError = AgentTimeoutError(
                        "specialist exceeded max_elapsed_seconds"
                    )
                    status = AgentRunStatus.TIMEOUT
                else:
                    error = AgentBudgetExceededError(
                        f"Agent usage exceeded budget limits: {', '.join(violations)}"
                    )
                    status = AgentRunStatus.BUDGET_EXCEEDED
                return self._failed_record(
                    request,
                    evidence,
                    specialist_version,
                    status,
                    error,
                    elapsed_start,
                    started_at,
                    retryable=status is AgentRunStatus.TIMEOUT,
                    usage=usage,
                )
            return self._record(
                request=request,
                evidence=evidence,
                specialist_version=specialist_version,
                status=opinion.status,
                usage=usage,
                started_at=started_at,
                opinion=opinion,
            )
        except AgentTimeoutError as exc:
            return self._failed_record(
                request,
                evidence,
                specialist_version,
                AgentRunStatus.TIMEOUT,
                exc,
                elapsed_start,
                started_at,
                retryable=True,
            )
        except AgentBudgetExceededError as exc:
            return self._failed_record(
                request,
                evidence,
                specialist_version,
                AgentRunStatus.BUDGET_EXCEEDED,
                exc,
                elapsed_start,
                started_at,
            )
        except (AgentError, ValidationError) as exc:
            return self._failed_record(
                request,
                evidence,
                specialist_version,
                AgentRunStatus.FAILED,
                exc,
                elapsed_start,
                started_at,
            )
        except Exception as exc:  # specialist code is an isolation boundary
            wrapped = AgentOutputValidationError(
                f"specialist raised unexpected {type(exc).__name__}"
            )
            return self._failed_record(
                request,
                evidence,
                specialist_version,
                AgentRunStatus.FAILED,
                wrapped,
                elapsed_start,
                started_at,
            )

    @staticmethod
    def _validate_evidence_contract(
        request: AgentRequest,
        evidence: AgentEvidencePack,
        definition: SpecialistCapability,
    ) -> None:
        if definition.specialist is not request.specialist:
            raise AgentOutputValidationError("specialist identity does not match request")
        if request.instrument_type not in definition.supported_instrument_types:
            raise AgentEvidenceError("specialist does not support request instrument type")
        if not set(definition.allowed_capabilities) <= set(request.allowed_capabilities):
            raise AgentEvidenceError("specialist requires a capability not allowed by request")
        if (
            evidence.request_id != request.request_id
            or evidence.subject != request.subject
            or evidence.evidence_fingerprint != request.evidence_fingerprint
            or evidence.deterministic_assessment_id
            != request.deterministic_baseline_reference
        ):
            raise AgentEvidenceError("evidence pack does not preserve request/A2 identity")

    @staticmethod
    def _missing_required_evidence(
        evidence: AgentEvidencePack,
        required_types: tuple[EvidenceType, ...],
    ) -> bool:
        usable = {EvidenceStatus.AVAILABLE, EvidenceStatus.PARTIAL, EvidenceStatus.STALE}
        available_types = {
            item.evidence_type
            for item in evidence.references
            if item.availability in usable
        }
        return not set(required_types) <= available_types

    @staticmethod
    def _validate_opinion(
        request: AgentRequest,
        evidence: AgentEvidencePack,
        specialist_version: str,
        opinion: AgentOpinionV2,
    ) -> None:
        if (
            opinion.request_id != request.request_id
            or opinion.run_id != request.run_id
            or opinion.specialist is not request.specialist
            or opinion.specialist_version != specialist_version
            or opinion.subject != request.subject
            or opinion.horizon != request.horizon
            or opinion.deterministic_baseline_reference
            != request.deterministic_baseline_reference
            or opinion.evidence_fingerprint != request.evidence_fingerprint
        ):
            raise AgentOutputValidationError("opinion does not preserve request identity")
        supplied_ids = {item.evidence_id for item in evidence.references}
        cited_ids = {
            citation.evidence_id
            for claim in opinion.evidence_claims
            for citation in claim.citations
        }
        if not cited_ids <= supplied_ids:
            raise AgentOutputValidationError("opinion cites evidence outside supplied pack")
        for claim in opinion.evidence_claims:
            for citation in claim.citations:
                reference = evidence.reference(citation.evidence_id)
                if reference is None or reference.evidence_type is not claim.evidence_type:
                    raise AgentOutputValidationError(
                        "claim evidence type does not match supplied reference"
                    )
                if reference.availability not in {
                    EvidenceStatus.AVAILABLE,
                    EvidenceStatus.PARTIAL,
                    EvidenceStatus.STALE,
                }:
                    raise AgentOutputValidationError(
                        "claim cannot cite unavailable evidence as factual support"
                    )
        opinion_ids = set(opinion.supporting_evidence_ids) | set(
            opinion.contradictory_evidence_ids
        )
        if not opinion_ids <= supplied_ids:
            raise AgentOutputValidationError("opinion references evidence outside supplied pack")
        if (
            opinion.evidence_quality is not evidence.overall_quality
            or opinion.evidence_freshness is not evidence.overall_freshness
            or opinion.confidence.evidence_coverage != evidence.evidence_coverage
        ):
            raise AgentOutputValidationError("opinion must preserve evidence quality/coverage")
        if any(
            item.capability not in request.allowed_capabilities
            for item in opinion.missing_evidence
        ):
            raise AgentOutputValidationError(
                "opinion requests evidence through an unauthorized capability"
            )
        if any(item.subject != request.subject for item in opinion.missing_evidence):
            raise AgentOutputValidationError(
                "opinion missing-evidence request must match request subject"
            )

    def _observed_usage(self, usage: AgentUsage, elapsed_start: float) -> AgentUsage:
        elapsed = max(0.0, self._elapsed_clock() - elapsed_start)
        return usage.model_copy(
            update={"elapsed_seconds": max(usage.elapsed_seconds, elapsed)}
        )

    def _record(
        self,
        *,
        request: AgentRequest,
        evidence: AgentEvidencePack,
        specialist_version: str,
        status: AgentRunStatus,
        usage: AgentUsage,
        started_at: datetime,
        opinion: AgentOpinionV2 | None = None,
        failure: AgentFailure | None = None,
    ) -> AgentRunRecord:
        return AgentRunRecord(
            record_id=f"{request.run_id}:record",
            request=request,
            evidence_pack=evidence,
            specialist=request.specialist,
            specialist_version=specialist_version,
            status=status,
            opinion=opinion,
            failure=failure,
            usage=usage,
            started_at=started_at,
            completed_at=self._wall_clock(),
        )

    def _failed_record(
        self,
        request: AgentRequest,
        evidence: AgentEvidencePack,
        specialist_version: str,
        status: AgentRunStatus,
        error: Exception,
        elapsed_start: float,
        started_at: datetime,
        *,
        retryable: bool = False,
        usage: AgentUsage | None = None,
    ) -> AgentRunRecord:
        actual_usage = usage or self._observed_usage(AgentUsage(), elapsed_start)
        return self._record(
            request=request,
            evidence=evidence,
            specialist_version=specialist_version,
            status=status,
            usage=actual_usage,
            started_at=started_at,
            failure=AgentFailure(
                error_type=type(error).__name__,
                detail=str(error),
                retryable=retryable,
            ),
        )
