"""Generic, transparent A5.1 deterministic policy."""

from .contracts import A5DeterministicPolicy
from .errors import UnsupportedA5PolicyError

_RULE_ORDER = (
    "UNSUPPORTED_SHAPE",
    "POSITION_STATE",
    "SNAPSHOT_FRESHNESS",
    "MISSING_A4",
    "EXPIRED_OR_EXIT_WINDOW",
    "THESIS_INVALIDATION",
    "MATERIAL_CONFLICT",
    "THESIS_WEAKENING",
    "FAVORABLE_CONTINUATION",
    "STRUCTURAL_MILESTONE",
    "A4_DISPOSITION",
    "SUPPORTED_MAINTAIN",
)


def deterministic_policy(*, version: str = "1.0") -> A5DeterministicPolicy:
    """Return the accepted baseline or its explicit comparison-only successor."""
    if version == "1.0":
        near_expiry_days = 3
        heartbeat_seconds = 3600
    elif version == "1.1-comparison":
        near_expiry_days = 5
        heartbeat_seconds = 1800
    else:
        raise UnsupportedA5PolicyError(
            f"unsupported deterministic A5 policy version: {version}"
        )
    return A5DeterministicPolicy(
        policy_id="a5-policy:deterministic-single-position",
        policy_version=version,
        monitoring_policy_ref="a5-monitoring-policy:bounded-intent",
        max_snapshot_age_seconds=900,
        near_expiry_days=near_expiry_days,
        heartbeat_seconds=heartbeat_seconds,
        intraday_exit_warning_seconds=1800,
        rule_order=_RULE_ORDER,
    )


def require_supported_policy(policy: A5DeterministicPolicy) -> A5DeterministicPolicy:
    expected = deterministic_policy(version=policy.policy_version)
    if policy != expected:
        raise UnsupportedA5PolicyError("A5 policy identity or rules are unsupported")
    return policy
