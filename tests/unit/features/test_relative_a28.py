"""A2.8 explicit benchmark alignment, arithmetic, quality, and safety tests."""

import math
from datetime import timedelta

import pytest
from pydantic import ValidationError

from tiaf.contracts import DataQuality
from tiaf.features import (
    BenchmarkReference,
    BenchmarkRole,
    FeatureParameterError,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    RelativeStrengthContext,
    RelativeStrengthEngine,
    relative_strength_context,
)
from tiaf.features.volatility import wilder_atr

from ..context._support import NOW
from ._support import context_with_bars


def _contexts(
    subject_closes: tuple[float, ...] = (100.0, 110.0, 121.0),
    benchmark_closes: tuple[float, ...] = (100.0, 105.0, 110.0),
    *,
    subject_quality: DataQuality = DataQuality.GOOD,
    benchmark_quality: DataQuality = DataQuality.GOOD,
) -> RelativeStrengthContext:
    subject = context_with_bars(
        subject_closes,
        symbol="RELIANCE",
        context_id="ctx-relative-subject",
        history_quality=subject_quality,
    )
    benchmark = context_with_bars(
        benchmark_closes,
        symbol="NIFTY",
        context_id="ctx-relative-benchmark",
        history_quality=benchmark_quality,
    )
    return relative_strength_context(
        subject,
        benchmark,
        BenchmarkReference(symbol="NIFTY", role=BenchmarkRole.MARKET, exchange="NSE"),
        interval="1d",
    )


def _result(
    feature_id: str,
    *,
    bars: int = 2,
    context: RelativeStrengthContext | None = None,
    atr_period: int | None = None,
) -> FeatureResult:
    parameters: tuple[tuple[str, int], ...] = (("bars", bars),)
    if atr_period is not None:
        parameters = (("atr_period", atr_period), ("bars", bars))
    return RelativeStrengthEngine().compute_one(
        context or _contexts(),
        FeatureRequest(feature_id=feature_id, parameters=parameters, interval="1d"),
    )


@pytest.mark.parametrize(
    ("feature_id", "expected"),
    (
        ("relative.subject_return_percent", 21.0),
        ("relative.benchmark_return_percent", 10.0),
        ("relative.return_spread_percent", 11.0),
        ("relative.return_ratio", 2.1),
        ("relative.strength_consistency", 1.0),
    ),
)
def test_relative_formulas_are_exact(feature_id: str, expected: float) -> None:
    result = _result(feature_id)
    assert result.status is FeatureStatus.AVAILABLE
    assert result.value == pytest.approx(expected)
    assert result.metadata["benchmark_symbol"] == "NIFTY"
    assert result.metadata["benchmark_role"] == "MARKET"


def test_excess_move_atr_uses_subject_wilder_atr_percent() -> None:
    context = _contexts(
        (100.0, 102.0, 104.0, 106.0),
        (100.0, 101.0, 102.0, 103.0),
    )
    assert context.subject_context.history is not None
    subject_bars = context.subject_context.history.bars
    spread = ((106 / 102 - 1) - (103 / 101 - 1)) * 100
    atr_percent = wilder_atr(subject_bars, 2) / 106 * 100
    assert _result(
        "relative.excess_move_atr", bars=2, atr_period=2, context=context
    ).value == pytest.approx(spread / atr_percent)


def test_zero_benchmark_return_only_invalidates_ratio() -> None:
    context = _contexts(benchmark_closes=(100.0, 100.0, 100.0))
    ratio = _result("relative.return_ratio", context=context)
    spread = _result("relative.return_spread_percent", context=context)
    assert ratio.status is FeatureStatus.FAILED
    assert ratio.value is None
    assert spread.value == pytest.approx(21.0)


def test_zero_subject_atr_only_invalidates_atr_normalization() -> None:
    context = _contexts(
        subject_closes=(100.0, 100.0, 100.0),
        benchmark_closes=(100.0, 99.0, 98.0),
    )
    assert context.subject_context.history is not None
    flat_bars = tuple(
        bar.model_copy(update={"open": 100.0, "high": 100.0, "low": 100.0})
        for bar in context.subject_context.history.bars
    )
    subject = context.subject_context.model_copy(
        update={
            "history": context.subject_context.history.model_copy(
                update={"bars": flat_bars}
            )
        }
    )
    result = _result(
        "relative.excess_move_atr",
        context=context.model_copy(update={"subject_context": subject}),
        atr_period=2,
    )
    assert result.status is FeatureStatus.FAILED
    assert "zero subject ATR" in result.warnings[0]


def test_differing_counts_are_allowed_when_latest_suffix_is_exact() -> None:
    context = _contexts(
        subject_closes=(90.0, 100.0, 110.0, 121.0),
        benchmark_closes=(100.0, 105.0, 110.0),
    )
    assert _result("relative.return_spread_percent", context=context).value == pytest.approx(11.0)


def test_latest_timestamp_mismatch_is_insufficient() -> None:
    context = _contexts()
    benchmark = context.benchmark_context
    assert benchmark is not None and benchmark.history is not None
    latest = benchmark.history.bars[-1]
    shifted = latest.model_copy(
        update={
            "start_at": latest.start_at + timedelta(days=1),
            "end_at": latest.end_at + timedelta(days=1),
        }
    )
    history = benchmark.history.model_copy(
        update={"bars": (*benchmark.history.bars[:-1], shifted)}
    )
    changed = benchmark.model_copy(update={"history": history})
    result = _result(
        "relative.return_spread_percent",
        context=context.model_copy(update={"benchmark_context": changed}),
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert "exact aligned suffix" in result.warnings[0]


def test_short_aligned_history_is_insufficient() -> None:
    result = _result(
        "relative.return_spread_percent",
        bars=5,
        context=_contexts(),
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA


def test_missing_benchmark_context_fails_dependent_result_safely() -> None:
    context = _contexts().model_copy(update={"benchmark_context": None})
    result = _result("relative.return_spread_percent", context=context)
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None


def test_benchmark_must_differ_from_subject() -> None:
    subject = context_with_bars(symbol="RELIANCE")
    with pytest.raises(ValidationError, match="differ"):
        relative_strength_context(
            subject,
            subject,
            BenchmarkReference(symbol="RELIANCE", role=BenchmarkRole.CUSTOM),
            interval="1d",
        )


def test_benchmark_reference_identity_must_match_context() -> None:
    context = _contexts()
    with pytest.raises(ValidationError, match="reference"):
        RelativeStrengthContext.model_validate(
            {
                **context.model_dump(mode="python"),
                "benchmark": BenchmarkReference(
                    symbol="BANKNIFTY", role=BenchmarkRole.SECTOR
                ),
            }
        )
    with pytest.raises(ValidationError, match="exchange"):
        RelativeStrengthContext.model_validate(
            {
                **context.model_dump(mode="python"),
                "benchmark": BenchmarkReference(
                    symbol="NIFTY", role=BenchmarkRole.MARKET, exchange="BSE"
                ),
            }
        )


@pytest.mark.parametrize("quality", (DataQuality.PARTIAL, DataQuality.DEGRADED))
def test_weakest_history_quality_is_preserved(quality: DataQuality) -> None:
    result = _result(
        "relative.return_spread_percent",
        context=_contexts(benchmark_quality=quality),
    )
    assert result.status is FeatureStatus.PARTIAL
    assert result.quality is quality


@pytest.mark.parametrize("bad", (math.nan, math.inf, -1.0))
def test_malformed_ohlc_never_escapes(bad: float) -> None:
    context = _contexts()
    assert context.subject_context.history is not None
    history = context.subject_context.history
    bar = history.bars[-1].model_copy(update={"close": bad})
    changed_history = history.model_copy(update={"bars": (*history.bars[:-1], bar)})
    subject = context.subject_context.model_copy(update={"history": changed_history})
    result = _result(
        "relative.return_spread_percent",
        context=context.model_copy(update={"subject_context": subject}),
    )
    assert result.status is FeatureStatus.FAILED


def test_relative_context_and_result_round_trip_with_kolkata_timestamps() -> None:
    context = _contexts()
    rebuilt = RelativeStrengthContext.model_validate(context.model_dump(mode="json"))
    assert rebuilt == context
    result = _result("relative.return_spread_percent", context=context)
    assert result.model_dump(mode="json")["as_of"].endswith("+05:30")


def test_relative_context_list_input_serializes_collections_as_json_arrays() -> None:
    result = _result("relative.return_spread_percent")
    rebuilt = type(result).model_validate(result.model_dump(mode="json"))
    assert rebuilt == result
    dumped = result.model_dump(mode="json")
    assert isinstance(dumped["source_evidence"], list)
    assert isinstance(dumped["warnings"], list)


@pytest.mark.parametrize("bars", (0, -1, True))
def test_invalid_window_is_rejected(bars: int) -> None:
    with pytest.raises(FeatureParameterError):
        _result("relative.return_spread_percent", bars=bars)


def test_context_identity_is_deterministic_and_immutable() -> None:
    first = _contexts()
    second = _contexts()
    assert first.context_id == second.context_id
    with pytest.raises(ValidationError):
        first.interval = "1h"


def test_normalized_interval_alias_has_same_deterministic_identity() -> None:
    base = _contexts()
    assert base.benchmark_context is not None
    aliased = relative_strength_context(
        base.subject_context,
        base.benchmark_context,
        base.benchmark,
        interval="1day",
    )
    assert aliased.context_id == base.context_id


def test_provenance_names_both_contexts_and_exact_alignment() -> None:
    context = _contexts()
    assert context.benchmark_context is not None
    result = _result("relative.return_spread_percent", context=context)
    assert result.source_context_id == context.context_id
    assert result.source_evidence == ("subject_history", "benchmark_history")
    assert result.metadata["subject_context_id"] == context.subject_context.context_id
    assert result.metadata["benchmark_context_id"] == context.benchmark_context.context_id
    assert result.metadata["alignment_semantics"] == "exact_latest_common_timestamp_suffix"
    assert result.as_of == NOW
