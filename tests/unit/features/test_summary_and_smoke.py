"""Factual summaries and user-runnable feature smoke wiring."""

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureRequest,
    builtin_feature_registry,
    summarize_feature_bundle,
)

from ._support import context_with_bars


def _load_smoke() -> dict[str, Any]:
    return runpy.run_path("scripts/feature_engine_smoke.py", run_name="feature_smoke")


def test_summary_is_stable_factual_and_contains_provenance() -> None:
    context = context_with_bars((100.0, 110.0))
    bundle = DeterministicFeatureEngine(builtin_feature_registry()).compute(
        context,
        (
            FeatureRequest(feature_id="price.current"),
            FeatureRequest(
                feature_id="return.percent",
                parameters=(("bars", 1),),
                interval="1d",
            ),
        ),
        bundle_id="bundle-summary",
    )
    first = summarize_feature_bundle(bundle)
    second = summarize_feature_bundle(bundle)
    assert first == second
    assert "RELIANCE FEATURE BUNDLE" in first
    assert "bundle-summary" in first
    assert "ctx-features" in first
    assert "return.percent[bars=1]" in first
    assert "Source : history" in first
    assert "+05:30" in first
    assert all(
        word not in first.casefold()
        for word in ("recommend", "buy signal", "sell signal", "trade now")
    )


def test_smoke_script_help_is_user_runnable(monkeypatch: pytest.MonkeyPatch) -> None:
    namespace = _load_smoke()
    monkeypatch.setattr(sys, "argv", ["feature_engine_smoke.py", "--help"])
    with pytest.raises(SystemExit) as caught:
        namespace["parse_args"]()
    assert caught.value.code == 0


@pytest.mark.parametrize(
    ("extended", "trend", "volume"),
    [
        (False, False, False),
        (True, False, False),
        (False, True, False),
        (True, True, False),
        (False, False, True),
        (True, True, True),
    ],
)
def test_smoke_script_builds_context_then_features_without_live_io(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    extended: bool,
    trend: bool,
    volume: bool,
) -> None:
    namespace = _load_smoke()
    smoke_globals = namespace["main"].__globals__
    context = context_with_bars(tuple(float(value) for value in range(100, 121)))

    class FakeBuilder:
        def __init__(self, *args: object, **kwargs: object) -> None:
            del args, kwargs

        def build(self, *args: object, **kwargs: object) -> object:
            del args, kwargs
            return context

    monkeypatch.setitem(smoke_globals, "AnalysisContextBuilder", FakeBuilder)
    monkeypatch.setitem(smoke_globals, "DhanInstrumentResolver", lambda: object())
    monkeypatch.setitem(smoke_globals, "DhanMarketDataProvider", lambda: object())
    monkeypatch.setitem(smoke_globals, "DataFetchCoordinator", lambda **kwargs: object())
    monkeypatch.setitem(smoke_globals, "ProviderScheduler", lambda policy: object())
    monkeypatch.setitem(smoke_globals, "dhan_rate_policy_registry", lambda: object())
    monkeypatch.setitem(
        smoke_globals,
        "parse_args",
        lambda: SimpleNamespace(
            symbol="RELIANCE",
            history_interval="1d",
            lookback_days=90,
            repeat=False,
            json=False,
            extended=extended,
            trend=trend,
            volume=volume,
            annualization_factor=None,
        ),
    )
    assert namespace["main"]() == 0
    output = capsys.readouterr().out
    assert "RELIANCE FEATURE BUNDLE" in output
    assert "price.current" in output
    assert "return.percent[bars=20]" in output
    if extended:
        assert "volatility.atr[period=14]" in output
        assert "range.move_over_atr[atr_period=14]" in output
    else:
        assert "volatility.atr[period=14]" not in output
    if trend:
        assert "trend.sma[period=20]" in output
        assert "trend.linear_r2[bars=20]" in output
        assert "structure.higher_high_fraction[bars=20]" in output
    else:
        assert "trend.sma[period=20]" not in output
    if volume:
        assert "volume.relative[bars=20]" in output
        assert "participation.signed_volume_balance[bars=20]" in output
    else:
        assert "volume.relative[bars=20]" not in output


def test_smoke_script_is_documented() -> None:
    assert Path("scripts/feature_engine_smoke.py").is_file()
    readme = Path("scripts/README.md").read_text(encoding="utf-8")
    assert "feature_engine_smoke.py" in readme
