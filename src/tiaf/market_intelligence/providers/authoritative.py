"""Read-only official-source adapters behind provider-neutral MI protocols."""

import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Protocol, Self, cast

from pydantic import Field, JsonValue, model_validator

from tiaf.contracts import ContractModel, DataQuality, FreshnessState
from tiaf.contracts.common import NonEmptyStr, Symbol, TiafDateTime
from tiaf.events import (
    EntityKind,
    EntityMappingStatus,
    EventEntity,
    EventFamily,
    EventMateriality,
    EventNovelty,
    EventRelevance,
    EventSource,
    EventSourceClass,
    EventStatus,
    EventType,
    NormalizedEvent,
    StructuredEventFact,
)
from tiaf.events.enums import StructuredFactKind

from ..authoritative import (
    DocumentContentCache,
    OfficialSourceRegistry,
    PlainTextHtmlDocumentParser,
    SourceValidationError,
)
from ..authoritative_models import (
    AuthoritativeDocumentEvidence,
    DocumentExtractionRule,
    OfficialSourceRegistration,
    SourceAuthorityMetadata,
)
from ..enums import (
    AuthoritativeDocumentKind,
    AvailabilityBasis,
    CapabilitySupport,
    DerivationClass,
    DocumentParseStatus,
    EvidenceOutputType,
    MarketIntelligenceCapability,
    OfficialSourceKind,
    PointInTimeQuality,
    ProviderFailureKind,
    ProviderResultStatus,
    SemanticMappingQuality,
    SourceAuthority,
)
from ..models import (
    CanonicalEvidenceProjection,
    MarketIntelligenceRequest,
    NormalizationRecord,
    NormalizedEvidenceBatch,
    ProviderCapabilityConstraints,
    ProviderCapabilityDeclaration,
    ProviderFailure,
    ProviderFetchResult,
    ProviderIdentity,
    ProviderManifest,
    ProviderNativeObservation,
)


class OfficialDocumentLocator(ContractModel):
    locator_id: NonEmptyStr
    subject: Symbol
    capability: MarketIntelligenceCapability
    document_kind: AuthoritativeDocumentKind
    source_url: NonEmptyStr
    title: NonEmptyStr
    provider_document_id: NonEmptyStr | None = None
    filing_reference: NonEmptyStr | None = None
    published_at: TiafDateTime | None = None
    exchange_timestamp: TiafDateTime | None = None
    event_date: date | None = None
    period: NonEmptyStr | None = None
    financial_year: NonEmptyStr | None = None
    quarter: NonEmptyStr | None = None
    statement_basis: NonEmptyStr | None = None
    audited: bool | None = None
    unit: NonEmptyStr | None = None
    currency: NonEmptyStr | None = None
    extraction_rules: tuple[DocumentExtractionRule, ...] = ()
    event_family: EventFamily | None = None
    event_type: EventType | None = None
    event_materiality: EventMateriality = EventMateriality.HIGH
    underlying_event_key: NonEmptyStr | None = None
    revision: int = Field(default=0, ge=0)
    supersedes_document_id: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_locator(self) -> Self:
        if self.currency is not None and self.unit is None:
            raise ValueError("locator currency requires unit")
        if (self.event_family is None) != (self.event_type is None):
            raise ValueError("event family and type must appear together")
        if self.supersedes_document_id is not None and self.revision == 0:
            raise ValueError("superseding locator requires a positive revision")
        return self


@dataclass(frozen=True, slots=True)
class OfficialDocumentResponse:
    requested_url: str
    final_url: str
    status_code: int
    mime_type: str
    content: bytes
    acquired_at: datetime


class OfficialDocumentTransportError(RuntimeError):
    def __init__(self, message: str, *, kind: ProviderFailureKind) -> None:
        super().__init__(message)
        self.kind = kind


class OfficialDocumentTransport(Protocol):
    def fetch(
        self,
        url: str,
        *,
        validate_url: Callable[[str], None],
        max_bytes: int,
        timeout_seconds: float,
    ) -> OfficialDocumentResponse: ...


def default_official_source_registry(
    company_ir_registrations: tuple[OfficialSourceRegistration, ...] = (),
) -> OfficialSourceRegistry:
    return OfficialSourceRegistry(
        (
            OfficialSourceRegistration(
                source_id="nse_official",
                provider_id="nse_official",
                display_name="National Stock Exchange of India",
                kind=OfficialSourceKind.EXCHANGE_OR_REGULATOR,
                authority=SourceAuthority.AUTHORITATIVE,
                official_domains=("nseindia.com",),
            ),
            OfficialSourceRegistration(
                source_id="bse_official",
                provider_id="bse_official",
                display_name="BSE India",
                kind=OfficialSourceKind.EXCHANGE_OR_REGULATOR,
                authority=SourceAuthority.AUTHORITATIVE,
                official_domains=("bseindia.com",),
            ),
            *company_ir_registrations,
        )
    )


class OfficialSourceMarketIntelligenceProvider:
    """One-call bounded direct-document provider for one registered source."""

    def __init__(
        self,
        source_id: str,
        source_registry: OfficialSourceRegistry,
        locators: tuple[OfficialDocumentLocator, ...],
        transport: OfficialDocumentTransport,
        cache: DocumentContentCache,
        *,
        parser: PlainTextHtmlDocumentParser | None = None,
        maximum_document_bytes: int = 20_000_000,
        timeout_seconds: float = 15.0,
    ) -> None:
        registration = source_registry.registration(source_id)
        if maximum_document_bytes <= 0 or timeout_seconds <= 0:
            raise ValueError("document size and timeout bounds must be positive")
        if any(locator.source_url != locator.source_url.strip() for locator in locators):
            raise ValueError("locator URLs must be normalized")
        locator_ids = tuple(item.locator_id for item in locators)
        if len(locator_ids) != len(set(locator_ids)):
            raise ValueError("official document locator IDs must be unique")
        self._registration = registration
        self._source_registry = source_registry
        self._locators = locators
        self._transport = transport
        self._cache = cache
        self._parser = parser or PlainTextHtmlDocumentParser()
        self._maximum_document_bytes = maximum_document_bytes
        self._timeout_seconds = timeout_seconds
        self._identity = ProviderIdentity(
            provider_id=registration.provider_id,
            display_name=registration.display_name,
            adapter_version="1.0",
        )
        capabilities = tuple(dict.fromkeys(item.capability for item in locators))
        declarations = tuple(self._declaration(capability) for capability in capabilities)
        self._manifest = ProviderManifest(
            identity=self._identity,
            source_authority=registration.authority,
            capabilities=declarations,
            read_only=True,
        )

    @property
    def identity(self) -> ProviderIdentity:
        return self._identity

    @property
    def manifest(self) -> ProviderManifest:
        return self._manifest

    def fetch(self, request: MarketIntelligenceRequest) -> ProviderFetchResult:
        candidates = tuple(item for item in self._locators if item.subject == request.subject)
        if not candidates:
            return self._failure(
                request,
                ProviderFailureKind.OUT_OF_COVERAGE,
                ProviderResultStatus.OUT_OF_COVERAGE,
                "official source has no configured coverage for canonical subject",
            )
        accepted_value = request.attributes.get("accepted_document_kinds", [])
        accepted_items = accepted_value if isinstance(accepted_value, list) else []
        accepted_kinds = {str(item) for item in accepted_items if isinstance(item, str)}
        matching = tuple(
            item
            for item in candidates
            if item.capability is request.capability
            and (not accepted_kinds or item.document_kind.value in accepted_kinds)
        )
        if not matching:
            return self._failure(
                request,
                ProviderFailureKind.DOCUMENT_UNAVAILABLE,
                ProviderResultStatus.UNAVAILABLE,
                "no matching authoritative document locator was found",
            )
        locator = matching[0]
        try:
            self._source_registry.validate(
                self._registration.source_id,
                locator.source_url,
            )

            def validate_redirect(url: str) -> None:
                self._source_registry.validate(self._registration.source_id, url)

            response = self._transport.fetch(
                locator.source_url,
                validate_url=validate_redirect,
                max_bytes=self._maximum_document_bytes,
                timeout_seconds=self._timeout_seconds,
            )
            validation = self._source_registry.validate(
                self._registration.source_id,
                locator.source_url,
                final_url=response.final_url,
            )
        except SourceValidationError as exc:
            return self._failure(
                request,
                exc.kind,
                ProviderResultStatus.INVALID_OUTPUT,
                str(exc),
            )
        except OfficialDocumentTransportError as exc:
            status = (
                ProviderResultStatus.TIMEOUT
                if exc.kind is ProviderFailureKind.TIMEOUT
                else ProviderResultStatus.UNAVAILABLE
            )
            return self._failure(request, exc.kind, status, str(exc))
        if response.status_code < 200 or response.status_code >= 300:
            return self._failure(
                request,
                ProviderFailureKind.PROVIDER_UNAVAILABLE,
                ProviderResultStatus.UNAVAILABLE,
                f"official source returned HTTP {response.status_code}",
            )
        if not response.content:
            return self._failure(
                request,
                ProviderFailureKind.DOCUMENT_UNAVAILABLE,
                ProviderResultStatus.UNAVAILABLE,
                "official document response was empty",
            )
        cached = self._cache.put(response.content)
        parsed = self._parser.parse(
            response.content,
            response.mime_type,
            locator.extraction_rules,
        )
        available_from = locator.exchange_timestamp or locator.published_at or response.acquired_at
        if available_from > request.as_of and (
            available_from - request.as_of
        ).total_seconds() > request.budget.max_elapsed_seconds:
            return self._failure(
                request,
                ProviderFailureKind.OUT_OF_COVERAGE,
                ProviderResultStatus.OUT_OF_COVERAGE,
                "authoritative document was not available by request as-of",
            )
        document_id = "authdoc:" + hashlib.sha256(
            f"{self.identity.provider_id}|{locator.locator_id}|{cached.content_hash}".encode()
        ).hexdigest()
        metadata: dict[str, object] = {
            "document_id": document_id,
            "source_id": self._registration.source_id,
            "source_display_name": self._registration.display_name,
            "source_kind": self._registration.kind.value,
            "source_authority": self._registration.authority.value,
            "validated_domain": validation.final_domain,
            "registry_version": self._registration.registry_version,
            "document_kind": locator.document_kind.value,
            "title": parsed.title or locator.title,
            "source_url": locator.source_url,
            "final_url": response.final_url,
            "mime_type": response.mime_type,
            "content_length": cached.content_length,
            "content_hash": cached.content_hash,
            "content_reference": cached.content_reference,
            "provider_document_id": locator.provider_document_id,
            "filing_reference": locator.filing_reference,
            "published_at": locator.published_at.isoformat() if locator.published_at else None,
            "exchange_timestamp": (
                locator.exchange_timestamp.isoformat() if locator.exchange_timestamp else None
            ),
            "event_date": locator.event_date.isoformat() if locator.event_date else None,
            "available_from": available_from.isoformat(),
            "acquired_at": response.acquired_at.isoformat(),
            "period": locator.period,
            "financial_year": locator.financial_year,
            "quarter": locator.quarter,
            "statement_basis": locator.statement_basis,
            "audited": locator.audited,
            "unit": locator.unit,
            "currency": locator.currency,
            "parse_status": parsed.status.value,
            "parser_id": parsed.parser_id,
            "parser_version": parsed.parser_version,
            "revision": locator.revision,
            "supersedes_document_id": locator.supersedes_document_id,
            "event_family": locator.event_family.value if locator.event_family else None,
            "event_type": locator.event_type.value if locator.event_type else None,
            "event_materiality": locator.event_materiality.value,
            "underlying_event_key": locator.underlying_event_key,
        }
        safe_metadata: dict[str, JsonValue] = {
            key: cast(JsonValue, value) for key, value in metadata.items() if value is not None
        }
        observations = [
            self._observation(
                request,
                document_id,
                "document.content_hash",
                cached.content_hash,
                safe_metadata,
                available_from,
                response.acquired_at,
                locator,
            )
        ]
        rules_by_metric = {item.canonical_metric: item for item in locator.extraction_rules}
        for fact in parsed.facts:
            rule = rules_by_metric[fact.field_id]
            fact_metadata = {
                **safe_metadata,
                "fact_kind": fact.kind.value,
                "canonical_metric": rule.canonical_metric,
                "mapping_quality": rule.mapping_quality.value,
                "source_locator": fact.locator,
                "extraction_method": fact.extraction_method,
                "extraction_version": fact.extraction_version,
            }
            observations.append(
                self._observation(
                    request,
                    document_id,
                    f"fact.{fact.field_id}",
                    fact.value,
                    fact_metadata,
                    available_from,
                    response.acquired_at,
                    locator,
                    unit=fact.unit,
                    currency=fact.currency,
                    period=rule.period or locator.period,
                )
            )
        failures: tuple[ProviderFailure, ...] = ()
        status = ProviderResultStatus.SUCCESS
        if parsed.status in {DocumentParseStatus.FAILED, DocumentParseStatus.UNSUPPORTED}:
            assert parsed.failure_kind is not None and parsed.message is not None
            failures = (
                ProviderFailure(
                    kind=parsed.failure_kind,
                    provider_id=self.identity.provider_id,
                    capability=request.capability,
                    message=parsed.message,
                ),
            )
            status = ProviderResultStatus.PARTIAL
        elif parsed.status is DocumentParseStatus.PARTIAL:
            failures = (
                ProviderFailure(
                    kind=ProviderFailureKind.AMBIGUOUS_MAPPING,
                    provider_id=self.identity.provider_id,
                    capability=request.capability,
                    message="not every explicit extraction rule matched",
                ),
            )
            status = ProviderResultStatus.PARTIAL
        return ProviderFetchResult(
            provider_id=self.identity.provider_id,
            capability=request.capability,
            status=status,
            observations=tuple(observations),
            failures=failures,
            elapsed_seconds=0,
        )

    def _declaration(
        self,
        capability: MarketIntelligenceCapability,
    ) -> ProviderCapabilityDeclaration:
        return ProviderCapabilityDeclaration(
            capability=capability,
            support=CapabilitySupport.PARTIAL,
            constraints=ProviderCapabilityConstraints(
                supported_markets=("INDIA",),
                supported_exchanges=("NSE", "BSE"),
                expected_freshness=FreshnessState.UNKNOWN,
                maximum_age=timedelta(days=3650),
                supports_historical_as_of=True,
                output_types=(EvidenceOutputType.PRIMARY_EVIDENCE,),
                source_authority=self._registration.authority,
                point_in_time_quality=PointInTimeQuality.CONSERVATIVE,
                normalizer_id=f"{self.identity.provider_id}-authoritative-normalizer",
                normalizer_version="1.0",
                native_schema_version="direct-document-v1",
                maximum_records=1,
                cost_units_per_call=0,
                limitations=("configured bounded document locators only",),
            ),
        )

    def _observation(
        self,
        request: MarketIntelligenceRequest,
        document_id: str,
        native_field: str,
        value: str | int | float | bool,
        metadata: dict[str, JsonValue],
        available_from: datetime,
        acquired_at: datetime,
        locator: OfficialDocumentLocator,
        *,
        unit: str | None = None,
        currency: str | None = None,
        period: str | None = None,
    ) -> ProviderNativeObservation:
        stable = json.dumps(
            [self.identity.provider_id, document_id, native_field, value],
            sort_keys=True,
            default=str,
        )
        return ProviderNativeObservation(
            observation_id="authobs:" + hashlib.sha256(stable.encode()).hexdigest(),
            provider_id=self.identity.provider_id,
            adapter_version=self.identity.adapter_version,
            provider_endpoint=locator.source_url,
            native_record_id=locator.provider_document_id or locator.locator_id,
            native_schema_version="direct-document-v1",
            capability=request.capability,
            subject=request.subject,
            native_field=native_field,
            native_label=native_field,
            value=value,
            unit=unit,
            currency=currency,
            period_label=period,
            native_semantics="official document metadata or explicitly extracted source label",
            published_at=locator.published_at,
            available_from=available_from,
            acquired_at=acquired_at,
            availability_basis=(
                AvailabilityBasis.EXACT_PUBLICATION_TIME
                if locator.published_at is not None or locator.exchange_timestamp is not None
                else AvailabilityBasis.ACQUISITION_TIME
            ),
            point_in_time_quality=PointInTimeQuality.CONSERVATIVE,
            source_reference=locator.source_url,
            source_quality=DataQuality.GOOD,
            revision=locator.revision,
            restatement_semantics=(
                "superseding authoritative document"
                if locator.supersedes_document_id is not None
                else None
            ),
            payload_checksum=str(metadata["content_hash"]),
            content_reference=str(metadata["content_reference"]),
            output_type=EvidenceOutputType.PRIMARY_EVIDENCE,
            derivation_class=DerivationClass.REPORTED,
            metadata=metadata,
        )

    def _failure(
        self,
        request: MarketIntelligenceRequest,
        kind: ProviderFailureKind,
        status: ProviderResultStatus,
        message: str,
    ) -> ProviderFetchResult:
        return ProviderFetchResult(
            provider_id=self.identity.provider_id,
            capability=request.capability,
            status=status,
            failures=(
                ProviderFailure(
                    kind=kind,
                    provider_id=self.identity.provider_id,
                    capability=request.capability,
                    message=message,
                ),
            ),
        )


class NseOfficialSourceProvider(OfficialSourceMarketIntelligenceProvider):
    def __init__(
        self,
        registry: OfficialSourceRegistry,
        locators: tuple[OfficialDocumentLocator, ...],
        transport: OfficialDocumentTransport,
        cache: DocumentContentCache,
        *,
        parser: PlainTextHtmlDocumentParser | None = None,
    ) -> None:
        super().__init__("nse_official", registry, locators, transport, cache, parser=parser)


class BseOfficialSourceProvider(OfficialSourceMarketIntelligenceProvider):
    def __init__(
        self,
        registry: OfficialSourceRegistry,
        locators: tuple[OfficialDocumentLocator, ...],
        transport: OfficialDocumentTransport,
        cache: DocumentContentCache,
        *,
        parser: PlainTextHtmlDocumentParser | None = None,
    ) -> None:
        super().__init__("bse_official", registry, locators, transport, cache, parser=parser)


class CompanyIrOfficialSourceProvider(OfficialSourceMarketIntelligenceProvider):
    def __init__(
        self,
        source_id: str,
        registry: OfficialSourceRegistry,
        locators: tuple[OfficialDocumentLocator, ...],
        transport: OfficialDocumentTransport,
        cache: DocumentContentCache,
        *,
        parser: PlainTextHtmlDocumentParser | None = None,
    ) -> None:
        registration = registry.registration(source_id)
        if registration.kind is not OfficialSourceKind.COMPANY_IR:
            raise ValueError("company IR provider requires COMPANY_IR registration")
        super().__init__(source_id, registry, locators, transport, cache, parser=parser)


class AuthoritativeDocumentNormalizer:
    def __init__(self, provider_id: str) -> None:
        self._provider_id = provider_id

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def normalize(
        self,
        request: MarketIntelligenceRequest,
        result: ProviderFetchResult,
    ) -> NormalizedEvidenceBatch:
        if result.provider_id != self.provider_id:
            raise ValueError("authoritative normalizer provider mismatch")
        if not result.observations:
            return NormalizedEvidenceBatch(
                provider_id=result.provider_id,
                capability=result.capability,
                native_observations=(),
                normalization_records=(),
                gaps=result.failures,
            )
        first = result.observations[0]
        metadata = first.metadata
        document = self._document(first, result.observations)
        records: list[NormalizationRecord] = []
        projections: list[CanonicalEvidenceProjection] = []
        for observation in result.observations:
            canonical_metric = observation.metadata.get("canonical_metric")
            if isinstance(canonical_metric, str):
                mapping = SemanticMappingQuality(
                    str(observation.metadata.get("mapping_quality", "EXACT"))
                )
                evidence_id = "authev:" + hashlib.sha256(
                    f"{observation.observation_id}|{canonical_metric}".encode()
                ).hexdigest()
                projections.append(
                    CanonicalEvidenceProjection(
                        evidence_id=evidence_id,
                        metric=canonical_metric,
                        value=observation.value,
                        unit=observation.unit,
                        currency=observation.currency,
                        period=observation.period_label,
                        available_from=observation.available_from,
                        source_reference=observation.source_reference or document.final_url,
                        provider_id=result.provider_id,
                        source_observation_id=observation.observation_id,
                        mapping_quality=mapping,
                        derivation_class=DerivationClass.REPORTED,
                    )
                )
                records.append(
                    NormalizationRecord(
                        record_id="authnorm:" + hashlib.sha256(
                            f"{observation.observation_id}|{canonical_metric}".encode()
                        ).hexdigest(),
                        observation_id=observation.observation_id,
                        provider_id=result.provider_id,
                        native_field=observation.native_field,
                        canonical_metric=canonical_metric,
                        mapping_quality=mapping,
                        derivation_class=DerivationClass.REPORTED,
                        rule_id=f"official-exact:{canonical_metric}",
                        rule_version="1.0",
                        source_observation_ids=(observation.observation_id,),
                        emitted_evidence_id=evidence_id,
                    )
                )
            else:
                records.append(
                    NormalizationRecord(
                        record_id="authnorm:" + hashlib.sha256(
                            f"{observation.observation_id}|native".encode()
                        ).hexdigest(),
                        observation_id=observation.observation_id,
                        provider_id=result.provider_id,
                        native_field=observation.native_field,
                        mapping_quality=SemanticMappingQuality.PROVIDER_DEFINED,
                        derivation_class=DerivationClass.REPORTED,
                        rule_id="official-document-metadata",
                        rule_version="1.0",
                        source_observation_ids=(observation.observation_id,),
                    )
                )
        events = self._events(document, metadata)
        return NormalizedEvidenceBatch(
            provider_id=result.provider_id,
            capability=result.capability,
            native_observations=result.observations,
            normalization_records=tuple(records),
            canonical_evidence=tuple(projections),
            normalized_events=events,
            authoritative_documents=(document,),
            gaps=result.failures,
        )

    @staticmethod
    def _document(
        first: ProviderNativeObservation,
        observations: tuple[ProviderNativeObservation, ...],
    ) -> AuthoritativeDocumentEvidence:
        metadata = first.metadata
        facts = tuple(
            StructuredEventFact(
                field_id=str(item.metadata["canonical_metric"]),
                kind=StructuredFactKind(str(item.metadata["fact_kind"])),
                value=item.value,
                unit=item.unit,
                currency=item.currency,
                locator=(
                    str(item.metadata["source_locator"])
                    if "source_locator" in item.metadata
                    else None
                ),
                extraction_method=str(item.metadata["extraction_method"]),
                extraction_version=str(item.metadata["extraction_version"]),
            )
            for item in observations
            if item.native_field.startswith("fact.")
        )
        return AuthoritativeDocumentEvidence(
            document_id=str(metadata["document_id"]),
            subject=first.subject,
            source=SourceAuthorityMetadata(
                source_id=str(metadata["source_id"]),
                provider_id=first.provider_id,
                display_name=str(metadata["source_display_name"]),
                kind=OfficialSourceKind(str(metadata["source_kind"])),
                authority=SourceAuthority(str(metadata["source_authority"])),
                validated_domain=str(metadata["validated_domain"]),
                registry_version=str(metadata["registry_version"]),
            ),
            document_kind=AuthoritativeDocumentKind(str(metadata["document_kind"])),
            title=str(metadata["title"]),
            source_url=str(metadata["source_url"]),
            final_url=str(metadata["final_url"]),
            mime_type=str(metadata["mime_type"]),
            content_length=_required_int(metadata, "content_length"),
            content_hash=str(metadata["content_hash"]),
            content_reference=str(metadata["content_reference"]),
            provider_document_id=_optional_str(metadata, "provider_document_id"),
            filing_reference=_optional_str(metadata, "filing_reference"),
            published_at=_optional_datetime(metadata, "published_at"),
            exchange_timestamp=_optional_datetime(metadata, "exchange_timestamp"),
            event_date=_optional_date(metadata, "event_date"),
            available_from=datetime.fromisoformat(str(metadata["available_from"])),
            acquired_at=datetime.fromisoformat(str(metadata["acquired_at"])),
            period=_optional_str(metadata, "period"),
            financial_year=_optional_str(metadata, "financial_year"),
            quarter=_optional_str(metadata, "quarter"),
            statement_basis=_optional_str(metadata, "statement_basis"),
            audited=_optional_bool(metadata, "audited"),
            unit=_optional_str(metadata, "unit"),
            currency=_optional_str(metadata, "currency"),
            facts=facts,
            parse_status=DocumentParseStatus(str(metadata["parse_status"])),
            parser_id=str(metadata["parser_id"]),
            parser_version=str(metadata["parser_version"]),
            point_in_time_quality=PointInTimeQuality.CONSERVATIVE,
            revision=_optional_int(metadata, "revision") or 0,
            supersedes_document_id=_optional_str(metadata, "supersedes_document_id"),
        )

    @staticmethod
    def _events(
        document: AuthoritativeDocumentEvidence,
        metadata: Mapping[str, JsonValue],
    ) -> tuple[NormalizedEvent, ...]:
        if "event_family" not in metadata or "event_type" not in metadata:
            return ()
        source_class = (
            EventSourceClass.COMPANY_RELEASE
            if document.source.kind is OfficialSourceKind.COMPANY_IR
            else EventSourceClass.EXCHANGE_FILING
        )
        return (
            NormalizedEvent(
                event_id=f"authevent:{document.document_id}",
                family=EventFamily(str(metadata["event_family"])),
                event_type=EventType(str(metadata["event_type"])),
                primary_entity=EventEntity(
                    entity_id=f"instrument:{document.subject}",
                    kind=EntityKind.COMPANY,
                    name=document.subject,
                    canonical_symbol=document.subject,
                    mapping_status=EntityMappingStatus.EXACT,
                ),
                source=EventSource(
                    source_id=document.source.source_id,
                    source_class=source_class,
                    publisher=document.source.display_name,
                    provider_id=document.source.provider_id,
                    source_reference=document.final_url,
                    document_id=document.document_id,
                    revision_marker=str(document.revision),
                ),
                publication_time=document.published_at or document.available_from,
                event_time=document.exchange_timestamp,
                acquisition_time=document.acquired_at,
                normalized_title=document.title,
                structured_facts=document.facts,
                content_reference=document.content_reference,
                relevance=EventRelevance.DIRECT,
                materiality=EventMateriality(str(metadata["event_materiality"])),
                novelty=(EventNovelty.CORRECTION if document.revision else EventNovelty.NEW),
                status=EventStatus.CONFIRMED,
                quality=DataQuality.GOOD,
                freshness=FreshnessState.UNKNOWN,
                underlying_event_key=_optional_str(metadata, "underlying_event_key"),
                revision=document.revision,
            ),
        )


def _optional_str(metadata: Mapping[str, JsonValue], key: str) -> str | None:
    value = metadata.get(key)
    return str(value) if value is not None else None


def _optional_datetime(metadata: Mapping[str, JsonValue], key: str) -> datetime | None:
    value = metadata.get(key)
    return datetime.fromisoformat(str(value)) if value is not None else None


def _optional_date(metadata: Mapping[str, JsonValue], key: str) -> date | None:
    value = metadata.get(key)
    return date.fromisoformat(str(value)) if value is not None else None


def _required_int(metadata: Mapping[str, JsonValue], key: str) -> int:
    value = metadata.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"authoritative metadata {key} must be an integer")
    return value


def _optional_int(metadata: Mapping[str, JsonValue], key: str) -> int | None:
    value = metadata.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"authoritative metadata {key} must be an integer")
    return value


def _optional_bool(metadata: Mapping[str, JsonValue], key: str) -> bool | None:
    value = metadata.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError(f"authoritative metadata {key} must be a boolean")
    return value
