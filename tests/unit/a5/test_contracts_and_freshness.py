"""A5.1 contracts, time policy, identity, and shape boundaries."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from tiaf.a4 import result_semantic_payload as a4_result_semantic_payload
from tiaf.a5 import (
    A5InputIntegrityError,
    MonitoringLifecycle,
    PositionFreshness,
    PositionIntelligenceRequest,
    PositionRecommendation,
    PositionShape,
    PositionSide,
    PositionSignalKind,
    PositionSnapshot,
    evaluate_position,
)
from tiaf.data import InstrumentType
from tiaf.planner.digests import digest

from ._support import IST, NOW, a4_result, request, signal, snapshot


def test_contracts_are_frozen_tuple_backed_json_arrays_and_round_trip() -> None:
    result = evaluate_position(request()).result
    dumped = result.model_dump(mode="json")
    assert isinstance(result.monitoring_needs, tuple)
    assert isinstance(dumped["monitoring_needs"], list)
    assert PositionIntelligenceRequest.model_validate(
        request().model_dump(mode="json")
    ) == request()
    with pytest.raises(ValidationError):
        result.recommendation = PositionRecommendation.EXIT_RECOMMENDED
    with pytest.raises(AttributeError):
        result.monitoring_needs.append(result.monitoring_needs[0])  # type: ignore[attr-defined]


def test_timestamps_normalize_to_kolkata_and_naive_is_rejected() -> None:
    value = snapshot(snapshot_at=NOW.astimezone(UTC))
    assert str(value.snapshot_at.tzinfo) == "Asia/Kolkata"
    assert value.model_dump(mode="json")["snapshot_at"].endswith("+05:30")
    with pytest.raises(ValidationError, match="timezone-aware"):
        snapshot(snapshot_at=NOW.replace(tzinfo=None))


def test_quantity_side_instrument_and_expiry_identity_are_strict() -> None:
    base = snapshot()
    with pytest.raises(ValidationError, match="LONG position"):
        PositionSnapshot.model_validate(base.model_dump(mode="json") | {"quantity": -1})
    with pytest.raises(ValidationError, match="instrument type"):
        PositionSnapshot.model_validate(
            base.model_dump(mode="json") | {"instrument_type": "FUTURE"}
        )
    with pytest.raises(ValidationError, match="derivative position requires expiry"):
        snapshot(kind=InstrumentType.FUTURE)


def test_future_snapshot_and_signal_are_rejected() -> None:
    future = NOW + timedelta(minutes=10)
    with pytest.raises(ValidationError, match="future"):
        request(position_snapshot=snapshot(snapshot_at=future))
    item = signal(PositionSignalKind.STRUCTURAL_MILESTONE).model_copy(
        update={"observed_at": future}
    )
    with pytest.raises(ValidationError, match="signal cannot be in the future"):
        request(signals=(item,))


@pytest.mark.parametrize(
    "freshness",
    (PositionFreshness.STALE, PositionFreshness.UNKNOWN),
)
def test_stale_and_unknown_snapshot_abstain(freshness: PositionFreshness) -> None:
    result = evaluate_position(
        request(position_snapshot=snapshot(freshness=freshness))
    ).result
    assert result.recommendation is PositionRecommendation.ABSTAIN
    assert result.effective_freshness is freshness
    assert result.posture.value == "UNDETERMINED"


def test_declared_fresh_but_old_snapshot_is_stale() -> None:
    old = snapshot(snapshot_at=NOW - timedelta(hours=1))
    result = evaluate_position(request(position_snapshot=old)).result
    assert result.effective_freshness is PositionFreshness.STALE
    assert result.recommendation is PositionRecommendation.ABSTAIN


def test_missing_a4_is_insufficient_not_maintain() -> None:
    result = evaluate_position(request(a4=None)).result
    assert result.recommendation is PositionRecommendation.INSUFFICIENT_EVIDENCE
    assert result.failure_codes[0].value == "MISSING_A4_RESULT"


def test_multi_leg_is_explicitly_unsupported_and_not_flattened() -> None:
    value = snapshot(shape=PositionShape.MULTI_LEG)
    result = evaluate_position(request(position_snapshot=value)).result
    assert result.status.value == "UNSUPPORTED"
    assert result.failure_codes[0].value == "UNSUPPORTED_SHAPE"
    assert result.snapshot_id == value.snapshot_id


@pytest.mark.parametrize(
    "kind",
    (InstrumentType.FUTURE, InstrumentType.CALL_OPTION, InstrumentType.PUT_OPTION),
)
def test_single_leg_derivatives_are_supported(kind: InstrumentType) -> None:
    expiry = NOW.date() + timedelta(days=10)
    result = evaluate_position(
        request(position_snapshot=snapshot(kind=kind, expiry=expiry))
    ).result
    assert result.status.value == "COMPLETE"
    assert result.recommendation is PositionRecommendation.MAINTAIN


def test_linked_a4_subject_and_fingerprint_mismatch_fail_closed() -> None:
    linked = a4_result()
    forged = linked.model_copy(update={"semantic_fingerprint": "f" * 64})
    with pytest.raises(A5InputIntegrityError, match="fingerprint"):
        evaluate_position(request(a4=forged))
    wrong_subject = linked.primary_thesis.model_copy(update={"subject": "OTHER"})
    provisional = linked.model_copy(update={"primary_thesis": wrong_subject})
    fingerprint = digest(a4_result_semantic_payload(provisional))
    resealed_subject = provisional.model_copy(
        update={
            "result_id": f"a4-result:{fingerprint[:24]}",
            "semantic_fingerprint": fingerprint,
        }
    )
    with pytest.raises(A5InputIntegrityError, match="subject mismatch"):
        evaluate_position(request(a4=resealed_subject))


def test_short_requires_negative_quantity() -> None:
    base = snapshot()
    valid = PositionSnapshot.model_validate(
        base.model_dump(mode="json") | {"side": PositionSide.SHORT, "quantity": -10}
    )
    assert valid.quantity == -10


def test_inactive_mandate_does_not_close_open_position() -> None:
    result = evaluate_position(request(lifecycle=MonitoringLifecycle.INACTIVE)).result
    assert result.watch_mandate.lifecycle is MonitoringLifecycle.INACTIVE
    assert not result.monitoring_needs
    assert result.recommendation is PositionRecommendation.MAINTAIN
    assert result.watch_mandate.position_ref == result.position_id


def test_naive_request_as_of_is_rejected() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        request(as_of=datetime(2026, 9, 10, 12, 5))


def test_current_timestamp_is_not_manually_offset() -> None:
    result = evaluate_position(request()).result
    assert result.as_of.tzinfo == IST
