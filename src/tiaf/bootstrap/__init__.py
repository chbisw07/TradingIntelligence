"""Trusted COLD startup; pure metadata inspection does not resolve optional SDKs."""

from .catalog import RegisteredComponent, registered_components
from .contracts import (
    ColdStartupConfig,
    ComponentResolution,
    ComponentSelection,
    MissingSelectionPolicy,
    RuntimeProfile,
    StartupComposition,
    StartupError,
    StartupFailure,
    replay_startup_composition,
    resolve_startup_config,
)
from .runtime import ColdRuntimeOwner, create_cold_runtime

__all__ = [
    "ColdRuntimeOwner",
    "ColdStartupConfig",
    "ComponentResolution",
    "ComponentSelection",
    "MissingSelectionPolicy",
    "RegisteredComponent",
    "RuntimeProfile",
    "StartupComposition",
    "StartupError",
    "StartupFailure",
    "create_cold_runtime",
    "registered_components",
    "replay_startup_composition",
    "resolve_startup_config",
]
