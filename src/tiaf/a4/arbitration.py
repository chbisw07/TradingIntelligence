"""Explicit deterministic arbitration over structured theses and findings."""

from tiaf.planner.digests import digest
from tiaf.source_semantics import A4SemanticInputProjection

from .contracts import (
    A4DeterministicPolicy,
    ArbitrationFinding,
    ChallengeFinding,
    InvestmentThesis,
)
from .enums import (
    A4Disposition,
    ArbitrationDisposition,
    ChallengeFamily,
    ChallengeStatus,
    Materiality,
    ThesisSupport,
)


class ArbitrationError(ValueError):
    """Fatal deterministic arbitration failure; no disposition is valid."""


def _arbitration_finding(
    challenge: ChallengeFinding,
    primary: InvestmentThesis,
    counter: InvestmentThesis | None,
    policy: A4DeterministicPolicy,
) -> ArbitrationFinding:
    disposition = (
        ArbitrationDisposition.ADMITTED
        if challenge.materiality is Materiality.HARD_CONSTRAINT
        and challenge.status is ChallengeStatus.UPHELD
        else ArbitrationDisposition.REJECTED
        if challenge.status is ChallengeStatus.RESOLVED
        else ArbitrationDisposition.QUALIFIED
        if challenge.status is ChallengeStatus.QUALIFIED
        else ArbitrationDisposition.UNRESOLVED
    )
    thesis_refs: tuple[str, ...] = (primary.thesis_id,)
    if challenge.family is ChallengeFamily.THESIS_TENSION and counter is not None:
        thesis_refs = (primary.thesis_id, counter.thesis_id)
    return ArbitrationFinding(
        finding_id=f"a4-arbitration-finding:{digest((challenge.finding_id, disposition))[:24]}",
        issue_ref=challenge.finding_id,
        thesis_refs=thesis_refs,
        argument_refs=(
            (challenge.challenged_premise_ref,)
            if challenge.challenged_premise_ref is not None
            else ()
        ),
        disposition=disposition,
        rule_id=f"a4-rule:{challenge.family.value.casefold().replace('_', '-')}",
        policy_id=policy.arbitration_policy_id,
        decisive_evidence_refs=tuple(
            sorted(
                {
                    *challenge.cited_support_refs,
                    *challenge.cited_opposition_refs,
                    *challenge.dispute_refs,
                }
            )
        ),
        reason_code=f"ARBITRATED_{challenge.reason_code}",
        dissent_refs=tuple(
            sorted({*challenge.cited_opposition_refs, *challenge.dispute_refs})
        ),
    )


def arbitrate(
    projection: A4SemanticInputProjection,
    policy: A4DeterministicPolicy,
    primary: InvestmentThesis,
    counter: InvestmentThesis | None,
    challenges: tuple[ChallengeFinding, ...],
) -> tuple[A4Disposition, tuple[ArbitrationFinding, ...], tuple[str, ...]]:
    """Apply declared precedence without votes, scalar trust, or confidence averaging."""
    findings = tuple(
        _arbitration_finding(item, primary, counter, policy) for item in challenges
    )
    upheld_material = tuple(
        item
        for item in challenges
        if item.status in {ChallengeStatus.UPHELD, ChallengeStatus.UNEVALUATED}
        and item.materiality in {Materiality.MATERIAL, Materiality.HARD_CONSTRAINT}
    )
    families = {item.family for item in upheld_material}
    reasons = {item.reason_code for item in upheld_material}
    a2_class = projection.opportunity.original_a2_candidate_class
    a39_state = projection.opportunity.a39_state

    if a2_class == "NO_TRADE":
        disposition = A4Disposition.NO_TRADE
        surviving: tuple[str, ...] = ()
    elif "CAPTURED_A3_RISK_VETO" in reasons:
        disposition = A4Disposition.AVOID
        surviving = (counter.thesis_id,) if counter is not None else ()
    elif ChallengeFamily.EVIDENCE_COVERAGE in families or ChallengeFamily.SOURCE_BASIS in families:
        disposition = A4Disposition.INSUFFICIENT_EVIDENCE
        surviving = ()
    elif ChallengeFamily.ASSUMPTION_SUPPORT in families:
        disposition = A4Disposition.ABSTAIN
        surviving = ()
    elif ChallengeFamily.THESIS_TENSION in families:
        if counter is None:
            raise ArbitrationError("material thesis tension requires an explicit counter-thesis")
        disposition = A4Disposition.CONFLICTED
        surviving = (primary.thesis_id, counter.thesis_id)
    elif ChallengeFamily.FRESHNESS in families or ChallengeFamily.TIMING_MATURITY in families:
        disposition = A4Disposition.WAIT
        surviving = (
            (primary.thesis_id, counter.thesis_id)
            if counter is not None and counter.conclusion_relation == "TIMING_ALTERNATIVE"
            else (primary.thesis_id,)
        )
    elif a39_state == "AVOID":
        disposition = A4Disposition.AVOID
        surviving = (counter.thesis_id,) if counter is not None else ()
    elif a39_state == "INSUFFICIENT_EVIDENCE":
        disposition = A4Disposition.INSUFFICIENT_EVIDENCE
        surviving = ()
    elif a39_state == "CONFLICTED":
        if counter is None:
            raise ArbitrationError("conflicted A3 input requires an explicit counter-thesis")
        disposition = A4Disposition.CONFLICTED
        surviving = (primary.thesis_id, counter.thesis_id)
    elif a39_state == "WAIT":
        disposition = A4Disposition.WAIT
        surviving = (primary.thesis_id,)
    elif primary.support in {ThesisSupport.SUPPORTED, ThesisSupport.CONDITIONAL} and a39_state in {
        "OPPORTUNITY",
        "WATCH",
    }:
        disposition = A4Disposition.SUPPORTIVE
        surviving = (primary.thesis_id,)
    else:
        disposition = A4Disposition.ABSTAIN
        surviving = ()

    if not findings:
        issue_ref = f"a4-issue:{digest((projection.semantic_fingerprint, 'PRIMARY_SURVIVAL'))[:24]}"
        findings = (
            ArbitrationFinding(
                finding_id=f"a4-arbitration-finding:{digest((issue_ref, disposition))[:24]}",
                issue_ref=issue_ref,
                thesis_refs=(primary.thesis_id,),
                argument_refs=primary.premise_refs,
                disposition=(
                    ArbitrationDisposition.ADMITTED
                    if disposition is A4Disposition.SUPPORTIVE
                    else ArbitrationDisposition.UNRESOLVED
                ),
                rule_id="a4-rule:surviving-thesis",
                policy_id=policy.arbitration_policy_id,
                decisive_evidence_refs=primary.support_refs,
                reason_code=f"A4_{disposition.value}",
            ),
        )
    return disposition, findings, surviving
