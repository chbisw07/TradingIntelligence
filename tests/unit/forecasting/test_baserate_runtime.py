"""FF0-04–07/11–16/18/26–27: synthetic pure BaseRate and trusted COLD execution."""

import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from types import MappingProxyType

import pytest
from pydantic import ValidationError

from tiaf.forecasting.capture import ForecastEvidenceSnapshot, capture_artifact
from tiaf.forecasting.contracts import BinaryProbabilityOutput, ForecastAbsence, ForecastRequest
from tiaf.forecasting.enums import ForecastReason, ForecastStatus
from tiaf.forecasting.errors import (
    ForecastAdmissionError,
    ForecastIntegrityError,
    ForecastStoreError,
)
from tiaf.forecasting.forecasters import (
    HistoricalBaseRateForecaster,
    registered_forecasters,
    resolve_forecaster,
)
from tiaf.forecasting.runtime import ForecastRuntimeOwner, create_forecast_runtime
from tiaf.forecasting.runtime_contracts import ColdForecastConfig
from tiaf.forecasting.support import BaseRateArtifact, BaseRatePolicy, admit_support

from ._runtime_support import FixedClock, RuntimeFixture, fixture
from ._support import instant


def owner(f: RuntimeFixture, root: Path, clock: FixedClock | None = None) -> ForecastRuntimeOwner:
    return create_forecast_runtime(
        f.config,
        f.artifact,
        f.blobs,
        root=root,
        build=f.build,
        _clock=clock or FixedClock(instant(9) if f.request.simulation_as_of else instant(4, 16, 6)),
    )


@pytest.mark.parametrize("pattern,expected", [("baseline", 0.6), ("zero", 0.0), ("one", 1.0)])
def test_exact_baserate_minimum_zero_one_and_repeatability(pattern: str, expected: float) -> None:
    f = fixture(pattern=pattern)
    support = admit_support(f.artifact, f.request)
    primitive = HistoricalBaseRateForecaster()
    first = primitive.forecast(f.request, support)
    assert first == primitive.forecast(f.request, support)
    assert isinstance(first.output, BinaryProbabilityOutput)
    assert first.output.probability == expected
    assert first.output.calibration == "RAW" and first.output.uncertainty == "NOT_ESTIMATED"
    assert support.summary.qualified_count == 20 and len(support.summary.outcome_refs) == 20
    assert json.loads(first.model_dump_json())["output"]["probability"] == expected
    if pattern == "baseline":
        assert f.artifact.positive_count == 12
        assert sum(row.label == 0 for row in f.artifact.rows) == 8
        assert (
            f.artifact.rows[-1].reference is not None and f.artifact.rows[-1].terminal is not None
        )
        assert f.artifact.rows[-1].label == 0  # Exact equal-close transition is included.


@pytest.mark.parametrize("n", [0, 1, 19, 20])
def test_fixed_window_no_backfill_and_minimum_support(n: int, tmp_path: Path) -> None:
    f = fixture(included=n)
    captured = owner(f, tmp_path).run(f.request, f.snapshot, f.blobs)
    result = captured.result
    assert result.inference is not None and result.inference.support is not None
    assert result.inference.support.qualified_count == n
    assert result.inference.usage.attempts == 1
    if n < 20:
        assert result.status is ForecastStatus.UNAVAILABLE and isinstance(
            result.output, ForecastAbsence
        )
        assert result.output.reasons == (ForecastReason.HISTORY_SUPPORT_INSUFFICIENT,)
        assert "probability" not in result.output.model_dump(mode="json")
    else:
        assert result.status is ForecastStatus.GENERATED


def test_future_availability_is_excluded_before_forecaster() -> None:
    f = fixture(late_label=True)
    support = admit_support(f.artifact, f.request)
    assert f.artifact.eligible_count == support.summary.qualified_count == 19
    assert f.artifact.rows[-1].label_source.artifact not in support.summary.outcome_refs
    assert (
        HistoricalBaseRateForecaster().forecast(f.request, support).status
        is ForecastStatus.UNAVAILABLE
    )
    assert not hasattr(support, "rows") and not hasattr(support, "journal")


@pytest.mark.parametrize(
    "field,value",
    [
        ("positive_count", -1),
        ("positive_count", 21),
        ("positive_count", True),
        ("positive_count", 11),
        ("eligible_count", 21),
        ("eligible_count", 19),
        ("eligible_count", 20.0),
        ("prepared_at", "2026-02-03T16:00:00+05:30"),
        ("data_basis", "QUALIFIED_CAPTURE"),
    ],
)
def test_count_artifact_corruption_and_unapproved_basis_reject(field: str, value: object) -> None:
    f = fixture()
    payload = f.artifact.model_dump(mode="json")
    payload[field] = value
    with pytest.raises(ValidationError):
        BaseRateArtifact.model_validate(payload)


@pytest.mark.parametrize(
    "fault",
    [
        "wrong_label",
        "future_included",
        "nonadjacent",
        "partial_window",
        "duplicate_window",
        "shared_close",
    ],
)
def test_complete_ordered_witness_is_not_an_arbitrary_filtered_sample(fault: str) -> None:
    f = fixture(late_label=fault == "future_included")
    data = f.artifact.model_dump(mode="json")
    if fault == "wrong_label":
        data["rows"][0]["label"] = 0
    elif fault == "future_included":
        data["rows"][-1].update(included=True, exclusion_reasons=[])
        data.update(eligible_count=20)
    elif fault == "nonadjacent":
        data["rows"][0]["reference_session_id"] = "session:s02"
    elif fault == "partial_window":
        data["rows"].pop()
    elif fault == "duplicate_window":
        data["rows"][-1] = data["rows"][0]
    else:
        data["rows"][1]["reference"]["observation_id"] = "observation:inconsistent"
    with pytest.raises(ValidationError):
        BaseRateArtifact.model_validate(data)


@pytest.mark.parametrize(
    "policy,value",
    [
        ("minimum_support", 19),
        ("window_transitions", 21),
        ("minimum_support", True),
        ("smoothing", True),
    ],
)
def test_no_new_hyperparameters_or_minimum_overrides(policy: str, value: object) -> None:
    with pytest.raises(ValidationError):
        BaseRatePolicy.model_validate({policy: value})


def test_registry_metadata_is_static_stable_and_not_authority() -> None:
    from tiaf.forecasting import forecasters

    catalog = registered_forecasters()
    assert len(catalog) == 1 and catalog == registered_forecasters()
    assert catalog[0].optional_dependencies == () and len(catalog[0].realization_modes) == 2
    assert isinstance(forecasters._REGISTRY, MappingProxyType)
    assert resolve_forecaster(catalog[0].forecaster_id, "1.0").descriptor() == catalog[0]
    with pytest.raises(ValidationError):
        catalog[0].implementation_version = "other"  # type: ignore[assignment]


@pytest.mark.parametrize(
    "identifier,version",
    [("unknown", "1.0"), ("forecaster:historical-base-rate", "2.0"), ("os.system", "1.0")],
)
def test_unknown_or_wrong_version_never_falls_back(identifier: str, version: str) -> None:
    with pytest.raises(ForecastIntegrityError, match="NOT_REGISTERED"):
        resolve_forecaster(identifier, version)


@pytest.mark.parametrize(
    "fault",
    [
        "unknown",
        "version",
        "descriptor",
        "artifact",
        "code",
        "missing_blob",
        "future_preparation",
        "model_path",
        "strict_currency_cap",
    ],
)
def test_cold_denial_precedes_any_write_or_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fault: str
) -> None:
    f = fixture()
    cfg, art = f.config.model_dump(mode="json"), f.artifact.model_dump(mode="json")
    blobs = f.blobs
    if fault == "unknown":
        cfg["forecaster_id"] = "forecaster:missing"
    elif fault == "version":
        cfg["implementation_version"] = "2.0"
    elif fault == "descriptor":
        cfg["descriptor_ref"]["fingerprint"] = "0" * 64
    elif fault == "artifact":
        cfg["composition"]["nodes"][0]["artifact_ref"]["fingerprint"] = "0" * 64
    elif fault == "code":
        art["code_ref"]["fingerprint"] = "0" * 64
    elif fault == "missing_blob":
        blobs = ()
    elif fault == "future_preparation":
        art["prepared_at"] = instant(10)
    elif fault == "model_path":
        cfg["model_path"] = "untrusted.pkl"
    else:
        cfg["strict_total_currency_cap"] = True

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("startup attempted inference")

    monkeypatch.setattr(HistoricalBaseRateForecaster, "forecast", forbidden)
    root = tmp_path / "new"
    with pytest.raises((ValidationError, ForecastIntegrityError, ForecastAdmissionError)):
        create_forecast_runtime(
            ColdForecastConfig.model_validate(cfg),
            BaseRateArtifact.model_validate(art),
            blobs,
            root=root,
            build=f.build,
            _clock=FixedClock(instant(9)),
        )
    assert not root.exists()


def test_cold_freeze_and_physical_root_not_scientific_identity(tmp_path: Path) -> None:
    f = fixture()
    first, second = owner(f, tmp_path / "one"), owner(f, tmp_path / "two")
    assert first.configuration_fingerprint == second.configuration_fingerprint
    assert first.composition_fingerprint == second.composition_fingerprint
    assert first.configuration_fingerprint != first.composition_fingerprint
    with pytest.raises(FrozenInstanceError):
        first.config = f.config  # type: ignore[misc]
    with pytest.raises(ValidationError):
        first.config.profile_id = "profile:changed"
    assert first.config.composition.roots[0].role == "BENCHMARK"


def test_request_cannot_replace_profile_or_backdate_production(tmp_path: Path) -> None:
    f = fixture()
    runtime = owner(f, tmp_path)
    data = f.request.model_dump(mode="json")
    data["configuration_ref"]["fingerprint"] = "0" * 64
    with pytest.raises(ForecastIntegrityError, match="PROFILE_PIN"):
        runtime.run(ForecastRequest.model_validate(data), f.snapshot, f.blobs)
    for field in ("issued_at", "computed_at", "clock", "minimum_support"):
        with pytest.raises(ValidationError):
            ForecastRequest.model_validate(
                {**f.request.model_dump(mode="json"), field: "forbidden"}
            )


@pytest.mark.parametrize("simulated", [False, True])
def test_runtime_controls_original_clocks_and_unique_attempt_usage(
    tmp_path: Path, simulated: bool
) -> None:
    f = fixture(simulated=simulated)
    now = instant(9) if simulated else instant(4, 16, 6)
    runtime = owner(f, tmp_path, FixedClock(now))
    first = runtime.run(f.request, f.snapshot, f.blobs)
    second = runtime.run(f.request, f.snapshot, f.blobs)
    assert first.result.run_id != second.result.run_id
    assert first.result.observation_id == second.result.observation_id
    result = first.result
    assert result.computed_at == now and result.issued_at == (None if simulated else now)
    assert result.inference is not None and result.inference.usage.attempts == 1
    usage = result.inference.usage
    assert usage.duration_seconds == pytest.approx(0.01)
    assert usage.local_cost == "UNPRICED" and usage.external_model_cost == 0
    assert (
        usage.external_model_calls
        == usage.external_provider_calls
        == usage.input_model_tokens
        == usage.output_model_tokens
        == 0
    )
    assert len((tmp_path / "forecast_runs.jsonl").read_text().splitlines()) == 2


def test_real_system_clock_simulates_history_but_cannot_issue_in_the_past(tmp_path: Path) -> None:
    from tiaf.forecasting.clocks import SystemClock

    clock = SystemClock()
    for simulated in (True, False):
        f = fixture(simulated=simulated)
        before = clock.now()
        runtime = create_forecast_runtime(
            f.config, f.artifact, f.blobs, root=tmp_path / str(simulated), build=f.build
        )
        captured = runtime.run(f.request, f.snapshot, f.blobs)
        assert before <= captured.recorded_at <= clock.now()
        assert captured.result.issued_at is None
        if simulated:
            assert (
                captured.result.computed_at is not None
                and before <= captured.result.computed_at <= captured.recorded_at
            )
        else:
            assert captured.result.status is ForecastStatus.UNAVAILABLE
            assert captured.result.computed_at is None


@pytest.mark.parametrize("fault", ["deadline", "exception", "late_completion", "disk"])
def test_runtime_failures_are_not_trading_nonaction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fault: str
) -> None:
    f = fixture(simulated=fault not in ("late_completion",))
    clock = FixedClock(
        instant(4, 16, 6) if fault == "late_completion" else instant(9),
        step=1.1 if fault == "deadline" else 0.01,
    )
    runtime = owner(f, tmp_path, clock)
    original = HistoricalBaseRateForecaster.forecast

    def run(
        self: HistoricalBaseRateForecaster, request: ForecastRequest, support: object
    ) -> object:
        if fault == "exception":
            raise RuntimeError("sensitive provider body must not be echoed")
        payload = original(self, request, support)  # type: ignore[arg-type]
        clock.at = f.request.window.target_open_time
        return payload

    if fault in ("exception", "late_completion"):
        monkeypatch.setattr(HistoricalBaseRateForecaster, "forecast", run)
    if fault == "disk":

        def denied(*args: object, **kwargs: object) -> None:
            raise ForecastStoreError("SYNTHETIC_DISK_DENIAL")

        monkeypatch.setattr("tiaf.forecasting.store.ForecastCorpusStore.append_forecast", denied)
        with pytest.raises(ForecastStoreError):
            runtime.run(f.request, f.snapshot, f.blobs)
        assert not (tmp_path / "forecast_runs.jsonl").exists()
        return
    result = runtime.run(f.request, f.snapshot, f.blobs).result
    assert result.status is (
        ForecastStatus.UNAVAILABLE if fault == "late_completion" else ForecastStatus.FAILED
    )
    assert result.issued_at is None and result.inference is not None
    assert result.inference.usage.attempts == 1 and "sensitive" not in result.model_dump_json()


def test_duplicate_injected_execution_id_cannot_reexecute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    f = fixture()
    runtime = create_forecast_runtime(
        f.config,
        f.artifact,
        f.blobs,
        root=tmp_path,
        build=f.build,
        _clock=FixedClock(instant(9)),
        _new_id=lambda: "same",
    )
    runtime.run(f.request, f.snapshot, f.blobs)

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("duplicate attempted to execute")

    monkeypatch.setattr(HistoricalBaseRateForecaster, "forecast", forbidden)
    with pytest.raises(ForecastIntegrityError, match="DUPLICATE_EXECUTION"):
        runtime.run(f.request, f.snapshot, f.blobs)


def with_reference_qualification(f: RuntimeFixture, status: str) -> RuntimeFixture:
    data = f.request.model_dump(mode="json")
    data["window"]["reference"].update(qualification=status, reasons=["EVIDENCE_UNQUALIFIED"])
    request = ForecastRequest.model_validate(data)
    snapshot = ForecastEvidenceSnapshot(
        window=request.window, history=f.snapshot.history, sources=f.snapshot.sources
    )
    data["evidence_ref"] = capture_artifact(
        "input:qualification-" + status, snapshot
    ).reference.model_dump(mode="json")
    return replace(f, request=ForecastRequest.model_validate(data), snapshot=snapshot)


@pytest.mark.parametrize("qualification", ["STALE", "PARTIAL", "AMBIGUOUS"])
def test_failed_current_evidence_qualification_never_calls_forecaster(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, qualification: str
) -> None:
    f = with_reference_qualification(fixture(), qualification)
    runtime = owner(f, tmp_path)

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("unqualified current evidence dispatched")

    monkeypatch.setattr(HistoricalBaseRateForecaster, "forecast", forbidden)
    result = runtime.run(f.request, f.snapshot, f.blobs).result
    assert result.status is ForecastStatus.UNAVAILABLE and result.inference is not None
    assert result.inference.usage.attempts == 0


def test_later_acquisition_retained_only_under_explicit_historical_basis(tmp_path: Path) -> None:
    f = fixture(late_acquisition=True)
    capture = owner(f, tmp_path).run(f.request, f.snapshot, f.blobs)
    assert capture.result.status is ForecastStatus.GENERATED
    assert all(source.acquired_at == instant(8) for source in f.artifact.fit_evidence)
    assert capture.result.request.simulation_as_of == instant(4, 16, 5)
    data = f.request.model_dump(mode="json")
    data["knowledge_basis"] = "CAPTURED_AS_KNOWN"
    with pytest.raises(ValueError, match="KNOWLEDGE_CUTOFF"):
        ForecastRequest.model_validate(data)


@pytest.mark.parametrize("cutoff", ["fit_after_cutoff", "label_at_cutoff"])
def test_artifact_and_label_cutoff_admission_never_reaches_primitive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, cutoff: str
) -> None:
    f = fixture()
    data = f.request.model_dump(mode="json")
    data["information_cutoff"] = instant(4, 15, 36)
    request = ForecastRequest.model_validate(data)
    if cutoff == "label_at_cutoff":
        art = f.artifact.model_dump(mode="json")
        art["fit_knowledge_cutoff"] = instant(4, 15, 36)
        artifact = BaseRateArtifact.model_validate(art)
        with pytest.raises(ForecastAdmissionError, match="KNOWLEDGE_CUTOFF"):
            admit_support(artifact, request)
        return
    runtime = owner(f, tmp_path)

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("future fit dispatched")

    monkeypatch.setattr(HistoricalBaseRateForecaster, "forecast", forbidden)
    result = runtime.run(request, f.snapshot, f.blobs).result
    assert result.status is ForecastStatus.UNAVAILABLE and result.inference is not None
    assert result.inference.usage.attempts == 0


@pytest.mark.parametrize("coverage", ["UNKNOWN", "AFFECTED"])
def test_action_absence_does_not_adjust_prices_or_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, coverage: str
) -> None:
    f = fixture()
    data = f.request.model_dump(mode="json")
    data["window"]["reference"]["action_coverage"] = coverage
    request = ForecastRequest.model_validate(data)
    snapshot = ForecastEvidenceSnapshot(
        window=request.window, history=f.snapshot.history, sources=f.snapshot.sources
    )
    data["evidence_ref"] = capture_artifact("input:action-" + coverage, snapshot).reference
    request = ForecastRequest.model_validate(data)

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("action-unqualified evidence dispatched")

    monkeypatch.setattr(HistoricalBaseRateForecaster, "forecast", forbidden)
    result = owner(f, tmp_path).run(request, snapshot, f.blobs).result
    assert result.status is ForecastStatus.UNAVAILABLE and result.inference is not None
    assert result.inference.usage.attempts == 0


def test_reused_bar_reference_cannot_hide_another_session() -> None:
    from tiaf.forecasting.support import validate_support_bars

    f = fixture()
    data = f.artifact.model_dump(mode="json")
    first = data["rows"][0]["reference"]["bar_ref"]
    data["rows"][0]["terminal"]["bar_ref"] = first
    data["rows"][1]["reference"]["bar_ref"] = first
    with pytest.raises(ForecastIntegrityError, match="SUPPORT_BAR_MISMATCH"):
        validate_support_bars(BaseRateArtifact.model_validate(data), f.blobs)


def test_no_sensitive_payloads_in_structured_runtime_log(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    f = fixture()
    with caplog.at_level("INFO", logger="tiaf.forecasting.runtime"):
        capture = owner(f, tmp_path).run(f.request, f.snapshot, f.blobs)
    record = caplog.records[-1].__dict__
    assert record["forecast_request"] == f.request.request_id
    assert record["forecast_forecaster"] == f.config.forecaster_id
    assert record["forecast_support_count"] == 20
    assert record["forecast_target_version"] == "1.0"
    assert record["forecast_replay_fingerprint"] == capture.result.replay_fingerprint
    assert not {"evidence", "prices", "metadata", "root", "exception"}.intersection(record)
    assert str(tmp_path) not in caplog.text
