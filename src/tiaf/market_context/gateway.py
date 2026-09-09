"""Controlled, reusable READ_SECTOR_CONTEXT and READ_MACRO_CONTEXT gateways."""

import hashlib
import json
from datetime import datetime

from tiaf.agents import (
    AgentCapability,
    AgentEvidencePack,
    AgentEvidenceReference,
    AgentFailure,
    AgentUsage,
    EvidenceFact,
    EvidenceFactKind,
    EvidenceFactParameter,
    EvidenceImportance,
    MissingEvidenceRequest,
)
from tiaf.agents.gateways import (
    EvidenceGatewayContext,
    EvidenceGatewayRequest,
    EvidenceGatewayResult,
    EvidenceGatewayStatus,
    GatewayCacheStatus,
    GatewayIdentity,
)
from tiaf.context import EvidenceStatus
from tiaf.contracts import DataQuality, EvidenceSource, EvidenceType, FreshnessState

from .enums import MacroEvidenceFamily, SectorEvidenceFamily
from .models import (
    ContextObservation,
    MacroContextRequest,
    MacroContextSnapshot,
    SectorContextRequest,
    SectorContextSnapshot,
)
from .provider import MacroContextProvider, MarketContextProviderError, SectorContextProvider

SECTOR_GATEWAY_ID = "tiaf.sector-context"
MACRO_GATEWAY_ID = "tiaf.macro-context"
GATEWAY_VERSION = "1.0"


def sector_gateway_attributes(
    *, sector_id: str, benchmark_symbol: str, families: tuple[SectorEvidenceFamily, ...]
) -> tuple[str, ...]:
    return (
        f"sector:{sector_id}",
        f"benchmark:{benchmark_symbol.strip().upper()}",
        *(f"family:{item.value}" for item in families),
    )


def macro_gateway_attributes(
    *, market: str, families: tuple[MacroEvidenceFamily, ...]
) -> tuple[str, ...]:
    return (f"market:{market.strip().upper()}", *(f"family:{item.value}" for item in families))


def _checksum(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


def _fact(item: ContextObservation) -> EvidenceFact:
    return EvidenceFact(
        fact_id=item.observation_id,
        kind=EvidenceFactKind.FEATURE,
        metric_id=item.metric_id,
        value=item.value,
        unit=item.unit,
        parameters=(
            EvidenceFactParameter(name="context_kind", value=item.kind.value),
            *(
                EvidenceFactParameter(name="driver_id", value=item.driver_id)
                for _ in (0,)
                if item.driver_id is not None
            ),
        ),
        interval=item.interval,
        as_of=item.observed_at,
        quality=item.quality,
        freshness=item.freshness,
        source_evidence=(item.source_reference,),
    )


def _observation_reference(
    item: ContextObservation, *, subject: str, evidence_type: EvidenceType, prefix: str
) -> AgentEvidenceReference:
    return AgentEvidenceReference(
        evidence_id=f"{prefix}:{item.observation_id}",
        evidence_type=evidence_type,
        subject=subject,
        producer_id=item.source_id,
        producer_version=item.source_version,
        source=EvidenceSource.THIRD_PARTY,
        availability=EvidenceStatus.STALE
        if item.freshness is FreshnessState.STALE
        else EvidenceStatus.AVAILABLE,
        quality=item.quality,
        freshness=item.freshness,
        observed_at=item.observed_at,
        acquired_at=item.available_at,
        checksum=_checksum(item.model_dump(mode="json")),
        source_reference=item.source_reference,
        facts=(_fact(item),),
        metadata={
            "family": item.family.value,
            "kind": item.kind.value,
            "driver_id": item.driver_id,
        },
    )


class SectorContextEvidenceGateway:
    """Read explicit sector context; cache source snapshots by sector, not stock."""

    def __init__(self, provider: SectorContextProvider) -> None:
        if not isinstance(provider, SectorContextProvider):
            raise TypeError("sector provider does not satisfy protocol")
        provider_id, provider_version = provider.identity()
        self._provider = provider
        self._identity = GatewayIdentity(
            gateway_id=f"{SECTOR_GATEWAY_ID}:{provider_id}",
            gateway_version=f"{GATEWAY_VERSION}+{provider_version}",
        )
        self._shared: dict[tuple[object, ...], SectorContextSnapshot] = {}

    def identity(self) -> GatewayIdentity:
        return self._identity

    def capabilities(self) -> tuple[AgentCapability, ...]:
        return (AgentCapability.READ_SECTOR_CONTEXT,)

    def can_handle(self, request: EvidenceGatewayRequest) -> bool:
        return (
            request.capability is AgentCapability.READ_SECTOR_CONTEXT
            and request.evidence_type is EvidenceType.SECTOR
        )

    def fetch(
        self, request: EvidenceGatewayRequest, context: EvidenceGatewayContext
    ) -> EvidenceGatewayResult:
        if request.deterministic_baseline_reference is None:
            return self._failure(request, context.invoked_at, "A2 baseline reference is required")
        try:
            sector_id, benchmark, families = _parse_sector_attributes(request.requested_attributes)
            mapping = self._provider.resolve_sector(request.subject, request.as_of)
            if mapping is None:
                return self._missing(
                    request, context.invoked_at, "Explicit sector mapping is unavailable"
                )
            if mapping.sector_id != sector_id or mapping.benchmark_symbol != benchmark:
                return self._failure(
                    request,
                    context.invoked_at,
                    "Requested sector identity does not match explicit mapping",
                )
            key = (
                sector_id,
                benchmark,
                request.as_of,
                request.horizon.model_dump_json(),
                families,
                request.required_freshness,
            )
            snapshot = self._shared.get(key)
            if snapshot is None or context.invoked_at >= snapshot.valid_until:
                snapshot = self._provider.fetch(
                    SectorContextRequest(
                        request_id=request.request_id,
                        subject=request.subject,
                        sector_id=sector_id,
                        benchmark_symbol=benchmark,
                        as_of=request.as_of,
                        horizon=request.horizon,
                        families=families,
                        required_freshness=request.required_freshness,
                    )
                )
                self._shared[key] = snapshot
            pack = sector_evidence_pack(
                request, snapshot, created_at=max(context.invoked_at, snapshot.acquired_at)
            )
            return _result(request, context.invoked_at, snapshot, pack, self._identity)
        except (MarketContextProviderError, ValueError) as exc:
            return self._failure(request, context.invoked_at, str(exc))

    def _missing(
        self, request: EvidenceGatewayRequest, produced_at: datetime, detail: str
    ) -> EvidenceGatewayResult:
        return EvidenceGatewayResult(
            request_id=request.request_id,
            capability=request.capability,
            subject=request.subject,
            status=EvidenceGatewayStatus.MISSING,
            gateway_identity=self._identity,
            produced_at=produced_at,
            cache_status=GatewayCacheStatus.MISS,
            warnings=(detail,),
            usage=AgentUsage(tool_calls=1),
        )

    def _failure(
        self, request: EvidenceGatewayRequest, produced_at: datetime, detail: str
    ) -> EvidenceGatewayResult:
        return EvidenceGatewayResult(
            request_id=request.request_id,
            capability=request.capability,
            subject=request.subject,
            status=EvidenceGatewayStatus.INVALID_REQUEST,
            gateway_identity=self._identity,
            produced_at=produced_at,
            cache_status=GatewayCacheStatus.MISS,
            failure=AgentFailure(error_type="SectorContextGatewayRequestError", detail=detail),
            usage=AgentUsage(tool_calls=1),
        )


class MacroContextEvidenceGateway:
    """Read bounded macro context; cache one market snapshot across subjects."""

    def __init__(self, provider: MacroContextProvider) -> None:
        if not isinstance(provider, MacroContextProvider):
            raise TypeError("macro provider does not satisfy protocol")
        provider_id, provider_version = provider.identity()
        self._provider = provider
        self._identity = GatewayIdentity(
            gateway_id=f"{MACRO_GATEWAY_ID}:{provider_id}",
            gateway_version=f"{GATEWAY_VERSION}+{provider_version}",
        )
        self._shared: dict[tuple[object, ...], MacroContextSnapshot] = {}

    def identity(self) -> GatewayIdentity:
        return self._identity

    def capabilities(self) -> tuple[AgentCapability, ...]:
        return (AgentCapability.READ_MACRO_CONTEXT,)

    def can_handle(self, request: EvidenceGatewayRequest) -> bool:
        return (
            request.capability is AgentCapability.READ_MACRO_CONTEXT
            and request.evidence_type is EvidenceType.MACRO
        )

    def fetch(
        self, request: EvidenceGatewayRequest, context: EvidenceGatewayContext
    ) -> EvidenceGatewayResult:
        if request.deterministic_baseline_reference is None:
            return self._failure(request, context.invoked_at, "A2 baseline reference is required")
        try:
            market, families = _parse_macro_attributes(request.requested_attributes)
            key = (
                market,
                request.as_of,
                request.horizon.model_dump_json(),
                families,
                request.required_freshness,
            )
            snapshot = self._shared.get(key)
            if snapshot is None or context.invoked_at >= snapshot.valid_until:
                snapshot = self._provider.fetch(
                    MacroContextRequest(
                        request_id=request.request_id,
                        subject=request.subject,
                        market=market,
                        as_of=request.as_of,
                        horizon=request.horizon,
                        families=families,
                        required_freshness=request.required_freshness,
                    )
                )
                self._shared[key] = snapshot
            if not snapshot.observations:
                return self._missing(
                    request,
                    context.invoked_at,
                    "No point-in-time macro observations satisfy the request",
                )
            pack = macro_evidence_pack(
                request, snapshot, created_at=max(context.invoked_at, snapshot.acquired_at)
            )
            return _result(request, context.invoked_at, snapshot, pack, self._identity)
        except (MarketContextProviderError, ValueError) as exc:
            return self._failure(request, context.invoked_at, str(exc))

    def _failure(
        self, request: EvidenceGatewayRequest, produced_at: datetime, detail: str
    ) -> EvidenceGatewayResult:
        return EvidenceGatewayResult(
            request_id=request.request_id,
            capability=request.capability,
            subject=request.subject,
            status=EvidenceGatewayStatus.INVALID_REQUEST,
            gateway_identity=self._identity,
            produced_at=produced_at,
            cache_status=GatewayCacheStatus.MISS,
            failure=AgentFailure(error_type="MacroContextGatewayRequestError", detail=detail),
            usage=AgentUsage(tool_calls=1),
        )

    def _missing(
        self,
        request: EvidenceGatewayRequest,
        produced_at: datetime,
        detail: str,
    ) -> EvidenceGatewayResult:
        return EvidenceGatewayResult(
            request_id=request.request_id,
            capability=request.capability,
            subject=request.subject,
            status=EvidenceGatewayStatus.MISSING,
            gateway_identity=self._identity,
            produced_at=produced_at,
            cache_status=GatewayCacheStatus.MISS,
            warnings=(detail,),
            usage=AgentUsage(tool_calls=1),
        )


def _result(
    request: EvidenceGatewayRequest,
    produced_at: datetime,
    snapshot: SectorContextSnapshot | MacroContextSnapshot,
    pack: AgentEvidencePack,
    identity: GatewayIdentity,
) -> EvidenceGatewayResult:
    if not snapshot.observations:
        return EvidenceGatewayResult(
            request_id=request.request_id,
            capability=request.capability,
            subject=request.subject,
            status=EvidenceGatewayStatus.MISSING,
            gateway_identity=identity,
            produced_at=produced_at,
            warnings=("No point-in-time context observations satisfy the request",),
            usage=AgentUsage(tool_calls=1),
        )
    status = (
        EvidenceGatewayStatus.STALE
        if snapshot.freshness is FreshnessState.STALE
        else EvidenceGatewayStatus.PARTIAL
        if snapshot.missing_families or snapshot.quality is not DataQuality.GOOD
        else EvidenceGatewayStatus.SUCCESS
    )
    return EvidenceGatewayResult(
        request_id=request.request_id,
        capability=request.capability,
        subject=request.subject,
        status=status,
        gateway_identity=identity,
        evidence_pack=pack,
        evidence_fingerprint=pack.evidence_fingerprint,
        source_timestamps=tuple(sorted({item.observed_at for item in snapshot.observations})),
        acquired_at=snapshot.acquired_at,
        produced_at=max(produced_at, snapshot.acquired_at),
        valid_until=snapshot.valid_until,
        freshness=snapshot.freshness,
        quality=snapshot.quality,
        cache_status=GatewayCacheStatus.MISS,
        usage=AgentUsage(tool_calls=1),
        warnings=tuple(
            f"Missing context family: {item.value}" for item in snapshot.missing_families
        ),
    )


def sector_evidence_pack(
    request: EvidenceGatewayRequest, snapshot: SectorContextSnapshot, *, created_at: datetime
) -> AgentEvidencePack:
    if request.deterministic_baseline_reference is None:
        raise ValueError("sector context requires A2 baseline identity")
    mapping_payload = snapshot.identity.model_dump(mode="json")
    mapping_reference = AgentEvidenceReference(
        evidence_id=f"sector-mapping:{snapshot.identity.sector_id}:{snapshot.identity.mapping_version}",
        evidence_type=EvidenceType.SECTOR,
        subject=request.subject,
        producer_id=snapshot.identity.mapping_source,
        producer_version=snapshot.identity.mapping_version,
        source=EvidenceSource.INTERNAL,
        availability=EvidenceStatus.AVAILABLE,
        quality=DataQuality.GOOD
        if snapshot.identity.quality.value in {"VERIFIED", "DECLARED"}
        else DataQuality.PARTIAL,
        freshness=FreshnessState.FRESH,
        observed_at=snapshot.acquired_at,
        acquired_at=snapshot.acquired_at,
        checksum=_checksum(mapping_payload),
        source_reference=snapshot.identity.mapping_source,
        facts=(
            EvidenceFact(
                fact_id=f"sector-mapping:{snapshot.identity.sector_id}:id",
                kind=EvidenceFactKind.FEATURE,
                metric_id="sector.mapping.sector_id",
                value=snapshot.identity.sector_id,
                as_of=snapshot.acquired_at,
                quality=DataQuality.GOOD,
                freshness=FreshnessState.FRESH,
                source_evidence=(snapshot.identity.mapping_source,),
            ),
            EvidenceFact(
                fact_id=f"sector-mapping:{snapshot.identity.sector_id}:benchmark",
                kind=EvidenceFactKind.FEATURE,
                metric_id="sector.mapping.benchmark_symbol",
                value=snapshot.identity.benchmark_symbol,
                as_of=snapshot.acquired_at,
                quality=DataQuality.GOOD,
                freshness=FreshnessState.FRESH,
                source_evidence=(snapshot.identity.mapping_source,),
            ),
        ),
        metadata={
            "sector_name": snapshot.identity.sector_name,
            "mapping_quality": snapshot.identity.quality.value,
            "mapping_version": snapshot.identity.mapping_version,
        },
    )
    references = (
        mapping_reference,
        *(
            _observation_reference(
                item,
                subject=request.subject,
                evidence_type=EvidenceType.SECTOR,
                prefix="sector-context",
            )
            for item in snapshot.observations
        ),
    )
    fingerprint = _checksum({"source_snapshot": snapshot.fingerprint, "subject": request.subject})
    return _pack(
        request,
        fingerprint,
        references,
        snapshot.missing_families,
        snapshot.quality,
        snapshot.freshness,
        created_at,
    )


def macro_evidence_pack(
    request: EvidenceGatewayRequest, snapshot: MacroContextSnapshot, *, created_at: datetime
) -> AgentEvidencePack:
    if request.deterministic_baseline_reference is None:
        raise ValueError("macro context requires A2 baseline identity")
    references: list[AgentEvidenceReference] = []
    for observation in snapshot.observations:
        reference = _observation_reference(
            observation,
            subject=request.subject,
            evidence_type=EvidenceType.MACRO,
            prefix="macro-context",
        )
        references.append(
            reference.model_copy(
                update={"metadata": {**reference.metadata, "market": snapshot.market}}
            )
        )
    for item in snapshot.sensitivities:
        if item.subject != request.subject:
            continue
        payload = item.model_dump(mode="json")
        references.append(
            AgentEvidenceReference(
                evidence_id=f"macro-sensitivity:{item.sensitivity_id}",
                evidence_type=EvidenceType.MACRO,
                subject=request.subject,
                producer_id=item.mapping_source,
                producer_version=item.mapping_version,
                source=EvidenceSource.INTERNAL,
                availability=EvidenceStatus.AVAILABLE,
                quality=DataQuality.GOOD
                if item.quality.value in {"VERIFIED", "DECLARED"}
                else DataQuality.PARTIAL,
                freshness=FreshnessState.FRESH,
                observed_at=snapshot.acquired_at,
                acquired_at=snapshot.acquired_at,
                checksum=_checksum(payload),
                source_reference=item.mapping_source,
                facts=(
                    EvidenceFact(
                        fact_id=item.sensitivity_id,
                        kind=EvidenceFactKind.FEATURE,
                        metric_id=f"macro.sensitivity.{item.family.value.lower()}",
                        value=item.direction.value,
                        parameters=(EvidenceFactParameter(name="driver_id", value=item.driver_id),),
                        as_of=snapshot.acquired_at,
                        quality=DataQuality.GOOD,
                        freshness=FreshnessState.FRESH,
                        source_evidence=(item.mapping_source,),
                    ),
                ),
                metadata={
                    "family": item.family.value,
                    "driver_id": item.driver_id,
                    "mapping_quality": item.quality.value,
                    "mapping_version": item.mapping_version,
                },
            )
        )
    selected_sensitivity_ids = tuple(
        item.sensitivity_id for item in snapshot.sensitivities if item.subject == request.subject
    )
    fingerprint = _checksum(
        {
            "source_snapshot": snapshot.fingerprint,
            "subject": request.subject,
            "sensitivity_ids": selected_sensitivity_ids,
        }
    )
    return _pack(
        request,
        fingerprint,
        tuple(references),
        snapshot.missing_families,
        snapshot.quality,
        snapshot.freshness,
        created_at,
    )


def _pack(
    request: EvidenceGatewayRequest,
    fingerprint: str,
    references: tuple[AgentEvidenceReference, ...],
    missing_families: tuple[SectorEvidenceFamily | MacroEvidenceFamily, ...],
    quality: DataQuality,
    freshness: FreshnessState,
    created_at: datetime,
) -> AgentEvidencePack:
    missing = tuple(
        MissingEvidenceRequest(
            missing_request_id=f"{request.request_id}:missing:{item.value}",
            evidence_type=request.evidence_type,
            capability=request.capability,
            subject=request.subject,
            reason=f"Requested context family {item.value} is unavailable",
            importance=EvidenceImportance.MATERIAL,
            required_freshness=request.required_freshness,
            requested_at=request.as_of,
        )
        for item in missing_families
    )
    requested_count = max(
        1, len(tuple(item for item in request.requested_attributes if item.startswith("family:")))
    )
    coverage = max(0.0, 1.0 - len(missing) / requested_count)
    return AgentEvidencePack(
        pack_id=f"context:{fingerprint[:16]}:agent-pack",
        request_id=request.request_id,
        subject=request.subject,
        evidence_fingerprint=fingerprint,
        references=references,
        analysis_context_ids=request.context_references,
        deterministic_assessment_id=request.deterministic_baseline_reference or "unavailable",
        overall_quality=quality,
        overall_freshness=freshness,
        evidence_coverage=coverage,
        missing_evidence=missing,
        created_at=created_at,
    )


def _parse_sector_attributes(
    attributes: tuple[str, ...],
) -> tuple[str, str, tuple[SectorEvidenceFamily, ...]]:
    sector = tuple(
        item.removeprefix("sector:") for item in attributes if item.startswith("sector:")
    )
    benchmark = tuple(
        item.removeprefix("benchmark:").upper()
        for item in attributes
        if item.startswith("benchmark:")
    )
    families = tuple(
        SectorEvidenceFamily(item.removeprefix("family:"))
        for item in attributes
        if item.startswith("family:")
    )
    if (
        len(sector) != 1
        or len(benchmark) != 1
        or not families
        or len(families) != len(set(families))
    ):
        raise ValueError("sector attributes require one sector, one benchmark, and unique families")
    return sector[0], benchmark[0], families


def _parse_macro_attributes(
    attributes: tuple[str, ...],
) -> tuple[str, tuple[MacroEvidenceFamily, ...]]:
    market = tuple(
        item.removeprefix("market:").upper() for item in attributes if item.startswith("market:")
    )
    families = tuple(
        MacroEvidenceFamily(item.removeprefix("family:"))
        for item in attributes
        if item.startswith("family:")
    )
    if len(market) != 1 or not families or len(families) != len(set(families)):
        raise ValueError("macro attributes require one market and unique families")
    return market[0], families
