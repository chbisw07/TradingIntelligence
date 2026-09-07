"""Snapshot identity, serialization, security, and offline replay tests."""

import socket
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from tiaf import __version__
from tiaf.baseline import BaselineEngine, default_policy
from tiaf.contracts import TradeStyle
from tiaf.evaluation import (
    BaselineRunRecord,
    ReplayRequest,
    SnapshotIntegrityError,
    create_evidence_snapshot,
    load_snapshot_json,
    replay,
    snapshot_json,
)

from ..baseline._support import NOW, baseline_request
from ._support import frozen_case


def test_snapshot_is_immutable_round_trips_and_has_stable_fingerprint() -> None:
    snapshot, _ = frozen_case()
    serialized = snapshot_json(snapshot)
    rebuilt = load_snapshot_json(serialized)
    assert rebuilt == snapshot
    assert snapshot_json(rebuilt) == serialized
    assert len(snapshot.fingerprint) == 64
    assert snapshot.snapshot_id == rebuilt.snapshot_id
    assert serialized.count("+05:30") > 0
    with pytest.raises(ValidationError):
        snapshot.subject = "OTHER"


def test_run_record_is_immutable_json_round_trippable_and_keeps_arrays() -> None:
    _, run = frozen_case()
    payload = run.model_dump(mode="json")
    assert isinstance(payload["component_scores"], list)
    assert isinstance(payload["reasons"], list)
    assert BaselineRunRecord.model_validate(payload) == run
    with pytest.raises(ValidationError):
        run.opportunity_score = 0.0


def test_snapshot_creation_time_is_nonsemantic_but_decision_evidence_is_semantic() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    request = baseline_request(policy)
    first = create_evidence_snapshot(
        request,
        policy_id=policy.policy_id,
        producer_version=__version__,
        benchmark_symbol="NIFTY",
        snapshot_created_at=NOW,
    )
    later = create_evidence_snapshot(
        request,
        policy_id=policy.policy_id,
        producer_version=__version__,
        benchmark_symbol="NIFTY",
        snapshot_created_at=NOW + timedelta(days=30),
        metadata={"archive_note": "copied later"},
    )
    assert first.fingerprint == later.fingerprint
    assert first.snapshot_id == later.snapshot_id


def test_tampered_semantic_evidence_fails_integrity_validation() -> None:
    snapshot, _ = frozen_case()
    payload = snapshot.model_dump(mode="json")
    payload["decision_request"]["subject"] = "OTHER"
    with pytest.raises(SnapshotIntegrityError):
        load_snapshot_json(__import__("json").dumps(payload))


def test_secret_bearing_metadata_is_rejected() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    request = baseline_request(policy).model_copy(update={"metadata": {"access_token": "x"}})
    with pytest.raises(ValueError, match="secret-bearing"):
        create_evidence_snapshot(
            request,
            policy_id=policy.policy_id,
            producer_version=__version__,
            snapshot_created_at=NOW,
        )


def test_freshness_source_order_is_canonical_and_assessment_identity_is_stable() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    request = baseline_request(policy, include_mtf=True)
    payload = request.model_dump(mode="python")
    payload["evidence_freshness"] = tuple(reversed(payload["evidence_freshness"]))
    reordered = type(request).model_validate(payload)
    assert reordered.evidence_freshness == request.evidence_freshness
    engine = BaselineEngine((policy,))
    assert engine.assess(reordered) == engine.assess(request)


def test_assessment_identity_ignores_metadata_dictionary_insertion_order() -> None:
    policy = default_policy(TradeStyle.POSITIONAL)
    request = baseline_request(policy).model_copy(
        update={"metadata": {"z_last": "value", "a_first": "value"}}
    )
    reversed_metadata = request.model_copy(
        update={"metadata": {"a_first": "value", "z_last": "value"}}
    )
    engine = BaselineEngine((policy,))
    assert engine.assess(request) == engine.assess(reversed_metadata)


def test_replay_is_exact_repeated_serialized_and_network_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    snapshot, run = frozen_case()
    monkeypatch.setattr(
        socket,
        "create_connection",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("network used")),
    )
    first = replay(
        ReplayRequest(
            snapshot=snapshot,
            policy=default_policy(TradeStyle.POSITIONAL),
            expected_assessment=run.assessment,
            replay_time=NOW,
        )
    )
    rebuilt = load_snapshot_json(snapshot_json(snapshot))
    second = replay(
        ReplayRequest(
            snapshot=rebuilt,
            policy=default_policy(TradeStyle.POSITIONAL),
            expected_assessment=run.assessment,
            replay_time=datetime(2035, 1, 1, tzinfo=UTC),
        )
    )
    assert first.assessment == run.assessment == second.assessment
    assert first.assessment.model_dump_json() == run.assessment.model_dump_json()
    assert first.replay_id == second.replay_id
    assert first.exact_match is second.exact_match is True
    assert first.differences == second.differences == ()
    assert first.replay_time != second.replay_time
    assert first.assessment.evidence_freshness == snapshot.decision_request.evidence_freshness
    assert all(
        item.state.value == "FRESH" for item in first.assessment.evidence_freshness
    )


def test_replay_ignores_failing_provider_and_resolver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from tiaf.data.providers.dhan import DhanInstrumentResolver, DhanMarketDataProvider

    snapshot, run = frozen_case()
    monkeypatch.setattr(
        DhanMarketDataProvider,
        "get_historical",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("provider used")),
    )
    monkeypatch.setattr(
        DhanInstrumentResolver,
        "search",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("resolver used")),
    )
    result = replay(
        ReplayRequest(
            snapshot=snapshot,
            policy=default_policy(TradeStyle.POSITIONAL),
            expected_assessment=run.assessment,
            replay_time=NOW,
        )
    )
    assert result.exact_match is True


def test_snapshot_rejects_wrong_policy_and_preserves_evidence_ids() -> None:
    snapshot, run = frozen_case()
    evidence_ids = tuple(
        item.source_evidence
        for component in run.assessment.market_state.components
        for item in component.contributions
    )
    replayed = replay(
        ReplayRequest(
            snapshot=snapshot,
            policy=default_policy(TradeStyle.POSITIONAL),
            replay_time=NOW,
        )
    )
    assert tuple(
        item.source_evidence
        for component in replayed.assessment.market_state.components
        for item in component.contributions
    ) == evidence_ids
    assert snapshot.policy_id == replayed.policy_id
    assert snapshot.policy_version == replayed.policy_version == "1.0"
