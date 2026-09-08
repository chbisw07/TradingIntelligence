"""Read-only gateway over already accepted, immutable A2 evidence packs."""

from datetime import datetime
from typing import Literal, Self

from pydantic import model_validator

from tiaf.agents.budget import AgentUsage
from tiaf.agents.enums import AgentCapability
from tiaf.agents.evidence import AgentEvidencePack
from tiaf.context import EvidenceStatus
from tiaf.contracts import ContractModel, DataQuality, FreshnessState
from tiaf.contracts.common import TiafDateTime

from .contracts import (
    EvidenceGatewayContext,
    EvidenceGatewayRequest,
    EvidenceGatewayResult,
    GatewayIdentity,
)
from .enums import EvidenceGatewayStatus, GatewayCacheStatus


class A2EvidenceEntry(ContractModel):
    """One accepted A2 pack plus its externally owned validity boundary."""

    schema_version: Literal["1.0"] = "1.0"
    evidence_pack: AgentEvidencePack
    valid_until: TiafDateTime

    @model_validator(mode="after")
    def validate_validity(self) -> Self:
        if self.valid_until <= self.evidence_pack.created_at:
            raise ValueError("A2 evidence validity must follow pack creation")
        return self


class A2EvidenceGateway:
    """Expose supplied frozen A2 evidence; never fetch or recompute it."""

    def __init__(
        self,
        entries: tuple[A2EvidenceEntry, ...],
        *,
        gateway_id: str = "tiaf.a2-evidence",
        gateway_version: str = "1.0",
    ) -> None:
        self._identity = GatewayIdentity(
            gateway_id=gateway_id,
            gateway_version=gateway_version,
        )
        self._entries: dict[tuple[str, str], A2EvidenceEntry] = {}
        for entry in entries:
            pack = entry.evidence_pack
            key = (pack.subject, pack.evidence_fingerprint)
            if key in self._entries:
                raise ValueError("duplicate A2 subject/fingerprint entry")
            self._entries[key] = entry

    def identity(self) -> GatewayIdentity:
        return self._identity

    def capabilities(self) -> tuple[AgentCapability, ...]:
        return (AgentCapability.READ_A2_EVIDENCE,)

    def can_handle(self, request: EvidenceGatewayRequest) -> bool:
        return request.capability is AgentCapability.READ_A2_EVIDENCE

    def fetch(
        self,
        request: EvidenceGatewayRequest,
        context: EvidenceGatewayContext,
    ) -> EvidenceGatewayResult:
        del context
        entry = self._resolve(request)
        if entry is None:
            return EvidenceGatewayResult(
                request_id=request.request_id,
                capability=request.capability,
                subject=request.subject,
                status=EvidenceGatewayStatus.MISSING,
                gateway_identity=self._identity,
                produced_at=request.as_of,
                cache_status=GatewayCacheStatus.MISS,
                warnings=("Requested A2 evidence is not present",),
            )
        pack = entry.evidence_pack
        if request.deterministic_baseline_reference is not None:
            if pack.deterministic_assessment_id != request.deterministic_baseline_reference:
                return self._missing(request, "A2 deterministic assessment ID does not match")
        if not any(item.evidence_type is request.evidence_type for item in pack.references):
            return self._missing(request, "Requested A2 evidence family is not present")
        acquired_at = max(
            (item.acquired_at for item in pack.references if item.acquired_at is not None),
            default=pack.created_at,
        )
        status = self._status(
            pack,
            request.as_of,
            entry.valid_until,
            request.required_freshness,
        )
        freshness = (
            FreshnessState.STALE
            if status is EvidenceGatewayStatus.STALE
            else pack.overall_freshness
        )
        source_timestamps = tuple(
            sorted(
                {
                    item.observed_at
                    for item in pack.references
                    if item.observed_at is not None
                }
            )
        )
        return EvidenceGatewayResult(
            request_id=request.request_id,
            capability=request.capability,
            subject=request.subject,
            status=status,
            gateway_identity=self._identity,
            evidence_pack=pack,
            evidence_fingerprint=pack.evidence_fingerprint,
            source_timestamps=source_timestamps,
            acquired_at=acquired_at,
            produced_at=max(request.as_of, acquired_at),
            valid_until=entry.valid_until,
            freshness=freshness,
            quality=pack.overall_quality,
            cache_status=GatewayCacheStatus.MISS,
            usage=AgentUsage(tool_calls=1),
        )

    def _resolve(self, request: EvidenceGatewayRequest) -> A2EvidenceEntry | None:
        if request.evidence_fingerprint is not None:
            return self._entries.get((request.subject, request.evidence_fingerprint))
        matches = tuple(
            entry
            for (subject, _), entry in self._entries.items()
            if subject == request.subject
        )
        return matches[0] if len(matches) == 1 else None

    def _missing(self, request: EvidenceGatewayRequest, warning: str) -> EvidenceGatewayResult:
        return EvidenceGatewayResult(
            request_id=request.request_id,
            capability=request.capability,
            subject=request.subject,
            status=EvidenceGatewayStatus.MISSING,
            gateway_identity=self._identity,
            produced_at=request.as_of,
            cache_status=GatewayCacheStatus.MISS,
            warnings=(warning,),
            usage=AgentUsage(tool_calls=1),
        )

    @staticmethod
    def _status(
        pack: AgentEvidencePack,
        as_of: datetime,
        valid_until: datetime,
        required_freshness: FreshnessState,
    ) -> EvidenceGatewayStatus:
        freshness_order = {
            FreshnessState.FRESH: 0,
            FreshnessState.AGING: 1,
            FreshnessState.STALE: 2,
            FreshnessState.UNKNOWN: 3,
        }
        if (
            as_of >= valid_until
            or pack.overall_freshness is FreshnessState.STALE
            or freshness_order[pack.overall_freshness]
            > freshness_order[required_freshness]
            or any(item.availability is EvidenceStatus.STALE for item in pack.references)
        ):
            return EvidenceGatewayStatus.STALE
        if (
            pack.overall_quality in {DataQuality.PARTIAL, DataQuality.DEGRADED}
            or any(item.availability is EvidenceStatus.PARTIAL for item in pack.references)
        ):
            return EvidenceGatewayStatus.PARTIAL
        return EvidenceGatewayStatus.SUCCESS
