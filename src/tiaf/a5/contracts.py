"""Immutable provider- and broker-neutral A5.1 contracts."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal, Self

from pydantic import Field, StringConstraints, model_validator

from tiaf.a4 import A4Result
from tiaf.contracts import ContractModel, Horizon
from tiaf.contracts.common import NonEmptyStr, Symbol, TiafDateTime
from tiaf.data import InstrumentKey, InstrumentType
from tiaf.planner.models import Sha256
from tiaf.source_semantics.contracts import QualifiedId

from ._validation import validate_no_secrets
from .enums import (
    A5ExecutionStatus,
    A5FailureCode,
    A5ReplayMode,
    MonitoringLifecycle,
    MonitoringPriority,
    MonitoringTriggerKind,
    OperationalPositionState,
    PositionFreshness,
    PositionProduct,
    PositionRecommendation,
    PositionRiskPosture,
    PositionShape,
    PositionSide,
    PositionSignalKind,
    ProtectionIntentKind,
    ReferenceLevelKind,
    RemainingOpportunity,
    ThesisHealth,
)

FiniteFloat = Annotated[float, Field(allow_inf_nan=False)]
PositiveFiniteFloat = Annotated[float, Field(gt=0, allow_inf_nan=False)]
NonZeroFiniteFloat = Annotated[
    float,
    Field(allow_inf_nan=False),
]
EvidenceFamily = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[A-Z][A-Z0-9_]*$"),
]


def _unique(values: tuple[object, ...], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must be unique")


class ReferenceLevel(ContractModel):
    """A cited analytical level; never an executable order price."""

    level_id: QualifiedId
    kind: ReferenceLevelKind
    value: PositiveFiniteFloat
    evidence_refs: tuple[NonEmptyStr, ...]
    observed_at: TiafDateTime
    executable: Literal[False] = False

    @model_validator(mode="after")
    def cited(self) -> Self:
        if not self.evidence_refs:
            raise ValueError("reference level requires cited supplied evidence")
        _unique(self.evidence_refs, "reference-level evidence refs")
        return self


class PositionSnapshot(ContractModel):
    schema_id: Literal["tiaf.a5.position-snapshot"] = "tiaf.a5.position-snapshot"
    schema_version: Literal["1.0"] = "1.0"
    position_id: QualifiedId
    snapshot_id: QualifiedId
    tm_position_ref: QualifiedId | None = None
    instrument: InstrumentKey
    underlying: Symbol
    instrument_type: InstrumentType
    shape: PositionShape
    leg_refs: tuple[QualifiedId, ...] = ()
    side: PositionSide
    quantity: NonZeroFiniteFloat
    entry_price: PositiveFiniteFloat
    entry_at: TiafDateTime
    current_price: PositiveFiniteFloat | None = None
    unrealized_pnl: FiniteFloat | None = None
    realized_pnl: FiniteFloat | None = None
    product: PositionProduct
    expiry: date | None = None
    operational_state: OperationalPositionState
    operational_source_id: NonEmptyStr
    snapshot_at: TiafDateTime
    snapshot_version: NonEmptyStr
    declared_freshness: PositionFreshness
    freshness_basis: NonEmptyStr
    supplied_levels: tuple[ReferenceLevel, ...] = ()
    mandatory_exit_at: TiafDateTime | None = None
    authority_refs: tuple[QualifiedId, ...]

    @model_validator(mode="after")
    def coherent_snapshot(self) -> Self:
        if self.instrument_type is not self.instrument.instrument_type:
            raise ValueError("position instrument type must match instrument identity")
        if self.quantity == 0:
            raise ValueError("position quantity must be non-zero")
        if self.side is PositionSide.LONG and self.quantity < 0:
            raise ValueError("LONG position requires positive signed quantity")
        if self.side is PositionSide.SHORT and self.quantity > 0:
            raise ValueError("SHORT position requires negative signed quantity")
        derivative = self.instrument_type in {
            InstrumentType.FUTURE,
            InstrumentType.CALL_OPTION,
            InstrumentType.PUT_OPTION,
        }
        if derivative and self.expiry is None:
            raise ValueError("derivative position requires expiry")
        if not derivative and self.expiry is not None:
            raise ValueError("non-derivative position cannot set expiry")
        if self.expiry != self.instrument.expiry:
            raise ValueError("position expiry must match instrument identity")
        if self.shape is PositionShape.SINGLE_LEG and len(self.leg_refs) > 1:
            raise ValueError("single-leg position cannot contain multiple leg refs")
        if self.shape is PositionShape.MULTI_LEG and len(self.leg_refs) < 2:
            raise ValueError("multi-leg position requires at least two leg refs")
        if self.snapshot_at < self.entry_at:
            raise ValueError("snapshot cannot precede position entry")
        if self.mandatory_exit_at is not None and self.product is not PositionProduct.INTRADAY:
            raise ValueError("mandatory exit window is only valid for intraday positions")
        if not self.authority_refs:
            raise ValueError("position snapshot requires authority refs")
        _unique(self.leg_refs, "position leg refs")
        _unique(self.authority_refs, "position authority refs")
        _unique(tuple(item.level_id for item in self.supplied_levels), "supplied level IDs")
        validate_no_secrets(self.model_dump(mode="json"))
        return self


class PositionSignal(ContractModel):
    """A normalized, caller-supplied position observation consumed without recalculation."""

    signal_id: QualifiedId
    kind: PositionSignalKind
    evidence_refs: tuple[NonEmptyStr, ...]
    observed_at: TiafDateTime
    condition_ref: QualifiedId | None = None
    reference_level: ReferenceLevel | None = None
    reason_code: NonEmptyStr

    @model_validator(mode="after")
    def cited(self) -> Self:
        if not self.evidence_refs:
            raise ValueError("position signal requires cited supplied evidence")
        if self.kind is PositionSignalKind.THESIS_INVALIDATION and self.condition_ref is None:
            raise ValueError("thesis-invalidation signal requires condition_ref")
        if self.reference_level is not None and not set(
            self.reference_level.evidence_refs
        ) <= set(self.evidence_refs):
            raise ValueError("signal reference level must use signal evidence")
        _unique(self.evidence_refs, "position-signal evidence refs")
        return self


class A5DeterministicPolicy(ContractModel):
    schema_id: Literal["tiaf.a5.deterministic-policy"] = "tiaf.a5.deterministic-policy"
    schema_version: Literal["1.0"] = "1.0"
    policy_id: QualifiedId
    policy_version: NonEmptyStr
    monitoring_policy_ref: QualifiedId
    max_snapshot_age_seconds: int = Field(gt=0)
    near_expiry_days: int = Field(ge=0)
    heartbeat_seconds: int = Field(gt=0)
    intraday_exit_warning_seconds: int = Field(gt=0)
    max_provider_calls: Literal[0] = 0
    max_model_calls: Literal[0] = 0
    rule_order: tuple[NonEmptyStr, ...]

    @model_validator(mode="after")
    def bounded(self) -> Self:
        if not self.rule_order:
            raise ValueError("A5 policy requires explicit rule order")
        _unique(self.rule_order, "A5 policy rule order")
        return self


class PositionIntelligenceRequest(ContractModel):
    schema_id: Literal["tiaf.a5.position-request"] = "tiaf.a5.position-request"
    schema_version: Literal["1.0"] = "1.0"
    request_id: QualifiedId
    snapshot: PositionSnapshot
    a4_result: A4Result | None
    successor_a4_result: A4Result | None = None
    objective: NonEmptyStr
    horizon: Horizon
    as_of: TiafDateTime
    policy_id: QualifiedId
    policy_version: NonEmptyStr
    monitoring_policy_ref: QualifiedId
    mandate_lifecycle: MonitoringLifecycle = MonitoringLifecycle.ACTIVE_POSITION
    authority_refs: tuple[QualifiedId, ...]
    budget_ref: QualifiedId
    signals: tuple[PositionSignal, ...] = ()
    previous_result: PositionIntelligenceResult | None = None
    successor_reason: NonEmptyStr | None = None

    @model_validator(mode="after")
    def coherent_request(self) -> Self:
        if self.snapshot.snapshot_at > self.as_of:
            raise ValueError("position snapshot cannot be in the future relative to as_of")
        if any(item.observed_at > self.as_of for item in self.signals):
            raise ValueError("position signal cannot be in the future relative to as_of")
        if not self.authority_refs:
            raise ValueError("position request requires authority refs")
        if self.previous_result is None and self.successor_reason is not None:
            raise ValueError("successor reason requires previous A5 result")
        if self.previous_result is not None:
            if self.successor_reason is None:
                raise ValueError("previous A5 result requires successor reason")
            if self.previous_result.position_id != self.snapshot.position_id:
                raise ValueError("previous A5 result position identity mismatch")
            if self.previous_result.as_of > self.as_of:
                raise ValueError("previous A5 result cannot be later than request")
        _unique(self.authority_refs, "request authority refs")
        _unique(tuple(item.signal_id for item in self.signals), "position signal IDs")
        validate_no_secrets(self.model_dump(mode="json"))
        return self


class ProtectionIntent(ContractModel):
    kind: ProtectionIntentKind
    reference_levels: tuple[ReferenceLevel, ...] = ()
    reason_codes: tuple[NonEmptyStr, ...]
    executable: Literal[False] = False


class MonitoringNeed(ContractModel):
    need_id: QualifiedId
    position_ref: QualifiedId
    objective: NonEmptyStr
    horizon: Horizon
    evidence_family: EvidenceFamily
    trigger_kind: MonitoringTriggerKind
    trigger_reference: NonEmptyStr
    priority: MonitoringPriority
    freshness_intent_seconds: int = Field(gt=0)
    cadence_hint_seconds: int | None = Field(default=None, gt=0)
    next_due_at: TiafDateTime | None = None
    reason_code: NonEmptyStr
    material: bool
    policy_ref: QualifiedId
    budget_ref: QualifiedId


class WatchMandate(ContractModel):
    schema_id: Literal["tiaf.a5.watch-mandate"] = "tiaf.a5.watch-mandate"
    schema_version: Literal["1.0"] = "1.0"
    mandate_id: QualifiedId
    revision: int = Field(gt=0)
    predecessor_ref: QualifiedId | None = None
    position_ref: QualifiedId
    instrument: InstrumentKey
    objective: NonEmptyStr
    horizon: Horizon
    lifecycle: MonitoringLifecycle
    priority: MonitoringPriority
    needs: tuple[MonitoringNeed, ...]
    analysis_depth_ref: QualifiedId
    policy_ref: QualifiedId
    budget_ref: QualifiedId
    created_at: TiafDateTime
    as_of: TiafDateTime
    authority_refs: tuple[QualifiedId, ...]

    @model_validator(mode="after")
    def bounded_mandate(self) -> Self:
        if self.lifecycle is MonitoringLifecycle.ACTIVE_POSITION and not self.needs:
            raise ValueError("active-position mandate requires monitoring needs")
        if any(item.position_ref != self.position_ref for item in self.needs):
            raise ValueError("monitoring need position mismatch")
        _unique(tuple(item.need_id for item in self.needs), "monitoring need IDs")
        _unique(self.authority_refs, "mandate authority refs")
        return self


class A5Usage(ContractModel):
    provider_calls: Literal[0] = 0
    model_calls: Literal[0] = 0
    input_tokens: Literal[0] = 0
    output_tokens: Literal[0] = 0
    model_cost_units: Literal[0] = 0
    model_cost_knowledge: Literal["KNOWN_ZERO"] = "KNOWN_ZERO"
    parent_usage_refs: tuple[NonEmptyStr, ...]


class PositionIntelligenceResult(ContractModel):
    schema_id: Literal["tiaf.a5.position-result"] = "tiaf.a5.position-result"
    schema_version: Literal["1.0"] = "1.0"
    result_id: QualifiedId
    run_id: QualifiedId
    request_id: QualifiedId
    position_id: QualifiedId
    snapshot_id: QualifiedId
    snapshot_at: TiafDateTime
    as_of: TiafDateTime
    effective_freshness: PositionFreshness
    freshness_reasons: tuple[NonEmptyStr, ...]
    linked_a4_result_id: QualifiedId | None
    linked_a4_fingerprint: Sha256 | None
    linked_thesis_refs: tuple[QualifiedId, ...]
    previous_result_ref: QualifiedId | None = None
    previous_posture: PositionRiskPosture | None = None
    successor_reason: NonEmptyStr | None = None
    changed_input_refs: tuple[NonEmptyStr, ...] = ()
    status: A5ExecutionStatus
    posture: PositionRiskPosture
    thesis_health: ThesisHealth
    recommendation: PositionRecommendation
    protection_intent: ProtectionIntent
    remaining_opportunity: RemainingOpportunity
    monitoring_needs: tuple[MonitoringNeed, ...]
    watch_mandate: WatchMandate
    evidence_refs: tuple[NonEmptyStr, ...]
    contradictions: tuple[NonEmptyStr, ...]
    gaps: tuple[NonEmptyStr, ...]
    reason_codes: tuple[NonEmptyStr, ...]
    invalidation_condition_refs: tuple[QualifiedId, ...]
    failure_codes: tuple[A5FailureCode, ...] = ()
    policy_id: QualifiedId
    policy_version: NonEmptyStr
    usage: A5Usage
    replay_identity: QualifiedId
    authority_statement: Literal[
        "ADVISORY_ONLY_TRADEMONITOR_DECIDES_BROKER_EXECUTION"
    ] = "ADVISORY_ONLY_TRADEMONITOR_DECIDES_BROKER_EXECUTION"
    semantic_fingerprint: Sha256

    @model_validator(mode="after")
    def coherent_result(self) -> Self:
        if self.watch_mandate.position_ref != self.position_id:
            raise ValueError("watch mandate position mismatch")
        if self.monitoring_needs != self.watch_mandate.needs:
            raise ValueError("result and watch mandate monitoring needs differ")
        predecessor_fields = (self.previous_posture, self.successor_reason)
        if self.previous_result_ref is None and any(
            value is not None for value in predecessor_fields
        ):
            raise ValueError("A5 successor fields require previous result ref")
        if self.previous_result_ref is not None and any(
            value is None for value in predecessor_fields
        ):
            raise ValueError("previous A5 result requires complete successor fields")
        if self.status is A5ExecutionStatus.COMPLETE and self.failure_codes:
            raise ValueError("complete A5 result cannot contain failure codes")
        for values, label in (
            (self.linked_thesis_refs, "linked thesis refs"),
            (self.changed_input_refs, "changed input refs"),
            (self.evidence_refs, "result evidence refs"),
            (self.contradictions, "result contradictions"),
            (self.gaps, "result gaps"),
            (self.reason_codes, "result reason codes"),
            (self.invalidation_condition_refs, "result invalidation refs"),
            (self.failure_codes, "result failure codes"),
        ):
            _unique(values, label)
        return self


class A5RunRecord(ContractModel):
    schema_id: Literal["tiaf.a5.deterministic-run"] = "tiaf.a5.deterministic-run"
    schema_version: Literal["1.0"] = "1.0"
    run_id: QualifiedId
    request: PositionIntelligenceRequest
    policy: A5DeterministicPolicy
    result: PositionIntelligenceResult
    evaluated_at: TiafDateTime
    fingerprint: Sha256


class A5Capture(ContractModel):
    schema_id: Literal["tiaf.a5.deterministic-capture"] = "tiaf.a5.deterministic-capture"
    schema_version: Literal["1.0"] = "1.0"
    capture_id: QualifiedId
    snapshot_json: NonEmptyStr
    snapshot_checksum: Sha256
    snapshot_fingerprint: Sha256
    a4_result_json: NonEmptyStr | None
    a4_result_checksum: Sha256 | None
    a4_result_fingerprint: Sha256 | None
    run_json: NonEmptyStr
    run_checksum: Sha256
    run_fingerprint: Sha256
    exact_capture_checksum: Sha256
    captured_at: TiafDateTime


class A5ReplayResult(ContractModel):
    replay_id: QualifiedId
    mode: Literal[A5ReplayMode.RECORDED] = A5ReplayMode.RECORDED
    record: A5RunRecord
    provider_calls: Literal[0] = 0
    model_calls: Literal[0] = 0
    replayed_at: TiafDateTime
    fingerprint: Sha256


class A5VerificationResult(ContractModel):
    verification_id: QualifiedId
    mode: Literal[A5ReplayMode.DETERMINISTIC_VERIFICATION] = (
        A5ReplayMode.DETERMINISTIC_VERIFICATION
    )
    recorded_run_fingerprint: Sha256
    verified_run_fingerprint: Sha256
    recorded_semantic_fingerprint: Sha256
    verified_semantic_fingerprint: Sha256
    exact_match: bool
    provider_calls: Literal[0] = 0
    model_calls: Literal[0] = 0
    verified_at: TiafDateTime
    fingerprint: Sha256


class A5PolicyComparison(ContractModel):
    comparison_id: QualifiedId
    mode: Literal[A5ReplayMode.POLICY_COMPARISON] = A5ReplayMode.POLICY_COMPARISON
    original_policy: tuple[QualifiedId, NonEmptyStr]
    candidate_policy: tuple[QualifiedId, NonEmptyStr]
    original_run_fingerprint: Sha256
    candidate_run_fingerprint: Sha256
    original_recommendation: PositionRecommendation
    candidate_recommendation: PositionRecommendation
    original_posture: PositionRiskPosture
    candidate_posture: PositionRiskPosture
    exact_match: bool
    compared_at: TiafDateTime
    fingerprint: Sha256
