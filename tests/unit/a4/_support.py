"""Synthetic admitted A4 projections for deterministic policy scenarios."""

from functools import lru_cache

from tiaf.contracts import DataQuality, FreshnessState
from tiaf.planner.digests import digest
from tiaf.source_semantics import (
    A4SemanticInputProjection,
    AssertionIdentity,
    AuthorityApplicability,
    ComparabilityStatus,
    ComparisonAssessment,
    DisputeEvent,
    DisputeState,
    EpistemicRole,
    EvidenceQualification,
    ExcludedEvidence,
    IndependenceAssessment,
    IndependenceDimension,
    IndependenceRelation,
    Missingness,
    ProjectionBuildInput,
    ProjectionGap,
    append_dispute_event,
    build_projection,
    compare_assertions,
    create_dispute,
    validate_projection,
)
from tiaf.source_semantics.projection import projection_semantic_payload

from ..source_semantics._support import (
    NOW,
    assertion,
    build_input,
    occurrence,
    proposition,
)


@lru_cache(maxsize=1)
def clean_projection() -> A4SemanticInputProjection:
    return build_projection(build_input())


def reseal(
    projection: A4SemanticInputProjection,
    **updates: object,
) -> A4SemanticInputProjection:
    provisional = projection.model_copy(
        update={
            **updates,
            "projection_id": "a4-input:pending",
            "semantic_fingerprint": "0" * 64,
        }
    )
    fingerprint = digest(projection_semantic_payload(provisional))
    return validate_projection(
        provisional.model_copy(
            update={
                "projection_id": f"a4-input:{fingerprint[:24]}",
                "semantic_fingerprint": fingerprint,
            }
        )
    )


def with_state(
    state: str,
    *,
    a2_class: str | None = "EARLY_OPPORTUNITY",
    a2_direction: str | None = "POSITIVE",
) -> A4SemanticInputProjection:
    base = clean_projection()
    opportunity = base.opportunity.model_copy(
        update={
            "a39_state": state,
            "original_a2_candidate_class": a2_class,
            "original_a2_direction": a2_direction,
        }
    )
    return reseal(base, opportunity=opportunity)


def with_gap(required: bool = True) -> A4SemanticInputProjection:
    base = clean_projection()
    gap = ProjectionGap(
        gap_id="gap:a4-required-evidence" if required else "gap:a4-optional-evidence",
        missingness=Missingness.REQUIRED if required else Missingness.OPTIONAL,
        code="REQUIRED_EVIDENCE_UNAVAILABLE" if required else "OPTIONAL_EVIDENCE_UNAVAILABLE",
        affected_reference="proposition:revenue",
        reason="captured semantic fixture",
    )
    return reseal(base, gaps=(gap,))


def with_unknown_authority() -> A4SemanticInputProjection:
    base = clean_projection()
    authority = base.authority_assessments[0].model_copy(
        update={"applicability": AuthorityApplicability.UNKNOWN}
    )
    return reseal(base, authority_assessments=(authority,))


def with_source_dependence() -> A4SemanticInputProjection:
    first = occurrence()
    second = occurrence("occurrence:two", evidence_id="evidence:two")
    value = build_input(occurrence_items=(first, second))
    relation = IndependenceAssessment(
        assessment_id="independence:copied-source",
        dimension=IndependenceDimension.MEASUREMENT_ORIGIN,
        relation=IndependenceRelation.SAME_ROOT,
        left_occurrence_id=first.occurrence_id,
        right_occurrence_id=second.occurrence_id,
        parent_occurrence_ids=(first.occurrence_id,),
        basis=("captured shared root",),
        policy_id="independence-policy:a4-fixture",
        policy_version="1.0",
    )
    return build_projection(value.model_copy(update={"independence": (relation,)}))


def with_stale_evidence() -> A4SemanticInputProjection:
    base = clean_projection()
    qualification = EvidenceQualification(
        evidence_id="evidence:one",
        quality=DataQuality.GOOD,
        freshness=FreshnessState.STALE,
        directness="DIRECT",
        completeness="COMPLETE",
    )
    return reseal(base, evidence_qualifications=(qualification,))


def with_excluded_evidence() -> A4SemanticInputProjection:
    base = clean_projection()
    excluded = ExcludedEvidence(
        evidence_id="evidence:outside-cutoff",
        reason="POINT_IN_TIME_INELIGIBLE",
    )
    return reseal(base, excluded_evidence=(excluded,))


def _two_assertion_input(
    *, scope_mismatch: bool = False
) -> tuple[
    ProjectionBuildInput,
    AssertionIdentity,
    AssertionIdentity,
    ComparisonAssessment,
]:
    first_occurrence = occurrence()
    second_occurrence = occurrence("occurrence:two", evidence_id="evidence:two")
    left = assertion("assertion:one", 100.0, occurrence_id=first_occurrence.occurrence_id)
    right_prop = (
        proposition(
            identifier="proposition:revenue-standalone",
            consolidation="STANDALONE",
        )
        if scope_mismatch
        else proposition(identifier="proposition:revenue-second")
    )
    right = assertion(
        "assertion:two",
        120.0,
        prop=right_prop,
        occurrence_id=second_occurrence.occurrence_id,
    )
    value = build_input(
        assertion_items=(left, right),
        occurrence_items=(first_occurrence, second_occurrence),
    )
    comparison = compare_assertions(
        left,
        right,
        comparison_policy_id="comparison-policy:default",
        comparison_policy_version="1.0",
    )
    return value, left, right, comparison


def with_unresolved_conflict() -> A4SemanticInputProjection:
    value, left, right, comparison = _two_assertion_input()
    assert comparison.status is ComparabilityStatus.EXACT
    detected = DisputeEvent(
        event_id="dispute-event:detected",
        state=DisputeState.DETECTED,
        recorded_at=NOW,
        policy_id="dispute-policy:default",
        policy_version="1.0",
        reason="captured incompatible values",
    )
    dispute = create_dispute(left, right, comparison, event=detected)
    dispute = append_dispute_event(
        dispute,
        DisputeEvent(
            event_id="dispute-event:unresolved",
            state=DisputeState.UNRESOLVED,
            recorded_at=NOW,
            evidence_ids=("evidence:one", "evidence:two"),
            policy_id="dispute-policy:default",
            policy_version="1.0",
            reason="authoritative values remain incompatible",
        ),
    )
    return build_projection(
        value.model_copy(update={"comparisons": (comparison,), "disputes": (dispute,)})
    )


def with_resolved_scope_mismatch() -> A4SemanticInputProjection:
    value, left, right, comparison = _two_assertion_input(scope_mismatch=True)
    assert comparison.status is ComparabilityStatus.NOT_COMPARABLE
    dispute = create_dispute(
        left,
        right,
        comparison,
        event=DisputeEvent(
            event_id="dispute-event:scope-detected",
            state=DisputeState.DETECTED,
            recorded_at=NOW,
            policy_id="dispute-policy:default",
            policy_version="1.0",
            reason="scope mismatch detected",
        ),
    )
    dispute = append_dispute_event(
        dispute,
        DisputeEvent(
            event_id="dispute-event:scope-resolved",
            state=DisputeState.RESOLVED_BY_SCOPE,
            recorded_at=NOW,
            evidence_ids=("evidence:one", "evidence:two"),
            policy_id="dispute-policy:default",
            policy_version="1.0",
            reason="standalone and consolidated scopes differ",
        ),
    )
    return build_projection(
        value.model_copy(update={"comparisons": (comparison,), "disputes": (dispute,)})
    )


def with_unsupported_assumption() -> A4SemanticInputProjection:
    hypothesis = assertion(
        "assertion:hypothesis",
        100.0,
        epistemic=EpistemicRole.HYPOTHESIS,
    )
    return build_projection(build_input(assertion_items=(hypothesis,)))
