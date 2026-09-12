"""Position-snapshot freshness evaluation without calendar claims."""

from .contracts import A5DeterministicPolicy, PositionSnapshot
from .enums import PositionFreshness


def evaluate_freshness(
    snapshot: PositionSnapshot,
    *,
    as_of_seconds: float,
    snapshot_seconds: float,
    policy: A5DeterministicPolicy,
) -> tuple[PositionFreshness, tuple[str, ...]]:
    """Evaluate explicit wall-clock freshness; no exchange calendar is inferred."""
    if snapshot.declared_freshness is PositionFreshness.INVALID:
        return PositionFreshness.INVALID, ("DECLARED_POSITION_SNAPSHOT_INVALID",)
    if snapshot.declared_freshness is PositionFreshness.UNKNOWN:
        return PositionFreshness.UNKNOWN, ("POSITION_SNAPSHOT_FRESHNESS_UNKNOWN",)
    age_seconds = as_of_seconds - snapshot_seconds
    if age_seconds < 0:
        return PositionFreshness.INVALID, ("POSITION_SNAPSHOT_FROM_FUTURE",)
    if snapshot.declared_freshness is PositionFreshness.STALE:
        return PositionFreshness.STALE, ("POSITION_SNAPSHOT_DECLARED_STALE",)
    if age_seconds > policy.max_snapshot_age_seconds:
        return PositionFreshness.STALE, ("POSITION_SNAPSHOT_EXCEEDS_MAX_AGE",)
    return PositionFreshness.CURRENT, ("POSITION_SNAPSHOT_WITHIN_MAX_AGE",)
