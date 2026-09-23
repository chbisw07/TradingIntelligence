"""TEST-ONLY future family: no production registration, training or market data."""

import ast
from dataclasses import dataclass
from datetime import UTC, timedelta
from pathlib import Path
from typing import Literal, cast

import pytest
from pydantic import ValidationError

from tiaf.evaluation.forecast_normalization import evaluate_normalized
from tiaf.forecasting import inference_contracts as core
from tiaf.forecasting import lifecycle_replay as replay
from tiaf.forecasting.contracts import BinaryProbabilityOutput, ForecastAbsence
from tiaf.forecasting.enums import ForecastRealizationMode, ForecastReason, ForecastStatus
from tiaf.forecasting.errors import ForecastIntegrityError
from tiaf.forecasting.forecaster_adapters import (
    LogisticContext,
    NativeInferenceBridge,
    reference,
    resolve_inference_forecaster,
)
from tiaf.forecasting.forecaster_seams import InferenceRequest, inference_descriptors
from tiaf.forecasting.identity import (
    ForecastContract,
    LogicalId,
    canonical_json,
    semantic_fingerprint,
)
from tiaf.forecasting.inference_contracts import (
    ForecasterCapability,
    ForecasterKey,
    ForecasterLifecycle,
    ForecasterRole,
    InferenceAdapter,
    InferenceDescriptor,
    InferenceProvenance,
    LifecycleIdentity,
    NeutralInferenceRequest,
    NeutralInferenceResult,
    run_inference,
)
from tiaf.forecasting.lifecycle_provenance import NeutralInferenceCapture
from tiaf.forecasting.logistic_forecasts import ResearchForecastResult
from tiaf.forecasting.logistic_projection import ForecastProjection
from tiaf.learning.forecast_jobs import TrainingRun

from . import test_evaluation_normalization as ev
from .test_forecaster_seams import base_request
from .test_lifecycle_integration import branches, changed, replay_request
from .test_logistic_forecasts import handoff as handoff
from .test_logistic_forecasts import projection as projection
from .test_logistic_forecasts import qualification as qualification
from .test_logistic_forecasts import records as records


class SyntheticInput(ForecastContract):
    """Validated native state lives at this TEST adapter, not in the common codec."""

    recipe: Literal["constant-042-v1"] = "constant-042-v1"
    observation_id: LogicalId = "synthetic:observation-0"


@dataclass(frozen=True)
class SyntheticAdapter:
    native: SyntheticInput = SyntheticInput()

    def descriptor(self) -> InferenceDescriptor:
        return InferenceDescriptor(
            identity=LifecycleIdentity(
                key=ForecasterKey(forecaster_id="test:future-family", implementation_version="1.0"),
                family="SYNTHETIC_FUTURE_FAMILY",
                role=ForecasterRole.CHALLENGER,
                lifecycle=ForecasterLifecycle.EXPERIMENTAL,
            ),
            capabilities=(ForecasterCapability.INFERENCE, ForecasterCapability.REPLAYABLE),
            modes=(ForecastRealizationMode.SIMULATED_ISSUANCE,),
        )

    def request(self) -> NeutralInferenceRequest:
        native = SyntheticInput.model_validate(self.native)
        return NeutralInferenceRequest(
            key=self.descriptor().identity.key,
            observation_id=native.observation_id,
            target_id="synthetic:next-step-direction/1.0",
            subject="synthetic:asset",
            mode=ForecastRealizationMode.SIMULATED_ISSUANCE,
            information_cutoff=ev.AT,
            as_of=ev.AT,
            computed_at=ev.AT,
            context_ref=reference("test-context", native),
            input_ref=reference("test-input", native),
            feature_schema=reference("test-schema", native),
            experiment=reference("test-experiment", native),
        )

    def forecast(self, request: NeutralInferenceRequest) -> NeutralInferenceResult:
        if request != self.request():
            raise ValueError("TEST_NATIVE_INPUT_MISMATCH")
        return NeutralInferenceResult(
            request=request,
            descriptor=self.descriptor(),
            artifacts=InferenceProvenance(
                context=request.context_ref,
                composition=reference("test-composition", self.descriptor()),
            ),
            status=ForecastStatus.GENERATED,
            output=BinaryProbabilityOutput(probability=0.42),
        )


def test_future_family_same_common_runner_and_roundtrip() -> None:
    catalog = inference_descriptors()
    adapter: InferenceAdapter = SyntheticAdapter()
    result = run_inference(adapter.request(), adapter)
    assert result.output == BinaryProbabilityOutput(probability=0.42)
    assert result.descriptor.identity.family == "SYNTHETIC_FUTURE_FAMILY"
    assert not result.descriptor.identity.activation_eligible
    rebuilt = NeutralInferenceResult.model_validate_json(canonical_json(result))
    assert rebuilt == result
    assert semantic_fingerprint(rebuilt) == semantic_fingerprint(result)
    assert inference_descriptors() == catalog  # no registration or user-visible choice
    assert result.request.feature_schema and result.request.experiment


@pytest.mark.parametrize("simulated", [True, False])
@pytest.mark.parametrize("pattern", ["baseline", "zero", "one"])
def test_baserate_bridge_identical(simulated: bool, pattern: str) -> None:
    context, request = base_request(simulated=simulated, pattern=pattern)
    original = resolve_inference_forecaster(request.key, context).forecast(request)
    bridge = NativeInferenceBridge(request, context)
    result = run_inference(bridge.request(), bridge)
    assert result.output == original.output
    assert result.status == original.status
    assert result.descriptor == original.descriptor
    assert result.native_result == reference("native-result", original)
    assert result.request.input_ref == reference("native-request", request)
    assert result.artifacts.model_dump() == original.artifacts.model_dump()


def test_logistic_bridge_all_development_results_and_absences(
    projection: ForecastProjection,
    handoff: TrainingRun,
    records: tuple[ResearchForecastResult, ...],
) -> None:
    context = LogisticContext(source=projection, training=handoff)
    selected = {r.request.fold_id: r for r in records if r.status == "GENERATED"}
    absences = {r.status: r for r in records if r.status != "GENERATED"}
    for native in (*selected.values(), *absences.values()):
        request = InferenceRequest(
            key=inference_descriptors()[1].identity.key,
            native=native.request,
            context_ref=context.reference,
            computed_at=native.computed_at,
        )
        original = resolve_inference_forecaster(request.key, context).forecast(request)
        bridge = NativeInferenceBridge(request, context)
        result = run_inference(bridge.request(), bridge)
        assert result.output == original.output and result.status == original.status
        assert result.native_result == reference("native-result", original)
        assert result.artifacts.model_dump() == original.artifacts.model_dump()


@pytest.mark.parametrize(
    "damage",
    [
        None,
        "target_id",
        "subject",
        "mode",
        "observation_id",
        "reused_capture",
        "probability",
        "forecaster",
        "composition",
        "report_role",
        "form",
    ],
)
def test_neutral_capture_custody_replay_and_independent_evaluation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, damage: str | None
) -> None:
    adapter = SyntheticAdapter()
    result = run_inference(adapter.request(), adapter)
    store = replay.LifecycleStore(tmp_path / "corpus", create=True)
    captures: list[NeutralInferenceCapture] = []
    for observation_id in ev.OBSERVATIONS:
        bound = SyntheticAdapter(SyntheticInput(observation_id=observation_id))
        output = run_inference(bound.request(), bound)
        if not captures and damage in {"target_id", "subject", "mode", "observation_id"}:
            updates: dict[str, object] = {
                "target_id": "synthetic:wrong-target/1.0",
                "subject": "synthetic:wrong-asset",
                "mode": ForecastRealizationMode.ACTUAL_ISSUANCE,
                "observation_id": ev.OBSERVATIONS[1],
            }
            request = output.request.model_copy(update={str(damage): updates[str(damage)]})
            descriptor = output.descriptor
            if damage == "mode":
                descriptor = descriptor.model_copy(update={"modes": (request.mode,)})
            output = NeutralInferenceResult.model_validate(
                output.model_copy(
                    update={
                        "request": request,
                        "descriptor": descriptor,
                    }
                )
            )
        captures.append(NeutralInferenceCapture(result=output))
    refs = tuple(replay.capture_record(store, item) for item in captures)
    assert len(set(refs)) == len(ev.OBSERVATIONS)
    ref = refs[0]
    assert store.resolve(ref) == captures[0]
    q = ev.request(paired=False)
    participant = changed(
        q.participants[0],
        forecaster=result.request.key,
        forecast_or_composition=result.artifacts.composition,
        form="PRIMITIVE_FORECASTER",
        report_role="CHALLENGER",
    )
    if damage in {"forecaster", "composition", "report_role", "form"}:
        metadata: dict[str, object] = {
            "forecaster": ForecasterKey(forecaster_id="test:wrong", implementation_version="1.0"),
            "composition": reference("wrong", "wrong"),
            "report_role": "BENCHMARK",
            "form": "ARTIFACT_BACKED_FORECASTER",
        }
        field = "forecast_or_composition" if damage == "composition" else str(damage)
        participant = changed(participant, **{field: metadata[str(damage)]})
    q = changed(q, participants=(participant,))
    supplied = ev.evaluation_input(q)
    rows = tuple(
        changed(
            row,
            forecast_ref=refs[0] if damage == "reused_capture" else capture_ref,
            probability=0.43 if damage == "probability" else 0.42,
        )
        for row, capture_ref in zip(supplied.forecast_sets[0].observations, refs, strict=True)
    )
    forecast_set = changed(supplied.forecast_sets[0], observations=rows)
    supplied = changed(supplied, forecast_sets=(forecast_set,))
    replay.capture_record(store, supplied)
    if damage and damage != "report_role":
        with pytest.raises(ValueError, match="PROVENANCE_EVALUATION"):
            replay.capture_provenance(
                store,
                provenance_id="test:invalid-join",
                root=result.request.key,
                branches=branches(INFERENCE=refs, EVALUATION=(replay.reference(supplied),)),
                created_at=supplied.captured_at,
            )
        return
    graph = replay.capture_provenance(
        store,
        provenance_id="test:neutral-graph",
        root=result.request.key,
        branches=branches(INFERENCE=refs, EVALUATION=(replay.reference(supplied),)),
        created_at=supplied.captured_at,
    )
    before = {p.name: p.read_bytes() for p in store.root.iterdir()}

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("recorded replay cannot run inference or write")

    monkeypatch.setattr(SyntheticAdapter, "forecast", forbidden)
    monkeypatch.setattr(replay.LifecycleStore, "put", forbidden)
    verified = replay.replay_lifecycle(store, replay_request(graph, ref, "INFERENCE"))
    assert verified.status == "MATCH"
    assert verified.historical_as_of == result.request.as_of
    assert verified.identity_only  # references are NOT claims of stored native bytes
    unsupported = replay.replay_lifecycle(
        store, replay_request(graph, ref, "INFERENCE", "RECONSTRUCT_FROM_ARTIFACTS")
    )
    assert unsupported.status == "UNSUPPORTED"
    assert unsupported.reason == "replay:neutral-native-reconstruction-unsupported"
    assert before == {p.name: p.read_bytes() for p in store.root.iterdir()}
    score = evaluate_normalized(q, supplied)
    # Evaluation report labels are independent of the forecaster's lifecycle role.
    if damage == "report_role":
        assert participant.report_role == "BENCHMARK"
        assert result.descriptor.identity.role == ForecasterRole.CHALLENGER
    brier = next(metric for metric in score.metrics.values if metric.metric_id == "BRIER")
    assert brier.value == pytest.approx(0.2404)
    assert brier.evaluated_count == 5  # external labels, five distinct bound observations


@pytest.mark.parametrize("damage", ["missing", "tampered", "wrong-root", "backdated"])
def test_neutral_replay_rejects_missing_bytes_and_invalid_lineage(
    tmp_path: Path, damage: str
) -> None:
    adapter = SyntheticAdapter()
    result = run_inference(adapter.request(), adapter)
    store = replay.LifecycleStore(tmp_path / "corpus", create=True)
    ref = replay.capture_record(store, NeutralInferenceCapture(result=result))
    graph = replay.capture_provenance(
        store,
        provenance_id="test:graph",
        root=result.request.key,
        branches=branches(INFERENCE=(ref,)),
        created_at=ev.AT,
    )
    path = store.root / f"neutralinfercapture-{ref.fingerprint}.json"
    if damage == "missing":
        path.unlink()
    elif damage == "tampered":
        path.write_text(path.read_text().replace("0.42", "0.43"))
    else:
        update: dict[str, object] = (
            {"root": ForecasterKey(forecaster_id="test:wrong", implementation_version="1.0")}
            if damage == "wrong-root"
            else {"created_at": ev.AT - timedelta(seconds=1)}
        )
        graph = changed(graph, **update)
        store.put("provenance", graph)
    assert replay.replay_lifecycle(store, replay_request(graph, ref, "INFERENCE")).status == (
        "UNAVAILABLE" if damage == "missing" else "MISMATCH"
    )


def test_unsupported_capability_and_realization_mode_are_not_execution_authority() -> None:
    class NoInference(SyntheticAdapter):
        def descriptor(self) -> InferenceDescriptor:
            return super().descriptor().model_copy(update={"capabilities": ()})

        def forecast(self, request: NeutralInferenceRequest) -> NeutralInferenceResult:
            raise AssertionError("must reject before execution")

    adapter = NoInference()
    with pytest.raises(ForecastIntegrityError, match="ADAPTER_REQUEST"):
        run_inference(adapter.request(), adapter)
    result = run_inference(SyntheticAdapter().request(), SyntheticAdapter())
    request = result.request.model_copy(update={"mode": ForecastRealizationMode.ACTUAL_ISSUANCE})
    with pytest.raises(ValidationError, match="LINEAGE"):
        NeutralInferenceResult.model_validate(result.model_copy(update={"request": request}))


@pytest.mark.parametrize("value", [-0.01, 1.01, float("nan"), float("inf"), True, "0.42"])
def test_bad_probability_rejected_even_unvalidated_copy(value: object) -> None:
    adapter = SyntheticAdapter()
    original = run_inference(adapter.request(), adapter)
    bad_output = original.output.model_copy(update={"probability": value})
    with pytest.raises(ValidationError):
        NeutralInferenceResult.model_validate(original.model_copy(update={"output": bad_output}))


@pytest.mark.parametrize(
    "field,value",
    [
        ("family", ""),
        ("family", "../family"),
        ("family", "https://family"),
        ("family", "A" * 65),
        ("activation_eligible", True),
        ("approval", "APPROVED"),
        ("key", None),
        ("unknown_metadata", "opaque"),
    ],
)
def test_invalid_identity_metadata(field: str, value: object) -> None:
    raw = SyntheticAdapter().descriptor().identity.model_dump()
    with pytest.raises(ValidationError):
        LifecycleIdentity.model_validate({**raw, field: value})


@pytest.mark.parametrize(
    "field,value",
    [
        ("capabilities", ["UNSUPPORTED_EXTENSION"]),
        ("capabilities", ["INFERENCE", "INFERENCE"]),
        ("modes", []),
        ("identity", None),
        ("extension_payload", {}),
    ],
)
def test_invalid_descriptor_metadata(field: str, value: object) -> None:
    raw = SyntheticAdapter().descriptor().model_dump()
    with pytest.raises(ValidationError):
        InferenceDescriptor.model_validate({**raw, field: value})


def test_bad_adapter_and_inconsistent_declared_result() -> None:
    adapter = SyntheticAdapter()
    with pytest.raises(ForecastIntegrityError, match="INVALID_INFERENCE_ADAPTER"):
        run_inference(adapter.request(), cast(InferenceAdapter, object()))

    class LyingAdapter(SyntheticAdapter):
        def forecast(self, request: NeutralInferenceRequest) -> NeutralInferenceResult:
            result = super().forecast(request)
            identity = self.descriptor().identity.model_copy(update={"family": "DIFFERENT"})
            return result.model_copy(
                update={"descriptor": self.descriptor().model_copy(update={"identity": identity})}
            )

    liar = LyingAdapter()
    with pytest.raises(ForecastIntegrityError, match="ADAPTER_RESULT"):
        run_inference(liar.request(), liar)


@pytest.mark.parametrize("field", ["key", "input_ref", "context_ref", "target_id", "subject"])
def test_wrong_bound_request_before_execution(field: str) -> None:
    adapter = SyntheticAdapter()
    raw = adapter.request().model_dump()
    replacements: dict[str, object] = {
        "key": {"forecaster_id": "test:other", "implementation_version": "1.0"},
        "input_ref": reference("wrong", "wrong"),
        "context_ref": reference("wrong", "wrong"),
        "target_id": "test:other",
        "subject": "test:other",
    }
    request = NeutralInferenceRequest.model_validate({**raw, field: replacements[field]})
    with pytest.raises(ForecastIntegrityError, match="ADAPTER_REQUEST"):
        run_inference(request, adapter)


def test_clocks_immutability_absence_and_artifact_validation() -> None:
    adapter = SyntheticAdapter()
    result = run_inference(adapter.request(), adapter)
    raw = result.request.model_dump()
    for at in (ev.AT.replace(tzinfo=None), ev.AT - timedelta(seconds=1)):
        with pytest.raises(ValidationError):
            NeutralInferenceRequest.model_validate({**raw, "computed_at": at})
    request = NeutralInferenceRequest.model_validate({**raw, "computed_at": ev.AT.astimezone(UTC)})
    assert request.model_dump(mode="json")["computed_at"].endswith("+05:30")
    with pytest.raises(ValidationError):
        result.status = ForecastStatus.UNAVAILABLE
    assert isinstance(result.descriptor.model_dump(mode="json")["capabilities"], list)
    assert not hasattr(result.descriptor.capabilities, "append")
    with pytest.raises(ValidationError, match="OUTPUT_STATUS"):
        NeutralInferenceResult.model_validate(
            result.model_copy(update={"status": ForecastStatus.FAILED})
        )
    absence = ForecastAbsence(reasons=(ForecastReason.EVIDENCE_MISSING,))
    absent = NeutralInferenceResult.model_validate(
        result.model_copy(
            update={
                "status": ForecastStatus.UNAVAILABLE,
                "output": absence,
            }
        )
    )
    assert absent.output == absence
    learned = result.descriptor.model_copy(
        update={
            "capabilities": (*result.descriptor.capabilities, ForecasterCapability.ARTIFACT_BACKED),
        }
    )
    with pytest.raises(ValidationError, match="MODEL_REFERENCE"):
        NeutralInferenceResult.model_validate(result.model_copy(update={"descriptor": learned}))
    # A future family need not invent a scaler merely to satisfy a Logistic triplet.
    provenance = result.artifacts.model_copy(update={"model": reference("test-model", "model")})
    assert (
        NeutralInferenceResult.model_validate(
            result.model_copy(
                update={
                    "descriptor": learned,
                    "artifacts": provenance,
                }
            )
        ).artifacts.scaler
        is None
    )


def test_common_core_has_no_family_import_branch_or_opaque_payload() -> None:
    assert core.__file__
    source = Path(core.__file__).read_text()
    tree = ast.parse(source)
    forbidden = {
        "ForecastRequest",
        "ResearchForecastRequest",
        "ResearchForecastResult",
        "BaseRateContext",
        "LogisticContext",
        "Any",
        "GenerationPayload",
    }
    assert not any(isinstance(n, ast.Name) and n.id in forbidden for n in ast.walk(tree))
    assert not any(
        isinstance(n, ast.ImportFrom)
        and any(
            s in (n.module or "")
            for s in ("logistic", "forecaster_legacy", "forecaster_adapters", "forecasters")
        )
        for n in ast.walk(tree)
    )
    assert "test:future-family" not in source
    assert "SYNTHETIC_FUTURE_FAMILY" not in source
