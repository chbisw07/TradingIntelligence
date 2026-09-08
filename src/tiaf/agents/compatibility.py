"""Explicit lossless compatibility seam for the frozen A0 opinion contract."""

from tiaf.contracts import AgentOpinion as AgentOpinionV1

from .budget import AgentUsage
from .enums import AgentRunStatus, AgentStance, BaselineAgreement
from .errors import AgentOutputValidationError
from .evidence import AgentEvidencePack
from .models import AgentConfidence, AgentOpinionV2, AgentRequest

_STANCE_MAP = {
    "BULLISH": AgentStance.POSITIVE,
    "BEARISH": AgentStance.NEGATIVE,
    "NEUTRAL": AgentStance.NEUTRAL,
}


def agent_opinion_v1_to_v2(
    opinion: AgentOpinionV1,
    *,
    request: AgentRequest,
    evidence_pack: AgentEvidencePack,
    opinion_id: str,
    specialist_version: str,
    policy_version: str,
    baseline_agreement: BaselineAgreement,
) -> AgentOpinionV2:
    """Wrap an A0 opinion without inventing claims, probability, or provenance."""
    if opinion.subject_id != request.subject:
        raise AgentOutputValidationError("A0 opinion subject does not match Agent request")
    if (
        evidence_pack.request_id != request.request_id
        or evidence_pack.subject != request.subject
        or evidence_pack.evidence_fingerprint != request.evidence_fingerprint
        or evidence_pack.deterministic_assessment_id
        != request.deterministic_baseline_reference
    ):
        raise AgentOutputValidationError("evidence pack does not match Agent request/A2 identity")
    available_ids = {item.evidence_id for item in evidence_pack.references}
    if not set(opinion.evidence_ids) <= available_ids:
        raise AgentOutputValidationError("A0 opinion references evidence outside the pack")
    return AgentOpinionV2(
        opinion_id=opinion_id,
        request_id=request.request_id,
        run_id=request.run_id,
        specialist=request.specialist,
        specialist_version=specialist_version,
        subject=request.subject,
        horizon=request.horizon,
        stance=_STANCE_MAP[opinion.stance.value],
        status=AgentRunStatus.SUCCESS,
        confidence=AgentConfidence(
            evidence_coverage=evidence_pack.evidence_coverage,
            evidence_quality=evidence_pack.overall_quality,
            self_reported=opinion.confidence,
            self_reported_basis="legacy A0 self-reported confidence; not probability",
        ),
        summary=opinion.summary,
        reason_codes=opinion.supporting_factors,
        evidence_claims=(),
        supporting_evidence_ids=opinion.evidence_ids,
        risks=opinion.concerns,
        deterministic_baseline_reference=request.deterministic_baseline_reference,
        baseline_agreement=baseline_agreement,
        evidence_fingerprint=request.evidence_fingerprint,
        evidence_quality=evidence_pack.overall_quality,
        evidence_freshness=opinion.freshness,
        policy_version=policy_version,
        usage=AgentUsage(),
        produced_at=opinion.produced_at,
        valid_until=opinion.valid_until,
        legacy_opinion=opinion,
        metadata={
            "legacy_agent_name": opinion.agent_name,
            "legacy_agent_role": opinion.agent_role,
        },
    )


def agent_opinion_v2_to_v1(opinion: AgentOpinionV2) -> AgentOpinionV1:
    """Return the exact embedded v1 object or reject potentially lossy conversion."""
    if opinion.legacy_opinion is None:
        raise AgentOutputValidationError(
            "A3 AgentOpinion v2 cannot be losslessly converted to A0 schema 1.0"
        )
    return opinion.legacy_opinion
