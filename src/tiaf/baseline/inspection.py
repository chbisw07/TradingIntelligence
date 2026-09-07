"""Deterministic human inspection of every versioned baseline policy value."""

from .enums import BaselineDirection, RuleRole, TransformKind
from .models import BaselinePolicy, EvidenceRule

_SIGNED = {TransformKind.SIGNED_LINEAR, TransformKind.CENTERED_LINEAR}


def _selector(rule: EvidenceRule) -> str:
    parameters = ",".join(f"{key}={value}" for key, value in rule.selector.parameters)
    output = f".{rule.selector.output_name}" if rule.selector.output_name else ""
    suffix = f"[{parameters}]" if parameters else ""
    return f"{rule.selector.source.value}:{rule.selector.evidence_id}{output}{suffix}"


def _bounds(rule: EvidenceRule) -> str:
    values: list[tuple[str, float]] = []
    for name, value in (
        ("scale", rule.scale),
        ("center", rule.center),
        ("floor", rule.floor),
        ("target", rule.target),
        ("ceiling", rule.ceiling),
    ):
        if value is not None:
            values.append((name, value))
    if rule.transform in {TransformKind.POSITIVE_ROOM, TransformKind.NEGATIVE_ROOM}:
        values.append(("post_boundary_credit", rule.post_boundary_credit))
    values.append(("code_threshold", rule.code_threshold))
    return ",".join(f"{name}={value:g}" for name, value in values)


def _sign_semantics(rule: EvidenceRule) -> str:
    if rule.transform is TransformKind.POSITIVE_ROOM:
        return "positive-side room suitability"
    if rule.transform is TransformKind.NEGATIVE_ROOM:
        return "negative-side room suitability"
    if rule.role is RuleRole.PENALTY:
        return "absolute magnitude penalty"
    if rule.role is RuleRole.SUITABILITY:
        return "unsigned suitability"
    if rule.transform in _SIGNED:
        return "raw sign selects positive/negative side"
    return "positive side" if rule.orientation > 0 else "negative side"


def _direction_capable(rule: EvidenceRule, direction: BaselineDirection) -> bool:
    if rule.role is not RuleRole.DIRECTIONAL:
        return False
    if rule.transform in _SIGNED:
        return True
    return (rule.orientation > 0) is (direction is BaselineDirection.POSITIVE)


def _score_included(rule: EvidenceRule, direction: BaselineDirection) -> bool:
    if rule.transform is TransformKind.POSITIVE_ROOM:
        return direction is BaselineDirection.POSITIVE
    if rule.transform is TransformKind.NEGATIVE_ROOM:
        return direction is BaselineDirection.NEGATIVE
    if rule.role is not RuleRole.DIRECTIONAL or rule.transform in _SIGNED:
        return True
    return (rule.orientation > 0) is (direction is BaselineDirection.POSITIVE)


def _maximums(policy: BaselinePolicy, rule: EvidenceRule) -> str:
    rules = tuple(item for item in policy.evidence_rules if item.component is rule.component)
    component = policy.weight(rule.component)
    direction_values: list[float] = []
    benefit_values: list[float] = []
    for direction in (BaselineDirection.POSITIVE, BaselineDirection.NEGATIVE):
        direction_denominator = sum(
            item.weight for item in rules if _direction_capable(item, direction)
        )
        direction_values.append(
            100.0 * component.direction_weight * rule.weight / direction_denominator
            if direction_denominator and _direction_capable(rule, direction)
            else 0.0
        )
        score_denominator = sum(
            item.weight for item in rules if _score_included(item, direction)
        )
        benefit_values.append(
            100.0 * component.opportunity_weight * rule.weight / score_denominator
            if score_denominator and _score_included(rule, direction)
            else 0.0
        )
    penalty = 0.0
    if rule.role is RuleRole.PENALTY and all(item.role is RuleRole.PENALTY for item in rules):
        penalty = policy.penalties.extension_points * rule.weight / sum(
            item.weight for item in rules
        )
    return (
        f"dir(+/-)={direction_values[0]:.3f}/{direction_values[1]:.3f}; "
        f"benefit(+/-)={benefit_values[0]:.3f}/{benefit_values[1]:.3f}; "
        f"penalty={penalty:.3f}"
    )


def summarize_policy(policy: BaselinePolicy) -> str:
    """Render weights, all rules, thresholds, and penalties without hidden constants."""
    lines = [
        f"{policy.policy_id} POLICY {policy.policy_version}",
        "=" * 88,
        "Effective maxima are full-evidence GOOD-quality points before renormalization.",
        "",
        "COMPONENT WEIGHTS (direction / opportunity / required)",
    ]
    lines.extend(
        f"  {item.component.value:<29} {item.direction_weight:.3f} / "
        f"{item.opportunity_weight:.3f} / {item.required}"
        for item in policy.component_weights
    )
    lines.extend(("", "EVIDENCE RULES (grouped by component)"))
    for component in policy.component_weights:
        lines.append(f"  [{component.component.value}]")
        for rule in policy.evidence_rules:
            if rule.component is not component.component:
                continue
            lines.extend(
                (
                    f"    {rule.rule_id}",
                    f"      selector  : {_selector(rule)}",
                    f"      transform : {rule.transform.value}; {_sign_semantics(rule)}",
                    f"      bounds    : {_bounds(rule)}",
                    f"      weight    : {rule.weight:g}; required={rule.required}; "
                    f"orientation={rule.orientation:+d}",
                    "      codes     : positive="
                    f"{rule.positive_code.value if rule.positive_code else '-'}; negative="
                    f"{rule.negative_code.value if rule.negative_code else '-'}",
                    f"      max points: {_maximums(policy, rule)}",
                )
            )
    direction = policy.direction_thresholds
    classification = policy.classification_thresholds
    penalties = policy.penalties
    lines.extend(
        (
            "",
            "DIRECTION (evaluated in shown order)",
            f"  CONFLICTED: positive >= {direction.conflict_score:g} and negative >= "
            f"{direction.conflict_score:g}",
            f"  NEUTRAL: max(positive, negative) < {direction.minimum_score:g}",
            f"  POSITIVE: margin >= {direction.minimum_margin:g}",
            f"  NEGATIVE: margin <= -{direction.minimum_margin:g}",
            "  CONFLICTED: remaining insufficient-margin cases",
            f"  Component conflict: both sides >= {direction.component_conflict_score:g}",
            "",
            "CLASSIFICATION (after required/stale/direction/alignment/score gates)",
            f"  Gate NO_TRADE: direction NEUTRAL/CONFLICTED, alignment < "
            f"{classification.minimum_alignment:g}, or opportunity < "
            f"{classification.minimum_opportunity_score:g}",
            f"  MATURE_AVOID_CHASE: extension >= {classification.mature_extension:g} "
            f"or room <= {classification.mature_room:g}",
            f"  TOP_MOVER: momentum >= {classification.top_mover_momentum:g} and "
            f"participation >= {classification.top_mover_participation:g}",
            f"  EARLY_OPPORTUNITY: opportunity >= {classification.early_opportunity_score:g}",
            "  NO_TRADE: otherwise",
            "",
            "PENALTIES / QUALITY",
            f"  extension={penalties.extension_points:g}; conflict={penalties.conflict_points:g}; "
            f"quality(partial/degraded/unavailable)={penalties.partial_quality_points:g}/"
            f"{penalties.degraded_quality_points:g}/{penalties.unavailable_quality_points:g}; "
            f"freshness(aging/unknown)={penalties.aging_freshness_points:g}/"
            f"{penalties.unknown_freshness_points:g}",
            "  quality factors: "
            + ", ".join(f"{item.quality.value}={item.factor:g}" for item in policy.quality_factors),
        )
    )
    return "\n".join(lines)
