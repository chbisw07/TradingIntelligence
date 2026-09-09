"""Framework-independent provider and normalization boundaries."""

from typing import Protocol, runtime_checkable

from .models import (
    MarketIntelligenceRequest,
    NormalizedEvidenceBatch,
    ProviderFetchResult,
    ProviderIdentity,
    ProviderManifest,
)


@runtime_checkable
class MarketIntelligenceProvider(Protocol):
    @property
    def identity(self) -> ProviderIdentity: ...

    @property
    def manifest(self) -> ProviderManifest: ...

    def fetch(self, request: MarketIntelligenceRequest) -> ProviderFetchResult: ...


@runtime_checkable
class MarketIntelligenceNormalizer(Protocol):
    @property
    def provider_id(self) -> str: ...

    def normalize(
        self,
        request: MarketIntelligenceRequest,
        result: ProviderFetchResult,
    ) -> NormalizedEvidenceBatch: ...
