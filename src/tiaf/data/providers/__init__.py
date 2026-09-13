"""Concrete market-data provider adapters with import-isolated transports."""

from typing import TYPE_CHECKING, Any

from tiaf.optional_adapters import load_optional_attribute

if TYPE_CHECKING:
    from tiaf.data.providers.dhan import DhanConfig, DhanInstrumentType, DhanMarketDataProvider

_OPTIONAL_EXPORTS = {
    "DhanConfig": "config",
    "DhanInstrumentType": "mappings",
    "DhanMarketDataProvider": "provider",
}


def __getattr__(name: str) -> Any:
    try:
        module = _OPTIONAL_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(name) from exc
    value = load_optional_attribute(
        adapter_id="provider.market-data.dhan",
        module=f"tiaf.data.providers.dhan.{module}",
        attribute=name,
        dependency_imports=("httpx", "pydantic_settings"),
    )
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))

__all__ = ["DhanConfig", "DhanInstrumentType", "DhanMarketDataProvider"]
