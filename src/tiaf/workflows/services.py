"""Controlled composition of existing MI/confirmation/research seams; no transports."""

from concurrent.futures import Future
from threading import RLock

from pydantic import Field

from tiaf.agents import AgentBudget, AgentEvidenceReference, AgentRunRecord
from tiaf.agents.evidence import EvidenceFact, EvidenceFactKind, EvidenceFactParameter
from tiaf.context import EvidenceStatus
from tiaf.contracts import ContractModel, DataQuality, EvidenceSource, EvidenceType, FreshnessState
from tiaf.market_intelligence import (
    AuthoritativeConfirmationGateway,
    AuthoritativeConfirmationResult,
    AuthoritativeConfirmationTask,
    CapabilityRoutePolicy,
    DeepResearchIntegrationController,
    GraphRelation,
    MarketIntelligenceRequest,
    MarketIntelligenceRouter,
    MarketIntelligenceRun,
    SparseEvidenceGraph,
)
from tiaf.planner.digests import digest
from tiaf.planner.models import OrchestrationRequest


class EvidenceAcquisition(ContractModel):
    evidence_type: EvidenceType
    request: MarketIntelligenceRequest
    route: CapabilityRoutePolicy
    material: bool = False
    required_metrics: tuple[str, ...] = ()

    def key(self) -> str:
        return digest(
            {
                "request": self.request.model_dump(mode="json", exclude={"request_id"}),
                "route": self.route.model_dump(mode="json"),
            }
        )


class EvidenceRevision(ContractModel):
    after_round: int = Field(ge=0)
    references: tuple[AgentEvidenceReference, ...]
    reason: str


class ControlledServices:
    """Caller-configured capabilities; cache futures also deduplicate in-flight work."""

    def __init__(
        self,
        *,
        router: MarketIntelligenceRouter | None = None,
        acquisitions: tuple[EvidenceAcquisition, ...] = (),
        confirmation_gateway: AuthoritativeConfirmationGateway | None = None,
        confirmation_tasks: tuple[AuthoritativeConfirmationTask, ...] = (),
        research_controller: DeepResearchIntegrationController | None = None,
        graph: SparseEvidenceGraph | None = None,
        revisions: tuple[EvidenceRevision, ...] = (),
        captured_runs: tuple[MarketIntelligenceRun, ...] = (),
        prior_runs: tuple[AgentRunRecord, ...] = (),
        captured_confirmations: tuple[AuthoritativeConfirmationResult, ...] = (),
        graph_relations: tuple[GraphRelation, ...] = tuple(GraphRelation),
    ) -> None:
        self.router = router
        self.acquisitions = acquisitions
        self.confirmation_gateway = confirmation_gateway
        self.confirmation_tasks = confirmation_tasks
        self.research_controller = research_controller
        self.graph = graph
        self.revisions = revisions
        self.captured_runs = captured_runs
        self.prior_runs = prior_runs
        self.captured_confirmations = captured_confirmations
        self.graph_relations = graph_relations
        self._lock = RLock()
        self._cache: dict[str, Future[MarketIntelligenceRun]] = {}

    def cached(self, acquisition: EvidenceAcquisition) -> bool:
        with self._lock:
            future = self._cache.get(acquisition.key())
            return future is not None and future.done() and future.exception() is None

    def acquire(self, acquisition: EvidenceAcquisition) -> tuple[MarketIntelligenceRun, bool]:
        with self._lock:
            key = acquisition.key()
            existing = self._cache.get(key)
            if existing is None:
                existing = Future()
                self._cache[key] = existing
                owner = True
            else:
                owner = False
        if owner:
            try:
                if self.router is None:
                    raise ValueError("no controlled capability router configured")
                existing.set_result(
                    self.router.execute(
                        acquisition.request,
                        acquisition.route,
                        run_id=f"acquire:{key}",
                    )
                )
            except Exception as exc:
                existing.set_exception(exc)
        return existing.result(), not owner

    def validate(self, request: OrchestrationRequest) -> None:
        if not set(request.inventory.normalized_run_ids) <= {r.run_id for r in self.captured_runs}:
            raise ValueError("missing captured normalized run")
        if not set(request.inventory.prior_run_ids) <= {r.record_id for r in self.prior_runs}:
            raise ValueError("missing captured prior specialist run")
        if not set(request.inventory.confirmation_ids) <= {
            r.confirmation_id for r in self.captured_confirmations
        }:
            raise ValueError("missing captured confirmation")
        if not set(request.inventory.graph_ids) <= ({self.graph.graph_id} if self.graph else set()):
            raise ValueError("missing captured graph snapshot")
        for run in self.captured_runs:
            MarketIntelligenceRun.model_validate_json(run.model_dump_json())
            if run.request.subject != request.subject or run.request.as_of > request.as_of:
                raise ValueError("captured normalized run identity/as-of mismatch")
        for prior in self.prior_runs:
            AgentRunRecord.model_validate_json(prior.model_dump_json())
            if prior.request.subject != request.subject or prior.request.horizon != request.horizon:
                raise ValueError("prior specialist identity mismatch")
        for confirmation in self.captured_confirmations:
            AuthoritativeConfirmationResult.model_validate_json(confirmation.model_dump_json())
            if (
                confirmation.request.claim.subject != request.subject
                or confirmation.request.as_of > request.as_of
            ):
                raise ValueError("captured confirmation identity/as-of mismatch")
        for acquisition in self.acquisitions:
            child = acquisition.request
            if child.subject != request.subject or child.as_of != request.as_of:
                raise ValueError("acquisition identity/as-of mismatch")
            if child.horizon != request.horizon:
                raise ValueError("acquisition horizon mismatch")
            if child.capability != acquisition.route.capability:
                raise ValueError("route capability mismatch")
        for revision in self.revisions:
            for ref in revision.references:
                if ref.subject != request.subject:
                    raise ValueError("revision subject mismatch")
                if any(
                    t is not None and t > request.as_of for t in (ref.observed_at, ref.acquired_at)
                ):
                    raise ValueError("future evidence belongs to a new request")


def acquire_budget(acquisition: EvidenceAcquisition) -> AgentBudget:
    # Full child budget includes all nested source fallbacks, never one allowance per consumer.
    return acquisition.request.budget


def normalized_references(
    run: MarketIntelligenceRun, evidence_type: EvidenceType
) -> tuple[AgentEvidenceReference, ...]:
    refs: dict[str, AgentEvidenceReference] = {}
    for batch in run.batches:
        for ref in batch.evidence_references:
            refs[ref.evidence_id] = ref
        for item in batch.canonical_evidence:
            if any(
                f.metric_id == item.metric and item.source_observation_id in f.source_evidence
                for ref in batch.evidence_references
                for f in ref.facts
            ):
                continue
            if item.evidence_id in refs or not isinstance(item.value, (str, int, float, bool)):
                continue
            native = next(
                (
                    n
                    for n in batch.native_observations
                    if n.observation_id == item.source_observation_id
                ),
                None,
            )
            quality = native.source_quality if native is not None else DataQuality.PARTIAL
            params = (
                ()
                if item.period is None
                else (EvidenceFactParameter(name="period", value=item.period),)
            )
            fact = EvidenceFact(
                fact_id=item.evidence_id,
                kind=(
                    EvidenceFactKind.FUNDAMENTAL
                    if evidence_type is EvidenceType.FUNDAMENTAL
                    else EvidenceFactKind.EVENT
                ),
                metric_id=item.metric,
                value=item.value,
                unit=item.unit,
                parameters=params,
                as_of=item.available_from,
                quality=quality,
                freshness=FreshnessState.UNKNOWN,
                source_evidence=(item.source_observation_id,),
            )
            refs[item.evidence_id] = AgentEvidenceReference(
                evidence_id=item.evidence_id,
                evidence_type=evidence_type,
                subject=run.request.subject,
                producer_id=item.provider_id,
                producer_version="normalized-1.0",
                source=EvidenceSource.DERIVED,
                availability=EvidenceStatus.PARTIAL,
                quality=quality,
                freshness=FreshnessState.UNKNOWN,
                observed_at=item.available_from,
                acquired_at=run.request.as_of,
                checksum=digest(item),
                source_reference=item.source_reference,
                facts=(fact,),
                metadata={"normalization_run": run.run_id, "mapping_quality": item.mapping_quality},
            )
    return tuple(refs.values())
