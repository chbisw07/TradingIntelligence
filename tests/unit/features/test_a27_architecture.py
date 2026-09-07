"""A2.7 registry, provenance, architecture, and contract-boundary tests."""

import ast
import json
import math
import runpy
from datetime import timedelta
from pathlib import Path

import pytest

from tiaf.contracts import OptionType
from tiaf.features import (
    DERIVATIVES_FEATURE_DEFINITIONS,
    DeterministicFeatureEngine,
    FeatureCategory,
    FeatureParameterError,
    FeatureRequest,
    FeatureSourceKind,
    FeatureStatus,
    builtin_feature_registry,
)

from ..context._support import EXPIRY
from ._derivatives_support import context_with_option_chain, option_chain


def test_registry_contains_exact_a27_core_in_stable_order() -> None:
    definitions = builtin_feature_registry().definitions()
    assert len(DERIVATIVES_FEATURE_DEFINITIONS) == 39
    assert len(definitions) == 124
    assert len({item.feature_id for item in definitions}) == 124
    assert tuple(item.feature_id for item in definitions) == tuple(
        sorted(item.feature_id for item in definitions)
    )
    assert {item.feature_id for item in DERIVATIVES_FEATURE_DEFINITIONS} <= {
        item.feature_id for item in definitions
    }
    assert all(
        item.required_sources == (FeatureSourceKind.OPTION_CHAIN,)
        for item in DERIVATIVES_FEATURE_DEFINITIONS
    )
    assert all(
        item.category in {FeatureCategory.DERIVATIVES, FeatureCategory.LIQUIDITY}
        for item in DERIVATIVES_FEATURE_DEFINITIONS
    )


def test_deferred_delta50_features_are_not_registered() -> None:
    ids = {item.feature_id for item in builtin_feature_registry().definitions()}
    assert "derivatives.ce_delta50_strike" not in ids
    assert "derivatives.pe_delta50_strike" not in ids


@pytest.mark.parametrize(
    "feature_id",
    (
        "derivatives.expiry_date",
        "derivatives.atm_strike",
        "derivatives.atm_ce_iv",
        "derivatives.atm_ce_delta",
    ),
)
def test_nonwindow_features_reject_parameters_and_intervals(feature_id: str) -> None:
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    context = context_with_option_chain()
    with pytest.raises(FeatureParameterError):
        engine.compute_one(
            context,
            FeatureRequest(feature_id=feature_id, parameters=(("unexpected", 1),)),
        )
    with pytest.raises(FeatureParameterError):
        engine.compute_one(
            context,
            FeatureRequest(feature_id=feature_id, interval="1d"),
        )


def test_window_feature_requires_only_strikes_each_side() -> None:
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    context = context_with_option_chain()
    with pytest.raises(FeatureParameterError, match="requires exactly"):
        engine.compute_one(
            context,
            FeatureRequest(feature_id="derivatives.ce_oi_total"),
        )
    with pytest.raises(FeatureParameterError):
        engine.compute_one(
            context,
            FeatureRequest(
                feature_id="derivatives.ce_oi_total",
                parameters=(("strikes_each_side", 2),),
                interval="1d",
            ),
        )


def test_feature_json_round_trip_preserves_date_value_and_kolkata_offset() -> None:
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context_with_option_chain(), FeatureRequest(feature_id="derivatives.expiry_date")
    )
    payload = result.model_dump(mode="json")
    assert payload["value"] == EXPIRY.isoformat()
    assert payload["as_of"].endswith("+05:30")
    assert type(result).model_validate(payload) == result
    assert json.loads(result.model_dump_json())["value"] == EXPIRY.isoformat()


def test_expiry_mismatch_never_mixes_chains() -> None:
    chain = option_chain().model_copy(update={"expiry": EXPIRY + timedelta(days=7)})
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context_with_option_chain(chain), FeatureRequest(feature_id="derivatives.atm_strike")
    )
    assert result.status is FeatureStatus.FAILED
    assert "explicitly requested expiry" in result.warnings[0]


@pytest.mark.parametrize("mutation", ("side", "strike", "expiry"))
def test_inconsistent_option_identity_fails_safely(mutation: str) -> None:
    chain = option_chain()
    atm = chain.strikes[2]
    assert atm.call is not None
    updates: dict[str, object]
    if mutation == "side":
        updates = {"option_type": OptionType.PE}
    elif mutation == "strike":
        updates = {"strike": 1450.0}
    else:
        updates = {"expiry": EXPIRY + timedelta(days=7)}
    call = atm.call.model_copy(update=updates)
    changed = atm.model_copy(update={"call": call})
    mutated = chain.model_copy(
        update={"strikes": (*chain.strikes[:2], changed, *chain.strikes[3:])}
    )
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context_with_option_chain(mutated),
        FeatureRequest(feature_id="derivatives.atm_ce_ltp"),
    )
    assert result.status is FeatureStatus.FAILED


def test_missing_spread_fields_do_not_cascade_into_oi_or_iv() -> None:
    chain = option_chain()
    atm = chain.strikes[2]
    assert atm.call is not None
    call = atm.call.model_copy(update={"bid": None, "ask": None})
    changed = atm.model_copy(update={"call": call})
    chain = chain.model_copy(
        update={"strikes": (*chain.strikes[:2], changed, *chain.strikes[3:])}
    )
    context = context_with_option_chain(chain)
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    spread = engine.compute_one(
        context,
        FeatureRequest(feature_id="derivatives.atm_ce_bid_ask_spread_percent"),
    )
    iv = engine.compute_one(
        context, FeatureRequest(feature_id="derivatives.atm_ce_iv")
    )
    oi = engine.compute_one(
        context,
        FeatureRequest(
            feature_id="derivatives.ce_oi_total",
            parameters=(("strikes_each_side", 2),),
        ),
    )
    assert spread.status is FeatureStatus.INSUFFICIENT_DATA
    assert iv.status is oi.status is FeatureStatus.AVAILABLE


def test_all_available_numeric_a27_outputs_are_finite() -> None:
    context = context_with_option_chain()
    requests = tuple(
        FeatureRequest(
            feature_id=definition.feature_id,
            parameters=(
                (("strikes_each_side", 2),)
                if definition.metadata.get("window_semantics")
                else ()
            ),
        )
        for definition in DERIVATIVES_FEATURE_DEFINITIONS
    )
    results = DeterministicFeatureEngine(builtin_feature_registry()).compute(
        context, requests
    ).results
    assert all(result.status is FeatureStatus.AVAILABLE for result in results)
    assert all(
        math.isfinite(result.value)
        for result in results
        if isinstance(result.value, (int, float))
    )


def test_a27_modules_have_no_provider_or_orchestration_imports() -> None:
    feature_root = Path("src/tiaf/features")
    files = (feature_root / "derivatives.py", feature_root / "_derivatives_calculation.py")
    forbidden_prefixes = (
        "tiaf.data.providers",
        "tiaf.data.runtime",
        "tiaf.agents",
        "httpx",
        "requests",
        "langgraph",
    )
    for file in files:
        tree = ast.parse(file.read_text(encoding="utf-8"))
        imports = tuple(
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        ) + tuple(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )
        assert not any(
            imported.startswith(prefix)
            for imported in imports
            for prefix in forbidden_prefixes
        )


def test_a27_source_contains_no_engine_recursion_or_strategy_models() -> None:
    source = "\n".join(
        Path(path).read_text(encoding="utf-8")
        for path in (
            "src/tiaf/features/derivatives.py",
            "src/tiaf/features/_derivatives_calculation.py",
        )
    ).casefold()
    forbidden = (
        "featureengine(",
        "deterministicfeatureengine",
        "max pain",
        "gamma exposure",
        "dealer positioning",
        "iron condor",
        "probability of profit",
    )
    assert all(term not in source for term in forbidden)


def test_derivatives_smoke_request_inventory_is_complete_and_deterministic() -> None:
    namespace = runpy.run_path("scripts/feature_engine_smoke.py", run_name="feature_smoke")
    requests = namespace["_derivatives_requests"]()
    assert len(requests) == 39
    assert requests == namespace["_derivatives_requests"]()
    assert {request.feature_id for request in requests} == {
        definition.feature_id for definition in DERIVATIVES_FEATURE_DEFINITIONS
    }
    assert all(
        request.parameters == (("strikes_each_side", 5),)
        for request in requests
        if request.parameters
    )
