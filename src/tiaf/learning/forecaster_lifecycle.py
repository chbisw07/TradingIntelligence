"""Externally authored lifecycle evidence, never a runtime promotion executor.

Records are stored by the existing Learning custody owner. A history is a
validated, caller-pinned chain, not a mutable current-state/active-model registry.
FLC-2 can demonstrate transitions in synthetic history; no record grants use.
"""

from typing import Literal, Self

from pydantic import Field, model_validator

from tiaf.forecasting.forecaster_seams import (
    ForecasterKey,
    ForecasterLifecycle,
    ForecasterRole,
)
from tiaf.forecasting.identity import ArtifactReference, ForecastDateTime, LogicalId

from .forecast_artifacts import SealedResearch
from .forecaster_training import reference


class LifecycleSubject(SealedResearch):
    forecaster: ForecasterKey
    model_identity: ArtifactReference | None = None
    role: ForecasterRole
    initial_state: ForecasterLifecycle
    purpose: Literal["READ_ONLY_LEGACY", "SYNTHETIC_DEMONSTRATION"]
    created_at: ForecastDateTime

    @model_validator(mode="after")
    def no_synthetic_initial_approval(self) -> Self:
        if (
            self.purpose == "SYNTHETIC_DEMONSTRATION"
            and self.initial_state != ForecasterLifecycle.EXPERIMENTAL
        ):
            raise ValueError("SYNTHETIC_LIFECYCLE_MUST_START_EXPERIMENTAL")
        return self


class TransitionRequest(SealedResearch):
    subject_reference: ArtifactReference
    predecessor_reference: ArtifactReference
    current_state: ForecasterLifecycle
    requested_state: ForecasterLifecycle
    scope: LogicalId
    evidence_references: tuple[ArtifactReference, ...] = Field(min_length=1)
    previous_policy: ArtifactReference
    proposed_policy: ArtifactReference
    requested_at: ForecastDateTime


class ApprovalDecision(SealedResearch):
    """Authored by an external reviewer. Hash integrity is not authentication."""

    approval_id: LogicalId
    request_reference: ArtifactReference
    subject_reference: ArtifactReference
    authority_reference: ArtifactReference
    reviewer: LogicalId
    decision: Literal["APPROVED", "DENIED", "HELD", "REJECTED"]
    scope: LogicalId
    evidence_references: tuple[ArtifactReference, ...] = Field(min_length=1)
    reason: str = Field(min_length=1)
    created_at: ForecastDateTime
    expires_at: ForecastDateTime

    @model_validator(mode="after")
    def clocks(self) -> Self:
        if self.expires_at <= self.created_at:
            raise ValueError("INVALID_APPROVAL_EXPIRY")
        return self


# Scope-authorized resumption is deliberately no broader than known stable states.
_EDGES = {
    ForecasterLifecycle.EXPERIMENTAL: {ForecasterLifecycle.VALIDATED, ForecasterLifecycle.RETIRED},
    ForecasterLifecycle.VALIDATED: {
        ForecasterLifecycle.SHADOW,
        ForecasterLifecycle.SUSPENDED,
        ForecasterLifecycle.RETIRED,
    },
    ForecasterLifecycle.SHADOW: {
        ForecasterLifecycle.APPROVED,
        ForecasterLifecycle.SUSPENDED,
        ForecasterLifecycle.RETIRED,
    },
    ForecasterLifecycle.APPROVED: {ForecasterLifecycle.SUSPENDED, ForecasterLifecycle.RETIRED},
    ForecasterLifecycle.SUSPENDED: {
        ForecasterLifecycle.VALIDATED,
        ForecasterLifecycle.SHADOW,
        ForecasterLifecycle.APPROVED,
        ForecasterLifecycle.RETIRED,
    },
    ForecasterLifecycle.RETIRED: set(),
    ForecasterLifecycle.UNSPECIFIED: set(),
}


class LifecycleRecord(SealedResearch):
    request: TransitionRequest
    approval: ApprovalDecision
    # Keep qualified original events rather than translating away A7 source data.
    source_event_id: LogicalId
    source_event_name: Literal[
        "VALIDATED",
        "SHADOW_APPROVED",
        "ADVISORY_APPROVED",
        "SUSPENDED",
        "RETIRED",
        "DENIED",
        "HELD",
        "REJECTED",
    ]
    source_event_schema: str = Field(min_length=1)
    effective_at: ForecastDateTime
    recorded_at: ForecastDateTime
    resulting_state: ForecasterLifecycle
    runtime_effect: Literal["NONE"] = "NONE"

    @model_validator(mode="after")
    def decision(self) -> Self:
        r, a = self.request, self.approval
        if (
            a.request_reference != reference("transition", r)
            or a.subject_reference != r.subject_reference
            or a.scope != r.scope
            or a.evidence_references != r.evidence_references
            or not r.requested_at <= a.created_at <= self.effective_at <= self.recorded_at
        ):
            raise ValueError("LIFECYCLE_APPROVAL_LINK_MISMATCH")
        accepted = a.decision == "APPROVED"
        if accepted and (
            r.requested_state not in _EDGES[r.current_state] or self.effective_at >= a.expires_at
        ):
            raise ValueError("INVALID_OR_EXPIRED_LIFECYCLE_TRANSITION")
        expected = r.requested_state if accepted else r.current_state
        name = (
            {
                ForecasterLifecycle.VALIDATED: "VALIDATED",
                ForecasterLifecycle.SHADOW: "SHADOW_APPROVED",
                ForecasterLifecycle.APPROVED: "ADVISORY_APPROVED",
                ForecasterLifecycle.SUSPENDED: "SUSPENDED",
                ForecasterLifecycle.RETIRED: "RETIRED",
            }.get(expected)
            if accepted
            else a.decision
        )
        if self.resulting_state != expected or self.source_event_name != name:
            raise ValueError("LOSSY_LIFECYCLE_EVENT_MAPPING")
        return self


class LifecycleObservation(SealedResearch):
    """Retain stage events without converting a fit/evaluation into approval."""

    subject_reference: ArtifactReference
    predecessor_reference: ArtifactReference
    source_event_id: LogicalId
    source_event_name: Literal["REGISTERED", "TRAINED", "CALIBRATION_FITTED", "EVALUATED"]
    source_event_schema: str = Field(min_length=1)
    evidence_references: tuple[ArtifactReference, ...] = Field(min_length=1)
    current_state: ForecasterLifecycle
    effective_at: ForecastDateTime
    recorded_at: ForecastDateTime
    runtime_effect: Literal["NONE"] = "NONE"

    @property
    def resulting_state(self) -> ForecasterLifecycle:
        return self.current_state

    @model_validator(mode="after")
    def stage(self) -> Self:
        if self.effective_at > self.recorded_at or (
            self.source_event_name != "EVALUATED"
            and self.current_state != ForecasterLifecycle.EXPERIMENTAL
        ):
            raise ValueError("STAGE_EVENT_CANNOT_PROMOTE")
        return self


class LifecycleHistory(SealedResearch):
    subject: LifecycleSubject
    records: tuple[LifecycleRecord | LifecycleObservation, ...] = Field(default=(), max_length=64)

    @model_validator(mode="after")
    def chain(self) -> Self:
        subject_ref = reference("subject", self.subject)
        previous = subject_ref
        state, at = self.subject.initial_state, self.subject.created_at
        policy: ArtifactReference | None = None
        ids: set[str] = set()
        attained = {state}
        for record in self.records:
            if isinstance(record, LifecycleObservation):
                if (
                    record.subject_reference != subject_ref
                    or record.predecessor_reference != previous
                    or record.current_state != state
                    or record.effective_at < at
                    or record.source_event_id in ids
                ):
                    raise ValueError("LIFECYCLE_HISTORY_MISMATCH")
                at = record.recorded_at
                previous = reference("observation", record)
                ids.add(record.source_event_id)
                continue
            req = record.request
            if (
                req.subject_reference != subject_ref
                or req.predecessor_reference != previous
                or req.current_state != state
                or req.requested_at < at
                or record.source_event_id in ids
                or (policy is not None and req.previous_policy != policy)
            ):
                raise ValueError("LIFECYCLE_HISTORY_MISMATCH")
            accepted = record.approval.decision == "APPROVED"
            if accepted and self.subject.purpose != "SYNTHETIC_DEMONSTRATION":
                raise ValueError("LEGACY_PROMOTION_NOT_IMPLEMENTED")
            if (
                accepted
                and state == ForecasterLifecycle.SUSPENDED
                and (
                    record.resulting_state not in attained
                    and record.resulting_state != ForecasterLifecycle.RETIRED
                )
            ):
                raise ValueError("RESUMPTION_CANNOT_SKIP_PRIOR_QUALIFICATION")
            state, at = record.resulting_state, record.recorded_at
            attained.add(state)
            policy = req.proposed_policy if accepted else req.previous_policy
            previous = reference("event", record)
            ids.add(record.source_event_id)
        return self


class ActivationState(SealedResearch):
    subject_reference: ArtifactReference
    eligible: Literal[False] = False
    selected: Literal[False] = False
    reason: Literal["FLC2_DOES_NOT_GRANT_RUNTIME_USE"] = "FLC2_DOES_NOT_GRANT_RUNTIME_USE"
