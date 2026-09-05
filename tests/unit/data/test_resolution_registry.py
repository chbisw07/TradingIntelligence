"""Resolver protocol and explicit registry routing tests."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from tiaf.data.resolution import (
    InstrumentQuery,
    InstrumentResolutionError,
    InstrumentResolver,
    InstrumentResolverRegistry,
)

from .providers.dhan._instrument_master_support import resolver_at


def test_dhan_resolver_satisfies_runtime_protocol(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    assert isinstance(resolver, InstrumentResolver)


def test_registry_routes_single_provider_without_query_provider(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    registry = InstrumentResolverRegistry()
    registry.register("DHAN", resolver)
    result = registry.resolve(InstrumentQuery(provider_instrument_id="1333"))
    assert result.resolved is not None
    assert result.resolved.provider_instrument_id == "1333"


def test_registry_routes_explicit_provider(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    registry = InstrumentResolverRegistry()
    registry.register("dhan", resolver)
    result = registry.resolve(InstrumentQuery(symbol="ABSENT", provider="DHAN"))
    assert result.not_found


def test_registry_rejects_unregistered_provider() -> None:
    registry = InstrumentResolverRegistry()
    with pytest.raises(InstrumentResolutionError, match="no instrument resolver"):
        registry.resolve(InstrumentQuery(symbol="R", provider="DHAN"))


def test_registry_requires_provider_when_multiple_are_registered(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    registry = InstrumentResolverRegistry()
    registry.register("DHAN", resolver)
    registry.register("SECOND", resolver)
    with pytest.raises(InstrumentResolutionError, match="provider is required"):
        registry.resolve(InstrumentQuery(symbol="R"))


def test_resolution_timestamp_serializes_with_ist_offset(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(InstrumentQuery(provider_instrument_id="1333"))
    dumped = result.model_dump(mode="json")
    assert str(dumped["observed_at"]).endswith("+05:30")
    assert datetime.fromisoformat(str(dumped["observed_at"])).astimezone(UTC)
