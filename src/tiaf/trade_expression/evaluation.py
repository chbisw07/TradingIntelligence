"""Pure bounded A6.2 candidate evaluation, ranking, and replay."""

from datetime import datetime
from decimal import Decimal
from typing import Literal, cast

from tiaf.a4 import A4Result
from tiaf.contracts import OptionType

from .admission import validate_admission_result, verify_admission_replay
from .contracts import (
    AdmissionResult,
    CandidateGateAssessment,
    CandidateRankingFacts,
    ExpressionCandidateEvaluation,
    ExpressionEvidenceBundle,
    ExpressionExplanation,
    OptionQuoteEvidence,
    RankDifference,
    SpreadAssessment,
    TradeExpressionAssessment,
    TradeExpressionCandidate,
    TradeExpressionPolicy,
    TradeExpressionRequest,
    semantic_fingerprint,
)
from .enums import (
    A6ErrorCode,
    AdmissionOutcome,
    CandidateEligibility,
    CandidateGateId,
    CoverageState,
    EventEvidenceState,
    EventMateriality,
    EventRelevance,
    ExpressionDirection,
    ExpressionDisposition,
    GateStatus,
    MoneynessLabel,
    SpreadEligibility,
    SpreadQualityTier,
    TimingQualification,
)
from .errors import A6ContractError, A6ReplayIntegrityError
from .policy import assess_spread, require_supported_policy, resolve_moneyness_geometry

_CANDIDATE_INVALIDATIONS = (
    "CONTRACT_AVAILABILITY_CHANGES",
    "DERIVATIVES_COVERAGE_CHANGES",
    "EXPIRY_CUSHION_THRESHOLD_CROSSED",
    "HOLDING_TARGET_CHANGES",
    "POLICY_OR_PROFILE_CHANGES",
    "QUOTE_FRESHNESS_EXPIRES",
    "SPREAD_LIMIT_BREACHED",
    "UNDERLYING_FRESHNESS_EXPIRES",
)
_ASSESSMENT_INVALIDATIONS = tuple(
    sorted((*_CANDIDATE_INVALIDATIONS, "EVENT_EVIDENCE_CHANGES", "UPSTREAM_THESIS_CHANGES"))
)


def _decimal_text(value: Decimal) -> str:
    return "0" if value == 0 else format(value.normalize(), "f")


def _seconds_between(later: datetime, earlier: datetime) -> Decimal:
    delta = later - earlier
    return Decimal(delta.days * 86400 + delta.seconds) + (
        Decimal(delta.microseconds) / Decimal(1_000_000)
    )


def _stable_unique(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _evaluation_payload(evaluation: ExpressionCandidateEvaluation) -> dict[str, object]:
    return evaluation.model_dump(
        mode="json",
        exclude={"evaluation_id": True, "semantic_fingerprint": True},
    )


def _assessment_payload(assessment: TradeExpressionAssessment) -> dict[str, object]:
    return assessment.model_dump(
        mode="json",
        exclude={"result_id": True, "semantic_fingerprint": True},
    )


def _candidate(
    quote: OptionQuoteEvidence,
    direction: ExpressionDirection,
    moneyness: MoneynessLabel,
) -> TradeExpressionCandidate:
    provisional = TradeExpressionCandidate(
        candidate_id="a6-candidate:pending",
        contract=quote.contract,
        direction=direction,
        moneyness=moneyness,
    )
    fingerprint = semantic_fingerprint(
        {
            "contract_identity": quote.contract.identity_fingerprint(),
            "direction": direction,
            "moneyness": moneyness,
            "position_side": "LONG",
        }
    )
    return provisional.model_copy(update={"candidate_id": f"a6-candidate:{fingerprint[:24]}"})


def _gate(
    gate_id: CandidateGateId,
    status: GateStatus,
    reason_code: str,
    *,
    policy: TradeExpressionPolicy,
    measured_value: Decimal | None = None,
    measured_unit: str | None = None,
    threshold_value: Decimal | None = None,
    threshold_unit: str | None = None,
    evidence_refs: tuple[str, ...] = (),
) -> CandidateGateAssessment:
    return CandidateGateAssessment(
        gate_id=gate_id,
        status=status,
        reason_code=reason_code,
        measured_value=measured_value,
        measured_unit=measured_unit,
        threshold_value=threshold_value,
        threshold_unit=threshold_unit,
        evidence_refs=evidence_refs,
        policy_ref=policy.policy_id,
    )


def _timing_gate(
    quote: OptionQuoteEvidence,
    chain_spot_at: datetime | None,
    cutoff: datetime,
    policy: TradeExpressionPolicy,
    evidence_refs: tuple[str, ...],
) -> CandidateGateAssessment:
    quote_at = quote.timing.authoritative_observed_at
    if quote_at is None or chain_spot_at is None:
        return _gate(
            CandidateGateId.TIMING_FRESHNESS,
            GateStatus.UNKNOWN,
            "MARKET_OBSERVATION_TIME_UNQUALIFIED",
            policy=policy,
            evidence_refs=evidence_refs,
        )
    quote_age = _seconds_between(cutoff, quote_at)
    spot_age = _seconds_between(cutoff, chain_spot_at)
    measured = max(quote_age, spot_age)
    if quote_age < 0 or spot_age < 0:
        status, reason = GateStatus.UNKNOWN, "MARKET_OBSERVATION_TIME_FUTURE"
    elif quote_age > policy.quote_max_age_seconds or spot_age > policy.spot_max_age_seconds:
        status, reason = GateStatus.UNKNOWN, "MARKET_OBSERVATION_STALE"
    else:
        status, reason = GateStatus.PASS, "MARKET_OBSERVATION_FRESH"
    return _gate(
        CandidateGateId.TIMING_FRESHNESS,
        status,
        reason,
        policy=policy,
        measured_value=measured,
        measured_unit="SECONDS_AGE_MAX",
        threshold_value=Decimal(max(policy.quote_max_age_seconds, policy.spot_max_age_seconds)),
        threshold_unit="SECONDS",
        evidence_refs=evidence_refs,
    )


def _horizon_gate(
    expiration_at: datetime | None,
    target_at: datetime,
    minimum_seconds: int,
    maximum_seconds: int | None,
    policy: TradeExpressionPolicy,
    evidence_refs: tuple[str, ...],
) -> tuple[CandidateGateAssessment, Decimal | None]:
    if expiration_at is None:
        return (
            _gate(
                CandidateGateId.HORIZON_FIT,
                GateStatus.UNKNOWN,
                "EXPIRATION_INSTANT_UNQUALIFIED",
                policy=policy,
                evidence_refs=evidence_refs,
            ),
            None,
        )
    residual = _seconds_between(expiration_at, target_at)
    if residual < minimum_seconds:
        status, reason = GateStatus.FAIL, "INSUFFICIENT_RESIDUAL_LIFE"
    elif maximum_seconds is not None and residual > maximum_seconds:
        status, reason = GateStatus.FAIL, "EXCESS_RESIDUAL_LIFE"
    else:
        status, reason = GateStatus.PASS, "EXPIRY_FITS_HORIZON"
    return (
        _gate(
            CandidateGateId.HORIZON_FIT,
            status,
            reason,
            policy=policy,
            measured_value=residual,
            measured_unit="SECONDS_AFTER_TARGET",
            threshold_value=Decimal(minimum_seconds),
            threshold_unit="MINIMUM_SECONDS_AFTER_TARGET",
            evidence_refs=evidence_refs,
        ),
        residual,
    )


def _quote_geometry_gate(
    quote: OptionQuoteEvidence,
    policy: TradeExpressionPolicy,
    evidence_refs: tuple[str, ...],
) -> CandidateGateAssessment:
    if quote.bid is None or quote.ask is None:
        status, reason = GateStatus.UNKNOWN, "MISSING_BID_OR_ASK"
    elif quote.bid <= 0:
        status, reason = GateStatus.FAIL, "NON_POSITIVE_BID"
    elif quote.ask <= 0 or quote.ask < quote.bid:
        status, reason = GateStatus.FAIL, "INVALID_OR_CROSSED_ASK"
    else:
        status, reason = GateStatus.PASS, "VALID_BID_ASK"
    return _gate(
        CandidateGateId.QUOTE_GEOMETRY,
        status,
        reason,
        policy=policy,
        evidence_refs=evidence_refs,
    )


def _depth_gate(
    quote: OptionQuoteEvidence,
    policy: TradeExpressionPolicy,
    evidence_refs: tuple[str, ...],
) -> CandidateGateAssessment:
    bid_quantity = quote.top_bid_quantity
    ask_quantity = quote.top_ask_quantity
    if bid_quantity is None or ask_quantity is None:
        status, reason, measured = GateStatus.UNKNOWN, "MISSING_TOP_QUANTITY", None
    else:
        measured = min(bid_quantity, ask_quantity)
        if measured <= policy.minimum_top_quantity_exclusive:
            status, reason = GateStatus.FAIL, "NON_POSITIVE_TOP_QUANTITY"
        else:
            status, reason = GateStatus.PASS, "POSITIVE_TOP_QUANTITY"
    return _gate(
        CandidateGateId.TOP_DEPTH,
        status,
        reason,
        policy=policy,
        measured_value=measured,
        measured_unit="CONTRACTS" if measured is not None else None,
        threshold_value=policy.minimum_top_quantity_exclusive,
        threshold_unit="EXCLUSIVE_CONTRACTS",
        evidence_refs=evidence_refs,
    )


def _spread_gate(
    spread: SpreadAssessment,
    policy: TradeExpressionPolicy,
    evidence_refs: tuple[str, ...],
) -> CandidateGateAssessment:
    status = {
        SpreadEligibility.ELIGIBLE: GateStatus.PASS,
        SpreadEligibility.INELIGIBLE: GateStatus.FAIL,
        SpreadEligibility.UNKNOWN: GateStatus.UNKNOWN,
    }[spread.eligibility]
    return _gate(
        CandidateGateId.SPREAD,
        status,
        spread.reason_code,
        policy=policy,
        measured_value=spread.relative_spread_bps,
        measured_unit="BASIS_POINTS" if spread.relative_spread_bps is not None else None,
        threshold_value=policy.hard_spread_limit_bps,
        threshold_unit="MAXIMUM_BASIS_POINTS",
        evidence_refs=evidence_refs,
    )


def _premium_gate(
    quote: OptionQuoteEvidence,
    request: TradeExpressionRequest,
    policy: TradeExpressionPolicy,
    evidence_refs: tuple[str, ...],
) -> CandidateGateAssessment:
    cap = request.preferences.premium_cap
    if cap is None:
        return _gate(
            CandidateGateId.PREMIUM_CAP,
            GateStatus.PASS,
            "PREMIUM_CAP_NOT_REQUESTED",
            policy=policy,
            evidence_refs=evidence_refs,
        )
    if quote.ask is None:
        status, reason = GateStatus.UNKNOWN, "ASK_MISSING_FOR_PREMIUM_CAP"
    elif quote.ask > cap:
        status, reason = GateStatus.FAIL, "ASK_ABOVE_PER_UNIT_PREMIUM_CAP"
    else:
        status, reason = GateStatus.PASS, "ASK_WITHIN_PER_UNIT_PREMIUM_CAP"
    return _gate(
        CandidateGateId.PREMIUM_CAP,
        status,
        reason,
        policy=policy,
        measured_value=quote.ask,
        measured_unit="INR_PER_UNIT" if quote.ask is not None else None,
        threshold_value=cap,
        threshold_unit="MAXIMUM_INR_PER_UNIT",
        evidence_refs=evidence_refs,
    )


def _evaluate_candidate(
    *,
    quote: OptionQuoteEvidence,
    chain_id: str,
    chain_spot_at: datetime | None,
    chain_provenance: tuple[str, ...],
    chain_coverage_refs: tuple[str, ...],
    direction: ExpressionDirection,
    moneyness: MoneynessLabel,
    request: TradeExpressionRequest,
    policy: TradeExpressionPolicy,
) -> ExpressionCandidateEvaluation:
    candidate = _candidate(quote, direction, moneyness)
    evidence_refs = tuple(
        sorted(
            set(
                (
                    quote.quote_id,
                    chain_id,
                    *quote.provenance_refs,
                    *quote.contract.provenance_refs,
                    *chain_provenance,
                    *chain_coverage_refs,
                )
            )
        )
    )
    identity = _gate(
        CandidateGateId.IDENTITY_MEMBERSHIP,
        GateStatus.PASS,
        "LISTED_CONTRACT_IDENTITY_CONFIRMED",
        policy=policy,
        evidence_refs=evidence_refs,
    )
    timing = _timing_gate(quote, chain_spot_at, request.evaluation_cutoff, policy, evidence_refs)
    residual_rule = next(
        item
        for item in policy.residual_life_rules
        if item.horizon_class is request.horizon.horizon_class
    )
    horizon, residual = _horizon_gate(
        quote.contract.expiration.expiration_at,
        request.horizon.target_end_at,
        residual_rule.minimum_seconds,
        residual_rule.maximum_seconds,
        policy,
        evidence_refs,
    )
    geometry = _quote_geometry_gate(quote, policy, evidence_refs)
    depth = _depth_gate(quote, policy, evidence_refs)
    spread = assess_spread(
        quote_ref=quote.quote_id,
        bid=quote.bid,
        ask=quote.ask,
        top_bid_quantity=quote.top_bid_quantity,
        top_ask_quantity=quote.top_ask_quantity,
        policy=policy,
    )
    spread_gate = _spread_gate(spread, policy, evidence_refs)
    premium = _premium_gate(quote, request, policy, evidence_refs)
    gates = (identity, timing, horizon, geometry, depth, spread_gate, premium)
    rejected = _stable_unique(
        [item.reason_code for item in gates if item.status is GateStatus.FAIL]
    )
    uncertain = _stable_unique(
        [item.reason_code for item in gates if item.status is GateStatus.UNKNOWN]
    )
    if uncertain:
        eligibility = CandidateEligibility.UNKNOWN
    elif rejected:
        eligibility = CandidateEligibility.INELIGIBLE
    else:
        eligibility = CandidateEligibility.ELIGIBLE
    ranking: CandidateRankingFacts | None = None
    if eligibility is CandidateEligibility.ELIGIBLE:
        assert residual is not None
        assert spread.relative_spread_bps is not None
        assert spread.quality_tier in {SpreadQualityTier.TIER_0, SpreadQualityTier.TIER_1}
        tier_rank: Literal[0, 1] = 0 if spread.quality_tier is SpreadQualityTier.TIER_0 else 1
        moneyness_rank = request.preferences.moneyness_order.index(moneyness)
        contract = quote.contract
        ranking = CandidateRankingFacts(
            spread_tier_rank=tier_rank,
            requested_moneyness_rank=moneyness_rank,
            expiry_cushion_excess_seconds=residual - residual_rule.minimum_seconds,
            exact_spread_bps=spread.relative_spread_bps,
            canonical_contract_key=(
                contract.exchange,
                contract.subject,
                contract.expiry_date.isoformat(),
                _decimal_text(contract.strike),
                contract.option_type.value,
            ),
        )
    provisional = ExpressionCandidateEvaluation(
        evaluation_id="a6-candidate-evaluation:pending",
        candidate=candidate,
        quote_ref=quote.quote_id,
        evaluated_at=request.evaluation_cutoff,
        gates=gates,
        spread=spread,
        eligibility=eligibility,
        rejection_reason_codes=rejected,
        uncertainty_reason_codes=uncertain,
        ranking_facts=ranking,
        invalidation_conditions=_CANDIDATE_INVALIDATIONS,
        evidence_refs=evidence_refs,
        policy_fingerprint=policy.fingerprint(),
        semantic_fingerprint="0" * 64,
    )
    fingerprint = semantic_fingerprint(_evaluation_payload(provisional))
    return provisional.model_copy(
        update={
            "evaluation_id": f"a6-candidate-evaluation:{fingerprint[:24]}",
            "semantic_fingerprint": fingerprint,
        }
    )


def _rank_key(evaluation: ExpressionCandidateEvaluation) -> tuple[object, ...]:
    facts = evaluation.ranking_facts
    if facts is None:
        raise ValueError("only eligible candidates have a rank key")
    return (
        facts.spread_tier_rank,
        facts.requested_moneyness_rank,
        facts.expiry_cushion_excess_seconds,
        facts.exact_spread_bps,
        facts.canonical_contract_key,
    )


def _rank_difference(
    preferred: ExpressionCandidateEvaluation,
    compared: ExpressionCandidateEvaluation,
) -> RankDifference:
    left = _rank_key(preferred)
    right = _rank_key(compared)
    labels = (
        "SPREAD_TIER",
        "MONEYNESS_PREFERENCE",
        "EXPIRY_CUSHION_EXCESS",
        "EXACT_SPREAD_BPS",
        "CANONICAL_CONTRACT_KEY",
    )
    index = next(
        index for index, pair in enumerate(zip(left, right, strict=True)) if pair[0] != pair[1]
    )
    decisive_dimension = cast(
        Literal[
            "SPREAD_TIER",
            "MONEYNESS_PREFERENCE",
            "EXPIRY_CUSHION_EXCESS",
            "EXACT_SPREAD_BPS",
            "CANONICAL_CONTRACT_KEY",
        ],
        labels[index],
    )
    return RankDifference(
        preferred_candidate_ref=preferred.candidate.candidate_id,
        compared_candidate_ref=compared.candidate.candidate_id,
        decisive_dimension=decisive_dimension,
        preferred_value=str(left[index]),
        compared_value=str(right[index]),
    )


def _event_precheck(
    request: TradeExpressionRequest,
    evidence: ExpressionEvidenceBundle,
) -> tuple[ExpressionDisposition | None, tuple[str, ...], tuple[str, ...]]:
    window = evidence.event_evidence
    if window is None:
        return None, (), ("EVENT_COVERAGE_NOT_SUPPLIED_OPTIONAL",)
    if window.state is EventEvidenceState.KNOWN_BLOCKER:
        blockers = [
            event
            for event in window.events
            if event.timing_qualification is TimingQualification.QUALIFIED
            and event.event_at is not None
            and request.evaluation_cutoff < event.event_at <= request.horizon.target_end_at
            and event.materiality is EventMateriality.MATERIAL
            and event.relevance is EventRelevance.RELEVANT
        ]
        if blockers:
            return (
                ExpressionDisposition.WAIT_FOR_EXPRESSION,
                ("KNOWN_MATERIAL_EVENT_IN_WINDOW",),
                (),
            )
        return None, (), ("KNOWN_EVENT_OUTSIDE_HOLDING_WINDOW",)
    if window.state is EventEvidenceState.QUALIFIED_NO_INTERSECTING_EVENT:
        incomplete = (
            window.window_start > request.evaluation_cutoff
            or window.window_end < request.horizon.target_end_at
        )
        if incomplete and request.preferences.require_event_clear:
            return (
                ExpressionDisposition.INSUFFICIENT_EVIDENCE,
                (),
                ("EVENT_CLEARANCE_WINDOW_INCOMPLETE",),
            )
        if incomplete:
            return None, (), ("EVENT_CLEARANCE_WINDOW_INCOMPLETE_OPTIONAL",)
        return None, (), ()
    ambiguous_relevant = any(
        event.relevance is not EventRelevance.NOT_RELEVANT
        and event.materiality is not EventMateriality.NOT_MATERIAL
        and (
            event.timing_qualification is not TimingQualification.QUALIFIED
            or event.event_at is None
            or request.evaluation_cutoff < event.event_at <= request.horizon.target_end_at
        )
        for event in window.events
    )
    if ambiguous_relevant:
        return ExpressionDisposition.INSUFFICIENT_EVIDENCE, (), ("EVENT_STATE_UNRESOLVED",)
    return None, (), ("EVENT_COVERAGE_UNKNOWN_OPTIONAL",)


def _base_assessment(
    *,
    request: TradeExpressionRequest,
    admission: AdmissionResult,
    evidence: ExpressionEvidenceBundle,
    policy: TradeExpressionPolicy,
    disposition: ExpressionDisposition,
    evaluations: tuple[ExpressionCandidateEvaluation, ...] = (),
    preferred: ExpressionCandidateEvaluation | None = None,
    alternatives: tuple[ExpressionCandidateEvaluation, ...] = (),
    blockers: tuple[str, ...] = (),
    gaps: tuple[str, ...] = (),
    reason_codes: tuple[str, ...],
    rank_differences: tuple[RankDifference, ...] = (),
    composition_refs: tuple[str, ...] = (),
) -> TradeExpressionAssessment:
    provisional = TradeExpressionAssessment(
        result_id="a6-assessment:pending",
        request_id=request.request_id,
        admission_result_id=admission.result_id,
        subject=request.subject,
        direction=admission.resolved_direction,
        horizon=request.horizon,
        evaluation_cutoff=request.evaluation_cutoff,
        disposition=disposition,
        preferred_candidate_ref=(None if preferred is None else preferred.candidate.candidate_id),
        alternative_candidate_refs=tuple(item.candidate.candidate_id for item in alternatives),
        candidate_evaluations=evaluations,
        blockers=blockers,
        gaps=gaps,
        explanation=ExpressionExplanation(
            disposition_reason_codes=reason_codes,
            preferred_reason_codes=(
                () if preferred is None else ("ALL_HARD_GATES_PASS", "LEXICOGRAPHIC_RANK_1")
            ),
            rank_differences=rank_differences,
        ),
        invalidation_conditions=_ASSESSMENT_INVALIDATIONS,
        request_fingerprint=semantic_fingerprint(request),
        admission_fingerprint=admission.semantic_fingerprint,
        a4_result_fingerprint=admission.a4_result_fingerprint,
        evidence_fingerprint=evidence.fingerprint(),
        policy=request.policy,
        composition_refs=composition_refs,
        semantic_fingerprint="0" * 64,
    )
    fingerprint = semantic_fingerprint(_assessment_payload(provisional))
    return provisional.model_copy(
        update={
            "result_id": f"a6-assessment:{fingerprint[:24]}",
            "semantic_fingerprint": fingerprint,
        }
    )


def evaluate_trade_expression(
    request: TradeExpressionRequest,
    a4_result: A4Result,
    evidence: ExpressionEvidenceBundle,
    policy: TradeExpressionPolicy,
    admission: AdmissionResult,
    *,
    composition_refs: tuple[str, ...] = (),
) -> TradeExpressionAssessment:
    """Evaluate captured evidence only; never acquires current state."""
    require_supported_policy(policy)
    verify_admission_replay(admission, request, a4_result, evidence, policy)
    if admission.outcome is AdmissionOutcome.INVALID_REQUEST:
        raise A6ContractError(
            A6ErrorCode.INVALID_REQUEST_SCHEMA,
            "invalid A6.1 admission cannot produce an A6.2 assessment",
        )
    if admission.outcome is AdmissionOutcome.UNSUPPORTED:
        return _base_assessment(
            request=request,
            admission=admission,
            evidence=evidence,
            policy=policy,
            disposition=ExpressionDisposition.UNSUPPORTED,
            gaps=admission.reason_codes,
            reason_codes=admission.reason_codes,
            composition_refs=composition_refs,
        )
    if admission.outcome is AdmissionOutcome.INSUFFICIENT_EVIDENCE:
        return _base_assessment(
            request=request,
            admission=admission,
            evidence=evidence,
            policy=policy,
            disposition=ExpressionDisposition.INSUFFICIENT_EVIDENCE,
            gaps=admission.reason_codes,
            reason_codes=admission.reason_codes,
            composition_refs=composition_refs,
        )
    if admission.outcome is AdmissionOutcome.REJECTED_UPSTREAM:
        wait = any(code in {"A4_WAIT", "A4_CONFLICTED"} for code in admission.reason_codes)
        disposition = (
            ExpressionDisposition.WAIT_FOR_EXPRESSION
            if wait
            else ExpressionDisposition.NO_OPTION_TRADE
        )
        return _base_assessment(
            request=request,
            admission=admission,
            evidence=evidence,
            policy=policy,
            disposition=disposition,
            blockers=admission.reason_codes,
            reason_codes=admission.reason_codes,
            composition_refs=composition_refs,
        )
    event_disposition, event_blockers, event_gaps = _event_precheck(request, evidence)
    if event_disposition is not None:
        reasons = event_blockers or event_gaps
        return _base_assessment(
            request=request,
            admission=admission,
            evidence=evidence,
            policy=policy,
            disposition=event_disposition,
            blockers=event_blockers,
            gaps=event_gaps,
            reason_codes=reasons,
            composition_refs=composition_refs,
        )
    qualified_coverage = {CoverageState.PRESENT, CoverageState.CONFIRMED_EMPTY}
    if evidence.derivatives.coverage.state not in qualified_coverage or any(
        chain.coverage.state not in qualified_coverage for chain in evidence.derivatives.chains
    ):
        return _base_assessment(
            request=request,
            admission=admission,
            evidence=evidence,
            policy=policy,
            disposition=ExpressionDisposition.INSUFFICIENT_EVIDENCE,
            gaps=("DERIVATIVES_OR_CHAIN_COVERAGE_UNQUALIFIED", *event_gaps),
            reason_codes=("DERIVATIVES_OR_CHAIN_COVERAGE_UNQUALIFIED",),
            composition_refs=composition_refs,
        )
    if evidence.derivatives.coverage.state is CoverageState.CONFIRMED_EMPTY:
        return _base_assessment(
            request=request,
            admission=admission,
            evidence=evidence,
            policy=policy,
            disposition=ExpressionDisposition.NO_OPTION_TRADE,
            blockers=("NO_LISTED_EXPIRIES_IN_SCOPE",),
            gaps=event_gaps,
            reason_codes=("NO_LISTED_EXPIRIES_IN_SCOPE",),
            composition_refs=composition_refs,
        )
    direction = admission.resolved_direction
    if direction is None:
        raise A6ContractError(A6ErrorCode.INVALID_ASSESSMENT, "admitted request has no direction")
    option_type = OptionType.CE if direction is ExpressionDirection.BULLISH else OptionType.PE
    evaluations: list[ExpressionCandidateEvaluation] = []
    for chain in evidence.derivatives.chains:
        side_quotes = [quote for quote in chain.quotes if quote.contract.option_type is option_type]
        if not side_quotes:
            continue
        quote_by_strike = {quote.contract.strike: quote for quote in side_quotes}
        geometry = resolve_moneyness_geometry(
            listed_strikes=tuple(sorted(quote_by_strike)),
            underlying_price=chain.underlying_price,
            option_type=option_type,
        )
        for moneyness, strike in geometry:
            if moneyness not in request.preferences.moneyness_order:
                continue
            evaluations.append(
                _evaluate_candidate(
                    quote=quote_by_strike[strike],
                    chain_id=chain.chain_id,
                    chain_spot_at=chain.underlying_timing.authoritative_observed_at,
                    chain_provenance=chain.provenance_refs,
                    chain_coverage_refs=chain.coverage.evidence_refs,
                    direction=direction,
                    moneyness=moneyness,
                    request=request,
                    policy=policy,
                )
            )
    if len(evaluations) > policy.max_evaluated_candidates:
        raise A6ContractError(
            A6ErrorCode.INVALID_COVERAGE, "candidate universe exceeds policy bound"
        )
    all_evaluations = tuple(evaluations)
    if not all_evaluations:
        return _base_assessment(
            request=request,
            admission=admission,
            evidence=evidence,
            policy=policy,
            disposition=ExpressionDisposition.NO_OPTION_TRADE,
            blockers=("NO_SUPPORTED_SIDE_CONTRACTS_IN_SCOPE",),
            gaps=event_gaps,
            reason_codes=("NO_SUPPORTED_SIDE_CONTRACTS_IN_SCOPE",),
            composition_refs=composition_refs,
        )
    unknown = [item for item in all_evaluations if item.eligibility is CandidateEligibility.UNKNOWN]
    if unknown:
        gaps = tuple(
            sorted(
                {
                    *event_gaps,
                    *(reason for item in unknown for reason in item.uncertainty_reason_codes),
                }
            )
        )
        return _base_assessment(
            request=request,
            admission=admission,
            evidence=evidence,
            policy=policy,
            disposition=ExpressionDisposition.INSUFFICIENT_EVIDENCE,
            evaluations=all_evaluations,
            gaps=gaps,
            reason_codes=("REQUIRED_CANDIDATE_EVIDENCE_UNKNOWN",),
            composition_refs=composition_refs,
        )
    eligible = sorted(
        (item for item in all_evaluations if item.eligibility is CandidateEligibility.ELIGIBLE),
        key=_rank_key,
    )
    if not eligible:
        blockers = tuple(
            sorted({reason for item in all_evaluations for reason in item.rejection_reason_codes})
        )
        return _base_assessment(
            request=request,
            admission=admission,
            evidence=evidence,
            policy=policy,
            disposition=ExpressionDisposition.NO_OPTION_TRADE,
            evaluations=all_evaluations,
            blockers=blockers,
            gaps=event_gaps,
            reason_codes=("NO_CANDIDATE_PASSED_ALL_HARD_GATES",),
            composition_refs=composition_refs,
        )
    preferred = eligible[0]
    alternatives = tuple(eligible[1 : 1 + policy.max_alternatives])
    differences = tuple(_rank_difference(preferred, item) for item in eligible[1:])
    return _base_assessment(
        request=request,
        admission=admission,
        evidence=evidence,
        policy=policy,
        disposition=ExpressionDisposition.EXPRESSION_AVAILABLE,
        evaluations=all_evaluations,
        preferred=preferred,
        alternatives=alternatives,
        gaps=event_gaps,
        reason_codes=("ELIGIBLE_CANDIDATE_SELECTED",),
        rank_differences=differences,
        composition_refs=composition_refs,
    )


def validate_trade_expression_assessment(
    assessment: TradeExpressionAssessment,
) -> TradeExpressionAssessment:
    for evaluation in assessment.candidate_evaluations:
        candidate_fingerprint = semantic_fingerprint(
            {
                "contract_identity": evaluation.candidate.contract.identity_fingerprint(),
                "direction": evaluation.candidate.direction,
                "moneyness": evaluation.candidate.moneyness,
                "position_side": evaluation.candidate.position_side,
            }
        )
        if evaluation.candidate.candidate_id != f"a6-candidate:{candidate_fingerprint[:24]}":
            raise A6ReplayIntegrityError(
                A6ErrorCode.INVALID_ASSESSMENT,
                "A6 candidate identity mismatch",
            )
        evaluation_fingerprint = semantic_fingerprint(_evaluation_payload(evaluation))
        if (
            evaluation.semantic_fingerprint != evaluation_fingerprint
            or evaluation.evaluation_id != f"a6-candidate-evaluation:{evaluation_fingerprint[:24]}"
        ):
            raise A6ReplayIntegrityError(
                A6ErrorCode.INVALID_ASSESSMENT,
                "A6 candidate evaluation integrity mismatch",
            )
    expected = semantic_fingerprint(_assessment_payload(assessment))
    if (
        assessment.semantic_fingerprint != expected
        or assessment.result_id != f"a6-assessment:{expected[:24]}"
    ):
        raise A6ReplayIntegrityError(
            A6ErrorCode.INVALID_ASSESSMENT,
            "A6 assessment integrity mismatch",
        )
    if assessment.disposition is ExpressionDisposition.EXPRESSION_AVAILABLE:
        by_id = {item.candidate.candidate_id: item for item in assessment.candidate_evaluations}
        ranked = sorted(
            (
                item
                for item in assessment.candidate_evaluations
                if item.eligibility is CandidateEligibility.ELIGIBLE
            ),
            key=_rank_key,
        )
        expected_refs = tuple(item.candidate.candidate_id for item in ranked[:3])
        actual_refs = (
            assessment.preferred_candidate_ref,
            *assessment.alternative_candidate_refs,
        )
        if actual_refs != expected_refs or any(item not in by_id for item in actual_refs):
            raise A6ReplayIntegrityError(
                A6ErrorCode.INVALID_ASSESSMENT,
                "A6 shortlist does not match deterministic rank",
            )
    return assessment


def verify_trade_expression_replay(
    recorded: TradeExpressionAssessment,
    request: TradeExpressionRequest,
    a4_result: A4Result,
    evidence: ExpressionEvidenceBundle,
    policy: TradeExpressionPolicy,
    admission: AdmissionResult,
    *,
    composition_refs: tuple[str, ...] = (),
) -> TradeExpressionAssessment:
    """Re-evaluate exact captured artifacts without current registry or network state."""
    validate_trade_expression_assessment(recorded)
    validate_admission_result(admission)
    replayed = evaluate_trade_expression(
        request,
        a4_result,
        evidence,
        policy,
        admission,
        composition_refs=composition_refs,
    )
    if replayed.semantic_fingerprint != recorded.semantic_fingerprint:
        raise A6ReplayIntegrityError(
            A6ErrorCode.INVALID_ASSESSMENT,
            "A6 assessment replay differs from recorded result",
        )
    return replayed
