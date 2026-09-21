"""FF-1.3 synthetic engineering; no licensed dataset, ML fits, truth or network."""

import json
import math
import platform
from datetime import timedelta
from hashlib import sha256
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import ValidationError
from scripts import generate_ff1_logistic_forecasts as cli

from tiaf.evaluation.forecast_retrospective_contracts import RetrospectiveQualification
from tiaf.forecasting.identity import canonical_json
from tiaf.forecasting.logistic_forecasts import (
    ForecastShard,
    LogisticForecastRun,
    ResearchForecastResult,
    eligibility,
    generate,
    model_for,
    population,
    validate_handoff,
)
from tiaf.forecasting.logistic_projection import (
    ForecastOrigin,
    ForecastProjection,
    object_spans,
    project_qualification,
)
from tiaf.forecasting.logistic_store import (
    ResearchForecastStore,
    capture_training,
    recorded_replay,
    verify_records,
    verify_run,
)
from tiaf.learning.forecast_artifacts import (
    LibraryVersions,
    LogisticArtifact,
    Reconstruction,
    ScalerArtifact,
)
from tiaf.learning.forecast_jobs import TrainingJob, TrainingRun
from tiaf.learning.forecast_training import prepare_training

from .test_adjusted_retrospective_research import AT
from .test_logistic_training_admission import bound
from .test_logistic_training_admission import qualification as qualification  # fixture


@pytest.fixture(scope="module")
def handoff(qualification: RetrospectiveQualification) -> TrainingRun:
    # Data-only synthetic parameters, never claim an empirical fit in tests.
    grant = bound(qualification, basis="QUALIFIED_ADJUSTED_RESEARCH")
    jobs = []
    for year in grant.allowed_folds:
        manifest = prepare_training(qualification, grant, year).manifest
        scale = float(year - 2019)
        scaler = ScalerArtifact(
            n=manifest.audit.train,
            means=(1.0, 2.0, 3.0, 4.0, 5.0),
            variances=(scale**2,) * 5,
            scales=(scale,) * 5,
            constant_columns=(),
            training_fingerprint=manifest.scientific_fingerprint,
        )
        model = LogisticArtifact(
            manifest=manifest,
            reconstruction=Reconstruction(
                scaler=scaler,
                coefficients=(0.1, -0.2, 0.3, -0.4, 0.5),
                intercept=0.07,
            ),
            versions=LibraryVersions(python="3.12.3", numeric_backends=("SYNTHETIC_NO_FIT",)),
            n_iter=1,
            created_at=AT,
            reconstruction_max_error=0.0,
        )
        jobs.append(
            TrainingJob(
                fold_id=year,
                grant_fingerprint=cast(str, grant.fingerprint),
                manifest_fingerprint=cast(str, manifest.fingerprint),
                status="TRAINED",
                artifact=model,
                started_at=AT,
                completed_at=AT,
                elapsed_seconds=0.0,
                address_space_limit_bytes=536870912,
                cpu_limit_seconds=60,
            )
        )
    return TrainingRun(grant=grant, jobs=tuple(jobs), created_at=AT, status="COMPLETE")


@pytest.fixture(scope="module")
def projection(
    qualification: RetrospectiveQualification,
    handoff: TrainingRun,
    tmp_path_factory: pytest.TempPathFactory,
) -> ForecastProjection:
    path = tmp_path_factory.mktemp("projection") / "qualification.json"
    raw = qualification.model_dump_json().encode()
    path.write_bytes(raw)
    return project_qualification(path, sha256(raw).hexdigest(), handoff.grant)


@pytest.fixture(scope="module")
def records(
    projection: ForecastProjection, handoff: TrainingRun
) -> tuple[ResearchForecastResult, ...]:
    # One generated row per fold plus every excluded/protected origin.
    selected = {
        next(o.observation_id for o in projection.origins if o.reference_date.year == y)
        for y in (2021, 2022, 2023, 2024)
    }
    return tuple(
        generate(o, projection, handoff, AT + timedelta(seconds=1))
        for o in projection.origins
        if o.observation_id in selected or o.reasons
    )


def build_store(
    root: Path, records: tuple[ResearchForecastResult, ...], handoff: TrainingRun
) -> tuple[ResearchForecastStore, str]:
    store = ResearchForecastStore(root, create=True)
    capture_training(store, handoff)
    refs = tuple(store.put("capture", r) for r in records)
    shard = store.put("shard", ForecastShard(captures=refs))
    q = records[0].request
    parent = LogisticForecastRun(
        **{
            k: getattr(q, k)
            for k in (
                "qualification_blob",
                "qualification_fingerprint",
                "dataset_fingerprint",
                "research_profile_fingerprint",
                "feature_schema_fingerprint",
                "training_run_fingerprint",
                "dependency_lock_fingerprint",
            )
        },
        shards=(shard,),
        populations=(
            population(2021, records),
            population(2022, records),
            population(2023, records),
            population(2024, records),
        ),
        verification_matches=len(records),
        created_at=AT + timedelta(seconds=2),
    )
    return store, store.put("run", parent)


def test_outcomes_never_decoded(
    qualification: RetrospectiveQualification,
    handoff: TrainingRun,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = qualification.model_dump(mode="json")
    data["audit"] = data["folds"] = "FORBIDDEN_OUTCOME"
    for row in data["observations"]:
        row["label"] = row["assumed_label_available_at"] = "FORBIDDEN_OUTCOME"
        if row["reference_date"] >= "2025" or (row["target_date"] or "") >= "2025":
            row["features"] = "FORBIDDEN_OUTCOME"
    raw = json.dumps(data).encode()
    path = tmp_path / "source.json"
    path.write_bytes(raw)
    original = json.loads

    def guarded(value: Any, *args: Any, **kwargs: Any) -> Any:
        assert "FORBIDDEN_OUTCOME" not in value
        return original(value, *args, **kwargs)

    monkeypatch.setattr(json, "loads", guarded)
    p = project_qualification(path, sha256(raw).hexdigest(), handoff.grant)
    assert len(p.origins) == 991
    assert all(o.reference_date.year < 2025 for o in p.origins)
    assert p.origins[-1].protected and p.origins[-1].features is None


def test_source_byte_pin_before_any_decode(tmp_path: Path, handoff: TrainingRun) -> None:
    p = tmp_path / "bad.json"
    p.write_bytes(b"not JSON")
    with pytest.raises(ValueError, match="BYTE_PIN"):
        project_qualification(p, "0" * 64, handoff.grant)


@pytest.mark.parametrize("text", ['{"a":1,"a":2}', "[]", '{"x":[}'])
def test_projection_malformed_or_duplicate(text: str) -> None:
    with pytest.raises(ValueError):
        object_spans(text)


@pytest.mark.parametrize(
    "year,candidate,generated,excluded,protected",
    [
        (2021, 248, 248, 0, 0),
        (2022, 248, 248, 0, 0),
        (2023, 246, 225, 21, 0),
        (2024, 249, 248, 0, 1),
    ],
)
def test_full_population_metadata(
    projection: ForecastProjection,
    year: int,
    candidate: int,
    generated: int,
    excluded: int,
    protected: int,
) -> None:
    states = [eligibility(o)[0] for o in projection.origins if o.reference_date.year == year]
    assert len(states) == candidate
    assert states.count("GENERATED") == generated
    assert states.count("EXCLUDED") == excluded
    assert states.count("PROTECTED") == protected
    assert states.count("UNAVAILABLE") == 0


@pytest.mark.parametrize("year", [2021, 2022, 2023, 2024])
def test_fixed_fold_scaler_probability_clocks(
    records: tuple[ResearchForecastResult, ...], handoff: TrainingRun, year: int
) -> None:
    r = next(r for r in records if r.request.fold_id == year and r.output is not None)
    m = model_for(handoff, year)
    f = r.request.origin.features
    assert f is not None and r.output is not None
    z = (
        sum(
            (x - mean) / scale * beta
            for x, mean, scale, beta in zip(
                f.values,
                m.reconstruction.scaler.means,
                m.reconstruction.scaler.scales,
                m.reconstruction.coefficients,
                strict=True,
            )
        )
        + m.reconstruction.intercept
    )
    assert r.output.probability == pytest.approx(1 / (1 + math.exp(-z)), abs=1e-12)
    assert m.manifest.fit_cutoff < r.request.origin.information_cutoff
    assert r.request.origin.target_opens_at is not None
    assert r.request.origin.simulation_as_of < r.request.origin.target_opens_at
    assert r.computed_at == AT + timedelta(seconds=1)
    assert "issued_at" not in r.model_dump_json()
    assert r.request.mode == "SIMULATED" and r.request.composition.role == "CHALLENGER"
    assert r.request.composition.scaler_fingerprint == m.reconstruction.scaler.fingerprint


@pytest.mark.parametrize(
    "updates",
    [
        {"reference_date": "2025-01-01"},
        {"simulation_as_of": "2021-01-01T16:05:00"},
        {"information_cutoff": "2021-01-01T15:30:00+05:30"},
        {"label": 1},
    ],
)
def test_bad_origin_or_truth_forbidden(
    projection: ForecastProjection, updates: dict[str, Any]
) -> None:
    with pytest.raises(ValidationError):
        ForecastOrigin.model_validate({**projection.origins[0].model_dump(), **updates})


def test_protected_origin_no_numeric_material(
    projection: ForecastProjection, records: tuple[ResearchForecastResult, ...]
) -> None:
    origin = projection.origins[-1]
    assert origin.protected and not origin.feature_window_dates and origin.features is None
    r = records[-1]
    assert r.status == "PROTECTED" and r.output is None
    assert r.reasons == ("TARGET_HOLDOUT_SEALED",)


def test_missing_features_unavailable(projection: ForecastProjection) -> None:
    origin = ForecastOrigin.model_validate({**projection.origins[0].model_dump(), "features": None})
    assert eligibility(origin) == ("UNAVAILABLE", ("MISSING_FEATURES_OR_TARGET_SESSION",))


def test_immutable_roundtrip_and_scientific_identity(
    projection: ForecastProjection, handoff: TrainingRun
) -> None:
    a = generate(projection.origins[0], projection, handoff, AT + timedelta(seconds=1))
    b = generate(projection.origins[0], projection, handoff, AT + timedelta(seconds=3))
    assert a.forecast_id == b.forecast_id and a.fingerprint != b.fingerprint
    assert ResearchForecastResult.model_validate_json(a.model_dump_json()) == a
    assert isinstance(a.model_dump(mode="json")["reasons"], list)
    with pytest.raises(ValidationError):
        a.computed_at = AT
    with pytest.raises(ValidationError):
        ResearchForecastResult.model_validate({**a.model_dump(), "issued_at": AT})


def test_no_fitting_or_network(
    records: tuple[ResearchForecastResult, ...],
    projection: ForecastProjection,
    handoff: TrainingRun,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import socket

    import tiaf.learning.forecast_jobs as jobs

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("forbidden fit/network call")

    monkeypatch.setattr(jobs, "run_fit", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    assert (
        generate(projection.origins[0], projection, handoff, records[0].computed_at) == records[0]
    )


def test_incomplete_training_and_holdout_refused(handoff: TrainingRun) -> None:
    empty = TrainingRun(grant=handoff.grant, jobs=(), created_at=AT, status="FAILED")
    with pytest.raises(ValueError, match="COMPLETE_EMPIRICAL"):
        validate_handoff(empty)
    with pytest.raises(ValueError, match="FOLD_MODEL"):
        model_for(handoff, 2025)


@pytest.mark.parametrize("package", list(cli.VERSIONS))
def test_dependency_mismatch_hold(package: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cli, "version", lambda name: "wrong" if name == package else cli.VERSIONS[name]
    )
    with pytest.raises(ValueError, match="DEPENDENCY_LOCK_MISMATCH"):
        cli.check_dependencies()


def test_lock_and_python_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(platform, "python_version", lambda: "3.12.4")
    with pytest.raises(ValueError, match="DEPENDENCY_LOCK_MISMATCH"):
        cli.check_dependencies()
    monkeypatch.setattr(platform, "python_version", lambda: "3.12.3")
    monkeypatch.setattr(cli, "LOCK_SHA", "0" * 64)
    with pytest.raises(ValueError, match="DEPENDENCY_LOCK_MISMATCH"):
        cli.check_dependencies()


def test_store_replay_idempotent_no_source_or_refit(
    tmp_path: Path,
    handoff: TrainingRun,
    records: tuple[ResearchForecastResult, ...],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, fp = build_store(tmp_path / "corpus", records, handoff)
    original = {p.name: p.read_bytes() for p in store.root.iterdir()}
    assert store.put("capture", records[0]) == records[0].fingerprint
    monkeypatch.setattr(cli, "check_dependencies", lambda: pytest.fail("ML not needed for replay"))
    result = verify_run(ResearchForecastStore(store.root), fp)
    assert result.status == "MATCH" and result.matches == len(records)
    assert recorded_replay(store, fp)[1] == records
    assert original == {p.name: p.read_bytes() for p in store.root.iterdir()}
    with pytest.raises(ValueError, match="READ_ONLY"):
        ResearchForecastStore(store.root).put("capture", records[0])


def test_verifier_streams_without_materialized_corpus(
    tmp_path: Path,
    handoff: TrainingRun,
    records: tuple[ResearchForecastResult, ...],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tiaf.forecasting.logistic_store as storage

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("verification must stream; no materialized whole-corpus replay")

    store, fp = build_store(tmp_path / "corpus", records, handoff)
    monkeypatch.setattr(storage, "recorded_replay", forbidden)
    assert verify_run(store, fp).status == "MATCH"


@pytest.mark.parametrize("kind", ["capture", "model", "scaler", "training", "shard"])
def test_missing_closure_mismatch(
    tmp_path: Path, handoff: TrainingRun, records: tuple[ResearchForecastResult, ...], kind: str
) -> None:
    store, fp = build_store(tmp_path / "corpus", records, handoff)
    path = next(store.root.glob(f"{kind}-*.json"))
    path.unlink()
    assert verify_run(store, fp).status == "MISMATCH"


def test_probability_tamper_with_new_seal_rejected(
    tmp_path: Path, handoff: TrainingRun, records: tuple[ResearchForecastResult, ...]
) -> None:
    store, _ = build_store(tmp_path / "corpus", records, handoff)
    first = records[0]
    assert first.output is not None
    bad = ResearchForecastResult.model_validate(
        {
            **first.model_dump(exclude={"fingerprint"}),
            "output": {**first.output.model_dump(), "probability": 0.99},
        }
    )
    with pytest.raises(ValueError, match="PROBABILITY_MISMATCH"):
        verify_records(store, (bad, *records[1:]), handoff)


def test_stale_seal_and_symlink_refused(
    tmp_path: Path, handoff: TrainingRun, records: tuple[ResearchForecastResult, ...]
) -> None:
    store, fp = build_store(tmp_path / "corpus", records, handoff)
    path = next(store.root.glob("capture-*.json"))
    payload = json.loads(path.read_text())
    payload["computed_at"] = "2026-09-22T16:00:00+05:30"
    path.write_text(canonical_json(payload) + "\n")
    assert verify_run(store, fp).status == "MISMATCH"
    link = tmp_path / "link"
    link.symlink_to(store.root, target_is_directory=True)
    with pytest.raises(ValueError, match="UNSAFE"):
        ResearchForecastStore(link)


def test_no_evaluation_or_action_fields(records: tuple[ResearchForecastResult, ...]) -> None:
    encoded = canonical_json(records)
    for name in ("brier", "log_loss", "accuracy", "bootstrap", "BUY", "SELL", "label_state"):
        assert name not in encoded
    assert '"label":' not in encoded


def test_missing_dependency_hold(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing(name: str) -> str:
        raise PackageNotFoundError(name)

    monkeypatch.setattr(cli, "version", missing)
    with pytest.raises(ValueError, match="DEPENDENCY_MISSING"):
        cli.check_dependencies()


def test_scientific_duplicate_does_not_overwrite(
    tmp_path: Path, handoff: TrainingRun, projection: ForecastProjection
) -> None:
    store = ResearchForecastStore(tmp_path / "duplicates", create=True)
    first = generate(projection.origins[0], projection, handoff, AT + timedelta(seconds=1))
    later = generate(projection.origins[0], projection, handoff, AT + timedelta(seconds=5))
    fp = store.put("capture", first)
    with pytest.raises(ValueError, match="DUPLICATE_SCIENTIFIC"):
        store.put("capture", later)
    assert store.get("capture", fp) == first


def test_wrong_fold_model_rejected(
    tmp_path: Path, handoff: TrainingRun, records: tuple[ResearchForecastResult, ...]
) -> None:
    store, _ = build_store(tmp_path / "corpus", records, handoff)
    first = records[0]
    wrong = model_for(handoff, 2022)
    q = first.request.model_dump(exclude={"fingerprint"})
    q["composition"] = {
        **first.request.composition.model_dump(exclude={"fingerprint"}),
        "model_fingerprint": wrong.fingerprint,
    }
    bad = ResearchForecastResult.model_validate(
        {
            **first.model_dump(exclude={"fingerprint"}),
            "request": q,
        }
    )
    with pytest.raises(ValueError, match="LINEAGE_MISMATCH"):
        verify_records(store, (bad,), handoff)


def test_protected_never_calls_numeric_inference(
    projection: ForecastProjection, handoff: TrainingRun, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tiaf.forecasting.logistic_forecasts as runtime

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("protected origin reached numerical inference")

    monkeypatch.setattr(runtime, "reconstruct", forbidden)
    r = generate(projection.origins[-1], projection, handoff, AT + timedelta(seconds=1))
    assert r.status == "PROTECTED" and r.output is None


def test_feature_order_change_refused(projection: ForecastProjection) -> None:
    data = projection.origins[0].model_dump()
    assert data["features"] is not None
    data["features"]["values"] = tuple(reversed(data["features"]["values"]))
    with pytest.raises(ValidationError, match="FEATURE_PROJECTION_MISMATCH"):
        ForecastOrigin.model_validate(data)


def test_parent_counts_and_shard_bound(records: tuple[ResearchForecastResult, ...]) -> None:
    p = population(2021, records)
    with pytest.raises(ValidationError):
        type(p).model_validate({**p.model_dump(), "candidate": p.candidate + 1})
    with pytest.raises(ValidationError):
        ForecastShard(captures=("0" * 64,) * 65)
