"""Deterministic policy comparison over one unchanged evidence snapshot."""

from uuid import NAMESPACE_URL, uuid5

from tiaf.baseline import BaselineEngine, BaselinePolicy, ComponentName, OpportunityAssessment

from .errors import ReplayError
from .models import BaselineComparison, ComponentDelta, EvidenceSnapshot
from .snapshot import canonical_json


def _assess(
    snapshot: EvidenceSnapshot,
    policy: BaselinePolicy,
) -> OpportunityAssessment:
    if policy.trade_style is not snapshot.trade_style:
        raise ReplayError("comparison policy style does not match snapshot")
    request = snapshot.decision_request.model_copy(
        update={"policy_version": policy.policy_version}
    )
    request = type(snapshot.decision_request).model_validate(request.model_dump())
    return BaselineEngine((policy,)).assess(request, policy=policy)


def _delta(old: float | None, new: float | None) -> float | None:
    return None if old is None or new is None else new - old


def compare_policies(
    snapshot: EvidenceSnapshot,
    old_policy: BaselinePolicy,
    new_policy: BaselinePolicy,
) -> BaselineComparison:
    """Compare policy outputs without mutating the snapshot or treating either as better."""
    old = _assess(snapshot, old_policy)
    new = _assess(snapshot, new_policy)
    old_scores = {item.component: item.score for item in old.market_state.components}
    new_scores = {item.component: item.score for item in new.market_state.components}
    deltas = tuple(
        ComponentDelta(
            component=component,
            old_score=old_scores[component],
            new_score=new_scores[component],
            delta=_delta(old_scores[component], new_scores[component]),
        )
        for component in ComponentName
    )
    old_reasons = set(old.explanation_codes)
    new_reasons = set(new.explanation_codes)
    identity = canonical_json(
        {
            "snapshot": snapshot.fingerprint,
            "old_policy": old_policy.model_dump(mode="json"),
            "new_policy": new_policy.model_dump(mode="json"),
        }
    )
    return BaselineComparison(
        comparison_id=str(uuid5(NAMESPACE_URL, f"tiaf:policy-comparison:{identity}")),
        snapshot_id=snapshot.snapshot_id,
        evidence_fingerprint=snapshot.fingerprint,
        old_policy_id=old_policy.policy_id,
        old_policy_version=old_policy.policy_version,
        new_policy_id=new_policy.policy_id,
        new_policy_version=new_policy.policy_version,
        old_assessment=old,
        new_assessment=new,
        old_direction=old.market_state.direction,
        new_direction=new.market_state.direction,
        old_opportunity_score=old.opportunity_score,
        new_opportunity_score=new.opportunity_score,
        opportunity_delta=new.opportunity_score - old.opportunity_score,
        old_candidate_class=old.candidate_class,
        new_candidate_class=new.candidate_class,
        component_deltas=deltas,
        added_reasons=tuple(
            code for code in new.explanation_codes if code not in old_reasons
        ),
        removed_reasons=tuple(
            code for code in old.explanation_codes if code not in new_reasons
        ),
    )
