"""Pure bounded workflow policy. No source selection or investment ranking."""

from tiaf.agents import AgentBudget, AgentEvidenceReference, AgentRegistry, SpecialistId
from tiaf.contracts import TradeStyle
from tiaf.data import InstrumentType
from tiaf.market_intelligence import ResearchDepth

from .digests import digest
from .models import (
    AnalysisPlan,
    Disposition,
    EvidenceTaskPlan,
    OrchestrationRequest,
    PlanNode,
    SkippedSpecialist,
    SpecialistDependencySpec,
    StopReason,
)

DOWNSTREAM = (SpecialistId.OPPORTUNITY_QUALITY, SpecialistId.OPPORTUNITY_RISK)
IMPLEMENTED = tuple(
    s
    for s in SpecialistId
    if s
    not in {
        SpecialistId.CONTRARIAN_HYPOTHESIS,
        SpecialistId.FORECAST_INTERPRETATION,
    }
)


def invocation_digest(
    request: OrchestrationRequest,
    spec: SpecialistDependencySpec,
    references: tuple[AgentEvidenceReference, ...],
) -> str:
    return digest(
        {
            "references": [r.model_dump(mode="json") for r in references],
            "policy": spec.model_dump(mode="json"),
            "horizon": request.horizon.model_dump(mode="json"),
            "instrument": request.instrument.model_dump(mode="json"),
            "purpose": request.purpose,
            "trade_style": request.trade_style,
            "analysis_mode": request.analysis_mode,
            "as_of": request.as_of.isoformat(),
            "a2_reference": request.inventory.a2_pack.deterministic_assessment_id,
            "a2_fingerprint": request.inventory.a2_pack.evidence_fingerprint,
        }
    )


def consumption_digest(
    request: OrchestrationRequest,
    spec: SpecialistDependencySpec,
    references: tuple[AgentEvidenceReference, ...],
) -> str:
    """Content/quality dependencies, separate from exact invocation serialization."""
    normalized = tuple(
        r.model_copy(update={"acquired_at": r.observed_at, "checksum": None}) for r in references
    )
    # These temporary copies are hash projections only, not validated evidence contracts.
    return invocation_digest(request, spec, normalized)


def dependencies(registry: AgentRegistry) -> tuple[SpecialistDependencySpec, ...]:
    result = []
    available = tuple(c.specialist for c in registry.capabilities() if c.specialist in IMPLEMENTED)
    for cap in registry.capabilities():
        if cap.specialist not in IMPLEMENTED:
            continue
        upstream = (
            tuple(s for s in available if s not in DOWNSTREAM)
            if (cap.specialist in DOWNSTREAM)
            else ()
        )
        if cap.specialist is SpecialistId.OPPORTUNITY_RISK:
            upstream = tuple(s for s in upstream if s is not SpecialistId.RELATIVE_STRENGTH)
        result.append(
            SpecialistDependencySpec(
                capability=cap,
                hard_evidence=cap.required_evidence_types,
                optional_evidence=cap.optional_evidence_types,
                upstream=upstream,
                required=cap.specialist is not SpecialistId.MACRO,
                include_baseline_facts=cap.specialist
                not in {
                    SpecialistId.FUNDAMENTAL,
                    SpecialistId.NEWS_EVENT,
                },
                required_metrics=(
                    "event.family",
                    "event.type",
                    "event.relevance",
                    "event.materiality",
                    "event.novelty",
                    "event.status",
                    "event.source_quality",
                )
                if cap.specialist is SpecialistId.NEWS_EVENT
                else (),
                required_metadata=("cluster_id", "active")
                if cap.specialist is SpecialistId.NEWS_EVENT
                else (),
            )
        )
    return tuple(result)


def build_plan(
    request: OrchestrationRequest,
    specs: tuple[SpecialistDependencySpec, ...],
    *,
    version: int = 1,
) -> AnalysisPlan:
    selected: list[SpecialistDependencySpec] = []
    skipped: list[SkippedSpecialist] = []
    instrument = request.instrument.underlying_type or request.instrument.instrument_type
    for spec in specs:
        sid = spec.capability.specialist
        reason: str | None = None
        unresolved = False
        if instrument not in spec.capability.supported_instrument_types:
            reason = "UNSUPPORTED_INSTRUMENT"
        elif not spec.capability.supports_no_llm:
            reason, unresolved = "NO_LLM_UNSUPPORTED", True
        elif sid is SpecialistId.MACRO and not request.include_macro:
            reason = "MACRO_NOT_REQUESTED"
        elif sid is SpecialistId.FUNDAMENTAL and request.trade_style is TradeStyle.DAY:
            reason = "DAY_SHALLOW_COMPANY_SCOPE"
        elif sid is SpecialistId.DERIVATIVES_CONTEXT and (
            instrument is InstrumentType.EQUITY and request.instrument.fno_eligible is not True
        ):
            unresolved = request.instrument.fno_eligible is None
            reason = "UNKNOWN_FNO_ELIGIBILITY" if unresolved else "ATTRIBUTED_NON_FNO"
        elif not set(spec.capability.allowed_capabilities) <= set(request.allowed_capabilities):
            reason, unresolved = "PERMISSION_DENIED", True
        elif len(selected) >= request.bounds.max_specialists:
            reason, unresolved = "SPECIALIST_CAP", True
        if reason is not None:
            skipped.append(SkippedSpecialist(specialist=sid, reason=reason, unresolved=unresolved))
        else:
            selected.append(spec)
    selected_ids = {s.capability.specialist for s in selected}
    nodes = tuple(
        PlanNode(
            node_id=spec.capability.specialist.value,
            specialist=spec.capability.specialist,
            dependencies=tuple(s.value for s in spec.upstream if s in selected_ids),
            required=spec.required,
            evidence_types=tuple(
                dict.fromkeys(
                    (
                        *spec.hard_evidence,
                        *spec.optional_evidence,
                    )
                )
            ),
        )
        for spec in selected
    )
    remaining = {n.node_id: n for n in nodes}
    complete: set[str] = set()
    waves: list[tuple[str, ...]] = []
    while remaining:
        ready = sorted(n for n, item in remaining.items() if set(item.dependencies) <= complete)
        if not ready:
            raise ValueError("cyclic dependency registry")
        wave = tuple(ready[: request.bounds.concurrency])
        waves.append(wave)
        complete.update(wave)
        for node_id in wave:
            del remaining[node_id]
    evidence_tasks = tuple(
        EvidenceTaskPlan(
            task_id=f"evidence:{kind.value}",
            kind="ACQUIRE",
            evidence_type=kind,
            consumers=tuple(
                s.capability.specialist.value for s in selected if kind in s.hard_evidence
            ),
            reason="reuse sufficient captured family or authorize a bounded capability read",
        )
        for kind in sorted({t for s in selected for t in s.hard_evidence}, key=lambda t: t.value)
    )
    if request.permit_confirmation:
        evidence_tasks += (
            EvidenceTaskPlan(
                task_id="material-confirmation",
                kind="CONFIRM",
                consumers=tuple(n.node_id for n in nodes if n.specialist in DOWNSTREAM),
                prerequisites=tuple(
                    n.node_id for n in nodes if n.specialist is SpecialistId.NEWS_EVENT
                ),
                reason="linked material claim, permitted configured route and reservation required",
            ),
        )
    if request.permit_deep_research:
        evidence_tasks += (
            EvidenceTaskPlan(
                task_id="normalized-research",
                kind="RESEARCH",
                consumers=tuple(n.node_id for n in nodes if n.specialist in DOWNSTREAM),
                reason="explicit depth, material need and normalized captured context required",
            ),
        )
    return AnalysisPlan(
        plan_id=f"{request.run_id}:plan:{version}",
        version=version,
        parent_version=version - 1 if version > 1 else None,
        request_digest=digest(request),
        registry=specs,
        nodes=nodes,
        skipped=tuple(skipped),
        waves=tuple(waves),
        bounds=request.bounds,
        evidence_tasks=evidence_tasks,
        specialist_budget=AgentBudget(max_elapsed_seconds=request.budget.max_elapsed_seconds),
    )


def missing_disposition(
    *,
    authorized: bool,
    supported: bool,
    specific: bool,
    pit_usable: bool,
    budget_available: bool,
    already_satisfied: bool = False,
    repeated: bool = False,
) -> Disposition:
    if not authorized:
        return Disposition.PERMISSION_DENIED
    if already_satisfied or repeated:
        return Disposition.NOT_WORTH_COST
    if not supported or not pit_usable:
        return Disposition.UNSUPPORTED
    if not specific:
        return Disposition.NOT_WORTH_COST
    if not budget_available:
        return Disposition.BUDGET_BLOCKED
    return Disposition.RECOVERABLE


def deep_research_allowed(request: OrchestrationRequest, *, material: bool) -> bool:
    return (
        request.permit_deep_research
        and (
            request.research_depth
            in {
                ResearchDepth.L2_INVESTMENT_RESEARCH,
                ResearchDepth.L3_DEEP_POSITION_INTELLIGENCE,
            }
        )
        and (material or request.purpose.value == "RESEARCH")
    )


def ordered_stops(reasons: set[StopReason]) -> tuple[StopReason, ...]:
    return tuple(reason for reason in StopReason if reason in reasons)


def affected_nodes(
    plan: AnalysisPlan, changed_ids: set[str], consumed: dict[str, set[str]]
) -> tuple[str, ...]:
    """Direct invalidation only; downstream propagation compares actual projected inputs."""
    return tuple(n.node_id for n in plan.nodes if consumed.get(n.node_id, set()) & changed_ids)
