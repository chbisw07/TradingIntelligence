"""Application coordinator: deterministic publication with pinned specialist inputs."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime
from time import monotonic

from tiaf.agents import (
    AgentBudget,
    AgentEvidencePack,
    AgentEvidenceReference,
    AgentOpinionV2,
    AgentRegistry,
    AgentRequest,
    AgentRunRecord,
    AgentRunStatus,
    AgentRuntime,
    AgentUsage,
)
from tiaf.agents.evidence import EvidenceFact, EvidenceFactKind
from tiaf.context import EvidenceStatus
from tiaf.contracts import ContractModel, DataQuality, EvidenceSource, EvidenceType, FreshnessState
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.market_intelligence import (
    AuthoritativeConfirmationResult,
    AuthoritativeEscalationPolicy,
    MarketIntelligenceResearchPolicy,
    MarketIntelligenceResearchRequest,
    MarketIntelligenceResearchRun,
    MarketIntelligenceRun,
    SparseEvidenceGraph,
)
from tiaf.planner.digests import digest
from tiaf.planner.models import (
    CapturedArtifact,
    Disposition,
    EvidenceInventory,
    NodeAttempt,
    NodeOutcome,
    NodeStatus,
    OrchestrationRequest,
    OrchestrationResult,
    PlanDecision,
    PlanNode,
    StopReason,
)
from tiaf.planner.policy import (
    build_plan,
    consumption_digest,
    deep_research_allowed,
    dependencies,
    invocation_digest,
    missing_disposition,
    ordered_stops,
)
from tiaf.planner.projection import SpecialistOutputProjection, project_opinion

from .ledger import ReservationLedger, add_usage, reserved_usage
from .records import OrchestrationRunRecord
from .services import ControlledServices, normalized_references

_QUALITY = tuple(DataQuality(v) for v in ("GOOD", "PARTIAL", "DEGRADED", "UNAVAILABLE"))
_FRESHNESS = tuple(FreshnessState(v) for v in ("FRESH", "AGING", "STALE", "UNKNOWN"))
_USABLE = {EvidenceStatus.AVAILABLE, EvidenceStatus.PARTIAL, EvidenceStatus.STALE}


class OrchestrationCoordinator:
    def __init__(
        self,
        registry: AgentRegistry,
        services: ControlledServices | None = None,
        *,
        parallel: bool = False,
        elapsed_clock: Callable[[], float] = monotonic,
        wall_clock: Callable[[], datetime] = lambda: datetime.now(TIAF_TIMEZONE),
    ) -> None:
        self.registry = registry
        self.services = services or ControlledServices()
        self.parallel = parallel
        self.elapsed_clock = elapsed_clock
        self.wall_clock = wall_clock

    def initialize(self, request: OrchestrationRequest) -> None:
        # Reconstruct, rather than trusting a frozen model's mutable metadata or model_copy.
        self.request = OrchestrationRequest.model_validate(request.model_dump(mode="python"))
        self.services.validate(self.request)
        self.started_at = self.wall_clock()
        self.elapsed_start = self.elapsed_clock()
        self.ledger = ReservationLedger(request.budget, request.bounds.max_provider_calls)
        self.plans = [build_plan(self.request, dependencies(self.registry))]
        self.refs = {r.evidence_id: r for r in request.inventory.all_references()}
        self.inventories = [request.inventory]
        self.decisions: list[PlanDecision] = []
        self.attempts: list[NodeAttempt] = []
        self.projections: list[SpecialistOutputProjection] = []
        self.active: dict[str, NodeAttempt] = {}
        self.active_projections: dict[str, SpecialistOutputProjection] = {}
        self.artifacts: list[CapturedArtifact] = []
        self.mi_runs: list[MarketIntelligenceRun] = list(self.services.captured_runs)
        self.confirmations: list[AuthoritativeConfirmationResult] = list(
            self.services.captured_confirmations
        )
        self.stops: set[StopReason] = set()
        self.gaps: set[str] = set()
        self.seen_needs: set[str] = set()
        self.pending_need_types: set[EvidenceType] = set()
        self.round = 0
        self.changed = False
        self.confirmed_tasks: set[str] = set()
        self.researched = False
        self.graph_snapshot: SparseEvidenceGraph | None = None
        for child in self.services.captured_runs:
            self.capture(child.run_id, child)
        for confirmation in self.services.captured_confirmations:
            self.capture(confirmation.confirmation_id, confirmation)
        for prior in self.services.prior_runs:
            self.capture(prior.record_id, prior)
            node = next((n for n in self.plans[0].nodes if n.specialist == prior.specialist), None)
            if node is None:
                continue
            prior_pack, signature = self.input_pack(node)
            if prior.request.evidence_fingerprint != signature:
                continue
            attempt = NodeAttempt(
                node_id=node.node_id,
                plan_version=1,
                status=NodeStatus.REUSED,
                input_digest=signature,
                consumed_digest=self.consumption(node, prior_pack),
                consumed_ids=tuple(r.evidence_id for r in prior.evidence_pack.references),
                record=prior,
            )
            self.attempts.append(attempt)
            self.active[node.node_id] = attempt
            if prior.opinion is not None:
                projection = project_opinion(prior.opinion)
                self.active_projections[node.node_id] = projection
                self.projections.append(projection)
            self.decide("REUSE", "captured prior invocation input matches", (node.node_id,))
        for skipped in self.plans[0].skipped:
            self.decide("SKIP", skipped.reason, (skipped.specialist.value,))
            if skipped.unresolved:
                self.gaps.add(skipped.reason)
        if request.instrument.benchmark_reference is None:
            self.gaps.add("MISSING_BENCHMARK_MAPPING")
        if request.instrument.sector_reference is None:
            self.gaps.add("MISSING_SECTOR_MAPPING")
        if self.services.graph is not None:
            graph = self.services.graph
            self.capture(graph.graph_id, graph)
            edges = tuple(
                e
                for e in graph.edges
                if e.relation in self.services.graph_relations
                and e
                in graph.neighborhood(
                    e.source_node_id,
                    as_of=request.as_of,
                )
                and any(
                    n.node_id in {e.source_node_id, e.target_node_id}
                    and n.canonical_name == request.subject
                    for n in graph.nodes
                )
            )
            # Only supplied one-hop relationships, never inferred new exposure.
            edges = edges[: request.bounds.max_graph_edges]
            ids = {i for e in edges for i in (e.source_node_id, e.target_node_id)}
            nodes = tuple(n for n in graph.nodes if n.node_id in ids)[
                : request.bounds.max_graph_nodes
            ]
            node_ids = {n.node_id for n in nodes}
            scoped = SparseEvidenceGraph(
                graph_id=graph.graph_id,
                nodes=nodes,
                edges=tuple(e for e in edges if {e.source_node_id, e.target_node_id} <= node_ids),
            )
            if scoped != graph:
                scoped = scoped.model_copy(update={"graph_id": f"scoped:{digest(scoped)}"})
            self.capture(scoped.graph_id, scoped)
            self.graph_snapshot = scoped

    def decide(
        self,
        action: str,
        reason: str,
        nodes: tuple[str, ...] = (),
        *,
        disposition: Disposition | None = None,
        triggers: tuple[str, ...] = (),
    ) -> None:
        self.decisions.append(
            PlanDecision(
                sequence=len(self.decisions) + 1,
                action=action,
                reason=reason,
                affected_nodes=nodes,
                disposition=disposition,
                trigger_ids=triggers,
            )
        )

    def capture(self, artifact_id: str, value: ContractModel) -> None:
        content = value.model_dump_json()
        existing = next((a for a in self.artifacts if a.artifact_id == artifact_id), None)
        if existing is not None:
            if existing.canonical_json != content or existing.kind != type(value).__name__:
                raise ValueError("captured artifact ID reused for different content")
            return
        self.artifacts.append(
            CapturedArtifact(
                artifact_id=artifact_id,
                kind=type(value).__name__,
                canonical_json=content,
                checksum=digest(content),
            )
        )

    def time_left(self) -> float:
        left = self.request.budget.max_elapsed_seconds - (self.elapsed_clock() - self.elapsed_start)
        if self.request.deadline is not None:
            left = min(left, (self.request.deadline - self.wall_clock()).total_seconds())
        if left <= 0:
            self.stops.add(StopReason.DEADLINE_EXCEEDED)
        return max(0, left)

    def controlled_call[T](self, call: Callable[[], T]) -> T:
        """Bound waiting; uncooperative calls retain reservations, without cancellation claims."""
        if self.time_left() <= 0:
            raise TimeoutError("deadline before dispatch")
        executor = ThreadPoolExecutor(max_workers=1)
        try:
            return executor.submit(call).result(timeout=self.time_left())
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    def publish(self, references: tuple[AgentEvidenceReference, ...], reason: str) -> bool:
        changed = []
        a2_ids = {r.evidence_id for r in self.request.inventory.a2_pack.references}
        for ref in references:
            if ref.subject != self.request.subject or any(
                t is not None and t > self.request.as_of for t in (ref.observed_at, ref.acquired_at)
            ):
                raise ValueError("inadmissible evidence subject or point-in-time")
            if ref.evidence_id in a2_ids and ref != self.refs[ref.evidence_id]:
                raise ValueError("cannot overwrite immutable A2 evidence")
        for ref in references:
            if digest(ref) != digest(self.refs.get(ref.evidence_id)):
                self.refs[ref.evidence_id] = ref
                changed.append(ref.evidence_id)
        if changed:
            self.inventories.append(
                EvidenceInventory(
                    inventory_id=f"{self.request.run_id}:inventory:{len(self.inventories)}",
                    a2_pack=self.request.inventory.a2_pack,
                    references=tuple(r for i, r in sorted(self.refs.items()) if i not in a2_ids),
                )
            )
            self.decide("PUBLISH", reason, triggers=tuple(changed))
        return bool(changed)

    def acquire(self) -> None:
        required = {
            t
            for spec in self.plans[-1].registry
            if spec.capability.specialist.value in {n.node_id for n in self.plans[-1].nodes}
            for t in spec.hard_evidence
        }
        present = {
            r.evidence_type for r in self.refs.values() if r.availability in _USABLE and r.facts
        }
        for acquisition in sorted(self.services.acquisitions, key=lambda a: a.key()):
            available_metrics = {f.metric_id for r in self.refs.values() for f in r.facts}
            need = (
                acquisition.evidence_type in required - present
                or (
                    acquisition.material
                    and not set(acquisition.required_metrics) <= available_metrics
                )
                or acquisition.evidence_type in self.pending_need_types
            )
            if not need:
                self.decide("REUSE", "existing evidence satisfies acquisition scope")
                continue
            key = acquisition.key()
            permitted = acquisition.request.authority in self.request.allowed_capabilities and set(
                acquisition.request.allowed_authorities
            ) <= set(self.request.allowed_capabilities)
            disposition = missing_disposition(
                authorized=permitted,
                supported=self.services.router is not None,
                specific=bool(acquisition.required_metrics)
                or acquisition.evidence_type in required,
                pit_usable=True,
                budget_available=self.time_left() > 0,
                repeated=key in self.seen_needs,
            )
            if disposition is not Disposition.RECOVERABLE:
                self.decide("ACQUIRE_DENIED", disposition.value, disposition=disposition)
                continue
            self.seen_needs.add(key)
            cached = self.services.cached(acquisition)
            budget = AgentBudget() if cached else acquisition.request.budget
            operation = f"acquire:{key}"
            if not self.ledger.reserve(
                operation, budget, 0 if cached else acquisition.route.maximum_provider_calls
            ):
                self.stops.add(StopReason.BUDGET_EXHAUSTED)
                self.decide(
                    "ACQUIRE_DENIED", "reservation ceiling", disposition=Disposition.BUDGET_BLOCKED
                )
                continue
            try:
                run, reused = self.controlled_call(lambda: self.services.acquire(acquisition))
                self.ledger.settle(
                    operation,
                    AgentUsage() if reused else run.usage,
                    0 if reused else len(run.audits),
                )
                self.mi_runs.append(run)
                self.capture(run.run_id, run)
                self.publish(
                    normalized_references(run, acquisition.evidence_type),
                    "normalized capability result",
                )
                self.decide("ACQUIRE", "controlled capability route", triggers=(run.run_id,))
                for failure in run.failures:
                    self.gaps.add(f"ACQUISITION:{failure.kind.value}")
            except Exception:
                if (
                    next(r for r in self.ledger.entries() if r.accounting_id == operation).state
                    == "OUTSTANDING"
                ):
                    self.ledger.settle(operation, None)
                self.gaps.add("ACQUISITION_FAILED_USAGE_UNKNOWN")
                self.decide("ACQUIRE_FAILED", "controlled service failed; reservation held")

    def input_pack(self, node: PlanNode) -> tuple[AgentEvidencePack, str]:
        spec = next(
            s for s in self.plans[-1].registry if s.capability.specialist == node.specialist
        )
        refs = [
            r
            for r in self.refs.values()
            if r.evidence_type in node.evidence_types
            or (
                spec.include_baseline_facts
                and any(f.metric_id.startswith("baseline.") for f in r.facts)
            )
        ]
        for upstream in node.dependencies:
            projection = self.active_projections.get(upstream)
            if projection is not None and projection.reference is not None:
                refs.append(projection.reference)
        refs = sorted({r.evidence_id: r for r in refs}.values(), key=lambda r: r.evidence_id)
        if not refs:
            refs = [self.request.inventory.a2_pack.references[0]]
        usable = [r for r in refs if r.availability in _USABLE]
        types = {
            r.evidence_type
            for r in usable
            if r.facts
            and any(f.value not in {"UNKNOWN", "ABSTAIN", "INSUFFICIENT_EVIDENCE"} for f in r.facts)
        }
        expected = set(spec.hard_evidence)
        coverage = len(expected & types) / max(1, len(expected))
        if spec.required_metrics and not any(
            set(spec.required_metrics) <= {f.metric_id for f in r.facts}
            and set(spec.required_metadata) <= set(r.metadata)
            and r.metadata.get("active") is True
            for r in usable
        ):
            coverage = 0.0
        signature = invocation_digest(self.request, spec, tuple(refs))
        request_id = f"{self.request.run_id}:{node.node_id}:{signature}"
        pack = AgentEvidencePack(
            pack_id=f"pack:{request_id}",
            request_id=request_id,
            subject=self.request.subject,
            evidence_fingerprint=signature,
            references=tuple(refs),
            deterministic_assessment_id=self.request.inventory.a2_pack.deterministic_assessment_id,
            analysis_context_ids=self.request.inventory.a2_pack.analysis_context_ids,
            overall_quality=max(
                (r.quality for r in usable if r.quality is not None),
                key=_QUALITY.index,
                default=DataQuality.UNAVAILABLE,
            ),
            overall_freshness=max(
                (r.freshness for r in usable if r.freshness is not None),
                key=_FRESHNESS.index,
                default=FreshnessState.UNKNOWN,
            ),
            evidence_coverage=coverage,
            created_at=self.request.as_of,
        )
        return pack, signature

    def invoke(self, node: PlanNode, pack: AgentEvidencePack) -> AgentRunRecord:
        definition = self.registry.get(node.specialist).capability()
        request = AgentRequest(
            request_id=pack.request_id,
            run_id=pack.request_id,
            subject=self.request.subject,
            instrument_type=self.request.instrument.underlying_type
            or self.request.instrument.instrument_type,
            horizon=self.request.horizon,
            specialist=node.specialist,
            purpose=self.request.purpose,
            trade_style=self.request.trade_style,
            analysis_mode=self.request.analysis_mode,
            task="Interpret supplied evidence only; workflow has no investment authority.",
            a2_context_ids=pack.analysis_context_ids,
            a2_evidence_ids=tuple(r.evidence_id for r in self.request.inventory.a2_pack.references),
            deterministic_baseline_reference=pack.deterministic_assessment_id,
            evidence_fingerprint=pack.evidence_fingerprint,
            allowed_capabilities=definition.allowed_capabilities,
            budget=AgentBudget(max_elapsed_seconds=self.request.budget.max_elapsed_seconds),
            created_at=self.request.as_of,
            correlation_id=self.request.correlation_id,
        )
        return AgentRuntime(self.registry, wall_clock=lambda: self.request.as_of).run(request, pack)

    def consumption(self, node: PlanNode, pack: AgentEvidencePack) -> str:
        spec = next(
            s for s in self.plans[-1].registry if s.capability.specialist == node.specialist
        )
        return consumption_digest(self.request, spec, pack.references)

    def measured_invoke(
        self, node: PlanNode, pack: AgentEvidencePack
    ) -> tuple[AgentRunRecord, datetime, datetime]:
        started = self.wall_clock()
        record = self.invoke(node, pack)
        return record, started, self.wall_clock()

    def run_waves(self) -> None:
        plan = self.plans[-1]
        nodes = {n.node_id: n for n in plan.nodes}
        for wave in plan.waves:
            work: list[tuple[PlanNode, AgentEvidencePack, str, str]] = []
            for node_id in wave:
                node = nodes[node_id]
                pack, signature = self.input_pack(node)
                previous = self.active.get(node_id)
                if previous is not None and previous.consumed_digest == self.consumption(
                    node, pack
                ):
                    self.decide("REUSE", "consumed input unchanged", (node_id,))
                    continue
                if previous is not None:
                    index = self.attempts.index(previous)
                    self.attempts[index] = previous.model_copy(update={"superseded": True})
                    del self.active[node_id]
                    self.active_projections.pop(node_id, None)
                count = sum(
                    a.node_id == node_id and a.status is not NodeStatus.BLOCKED
                    for a in self.attempts
                )
                reason = None
                if count >= self.request.bounds.max_attempts_per_specialist:
                    reason = "ATTEMPT_LIMIT"
                elif (
                    sum(a.status is not NodeStatus.BLOCKED for a in self.attempts) + len(work)
                    >= self.request.bounds.max_invocations
                ):
                    reason = "INVOCATION_LIMIT"
                elif self.time_left() <= 0:
                    reason = "DEADLINE"
                operation = f"specialist:{node_id}:{len(self.attempts)}:{plan.version}"
                if reason is None and not self.ledger.reserve(
                    operation,
                    AgentBudget(
                        max_elapsed_seconds=self.request.budget.max_elapsed_seconds,
                    ),
                ):
                    reason = "BUDGET"
                if reason is not None:
                    self.gaps.add(f"{node_id}:{reason}")
                    self.stops.add(
                        StopReason.DEADLINE_EXCEEDED
                        if reason == "DEADLINE"
                        else StopReason.DEPTH_LIMIT
                        if reason in {"ATTEMPT_LIMIT", "INVOCATION_LIMIT"}
                        else StopReason.BUDGET_EXHAUSTED
                    )
                    self.attempts.append(
                        NodeAttempt(
                            node_id=node_id,
                            plan_version=plan.version,
                            status=NodeStatus.BLOCKED,
                            input_digest=signature,
                            consumed_digest=self.consumption(node, pack),
                            consumed_ids=tuple(r.evidence_id for r in pack.references),
                            reason=reason,
                        )
                    )
                    continue
                work.append((node, pack, signature, operation))
            executor = ThreadPoolExecutor(max_workers=len(work) or 1)
            futures = (
                [executor.submit(self.measured_invoke, node, pack) for node, pack, _, _ in work]
                if self.parallel
                else []
            )
            for index, (node, pack, signature, operation) in enumerate(work):
                record = None
                status = NodeStatus.FAILED
                failure_reason = None
                actual_start = actual_end = None
                try:
                    if not self.parallel and self.time_left() <= 0:
                        self.ledger.settle(operation, AgentUsage(), 0)
                        raise TimeoutError("not dispatched after deadline")
                    future = (
                        futures[index]
                        if self.parallel
                        else executor.submit(self.measured_invoke, node, pack)
                    )
                    record, actual_start, actual_end = future.result(timeout=self.time_left())
                    self.ledger.settle(operation, record.usage, 0)
                    status = (
                        NodeStatus.TIMED_OUT
                        if record.status is AgentRunStatus.TIMEOUT
                        else NodeStatus.FAILED
                        if record.status is AgentRunStatus.FAILED
                        else NodeStatus.BLOCKED
                        if record.status is AgentRunStatus.BUDGET_EXCEEDED
                        else NodeStatus.COMPLETED
                        if record.status is AgentRunStatus.SUCCESS
                        else NodeStatus.PARTIAL
                    )
                    if record.status is AgentRunStatus.TIMEOUT:
                        self.stops.add(StopReason.DEADLINE_EXCEEDED)
                    elif record.status is AgentRunStatus.BUDGET_EXCEEDED:
                        self.stops.add(StopReason.BUDGET_EXHAUSTED)
                except TimeoutError:
                    if (
                        next(r for r in self.ledger.entries() if r.accounting_id == operation).state
                        == "OUTSTANDING"
                    ):
                        self.ledger.settle(operation, None)
                    self.stops.add(StopReason.DEADLINE_EXCEEDED)
                    status = NodeStatus.TIMED_OUT
                    failure_reason = "DEADLINE_EXCEEDED_USAGE_HELD_IF_DISPATCHED"
                except Exception as exc:
                    if (
                        next(r for r in self.ledger.entries() if r.accounting_id == operation).state
                        == "OUTSTANDING"
                    ):
                        self.ledger.settle(operation, None)
                    failure_reason = type(exc).__name__
                attempt = NodeAttempt(
                    node_id=node.node_id,
                    plan_version=plan.version,
                    status=status,
                    input_digest=signature,
                    consumed_digest=self.consumption(node, pack),
                    consumed_ids=tuple(r.evidence_id for r in pack.references),
                    record=record,
                    reason=failure_reason,
                    started_at=actual_start,
                    completed_at=actual_end,
                )
                self.attempts.append(attempt)
                self.active[node.node_id] = attempt
                if record is not None and record.opinion is not None:
                    projection = project_opinion(record.opinion)
                    self.projections.append(projection)
                    self.active_projections[node.node_id] = projection
                self.decide("RUN", status.value, (node.node_id,))
            executor.shutdown(wait=False, cancel_futures=True)

    def inspect(self) -> bool:
        self.changed = False
        for revision in self.services.revisions:
            if revision.after_round == self.round:
                self.changed |= self.publish(revision.references, revision.reason)
        self.confirm()
        self.research()
        needs_acquisition = False
        for attempt in self.active.values():
            if attempt.record is None or attempt.record.opinion is None:
                continue
            for missing in attempt.record.opinion.missing_evidence:
                supported = tuple(
                    a
                    for a in self.services.acquisitions
                    if a.evidence_type == missing.evidence_type
                    and a.request.authority == missing.capability
                )
                disposition = missing_disposition(
                    authorized=missing.capability in self.request.allowed_capabilities,
                    supported=bool(supported),
                    specific=True,
                    pit_usable=True,
                    budget_available=self.time_left() > 0 and not self.ledger.exceeded,
                    repeated=bool(supported) and all(a.key() in self.seen_needs for a in supported),
                )
                self.decide(
                    "MISSING_EVIDENCE",
                    missing.reason,
                    (attempt.node_id,),
                    disposition=disposition,
                    triggers=(missing.missing_request_id,),
                )
                if disposition is Disposition.RECOVERABLE:
                    self.pending_need_types.add(missing.evidence_type)
                    needs_acquisition = True
        self.changed = needs_acquisition or (
            self.changed
            and any(
                self.consumption(node, self.input_pack(node)[0])
                != self.active[node.node_id].consumed_digest
                for node in self.plans[-1].nodes
                if node.node_id in self.active
            )
        )
        if not self.changed:
            return False
        if self.round >= min(
            self.request.bounds.max_replans, self.request.bounds.max_enrichment_rounds
        ):
            self.stops.add(StopReason.DEPTH_LIMIT)
            self.gaps.add("UPDATED_EVIDENCE_NOT_REINTERPRETED")
            # Prevent stale opinions being advertised as covering the admitted new snapshot.
            # Removing an upstream projection may invalidate a downstream consumer
            # even if that consumer does not subscribe to the revised raw family.
            for _ in self.plans[-1].nodes:
                invalidated = False
                for node in self.plans[-1].nodes:
                    active = self.active.get(node.node_id)
                    if (
                        active is not None
                        and self.consumption(node, self.input_pack(node)[0])
                        != active.consumed_digest
                    ):
                        self.attempts[self.attempts.index(active)] = active.model_copy(
                            update={"superseded": True}
                        )
                        del self.active[node.node_id]
                        self.active_projections.pop(node.node_id, None)
                        invalidated = True
                if not invalidated:
                    break
            return False
        self.round += 1
        self.plans.append(build_plan(self.request, self.plans[0].registry, version=self.round + 1))
        self.decide("REPLAN", "admitted consumed evidence changed")
        return True

    def confirm(self) -> None:
        for task in self.services.confirmation_tasks:
            if task.confirmation_id in self.confirmed_tasks:
                continue
            self.confirmed_tasks.add(task.confirmation_id)
            request = task.request
            material = AuthoritativeEscalationPolicy().evaluate(
                request.claim.materiality, request.materiality_triggers
            )
            permitted = (
                self.request.permit_confirmation
                and request.authority in self.request.allowed_capabilities
                and set(request.allowed_authorities) <= set(self.request.allowed_capabilities)
            )
            if (
                not permitted
                or not material.should_confirm
                or self.services.confirmation_gateway is None
            ):
                self.decide("CONFIRM_DENIED", "permission, materiality or route unavailable")
                continue
            if request.claim.subject != self.request.subject or request.as_of != self.request.as_of:
                raise ValueError("confirmation identity mismatch")
            if not set(request.claim.discovery_evidence_ids) <= set(self.refs):
                self.gaps.add("CONFIRMATION_DISCOVERY_NOT_CAPTURED")
                continue
            operation = f"confirm:{task.confirmation_id}"
            if not self.time_left() or not self.ledger.reserve(
                operation, request.budget, task.route_policy.maximum_provider_calls
            ):
                self.stops.add(StopReason.BUDGET_EXHAUSTED)
                continue
            try:
                gateway = self.services.confirmation_gateway
                result = self.controlled_call(
                    lambda: gateway.execute(
                        request,
                        task.route_policy,
                        run_id=task.run_id,
                        confirmation_id=task.confirmation_id,
                    )
                )
                self.ledger.settle(operation, result.usage, result.usage.tool_calls)
                self.confirmations.append(result)
                self.capture(task.confirmation_id, result)
                self.decide(
                    "CONFIRM", "material discovered claim", triggers=(task.confirmation_id,)
                )
                confirmation_fact = EvidenceFact(
                    fact_id=f"confirmation:{task.confirmation_id}:status",
                    kind=EvidenceFactKind.EVENT,
                    metric_id="event.confirmation_status",
                    value=result.status.value,
                    as_of=self.request.as_of,
                    quality=result.quality,
                    freshness=FreshnessState.UNKNOWN,
                    source_evidence=request.claim.discovery_evidence_ids,
                )
                ref = AgentEvidenceReference(
                    evidence_id=f"confirmation:{task.confirmation_id}",
                    evidence_type=EvidenceType.NEWS,
                    subject=self.request.subject,
                    producer_id="tiaf.authoritative-confirmation",
                    producer_version="1.0",
                    source=EvidenceSource.DERIVED,
                    availability=EvidenceStatus.PARTIAL,
                    quality=result.quality,
                    freshness=FreshnessState.UNKNOWN,
                    observed_at=self.request.as_of,
                    acquired_at=self.request.as_of,
                    checksum=result.semantic_fingerprint,
                    facts=(confirmation_fact,),
                    metadata={"confirmation_id": task.confirmation_id},
                )
                self.changed |= self.publish(
                    (ref,), "field-level authoritative confirmation status"
                )
                if result.unresolved_discrepancies or not result.confirmed_facts:
                    self.gaps.add(f"CONFIRMATION:{result.status.value}")
            except Exception:
                if (
                    next(r for r in self.ledger.entries() if r.accounting_id == operation).state
                    == "OUTSTANDING"
                ):
                    self.ledger.settle(operation, None)
                self.gaps.add("CONFIRMATION_UNAVAILABLE")

    def research(self) -> None:
        try:
            self._research()
        except Exception:
            self.gaps.add("RESEARCH_UNAVAILABLE")
            self.decide("RESEARCH_FAILED", "normalized research assembly unavailable")

    def _research(self) -> None:
        if self.researched or self.services.research_controller is None:
            return
        material = any(a.material for a in self.services.acquisitions)
        if not deep_research_allowed(self.request, material=material) or not self.mi_runs:
            self.decide(
                "RESEARCH_DENIED", "permission/depth/materiality or captured acquisition absent"
            )
            return
        self.researched = True
        # Exact executed subset only; never claim unexecuted capabilities were acquired.
        runs = tuple({r.request.capability: r for r in self.mi_runs}.values())
        request = MarketIntelligenceResearchRequest(
            research_request_id=f"{self.request.run_id}:research",
            subject=self.request.subject,
            as_of=self.request.as_of,
            horizon=self.request.horizon,
            capability_requests=tuple(r.request for r in runs),
            budget=self.request.budget,
        )
        policy = MarketIntelligenceResearchPolicy(
            plan_id="orchestration-captured-subset",
            plan_version="1.0",
            routes=tuple(r.policy for r in runs),
        )
        acquisition = MarketIntelligenceResearchRun(
            research_run_id=request.research_request_id,
            request=request,
            policy=policy,
            capability_runs=runs,
            usage=add_usage(tuple(r.usage for r in runs)),
            fingerprint=MarketIntelligenceResearchRun.fingerprint_for(request, policy, runs),
        )
        result = self.services.research_controller.assemble(
            acquisition,
            research_id=request.research_request_id,
            objective=self.request.purpose.value,
            depth=self.request.research_depth,
            a2_evidence_fingerprint=self.request.inventory.a2_pack.evidence_fingerprint,
            confirmations=tuple(self.confirmations),
            evidence_graph=self.graph_snapshot,
            prior_opinions=tuple(
                a.record.opinion
                for a in self.active.values()
                if a.record is not None and a.record.opinion is not None
            ),
        )
        self.capture(request.research_request_id, result)
        self.decide(
            "RESEARCH",
            "assembled captured normalized evidence; no new provider call",
            triggers=(request.research_request_id,),
        )

    def finalize(self, adapter: str) -> OrchestrationRunRecord:
        self.time_left()
        if self.ledger.exceeded:
            self.stops.add(StopReason.BUDGET_EXHAUSTED)
        opinions: tuple[AgentOpinionV2, ...] = tuple(
            a.record.opinion
            for _, a in sorted(self.active.items())
            if a.record is not None and a.record.opinion is not None
        )
        for node in self.plans[-1].nodes:
            attempt = self.active.get(node.node_id)
            if (
                attempt is None
                or attempt.record is None
                or attempt.record.status is not AgentRunStatus.SUCCESS
            ):
                if node.required:
                    self.gaps.add(f"{node.node_id}:INCOMPLETE_REQUIRED_COVERAGE")
        if not self.plans[-1].nodes:
            self.gaps.add("NO_APPLICABLE_REGISTERED_SPECIALISTS")
        if self.active and all(a.status is NodeStatus.FAILED for a in self.active.values()):
            self.stops.add(StopReason.TERMINAL_FAILURE)
        for opinion in opinions:
            self.gaps.update(m.missing_request_id for m in opinion.missing_evidence)
        if not self.stops:
            self.stops.add(
                StopReason.UNSUPPORTED_REMAINING if self.gaps else StopReason.REQUIRED_WORK_COMPLETE
            )
            if not self.gaps:
                self.stops.add(StopReason.EVIDENCE_SUFFICIENT)
        if any(o.status is AgentRunStatus.ABSTAINED for o in opinions):
            self.stops.add(StopReason.ABSTENTION_ACCEPTED)
        result = OrchestrationResult(
            run_id=self.request.run_id,
            status="PARTIAL"
            if StopReason.BUDGET_EXHAUSTED in self.stops
            or StopReason.DEADLINE_EXCEEDED in self.stops
            else "INSUFFICIENT_EVIDENCE"
            if not opinions
            else "ABSTAIN"
            if all(o.status is AgentRunStatus.ABSTAINED for o in opinions)
            else "PARTIAL"
            if self.gaps
            else "COMPLETE",
            opinions=opinions,
            a2_reference=self.request.inventory.a2_pack.deterministic_assessment_id,
            a2_fingerprint=self.request.inventory.a2_pack.evidence_fingerprint,
            gaps=tuple(sorted(self.gaps)),
            conflicts=tuple(
                sorted(
                    {
                        f"{o.specialist.value}:A2:{o.baseline_agreement.value}"
                        for o in opinions
                        if o.baseline_agreement.value in {"DISAGREES", "PARTIALLY_AGREES"}
                    }
                )
            ),
            stop_reasons=ordered_stops(self.stops),
            usage=add_usage(
                tuple(r.actual for r in self.ledger.entries() if r.actual is not None),
                elapsed=max(0, self.elapsed_clock() - self.elapsed_start),
            ),
            provider_calls=sum(r.actual_provider_calls or 0 for r in self.ledger.entries()),
            usage_is_complete=all(r.state == "SETTLED" for r in self.ledger.entries()),
            held_usage=add_usage(
                tuple(
                    reserved_usage(r.budget) for r in self.ledger.entries() if r.state != "SETTLED"
                )
            ),
            held_provider_calls=sum(
                r.provider_calls for r in self.ledger.entries() if r.state != "SETTLED"
            ),
            research_ids=tuple(
                a.artifact_id for a in self.artifacts if a.kind == "DeepResearchResult"
            ),
            confirmation_ids=tuple(
                a.artifact_id for a in self.artifacts if a.kind == "AuthoritativeConfirmationResult"
            ),
            graph_ids=tuple(
                a.artifact_id for a in self.artifacts if a.kind == "SparseEvidenceGraph"
            ),
            skipped=self.plans[-1].skipped,
            outcomes=tuple(
                NodeOutcome(
                    node_id=node.node_id,
                    status=NodeStatus.SUPERSEDED if attempt.superseded else attempt.status,
                    required=node.required,
                    reason=attempt.reason,
                    run_record_id=attempt.record.record_id if attempt.record else None,
                )
                for node in self.plans[-1].nodes
                for attempt in [
                    next(a for a in reversed(self.attempts) if a.node_id == node.node_id)
                ]
            ),
        )
        return OrchestrationRunRecord.seal(
            request=self.request,
            plans=tuple(self.plans),
            inventories=tuple(self.inventories),
            decisions=tuple(self.decisions),
            attempts=tuple(self.attempts),
            projections=tuple(self.projections),
            reservations=self.ledger.entries(),
            artifacts=tuple(self.artifacts),
            result=result,
            started_at=self.started_at,
            completed_at=self.wall_clock(),
            runtime_adapter=adapter,
        )


def run_serial(
    request: OrchestrationRequest,
    registry: AgentRegistry,
    services: ControlledServices | None = None,
) -> OrchestrationRunRecord:
    coordinator = OrchestrationCoordinator(registry, services)
    coordinator.initialize(request)
    while True:
        coordinator.acquire()
        coordinator.run_waves()
        if not coordinator.inspect():
            return coordinator.finalize("serial-1.0")
