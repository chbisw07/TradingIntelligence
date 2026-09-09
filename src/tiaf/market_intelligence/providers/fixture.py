"""Deterministic secondary provider used for routing, replay, and substitution tests."""

from collections.abc import Mapping

from ..enums import (
    CapabilitySupport,
    ProviderFailureKind,
    ProviderResultStatus,
    SourceAuthority,
)
from ..models import (
    MarketIntelligenceRequest,
    ProviderCapabilityDeclaration,
    ProviderFailure,
    ProviderFetchResult,
    ProviderIdentity,
    ProviderManifest,
    ProviderNativeObservation,
)


class FixtureMarketIntelligenceProvider:
    def __init__(
        self,
        provider_id: str,
        declarations: tuple[ProviderCapabilityDeclaration, ...],
        results: Mapping[tuple[str, str], ProviderFetchResult],
        *,
        source_authority: SourceAuthority = SourceAuthority.TRUSTED_SECONDARY,
    ) -> None:
        self._identity = ProviderIdentity(
            provider_id=provider_id,
            display_name=f"Fixture provider {provider_id}",
            adapter_version="1.0",
        )
        self._manifest = ProviderManifest(
            identity=self._identity,
            source_authority=source_authority,
            capabilities=declarations,
        )
        self._results = dict(results)
        self.calls: list[tuple[str, str]] = []

    @property
    def identity(self) -> ProviderIdentity:
        return self._identity

    @property
    def manifest(self) -> ProviderManifest:
        return self._manifest

    def fetch(self, request: MarketIntelligenceRequest) -> ProviderFetchResult:
        key = (request.capability.value, request.subject)
        self.calls.append(key)
        declaration = self.manifest.declaration_for(request.capability)
        if declaration is None or declaration.support is CapabilitySupport.UNSUPPORTED:
            return self._failure(request, ProviderFailureKind.UNSUPPORTED_CAPABILITY)
        result = self._results.get(key)
        if result is None:
            return self._failure(request, ProviderFailureKind.OUT_OF_COVERAGE)
        visible: tuple[ProviderNativeObservation, ...] = tuple(
            item for item in result.observations if item.available_from <= request.as_of
        )
        if visible == result.observations:
            return result
        if visible:
            return result.model_copy(
                update={"status": ProviderResultStatus.PARTIAL, "observations": visible}
            )
        return self._failure(request, ProviderFailureKind.OUT_OF_COVERAGE)

    def _failure(
        self, request: MarketIntelligenceRequest, kind: ProviderFailureKind
    ) -> ProviderFetchResult:
        status = (
            ProviderResultStatus.UNSUPPORTED
            if kind is ProviderFailureKind.UNSUPPORTED_CAPABILITY
            else ProviderResultStatus.OUT_OF_COVERAGE
        )
        return ProviderFetchResult(
            provider_id=self.identity.provider_id,
            capability=request.capability,
            status=status,
            failures=(
                ProviderFailure(
                    kind=kind,
                    provider_id=self.identity.provider_id,
                    capability=request.capability,
                    message=f"fixture has no {request.capability} evidence for {request.subject}",
                ),
            ),
        )
