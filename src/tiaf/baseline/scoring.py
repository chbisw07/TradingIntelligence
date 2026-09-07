"""Pure policy-driven scoring for the deterministic A2.9 benchmark."""

from dataclasses import dataclass
from uuid import NAMESPACE_URL, uuid5

from tiaf.contracts import DataQuality, FreshnessState
from tiaf.contracts.common import Metadata
from tiaf.features import FeatureBundle, FeatureResult, FeatureStatus
from tiaf.indicators import IndicatorBundle, IndicatorResult

from .enums import (
    BaselineDirection,
    BaselineEvidenceSource,
    CandidateClass,
    ComponentName,
    ExplanationCode,
    RuleRole,
    ScoreSemantics,
    TransformKind,
)
from .models import (
    BaselinePolicy,
    DeterministicBaselineRequest,
    EvidenceContribution,
    EvidenceRule,
    MarketStateAssessment,
    OpportunityAssessment,
    ScoreComponent,
    finite,
    worst_quality,
)

_USABLE = {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}


@dataclass(frozen=True)
class _ResolvedRule:
    rule: EvidenceRule
    contribution: EvidenceContribution | None
    missing_key: str | None


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return min(upper, max(lower, finite(value)))


def _transform(rule: EvidenceRule, value: float) -> float:
    kind = rule.transform
    if kind is TransformKind.SIGNED_LINEAR:
        assert rule.scale is not None
        return _clamp(value / rule.scale, -1.0, 1.0) * rule.orientation
    if kind is TransformKind.CENTERED_LINEAR:
        assert rule.center is not None and rule.scale is not None
        return _clamp((value - rule.center) / rule.scale, -1.0, 1.0) * rule.orientation
    if kind is TransformKind.UNSIGNED_LINEAR:
        assert rule.floor is not None and rule.ceiling is not None
        score = _clamp((value - rule.floor) / (rule.ceiling - rule.floor))
        return score * rule.orientation
    if kind is TransformKind.LOWER_BETTER:
        assert rule.floor is not None and rule.ceiling is not None
        return 1.0 - _clamp((value - rule.floor) / (rule.ceiling - rule.floor))
    if kind is TransformKind.TRIANGLE:
        assert rule.floor is not None and rule.target is not None and rule.ceiling is not None
        if value <= rule.floor or value >= rule.ceiling:
            return 0.0
        if value <= rule.target:
            return _clamp((value - rule.floor) / (rule.target - rule.floor))
        return _clamp((rule.ceiling - value) / (rule.ceiling - rule.target))
    if kind is TransformKind.POSITIVE_ROOM:
        assert rule.scale is not None and rule.ceiling is not None
        if value <= 0:
            return _clamp(-value / rule.scale)
        return rule.post_boundary_credit * (1.0 - _clamp(value / rule.ceiling))
    assert kind is TransformKind.NEGATIVE_ROOM
    assert rule.scale is not None and rule.ceiling is not None
    if value >= 0:
        return _clamp(value / rule.scale)
    return rule.post_boundary_credit * (1.0 - _clamp(-value / rule.ceiling))


def _effective_quality(status: FeatureStatus, quality: DataQuality) -> DataQuality:
    if status is FeatureStatus.PARTIAL and quality is DataQuality.GOOD:
        return DataQuality.PARTIAL
    return quality


def _feature_result(
    bundle: FeatureBundle | None,
    rule: EvidenceRule,
) -> FeatureResult | None:
    if bundle is None:
        return None
    matches = tuple(
        item
        for item in bundle.results
        if item.request.feature_id == rule.selector.evidence_id
        and item.request.parameters == rule.selector.parameters
    )
    return matches[0] if len(matches) == 1 else None


def _indicator_result(
    bundle: IndicatorBundle | None,
    rule: EvidenceRule,
) -> IndicatorResult | None:
    if bundle is None:
        return None
    matches = tuple(
        item
        for item in bundle.results
        if item.indicator_id == rule.selector.evidence_id
        and item.parameters == rule.selector.parameters
    )
    return matches[0] if len(matches) == 1 else None


def _source_bundle(
    request: DeterministicBaselineRequest,
    source: BaselineEvidenceSource,
) -> FeatureBundle | None:
    return {
        BaselineEvidenceSource.PRIMARY: request.primary_features,
        BaselineEvidenceSource.RELATIVE: request.relative_features,
        BaselineEvidenceSource.MULTI_TIMEFRAME: request.multi_timeframe_features,
        BaselineEvidenceSource.DERIVATIVES: request.derivatives_features,
    }.get(source)


def _freshness(
    request: DeterministicBaselineRequest,
    source: BaselineEvidenceSource,
) -> FreshnessState:
    return next(item.state for item in request.evidence_freshness if item.source is source)


def _evidence_key(rule: EvidenceRule) -> str:
    parameters = ",".join(f"{name}={value}" for name, value in rule.selector.parameters)
    suffix = f"[{parameters}]" if parameters else ""
    output = f".{rule.selector.output_name}" if rule.selector.output_name else ""
    return f"{rule.selector.source.value}:{rule.selector.evidence_id}{output}{suffix}"


def _resolve_rule(
    request: DeterministicBaselineRequest,
    policy: BaselinePolicy,
    rule: EvidenceRule,
) -> _ResolvedRule:
    key = _evidence_key(rule)
    try:
        freshness = _freshness(request, rule.selector.source)
    except StopIteration:
        return _ResolvedRule(rule, None, key)
    if freshness is FreshnessState.STALE:
        return _ResolvedRule(rule, None, key)
    raw: int | float | None = None
    status: FeatureStatus
    quality: DataQuality
    as_of = request.requested_at
    context_id: str
    source_evidence: tuple[str, ...]
    evidence_warnings: tuple[str, ...]
    evidence_metadata: Metadata
    if rule.selector.source is BaselineEvidenceSource.INDICATOR:
        indicator_result = _indicator_result(request.indicators, rule)
        if indicator_result is None:
            return _ResolvedRule(rule, None, key)
        status = indicator_result.status
        quality = indicator_result.quality
        as_of = indicator_result.as_of
        context_id = indicator_result.source_context_id
        source_evidence = indicator_result.source_evidence
        evidence_warnings = indicator_result.warnings
        evidence_metadata = dict(indicator_result.metadata)
        assert rule.selector.output_name is not None
        raw = indicator_result.value(rule.selector.output_name)
    else:
        feature_result = _feature_result(_source_bundle(request, rule.selector.source), rule)
        if feature_result is None:
            return _ResolvedRule(rule, None, key)
        status = feature_result.status
        quality = feature_result.quality
        as_of = feature_result.as_of
        context_id = feature_result.source_context_id
        source_evidence = feature_result.source_evidence
        evidence_warnings = feature_result.warnings
        evidence_metadata = dict(feature_result.metadata)
        if isinstance(feature_result.value, (int, float)) and not isinstance(
            feature_result.value, bool
        ):
            raw = feature_result.value
    if status not in _USABLE or raw is None:
        return _ResolvedRule(rule, None, key)
    quality = _effective_quality(status, quality)
    signal = _transform(rule, float(raw))
    weighted = signal * rule.weight * policy.quality_factor(quality)
    codes: tuple[ExplanationCode, ...] = ()
    if abs(signal) >= rule.code_threshold and signal > 0 and rule.positive_code is not None:
        codes = (rule.positive_code,)
    elif abs(signal) >= rule.code_threshold and signal < 0 and rule.negative_code is not None:
        codes = (rule.negative_code,)
    contribution = EvidenceContribution(
        rule_id=rule.rule_id,
        component=rule.component,
        source=rule.selector.source,
        evidence_id=key,
        source_context_id=context_id,
        source_evidence=source_evidence,
        as_of=as_of,
        raw_value=float(raw),
        normalized_signal=signal,
        weighted_signal=weighted,
        quality=quality,
        freshness=freshness,
        explanation_codes=codes,
        warnings=evidence_warnings,
        metadata=evidence_metadata,
    )
    return _ResolvedRule(rule, contribution, None)


def _directional_scores(items: tuple[_ResolvedRule, ...]) -> tuple[float | None, float | None]:
    directional = tuple(
        (item.rule, item.contribution)
        for item in items
        if item.contribution is not None and item.rule.role is RuleRole.DIRECTIONAL
    )
    if not directional:
        return None, None
    signed_transforms = {TransformKind.SIGNED_LINEAR, TransformKind.CENTERED_LINEAR}
    positive_denominator = sum(
        rule.weight
        for rule, _ in directional
        if rule.transform in signed_transforms or rule.orientation > 0
    )
    negative_denominator = sum(
        rule.weight
        for rule, _ in directional
        if rule.transform in signed_transforms or rule.orientation < 0
    )
    positive = sum(max(contribution.weighted_signal, 0.0) for _, contribution in directional)
    negative = sum(max(-contribution.weighted_signal, 0.0) for _, contribution in directional)
    return (
        positive / positive_denominator * 100.0 if positive_denominator else None,
        negative / negative_denominator * 100.0 if negative_denominator else None,
    )


def _component_score(
    items: tuple[_ResolvedRule, ...],
    direction: BaselineDirection,
) -> float | None:
    usable: list[tuple[float, float]] = []
    for item in items:
        contribution = item.contribution
        if contribution is None:
            continue
        signal = contribution.weighted_signal / item.rule.weight
        if item.rule.transform is TransformKind.POSITIVE_ROOM:
            if direction is not BaselineDirection.POSITIVE:
                continue
            value = max(signal, 0.0)
        elif item.rule.transform is TransformKind.NEGATIVE_ROOM:
            if direction is not BaselineDirection.NEGATIVE:
                continue
            value = max(signal, 0.0)
        elif item.rule.role is RuleRole.DIRECTIONAL:
            if direction is BaselineDirection.POSITIVE:
                if (
                    item.rule.transform is TransformKind.UNSIGNED_LINEAR
                    and item.rule.orientation < 0
                ):
                    continue
                value = max(signal, 0.0)
            elif direction is BaselineDirection.NEGATIVE:
                if (
                    item.rule.transform is TransformKind.UNSIGNED_LINEAR
                    and item.rule.orientation > 0
                ):
                    continue
                value = max(-signal, 0.0)
            else:
                value = abs(signal)
        elif item.rule.role is RuleRole.PENALTY:
            if all(candidate.rule.role is RuleRole.PENALTY for candidate in items):
                value = abs(signal)
            else:
                value = 1.0 - abs(signal)
        else:
            value = max(signal, 0.0)
        usable.append((value, item.rule.weight))
    if not usable:
        return None
    numerator = sum(value * weight for value, weight in usable)
    return numerator / sum(weight for _, weight in usable) * 100.0


def _semantics(items: tuple[_ResolvedRule, ...]) -> ScoreSemantics:
    roles = {item.rule.role for item in items}
    if roles == {RuleRole.PENALTY}:
        return ScoreSemantics.PENALTY
    if RuleRole.DIRECTIONAL in roles or any(
        item.rule.transform in {TransformKind.POSITIVE_ROOM, TransformKind.NEGATIVE_ROOM}
        for item in items
    ):
        return ScoreSemantics.DIRECTIONAL_SUPPORT
    return ScoreSemantics.SUITABILITY


def _supports_score(
    item: _ResolvedRule,
    direction: BaselineDirection,
) -> bool:
    """Return whether a contribution supplies positive support to the displayed score."""
    contribution = item.contribution
    if contribution is None:
        return False
    signal = contribution.weighted_signal / item.rule.weight
    if item.rule.transform is TransformKind.POSITIVE_ROOM:
        return direction is BaselineDirection.POSITIVE and signal > 0
    if item.rule.transform is TransformKind.NEGATIVE_ROOM:
        return direction is BaselineDirection.NEGATIVE and signal > 0
    if item.rule.role is RuleRole.DIRECTIONAL:
        if direction is BaselineDirection.POSITIVE:
            if item.rule.transform is TransformKind.UNSIGNED_LINEAR and item.rule.orientation < 0:
                return False
            return signal > 0
        if item.rule.transform is TransformKind.UNSIGNED_LINEAR and item.rule.orientation > 0:
            return False
        return signal < 0
    if item.rule.role is RuleRole.PENALTY:
        return False
    return signal > 0


def _score_codes(
    items: tuple[_ResolvedRule, ...],
    component: ComponentName,
    semantics: ScoreSemantics,
    direction: BaselineDirection,
    score: float | None,
    positive: float | None,
    negative: float | None,
    policy: BaselinePolicy,
) -> tuple[ExplanationCode, ...]:
    if score is None:
        return ()
    if component is ComponentName.MULTI_TIMEFRAME_ALIGNMENT:
        conflict = policy.direction_thresholds.component_conflict_score
        if (
            positive is not None
            and negative is not None
            and positive >= conflict
            and negative >= conflict
        ):
            return (ExplanationCode.MTF_CONFLICTED,)
        if score >= policy.classification_thresholds.minimum_alignment:
            return (ExplanationCode.MTF_ALIGNED,)
        return (ExplanationCode.MTF_MIXED,)
    if semantics is not ScoreSemantics.DIRECTIONAL_SUPPORT:
        return tuple(
            dict.fromkeys(
                code
                for item in items
                if item.contribution is not None
                for code in item.contribution.explanation_codes
            )
        )
    return tuple(
        dict.fromkeys(
            code
            for item in items
            if _supports_score(item, direction) and item.contribution is not None
            for code in item.contribution.explanation_codes
        )
    )


def _round(policy: BaselinePolicy, value: float) -> float:
    return round(_clamp(value, 0.0, 100.0), policy.rounding_digits)


def _market_direction(
    policy: BaselinePolicy,
    positive: float,
    negative: float,
) -> BaselineDirection:
    thresholds = policy.direction_thresholds
    margin = positive - negative
    if positive >= thresholds.conflict_score and negative >= thresholds.conflict_score:
        return BaselineDirection.CONFLICTED
    if max(positive, negative) < thresholds.minimum_score:
        return BaselineDirection.NEUTRAL
    if margin >= thresholds.minimum_margin:
        return BaselineDirection.POSITIVE
    if margin <= -thresholds.minimum_margin:
        return BaselineDirection.NEGATIVE
    return BaselineDirection.CONFLICTED


def _quality_penalty(policy: BaselinePolicy, quality: DataQuality) -> float:
    if quality is DataQuality.PARTIAL:
        return policy.penalties.partial_quality_points
    if quality is DataQuality.DEGRADED:
        return policy.penalties.degraded_quality_points
    if quality is DataQuality.UNAVAILABLE:
        return policy.penalties.unavailable_quality_points
    return 0.0


def score_request(
    request: DeterministicBaselineRequest,
    policy: BaselinePolicy,
) -> OpportunityAssessment:
    """Score one immutable evidence request without I/O or wall-clock access."""
    if request.policy_version != policy.policy_version:
        raise ValueError("request policy_version does not match BaselinePolicy")
    if request.trade_style is not policy.trade_style:
        raise ValueError("request trade_style does not match BaselinePolicy")
    resolved = tuple(_resolve_rule(request, policy, rule) for rule in policy.evidence_rules)
    grouped = {
        component: tuple(item for item in resolved if item.rule.component is component)
        for component in ComponentName
    }
    preliminary = {component: _directional_scores(items) for component, items in grouped.items()}
    direction_numerator_positive = 0.0
    direction_numerator_negative = 0.0
    direction_denominator = 0.0
    for weights in policy.component_weights:
        positive, negative = preliminary[weights.component]
        if weights.direction_weight > 0 and positive is not None and negative is not None:
            direction_numerator_positive += weights.direction_weight * positive
            direction_numerator_negative += weights.direction_weight * negative
            direction_denominator += weights.direction_weight
    positive_score = (
        direction_numerator_positive / direction_denominator if direction_denominator else 0.0
    )
    negative_score = (
        direction_numerator_negative / direction_denominator if direction_denominator else 0.0
    )
    direction = _market_direction(policy, positive_score, negative_score)
    dominant = (
        BaselineDirection.POSITIVE
        if positive_score >= negative_score
        else BaselineDirection.NEGATIVE
    )
    component_models: list[ScoreComponent] = []
    for weights in policy.component_weights:
        items = grouped[weights.component]
        positive, negative = preliminary[weights.component]
        contributions = tuple(item.contribution for item in items if item.contribution is not None)
        missing = tuple(item.missing_key for item in items if item.missing_key is not None)
        score = _component_score(items, dominant)
        semantics = _semantics(items)
        item_codes = tuple(
            dict.fromkeys(code for item in contributions for code in item.explanation_codes)
        )
        score_codes = _score_codes(
            items,
            weights.component,
            semantics,
            dominant,
            score,
            positive,
            negative,
            policy,
        )
        component_models.append(
            ScoreComponent(
                component=weights.component,
                semantics=semantics,
                available=score is not None,
                score=None if score is None else _round(policy, score),
                score_basis_direction=(
                    dominant
                    if score is not None and semantics is ScoreSemantics.DIRECTIONAL_SUPPORT
                    else None
                ),
                positive_score=None if positive is None else _round(policy, positive),
                negative_score=None if negative is None else _round(policy, negative),
                quality=worst_quality(tuple(item.quality for item in contributions)),
                contributions=contributions,
                missing_evidence=missing,
                score_explanation_codes=score_codes,
                explanation_codes=item_codes,
            )
        )
    components = tuple(component_models)
    conflict_threshold = policy.direction_thresholds.component_conflict_score
    conflicting_count = sum(
        item.positive_score is not None
        and item.negative_score is not None
        and item.positive_score >= conflict_threshold
        and item.negative_score >= conflict_threshold
        for item in components
    )
    directional_total = positive_score + negative_score
    aligned = (
        max(positive_score, negative_score) / directional_total * 100.0
        if directional_total > 0
        else 0.0
    )
    quality_inputs = [request.primary_features.overall_quality]
    quality_inputs.extend(item.quality for item in components if item.available)
    quality = worst_quality(tuple(quality_inputs))
    required_missing = tuple(
        item for item in resolved if item.rule.required and item.contribution is None
    )
    required_components_missing = tuple(
        item.component
        for item in components
        if policy.weight(item.component).required and not item.available
    )
    freshness = {item.source: item.state for item in request.evidence_freshness}
    stale_critical = tuple(
        source
        for source in policy.critical_freshness_sources
        if freshness.get(source) is FreshnessState.STALE
    )
    warnings: list[str] = []
    assessment_codes: list[ExplanationCode] = []
    supplied_bundles = (
        (BaselineEvidenceSource.PRIMARY, request.primary_features),
        (BaselineEvidenceSource.RELATIVE, request.relative_features),
        (BaselineEvidenceSource.MULTI_TIMEFRAME, request.multi_timeframe_features),
        (BaselineEvidenceSource.DERIVATIVES, request.derivatives_features),
    )
    warnings.extend(
        f"{source.value}: {warning}"
        for source, bundle in supplied_bundles
        if bundle is not None
        for warning in bundle.warnings
    )
    if request.indicators is not None:
        warnings.extend(f"INDICATOR: {warning}" for warning in request.indicators.warnings)
    if required_missing or required_components_missing:
        warnings.append("required baseline evidence is unavailable")
        assessment_codes.append(ExplanationCode.EVIDENCE_MISSING)
    if stale_critical:
        warnings.append("critical evidence is explicitly stale")
        assessment_codes.append(ExplanationCode.EVIDENCE_STALE)
    if quality is DataQuality.PARTIAL:
        assessment_codes.append(ExplanationCode.EVIDENCE_PARTIAL)
    elif quality is DataQuality.DEGRADED:
        assessment_codes.append(ExplanationCode.EVIDENCE_DEGRADED)
    if direction is BaselineDirection.NEUTRAL:
        assessment_codes.append(ExplanationCode.DIRECTION_NEUTRAL)
    elif direction is BaselineDirection.CONFLICTED:
        assessment_codes.append(ExplanationCode.DIRECTION_CONFLICTED)
    if aligned < policy.classification_thresholds.minimum_alignment:
        assessment_codes.append(ExplanationCode.ALIGNMENT_BELOW_THRESHOLD)

    benefit_numerator = 0.0
    benefit_denominator = 0.0
    for item in components:
        weight = policy.weight(item.component).opportunity_weight
        if weight > 0 and item.available and item.score is not None:
            benefit_numerator += weight * item.score
            benefit_denominator += weight
    benefit = benefit_numerator / benefit_denominator if benefit_denominator else 0.0
    extension = next(
        item for item in components if item.component is ComponentName.EXTENSION_CHASE_RISK
    )
    extension_score = extension.score or 0.0
    opportunity = benefit
    opportunity -= policy.penalties.extension_points * extension_score / 100.0
    opportunity -= policy.penalties.conflict_points * (1.0 - aligned / 100.0)
    opportunity -= _quality_penalty(policy, quality)
    opportunity -= sum(
        policy.penalties.aging_freshness_points
        if state is FreshnessState.AGING
        else policy.penalties.unknown_freshness_points
        if state is FreshnessState.UNKNOWN
        else 0.0
        for state in freshness.values()
    )
    opportunity_score = _round(policy, opportunity)
    thresholds = policy.classification_thresholds
    gated = bool(required_missing or required_components_missing or stale_critical)
    gated = gated or direction in {BaselineDirection.NEUTRAL, BaselineDirection.CONFLICTED}
    gated = gated or aligned < thresholds.minimum_alignment
    gated = gated or opportunity_score < thresholds.minimum_opportunity_score
    room = next(item for item in components if item.component is ComponentName.REMAINING_ROOM)
    momentum = next(item for item in components if item.component is ComponentName.MOMENTUM)
    participation = next(
        item for item in components if item.component is ComponentName.PARTICIPATION
    )
    if opportunity_score < thresholds.minimum_opportunity_score:
        assessment_codes.append(ExplanationCode.BELOW_OPPORTUNITY_THRESHOLD)
    if gated:
        candidate_class = CandidateClass.NO_TRADE
    elif extension_score >= thresholds.mature_extension:
        candidate_class = CandidateClass.MATURE_AVOID_CHASE
        assessment_codes.append(ExplanationCode.MATURE_EXTENSION)
    elif room.score is not None and room.score <= thresholds.mature_room:
        candidate_class = CandidateClass.MATURE_AVOID_CHASE
        assessment_codes.extend(
            (ExplanationCode.MATURE_LOW_ROOM, ExplanationCode.LOW_REMAINING_ROOM)
        )
    elif (momentum.score or 0.0) >= thresholds.top_mover_momentum and (
        participation.score or 0.0
    ) >= thresholds.top_mover_participation:
        candidate_class = CandidateClass.TOP_MOVER
    elif opportunity_score >= thresholds.early_opportunity_score:
        candidate_class = CandidateClass.EARLY_OPPORTUNITY
    else:
        candidate_class = CandidateClass.NO_TRADE
        assessment_codes.append(ExplanationCode.BELOW_OPPORTUNITY_THRESHOLD)
    eligible = candidate_class is not CandidateClass.NO_TRADE
    component_codes = tuple(
        code
        for item in components
        for code in (*item.explanation_codes, *item.score_explanation_codes)
    )
    all_codes = tuple(dict.fromkeys((*component_codes, *assessment_codes)))
    state = MarketStateAssessment(
        direction=direction,
        positive_direction_score=_round(policy, positive_score),
        negative_direction_score=_round(policy, negative_score),
        directional_margin=round(positive_score - negative_score, policy.rounding_digits),
        evidence_alignment_score=_round(policy, aligned),
        conflicting_component_count=conflicting_count,
        unavailable_component_count=sum(not item.available for item in components),
        quality=quality,
        components=components,
        explanation_codes=all_codes,
        warnings=tuple(warnings),
    )
    feature_bundles = tuple(
        bundle
        for bundle in (
            request.primary_features,
            request.relative_features,
            request.multi_timeframe_features,
            request.derivatives_features,
        )
        if bundle is not None
    )
    context_ids = tuple(
        dict.fromkeys(
            (
                *(bundle.context_id for bundle in feature_bundles),
                *((request.indicators.context_id,) if request.indicators is not None else ()),
            )
        )
    )
    bundle_ids = tuple(
        dict.fromkeys(
            (
                *(bundle.bundle_id for bundle in feature_bundles),
                *((request.indicators.bundle_id,) if request.indicators is not None else ()),
            )
        )
    )
    identity = f"{request.model_dump_json()}|{policy.model_dump_json()}"
    return OpportunityAssessment(
        assessment_id=str(uuid5(NAMESPACE_URL, f"tiaf:baseline:{identity}")),
        request_id=request.request_id,
        subject=request.subject,
        trade_style=request.trade_style,
        horizon=request.horizon,
        primary_timeframe=request.primary_timeframe,
        supporting_timeframes=request.supporting_timeframes,
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
        market_state=state,
        opportunity_score=opportunity_score,
        maturity_score=_round(policy, extension_score),
        chase_risk_score=_round(policy, extension_score),
        candidate_class=candidate_class,
        eligible=eligible,
        evidence_context_ids=context_ids,
        evidence_bundle_ids=bundle_ids,
        evidence_freshness=request.evidence_freshness,
        created_at=request.requested_at,
        explanation_codes=all_codes,
        warnings=tuple(warnings),
        metadata={
            "benchmark_kind": "deterministic_non_ai",
            "opportunity_base_before_penalties": round(benefit, policy.rounding_digits),
        },
    )
