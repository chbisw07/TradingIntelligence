"""Deterministic premise resolution and bounded primary/counter thesis construction."""

from collections.abc import Iterable

from tiaf.planner.digests import digest
from tiaf.source_semantics import (
    A4SemanticInputProjection,
    AssertionValueKind,
    DisputeState,
    EpistemicMappingStatus,
    EpistemicRole,
)

from .contracts import (
    A4DeterministicPolicy,
    ArgumentPremise,
    InvalidationCondition,
    InvestmentThesis,
)
from .enums import (
    InvalidationKind,
    PremisePolarity,
    PremiseRole,
    ScopeRelevance,
    SupportState,
    ThesisRole,
    ThesisSupport,
)


class ThesisConstructionError(ValueError):
    """Admitted input cannot form the minimum bounded A4 thesis graph."""


def _qid(prefix: str, value: object) -> str:
    return f"{prefix}:{digest(value)[:24]}"


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def _qualification_id(evidence_id: str) -> str:
    return _qid("evidence-qualification", evidence_id)


def _reason_universe(projection: A4SemanticInputProjection) -> set[str]:
    return {
        *projection.opportunity.a39_reason_ids,
        *projection.opportunity.a39_gap_ids,
        *projection.opportunity.active_opinion_ids,
        *projection.opportunity.superseded_opinion_ids,
        projection.parents.a2_assessment_id,
        f"a39-state:{projection.opportunity.a39_state}",
        *(
            (f"a2-class:{projection.opportunity.original_a2_candidate_class}",)
            if projection.opportunity.original_a2_candidate_class
            else ()
        ),
        *(item.gap_id for item in projection.gaps),
        *(item.code for item in projection.gaps),
        *(item.dispute_id for item in projection.disputes),
        *(ref for item in projection.assertions for ref in item.original_claim_ids),
    }


def validate_premise(
    premise: ArgumentPremise,
    projection: A4SemanticInputProjection,
) -> ArgumentPremise:
    """Resolve every premise edge against admitted projection identities."""
    assertions = {item.assertion_id: item for item in projection.assertions}
    evidence = {item.evidence_id for item in projection.occurrences}
    propositions = {item.proposition.proposition_id for item in projection.assertions}
    comparisons = {item.comparison_id for item in projection.comparisons}
    qualifications = {
        *(item.assessment_id for item in projection.authority_assessments),
        *(item.assessment_id for item in projection.independence),
        *(_qualification_id(item.evidence_id) for item in projection.evidence_qualifications),
    }
    if not set(premise.claim_refs) <= set(assertions):
        raise ThesisConstructionError("premise claim reference is not admitted")
    if not set(premise.evidence_refs) <= evidence:
        raise ThesisConstructionError("premise evidence reference is not admitted")
    if not set(premise.reason_refs) <= _reason_universe(projection):
        raise ThesisConstructionError("premise reason reference is not admitted")
    if not set(premise.proposition_refs) <= propositions:
        raise ThesisConstructionError("premise proposition reference is not admitted")
    if not set(premise.comparison_refs) <= comparisons:
        raise ThesisConstructionError("premise comparison reference is not admitted")
    if not set(premise.source_qualification_refs) <= qualifications:
        raise ThesisConstructionError("premise source qualification is not admitted")
    if premise.role is PremiseRole.FACT and not premise.claim_refs:
        raise ThesisConstructionError("fact premise requires an admitted assertion")
    for claim_ref in premise.claim_refs:
        assertion = assertions[claim_ref]
        if (
            premise.role is PremiseRole.FACT
            and assertion.epistemic_role is not EpistemicRole.FACT
        ):
            raise ThesisConstructionError("non-factual assertion cannot be promoted to fact")
        if assertion.proposition.proposition_id not in premise.proposition_refs:
            raise ThesisConstructionError("premise claim and proposition references disagree")
        assertion_evidence = {
            occurrence.evidence_id
            for occurrence in projection.occurrences
            if occurrence.occurrence_id in assertion.occurrence_ids
        }
        if not assertion_evidence <= set(premise.evidence_refs):
            raise ThesisConstructionError("premise omits claim evidence occurrence")
    return premise


def validate_premises(
    premises: tuple[ArgumentPremise, ...],
    projection: A4SemanticInputProjection,
) -> tuple[ArgumentPremise, ...]:
    """Resolve dependencies and reject cycles or fact promotion."""
    validated = tuple(validate_premise(item, projection) for item in premises)
    by_id = {item.premise_id: item for item in validated}
    if len(by_id) != len(validated):
        raise ThesisConstructionError("premise IDs must be unique")
    if any(not set(item.dependency_refs) <= set(by_id) for item in validated):
        raise ThesisConstructionError("premise dependency is unresolved")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(premise_id: str) -> None:
        if premise_id in visiting:
            raise ThesisConstructionError("premise dependency cycle")
        if premise_id in visited:
            return
        visiting.add(premise_id)
        for dependency in by_id[premise_id].dependency_refs:
            visit(dependency)
        visiting.remove(premise_id)
        visited.add(premise_id)

    for premise_id in by_id:
        visit(premise_id)
    return validated


def _primary_premises(
    projection: A4SemanticInputProjection,
) -> list[ArgumentPremise]:
    a39_state = projection.opportunity.a39_state
    state_support = (
        SupportState.TRUE
        if a39_state in {"OPPORTUNITY", "WATCH", "WAIT"}
        else SupportState.FALSE
        if a39_state == "AVOID"
        else SupportState.UNKNOWN
    )
    reasons = _unique(
        (
            f"a39-state:{a39_state}",
            *projection.opportunity.a39_reason_ids,
            *projection.opportunity.active_opinion_ids,
        )
    )
    premises = [
        ArgumentPremise(
            premise_id="a4-premise:captured-a39-observation",
            role=PremiseRole.INFERENCE,
            polarity=PremisePolarity.SUPPORTS,
            reason_refs=reasons,
            support_state=state_support,
            reason_code=f"CAPTURED_A39_{a39_state}",
            scope_relevance=ScopeRelevance.APPLICABLE,
            horizon_relevant=True,
        )
    ]
    a2_class = projection.opportunity.original_a2_candidate_class
    premises.append(
        ArgumentPremise(
            premise_id="a4-premise:unchanged-a2-gate",
            role=PremiseRole.INFERENCE,
            polarity=PremisePolarity.SUPPORTS,
            reason_refs=_unique(
                (
                    projection.parents.a2_assessment_id,
                    *((f"a2-class:{a2_class}",) if a2_class else ()),
                )
            ),
            support_state=(
                SupportState.FALSE
                if a2_class == "NO_TRADE"
                else SupportState.TRUE
                if a2_class is not None
                else SupportState.UNKNOWN
            ),
            reason_code="UNCHANGED_A2_GATE",
            scope_relevance=ScopeRelevance.APPLICABLE,
            horizon_relevant=True,
        )
    )
    epistemic = {item.assertion_id: item for item in projection.epistemic_projections}
    for assertion in projection.assertions:
        mapped = epistemic.get(assertion.assertion_id)
        role = (
            PremiseRole.ASSUMPTION
            if assertion.epistemic_role is EpistemicRole.HYPOTHESIS
            else PremiseRole.INFERENCE
            if assertion.epistemic_role is EpistemicRole.INFERENCE
            else PremiseRole.FACT
        )
        support = (
            SupportState.UNKNOWN
            if assertion.value.kind is AssertionValueKind.MISSING
            or assertion.epistemic_role is EpistemicRole.HYPOTHESIS
            or mapped is None
            or mapped.mapping_status
            in {EpistemicMappingStatus.UNMAPPED, EpistemicMappingStatus.UNKNOWN}
            else SupportState.TRUE
        )
        evidence_refs = _unique(
            occurrence.evidence_id
            for occurrence in projection.occurrences
            if occurrence.occurrence_id in assertion.occurrence_ids
        )
        qualification_refs = _unique(
            (
                *(
                    item.assessment_id
                    for item in projection.authority_assessments
                    if item.scope.predicate_id == assertion.proposition.predicate_id
                ),
                *(
                    _qualification_id(item.evidence_id)
                    for item in projection.evidence_qualifications
                    if item.evidence_id in evidence_refs
                ),
            )
        )
        premises.append(
            ArgumentPremise(
                premise_id=_qid("a4-premise", assertion.assertion_id),
                role=role,
                polarity=PremisePolarity.QUALIFIES,
                claim_refs=(assertion.assertion_id,),
                evidence_refs=evidence_refs,
                reason_refs=assertion.original_claim_ids,
                proposition_refs=(assertion.proposition.proposition_id,),
                source_qualification_refs=qualification_refs,
                support_state=support,
                reason_code=(
                    "UNSUPPORTED_ASSUMPTION"
                    if role is PremiseRole.ASSUMPTION and support is SupportState.UNKNOWN
                    else "ADMITTED_ASSERTION"
                ),
                scope_relevance=(
                    ScopeRelevance.APPLICABLE
                    if assertion.proposition.horizon in {None, projection.header.horizon}
                    else ScopeRelevance.NOT_APPLICABLE
                ),
                horizon_relevant=assertion.proposition.horizon
                in {None, projection.header.horizon},
            )
        )
    return premises


def _counter_basis(projection: A4SemanticInputProjection) -> tuple[str, tuple[str, ...]] | None:
    unresolved = tuple(
        item.dispute_id
        for item in projection.disputes
        if item.events[-1].state
        in {DisputeState.CONFIRMED_CONFLICT, DisputeState.UNRESOLVED}
    )
    if unresolved or projection.opportunity.a39_state == "CONFLICTED":
        return "MATERIAL_OPPOSITION", _unique(
            (*unresolved, f"a39-state:{projection.opportunity.a39_state}")
        )
    if projection.opportunity.a39_state == "AVOID":
        return "RISK_DOMINANT", _unique(
            (
                f"a39-state:{projection.opportunity.a39_state}",
                *projection.opportunity.a39_reason_ids,
            )
        )
    if projection.opportunity.a39_state == "WAIT":
        return "TIMING_ALTERNATIVE", _unique(
            (
                f"a39-state:{projection.opportunity.a39_state}",
                *projection.opportunity.a39_reason_ids,
            )
        )
    return None


def build_theses(
    projection: A4SemanticInputProjection,
    policy: A4DeterministicPolicy,
) -> tuple[tuple[ArgumentPremise, ...], InvestmentThesis, InvestmentThesis | None]:
    premises = _primary_premises(projection)
    primary_id = _qid("a4-thesis", (projection.semantic_fingerprint, "PRIMARY"))
    assumption_refs = tuple(
        item.premise_id
        for item in premises
        if item.role is PremiseRole.ASSUMPTION and item.horizon_relevant
    )
    primary_premise_refs = (
        "a4-premise:captured-a39-observation",
        "a4-premise:unchanged-a2-gate",
        *assumption_refs,
    )
    primary_support = (
        ThesisSupport.REFUTED
        if any(
            item.support_state is SupportState.FALSE
            for item in premises
            if item.premise_id in primary_premise_refs
        )
        else ThesisSupport.UNDETERMINED
        if any(
            item.support_state is SupportState.UNKNOWN
            for item in premises
            if item.premise_id in primary_premise_refs
        )
        else ThesisSupport.CONDITIONAL
        if projection.opportunity.a39_state in {"WATCH", "WAIT"}
        else ThesisSupport.SUPPORTED
    )
    primary_condition = InvalidationCondition(
        condition_id=_qid("a4-condition", (primary_id, "primary-premise")),
        premise_ref="a4-premise:captured-a39-observation",
        kind=InvalidationKind.PREMISE_NO_LONGER_TRUE,
        cited_refs=(f"a39-state:{projection.opportunity.a39_state}",),
        reason_code="CAPTURED_A39_STATE_CHANGES",
    )
    primary = InvestmentThesis(
        thesis_id=primary_id,
        role=ThesisRole.PRIMARY,
        parent_a2_assessment_ref=projection.parents.a2_assessment_id,
        parent_a3_package_ref=projection.parents.a3_package_id,
        parent_a39_fingerprint_ref=projection.parents.a39_semantic_fingerprint,
        subject=projection.header.subject,
        objective=projection.header.objective,
        horizon=projection.header.horizon,
        directional_interpretation=projection.opportunity.original_a2_direction,
        premise_refs=primary_premise_refs,
        assumption_refs=assumption_refs,
        support_refs=projection.opportunity.a39_reason_ids,
        opposition_refs=tuple(item.dispute_id for item in projection.disputes),
        gaps=_unique(
            (*projection.opportunity.a39_gap_ids, *(item.code for item in projection.gaps))
        ),
        risks=(
            _unique(projection.opportunity.a39_reason_ids)
            if projection.opportunity.a39_state == "AVOID"
            else ()
        ),
        invalidation_conditions=(primary_condition,),
        conclusion_relation="CAPTURED_UNDERLYING_THESIS",
        conclusion_policy_id=policy.policy_id,
        support=primary_support,
    )
    counter: InvestmentThesis | None = None
    basis = _counter_basis(projection)
    if basis is not None:
        relation, refs = basis
        counter_premise = ArgumentPremise(
            premise_id=_qid("a4-premise", (projection.semantic_fingerprint, relation)),
            role=PremiseRole.INFERENCE,
            polarity=PremisePolarity.OPPOSES,
            reason_refs=refs,
            support_state=SupportState.TRUE,
            reason_code=relation,
            scope_relevance=ScopeRelevance.APPLICABLE,
            horizon_relevant=True,
        )
        premises.append(counter_premise)
        counter_id = _qid("a4-thesis", (projection.semantic_fingerprint, "COUNTER", relation))
        counter_condition = InvalidationCondition(
            condition_id=_qid("a4-condition", (counter_id, relation)),
            premise_ref=counter_premise.premise_id,
            kind=(
                InvalidationKind.TIMING_CONDITION_RESOLVED
                if relation == "TIMING_ALTERNATIVE"
                else InvalidationKind.RISK_CONSTRAINT_REMOVED
                if relation == "RISK_DOMINANT"
                else InvalidationKind.ELIGIBLE_REVISION_CONTRADICTS
            ),
            cited_refs=refs,
            reason_code=f"{relation}_NO_LONGER_APPLIES",
        )
        counter = InvestmentThesis(
            thesis_id=counter_id,
            role=ThesisRole.COUNTER,
            opposed_thesis_ref=primary_id,
            parent_a2_assessment_ref=projection.parents.a2_assessment_id,
            parent_a3_package_ref=projection.parents.a3_package_id,
            parent_a39_fingerprint_ref=projection.parents.a39_semantic_fingerprint,
            subject=projection.header.subject,
            objective=projection.header.objective,
            horizon=projection.header.horizon,
            premise_refs=(counter_premise.premise_id,),
            support_refs=refs,
            opposition_refs=primary.support_refs,
            invalidation_conditions=(counter_condition,),
            conclusion_relation=relation,
            conclusion_policy_id=policy.policy_id,
            support=(
                ThesisSupport.CONDITIONAL
                if relation == "TIMING_ALTERNATIVE"
                else ThesisSupport.SUPPORTED
            ),
        )
    validated = validate_premises(tuple(premises), projection)
    return validated, primary, counter
