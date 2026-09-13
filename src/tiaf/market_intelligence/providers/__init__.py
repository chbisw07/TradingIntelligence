"""Concrete read-only market-intelligence provider adapters.

Transport-backed exports are resolved only when explicitly selected so fixture
and provider-neutral imports do not require optional HTTP or MCP packages.
"""

from typing import TYPE_CHECKING, Any

from tiaf.optional_adapters import load_optional_attribute

from .authoritative import (
    AuthoritativeDocumentNormalizer,
    BseOfficialSourceProvider,
    CompanyIrOfficialSourceProvider,
    NseOfficialSourceProvider,
    OfficialDocumentLocator,
    OfficialDocumentResponse,
    OfficialDocumentTransport,
    OfficialDocumentTransportError,
    OfficialSourceMarketIntelligenceProvider,
    default_official_source_registry,
)
from .fixture import FixtureMarketIntelligenceProvider
from .tapetide import TapetideMarketIntelligenceProvider, TapetideToolClient
from .yahoo import (
    YahooMarketIntelligenceProvider,
    YahooNormalizer,
    YahooSymbolMapper,
    YahooToolClient,
    india_yahoo_symbol_mapper,
    yahoo_normalizer,
)

if TYPE_CHECKING:
    from .authoritative_http import HttpxOfficialDocumentTransport
    from .tapetide_mcp import (
        TAPETIDE_READ_TOOLS,
        TapetideCallTimeoutError,
        TapetideConnectionClosedError,
        TapetideConnectorError,
        TapetideCredentialError,
        TapetideInitializationError,
        TapetideMalformedResultError,
        TapetideMcpClient,
        TapetideProcessLaunchError,
        TapetideProviderCallError,
        TapetideSchemaDriftError,
        TapetideToolNotAllowedError,
    )
    from .yahoo_mcp import (
        YAHOO_READ_TOOLS,
        YahooCallTimeoutError,
        YahooConnectionClosedError,
        YahooConnectorError,
        YahooInitializationError,
        YahooMalformedResultError,
        YahooMcpClient,
        YahooProcessLaunchError,
        YahooProviderCallError,
        YahooSchemaDriftError,
        YahooToolNotAllowedError,
    )


_OPTIONAL_EXPORTS: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "HttpxOfficialDocumentTransport": (
        "provider.market-intelligence.authoritative-http",
        ".authoritative_http",
        ("httpx",),
    ),
    **{
        name: ("provider.market-intelligence.tapetide-mcp", ".tapetide_mcp", ("mcp", "dotenv"))
        for name in (
            "TAPETIDE_READ_TOOLS",
            "TapetideCallTimeoutError",
            "TapetideConnectionClosedError",
            "TapetideConnectorError",
            "TapetideCredentialError",
            "TapetideInitializationError",
            "TapetideMalformedResultError",
            "TapetideMcpClient",
            "TapetideProcessLaunchError",
            "TapetideProviderCallError",
            "TapetideSchemaDriftError",
            "TapetideToolNotAllowedError",
        )
    },
    **{
        name: ("provider.market-intelligence.yahoo-mcp", ".yahoo_mcp", ("mcp",))
        for name in (
            "YAHOO_READ_TOOLS",
            "YahooCallTimeoutError",
            "YahooConnectionClosedError",
            "YahooConnectorError",
            "YahooInitializationError",
            "YahooMalformedResultError",
            "YahooMcpClient",
            "YahooProcessLaunchError",
            "YahooProviderCallError",
            "YahooSchemaDriftError",
            "YahooToolNotAllowedError",
        )
    },
}


def __getattr__(name: str) -> Any:
    try:
        adapter_id, relative_module, dependencies = _OPTIONAL_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(name) from exc
    value = load_optional_attribute(
        adapter_id=adapter_id,
        module=f"{__name__}{relative_module}",
        attribute=name,
        dependency_imports=dependencies,
    )
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))

__all__ = [
    "AuthoritativeDocumentNormalizer",
    "BseOfficialSourceProvider",
    "CompanyIrOfficialSourceProvider",
    "FixtureMarketIntelligenceProvider",
    "HttpxOfficialDocumentTransport",
    "NseOfficialSourceProvider",
    "OfficialDocumentLocator",
    "OfficialDocumentResponse",
    "OfficialDocumentTransport",
    "OfficialDocumentTransportError",
    "OfficialSourceMarketIntelligenceProvider",
    "TAPETIDE_READ_TOOLS",
    "TapetideCallTimeoutError",
    "TapetideConnectionClosedError",
    "TapetideConnectorError",
    "TapetideCredentialError",
    "TapetideInitializationError",
    "TapetideMarketIntelligenceProvider",
    "TapetideMalformedResultError",
    "TapetideMcpClient",
    "TapetideProcessLaunchError",
    "TapetideProviderCallError",
    "TapetideSchemaDriftError",
    "TapetideToolClient",
    "TapetideToolNotAllowedError",
    "YAHOO_READ_TOOLS",
    "YahooCallTimeoutError",
    "YahooConnectionClosedError",
    "YahooConnectorError",
    "YahooInitializationError",
    "YahooMalformedResultError",
    "YahooMarketIntelligenceProvider",
    "YahooMcpClient",
    "YahooNormalizer",
    "YahooProcessLaunchError",
    "YahooProviderCallError",
    "YahooSchemaDriftError",
    "YahooSymbolMapper",
    "YahooToolClient",
    "YahooToolNotAllowedError",
    "india_yahoo_symbol_mapper",
    "yahoo_normalizer",
    "default_official_source_registry",
]
