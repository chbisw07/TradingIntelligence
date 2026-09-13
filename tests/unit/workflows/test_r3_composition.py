"""R3 immutable composition identity and pinned-verifier acceptance."""

import json
import socket
from typing import Any

import pytest
from pydantic import ValidationError
from scripts._a3_8_fixtures import request

from tiaf.a5 import capture_run as capture_a5_run
from tiaf.a5 import evaluate_position
from tiaf.agents import (
    AgentEvidencePack,
    AgentOpinionV2,
    AgentRegistry,
    AgentRequest,
    SpecialistCapability,
    SpecialistId,
)
from tiaf.agents.protocols import SpecialistAgent
from tiaf.planner.digests import digest
from tiaf.workflows import (
    CompositionEnvelope,
    CompositionParticipant,
    CompositionParticipantStatus,
    CompositionRequiredness,
    CompositionUsageKnowledge,
    PinnedVerificationError,
    PinnedVerificationFailure,
    build_orchestration_composition,
    capture_json,
    default_registry,
    replay_recorded,
    run_serial,
    specialist_capability_id,
    verify_deterministic,
)

from ..a5._support import request as position_request


def _without(specialist: SpecialistId) -> AgentRegistry:
    registry = default_registry()
    return AgentRegistry(
        tuple(
            registry.get(item.specialist)
            for item in registry.capabilities()
            if item.specialist is not specialist
        )
    )


def _participant(
    envelope: CompositionEnvelope,
    specialist: SpecialistId,
) -> CompositionParticipant:
    capability_id = specialist_capability_id(specialist)
    return next(item for item in envelope.participants if item.capability_id == capability_id)


def _reseal(
    envelope: CompositionEnvelope,
    **updates: Any,
) -> CompositionEnvelope:
    fields = {
        name: getattr(envelope, name)
        for name in CompositionEnvelope.model_fields
        if name != "composition_fingerprint"
    }
    fields.update(updates)
    return CompositionEnvelope.seal(**fields)


class _VersionChangedSpecialist:
    def __init__(self, delegate: SpecialistAgent) -> None:
        self._delegate = delegate

    def capability(self) -> SpecialistCapability:
        capability = self._delegate.capability()
        return capability.model_copy(update={"specialist_version": "999.0"})

    def analyze(
        self,
        value: AgentRequest,
        evidence: AgentEvidencePack,
    ) -> AgentOpinionV2:
        return self._delegate.analyze(value, evidence)


def test_composition_identity_scope_and_order_are_deterministic() -> None:
    record = run_serial(request(), default_registry())
    envelope = record.composition
    assert record.schema_version == "1.1" and envelope is not None
    assert envelope.schema_version == "1.0"
    assert envelope.run_id == record.request.run_id
    assert envelope.requested_scope == tuple(
        sorted(item.capability_id for item in envelope.participants)
    )
    assert set(envelope.required_scope).isdisjoint(envelope.optional_scope)
    assert envelope.requested_scope == tuple(
        sorted((*envelope.required_scope, *envelope.optional_scope))
    )
    assert any(
        item.usage_knowledge is CompositionUsageKnowledge.KNOWN
        and item.usage is not None
        for item in envelope.participants
    )
    rebuilt = build_orchestration_composition(
        record.request,
        record.plans,
        tuple(reversed(record.attempts)),
        record.result,
    )
    assert rebuilt == envelope


def test_composition_contract_is_immutable_and_json_key_order_is_irrelevant() -> None:
    envelope = run_serial(request(), default_registry()).composition
    assert envelope is not None
    with pytest.raises(ValidationError, match="frozen"):
        setattr(envelope, "policy_version", "other")
    assert isinstance(envelope.participants, tuple)
    with pytest.raises(AttributeError):
        getattr(envelope.participants, "append")
    payload = envelope.model_dump(mode="json")
    reversed_keys = dict(reversed(tuple(payload.items())))
    assert CompositionEnvelope.model_validate_json(json.dumps(reversed_keys)) == envelope
    known = next(item for item in envelope.participants if item.usage is not None)
    usage = known.usage
    assert usage is not None
    changed_usage = known.model_copy(
        update={
            "usage": usage.model_copy(
                update={"elapsed_seconds": usage.elapsed_seconds + 1.0}
            )
        }
    )
    usage_variant = _reseal(
        envelope,
        participants=tuple(
            changed_usage if item is known else item for item in envelope.participants
        ),
    )
    assert usage_variant.composition_fingerprint == envelope.composition_fingerprint


def test_required_absence_is_explicit_and_optional_absence_is_not_required() -> None:
    required_record = run_serial(
        request(),
        _without(SpecialistId.FUNDAMENTAL),
    )
    required = required_record.composition
    assert required is not None
    fundamental = _participant(required, SpecialistId.FUNDAMENTAL)
    assert fundamental.requiredness is CompositionRequiredness.REQUIRED
    assert fundamental.status is CompositionParticipantStatus.NOT_REGISTERED
    assert not fundamental.invoked and not required.required_complete
    assert fundamental.usage_knowledge.value == "NOT_APPLICABLE"
    assert fundamental.usage is None

    optional_record = run_serial(
        request().model_copy(update={"include_macro": True}),
        _without(SpecialistId.MACRO),
    )
    optional = optional_record.composition
    assert optional is not None
    macro = _participant(optional, SpecialistId.MACRO)
    assert macro.requiredness is CompositionRequiredness.OPTIONAL
    assert macro.status is CompositionParticipantStatus.NOT_REGISTERED
    assert macro.capability_id not in optional.required_scope
    assert macro.usage_knowledge.value == "NOT_APPLICABLE"
    assert macro.usage is None


def test_later_registry_expansion_cannot_enter_recorded_or_verified_composition() -> None:
    reduced = _without(SpecialistId.FUNDAMENTAL)
    record = run_serial(request(), reduced)
    content = capture_json(record)
    recorded = replay_recorded(content)
    verified = verify_deterministic(content, default_registry())
    assert recorded == verified == record
    assert verified.composition == record.composition


def test_pinned_verifier_rejects_missing_and_incompatible_implementations() -> None:
    record = run_serial(request(), default_registry())
    content = capture_json(record)
    with pytest.raises(PinnedVerificationError) as missing:
        verify_deterministic(content, _without(SpecialistId.TECHNICAL))
    assert missing.value.failure is PinnedVerificationFailure.REQUIRED_PARTICIPANT_UNRESOLVED

    original = default_registry()
    changed = AgentRegistry(
        tuple(
            _VersionChangedSpecialist(original.get(item.specialist))
            if item.specialist is SpecialistId.TECHNICAL
            else original.get(item.specialist)
            for item in original.capabilities()
        )
    )
    with pytest.raises(PinnedVerificationError) as incompatible:
        verify_deterministic(content, changed)
    assert (
        incompatible.value.failure
        is PinnedVerificationFailure.INCOMPATIBLE_CAPABILITY_VERSION
    )


def test_composition_fingerprint_changes_for_participant_version_and_requiredness() -> None:
    envelope = run_serial(request(), default_registry()).composition
    assert envelope is not None
    technical = _participant(envelope, SpecialistId.TECHNICAL)
    changed_technical = CompositionParticipant.model_validate(
        technical.model_dump(mode="python") | {"interface_version": "other-version"}
    )
    changed_version = _reseal(
        envelope,
        participants=tuple(
            changed_technical if item is technical else item
            for item in envelope.participants
        ),
    )
    assert changed_version.composition_fingerprint != envelope.composition_fingerprint

    macro = _participant(envelope, SpecialistId.MACRO)
    required_macro = CompositionParticipant.model_validate(
        macro.model_dump(mode="python")
        | {"requiredness": CompositionRequiredness.REQUIRED}
    )
    changed_requiredness = _reseal(
        envelope,
        required_scope=tuple(sorted((*envelope.required_scope, macro.capability_id))),
        optional_scope=tuple(
            item for item in envelope.optional_scope if item != macro.capability_id
        ),
        participants=tuple(
            required_macro if item is macro else item for item in envelope.participants
        ),
    )
    assert (
        changed_requiredness.composition_fingerprint
        != envelope.composition_fingerprint
    )


def test_composition_fingerprint_changes_when_participant_set_changes() -> None:
    envelope = run_serial(request(), default_registry()).composition
    assert envelope is not None
    macro_id = specialist_capability_id(SpecialistId.MACRO)
    without_macro = _reseal(
        envelope,
        requested_scope=tuple(item for item in envelope.requested_scope if item != macro_id),
        optional_scope=tuple(item for item in envelope.optional_scope if item != macro_id),
        participants=tuple(
            item for item in envelope.participants if item.capability_id != macro_id
        ),
    )
    assert without_macro.composition_fingerprint != envelope.composition_fingerprint


def test_corrupt_or_output_mismatched_envelope_fails_closed() -> None:
    record = run_serial(request(), default_registry())
    captured = json.loads(capture_json(record))
    captured["record"]["composition"]["participants"][0]["output_fingerprint"] = "f" * 64
    captured["checksum"] = digest(captured["record"])
    with pytest.raises(ValidationError, match="composition fingerprint mismatch"):
        replay_recorded(json.dumps(captured))

    envelope = record.composition
    assert envelope is not None
    participant = next(item for item in envelope.participants if item.output_ref is not None)
    changed = CompositionParticipant.model_validate(
        participant.model_dump(mode="python") | {"output_fingerprint": "f" * 64}
    )
    forged_envelope = _reseal(
        envelope,
        participants=tuple(
            changed if item is participant else item for item in envelope.participants
        ),
    )
    forged: dict[str, Any] = {
        name: getattr(record, name)
        for name in record.__class__.model_fields
    }
    forged["composition"] = forged_envelope
    provisional = record.__class__.model_construct(**forged)
    forged["fingerprint"] = digest(provisional.semantic_payload())
    with pytest.raises(ValidationError, match="composition output fingerprint mismatch"):
        record.__class__.model_validate(forged)
    serialized = provisional.model_dump(mode="json")
    serialized["fingerprint"] = forged["fingerprint"]
    forged_capture = json.dumps(
        {"record": serialized, "checksum": digest(serialized)},
        sort_keys=True,
    )
    with pytest.raises(PinnedVerificationError) as mismatch:
        verify_deterministic(forged_capture, default_registry())
    assert mismatch.value.failure is PinnedVerificationFailure.OUTPUT_FINGERPRINT_MISMATCH


def test_composition_policy_mismatch_has_typed_fail_closed_status() -> None:
    record = run_serial(request(), default_registry())
    envelope = record.composition
    assert envelope is not None
    changed = _reseal(envelope, policy_version="other-policy")
    forged: dict[str, Any] = {
        name: (changed if name == "composition" else getattr(record, name))
        for name in record.__class__.model_fields
    }
    provisional = record.__class__.model_construct(**forged)
    forged["fingerprint"] = digest(provisional.semantic_payload())
    serialized = provisional.model_dump(mode="json")
    serialized["fingerprint"] = forged["fingerprint"]
    content = json.dumps(
        {"record": serialized, "checksum": digest(serialized)},
        sort_keys=True,
    )
    with pytest.raises(PinnedVerificationError) as mismatch:
        verify_deterministic(content, default_registry())
    assert mismatch.value.failure is PinnedVerificationFailure.POLICY_MISMATCH


def test_composition_successor_is_new_identity_without_history_rewrite() -> None:
    envelope = run_serial(request(), default_registry()).composition
    assert envelope is not None
    original_json = envelope.model_dump_json()
    successor = _reseal(
        envelope,
        run_id="comparison-run",
        policy_version="comparison-policy-1",
        parent_composition_fingerprint=envelope.composition_fingerprint,
        baseline_composition_fingerprint=envelope.composition_fingerprint,
    )
    assert successor.composition_fingerprint != envelope.composition_fingerprint
    assert successor.parent_composition_fingerprint == envelope.composition_fingerprint
    assert envelope.model_dump_json() == original_json


def test_recorded_replay_and_pinned_verification_make_no_network_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = run_serial(request(), default_registry())
    content = capture_json(record)

    def forbidden(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("R3 replay or verification attempted a network call")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    assert replay_recorded(content) == record
    assert verify_deterministic(content, default_registry()) == record
    assert record.result.provider_calls == 0
    assert record.result.usage.llm_calls == 0


def test_r3_capture_does_not_change_frozen_a5_domain_semantics() -> None:
    value = position_request()
    before = evaluate_position(value)
    before_capture = capture_a5_run(before, captured_at=before.evaluated_at)

    orchestration = run_serial(request(), default_registry())
    assert orchestration.composition is not None

    after = evaluate_position(value)
    after_capture = capture_a5_run(after, captured_at=after.evaluated_at)
    assert after == before
    assert after.result.semantic_fingerprint == before.result.semantic_fingerprint
    assert after.fingerprint == before.fingerprint
    assert after_capture == before_capture
