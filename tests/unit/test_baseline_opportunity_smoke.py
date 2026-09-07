"""Read-only A2.9 smoke wiring tests without network access."""

import runpy
from collections.abc import Callable
from typing import Any, cast

import pytest

from tiaf.baseline import CandidateClass, ComponentName, OpportunityAssessment
from tiaf.contracts import TradeStyle

from .context._support import NOW, make_builder


def test_missing_benchmark_reaches_baseline_as_optional_absence() -> None:
    namespace = runpy.run_path("scripts/baseline_opportunity_smoke.py")
    assess = cast(Callable[..., OpportunityAssessment], namespace["_assess_symbol"])
    builder, _, _, _, _ = make_builder()
    assessment = assess(
        builder,
        "RELIANCE",
        None,
        ("1d",),
        10,
        TradeStyle.POSITIONAL,
        NOW,
    )
    relative = next(
        item
        for item in assessment.market_state.components
        if item.component is ComponentName.RELATIVE_STRENGTH
    )
    assert relative.score is None
    assert assessment.candidate_class is CandidateClass.NO_TRADE


def test_cli_requires_horizon_and_preserves_explicit_benchmark_map(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    namespace = runpy.run_path("scripts/baseline_opportunity_smoke.py")
    parse_args = cast(Callable[[], Any], namespace["parse_args"])
    monkeypatch.setattr(
        "sys.argv",
        [
            "baseline-smoke",
            "--symbols",
            "RELIANCE,HDFCBANK",
            "--horizon",
            "POSITIONAL",
            "--benchmark",
            "NIFTY",
            "--benchmark-map",
            "HDFCBANK=BANKNIFTY",
        ],
    )
    args = parse_args()
    assert args.horizon is TradeStyle.POSITIONAL
    assert args.symbols == ("RELIANCE", "HDFCBANK")
    assert args.benchmark == "NIFTY"
    assert args.benchmark_map == {"HDFCBANK": "BANKNIFTY"}
