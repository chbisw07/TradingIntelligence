"""Provider-neutral authoritative source validation, parsing, and confirmation."""

import hashlib
import ipaddress
import re
from collections.abc import Iterable
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import parse_qsl, urlsplit

from tiaf.contracts import DataQuality, FreshnessState
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.events import EventCluster, EventMateriality, NormalizedEvent, StructuredEventFact
from tiaf.events.enums import StructuredFactKind

from .authoritative_models import (
    AuthoritativeConfirmationRequest,
    AuthoritativeConfirmationResult,
    AuthoritativeDocumentEvidence,
    AuthoritativeEscalationDecision,
    CachedDocumentContent,
    ConfirmationRouteAudit,
    ConfirmedFieldFact,
    DocumentExtractionRule,
    DocumentParseResult,
    DomainValidationRecord,
    OfficialSourceRegistration,
    SourceAuthorityMetadata,
    UnresolvedDiscrepancy,
)
from .enums import (
    ConfirmationReasonCode,
    ConfirmationStatus,
    DerivationClass,
    DocumentParseStatus,
    GraphEdgeStatus,
    GraphRelation,
    MaterialityTrigger,
    ProviderFailureKind,
    RoutingMode,
    SemanticMappingQuality,
    SourceAuthority,
)
from .graph import EvidenceGraphEdge, EvidenceGraphProvenance
from .models import CapabilityRoutePolicy, MarketIntelligenceRequest
from .routing import MarketIntelligenceRouter


class SourceValidationError(ValueError):
    def __init__(self, message: str, *, kind: ProviderFailureKind) -> None:
        super().__init__(message)
        self.kind = kind


class OfficialSourceRegistry:
    """Explicit configuration registry; a URL cannot elevate its own authority."""

    def __init__(self, registrations: Iterable[OfficialSourceRegistration] = ()) -> None:
        self._registrations: dict[str, OfficialSourceRegistration] = {}
        for registration in registrations:
            self.register(registration)

    def register(self, registration: OfficialSourceRegistration) -> None:
        if registration.source_id in self._registrations:
            raise ValueError(f"official source already registered: {registration.source_id}")
        self._registrations[registration.source_id] = registration

    def registration(self, source_id: str) -> OfficialSourceRegistration:
        try:
            return self._registrations[source_id]
        except KeyError as exc:
            raise LookupError(f"official source not registered: {source_id}") from exc

    def validate(
        self,
        source_id: str,
        requested_url: str,
        *,
        final_url: str | None = None,
    ) -> DomainValidationRecord:
        registration = self.registration(source_id)
        requested_domain = self._validated_host(requested_url, registration)
        resolved_url = final_url or requested_url
        final_domain = self._validated_host(resolved_url, registration)
        return DomainValidationRecord(
            source_id=source_id,
            requested_url=requested_url,
            final_url=resolved_url,
            requested_domain=requested_domain,
            final_domain=final_domain,
            source=SourceAuthorityMetadata(
                source_id=registration.source_id,
                provider_id=registration.provider_id,
                display_name=registration.display_name,
                kind=registration.kind,
                authority=registration.authority,
                validated_domain=final_domain,
                registry_version=registration.registry_version,
            ),
        )

    @staticmethod
    def _validated_host(url: str, registration: OfficialSourceRegistration) -> str:
        parsed = urlsplit(url)
        if parsed.scheme.casefold() != "https":
            raise SourceValidationError(
                "official sources require HTTPS",
                kind=ProviderFailureKind.AMBIGUOUS_SOURCE_AUTHENTICITY,
            )
        if parsed.username is not None or parsed.password is not None:
            raise SourceValidationError(
                "official source URL cannot contain credentials",
                kind=ProviderFailureKind.AMBIGUOUS_SOURCE_AUTHENTICITY,
            )
        sensitive_markers = ("token", "secret", "password", "cookie", "session", "api_key")
        query_keys = tuple(key.casefold() for key, _ in parse_qsl(parsed.query))
        if any(marker in key for key in query_keys for marker in sensitive_markers):
            raise SourceValidationError(
                "official source URL cannot contain credential-like query parameters",
                kind=ProviderFailureKind.AMBIGUOUS_SOURCE_AUTHENTICITY,
            )
        try:
            port = parsed.port
        except ValueError as exc:
            raise SourceValidationError(
                "official source URL has invalid port",
                kind=ProviderFailureKind.AMBIGUOUS_SOURCE_AUTHENTICITY,
            ) from exc
        if port not in {None, 443}:
            raise SourceValidationError(
                "official source URL cannot use a non-HTTPS port",
                kind=ProviderFailureKind.AMBIGUOUS_SOURCE_AUTHENTICITY,
            )
        host = (parsed.hostname or "").casefold().rstrip(".")
        if not host:
            raise SourceValidationError(
                "official source URL requires a host",
                kind=ProviderFailureKind.AMBIGUOUS_SOURCE_AUTHENTICITY,
            )
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            raise SourceValidationError(
                "official source URL cannot use an IP literal",
                kind=ProviderFailureKind.AMBIGUOUS_SOURCE_AUTHENTICITY,
            )
        if not any(
            host == domain or host.endswith(f".{domain}")
            for domain in registration.official_domains
        ):
            raise SourceValidationError(
                f"domain is not registered for official source: {host}",
                kind=ProviderFailureKind.INVALID_REDIRECT,
            )
        return host


class DocumentContentCache:
    """Small immutable content-addressed cache; provenance stays on documents."""

    def __init__(self) -> None:
        self._content: dict[str, bytes] = {}

    def put(self, content: bytes) -> CachedDocumentContent:
        if not content:
            raise ValueError("authoritative document content cannot be empty")
        content_hash = hashlib.sha256(content).hexdigest()
        self._content.setdefault(content_hash, bytes(content))
        return CachedDocumentContent(
            content_hash=content_hash,
            content_length=len(content),
            content_reference=f"sha256:{content_hash}",
        )

    def get(self, content_hash: str) -> bytes:
        try:
            return self._content[content_hash]
        except KeyError as exc:
            raise LookupError(f"document content not cached: {content_hash}") from exc

    def __len__(self) -> int:
        return len(self._content)


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text: list[str] = []
        self.title: list[str] = []
        self._in_title = False
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag in {"script", "style"}:
            self._ignored_depth += 1
        elif tag == "title":
            self._in_title = True
        elif tag in {"br", "p", "div", "tr", "li", "h1", "h2", "h3"}:
            self.text.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._ignored_depth:
            self._ignored_depth -= 1
        elif tag == "title":
            self._in_title = False
        elif tag in {"p", "div", "tr", "li", "h1", "h2", "h3"}:
            self.text.append("\n")

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        self.text.append(data)
        if self._in_title:
            self.title.append(data)


class PlainTextHtmlDocumentParser:
    parser_id = "tiaf-plain-text-html"
    parser_version = "1.0"

    def parse(
        self,
        content: bytes,
        mime_type: str,
        rules: tuple[DocumentExtractionRule, ...] = (),
    ) -> DocumentParseResult:
        normalized_mime = mime_type.partition(";")[0].strip().casefold()
        if normalized_mime not in {"text/plain", "text/html", "application/xhtml+xml"}:
            return DocumentParseResult(
                parser_id=self.parser_id,
                parser_version=self.parser_version,
                status=DocumentParseStatus.UNSUPPORTED,
                failure_kind=ProviderFailureKind.UNSUPPORTED_DOCUMENT_TYPE,
                message=(
                    "deterministic parser does not support "
                    f"{normalized_mime or 'unknown MIME'}"
                ),
            )
        try:
            decoded = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                decoded = content.decode("latin-1")
            except UnicodeDecodeError:
                return DocumentParseResult(
                    parser_id=self.parser_id,
                    parser_version=self.parser_version,
                    status=DocumentParseStatus.FAILED,
                    failure_kind=ProviderFailureKind.PARSE_FAILURE,
                    message="document text decoding failed",
                )
        if not decoded.strip():
            return DocumentParseResult(
                parser_id=self.parser_id,
                parser_version=self.parser_version,
                status=DocumentParseStatus.FAILED,
                failure_kind=ProviderFailureKind.PARSE_FAILURE,
                message="document contains no text",
            )
        title: str | None = None
        if normalized_mime in {"text/html", "application/xhtml+xml"}:
            extractor = _VisibleTextParser()
            try:
                extractor.feed(decoded)
            except Exception:
                return DocumentParseResult(
                    parser_id=self.parser_id,
                    parser_version=self.parser_version,
                    status=DocumentParseStatus.FAILED,
                    failure_kind=ProviderFailureKind.PARSE_FAILURE,
                    message="HTML parsing failed",
                )
            text = " ".join("".join(extractor.text).split())
            title_text = " ".join("".join(extractor.title).split())
            title = title_text or None
        else:
            text = " ".join(decoded.split())

        facts: list[StructuredEventFact] = []
        matched: list[str] = []
        for rule in rules:
            raw_value = self._extract_label_value(text, rule)
            if raw_value is None:
                continue
            try:
                value = self._coerce_value(raw_value, rule.kind)
            except ValueError:
                continue
            facts.append(
                StructuredEventFact(
                    field_id=rule.canonical_metric,
                    kind=StructuredFactKind(rule.kind),
                    value=value,
                    unit=rule.unit,
                    currency=rule.currency,
                    locator=f"label:{rule.source_label}",
                    extraction_method="DETERMINISTIC_EXACT_LABEL",
                    extraction_version=self.parser_version,
                )
            )
            matched.append(rule.field_id)
        status = (
            DocumentParseStatus.SUCCESS
            if len(facts) == len(rules)
            else DocumentParseStatus.PARTIAL
        )
        if not rules:
            status = DocumentParseStatus.SUCCESS
        return DocumentParseResult(
            parser_id=self.parser_id,
            parser_version=self.parser_version,
            status=status,
            title=title,
            facts=tuple(facts),
            matched_rule_ids=tuple(matched),
        )

    @staticmethod
    def _extract_label_value(text: str, rule: DocumentExtractionRule) -> str | None:
        escaped = re.escape(rule.source_label)
        if rule.kind in {"INTEGER", "NUMBER"}:
            suffix = r"([-+]?[0-9][0-9,]*(?:\.[0-9]+)?)"
        elif rule.kind == "BOOLEAN":
            suffix = r"(true|false|yes|no)"
        elif rule.kind == "DATE":
            suffix = r"([0-9]{4}-[0-9]{2}-[0-9]{2})"
        else:
            suffix = r"([^|;]{1,200}?)(?=\s+[A-Z][A-Za-z ]{2,40}\s*[:=]|$)"
        match = re.search(rf"{escaped}\s*[:=]\s*{suffix}", text, flags=re.IGNORECASE)
        return match.group(1).strip() if match else None

    @staticmethod
    def _coerce_value(value: str, kind: str) -> str | int | float | bool:
        if kind == "INTEGER":
            return int(value.replace(",", ""))
        if kind == "NUMBER":
            return float(value.replace(",", ""))
        if kind == "BOOLEAN":
            return value.casefold() in {"true", "yes"}
        return value


class AuthoritativeEscalationPolicy:
    policy_id = "authoritative-materiality"
    policy_version = "1.0"

    def evaluate(
        self,
        claim_materiality: EventMateriality,
        triggers: tuple[MaterialityTrigger, ...],
    ) -> AuthoritativeEscalationDecision:
        material_triggers = tuple(
            item for item in triggers if item is not MaterialityTrigger.ROUTINE_LOW_MATERIALITY
        )
        should_confirm = (
            bool(material_triggers) and claim_materiality is not EventMateriality.IMMATERIAL
        )
        reason = (
            "material claim has an allow-listed authoritative-confirmation trigger"
            if should_confirm
            else "routine or immaterial evidence does not justify authoritative acquisition"
        )
        return AuthoritativeEscalationDecision(
            should_confirm=should_confirm,
            triggers=material_triggers if should_confirm else (),
            reason=reason,
            policy_id=self.policy_id,
            policy_version=self.policy_version,
        )


class AuthoritativeConfirmationGateway:
    """Reconcile a material claim using an existing authoritative router run."""

    def __init__(
        self,
        router: MarketIntelligenceRouter,
        *,
        escalation_policy: AuthoritativeEscalationPolicy | None = None,
    ) -> None:
        self._router = router
        self._escalation_policy = escalation_policy or AuthoritativeEscalationPolicy()

    def execute(
        self,
        request: AuthoritativeConfirmationRequest,
        route_policy: CapabilityRoutePolicy,
        *,
        run_id: str,
        confirmation_id: str,
    ) -> AuthoritativeConfirmationResult:
        escalation = self._escalation_policy.evaluate(
            request.claim.materiality,
            request.materiality_triggers,
        )
        if not escalation.should_confirm:
            raise ValueError("authoritative confirmation is not justified by materiality policy")
        if route_policy.mode is not RoutingMode.AUTHORITATIVE_CONFIRMATION:
            raise ValueError("authoritative gateway requires AUTHORITATIVE_CONFIRMATION routing")
        if route_policy.policy_id != request.route_policy_id:
            raise ValueError("confirmation request and route policy IDs disagree")
        if route_policy.policy_version != request.route_policy_version:
            raise ValueError("confirmation request and route policy versions disagree")

        market_request = MarketIntelligenceRequest(
            request_id=f"{request.request_id}:route",
            capability=request.claim.capability,
            authority=request.authority,
            allowed_authorities=request.allowed_authorities,
            subject=request.claim.subject,
            as_of=request.as_of,
            horizon=request.horizon,
            required_freshness=FreshnessState.UNKNOWN,
            required_canonical_metrics=request.required_fields,
            budget=request.budget,
            attributes={
                "accepted_document_kinds": [item.value for item in request.accepted_document_kinds],
                "eligible_source_kinds": [item.value for item in request.eligible_source_kinds],
                "claim_id": request.claim.claim_id,
            },
        )
        run = self._router.execute(market_request, route_policy, run_id=run_id)
        documents = tuple(
            document
            for batch in run.batches
            for document in batch.authoritative_documents
            if document.document_kind in request.accepted_document_kinds
            and document.source.kind in request.eligible_source_kinds
        )
        canonical_by_metric = {
            item.metric: item
            for batch in run.batches
            for item in batch.canonical_evidence
        }
        facts_by_field = {
            fact.field_id: (document, fact)
            for document in documents
            for fact in document.facts
        }
        claimed_by_field = {item.field_id: item for item in request.claim.asserted_facts}
        confirmed: list[ConfirmedFieldFact] = []
        discrepancies: list[UnresolvedDiscrepancy] = []
        for field_id in request.required_fields:
            claimed = claimed_by_field[field_id]
            authoritative = facts_by_field.get(field_id)
            if authoritative is None:
                discrepancies.append(
                    UnresolvedDiscrepancy(
                        field_id=field_id,
                        claimed_value=claimed.value,
                        discovery_evidence_ids=request.claim.discovery_evidence_ids,
                        reason="required field absent from acquired authoritative evidence",
                    )
                )
                continue
            document, fact = authoritative
            if fact.value == claimed.value:
                projection = canonical_by_metric.get(field_id)
                confirmed.append(
                    ConfirmedFieldFact(
                        field_id=field_id,
                        claimed_value=claimed.value,
                        authoritative_value=fact.value,
                        authoritative_evidence_id=(
                            projection.evidence_id
                            if projection is not None
                            else document.document_id
                        ),
                        canonical_metric=field_id,
                        mapping_quality=(
                            projection.mapping_quality
                            if projection is not None
                            else SemanticMappingQuality.EXACT
                        ),
                        source_locator=fact.locator,
                        unit=fact.unit,
                        currency=fact.currency,
                        period=document.period,
                        statement_basis=document.statement_basis,
                    )
                )
            else:
                discrepancies.append(
                    UnresolvedDiscrepancy(
                        field_id=field_id,
                        claimed_value=claimed.value,
                        authoritative_value=fact.value,
                        discovery_evidence_ids=request.claim.discovery_evidence_ids,
                        authoritative_evidence_ids=(document.document_id,),
                        reason="authoritative field value contradicts discovery claim",
                    )
                )

        status, reasons, quality = self._classify(
            documents,
            tuple(confirmed),
            tuple(discrepancies),
            tuple(item.kind for item in run.failures),
        )
        authority = self._strongest_authority(documents)
        evidence_ids = tuple(
            dict.fromkeys(
                [item.document_id for item in documents]
                + [item.evidence_id for batch in run.batches for item in batch.canonical_evidence]
            )
        )
        audits = tuple(
            ConfirmationRouteAudit(
                sequence=item.sequence,
                provider_id=item.provider_id,
                status=item.status,
                failure_kinds=item.failure_kinds,
            )
            for item in run.audits
        )
        confirmed_at = datetime.now(TIAF_TIMEZONE)
        confirmed_facts = tuple(confirmed)
        unresolved_discrepancies = tuple(discrepancies)
        fingerprint = AuthoritativeConfirmationResult.fingerprint_for(
            confirmation_id=confirmation_id,
            request=request,
            status=status,
            authoritative_documents=documents,
            authoritative_evidence_ids=evidence_ids,
            confirmed_facts=confirmed_facts,
            unresolved_discrepancies=unresolved_discrepancies,
            source_authority=authority,
            reason_codes=reasons,
            route_run_id=run.run_id,
            route_run_fingerprint=run.fingerprint,
            route_audits=audits,
            event_cluster_id=request.claim.event_cluster_id,
            evidence_graph_node_ids=(),
            confirmed_at=confirmed_at,
            quality=quality,
        )
        return AuthoritativeConfirmationResult(
            confirmation_id=confirmation_id,
            request=request,
            status=status,
            authoritative_documents=documents,
            authoritative_evidence_ids=evidence_ids,
            confirmed_facts=confirmed_facts,
            unresolved_discrepancies=unresolved_discrepancies,
            source_authority=authority,
            reason_codes=reasons,
            route_run_id=run.run_id,
            route_run_fingerprint=run.fingerprint,
            route_audits=audits,
            event_cluster_id=request.claim.event_cluster_id,
            evidence_graph_node_ids=(),
            usage=run.usage,
            confirmed_at=confirmed_at,
            quality=quality,
            semantic_fingerprint=fingerprint,
        )

    @staticmethod
    def _classify(
        documents: tuple[AuthoritativeDocumentEvidence, ...],
        confirmed: tuple[ConfirmedFieldFact, ...],
        discrepancies: tuple[UnresolvedDiscrepancy, ...],
        failure_kinds: tuple[ProviderFailureKind, ...],
    ) -> tuple[ConfirmationStatus, tuple[ConfirmationReasonCode, ...], DataQuality]:
        conflicts = any(item.authoritative_value is not None for item in discrepancies)
        if confirmed and not discrepancies:
            return (
                ConfirmationStatus.CONFIRMED,
                (ConfirmationReasonCode.ALL_REQUIRED_FIELDS_MATCH,),
                DataQuality.GOOD,
            )
        if confirmed:
            return (
                ConfirmationStatus.PARTIALLY_CONFIRMED,
                (
                    ConfirmationReasonCode.SOME_REQUIRED_FIELDS_MATCH,
                    ConfirmationReasonCode.REQUIRED_FIELD_MISSING,
                ),
                DataQuality.PARTIAL,
            )
        if conflicts:
            return (
                ConfirmationStatus.CONTRADICTED,
                (ConfirmationReasonCode.AUTHORITATIVE_FIELD_CONFLICT,),
                DataQuality.GOOD,
            )
        if documents:
            return (
                ConfirmationStatus.AMBIGUOUS,
                (
                    ConfirmationReasonCode.SEMANTICS_AMBIGUOUS,
                    ConfirmationReasonCode.REQUIRED_FIELD_MISSING,
                ),
                DataQuality.PARTIAL,
            )
        if ProviderFailureKind.OUT_OF_COVERAGE in failure_kinds:
            return (
                ConfirmationStatus.OUT_OF_COVERAGE,
                (ConfirmationReasonCode.SOURCE_OUT_OF_COVERAGE,),
                DataQuality.UNAVAILABLE,
            )
        if ProviderFailureKind.DOCUMENT_UNAVAILABLE in failure_kinds:
            return (
                ConfirmationStatus.NOT_FOUND,
                (ConfirmationReasonCode.DOCUMENT_NOT_FOUND,),
                DataQuality.UNAVAILABLE,
            )
        if ProviderFailureKind.AMBIGUOUS_SOURCE_AUTHENTICITY in failure_kinds or (
            ProviderFailureKind.INVALID_REDIRECT in failure_kinds
        ):
            return (
                ConfirmationStatus.AMBIGUOUS,
                (ConfirmationReasonCode.SOURCE_AUTHENTICITY_AMBIGUOUS,),
                DataQuality.UNAVAILABLE,
            )
        access_failures = {
            ProviderFailureKind.ACCESS_RESTRICTED,
            ProviderFailureKind.ANTI_BOT_DENIED,
        }
        reasons = (
            (ConfirmationReasonCode.ACCESS_RESTRICTED,)
            if access_failures & set(failure_kinds)
            else (ConfirmationReasonCode.SOURCE_UNAVAILABLE,)
        )
        return ConfirmationStatus.UNAVAILABLE, reasons, DataQuality.UNAVAILABLE

    @staticmethod
    def _strongest_authority(
        documents: tuple[AuthoritativeDocumentEvidence, ...],
    ) -> SourceAuthority | None:
        rank = {
            SourceAuthority.UNKNOWN: 0,
            SourceAuthority.AGGREGATOR: 1,
            SourceAuthority.TRUSTED_SECONDARY: 2,
            SourceAuthority.PRIMARY: 3,
            SourceAuthority.AUTHORITATIVE: 4,
        }
        return max(
            (item.source.authority for item in documents),
            key=lambda item: rank[item],
            default=None,
        )


def merge_authoritative_event(
    cluster: EventCluster,
    event: NormalizedEvent,
) -> EventCluster:
    """Add one source record to an existing economic-event cluster."""
    if event.primary_entity.canonical_symbol != cluster.subject:
        raise ValueError("authoritative event subject must match cluster")
    if event.family is not cluster.family or event.event_type is not cluster.event_type:
        raise ValueError("authoritative event semantics must match cluster")
    if event.event_id in cluster.event_ids:
        return cluster
    active = list(cluster.active_event_ids)
    superseded = list(cluster.superseded_event_ids)
    if event.supersedes_event_id is not None:
        if event.supersedes_event_id not in cluster.event_ids:
            raise ValueError("superseded event must already belong to cluster")
        active = [item for item in active if item != event.supersedes_event_id]
        if event.supersedes_event_id not in superseded:
            superseded.append(event.supersedes_event_id)
    active.append(event.event_id)
    return cluster.model_copy(
        update={
            "event_ids": (*cluster.event_ids, event.event_id),
            "active_event_ids": tuple(active),
            "superseded_event_ids": tuple(superseded),
        }
    )


def authoritative_event_graph_edge(
    document: AuthoritativeDocumentEvidence,
    event: NormalizedEvent,
    *,
    edge_id: str,
    source_node_id: str,
    target_node_id: str,
    materiality: float,
) -> EvidenceGraphEdge:
    """Project one official event into the existing evidence-graph contract."""
    if event.source.document_id != document.document_id:
        raise ValueError("graph event must cite the authoritative document")
    return EvidenceGraphEdge(
        edge_id=edge_id,
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        relation=GraphRelation.HAS_CATALYST,
        status=GraphEdgeStatus.CONFIRMED,
        materiality=materiality,
        evidence_quality=DataQuality.GOOD,
        confidence_basis="validated official-source document",
        provenance=EvidenceGraphProvenance(
            provider_id=document.source.provider_id,
            evidence_ids=(document.document_id, event.event_id),
            source_references=(document.final_url,),
            observed_at=event.event_time,
            available_from=document.available_from,
            acquired_at=document.acquired_at,
            last_verified_at=document.acquired_at,
            derivation_class=DerivationClass.REPORTED,
        ),
        valid_from=event.event_time,
        edge_version=document.revision + 1,
        supersedes_edge_id=None,
    )
