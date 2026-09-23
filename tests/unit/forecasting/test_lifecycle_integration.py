"""FLC-7 synthetic integration and adversarial offline closure tests."""

import builtins
import hashlib
import json
import shutil
import socket
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tiaf.evaluation import forecast_normalization as evaluation
from tiaf.evaluation.forecast_normalization_contracts import (
    NormalizedEvaluationLedger,
)
from tiaf.forecasting import lifecycle_replay as service
from tiaf.forecasting.forecaster_adapters import resolve_inference_forecaster
from tiaf.forecasting.forecaster_seams import ForecasterKey
from tiaf.forecasting.identity import ArtifactReference, canonical_json
from tiaf.forecasting.lifecycle_provenance import (
    ArtifactPrediction,
    InferenceCapture,
    InferenceContext,
    LineageBranch,
    ProvenanceEdge,
    ProvenanceNode,
    ProvenanceRecord,
    Relation,
    ReplayRequest,
    Stage,
)
from tiaf.forecasting.logistic_store import ResearchForecastStore
from tiaf.learning import calibration
from tiaf.learning.forecast_artifacts import SealedResearch
from tiaf.learning.forecaster_custody import CustodyClass, ForecasterStore, restore_predictor
from tiaf.learning.forecaster_diagnostics import (
    DiagnosticKind,
    DiagnosticRequest,
    generate_diagnostic,
)
from tiaf.learning.forecaster_lifecycle import ApprovalDecision
from tiaf.learning.forecaster_training import TrainingBundle
from tiaf.learning.optimization import OptimizationStore
from tiaf.learning.optimization_contracts import OptimizationResult

from . import test_calibration as cal
from . import test_evaluation_normalization as ev
from .test_forecaster_lifecycle import pin
from .test_forecaster_lifecycle import trained as trained
from .test_forecaster_seams import base_request
from .test_optimization import campaign as campaign


def changed[T: SealedResearch](value: T, **updates: Any) -> T:
    return type(value).model_validate({**value.model_dump(), **updates, "fingerprint": None})


def branches(**items: tuple[ArtifactReference, ...]) -> tuple[LineageBranch, ...]:
    return tuple(
        LineageBranch(
            stage=stage,
            references=items.get(stage.value, ()),
            absence=None if items.get(stage.value) else "NOT_REQUESTED",
        )
        for stage in Stage
    )


@pytest.fixture(scope="module")
def integrated(
    trained: tuple[ForecasterStore, TrainingBundle],
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]]:
    original, bundle = trained
    root = tmp_path_factory.mktemp("flc7") / "corpus"
    store = service.LifecycleStore(root, create=True)
    # Copy through the one existing store's codecs; no re-fit of the existing job.
    for path in original.root.iterdir():
        kind, fp = path.stem.split("-", 1)
        store.put(kind, original.get(kind, fp))
    service.capture_record(store, bundle)
    at = bundle.execution.completed_at + timedelta(seconds=1)
    model = bundle.result.model_identity
    scaler = bundle.result.preprocessor_identity
    assert model and scaler
    predictor = restore_predictor(store, service.reference(bundle))
    probes = tuple(
        ArtifactPrediction(
            bundle=service.reference(bundle),
            forecaster=model.forecaster,
            model=model.artifact,
            scaler=scaler.artifact,
            features=(float(i), 0.0, 1.0, 2.0, 3.0),
            output=predictor.predict((float(i), 0.0, 1.0, 2.0, 3.0)),
            computed_at=at,
        )
        for i in range(5)
    )
    for probe in probes:
        service.capture_record(store, probe)
    diag = generate_diagnostic(
        store,
        DiagnosticRequest(
            diagnostic_request_id="flc7:coefficients",
            forecaster=model.forecaster,
            artifact_reference=model.artifact,
            model_identity_reference=service.reference(model),
            kind=DiagnosticKind.LOGISTIC_COEFFICIENTS,
            subject=model.subject,
            target_id=model.target_id,
            evidence_references=(model.artifact,),
            created_at=at,
        ),
    )
    q = ev.request(paired=False)
    participant = changed(
        q.participants[0], forecaster=model.forecaster, forecast_or_composition=model.artifact
    )
    q = changed(q, participants=(participant,))
    supplied = ev.evaluation_input(q)
    q = changed(q, created_at=at)
    rows = tuple(
        changed(row, forecast_ref=service.reference(probe), probability=probe.output.probability)
        for row, probe in zip(supplied.forecast_sets[0].observations, probes, strict=True)
    )
    forecast_set = changed(supplied.forecast_sets[0], participant=participant, observations=rows)
    supplied = changed(supplied, request=q, forecast_sets=(forecast_set,), captured_at=at)
    # External Outcome Journal remains the source; integration does not label.
    service.capture_record(store, supplied)
    ledger_ref = evaluation.persist_normalized_evaluation(store, supplied)
    ledger = store.resolve(ledger_ref)
    assert isinstance(ledger, NormalizedEvaluationLedger)
    service.capture_record(store, store.resolve(ledger.result))
    # Optional calibration is FLC-5's authored reference branch, not this learned probe.
    source, artifact = cal.source(), cal.artifact()
    service.capture_record(store, source)
    calibration.persist_reference_artifact(store, artifact)
    calibrated = calibration.apply_calibration(store, cal.request(source, artifact))
    service.capture_record(store, calibrated)
    approval = ApprovalDecision(
        approval_id="flc7:external-held",
        request_reference=pin("external-request"),
        subject_reference=service.reference(model),
        authority_reference=pin("reviewer-authority"),
        reviewer="reviewer:synthetic",
        decision="HELD",
        scope="scope:engineering-only",
        evidence_references=(ledger.result,),
        reason="Engineering evidence grants no activation",
        created_at=at,
        expires_at=at + timedelta(days=1),
    )
    service.capture_record(store, approval)
    refs = {
        "INFERENCE": service.reference(probes[0]),
        "TRAINING_ARTIFACTS": service.reference(bundle),
        "DIAGNOSTICS": service.reference(diag),
        "EVALUATION": ledger_ref,
        "CALIBRATION": service.reference(calibrated),
    }
    graph = service.capture_provenance(
        store,
        provenance_id="flc7:synthetic-reference",
        root=model.forecaster,
        branches=branches(
            TRAINING=(service.reference(bundle),),
            MODEL=(model.artifact,),
            PREPROCESSOR=(scaler.artifact,),
            INFERENCE=tuple(service.reference(p) for p in probes),
            DIAGNOSTICS=(service.reference(diag),),
            CALIBRATION=(service.reference(calibrated),),
            EVALUATION=(ledger_ref,),
            LIFECYCLE=(service.reference(approval),),
        ),
        created_at=at,
    )
    refs["PROVENANCE"] = service.reference(graph)
    return root, graph, refs


def replay_request(
    graph: ProvenanceRecord,
    ref: ArtifactReference,
    kind: str,
    mode: str = "RECORDED_VERIFY",
    **updates: Any,
) -> ReplayRequest:
    return ReplayRequest.model_validate(
        {
            "request_id": "flc7:replay",
            "provenance": service.reference(graph),
            "target": ref,
            "target_kind": kind,
            "mode": mode,
            "checked_at": graph.created_at + timedelta(seconds=1),
            **updates,
        }
    )


@pytest.mark.parametrize(
    "kind",
    ["INFERENCE", "TRAINING_ARTIFACTS", "DIAGNOSTICS", "CALIBRATION", "EVALUATION", "PROVENANCE"],
)
@pytest.mark.parametrize("mode", ["RECORDED_VERIFY", "RECONSTRUCT_FROM_ARTIFACTS"])
def test_end_to_end_offline_replay(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]],
    kind: str,
    mode: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, graph, refs = integrated
    before = {p.name: p.read_bytes() for p in root.iterdir()}
    original_import = builtins.__import__

    def no_ml(name: str, *args: Any, **kwargs: Any) -> Any:
        if name.split(".")[0] in {"sklearn", "numpy", "scipy", "joblib", "threadpoolctl"}:
            pytest.fail("ML import during offline replay")
        return original_import(name, *args, **kwargs)

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("offline replay attempted external or mutation operation")

    monkeypatch.setattr(builtins, "__import__", no_ml)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(service.LifecycleStore, "put", forbidden)
    if mode == "RECORDED_VERIFY":
        monkeypatch.setattr(service, "_reconstruct", forbidden)
        monkeypatch.setattr(evaluation, "evaluate_normalized", forbidden)
    result = service.replay_lifecycle(
        service.LifecycleStore(root), replay_request(graph, refs[kind], kind, mode)
    )
    assert result.status == "MATCH", result
    assert not result.grants_reuse and result.lifecycle_effect == "NONE"
    assert result.identity_only and result.artifact_reads <= 512
    assert before == {p.name: p.read_bytes() for p in root.iterdir()}


def test_component_observability(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]],
) -> None:
    _, graph, _ = integrated
    kinds = {n.reference.artifact_id for n in graph.nodes}
    assert {
        "flc:request",
        "flc:execution",
        "flc:result",
        "flc:model",
        "flc:scaler",
        "flc:diagnostic",
        "flc:calartifact",
        "flc:calcomposition",
        "flc6:evalrequest",
        "flc6:evalmetrics",
        "flc6:evalstatistics",
        "flc7:externaltruth",
        "flc:approval",
    } <= kinds
    assert {
        Relation.TRAINED_FROM,
        Relation.DIAGNOSES,
        Relation.CALIBRATED_FROM,
        Relation.EVALUATED_AGAINST,
        Relation.APPROVAL_REFERENCES,
    } <= {e.relation for e in graph.edges}
    assert (
        next(b for b in graph.branches if b.stage == Stage.OPTIMIZATION).absence == "NOT_REQUESTED"
    )


@pytest.mark.parametrize(
    "kind",
    [
        "request",
        "result",
        "model",
        "scaler",
        "predictionprobe",
        "diagnostic",
        "calartifact",
        "calresult",
        "evalrequest",
        "evalresult",
        "provenance",
    ],
)
def test_tamper_matrix(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]],
    tmp_path: Path,
    kind: str,
) -> None:
    root, graph, refs = integrated
    copied = tmp_path / "tamper"
    shutil.copytree(root, copied)
    path = next(copied.glob(f"{kind}-*.json"))
    payload = json.loads(path.read_text())
    payload["fingerprint"] = "0" * 64
    path.write_text(json.dumps(payload))
    result = service.replay_lifecycle(
        service.LifecycleStore(copied), replay_request(graph, refs["PROVENANCE"], "PROVENANCE")
    )
    assert result.status == "MISMATCH"
    assert next(root.glob(f"{kind}-*.json")).read_bytes() != path.read_bytes()


@pytest.mark.parametrize("kind", ["model", "scaler", "calartifact", "externaltruth", "evalinput"])
def test_missing_required_artifacts(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]],
    tmp_path: Path,
    kind: str,
) -> None:
    root, graph, refs = integrated
    copied = tmp_path / "missing"
    shutil.copytree(root, copied)
    next(copied.glob(f"{kind}-*.json")).unlink()
    result = service.replay_lifecycle(
        service.LifecycleStore(copied), replay_request(graph, refs["PROVENANCE"], "PROVENANCE")
    )
    assert result.status == "UNAVAILABLE"


def test_graph_identity_and_clocks(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]],
) -> None:
    _, graph, _ = integrated
    reordered = ProvenanceRecord.model_validate(
        {
            **graph.model_dump(),
            "nodes": tuple(reversed(graph.nodes)),
            "edges": tuple(reversed(graph.edges)),
            "branches": tuple(reversed(graph.branches)),
        }
    )
    assert reordered == graph
    assert ProvenanceRecord.model_validate_json(canonical_json(graph)) == graph
    assert changed(graph, created_at=graph.created_at.astimezone(UTC)) == graph
    later = changed(graph, created_at=graph.created_at + timedelta(days=1))
    assert later.fingerprint != graph.fingerprint
    assert later.structure_fingerprint == graph.structure_fingerprint
    assert "+05:30" in canonical_json(graph)
    assert isinstance(graph.model_dump(mode="json")["nodes"], list)
    assert not hasattr(graph.nodes, "append")
    with pytest.raises(ValidationError):
        graph.created_at = datetime.now(UTC)
    with pytest.raises(ValidationError):
        changed(graph, created_at=graph.created_at.replace(tzinfo=None))


@pytest.mark.parametrize(
    "field",
    [
        "grants_training",
        "grants_calibration_fit",
        "grants_approval",
        "grants_promotion",
        "grants_activation",
        "grants_unseen_status",
        "grants_holdout_execution",
    ],
)
def test_provenance_never_authorizes(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]], field: str
) -> None:
    with pytest.raises(ValidationError):
        changed(integrated[1], **{field: True})


def test_cycles_and_bounds(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]],
) -> None:
    _, graph, _ = integrated
    edge = graph.edges[0]
    with pytest.raises(ValidationError, match="CYCLE"):
        changed(
            graph,
            edges=(
                *graph.edges,
                ProvenanceEdge(source=edge.target, target=edge.source, relation=Relation.USES),
            ),
        )
    with pytest.raises(ValidationError):
        changed(graph, nodes=graph.nodes * 257)
    with pytest.raises(ValidationError):
        changed(graph, edges=graph.edges * 1025)
    with pytest.raises(ValidationError):
        changed(edge, relation="EXECUTE_SCRIPT")


def test_budget_and_unknown_version(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]],
) -> None:
    root, graph, refs = integrated
    request = replay_request(graph, refs["PROVENANCE"], "PROVENANCE", max_artifact_reads=1)
    result = service.replay_lifecycle(service.LifecycleStore(root), request)
    assert result.status == "MISMATCH" and result.artifact_reads == 1
    bad_ref = refs["PROVENANCE"].model_copy(update={"artifact_version": "unknown"})
    result = service.replay_lifecycle(
        service.LifecycleStore(root),
        replay_request(graph, refs["PROVENANCE"], "PROVENANCE", provenance=bad_ref),
    )
    assert result.status == "MISMATCH"


def test_immutable_existing_store(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]], tmp_path: Path
) -> None:
    root, graph, _ = integrated
    assert service.LifecycleStore.put is ResearchForecastStore.put
    assert service.LifecycleStore.get is ResearchForecastStore.get
    store = service.LifecycleStore(tmp_path / "duplicates", create=True)
    store.put("provenance", graph)
    first = {p.name: p.read_bytes() for p in store.root.iterdir()}
    store.put("provenance", graph)
    assert first == {p.name: p.read_bytes() for p in store.root.iterdir()}
    later = changed(graph, created_at=graph.created_at + timedelta(seconds=1))
    store.put("provenance", later)
    assert len(list(store.root.iterdir())) == 2
    with pytest.raises(ValueError):
        store.put("provenance", graph.model_copy(update={"grants_activation": True}))
    assert service.LifecycleStore(root).resolve(service.reference(graph)) == graph


@pytest.mark.parametrize("simulated", [True, False])
def test_native_baserate_replay_no_training(tmp_path: Path, simulated: bool) -> None:
    store = service.LifecycleStore(tmp_path / "base", create=True)
    context, request = base_request(simulated=simulated)
    native = resolve_inference_forecaster(request.key, context).forecast(request)
    original = canonical_json(native)
    context_ref = service.capture_record(store, InferenceContext(native=context))
    captured = InferenceCapture(result=native, context=context_ref)
    ref = service.capture_record(store, captured)
    graph = service.capture_provenance(
        store,
        provenance_id="flc7:base",
        root=request.key,
        branches=branches(INFERENCE=(ref,)),
        created_at=request.computed_at,
    )
    for mode in ("RECORDED_VERIFY", "RECONSTRUCT_FROM_ARTIFACTS"):
        result = service.replay_lifecycle(store, replay_request(graph, ref, "INFERENCE", mode))
        assert result.status == "MATCH", result
        assert result.realization_mode == request.mode
        assert result.historical_as_of == request.as_of
    assert canonical_json(native) == original
    wrong_root = changed(
        graph,
        root=ForecasterKey(forecaster_id="forecaster:unrelated", implementation_version="1.0"),
    )
    store.put("provenance", wrong_root)
    assert (
        service.replay_lifecycle(store, replay_request(wrong_root, ref, "INFERENCE")).status
        == "MISMATCH"
    )
    wrong = changed(graph, created_at=request.computed_at - timedelta(seconds=1))
    store.put("provenance", wrong)
    assert (
        service.replay_lifecycle(store, replay_request(wrong, ref, "INFERENCE")).status
        == "MISMATCH"
    )
    (store.root / f"infercontext-{context_ref.fingerprint}.json").unlink()
    assert (
        service.replay_lifecycle(store, replay_request(graph, ref, "INFERENCE")).status
        == "UNAVAILABLE"
    )


def test_consumed_legacy_view_is_readonly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    protocol, execution, result, ledger = ev._legacy_records()
    before = tuple(canonical_json(v) for v in (protocol, execution, result, ledger))
    view = evaluation.adapt_legacy_ff1_final(protocol, execution, result, ledger)
    store = service.LifecycleStore(tmp_path / "legacy", create=True)
    ref = service.capture_record(store, view)
    graph = service.capture_provenance(
        store,
        provenance_id="flc7:legacy-ff1",
        root=ForecasterKey(
            forecaster_id="forecaster:logistic-regression", implementation_version="1.0"
        ),
        branches=branches(EVALUATION=(ref,)),
        created_at=view.created_at,
        consumed=True,
    )
    monkeypatch.setattr(service, "_reconstruct", lambda *a: pytest.fail("consumed recomputation"))
    assert (
        service.replay_lifecycle(store, replay_request(graph, ref, "EVALUATION")).status == "MATCH"
    )
    assert (
        service.replay_lifecycle(
            store, replay_request(graph, ref, "EVALUATION", "RECONSTRUCT_FROM_ARTIFACTS")
        ).status
        == "UNSUPPORTED"
    )
    changed_graph = changed(graph, evidence_state="SYNTHETIC_ENGINEERING")
    store.put("provenance", changed_graph)
    assert (
        service.replay_lifecycle(store, replay_request(changed_graph, ref, "EVALUATION")).status
        == "MISMATCH"
    )
    assert before == tuple(canonical_json(v) for v in (protocol, execution, result, ledger))


def test_identity_does_not_archive_private_bytes(tmp_path: Path) -> None:
    store = service.LifecycleStore(tmp_path / "private", create=True)
    ref = pin("private-dataset")
    graph = ProvenanceRecord(
        provenance_id="flc7:private",
        root=ForecasterKey(
            forecaster_id="forecaster:historical-base-rate", implementation_version="1.0"
        ),
        branches=branches(QUALIFICATION=(ref,)),
        nodes=(
            ProvenanceNode(
                reference=ref, custody=CustodyClass.PRIVATE_LICENSED_DATA, closure="IDENTITY_ONLY"
            ),
        ),
        created_at=cal.AT,
        evidence_state="SYNTHETIC_ENGINEERING",
    )
    store.put("provenance", graph)
    result = service.replay_lifecycle(store, replay_request(graph, ref, "PROVENANCE"))
    assert result.status == "UNAVAILABLE" and not result.grants_reuse
    graph_check = service.replay_lifecycle(
        store, replay_request(graph, service.reference(graph), "PROVENANCE")
    )
    assert graph_check.status == "MATCH" and graph_check.identity_only == (ref,)


def test_optimization_branch_uses_recorded_selection(
    campaign: tuple[OptimizationStore, OptimizationResult],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old, result = campaign
    store = service.LifecycleStore(tmp_path / "optimization", create=True)
    for path in old.root.iterdir():
        kind, fp = path.stem.split("-", 1)
        service.capture_record(store, old.get(kind, fp))
    selected = result.selected_model_identity
    assert selected is not None
    graph = service.capture_provenance(
        store,
        provenance_id="flc7:optimization",
        root=selected.forecaster,
        branches=branches(OPTIMIZATION=(service.reference(result),)),
        created_at=datetime.now(UTC),
    )
    assert Relation.SELECTED_FROM in {edge.relation for edge in graph.edges}
    before = canonical_json(result)
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: pytest.fail("refit"))
    from tiaf.evaluation import optimization_evaluation

    monkeypatch.setattr(
        optimization_evaluation, "evaluate_trial", lambda *a, **kw: pytest.fail("new evaluation")
    )
    for mode in ("RECORDED_VERIFY", "RECONSTRUCT_FROM_ARTIFACTS"):
        replayed = service.replay_lifecycle(
            store, replay_request(graph, service.reference(result), "OPTIMIZATION", mode)
        )
        assert replayed.status == "MATCH", replayed
    assert canonical_json(result) == before


def test_resealed_wrong_edge_and_identity_downgrade(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]],
    tmp_path: Path,
) -> None:
    root, graph, refs = integrated
    copied = tmp_path / "resealed"
    shutil.copytree(root, copied)
    # Store opened read-only; create a separate immutable candidate record directly
    # through its original writable instance profile for this adversarial test.
    store = service.LifecycleStore(copied)
    store.writable = True
    first = graph.edges[0]
    altered = changed(
        first,
        relation=Relation.DERIVED_FROM
        if first.relation != Relation.DERIVED_FROM
        else Relation.USES,
    )
    wrong = changed(graph, edges=(altered, *graph.edges[1:]))
    store.put("provenance", wrong)
    assert (
        service.replay_lifecycle(
            store, replay_request(wrong, service.reference(wrong), "PROVENANCE")
        ).status
        == "MISMATCH"
    )
    node = next(n for n in graph.nodes if n.closure == "REQUIRED_BYTES")
    wrong = changed(
        graph,
        nodes=tuple(changed(n, closure="IDENTITY_ONLY") if n == node else n for n in graph.nodes),
    )
    store.put("provenance", wrong)
    assert (
        service.replay_lifecycle(
            store, replay_request(wrong, service.reference(wrong), "PROVENANCE")
        ).status
        == "MISMATCH"
    )


def test_backdating_and_wrong_root_rejected(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]],
    tmp_path: Path,
) -> None:
    root, graph, _ = integrated
    copied = tmp_path / "backdated"
    shutil.copytree(root, copied)
    store = service.LifecycleStore(copied)
    store.writable = True
    for wrong in (
        changed(graph, created_at=graph.created_at - timedelta(days=1)),
        changed(
            graph,
            root=ForecasterKey(forecaster_id="forecaster:other", implementation_version="1.0"),
        ),
    ):
        store.put("provenance", wrong)
        assert (
            service.replay_lifecycle(
                store, replay_request(wrong, service.reference(wrong), "PROVENANCE")
            ).status
            == "MISMATCH"
        )


def test_unmounted_corpus_is_unavailable(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]],
    tmp_path: Path,
) -> None:
    _, graph, refs = integrated
    store = service.LifecycleStore(tmp_path / "unmounted", create=True)
    store.root.rmdir()
    result = service.replay_lifecycle(
        store, replay_request(graph, refs["PROVENANCE"], "PROVENANCE")
    )
    assert result.status == "UNAVAILABLE" and result.artifact_reads == 0


def test_resealed_forecast_probability_cannot_break_evaluation_link(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]],
    tmp_path: Path,
) -> None:
    root, graph, refs = integrated
    copied = tmp_path / "wrong-probability"
    shutil.copytree(root, copied)
    store = service.LifecycleStore(copied)
    store.writable = True
    from tiaf.evaluation.forecast_normalization_contracts import EvaluationInput

    supplied = next(
        store.get("evalinput", p.stem.split("-", 1)[1]) for p in copied.glob("evalinput-*.json")
    )
    assert isinstance(supplied, EvaluationInput)
    forecast_set = supplied.forecast_sets[0]
    bad_row = changed(forecast_set.observations[0], probability=0.123456789)
    supplied = changed(
        supplied,
        forecast_sets=(
            changed(forecast_set, observations=(bad_row, *forecast_set.observations[1:])),
        ),
    )
    service.capture_record(store, supplied)
    new_ledger = evaluation.persist_normalized_evaluation(store, supplied)
    ledger = store.resolve(new_ledger)
    assert isinstance(ledger, NormalizedEvaluationLedger)
    service.capture_record(store, store.resolve(ledger.result))
    with pytest.raises(ValueError, match="FORECAST_MISMATCH"):
        service.capture_provenance(
            store,
            provenance_id="flc7:wrong-value",
            root=graph.root,
            branches=branches(EVALUATION=(new_ledger,)),
            created_at=graph.created_at,
        )


def test_depth_limit() -> None:
    refs = tuple(pin(f"depth-{i}") for i in range(33))
    with pytest.raises(ValueError, match="DEPTH_LIMIT"):
        ProvenanceRecord(
            provenance_id="flc7:deep",
            root=ForecasterKey(
                forecaster_id="forecaster:historical-base-rate", implementation_version="1.0"
            ),
            branches=branches(INFERENCE=(refs[-1],)),
            nodes=tuple(
                ProvenanceNode(
                    reference=r,
                    custody=CustodyClass.TRACKED_REPOSITORY_METADATA,
                    closure="IDENTITY_ONLY",
                )
                for r in refs
            ),
            edges=tuple(
                ProvenanceEdge(source=refs[i], target=refs[i - 1], relation=Relation.USES)
                for i in range(1, 33)
            ),
            created_at=cal.AT,
            evidence_state="SYNTHETIC_ENGINEERING",
        )


def test_ff1_four_fingerprints_and_78_frozen_pins() -> None:
    # Metadata parsing + byte hashes only. No scoring/verifier/empirical generation.
    protocol, execution, result, ledger = ev._legacy_records()
    assert tuple(v.fingerprint for v in (protocol, execution, result, ledger)) == (
        "2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814",
        "2948bc46874f8196c535720bd4f7882f6293fc96077acb563e2e11409c3e4840",
        "8c0556e7b88284c170db57d745de7ece707d365ab52a585db5ebb0d3e81a7d0e",
        "630dd96c0bcd65cb84139dfb20c7488d3e9385e16db18fbaacf60176c99fc583",
    )
    pins = (*protocol.source_pins, *execution.implementation_pins)
    assert len(pins) == 78
    for path, expected in pins:
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected, path


def test_conflicting_duplicate_never_repaired(tmp_path: Path) -> None:
    store = service.LifecycleStore(tmp_path / "conflict", create=True)
    value = InferenceContext(native=base_request()[0])
    service.capture_record(store, value)
    path = store.root / f"infercontext-{value.fingerprint}.json"
    corrupt = path.read_bytes() + b" "
    path.write_bytes(corrupt)
    with pytest.raises(ValueError):
        store.put("infercontext", value)
    assert path.read_bytes() == corrupt


def test_resealed_diagnostic_copied_identity_rejected(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]],
    tmp_path: Path,
) -> None:
    root, graph, refs = integrated
    copied = tmp_path / "copied-id"
    shutil.copytree(root, copied)
    store = service.LifecycleStore(copied)
    store.writable = True
    diagnostic = store.resolve(refs["DIAGNOSTICS"])
    wrong = changed(diagnostic, subject="synthetic:unrelated")
    service.capture_record(store, wrong)
    with pytest.raises(ValueError, match="DIAGNOSTIC_LINEAGE"):
        service.capture_provenance(
            store,
            provenance_id="flc7:copied-id",
            root=graph.root,
            branches=branches(DIAGNOSTICS=(service.reference(wrong),)),
            created_at=graph.created_at,
        )


def test_unknown_fields_cannot_grant_reuse(
    integrated: tuple[Path, ProvenanceRecord, dict[str, ArtifactReference]],
) -> None:
    _, graph, refs = integrated
    q = replay_request(graph, refs["PROVENANCE"], "PROVENANCE")
    for name in (
        "retraining_authorized",
        "empirical_rerun_authorized",
        "grant_calibration_rescue",
        "holdout_unseen",
        "second_execution",
        "post_holdout_refit",
    ):
        with pytest.raises(ValidationError):
            changed(q, **{name: True})
