"""R1: semantic scope is independent of currently bound implementations."""

import pytest
from pydantic import ValidationError
from scripts._a3_8_fixtures import request

import tiaf.workflows.coordinator as coordinator_module
from tiaf.agents import (
    AgentEvidencePack,
    AgentOpinionV2,
    AgentRegistry,
    AgentRequest,
    AgentRunRecord,
    SpecialistCapability,
    SpecialistId,
)
from tiaf.planner import build_plan, dependencies
from tiaf.planner.models import AnalysisPlan, PlanNode
from tiaf.service.opportunity_intelligence.contracts import CompletenessProfile
from tiaf.service.opportunity_intelligence.contributions import (
    completeness,
    project_contributions,
)
from tiaf.service.opportunity_intelligence.policy import default_policy
from tiaf.workflows import (
    OrchestrationRunRecord,
    capture_json,
    default_registry,
    replay_recorded,
    run_serial,
    verify_deterministic,
)


def _without(registry: AgentRegistry, specialist: SpecialistId) -> AgentRegistry:
    return AgentRegistry(
        tuple(
            registry.get(capability.specialist)
            for capability in registry.capabilities()
            if capability.specialist is not specialist
        )
    )


def _coverage(record: OrchestrationRunRecord) -> CompletenessProfile:
    contributions, _ = project_contributions(record, default_policy())
    return completeness(contributions, record.result.gaps)


def test_removed_required_binding_stays_required_and_explicitly_absent() -> None:
    full = run_serial(request(), default_registry())
    reduced = run_serial(request(), _without(default_registry(), SpecialistId.FUNDAMENTAL))
    full_coverage = _coverage(full)
    reduced_coverage = _coverage(reduced)

    assert full_coverage.denominator == reduced_coverage.denominator == 8
    assert reduced_coverage.numerator <= full_coverage.numerator
    assert SpecialistId.FUNDAMENTAL in reduced_coverage.required
    assert SpecialistId.FUNDAMENTAL in reduced_coverage.missing
    absent = next(
        item
        for item in reduced.result.skipped
        if item.specialist is SpecialistId.FUNDAMENTAL
    )
    assert absent.reason == "NOT_REGISTERED" and absent.unresolved and absent.required is True
    assert absent.schema_version == "1.1"
    assert "FUNDAMENTAL:NOT_REGISTERED" in reduced.result.gaps
    assert reduced.result.status == "PARTIAL"
    assert reduced.plans[0].schema_version == "1.1"
    assert reduced.plans[0].planner_version == "1.1"
    assert reduced.plans[0].policy_version == "1.1"
    assert all(
        spec.schema_version == spec.policy_version == "1.1"
        for spec in reduced.plans[0].registry
    )
    tampered = reduced.plans[0].model_dump(mode="python")
    next(
        item
        for item in tampered["skipped"]
        if item["specialist"] is SpecialistId.FUNDAMENTAL
    )["required"] = False
    with pytest.raises(ValidationError, match="requirement classification mismatch"):
        AnalysisPlan.model_validate(tampered)


def test_removed_optional_binding_is_visible_without_changing_required_completeness() -> None:
    req = request().model_copy(update={"include_macro": True})
    full = run_serial(req, default_registry())
    reduced = run_serial(req, _without(default_registry(), SpecialistId.MACRO))
    full_coverage = _coverage(full)
    reduced_coverage = _coverage(reduced)

    assert (full_coverage.numerator, full_coverage.denominator) == (
        reduced_coverage.numerator,
        reduced_coverage.denominator,
    )
    assert SpecialistId.MACRO in reduced_coverage.optional
    absent = next(item for item in reduced.result.skipped if item.specialist is SpecialistId.MACRO)
    assert (
        absent.reason == "OPTIONAL_NOT_REGISTERED"
        and not absent.unresolved
        and absent.required is False
    )


def test_failed_required_contributor_preserves_scope_and_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = coordinator_module.OrchestrationCoordinator.invoke

    def broken(
        self: coordinator_module.OrchestrationCoordinator,
        node: PlanNode,
        pack: AgentEvidencePack,
    ) -> AgentRunRecord:
        if node.specialist is SpecialistId.FUNDAMENTAL:
            raise RuntimeError("fixture failure")
        return original(self, node, pack)

    monkeypatch.setattr(coordinator_module.OrchestrationCoordinator, "invoke", broken)
    record = run_serial(request(), default_registry())

    coverage = _coverage(record)
    assert coverage.denominator == 8
    assert SpecialistId.FUNDAMENTAL in coverage.required
    assert SpecialistId.FUNDAMENTAL in coverage.failed
    failure = next(item for item in record.result.outcomes if item.node_id == "FUNDAMENTAL")
    assert failure.status.value == "FAILED" and failure.reason == "RuntimeError"


def test_unauthorized_required_contributor_remains_in_denominator() -> None:
    req = request().model_copy(
        update={
            "allowed_capabilities": tuple(
                item
                for item in request().allowed_capabilities
                if item.value != "READ_FUNDAMENTALS"
            )
        }
    )
    record = run_serial(req, default_registry())
    coverage = _coverage(record)

    assert coverage.denominator == 8
    assert SpecialistId.FUNDAMENTAL in coverage.required
    assert SpecialistId.FUNDAMENTAL in coverage.missing
    denied = next(
        item
        for item in record.result.skipped
        if item.specialist is SpecialistId.FUNDAMENTAL
    )
    assert denied.reason == "PERMISSION_DENIED" and denied.unresolved and denied.required is True


class _UndeclaredSpecialist:
    def __init__(self) -> None:
        technical = default_registry().get(SpecialistId.TECHNICAL).capability()
        self._capability = technical.model_copy(
            update={
                "specialist": SpecialistId.CONTRARIAN_HYPOTHESIS,
                "specialist_version": "test-only-1.0",
            }
        )

    def capability(self) -> SpecialistCapability:
        return self._capability

    def analyze(
        self,
        request: AgentRequest,
        evidence: AgentEvidencePack,
    ) -> AgentOpinionV2:
        del request, evidence
        raise AssertionError("undeclared implementation must not be invoked")


def test_registry_expansion_does_not_expand_declared_scope() -> None:
    base = default_registry()
    expanded = AgentRegistry(
        (*tuple(base.get(item.specialist) for item in base.capabilities()), _UndeclaredSpecialist())
    )
    base_record = run_serial(request(), base)
    expanded_record = run_serial(request(), expanded)

    assert _coverage(base_record).denominator == _coverage(expanded_record).denominator == 8
    declared = {item.capability.specialist for item in expanded_record.plans[0].registry}
    assert SpecialistId.CONTRARIAN_HYPOTHESIS not in declared
    assert all(
        item.specialist is not SpecialistId.CONTRARIAN_HYPOTHESIS
        for item in expanded_record.result.opinions
    )


def test_new_capture_replay_is_offline_and_scope_is_registry_independent() -> None:
    reduced = _without(default_registry(), SpecialistId.FUNDAMENTAL)
    record = run_serial(request(), reduced)
    content = capture_json(record)

    assert replay_recorded(content) == record
    assert verify_deterministic(content, reduced) == record
    with pytest.raises(ValueError, match="planner/dependency version"):
        verify_deterministic(content, default_registry())
    assert _coverage(replay_recorded(content)).denominator == 8


def test_legacy_policy_capture_remains_readable_and_verifiable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reduced = _without(default_registry(), SpecialistId.FUNDAMENTAL)
    monkeypatch.setattr(
        coordinator_module,
        "dependencies",
        lambda registry: dependencies(registry, policy_version="1.0"),
    )

    def legacy_plan(
        req: object,
        specs: object,
        *,
        version: int = 1,
        policy_version: str = "1.0",
    ) -> object:
        del policy_version
        return build_plan(req, specs, version=version, policy_version="1.0")  # type: ignore[arg-type]

    monkeypatch.setattr(coordinator_module, "build_plan", legacy_plan)
    legacy = run_serial(request(), reduced)
    assert legacy.plans[0].schema_version == "1.0"
    assert legacy.plans[0].planner_version == "1.0"
    assert legacy.plans[0].policy_version == "1.0"
    assert all(item.schema_version == "1.0" for item in legacy.result.skipped)
    content = capture_json(legacy)
    assert replay_recorded(content) == legacy
    assert verify_deterministic(content, reduced) == legacy
    assert _coverage(legacy).denominator == 7


def test_a2_identity_is_unchanged_by_required_binding_absence() -> None:
    req = request()
    reduced = run_serial(req, _without(default_registry(), SpecialistId.FUNDAMENTAL))

    assert reduced.request.inventory.a2_pack == req.inventory.a2_pack
    assert reduced.result.a2_reference == req.inventory.a2_pack.deterministic_assessment_id
    assert reduced.result.a2_fingerprint == req.inventory.a2_pack.evidence_fingerprint
