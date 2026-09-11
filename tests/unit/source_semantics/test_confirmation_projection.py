"""Field-level projection over unchanged A3 authoritative confirmation records."""

import pytest

from tiaf.market_intelligence import (
    AuthoritativeConfirmationResult,
    AuthoritativeDocumentKind,
    ConfirmationStatus,
    ProviderFailureKind,
)
from tiaf.source_semantics import (
    AssertionIdentity,
    AuthorityAssessment,
    ComparisonAssessment,
    ConfirmationAdmissibility,
    ConfirmationFieldBinding,
    DocumentVersionIdentity,
    compare_assertions,
    project_confirmation,
)

from ..market_intelligence.test_authoritative_gateway import claim, exact_rule, execute
from ._support import assertion, authority, proposition


def document_versions(
    result: AuthoritativeConfirmationResult,
) -> tuple[DocumentVersionIdentity, ...]:
    return tuple(
        DocumentVersionIdentity(
            document_version_id=f"document:{index}",
            family_id="document-family:ril-results",
            content_hash=item.content_hash,
            published_at=item.published_at,
            available_from=item.available_from,
            original_document_id=item.document_id,
            locator_refs=(f"locator:official-{index}",),
        )
        for index, item in enumerate(result.authoritative_documents, 1)
    )


def projection_material(
    result: AuthoritativeConfirmationResult,
) -> tuple[
    tuple[ConfirmationFieldBinding, ...],
    tuple[AssertionIdentity, ...],
    tuple[ComparisonAssessment, ...],
    tuple[AuthorityAssessment, ...],
]:
    assertions: list[AssertionIdentity] = []
    comparisons: list[ComparisonAssessment] = []
    authorities: list[AuthorityAssessment] = []
    bindings: list[ConfirmationFieldBinding] = []
    documents = document_versions(result)
    authoritative_facts = {
        fact.field_id: fact
        for document in result.authoritative_documents
        for fact in document.facts
    }
    for discovered in result.request.claim.asserted_facts:
        field = discovered.field_id
        prop = proposition(
            identifier=f"proposition:{field}",
            predicate=f"metric:{field}",
            unit=discovered.unit,
        )
        found = assertion(f"assertion:discovered-{field}", discovered.value, prop=prop)
        assertions.append(found)
        authoritative_ids: tuple[str, ...] = ()
        comparison_ids: tuple[str, ...] = ()
        authority_ids: tuple[str, ...] = ()
        applicable_documents: tuple[DocumentVersionIdentity, ...] = ()
        if field in authoritative_facts:
            official = assertion(
                f"assertion:authoritative-{field}",
                authoritative_facts[field].value,
                prop=prop,
            )
            comparison = compare_assertions(
                found,
                official,
                comparison_policy_id="comparison-policy:default",
                comparison_policy_version="1.0",
            )
            assessment = authority().model_copy(
                update={
                    "assessment_id": f"authority:{field}",
                    "scope": authority().scope.model_copy(
                        update={"predicate_id": f"metric:{field}"}
                    ),
                }
            )
            assertions.append(official)
            comparisons.append(comparison)
            authorities.append(assessment)
            authoritative_ids = (official.assertion_id,)
            comparison_ids = (comparison.comparison_id,)
            authority_ids = (assessment.assessment_id,)
            applicable_documents = tuple(
                document
                for document, native in zip(
                    documents, result.authoritative_documents, strict=True
                )
                if any(fact.field_id == field for fact in native.facts)
            )
        bindings.append(
            ConfirmationFieldBinding(
                field_id=field,
                discovered_assertion_ids=(found.assertion_id,),
                authoritative_assertion_ids=authoritative_ids,
                comparison_ids=comparison_ids,
                authority_assessment_ids=authority_ids,
                document_versions=applicable_documents,
            )
        )
    return tuple(bindings), tuple(assertions), tuple(comparisons), tuple(authorities)


def project(result: AuthoritativeConfirmationResult):  # type: ignore[no-untyped-def]
    bindings, assertions, comparisons, authorities = projection_material(result)
    return project_confirmation(
        result,
        bindings,
        assertions=assertions,
        comparisons=comparisons,
        authorities=authorities,
    )


def test_exact_confirmation_is_field_scoped_and_preserves_parent_record() -> None:
    result, _, _ = execute(b"Revenue from Operations: 100")
    original = result.model_dump_json()
    projected = project(result)
    assert result.model_dump_json() == original
    assert projected.recorded_status == ConfirmationStatus.CONFIRMED
    assert projected.recorded_semantic_fingerprint == result.semantic_fingerprint
    assert projected.fields[0].admissibility is ConfirmationAdmissibility.ADMISSIBLE_MATCH


def test_field_confirmation_cannot_leak_to_another_predicate_or_authority_scope() -> None:
    result, _, _ = execute(b"Revenue from Operations: 100")
    bindings, assertions, comparisons, authorities = projection_material(result)
    wrong = assertions[0].model_copy(
        update={
            "proposition": assertions[0].proposition.model_copy(
                update={"predicate_id": "metric:profit_after_tax"}
            )
        }
    )
    with pytest.raises(ValueError, match="leak"):
        project_confirmation(
            result,
            bindings,
            assertions=(wrong, *assertions[1:]),
            comparisons=comparisons,
            authorities=authorities,
        )
    wrong_authority = authorities[0].model_copy(
        update={
            "scope": authorities[0].scope.model_copy(
                update={"predicate_id": "metric:profit_after_tax"}
            )
        }
    )
    with pytest.raises(ValueError, match="another field"):
        project_confirmation(
            result,
            bindings,
            assertions=assertions,
            comparisons=comparisons,
            authorities=(wrong_authority,),
        )


@pytest.mark.parametrize(
    ("result", "expected"),
    (
        (
            execute(
                b"unused",
                kinds=(AuthoritativeDocumentKind.ANNUAL_REPORT,),
            )[0],
            ConfirmationAdmissibility.NOT_FOUND,
        ),
        (
            execute(
                b"unused",
                transport_failure=ProviderFailureKind.ACCESS_RESTRICTED,
            )[0],
            ConfirmationAdmissibility.UNAVAILABLE,
        ),
    ),
)
def test_absence_status_is_preserved_not_interpreted_as_false(
    result: AuthoritativeConfirmationResult,
    expected: ConfirmationAdmissibility,
) -> None:
    projected = project(result)
    assert projected.fields[0].admissibility is expected
    if expected is ConfirmationAdmissibility.NOT_FOUND:
        assert "DOCUMENT_NOT_FOUND_IS_NOT_FALSE" in projected.fields[0].unresolved_gaps


def test_multiple_authoritative_documents_never_resolve_by_binding_order() -> None:
    result, _, _ = execute(b"Revenue from Operations: 90")
    bindings, assertions, comparisons, authorities = projection_material(result)
    existing = bindings[0].document_versions[0]
    additional = existing.model_copy(
        update={
            "document_version_id": "document:additional",
            "original_document_id": "legacy-additional",
        }
    )
    left = bindings[0].model_copy(
        update={"document_versions": (existing, additional)}
    )
    right = bindings[0].model_copy(
        update={"document_versions": (additional, existing)}
    )
    first = project_confirmation(
        result,
        (left,),
        assertions=assertions,
        comparisons=comparisons,
        authorities=authorities,
    )
    second = project_confirmation(
        result,
        (right,),
        assertions=assertions,
        comparisons=comparisons,
        authorities=authorities,
    )
    assert first == second
    assert first.fields[0].admissibility is ConfirmationAdmissibility.ADMISSIBLE_CONFLICT


def test_equal_authority_conflicts_remain_unresolved_without_winner() -> None:
    result, _, _ = execute(b"Revenue from Operations: 90")
    bindings, assertions, comparisons, authorities = projection_material(result)
    discovered, official = assertions
    other = official.model_copy(
        update={
            "assertion_id": "assertion:authoritative-second",
            "value": official.value.model_copy(update={"scalar": 91}),
        }
    )
    other_comparison = compare_assertions(
        discovered,
        other,
        comparison_policy_id="comparison-policy:default",
        comparison_policy_version="1.0",
    )
    other_authority = authorities[0].model_copy(
        update={"assessment_id": "authority:second-equal-rank"}
    )
    binding = bindings[0].model_copy(
        update={
            "authoritative_assertion_ids": (official.assertion_id, other.assertion_id),
            "comparison_ids": (comparisons[0].comparison_id, other_comparison.comparison_id),
            "authority_assessment_ids": (
                authorities[0].assessment_id,
                other_authority.assessment_id,
            ),
        }
    )
    projected = project_confirmation(
        result,
        (binding,),
        assertions=(*assertions, other),
        comparisons=(*comparisons, other_comparison),
        authorities=(*authorities, other_authority),
    )
    assert projected.fields[0].admissibility is ConfirmationAdmissibility.ADMISSIBLE_CONFLICT
    assert len(projected.fields[0].authoritative_assertion_ids) == 2


def test_partial_confirmation_retains_match_and_conflict() -> None:
    result, _, _ = execute(
        b"Revenue from Operations: 100\nProfit After Tax: 19",
        discovered=claim(include_pat=True),
        rules=(exact_rule(), exact_rule("pat", "Profit After Tax")),
    )
    assert result.status is ConfirmationStatus.PARTIALLY_CONFIRMED
    projected = project(result)
    states = {item.field_id: item.admissibility for item in projected.fields}
    assert states == {
        "pat": ConfirmationAdmissibility.ADMISSIBLE_CONFLICT,
        "revenue_from_operations": ConfirmationAdmissibility.ADMISSIBLE_MATCH,
    }
