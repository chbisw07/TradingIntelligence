"""Pure shared calculations for A2.5 volume and participation features."""

import math
from dataclasses import dataclass

from tiaf.data import OHLCVBar


class MissingVolumeError(ValueError):
    """A required completed bar has no reported volume."""


class InvalidVolumeError(ValueError):
    """A required completed bar has malformed volume."""


@dataclass(frozen=True)
class ParticipationTotals:
    """Destination-bar volume totals grouped by close transition direction."""

    up: int
    down: int
    flat: int

    @property
    def total(self) -> int:
        """Return all destination-bar volume in the transition window."""
        return self.up + self.down + self.flat


def volume_values(bars: tuple[OHLCVBar, ...]) -> tuple[int, ...]:
    """Extract present, nonnegative integer volumes from exact source bars."""
    values: list[int] = []
    for bar in bars:
        value = bar.volume
        if value is None:
            raise MissingVolumeError("required historical bar volume is unavailable")
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise InvalidVolumeError(
                "historical bar volume must be a nonnegative integer"
            )
        values.append(value)
    return tuple(values)


def arithmetic_mean(values: tuple[int, ...]) -> float:
    """Return an exact-window arithmetic mean using stable summation."""
    if not values:
        raise ValueError("mean requires at least one value")
    return math.fsum(values) / len(values)


def participation_totals(
    bars: tuple[OHLCVBar, ...],
) -> ParticipationTotals:
    """Attach each close transition to its destination bar's volume."""
    if len(bars) < 2:
        raise ValueError("participation totals require at least two bars")
    destination_volumes = volume_values(bars[1:])
    up = down = flat = 0
    for previous, current, volume in zip(
        bars[:-1], bars[1:], destination_volumes, strict=True
    ):
        if current.close > previous.close:
            up += volume
        elif current.close < previous.close:
            down += volume
        else:
            flat += volume
    return ParticipationTotals(up=up, down=down, flat=flat)


def pearson_correlation(
    first: tuple[float, ...], second: tuple[float, ...]
) -> float | None:
    """Return Pearson correlation, or None when either variance is zero."""
    if len(first) != len(second) or len(first) < 2:
        raise ValueError("correlation requires equal series of at least two values")
    first_mean = math.fsum(first) / len(first)
    second_mean = math.fsum(second) / len(second)
    first_centered = tuple(value - first_mean for value in first)
    second_centered = tuple(value - second_mean for value in second)
    first_ss = math.fsum(value * value for value in first_centered)
    second_ss = math.fsum(value * value for value in second_centered)
    if first_ss == 0 or second_ss == 0:
        return None
    covariance = math.fsum(
        first_value * second_value
        for first_value, second_value in zip(
            first_centered, second_centered, strict=True
        )
    )
    value = covariance / math.sqrt(first_ss * second_ss)
    return min(1.0, max(-1.0, value))


def consecutive_volume_run(
    values: tuple[int, ...], *, increasing: bool
) -> tuple[int, int]:
    """Return the latest strict volume run and source observations inspected."""
    if not values:
        raise ValueError("volume run requires at least one value")
    if len(values) == 1:
        return 0, 1
    run = 0
    comparisons = 0
    for index in range(len(values) - 1, 0, -1):
        comparisons += 1
        moved = values[index] > values[index - 1]
        if not increasing:
            moved = values[index] < values[index - 1]
        if not moved:
            break
        run += 1
    return run, comparisons + 1
