from datetime import timedelta

import pytest
from pydantic import ValidationError

from tiaf.a4 import (
    A4EvidenceCapability,
    Materiality,
    record_fingerprint,
    result_semantic_payload,
    validate_run,
)
from tiaf.a4_enrichment import (
    EvidenceBridgePolicy,
    EvidenceNeedAdmissionError,
    EvidenceNeedAdmissionOutcome,
    admit_evidence_need,
)
from tiaf.agents import AgentBudget
from tiaf.planner.digests import digest

from ..source_semantics._support import LATER, NOW
from ._support import grant, parent_case


def test_real_evidence_need_is_bounded_provider_neutral_and_frozen() -> None:
    need = parent_case().need
    required = {
        "evidence_need_id",
        "parent_a4_run_id",
        "parent_projection_id",
        "parent_projection_fingerprint",
        "subject",
        "objective",
        "horizon",
        "original_as_of",
        "semantic_question",
        "requested_capability",
        "challenge_refs",
        "materiality",
        "reason_codes",
        "minimum_source_roles",
        "budget_ref",
        "dedupe_key",
        "policy_version",
        "created_at",
    }
    forbidden = {"provider", "endpoint", "url", "browser", "model", "broker", "trade"}
    assert required <= set(type(need).model_fields)
    assert not any(any(word in field for word in forbidden) for field in type(need).model_fields)
    assert isinstance(need.challenge_refs, tuple)
    assert isinstance(need.model_dump(mode="json")["challenge_refs"], list)
    with pytest.raises(ValidationError):
        need.evidence_need_id = "a4-evidence-need:changed"


def test_admits_material_unresolved_need() -> None:
    case = parent_case()
    result = admit_evidence_need(case.run, case.need, grant(case), decided_at=NOW)
    assert result.outcome is EvidenceNeedAdmissionOutcome.ADMITTED
    assert result.admitted_budget is not None
    assert result.admitted_provider_calls == 1


@pytest.mark.parametrize(
    ("permission", "outcome"),
    [
        ({"dedupe": True}, EvidenceNeedAdmissionOutcome.DUPLICATE),
        ({"resolved": True}, EvidenceNeedAdmissionOutcome.ALREADY_RESOLVED),
        ({"tool_calls": 0}, EvidenceNeedAdmissionOutcome.DENIED_BUDGET),
        ({"provider_calls": 0}, EvidenceNeedAdmissionOutcome.DENIED_BUDGET),
        ({"authority": False}, EvidenceNeedAdmissionOutcome.DENIED_AUTHORITY),
        (
            {"deadline": NOW - timedelta(seconds=1)},
            EvidenceNeedAdmissionOutcome.DEADLINE_EXCEEDED,
        ),
    ],
)
def test_typed_admission_denials(
    permission: dict[str, object],
    outcome: EvidenceNeedAdmissionOutcome,
) -> None:
    case = parent_case()
    decision = admit_evidence_need(
        case.run,
        case.need,
        grant(case, **permission),  # type: ignore[arg-type]
        decided_at=NOW,
    )
    assert decision.outcome is outcome
    assert decision.admitted_budget is None
    assert decision.admitted_provider_calls == 0


def test_unsupported_capability_is_typed_not_exception() -> None:
    case = parent_case()
    policy = EvidenceBridgePolicy(
        supported_capabilities=(A4EvidenceCapability.AUTHORITATIVE_CONFIRMATION,)
    )
    decision = admit_evidence_need(
        case.run,
        case.need,
        grant(case),
        policy=policy,
        decided_at=NOW,
    )
    assert decision.outcome is EvidenceNeedAdmissionOutcome.UNSUPPORTED_CAPABILITY


def test_missing_entitlement_is_denied_by_policy() -> None:
    case = parent_case()
    permission = grant(case).model_copy(update={"entitlement_refs": ()})
    decision = admit_evidence_need(case.run, case.need, permission, decided_at=NOW)
    assert decision.outcome is EvidenceNeedAdmissionOutcome.DENIED_POLICY


def test_unowned_need_fails_parent_integrity_closed() -> None:
    case = parent_case()
    unrelated = case.need.model_copy(update={"evidence_need_id": "a4-evidence-need:other"})
    with pytest.raises(EvidenceNeedAdmissionError):
        admit_evidence_need(case.run, unrelated, grant(case), decided_at=NOW)


def test_nonmaterial_need_returns_typed_not_material() -> None:
    case = parent_case()
    need = case.need.model_copy(
        update={"materiality": Materiality.NON_MATERIAL, "required": False}
    )
    result = case.run.result.model_copy(
        update={
            "result_id": "a4-result:pending",
            "evidence_needs": (need,),
            "semantic_fingerprint": "0" * 64,
        }
    )
    result_fp = digest(result_semantic_payload(result))
    result = result.model_copy(
        update={
            "result_id": f"a4-result:{result_fp[:24]}",
            "semantic_fingerprint": result_fp,
        }
    )
    run = case.run.model_copy(update={"result": result, "fingerprint": "0" * 64})
    run = validate_run(run.model_copy(update={"fingerprint": record_fingerprint(run)}))
    decision = admit_evidence_need(run, need, grant(case), decided_at=NOW)
    assert decision.outcome is EvidenceNeedAdmissionOutcome.NOT_MATERIAL


def test_parent_budget_is_carried_not_reset() -> None:
    case = parent_case()
    permission = grant(case).model_copy(
        update={
            "budget": AgentBudget(
                max_tool_calls=1,
                max_cost_units=0.25,
                max_elapsed_seconds=7,
            )
        }
    )
    decision = admit_evidence_need(case.run, case.need, permission, decided_at=NOW)
    assert decision.admitted_budget == permission.budget
    assert decision.admitted_budget.max_cost_units == 0.25


def test_need_rejects_naive_timestamp_and_normalizes_utc() -> None:
    need = parent_case().need
    with pytest.raises(ValidationError):
        type(need).model_validate(
            need.model_dump(mode="python")
            | {"original_as_of": need.original_as_of.replace(tzinfo=None)}
        )
    restored = type(need).model_validate_json(need.model_dump_json())
    assert str(restored.original_as_of.tzinfo) == "Asia/Kolkata"
    assert restored.model_dump(mode="json")["original_as_of"].endswith("+05:30")


def test_bounds_are_explicitly_one_round_and_one_successor() -> None:
    policy = EvidenceBridgePolicy()
    assert policy.max_enrichment_rounds == 1
    assert policy.max_successor_cycles == 1
    with pytest.raises(ValidationError):
        EvidenceBridgePolicy(max_enrichment_rounds=2)  # type: ignore[arg-type]


def test_deadline_after_admission_is_accepted() -> None:
    case = parent_case()
    result = admit_evidence_need(
        case.run,
        case.need,
        grant(case, deadline=LATER),
        decided_at=NOW,
    )
    assert result.outcome is EvidenceNeedAdmissionOutcome.ADMITTED
