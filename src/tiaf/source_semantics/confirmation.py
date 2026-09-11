"""Field-scoped A4 view over an unchanged A3 authoritative confirmation record."""

from tiaf.market_intelligence import AuthoritativeConfirmationResult, ConfirmationStatus
from tiaf.planner.digests import digest

from .comparison import values_conflict
from .contracts import (
    AssertionIdentity,
    AuthorityAssessment,
    ComparisonAssessment,
    ConfirmationFieldBinding,
    ConfirmationFieldProjection,
    ConfirmationProjection,
)
from .enums import AuthorityApplicability, ComparabilityStatus, ConfirmationAdmissibility


def project_confirmation(
    result: AuthoritativeConfirmationResult,
    bindings: tuple[ConfirmationFieldBinding, ...],
    *,
    assertions: tuple[AssertionIdentity, ...],
    comparisons: tuple[ComparisonAssessment, ...],
    authorities: tuple[AuthorityAssessment, ...],
) -> ConfirmationProjection:
    """Project every required field; never collapse documents or change recorded status."""
    result = AuthoritativeConfirmationResult.model_validate_json(result.model_dump_json())
    by_assertion = {item.assertion_id: item for item in assertions}
    by_comparison = {item.comparison_id: item for item in comparisons}
    by_authority = {item.assessment_id: item for item in authorities}
    if len(bindings) != len({item.field_id for item in bindings}):
        raise ValueError("confirmation field bindings must be unique")
    if {item.field_id for item in bindings} != set(result.request.required_fields):
        raise ValueError("bindings must cover exactly the requested confirmation fields")

    confirmed = {item.field_id for item in result.confirmed_facts}
    discrepant = {item.field_id for item in result.unresolved_discrepancies}
    fields: list[ConfirmationFieldProjection] = []
    all_documents: set[str] = set()
    for binding in sorted(bindings, key=lambda item: item.field_id):
        assertion_ids = (*binding.discovered_assertion_ids, *binding.authoritative_assertion_ids)
        if not set(assertion_ids) <= set(by_assertion):
            raise ValueError("confirmation binding references unknown assertion")
        if not set(binding.comparison_ids) <= set(by_comparison):
            raise ValueError("confirmation binding references unknown comparison")
        if not set(binding.authority_assessment_ids) <= set(by_authority):
            raise ValueError("confirmation binding references unknown authority assessment")
        if any(
            by_assertion[item].proposition.predicate_id.split(":", 1)[-1] != binding.field_id
            for item in assertion_ids
        ):
            raise ValueError("field confirmation cannot leak across predicates")
        if any(
            by_authority[item].scope.predicate_id.split(":", 1)[-1] != binding.field_id
            for item in binding.authority_assessment_ids
        ):
            raise ValueError("field confirmation cannot use authority scoped to another field")
        expected_docs = {
            doc.document_id
            for doc in result.authoritative_documents
            if any(fact.field_id == binding.field_id for fact in doc.facts)
        }
        supplied_docs = {doc.original_document_id for doc in binding.document_versions}
        if expected_docs - supplied_docs:
            raise ValueError("all authoritative candidate documents for field must be represented")
        all_documents.update(doc.document_version_id for doc in binding.document_versions)
        statuses = {by_comparison[item].status for item in binding.comparison_ids}
        discovered_ids = set(binding.discovered_assertion_ids)
        authoritative_ids = set(binding.authoritative_assertion_ids)
        for comparison_id in binding.comparison_ids:
            pair = set(by_comparison[comparison_id].assertion_ids)
            if not pair & discovered_ids or not pair & authoritative_ids:
                raise ValueError("field comparison must bind discovered to authoritative assertion")
        compared_authoritative_ids = {
            assertion_id
            for comparison_id in binding.comparison_ids
            for assertion_id in by_comparison[comparison_id].assertion_ids
            if assertion_id in authoritative_ids
        }
        if compared_authoritative_ids != authoritative_ids:
            raise ValueError("every authoritative assertion requires a field comparison")
        applicable = any(
            by_authority[item].applicability is AuthorityApplicability.APPLICABLE
            for item in binding.authority_assessment_ids
        )
        comparable = bool(
            statuses & {ComparabilityStatus.EXACT, ComparabilityStatus.COMPARABLE_WITH_TRANSFORM}
        )
        conflicting = any(
            values_conflict(
                by_assertion[comparison.assertion_ids[0]],
                by_assertion[comparison.assertion_ids[1]],
                comparison,
            )
            for comparison in (by_comparison[item] for item in binding.comparison_ids)
            if comparison.status
            in {ComparabilityStatus.EXACT, ComparabilityStatus.COMPARABLE_WITH_TRANSFORM}
        )
        gaps: list[str] = []
        if not applicable:
            gaps.append("NO_APPLICABLE_SCOPED_AUTHORITY")
        if binding.authoritative_assertion_ids and not comparable:
            gaps.append("NO_COMPARABLE_AUTHORITATIVE_ASSERTION")

        if result.status is ConfirmationStatus.NOT_FOUND:
            admissibility = ConfirmationAdmissibility.NOT_FOUND
            gaps.append("DOCUMENT_NOT_FOUND_IS_NOT_FALSE")
        elif result.status is ConfirmationStatus.UNAVAILABLE:
            admissibility = ConfirmationAdmissibility.UNAVAILABLE
        elif result.status is ConfirmationStatus.OUT_OF_COVERAGE:
            admissibility = ConfirmationAdmissibility.OUT_OF_COVERAGE
        elif result.status is ConfirmationStatus.AMBIGUOUS:
            admissibility = ConfirmationAdmissibility.AMBIGUOUS
        elif binding.field_id in discrepant and comparable and applicable and conflicting:
            admissibility = ConfirmationAdmissibility.ADMISSIBLE_CONFLICT
        elif binding.field_id in confirmed and comparable and applicable and not conflicting:
            admissibility = ConfirmationAdmissibility.ADMISSIBLE_MATCH
        elif binding.field_id in confirmed or binding.field_id in discrepant:
            admissibility = ConfirmationAdmissibility.UNDETERMINED
        else:
            admissibility = ConfirmationAdmissibility.NOT_ADMISSIBLE
            gaps.append("REQUESTED_FIELD_NOT_RESOLVED")
        fields.append(
            ConfirmationFieldProjection(
                field_id=binding.field_id,
                discovered_assertion_ids=tuple(sorted(binding.discovered_assertion_ids)),
                authoritative_assertion_ids=tuple(sorted(binding.authoritative_assertion_ids)),
                comparison_ids=tuple(sorted(binding.comparison_ids)),
                authority_assessment_ids=tuple(sorted(binding.authority_assessment_ids)),
                admissibility=admissibility,
                document_version_ids=tuple(
                    sorted(doc.document_version_id for doc in binding.document_versions)
                ),
                unresolved_gaps=tuple(sorted(set(gaps))),
            )
        )
    identity = digest(
        {
            "confirmation": result.confirmation_id,
            "recorded": result.semantic_fingerprint,
            "fields": [field.model_dump(mode="json") for field in fields],
        }
    )
    projection_id = f"confirmation-projection:{identity[:24]}"
    return ConfirmationProjection(
        projection_id=projection_id,
        confirmation_id=result.confirmation_id,
        recorded_status=result.status.value,
        recorded_semantic_fingerprint=result.semantic_fingerprint,
        fields=tuple(fields),
        all_document_version_ids=tuple(sorted(all_documents)),
    )
