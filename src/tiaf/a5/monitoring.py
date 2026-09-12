"""Pure construction of bounded monitoring intent; no scheduler or dispatch."""

from datetime import timedelta

from tiaf.planner.digests import digest

from .contracts import (
    A5DeterministicPolicy,
    MonitoringNeed,
    PositionIntelligenceRequest,
    WatchMandate,
)
from .enums import (
    MonitoringLifecycle,
    MonitoringPriority,
    MonitoringTriggerKind,
    PositionFreshness,
    PositionRecommendation,
    PositionSignalKind,
)


def _need(
    request: PositionIntelligenceRequest,
    policy: A5DeterministicPolicy,
    *,
    family: str,
    trigger: MonitoringTriggerKind,
    reference: str,
    priority: MonitoringPriority,
    reason: str,
    material: bool,
    immediate: bool = False,
) -> MonitoringNeed:
    next_due = request.as_of if immediate else request.as_of + timedelta(
        seconds=policy.heartbeat_seconds
    )
    identity = {
        "position": request.snapshot.position_id,
        "snapshot": request.snapshot.snapshot_id,
        "family": family,
        "trigger": trigger,
        "reference": reference,
        "reason": reason,
        "policy": (policy.policy_id, policy.policy_version),
    }
    return MonitoringNeed(
        need_id=f"a5-monitoring-need:{digest(identity)[:24]}",
        position_ref=request.snapshot.position_id,
        objective=request.objective,
        horizon=request.horizon,
        evidence_family=family,
        trigger_kind=trigger,
        trigger_reference=reference,
        priority=priority,
        freshness_intent_seconds=policy.max_snapshot_age_seconds,
        cadence_hint_seconds=policy.heartbeat_seconds,
        next_due_at=next_due,
        reason_code=reason,
        material=material,
        policy_ref=policy.monitoring_policy_ref,
        budget_ref=request.budget_ref,
    )


def build_monitoring_needs(
    request: PositionIntelligenceRequest,
    policy: A5DeterministicPolicy,
    *,
    freshness: PositionFreshness,
    recommendation: PositionRecommendation,
    near_expiry: bool,
    intraday_time_risk: bool,
) -> tuple[MonitoringNeed, ...]:
    if request.mandate_lifecycle is MonitoringLifecycle.INACTIVE:
        return ()

    needs: list[MonitoringNeed] = []
    stale = freshness is not PositionFreshness.CURRENT
    needs.append(
        _need(
            request,
            policy,
            family="POSITION_STATE",
            trigger=MonitoringTriggerKind.POSITION_SNAPSHOT_CHANGE,
            reference=request.snapshot.snapshot_id,
            priority=MonitoringPriority.URGENT if stale else MonitoringPriority.ROUTINE,
            reason="REFRESH_AUTHORITATIVE_POSITION" if stale else "POSITION_HEARTBEAT_HINT",
            material=stale,
            immediate=stale,
        )
    )
    if recommendation in {
        PositionRecommendation.EXIT_RECOMMENDED,
        PositionRecommendation.REDUCE_RISK,
        PositionRecommendation.WAIT_FOR_CONFIRMATION,
    }:
        needs.append(
            _need(
                request,
                policy,
                family="THESIS_STATE",
                trigger=MonitoringTriggerKind.THESIS_INVALIDATION,
                reference=(
                    request.a4_result.result_id
                    if request.a4_result is not None
                    else "a4-result:missing"
                ),
                priority=(
                    MonitoringPriority.URGENT
                    if recommendation is PositionRecommendation.EXIT_RECOMMENDED
                    else MonitoringPriority.ELEVATED
                ),
                reason="REVIEW_THESIS_STATE",
                material=True,
                immediate=recommendation is PositionRecommendation.EXIT_RECOMMENDED,
            )
        )
    if near_expiry or intraday_time_risk:
        needs.append(
            _need(
                request,
                policy,
                family="TIME_RISK",
                trigger=MonitoringTriggerKind.EXPIRY_TIME,
                reference=str(request.snapshot.expiry or request.snapshot.mandatory_exit_at),
                priority=MonitoringPriority.URGENT,
                reason="TIME_RISK_REVIEW_REQUIRED",
                material=True,
                immediate=True,
            )
        )
    for signal in request.signals:
        trigger = {
            PositionSignalKind.THESIS_INVALIDATION: MonitoringTriggerKind.THESIS_INVALIDATION,
            PositionSignalKind.VOLATILITY_RISK: MonitoringTriggerKind.VOLATILITY_DERIVATIVES,
            PositionSignalKind.LIQUIDITY_RISK: MonitoringTriggerKind.VOLATILITY_DERIVATIVES,
            PositionSignalKind.EXPRESSION_UNSUITABLE: (
                MonitoringTriggerKind.VOLATILITY_DERIVATIVES
            ),
        }.get(signal.kind, MonitoringTriggerKind.PRICE_STRUCTURE)
        if signal.kind in {
            PositionSignalKind.THESIS_INVALIDATION,
            PositionSignalKind.MATERIAL_CONFLICT,
            PositionSignalKind.VOLATILITY_RISK,
            PositionSignalKind.LIQUIDITY_RISK,
            PositionSignalKind.EXPRESSION_UNSUITABLE,
        }:
            needs.append(
                _need(
                    request,
                    policy,
                    family="POSITION_EVIDENCE",
                    trigger=trigger,
                    reference=signal.condition_ref or signal.signal_id,
                    priority=MonitoringPriority.ELEVATED,
                    reason=signal.reason_code,
                    material=True,
                )
            )
    unique = {item.need_id: item for item in needs}
    return tuple(unique[key] for key in sorted(unique))


def build_watch_mandate(
    request: PositionIntelligenceRequest,
    policy: A5DeterministicPolicy,
    needs: tuple[MonitoringNeed, ...],
) -> WatchMandate:
    previous = request.previous_result.watch_mandate if request.previous_result else None
    revision = previous.revision + 1 if previous is not None else 1
    payload = {
        "position": request.snapshot.position_id,
        "snapshot": request.snapshot.snapshot_id,
        "revision": revision,
        "lifecycle": request.mandate_lifecycle,
        "needs": tuple(item.need_id for item in needs),
        "policy": (policy.policy_id, policy.policy_version),
    }
    priorities = {item.priority for item in needs}
    priority = (
        MonitoringPriority.URGENT
        if MonitoringPriority.URGENT in priorities
        else MonitoringPriority.ELEVATED
        if MonitoringPriority.ELEVATED in priorities
        else MonitoringPriority.ROUTINE
    )
    return WatchMandate(
        mandate_id=f"a5-watch-mandate:{digest(payload)[:24]}",
        revision=revision,
        predecessor_ref=previous.mandate_id if previous is not None else None,
        position_ref=request.snapshot.position_id,
        instrument=request.snapshot.instrument,
        objective=request.objective,
        horizon=request.horizon,
        lifecycle=request.mandate_lifecycle,
        priority=priority,
        needs=needs,
        analysis_depth_ref="a5-analysis-depth:single-position-baseline",
        policy_ref=policy.monitoring_policy_ref,
        budget_ref=request.budget_ref,
        created_at=request.as_of,
        as_of=request.as_of,
        authority_refs=request.authority_refs,
    )
