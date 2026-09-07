"""Pure shared calculations for deterministic A2.3 trend and structure features."""

import math
from dataclasses import dataclass

from tiaf.data import OHLCVBar


@dataclass(frozen=True)
class LinearRegression:
    """Ordinary least-squares measurements for an equally spaced close path."""

    slope: float
    mean_close: float
    r_squared: float


@dataclass(frozen=True)
class DirectionCounts:
    """Counts for a fixed number of adjacent close comparisons."""

    up: int
    down: int
    flat: int


@dataclass(frozen=True)
class StructureCounts:
    """Counts for adjacent high and low comparisons."""

    higher_high: int
    lower_high: int
    higher_low: int
    lower_low: int


def simple_moving_average(closes: tuple[float, ...], period: int) -> float:
    """Return the arithmetic mean of the latest exact period closes."""
    if period <= 0 or len(closes) < period:
        raise ValueError("SMA requires a positive period and sufficient closes")
    return math.fsum(closes[-period:]) / period


def exponential_moving_average(closes: tuple[float, ...], period: int) -> float:
    """Return canonical EMA seeded by the first period-close SMA."""
    return exponential_moving_average_series(closes, period)[-1]


def exponential_moving_average_series(
    closes: tuple[float, ...], period: int
) -> tuple[float, ...]:
    """Return the canonical EMA series beginning at the seed observation."""
    if period <= 0 or len(closes) < period:
        raise ValueError("EMA requires a positive period and sufficient closes")
    alpha = 2.0 / (period + 1.0)
    value = math.fsum(closes[:period]) / period
    values = [value]
    for close in closes[period:]:
        value = (alpha * close) + ((1.0 - alpha) * value)
        values.append(value)
    return tuple(values)


def linear_regression(closes: tuple[float, ...]) -> LinearRegression:
    """Return OLS slope, mean close, and coefficient of determination."""
    if len(closes) < 2:
        raise ValueError("linear regression requires at least two closes")
    count = len(closes)
    mean_x = (count - 1) / 2.0
    mean_y = math.fsum(closes) / count
    centered_x = tuple(index - mean_x for index in range(count))
    centered_y = tuple(close - mean_y for close in closes)
    sum_xx = math.fsum(value * value for value in centered_x)
    sum_yy = math.fsum(value * value for value in centered_y)
    sum_xy = math.fsum(
        x_value * y_value
        for x_value, y_value in zip(centered_x, centered_y, strict=True)
    )
    slope = sum_xy / sum_xx
    if sum_yy == 0:
        r_squared = 1.0
    else:
        r_squared = min(1.0, max(0.0, (sum_xy * sum_xy) / (sum_xx * sum_yy)))
    return LinearRegression(
        slope=slope,
        mean_close=mean_y,
        r_squared=r_squared,
    )


def directional_efficiency(closes: tuple[float, ...]) -> tuple[float, float]:
    """Return unsigned and signed net displacement divided by path length."""
    if len(closes) < 2:
        raise ValueError("directional efficiency requires at least two closes")
    displacement = closes[-1] - closes[0]
    path_length = math.fsum(
        abs(closes[index] - closes[index - 1])
        for index in range(1, len(closes))
    )
    if path_length == 0:
        return 0.0, 0.0
    signed = displacement / path_length
    return abs(signed), signed


def close_direction_counts(closes: tuple[float, ...]) -> DirectionCounts:
    """Count up, down, and equal adjacent close transitions."""
    if len(closes) < 2:
        raise ValueError("close direction counts require at least two closes")
    up = down = flat = 0
    for previous, current in zip(closes[:-1], closes[1:], strict=True):
        if current > previous:
            up += 1
        elif current < previous:
            down += 1
        else:
            flat += 1
    return DirectionCounts(up=up, down=down, flat=flat)


def consecutive_close_run(
    closes: tuple[float, ...], *, increasing: bool
) -> tuple[int, int]:
    """Return latest consecutive run and number of source bars inspected."""
    if len(closes) < 2:
        raise ValueError("consecutive close run requires at least two closes")
    run = 0
    comparisons = 0
    for index in range(len(closes) - 1, 0, -1):
        comparisons += 1
        moved = closes[index] > closes[index - 1]
        if not increasing:
            moved = closes[index] < closes[index - 1]
        if not moved:
            break
        run += 1
    return run, comparisons + 1


def adjacent_structure_counts(bars: tuple[OHLCVBar, ...]) -> StructureCounts:
    """Count strict adjacent high/low progression; equality counts as neither."""
    if len(bars) < 2:
        raise ValueError("structure counts require at least two bars")
    higher_high = lower_high = higher_low = lower_low = 0
    for previous, current in zip(bars[:-1], bars[1:], strict=True):
        if current.high > previous.high:
            higher_high += 1
        elif current.high < previous.high:
            lower_high += 1
        if current.low > previous.low:
            higher_low += 1
        elif current.low < previous.low:
            lower_low += 1
    return StructureCounts(
        higher_high=higher_high,
        lower_high=lower_high,
        higher_low=higher_low,
        lower_low=lower_low,
    )
