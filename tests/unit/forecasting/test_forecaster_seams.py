"""FLC-1 synthetic adapter proof. No empirical data, fits, providers or holdout."""

from datetime import UTC, timedelta
from pathlib import Path
from typing import cast

import pytest
from pydantic import ValidationError

from tiaf.forecasting import forecaster_adapters as adapters
from tiaf.forecasting import forecaster_seams as seams
from tiaf.forecasting.contracts import BinaryProbabilityOutput, ForecastRequest
from tiaf.forecasting.enums import ForecastRealizationMode, ForecastStatus
from tiaf.forecasting.errors import ForecastIntegrityError
from tiaf.forecasting.forecaster_adapters import (
    BaseRateContext,
    LogisticContext,
    recorded_inference_replay,
    resolve_inference_forecaster,
)
from tiaf.forecasting.forecaster_seams import (
    CalibratableOutput,
    DiagnosticReport,
    DiagnosticRequest,
    ForecasterCapability,
    ForecasterKey,
    InferenceRequest,
    InferenceResult,
    TrainingRequest,
    TrainingResult,
    describe_forecaster,
    inference_descriptors,
)
from tiaf.forecasting.forecasters import HistoricalBaseRateForecaster
from tiaf.forecasting.identity import ForecastContract, canonical_json, semantic_fingerprint
from tiaf.forecasting.logistic_forecasts import ResearchForecastResult
from tiaf.forecasting.logistic_projection import ForecastProjection
from tiaf.forecasting.support import admit_support
from tiaf.learning.forecast_jobs import TrainingRun

from ._runtime_support import fixture
from .test_logistic_forecasts import handoff as handoff  # fixture: synthetic parameters, no fit
from .test_logistic_forecasts import projection as projection  # fixture
from .test_logistic_forecasts import qualification as qualification  # fixture
from .test_logistic_forecasts import records as records  # fixture


def base_request(
    *, simulated: bool = True, pattern: str = "baseline"
) -> tuple[BaseRateContext, InferenceRequest]:
    f = fixture(simulated=simulated, pattern=pattern)
    context = BaseRateContext(artifact=f.artifact, composition=f.config.composition)
    return context, InferenceRequest(
        key=inference_descriptors()[0].identity.key,
        native=f.request,
        context_ref=context.reference,
        computed_at=f.request.as_of + timedelta(seconds=1),
    )


@pytest.mark.parametrize("simulated", [True, False])
@pytest.mark.parametrize("pattern", ["baseline", "zero", "one"])
def test_baserate_identical_native_payload(simulated: bool, pattern: str) -> None:
    context, request = base_request(simulated=simulated, pattern=pattern)
    assert isinstance(request.native, ForecastRequest)
    legacy = HistoricalBaseRateForecaster().forecast(
        request.native, admit_support(context.artifact, request.native)
    )
    adapter = resolve_inference_forecaster(request.key, context)
    result = adapter.forecast(request)
    assert type(result) is InferenceResult
    assert canonical_json(result.native) == canonical_json(legacy)
    assert result.status == legacy.status and result.output == legacy.output
    assert result.artifacts.model is result.artifacts.scaler is result.artifacts.training is None
    assert result.request.native == request.native
    assert result.request.mode == request.native.realization_mode
    assert not adapter.descriptor().supports(ForecasterCapability.TRAINING)


def test_logistic_identical_native_results(
    projection: ForecastProjection,
    handoff: TrainingRun,
    records: tuple[ResearchForecastResult, ...],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = LogisticContext(source=projection, training=handoff)
    key = inference_descriptors()[1].identity.key
    adapter = resolve_inference_forecaster(key, context)
    original = canonical_json(handoff)
    selected = {r.request.fold_id: r for r in records if r.status == "GENERATED"}
    absences = {r.status: r for r in records if r.status != "GENERATED"}
    for native in (*selected.values(), *absences.values()):
        request = InferenceRequest(
            key=key,
            native=native.request,
            context_ref=context.reference,
            computed_at=native.computed_at,
        )
        result = adapter.forecast(request)
        assert type(result) is InferenceResult
        assert canonical_json(result.native) == canonical_json(native)
        assert result.artifacts.model is not None
        assert result.artifacts.model.fingerprint == native.request.composition.model_fingerprint
        assert request.mode is ForecastRealizationMode.SIMULATED_ISSUANCE
        assert request.as_of == native.request.origin.simulation_as_of
        assert request.information_cutoff == native.request.origin.information_cutoff
        assert request.target_id == native.request.target_id
        assert request.subject == native.request.subject
        assert result.status is (
            ForecastStatus.GENERATED if native.output else ForecastStatus.UNAVAILABLE
        )
        if native.output:
            assert result.output == native.output
        else:
            assert result.output.kind == "ABSENCE"
            assert cast(ResearchForecastResult, result.native).reasons == native.reasons
        with monkeypatch.context() as patch:

            def forbidden(*args: object, **kwargs: object) -> None:
                raise AssertionError("numeric inference during recorded replay")

            patch.setattr(adapters, "generate", forbidden)
            assert (
                recorded_inference_replay(canonical_json(result), semantic_fingerprint(result))
                == result
            )
    assert canonical_json(handoff) == original


def test_recorded_replay_does_not_infer(monkeypatch: pytest.MonkeyPatch) -> None:
    context, request = base_request()
    result = resolve_inference_forecaster(request.key, context).forecast(request)

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("execution during recorded replay")

    monkeypatch.setattr(HistoricalBaseRateForecaster, "forecast", forbidden)
    monkeypatch.setattr(adapters, "generate", forbidden)
    encoded = canonical_json(result)
    assert recorded_inference_replay(encoded, semantic_fingerprint(result)) == result
    with pytest.raises(ForecastIntegrityError, match="FINGERPRINT"):
        recorded_inference_replay(encoded, "0" * 64)
    with pytest.raises(ValueError):
        recorded_inference_replay(encoded[:-1] + ',"schema_version":"1.0"}', "0" * 64)


def test_capabilities_and_authority() -> None:
    base, learned = inference_descriptors()
    assert base.identity.role.value == "BENCHMARK"
    assert base.identity.lifecycle.value == "UNSPECIFIED"
    assert learned.identity.role.value == "CHALLENGER"
    assert learned.identity.lifecycle.value == "EXPERIMENTAL"
    for descriptor in (base, learned):
        assert descriptor.supports(ForecasterCapability.INFERENCE)
        assert descriptor.supports(ForecasterCapability.CALIBRATION_COMPATIBLE)
        assert not descriptor.supports(ForecasterCapability.TRAINING)
        assert not descriptor.supports(ForecasterCapability.DIAGNOSTICS)
        assert not descriptor.identity.activation_eligible
        for key, value in (("activation_eligible", True), ("approval", "APPROVED")):
            with pytest.raises(ValidationError):
                type(descriptor.identity).model_validate(
                    {**descriptor.identity.model_dump(), key: value}
                )
    assert learned.supports(ForecasterCapability.ARTIFACT_BACKED)
    assert not base.supports(ForecasterCapability.ARTIFACT_BACKED)


@pytest.mark.parametrize(
    "identity,version",
    [
        ("forecaster:unknown", "1.0"),
        ("forecaster:historical-base-rate", "2.0"),
        ("forecaster:logistic-regression", "latest"),
    ],
)
def test_exact_lookup_only(identity: str, version: str) -> None:
    with pytest.raises(ForecastIntegrityError, match="NOT_REGISTERED_EXACT_VERSION"):
        describe_forecaster(ForecasterKey(forecaster_id=identity, implementation_version=version))


def test_duplicate_lookup_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    legacy = HistoricalBaseRateForecaster().descriptor()
    monkeypatch.setattr(seams, "registered_forecasters", lambda: (legacy, legacy))
    with pytest.raises(ForecastIntegrityError, match="DUPLICATE"):
        inference_descriptors()


@pytest.mark.parametrize("path", ["../module", "https://module", "/tmp/code.py"])
def test_no_module_loading(path: str) -> None:
    with pytest.raises(ValidationError):
        ForecasterKey(forecaster_id=path, implementation_version="1.0")


def test_frozen_json_arrays_and_clocks() -> None:
    context, request = base_request()
    descriptor = describe_forecaster(request.key)
    assert isinstance(descriptor.model_dump(mode="json")["capabilities"], list)
    assert type(descriptor).model_validate(descriptor.model_dump(mode="json")) == descriptor
    with pytest.raises(ValidationError):
        descriptor.capabilities = ()
    assert not hasattr(descriptor.capabilities, "append")
    naive = request.computed_at.replace(tzinfo=None)
    with pytest.raises(ValidationError):
        InferenceRequest.model_validate({**request.model_dump(), "computed_at": naive})
    utc = request.computed_at.astimezone(UTC)
    rebuilt = InferenceRequest.model_validate({**request.model_dump(), "computed_at": utc})
    assert rebuilt == request
    assert rebuilt.model_dump(mode="json")["computed_at"].endswith("+05:30")
    result = resolve_inference_forecaster(request.key, context).forecast(rebuilt)
    assert InferenceResult.model_validate_json(result.model_dump_json()) == result


@pytest.mark.parametrize("partition", ["PROTECTED", "CONSUMED", "2025"])
def test_training_proposal_cannot_admit_holdout(partition: str) -> None:
    context, request = base_request()
    proposal = TrainingRequest(
        key=request.key,
        inputs=[context.reference],  # type: ignore[arg-type]
        configuration=context.artifact.configuration_ref,
        qualification=context.reference,
    )
    assert TrainingResult(request=proposal).status == "NOT_EXECUTED"
    with pytest.raises(ValidationError):
        TrainingRequest.model_validate({**proposal.model_dump(), "partition": partition})
    with pytest.raises(ValidationError):
        TrainingRequest.model_validate({**proposal.model_dump(), "status": "AUTHORIZED"})


def test_optional_seams_cannot_execute() -> None:
    context, request = base_request()
    compatible = CalibratableOutput(
        output=BinaryProbabilityOutput(probability=0.0),
        forecaster=describe_forecaster(request.key).identity,
        input_forecast=context.reference,
    )
    assert not compatible.fit_authorized and not compatible.apply_authorized
    assert not hasattr(compatible, "fit") and not hasattr(compatible, "apply")
    with pytest.raises(ValidationError):
        CalibratableOutput.model_validate({**compatible.model_dump(), "fit_authorized": True})

    class SyntheticPayload(ForecastContract):
        note: str

    report = DiagnosticReport[SyntheticPayload](
        request=DiagnosticRequest(
            key=request.key, artifact=context.reference, kind="diagnostic:synthetic"
        ),
        payload=SyntheticPayload(note="interface proof only"),
    )
    assert type(report).model_validate_json(report.model_dump_json()) == report


def test_wrong_context_and_tampered_descriptor() -> None:
    context, request = base_request()
    different, _ = base_request(pattern="one")
    with pytest.raises(ForecastIntegrityError, match="CONTEXT"):
        resolve_inference_forecaster(request.key, different).forecast(request)
    with pytest.raises(ForecastIntegrityError, match="FAMILY"):
        resolve_inference_forecaster(inference_descriptors()[1].identity.key, context)
    result = resolve_inference_forecaster(request.key, context).forecast(request)
    value = result.model_dump(mode="json")
    value["descriptor"]["identity"]["role"] = "CHALLENGER"
    with pytest.raises(ValidationError, match="LINEAGE"):
        InferenceResult.model_validate(value)


@pytest.mark.parametrize(
    "field,value",
    [
        ("target_id", "arbitrary.target"),
        ("target_version", "latest"),
    ],
)
def test_target_semantics_not_generalized(field: str, value: str) -> None:
    _, request = base_request()
    raw = request.model_dump(mode="json")
    raw["native"]["target"][field] = value
    with pytest.raises(ValidationError):
        InferenceRequest.model_validate(raw)


def test_context_missing_and_invalid_copy_rejected() -> None:
    context, request = base_request()
    with pytest.raises(ValidationError):
        BaseRateContext.model_validate({"composition": context.composition, "artifact": None})
    forged = request.model_copy(update={"computed_at": request.as_of - timedelta(seconds=1)})
    with pytest.raises(ValidationError, match="COMPUTATION_BEFORE"):
        resolve_inference_forecaster(request.key, context).forecast(forged)


def test_absent_baserate_support_is_not_negative_forecast() -> None:
    f = fixture(included=19)
    context = BaseRateContext(artifact=f.artifact, composition=f.config.composition)
    request = InferenceRequest(
        key=inference_descriptors()[0].identity.key,
        native=f.request,
        context_ref=context.reference,
        computed_at=f.request.as_of + timedelta(seconds=1),
    )
    result = resolve_inference_forecaster(request.key, context).forecast(request)
    assert result.status is ForecastStatus.UNAVAILABLE
    assert result.output.kind == "ABSENCE"


def test_new_modules_have_no_execution_imports() -> None:
    import ast

    for module in (adapters, seams):
        assert module.__file__ is not None
        tree = ast.parse(Path(module.__file__).read_text())
        imports = [
            node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        ] + [
            name.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for name in node.names
        ]
        assert not any(
            any(
                word in name
                for word in (
                    "sklearn",
                    "numpy",
                    "forecast_worker",
                    "forecast_training",
                    "provider",
                    "socket",
                )
            )
            for name in imports
        )
