"""Explicit provider registration without SDK imports in core routing."""

from .enums import CapabilitySupport, MarketIntelligenceCapability
from .protocols import MarketIntelligenceNormalizer, MarketIntelligenceProvider


class MarketIntelligenceRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, MarketIntelligenceProvider] = {}
        self._normalizers: dict[str, MarketIntelligenceNormalizer] = {}

    def register(
        self,
        provider: MarketIntelligenceProvider,
        normalizer: MarketIntelligenceNormalizer,
    ) -> None:
        provider_id = provider.identity.provider_id
        if provider_id != provider.manifest.identity.provider_id:
            raise ValueError("provider identity and manifest identity disagree")
        if normalizer.provider_id != provider_id:
            raise ValueError("normalizer must identify its provider")
        if provider_id in self._providers:
            raise ValueError(f"provider already registered: {provider_id}")
        self._providers[provider_id] = provider
        self._normalizers[provider_id] = normalizer

    def provider(self, provider_id: str) -> MarketIntelligenceProvider:
        try:
            return self._providers[provider_id]
        except KeyError as exc:
            raise LookupError(
                f"market-intelligence provider not registered: {provider_id}"
            ) from exc

    def normalizer(self, provider_id: str) -> MarketIntelligenceNormalizer:
        try:
            return self._normalizers[provider_id]
        except KeyError as exc:
            raise LookupError(f"normalizer not registered: {provider_id}") from exc

    def eligible(
        self, capability: MarketIntelligenceCapability
    ) -> tuple[MarketIntelligenceProvider, ...]:
        providers = []
        for provider in self._providers.values():
            declaration = provider.manifest.declaration_for(capability)
            if declaration is not None and declaration.support is not CapabilitySupport.UNSUPPORTED:
                providers.append(provider)
        return tuple(providers)
