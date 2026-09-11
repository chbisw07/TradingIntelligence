"""Deterministic proposition comparison, dispute identity and lineage checks."""

from collections import defaultdict
from typing import TypeVar

from tiaf.planner.digests import digest

from .contracts import (
    AssertionIdentity,
    ComparisonAssessment,
    DisputeEvent,
    DisputeRecord,
    IndependenceAssessment,
    PropositionKey,
    TransformRule,
)
from .enums import (
    AssertionValueKind,
    ComparabilityStatus,
    DisputeCategory,
    DisputeState,
    IndependenceRelation,
)

T = TypeVar("T")


def _pair(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((left, right)))  # type: ignore[return-value]


def _unknown_pair(left: object, right: object) -> bool:
    """Two absent non-applicable optionals can agree; explicit UNKNOWN cannot."""
    return left == "UNKNOWN" or right == "UNKNOWN" or (left is None) != (right is None)


def _unknown(value: object) -> bool:
    return value is None or value == "UNKNOWN"


def _scope_mismatch(left: PropositionKey, right: PropositionKey) -> bool:
    return any(
        not _unknown(a) and not _unknown(b) and a != b
        for a, b in (
            (left.consolidation_basis, right.consolidation_basis),
            (left.segment, right.segment),
            (left.accounting_basis, right.accounting_basis),
        )
    )


def compare_assertions(
    left: AssertionIdentity,
    right: AssertionIdentity,
    *,
    comparison_policy_id: str,
    comparison_policy_version: str,
    transforms: tuple[TransformRule, ...] = (),
) -> ComparisonAssessment:
    """Compare typed meaning only; unknown dimensions never match as wildcards."""
    if right.assertion_id < left.assertion_id:
        left, right = right, left
    a, b = left.proposition, right.proposition
    reasons: list[str] = []
    status = ComparabilityStatus.EXACT
    rule: TransformRule | None = None
    transformed = None

    if a.subject != b.subject:
        status, reasons = ComparabilityStatus.NOT_COMPARABLE, ["SUBJECT_MISMATCH"]
    elif a.predicate_id != b.predicate_id or a.predicate_version != b.predicate_version:
        status, reasons = ComparabilityStatus.NOT_COMPARABLE, ["PREDICATE_MISMATCH"]
    elif _scope_mismatch(a, b):
        status, reasons = ComparabilityStatus.NOT_COMPARABLE, ["SCOPE_MISMATCH"]
    else:
        dimensions = (
            a.qualifiers,
            a.unit,
            a.currency,
            a.reporting_period,
            a.effective_interval,
            a.consolidation_basis,
            a.segment,
            a.accounting_basis,
            a.statement_basis,
            a.adjustment_basis,
            a.measure_type,
            a.measure_role,
            a.horizon,
            a.target_interval,
        )
        peers = (
            b.qualifiers,
            b.unit,
            b.currency,
            b.reporting_period,
            b.effective_interval,
            b.consolidation_basis,
            b.segment,
            b.accounting_basis,
            b.statement_basis,
            b.adjustment_basis,
            b.measure_type,
            b.measure_role,
            b.horizon,
            b.target_interval,
        )
        unknown = any(_unknown_pair(x, y) for x, y in zip(dimensions, peers, strict=True))
        differing = [(x, y) for x, y in zip(dimensions, peers, strict=True) if x != y]
        if unknown:
            status, reasons = ComparabilityStatus.UNDETERMINED, ["UNKNOWN_SEMANTIC_DIMENSION"]
        elif differing:
            direct = tuple(
                item for item in transforms if item.from_unit == a.unit and item.to_unit == b.unit
            )
            reverse = tuple(
                item for item in transforms if item.from_unit == b.unit and item.to_unit == a.unit
            )
            other_equal = dimensions[:1] + dimensions[2:] == peers[:1] + peers[2:]
            if (direct or reverse) and other_equal:
                candidates = direct or reverse
                rule = sorted(candidates, key=lambda item: (item.rule_id, item.version))[0]
                if (
                    left.value.kind is AssertionValueKind.SCALAR
                    and right.value.kind is AssertionValueKind.SCALAR
                    and isinstance(left.value.scalar, (int, float))
                    and not isinstance(left.value.scalar, bool)
                    and isinstance(right.value.scalar, (int, float))
                    and not isinstance(right.value.scalar, bool)
                ):
                    transformed = (
                        (left.value.scalar * rule.multiplier, right.value.scalar)
                        if direct
                        else (left.value.scalar, right.value.scalar * rule.multiplier)
                    )
                    status = ComparabilityStatus.COMPARABLE_WITH_TRANSFORM
                    reasons = ["EXPLICIT_UNIT_TRANSFORM"]
                else:
                    status, reasons = (
                        ComparabilityStatus.UNDETERMINED,
                        ["TRANSFORM_VALUE_UNSUPPORTED"],
                    )
            else:
                status, reasons = (
                    ComparabilityStatus.NOT_COMPARABLE,
                    ["SEMANTIC_DIMENSION_MISMATCH"],
                )
    identity = digest(
        {
            "pair": _pair(left.assertion_id, right.assertion_id),
            "policy": comparison_policy_id,
            "version": comparison_policy_version,
            "status": status,
            "rule": rule.model_dump(mode="json") if rule else None,
        }
    )
    comparison_id = f"comparison:{identity[:24]}"
    return ComparisonAssessment(
        comparison_id=comparison_id,
        assertion_ids=_pair(left.assertion_id, right.assertion_id),
        status=status,
        rule_id=rule.rule_id if rule else None,
        rule_version=rule.version if rule else None,
        transform_multiplier=rule.multiplier if rule else None,
        tolerance=rule.tolerance if rule else None,
        transformed_values=transformed,
        reasons=tuple(reasons or ["EXACT_SEMANTICS"]),
    )


def values_conflict(
    left: AssertionIdentity,
    right: AssertionIdentity,
    comparison: ComparisonAssessment,
) -> bool:
    if comparison.status not in {
        ComparabilityStatus.EXACT,
        ComparabilityStatus.COMPARABLE_WITH_TRANSFORM,
    }:
        return False
    if (
        left.value.kind is AssertionValueKind.MISSING
        or right.value.kind is AssertionValueKind.MISSING
    ):
        return True
    if comparison.transformed_values is not None:
        a, b = comparison.transformed_values
        tolerance = comparison.tolerance or 0.0
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return abs(a - b) > tolerance
    return left.value != right.value


def dispute_category(
    left: AssertionIdentity,
    right: AssertionIdentity,
    comparison: ComparisonAssessment,
) -> DisputeCategory:
    if comparison.status is ComparabilityStatus.UNDETERMINED:
        return DisputeCategory.SEMANTIC_MISMATCH
    if comparison.status is ComparabilityStatus.NOT_COMPARABLE:
        if "SCOPE_MISMATCH" in comparison.reasons:
            return DisputeCategory.SCOPE_MISMATCH
        return DisputeCategory.SEMANTIC_MISMATCH
    if (
        left.proposition.measure_role.value == "FORECAST"
        or right.proposition.measure_role.value == "FORECAST"
    ):
        return DisputeCategory.FORECAST_DISAGREEMENT
    if left.epistemic_role.value != "FACT" or right.epistemic_role.value != "FACT":
        return DisputeCategory.INTERPRETIVE_DISAGREEMENT
    return DisputeCategory.FACTUAL_CONFLICT


def create_dispute(
    left: AssertionIdentity,
    right: AssertionIdentity,
    comparison: ComparisonAssessment,
    *,
    event: DisputeEvent,
) -> DisputeRecord:
    pair = _pair(left.assertion_id, right.assertion_id)
    category = dispute_category(left, right, comparison)
    dispute_id = f"dispute:{digest({'assertions': pair, 'category': category})[:24]}"
    return DisputeRecord(
        dispute_id=dispute_id,
        category=category,
        assertion_ids=pair,
        events=(event,),
    )


def append_dispute_event(
    record: DisputeRecord,
    event: DisputeEvent,
    *,
    successor_dispute_id: str | None = None,
) -> DisputeRecord:
    if record.events[-1].state not in {DisputeState.DETECTED, DisputeState.UNDER_REVIEW}:
        raise ValueError("cannot append after terminal dispute state")
    return record.model_copy(
        update={"events": (*record.events, event), "successor_dispute_id": successor_dispute_id}
    ).__class__.model_validate(
        record.model_dump()
        | {"events": [*record.events, event], "successor_dispute_id": successor_dispute_id}
    )


def validate_independence_lineage(
    assessments: tuple[IndependenceAssessment, ...],
) -> tuple[IndependenceAssessment, ...]:
    """Validate direct derivation edges only; independence is never made transitive."""
    graph: dict[str, set[str]] = defaultdict(set)
    for item in assessments:
        if item.relation is IndependenceRelation.DERIVED_FROM:
            for parent in item.parent_occurrence_ids:
                graph[item.left_occurrence_id].add(parent)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise ValueError("derived occurrence lineage contains a cycle")
        if node in visited:
            return
        visiting.add(node)
        for parent in graph[node]:
            visit(parent)
        visiting.remove(node)
        visited.add(node)

    for node in tuple(graph):
        visit(node)
    return assessments
