"""Deterministic challenge generation over admitted A4 semantic projections."""

from collections.abc import Iterable

from tiaf.contracts import DataQuality, FreshnessState
from tiaf.planner.digests import digest
from tiaf.source_semantics import (
    A4SemanticInputProjection,
    AuthorityApplicability,
    ComparabilityStatus,
    DisputeState,
    IndependenceRelation,
    Missingness,
    SourceEntityRole,
)

from .contracts import (
    A4DeterministicPolicy,
    A4EvidenceNeed,
    ArgumentPremise,
    ChallengeFinding,
    InvestmentThesis,
    ResidualUncertainty,
)
from .enums import (
    A4EvidenceCapability,
    ChallengeFamily,
    ChallengeStatus,
    FindingSeverity,
    Materiality,
    PremiseRole,
    SupportState,
    UncertaintyKind,
)


class ChallengerError(ValueError):
    """The required deterministic challenge stage could not complete."""


def _qid(prefix: str, value: object) -> str:
    return f"{prefix}:{digest(value)[:24]}"


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def _finding(
    projection: A4SemanticInputProjection,
    thesis: InvestmentThesis,
    *,
    family: ChallengeFamily,
    reason_code: str,
    cited: Iterable[str],
    severity: FindingSeverity,
    materiality: Materiality,
    status: ChallengeStatus,
    premise_ref: str | None = None,
    dispute_refs: tuple[str, ...] = (),
    needs_evidence: bool = False,
    parent_run_id: str,
    requested_capability: A4EvidenceCapability | None = None,
) -> tuple[ChallengeFinding, A4EvidenceNeed | None]:
    cited_refs = _unique(cited)
    finding_id = _qid(
        "a4-finding",
        (
            projection.semantic_fingerprint,
            thesis.thesis_id,
            premise_ref,
            family,
            reason_code,
            cited_refs,
            dispute_refs,
        ),
    )
    need_id = _qid("a4-evidence-need", (finding_id, reason_code)) if needs_evidence else None
    finding = ChallengeFinding(
        finding_id=finding_id,
        challenged_thesis_ref=thesis.thesis_id,
        challenged_premise_ref=premise_ref,
        family=family,
        severity=severity,
        materiality=materiality,
        cited_opposition_refs=cited_refs,
        dispute_refs=dispute_refs,
        affected_conclusion=thesis.conclusion_relation,
        status=status,
        reason_code=reason_code,
        evidence_need_ref=need_id,
    )
    need = (
        A4EvidenceNeed(
            evidence_need_id=need_id,
            parent_a4_run_id=parent_run_id,
            parent_projection_id=projection.projection_id,
            parent_projection_fingerprint=projection.semantic_fingerprint,
            subject=projection.header.subject,
            objective=projection.header.objective,
            original_as_of=projection.header.evidence_as_of,
            semantic_question=reason_code,
            requested_evidence_family=family.value,
            requested_capability=requested_capability
            or (
                A4EvidenceCapability.AUTHORITATIVE_CONFIRMATION
                if family in {ChallengeFamily.SOURCE_BASIS, ChallengeFamily.THESIS_TENSION}
                else A4EvidenceCapability.EVENT_NEWS_CONTEXT
                if family is ChallengeFamily.FRESHNESS
                else A4EvidenceCapability.BOUNDED_DEEP_RESEARCH
            ),
            horizon=projection.header.horizon,
            challenge_refs=(finding_id,),
            dispute_refs=dispute_refs,
            materiality=materiality,
            reason_codes=(reason_code,),
            expected_resolvable_question=reason_code,
            minimum_source_roles=(
                SourceEntityRole.PUBLISHER,
                SourceEntityRole.ISSUER,
            ),
            require_independent_evidence=family is ChallengeFamily.SOURCE_BASIS,
            require_authoritative_source=family
            in {ChallengeFamily.SOURCE_BASIS, ChallengeFamily.THESIS_TENSION},
            allow_partial_evidence=False,
            required=materiality is not Materiality.NON_MATERIAL,
            dedupe_key=digest(
                (
                    projection.header.subject,
                    reason_code,
                    projection.semantic_fingerprint,
                    projection.header.evidence_as_of.isoformat(),
                )
            ),
            permitted_authority_refs=(projection.header.authority_ref,),
            budget_ref=projection.header.budget_ref,
            policy_id="a4-evidence-need-policy:deterministic",
            policy_version="1.0",
            created_at=projection.header.evidence_as_of,
        )
        if need_id is not None
        else None
    )
    return finding, need


def _resolved_scope_pairs(projection: A4SemanticInputProjection) -> set[frozenset[str]]:
    return {
        frozenset(item.assertion_ids)
        for item in projection.disputes
        if item.events[-1].state is DisputeState.RESOLVED_BY_SCOPE
    }


def generate_challenges(
    projection: A4SemanticInputProjection,
    policy: A4DeterministicPolicy,
    premises: tuple[ArgumentPremise, ...],
    primary: InvestmentThesis,
    counter: InvestmentThesis | None,
    *,
    parent_run_id: str,
) -> tuple[
    tuple[ChallengeFinding, ...],
    tuple[A4EvidenceNeed, ...],
    tuple[ResidualUncertainty, ...],
]:
    """Apply only declared checks; values and lower-layer metrics are never recomputed."""
    del policy
    findings: list[ChallengeFinding] = []
    needs: list[A4EvidenceNeed] = []

    def add(pair: tuple[ChallengeFinding, A4EvidenceNeed | None]) -> None:
        finding, need = pair
        findings.append(finding)
        if need is not None:
            needs.append(need)

    for gap in projection.gaps:
        required = gap.missingness is Missingness.REQUIRED
        add(
            _finding(
                projection,
                primary,
                family=ChallengeFamily.EVIDENCE_COVERAGE,
                reason_code=gap.code,
                cited=(gap.gap_id, gap.affected_reference),
                severity=FindingSeverity.HIGH if required else FindingSeverity.LOW,
                materiality=Materiality.MATERIAL if required else Materiality.NON_MATERIAL,
                status=ChallengeStatus.UPHELD if required else ChallengeStatus.QUALIFIED,
                needs_evidence=required,
                parent_run_id=parent_run_id,
                requested_capability=(
                    A4EvidenceCapability.COMPANY_FUNDAMENTALS
                    if any(
                        token in gap.affected_reference.casefold()
                        for token in ("revenue", "fundamental", "company")
                    )
                    else A4EvidenceCapability.BOUNDED_DEEP_RESEARCH
                ),
            )
        )
    for gap_id in projection.opportunity.a39_gap_ids:
        add(
            _finding(
                projection,
                primary,
                family=ChallengeFamily.EVIDENCE_COVERAGE,
                reason_code="CAPTURED_A39_REQUIRED_GAP",
                cited=(gap_id,),
                severity=FindingSeverity.HIGH,
                materiality=Materiality.MATERIAL,
                status=ChallengeStatus.UPHELD,
                needs_evidence=True,
                parent_run_id=parent_run_id,
            )
        )
    for excluded in projection.excluded_evidence:
        add(
            _finding(
                projection,
                primary,
                family=ChallengeFamily.EVIDENCE_COVERAGE,
                reason_code="EVIDENCE_EXCLUDED_BY_PROJECTION",
                cited=(excluded.evidence_id, excluded.reason),
                severity=FindingSeverity.LOW,
                materiality=Materiality.NON_MATERIAL,
                status=ChallengeStatus.QUALIFIED,
                parent_run_id=parent_run_id,
            )
        )
    if projection.opportunity.original_a2_candidate_class is None:
        add(
            _finding(
                projection,
                primary,
                family=ChallengeFamily.EVIDENCE_COVERAGE,
                reason_code="A2_BASELINE_PROJECTION_UNAVAILABLE",
                cited=(projection.parents.a2_assessment_id,),
                severity=FindingSeverity.CRITICAL,
                materiality=Materiality.MATERIAL,
                status=ChallengeStatus.UPHELD,
                needs_evidence=True,
                parent_run_id=parent_run_id,
            )
        )
    for authority in projection.authority_assessments:
        if authority.applicability is AuthorityApplicability.UNKNOWN or authority.limitations:
            cited = (authority.assessment_id, *authority.limitations)
            add(
                _finding(
                    projection,
                    primary,
                    family=ChallengeFamily.SOURCE_BASIS,
                    reason_code=(
                        "AUTHORITY_BASIS_UNKNOWN"
                        if authority.applicability is AuthorityApplicability.UNKNOWN
                        else "AUTHORITY_BASIS_LIMITED"
                    ),
                    cited=cited,
                    severity=FindingSeverity.HIGH,
                    materiality=Materiality.MATERIAL,
                    status=ChallengeStatus.UPHELD,
                    needs_evidence=True,
                    parent_run_id=parent_run_id,
                )
            )
    for relation in projection.independence:
        if relation.relation is not IndependenceRelation.INDEPENDENT:
            add(
                _finding(
                    projection,
                    primary,
                    family=ChallengeFamily.SOURCE_BASIS,
                    reason_code=f"SOURCE_DEPENDENCE_{relation.relation.value}",
                    cited=(
                        relation.assessment_id,
                        relation.left_occurrence_id,
                        relation.right_occurrence_id,
                        *relation.basis,
                    ),
                    severity=FindingSeverity.HIGH,
                    materiality=Materiality.MATERIAL,
                    status=ChallengeStatus.UPHELD,
                    needs_evidence=True,
                    parent_run_id=parent_run_id,
                )
            )
    resolved_scope = _resolved_scope_pairs(projection)
    for comparison in projection.comparisons:
        if comparison.status not in {
            ComparabilityStatus.NOT_COMPARABLE,
            ComparabilityStatus.UNDETERMINED,
        }:
            continue
        resolved = frozenset(comparison.assertion_ids) in resolved_scope
        add(
            _finding(
                projection,
                primary,
                family=ChallengeFamily.SOURCE_BASIS,
                reason_code=(
                    "SCOPE_MISMATCH_RESOLVED"
                    if resolved
                    else f"COMPARABILITY_{comparison.status.value}"
                ),
                cited=(comparison.comparison_id, *comparison.reasons),
                severity=FindingSeverity.LOW if resolved else FindingSeverity.HIGH,
                materiality=(
                    Materiality.NON_MATERIAL if resolved else Materiality.MATERIAL
                ),
                status=ChallengeStatus.RESOLVED if resolved else ChallengeStatus.UPHELD,
                needs_evidence=not resolved,
                parent_run_id=parent_run_id,
            )
        )
    for dispute in projection.disputes:
        final = dispute.events[-1]
        unresolved = final.state in {
            DisputeState.CONFIRMED_CONFLICT,
            DisputeState.UNRESOLVED,
        }
        resolved = final.state in {
            DisputeState.RESOLVED_BY_SCOPE,
            DisputeState.RESOLVED_BY_REVISION,
            DisputeState.RESOLVED_BY_AUTHORITATIVE_FIELD,
            DisputeState.SUPERSEDED,
        }
        add(
            _finding(
                projection,
                primary,
                family=(
                    ChallengeFamily.THESIS_TENSION
                    if unresolved
                    else ChallengeFamily.SOURCE_BASIS
                ),
                reason_code=f"DISPUTE_{final.state.value}",
                cited=(final.event_id, *final.evidence_ids),
                severity=FindingSeverity.HIGH if unresolved else FindingSeverity.LOW,
                materiality=(
                    Materiality.MATERIAL if unresolved else Materiality.NON_MATERIAL
                ),
                status=(
                    ChallengeStatus.UPHELD
                    if unresolved
                    else ChallengeStatus.RESOLVED
                    if resolved
                    else ChallengeStatus.QUALIFIED
                ),
                dispute_refs=(dispute.dispute_id,),
                needs_evidence=unresolved,
                parent_run_id=parent_run_id,
            )
        )
    premise_by_evidence = {
        evidence_ref: premise.premise_id
        for premise in premises
        for evidence_ref in premise.evidence_refs
    }
    for qualification in projection.evidence_qualifications:
        premise_ref = premise_by_evidence.get(qualification.evidence_id)
        if qualification.freshness in {FreshnessState.STALE, FreshnessState.UNKNOWN}:
            stale = qualification.freshness is FreshnessState.STALE
            add(
                _finding(
                    projection,
                    primary,
                    family=ChallengeFamily.FRESHNESS,
                    reason_code=("EVIDENCE_STALE" if stale else "FRESHNESS_UNKNOWN"),
                    cited=(qualification.evidence_id,),
                    severity=FindingSeverity.HIGH,
                    materiality=Materiality.MATERIAL,
                    status=ChallengeStatus.UPHELD,
                    premise_ref=premise_ref,
                    needs_evidence=not stale,
                    parent_run_id=parent_run_id,
                )
            )
        if qualification.quality in {DataQuality.DEGRADED, DataQuality.UNAVAILABLE}:
            unavailable = qualification.quality is DataQuality.UNAVAILABLE
            add(
                _finding(
                    projection,
                    primary,
                    family=ChallengeFamily.SOURCE_BASIS,
                    reason_code=f"EVIDENCE_QUALITY_{qualification.quality.value}",
                    cited=(qualification.evidence_id,),
                    severity=FindingSeverity.HIGH,
                    materiality=Materiality.MATERIAL,
                    status=ChallengeStatus.UPHELD,
                    premise_ref=premise_ref,
                    needs_evidence=unavailable,
                    parent_run_id=parent_run_id,
                )
            )
    for premise in premises:
        if premise.role is PremiseRole.ASSUMPTION and premise.support_state is SupportState.UNKNOWN:
            add(
                _finding(
                    projection,
                    primary,
                    family=ChallengeFamily.ASSUMPTION_SUPPORT,
                    reason_code="UNSUPPORTED_ASSUMPTION",
                    cited=(*premise.claim_refs, *premise.evidence_refs, *premise.reason_refs),
                    severity=FindingSeverity.HIGH,
                    materiality=Materiality.MATERIAL,
                    status=ChallengeStatus.UPHELD,
                    premise_ref=premise.premise_id,
                    needs_evidence=True,
                    parent_run_id=parent_run_id,
                )
            )
    a39_state = projection.opportunity.a39_state
    if projection.opportunity.original_a2_candidate_class == "NO_TRADE":
        add(
            _finding(
                projection,
                primary,
                family=ChallengeFamily.BASELINE_DIVERGENCE,
                reason_code="A2_NO_TRADE_HARD_GATE",
                cited=(
                    projection.parents.a2_assessment_id,
                    f"a2-class:{projection.opportunity.original_a2_candidate_class}",
                    f"a39-state:{a39_state}",
                ),
                severity=FindingSeverity.CRITICAL,
                materiality=Materiality.HARD_CONSTRAINT,
                status=ChallengeStatus.UPHELD,
                parent_run_id=parent_run_id,
            )
        )
    a2_direction = projection.opportunity.original_a2_direction
    directional_divergence = (
        a2_direction == "NEGATIVE" and a39_state in {"OPPORTUNITY", "WATCH"}
    ) or (a2_direction == "POSITIVE" and a39_state == "AVOID")
    if directional_divergence:
        add(
            _finding(
                projection,
                primary,
                family=ChallengeFamily.BASELINE_DIVERGENCE,
                reason_code="A2_A3_DIRECTIONAL_DIVERGENCE",
                cited=(
                    projection.parents.a2_assessment_id,
                    f"a2-direction:{a2_direction}",
                    f"a39-state:{a39_state}",
                ),
                severity=FindingSeverity.MEDIUM,
                materiality=Materiality.NON_MATERIAL,
                status=ChallengeStatus.QUALIFIED,
                parent_run_id=parent_run_id,
            )
        )
    if a39_state == "AVOID":
        add(
            _finding(
                projection,
                primary,
                family=ChallengeFamily.RISK_CONSTRAINT,
                reason_code="CAPTURED_A3_RISK_VETO",
                cited=(f"a39-state:{a39_state}", *projection.opportunity.a39_reason_ids),
                severity=FindingSeverity.CRITICAL,
                materiality=Materiality.HARD_CONSTRAINT,
                status=ChallengeStatus.UPHELD,
                parent_run_id=parent_run_id,
            )
        )
    elif a39_state == "WAIT":
        add(
            _finding(
                projection,
                primary,
                family=ChallengeFamily.TIMING_MATURITY,
                reason_code="CAPTURED_A3_TIMING_CONDITION",
                cited=(f"a39-state:{a39_state}", *projection.opportunity.a39_reason_ids),
                severity=FindingSeverity.MEDIUM,
                materiality=Materiality.MATERIAL,
                status=ChallengeStatus.UPHELD,
                parent_run_id=parent_run_id,
            )
        )
    elif a39_state == "INSUFFICIENT_EVIDENCE":
        add(
            _finding(
                projection,
                primary,
                family=ChallengeFamily.EVIDENCE_COVERAGE,
                reason_code="CAPTURED_A3_INSUFFICIENT_EVIDENCE",
                cited=(f"a39-state:{a39_state}", *projection.opportunity.a39_reason_ids),
                severity=FindingSeverity.CRITICAL,
                materiality=Materiality.MATERIAL,
                status=ChallengeStatus.UPHELD,
                needs_evidence=True,
                parent_run_id=parent_run_id,
            )
        )
    elif a39_state == "CONFLICTED" and not any(
        item.family is ChallengeFamily.THESIS_TENSION for item in findings
    ):
        add(
            _finding(
                projection,
                primary,
                family=ChallengeFamily.THESIS_TENSION,
                reason_code="CAPTURED_A3_CONFLICT",
                cited=(f"a39-state:{a39_state}", *projection.opportunity.a39_reason_ids),
                severity=FindingSeverity.HIGH,
                materiality=Materiality.MATERIAL,
                status=ChallengeStatus.UPHELD,
                parent_run_id=parent_run_id,
            )
        )
    elif a39_state not in {
        "OPPORTUNITY",
        "WATCH",
        "WAIT",
        "AVOID",
        "NO_TRADE",
        "CONFLICTED",
        "INSUFFICIENT_EVIDENCE",
    }:
        add(
            _finding(
                projection,
                primary,
                family=ChallengeFamily.ASSUMPTION_SUPPORT,
                reason_code="A3_STATE_OUTSIDE_SUPPORTED_POLICY",
                cited=(f"a39-state:{a39_state}",),
                severity=FindingSeverity.CRITICAL,
                materiality=Materiality.MATERIAL,
                status=ChallengeStatus.UNEVALUATED,
                parent_run_id=parent_run_id,
            )
        )
    if counter is not None and counter.conclusion_relation == "MATERIAL_OPPOSITION" and not any(
        item.family is ChallengeFamily.THESIS_TENSION for item in findings
    ):
        add(
            _finding(
                projection,
                primary,
                family=ChallengeFamily.THESIS_TENSION,
                reason_code="SUPPORTED_COUNTER_THESIS",
                cited=counter.support_refs,
                severity=FindingSeverity.HIGH,
                materiality=Materiality.MATERIAL,
                status=ChallengeStatus.UPHELD,
                parent_run_id=parent_run_id,
            )
        )
    ordered_findings = tuple(sorted(findings, key=lambda item: item.finding_id))
    uncertainties = tuple(
        ResidualUncertainty(
            uncertainty_id=_qid("a4-uncertainty", item.finding_id),
            affected_thesis_ref=item.challenged_thesis_ref,
            affected_premise_ref=item.challenged_premise_ref,
            kind=(
                UncertaintyKind.UNKNOWN
                if item.status in {ChallengeStatus.UPHELD, ChallengeStatus.UNEVALUATED}
                else UncertaintyKind.KNOWN_LIMITATION
            ),
            materiality=item.materiality,
            consequence_code=f"UNRESOLVED_{item.family.value}",
            resolution_requirement=(
                "ADMIT_ELIGIBLE_EVIDENCE"
                if item.evidence_need_ref is not None
                else "REVIEW_DECLARED_RULE"
            ),
            evidence_need_refs=(
                (item.evidence_need_ref,) if item.evidence_need_ref is not None else ()
            ),
        )
        for item in ordered_findings
        if item.status is not ChallengeStatus.RESOLVED
    )
    return (
        ordered_findings,
        tuple(sorted(needs, key=lambda item: item.need_id)),
        uncertainties,
    )
