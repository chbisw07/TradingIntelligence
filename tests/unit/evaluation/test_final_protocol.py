"""Synthetic pre-open protocol proofs; never open a private empirical corpus."""

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime, timedelta
from hashlib import sha256
from itertools import product
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.evaluation.forecast_final_custody import FinalProtocolStore, final_grid
from tiaf.evaluation.forecast_final_protocol import (
    FinalEvidence,
    FinalPolicy,
    FinalPopulation,
    FinalProtocol,
    FinalSlot,
    final_decision,
)
from tiaf.learning.forecast_artifacts import FIFTH_CUTOFF, TrainingRow


@pytest.fixture
def protocol() -> FinalProtocol:
    fp = "a" * 64
    pins: dict[str, Any] = {
        field: fp for field in FinalProtocol.model_fields if field.endswith("_fingerprint")
    }
    return FinalProtocol(
        **pins,
        qualification_blob=fp,
        source_pins=(("src/synthetic.py", fp),),
        population=FinalPopulation(
            qualification_blob=fp,
            qualification_fingerprint=fp,
            context_fingerprint=fp,
            slots=(
                FinalSlot(
                    observation_id="ff1-adjusted:RELIANCE:2025-12-31",
                    reference_date=date(2025, 12, 31),
                    target_date=date(2026, 1, 1),
                ),
            ),
        ),
        authorized=True,
        created_at=datetime(2026, 9, 22, tzinfo=TIAF_TIMEZONE),
    )


def update(value: Any, **fields: Any) -> Any:
    return type(value).model_validate({**value.model_dump(exclude={"fingerprint"}), **fields})


def evidence(**fields: Any) -> FinalEvidence:
    return FinalEvidence.model_validate(
        {
            "intended": 250,
            "paired": 200,
            "positive": 100,
            "zero": 100,
            "complete_blocks": 20,
            "integrity_passed": True,
            "replay_passed": True,
            "methodology_valid": True,
            "metrics_evaluable": True,
            "intervals_estimable": True,
            "brier_interval": (-0.05, -0.001),
            "logloss_interval": (-0.03, 0.01),
            **fields,
        }
    )


@pytest.mark.parametrize(
    "field", [name for name in FinalProtocol.model_fields if name.endswith("_fingerprint")]
)
def test_required_pins(protocol: FinalProtocol, field: str) -> None:
    values = protocol.model_dump(exclude={"fingerprint", field})
    with pytest.raises(ValidationError):
        FinalProtocol.model_validate(values)


def test_cutoff_timezone_and_immutable_json_roundtrip(protocol: FinalProtocol) -> None:
    assert protocol.fifth_cutoff == FIFTH_CUTOFF
    assert update(protocol, fifth_cutoff=FIFTH_CUTOFF.astimezone(UTC)) == protocol
    for bad in (FIFTH_CUTOFF + timedelta(seconds=1), FIFTH_CUTOFF.replace(tzinfo=None)):
        with pytest.raises(ValidationError):
            update(protocol, fifth_cutoff=bad)
    assert FinalProtocol.model_validate_json(protocol.model_dump_json()) == protocol
    assert isinstance(protocol.model_dump(mode="json")["population"]["slots"], list)
    assert protocol.model_dump(mode="json")["fifth_cutoff"].endswith("+05:30")
    with pytest.raises(ValidationError):
        protocol.authorized = False
    with pytest.raises(AttributeError):
        protocol.population.slots.append(protocol.population.slots[0])  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "fields",
    [
        {"baserate_positive": 9},
        {"baserate_support": 19},
        {"baserate_rule": "BACKFILL"},
        {"holdout_status_at_freeze": "OPEN"},
    ],
)
def test_baseline_exact_identity(protocol: FinalProtocol, fields: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        update(protocol, **fields)


@pytest.mark.parametrize(
    "fields",
    [
        {"seed": 1},
        {"block_length": 10},
        {"replicates": 100},
        {"minimum_pairs": 150},
        {"minimum_class": 30},
        {"minimum_coverage": "0.7"},
        {"confidence": "0.95"},
        {"executions_allowed": 2},
        {"post_holdout_refit_allowed": True},
        {"secondary_diagnostics": ("OPTIMIZED_THRESHOLD",)},
    ],
)
def test_fixed_policy_and_no_refit(fields: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        FinalPolicy.model_validate(fields)


@pytest.mark.parametrize(
    "brier,logloss,expected",
    [
        ((-0.04, -0.001), (-0.02, 0.01), "LOGISTIC_SUPPORTED"),
        ((-0.04, 0.0), (-0.02, 0.01), "INSUFFICIENT_EVIDENCE"),
        ((0.0, 0.02), (-0.02, 0.01), "LOGISTIC_NOT_SUPPORTED"),
        ((-0.04, -0.001), (0.01, 0.02), "INSUFFICIENT_EVIDENCE"),
        ((-0.04, -0.001), (0.010001, 0.02), "LOGISTIC_NOT_SUPPORTED"),
        ((-0.04, 0.02), (-0.03, 0.04), "INSUFFICIENT_EVIDENCE"),
        ((0.0, 0.0), (0.01, 0.01), "LOGISTIC_NOT_SUPPORTED"),
        ((-0.01, -0.01), (0.01, 0.01), "LOGISTIC_SUPPORTED"),
    ],
)
def test_exact_interval_boundaries(
    brier: tuple[float, float],
    logloss: tuple[float, float],
    expected: str,
) -> None:
    decision = final_decision(evidence(brier_interval=brier, logloss_interval=logloss))
    assert decision.classification == expected
    assert not decision.automatic_promotion
    assert decision.logistic_role == "CHALLENGER_EXPERIMENTAL"
    assert decision.baserate_role == "BENCHMARK"


@pytest.mark.parametrize(
    "fields",
    [
        {"paired": 199, "positive": 99},
        {"positive": 39, "zero": 161},
        {"intended": 251},
        {"complete_blocks": 19},
        {"integrity_passed": False},
        {"replay_passed": False},
        {"methodology_valid": False},
        {"metrics_evaluable": False},
        {"intervals_estimable": False, "brier_interval": None, "logloss_interval": None},
    ],
)
def test_inadequacy_precedes_rejection_or_support(fields: dict[str, Any]) -> None:
    for b in ((-0.03, -0.01), (0.01, 0.03)):
        assert (
            final_decision(evidence(**{"brier_interval": b, **fields})).classification
            == "INSUFFICIENT_EVIDENCE"
        )


def test_all_valid_state_partitions_are_exclusive_and_total() -> None:
    # Exhaust all six validity/support states and all relevant interval regions.
    for flags in product((False, True), repeat=6):
        for b, ll in product(
            ((-0.03, -0.01), (-0.01, 0.01), (0.0, 0.02)),
            ((-0.01, 0.01), (0.01, 0.02), (0.02, 0.03)),
        ):
            integrity, replay, methodology, metrics, intervals, support = flags
            e = evidence(
                integrity_passed=integrity,
                replay_passed=replay,
                methodology_valid=methodology,
                metrics_evaluable=metrics,
                intervals_estimable=intervals,
                complete_blocks=20 if support else 19,
                brier_interval=b if intervals else None,
                logloss_interval=ll if intervals else None,
            )
            adequate = all(flags)
            supported = adequate and b[1] < 0 and ll[1] <= 0.01
            rejected = adequate and (b[0] >= 0 or ll[0] > 0.01)
            insufficient = not adequate or not (supported or rejected)
            assert sum((supported, rejected, insufficient)) == 1
            expected = (
                "LOGISTIC_SUPPORTED"
                if supported
                else "LOGISTIC_NOT_SUPPORTED"
                if rejected
                else "INSUFFICIENT_EVIDENCE"
            )
            assert final_decision(e).classification == expected


@pytest.mark.parametrize(
    "fields",
    [
        {"positive": 101},
        {"paired": True},
        {"brier_interval": (0.1, -0.1)},
        {"brier_interval": (float("nan"), 0.0)},
        {"intended": 100},
        {"complete_blocks": 41},
        {"intervals_estimable": True, "brier_interval": None},
    ],
)
def test_invalid_computation_not_scientific_rejection(fields: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        evidence(**fields)


def test_no_protected_training_outcome() -> None:
    with pytest.raises(ValidationError, match="HOLDOUT_NOT_AUTHORIZED"):
        TrainingRow(
            observation_id="ff1-adjusted:RELIANCE:2024-12-31",
            reference_date=date(2024, 12, 31),
            target_date=date(2025, 1, 1),
            label_available_at=FIFTH_CUTOFF,
            values=(0.0, 0.0, 0.0, 0.0, 0.0),
            label=0,
        )


def test_freeze_metadata_does_not_decode_protected_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fp = "a" * 64
    oid = "ff1-adjusted:RELIANCE:2025-12-31"
    sentinel = "DO_NOT_DECODE_PROTECTED"
    payload = {
        "fingerprint": fp,
        "context_fingerprint": fp,
        "observations": [
            {
                "reference_date": "2025-12-31",
                "target_date": "2026-01-01",
                "observation_id": oid,
                "features": sentinel,
                "label": sentinel,
                "label_state": sentinel,
                "assumed_label_available_at": sentinel,
            }
        ],
        "folds": [
            {
                "test_year": 2025,
                "test_ids": [oid],
                "test_positive": sentinel,
                "test_zero": sentinel,
                "test_feature_complete": sentinel,
            }
        ],
        "audit": sentinel,
    }
    raw = json.dumps(payload).encode()
    path = tmp_path / "qualification.json"
    path.write_bytes(raw)
    original = json.loads

    def guarded(value: Any, *args: Any, **kwargs: Any) -> Any:
        assert sentinel not in str(value)
        return original(value, *args, **kwargs)

    monkeypatch.setattr(json, "loads", guarded)
    p = final_grid(path, sha256(raw).hexdigest(), fp)
    assert len(p.slots) == 1 and p.slots[0].target_date == date(2026, 1, 1)
    with pytest.raises(ValueError, match="BYTE_PIN"):
        final_grid(path, "b" * 64, fp)


def test_first_authorized_execution_once_and_no_mutation(
    protocol: FinalProtocol,
    tmp_path: Path,
) -> None:
    root = tmp_path / "custody"
    store = FinalProtocolStore(root, create=True)
    fp = store.put("protocol", protocol)
    with pytest.raises(ValueError, match="NOT_AUTHORIZED"):
        store.consume_once(fp, approved_protocol="b" * 64)
    reopened = FinalProtocolStore(root)
    claim = reopened.consume_once(fp, approved_protocol=fp)
    assert claim.consumed_before_outcome_access and not claim.post_holdout_refit_allowed
    for caller in (store, reopened, FinalProtocolStore(root)):
        with pytest.raises(ValueError, match="ALREADY_CONSUMED"):
            caller.consume_once(fp, approved_protocol=fp)
    with pytest.raises(ValueError, match="ALREADY_FROZEN"):
        store.put(
            "protocol", update(protocol, created_at=protocol.created_at + timedelta(seconds=1))
        )
    with pytest.raises(ValidationError):
        FinalProtocol.model_validate({**protocol.model_dump(), "authorized": False})
    assert reopened.protocol(fp) == protocol  # replay consumes no second claim


def test_denied_protocol_cannot_consume(protocol: FinalProtocol, tmp_path: Path) -> None:
    store = FinalProtocolStore(tmp_path / "denied", create=True)
    fp = store.put("protocol", update(protocol, authorized=False))
    with pytest.raises(ValueError, match="NOT_AUTHORIZED"):
        store.consume_once(fp, approved_protocol=fp)
    assert not tuple(store.root.glob("attempt-*.json"))


def test_failed_claim_stays_consumed(
    protocol: FinalProtocol,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = FinalProtocolStore(tmp_path / "failed", create=True)
    fp = store.put("protocol", protocol)
    original = store.get

    def fail(kind: str, fingerprint: str) -> Any:
        if kind == "attempt":
            raise OSError("synthetic interruption after durable claim")
        return original(kind, fingerprint)

    monkeypatch.setattr(store, "get", fail)
    with pytest.raises(OSError):
        store.consume_once(fp, approved_protocol=fp)
    with pytest.raises(ValueError, match="ALREADY_CONSUMED"):
        FinalProtocolStore(store.root).consume_once(fp, approved_protocol=fp)


def test_concurrent_consumers_only_one_succeeds(protocol: FinalProtocol, tmp_path: Path) -> None:
    store = FinalProtocolStore(tmp_path / "concurrent", create=True)
    fp = store.put("protocol", protocol)

    def attempt(_: int) -> bool:
        try:
            FinalProtocolStore(store.root).consume_once(fp, approved_protocol=fp)
            return True
        except (ValueError, OSError):
            return False

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sum(pool.map(attempt, range(4))) == 1


def test_cli_safe_default_and_no_execution_option() -> None:
    script = Path(__file__).resolve().parents[3] / "scripts/freeze_ff1_final_protocol.py"
    result = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True, check=True
    )
    assert "Safe: no operation" in result.stdout
    help_text = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "--freeze" in help_text and "--verify-protocol" in help_text
    assert "--execute" not in help_text and "--open" not in help_text
