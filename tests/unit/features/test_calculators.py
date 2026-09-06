"""Pure deterministic behavior of the A2.1 built-in calculators."""

from collections.abc import Callable
from typing import Any, cast

import pytest

from tiaf.context import AnalysisContext
from tiaf.contracts import DataQuality
from tiaf.features import (
    DeterministicFeatureEngine,
    FeatureParameterError,
    FeatureRequest,
    FeatureStatus,
    builtin_feature_registry,
)

from ._support import (
    context_with_bars,
    context_with_failed_history,
    context_with_failed_quote,
    context_with_missing_quote,
    context_without_sources,
)


def _engine() -> DeterministicFeatureEngine:
    return DeterministicFeatureEngine(builtin_feature_registry())


def _history_request(
    feature_id: str, *, bars: int | None = None, interval: str = "1d"
) -> FeatureRequest:
    parameters = () if bars is None else (("bars", bars),)
    return FeatureRequest(
        feature_id=feature_id,
        parameters=parameters,
        interval=interval,
    )


def test_current_price_preserves_quote_provenance_and_quality() -> None:
    context = context_with_bars(quote_quality=DataQuality.PARTIAL)
    result = _engine().compute_one(
        context, FeatureRequest(feature_id="price.current")
    )
    descriptor = next(item for item in context.evidence if item.evidence_name == "quote")
    assert result.status is FeatureStatus.PARTIAL
    assert result.value == 1400.0
    assert result.quality is DataQuality.PARTIAL
    assert result.source_context_id == context.context_id
    assert result.subject_symbol == context.subject.symbol
    assert result.source_evidence == ("quote",)
    assert result.source_observed_at == descriptor.source_observed_at
    assert result.as_of == descriptor.source_observed_at


def test_current_price_is_available_from_good_quote() -> None:
    result = _engine().compute_one(
        context_with_bars(), FeatureRequest(feature_id="price.current")
    )
    assert result.status is FeatureStatus.AVAILABLE
    assert result.value == 1400.0
    assert result.quality is DataQuality.GOOD


@pytest.mark.parametrize(
    "context_factory",
    [context_with_missing_quote, context_with_failed_quote],
)
def test_requested_but_unusable_quote_is_insufficient(
    context_factory: Callable[[], AnalysisContext],
) -> None:
    context = context_factory()
    result = _engine().compute_one(
        context, FeatureRequest(feature_id="price.current")
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None
    assert result.quality is DataQuality.UNAVAILABLE


def test_unrequested_sources_are_not_applicable() -> None:
    context = context_without_sources()
    quote = _engine().compute_one(
        context, FeatureRequest(feature_id="price.current")
    )
    history = _engine().compute_one(
        context, _history_request("history.bar_count")
    )
    assert quote.status is FeatureStatus.NOT_APPLICABLE
    assert history.status is FeatureStatus.NOT_APPLICABLE
    assert quote.quality is DataQuality.UNAVAILABLE
    assert history.quality is DataQuality.UNAVAILABLE


def test_failed_history_retains_source_failure_diagnostic() -> None:
    result = _engine().compute_one(
        context_with_failed_history(), _history_request("return.percent", bars=20)
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None
    assert result.warnings == ("source evidence history is FAILED",)


def test_history_count_first_and_last_close() -> None:
    context = context_with_bars((98.0, 103.0, 101.0))
    count = _engine().compute_one(
        context, _history_request("history.bar_count")
    )
    first = _engine().compute_one(
        context, _history_request("history.first_close")
    )
    last = _engine().compute_one(context, _history_request("history.last_close"))
    assert (count.value, count.lookback_bars_used) == (3, 3)
    assert (first.value, first.lookback_bars_used) == (98.0, 1)
    assert (last.value, last.lookback_bars_used) == (101.0, 1)


@pytest.mark.parametrize("bars", [1, 5, 20])
def test_return_windows_use_exact_intervals_back(bars: int) -> None:
    closes = tuple(float(value) for value in range(100, 121))
    context = context_with_bars(closes)
    absolute = _engine().compute_one(
        context, _history_request("return.absolute", bars=bars)
    )
    percent = _engine().compute_one(
        context, _history_request("return.percent", bars=bars)
    )
    base = closes[-1 - bars]
    latest = closes[-1]
    assert absolute.value == pytest.approx(latest - base)
    assert percent.value == pytest.approx(((latest / base) - 1) * 100)
    assert absolute.lookback_bars_used == bars + 1
    assert percent.lookback_bars_used == bars + 1


@pytest.mark.parametrize(
    ("quality", "status"),
    [
        (DataQuality.GOOD, FeatureStatus.AVAILABLE),
        (DataQuality.DEGRADED, FeatureStatus.PARTIAL),
    ],
)
def test_return_never_upgrades_history_quality(
    quality: DataQuality, status: FeatureStatus
) -> None:
    result = _engine().compute_one(
        context_with_bars((100.0, 110.0), history_quality=quality),
        _history_request("return.percent", bars=1),
    )
    assert result.status is status
    assert result.quality is quality


@pytest.mark.parametrize(
    ("closes", "expected"),
    [
        ((100.0, 110.0), 10.0),
        ((100.0, 90.0), -10.0),
        ((100.0, 100.0), 0.0),
    ],
)
def test_percentage_return_handles_positive_negative_and_zero_returns(
    closes: tuple[float, ...], expected: float
) -> None:
    result = _engine().compute_one(
        context_with_bars(closes), _history_request("return.percent", bars=1)
    )
    assert result.status is FeatureStatus.AVAILABLE
    assert result.value == pytest.approx(expected)


def test_returns_do_not_silently_shorten_an_insufficient_window() -> None:
    context = context_with_bars((100.0, 101.0, 102.0, 103.0, 104.0))
    result = _engine().compute_one(
        context, _history_request("return.percent", bars=5)
    )
    assert result.status is FeatureStatus.INSUFFICIENT_DATA
    assert result.value is None
    assert result.lookback_bars_used is None
    assert result.warnings == ("requires 6 history bars; available 5",)


def test_percentage_return_marks_zero_base_as_failed() -> None:
    result = _engine().compute_one(
        context_with_bars((0.0, 10.0)),
        _history_request("return.percent", bars=1),
    )
    assert result.status is FeatureStatus.FAILED
    assert result.value is None
    assert "zero base close" in result.warnings[0]


def test_high_low_range_uses_only_latest_requested_bars() -> None:
    context = context_with_bars(
        (100.0, 105.0, 110.0),
        highs=(500.0, 120.0, 130.0),
        lows=(50.0, 90.0, 100.0),
    )
    result = _engine().compute_one(
        context, _history_request("range.high_low_percent", bars=2)
    )
    assert result.value == pytest.approx(((130.0 - 90.0) / 110.0) * 100)
    assert result.lookback_bars_used == 2


def test_high_low_range_requires_exact_window_and_nonzero_latest_close() -> None:
    insufficient = _engine().compute_one(
        context_with_bars((100.0,)),
        _history_request("range.high_low_percent", bars=2),
    )
    zero_close = _engine().compute_one(
        context_with_bars((0.0,), highs=(1.0,), lows=(0.0,)),
        _history_request("range.high_low_percent", bars=1),
    )
    assert insufficient.status is FeatureStatus.INSUFFICIENT_DATA
    assert insufficient.warnings == ("requires 2 history bars; available 1",)
    assert zero_close.status is FeatureStatus.FAILED
    assert "zero latest close" in zero_close.warnings[0]


@pytest.mark.parametrize("bars", [0, -1, True, 1.5, "5"])
def test_bars_parameter_requires_a_positive_strict_integer(bars: object) -> None:
    request = FeatureRequest(
        feature_id="return.percent",
        parameters=cast(Any, (("bars", bars),)),
        interval="1d",
    )
    with pytest.raises(FeatureParameterError, match="positive integer"):
        _engine().compute_one(context_with_bars(), request)


def test_calculator_rejects_wrong_parameters_and_interval_shape() -> None:
    context = context_with_bars()
    with pytest.raises(FeatureParameterError, match="does not accept parameters"):
        _engine().compute_one(
            context,
            FeatureRequest(feature_id="price.current", parameters=(("bars", 1),)),
        )
    with pytest.raises(FeatureParameterError, match="requires an interval"):
        _engine().compute_one(
            context,
            FeatureRequest(
                feature_id="return.percent", parameters=(("bars", 1),)
            ),
        )
    mismatch = _engine().compute_one(
        context, _history_request("history.last_close", interval="1h")
    )
    assert mismatch.status is FeatureStatus.NOT_APPLICABLE
    assert "does not match" in mismatch.warnings[0]
