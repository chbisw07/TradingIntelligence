"""Observational A2/A3 comparison; no winner, scalar merge or arbitration."""

from datetime import datetime

from tiaf.agents import AgentStance, SpecialistId
from tiaf.baseline import BaselineDirection, CandidateClass
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.planner.digests import digest
from tiaf.service.opportunity_intelligence import (
    IntelligenceRunRecord,
    OpportunityState,
    replay_intelligence,
)

from .contracts import (
    A2A3ComparisonRecord,
    A2Side,
    A3Side,
    AdditionCategory,
    AdditionStatus,
    BlobKind,
    DirectionAxis,
    DisagreementClass,
    InformationAddition,
    OpportunityAxis,
    PortableA3ReplayPackage,
)
from .package import package_blob, validate_package


def direction_axis(
    a2: BaselineDirection | None,
    a3: AgentStance,
    *,
    comparable: bool = True,
) -> DirectionAxis:
    if not comparable or a2 is None:
        return DirectionAxis.NON_COMPARABLE
    if a2 is BaselineDirection.CONFLICTED:
        return DirectionAxis.A2_CONFLICTED
    if a3 in {AgentStance.ABSTAIN, AgentStance.INSUFFICIENT_EVIDENCE}:
        return DirectionAxis.A3_INSUFFICIENT
    if a2 is BaselineDirection.NEUTRAL and a3 in {
        AgentStance.POSITIVE,
        AgentStance.NEGATIVE,
    }:
        return DirectionAxis.A3_DIRECTIONAL_A2_NEUTRAL
    if (a2.value, a3.value) in {("POSITIVE", "POSITIVE"), ("NEGATIVE", "NEGATIVE")}:
        return DirectionAxis.ALIGNED
    if a2 in {BaselineDirection.POSITIVE, BaselineDirection.NEGATIVE} and a3 in {
        AgentStance.POSITIVE,
        AgentStance.NEGATIVE,
    }:
        return DirectionAxis.OPPOSED
    return DirectionAxis.NON_COMPARABLE


def opportunity_axis(
    a2: CandidateClass | None,
    a3: OpportunityState,
    *,
    comparable: bool = True,
) -> OpportunityAxis:
    if not comparable or a2 is None:
        return OpportunityAxis.NON_COMPARABLE
    if a3 is OpportunityState.INSUFFICIENT_EVIDENCE:
        return OpportunityAxis.A3_EVIDENCE_INSUFFICIENT
    if a2 in {CandidateClass.TOP_MOVER, CandidateClass.EARLY_OPPORTUNITY}:
        if a3 is OpportunityState.OPPORTUNITY:
            return OpportunityAxis.ALIGNED_OPPORTUNITY
        if a3 in {OpportunityState.WAIT, OpportunityState.AVOID, OpportunityState.CONFLICTED}:
            return OpportunityAxis.A3_RESTRICTION_ADDED
    if a2 is CandidateClass.MATURE_AVOID_CHASE and a3 is OpportunityState.WAIT:
        return OpportunityAxis.ALIGNED_TIMING_CAUTION
    if a2 is CandidateClass.NO_TRADE:
        if a3 is OpportunityState.WATCH:
            return OpportunityAxis.BASELINE_NO_TRADE_WATCH
        if a3 is OpportunityState.NO_TRADE:
            return OpportunityAxis.BASELINE_NO_TRADE_PRESERVED
    return OpportunityAxis.SEMANTIC_DIVERGENCE


def _additions(record: IntelligenceRunRecord) -> tuple[InformationAddition, ...]:
    result = record.result
    contributions = {c.specialist: c for c in result.contributions}

    def contribution_status(*specialists: SpecialistId) -> tuple[AdditionStatus, tuple[str, ...]]:
        selected = tuple(contributions[s] for s in specialists if s in contributions)
        refs = tuple(sorted(c.opinion_id for c in selected if c.opinion_id))
        if any(c.applicability == "UNKNOWN" or c.usable.value == "UNKNOWN" for c in selected):
            return AdditionStatus.UNKNOWN, refs
        if any(c.opinion_id and c.applicability == "APPLICABLE" for c in selected):
            return AdditionStatus.PRESENT, refs
        return AdditionStatus.ABSENT, refs

    additions: list[InformationAddition] = []
    for category, specialists in (
        (AdditionCategory.COMPANY_QUALITY, (SpecialistId.FUNDAMENTAL,)),
        (AdditionCategory.EVENT_CATALYST_CONTEXT, (SpecialistId.NEWS_EVENT,)),
        (AdditionCategory.SECTOR_MACRO_CONTEXT, (SpecialistId.SECTOR, SpecialistId.MACRO)),
        (AdditionCategory.DERIVATIVES_CONTEXT, (SpecialistId.DERIVATIVES_CONTEXT,)),
    ):
        status, refs = contribution_status(*specialists)
        additions.append(InformationAddition(category=category, status=status, source_refs=refs))
    additions.extend(
        (
            InformationAddition(
                category=AdditionCategory.EXTENSION_TIMING_RESTRICTION,
                status=(
                    AdditionStatus.PRESENT
                    if result.summary.state is OpportunityState.WAIT
                    else AdditionStatus.ABSENT
                ),
                source_refs=tuple(r.reason_id for r in result.reasons if r.code == "AVOID_CHASE"),
            ),
            InformationAddition(
                category=AdditionCategory.EVIDENCE_INSUFFICIENCY,
                status=(
                    AdditionStatus.PRESENT
                    if result.summary.state is OpportunityState.INSUFFICIENT_EVIDENCE
                    else AdditionStatus.ABSENT
                ),
                source_refs=tuple(sorted(result.completeness.gaps)),
            ),
            InformationAddition(
                category=AdditionCategory.SOURCE_CONTRADICTION_CONFIRMATION,
                status=(AdditionStatus.PRESENT if result.contradictions else AdditionStatus.ABSENT),
                source_refs=tuple(sorted(c.contradiction_id for c in result.contradictions)),
            ),
            InformationAddition(
                category=AdditionCategory.EXPLICIT_MISSING_EVIDENCE,
                status=(AdditionStatus.PRESENT if result.prerequisites else AdditionStatus.ABSENT),
                source_refs=tuple(sorted(p.requirement_id for p in result.prerequisites)),
            ),
            InformationAddition(
                category=AdditionCategory.RISK_RESTRICTION,
                status=(
                    AdditionStatus.PRESENT
                    if result.summary.risk and result.summary.risk.value in {"HIGH", "CRITICAL"}
                    else AdditionStatus.ABSENT
                ),
                source_refs=(
                    (result.summary.risk.source.opinion_id,)
                    if result.summary.risk and result.summary.risk.source.opinion_id
                    else ()
                ),
            ),
            InformationAddition(
                category=AdditionCategory.PRESERVED_SPECIALIST_DISAGREEMENT,
                status=(AdditionStatus.PRESENT if result.contradictions else AdditionStatus.ABSENT),
                source_refs=tuple(sorted(c.contradiction_id for c in result.contradictions)),
            ),
        )
    )
    return tuple(additions)


def compare_a2_a3(
    package: PortableA3ReplayPackage, *, compared_at: datetime | None = None
) -> A2A3ComparisonRecord:
    package = validate_package(package)
    record = replay_intelligence(package_blob(package, BlobKind.A39_CAPTURE).content)
    result = record.result
    baseline = result.baseline
    a2 = A2Side(
        assessment_id=baseline.assessment_id,
        evidence_fingerprint=baseline.evidence_fingerprint,
        capture_mode=package.manifest.a2_capture.mode,
        direction=baseline.direction,
        candidate_class=baseline.candidate_class,
        opportunity_score=baseline.opportunity_score,
        eligible=baseline.eligible,
        eligibility_basis=baseline.eligibility_basis,
        reason_refs=baseline.evidence_ids,
        warnings=(baseline.captured_assessment.warnings if baseline.captured_assessment else ()),
    )
    a3 = A3Side(
        intelligence_id=result.intelligence_id,
        fingerprint=record.fingerprint,
        state=result.summary.state,
        price_direction=result.summary.bias.price_direction,
        qualified_bias=result.summary.bias.headline,
        quality=result.summary.quality.value if result.summary.quality else None,
        risk=result.summary.risk.value if result.summary.risk else None,
        maturity=result.summary.maturity.value if result.summary.maturity else None,
        extension=result.summary.extension.value if result.summary.extension else None,
        remaining_room=tuple(f.value for f in result.summary.remaining_room),
        completeness_numerator=result.completeness.numerator,
        completeness_denominator=result.completeness.denominator,
        gaps=result.completeness.gaps,
        contradiction_ids=tuple(c.contradiction_id for c in result.contradictions),
        reason_refs=tuple(r.reason_id for r in result.reasons),
    )
    d_axis = direction_axis(a2.direction, a3.price_direction)
    o_axis = opportunity_axis(a2.candidate_class, a3.state)
    disagreements: list[DisagreementClass] = []
    if d_axis is DirectionAxis.ALIGNED and o_axis in {
        OpportunityAxis.ALIGNED_OPPORTUNITY,
        OpportunityAxis.ALIGNED_TIMING_CAUTION,
        OpportunityAxis.BASELINE_NO_TRADE_PRESERVED,
    }:
        disagreements.append(DisagreementClass.ALIGNED)
    if d_axis is DirectionAxis.OPPOSED:
        disagreements.append(DisagreementClass.DIRECTION_CONFLICT)
    if o_axis is OpportunityAxis.A3_RESTRICTION_ADDED:
        disagreements.append(DisagreementClass.A3_MORE_CONSERVATIVE)
        if a3.state is OpportunityState.WAIT:
            disagreements.append(DisagreementClass.TIMING_CONFLICT)
    if o_axis is OpportunityAxis.BASELINE_NO_TRADE_WATCH:
        disagreements.extend(
            (
                DisagreementClass.A3_MORE_PERMISSIVE,
                DisagreementClass.BASELINE_NO_TRADE_PRESERVED,
            )
        )
    elif a2.candidate_class is CandidateClass.NO_TRADE:
        disagreements.append(DisagreementClass.BASELINE_NO_TRADE_PRESERVED)
    if a3.gaps:
        disagreements.append(DisagreementClass.EVIDENCE_GAP_DIFFERENCE)
    if a3.risk in {"HIGH", "CRITICAL"} or a3.contradiction_ids:
        disagreements.append(DisagreementClass.RISK_CONTEXT_DIFFERENCE)
    if a3.state is OpportunityState.INSUFFICIENT_EVIDENCE:
        disagreements.append(DisagreementClass.INSUFFICIENT_EVIDENCE)
    if d_axis is DirectionAxis.NON_COMPARABLE or o_axis is OpportunityAxis.NON_COMPARABLE:
        disagreements.append(DisagreementClass.NON_COMPARABLE)
    when = compared_at or datetime.now(TIAF_TIMEZONE)
    additions = _additions(record)
    roots = tuple(sorted({root for group in result.lineages for root in group.roots}))
    payload = {
        "a2": a2.model_dump(mode="json"),
        "a3": a3.model_dump(mode="json"),
        "direction_axis": d_axis,
        "opportunity_axis": o_axis,
        "disagreements": disagreements,
        "information_additions": [x.model_dump(mode="json") for x in additions],
        "common_evidence_roots": roots,
        "policy": "a3.10-observational-comparison-v1/1.0",
    }
    fingerprint = digest(payload)
    return A2A3ComparisonRecord(
        comparison_id=f"a2-a3:{fingerprint[:24]}",
        package_id=package.manifest.package_id,
        subject=result.subject,
        horizon=result.horizon,
        as_of=result.as_of,
        a2=a2,
        a3=a3,
        direction_axis=d_axis,
        opportunity_axis=o_axis,
        disagreements=tuple(disagreements),
        information_additions=additions,
        common_evidence_roots=roots,
        compared_at=when,
        fingerprint=fingerprint,
    )
