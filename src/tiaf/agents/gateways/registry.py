"""Deterministic registries for evidence gateways and reasoning providers."""

from dataclasses import dataclass

from tiaf.agents.enums import AgentCapability
from tiaf.agents.models import ReasoningModelIdentity
from tiaf.agents.protocols import ReasoningProvider

from .contracts import EvidenceGatewayRequest, GatewayIdentity
from .enums import ModelTier, model_tier_rank
from .errors import GatewayNotFoundError, GatewayRegistrationError
from .protocols import EvidenceGateway


class EvidenceGatewayRegistry:
    """Discover gateways by stable ID/capability without central branching."""

    def __init__(self, gateways: tuple[EvidenceGateway, ...] = ()) -> None:
        self._gateways: dict[str, EvidenceGateway] = {}
        for gateway in gateways:
            self.register(gateway)

    def register(self, gateway: EvidenceGateway) -> None:
        """Register one protocol-conforming gateway and reject duplicate IDs."""
        if not isinstance(gateway, EvidenceGateway):
            raise GatewayRegistrationError("gateway does not satisfy EvidenceGateway")
        identity = gateway.identity()
        if not isinstance(identity, GatewayIdentity):
            raise GatewayRegistrationError("gateway identity must be GatewayIdentity")
        capabilities = gateway.capabilities()
        if not capabilities or len(capabilities) != len(set(capabilities)):
            raise GatewayRegistrationError("gateway capabilities must be non-empty and unique")
        if identity.gateway_id in self._gateways:
            raise GatewayRegistrationError(f"duplicate gateway ID: {identity.gateway_id}")
        self._gateways[identity.gateway_id] = gateway

    def get(self, gateway_id: str) -> EvidenceGateway:
        """Return a gateway by exact ID."""
        try:
            return self._gateways[gateway_id]
        except KeyError as exc:
            raise GatewayNotFoundError(f"gateway {gateway_id!r} is not registered") from exc

    def identities(self) -> tuple[GatewayIdentity, ...]:
        """Return a stable gateway-ID-sorted discovery snapshot."""
        return tuple(
            self._gateways[key].identity() for key in sorted(self._gateways)
        )

    def capabilities(self) -> tuple[AgentCapability, ...]:
        """Return sorted unique capabilities across registered gateways."""
        return tuple(
            sorted(
                {item for gateway in self._gateways.values() for item in gateway.capabilities()},
                key=lambda item: item.value,
            )
        )

    def resolve(
        self,
        request: EvidenceGatewayRequest,
        *,
        gateway_id: str | None = None,
    ) -> EvidenceGateway:
        """Resolve one handler, requiring explicit choice when ownership overlaps."""
        if gateway_id is not None:
            gateway = self.get(gateway_id)
            if request.capability not in gateway.capabilities() or not gateway.can_handle(request):
                raise GatewayNotFoundError(
                    f"gateway {gateway_id!r} cannot handle {request.capability.value}"
                )
            return gateway
        matches = tuple(
            gateway
            for gateway in self._gateways.values()
            if request.capability in gateway.capabilities() and gateway.can_handle(request)
        )
        if not matches:
            raise GatewayNotFoundError(
                f"no gateway handles capability {request.capability.value}"
            )
        if len(matches) > 1:
            ids = ", ".join(sorted(item.identity().gateway_id for item in matches))
            raise GatewayRegistrationError(
                f"capability {request.capability.value} is ambiguous across: {ids}"
            )
        return matches[0]


@dataclass(frozen=True)
class ReasoningProviderRegistration:
    """One provider plus its explicitly supported vendor-neutral tiers."""

    provider: ReasoningProvider
    identity: ReasoningModelIdentity
    supported_tiers: tuple[ModelTier, ...]


class ReasoningProviderRegistry:
    """Provider-neutral registry selected only by configured model mappings."""

    def __init__(self) -> None:
        self._providers: dict[str, ReasoningProviderRegistration] = {}

    def register(
        self,
        provider: ReasoningProvider,
        *,
        supported_tiers: tuple[ModelTier, ...],
    ) -> None:
        """Register one provider identity and reject duplicates/invalid tiers."""
        if not isinstance(provider, ReasoningProvider):
            raise GatewayRegistrationError("provider does not satisfy ReasoningProvider")
        identity = provider.identity()
        if not isinstance(identity, ReasoningModelIdentity):
            raise GatewayRegistrationError(
                "reasoning provider identity must be ReasoningModelIdentity"
            )
        if (
            not supported_tiers
            or len(supported_tiers) != len(set(supported_tiers))
            or ModelTier.NONE in supported_tiers
        ):
            raise GatewayRegistrationError("supported model tiers are invalid")
        if identity.provider_id in self._providers:
            raise GatewayRegistrationError(
                f"duplicate reasoning provider ID: {identity.provider_id}"
            )
        self._providers[identity.provider_id] = ReasoningProviderRegistration(
            provider=provider,
            identity=identity,
            supported_tiers=tuple(sorted(supported_tiers, key=model_tier_rank)),
        )

    def get(self, provider_id: str) -> ReasoningProviderRegistration:
        """Return one exact provider registration."""
        try:
            return self._providers[provider_id]
        except KeyError as exc:
            raise GatewayNotFoundError(
                f"reasoning provider {provider_id!r} is not registered"
            ) from exc

    def registrations(self) -> tuple[ReasoningProviderRegistration, ...]:
        """Return a deterministic provider-ID-sorted snapshot."""
        return tuple(self._providers[key] for key in sorted(self._providers))
