"""Bounded provider protocols and deterministic point-in-time fixture adapters."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Protocol, runtime_checkable

from tiaf.contracts import DataQuality, FreshnessState

from .models import (
    ContextObservation,
    MacroContextRequest,
    MacroContextSnapshot,
    SectorContextRequest,
    SectorContextSnapshot,
    SectorIdentity,
    SubjectMacroSensitivity,
    context_fingerprint,
)


class MarketContextProviderError(RuntimeError):
    """Sanitized provider-neutral context acquisition failure."""


@runtime_checkable
class SectorContextProvider(Protocol):
    def identity(self) -> tuple[str, str]: ...
    def resolve_sector(self, subject: str, as_of: datetime) -> SectorIdentity | None: ...
    def fetch(self, request: SectorContextRequest) -> SectorContextSnapshot: ...


@runtime_checkable
class MacroContextProvider(Protocol):
    def identity(self) -> tuple[str, str]: ...
    def fetch(self, request: MacroContextRequest) -> MacroContextSnapshot: ...


def _quality(observations: tuple[ContextObservation, ...]) -> DataQuality:
    if not observations:
        return DataQuality.UNAVAILABLE
    order = {
        DataQuality.GOOD: 0,
        DataQuality.PARTIAL: 1,
        DataQuality.DEGRADED: 2,
        DataQuality.UNAVAILABLE: 3,
    }
    return max((item.quality for item in observations), key=order.__getitem__)


def _freshness(observations: tuple[ContextObservation, ...]) -> FreshnessState:
    if not observations:
        return FreshnessState.UNKNOWN
    order = {
        FreshnessState.FRESH: 0,
        FreshnessState.AGING: 1,
        FreshnessState.STALE: 2,
        FreshnessState.UNKNOWN: 3,
    }
    return max((item.freshness for item in observations), key=order.__getitem__)


class InMemorySectorContextProvider:
    """Exact-mapping read adapter for tests and caller-supplied licensed data."""

    def __init__(
        self,
        mappings: dict[str, tuple[SectorIdentity, ...]],
        observations: tuple[ContextObservation, ...],
        *,
        provider_id: str = "tiaf.in-memory-sector-context",
        provider_version: str = "1.0",
        validity_minutes: int = 60,
    ) -> None:
        if validity_minutes <= 0:
            raise ValueError("context validity_minutes must be positive")
        self._mappings = {symbol.strip().upper(): values for symbol, values in mappings.items()}
        self._observations: dict[str, tuple[ContextObservation, ...]] = {}
        grouped: dict[str, list[ContextObservation]] = defaultdict(list)
        for item in observations:
            sector_id = item.metadata.get("sector_id")
            if not isinstance(sector_id, str) or not sector_id.strip():
                raise ValueError("sector observation requires explicit metadata.sector_id")
            grouped[sector_id].append(item)
        self._observations = {key: tuple(value) for key, value in grouped.items()}
        self._identity = (provider_id, provider_version)
        self._validity = timedelta(minutes=validity_minutes)
        self.fetch_count = 0

    def identity(self) -> tuple[str, str]:
        return self._identity

    def resolve_sector(self, subject: str, as_of: datetime) -> SectorIdentity | None:
        applicable = tuple(
            item
            for item in self._mappings.get(subject.strip().upper(), ())
            if item.applies_at(as_of)
        )
        if len(applicable) > 1:
            raise MarketContextProviderError("multiple sector mappings apply at decision time")
        return applicable[0] if applicable else None

    def fetch(self, request: SectorContextRequest) -> SectorContextSnapshot:
        self.fetch_count += 1
        identity = self.resolve_sector(request.subject, request.as_of)
        if (
            identity is None
            or identity.sector_id != request.sector_id
            or identity.benchmark_symbol != request.benchmark_symbol
        ):
            raise MarketContextProviderError(
                "request does not match an explicit active sector mapping"
            )
        selected = tuple(
            item
            for item in self._observations.get(identity.sector_id, ())
            if item.available_at <= request.as_of
            and item.family in request.families
            and (
                not item.applicable_horizons
                or (request.horizon.label or "") in item.applicable_horizons
            )
        )
        present = {item.family for item in selected}
        missing = tuple(item for item in request.families if item not in present)
        acquired_at = max((item.available_at for item in selected), default=request.as_of)
        provider_id, provider_version = self._identity
        payload = {
            "identity": identity,
            "as_of": request.as_of,
            "observations": selected,
            "missing": missing,
            "provider": self._identity,
        }
        fingerprint = context_fingerprint(payload)
        return SectorContextSnapshot(
            snapshot_id=f"sector:{identity.sector_id}:{fingerprint[:16]}",
            identity=identity,
            requested_as_of=request.as_of,
            observations=selected,
            missing_families=missing,
            quality=_quality(selected),
            freshness=_freshness(selected),
            acquired_at=acquired_at,
            valid_until=max(acquired_at, request.as_of) + self._validity,
            provider_id=provider_id,
            provider_version=provider_version,
            fingerprint=fingerprint,
        )


class InMemoryMacroContextProvider:
    """Reusable market snapshot adapter with explicit subject sensitivities."""

    def __init__(
        self,
        market_observations: dict[str, tuple[ContextObservation, ...]],
        sensitivities: tuple[SubjectMacroSensitivity, ...] = (),
        *,
        provider_id: str = "tiaf.in-memory-macro-context",
        provider_version: str = "1.0",
        validity_minutes: int = 60,
    ) -> None:
        if validity_minutes <= 0:
            raise ValueError("context validity_minutes must be positive")
        self._observations = {
            key.strip().upper(): value for key, value in market_observations.items()
        }
        self._sensitivities = sensitivities
        self._identity = (provider_id, provider_version)
        self._validity = timedelta(minutes=validity_minutes)
        self.fetch_count = 0

    def identity(self) -> tuple[str, str]:
        return self._identity

    def fetch(self, request: MacroContextRequest) -> MacroContextSnapshot:
        self.fetch_count += 1
        market = request.market.strip().upper()
        selected = tuple(
            item
            for item in self._observations.get(market, ())
            if item.available_at <= request.as_of
            and item.family in request.families
            and (
                not item.applicable_horizons
                or (request.horizon.label or "") in item.applicable_horizons
            )
        )
        # The market snapshot is intentionally subject-independent so one fetch can be
        # shared.  The gateway projects only the requesting subject's explicit mappings.
        sensitivities = tuple(
            item
            for item in self._sensitivities
            if item.family in request.families and item.applies_at(request.as_of)
        )
        present = {item.family for item in selected}
        missing = tuple(item for item in request.families if item not in present)
        acquired_at = max((item.available_at for item in selected), default=request.as_of)
        provider_id, provider_version = self._identity
        payload = {
            "market": market,
            "as_of": request.as_of,
            "observations": selected,
            "sensitivities": sensitivities,
            "missing": missing,
            "provider": self._identity,
        }
        fingerprint = context_fingerprint(payload)
        return MacroContextSnapshot(
            snapshot_id=f"macro:{market}:{fingerprint[:16]}",
            market=market,
            requested_as_of=request.as_of,
            observations=selected,
            sensitivities=sensitivities,
            missing_families=missing,
            quality=_quality(selected),
            freshness=_freshness(selected),
            acquired_at=acquired_at,
            valid_until=max(acquired_at, request.as_of) + self._validity,
            provider_id=provider_id,
            provider_version=provider_version,
            fingerprint=fingerprint,
        )
