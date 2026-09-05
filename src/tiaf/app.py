"""Minimal application context for the bootstrap baseline."""

from tiaf.version import __version__


def create_app_context() -> dict[str, str]:
    """Return static project metadata without initializing external services."""
    return {
        "project": "TradingIntelligence",
        "architecture": "TIAF",
        "milestone": "TIAF_TGT0",
        "version": __version__,
        "status": "bootstrap",
    }
