"""Immutable per-run composition capture and exact pinned resolution semantics."""

from enum import StrEnum
from typing import Any, Literal, Self

from pydantic import model_validator

from tiaf.agents import AgentRunStatus, AgentUsage, SpecialistId
from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr
from tiaf.planner.digests import digest, semantic
from tiaf.planner.models import (
    AnalysisPlan,
    NodeAttempt,
    NodeStatus,
    OrchestrationRequest,
    OrchestrationResult,
    Sha256,
)


class CompositionRequiredness(StrEnum):
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"


class CompositionParticipantStatus(StrEnum):
    """Run participation state, distinct from availability and market disposition."""

    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    ABSTAINED = "ABSTAINED"
    SUPERSEDED = "SUPERSEDED"
    NOT_REGISTERED = "NOT_REGISTERED"
    UNAUTHORIZED = "UNAUTHORIZED"
    DEPENDENCY_UNAVAILABLE = "DEPENDENCY_UNAVAILABLE"
    SKIPPED_BY_POLICY = "SKIPPED_BY_POLICY"
    NOT_SELECTED = "NOT_SELECTED"
    UNSUPPORTED = "UNSUPPORTED"


class CompositionUsageKnowledge(StrEnum):
    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class PinnedVerificationFailure(StrEnum):
    CORRUPTED_ENVELOPE = "CORRUPTED_ENVELOPE"
    MISSING_PINNED_CAPABILITY = "MISSING_PINNED_CAPABILITY"
    INCOMPATIBLE_CAPABILITY_VERSION = "INCOMPATIBLE_CAPABILITY_VERSION"
    PINNED_DEPENDENCY_MISMATCH = "PINNED_DEPENDENCY_MISMATCH"
    POLICY_MISMATCH = "POLICY_MISMATCH"
    REQUIRED_PARTICIPANT_UNRESOLVED = "REQUIRED_PARTICIPANT_UNRESOLVED"
    MISSING_ARTIFACT = "MISSING_ARTIFACT"
    OUTPUT_FINGERPRINT_MISMATCH = "OUTPUT_FINGERPRINT_MISMATCH"
    UNAUTHORIZED = "UNAUTHORIZED"
    DETERMINISTIC_OUTPUT_MISMATCH = "DETERMINISTIC_OUTPUT_MISMATCH"


class PinnedVerificationError(ValueError):
    """Typed fail-closed verification error; never repaired or substituted."""

    def __init__(self, failure: PinnedVerificationFailure, detail: str) -> None:
        self.failure = failure
        super().__init__(f"{failure.value}:{detail}")


class CompositionParticipant(ContractModel):
    capability_id: NonEmptyStr
    interface_version: NonEmptyStr | None = None
    semantic_role: NonEmptyStr
    requiredness: CompositionRequiredness
    dependency_fingerprint: Sha256 | None = None
    invoked: bool
    input_refs: tuple[NonEmptyStr, ...] = ()
    output_ref: NonEmptyStr | None = None
    output_fingerprint: Sha256 | None = None
    status: CompositionParticipantStatus
    failure_reason: NonEmptyStr | None = None
    usage_knowledge: CompositionUsageKnowledge
    usage: AgentUsage | None = None

    @model_validator(mode="after")
    def coherent_participation(self) -> Self:
        if self.input_refs != tuple(sorted(set(self.input_refs))):
            raise ValueError("composition input references must be unique and sorted")
        invoked_states = {
            CompositionParticipantStatus.SUCCEEDED,
            CompositionParticipantStatus.FAILED,
            CompositionParticipantStatus.ABSTAINED,
            CompositionParticipantStatus.SUPERSEDED,
        }
        if self.invoked != (self.status in invoked_states):
            raise ValueError("composition invocation flag and status disagree")
        if self.invoked and self.interface_version is None:
            raise ValueError("invoked participant requires an exact interface version")
        if (self.output_ref is None) != (self.output_fingerprint is None):
            raise ValueError("composition output reference and fingerprint must be paired")
        if self.status in {
            CompositionParticipantStatus.SUCCEEDED,
            CompositionParticipantStatus.ABSTAINED,
        } and self.output_ref is None:
            raise ValueError("completed participant requires captured output identity")
        if not self.invoked and (self.output_ref is not None or self.input_refs):
            raise ValueError("non-invoked participant cannot claim consumed input or output")
        if self.status is CompositionParticipantStatus.SUCCEEDED:
            if self.failure_reason is not None:
                raise ValueError("successful participant cannot report a failure reason")
        elif self.failure_reason is None:
            raise ValueError("non-success participant requires an explicit reason")
        if self.usage_knowledge is CompositionUsageKnowledge.KNOWN:
            if self.usage is None:
                raise ValueError("known participant usage requires a usage record")
        elif self.usage is not None:
            raise ValueError("unknown/not-applicable usage cannot carry fabricated values")
        if (
            not self.invoked
            and self.usage_knowledge is not CompositionUsageKnowledge.NOT_APPLICABLE
        ):
            raise ValueError("non-invoked participant usage must be not applicable")
        return self


class CompositionEnvelope(ContractModel):
    """Exact policy/scope/participation identity for one orchestration run."""

    schema_id: Literal["tiaf.workflows.composition-envelope"] = (
        "tiaf.workflows.composition-envelope"
    )
    schema_version: Literal["1.0"] = "1.0"
    run_id: NonEmptyStr
    policy_id: Literal["policy:tiaf.orchestration-planner"] = (
        "policy:tiaf.orchestration-planner"
    )
    policy_version: NonEmptyStr
    planner_version: NonEmptyStr
    requested_scope: tuple[NonEmptyStr, ...]
    required_scope: tuple[NonEmptyStr, ...]
    optional_scope: tuple[NonEmptyStr, ...]
    participants: tuple[CompositionParticipant, ...]
    parent_composition_fingerprint: Sha256 | None = None
    baseline_composition_fingerprint: Sha256 | None = None
    composition_fingerprint: Sha256

    def fingerprint_payload(self) -> Any:
        data = self.model_dump(mode="json", exclude={"composition_fingerprint"})
        for participant in data["participants"]:
            participant.pop("usage", None)
        return semantic(data)

    @property
    def required_complete(self) -> bool:
        complete = {
            CompositionParticipantStatus.SUCCEEDED,
            CompositionParticipantStatus.ABSTAINED,
        }
        return all(
            item.status in complete
            for item in self.participants
            if item.requiredness is CompositionRequiredness.REQUIRED
        )

    @model_validator(mode="after")
    def coherent_envelope(self) -> Self:
        for scope, label in (
            (self.requested_scope, "requested"),
            (self.required_scope, "required"),
            (self.optional_scope, "optional"),
        ):
            if scope != tuple(sorted(set(scope))):
                raise ValueError(f"composition {label} scope must be unique and sorted")
        if set(self.required_scope) & set(self.optional_scope):
            raise ValueError("composition required and optional scope must be disjoint")
        if self.requested_scope != tuple(
            sorted((*self.required_scope, *self.optional_scope))
        ):
            raise ValueError("composition requested scope must equal required plus optional scope")
        participant_ids = tuple(item.capability_id for item in self.participants)
        if participant_ids != self.requested_scope:
            raise ValueError("composition participants must exactly cover requested scope in order")
        for item in self.participants:
            required = item.capability_id in self.required_scope
            if required != (item.requiredness is CompositionRequiredness.REQUIRED):
                raise ValueError("composition participant requiredness contradicts pinned scope")
        if self.parent_composition_fingerprint == self.composition_fingerprint:
            raise ValueError("composition cannot be its own parent")
        if self.baseline_composition_fingerprint == self.composition_fingerprint:
            raise ValueError("composition cannot be its own baseline")
        if digest(self.fingerprint_payload()) != self.composition_fingerprint:
            raise ValueError("composition fingerprint mismatch")
        return self

    @classmethod
    def seal(cls, **fields: Any) -> Self:
        provisional = cls.model_construct(composition_fingerprint="0" * 64, **fields)
        data = provisional.model_dump(mode="python")
        data["composition_fingerprint"] = digest(provisional.fingerprint_payload())
        return cls.model_validate(data)


def specialist_capability_id(specialist: SpecialistId) -> str:
    return f"specialist:{specialist.value.casefold().replace('_', '-')}"


def _skipped_status(reason: str) -> CompositionParticipantStatus:
    if reason in {"NOT_REGISTERED", "OPTIONAL_NOT_REGISTERED"}:
        return CompositionParticipantStatus.NOT_REGISTERED
    if reason == "PERMISSION_DENIED":
        return CompositionParticipantStatus.UNAUTHORIZED
    if reason in {"UNKNOWN_FNO_ELIGIBILITY", "NO_LLM_UNSUPPORTED"}:
        return CompositionParticipantStatus.DEPENDENCY_UNAVAILABLE
    if reason == "SPECIALIST_CAP":
        return CompositionParticipantStatus.NOT_SELECTED
    if reason in {"UNSUPPORTED_INSTRUMENT", "ATTRIBUTED_NON_FNO"}:
        return CompositionParticipantStatus.UNSUPPORTED
    return CompositionParticipantStatus.SKIPPED_BY_POLICY


def _attempt_status(
    attempt: NodeAttempt,
) -> tuple[CompositionParticipantStatus, str | None]:
    if attempt.superseded:
        return (
            CompositionParticipantStatus.SUPERSEDED,
            "SUPERSEDED_BY_CAPTURED_EVIDENCE_CHANGE",
        )
    if attempt.status in {NodeStatus.FAILED, NodeStatus.TIMED_OUT}:
        reason = attempt.reason
        if reason is None and attempt.record is not None and attempt.record.failure is not None:
            reason = attempt.record.failure.error_type
        return CompositionParticipantStatus.FAILED, reason or attempt.status.value
    if attempt.status is NodeStatus.BLOCKED:
        return CompositionParticipantStatus.SKIPPED_BY_POLICY, attempt.reason or "BLOCKED"
    if attempt.record is not None and attempt.record.status is AgentRunStatus.ABSTAINED:
        return CompositionParticipantStatus.ABSTAINED, "SPECIALIST_ABSTAINED"
    return CompositionParticipantStatus.SUCCEEDED, None


def build_orchestration_composition(
    request: OrchestrationRequest,
    plans: tuple[AnalysisPlan, ...],
    attempts: tuple[NodeAttempt, ...],
    result: OrchestrationResult,
    *,
    parent_composition_fingerprint: str | None = None,
    baseline_composition_fingerprint: str | None = None,
) -> CompositionEnvelope:
    """Project exact final-plan participation; never consult a current registry."""

    plan = plans[-1]
    specs = {item.capability.specialist: item for item in plan.registry}
    outcomes = {item.node_id: item for item in result.outcomes}
    entries: list[CompositionParticipant] = []
    for node in plan.nodes:
        attempt = next(item for item in reversed(attempts) if item.node_id == node.node_id)
        outcome = outcomes[node.node_id]
        expected_outcome = NodeStatus.SUPERSEDED if attempt.superseded else attempt.status
        if outcome.status is not expected_outcome:
            raise ValueError("composition outcome and final attempt status disagree")
        node_spec = specs[node.specialist]
        status, reason = _attempt_status(attempt)
        record = attempt.record
        invoked = status in {
            CompositionParticipantStatus.SUCCEEDED,
            CompositionParticipantStatus.FAILED,
            CompositionParticipantStatus.ABSTAINED,
            CompositionParticipantStatus.SUPERSEDED,
        }
        entries.append(
            CompositionParticipant(
                capability_id=specialist_capability_id(node.specialist),
                interface_version=(
                    record.specialist_version
                    if record is not None
                    else node_spec.capability.specialist_version
                ),
                semantic_role=node.specialist.value,
                requiredness=(
                    CompositionRequiredness.REQUIRED
                    if node.required
                    else CompositionRequiredness.OPTIONAL
                ),
                dependency_fingerprint=digest(node_spec),
                invoked=invoked,
                input_refs=tuple(sorted(attempt.consumed_ids)) if invoked else (),
                output_ref=record.record_id if record is not None else None,
                output_fingerprint=(
                    digest(semantic(record)) if record is not None else None
                ),
                status=status,
                failure_reason=reason,
                usage_knowledge=(
                    CompositionUsageKnowledge.KNOWN
                    if record is not None
                    else CompositionUsageKnowledge.UNKNOWN
                    if invoked
                    else CompositionUsageKnowledge.NOT_APPLICABLE
                ),
                usage=record.usage if record is not None else None,
            )
        )
    for skipped in plan.skipped:
        skipped_spec = specs.get(skipped.specialist)
        required = bool(skipped.required)
        entries.append(
            CompositionParticipant(
                capability_id=specialist_capability_id(skipped.specialist),
                interface_version=(
                    skipped_spec.capability.specialist_version
                    if skipped_spec is not None
                    else None
                ),
                semantic_role=skipped.specialist.value,
                requiredness=(
                    CompositionRequiredness.REQUIRED
                    if required
                    else CompositionRequiredness.OPTIONAL
                ),
                dependency_fingerprint=(
                    digest(skipped_spec) if skipped_spec is not None else None
                ),
                invoked=False,
                status=_skipped_status(skipped.reason),
                failure_reason=skipped.reason,
                usage_knowledge=CompositionUsageKnowledge.NOT_APPLICABLE,
            )
        )
    participants = tuple(sorted(entries, key=lambda item: item.capability_id))
    required_scope = tuple(
        item.capability_id
        for item in participants
        if item.requiredness is CompositionRequiredness.REQUIRED
    )
    optional_scope = tuple(
        item.capability_id
        for item in participants
        if item.requiredness is CompositionRequiredness.OPTIONAL
    )
    return CompositionEnvelope.seal(
        run_id=request.run_id,
        policy_version=plan.policy_version,
        planner_version=plan.planner_version,
        requested_scope=tuple(item.capability_id for item in participants),
        required_scope=required_scope,
        optional_scope=optional_scope,
        participants=participants,
        parent_composition_fingerprint=parent_composition_fingerprint,
        baseline_composition_fingerprint=baseline_composition_fingerprint,
    )
