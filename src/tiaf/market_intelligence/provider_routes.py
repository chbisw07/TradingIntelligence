"""Explicit provider-ID configuration for the Yahoo secondary integration."""

from .enums import MarketIntelligenceCapability, RoutingMode
from .models import CapabilityRoutePolicy

_TAPETIDE_YAHOO_CAPABILITIES = frozenset(
    {
        MarketIntelligenceCapability.READ_COMPANY_PROFILE,
        MarketIntelligenceCapability.READ_COMPANY_IDENTITY,
        MarketIntelligenceCapability.READ_FINANCIALS,
        MarketIntelligenceCapability.READ_VALUATION_CONTEXT,
        MarketIntelligenceCapability.READ_NEWS,
        MarketIntelligenceCapability.READ_ANALYST_FORECASTS,
    }
)


def yahoo_secondary_route_policy(
    capability: MarketIntelligenceCapability,
    *,
    mode: RoutingMode | None = None,
    required_canonical_metrics: tuple[str, ...] = (),
) -> CapabilityRoutePolicy:
    """Build the bounded Tapetide→Yahoo route or Yahoo-only earnings route."""
    if capability is MarketIntelligenceCapability.READ_EARNINGS_CALENDAR:
        selected_mode = mode or RoutingMode.FIRST_SUCCESS
        if selected_mode is not RoutingMode.FIRST_SUCCESS:
            raise ValueError("Yahoo earnings route supports FIRST_SUCCESS only")
        return CapabilityRoutePolicy(
            policy_id="yahoo-earnings-primary",
            capability=capability,
            mode=selected_mode,
            provider_ids=("yahoo",),
            maximum_provider_calls=1,
            required_canonical_metrics=required_canonical_metrics,
        )
    if capability not in _TAPETIDE_YAHOO_CAPABILITIES:
        raise ValueError(f"Yahoo secondary route does not support {capability}")
    selected_mode = mode or RoutingMode.PRIMARY_WITH_FALLBACK
    if selected_mode not in {RoutingMode.PRIMARY_WITH_FALLBACK, RoutingMode.MULTI_SOURCE}:
        raise ValueError("Yahoo secondary route supports fallback or multi-source mode")
    return CapabilityRoutePolicy(
        policy_id="tapetide-yahoo-secondary",
        capability=capability,
        mode=selected_mode,
        provider_ids=("tapetide", "yahoo"),
        maximum_provider_calls=2,
        minimum_successful_providers=(
            2 if selected_mode is RoutingMode.MULTI_SOURCE else 1
        ),
        required_canonical_metrics=required_canonical_metrics,
    )
