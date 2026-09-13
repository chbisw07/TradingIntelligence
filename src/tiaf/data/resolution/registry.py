"""Small explicit registry for provider-specific instrument resolvers."""

from tiaf.cold_bindings import FrozenBindingsError
from tiaf.data.normalization import normalize_provider_name
from tiaf.data.resolution.errors import InstrumentResolutionError
from tiaf.data.resolution.models import InstrumentQuery, ResolutionResult
from tiaf.data.resolution.resolver import InstrumentResolver


class InstrumentResolverRegistry:
    """Select a resolver only when the provider is explicit or uniquely registered."""

    def __init__(self) -> None:
        self._frozen = False
        self._resolvers: dict[str, InstrumentResolver] = {}

    def register(self, provider: str, resolver: InstrumentResolver) -> None:
        """Register or explicitly replace one provider's resolver."""
        if self._frozen:
            raise FrozenBindingsError()
        self._resolvers[normalize_provider_name(provider)] = resolver

    def frozen_copy(self) -> "InstrumentResolverRegistry":
        """Create a startup-owned binding snapshot; pre-start replacement stays valid."""
        snapshot = InstrumentResolverRegistry()
        snapshot._resolvers = self._resolvers.copy()
        snapshot._frozen = True
        return snapshot

    def resolve(self, query: InstrumentQuery) -> ResolutionResult:
        """Route a query without guessing among multiple providers."""
        self._frozen = True
        if query.provider is not None:
            provider = query.provider
        elif len(self._resolvers) == 1:
            provider = next(iter(self._resolvers))
        else:
            raise InstrumentResolutionError(
                "query.provider is required when multiple resolvers are registered"
            )
        try:
            resolver = self._resolvers[provider]
        except KeyError as exc:
            raise InstrumentResolutionError(
                f"no instrument resolver registered for {provider}",
                provider=provider,
            ) from exc
        return resolver.resolve(query)
