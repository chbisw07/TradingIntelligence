"""Public DhanHQ v2 read-only core, live, and historical derivatives adapter."""

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
from tiaf.data.providers.dhan.provider import DhanMarketDataProvider, plan_rolling_option_chunks
from tiaf.data.providers.dhan.rate_policies import (
    DHAN_OPTION_CHAIN_RATE_POLICY,
    DHAN_QUOTE_RATE_POLICY,
    DHAN_RATE_POLICIES,
    dhan_rate_policy_registry,
)
from tiaf.data.providers.dhan.transport import DhanTransport, HttpxDhanTransport

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
