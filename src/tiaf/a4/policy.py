"""Versioned generic engineering policy for deterministic A4 arbitration."""

from .contracts import A4DeterministicPolicy

_RULE_ORDER = (
    "A2_NO_TRADE",
    "RISK_VETO",
    "REQUIRED_EVIDENCE",
    "INCOMPLETE_REVIEW",
    "MATERIAL_CONFLICT",
    "TIMING_CONDITION",
    "SURVIVING_THESIS",
    "NO_SUPPORTED_THESIS",
)


class UnsupportedA4PolicyError(ValueError):
    """The requested policy identity is not executable by this code version."""


def deterministic_policy(*, version: str = "1.0") -> A4DeterministicPolicy:
    """Return an accepted deterministic policy or its comparison-only successor."""
    if version not in {"1.0", "1.1-comparison"}:
        raise UnsupportedA4PolicyError(f"unsupported deterministic A4 policy version: {version}")
    return A4DeterministicPolicy(
        policy_id="a4-policy:deterministic-baseline",
        policy_version=version,
        challenge_policy_id="a4-challenge-policy:deterministic-baseline",
        challenge_policy_version="1.0",
        arbitration_policy_id="a4-arbitration-policy:deterministic-baseline",
        arbitration_policy_version=version,
        rule_order=_RULE_ORDER,
    )


def require_supported_policy(policy: A4DeterministicPolicy) -> A4DeterministicPolicy:
    expected = deterministic_policy(version=policy.policy_version)
    if policy != expected:
        raise UnsupportedA4PolicyError("A4 policy identity or rules are unsupported")
    return policy

