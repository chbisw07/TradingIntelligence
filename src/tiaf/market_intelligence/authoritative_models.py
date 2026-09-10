"""Immutable provider-neutral contracts for authoritative confirmation."""

import hashlib
import json
from datetime import date
from typing import Annotated, Self

from pydantic import Field, StrictBool, StrictFloat, StrictInt, StrictStr, model_validator

from tiaf.agents import AgentBudget, AgentCapability, AgentUsage
from tiaf.contracts import ContractModel, DataQuality, Horizon
from tiaf.contracts.common import NonEmptyStr, Symbol, TiafDateTime
from tiaf.events import EventMateriality, StructuredEventFact

from .enums import (
    AuthoritativeDocumentKind,
    ConfirmationReasonCode,
    ConfirmationStatus,
    DocumentParseStatus,
    MarketIntelligenceCapability,
    MaterialityTrigger,
    OfficialSourceKind,
    PointInTimeQuality,
    ProviderFailureKind,
    ProviderResultStatus,
    SemanticMappingQuality,
    SourceAuthority,
)

type AuthoritativeFactValue = StrictStr | StrictInt | StrictFloat | StrictBool
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


def _unique(values: tuple[object, ...], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must be unique")


class OfficialSourceRegistration(ContractModel):
    source_id: NonEmptyStr
    provider_id: NonEmptyStr
    display_name: NonEmptyStr
    kind: OfficialSourceKind
    authority: SourceAuthority
    official_domains: tuple[NonEmptyStr, ...]
    registry_version: NonEmptyStr = "1.0"
    limitations: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_registration(self) -> Self:
        if self.authority not in {SourceAuthority.AUTHORITATIVE, SourceAuthority.PRIMARY}:
            raise ValueError("official source must have authoritative or primary authority")
        if not self.official_domains:
            raise ValueError("official source requires validated domains")
        normalized = tuple(item.casefold().rstrip(".") for item in self.official_domains)
        if normalized != self.official_domains:
            raise ValueError("official domains must be normalized lower-case host names")
        if any("://" in item or "*" in item or "/" in item for item in normalized):
            raise ValueError("official domains must be literal host names")
        _unique(normalized, "official domains")
        return self


class SourceAuthorityMetadata(ContractModel):
    source_id: NonEmptyStr
    provider_id: NonEmptyStr
    display_name: NonEmptyStr
    kind: OfficialSourceKind
    authority: SourceAuthority
    validated_domain: NonEmptyStr
    registry_version: NonEmptyStr


class DomainValidationRecord(ContractModel):
    source_id: NonEmptyStr
    requested_url: NonEmptyStr
    final_url: NonEmptyStr
    requested_domain: NonEmptyStr
    final_domain: NonEmptyStr
    source: SourceAuthorityMetadata


class DocumentExtractionRule(ContractModel):
    field_id: NonEmptyStr
    source_label: NonEmptyStr
    kind: NonEmptyStr = "NUMBER"
    canonical_metric: NonEmptyStr
    mapping_quality: SemanticMappingQuality = SemanticMappingQuality.EXACT
    unit: NonEmptyStr | None = None
    currency: NonEmptyStr | None = None
    period: NonEmptyStr | None = None
    statement_basis: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_rule(self) -> Self:
        if self.mapping_quality not in {
            SemanticMappingQuality.EXACT,
            SemanticMappingQuality.WELL_SUPPORTED,
        }:
            raise ValueError("authoritative extraction rule must have canonical semantics")
        if self.kind not in {"TEXT", "INTEGER", "NUMBER", "BOOLEAN", "DATE"}:
            raise ValueError("unsupported extraction kind")
        if self.currency is not None and self.unit is None:
            raise ValueError("currency requires unit")
        return self


class DocumentParseResult(ContractModel):
    parser_id: NonEmptyStr
    parser_version: NonEmptyStr
    status: DocumentParseStatus
    title: NonEmptyStr | None = None
    facts: tuple[StructuredEventFact, ...] = ()
    matched_rule_ids: tuple[NonEmptyStr, ...] = ()
    failure_kind: ProviderFailureKind | None = None
    message: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        _unique(tuple(item.field_id for item in self.facts), "parsed fact fields")
        if self.status in {DocumentParseStatus.FAILED, DocumentParseStatus.UNSUPPORTED}:
            if self.failure_kind is None or self.message is None:
                raise ValueError("failed/unsupported parse requires typed failure")
            if self.facts:
                raise ValueError("failed parse cannot emit facts")
        elif self.failure_kind is not None or self.message is not None:
            raise ValueError("successful parse cannot carry failure")
        return self


class CachedDocumentContent(ContractModel):
    content_hash: Sha256
    content_length: int = Field(ge=0)
    content_reference: NonEmptyStr


class AuthoritativeDocumentEvidence(ContractModel):
    document_id: NonEmptyStr
    subject: Symbol
    source: SourceAuthorityMetadata
    document_kind: AuthoritativeDocumentKind
    title: NonEmptyStr
    source_url: NonEmptyStr
    final_url: NonEmptyStr
    mime_type: NonEmptyStr
    content_length: int = Field(ge=0)
    content_hash: Sha256
    content_reference: NonEmptyStr
    provider_document_id: NonEmptyStr | None = None
    filing_reference: NonEmptyStr | None = None
    published_at: TiafDateTime | None = None
    exchange_timestamp: TiafDateTime | None = None
    event_date: date | None = None
    available_from: TiafDateTime
    acquired_at: TiafDateTime
    period: NonEmptyStr | None = None
    financial_year: NonEmptyStr | None = None
    quarter: NonEmptyStr | None = None
    statement_basis: NonEmptyStr | None = None
    audited: bool | None = None
    unit: NonEmptyStr | None = None
    currency: NonEmptyStr | None = None
    facts: tuple[StructuredEventFact, ...] = ()
    parse_status: DocumentParseStatus = DocumentParseStatus.NOT_ATTEMPTED
    parser_id: NonEmptyStr | None = None
    parser_version: NonEmptyStr | None = None
    point_in_time_quality: PointInTimeQuality
    revision: int = Field(default=0, ge=0)
    supersedes_document_id: NonEmptyStr | None = None
    superseded_by_document_id: NonEmptyStr | None = None
    raw_content_retained: bool = True

    @model_validator(mode="after")
    def validate_document(self) -> Self:
        if self.acquired_at < self.available_from:
            raise ValueError("document acquisition cannot predate availability")
        if self.published_at is not None and self.available_from < self.published_at:
            raise ValueError("document availability cannot predate publication")
        if self.exchange_timestamp is not None and self.available_from < self.exchange_timestamp:
            raise ValueError("document availability cannot predate exchange timestamp")
        if self.currency is not None and self.unit is None:
            raise ValueError("document currency requires unit")
        if self.document_id in {
            self.supersedes_document_id,
            self.superseded_by_document_id,
        }:
            raise ValueError("document cannot supersede itself")
        if self.supersedes_document_id is not None and self.revision == 0:
            raise ValueError("superseding document requires a positive revision")
        if (self.parser_id is None) != (self.parser_version is None):
            raise ValueError("parser ID and version must appear together")
        if self.parse_status is not DocumentParseStatus.NOT_ATTEMPTED and self.parser_id is None:
            raise ValueError("attempted parse requires parser identity")
        _unique(tuple(item.field_id for item in self.facts), "document fact fields")
        return self


class DiscoveredClaim(ContractModel):
    claim_id: NonEmptyStr
    subject: Symbol
    capability: MarketIntelligenceCapability
    asserted_facts: tuple[StructuredEventFact, ...]
    discovery_evidence_ids: tuple[NonEmptyStr, ...]
    event_cluster_id: NonEmptyStr | None = None
    materiality: EventMateriality
    published_at: TiafDateTime | None = None
    available_from: TiafDateTime
    created_at: TiafDateTime

    @model_validator(mode="after")
    def validate_claim(self) -> Self:
        if not self.asserted_facts or not self.discovery_evidence_ids:
            raise ValueError("discovered claim requires facts and discovery evidence")
        _unique(tuple(item.field_id for item in self.asserted_facts), "claim fact fields")
        _unique(self.discovery_evidence_ids, "discovery evidence IDs")
        if self.created_at < self.available_from:
            raise ValueError("claim creation cannot predate availability")
        if self.published_at is not None and self.available_from < self.published_at:
            raise ValueError("claim availability cannot predate publication")
        return self


class AuthoritativeConfirmationRequest(ContractModel):
    request_id: NonEmptyStr
    claim: DiscoveredClaim
    as_of: TiafDateTime
    horizon: Horizon
    authority: AgentCapability
    allowed_authorities: tuple[AgentCapability, ...]
    accepted_document_kinds: tuple[AuthoritativeDocumentKind, ...]
    eligible_source_kinds: tuple[OfficialSourceKind, ...]
    required_fields: tuple[NonEmptyStr, ...]
    materiality_triggers: tuple[MaterialityTrigger, ...]
    budget: AgentBudget
    route_policy_id: NonEmptyStr
    route_policy_version: NonEmptyStr

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        if self.as_of < self.claim.available_from:
            raise ValueError("confirmation as-of cannot predate claim availability")
        if self.authority not in self.allowed_authorities:
            raise ValueError("confirmation authority exceeds allowed authorities")
        for values, label in (
            (self.accepted_document_kinds, "accepted document kinds"),
            (self.eligible_source_kinds, "eligible source kinds"),
            (self.required_fields, "required confirmation fields"),
            (self.materiality_triggers, "materiality triggers"),
        ):
            if not values:
                raise ValueError(f"{label} cannot be empty")
            _unique(values, label)
        claim_fields = {item.field_id for item in self.claim.asserted_facts}
        if not set(self.required_fields) <= claim_fields:
            raise ValueError("required fields must belong to the discovered claim")
        return self


class AuthoritativeEscalationDecision(ContractModel):
    should_confirm: bool
    triggers: tuple[MaterialityTrigger, ...]
    reason: NonEmptyStr
    policy_id: NonEmptyStr
    policy_version: NonEmptyStr

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        _unique(self.triggers, "escalation triggers")
        if self.should_confirm and not self.triggers:
            raise ValueError("confirmation escalation requires a trigger")
        return self


class ConfirmedFieldFact(ContractModel):
    field_id: NonEmptyStr
    claimed_value: AuthoritativeFactValue
    authoritative_value: AuthoritativeFactValue
    authoritative_evidence_id: NonEmptyStr
    canonical_metric: NonEmptyStr
    mapping_quality: SemanticMappingQuality
    source_locator: NonEmptyStr | None = None
    unit: NonEmptyStr | None = None
    currency: NonEmptyStr | None = None
    period: NonEmptyStr | None = None
    statement_basis: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_confirmation(self) -> Self:
        if self.claimed_value != self.authoritative_value:
            raise ValueError("confirmed field values must match")
        if self.mapping_quality not in {
            SemanticMappingQuality.EXACT,
            SemanticMappingQuality.WELL_SUPPORTED,
        }:
            raise ValueError("confirmed field requires accepted mapping semantics")
        if self.currency is not None and self.unit is None:
            raise ValueError("confirmed field currency requires unit")
        return self


class UnresolvedDiscrepancy(ContractModel):
    field_id: NonEmptyStr
    claimed_value: AuthoritativeFactValue
    authoritative_value: AuthoritativeFactValue | None = None
    discovery_evidence_ids: tuple[NonEmptyStr, ...]
    authoritative_evidence_ids: tuple[NonEmptyStr, ...] = ()
    reason: NonEmptyStr

    @model_validator(mode="after")
    def validate_discrepancy(self) -> Self:
        if not self.discovery_evidence_ids:
            raise ValueError("discrepancy must retain discovery evidence")
        _unique(self.discovery_evidence_ids, "discrepancy discovery evidence IDs")
        _unique(self.authoritative_evidence_ids, "discrepancy authoritative evidence IDs")
        return self


class ConfirmationRouteAudit(ContractModel):
    sequence: int = Field(gt=0)
    provider_id: NonEmptyStr
    status: ProviderResultStatus
    failure_kinds: tuple[ProviderFailureKind, ...] = ()


class AuthoritativeConfirmationResult(ContractModel):
    confirmation_id: NonEmptyStr
    request: AuthoritativeConfirmationRequest
    status: ConfirmationStatus
    authoritative_documents: tuple[AuthoritativeDocumentEvidence, ...] = ()
    authoritative_evidence_ids: tuple[NonEmptyStr, ...] = ()
    confirmed_facts: tuple[ConfirmedFieldFact, ...] = ()
    unresolved_discrepancies: tuple[UnresolvedDiscrepancy, ...] = ()
    source_authority: SourceAuthority | None = None
    reason_codes: tuple[ConfirmationReasonCode, ...]
    route_run_id: NonEmptyStr
    route_run_fingerprint: Sha256
    route_audits: tuple[ConfirmationRouteAudit, ...]
    event_cluster_id: NonEmptyStr | None = None
    evidence_graph_node_ids: tuple[NonEmptyStr, ...] = ()
    usage: AgentUsage = Field(default_factory=AgentUsage)
    confirmed_at: TiafDateTime
    quality: DataQuality
    semantic_fingerprint: Sha256

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        _unique(
            tuple(item.document_id for item in self.authoritative_documents),
            "authoritative document IDs",
        )
        _unique(self.authoritative_evidence_ids, "authoritative evidence IDs")
        _unique(tuple(item.field_id for item in self.confirmed_facts), "confirmed fields")
        _unique(self.reason_codes, "confirmation reason codes")
        if self.status is ConfirmationStatus.CONFIRMED and not self.confirmed_facts:
            raise ValueError("confirmed result requires confirmed facts")
        if self.status is ConfirmationStatus.PARTIALLY_CONFIRMED:
            if not self.confirmed_facts or not self.unresolved_discrepancies:
                raise ValueError("partial result requires confirmed and unresolved fields")
        if self.status is ConfirmationStatus.CONTRADICTED:
            if not any(
                item.authoritative_value is not None
                for item in self.unresolved_discrepancies
            ):
                raise ValueError("contradiction requires an authoritative conflicting value")
        if self.status in {
            ConfirmationStatus.NOT_FOUND,
            ConfirmationStatus.OUT_OF_COVERAGE,
            ConfirmationStatus.UNAVAILABLE,
        } and (self.authoritative_documents or self.confirmed_facts):
            raise ValueError("absent-source result cannot claim authoritative evidence")
        if self.authoritative_documents and self.source_authority is None:
            raise ValueError("document result requires source authority")
        if self.semantic_fingerprint != self.compute_fingerprint():
            raise ValueError("confirmation semantic fingerprint does not match content")
        return self

    def compute_fingerprint(self) -> str:
        payload = {
            "request": self.request.model_dump(mode="json"),
            "status": self.status,
            "documents": [item.model_dump(mode="json") for item in self.authoritative_documents],
            "authoritative_evidence_ids": self.authoritative_evidence_ids,
            "confirmed_facts": [item.model_dump(mode="json") for item in self.confirmed_facts],
            "unresolved_discrepancies": [
                item.model_dump(mode="json") for item in self.unresolved_discrepancies
            ],
            "source_authority": self.source_authority,
            "reason_codes": self.reason_codes,
            "route_run_id": self.route_run_id,
            "route_run_fingerprint": self.route_run_fingerprint,
            "route_audits": [item.model_dump(mode="json") for item in self.route_audits],
            "event_cluster_id": self.event_cluster_id,
            "evidence_graph_node_ids": self.evidence_graph_node_ids,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(encoded.encode()).hexdigest()

    @classmethod
    def fingerprint_for(
        cls,
        *,
        confirmation_id: str,
        request: AuthoritativeConfirmationRequest,
        status: ConfirmationStatus,
        authoritative_documents: tuple[AuthoritativeDocumentEvidence, ...],
        authoritative_evidence_ids: tuple[str, ...],
        confirmed_facts: tuple[ConfirmedFieldFact, ...],
        unresolved_discrepancies: tuple[UnresolvedDiscrepancy, ...],
        source_authority: SourceAuthority | None,
        reason_codes: tuple[ConfirmationReasonCode, ...],
        route_run_id: str,
        route_run_fingerprint: str,
        route_audits: tuple[ConfirmationRouteAudit, ...],
        event_cluster_id: str | None,
        evidence_graph_node_ids: tuple[str, ...],
        confirmed_at: TiafDateTime,
        quality: DataQuality,
    ) -> str:
        provisional = cls.model_construct(
            confirmation_id=confirmation_id,
            request=request,
            status=status,
            authoritative_documents=authoritative_documents,
            authoritative_evidence_ids=authoritative_evidence_ids,
            confirmed_facts=confirmed_facts,
            unresolved_discrepancies=unresolved_discrepancies,
            source_authority=source_authority,
            reason_codes=reason_codes,
            route_run_id=route_run_id,
            route_run_fingerprint=route_run_fingerprint,
            route_audits=route_audits,
            event_cluster_id=event_cluster_id,
            evidence_graph_node_ids=evidence_graph_node_ids,
            confirmed_at=confirmed_at,
            quality=quality,
            semantic_fingerprint="0" * 64,
        )
        return provisional.compute_fingerprint()
