"""A2.8 ordered multi-timeframe contracts and factual aggregation tests."""

from datetime import timedelta

import pytest
from pydantic import ValidationError

from tiaf.contracts import DataQuality
from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureRequest,
    FeatureResult,
    FeatureStatus,
    MultiTimeframeContext,
    MultiTimeframeFeatureEngine,
    TimeframeFeatureContext,
    builtin_feature_registry,
    multi_timeframe_context,
    timeframe_feature_context,
)

from ..context._support import NOW
from ._support import context_with_bars


def _timeframe(interval: str, closes: tuple[float, ...]) -> TimeframeFeatureContext:
    context = context_with_bars(
        closes,
        interval=interval,
        symbol="RELIANCE",
        context_id=f"ctx-mtf-{interval}",
        latest_bar_end_at=NOW,
    )
    requests = (
        FeatureRequest(
            feature_id="return.percent", parameters=(("bars", 2),), interval=interval
        ),
        FeatureRequest(
            feature_id="trend.distance_from_ema_percent",
            parameters=(("period", 3),),
            interval=interval,
        ),
        FeatureRequest(
            feature_id="trend.linear_slope",
            parameters=(("bars", 3),),
            interval=interval,
        ),
    )
    bundle = DeterministicFeatureEngine(builtin_feature_registry()).compute(
        context, requests
    )
    return timeframe_feature_context(interval, bundle)


def _context(*, unavailable: bool = False) -> MultiTimeframeContext:
    timeframes: tuple[TimeframeFeatureContext, ...] = (
        _timeframe("1d", (100.0, 105.0, 110.0, 120.0)),
        _timeframe("1h", (100.0, 99.0, 98.0, 97.0)),
        (
            TimeframeFeatureContext(
                interval="15m",
                status=FeatureStatus.INSUFFICIENT_DATA,
                quality=DataQuality.UNAVAILABLE,
                as_of=NOW,
                warnings=("history unavailable",),
            )
            if unavailable
            else _timeframe("15m", (100.0, 101.0, 102.0, 103.0))
        ),
    )
    return multi_timeframe_context("RELIANCE", timeframes, created_at=NOW)


def _result(
    feature_id: str,
    parameter: tuple[str, int] | None = None,
    *,
    unavailable: bool = False,
) -> FeatureResult:
    return MultiTimeframeFeatureEngine().compute_one(
        _context(unavailable=unavailable),
        FeatureRequest(
            feature_id=feature_id,
            parameters=() if parameter is None else (parameter,),
        ),
    )


def test_timeframe_counts_preserve_requested_and_available_facts() -> None:
    assert _result("mtf.requested_timeframe_count").value == 3
    assert _result("mtf.available_timeframe_count").value == 3
    missing = _result("mtf.available_timeframe_count", unavailable=True)
    assert missing.value == 2
    assert missing.status is FeatureStatus.PARTIAL


@pytest.mark.parametrize(
    ("feature_id", "parameter", "expected"),
    (
        ("mtf.positive_return_fraction", ("bars", 2), 2 / 3),
        ("mtf.negative_return_fraction", ("bars", 2), 1 / 3),
        ("mtf.price_above_ema_fraction", ("period", 3), 2 / 3),
        ("mtf.price_below_ema_fraction", ("period", 3), 1 / 3),
        ("mtf.positive_slope_fraction", ("bars", 3), 2 / 3),
        ("mtf.negative_slope_fraction", ("bars", 3), 1 / 3),
        ("mtf.directional_agreement_fraction", ("bars", 2), 2 / 3),
        ("mtf.disagreement_fraction", ("bars", 2), 1 / 3),
    ),
)
def test_multi_timeframe_fractions_use_valid_constituent_features(
    feature_id: str, parameter: tuple[str, int], expected: float
) -> None:
    result = _result(feature_id, parameter)
    assert result.status is FeatureStatus.AVAILABLE
    assert result.value == pytest.approx(expected)
    assert result.metadata["valid_contributor_count"] == 3


def test_unavailable_timeframe_is_excluded_not_neutral() -> None:
    result = _result(
        "mtf.positive_return_fraction", ("bars", 2), unavailable=True
    )
    assert result.value == 0.5
    assert result.status is FeatureStatus.PARTIAL
    assert result.metadata["contributing_intervals"] == ["1d", "1h"]
    assert result.metadata["excluded_intervals"] == ["15m"]


def test_missing_constituent_feature_returns_insufficient() -> None:
    context = context_with_bars((100.0, 101.0, 102.0), interval="1d")
    bundle = DeterministicFeatureEngine(builtin_feature_registry()).compute(
        context,
        (FeatureRequest(feature_id="history.bar_count", interval="1d"),),
    )
    timeframe = timeframe_feature_context("1d", bundle)
    mtf = multi_timeframe_context("RELIANCE", (timeframe,), created_at=NOW)
    result = MultiTimeframeFeatureEngine().compute_one(
        mtf,
        FeatureRequest(
            feature_id="mtf.positive_return_fraction",
            parameters=(("bars", 2),),
        ),
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None


def test_bundle_with_no_usable_results_is_an_unavailable_timeframe() -> None:
    context = context_with_bars((100.0,), interval="1d", context_id="ctx-short")
    bundle = DeterministicFeatureEngine(builtin_feature_registry()).compute(
        context,
        (
            FeatureRequest(
                feature_id="return.percent",
                parameters=(("bars", 20),),
                interval="1d",
            ),
        ),
    )
    timeframe = timeframe_feature_context("1d", bundle)
    assert timeframe.status is FeatureStatus.INSUFFICIENT_DATA
    assert timeframe.feature_bundle == bundle
    mtf = multi_timeframe_context("RELIANCE", (timeframe,), created_at=NOW)
    assert not mtf.complete
    assert mtf.missing_intervals == ("1d",)


def test_request_order_and_bundle_references_round_trip() -> None:
    context = _context()
    assert context.requested_intervals == ("1d", "1h", "15m")
    assert tuple(item.interval for item in context.timeframes) == context.requested_intervals
    assert MultiTimeframeContext.model_validate(context.model_dump(mode="json")) == context
    assert context.model_dump(mode="json")["created_at"].endswith("+05:30")


def test_duplicate_or_reordered_intervals_are_rejected() -> None:
    context = _context()
    with pytest.raises(ValidationError):
        MultiTimeframeContext.model_validate(
            {
                **context.model_dump(mode="python"),
                "requested_intervals": ("1d", "1d", "15m"),
            }
        )
    with pytest.raises(ValidationError, match="preserve"):
        MultiTimeframeContext.model_validate(
            {
                **context.model_dump(mode="python"),
                "timeframes": tuple(reversed(context.timeframes)),
            }
        )


def test_timeframe_bundle_identity_mismatch_is_rejected() -> None:
    timeframe = _timeframe("1d", (100.0, 101.0, 102.0, 103.0))
    with pytest.raises(ValidationError, match="context_id"):
        timeframe.model_copy(update={"context_id": "wrong"}).model_validate(
            timeframe.model_copy(update={"context_id": "wrong"}).model_dump()
        )


def test_timeframe_rejects_a_bundle_from_another_interval() -> None:
    timeframe = _timeframe("1d", (100.0, 101.0, 102.0, 103.0))
    with pytest.raises(ValidationError, match="intervals"):
        TimeframeFeatureContext.model_validate(
            {**timeframe.model_dump(mode="python"), "interval": "1h"}
        )


def test_as_of_is_oldest_contributing_timeframe_time() -> None:
    context = _context()
    first = context.timeframes[0]
    earlier = first.model_copy(update={"as_of": NOW - timedelta(hours=1)})
    changed = context.model_copy(update={"timeframes": (earlier, *context.timeframes[1:])})
    result = MultiTimeframeFeatureEngine().compute_one(
        changed,
        FeatureRequest(
            feature_id="mtf.positive_return_fraction", parameters=(("bars", 2),)
        ),
    )
    assert result.as_of == NOW - timedelta(hours=1)
    contributing_as_of = result.metadata["contributing_as_of"]
    assert isinstance(contributing_as_of, dict)
    assert contributing_as_of["1d"] == (
        NOW - timedelta(hours=1)
    ).isoformat()


def test_context_is_immutable_and_deterministically_identified() -> None:
    first = _context()
    second = _context()
    assert first.context_id == second.context_id
    with pytest.raises(ValidationError):
        first.complete = False


def test_context_collections_accept_lists_and_emit_json_arrays() -> None:
    context = _context()
    payload = context.model_dump(mode="json")
    assert isinstance(payload["requested_intervals"], list)
    assert isinstance(payload["timeframes"], list)
    assert isinstance(payload["missing_intervals"], list)
    rebuilt = MultiTimeframeContext.model_validate(payload)
    assert rebuilt == context
