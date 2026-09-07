"""Pure anti-lookahead calculations for A2.6 prior-range geometry."""

from dataclasses import dataclass

from tiaf.data import OHLCVBar


@dataclass(frozen=True)
class PriorRange:
    """One fixed high/low boundary derived only from prior completed bars."""

    high: float
    low: float

    @property
    def width(self) -> float:
        """Return the nonnegative raw boundary width."""
        return self.high - self.low

    @property
    def midpoint(self) -> float:
        """Return the arithmetic midpoint of both boundaries."""
        return (self.high + self.low) / 2.0


def prior_range(bars: tuple[OHLCVBar, ...]) -> PriorRange:
    """Derive fixed boundaries from an explicit nonempty prior-bar window."""
    if not bars:
        raise ValueError("prior range requires at least one prior bar")
    return PriorRange(
        high=max(bar.high for bar in bars),
        low=min(bar.low for bar in bars),
    )


def midpoint_range_percent(value: PriorRange) -> float:
    """Normalize a prior range by its midpoint and express it as percent."""
    if value.midpoint <= 0:
        raise ValueError("prior range percentage requires a positive midpoint")
    return value.width / value.midpoint * 100.0


def signed_distance_percent(price: float, boundary: float) -> float:
    """Return signed price distance from one positive fixed boundary."""
    if boundary <= 0:
        raise ValueError("boundary percentage distance requires a positive boundary")
    return (price - boundary) / boundary * 100.0
