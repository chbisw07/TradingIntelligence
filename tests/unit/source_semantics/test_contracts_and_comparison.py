"""Contract, comparison, dispute and independence requirements."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from tiaf.source_semantics import (
    AssertionIdentity,
    AssertionValue,
    AssertionValueKind,
    AuthorityApplicability,
    ClaimRole,
    ComparabilityStatus,
    ComparisonAssessment,
    DerivationRole,
    DisputeCategory,
    DisputeEvent,
    DisputeState,
    DocumentVersionIdentity,
    EpistemicMappingStatus,
    EpistemicProjection,
    EpistemicRole,
    IndependenceAssessment,
    IndependenceDimension,
    IndependenceRelation,
    SourceEntityIdentity,
    TransformRule,
    append_dispute_event,
    compare_assertions,
    create_dispute,
    validate_independence_lineage,
    values_conflict,
)

from ._support import HASH_A, IST, LATER, NOW, assertion, authority, proposition, source


def compare(
    left: AssertionIdentity,
    right: AssertionIdentity,
    *,
    transforms: tuple[TransformRule, ...] = (),
) -> ComparisonAssessment:
    return compare_assertions(
        left,
        right,
        comparison_policy_id="comparison-policy:default",
        comparison_policy_version="1.0",
        transforms=transforms,
    )


def test_identity_authority_immutability_and_timestamp_contracts() -> None:
    item = source()
    assert item.source_id != "provider:official-ir"
    assert authority(applicability=AuthorityApplicability.UNKNOWN).applicability == "UNKNOWN"
    with pytest.raises(ValidationError):
        SourceEntityIdentity.model_validate(
            {"source_id": "https://example.test/source", "role": "ISSUER", "knowledge": "UNKNOWN"}
        )
    with pytest.raises(ValidationError):
        type(authority()).model_validate(
            authority().model_dump() | {"assessed_at": datetime(2026, 1, 1)}
        )
    with pytest.raises(ValidationError):
        item.source_id = "source:other"
    rebuilt = type(item).model_validate(item.model_dump(mode="json"))
    assert isinstance(rebuilt.original_a3_source_ids, tuple)
    assert isinstance(item.model_dump(mode="json")["original_a3_source_ids"], list)
    assert authority().assessed_at.tzinfo == IST


def test_typed_propositions_do_not_collapse_scope_or_unknowns() -> None:
    revenue = assertion("assertion:revenue", 100)
    total = assertion(
        "assertion:total-income",
        100,
        prop=proposition(predicate="metric:total_income"),
    )
    mismatch = compare(revenue, total)
    assert mismatch.status is ComparabilityStatus.NOT_COMPARABLE
    assert "PREDICATE_MISMATCH" in mismatch.reasons
    assert DisputeCategory.SEMANTIC_MISMATCH is DisputeCategory.SEMANTIC_MISMATCH

    standalone = assertion(
        "assertion:standalone",
        100,
        prop=proposition(consolidation="STANDALONE"),
    )
    scoped = compare(revenue, standalone)
    assert scoped.status is ComparabilityStatus.NOT_COMPARABLE
    assert DisputeCategory.SCOPE_MISMATCH == DisputeCategory.SCOPE_MISMATCH

    unknown = assertion(
        "assertion:unknown",
        100,
        prop=proposition(consolidation="UNKNOWN"),
    )
    assert compare(revenue, unknown).status is ComparabilityStatus.UNDETERMINED


def test_only_explicit_transform_makes_units_comparable() -> None:
    crore = assertion("assertion:crore", 100)
    lakh = assertion(
        "assertion:lakh",
        10_000,
        prop=proposition(unit="INR lakh"),
    )
    rule = TransformRule(
        rule_id="transform:crore-to-lakh",
        version="1.0",
        from_unit="INR crore",
        to_unit="INR lakh",
        multiplier=100,
        tolerance=0,
    )
    assert compare(crore, lakh).status is ComparabilityStatus.NOT_COMPARABLE
    transformed = compare(crore, lakh, transforms=(rule,))
    assert transformed.status is ComparabilityStatus.COMPARABLE_WITH_TRANSFORM
    assert transformed.transformed_values == (10_000, 10_000)
    assert not values_conflict(crore, lakh, transformed)
    assert compare(lakh, crore, transforms=(rule,)) == transformed


def test_zero_is_factual_and_missing_is_not_zero() -> None:
    zero = assertion("assertion:zero", 0)
    missing = assertion("assertion:missing", None)
    comparison = compare(zero, missing)
    assert comparison.status is ComparabilityStatus.EXACT
    assert values_conflict(zero, missing, comparison)
    assert zero.value == AssertionValue(kind=AssertionValueKind.SCALAR, scalar=0)


def test_same_provider_facts_can_conflict_and_dispute_history_is_append_only() -> None:
    left = assertion("assertion:left", 100)
    right = assertion("assertion:right", 101)
    comparison = compare(left, right)
    assert values_conflict(left, right, comparison)
    detected = DisputeEvent(
        event_id="dispute-event:detected",
        state=DisputeState.DETECTED,
        recorded_at=NOW,
        policy_id="dispute-policy:default",
        policy_version="1.0",
        reason="two captured facts differ",
    )
    dispute = create_dispute(left, right, comparison, event=detected)
    assert dispute.category is DisputeCategory.FACTUAL_CONFLICT
    resolved = append_dispute_event(
        dispute,
        DisputeEvent(
            event_id="dispute-event:confirmed",
            state=DisputeState.CONFIRMED_CONFLICT,
            recorded_at=LATER,
            evidence_ids=("evidence:one",),
            policy_id="dispute-policy:default",
            policy_version="1.0",
            reason="conflict retained",
        ),
    )
    assert dispute.events == (detected,)
    assert [item.state for item in resolved.events] == ["DETECTED", "CONFIRMED_CONFLICT"]
    with pytest.raises(ValueError, match="cannot append"):
        append_dispute_event(resolved, detected)


def test_document_hash_change_is_not_implicitly_a_revision() -> None:
    first = DocumentVersionIdentity(
        document_version_id="document:first",
        family_id="document-family:ril-results",
        content_hash=HASH_A,
        available_from=NOW,
    )
    second = DocumentVersionIdentity(
        document_version_id="document:second",
        family_id=first.family_id,
        content_hash="b" * 64,
        available_from=LATER,
    )
    assert first.content_hash != second.content_hash
    assert second.supersedes_document_version_id is None
    with pytest.raises(ValidationError, match="explicit correction"):
        DocumentVersionIdentity.model_validate(
            second.model_dump()
            | {"supersedes_document_version_id": first.document_version_id}
        )
    with pytest.raises(ValidationError, match="predicate or period scope"):
        DocumentVersionIdentity(
            document_version_id="document:unscoped-correction",
            family_id="document-family:ril-results",
            content_hash="d" * 64,
            available_from=LATER,
            revision_number=1,
            correction_kind="CORRECTION",
            supersedes_document_version_id="document:first",
        )


def test_explicit_correction_has_scoped_predicates_and_periods() -> None:
    corrected = DocumentVersionIdentity(
        document_version_id="document:corrected",
        family_id="document-family:ril-results",
        content_hash="c" * 64,
        available_from=LATER,
        revision_number=1,
        correction_kind="CORRECTION",
        supersedes_document_version_id="document:first",
        corrected_predicates=("metric:revenue_from_operations",),
        corrected_periods=("Q1-FY2027",),
    )
    assert corrected.corrected_predicates == ("metric:revenue_from_operations",)
    assert corrected.corrected_periods == ("Q1-FY2027",)


def independence(identifier: str, left: str, right: str, *, relation, parents=()):  # type: ignore[no-untyped-def]
    return IndependenceAssessment(
        assessment_id=identifier,
        dimension=IndependenceDimension.MEASUREMENT_ORIGIN,
        relation=relation,
        left_occurrence_id=left,
        right_occurrence_id=right,
        parent_occurrence_ids=parents,
        independence_basis_ids=(
            ("analysis:left", "analysis:right")
            if relation is IndependenceRelation.INDEPENDENT
            else ()
        ),
        basis=(
            ("explicit captured lineage",)
            if relation is IndependenceRelation.INDEPENDENT
            else ()
        ),
        policy_id="independence-policy:default",
        policy_version="1.0",
    )


def test_independence_is_dimensioned_non_transitive_and_acyclic() -> None:
    same_root = independence(
        "independence:same-root",
        "occurrence:one",
        "occurrence:two",
        relation=IndependenceRelation.SAME_ROOT,
        parents=("occurrence:root",),
    )
    analytical = independence(
        "independence:analysis",
        "occurrence:one",
        "occurrence:two",
        relation=IndependenceRelation.INDEPENDENT,
    ).model_copy(update={"dimension": IndependenceDimension.ANALYTICAL_DERIVATION})
    assert same_root.relation is IndependenceRelation.SAME_ROOT
    assert analytical.relation is IndependenceRelation.INDEPENDENT
    cycle = (
        independence(
            "independence:a",
            "occurrence:a",
            "occurrence:b",
            relation=IndependenceRelation.DERIVED_FROM,
            parents=("occurrence:b",),
        ),
        independence(
            "independence:b",
            "occurrence:b",
            "occurrence:a",
            relation=IndependenceRelation.DERIVED_FROM,
            parents=("occurrence:a",),
        ),
    )
    with pytest.raises(ValueError, match="cycle"):
        validate_independence_lineage(cycle)


def test_provider_names_alone_never_establish_independence() -> None:
    with pytest.raises(ValidationError, match="basis identities"):
        IndependenceAssessment(
            assessment_id="independence:provider-names-only",
            dimension=IndependenceDimension.MEASUREMENT_ORIGIN,
            relation=IndependenceRelation.INDEPENDENT,
            left_occurrence_id="occurrence:one",
            right_occurrence_id="occurrence:two",
            basis=("different provider display names",),
            policy_id="independence-policy:default",
            policy_version="1.0",
        )


def test_provider_derived_value_cannot_be_relabeled_reported_without_mapping() -> None:
    with pytest.raises(ValidationError, match="mapping"):
        EpistemicProjection(
            projection_id="epistemic:bad",
            assertion_id="assertion:one",
            claim_role=ClaimRole.OBSERVED_REPORTED_VALUE,
            epistemic_role=EpistemicRole.FACT,
            derivation_role=DerivationRole.PROVIDER_DERIVED,
            mapping_status=EpistemicMappingStatus.UNMAPPED,
        )
