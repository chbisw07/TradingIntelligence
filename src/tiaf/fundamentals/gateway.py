"""Controlled READ_FUNDAMENTALS gateway and lossless Agent evidence projection."""

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

from .enums import FundamentalFamily, ReportingPeriodKind
from .models import FundamentalDataset, FundamentalFact, FundamentalRequest, PeriodRequirement
from .provider import FundamentalProvider, FundamentalProviderError

GATEWAY_ID = "tiaf.fundamentals"
GATEWAY_VERSION = "1.0"


def fundamental_gateway_attributes(request: FundamentalRequest) -> tuple[str, ...]:
    """Encode the typed request into the existing bounded gateway vocabulary."""
    return (
        *(f"family:{item.value}" for item in request.families),
        *(f"period:{item.kind.value}:{item.count}" for item in request.periods),
    )


class FundamentalEvidenceGateway:
    """Read normalized facts through a provider; never expose transport authority."""

    def __init__(self, provider: FundamentalProvider) -> None:
        if not isinstance(provider, FundamentalProvider):
            raise TypeError("fundamental provider does not satisfy protocol")
        provider_id, provider_version = provider.identity()
        self._provider = provider
        self._identity = GatewayIdentity(
            gateway_id=f"{GATEWAY_ID}:{provider_id}",
            gateway_version=f"{GATEWAY_VERSION}+{provider_version}",
        )

    def identity(self) -> GatewayIdentity:
        return self._identity

    def capabilities(self) -> tuple[AgentCapability, ...]:
        return (AgentCapability.READ_FUNDAMENTALS,)

    def can_handle(self, request: EvidenceGatewayRequest) -> bool:
        return (
            request.capability is AgentCapability.READ_FUNDAMENTALS
            and request.evidence_type is EvidenceType.FUNDAMENTAL
        )

    def fetch(
        self,
        request: EvidenceGatewayRequest,
        context: EvidenceGatewayContext,
    ) -> EvidenceGatewayResult:
        if request.deterministic_baseline_reference is None:
            return self._failure(request, context.invoked_at, "A2 baseline reference is required")
        company = self._provider.resolve_company(request.subject)
        if company is None:
            return EvidenceGatewayResult(
                request_id=request.request_id,
                capability=request.capability,
                subject=request.subject,
                status=EvidenceGatewayStatus.MISSING,
                gateway_identity=self._identity,
                produced_at=context.invoked_at,
                cache_status=GatewayCacheStatus.MISS,
                warnings=("Canonical company identity is unavailable",),
                usage=AgentUsage(tool_calls=1),
            )
        try:
            families, periods = _parse_attributes(request.requested_attributes)
            dataset = self._provider.fetch(
                FundamentalRequest(
                    request_id=request.request_id,
                    company=company,
                    as_of=request.as_of,
                    horizon=request.horizon,
                    families=families,
                    periods=periods,
                    required_freshness=request.required_freshness,
                )
            )
        except (FundamentalProviderError, ValueError) as exc:
            return self._failure(request, context.invoked_at, str(exc))
        if not dataset.facts:
            return EvidenceGatewayResult(
                request_id=request.request_id,
                capability=request.capability,
                subject=request.subject,
                status=EvidenceGatewayStatus.MISSING,
                gateway_identity=self._identity,
                produced_at=context.invoked_at,
                cache_status=GatewayCacheStatus.MISS,
                warnings=("No point-in-time fundamental facts satisfy the request",),
                usage=AgentUsage(tool_calls=1),
            )
        pack = fundamental_evidence_pack(
            request,
            dataset,
            created_at=max(context.invoked_at, dataset.acquired_at),
        )
        status = _gateway_status(dataset)
        warnings = tuple(
            item
            for item in (
                dataset.point_in_time_limitation,
                (
                    "Missing families: "
                    + ", ".join(item.value for item in dataset.missing_families)
                    if dataset.missing_families
                    else None
                ),
                (
                    "Underfilled period history: "
                    + ", ".join(
                        f"{item.kind.value}<{item.count}"
                        for item in dataset.missing_periods
                    )
                    if dataset.missing_periods
                    else None
                ),
            )
            if item is not None
        )
        return EvidenceGatewayResult(
            request_id=request.request_id,
            capability=request.capability,
            subject=request.subject,
            status=status,
            gateway_identity=self._identity,
            evidence_pack=pack,
            evidence_fingerprint=dataset.fingerprint,
            source_timestamps=tuple(sorted({item.published_at for item in dataset.facts})),
            acquired_at=dataset.acquired_at,
            produced_at=max(context.invoked_at, dataset.acquired_at),
            valid_until=dataset.valid_until,
            freshness=dataset.freshness,
            quality=dataset.quality,
            cache_status=GatewayCacheStatus.MISS,
            usage=AgentUsage(tool_calls=1),
            warnings=warnings,
        )

    def _failure(
        self,
        request: EvidenceGatewayRequest,
        produced_at: datetime,
        detail: str,
    ) -> EvidenceGatewayResult:
        return EvidenceGatewayResult(
            request_id=request.request_id,
            capability=request.capability,
            subject=request.subject,
            status=EvidenceGatewayStatus.INVALID_REQUEST,
            gateway_identity=self._identity,
            produced_at=produced_at,
            cache_status=GatewayCacheStatus.MISS,
            usage=AgentUsage(tool_calls=1),
            failure=AgentFailure(error_type="FundamentalGatewayRequestError", detail=detail),
        )


def fundamental_evidence_pack(
    request: EvidenceGatewayRequest,
    dataset: FundamentalDataset,
    *,
    created_at: datetime,
) -> AgentEvidencePack:
    """Project rich normalized facts without recalculation into Agent evidence."""
    if request.deterministic_baseline_reference is None:
        raise ValueError("fundamental evidence pack requires A2 baseline identity")
    references = tuple(_fact_reference(item, dataset) for item in dataset.facts)
    requested_families, requested_periods = _parse_attributes(
        request.requested_attributes
    )
    covered = {item.family for item in dataset.facts}
    family_coverage = len(covered & set(requested_families)) / len(requested_families)
    period_coverage = 1.0 - len(dataset.missing_periods) / len(requested_periods)
    coverage = (family_coverage + period_coverage) / 2.0
    missing_families = tuple(
        MissingEvidenceRequest(
            missing_request_id=f"{request.request_id}:missing:{family.value}",
            evidence_type=EvidenceType.FUNDAMENTAL,
            capability=AgentCapability.READ_FUNDAMENTALS,
            subject=request.subject,
            reason=f"Requested fundamental family {family.value} is unavailable",
            importance=EvidenceImportance.MATERIAL,
            required_freshness=request.required_freshness,
            requested_at=request.as_of,
        )
        for family in dataset.missing_families
    )
    missing_periods = tuple(
        MissingEvidenceRequest(
            missing_request_id=f"{request.request_id}:missing:period:{item.kind.value}",
            evidence_type=EvidenceType.FUNDAMENTAL,
            capability=AgentCapability.READ_FUNDAMENTALS,
            subject=request.subject,
            reason=(
                f"Requested {item.count} {item.kind.value} reporting periods are unavailable"
            ),
            importance=EvidenceImportance.MATERIAL,
            required_freshness=request.required_freshness,
            requested_at=request.as_of,
        )
        for item in dataset.missing_periods
    )
    return AgentEvidencePack(
        pack_id=f"{dataset.dataset_id}:agent-pack",
        request_id=request.request_id,
        subject=request.subject,
        evidence_fingerprint=dataset.fingerprint,
        references=references,
        analysis_context_ids=request.context_references,
        deterministic_assessment_id=request.deterministic_baseline_reference,
        overall_quality=dataset.quality,
        overall_freshness=dataset.freshness,
        evidence_coverage=round(coverage, 4),
        missing_evidence=(*missing_families, *missing_periods),
        created_at=created_at,
        metadata={
            "provider_id": dataset.provider_id,
            "provider_version": dataset.provider_version,
            "sector": dataset.company.sector,
            "industry": dataset.company.industry,
            "point_in_time_limitation": dataset.point_in_time_limitation,
        },
    )


def _fact_reference(
    fact: FundamentalFact,
    dataset: FundamentalDataset,
) -> AgentEvidenceReference:
    canonical = json.dumps(
        fact.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    )
    evidence_fact = EvidenceFact(
        fact_id=fact.fact_id,
        kind=EvidenceFactKind.FUNDAMENTAL,
        metric_id=fact.metric.value,
        value=fact.value,
        unit=fact.unit.value,
        parameters=(
            EvidenceFactParameter(name="period_id", value=fact.period.period_id),
            EvidenceFactParameter(name="period_kind", value=fact.period.kind.value),
            EvidenceFactParameter(name="period_start", value=fact.period.start_date.isoformat()),
            EvidenceFactParameter(name="period_end", value=fact.period.end_date.isoformat()),
            EvidenceFactParameter(name="basis", value=fact.basis.value),
            EvidenceFactParameter(name="scale", value=fact.scale.value),
            EvidenceFactParameter(name="currency", value=fact.currency),
            EvidenceFactParameter(name="published_at", value=fact.published_at.isoformat()),
            EvidenceFactParameter(name="revision", value=fact.revision),
            EvidenceFactParameter(name="source_quality", value=fact.source_quality.value),
        ),
        interval=fact.period.period_id,
        as_of=fact.published_at,
        quality=fact.quality,
        freshness=fact.freshness,
        source_evidence=(
            fact.source_reference,
            *((fact.derivation.source_fact_ids) if fact.derivation is not None else ()),
        ),
    )
    availability = (
        EvidenceStatus.STALE
        if fact.freshness is FreshnessState.STALE
        else EvidenceStatus.PARTIAL
        if fact.quality is not DataQuality.GOOD
        else EvidenceStatus.AVAILABLE
    )
    return AgentEvidenceReference(
        evidence_id=fact.fact_id,
        evidence_type=EvidenceType.FUNDAMENTAL,
        subject=fact.company.symbol,
        producer_id=dataset.provider_id,
        producer_version=dataset.provider_version,
        source=(
            EvidenceSource.INTERNAL
            if dataset.provider_id.startswith("tiaf.")
            else EvidenceSource.THIRD_PARTY
        ),
        availability=availability,
        quality=fact.quality,
        freshness=fact.freshness,
        observed_at=fact.published_at,
        acquired_at=fact.acquired_at,
        checksum=hashlib.sha256(canonical.encode()).hexdigest(),
        source_reference=fact.source_reference,
        facts=(evidence_fact,),
        metadata={
            "source_quality": fact.source_quality.value,
            "revision_id": fact.revision_id,
            "replaces_fact_id": fact.replaces_fact_id,
            "formula_id": fact.derivation.formula_id if fact.derivation else None,
            "formula_version": fact.derivation.formula_version if fact.derivation else None,
        },
    )


def _parse_attributes(
    attributes: tuple[str, ...],
) -> tuple[tuple[FundamentalFamily, ...], tuple[PeriodRequirement, ...]]:
    families: list[FundamentalFamily] = []
    periods: list[PeriodRequirement] = []
    for attribute in attributes:
        parts = attribute.split(":")
        if len(parts) == 2 and parts[0] == "family":
            families.append(FundamentalFamily(parts[1]))
        elif len(parts) == 3 and parts[0] == "period":
            periods.append(
                PeriodRequirement(kind=ReportingPeriodKind(parts[1]), count=int(parts[2]))
            )
        else:
            raise ValueError(f"unsupported fundamental gateway attribute: {attribute}")
    if not families or not periods:
        raise ValueError("fundamental gateway requires typed family and period attributes")
    if len(families) != len(set(families)) or len(periods) != len(
        {item.kind for item in periods}
    ):
        raise ValueError("fundamental gateway attributes must be unique")
    return tuple(families), tuple(periods)


def _gateway_status(dataset: FundamentalDataset) -> EvidenceGatewayStatus:
    if dataset.freshness is FreshnessState.STALE:
        return EvidenceGatewayStatus.STALE
    if (
        dataset.missing_families
        or dataset.missing_periods
        or dataset.quality is not DataQuality.GOOD
    ):
        return EvidenceGatewayStatus.PARTIAL
    return EvidenceGatewayStatus.SUCCESS
