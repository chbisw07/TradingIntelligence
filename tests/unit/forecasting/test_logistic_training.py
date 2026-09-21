"""FF-1.2 engineering only: synthetic fits, no holdout outcomes or quality metrics."""

import math
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.identity import semantic_fingerprint
from tiaf.learning.forecast_artifacts import (
    FEATURE_ORDER,
    FoldManifest,
    LogisticArtifact,
    LogisticConfig,
    PopulationAudit,
    Reconstruction,
    ScalerArtifact,
    TrainingGrant,
    TrainingInput,
    TrainingRow,
    reconstruct,
)
from tiaf.learning.forecast_jobs import TrainingJob, TrainingRun, TrainingStore, run_fit
from tiaf.learning.forecast_training import read_bounded

AT = datetime(2026, 9, 21, tzinfo=TIAF_TIMEZONE)


def grant() -> TrainingGrant:
    return TrainingGrant(
        grant_id="synthetic-test",
        basis="SYNTHETIC_ENGINEERING",
        qualification_fingerprint="a" * 64,
        dataset_fingerprint="b" * 64,
        research_profile_fingerprint="c" * 64,
        feature_schema_fingerprint="d" * 64,
        protocol_fingerprint="e" * 64,
        dependency_lock_fingerprint="f" * 64,
        code_fingerprint="0" * 64,
        issued_at=AT,
    )


def training(n: int = 600) -> TrainingInput:
    rows = tuple(
        TrainingRow(
            observation_id=(
                f"ff1-adjusted:RELIANCE:{(date(2018, 1, 1) + timedelta(days=i)).isoformat()}"
            ),
            reference_date=date(2018, 1, 1) + timedelta(days=i),
            target_date=date(2018, 1, 2) + timedelta(days=i),
            label_available_at=datetime(2018, 1, 2, 16, tzinfo=TIAF_TIMEZONE) + timedelta(days=i),
            values=(math.sin(i), math.cos(i), float(i % 7), float(i % 11), 7.0),
            label=i % 2,
        )
        for i in range(n)
    )
    ids = tuple(r.observation_id for r in rows)
    return TrainingInput(
        manifest=FoldManifest(
            grant=grant(),
            fold_id=2021,
            fit_cutoff=datetime(2020, 12, 31, 9, 15, tzinfo=TIAF_TIMEZONE),
            embargo_date=date(2020, 12, 31),
            train_start=rows[0].reference_date,
            train_end=rows[-1].reference_date,
            observation_ids=ids,
            observation_order_fingerprint=semantic_fingerprint(ids),
            training_values_fingerprint=semantic_fingerprint(rows),
            audit=PopulationAudit(
                requested=n,
                train=n,
                positive=n // 2,
                zero=n - n // 2,
                ineligible=0,
                purge_only=0,
                embargo=0,
                sealed=0,
                later_unsealed=0,
            ),
        ),
        rows=rows,
    )


@pytest.fixture(scope="module")
def fitted() -> TrainingJob:
    pytest.importorskip("sklearn")
    result = run_fit(training())
    assert result.status == "TRAINED", result.reason
    return result


def test_fixed_config() -> None:
    assert LogisticConfig().model_dump(exclude={"fingerprint", "schema_version"}) == {
        "penalty": "l2",
        "C": 1.0,
        "solver": "lbfgs",
        "tol": 1e-8,
        "max_iter": 1000,
        "fit_intercept": True,
        "class_weight": None,
        "dual": False,
        "warm_start": False,
        "random_state": 1729,
        "n_jobs": 1,
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("C", 2.0),
        ("solver", "saga"),
        ("tol", 1e-4),
        ("max_iter", 2000),
        ("fit_intercept", False),
        ("class_weight", "balanced"),
        ("penalty", None),
        ("warm_start", True),
        ("random_state", 9),
        ("n_jobs", 2),
    ],
)
def test_no_tuning(field: str, value: Any) -> None:
    with pytest.raises(ValidationError):
        LogisticConfig.model_validate({field: value})


def test_immutable_tuple_json_round_trip() -> None:
    x = training()
    assert TrainingInput.model_validate_json(x.model_dump_json()) == x
    assert isinstance(x.model_dump(mode="json")["rows"], list)
    with pytest.raises(ValidationError):
        x.rows = ()
    assert not hasattr(x.rows, "append")
    assert x.manifest.feature_order == FEATURE_ORDER


@pytest.mark.parametrize(
    "updates",
    [
        {"reference_date": "2025-01-01", "target_date": "2025-01-02"},
        {"reference_date": "2024-12-31", "target_date": "2025-01-01"},
        {"values": [0.0, 0.0, 0.0, float("nan"), 0.0]},
        {"label": None},
        {"label": True},
    ],
)
def test_unusable_rows_rejected(updates: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        TrainingRow.model_validate({**training().rows[0].model_dump(), **updates})


def test_mutated_order_and_fingerprint_refused() -> None:
    x = training()
    with pytest.raises(ValidationError):
        TrainingInput.model_validate({**x.model_dump(), "rows": tuple(reversed(x.rows))})
    with pytest.raises(ValidationError):
        FoldManifest.model_validate({**x.manifest.model_dump(), "train_end": "2025-01-01"})


def test_train_scaler_constant_and_reconstruction(fitted: TrainingJob) -> None:
    a = fitted.artifact
    assert a is not None
    s = a.reconstruction.scaler
    rows = training().rows
    assert s.n == len(rows) == 600
    assert s.means == pytest.approx(tuple(sum(r.values[i] for r in rows) / 600 for i in range(5)))
    assert s.variances == pytest.approx(
        tuple(sum((r.values[i] - s.means[i]) ** 2 for r in rows) / 600 for i in range(5))
    )
    assert s.constant_columns == (4,) and s.scales[4] == 1.0
    assert a.reconstruction_max_error <= 1e-12
    assert a.role == "CHALLENGER" and a.lifecycle == "EXPERIMENTAL"
    assert a.versions.sklearn == "1.7.2" and a.versions.python
    assert all("threads=1" in b for b in a.versions.numeric_backends)
    assert 0.0 <= reconstruct(a.reconstruction, (0.0, 0.0, 0.0, 0.0, 7.0)) <= 1.0
    assert LogisticArtifact.model_validate_json(a.model_dump_json()) == a
    assert fitted.peak_rss_kib is not None and fitted.peak_rss_kib > 0
    assert fitted.address_space_limit_bytes == 512 * 1024 * 1024
    assert fitted.cpu_limit_seconds == 60


def test_repeat_fit_scientific_identity(fitted: TrainingJob) -> None:
    second = run_fit(training())
    assert second.artifact is not None and fitted.artifact is not None
    assert second.artifact.scientific_fingerprint == fitted.artifact.scientific_fingerprint
    assert second.artifact.fingerprint != fitted.artifact.fingerprint  # real job clocks differ


@pytest.mark.parametrize(
    "field,value",
    [
        ("n_iter", 1000),
        ("converged", False),
        ("role", "PRIMARY"),
        ("lifecycle", "APPROVED"),
        ("reconstruction_max_error", 1e-8),
    ],
)
def test_malformed_model_rejected(fitted: TrainingJob, field: str, value: Any) -> None:
    assert fitted.artifact is not None
    body = fitted.artifact.model_dump(exclude={"fingerprint"})
    with pytest.raises(ValidationError):
        LogisticArtifact.model_validate({**body, field: value})


def test_scaler_and_coefficient_tamper(fitted: TrainingJob) -> None:
    assert fitted.artifact is not None
    r = fitted.artifact.reconstruction
    with pytest.raises(ValidationError):
        Reconstruction.model_validate({**r.model_dump(), "intercept": r.intercept + 0.1})
    body = r.scaler.model_dump(exclude={"fingerprint"})
    with pytest.raises(ValidationError):
        ScalerArtifact.model_validate({**body, "scales": [0.0] * 5})


def test_reconstruction_extremes(fitted: TrainingJob) -> None:
    assert fitted.artifact is not None
    r = fitted.artifact.reconstruction
    for x in (-1e200, 1e200):
        assert 0 <= reconstruct(r, (x, x, x, x, x)) <= 1
    with pytest.raises(ValueError):
        reconstruct(r, (float("inf"), 0.0, 0.0, 0.0, 0.0))


def test_insufficient_support_unavailable() -> None:
    job = run_fit(training(300))
    assert job.status == "UNAVAILABLE" and job.reason == "INSUFFICIENT_TRAINING_DATA"
    assert job.artifact is None


def test_actual_convergence_warning_is_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    sklearn = pytest.importorskip("sklearn.linear_model")
    exceptions = pytest.importorskip("sklearn.exceptions")
    pools = pytest.importorskip("threadpoolctl")
    import warnings

    from tiaf.learning.forecast_worker import fit

    calls = []

    class Nonconverging:
        def __init__(self, **kwargs: Any) -> None:
            assert kwargs["solver"] == "lbfgs" and kwargs["max_iter"] == 1000

        def fit(self, x: Any, y: Any) -> None:
            calls.append(1)
            warnings.warn("synthetic nonconvergence", exceptions.ConvergenceWarning)

    monkeypatch.setattr(sklearn, "LogisticRegression", Nonconverging)
    monkeypatch.setattr(pools, "threadpool_info", lambda: [{"num_threads": 1}])
    with pytest.raises(exceptions.ConvergenceWarning):
        fit(training())
    assert len(calls) == 1


def test_incompatible_dependency_refuses_fit(monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib.metadata

    from tiaf.learning.forecast_worker import fit

    monkeypatch.setattr(importlib.metadata, "version", lambda _: "wrong-version")
    with pytest.raises(ModuleNotFoundError, match="ML_DEPENDENCY_VERSION_MISMATCH"):
        fit(training())


def test_timeout_no_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def timeout(*args: Any, **kwargs: Any) -> Any:
        calls.append(args)
        assert kwargs["timeout"] == 60
        assert "DHAN_ACCESS_TOKEN" not in kwargs["env"]
        raise subprocess.TimeoutExpired(args[0], 60)

    monkeypatch.setattr(subprocess, "run", timeout)
    job = run_fit(training())
    assert job.status == "FAILED" and job.reason == "RESOURCE_LIMIT_EXCEEDED"
    assert len(calls) == 1


@pytest.mark.parametrize(
    "stdout,code",
    [
        ('{"status":"FAILED","reason":"MODEL_FIT_FAILED:ConvergenceWarning"}', 0),
        ('{"status":"UNAVAILABLE","reason":"ML_DEPENDENCY_UNAVAILABLE"}', 0),
        ('{"status":"TRAINED","artifact":{}}', 0),
        ("[]", 0),
        ("", -9),
    ],
)
def test_failed_worker_never_fabricates_model(
    monkeypatch: pytest.MonkeyPatch, stdout: str, code: int
) -> None:
    def result(*args: Any, **kwargs: Any) -> Any:
        return subprocess.CompletedProcess(args[0], code, stdout=stdout)

    monkeypatch.setattr(subprocess, "run", result)
    job = run_fit(training())
    assert job.status in {"FAILED", "UNAVAILABLE"} and job.artifact is None


def test_storage_immutable_and_recorded_read(tmp_path: Path, fitted: TrainingJob) -> None:
    store = TrainingStore(tmp_path / "attempt", grant())
    path = store.put("job", fitted)
    assert TrainingJob.model_validate_json(read_bounded(path)) == fitted
    with pytest.raises(FileExistsError):
        store.put("job", fitted)
    with pytest.raises(FileExistsError):
        TrainingStore(tmp_path / "attempt", grant())
    with pytest.raises(ValidationError):
        TrainingRun(grant=grant(), jobs=(fitted,), created_at=AT, status="COMPLETE")


def test_optional_dependency_isolation(fitted: TrainingJob, tmp_path: Path) -> None:
    assert fitted.artifact is not None
    path = tmp_path / "model.json"
    path.write_text(fitted.artifact.model_dump_json())
    code = """
import sys
class Block:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'sklearn', 'numpy', 'scipy', 'joblib', 'threadpoolctl'}:
            raise ImportError('optional dependency blocked')
sys.meta_path.insert(0, Block())
from pathlib import Path
from tiaf.learning.forecast_artifacts import LogisticArtifact, reconstruct
from tiaf.learning.forecast_jobs import TrainingRun
from tiaf.forecasting.runtime import ColdForecastRuntime
a = LogisticArtifact.model_validate_json(Path(sys.argv[1]).read_text())
p = reconstruct(a.reconstruction, (0., 0., 0., 0., 7.))
assert 0 <= p <= 1
"""
    # Use only existing runtime module import; don't assume a runtime class export.
    code = code.replace(
        "from tiaf.forecasting.runtime import ColdForecastRuntime",
        "import tiaf.forecasting.runtime",
    )
    result = subprocess.run([sys.executable, "-c", code, str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_worker_has_no_quality_metrics_or_provider_imports() -> None:
    import ast

    root = Path(__file__).resolve().parents[3]
    for path in (root / "src/tiaf/learning").glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                assert not module.startswith(
                    ("tiaf.providers", "tiaf.data.providers", "sklearn.metrics")
                )
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"score", "predict", "partial_fit"}


def test_cli_help_and_dependency_approval_guard(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[3]
    script = root / "scripts/train_ff1_logistic_candidate.py"
    result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
    assert result.returncode == 0 and "approve-dependency-lock" in result.stdout
    result = subprocess.run(
        [sys.executable, str(script), "--output", str(tmp_path / "no")],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0 and not (tmp_path / "no").exists()
