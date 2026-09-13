"""Import-safe metadata and failure handling for optional adapters.

This module is deliberately dependency-free.  It describes optional integration
surfaces without importing their implementations or probing the environment.
"""

from dataclasses import dataclass
from enum import StrEnum
from importlib import import_module
from typing import Any


class OptionalAdapterClassification(StrEnum):
    """R4 audit classification for an optional, import-isolated integration."""

    OPTIONAL_ISOLATED = "OPTIONAL_ISOLATED"


class OptionalAdapterFailure(StrEnum):
    """Stable, non-secret failure categories for explicit adapter selection."""

    OPTIONAL_DEPENDENCY_MISSING = "OPTIONAL_DEPENDENCY_MISSING"
    OPTIONAL_ADAPTER_IMPORT_FAILED = "OPTIONAL_ADAPTER_IMPORT_FAILED"
    UNSUPPORTED_ADAPTER = "UNSUPPORTED_ADAPTER"


@dataclass(frozen=True, slots=True)
class OptionalAdapterDescriptor:
    """Static discovery metadata that never imports an adapter implementation."""

    adapter_id: str
    classification: OptionalAdapterClassification
    dependencies: tuple[str, ...]
    install_extra: str


class OptionalAdapterError(RuntimeError):
    """A bounded failure raised only after an optional adapter is selected."""

    def __init__(
        self,
        *,
        failure: OptionalAdapterFailure,
        adapter_id: str,
        dependency: str | None = None,
    ) -> None:
        self.failure = failure
        self.adapter_id = adapter_id
        self.dependency = dependency
        detail = f"; missing dependency: {dependency}" if dependency else ""
        super().__init__(f"optional adapter '{adapter_id}' is unavailable ({failure}){detail}")


_OPTIONAL_ADAPTERS = (
    OptionalAdapterDescriptor(
        adapter_id="provider.market-data.dhan",
        classification=OptionalAdapterClassification.OPTIONAL_ISOLATED,
        dependencies=("httpx", "pydantic-settings"),
        install_extra="data-provider-dhan",
    ),
    OptionalAdapterDescriptor(
        adapter_id="provider.market-intelligence.authoritative-http",
        classification=OptionalAdapterClassification.OPTIONAL_ISOLATED,
        dependencies=("httpx",),
        install_extra="market-intelligence-http",
    ),
    OptionalAdapterDescriptor(
        adapter_id="provider.market-intelligence.tapetide-mcp",
        classification=OptionalAdapterClassification.OPTIONAL_ISOLATED,
        dependencies=("mcp", "python-dotenv"),
        install_extra="market-intelligence-mcp",
    ),
    OptionalAdapterDescriptor(
        adapter_id="provider.market-intelligence.yahoo-mcp",
        classification=OptionalAdapterClassification.OPTIONAL_ISOLATED,
        dependencies=("mcp",),
        install_extra="market-intelligence-mcp",
    ),
    OptionalAdapterDescriptor(
        adapter_id="workflow.langgraph",
        classification=OptionalAdapterClassification.OPTIONAL_ISOLATED,
        dependencies=("langgraph", "langsmith"),
        install_extra="orchestration",
    ),
)


def optional_adapter_catalog() -> tuple[OptionalAdapterDescriptor, ...]:
    """Return static R4 metadata without importing or testing integrations."""

    return _OPTIONAL_ADAPTERS


def optional_adapter_descriptor(adapter_id: str) -> OptionalAdapterDescriptor:
    """Resolve static metadata or fail explicitly for an unknown adapter ID."""

    descriptor = next((item for item in _OPTIONAL_ADAPTERS if item.adapter_id == adapter_id), None)
    if descriptor is None:
        raise OptionalAdapterError(
            failure=OptionalAdapterFailure.UNSUPPORTED_ADAPTER,
            adapter_id=adapter_id,
        )
    return descriptor


def load_optional_attribute(
    *,
    adapter_id: str,
    module: str,
    attribute: str,
    dependency_imports: tuple[str, ...],
) -> Any:
    """Load one selected adapter attribute and classify only known missing SDKs.

    An unrelated ``ModuleNotFoundError`` is intentionally allowed to escape so a
    defect inside an installed adapter is not misreported as an absent optional
    dependency.
    """

    try:
        implementation = import_module(module)
    except ModuleNotFoundError as exc:
        missing = exc.name or ""
        missing_root = missing.partition(".")[0]
        if missing_root in dependency_imports:
            raise OptionalAdapterError(
                failure=OptionalAdapterFailure.OPTIONAL_DEPENDENCY_MISSING,
                adapter_id=adapter_id,
                dependency=missing_root,
            ) from exc
        raise
    try:
        return getattr(implementation, attribute)
    except AttributeError as exc:
        raise OptionalAdapterError(
            failure=OptionalAdapterFailure.OPTIONAL_ADAPTER_IMPORT_FAILED,
            adapter_id=adapter_id,
        ) from exc


__all__ = [
    "OptionalAdapterClassification",
    "OptionalAdapterDescriptor",
    "OptionalAdapterError",
    "OptionalAdapterFailure",
    "load_optional_attribute",
    "optional_adapter_catalog",
    "optional_adapter_descriptor",
]
