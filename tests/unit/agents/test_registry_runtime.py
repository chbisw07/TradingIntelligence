"""Registry extensibility and single-specialist runtime acceptance tests."""

import pytest

from tiaf.agents import (
    AgentBudget,
    AgentCapability,
    AgentEvidenceError,
    AgentNotRegisteredError,
    AgentOutputValidationError,
    AgentRegistry,
    AgentRunStatus,
    AgentRuntime,
    AgentStance,
    AgentUsage,
    SpecialistId,
)
from tiaf.context import EvidenceStatus
from tiaf.contracts import EvidenceType

from ._support import (
    NOW,
    DummySpecialist,
    StepClock,
    agent_opinion,
    agent_request,
    capability,
    evidence_pack,
    evidence_reference,
)


def runtime_for(specialist: DummySpecialist, *elapsed: float) -> AgentRuntime:
    return AgentRuntime(
        AgentRegistry((specialist,)),
        wall_clock=lambda: NOW,
        elapsed_clock=StepClock(*elapsed),
    )


def test_registry_register_lookup_duplicate_and_deterministic_discovery() -> None:
    relative = DummySpecialist(
        definition=capability(specialist=SpecialistId.RELATIVE_STRENGTH),
        opinion=agent_opinion(
            request=agent_request(specialist=SpecialistId.RELATIVE_STRENGTH)
        ),
    )
    technical = DummySpecialist()
    registry = AgentRegistry((technical, relative))
    assert registry.get(SpecialistId.TECHNICAL) is technical
    assert tuple(item.specialist for item in registry.capabilities()) == (
        SpecialistId.RELATIVE_STRENGTH,
        SpecialistId.TECHNICAL,
    )
    with pytest.raises(AgentOutputValidationError, match="duplicate"):
        registry.register(DummySpecialist())
    with pytest.raises(AgentNotRegisteredError):
        AgentRegistry().get(SpecialistId.MACRO)


def test_dummy_specialist_extends_registry_without_runtime_branch_change() -> None:
    specialist = DummySpecialist()
    record = runtime_for(specialist, 0.0, 0.1).run(agent_request(), evidence_pack())
    assert specialist.calls == 1
    assert record.status is AgentRunStatus.SUCCESS
    assert record.opinion is not None
    assert record.opinion.stance is AgentStance.POSITIVE


@pytest.mark.parametrize(
    ("stance", "status"),
    [
        (AgentStance.MIXED, AgentRunStatus.PARTIAL),
        (AgentStance.INSUFFICIENT_EVIDENCE, AgentRunStatus.INSUFFICIENT_EVIDENCE),
        (AgentStance.ABSTAIN, AgentRunStatus.ABSTAINED),
    ],
)
def test_runtime_preserves_partial_insufficient_and_abstaining_opinions(
    stance: AgentStance,
    status: AgentRunStatus,
) -> None:
    specialist = DummySpecialist(opinion=agent_opinion(stance=stance, status=status))
    record = runtime_for(specialist, 0.0, 0.1).run(agent_request(), evidence_pack())
    assert record.status is status
    assert record.opinion is not None
    assert record.opinion.stance is stance


@pytest.mark.parametrize("status", [EvidenceStatus.MISSING, EvidenceStatus.FAILED])
def test_runtime_does_not_invoke_specialist_when_required_evidence_is_unusable(
    status: EvidenceStatus,
) -> None:
    specialist = DummySpecialist()
    missing_pack = evidence_pack(
        reference=evidence_reference(availability=status)
    )
    record = runtime_for(specialist, 0.0, 0.1).run(agent_request(), missing_pack)
    assert specialist.calls == 0
    assert record.status is AgentRunStatus.INSUFFICIENT_EVIDENCE
    assert record.opinion is None
    assert record.evidence_pack.deterministic_assessment_id == "a2-assessment-1"


def test_runtime_isolates_unregistered_specialist() -> None:
    runtime = AgentRuntime(
        AgentRegistry(),
        wall_clock=lambda: NOW,
        elapsed_clock=StepClock(0.0, 0.1),
    )
    record = runtime.run(agent_request(), evidence_pack())
    assert record.status is AgentRunStatus.FAILED
    assert record.opinion is None
    assert record.failure is not None
    assert record.failure.error_type == AgentNotRegisteredError.__name__


def test_runtime_rejects_unauthorized_specialist_capability() -> None:
    definition = capability(
        allowed_capabilities=(
            AgentCapability.READ_A2_EVIDENCE,
            AgentCapability.READ_NEWS,
        )
    )
    specialist = DummySpecialist(definition=definition)
    record = runtime_for(specialist, 0.0, 0.1).run(agent_request(), evidence_pack())
    assert record.status is AgentRunStatus.FAILED
    assert record.failure is not None
    assert record.failure.error_type == AgentEvidenceError.__name__


@pytest.mark.parametrize(
    "usage",
    [
        AgentUsage(llm_calls=1, input_tokens=1),
        AgentUsage(tool_calls=1),
        AgentUsage(input_tokens=1),
        AgentUsage(output_tokens=1),
        AgentUsage(cost_units=0.1),
    ],
)
def test_runtime_enforces_every_non_elapsed_budget(usage: AgentUsage) -> None:
    specialist = DummySpecialist(opinion=agent_opinion(usage=usage))
    record = runtime_for(specialist, 0.0, 0.1).run(agent_request(), evidence_pack())
    assert record.status is AgentRunStatus.BUDGET_EXCEEDED
    assert record.opinion is None
    assert record.failure is not None
    assert record.usage.llm_calls == usage.llm_calls
    assert record.usage.tool_calls == usage.tool_calls


def test_runtime_classifies_observed_elapsed_limit_as_timeout() -> None:
    request = agent_request(budget=AgentBudget(max_elapsed_seconds=0.5))
    record = runtime_for(DummySpecialist(), 0.0, 0.75).run(request, evidence_pack())
    assert record.status is AgentRunStatus.TIMEOUT
    assert record.failure is not None
    assert record.usage.elapsed_seconds == 0.75


@pytest.mark.parametrize(
    "error",
    [
        AgentEvidenceError("evidence failed"),
        AgentOutputValidationError("invalid output"),
        RuntimeError("specialist bug"),
    ],
)
def test_specialist_exception_is_isolated_without_market_opinion(
    error: Exception,
) -> None:
    record = runtime_for(DummySpecialist(error=error), 0.0, 0.1).run(
        agent_request(), evidence_pack()
    )
    assert record.status is AgentRunStatus.FAILED
    assert record.opinion is None
    assert record.failure is not None


def test_runtime_rejects_invalid_specialist_output() -> None:
    record = runtime_for(DummySpecialist(invalid_output=True), 0.0, 0.1).run(
        agent_request(), evidence_pack()
    )
    assert record.status is AgentRunStatus.FAILED
    assert record.failure is not None
    assert record.failure.error_type == AgentOutputValidationError.__name__


def test_runtime_preserves_a2_baseline_and_evidence_fingerprint() -> None:
    record = runtime_for(DummySpecialist(), 0.0, 0.1).run(
        agent_request(), evidence_pack()
    )
    assert record.request.deterministic_baseline_reference == "a2-assessment-1"
    assert record.evidence_pack.deterministic_assessment_id == "a2-assessment-1"
    assert record.request.evidence_fingerprint == record.evidence_pack.evidence_fingerprint


def test_runtime_isolates_mismatched_evidence_pack_as_typed_failure() -> None:
    record = runtime_for(DummySpecialist(), 0.0, 0.1).run(
        agent_request(),
        evidence_pack(request_id="other-request"),
    )
    assert record.status is AgentRunStatus.FAILED
    assert record.failure is not None
    assert record.failure.error_type == AgentEvidenceError.__name__


def test_runtime_prevents_claims_outside_the_supplied_pack() -> None:
    invalid = agent_opinion().model_copy(
        update={"supporting_evidence_ids": ("outside-pack",)}
    )
    specialist = DummySpecialist(opinion=invalid)
    record = runtime_for(specialist, 0.0, 0.1).run(agent_request(), evidence_pack())
    assert record.status is AgentRunStatus.FAILED
    assert record.failure is not None
    assert record.failure.error_type == AgentOutputValidationError.__name__


def test_required_evidence_type_is_discovered_from_declaration() -> None:
    definition = capability(required_evidence_types=(EvidenceType.FUNDAMENTAL,))
    specialist = DummySpecialist(definition=definition)
    record = runtime_for(specialist, 0.0, 0.1).run(agent_request(), evidence_pack())
    assert record.status is AgentRunStatus.INSUFFICIENT_EVIDENCE
    assert specialist.calls == 0
