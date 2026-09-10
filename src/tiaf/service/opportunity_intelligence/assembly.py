"""Pure captured-input assembly. No acquisition, specialist or framework execution."""

from datetime import datetime
from time import monotonic
from typing import Literal

from tiaf.agents import AgentUsage
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.market_intelligence import (
    AuthoritativeConfirmationResult,
    DeepResearchResult,
    MarketIntelligenceRun,
    SparseEvidenceGraph,
)
from tiaf.planner.digests import digest
from tiaf.workflows.records import OrchestrationRunRecord

from .contracts import (
    ContextSummary,
    Contradiction,
    IntelligenceReason,
    IntelligenceRunRecord,
    OpportunityIntelligenceRequest,
    OrchestrationAuditLink,
    Prerequisite,
    SourceLocator,
    SpecialistContribution,
    StructuredOpportunityIntelligence,
    Truth,
)
from .contributions import completeness, lineage_groups, project_contributions
from .handoff import baseline_view, validate_handoff
from .policy import evaluate, require_supported_policy


def captured_context(
    record: OrchestrationRunRecord, contributions: tuple[SpecialistContribution, ...]
) -> tuple[
    tuple[ContextSummary, ...], tuple[Contradiction, ...], tuple[Prerequisite, ...], set[str]
]:
    contexts: list[ContextSummary] = []
    conflicts: list[Contradiction] = []
    needs: list[Prerequisite] = []
    invalidated: set[str] = set()
    represented_baseline = {
        f"{o.specialist.value}:A2:{o.baseline_agreement.value}"
        for o in record.result.opinions
        if o.baseline_agreement.value in {"DISAGREES", "PARTIALLY_AGREES"}
    }
    for code in sorted(record.result.conflicts):
        if code in represented_baseline:
            continue  # Already preserved as typed BASELINE_DISAGREEMENT, not a factual dispute.
        conflicts.append(
            Contradiction(
                contradiction_id=f"orchestration:{code}",
                kind="SOURCE_DISCREPANCY",
                code=code,
                blocking=Truth.UNKNOWN,
                sources=(SourceLocator(run_id=record.result.run_id, field="result.conflicts"),),
            )
        )
    for artifact in sorted(record.artifacts, key=lambda a: a.artifact_id):
        source = SourceLocator(field=artifact.kind, artifact_ids=(artifact.artifact_id,))
        if artifact.kind == "AuthoritativeConfirmationResult":
            confirmation = AuthoritativeConfirmationResult.model_validate_json(
                artifact.canonical_json
            )
            contexts.append(
                ContextSummary(
                    artifact_id=artifact.artifact_id,
                    kind=artifact.kind,
                    status=confirmation.status.value,
                    confirmed_fields=tuple(f.field_id for f in confirmation.confirmed_facts),
                    unresolved_fields=tuple(
                        f.field_id for f in confirmation.unresolved_discrepancies
                    ),
                )
            )
            conflicts.append(
                Contradiction(
                    contradiction_id=f"confirmation:{artifact.artifact_id}",
                    kind="AUTHORITATIVE_FIELD",
                    code=confirmation.status.value,
                    blocking=Truth.FALSE,
                    sources=(source,),
                )
            )
            if confirmation.unresolved_discrepancies:
                conflicts.append(
                    Contradiction(
                        contradiction_id=f"unresolved:{artifact.artifact_id}",
                        kind="SOURCE_DISCREPANCY",
                        code="UNRESOLVED_AUTHORITATIVE_FIELDS",
                        blocking=Truth.TRUE,
                        sources=(source,),
                    )
                )
            for c in contributions:
                if not set(c.evidence_ids) & set(confirmation.request.claim.discovery_evidence_ids):
                    continue
                run = next(
                    (
                        a.record
                        for a in record.attempts
                        if not a.superseded and a.record and a.record.record_id == c.run_id
                    ),
                    None,
                )
                admitted = run is not None and any(
                    r.metadata.get("confirmation_id") == artifact.artifact_id
                    for r in run.evidence_pack.references
                )
                if not admitted and (
                    confirmation.confirmed_facts or confirmation.unresolved_discrepancies
                ):
                    invalidated.add(c.specialist.value)
                    needs.append(
                        Prerequisite(
                            requirement_id=f"{artifact.artifact_id}:{c.specialist}",
                            source=source,
                            reason="CONFIRMATION_NOT_CONSUMED_BY_ACTIVE_OPINION",
                        )
                    )
            if confirmation.status.value in {"NOT_FOUND", "UNAVAILABLE", "OUT_OF_COVERAGE"}:
                needs.append(
                    Prerequisite(
                        requirement_id=confirmation.request.request_id,
                        source=source,
                        reason=f"CONFIRMATION_{confirmation.status.value}",
                    )
                )
        elif artifact.kind == "MarketIntelligenceRun":
            mi_run = MarketIntelligenceRun.model_validate_json(artifact.canonical_json)
            contexts.append(
                ContextSummary(
                    artifact_id=artifact.artifact_id,
                    kind=artifact.kind,
                    gaps=tuple(f.kind.value for f in mi_run.failures),
                )
            )
            for conflict in mi_run.contradictions:
                conflicts.append(
                    Contradiction(
                        contradiction_id=conflict.contradiction_id,
                        kind="SOURCE_DISCREPANCY",
                        code=conflict.resolution.value,
                        blocking=Truth.TRUE
                        if conflict.material and conflict.resolution.value == "UNRESOLVED"
                        else Truth.FALSE,
                        sources=(
                            source.model_copy(update={"evidence_ids": conflict.evidence_ids}),
                        ),
                    )
                )
            for batch in mi_run.batches:
                for item in batch.canonical_evidence:
                    if item.mapping_quality.value in {"PROVIDER_DEFINED", "AMBIGUOUS"}:
                        conflicts.append(
                            Contradiction(
                                contradiction_id=f"semantic:{item.evidence_id}",
                                kind="SOURCE_DISCREPANCY",
                                code=item.mapping_quality.value,
                                blocking=Truth.UNKNOWN,
                                sources=(
                                    source.model_copy(
                                        update={
                                            "field": item.metric,
                                            "evidence_ids": (item.evidence_id,),
                                        }
                                    ),
                                ),
                            )
                        )
        elif artifact.kind == "DeepResearchResult":
            research = DeepResearchResult.model_validate_json(artifact.canonical_json)
            contexts.append(
                ContextSummary(
                    artifact_id=artifact.artifact_id,
                    kind=artifact.kind,
                    gaps=tuple(g.gap_id for g in research.context.research_gaps),
                    epistemics=tuple(
                        sorted({a.kind.value for c in research.components for a in c.assertions})
                    ),
                )
            )
            for discrepancy in research.context.contradictions:
                conflicts.append(
                    Contradiction(
                        contradiction_id=f"research:{discrepancy.contradiction_id}",
                        kind="SOURCE_DISCREPANCY",
                        code=discrepancy.resolution.value,
                        blocking=Truth.TRUE
                        if discrepancy.material and discrepancy.resolution.value == "UNRESOLVED"
                        else Truth.FALSE,
                        sources=(
                            source.model_copy(
                                update={
                                    "evidence_ids": discrepancy.evidence_ids,
                                }
                            ),
                        ),
                    )
                )
            for ambiguous in research.context.ambiguous_evidence:
                conflicts.append(
                    Contradiction(
                        contradiction_id=f"research-ambiguous:{ambiguous.observation_id}",
                        kind="SOURCE_DISCREPANCY",
                        code="UNRESOLVED_SEMANTICS",
                        blocking=Truth.UNKNOWN,
                        sources=(source,),
                    )
                )
        elif artifact.kind == "SparseEvidenceGraph":
            graph = SparseEvidenceGraph.model_validate_json(artifact.canonical_json)
            contexts.append(
                ContextSummary(
                    artifact_id=artifact.artifact_id,
                    kind=artifact.kind,
                    epistemics=tuple(sorted({e.status.value for e in graph.edges})),
                )
            )
            for edge in graph.edges:
                if edge.contradiction_unresolved:
                    conflicts.append(
                        Contradiction(
                            contradiction_id=f"graph:{edge.edge_id}",
                            kind="SOURCE_DISCREPANCY",
                            code="UNRESOLVED_GRAPH_RELATION",
                            blocking=Truth.UNKNOWN,
                            sources=(
                                source.model_copy(
                                    update={
                                        "field": edge.edge_id,
                                        "evidence_ids": edge.provenance.evidence_ids,
                                    }
                                ),
                            ),
                        )
                    )
    return tuple(contexts), tuple(conflicts), tuple(needs), invalidated


def assemble_opportunity_intelligence(
    request: OpportunityIntelligenceRequest,
) -> IntelligenceRunRecord:
    started = monotonic()
    # Reconstruct even a frozen instance: nested source metadata may be mutable.
    request = OpportunityIntelligenceRequest.model_validate_json(request.model_dump_json())
    require_supported_policy(request.policy)
    record = validate_handoff(request)
    baseline = baseline_view(record)
    contributions, conflicts = project_contributions(record, request.policy)
    contexts, external_conflicts, needs, invalidated = captured_context(record, contributions)
    if invalidated:
        contributions = tuple(
            c.model_copy(
                update={
                    "usable": Truth.UNKNOWN,
                    "facets": tuple(
                        f.model_copy(update={"usable": Truth.UNKNOWN}) for f in c.facets
                    ),
                }
            )
            if c.specialist.value in invalidated
            else c
            for c in contributions
        )
    gaps = tuple(
        sorted(
            set(
                (
                    *record.result.gaps,
                    *(m for c in contributions for m in c.missing_ids),
                    *(n.requirement_id for n in needs),
                    *(
                        ("BASELINE_CONTENT_MISSING",)
                        if baseline.availability == "MISSING_CONTENT"
                        else ()
                    ),
                )
            )
        )
    )
    profile = completeness(contributions, gaps)
    summary, predicates, rules, conflicts = evaluate(
        request.policy,
        baseline,
        contributions,
        profile,
        (*conflicts, *external_conflicts),
        record.request.trade_style,
    )
    reasons: list[IntelligenceReason] = [
        IntelligenceReason(
            reason_id=digest(("baseline", baseline.assessment_id, summary.state)),
            code="UNCHANGED_A2_COMPARISON",
            category="CONTEXT",
            template_id="BENCHMARK_AND_OBSERVATION",
            parameters=(
                ("baseline_class", str(baseline.candidate_class)),
                ("observation_state", summary.state.value),
            ),
            sources=(SourceLocator(field="baseline", evidence_ids=baseline.evidence_ids),),
            epistemic="QUOTED_SOURCE",
            rule_ids=summary.matched_rules,
        )
    ]
    for c in contributions:
        for f in c.facets:
            if not f.source.evidence_ids:
                continue
            effects = {
                m.effect
                for m in request.policy.mappings
                if m.specialist == c.specialist and m.field == f.field and f.value in m.values
            }
            category: Literal["SUPPORT", "OPPOSITION", "RISK", "GAP", "CONTEXT"] = (
                "RISK"
                if effects & {"CHASE", "TIMING"} or f.field == "risk_level"
                else "OPPOSITION"
                if effects & {"QUALIFICATION", "COMPANY_CONFLICT"}
                else "SUPPORT"
                if "SUPPORT" in effects and f.usable is Truth.TRUE
                else "CONTEXT"
            )
            reasons.append(
                IntelligenceReason(
                    reason_id=digest((c.opinion_id, f.field, f.value)),
                    code="AVOID_CHASE" if "CHASE" in effects else f"{c.specialist}.{f.field}",
                    category=category,
                    template_id="QUOTED_TYPED_FIELD",
                    parameters=((f.field, f.value),),
                    sources=(f.source,),
                    epistemic="INFERENCE",
                    rule_ids=summary.matched_rules,
                )
            )
    for conflict in conflicts:
        reasons.append(
            IntelligenceReason(
                reason_id=digest(conflict.contradiction_id),
                code=conflict.code,
                category="OPPOSITION",
                template_id="CAPTURED_CONTRADICTION",
                parameters=(("kind", conflict.kind),),
                sources=conflict.sources,
                epistemic="QUOTED_SOURCE",
                rule_ids=summary.matched_rules,
            )
        )
    prerequisites = list(needs)
    for gap in profile.gaps:
        source = SourceLocator(field=f"orchestration.gaps:{gap}", run_id=record.result.run_id)
        prerequisites.append(
            Prerequisite(requirement_id=gap, source=source, reason="CAPTURED_PREREQUISITE")
        )
        reasons.append(
            IntelligenceReason(
                reason_id=digest(("gap", gap)),
                code="CAPTURED_GAP",
                category="GAP",
                template_id="CAPTURED_OUTCOME",
                parameters=(("requirement_id", gap),),
                sources=(source,),
                epistemic="WORKFLOW",
                rule_ids=summary.matched_rules,
            )
        )
    result = StructuredOpportunityIntelligence(
        intelligence_id=f"intelligence:{request.request_id}",
        request_id=request.request_id,
        subject=record.request.subject,
        instrument_type=record.request.instrument.underlying_type
        or record.request.instrument.instrument_type,
        purpose=record.request.purpose,
        trade_style=record.request.trade_style,
        horizon=record.request.horizon,
        as_of=record.request.as_of,
        policy_id=request.policy.policy_id,
        policy_version=request.policy.version,
        summary=summary,
        baseline=baseline,
        contributions=contributions,
        contradictions=conflicts,
        completeness=profile,
        reasons=tuple(sorted(reasons, key=lambda r: (r.category, r.code, r.reason_id))),
        lineages=lineage_groups(record, contributions),
        contexts=contexts,
        prerequisites=tuple(
            {
                p.requirement_id: p for p in sorted(prerequisites, key=lambda p: p.requirement_id)
            }.values()
        ),
        audit=OrchestrationAuditLink(
            run_id=record.result.run_id,
            semantic_fingerprint=record.fingerprint,
            capture_checksum=request.capture_checksum,
            active_opinion_ids=tuple(sorted(o.opinion_id for o in record.result.opinions)),
            superseded_opinion_ids=tuple(
                sorted(
                    a.record.opinion.opinion_id
                    for a in record.attempts
                    if a.superseded and a.record is not None and a.record.opinion is not None
                )
            ),
            stop_reasons=tuple(s.value for s in record.result.stop_reasons),
            imported_usage=record.result.usage,
            held_usage=record.result.held_usage,
            imported_provider_calls=record.result.provider_calls,
            held_provider_calls=record.result.held_provider_calls,
            usage_is_complete=record.result.usage_is_complete,
        ),
    )
    provisional = IntelligenceRunRecord.model_construct(
        request=request,
        result=result,
        predicates=predicates,
        rules=rules,
        assembled_at=datetime.now(TIAF_TIMEZONE),
        assembly_usage=AgentUsage(elapsed_seconds=monotonic() - started),
        fingerprint="0" * 64,
    )
    return IntelligenceRunRecord.model_validate(
        provisional.model_dump() | {"fingerprint": provisional.compute_fingerprint()}
    )
