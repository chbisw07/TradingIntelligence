"""Portable zero-live replay and deterministic verification of A4.2 chains."""

from datetime import datetime

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.planner.digests import digest

from .admission import admit_evidence_need
from .bridge import build_planner_bridge_plan
from .contracts import (
    A4EnrichmentCapture,
    A4EnrichmentChain,
    A4EnrichmentPolicyComparison,
    A4EnrichmentReplayResult,
    A4EnrichmentVerificationResult,
    EvidenceBridgePolicy,
)
from .enums import EvidenceNeedAdmissionOutcome
from .successor import build_successor_outcome, denied_outcome


class A4EnrichmentReplayError(ValueError):
    """A captured A4.2 chain is missing, corrupt, or not deterministically reproducible."""


def capture_chain(
    chain: A4EnrichmentChain,
    *,
    captured_at: datetime | None = None,
) -> A4EnrichmentCapture:
    chain = A4EnrichmentChain.model_validate_json(chain.model_dump_json())
    content = chain.model_dump_json()
    checksum = digest(content)
    return A4EnrichmentCapture(
        capture_id=f"a4-enrichment-capture:{checksum[:24]}",
        chain_json=content,
        chain_checksum=checksum,
        chain_fingerprint=chain.fingerprint,
        captured_at=captured_at or datetime.now(TIAF_TIMEZONE),
    )


def replay_recorded(
    capture: A4EnrichmentCapture,
    *,
    replayed_at: datetime | None = None,
) -> A4EnrichmentReplayResult:
    """Deserialize only captured contracts; this function has no service/network input."""
    try:
        capture = A4EnrichmentCapture.model_validate_json(capture.model_dump_json())
        if digest(capture.chain_json) != capture.chain_checksum:
            raise ValueError("A4.2 capture checksum mismatch")
        chain = A4EnrichmentChain.model_validate_json(capture.chain_json)
        if chain.fingerprint != capture.chain_fingerprint:
            raise ValueError("A4.2 capture chain fingerprint mismatch")
    except (TypeError, ValueError) as exc:
        raise A4EnrichmentReplayError(str(exc)) from exc
    when = replayed_at or datetime.now(TIAF_TIMEZONE)
    payload = {
        "chain": chain.fingerprint,
        "provider_calls": 0,
        "model_calls": 0,
        "replayed_at": when.isoformat(),
    }
    return A4EnrichmentReplayResult(
        replay_id=f"a4-enrichment-replay:{digest(payload)[:24]}",
        chain=chain,
        replayed_at=when,
        fingerprint=digest(payload),
    )


def verify_deterministic(
    capture: A4EnrichmentCapture,
    *,
    verified_at: datetime | None = None,
) -> A4EnrichmentVerificationResult:
    """Re-run admission, bridge mapping, projection and A4 using captured evidence only."""
    recorded = replay_recorded(capture, replayed_at=verified_at).chain
    parent = recorded.parent_run
    need = recorded.evidence_need
    outcome = recorded.outcome
    admission = admit_evidence_need(
        parent,
        need,
        recorded.grant,
        policy=recorded.policy,
        decided_at=outcome.admission.decided_at,
    )
    if admission.outcome is EvidenceNeedAdmissionOutcome.ADMITTED:
        if outcome.bridge_plan is None or outcome.execution is None:
            raise A4EnrichmentReplayError("admitted capture is missing bridge artifacts")
        plan = build_planner_bridge_plan(
            parent,
            need,
            admission,
            recorded.grant,
            outcome.bridge_plan.orchestration_request,
            execution_as_of=outcome.bridge_plan.orchestration_request.as_of,
            policy=recorded.policy,
        )
        verified_outcome = build_successor_outcome(
            parent,
            need,
            admission,
            plan,
            outcome.execution,
            outcome.evidence_capture,
            completed_at=outcome.completed_at,
        )
    else:
        verified_outcome = denied_outcome(
            parent,
            need,
            admission,
            completed_at=outcome.completed_at,
        )
    verified = A4EnrichmentChain.seal(
        parent_run=parent,
        evidence_need=need,
        grant=recorded.grant,
        policy=recorded.policy,
        outcome=verified_outcome,
    )
    when = verified_at or datetime.now(TIAF_TIMEZONE)
    exact = verified.fingerprint == recorded.fingerprint
    payload = {
        "recorded": recorded.fingerprint,
        "verified": verified.fingerprint,
        "exact_match": exact,
        "verified_at": when.isoformat(),
    }
    return A4EnrichmentVerificationResult(
        verification_id=f"a4-enrichment-verification:{digest(payload)[:24]}",
        recorded_fingerprint=recorded.fingerprint,
        verified_fingerprint=verified.fingerprint,
        exact_match=exact,
        verified_at=when,
        fingerprint=digest(payload),
    )


def compare_policy(
    chain: A4EnrichmentChain,
    candidate: EvidenceBridgePolicy,
    *,
    compared_at: datetime | None = None,
) -> A4EnrichmentPolicyComparison:
    original = (chain.policy.policy_id, chain.policy.policy_version)
    changed = (candidate.policy_id, candidate.policy_version)
    if original == changed:
        raise A4EnrichmentReplayError("policy comparison requires a new policy identity")
    admission = admit_evidence_need(
        chain.parent_run,
        chain.evidence_need,
        chain.grant,
        policy=candidate,
        decided_at=chain.outcome.admission.decided_at,
    )
    when = compared_at or datetime.now(TIAF_TIMEZONE)
    payload = {
        "chain": chain.fingerprint,
        "original_policy": original,
        "candidate_policy": changed,
        "original_admission": chain.outcome.admission.fingerprint,
        "candidate_admission": admission.fingerprint,
        "compared_at": when.isoformat(),
    }
    return A4EnrichmentPolicyComparison(
        comparison_id=f"a4-enrichment-comparison:{digest(payload)[:24]}",
        original_policy=original,
        candidate_policy=changed,
        original_admission_fingerprint=chain.outcome.admission.fingerprint,
        candidate_admission_fingerprint=admission.fingerprint,
        exact_match=admission.fingerprint == chain.outcome.admission.fingerprint,
        compared_at=when,
        fingerprint=digest(payload),
    )
