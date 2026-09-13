"""Public DhanHQ v2 adapter with lazy, adapter-local implementation imports."""

from typing import TYPE_CHECKING, Any

from tiaf.optional_adapters import load_optional_attribute

if TYPE_CHECKING:
    from tiaf.data.providers.dhan.config import DhanConfig
    from tiaf.data.providers.dhan.identity import (
        DhanIdentityMismatchError,
        resolve_dhan_diagnostic_instrument,
    )
    from tiaf.data.providers.dhan.instrument_master import (
        DHAN_DETAILED_INSTRUMENT_MASTER_URL,
        DhanInstrumentMaster,
        DhanInstrumentMasterSnapshot,
        DhanInstrumentResolver,
        HttpxInstrumentMasterDownloader,
        InstrumentMasterDownloader,
    )
    from tiaf.data.providers.dhan.mappings import (
        DhanInstrumentType,
        to_dhan_instrument_type,
        to_dhan_segment,
    )
    from tiaf.data.providers.dhan.provider import (
        DhanMarketDataProvider,
        plan_rolling_option_chunks,
    )
    from tiaf.data.providers.dhan.rate_policies import (
        DHAN_OPTION_CHAIN_RATE_POLICY,
        DHAN_QUOTE_RATE_POLICY,
        DHAN_RATE_POLICIES,
        dhan_rate_policy_registry,
    )
    from tiaf.data.providers.dhan.transport import DhanTransport, HttpxDhanTransport


_EXPORT_MODULES = {
    "DhanConfig": "config",
    "DhanIdentityMismatchError": "identity",
    "resolve_dhan_diagnostic_instrument": "identity",
    "DHAN_DETAILED_INSTRUMENT_MASTER_URL": "instrument_master",
    "DhanInstrumentMaster": "instrument_master",
    "DhanInstrumentMasterSnapshot": "instrument_master",
    "DhanInstrumentResolver": "instrument_master",
    "HttpxInstrumentMasterDownloader": "instrument_master",
    "InstrumentMasterDownloader": "instrument_master",
    "DhanInstrumentType": "mappings",
    "to_dhan_instrument_type": "mappings",
    "to_dhan_segment": "mappings",
    "DhanMarketDataProvider": "provider",
    "plan_rolling_option_chunks": "provider",
    "DHAN_OPTION_CHAIN_RATE_POLICY": "rate_policies",
    "DHAN_QUOTE_RATE_POLICY": "rate_policies",
    "DHAN_RATE_POLICIES": "rate_policies",
    "dhan_rate_policy_registry": "rate_policies",
    "DhanTransport": "transport",
    "HttpxDhanTransport": "transport",
}


def __getattr__(name: str) -> Any:
    try:
        module = _EXPORT_MODULES[name]
    except KeyError as exc:
        raise AttributeError(name) from exc
    value = load_optional_attribute(
        adapter_id="provider.market-data.dhan",
        module=f"{__name__}.{module}",
        attribute=name,
        dependency_imports=("httpx", "pydantic_settings"),
    )
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))

__all__ = [
    "DhanConfig",
    "DHAN_DETAILED_INSTRUMENT_MASTER_URL",
    "DhanInstrumentMaster",
    "DhanInstrumentMasterSnapshot",
    "DhanInstrumentResolver",
    "DhanInstrumentType",
    "DhanIdentityMismatchError",
    "DhanMarketDataProvider",
    "DhanTransport",
    "HttpxDhanTransport",
    "HttpxInstrumentMasterDownloader",
    "InstrumentMasterDownloader",
    "DHAN_OPTION_CHAIN_RATE_POLICY",
    "DHAN_QUOTE_RATE_POLICY",
    "DHAN_RATE_POLICIES",
    "dhan_rate_policy_registry",
    "plan_rolling_option_chunks",
    "resolve_dhan_diagnostic_instrument",
    "to_dhan_instrument_type",
    "to_dhan_segment",
]
