"""Typed field projection, applicability and conservative shared-lineage grouping."""

from typing import Any

from tiaf.agents import AgentRunStatus, EvidenceImportance, SpecialistId
from tiaf.contracts import FreshnessState
from tiaf.planner.digests import digest
from tiaf.workflows.records import OrchestrationRunRecord

from .contracts import (
    CompletenessProfile,
    Contradiction,
    Facet,
    LineageGroup,
    OpportunitySynthesisPolicy,
    SourceLocator,
    SpecialistContribution,
    Truth,
)
from .handoff import detail

FIELDS: dict[str, tuple[str, ...]] = {
    "TECHNICAL": (
        "stance",
        "trend_state",
        "momentum_state",
        "structure_state",
        "breakout_state",
        "mtf_state",
        "extension_state",
        "remaining_room",
        "participation_state",
        "volatility_state",
    ),
    "FUNDAMENTAL": (
        "stance",
        "company_quality",
        "balance_sheet_state",
        "valuation_state",
        "cash_flow_state",
    ),
    "NEWS_EVENT": (
        "stance",
        "materiality",
        "execution_risk",
        "catalyst_direction",
        "contradiction_state",
    ),
    "RELATIVE_STRENGTH": ("stance", "relative_strength", "relative_consistency", "mtf_alignment"),
    "SECTOR": ("stance", "sector_state", "rotation_state"),
    "MACRO": ("stance", "market_risk_regime", "subject_sensitivity"),
    "DERIVATIVES_CONTEXT": ("stance", "volatility_state", "liquidity_state", "positioning_state"),
    "OPPORTUNITY_QUALITY": ("stance", "quality_state", "maturity_state", "remaining_room"),
    "OPPORTUNITY_RISK": ("stance", "risk_level"),
}
PRIMARY: dict[str, tuple[str, ...]] = {
    "TECHNICAL": ("stance", "extension_state", "remaining_room"),
    "FUNDAMENTAL": ("company_quality",),
    "NEWS_EVENT": ("materiality", "execution_risk"),
    "RELATIVE_STRENGTH": ("relative_strength",),
    "SECTOR": ("sector_state",),
    "MACRO": ("market_risk_regime",),
    "DERIVATIVES_CONTEXT": ("volatility_state", "liquidity_state"),
    "OPPORTUNITY_QUALITY": ("quality_state", "maturity_state", "remaining_room"),
    "OPPORTUNITY_RISK": ("risk_level",),
}
DOWNSTREAM = {SpecialistId.OPPORTUNITY_QUALITY, SpecialistId.OPPORTUNITY_RISK}
UNUSABLE = {
    "UNKNOWN",
    "INSUFFICIENT_EVIDENCE",
    "ABSTAIN",
    "SECTOR_POLICY_REQUIRED",
    "MAPPING_REQUIRED",
}


def project_contributions(
    record: OrchestrationRunRecord, policy: OpportunitySynthesisPolicy
) -> tuple[tuple[SpecialistContribution, ...], tuple[Contradiction, ...]]:
    result: list[SpecialistContribution] = []
    conflicts: list[Contradiction] = []
    active = {o.specialist: o for o in record.result.opinions}
    outcomes = {o.node_id: o for o in record.result.outcomes}
    for node in record.plans[-1].nodes:
        sid = node.specialist
        opinion = active.get(sid)
        common: dict[str, Any] = dict(
            specialist=sid,
            role="DOWNSTREAM_SUMMARY" if sid in DOWNSTREAM else "FIRST_ORDER",
            applicability="APPLICABLE",
            required=node.required,
            outcome=outcomes[node.node_id].status.value,
        )
        if opinion is None:
            result.append(SpecialistContribution(**common, reason="NO_ACTIVE_OPINION"))
            continue
        run = next(
            a.record
            for a in record.attempts
            if not a.superseded
            and a.record is not None
            and a.record.opinion is not None
            and a.record.opinion.opinion_id == opinion.opinion_id
        )
        assert run is not None
        decoded = detail(opinion)
        citations = tuple(
            sorted({c.evidence_id for claim in opinion.evidence_claims for c in claim.citations})
        )
        cited_references = tuple(
            r for r in run.evidence_pack.references if r.evidence_id in citations
        )
        base_usable = (
            opinion.status in {AgentRunStatus.SUCCESS, AgentRunStatus.PARTIAL}
            and opinion.evidence_quality in policy.usable_quality
            and opinion.evidence_freshness in policy.usable_freshness
            and (opinion.valid_until is None or opinion.valid_until > record.request.as_of)
            and bool(citations)
            and bool(decoded)
            and all(
                r.quality in policy.usable_quality
                and r.freshness in policy.usable_freshness
                and all(
                    f.quality in policy.usable_quality and f.freshness in policy.usable_freshness
                    for f in r.facts
                )
                for r in cited_references
            )
        )
        facets: list[Facet] = []
        for field in FIELDS[sid.value]:
            value = decoded.get(field)
            if not isinstance(value, str):
                continue
            source = SourceLocator(
                specialist=sid,
                opinion_id=opinion.opinion_id,
                run_id=run.record_id,
                schema_id=opinion.specialist_detail_schema_id,
                field=field,
                claim_ids=tuple(sorted(c.claim_id for c in opinion.evidence_claims)),
                evidence_ids=citations,
                fact_ids=tuple(
                    sorted(
                        {
                            f.fact_id
                            for r in run.evidence_pack.references
                            if r.evidence_id in citations
                            for f in r.facts
                        }
                    )
                ),
            )
            facets.append(
                Facet(
                    field=field,
                    value=value,
                    source=source,
                    usable=Truth.TRUE if base_usable and value not in UNUSABLE else Truth.UNKNOWN,
                )
            )
        usable_fields = {f.field for f in facets if f.usable is Truth.TRUE}
        if sid is SpecialistId.OPPORTUNITY_QUALITY:
            family_evidence = dict(decoded.get("evidence_ids_by_family", ()))
            for family in sorted(decoded.get("supportive_families", ())):
                ids = tuple(sorted(family_evidence.get(family, ())))
                if not ids or not set(ids) <= set(citations):
                    continue
                facets.append(
                    Facet(
                        field=f"supportive_families.{family}",
                        value="SUPPORTING",
                        usable=Truth.TRUE if base_usable else Truth.UNKNOWN,
                        source=SourceLocator(
                            specialist=sid,
                            opinion_id=opinion.opinion_id,
                            run_id=run.record_id,
                            schema_id=opinion.specialist_detail_schema_id,
                            field=f"supportive_families.{family}",
                            evidence_ids=ids,
                        ),
                    )
                )
        usable = Truth.TRUE if set(PRIMARY[sid.value]) <= usable_fields else Truth.UNKNOWN
        common.update(
            opinion_id=opinion.opinion_id,
            run_id=run.record_id,
            specialist_version=opinion.specialist_version,
            policy_version=opinion.policy_version,
            input_digest=opinion.evidence_fingerprint,
            stance=opinion.stance,
            usable=usable,
            facets=tuple(facets),
            confidence=opinion.confidence,
            confidence_basis=tuple(decoded.get("confidence_basis", ())),
            quality=opinion.evidence_quality,
            freshness=opinion.evidence_freshness,
            baseline_agreement=opinion.baseline_agreement.value,
            evidence_ids=citations,
            missing_ids=tuple(sorted(m.missing_request_id for m in opinion.missing_evidence)),
            material_missing_ids=tuple(
                sorted(
                    m.missing_request_id
                    for m in opinion.missing_evidence
                    if m.importance != EvidenceImportance.OPTIONAL
                )
            ),
            reason_codes=tuple(sorted(opinion.reason_codes)),
        )
        result.append(SpecialistContribution(**common))
        if opinion.baseline_agreement.value in {"DISAGREES", "PARTIALLY_AGREES"}:
            conflicts.append(
                Contradiction(
                    contradiction_id=f"baseline:{opinion.opinion_id}",
                    kind="BASELINE_DISAGREEMENT",
                    code=opinion.baseline_agreement.value,
                    blocking=Truth.FALSE,
                    sources=(
                        SourceLocator(
                            opinion_id=opinion.opinion_id,
                            run_id=run.record_id,
                            specialist=sid,
                            field="baseline_agreement",
                            evidence_ids=citations,
                        ),
                    ),
                )
            )
        for item in decoded.get("contradictions", []):
            # Preserve typed within-domain contradictions, not string-summary sentiment.
            cited = tuple(item.get("evidence_ids", ()))
            comparable = (
                sid == SpecialistId.TECHNICAL and item["code"] == "DIRECTIONAL_DIMENSION_CONFLICT"
            )
            conflicts.append(
                Contradiction(
                    contradiction_id=f"detail:{opinion.opinion_id}:{item['code']}",
                    kind="SAME_PROPOSITION" if comparable else "CROSS_DOMAIN_TENSION",
                    code=item["code"],
                    blocking=Truth.TRUE if comparable and cited else Truth.UNKNOWN,
                    sources=(
                        SourceLocator(
                            specialist=sid,
                            opinion_id=opinion.opinion_id,
                            run_id=run.record_id,
                            schema_id=opinion.specialist_detail_schema_id,
                            field=f"contradictions.{item['code']}",
                            evidence_ids=cited,
                        ),
                    ),
                )
            )
    explicit_scope = record.plans[-1].policy_version == "1.1"
    for skipped in record.result.skipped:
        required_absence = explicit_scope and skipped.required is True and skipped.reason in {
            "NOT_REGISTERED",
            "NO_LLM_UNSUPPORTED",
            "PERMISSION_DENIED",
            "SPECIALIST_CAP",
        }
        optional_absence = (
            explicit_scope
            and skipped.required is False
            and skipped.reason == "OPTIONAL_NOT_REGISTERED"
        )
        result.append(
            SpecialistContribution(
                specialist=skipped.specialist,
                role="DOWNSTREAM_SUMMARY" if skipped.specialist in DOWNSTREAM else "FIRST_ORDER",
                applicability=(
                    "APPLICABLE"
                    if required_absence or optional_absence
                    else "UNKNOWN"
                    if skipped.unresolved
                    else "NOT_APPLICABLE"
                ),
                required=required_absence,
                outcome="SKIPPED",
                reason=skipped.reason,
            )
        )
    return tuple(sorted(result, key=lambda c: c.specialist.value)), tuple(conflicts)


def completeness(
    contributions: tuple[SpecialistContribution, ...], gaps: tuple[str, ...]
) -> CompletenessProfile:
    def select(test: Any) -> tuple[SpecialistId, ...]:
        return tuple(c.specialist for c in contributions if test(c))

    required = select(lambda c: c.required and c.applicability == "APPLICABLE")
    usable = select(lambda c: c.usable is Truth.TRUE)
    return CompletenessProfile(
        required=required,
        optional=select(lambda c: not c.required and c.applicability == "APPLICABLE"),
        applicable=select(lambda c: c.applicability == "APPLICABLE"),
        not_applicable=select(lambda c: c.applicability == "NOT_APPLICABLE"),
        unknown_applicability=select(lambda c: c.applicability == "UNKNOWN"),
        usable=usable,
        partial=select(lambda c: c.outcome == "PARTIAL"),
        stale=select(lambda c: c.freshness is FreshnessState.STALE),
        missing=select(lambda c: c.applicability == "APPLICABLE" and c.usable is not Truth.TRUE),
        failed=select(lambda c: c.outcome == "FAILED"),
        blocked=select(lambda c: c.outcome in {"BLOCKED", "TIMED_OUT", "SUPERSEDED"}),
        numerator=len(set(required) & set(usable)),
        denominator=len(required),
        gaps=tuple(sorted(set(gaps))),
    )


def lineage_groups(
    record: OrchestrationRunRecord, contributions: tuple[SpecialistContribution, ...]
) -> tuple[LineageGroup, ...]:
    refs = {r.evidence_id: r for i in record.inventories for r in i.all_references()}
    refs.update(
        {
            p.reference.evidence_id: p.reference
            for p in record.projections
            if p.reference is not None
        }
    )
    for attempt in record.attempts:
        if attempt.record:
            refs.update({r.evidence_id: r for r in attempt.record.evidence_pack.references})

    def roots(ref_id: str, seen: frozenset[str] = frozenset()) -> set[str]:
        if ref_id in seen:
            return {ref_id}
        ref = refs.get(ref_id)
        if ref is None:
            return {ref_id}  # opaque source identifier, never a claim of independence
        parents = {p for f in ref.facts for p in f.source_evidence if p != ref_id}
        return set().union(*(roots(p, seen | {ref_id}) for p in parents)) if parents else {ref_id}

    groups: dict[str, tuple[set[str], set[str]]] = {}
    for c in contributions:
        if c.opinion_id is None:
            continue
        for ref_id in c.evidence_ids:
            for root in roots(ref_id):
                opinions, families = groups.setdefault(root, (set(), set()))
                opinions.add(c.opinion_id)
                families.add(refs[ref_id].evidence_type.value)
    return tuple(
        LineageGroup(
            lineage_id=digest(root),
            roots=(root,),
            opinion_ids=tuple(sorted(ids)),
            families=tuple(sorted(families)),
        )
        for root, (ids, families) in sorted(groups.items())
    )
