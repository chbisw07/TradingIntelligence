"""Versioned finite observation rules. No weights, votes, inference or execution."""

from tiaf.agents import AgentStance, SpecialistId
from tiaf.baseline.enums import CandidateClass
from tiaf.contracts import DataQuality, FreshnessState, TradeStyle

from .contracts import (
    BaselineView,
    BiasSummary,
    CompletenessProfile,
    Contradiction,
    Facet,
    FieldMapping,
    OpportunityState,
    OpportunitySummary,
    OpportunitySynthesisPolicy,
    PredicateTrace,
    RuleTrace,
    SourceLocator,
    SpecialistContribution,
    Truth,
)


def default_policy() -> OpportunitySynthesisPolicy:
    rows = (
        (
            "TECHNICAL",
            "structure_state",
            ("BULLISH_STRUCTURE", "BEARISH_STRUCTURE", "BREAKOUT_ATTEMPT", "BREAKDOWN_ATTEMPT"),
            "SUPPORT",
        ),
        ("TECHNICAL", "extension_state", ("EXTENDED", "EXHAUSTION_RISK"), "CHASE"),
        ("TECHNICAL", "remaining_room", ("LIMITED", "MINIMAL"), "CHASE"),
        ("TECHNICAL", "momentum_state", ("MIXED", "FADING_POSITIVE", "FADING_NEGATIVE"), "TIMING"),
        ("TECHNICAL", "structure_state", ("MIXED", "RANGE_BOUND"), "TIMING"),
        ("FUNDAMENTAL", "company_quality", ("HIGH_QUALITY", "GOOD_QUALITY"), "SUPPORT"),
        ("FUNDAMENTAL", "company_quality", ("WEAK", "DETERIORATING"), "COMPANY_CONFLICT"),
        ("FUNDAMENTAL", "balance_sheet_state", ("DISTRESSED_RISK",), "COMPANY_CONFLICT"),
        ("FUNDAMENTAL", "valuation_state", ("EXPENSIVE", "VERY_EXPENSIVE"), "QUALIFICATION"),
        ("SECTOR", "sector_state", ("WEAK", "VERY_WEAK", "MIXED"), "QUALIFICATION"),
        ("RELATIVE_STRENGTH", "stance", ("NEGATIVE", "MIXED"), "QUALIFICATION"),
        ("MACRO", "stance", ("NEGATIVE", "MIXED"), "QUALIFICATION"),
        ("DERIVATIVES_CONTEXT", "liquidity_state", ("WEAK", "MIXED"), "QUALIFICATION"),
    )
    return OpportunitySynthesisPolicy(
        mappings=tuple(
            FieldMapping.model_validate(
                {
                    "specialist": sid,
                    "field": field,
                    "values": values,
                    "effect": effect,
                }
            )
            for sid, field, values, effect in rows
        )
    )


def require_supported_policy(policy: OpportunitySynthesisPolicy) -> None:
    if policy != default_policy():
        raise ValueError(
            "unsupported synthesis policy snapshot; compare under an explicitly implemented version"
        )


def conjunction(*values: Truth) -> Truth:
    if Truth.FALSE in values:
        return Truth.FALSE
    return Truth.UNKNOWN if Truth.UNKNOWN in values else Truth.TRUE


def disjunction(*values: Truth) -> Truth:
    if Truth.TRUE in values:
        return Truth.TRUE
    return Truth.UNKNOWN if Truth.UNKNOWN in values else Truth.FALSE


def tf(value: bool) -> Truth:
    return Truth.TRUE if value else Truth.FALSE


def facet(contributions: tuple[SpecialistContribution, ...], sid: str, field: str) -> Facet | None:
    return next(
        (
            f
            for c in contributions
            if c.specialist.value == sid
            for f in c.facets
            if f.field == field
        ),
        None,
    )


def evaluate(
    policy: OpportunitySynthesisPolicy,
    baseline: BaselineView,
    contributions: tuple[SpecialistContribution, ...],
    coverage: CompletenessProfile,
    conflicts: tuple[Contradiction, ...],
    style: TradeStyle,
) -> tuple[
    OpportunitySummary, tuple[PredicateTrace, ...], tuple[RuleTrace, ...], tuple[Contradiction, ...]
]:
    require_supported_policy(policy)
    by_id = {c.specialist: c for c in contributions}
    all_sources = tuple(f.source for c in contributions for f in c.facets)
    traces: list[PredicateTrace] = []
    effects: dict[str, list[Facet]] = {}
    for mapping in policy.mappings:
        f = facet(contributions, mapping.specialist.value, mapping.field)
        value = (
            Truth.UNKNOWN
            if f is None or f.usable is not Truth.TRUE
            else tf(f.value in mapping.values)
        )
        traces.append(
            PredicateTrace(
                predicate=f"field:{mapping.specialist}.{mapping.field}:{mapping.effect}",
                value=value,
                sources=(f.source,)
                if f
                else (SourceLocator(specialist=mapping.specialist, field=mapping.field),),
                reason_codes=(mapping.effect,),
            )
        )
        if value is Truth.TRUE and f is not None:
            effects.setdefault(mapping.effect, []).append(f)

    def check(sid: str, field: str, values: set[str]) -> Truth:
        f = facet(contributions, sid, field)
        return Truth.UNKNOWN if f is None or f.usable is not Truth.TRUE else tf(f.value in values)

    # A cited Quality family summarizes underlying support, never an extra vote.
    family_support = tuple(
        f
        for c in contributions
        if c.specialist is SpecialistId.OPPORTUNITY_QUALITY
        for f in c.facets
        if f.field.startswith("supportive_families.") and f.usable is Truth.TRUE
    )
    support = tf(bool(effects.get("SUPPORT")) or bool(family_support))
    if support is Truth.FALSE and not any(
        c.usable is Truth.TRUE and c.role == "FIRST_ORDER" for c in contributions
    ):
        support = Truth.UNKNOWN
    company_conflict = (
        bool(effects.get("COMPANY_CONFLICT"))
        and style is TradeStyle.POSITIONAL
        and support is Truth.TRUE
    )
    new_conflicts = list(conflicts)
    if company_conflict:
        new_conflicts.append(
            Contradiction(
                contradiction_id="company-context",
                kind="CROSS_DOMAIN_TENSION",
                code="MATERIAL_COMPANY_QUALITY_TENSION",
                blocking=Truth.TRUE,
                sources=tuple(f.source for f in effects["COMPANY_CONFLICT"]),
            )
        )
    technical = facet(contributions, "TECHNICAL", "stance")
    price = AgentStance.INSUFFICIENT_EVIDENCE
    if technical and technical.usable is Truth.TRUE:
        price = AgentStance(technical.value)
    elif technical and technical.value == "ABSTAIN":
        price = AgentStance.ABSTAIN
    comparable_conflict = price is AgentStance.MIXED
    if comparable_conflict and technical:
        new_conflicts.append(
            Contradiction(
                contradiction_id="price-direction",
                kind="SAME_PROPOSITION",
                code="MIXED_PRICE_DIRECTION",
                blocking=Truth.TRUE,
                sources=(technical.source,),
            )
        )
    news = next(
        (
            c
            for c in contributions
            if c.specialist == SpecialistId.NEWS_EVENT and c.applicability == "APPLICABLE"
        ),
        None,
    )
    event_risk = (
        conjunction(
            check("NEWS_EVENT", "materiality", {"HIGH", "CRITICAL"}),
            check("NEWS_EVENT", "execution_risk", {"HIGH"}),
        )
        if news
        else Truth.FALSE
    )
    if (
        news
        and check("NEWS_EVENT", "contradiction_state", {"SOURCE_CONFLICT", "DISPUTED"})
        is Truth.TRUE
    ):
        sources = tuple(f.source for f in news.facets if f.field == "contradiction_state")
        new_conflicts.append(
            Contradiction(
                contradiction_id="news-source",
                kind="SOURCE_DISCREPANCY",
                code="DISPUTED_EVENT_GATE",
                blocking=Truth.TRUE,
                sources=sources,
            )
        )
    blocking = disjunction(
        *(c.blocking for c in new_conflicts if c.kind != "BASELINE_DISAGREEMENT")
    )
    qualified = (
        AgentStance.MIXED
        if blocking is Truth.TRUE and price in {AgentStance.POSITIVE, AgentStance.NEGATIVE}
        else price
    )
    bias = BiasSummary(
        headline=qualified,
        price_direction=price,
        domain_views=tuple((c.specialist, c.stance) for c in contributions if c.stance is not None),
        sources=(technical.source,) if technical else (),
    )
    core = conjunction(
        tf(baseline.availability == "CAPTURED_PROJECTION"),
        *(by_id[s].usable if s in by_id else Truth.UNKNOWN for s in policy.core),
    )
    critical = check("OPPORTUNITY_RISK", "risk_level", {"CRITICAL"})
    timing = disjunction(
        tf(bool(effects.get("CHASE"))),
        tf(bool(effects.get("TIMING")) and support is Truth.TRUE),
        event_risk,
        check("OPPORTUNITY_RISK", "risk_level", {"HIGH"}),
    )
    required = tuple(c for c in contributions if c.required and c.applicability == "APPLICABLE")
    coverage_ok = conjunction(
        *(c.usable for c in required),
        tf(bool(required)),
        tf(not coverage.unknown_applicability),
        tf(not any(c.material_missing_ids for c in contributions)),
        tf(
            all(
                c.quality is DataQuality.GOOD and c.freshness is FreshnessState.FRESH
                for c in required
            )
        ),
    )
    low_risk = check("OPPORTUNITY_RISK", "risk_level", {"LOW", "MODERATE"})
    complete = conjunction(
        core,
        coverage_ok,
        low_risk,
        check("OPPORTUNITY_QUALITY", "quality_state", {"STRONG", "GOOD"}),
        tf(qualified in {AgentStance.POSITIVE, AgentStance.NEGATIVE}),
        tf(blocking is Truth.FALSE),
        tf(timing is Truth.FALSE),
        tf(not effects.get("QUALIFICATION")),
        tf(not any(c.blocking is Truth.UNKNOWN for c in new_conflicts)),
    )
    baseline_no_trade = (
        tf(baseline.candidate_class == CandidateClass.NO_TRADE)
        if baseline.candidate_class is not None
        else Truth.UNKNOWN
    )
    row5_watch = conjunction(
        support, tf(qualified in {AgentStance.POSITIVE, AgentStance.NEGATIVE}), low_risk
    )
    predicates = {
        "core_available": core,
        "support_present": support,
        "blocking_conflict": blocking,
        "critical_risk": critical,
        "timing_restriction": timing,
        "coverage_complete": coverage_ok,
        "complete_for_opportunity": complete,
        "baseline_no_trade": baseline_no_trade,
        "row5_watch": row5_watch,
    }
    for name, value in predicates.items():
        traces.append(
            PredicateTrace(
                predicate=name,
                value=value,
                sources=all_sources
                + (SourceLocator(field="baseline", evidence_ids=baseline.evidence_ids),),
                reason_codes=(name.upper(),),
            )
        )
    rules = (
        RuleTrace(
            rule_id="CORE_UNUSABLE",
            value=tf(core is not Truth.TRUE),
            state=OpportunityState.INSUFFICIENT_EVIDENCE,
            predicates=("core_available",),
        ),
        RuleTrace(
            rule_id="UNRESOLVED_CONFLICT",
            value=blocking,
            state=OpportunityState.CONFLICTED,
            predicates=("blocking_conflict",),
        ),
        RuleTrace(
            rule_id="CRITICAL_RISK",
            value=critical,
            state=OpportunityState.AVOID,
            predicates=("critical_risk",),
        ),
        RuleTrace(
            rule_id="TIMING_RESTRICTION",
            value=timing,
            state=OpportunityState.WAIT,
            predicates=("timing_restriction",),
        ),
        RuleTrace(
            rule_id="BASELINE_NO_TRADE",
            value=baseline_no_trade,
            state=OpportunityState.WATCH if row5_watch is Truth.TRUE else OpportunityState.NO_TRADE,
            predicates=("baseline_no_trade", "row5_watch"),
        ),
        RuleTrace(
            rule_id="SUPPORTED_SETUP",
            value=conjunction(complete, support, tf(baseline_no_trade is Truth.FALSE)),
            state=OpportunityState.OPPORTUNITY,
            predicates=("complete_for_opportunity", "support_present", "baseline_no_trade"),
        ),
        RuleTrace(
            rule_id="QUALIFIED_SUPPORT",
            value=conjunction(support, tf(complete is not Truth.TRUE)),
            state=OpportunityState.WATCH,
            predicates=("support_present", "complete_for_opportunity"),
        ),
        RuleTrace(
            rule_id="NO_SUPPORTED_SETUP",
            value=conjunction(core, tf(support is not Truth.TRUE)),
            state=OpportunityState.NO_TRADE,
            predicates=("core_available", "support_present"),
        ),
    )
    matched = tuple(r for r in rules if r.value is Truth.TRUE)
    if not matched:
        raise ValueError("policy has no terminal observation rule")
    summary = OpportunitySummary(
        state=matched[0].state,
        primary_rule=matched[0].rule_id,
        matched_rules=tuple(r.rule_id for r in matched),
        bias=bias,
        quality=facet(contributions, "OPPORTUNITY_QUALITY", "quality_state"),
        risk=facet(contributions, "OPPORTUNITY_RISK", "risk_level"),
        maturity=facet(contributions, "OPPORTUNITY_QUALITY", "maturity_state"),
        extension=facet(contributions, "TECHNICAL", "extension_state"),
        remaining_room=tuple(
            f for c in contributions for f in c.facets if f.field == "remaining_room"
        ),
    )
    return (
        summary,
        tuple(traces),
        rules,
        tuple(sorted(new_conflicts, key=lambda c: c.contradiction_id)),
    )
