"""Deterministic A5.1 fixtures over accepted A4 records."""

from datetime import date, datetime, timedelta
from typing import cast
from zoneinfo import ZoneInfo

from tiaf.a4 import A4Result, evaluate_projection
from tiaf.a5 import (
    MonitoringLifecycle,
    OperationalPositionState,
    PositionFreshness,
    PositionIntelligenceRequest,
    PositionIntelligenceResult,
    PositionProduct,
    PositionShape,
    PositionSide,
    PositionSignal,
    PositionSignalKind,
    PositionSnapshot,
    deterministic_policy,
)
from tiaf.contracts import Horizon, OptionType
from tiaf.data import InstrumentKey, InstrumentType, MarketSegment

from ..a4._support import clean_projection, with_state

IST = ZoneInfo("Asia/Kolkata")
NOW = datetime(2026, 9, 10, 12, tzinfo=IST)
_DEFAULT_A4 = object()


def a4_result(state: str = "OPPORTUNITY") -> A4Result:
    projection = clean_projection() if state == "OPPORTUNITY" else with_state(state)
    return evaluate_projection(
        projection,
        evaluated_at=projection.header.evidence_as_of,
    ).result


def instrument(
    kind: InstrumentType = InstrumentType.EQUITY,
    *,
    expiry: date | None = None,
) -> InstrumentKey:
    if kind is InstrumentType.EQUITY:
        return InstrumentKey(
            symbol="SYNTHETIC",
            exchange="NSE",
            segment=MarketSegment.NSE_EQUITY,
            instrument_type=kind,
        )
    if kind is InstrumentType.FUTURE:
        return InstrumentKey(
            symbol="SYNTHETIC-FUT",
            exchange="NSE",
            segment=MarketSegment.NSE_FNO,
            instrument_type=kind,
            expiry=expiry,
        )
    option_type = OptionType.CE if kind is InstrumentType.CALL_OPTION else OptionType.PE
    return InstrumentKey(
        symbol="SYNTHETIC-100-CE" if option_type is OptionType.CE else "SYNTHETIC-100-PE",
        exchange="NSE",
        segment=MarketSegment.NSE_FNO,
        instrument_type=kind,
        expiry=expiry,
        strike=100.0,
        option_type=option_type,
    )


def snapshot(
    *,
    kind: InstrumentType = InstrumentType.EQUITY,
    expiry: date | None = None,
    freshness: PositionFreshness = PositionFreshness.CURRENT,
    snapshot_at: datetime = NOW,
    shape: PositionShape = PositionShape.SINGLE_LEG,
    product: PositionProduct = PositionProduct.DELIVERY,
    mandatory_exit_at: datetime | None = None,
) -> PositionSnapshot:
    return PositionSnapshot(
        position_id="position:synthetic-one",
        snapshot_id=f"position-snapshot:{kind.value.lower()}-{int(snapshot_at.timestamp())}",
        tm_position_ref="tm-position:synthetic-one",
        instrument=instrument(kind, expiry=expiry),
        underlying="SYNTHETIC",
        instrument_type=kind,
        shape=shape,
        leg_refs=(
            ("position-leg:one", "position-leg:two")
            if shape is PositionShape.MULTI_LEG
            else ()
        ),
        side=PositionSide.LONG,
        quantity=10,
        entry_price=100.0,
        entry_at=NOW - timedelta(days=2),
        current_price=105.0,
        unrealized_pnl=50.0,
        realized_pnl=0.0,
        product=product,
        expiry=expiry,
        operational_state=OperationalPositionState.OPEN,
        operational_source_id="operational-source:fixture",
        snapshot_at=snapshot_at,
        snapshot_version="1",
        declared_freshness=freshness,
        freshness_basis="fixture wall-clock status",
        mandatory_exit_at=mandatory_exit_at,
        authority_refs=("authority:position-fixture",),
    )


def signal(kind: PositionSignalKind, *, a4: A4Result | None = None) -> PositionSignal:
    condition_ref = None
    if kind is PositionSignalKind.THESIS_INVALIDATION:
        assert a4 is not None and a4.invalidation_conditions
        condition_ref = a4.invalidation_conditions[0].condition_id
    return PositionSignal(
        signal_id=f"position-signal:{kind.value.lower()}",
        kind=kind,
        evidence_refs=(f"evidence:{kind.value.lower()}",),
        observed_at=NOW,
        condition_ref=condition_ref,
        reason_code=f"SUPPLIED_{kind.value}",
    )


def request(
    *,
    position_snapshot: PositionSnapshot | None = None,
    a4: A4Result | None | object = _DEFAULT_A4,
    successor: A4Result | None = None,
    signals: tuple[PositionSignal, ...] = (),
    as_of: datetime = NOW + timedelta(minutes=5),
    previous: PositionIntelligenceResult | None = None,
    successor_reason: str | None = None,
    lifecycle: MonitoringLifecycle = MonitoringLifecycle.ACTIVE_POSITION,
    policy_version: str = "1.0",
) -> PositionIntelligenceRequest:
    policy = deterministic_policy(version=policy_version)
    selected_a4 = (
        a4_result() if a4 is _DEFAULT_A4 else cast(A4Result | None, a4)
    )
    return PositionIntelligenceRequest(
        request_id=f"a5-request:{int(as_of.timestamp())}-{policy_version}",
        snapshot=position_snapshot or snapshot(),
        a4_result=selected_a4,
        successor_a4_result=successor,
        objective="manage current position",
        horizon=Horizon(label="POSITIONAL", min_days=1, max_days=20),
        as_of=as_of,
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
        monitoring_policy_ref=policy.monitoring_policy_ref,
        mandate_lifecycle=lifecycle,
        authority_refs=("authority:a5-fixture",),
        budget_ref="budget:a5-zero-live",
        signals=signals,
        previous_result=previous,
        successor_reason=successor_reason,
    )
