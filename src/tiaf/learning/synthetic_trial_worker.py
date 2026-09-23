"""Private versioned worker of the existing FLC-2 service; authored data only."""

import importlib.metadata
import platform
import resource
import sys
import warnings
from datetime import datetime
from typing import Any, cast

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.identity import ArtifactReference, ForecastContract, canonical_json

from .forecast_artifacts import LibraryVersions, Reconstruction, ScalerArtifact, reconstruct
from .forecast_worker import VERSIONS
from .synthetic_trials import SyntheticModel, SyntheticSpec, code_pin, dependency_pin, training_rows


class WorkerInput(ForecastContract):
    spec: SyntheticSpec
    request_reference: ArtifactReference


def fit(value: WorkerInput) -> SyntheticModel:
    spec = value.spec
    if (
        spec.implementation_fingerprint != code_pin()
        or spec.dependency_lock_fingerprint != dependency_pin()
    ):
        raise ValueError("SYNTHETIC_WORKER_PIN_MISMATCH")
    for name, version in VERSIONS.items():
        if importlib.metadata.version(name) != version:
            raise ModuleNotFoundError("SYNTHETIC_DEPENDENCY_VERSION")
    import numpy as np
    from sklearn.exceptions import ConvergenceWarning  # type: ignore[import-untyped]
    from sklearn.linear_model import LogisticRegression  # type: ignore[import-untyped]
    from sklearn.preprocessing import StandardScaler  # type: ignore[import-untyped]
    from threadpoolctl import threadpool_info  # type: ignore[import-untyped]

    backends = threadpool_info()
    if not backends or any(b["num_threads"] != 1 for b in backends):
        raise ValueError("SYNTHETIC_THREAD_LIMIT")
    rows = training_rows(spec)  # No development positions are materialized here.
    x = np.asarray([x for x, _ in rows])
    y = np.asarray([y for _, y in rows])
    scaler = StandardScaler()
    transformed = scaler.fit_transform(x)
    model = LogisticRegression(
        C=spec.config.C,
        fit_intercept=spec.config.fit_intercept,
        solver="lbfgs",
        penalty="l2",
        tol=1e-8,
        max_iter=1000,
        random_state=1729,
        n_jobs=1,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(transformed, y)
    if model.n_iter_[0] >= 1000 or list(model.classes_) != [0, 1]:
        raise ValueError("SYNTHETIC_NONCONVERGENCE")
    s = ScalerArtifact(
        n=len(rows),
        means=tuple(scaler.mean_),
        variances=tuple(scaler.var_),
        scales=tuple(scaler.scale_),
        constant_columns=(4,),
        training_fingerprint=cast(str, spec.fingerprint),
    )
    reconstruction = Reconstruction(
        scaler=s, coefficients=tuple(model.coef_[0]), intercept=float(model.intercept_[0])
    )
    # Numeric codec fidelity, not objective scoring or candidate selection.
    native = model.predict_proba(transformed[:3])[:, 1]
    if any(
        abs(reconstruct(reconstruction, rows[i][0]) - float(native[i])) > 1e-12 for i in range(3)
    ):
        raise ValueError("SYNTHETIC_RECONSTRUCTION_MISMATCH")
    return SyntheticModel(
        spec=spec,
        request_reference=value.request_reference,
        reconstruction=reconstruction,
        versions=LibraryVersions(
            python=platform.python_version(),
            numeric_backends=tuple(
                sorted(f"{b['internal_api']}:{b['version']}:threads=1" for b in backends)
            ),
        ),
        n_iter=int(model.n_iter_[0]),
        created_at=datetime.now(TIAF_TIMEZONE),
    )


def main() -> int:
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2, 512 * 1024**2))
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    result: dict[str, Any]
    try:
        raw = sys.stdin.buffer.read(1024**2 + 1)
        if len(raw) > 1024**2:
            raise ValueError("WORKER_INPUT_LIMIT")
        artifact = fit(WorkerInput.model_validate_json(raw))
        result = {"status": "TRAINED", "artifact": artifact.model_dump(mode="json")}
    except (ImportError, importlib.metadata.PackageNotFoundError):
        result = {"status": "UNAVAILABLE", "reason": "SYNTHETIC_DEPENDENCY_UNAVAILABLE"}
    except Exception as exc:
        result = {"status": "FAILED", "reason": f"SYNTHETIC_FIT_FAILED:{type(exc).__name__}"}
    print(canonical_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
