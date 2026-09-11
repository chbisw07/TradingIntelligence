"""Deterministic projection of frozen A2/A3 captures into pre-A4 semantic input."""

from collections.abc import Callable
from typing import Any, cast

from tiaf.a3_hardening import A2CaptureMode, BlobKind, package_blob, validate_package
from tiaf.planner.digests import digest, semantic
from tiaf.service.opportunity_intelligence import replay_intelligence
from tiaf.workflows import replay_recorded

from .comparison import validate_independence_lineage
from .contracts import (
    A4SemanticInputProjection,
    FrozenParentReferences,
    OpportunityOpinionView,
    ProjectionBuildInput,
)


class ProjectionIntegrityError(ValueError):
    """Mandatory captured identity, relationship or semantic input is invalid."""


def _sorted[T](items: tuple[T, ...], key: Callable[[T], Any]) -> tuple[T, ...]:
    return tuple(sorted(items, key=key))


def projection_semantic_payload(projection: A4SemanticInputProjection) -> dict[str, Any]:
    """Exclude self/operational creation identity, retain all semantic parent/run policy."""
    return cast(
        dict[str, Any],
        semantic(
            projection.model_dump(
                mode="json",
                exclude={
                    "projection_id": True,
                    "semantic_fingerprint": True,
                    "header": {"created_at"},
                },
            )
        ),
    )


def validate_projection(projection: A4SemanticInputProjection) -> A4SemanticInputProjection:
    rebuilt = A4SemanticInputProjection.model_validate_json(projection.model_dump_json())
    expected = digest(projection_semantic_payload(rebuilt))
    if rebuilt.semantic_fingerprint != expected:
        raise ProjectionIntegrityError("projection semantic fingerprint mismatch")
    if rebuilt.projection_id != f"a4-input:{expected[:24]}":
        raise ProjectionIntegrityError("projection ID does not match semantic fingerprint")
    return rebuilt


def build_projection(value: ProjectionBuildInput) -> A4SemanticInputProjection:
    """Build from captured artifacts only; contains no provider/model execution path."""
    try:
        value = ProjectionBuildInput.model_validate_json(value.model_dump_json())
        package = validate_package(value.package)
        manifest = package.manifest
        replay_recorded(package_blob(package, BlobKind.A38_CAPTURE).content)
        a39 = replay_intelligence(package_blob(package, BlobKind.A39_CAPTURE).content)
        if (
            value.header.subject != manifest.subject
            or value.header.horizon != manifest.horizon
            or value.header.objective != manifest.purpose.value
        ):
            raise ValueError("projection header does not match frozen parent identity")
        if value.parent_projection_id is None and value.header.evidence_as_of != manifest.as_of:
            raise ValueError("initial projection as-of must equal frozen package as-of")
        if value.parent_projection_id and value.header.evidence_as_of <= manifest.as_of:
            raise ValueError("successor projection must advance beyond frozen package as-of")
        if (
            manifest.a2_capture.mode is A2CaptureMode.ORIGINAL_A38_PROJECTION
            and value.requires_full_a2_assertion_ids
        ):
            raise ValueError("projection-only A2 capture cannot support full-evidence assertions")
        expected_artifacts = {
            "a3-package": manifest.exact_package_checksum,
            "a2-capture": manifest.a2_capture.blob.checksum,
            "a38-capture": manifest.a38_capture.checksum,
            "a39-capture": manifest.a39_capture.checksum,
        }
        supplied_artifacts = dict(value.referenced_artifact_digests)
        if len(supplied_artifacts) != len(value.referenced_artifact_digests):
            raise ValueError("duplicate referenced artifact identity")
        if supplied_artifacts != expected_artifacts:
            raise ValueError("missing or corrupt mandatory referenced artifact digest")

        sources = {item.source_id: item for item in value.sources}
        providers = {item.adapter_id: item for item in value.providers}
        origins = {item.origin_id: item for item in value.origins}
        families = {item.family_id: item for item in value.document_families}
        documents = {item.document_version_id: item for item in value.document_versions}
        occurrences = {item.occurrence_id: item for item in value.occurrences}
        assertions = {item.assertion_id: item for item in value.assertions}
        admissions = {item.admission_id: item for item in value.admissions}
        authorities = {item.assessment_id: item for item in value.authority_assessments}
        comparisons = {item.comparison_id: item for item in value.comparisons}
        disputes = {item.dispute_id: item for item in value.disputes}
        for mapping, items, label in (
            (sources, value.sources, "source"),
            (providers, value.providers, "provider adapter"),
            (origins, value.origins, "origin"),
            (families, value.document_families, "document family"),
            (documents, value.document_versions, "document version"),
            (occurrences, value.occurrences, "occurrence"),
            (assertions, value.assertions, "assertion"),
            (admissions, value.admissions, "admission"),
            (authorities, value.authority_assessments, "authority assessment"),
            (comparisons, value.comparisons, "comparison"),
            (disputes, value.disputes, "dispute"),
        ):
            if len(mapping) != len(items):
                raise ValueError(f"duplicate {label} identity")
        if set(sources) & ({item.provider_id for item in value.providers} | set(providers)):
            raise ValueError("source identity cannot double as provider/adapter identity")
        for family in value.document_families:
            if family.source_id not in sources or family.subject != value.header.subject:
                raise ValueError("document family source/subject is unresolved")
        for doc in value.document_versions:
            if doc.family_id not in families:
                raise ValueError("document version family is unresolved")
            if doc.available_from > value.header.evidence_as_of:
                raise ValueError("document version is later than projection cutoff")
            if (
                doc.supersedes_document_version_id
                and doc.supersedes_document_version_id not in documents
            ):
                raise ValueError("superseded document version is unresolved")
        for origin in value.origins:
            if not set(origin.source_ids) <= set(sources):
                raise ValueError("origin source identity is unresolved")
        for occurrence in value.occurrences:
            if occurrence.source_id not in sources or occurrence.origin_id not in origins:
                raise ValueError("occurrence source/origin is unresolved")
            if occurrence.provider_adapter_id and occurrence.provider_adapter_id not in providers:
                raise ValueError("occurrence provider adapter is unresolved")
            if occurrence.document_version_id and occurrence.document_version_id not in documents:
                raise ValueError("occurrence document version is unresolved")
            if occurrence.acquired_at > value.header.evidence_as_of:
                raise ValueError("occurrence is later than projection cutoff")
            if occurrence.document_version_id:
                document = documents[occurrence.document_version_id]
                if occurrence.acquired_at < document.available_from:
                    raise ValueError("occurrence predates document availability")
        for assertion in value.assertions:
            if assertion.proposition.subject != value.header.subject:
                raise ValueError("assertion subject differs from projection")
            if not set(assertion.occurrence_ids) <= set(occurrences):
                raise ValueError("assertion occurrence is unresolved")
        for admission in value.admissions:
            if admission.assertion_id not in assertions or not set(admission.source_ids) <= set(
                sources
            ):
                raise ValueError("admission assertion/source is unresolved")
            if admission.as_of != value.header.evidence_as_of:
                raise ValueError("admission as-of differs from projection")
        for authority in value.authority_assessments:
            if authority.source_id not in sources:
                raise ValueError("authority source is unresolved")
            if authority.document_version_id and authority.document_version_id not in documents:
                raise ValueError("authority document is unresolved")
            if authority.document_version_id:
                family_id = documents[authority.document_version_id].family_id
                if families[family_id].source_id != authority.source_id:
                    raise ValueError("authority source differs from document source")
            if authority.scope.subject != value.header.subject:
                raise ValueError("authority scope subject differs from projection")
            if authority.assessed_at > value.header.evidence_as_of:
                raise ValueError("authority assessment is later than projection cutoff")
        for comparison in value.comparisons:
            if not set(comparison.assertion_ids) <= set(assertions):
                raise ValueError("comparison assertion is unresolved")
        for dispute in value.disputes:
            if not set(dispute.assertion_ids) <= set(assertions):
                raise ValueError("dispute assertion is unresolved")
        validate_independence_lineage(value.independence)
        for relation in value.independence:
            refs = {
                relation.left_occurrence_id,
                relation.right_occurrence_id,
                *relation.parent_occurrence_ids,
            }
            if not refs <= set(occurrences):
                raise ValueError("independence occurrence is unresolved")
        for epistemic in value.epistemic_projections:
            if epistemic.assertion_id not in assertions:
                raise ValueError("epistemic projection assertion is unresolved")
        for confirmation in value.confirmation_projections:
            field_refs = {
                ref
                for field in confirmation.fields
                for ref in (*field.discovered_assertion_ids, *field.authoritative_assertion_ids)
            }
            if not field_refs <= set(assertions):
                raise ValueError("confirmation projection assertion is unresolved")
            if not {ref for field in confirmation.fields for ref in field.comparison_ids} <= set(
                comparisons
            ):
                raise ValueError("confirmation projection comparison is unresolved")
            if not {
                ref for field in confirmation.fields for ref in field.authority_assessment_ids
            } <= set(authorities):
                raise ValueError("confirmation projection authority is unresolved")
        admitted_evidence = {occurrence.evidence_id for occurrence in value.occurrences}
        if not set(value.new_evidence_ids) <= admitted_evidence:
            raise ValueError("successor new evidence IDs require captured occurrences")
        if value.parent_evidence_as_of and any(
            occurrence.acquired_at <= value.parent_evidence_as_of
            for occurrence in value.occurrences
            if occurrence.evidence_id in value.new_evidence_ids
        ):
            raise ValueError("successor new evidence must be acquired after parent cutoff")

        parents = FrozenParentReferences(
            a3_package_id=manifest.package_id,
            a3_package_semantic_fingerprint=manifest.package_semantic_fingerprint,
            a3_package_exact_checksum=manifest.exact_package_checksum,
            a38_capture_checksum=manifest.a38_capture.checksum,
            a38_semantic_fingerprint=manifest.a38_semantic_fingerprint,
            a39_capture_checksum=manifest.a39_capture.checksum,
            a39_semantic_fingerprint=manifest.a39_semantic_fingerprint,
            a2_mode=manifest.a2_capture.mode,
            a2_assessment_id=manifest.a2_assessment_id,
            a2_evidence_fingerprint=manifest.a2_evidence_fingerprint,
        )
        opportunity = OpportunityOpinionView(
            a39_state=a39.result.summary.state.value,
            a39_reason_ids=tuple(sorted(item.reason_id for item in a39.result.reasons)),
            a39_gap_ids=tuple(
                sorted(
                    {
                        *a39.result.completeness.gaps,
                        *(item.requirement_id for item in a39.result.prerequisites),
                    }
                )
            ),
            active_opinion_ids=tuple(sorted(manifest.active_opinion_ids)),
            superseded_opinion_ids=tuple(sorted(manifest.superseded_opinion_ids)),
            original_a2_direction=(
                a39.result.baseline.direction.value if a39.result.baseline.direction else None
            ),
            original_a2_candidate_class=(
                a39.result.baseline.candidate_class.value
                if a39.result.baseline.candidate_class
                else None
            ),
            original_a2_score=a39.result.baseline.opportunity_score,
            full_a2_evidence_available=manifest.a2_capture.mode is A2CaptureMode.FULL_BASELINE_CASE,
        )
        kwargs: dict[str, Any] = {
            "projection_id": "a4-input:pending",
            "header": value.header,
            "parents": parents,
            "parent_projection_id": value.parent_projection_id,
            "parent_evidence_as_of": value.parent_evidence_as_of,
            "new_evidence_ids": tuple(sorted(value.new_evidence_ids)),
            "opportunity": opportunity,
            "sources": _sorted(value.sources, lambda item: item.source_id),
            "providers": _sorted(value.providers, lambda item: item.adapter_id),
            "origins": _sorted(value.origins, lambda item: item.origin_id),
            "document_families": _sorted(value.document_families, lambda item: item.family_id),
            "document_versions": _sorted(
                value.document_versions, lambda item: item.document_version_id
            ),
            "occurrences": _sorted(value.occurrences, lambda item: item.occurrence_id),
            "assertions": _sorted(value.assertions, lambda item: item.assertion_id),
            "admissions": _sorted(value.admissions, lambda item: item.admission_id),
            "authority_assessments": _sorted(
                value.authority_assessments, lambda item: item.assessment_id
            ),
            "comparisons": _sorted(value.comparisons, lambda item: item.comparison_id),
            "disputes": _sorted(value.disputes, lambda item: item.dispute_id),
            "independence": _sorted(value.independence, lambda item: item.assessment_id),
            "epistemic_projections": _sorted(
                value.epistemic_projections, lambda item: item.projection_id
            ),
            "confirmation_projections": _sorted(
                value.confirmation_projections, lambda item: item.projection_id
            ),
            "evidence_qualifications": _sorted(
                value.evidence_qualifications, lambda item: item.evidence_id
            ),
            "gaps": _sorted(value.gaps, lambda item: item.gap_id),
            "excluded_evidence": _sorted(value.excluded_evidence, lambda item: item.evidence_id),
            "referenced_artifact_digests": tuple(sorted(value.referenced_artifact_digests)),
            "usage_cost_knowledge": tuple(sorted(value.usage_cost_knowledge)),
            "semantic_fingerprint": "0" * 64,
        }
        provisional = A4SemanticInputProjection(**kwargs)
        fingerprint = digest(projection_semantic_payload(provisional))
        return validate_projection(
            provisional.model_copy(
                update={
                    "projection_id": f"a4-input:{fingerprint[:24]}",
                    "semantic_fingerprint": fingerprint,
                }
            )
        )
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, ProjectionIntegrityError):
            raise
        raise ProjectionIntegrityError(str(exc)) from exc
