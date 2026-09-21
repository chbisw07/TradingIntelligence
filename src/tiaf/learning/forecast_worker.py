"""Private isolated trainer. Only this module imports optional ML dependencies.

The parent sets single-thread environment before process creation. The worker
sets a hard address-space cap before numeric imports. No executable model loader.
"""

import importlib.metadata
import platform
import resource
import sys
import time
import warnings
from datetime import datetime
from typing import Any

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.identity import canonical_json

from .forecast_artifacts import (
    LibraryVersions,
    LogisticArtifact,
    Reconstruction,
    ScalerArtifact,
    TrainingInput,
    reconstruct,
)

VERSIONS = {
    "scikit-learn": "1.7.2",
    "numpy": "2.3.3",
    "scipy": "1.16.2",
    "joblib": "1.5.2",
    "threadpoolctl": "3.6.0",
}


def fit(request: TrainingInput) -> LogisticArtifact:
    """One fit, with no access to qualification files, test rows or provider credentials."""
    for name, version in VERSIONS.items():
        if importlib.metadata.version(name) != version:
            raise ModuleNotFoundError("ML_DEPENDENCY_VERSION_MISMATCH")
    import numpy as np
    from sklearn.exceptions import ConvergenceWarning  # type: ignore[import-untyped]
    from sklearn.linear_model import LogisticRegression  # type: ignore[import-untyped]
    from sklearn.preprocessing import StandardScaler  # type: ignore[import-untyped]
    from threadpoolctl import threadpool_info  # type: ignore[import-untyped]

    backends = threadpool_info()
    if not backends or any(b["num_threads"] != 1 for b in backends):
        raise ValueError("NUMERIC_THREAD_LIMIT")
    x = np.asarray([r.values for r in request.rows], dtype=np.float64)
    y = np.asarray([r.label for r in request.rows], dtype=np.int64)
    scaler = StandardScaler(with_mean=True, with_std=True)
    transformed = scaler.fit_transform(x)
    config = request.manifest.model_config_value.model_dump(
        exclude={"schema_version", "fingerprint"}
    )
    model = LogisticRegression(**config)
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(transformed, y)
    if int(model.n_iter_[0]) >= 1000 or list(model.classes_) != [0, 1]:
        raise ValueError("MODEL_NONCONVERGENCE_OR_CLASS_MAPPING")
    s = ScalerArtifact(
        n=int(scaler.n_samples_seen_),
        means=tuple(scaler.mean_),
        variances=tuple(scaler.var_),
        scales=tuple(scaler.scale_),
        constant_columns=tuple(
            i
            for i in range(5)
            if scaler.var_[i]
            <= (
                scaler.n_samples_seen_ * np.finfo(np.float64).eps * scaler.var_[i]
                + (scaler.n_samples_seen_ * scaler.mean_[i] * np.finfo(np.float64).eps) ** 2
            )
        ),
        training_fingerprint=request.manifest.scientific_fingerprint,
    )
    representation = Reconstruction(
        scaler=s, coefficients=tuple(model.coef_[0]), intercept=float(model.intercept_[0])
    )
    # Five algebraic probes derived ONLY from the TRAIN scaler, not market/test rows.
    probes = tuple(
        tuple(m + k * scale for m, scale in zip(s.means, s.scales, strict=True))
        for k in (0.0, 1.0, -1.0, 1e6, -1e6)
    )
    expected = model.predict_proba(scaler.transform(np.asarray(probes)))[:, 1]
    errors = [
        abs(reconstruct(representation, p) - float(expected[i]))  # type: ignore[arg-type]
        for i, p in enumerate(probes)
    ]
    return LogisticArtifact(
        manifest=request.manifest,
        reconstruction=representation,
        versions=LibraryVersions(
            python=platform.python_version(),
            numeric_backends=tuple(
                sorted(
                    f"{b['internal_api']}:{b['version']}:"
                    f"{b.get('architecture', 'unknown')}:threads=1"
                    for b in backends
                )
            ),
        ),
        n_iter=int(model.n_iter_[0]),
        created_at=datetime.now(TIAF_TIMEZONE),
        reconstruction_max_error=max(errors),
    )


def main() -> int:
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    started = time.process_time()
    output: dict[str, Any]
    try:
        raw = sys.stdin.buffer.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError("WORKER_INPUT_LIMIT")
        request = TrainingInput.model_validate_json(raw)
        audit = request.manifest.audit
        if audit.train < 500 or min(audit.positive, audit.zero) < 100:
            output = {"status": "UNAVAILABLE", "reason": "INSUFFICIENT_TRAINING_DATA"}
        else:
            artifact = fit(request)
            output = {"status": "TRAINED", "artifact": artifact.model_dump(mode="json")}
    except (ImportError, importlib.metadata.PackageNotFoundError):
        output = {"status": "UNAVAILABLE", "reason": "ML_DEPENDENCY_UNAVAILABLE"}
    except Exception as exc:
        # No data-bearing exception text or traceback is exported.
        output = {"status": "FAILED", "reason": f"MODEL_FIT_FAILED:{type(exc).__name__}"}
    output["cpu_seconds"] = time.process_time() - started
    output["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    output["address_space_limit_bytes"] = resource.getrlimit(resource.RLIMIT_AS)[0]
    output["cpu_limit_seconds"] = resource.getrlimit(resource.RLIMIT_CPU)[0]
    print(canonical_json(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
