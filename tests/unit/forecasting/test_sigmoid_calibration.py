"""FF-2.2 synthetic-only acceptance, authority denials and captured replay."""

import json
import math
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

import pytest
from pydantic import ValidationError

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.evaluation.forecast_normalization import (
    NormalizedEvaluationStore,
    evaluate_normalized,
    persist_normalized_evaluation,
    replay_normalized_evaluation,
)
from tiaf.evaluation.forecast_normalization_contracts import (
    EvaluationInput,
    EvaluationParticipant,
    EvaluationTargetIdentity,
    ForecastObservation,
    GroundTruthObservation,
    GroundTruthSet,
    ParticipantForecastSet,
)
from tiaf.evaluation.sigmoid_evaluation import calibration_diagnostics, evaluate_calibrated
from tiaf.forecasting.contracts import BinaryProbabilityOutput
from tiaf.forecasting.forecaster_adapters import resolve_inference_forecaster
from tiaf.forecasting.identity import canonical_json, semantic_fingerprint
from tiaf.learning import sigmoid_calibration as service
from tiaf.learning.forecaster_authority import TrainingAuthorization, custody_root_fingerprint
from tiaf.learning.forecaster_training import TrainingBundle, reference
from tiaf.learning.sigmoid_contracts import (
    CalibratedCapture,
    CalibrationSample,
    SigmoidArtifact,
    SigmoidParameters,
    synthetic_sample,
)
from tiaf.learning.sigmoid_math import _estimate, logit, transform
from tiaf.learning.sigmoid_synthetic import (
    SyntheticCalibrationInput,
    pin,
    synthetic_source,
)

from . import test_evaluation_normalization as ev
from .test_forecaster_seams import base_request


def setup_fit(root: Path) -> tuple[service.SigmoidStore, TrainingAuthorization]:
    at = datetime.now(TIAF_TIMEZONE) - timedelta(seconds=1)
    store = service.SigmoidStore(root, create=True)
    request = service.synthetic_fit_request(at)
    grant = TrainingAuthorization(
        grant_id="grant:ff2-synthetic",
        authority_reference=request.authority_reference,
        experiment=request.experiment,
        request_reference=reference("request", request),
        input_fingerprint=semantic_fingerprint(synthetic_sample()),
        custody_root_fingerprint=custody_root_fingerprint(root),
        experiment_status="OPEN",
        holdout_status="NONE",
        qualification_reference=pin("qualification"),
        evidence_policy="SYNTHETIC_TRAIN_ONLY",
        issued_at=at,
        expires_at=at + timedelta(hours=1),
    )
    return store, grant


@pytest.fixture(scope="module")
def fitted(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[service.SigmoidStore, SigmoidArtifact, TrainingBundle]:
    store, grant = setup_fit(tmp_path_factory.mktemp("ff2") / "fit")
    artifact, bundle = service.fit_synthetic_once(
        store, service.synthetic_fit_request(grant.issued_at), grant, synthetic_sample()
    )
    return store, artifact, bundle


@pytest.fixture(scope="module")
def captures(
    fitted: tuple[service.SigmoidStore, SigmoidArtifact, TrainingBundle],
) -> tuple[CalibratedCapture, ...]:
    store, artifact, bundle = fitted
    candidate = service.compose(artifact, pin("source-composition"))
    at = artifact.fitted_at + timedelta(seconds=1)
    return tuple(
        service.apply_synthetic(store, candidate, bundle, native, synthetic_source(native))
        for native in (SyntheticCalibrationInput(index=i, at=at) for i in range(60, 120))
    )


def eval_input(captures: tuple[CalibratedCapture, ...]) -> EvaluationInput:
    """External TEST truth, distinct observations from the fit fixture, no price labeler."""
    at = captures[0].created_at + timedelta(seconds=1)
    component = captures[0].candidate.artifact.component
    target = EvaluationTargetIdentity(
        target_id=component.target.target_id,
        target_version=component.target.target_version,
        horizon=component.target.horizon,
        event=component.target.positive_event,
        cutoff_policy=component.target.cutoff_policy,
    )
    pop = ev.changed(
        ev.population(),
        observation_ids=tuple(c.source.result.request.observation_id for c in captures),
        window_start=captures[0].created_at,
        window_end=at,
    )
    truth = ev.changed(ev.truth_identity(), target=target)
    participants = tuple(
        EvaluationParticipant(
            participant_id=f"participant:{name}",
            form="ARTIFACT_BACKED_FORECASTER" if i == 0 else "CALIBRATED_COMPOSITION",
            report_role="SUBJECT" if i == 0 else "CHALLENGER",
            forecast_or_composition=pin("source-composition")
            if i == 0
            else reference("sigmoidcandidate", captures[0].candidate),
            forecaster=component.source_forecaster if i == 0 else captures[0].candidate.key,
            target=target,
            population_fingerprint=str(pop.fingerprint),
            realization_mode=component.mode,
            cutoff_policy=target.cutoff_policy,
        )
        for i, name in enumerate(("raw", "calibrated"))
    )
    original = ev.request()
    pairing = ev.changed(
        original.pairing, participant_ids=tuple(p.participant_id for p in participants)
    )
    identity = ev.changed(
        original.identity,
        target=target,
        population_fingerprint=pop.fingerprint,
        ground_truth_fingerprint=truth.fingerprint,
        comparison_fingerprint=pairing.fingerprint,
        created_at=at,
    )
    request = ev.changed(
        original,
        identity=identity,
        participants=participants,
        population=pop,
        ground_truth=truth,
        pairing=pairing,
        created_at=at,
    )
    forecast_sets = tuple(
        ParticipantForecastSet(
            participant=p,
            population_fingerprint=str(pop.fingerprint),
            observations=tuple(
                ForecastObservation(
                    observation_id=c.source.result.request.observation_id,
                    participant_id=p.participant_id,
                    forecast_ref=reference("neutralinfercapture", c.source)
                    if i == 0
                    else reference("sigmoidcapture", c),
                    probability=c.raw_probability if i == 0 else c.calibrated_probability,
                    status="AVAILABLE",
                    reason="evaluation:available",
                )
                for c in captures
            ),
        )
        for i, p in enumerate(participants)
    )
    ground_truth = GroundTruthSet(
        identity=truth,
        population_fingerprint=str(pop.fingerprint),
        observations=tuple(
            GroundTruthObservation(
                observation_id=c.source.result.request.observation_id,
                journal_entry_ref=pin(f"evaluation-truth-{i}"),
                label=int(i // 6 < (1, 2, 5, 5, 8, 9)[i % 6]),
                status="AVAILABLE",
                reason="evaluation:available",
            )
            for i, c in enumerate(captures)
        ),
    )
    return EvaluationInput(
        request=request, forecast_sets=forecast_sets, ground_truth=ground_truth, captured_at=at
    )


def test_synthetic_e2e(
    fitted: tuple[service.SigmoidStore, SigmoidArtifact, TrainingBundle],
    captures: tuple[CalibratedCapture, ...],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, artifact, bundle = fitted
    assert artifact.parameters.intercept == pytest.approx(0, abs=1e-12)
    assert artifact.parameters.slope == pytest.approx(0.6365858283318643, abs=1e-12)
    assert not artifact.qualified
    assert bundle.execution.resources.numeric_threads == 1
    assert len(tuple(store.root.glob("attempt-*.json"))) == 1
    readonly = service.SigmoidStore(store.root)
    before = {p.name: p.read_bytes() for p in store.root.iterdir()}

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("recorded replay must not execute")

    with monkeypatch.context() as patch:
        patch.setattr(service, "transform", forbidden)
        patch.setattr(service, "synthetic_source", forbidden)
        patch.setattr(subprocess, "run", forbidden)
        for capture in captures:
            replayed = service.replay_sigmoid(readonly, reference("sigmoidcapture", capture))
            assert replayed.status == "MATCH" and replayed.capture == capture
            assert CalibratedCapture.model_validate_json(canonical_json(capture)) == capture
            assert capture.source.result.output == BinaryProbabilityOutput(
                probability=capture.raw_probability
            )
            assert capture.raw_probability != capture.calibrated_probability
        assert (
            service.replay_sigmoid(
                readonly, reference("sigmoidcapture", captures[0]), reconstruct=True
            ).status
            == "UNSUPPORTED"
        )
    assert before == {p.name: p.read_bytes() for p in store.root.iterdir()}
    supplied = eval_input(captures)
    result = evaluate_calibrated(supplied, captures)
    assert result.status == "GENERATED"
    evaluation_store = NormalizedEvaluationStore(tmp_path / "evaluation", create=True)
    ledger = persist_normalized_evaluation(evaluation_store, supplied)
    assert (
        replay_normalized_evaluation(NormalizedEvaluationStore(evaluation_store.root), ledger)
        == "MATCH"
    )
    # FLC-6 independently owns proper scores; compare a separate scalar oracle.
    for index, participant in enumerate(result.request.participants):
        ps = [c.raw_probability if index == 0 else c.calibrated_probability for c in captures]
        ys = [cast(int, y.label) for y in supplied.ground_truth.observations]
        expected_brier = sum((p - y) ** 2 for p, y in zip(ps, ys, strict=True)) / 60
        expected_log = (
            -sum(y * math.log(p) + (1 - y) * math.log1p(-p) for p, y in zip(ps, ys, strict=True))
            / 60
        )
        values = {
            m.metric_id: m.value
            for m in result.metrics.values
            if m.participant_id == participant.participant_id
        }
        assert values["BRIER"] == pytest.approx(expected_brier)
        assert values["NATURAL_LOG_LOSS"] == pytest.approx(expected_log)


@pytest.mark.parametrize(
    "value", [-0.01, 1.01, float("nan"), float("inf"), -float("inf"), True, "0.5"]
)
def test_bad_probability(value: object) -> None:
    with pytest.raises(ValidationError):
        CalibrationSample.model_validate({"probabilities": [value, 0.5], "labels": [0, 1]})


@pytest.mark.parametrize(
    "values,labels",
    [([0.1], [0]), ([0.1, 0.2], [0]), ([0.1, 0.2], [0, 2]), ([0.1, 0.2], [False, 1])],
)
def test_bad_shape_or_labels(values: list[float], labels: list[int]) -> None:
    with pytest.raises(ValidationError):
        CalibrationSample(probabilities=tuple(values), labels=tuple(labels))


@pytest.mark.parametrize(
    "field,value",
    [
        ("intercept", float("nan")),
        ("slope", 0),
        ("slope", -1),
        ("slope", float("inf")),
        ("epsilon", 1e-4),
        ("adapter_version", "other"),
    ],
)
def test_bad_parameters(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        SigmoidParameters.model_validate({"intercept": 0.0, "slope": 1.0, field: value})


def test_math_and_deterministic_fit() -> None:
    parameters = SigmoidParameters(intercept=0.0, slope=1.0)
    for p in (0.0, 0.1, 0.5, 0.9, 1.0):
        assert transform(parameters, p) == pytest.approx(min(1 - 1e-15, max(1e-15, p)), abs=1e-15)
    assert _estimate(synthetic_sample()) == _estimate(synthetic_sample())
    with pytest.raises(ValidationError):
        logit(-0.1)
    with pytest.raises(ValueError, match="SEPARATION"):
        _estimate(CalibrationSample(probabilities=(0.1, 0.9), labels=(0, 1)))


@pytest.mark.parametrize(
    "field,value",
    [
        ("subject", "RELIANCE"),
        ("subject", "Dhan"),
        ("purpose", "READ_ONLY_LEGACY"),
        ("configuration_fingerprint", "0" * 64),
    ],
)
def test_empirical_or_changed_request_denied(tmp_path: Path, field: str, value: object) -> None:
    store, grant = setup_fit(tmp_path / "store")
    request = ev.changed(service.synthetic_fit_request(grant.issued_at), **{field: value})
    with pytest.raises(ValueError, match="ONLY_COMPILED"):
        service.fit_synthetic_once(store, request, grant, synthetic_sample())
    assert not tuple(store.root.iterdir())


def test_relabelled_arbitrary_values_denied(tmp_path: Path) -> None:
    store, grant = setup_fit(tmp_path / "store")
    sample = ev.changed(synthetic_sample(), probabilities=(0.5,) * 60)
    with pytest.raises(ValueError, match="ONLY_COMPILED"):
        service.fit_synthetic_once(
            store, service.synthetic_fit_request(grant.issued_at), grant, sample
        )
    assert not tuple(store.root.iterdir())


@pytest.mark.parametrize(
    "field,value",
    [
        ("holdout_status", "CONSUMED"),
        ("holdout_status", "PROTECTED"),
        ("experiment_status", "CLOSED"),
        ("input_fingerprint", "0" * 64),
        ("custody_root_fingerprint", "0" * 64),
    ],
)
def test_authority_denials(tmp_path: Path, field: str, value: object) -> None:
    store, grant = setup_fit(tmp_path / "store")
    with pytest.raises(ValueError):
        service.fit_synthetic_once(
            store,
            service.synthetic_fit_request(grant.issued_at),
            ev.changed(grant, **{field: value}),
            synthetic_sample(),
        )
    assert not tuple(store.root.iterdir())


def test_failure_consumes_attempt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store, grant = setup_fit(tmp_path / "store")
    request = service.synthetic_fit_request(grant.issued_at)

    def timeout(*args: object, **kwargs: object) -> None:
        raise subprocess.TimeoutExpired("worker", 60)

    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(subprocess.TimeoutExpired):
        service.fit_synthetic_once(store, request, grant, synthetic_sample())
    with pytest.raises(ValueError, match="CONSUMED"):
        service.fit_synthetic_once(store, request, grant, synthetic_sample())
    assert len(tuple(store.root.glob("attempt-*.json"))) == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("raw_probability", 0.5),
        ("calibrated_probability", -1.0),
        ("calibrated_probability", 2.0),
        ("calibrated_probability", float("nan")),
        ("lineage", ()),
        ("output_semantics", "RAW"),
    ],
)
def test_bad_captured_output(
    captures: tuple[CalibratedCapture, ...], field: str, value: object
) -> None:
    with pytest.raises(ValidationError):
        ev.changed(captures[0], **{field: value})


@pytest.mark.parametrize("field", ["feature_schema", "source_training", "fit_request"])
def test_artifact_binding_mismatch(captures: tuple[CalibratedCapture, ...], field: str) -> None:
    capture = captures[0]
    artifact = ev.changed(capture.candidate.artifact, **{field: pin("wrong")})
    candidate = ev.changed(capture.candidate, artifact=artifact)
    with pytest.raises(ValidationError):
        ev.changed(capture, candidate=candidate)


def test_parameter_and_candidate_identity(captures: tuple[CalibratedCapture, ...]) -> None:
    capture = captures[0]
    parameters = ev.changed(capture.candidate.artifact.parameters, slope=0.8)
    artifact = ev.changed(capture.candidate.artifact, parameters=parameters)
    candidate = ev.changed(capture.candidate, artifact=artifact)
    assert candidate.candidate_id != capture.candidate.candidate_id
    with pytest.raises(ValidationError):
        ev.changed(capture, candidate=candidate)
    with pytest.raises(ValidationError):
        SigmoidParameters.model_validate({**parameters.model_dump(), "slope": 0.7})


def test_collections_clocks_and_frozen(captures: tuple[CalibratedCapture, ...]) -> None:
    capture = captures[0]
    assert isinstance(capture.model_dump(mode="json")["lineage"], list)
    assert isinstance(
        CalibratedCapture.model_validate(capture.model_dump(mode="json")).lineage, tuple
    )
    assert "+05:30" in capture.model_dump_json()
    utc = ev.changed(capture, created_at=capture.created_at.astimezone(UTC))
    assert utc == capture
    with pytest.raises(ValidationError):
        ev.changed(capture, created_at=capture.created_at.replace(tzinfo=None))
    with pytest.raises(ValidationError):
        capture.raw_probability = 0.9
    with pytest.raises(AttributeError):
        getattr(capture.lineage, "append")(pin("forbidden"))


def test_diagnostics() -> None:
    diagnostics = calibration_diagnostics(synthetic_sample())
    assert diagnostics.count == 60 and len(diagnostics.bins) == 10
    assert diagnostics.slope == pytest.approx(0.6365858283318643)
    assert diagnostics.offset_intercept == pytest.approx(0, abs=1e-12)
    assert sum(b.count for b in diagnostics.bins) == 60
    assert diagnostics.ece > 0 and not diagnostics.feedback_to_calibrator
    assert all(b.mean_probability is None for b in diagnostics.bins if b.support == "EMPTY")
    constant = calibration_diagnostics(
        CalibrationSample(probabilities=(0.5,) * 20, labels=(0, 1) * 10)
    )
    assert constant.slope is None and constant.slope_status == "NOT_ESTIMABLE"
    assert constant.bins[5].support == "SUPPORTED"
    endpoints = calibration_diagnostics(CalibrationSample(probabilities=(0.0, 1.0), labels=(0, 1)))
    assert endpoints.bins[0].count == endpoints.bins[9].count == 1
    assert endpoints.slope_status == "NOT_ESTIMABLE"


def test_evaluation_rejects_output_swap(captures: tuple[CalibratedCapture, ...]) -> None:
    supplied = eval_input(captures)
    first = supplied.forecast_sets[0]
    changed = ev.changed(
        first,
        observations=(
            ev.changed(first.observations[0], probability=captures[0].calibrated_probability),
            *first.observations[1:],
        ),
    )
    with pytest.raises(ValueError, match="OUTPUT_CONTRADICTION"):
        evaluate_calibrated(
            ev.changed(supplied, forecast_sets=(changed, supplied.forecast_sets[1])), captures
        )


def test_persistence_tamper_and_absence(
    fitted: tuple[service.SigmoidStore, SigmoidArtifact, TrainingBundle],
    captures: tuple[CalibratedCapture, ...],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, _, _ = fitted
    target = reference("sigmoidcapture", captures[0])
    assert (
        service.replay_sigmoid(store, target.model_copy(update={"fingerprint": "0" * 64})).status
        == "UNAVAILABLE"
    )
    original = store.resolve

    def tampered(ref: object) -> object:
        if ref == target:
            raise ValueError("CORRUPTED_BYTES")
        return original(ref)  # type: ignore[arg-type]

    monkeypatch.setattr(store, "resolve", tampered)
    assert service.replay_sigmoid(store, target).status == "MISMATCH"


def test_actual_store_rejects_malformed_record(tmp_path: Path) -> None:
    store = service.SigmoidStore(tmp_path / "store", create=True)
    sample = synthetic_sample()
    store.put("sigmoidsample", sample)
    path = store.root / f"sigmoidsample-{sample.fingerprint}.json"
    data = json.loads(path.read_text())
    data["labels"][0] = 0
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        store.resolve(reference("sigmoidsample", sample))


def test_baserate_raw_calibrated_common_population(captures: tuple[CalibratedCapture, ...]) -> None:
    supplied = eval_input(captures)
    raw_comparison = evaluate_calibrated(supplied, captures)
    # Existing native BaseRate on its authored 20-transition fixture. No new estimator.
    context, request = base_request()
    base = resolve_inference_forecaster(request.key, context).forecast(request)
    assert isinstance(base.output, BinaryProbabilityOutput)
    # Test-only normalized population: the fixed benchmark is explicitly projected
    # onto all synthetic slots, not asserted to be real per-slot issuance.
    first = ev.changed(
        supplied.request.participants[0],
        participant_id="participant:baserate",
        form="PRIMITIVE_FORECASTER",
        report_role="BENCHMARK",
        forecaster=base.request.key,
        forecast_or_composition=pin("synthetic-fixed-baserate-support"),
    )
    participants = (first, supplied.request.participants[1])
    pairing = ev.changed(
        supplied.request.pairing, participant_ids=tuple(p.participant_id for p in participants)
    )
    identity = ev.changed(supplied.request.identity, comparison_fingerprint=pairing.fingerprint)
    comparison_request = ev.changed(
        supplied.request, participants=participants, pairing=pairing, identity=identity
    )
    forecasts = ev.changed(
        supplied.forecast_sets[0],
        participant=first,
        observations=tuple(
            ev.changed(
                row,
                participant_id=first.participant_id,
                probability=base.output.probability,
                forecast_ref=pin("synthetic-fixed-baserate-support"),
            )
            for row in supplied.forecast_sets[0].observations
        ),
    )
    base_supplied = ev.changed(
        supplied, request=comparison_request, forecast_sets=(forecasts, supplied.forecast_sets[1])
    )
    base_comparison = evaluate_normalized(comparison_request, base_supplied)
    assert (
        base_comparison.coverage.paired_eligible.value
        == raw_comparison.coverage.paired_eligible.value
        == 60
    )
    assert base_supplied.ground_truth == supplied.ground_truth
    metrics = {
        m.metric_id: m.value
        for m in base_comparison.metrics.values
        if m.participant_id == first.participant_id
    }
    labels = tuple(cast(int, y.label) for y in supplied.ground_truth.observations)
    probability = base.output.probability
    assert metrics["BRIER"] == pytest.approx(sum((probability - y) ** 2 for y in labels) / 60)
    assert metrics["NATURAL_LOG_LOSS"] == pytest.approx(
        -sum(y * math.log(probability) + (1 - y) * math.log1p(-probability) for y in labels) / 60
    )


@pytest.mark.parametrize("field", ["forecaster", "forecast_or_composition", "form"])
def test_evaluation_identity_contradiction(
    captures: tuple[CalibratedCapture, ...], field: str
) -> None:
    supplied = eval_input(captures)
    calibrated = supplied.request.participants[1]
    wrong = ev.changed(calibrated, **{field: getattr(supplied.request.participants[0], field)})
    request = ev.changed(supplied.request, participants=(supplied.request.participants[0], wrong))
    data = ev.changed(
        supplied,
        request=request,
        forecast_sets=(
            supplied.forecast_sets[0],
            ev.changed(supplied.forecast_sets[1], participant=wrong),
        ),
    )
    with pytest.raises(ValueError, match="CALIBRATED_EVALUATION"):
        evaluate_calibrated(data, captures)


@pytest.mark.parametrize("field", ["source_forecaster", "source_model", "calibrator_id"])
def test_component_mismatch(captures: tuple[CalibratedCapture, ...], field: str) -> None:
    capture = captures[0]
    component = capture.candidate.artifact.component
    value = (
        component.source_forecaster.model_copy(update={"implementation_version": "other"})
        if field == "source_forecaster"
        else pin("wrong")
        if field == "source_model"
        else "calibrator:wrong"
    )
    artifact = ev.changed(
        capture.candidate.artifact, component=ev.changed(component, **{field: value})
    )
    candidate = ev.changed(capture.candidate, artifact=artifact)
    with pytest.raises(ValidationError):
        ev.changed(capture, candidate=candidate)
