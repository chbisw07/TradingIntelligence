"""Synthetic pre-holdout preparation; never consume private empirical source data."""

import json
import subprocess
import sys
from datetime import timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import ValidationError

from tiaf.evaluation.forecast_retrospective_contracts import RetrospectiveQualification
from tiaf.forecasting.identity import semantic_fingerprint
from tiaf.learning.forecast_artifacts import (
    FEATURE_ORDER,
    FIFTH_CUTOFF,
    FifthFoldGrant,
    TrainingGrant,
    TrainingInput,
)
from tiaf.learning.forecast_fifth_preparation import (
    FifthPreparation,
    prepare_fifth,
)
from tiaf.learning.forecast_fifth_store import (
    FifthHandoff,
    FifthStore,
    execute_once,
    verify_fifth,
)
from tiaf.learning.forecast_jobs import run_fit

from .test_logistic_training_admission import qualification as qualification


def update(value: Any, **fields: Any) -> Any:
    return type(value).model_validate({**value.model_dump(exclude={"fingerprint"}), **fields})


def authority(q: RetrospectiveQualification, raw: bytes) -> FifthFoldGrant:
    return FifthFoldGrant(
        basis="SYNTHETIC_ENGINEERING",
        qualification_fingerprint=cast(str, q.fingerprint),
        qualification_blob=sha256(raw).hexdigest(),
        dataset_fingerprint=q.dataset_fingerprint,
        research_profile_fingerprint=q.profile.fingerprint,
        feature_schema_fingerprint=q.feature_schema.fingerprint,
        protocol_fingerprint="a" * 64,
        authority_document_fingerprint="b" * 64,
        dependency_lock_fingerprint="c" * 64,
        code_fingerprint="d" * 64,
        issued_at=q.assessed_at + timedelta(seconds=1),
    )


@pytest.fixture(scope="module")
def prepared(
    qualification: RetrospectiveQualification, tmp_path_factory: pytest.TempPathFactory
) -> FifthPreparation:
    raw = qualification.model_dump_json().encode()
    path = tmp_path_factory.mktemp("fifth-source") / "q.json"
    path.write_bytes(raw)
    return prepare_fifth(path, authority(qualification, raw))


@pytest.mark.parametrize(
    "field,value",
    [
        ("cutoff", FIFTH_CUTOFF + timedelta(minutes=1)),
        ("holdout_status", "OPEN"),
        ("protected_outcome_access", "OBSERVED"),
        ("post_holdout_refit", "AUTHORIZED"),
        ("allowed_folds", (2024,)),
        ("max_fits", 2),
        ("max_scaler_fits", 2),
        ("max_attempts_per_fold", 2),
        ("final_evaluation_authorized", True),
    ],
)
def test_narrow_authority(prepared: FifthPreparation, field: str, value: Any) -> None:
    with pytest.raises(ValidationError):
        update(prepared.training.manifest.grant, **{field: value})


def test_old_grant_not_widened(prepared: FifthPreparation) -> None:
    with pytest.raises(ValidationError):
        TrainingGrant.model_validate(prepared.training.manifest.grant.model_dump())
    with pytest.raises(ValueError, match="DEVELOPMENT_GRANT_REQUIRED"):
        run_fit(prepared.training)
    with pytest.raises(ValidationError):
        update(prepared.training.manifest, fold_id=2024)


def test_exact_cutoff_train_membership(
    prepared: FifthPreparation, qualification: RetrospectiveQualification
) -> None:
    m = prepared.training.manifest
    f = next(f for f in qualification.folds if f.test_year == 2025)
    assert m.fit_cutoff == FIFTH_CUTOFF
    assert m.observation_ids == f.train_ids
    assert m.audit.positive == f.train_positive and m.audit.zero == f.train_zero
    assert prepared.purged_ids == f.purged_ids
    assert m.audit.sealed == 250 and m.audit.embargo == 0 and m.audit.purge_only == 1
    # Protected embargo origin is counted once in sealed, as in existing prepare_training.
    assert all(
        r.reference_date.year < 2025
        and r.target_date < FIFTH_CUTOFF.date()
        and r.label_available_at < FIFTH_CUTOFF
        for r in prepared.training.rows
    )
    assert m.observation_order_fingerprint == semantic_fingerprint(m.observation_ids)
    assert m.feature_order == FEATURE_ORDER


@pytest.mark.parametrize("field,value", [("C", 2.0), ("solver", "saga"), ("max_iter", 2000)])
def test_config_immutable(prepared: FifthPreparation, field: str, value: Any) -> None:
    config = prepared.training.manifest.model_config_value
    with pytest.raises(ValidationError):
        update(config, **{field: value})


def test_late_training_value_rejected(prepared: FifthPreparation) -> None:
    row = update(prepared.training.rows[-1], label_available_at=FIFTH_CUTOFF)
    rows = (*prepared.training.rows[:-1], row)
    m = update(prepared.training.manifest, training_values_fingerprint=semantic_fingerprint(rows))
    with pytest.raises(ValidationError):
        TrainingInput(manifest=m, rows=rows)
    with pytest.raises(ValidationError):
        update(prepared.training.manifest, fit_cutoff=FIFTH_CUTOFF - timedelta(days=1))


def test_protected_fields_never_decoded(
    qualification: RetrospectiveQualification, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dump = qualification.model_dump(mode="json")
    for row in dump["observations"]:
        if row["reference_date"] >= "2025" or (row["target_date"] and row["target_date"] >= "2025"):
            for key in ("features", "label", "label_state", "assumed_label_available_at"):
                row[key] = "PROTECTED_SENTINEL"
    # Entire test summaries must stay opaque, even in fifth-fold metadata.
    for f in dump["folds"]:
        for key in tuple(f):
            if key.startswith("test_") and key != "test_year":
                f[key] = "PROTECTED_SENTINEL"
    raw = json.dumps(dump).encode()
    path = tmp_path / "q.json"
    path.write_bytes(raw)
    a = authority(qualification, raw)
    original = json.loads

    def loads(value: Any, *args: Any, **kwargs: Any) -> Any:
        assert "PROTECTED_SENTINEL" not in str(value)
        return original(value, *args, **kwargs)

    monkeypatch.setattr(json, "loads", loads)
    p = prepare_fifth(path, a)
    assert (
        p.training.manifest.audit.train
        == next(f for f in qualification.folds if f.test_year == 2025).train_positive
        + next(f for f in qualification.folds if f.test_year == 2025).train_zero
    )


def test_wrong_bytes_fail_before_decode(prepared: FifthPreparation, tmp_path: Path) -> None:
    p = tmp_path / "bad"
    p.write_bytes(b"not-json")
    with pytest.raises(ValueError, match="BYTE_PIN"):
        prepare_fifth(p, cast(FifthFoldGrant, prepared.training.manifest.grant))


def test_baseline_last20_no_backfill(prepared: FifthPreparation) -> None:
    b = prepared.baseline
    assert b.scheduled_ids == prepared.scheduled_pre_cutoff_ids[-20:]
    assert b.output is not None
    assert b.output.probability == sum(cast(int, e.label) for e in b.support) / 20
    absent = update(
        b.support[-1],
        label=None,
        label_state="UNAVAILABLE",
        assumed_label_available_at=None,
        reasons=("SYNTHETIC_MISSING",),
    )
    bad = update(b, support=(*b.support[:-1], absent), output=None)
    assert bad.output is None and len(bad.support) == 20
    with pytest.raises(ValidationError):
        update(bad, output=b.output)
    with pytest.raises(ValidationError):
        update(b, cutoff=FIFTH_CUTOFF + timedelta(days=1))


@pytest.fixture(scope="module")
def fitted(
    prepared: FifthPreparation, tmp_path_factory: pytest.TempPathFactory
) -> tuple[Path, str]:
    store = FifthStore(tmp_path_factory.mktemp("fifth-fit") / "corpus", create=True)
    return store.root, execute_once(store, prepared)


def test_handoff_fit_replay_once(
    fitted: tuple[Path, str], prepared: FifthPreparation, monkeypatch: pytest.MonkeyPatch
) -> None:
    import socket

    import tiaf.learning.forecast_fifth_store as fs

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("FORBIDDEN_FIT_OR_NETWORK")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(fs, "_run_fit", forbidden)
    store = FifthStore(fitted[0])
    h = cast(FifthHandoff, store.get("handoff", fitted[1]))
    assert verify_fifth(store, fitted[1]) == "MATCH"
    assert h.holdout_status == "SEALED" and h.protected_outcome_access == "NONE"
    assert h.evaluation_metrics == 0 and h.forecast_records == 0 and not h.final_protocol_frozen
    with pytest.raises(ValueError, match="CONSUMED_OR_READ_ONLY"):
        execute_once(store, prepared)
    store.writable = True
    with pytest.raises(ValueError, match="CONSUMED_OR_READ_ONLY"):
        execute_once(store, prepared)
    assert FifthHandoff.model_validate_json(h.model_dump_json()) == h
    with pytest.raises(ValidationError):
        h.holdout_status = "OPEN"  # type: ignore[assignment]
    with pytest.raises(ValidationError):
        update(h, post_holdout_refit_allowed=True)


def test_failed_worker_consumes_attempt(
    prepared: FifthPreparation, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def timeout(*args: Any, **kwargs: Any) -> Any:
        raise subprocess.TimeoutExpired(args[0], 60)

    monkeypatch.setattr(subprocess, "run", timeout)
    s = FifthStore(tmp_path / "corpus", create=True)
    with pytest.raises(ValueError, match="NO_RETRY"):
        execute_once(s, prepared)
    assert len(tuple(s.root.glob("attempt-*.json"))) == 1
    with pytest.raises(ValueError, match="CONSUMED_OR_READ_ONLY"):
        execute_once(s, prepared)


def test_handoff_tamper(fitted: tuple[Path, str]) -> None:
    s = FifthStore(fitted[0])
    h = cast(FifthHandoff, s.get("handoff", fitted[1]))
    with pytest.raises(ValidationError):
        FifthHandoff.model_validate({**h.model_dump(), "model_artifact_fingerprint": "a" * 64})
    assert verify_fifth(s, "0" * 64) == "MISMATCH"


def test_replay_no_ml_or_source(fitted: tuple[Path, str]) -> None:
    code = """
import sys,socket
from pathlib import Path
class Block:
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split('.')[0] in {'numpy','sklearn','scipy','joblib','threadpoolctl'}:
            raise AssertionError('ML_FORBIDDEN')
sys.meta_path.insert(0,Block())
def forbidden(*a,**kw):raise AssertionError('NETWORK_FORBIDDEN')
socket.socket=forbidden
from tiaf.learning.forecast_fifth_store import FifthStore,verify_fifth
assert verify_fifth(FifthStore(Path(sys.argv[1])),sys.argv[2])=='MATCH'
"""
    r = subprocess.run(
        [sys.executable, "-c", code, str(fitted[0]), fitted[1]], capture_output=True, text=True
    )
    assert r.returncode == 0, r.stderr


def test_cli_safe_default() -> None:
    script = Path(__file__).resolve().parents[3] / "scripts/prepare_ff1_fifth_fold_artifacts.py"
    for args in ([], ["--help"]):
        result = subprocess.run(
            [sys.executable, str(script), *args], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "Safe:" in result.stdout or "--preflight" in result.stdout


def test_cli_preflight_serializes_without_fit(
    prepared: FifthPreparation,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from scripts import prepare_ff1_fifth_fold_artifacts as cli

    brief = tmp_path / "brief.md"
    brief.write_text("SYNTHETIC ENGINEERING AUTHORITY")
    monkeypatch.setattr(cli, "BRIEF", brief)
    monkeypatch.setattr(cli, "prepare_fifth", lambda *_: prepared)

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("preflight must not fit or write corpus")

    monkeypatch.setattr(cli, "execute_once", forbidden)
    monkeypatch.setattr(
        sys, "argv", ["prepare", "--preflight", "--approve-dependency-lock", cli.LOCK_FP]
    )
    assert cli.main() == 0
    assert "TRAIN_ONLY_PREFLIGHT" in capsys.readouterr().out
