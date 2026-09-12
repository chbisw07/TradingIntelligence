"""Deterministic single-position A5.1 evaluation."""

from datetime import datetime
from typing import Any

from pydantic import ValidationError

from tiaf.a4 import A4Disposition, A4Result
from tiaf.a4 import result_semantic_payload as a4_result_semantic_payload
from tiaf.planner.digests import digest

from ._validation import validate_no_secrets
from .contracts import (
    A5DeterministicPolicy,
    A5RunRecord,
    A5Usage,
    PositionIntelligenceRequest,
    PositionIntelligenceResult,
    ProtectionIntent,
)
from .enums import (
    A5ExecutionStatus,
    A5FailureCode,
    OperationalPositionState,
    PositionFreshness,
    PositionRecommendation,
    PositionRiskPosture,
    PositionShape,
    PositionSignalKind,
    ProtectionIntentKind,
    RemainingOpportunity,
    ThesisHealth,
)
from .errors import A5InputIntegrityError, A5OutputIntegrityError
from .freshness import evaluate_freshness
from .monitoring import build_monitoring_needs, build_watch_mandate
from .policy import deterministic_policy, require_supported_policy


def result_semantic_payload(result: PositionIntelligenceResult) -> dict[str, Any]:
    return result.model_dump(
        mode="json",
        exclude={
            "result_id": True,
            "run_id": True,
            "request_id": True,
            "replay_identity": True,
            "semantic_fingerprint": True,
        },
    )


def _validate_a4_result(result: A4Result) -> A4Result:
    expected = digest(a4_result_semantic_payload(result))
    if result.semantic_fingerprint != expected:
        raise A5InputIntegrityError("linked A4 result semantic fingerprint mismatch")
    if result.result_id != f"a4-result:{expected[:24]}":
        raise A5InputIntegrityError("linked A4 result identity mismatch")
    return result


def validate_request(
    request: PositionIntelligenceRequest,
    policy: A5DeterministicPolicy,
) -> PositionIntelligenceRequest:
    try:
        request = PositionIntelligenceRequest.model_validate_json(request.model_dump_json())
        policy = require_supported_policy(policy)
        if (request.policy_id, request.policy_version) != (
            policy.policy_id,
            policy.policy_version,
        ):
            raise A5InputIntegrityError("request and executable A5 policy mismatch")
        if request.monitoring_policy_ref != policy.monitoring_policy_ref:
            raise A5InputIntegrityError("request monitoring policy mismatch")
        for value in (request.a4_result, request.successor_a4_result):
            if value is not None:
                _validate_a4_result(value)
                if value.primary_thesis.subject != request.snapshot.underlying:
                    raise A5InputIntegrityError(
                        "position underlying and linked A4 subject mismatch"
                    )
        if request.a4_result is None and request.successor_a4_result is not None:
            raise A5InputIntegrityError("A4 successor requires an original A4 result")
        if request.a4_result is not None and request.successor_a4_result is not None:
            original = request.a4_result
            successor = request.successor_a4_result
            if (
                successor.original_a2_assessment_ref != original.original_a2_assessment_ref
                or successor.original_a3_package_ref != original.original_a3_package_ref
            ):
                raise A5InputIntegrityError("A4 successor lineage is not comparable")
        invalidation_ids = {
            item.condition_id
            for value in (request.a4_result, request.successor_a4_result)
            if value is not None
            for item in value.invalidation_conditions
        }
        for signal in request.signals:
            if (
                signal.kind is PositionSignalKind.THESIS_INVALIDATION
                and signal.condition_ref not in invalidation_ids
            ):
                raise A5InputIntegrityError(
                    "thesis-invalidation signal does not reference linked A4 condition"
                )
        if request.previous_result is not None:
            validate_result(request.previous_result)
        return request
    except (TypeError, ValueError, ValidationError) as exc:
        if isinstance(exc, A5InputIntegrityError):
            raise
        raise A5InputIntegrityError(str(exc)) from exc


def _thesis_health(request: PositionIntelligenceRequest) -> ThesisHealth:
    kinds = {item.kind for item in request.signals}
    if PositionSignalKind.THESIS_INVALIDATION in kinds:
        return ThesisHealth.INVALIDATED
    if PositionSignalKind.THESIS_WEAKENING in kinds:
        return ThesisHealth.WEAKENED
    successor = request.successor_a4_result
    original = request.a4_result
    if successor is not None and original is not None:
        if successor.disposition is A4Disposition.SUPPORTIVE and (
            original.disposition is not A4Disposition.SUPPORTIVE
        ):
            return ThesisHealth.STRENGTHENED
        if successor.disposition in {
            A4Disposition.AVOID,
            A4Disposition.NO_TRADE,
            A4Disposition.CONFLICTED,
            A4Disposition.WAIT,
            A4Disposition.ABSTAIN,
            A4Disposition.INSUFFICIENT_EVIDENCE,
        } and successor.disposition is not original.disposition:
            return ThesisHealth.WEAKENED
    if original is not None and original.disposition is A4Disposition.SUPPORTIVE:
        return ThesisHealth.INTACT
    return ThesisHealth.UNDETERMINED


def _remaining_opportunity(kinds: set[PositionSignalKind]) -> RemainingOpportunity:
    mapping = (
        (PositionSignalKind.REMAINING_ROOM_EXHAUSTED, RemainingOpportunity.EXHAUSTED),
        (PositionSignalKind.REMAINING_ROOM_LIMITED, RemainingOpportunity.LIMITED),
        (PositionSignalKind.REMAINING_ROOM_MODERATE, RemainingOpportunity.MODERATE),
        (PositionSignalKind.REMAINING_ROOM_STRONG, RemainingOpportunity.STRONG),
    )
    for kind, value in mapping:
        if kind in kinds:
            return value
    return RemainingOpportunity.UNKNOWN


def _changed_input_refs(request: PositionIntelligenceRequest) -> tuple[str, ...]:
    previous = request.previous_result
    if previous is None:
        return ()
    changed: list[str] = []
    if previous.snapshot_id != request.snapshot.snapshot_id:
        changed.append(request.snapshot.snapshot_id)
    if previous.as_of != request.as_of:
        changed.append(f"as_of:{request.as_of.isoformat()}")
    current_a4 = request.successor_a4_result or request.a4_result
    if current_a4 is not None and previous.linked_a4_fingerprint != current_a4.semantic_fingerprint:
        changed.append(current_a4.result_id)
    if (previous.policy_id, previous.policy_version) != (
        request.policy_id,
        request.policy_version,
    ):
        changed.append(f"{request.policy_id}@{request.policy_version}")
    if request.signals:
        changed.extend(item.signal_id for item in request.signals)
    return tuple(dict.fromkeys(changed)) or ("NO_SEMANTIC_INPUT_CHANGE",)


def _decision(
    request: PositionIntelligenceRequest,
    *,
    freshness: PositionFreshness,
    expired: bool,
    intraday_exit_reached: bool,
    near_expiry: bool,
    intraday_time_risk: bool,
) -> tuple[
    A5ExecutionStatus,
    PositionRiskPosture,
    ThesisHealth,
    PositionRecommendation,
    tuple[A5FailureCode, ...],
    tuple[str, ...],
]:
    kinds = {item.kind for item in request.signals}
    health = _thesis_health(request)
    current_a4 = request.successor_a4_result or request.a4_result
    if request.snapshot.shape is PositionShape.MULTI_LEG:
        return (
            A5ExecutionStatus.UNSUPPORTED,
            PositionRiskPosture.UNDETERMINED,
            ThesisHealth.UNDETERMINED,
            PositionRecommendation.INSUFFICIENT_EVIDENCE,
            (A5FailureCode.UNSUPPORTED_SHAPE,),
            ("MULTI_LEG_POSITION_UNSUPPORTED_A5_1",),
        )
    if request.snapshot.operational_state is not OperationalPositionState.OPEN:
        return (
            A5ExecutionStatus.PARTIAL,
            PositionRiskPosture.UNDETERMINED,
            ThesisHealth.UNDETERMINED,
            PositionRecommendation.ABSTAIN,
            (A5FailureCode.CLOSED_OR_UNKNOWN_POSITION,),
            ("POSITION_NOT_AUTHORITATIVELY_OPEN",),
        )
    if freshness is not PositionFreshness.CURRENT:
        code = {
            PositionFreshness.STALE: A5FailureCode.STALE_SNAPSHOT,
            PositionFreshness.UNKNOWN: A5FailureCode.UNKNOWN_FRESHNESS,
            PositionFreshness.INVALID: A5FailureCode.INVALID_SNAPSHOT,
        }[freshness]
        return (
            A5ExecutionStatus.PARTIAL,
            PositionRiskPosture.UNDETERMINED,
            ThesisHealth.UNDETERMINED,
            PositionRecommendation.ABSTAIN,
            (code,),
            ("CURRENT_POSITION_TRUTH_REQUIRED",),
        )
    if request.a4_result is None:
        return (
            A5ExecutionStatus.PARTIAL,
            PositionRiskPosture.UNDETERMINED,
            ThesisHealth.UNDETERMINED,
            PositionRecommendation.INSUFFICIENT_EVIDENCE,
            (A5FailureCode.MISSING_A4_RESULT,),
            ("CURRENT_ACCEPTED_A4_RESULT_REQUIRED",),
        )
    if expired or intraday_exit_reached:
        return (
            A5ExecutionStatus.PARTIAL if expired else A5ExecutionStatus.COMPLETE,
            PositionRiskPosture.UNDETERMINED,
            health,
            PositionRecommendation.EXIT_RECOMMENDED,
            (A5FailureCode.EXPIRED_INSTRUMENT,) if expired else (),
            ("INSTRUMENT_EXPIRED" if expired else "MANDATORY_EXIT_WINDOW_REACHED",),
        )
    if health is ThesisHealth.INVALIDATED:
        return (
            A5ExecutionStatus.COMPLETE,
            PositionRiskPosture.UNDETERMINED,
            health,
            PositionRecommendation.EXIT_RECOMMENDED,
            (),
            ("A4_INVALIDATION_CONDITION_SATISFIED",),
        )
    if PositionSignalKind.MATERIAL_CONFLICT in kinds or (
        current_a4 is not None and current_a4.disposition is A4Disposition.CONFLICTED
    ):
        return (
            A5ExecutionStatus.COMPLETE,
            PositionRiskPosture.CAPITAL_AT_RISK,
            health,
            PositionRecommendation.WAIT_FOR_CONFIRMATION,
            (),
            ("MATERIAL_POSITION_THESIS_CONFLICT",),
        )
    if health is ThesisHealth.WEAKENED or kinds & {
        PositionSignalKind.LIQUIDITY_RISK,
        PositionSignalKind.VOLATILITY_RISK,
        PositionSignalKind.EXPRESSION_UNSUITABLE,
    }:
        return (
            A5ExecutionStatus.COMPLETE,
            PositionRiskPosture.CAPITAL_AT_RISK,
            health,
            PositionRecommendation.REDUCE_RISK,
            (),
            ("POSITION_RISK_MATERIALLY_INCREASED",),
        )
    if PositionSignalKind.FAVORABLE_CONTINUATION in kinds:
        return (
            A5ExecutionStatus.COMPLETE,
            PositionRiskPosture.PROFIT_PROTECTION_ACTIVE,
            health,
            PositionRecommendation.TRAIL_PROTECTION,
            (),
            ("FAVORABLE_CONTINUATION_WITH_PROFIT_PROTECTION",),
        )
    if kinds & {
        PositionSignalKind.STRUCTURAL_MILESTONE,
        PositionSignalKind.PROTECTION_CONFIRMED,
    }:
        return (
            A5ExecutionStatus.COMPLETE,
            PositionRiskPosture.RISK_REDUCED,
            health,
            PositionRecommendation.PROTECT,
            (),
            ("CITED_STRUCTURAL_PROTECTION_MILESTONE",),
        )
    disposition = request.a4_result.disposition
    if disposition in {A4Disposition.AVOID, A4Disposition.NO_TRADE}:
        return (
            A5ExecutionStatus.COMPLETE,
            PositionRiskPosture.CAPITAL_AT_RISK,
            health,
            PositionRecommendation.EXIT_RECOMMENDED,
            (),
            ("LINKED_A4_DISPOSITION_OPPOSES_CONTINUED_POSITION",),
        )
    if disposition in {A4Disposition.CONFLICTED, A4Disposition.WAIT} or near_expiry or (
        intraday_time_risk
    ):
        return (
            A5ExecutionStatus.COMPLETE,
            PositionRiskPosture.CAPITAL_AT_RISK,
            health,
            PositionRecommendation.WATCH_CLOSELY,
            (),
            ("HEIGHTENED_REVIEW_REQUIRED",),
        )
    if disposition in {A4Disposition.ABSTAIN, A4Disposition.INSUFFICIENT_EVIDENCE}:
        return (
            A5ExecutionStatus.PARTIAL,
            PositionRiskPosture.UNDETERMINED,
            health,
            PositionRecommendation.INSUFFICIENT_EVIDENCE,
            (A5FailureCode.INSUFFICIENT_EVIDENCE,),
            ("LINKED_A4_EVIDENCE_INSUFFICIENT",),
        )
    return (
        A5ExecutionStatus.COMPLETE,
        PositionRiskPosture.CAPITAL_AT_RISK,
        health,
        PositionRecommendation.MAINTAIN,
        (),
        ("CURRENT_POSITION_CONSISTENT_WITH_SUPPORTED_A4_THESIS",),
    )


def _protection(
    recommendation: PositionRecommendation,
    request: PositionIntelligenceRequest,
    reasons: tuple[str, ...],
) -> ProtectionIntent:
    kind = {
        PositionRecommendation.MAINTAIN: ProtectionIntentKind.NO_PROTECTION_CHANGE,
        PositionRecommendation.WATCH_CLOSELY: ProtectionIntentKind.HOLD_CURRENT_PROTECTION,
        PositionRecommendation.PROTECT: ProtectionIntentKind.TIGHTEN_PROTECTION,
        PositionRecommendation.REDUCE_RISK: ProtectionIntentKind.TIGHTEN_PROTECTION,
        PositionRecommendation.TRAIL_PROTECTION: ProtectionIntentKind.TRAIL_STRUCTURALLY,
        PositionRecommendation.EXIT_RECOMMENDED: ProtectionIntentKind.EXIT_IF_INVALIDATED,
        PositionRecommendation.WAIT_FOR_CONFIRMATION: (
            ProtectionIntentKind.HOLD_CURRENT_PROTECTION
        ),
        PositionRecommendation.ABSTAIN: ProtectionIntentKind.UNDETERMINED,
        PositionRecommendation.INSUFFICIENT_EVIDENCE: ProtectionIntentKind.UNDETERMINED,
    }[recommendation]
    if any(item.kind is PositionSignalKind.EXPRESSION_UNSUITABLE for item in request.signals):
        kind = ProtectionIntentKind.EXPRESSION_REFRESH_REQUIRED
    levels = list(request.snapshot.supplied_levels)
    levels.extend(
        item.reference_level
        for item in request.signals
        if item.reference_level is not None
    )
    unique = {item.level_id: item for item in levels}
    return ProtectionIntent(
        kind=kind,
        reference_levels=tuple(unique[key] for key in sorted(unique)),
        reason_codes=reasons,
    )


def _evidence(request: PositionIntelligenceRequest) -> tuple[str, ...]:
    refs: list[str] = []
    if request.a4_result is not None:
        refs.extend((request.a4_result.result_id, request.a4_result.primary_thesis.thesis_id))
    if request.successor_a4_result is not None:
        refs.extend(
            (
                request.successor_a4_result.result_id,
                request.successor_a4_result.primary_thesis.thesis_id,
            )
        )
    refs.extend(ref for signal in request.signals for ref in signal.evidence_refs)
    refs.extend(
        ref for level in request.snapshot.supplied_levels for ref in level.evidence_refs
    )
    return tuple(dict.fromkeys(refs))


def _contradictions(request: PositionIntelligenceRequest) -> tuple[str, ...]:
    refs: list[str] = []
    for result in (request.a4_result, request.successor_a4_result):
        if result is not None and result.counter_thesis is not None:
            refs.append(result.counter_thesis.thesis_id)
        if result is not None:
            refs.extend(item.finding_id for item in result.challenge_findings)
    refs.extend(
        item.signal_id
        for item in request.signals
        if item.kind is PositionSignalKind.MATERIAL_CONFLICT
    )
    return tuple(dict.fromkeys(refs))


def _gaps(
    request: PositionIntelligenceRequest,
    failures: tuple[A5FailureCode, ...],
) -> tuple[str, ...]:
    gaps: list[str] = [item.value for item in failures]
    for result in (request.a4_result, request.successor_a4_result):
        if result is not None:
            gaps.extend(item.resolution_requirement for item in result.residual_uncertainties)
    return tuple(dict.fromkeys(gaps))


def evaluate_position(
    request: PositionIntelligenceRequest,
    *,
    policy: A5DeterministicPolicy | None = None,
    evaluated_at: datetime | None = None,
) -> A5RunRecord:
    policy = require_supported_policy(policy or deterministic_policy())
    request = validate_request(request, policy)
    freshness, freshness_reasons = evaluate_freshness(
        request.snapshot,
        as_of_seconds=request.as_of.timestamp(),
        snapshot_seconds=request.snapshot.snapshot_at.timestamp(),
        policy=policy,
    )
    expiry = request.snapshot.expiry
    expiry_days = (expiry - request.as_of.date()).days if expiry is not None else None
    expired = expiry_days is not None and expiry_days < 0
    near_expiry = expiry_days is not None and 0 <= expiry_days <= policy.near_expiry_days
    mandatory_exit = request.snapshot.mandatory_exit_at
    intraday_exit_reached = mandatory_exit is not None and request.as_of >= mandatory_exit
    intraday_time_risk = mandatory_exit is not None and (
        0 <= (mandatory_exit - request.as_of).total_seconds()
        <= policy.intraday_exit_warning_seconds
    )
    status, posture, health, recommendation, failures, reasons = _decision(
        request,
        freshness=freshness,
        expired=expired,
        intraday_exit_reached=intraday_exit_reached,
        near_expiry=near_expiry,
        intraday_time_risk=intraday_time_risk,
    )
    monitoring_needs = build_monitoring_needs(
        request,
        policy,
        freshness=freshness,
        recommendation=recommendation,
        near_expiry=near_expiry,
        intraday_time_risk=intraday_time_risk or intraday_exit_reached,
    )
    watch_mandate = build_watch_mandate(request, policy, monitoring_needs)
    current_a4 = request.successor_a4_result or request.a4_result
    linked_theses = (
        tuple(current_a4.surviving_thesis_refs) or (current_a4.primary_thesis.thesis_id,)
        if current_a4 is not None
        else ()
    )
    invalidation_refs = (
        tuple(item.condition_id for item in current_a4.invalidation_conditions)
        if current_a4 is not None
        else ()
    )
    logical_identity = {
        "request": request.model_dump(mode="json"),
        "policy": policy.model_dump(mode="json"),
    }
    run_id = f"a5-run:{digest(logical_identity)[:24]}"
    provisional = PositionIntelligenceResult(
        result_id="a5-result:pending",
        run_id=run_id,
        request_id=request.request_id,
        position_id=request.snapshot.position_id,
        snapshot_id=request.snapshot.snapshot_id,
        snapshot_at=request.snapshot.snapshot_at,
        as_of=request.as_of,
        effective_freshness=freshness,
        freshness_reasons=freshness_reasons,
        linked_a4_result_id=current_a4.result_id if current_a4 is not None else None,
        linked_a4_fingerprint=(
            current_a4.semantic_fingerprint if current_a4 is not None else None
        ),
        linked_thesis_refs=linked_theses,
        previous_result_ref=(
            request.previous_result.result_id if request.previous_result is not None else None
        ),
        previous_posture=(
            request.previous_result.posture if request.previous_result is not None else None
        ),
        successor_reason=request.successor_reason,
        changed_input_refs=_changed_input_refs(request),
        status=status,
        posture=posture,
        thesis_health=health,
        recommendation=recommendation,
        protection_intent=_protection(recommendation, request, reasons),
        remaining_opportunity=_remaining_opportunity(
            {item.kind for item in request.signals}
        ),
        monitoring_needs=monitoring_needs,
        watch_mandate=watch_mandate,
        evidence_refs=_evidence(request),
        contradictions=_contradictions(request),
        gaps=_gaps(request, failures),
        reason_codes=reasons,
        invalidation_condition_refs=invalidation_refs,
        failure_codes=failures,
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
        usage=A5Usage(
            parent_usage_refs=(
                (current_a4.result_id,) if current_a4 is not None else ()
            )
        ),
        replay_identity="a5-replay-key:pending",
        semantic_fingerprint="0" * 64,
    )
    semantic_fingerprint = digest(result_semantic_payload(provisional))
    result = provisional.model_copy(
        update={
            "result_id": f"a5-result:{semantic_fingerprint[:24]}",
            "replay_identity": f"a5-replay-key:{semantic_fingerprint[:24]}",
            "semantic_fingerprint": semantic_fingerprint,
        }
    )
    validate_result(result)
    when = evaluated_at or request.as_of
    record_payload = {
        "run_id": run_id,
        "request": request.model_dump(mode="json"),
        "policy": policy.model_dump(mode="json"),
        "result": result.model_dump(mode="json"),
        "evaluated_at": when.isoformat(),
    }
    record = A5RunRecord(
        run_id=run_id,
        request=request,
        policy=policy,
        result=result,
        evaluated_at=when,
        fingerprint=digest(record_payload),
    )
    return validate_run(record)


def validate_result(result: PositionIntelligenceResult) -> PositionIntelligenceResult:
    try:
        result = PositionIntelligenceResult.model_validate_json(result.model_dump_json())
        expected = digest(result_semantic_payload(result))
        if result.semantic_fingerprint != expected:
            raise A5OutputIntegrityError("A5 result semantic fingerprint mismatch")
        if result.result_id != f"a5-result:{expected[:24]}":
            raise A5OutputIntegrityError("A5 result identity mismatch")
        if result.replay_identity != f"a5-replay-key:{expected[:24]}":
            raise A5OutputIntegrityError("A5 replay identity mismatch")
        if result.usage.provider_calls or result.usage.model_calls:
            raise A5OutputIntegrityError("deterministic A5 result cannot use live calls")
        validate_no_secrets(result.model_dump(mode="json"))
        return result
    except (TypeError, ValueError, ValidationError) as exc:
        if isinstance(exc, A5OutputIntegrityError):
            raise
        raise A5OutputIntegrityError(str(exc)) from exc


def validate_run(record: A5RunRecord) -> A5RunRecord:
    try:
        record = A5RunRecord.model_validate_json(record.model_dump_json())
        validate_request(record.request, record.policy)
        validate_result(record.result)
        logical_identity = {
            "request": record.request.model_dump(mode="json"),
            "policy": record.policy.model_dump(mode="json"),
        }
        expected_run_id = f"a5-run:{digest(logical_identity)[:24]}"
        if record.run_id != expected_run_id:
            raise A5OutputIntegrityError("A5 logical run identity mismatch")
        if record.run_id != record.result.run_id:
            raise A5OutputIntegrityError("A5 run/result identity mismatch")
        if record.request.request_id != record.result.request_id:
            raise A5OutputIntegrityError("A5 request/result identity mismatch")
        request = record.request
        result = record.result
        if (
            result.position_id != request.snapshot.position_id
            or result.snapshot_id != request.snapshot.snapshot_id
            or result.snapshot_at != request.snapshot.snapshot_at
            or result.as_of != request.as_of
        ):
            raise A5OutputIntegrityError("A5 result position snapshot link mismatch")
        current_a4 = request.successor_a4_result or request.a4_result
        if current_a4 is None:
            if (
                result.linked_a4_result_id is not None
                or result.linked_a4_fingerprint is not None
            ):
                raise A5OutputIntegrityError("A5 result has unexpected A4 link")
        elif (
            result.linked_a4_result_id != current_a4.result_id
            or result.linked_a4_fingerprint != current_a4.semantic_fingerprint
        ):
            raise A5OutputIntegrityError("A5 result A4 link mismatch")
        allowed_theses = set()
        allowed_invalidations = set()
        if current_a4 is not None:
            allowed_theses = {
                current_a4.primary_thesis.thesis_id,
                *current_a4.surviving_thesis_refs,
            }
            if current_a4.counter_thesis is not None:
                allowed_theses.add(current_a4.counter_thesis.thesis_id)
            allowed_invalidations = {
                item.condition_id for item in current_a4.invalidation_conditions
            }
        if not set(result.linked_thesis_refs) <= allowed_theses:
            raise A5OutputIntegrityError("A5 result contains unresolved thesis reference")
        if set(result.invalidation_condition_refs) != allowed_invalidations:
            raise A5OutputIntegrityError("A5 result invalidation links differ from A4")
        allowed_evidence = set(_evidence(request))
        if not set(result.evidence_refs) <= allowed_evidence:
            raise A5OutputIntegrityError("A5 result contains uncited evidence reference")
        allowed_contradictions = set(_contradictions(request))
        if not set(result.contradictions) <= allowed_contradictions:
            raise A5OutputIntegrityError("A5 result contains unresolved contradiction reference")
        if result.previous_result_ref != (
            request.previous_result.result_id if request.previous_result is not None else None
        ):
            raise A5OutputIntegrityError("A5 result predecessor link mismatch")
        if result.watch_mandate.instrument != request.snapshot.instrument:
            raise A5OutputIntegrityError("A5 watch mandate instrument mismatch")
        supplied_level_ids = {
            item.level_id for item in request.snapshot.supplied_levels
        } | {
            item.reference_level.level_id
            for item in request.signals
            if item.reference_level is not None
        }
        if not {
            item.level_id for item in result.protection_intent.reference_levels
        } <= supplied_level_ids:
            raise A5OutputIntegrityError("A5 result contains invented reference level")
        if (result.policy_id, result.policy_version) != (
            record.policy.policy_id,
            record.policy.policy_version,
        ):
            raise A5OutputIntegrityError("A5 result policy link mismatch")
        payload = {
            "run_id": record.run_id,
            "request": record.request.model_dump(mode="json"),
            "policy": record.policy.model_dump(mode="json"),
            "result": record.result.model_dump(mode="json"),
            "evaluated_at": record.evaluated_at.isoformat(),
        }
        if record.fingerprint != digest(payload):
            raise A5OutputIntegrityError("A5 run fingerprint mismatch")
        return record
    except (TypeError, ValueError, ValidationError) as exc:
        if isinstance(exc, (A5InputIntegrityError, A5OutputIntegrityError)):
            raise
        raise A5OutputIntegrityError(str(exc)) from exc
