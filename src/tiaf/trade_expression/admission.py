"""Pure A4/request/evidence admission for the A6.1 boundary."""

from datetime import datetime

from tiaf.a4 import (
    A4Disposition,
    A4ExecutionStatus,
    A4Result,
    ThesisSupport,
    result_semantic_payload,
)
from tiaf.planner.digests import digest

from .contracts import (
    AdmissionResult,
    ExpressionEvidenceBundle,
    TradeExpressionPolicy,
    TradeExpressionRequest,
    semantic_fingerprint,
)
from .enums import (
    A6ErrorCode,
    AdmissionOutcome,
    CoverageState,
    EventEvidenceState,
    ExpirationQualification,
    ExpressionDirection,
)
from .errors import A6ReplayIntegrityError
from .policy import require_supported_policy, validate_preferences


def _age_seconds(cutoff: datetime, observed_at: datetime) -> int | None:
    age = cutoff - observed_at
    seconds = age.days * 86400 + age.seconds
    if age.microseconds:
        seconds += 1
    return None if seconds < 0 else seconds


def _result_payload(result: AdmissionResult) -> dict[str, object]:
    return result.model_dump(
        mode="json",
        exclude={"result_id": True, "semantic_fingerprint": True},
    )


def _make_result(
    *,
    request: TradeExpressionRequest,
    a4_result: A4Result,
    evidence: ExpressionEvidenceBundle,
    policy: TradeExpressionPolicy,
    outcome: AdmissionOutcome,
    reasons: tuple[str, ...],
    direction: ExpressionDirection | None = None,
) -> AdmissionResult:
    provisional = AdmissionResult(
        result_id="a6-admission:pending",
        request_id=request.request_id,
        outcome=outcome,
        resolved_direction=direction,
        reason_codes=reasons,
        request_fingerprint=semantic_fingerprint(request),
        a4_result_fingerprint=a4_result.semantic_fingerprint,
        evidence_fingerprint=evidence.fingerprint(),
        policy_fingerprint=policy.fingerprint(),
        semantic_fingerprint="0" * 64,
    )
    fingerprint = semantic_fingerprint(_result_payload(provisional))
    return provisional.model_copy(
        update={
            "result_id": f"a6-admission:{fingerprint[:24]}",
            "semantic_fingerprint": fingerprint,
        }
    )


def _outcome(
    *,
    request: TradeExpressionRequest,
    a4_result: A4Result,
    evidence: ExpressionEvidenceBundle,
    policy: TradeExpressionPolicy,
    outcome: AdmissionOutcome,
    reason: str,
    direction: ExpressionDirection | None = None,
) -> AdmissionResult:
    return _make_result(
        request=request,
        a4_result=a4_result,
        evidence=evidence,
        policy=policy,
        outcome=outcome,
        reasons=(reason,),
        direction=direction,
    )


def _resolve_direction(value: str | None) -> ExpressionDirection | None:
    if value == "POSITIVE":
        return ExpressionDirection.BULLISH
    if value == "NEGATIVE":
        return ExpressionDirection.BEARISH
    return None


def admit_request(
    request: TradeExpressionRequest,
    a4_result: A4Result,
    evidence: ExpressionEvidenceBundle,
    policy: TradeExpressionPolicy,
) -> AdmissionResult:
    """Return a normal typed outcome using captured inputs and no current data."""
    require_supported_policy(policy)
    validate_preferences(request.preferences, policy)
    policy_identity = (
        policy.policy_id,
        policy.policy_version,
        policy.profile_id,
        policy.fingerprint(),
        policy.evaluator_id,
        policy.evaluator_version,
        policy.normalizer_id,
        policy.normalizer_version,
    )
    request_policy = (
        request.policy.policy_id,
        request.policy.policy_version,
        request.policy.profile_id,
        request.policy.policy_fingerprint,
        request.policy.evaluator_id,
        request.policy.evaluator_version,
        request.policy.normalizer_id,
        request.policy.normalizer_version,
    )
    if request_policy != policy_identity:
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.INVALID_REQUEST,
            reason="POLICY_IDENTITY_MISMATCH",
        )
    a4_fingerprint = digest(result_semantic_payload(a4_result))
    if (
        a4_result.semantic_fingerprint != a4_fingerprint
        or a4_result.result_id != f"a4-result:{a4_fingerprint[:24]}"
    ):
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.INVALID_REQUEST,
            reason="A4_RESULT_INTEGRITY_FAILED",
        )
    if (
        request.a4_result_ref != a4_result.result_id
        or request.a4_result_fingerprint != a4_result.semantic_fingerprint
        or evidence.upstream_a4.a4_result_ref != a4_result.result_id
        or evidence.upstream_a4.a4_result_fingerprint != a4_result.semantic_fingerprint
    ):
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.INVALID_REQUEST,
            reason="A4_IDENTITY_MISMATCH",
        )
    if (
        request.derivatives_capture_ref != evidence.derivatives.capture_id
        or request.derivatives_capture_fingerprint != evidence.derivatives.fingerprint()
        or request.evaluation_cutoff != evidence.evaluation_cutoff
    ):
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.INVALID_REQUEST,
            reason="EVIDENCE_IDENTITY_OR_CUTOFF_MISMATCH",
        )
    if (
        request.subject != evidence.subject
        or request.subject_class is not evidence.subject_class
        or request.subject != a4_result.primary_thesis.subject
        or request.objective != a4_result.primary_thesis.objective
    ):
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.INVALID_REQUEST,
            reason="SUBJECT_OR_OBJECTIVE_MISMATCH",
        )
    if a4_result.execution_status is not A4ExecutionStatus.COMPLETE:
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.INSUFFICIENT_EVIDENCE,
            reason="A4_EXECUTION_INCOMPLETE",
        )
    if a4_result.disposition in {
        A4Disposition.NO_TRADE,
        A4Disposition.AVOID,
        A4Disposition.CONFLICTED,
        A4Disposition.WAIT,
    }:
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.REJECTED_UPSTREAM,
            reason=f"A4_{a4_result.disposition.value}",
        )
    if a4_result.disposition in {
        A4Disposition.INSUFFICIENT_EVIDENCE,
        A4Disposition.ABSTAIN,
    }:
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.INSUFFICIENT_EVIDENCE,
            reason=f"A4_{a4_result.disposition.value}",
        )
    primary = a4_result.primary_thesis
    if (
        a4_result.disposition is not A4Disposition.SUPPORTIVE
        or primary.support is not ThesisSupport.SUPPORTED
        or primary.thesis_id not in a4_result.surviving_thesis_refs
    ):
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.REJECTED_UPSTREAM,
            reason="A4_PRIMARY_NOT_SUPPORTED_AND_SURVIVING",
        )
    direction = _resolve_direction(primary.directional_interpretation)
    if direction is None:
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.REJECTED_UPSTREAM,
            reason="A4_DIRECTION_UNRESOLVED",
        )
    if request.direction is not direction:
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.INVALID_REQUEST,
            reason="REQUEST_DIRECTION_CONFLICTS_WITH_A4",
            direction=direction,
        )
    if request.subject_class not in policy.supported_subject_classes:
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.UNSUPPORTED,
            reason="SUBJECT_CLASS_OUTSIDE_V1",
        )
    if request.horizon.horizon_class not in policy.allowed_horizons:
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.UNSUPPORTED,
            reason="HORIZON_CLASS_OUTSIDE_V1",
        )
    duration_limit = next(
        item.maximum_seconds
        for item in policy.horizon_duration_limits
        if item.horizon_class is request.horizon.horizon_class
    )
    if duration_limit is not None:
        if request.horizon.exact_duration_seconds > duration_limit:
            return _outcome(
                request=request,
                a4_result=a4_result,
                evidence=evidence,
                policy=policy,
                outcome=AdmissionOutcome.UNSUPPORTED,
                reason="HORIZON_OUTSIDE_V1",
            )
    elif evidence.session is None or not (
        evidence.session.opens_at
        <= request.evaluation_cutoff
        < request.horizon.target_end_at
        <= evidence.session.closes_at
    ):
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.INSUFFICIENT_EVIDENCE,
            reason="DAY_SESSION_NOT_QUALIFIED",
        )
    upstream_limit = next(
        item.max_age_seconds
        for item in policy.upstream_age_limits
        if item.horizon_class is request.horizon.horizon_class
    )
    upstream_age = _age_seconds(request.evaluation_cutoff, evidence.upstream_a4.evidence_as_of)
    if upstream_age is None or upstream_age > upstream_limit:
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.INSUFFICIENT_EVIDENCE,
            reason="A4_EVIDENCE_STALE_OR_FUTURE",
            direction=direction,
        )
    if (
        evidence.event_evidence is not None
        and evidence.event_evidence.state is EventEvidenceState.KNOWN_BLOCKER
    ):
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.ADMITTED,
            reason="ADMITTED_WITH_KNOWN_EVENT_BLOCKER",
            direction=direction,
        )
    if evidence.derivatives.coverage.state not in {
        CoverageState.PRESENT,
        CoverageState.CONFIRMED_EMPTY,
    }:
        return _outcome(
            request=request,
            a4_result=a4_result,
            evidence=evidence,
            policy=policy,
            outcome=AdmissionOutcome.INSUFFICIENT_EVIDENCE,
            reason="DERIVATIVES_COVERAGE_UNQUALIFIED",
            direction=direction,
        )
    for chain in evidence.derivatives.chains:
        if chain.coverage.state not in {
            CoverageState.PRESENT,
            CoverageState.CONFIRMED_EMPTY,
        }:
            return _outcome(
                request=request,
                a4_result=a4_result,
                evidence=evidence,
                policy=policy,
                outcome=AdmissionOutcome.INSUFFICIENT_EVIDENCE,
                reason="CHAIN_COVERAGE_UNQUALIFIED",
                direction=direction,
            )
        if chain.expiration.qualification is not ExpirationQualification.QUALIFIED_INSTANT:
            return _outcome(
                request=request,
                a4_result=a4_result,
                evidence=evidence,
                policy=policy,
                outcome=AdmissionOutcome.INSUFFICIENT_EVIDENCE,
                reason="EXPIRATION_INSTANT_UNQUALIFIED",
                direction=direction,
            )
        spot_at = chain.underlying_timing.authoritative_observed_at
        spot_age = None if spot_at is None else _age_seconds(request.evaluation_cutoff, spot_at)
        if spot_age is None or spot_age > policy.spot_max_age_seconds:
            return _outcome(
                request=request,
                a4_result=a4_result,
                evidence=evidence,
                policy=policy,
                outcome=AdmissionOutcome.INSUFFICIENT_EVIDENCE,
                reason="SPOT_TIMING_UNQUALIFIED_OR_STALE",
                direction=direction,
            )
        for quote in chain.quotes:
            quote_at = quote.timing.authoritative_observed_at
            quote_age = (
                None if quote_at is None else _age_seconds(request.evaluation_cutoff, quote_at)
            )
            if quote_age is None or quote_age > policy.quote_max_age_seconds:
                return _outcome(
                    request=request,
                    a4_result=a4_result,
                    evidence=evidence,
                    policy=policy,
                    outcome=AdmissionOutcome.INSUFFICIENT_EVIDENCE,
                    reason="QUOTE_TIMING_UNQUALIFIED_OR_STALE",
                    direction=direction,
                )
    if request.preferences.require_event_clear:
        if (
            evidence.event_evidence is None
            or evidence.event_evidence.state
            is not EventEvidenceState.QUALIFIED_NO_INTERSECTING_EVENT
        ):
            return _outcome(
                request=request,
                a4_result=a4_result,
                evidence=evidence,
                policy=policy,
                outcome=AdmissionOutcome.INSUFFICIENT_EVIDENCE,
                reason="EVENT_CLEARANCE_NOT_PROVEN",
                direction=direction,
            )
    return _outcome(
        request=request,
        a4_result=a4_result,
        evidence=evidence,
        policy=policy,
        outcome=AdmissionOutcome.ADMITTED,
        reason="ADMITTED_FOR_A6_EVALUATION",
        direction=direction,
    )


def validate_admission_result(result: AdmissionResult) -> AdmissionResult:
    """Validate content-addressed A6.1 result integrity."""
    expected = semantic_fingerprint(_result_payload(result))
    if result.semantic_fingerprint != expected:
        raise A6ReplayIntegrityError(
            A6ErrorCode.INCOMPATIBLE_EVIDENCE_VERSION,
            "A6 admission semantic fingerprint mismatch",
        )
    if result.result_id != f"a6-admission:{expected[:24]}":
        raise A6ReplayIntegrityError(
            A6ErrorCode.INCOMPATIBLE_EVIDENCE_VERSION,
            "A6 admission result identity mismatch",
        )
    return result


def verify_admission_replay(
    recorded: AdmissionResult,
    request: TradeExpressionRequest,
    a4_result: A4Result,
    evidence: ExpressionEvidenceBundle,
    policy: TradeExpressionPolicy,
) -> AdmissionResult:
    """Re-evaluate captured artifacts; performs no live or wall-clock reads."""
    validate_admission_result(recorded)
    replayed = admit_request(request, a4_result, evidence, policy)
    if replayed.semantic_fingerprint != recorded.semantic_fingerprint:
        raise A6ReplayIntegrityError(
            A6ErrorCode.INCOMPATIBLE_EVIDENCE_VERSION,
            "A6 admission replay differs from the captured result",
        )
    return replayed
