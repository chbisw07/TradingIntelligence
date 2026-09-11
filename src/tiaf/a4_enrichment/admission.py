"""Deterministic admission policy for material A4 evidence needs."""

from datetime import datetime
from typing import Any, cast

from tiaf.a4 import (
    A4Disposition,
    A4EvidenceNeed,
    A4RunRecord,
    ChallengeStatus,
    Materiality,
    validate_run,
)
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.planner.digests import digest

from .contracts import (
    EvidenceBridgeGrant,
    EvidenceBridgePolicy,
    EvidenceNeedAdmission,
)
from .enums import EvidenceNeedAdmissionOutcome


class EvidenceNeedAdmissionError(ValueError):
    """Parent or evidence-need integrity is invalid, rather than merely denied."""


def _seal(
    *,
    need: A4EvidenceNeed,
    grant: EvidenceBridgeGrant,
    policy: EvidenceBridgePolicy,
    outcome: EvidenceNeedAdmissionOutcome,
    reason: str,
    decided_at: datetime,
) -> EvidenceNeedAdmission:
    values = {
        "admission_id": "a4-need-admission:pending",
        "evidence_need_id": need.evidence_need_id,
        "parent_a4_run_id": need.parent_a4_run_id,
        "outcome": outcome,
        "reason_code": reason,
        "policy_id": policy.policy_id,
        "policy_version": policy.policy_version,
        "grant_id": grant.grant_id,
        "admitted_budget": grant.budget
        if outcome is EvidenceNeedAdmissionOutcome.ADMITTED
        else None,
        "admitted_provider_calls": grant.max_provider_calls
        if outcome is EvidenceNeedAdmissionOutcome.ADMITTED
        else 0,
        "decided_at": decided_at,
        "fingerprint": "0" * 64,
    }
    provisional = EvidenceNeedAdmission.model_construct(**cast(Any, values))
    identity = digest(
        provisional.model_dump(
            mode="json", exclude={"admission_id": True, "fingerprint": True}
        )
    )
    provisional = provisional.model_copy(
        update={"admission_id": f"a4-need-admission:{identity[:24]}"}
    )
    final = provisional.model_copy(
        update={
            "fingerprint": digest(
                provisional.model_dump(mode="json", exclude={"fingerprint": True})
            )
        }
    )
    return EvidenceNeedAdmission.model_validate(final.model_dump(mode="python"))


def admit_evidence_need(
    parent: A4RunRecord,
    need: A4EvidenceNeed,
    grant: EvidenceBridgeGrant,
    *,
    policy: EvidenceBridgePolicy | None = None,
    decided_at: datetime | None = None,
) -> EvidenceNeedAdmission:
    """Admit one need without selecting a provider or expressing a market view."""
    selected = policy or EvidenceBridgePolicy()
    when = decided_at or datetime.now(TIAF_TIMEZONE)
    try:
        parent = validate_run(parent)
        need = A4EvidenceNeed.model_validate_json(need.model_dump_json())
    except (TypeError, ValueError) as exc:
        raise EvidenceNeedAdmissionError(str(exc)) from exc
    if need.parent_a4_run_id != parent.run_id or need not in parent.result.evidence_needs:
        raise EvidenceNeedAdmissionError("evidence need is not owned by the supplied A4 run")
    finding_by_id = {item.finding_id: item for item in parent.result.challenge_findings}
    findings = tuple(finding_by_id.get(ref) for ref in need.challenge_refs)
    if any(item is None for item in findings):
        raise EvidenceNeedAdmissionError("evidence need challenge reference is unresolved")

    outcome = EvidenceNeedAdmissionOutcome.ADMITTED
    reason = "MATERIAL_UNRESOLVED_NEED_ADMITTED"
    if need.evidence_need_id in grant.resolved_need_ids or all(
        item is not None and item.status is ChallengeStatus.RESOLVED for item in findings
    ):
        outcome, reason = (
            EvidenceNeedAdmissionOutcome.ALREADY_RESOLVED,
            "NEED_ALREADY_RESOLVED",
        )
    elif need.dedupe_key in grant.processed_dedupe_keys:
        outcome, reason = EvidenceNeedAdmissionOutcome.DUPLICATE, "DEDUPE_KEY_ALREADY_PROCESSED"
    elif need.materiality is Materiality.NON_MATERIAL or not need.required:
        outcome, reason = EvidenceNeedAdmissionOutcome.NOT_MATERIAL, "NEED_IS_NOT_MATERIAL"
    elif need.requested_capability not in selected.supported_capabilities:
        outcome, reason = (
            EvidenceNeedAdmissionOutcome.UNSUPPORTED_CAPABILITY,
            "SEMANTIC_CAPABILITY_UNSUPPORTED",
        )
    elif parent.result.disposition in {A4Disposition.NO_TRADE, A4Disposition.AVOID}:
        outcome, reason = (
            EvidenceNeedAdmissionOutcome.DENIED_POLICY,
            "DECISIVE_HARD_STOP_MAKES_ENRICHMENT_IRRELEVANT",
        )
    elif (
        need.requested_capability not in grant.capabilities
        or not grant.entitlement_refs
        or parent.input_projection.header.profile_ref not in grant.profile_refs
    ):
        outcome, reason = EvidenceNeedAdmissionOutcome.DENIED_POLICY, "CAPABILITY_NOT_ENTITLED"
    elif (
        not set(need.permitted_authority_refs) <= set(grant.authority_refs)
        or not set(need.minimum_source_roles) & set(grant.source_roles)
    ):
        outcome, reason = (
            EvidenceNeedAdmissionOutcome.DENIED_AUTHORITY,
            "AUTHORITY_OR_SOURCE_ROLE_SCOPE_DENIED",
        )
    elif need.budget_ref not in grant.budget_refs:
        outcome, reason = EvidenceNeedAdmissionOutcome.DENIED_BUDGET, "PARENT_BUDGET_REF_DENIED"
    elif grant.budget.max_tool_calls < 1 or grant.max_provider_calls < 1:
        outcome, reason = EvidenceNeedAdmissionOutcome.DENIED_BUDGET, "NO_REMAINING_CHILD_BUDGET"
    elif grant.deadline is not None and when >= grant.deadline:
        outcome, reason = EvidenceNeedAdmissionOutcome.DEADLINE_EXCEEDED, "DEADLINE_EXCEEDED"

    return _seal(
        need=need,
        grant=grant,
        policy=selected,
        outcome=outcome,
        reason=reason,
        decided_at=when,
    )
