"""Code-owned implementation allowlist. No config value is an import path."""

from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from tiaf.optional_adapters import load_optional_attribute

from .contracts import StartupError, StartupFailure


@dataclass(frozen=True, slots=True)
class RegisteredComponent:
    component_id: str
    implementation_version: str
    category: str


# Paths/exports below are reviewed Python code, never configuration or discovery input.
_ADAPTER_EXPORTS = {
    "provider.market-data.dhan": (
        "tiaf.data.providers.dhan.provider",
        "DhanMarketDataProvider",
        ("httpx", "pydantic_settings"),
    ),
    "provider.market-intelligence.authoritative-http": (
        "tiaf.market_intelligence.providers.authoritative_http",
        "HttpxOfficialDocumentTransport",
        ("httpx",),
    ),
    "provider.market-intelligence.tapetide-mcp": (
        "tiaf.market_intelligence.providers.tapetide_mcp",
        "TapetideMcpClient",
        ("mcp", "dotenv"),
    ),
    "provider.market-intelligence.yahoo-mcp": (
        "tiaf.market_intelligence.providers.yahoo_mcp",
        "YahooMcpClient",
        ("mcp",),
    ),
}
_SPECIALISTS = (
    "derivatives-context",
    "fundamental",
    "macro",
    "news-event",
    "opportunity-quality",
    "opportunity-risk",
    "relative-strength",
    "sector",
    "technical",
)
_COMPONENTS = tuple(
    sorted(
        (
            *(RegisteredComponent(key, "1.0", "adapter") for key in _ADAPTER_EXPORTS),
            *(
                RegisteredComponent(f"specialist:{key}", "1.0", "specialist")
                for key in _SPECIALISTS
            ),
            RegisteredComponent("workflow.serial", "1.0", "workflow"),
            RegisteredComponent("workflow.langgraph", "1.2.11", "workflow"),
        ),
        key=lambda x: x.component_id,
    )
)


def registered_components() -> tuple[RegisteredComponent, ...]:
    """Pure declarations; no readiness/authority claim or plugin registration API."""
    return _COMPONENTS


def registered_component(component_id: str) -> RegisteredComponent:
    for item in _COMPONENTS:
        if item.component_id == component_id:
            return item
    raise StartupError(StartupFailure.UNKNOWN_COMPONENT_ID)


def load_selected_adapter(component_id: str) -> Any:
    try:
        module, attribute, imports = _ADAPTER_EXPORTS[component_id]
    except KeyError:
        raise StartupError(StartupFailure.UNKNOWN_COMPONENT_ID) from None
    return load_optional_attribute(
        adapter_id=component_id, module=module, attribute=attribute, dependency_imports=imports
    )


def check_langgraph_imports() -> None:
    # The R4 module is itself import-safe: selection must also resolve its SDKs now.
    for module, attribute in (
        ("langgraph.graph", "StateGraph"),
        ("langgraph.graph", "START"),
        ("langgraph.graph", "END"),
        ("langsmith.run_helpers", "tracing_context"),
    ):
        load_optional_attribute(
            adapter_id="workflow.langgraph",
            module=module,
            attribute=attribute,
            dependency_imports=("langgraph", "langsmith"),
        )
    try:
        installed_version = version("langgraph")
    except PackageNotFoundError:
        raise StartupError(StartupFailure.COMPONENT_IMPORT_FAILED) from None
    if installed_version != "1.2.11":
        raise StartupError(StartupFailure.INCOMPATIBLE_COMPONENT_VERSION)
