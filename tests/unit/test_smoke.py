"""Smoke tests for the TIAF bootstrap baseline."""

from importlib import import_module

import tiaf
from tiaf.app import create_app_context
from tiaf.config import Settings


def test_package_exposes_version() -> None:
    assert tiaf.__version__ == "0.1.0"


def test_settings_have_safe_defaults() -> None:
    settings = Settings()

    assert settings.env == "development"
    assert settings.log_level == "INFO"
    assert str(settings.data_dir) == "data"
    assert settings.primary_exchange == "NSE"
    assert settings.primary_fno_exchange == "NSE"


def test_primary_market_scope_settings_are_configurable_and_normalized() -> None:
    settings = Settings(
        primary_exchange=" bse ",
        primary_fno_exchange="bse",
    )
    assert settings.primary_exchange == "BSE"
    assert settings.primary_fno_exchange == "BSE"


def test_app_context_contains_baseline_metadata() -> None:
    assert create_app_context() == {
        "project": "TradingIntelligence",
        "architecture": "TIAF",
        "milestone": "TIAF_TGT0",
        "version": "0.1.0",
        "status": "bootstrap",
    }


def test_package_namespaces_are_importable() -> None:
    namespaces = (
        "agents",
        "arbitration",
        "config",
        "contracts",
        "data",
        "evaluation",
        "memory",
        "observability",
        "planner",
        "service",
        "workflows",
    )

    for namespace in namespaces:
        assert import_module(f"tiaf.{namespace}") is not None
