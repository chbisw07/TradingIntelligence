from datetime import datetime
from zoneinfo import ZoneInfo

from tiaf.agents import AgentBudget, AgentCapability
from tiaf.contracts import DataQuality, FreshnessState, Horizon
from tiaf.market_intelligence import (
    AvailabilityBasis,
    CapabilitySupport,
    DerivationClass,
    EvidenceOutputType,
    MarketIntelligenceCapability,
    MarketIntelligenceRequest,
    PointInTimeQuality,
    ProviderCapabilityConstraints,
    ProviderCapabilityDeclaration,
    ProviderFetchResult,
    ProviderNativeObservation,
    ProviderResultStatus,
    SourceAuthority,
    authority_for,
)

IST = ZoneInfo("Asia/Kolkata")
AS_OF = datetime(2026, 9, 9, 12, tzinfo=IST)
AVAILABLE = datetime(2026, 8, 1, 23, 59, tzinfo=IST)


def declaration(
    capability: MarketIntelligenceCapability = MarketIntelligenceCapability.READ_FINANCIALS,
    *,
    support: CapabilitySupport = CapabilitySupport.FULL,
) -> ProviderCapabilityDeclaration:
    return ProviderCapabilityDeclaration(
        capability=capability,
        support=support,
        constraints=(
            ProviderCapabilityConstraints(
                output_types=(EvidenceOutputType.SECONDARY_STRUCTURED,),
                source_authority=SourceAuthority.TRUSTED_SECONDARY,
                point_in_time_quality=PointInTimeQuality.CONSERVATIVE,
                cost_units_per_call=1,
                normalizer_id=f"fixture-{capability.value.casefold()}",
                normalizer_version="1.0",
                native_schema_version="1.0",
            )
            if support is not CapabilitySupport.UNSUPPORTED
            else None
        ),
    )


def request(
    capability: MarketIntelligenceCapability = MarketIntelligenceCapability.READ_FINANCIALS,
    *,
    required: tuple[str, ...] = (),
    max_calls: int = 3,
    max_cost: float = 3,
) -> MarketIntelligenceRequest:
    authority = authority_for(capability)
    return MarketIntelligenceRequest(
        request_id="request-1",
        capability=capability,
        authority=authority,
        allowed_authorities=(AgentCapability.READ_A2_EVIDENCE, authority),
        subject="reliance",
        as_of=AS_OF,
        horizon=Horizon(label="POSITIONAL"),
        required_freshness=FreshnessState.FRESH,
        required_canonical_metrics=required,
        budget=AgentBudget(
            max_tool_calls=max_calls,
            max_cost_units=max_cost,
            max_elapsed_seconds=30,
        ),
    )


def observation(
    provider_id: str,
    observation_id: str,
    field: str,
    value: float,
    *,
    capability: MarketIntelligenceCapability = MarketIntelligenceCapability.READ_FINANCIALS,
    available_at: datetime = AVAILABLE,
    source_reference: str | None = "https://example.test/source",
    period: str | None = "FY2026",
    lineage: tuple[str, ...] = (),
) -> ProviderNativeObservation:
    return ProviderNativeObservation(
        observation_id=observation_id,
        provider_id=provider_id,
        capability=capability,
        subject="RELIANCE",
        native_field=field,
        native_label=field,
        value=value,
        unit="INR crore",
        currency="INR",
        period_label=period,
        available_from=available_at,
        acquired_at=max(available_at, AS_OF),
        availability_basis=AvailabilityBasis.PROVIDER_AVAILABLE_FROM,
        point_in_time_quality=PointInTimeQuality.EXACT,
        source_reference=source_reference,
        source_quality=DataQuality.GOOD,
        output_type=EvidenceOutputType.SECONDARY_STRUCTURED,
        derivation_class=DerivationClass.REPORTED,
        lineage_observation_ids=lineage,
    )


def result(
    provider_id: str,
    *observations: ProviderNativeObservation,
    status: ProviderResultStatus = ProviderResultStatus.SUCCESS,
) -> ProviderFetchResult:
    capability = (
        observations[0].capability if observations else MarketIntelligenceCapability.READ_FINANCIALS
    )
    return ProviderFetchResult(
        provider_id=provider_id,
        capability=capability,
        status=status,
        observations=observations,
        cost_units=1,
    )
