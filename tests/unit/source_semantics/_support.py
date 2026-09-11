"""Synthetic, fully captured pre-A4 semantic fixtures."""

from datetime import datetime, timedelta
from typing import Literal
from zoneinfo import ZoneInfo

from tiaf.a3_hardening import PortableA3ReplayPackage
from tiaf.source_semantics import (
    A4ProjectionHeader,
    AdmissionIdentity,
    AssertionIdentity,
    AssertionValue,
    AssertionValueKind,
    AuthorityApplicability,
    AuthorityAssessment,
    AuthorityScope,
    ClaimRole,
    DerivationRole,
    DocumentFamilyIdentity,
    DocumentVersionIdentity,
    EpistemicMappingStatus,
    EpistemicProjection,
    EpistemicRole,
    EvidenceOccurrenceIdentity,
    IdentityKnowledge,
    MeasureRole,
    MeasureType,
    ProjectionBuildInput,
    PropositionKey,
    ProviderAdapterIdentity,
    SourceEntityIdentity,
    SourceEntityRole,
    UpstreamOriginIdentity,
)

from ..a3_hardening._support import package_for

IST = ZoneInfo("Asia/Kolkata")
NOW = datetime(2026, 9, 10, 12, tzinfo=IST)
LATER = NOW + timedelta(days=1)
HASH_A = "a" * 64


def proposition(
    identifier: str = "proposition:revenue",
    *,
    predicate: str = "metric:revenue_from_operations",
    unit: str | None = "INR crore",
    period: str | None = "Q1-FY2027",
    consolidation: Literal[
        "STANDALONE", "CONSOLIDATED", "NOT_APPLICABLE", "UNKNOWN"
    ] = "CONSOLIDATED",
    statement_basis: str | None = "IND_AS",
    adjustment: Literal[
        "ADJUSTED", "UNADJUSTED", "NOT_APPLICABLE", "UNKNOWN"
    ] = "NOT_APPLICABLE",
    measure_role: MeasureRole = MeasureRole.ACTUAL,
) -> PropositionKey:
    return PropositionKey(
        proposition_id=identifier,
        subject="SYNTHETIC",
        predicate_id=predicate,
        predicate_version="1.0",
        qualifiers=(("definition", predicate),),
        unit=unit,
        currency="INR" if unit is not None else None,
        reporting_period=period,
        consolidation_basis=consolidation,
        segment="ALL",
        accounting_basis="IND_AS",
        statement_basis=statement_basis,
        adjustment_basis=adjustment,
        measure_type=MeasureType.NUMBER,
        measure_role=measure_role,
    )


def assertion(
    identifier: str,
    value: str | int | float | bool | None,
    *,
    prop: PropositionKey | None = None,
    occurrence_id: str = "occurrence:one",
    epistemic: EpistemicRole = EpistemicRole.FACT,
    derivation: DerivationRole = DerivationRole.REPORTED,
) -> AssertionIdentity:
    assertion_value = (
        AssertionValue(kind=AssertionValueKind.MISSING)
        if value is None
        else AssertionValue(kind=AssertionValueKind.SCALAR, scalar=value)
    )
    return AssertionIdentity(
        assertion_id=identifier,
        proposition=prop or proposition(),
        value=assertion_value,
        epistemic_role=epistemic,
        derivation_role=derivation,
        occurrence_ids=(occurrence_id,),
        original_claim_ids=(f"legacy:{identifier}",),
    )


def source(identifier: str = "source:ril") -> SourceEntityIdentity:
    return SourceEntityIdentity(
        source_id=identifier,
        role=SourceEntityRole.ISSUER,
        knowledge=IdentityKnowledge.KNOWN,
        display_name="Reliance Industries Limited",
        jurisdiction="IN",
        original_a3_source_ids=("reliance_ir",),
    )


def origin(identifier: str = "origin:ril-filing") -> UpstreamOriginIdentity:
    return UpstreamOriginIdentity(
        origin_id=identifier,
        knowledge=IdentityKnowledge.KNOWN,
        source_ids=("source:ril",),
        basis=("issuer filing identity",),
    )


def occurrence(
    identifier: str = "occurrence:one",
    *,
    evidence_id: str = "evidence:one",
    acquired_at: datetime = NOW,
) -> EvidenceOccurrenceIdentity:
    return EvidenceOccurrenceIdentity(
        occurrence_id=identifier,
        evidence_id=evidence_id,
        source_id="source:ril",
        provider_adapter_id="adapter:official-ir",
        origin_id="origin:ril-filing",
        document_version_id="document:ril-q1-v1",
        observed_at=acquired_at,
        acquired_at=acquired_at,
    )


def authority(
    identifier: str = "authority:revenue",
    applicability: AuthorityApplicability = AuthorityApplicability.APPLICABLE,
) -> AuthorityAssessment:
    return AuthorityAssessment(
        assessment_id=identifier,
        source_id="source:ril",
        document_version_id="document:ril-q1-v1",
        scope=AuthorityScope(
            authority_domain="authority-domain:company-financials",
            subject="SYNTHETIC",
            jurisdiction="IN",
            predicate_id="metric:revenue_from_operations",
            period="Q1-FY2027",
            statement_basis="CONSOLIDATED",
        ),
        source_role=SourceEntityRole.ISSUER,
        authenticity_basis=("configured issuer and captured content hash",),
        applicability=applicability,
        policy_id="authority-policy:default",
        policy_version="1.0",
        assessed_at=NOW,
    )


def build_input(
    *,
    assertion_items: tuple[AssertionIdentity, ...] | None = None,
    occurrence_items: tuple[EvidenceOccurrenceIdentity, ...] | None = None,
    as_of: datetime = NOW,
    parent_projection_id: str | None = None,
    parent_as_of: datetime | None = None,
    new_evidence_ids: tuple[str, ...] = (),
    package: PortableA3ReplayPackage | None = None,
) -> ProjectionBuildInput:
    package = package or package_for()
    occurrence_items = occurrence_items or (occurrence(),)
    assertion_items = assertion_items or (assertion("assertion:one", 100.0),)
    family = DocumentFamilyIdentity(
        family_id="document-family:ril-results",
        source_id="source:ril",
        document_kind="FINANCIAL_RESULT",
        subject="SYNTHETIC",
    )
    document = DocumentVersionIdentity(
        document_version_id="document:ril-q1-v1",
        family_id=family.family_id,
        content_hash=HASH_A,
        published_at=NOW,
        available_from=NOW,
        original_document_id="legacy-document-1",
        locator_refs=("locator:ril-results-q1",),
    )
    admissions = tuple(
        AdmissionIdentity(
            admission_id=f"admission:{item.assertion_id.split(':')[-1]}",
            run_id="foundation-run-1",
            capture_id=package.manifest.package_id,
            assertion_id=item.assertion_id,
            as_of=as_of,
            available_from=max(
                occurrence_item.acquired_at
                for occurrence_item in occurrence_items
                if occurrence_item.occurrence_id in item.occurrence_ids
            ),
            projection_policy_id="projection-policy:default",
            projection_policy_version="1.0",
            comparison_policy_id="comparison-policy:default",
            comparison_policy_version="1.0",
            source_ids=("source:ril",),
            mapping_status=EpistemicMappingStatus.MAPPED,
        )
        for item in assertion_items
    )
    epistemic = tuple(
        EpistemicProjection(
            projection_id=f"epistemic:{item.assertion_id.split(':')[-1]}",
            assertion_id=item.assertion_id,
            claim_role=(
                ClaimRole.OBSERVED_REPORTED_VALUE
                if item.derivation_role is DerivationRole.REPORTED
                else ClaimRole.DERIVED_METRIC
            ),
            epistemic_role=item.epistemic_role,
            derivation_role=item.derivation_role,
            mapping_status=EpistemicMappingStatus.MAPPED,
            mapping_rule_id="mapping-rule:fixture",
        )
        for item in assertion_items
    )
    return ProjectionBuildInput(
        package=package,
        header=A4ProjectionHeader(
            projection_policy_id="projection-policy:default",
            projection_policy_version="1.0",
            comparison_policy_id="comparison-policy:default",
            comparison_policy_version="1.0",
            subject=package.manifest.subject,
            objective="OPPORTUNITY",
            horizon=package.manifest.horizon,
            evidence_as_of=as_of,
            created_at=as_of,
            run_id="foundation-run-1",
            correlation_id="foundation-correlation-1",
            authority_ref="authority-grant:fixture",
            profile_ref="profile:deterministic",
            budget_ref="budget:zero-external",
            model_policy_ref="model-policy:no-llm",
        ),
        parent_projection_id=parent_projection_id,
        parent_evidence_as_of=parent_as_of,
        new_evidence_ids=new_evidence_ids,
        sources=(source(),),
        providers=(
            ProviderAdapterIdentity(
                provider_id="provider:official-ir",
                adapter_id="adapter:official-ir",
                adapter_version="1.0",
                original_provider_id="reliance_ir",
            ),
        ),
        origins=(origin(),),
        document_families=(family,),
        document_versions=(document,),
        occurrences=occurrence_items,
        assertions=assertion_items,
        admissions=admissions,
        authority_assessments=(authority(),),
        epistemic_projections=epistemic,
        referenced_artifact_digests=(
            ("a3-package", package.manifest.exact_package_checksum),
            ("a2-capture", package.manifest.a2_capture.blob.checksum),
            ("a38-capture", package.manifest.a38_capture.checksum),
            ("a39-capture", package.manifest.a39_capture.checksum),
        ),
        usage_cost_knowledge=(("provider/model calls", "KNOWN_ZERO"),),
    )
