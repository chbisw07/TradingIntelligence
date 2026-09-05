"""Small explicit registry for provider-specific instrument resolvers."""

from tiaf.data.normalization import normalize_provider_name
from tiaf.data.resolution.errors import InstrumentResolutionError
from tiaf.data.resolution.models import InstrumentQuery, ResolutionResult
from tiaf.data.resolution.resolver import InstrumentResolver


class InstrumentResolverRegistry:
    """Select a resolver only when the provider is explicit or uniquely registered."""

    def __init__(self) -> None:
        self._resolvers: dict[str, InstrumentResolver] = {}

    def register(self, provider: str, resolver: InstrumentResolver) -> None:
        """Register or explicitly replace one provider's resolver."""
        self._resolvers[normalize_provider_name(provider)] = resolver

    def resolve(self, query: InstrumentQuery) -> ResolutionResult:
        """Route a query without guessing among multiple providers."""
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
