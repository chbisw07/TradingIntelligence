"""A2.8 boundaries, public inventory, and smoke-request architecture tests."""

import ast
import runpy
from pathlib import Path
from typing import Any

from tiaf.features import (
    MULTI_TIMEFRAME_FEATURE_DEFINITIONS,
    RELATIVE_FEATURE_DEFINITIONS,
    BenchmarkRole,
    builtin_feature_registry,
)


def _load(path: str, name: str) -> dict[str, Any]:
    return runpy.run_path(path, run_name=name)


def test_relative_feature_inventory_is_exact_and_not_single_context_registered() -> None:
    identifiers = tuple(item.feature_id for item in RELATIVE_FEATURE_DEFINITIONS)
    assert identifiers == (
        "relative.subject_return_percent",
        "relative.benchmark_return_percent",
        "relative.return_spread_percent",
        "relative.return_ratio",
        "relative.excess_move_atr",
        "relative.strength_consistency",
    )
    registered = {item.feature_id for item in builtin_feature_registry().definitions()}
    assert not registered.intersection(identifiers)


def test_multi_timeframe_feature_inventory_is_exact() -> None:
    assert tuple(item.feature_id for item in MULTI_TIMEFRAME_FEATURE_DEFINITIONS) == (
        "mtf.requested_timeframe_count",
        "mtf.available_timeframe_count",
        "mtf.positive_return_fraction",
        "mtf.negative_return_fraction",
        "mtf.price_above_ema_fraction",
        "mtf.price_below_ema_fraction",
        "mtf.positive_slope_fraction",
        "mtf.negative_slope_fraction",
        "mtf.directional_agreement_fraction",
        "mtf.disagreement_fraction",
    )


def test_benchmark_roles_are_explicit() -> None:
    assert tuple(role.value for role in BenchmarkRole) == (
        "MARKET",
        "SECTOR",
        "PEER",
        "CUSTOM",
    )


def test_a28_calculators_have_no_provider_or_policy_dependencies() -> None:
    for path in (
        Path("src/tiaf/features/relative.py"),
        Path("src/tiaf/features/multi_timeframe.py"),
    ):
        tree = ast.parse(path.read_text())
        imports = {
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        imported_names = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        assert not any("provider" in name for name in imports | imported_names)
        source = path.read_text().casefold()
        for forbidden in ("recommendation", "ranking", "langgraph", "broker execution"):
            assert forbidden not in source


def test_relative_smoke_request_inventory_is_explicit() -> None:
    namespace = _load("scripts/relative_strength_smoke.py", "relative_smoke")
    requests = namespace["_requests"]("1d", 20, 14)
    assert tuple(request.feature_id for request in requests) == tuple(
        item.feature_id for item in RELATIVE_FEATURE_DEFINITIONS
    )
    assert all(request.interval == "1d" for request in requests)


def test_multi_timeframe_smoke_request_inventory_is_factual() -> None:
    namespace = _load("scripts/multi_timeframe_smoke.py", "mtf_smoke")
    constituent = namespace["_constituent_requests"]("15m", 20, 20)
    assert tuple(request.feature_id for request in constituent) == (
        "return.percent",
        "trend.distance_from_ema_percent",
        "trend.linear_slope",
    )
    aggregate = namespace["_aggregate_requests"](20, 20)
    assert {request.feature_id for request in aggregate} == {
        item.feature_id for item in MULTI_TIMEFRAME_FEATURE_DEFINITIONS
    }


def test_dhan_intraday_smoke_limit_is_visible_and_daily_is_unchanged() -> None:
    namespace = _load("scripts/multi_timeframe_smoke.py", "mtf_smoke_limits")
    effective = namespace["_effective_lookback"]
    assert effective("1d", 180) == 180
    assert effective("1h", 180) == 90
    assert effective("15m", 30) == 30
