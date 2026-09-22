"""FLC-2 synthetic engineering, no empirical fit, providers or holdout reads."""

import builtins
import hashlib
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Literal, cast

import pytest
from pydantic import ValidationError

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.forecaster_seams import (
    ForecasterCapability,
    ForecasterRole,
    describe_forecaster,
    inference_descriptors,
)
from tiaf.forecasting.forecaster_seams import ForecasterLifecycle as State
from tiaf.forecasting.identity import ArtifactReference, canonical_json, semantic_fingerprint
from tiaf.forecasting.logistic_store import ResearchForecastStore
from tiaf.learning import forecaster_reference as runner
from tiaf.learning.forecast_artifacts import SealedResearch, reconstruct
from tiaf.learning.forecast_jobs import TrainingJob, TrainingRun
from tiaf.learning.forecaster_authority import (
    TrainingAuthorization,
    admit_training,
    custody_root_fingerprint,
)
from tiaf.learning.forecaster_custody import (
    ArtifactPersistence,
    CustodyClass,
    ForecasterStore,
    RestoredLogisticPredictor,
    persist_training,
    restore_predictor,
    restore_training,
)
from tiaf.learning.forecaster_lifecycle import (
    ActivationState,
    ApprovalDecision,
    LifecycleHistory,
    LifecycleObservation,
    LifecycleRecord,
    LifecycleSubject,
    TransitionRequest,
)
from tiaf.learning.forecaster_training import (
    ExperimentIdentity,
    TrainingBundle,
    TrainingExecution,
    TrainingIdentity,
    TrainingResult,
    logistic_request,
    normalize_logistic,
    reference,
)

from .test_logistic_forecasts import handoff as handoff
from .test_logistic_forecasts import qualification as qualification

AT = datetime(2026, 9, 22, tzinfo=TIAF_TIMEZONE)
KEY = inference_descriptors()[1].identity.key


def pin(name: str) -> ArtifactReference:
    return ArtifactReference(
        artifact_id=f"test:{name}", artifact_version="1.0", fingerprint=semantic_fingerprint(name)
    )


def changed[T: SealedResearch](value: T, **updates: Any) -> T:
    return type(value).model_validate({**value.model_dump(), **updates, "fingerprint": None})


def request() -> TrainingIdentity:
    data = runner.synthetic_input(
        issued_at=AT,
        dependency_lock_fingerprint=hashlib.sha256(
            Path("requirements/ff1-training-linux-py312.lock").read_bytes()
        ).hexdigest(),
        code_fingerprint=hashlib.sha256(Path(runner.__file__).read_bytes()).hexdigest(),
    )
    exp = ExperimentIdentity(
        experiment_id="flc2:synthetic-new-experiment",
        candidate_id="flc2:synthetic-candidate-v1",
        forecaster=KEY,
        design_reference=pin("design"),
    )
    return logistic_request(data.manifest, exp, created_at=AT, purpose="SYNTHETIC_ENGINEERING")


def authorization(req: TrainingIdentity, root: Path) -> TrainingAuthorization:
    data = runner.synthetic_input(
        issued_at=req.created_at,
        dependency_lock_fingerprint=req.dependency_lock_fingerprint,
        code_fingerprint=req.implementation_fingerprint,
    )
    return TrainingAuthorization(
        grant_id="flc2:external-test-permit",
        authority_reference=pin("test-owner"),
        experiment=req.experiment,
        request_reference=reference("request", req),
        input_fingerprint=semantic_fingerprint(data),
        custody_root_fingerprint=custody_root_fingerprint(root),
        experiment_status="OPEN",
        holdout_status="NONE",
        qualification_reference=ArtifactReference(
            artifact_id="test:synthetic-qualification",
            artifact_version="1.0",
            fingerprint=req.qualification_fingerprint,
        ),
        evidence_policy="SYNTHETIC_TRAIN_ONLY",
        issued_at=AT,
        expires_at=datetime(2099, 1, 1, tzinfo=TIAF_TIMEZONE),
    )


@pytest.fixture(scope="module")
def trained(tmp_path_factory: pytest.TempPathFactory) -> tuple[ForecasterStore, TrainingBundle]:
    # Exactly one native synthetic worker invocation for this new module.
    store = ForecasterStore(tmp_path_factory.mktemp("flc2") / "attempt", create=True)
    req = request()
    bundle = runner.execute_synthetic_once(store, req, authorization(req, store.root))
    assert bundle.result.status == "TRAINED", bundle.result.failure_reason
    return store, bundle


def test_train_persist_restore_numeric_replay(
    trained: tuple[ForecasterStore, TrainingBundle],
) -> None:
    store, bundle = trained
    restored = restore_training(ForecasterStore(store.root), reference("bundle", bundle))
    assert restored == bundle
    assert bundle.request.fingerprint != bundle.execution.fingerprint != bundle.result.fingerprint
    assert bundle.result.request_reference == reference("request", bundle.request)
    assert bundle.result.execution_reference == reference("execution", bundle.execution)
    assert bundle.result.model_identity and bundle.result.preprocessor_identity
    assert bundle.execution.resources.attempts == 1
    assert bundle.execution.libraries and bundle.execution.worker_identity is None
    predictor = restore_predictor(ForecasterStore(store.root), reference("bundle", bundle))
    values = (1.0, 2.0, 3.0, 4.0, 7.0)
    output = predictor.predict(values)
    assert output.probability == reconstruct(predictor.artifact.reconstruction, values)
    assert output.calibration == "RAW" and output.validity == "UNKNOWN"
    assert (
        predictor.artifact.role == "CHALLENGER" and predictor.artifact.lifecycle == "EXPERIMENTAL"
    )
    assert describe_forecaster(KEY).identity.lifecycle == State.EXPERIMENTAL


def test_restore_without_training_libraries_or_fit(
    trained: tuple[ForecasterStore, TrainingBundle],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, bundle = trained
    original_import = builtins.__import__

    def no_training(name: str, *args: Any, **kwargs: Any) -> Any:
        if name.split(".")[0] in {"sklearn", "numpy", "scipy", "joblib", "threadpoolctl"}:
            raise AssertionError("training dependency during restore")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_training)
    monkeypatch.setattr(runner, "run_fit", lambda *a: pytest.fail("refit during restore"))
    assert (
        restore_predictor(store, reference("bundle", bundle)).predict((0.0,) * 5).probability >= 0
    )


def test_canonical_immutable_duplicate_and_native_bytes(
    trained: tuple[ForecasterStore, TrainingBundle],
) -> None:
    store, bundle = trained
    before = {p.name: p.read_bytes() for p in store.root.iterdir()}
    job = store.resolve(bundle.execution.native_job_reference)
    assert isinstance(job, TrainingJob) and job.artifact
    assert (
        before[f"model-{job.artifact.fingerprint}.json"]
        == (canonical_json(job.artifact) + "\n").encode()
    )
    assert persist_training(store, bundle.request, job.artifact.manifest, job) == bundle
    assert before == {p.name: p.read_bytes() for p in store.root.iterdir()}
    assert TrainingBundle.model_validate_json(canonical_json(bundle)) == bundle
    assert isinstance(bundle.result.model_dump(mode="json")["diagnostic_references"], list)
    assert not hasattr(bundle.result.diagnostic_references, "append")
    with pytest.raises(ValidationError):
        bundle.request = bundle.request
    with pytest.raises(ValueError, match="READ_ONLY"):
        ForecasterStore(store.root).put("bundle", bundle)
    assert ForecasterStore.put is ResearchForecastStore.put
    assert ForecasterStore.get is ResearchForecastStore.get


@pytest.mark.parametrize(
    "updates",
    [
        {"created_at": AT.replace(tzinfo=None)},
        {"qualification_fingerprint": None},
        {"protected_evidence_used": True},
        {"evidence_partition": "CONSUMED_HOLDOUT"},
        {"mutable_status": "TRAINED"},
    ],
)
def test_bad_training_identity(updates: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        changed(request(), **updates)


def test_request_time_and_fingerprint_stable() -> None:
    req = request()
    assert changed(req, created_at=AT.astimezone(UTC)) == req
    assert "+05:30" in req.model_dump_json()
    assert TrainingIdentity.model_validate_json(canonical_json(req)) == req
    assert changed(req, population_fingerprint="f" * 64).fingerprint != req.fingerprint


@pytest.mark.parametrize("status", ["UNAVAILABLE", "FAILED"])
def test_failure_keeps_identity_without_artifact(tmp_path: Path, status: Any) -> None:
    req = request()
    data = runner.synthetic_input(
        issued_at=AT,
        dependency_lock_fingerprint=req.dependency_lock_fingerprint,
        code_fingerprint=req.implementation_fingerprint,
    )
    job = TrainingJob(
        fold_id=2021,
        grant_fingerprint=cast(str, data.manifest.grant.fingerprint),
        manifest_fingerprint=cast(str, data.manifest.fingerprint),
        status=status,
        reason="MISSING_DEPENDENCY" if status == "UNAVAILABLE" else "WORKER_FAILURE",
        started_at=AT,
        completed_at=AT,
        elapsed_seconds=0.0,
    )
    store = ForecasterStore(tmp_path / "failed", create=True)
    bundle = persist_training(store, req, data.manifest, job)
    assert bundle.result.model_identity is None
    assert bundle.result.preprocessor_identity is None
    assert bundle.execution.libraries is None
    assert restore_training(store, reference("bundle", bundle)) == bundle
    with pytest.raises(ValueError, match="MODEL_UNAVAILABLE"):
        restore_predictor(store, reference("bundle", bundle))


@pytest.mark.parametrize("field", ["status", "request_reference", "execution_reference"])
def test_result_crosslink_mismatch(
    trained: tuple[ForecasterStore, TrainingBundle], field: str
) -> None:
    _, b = trained
    with pytest.raises(ValidationError):
        changed(b.result, **{field: "FAILED" if field == "status" else pin("wrong")})


@pytest.mark.parametrize(
    "updates",
    [
        {"holdout_status": "CONSUMED"},
        {"holdout_status": "PROTECTED"},
        {"experiment_status": "CLOSED"},
        {"input_fingerprint": "f" * 64},
        {"qualification_reference": pin("wrong")},
    ],
)
def test_external_evidence_authority_denies_before_worker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    updates: dict[str, Any],
) -> None:
    store = ForecasterStore(tmp_path / "deny", create=True)
    req = request()
    grant = changed(authorization(req, store.root), **updates)
    monkeypatch.setattr(runner, "run_fit", lambda *a: pytest.fail("unauthorized fit"))
    with pytest.raises(ValueError):
        runner.execute_synthetic_once(store, req, grant)
    assert list(store.root.iterdir()) == []


@pytest.mark.parametrize("which", ["candidate", "version", "experiment", "location", "legacy"])
def test_new_candidate_version_experiment_require_new_external_authority(
    tmp_path: Path, which: str
) -> None:
    req, root = request(), tmp_path / "new"
    grant = authorization(req, root)
    if which == "location":
        root = tmp_path / "another"
    elif which == "legacy":
        req = changed(req, purpose="READ_ONLY_LEGACY")
    else:
        exp = req.experiment
        if which == "candidate":
            exp = changed(exp, candidate_id="flc2:different-candidate")
        elif which == "experiment":
            exp = changed(exp, experiment_id="flc2:different-experiment")
        else:
            exp = changed(exp, forecaster={**KEY.model_dump(), "implementation_version": "2.0"})
        req = changed(req, experiment=exp)
    with pytest.raises(ValueError):
        admit_training(req, grant, input_fingerprint=grant.input_fingerprint, root=root, at=AT)


def test_no_arbitrary_or_empirical_training_recipe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = ForecasterStore(tmp_path / "relabel", create=True)
    req = changed(request(), population_fingerprint="a" * 64)
    # Even a caller-issued synthetic grant cannot pass a relabelled population.
    grant = authorization(req, store.root)
    monkeypatch.setattr(runner, "run_fit", lambda *a: pytest.fail("non-recipe fit"))
    with pytest.raises(ValueError, match="ONLY_COMPILED"):
        runner.execute_synthetic_once(store, req, grant)


def test_no_retry_after_success(trained: tuple[ForecasterStore, TrainingBundle]) -> None:
    store, bundle = trained
    with pytest.raises(ValueError, match="CONSUMED"):
        runner.execute_synthetic_once(
            store, bundle.request, authorization(bundle.request, store.root)
        )
    with pytest.raises(ValueError, match="READ_ONLY"):
        runner.execute_synthetic_once(
            ForecasterStore(store.root), bundle.request, authorization(bundle.request, store.root)
        )


def test_persistence_failure_consumes_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = ForecasterStore(tmp_path / "interrupted", create=True)
    req = request()

    def crash(*args: Any) -> Any:
        raise OSError("simulated worker/host crash")

    monkeypatch.setattr(runner, "run_fit", crash)
    with pytest.raises(OSError):
        runner.execute_synthetic_once(store, req, authorization(req, store.root))
    assert len(list(store.root.glob("attempt-*.json"))) == 1
    assert not list(store.root.glob("bundle-*.json"))
    with pytest.raises(ValueError, match="CONSUMED"):
        runner.execute_synthetic_once(store, req, authorization(req, store.root))


def subject(purpose: Any = "SYNTHETIC_DEMONSTRATION") -> LifecycleSubject:
    return LifecycleSubject(
        forecaster=KEY,
        model_identity=pin("model-identity"),
        role=ForecasterRole.CHALLENGER,
        initial_state=State.EXPERIMENTAL,
        purpose=purpose,
        created_at=AT,
    )


def event(
    history: LifecycleHistory,
    to: State,
    decision: Literal["APPROVED", "DENIED", "HELD", "REJECTED"] = "APPROVED",
) -> LifecycleRecord:
    previous = history.records[-1] if history.records else None
    now = AT + timedelta(seconds=len(history.records) + 1)
    req = TransitionRequest(
        subject_reference=reference("subject", history.subject),
        predecessor_reference=reference("event", previous)
        if previous
        else reference("subject", history.subject),
        current_state=previous.resulting_state if previous else history.subject.initial_state,
        requested_state=to,
        scope="test:noninfluencing-demonstration",
        evidence_references=(pin("evidence"),),
        previous_policy=pin("policy"),
        proposed_policy=pin("policy"),
        requested_at=now,
    )
    approval = ApprovalDecision(
        approval_id=f"test:approval-{len(history.records)}",
        request_reference=reference("transition", req),
        subject_reference=req.subject_reference,
        authority_reference=pin("independent-reviewer"),
        reviewer="test:independent-reviewer",
        decision=decision,
        scope=req.scope,
        evidence_references=req.evidence_references,
        reason="Synthetic governance fixture; not scientific approval",
        created_at=now,
        expires_at=now + timedelta(hours=1),
    )
    state = to if decision == "APPROVED" else req.current_state
    names = {
        State.VALIDATED: "VALIDATED",
        State.SHADOW: "SHADOW_APPROVED",
        State.APPROVED: "ADVISORY_APPROVED",
        State.SUSPENDED: "SUSPENDED",
        State.RETIRED: "RETIRED",
    }
    return LifecycleRecord(
        request=req,
        approval=approval,
        source_event_id=f"test:event-{len(history.records)}",
        source_event_name=cast(Any, names[state] if decision == "APPROVED" else decision),
        source_event_schema="a7.synthetic.fixture.1",
        effective_at=now,
        recorded_at=now,
        resulting_state=state,
    )


def test_external_history_suspension_denied_resumption_and_no_activation(tmp_path: Path) -> None:
    h = LifecycleHistory(subject=subject())
    for to, decision in (
        (State.VALIDATED, "APPROVED"),
        (State.SHADOW, "APPROVED"),
        (State.APPROVED, "APPROVED"),
        (State.SUSPENDED, "APPROVED"),
        (State.APPROVED, "DENIED"),
    ):
        h = changed(h, records=(*h.records, event(h, to, cast(Any, decision))))
    assert h.records[-1].resulting_state == State.SUSPENDED
    assert h.records[-1].source_event_name == "DENIED"
    assert h.subject.role == ForecasterRole.CHALLENGER
    assert all(r.runtime_effect == "NONE" for r in h.records)
    store = ForecasterStore(tmp_path / "history", create=True)
    for r in h.records:
        assert isinstance(r, LifecycleRecord)
        store.put("event", r)
        store.put("approval", r.approval)
    store.put("history", h)
    assert store.resolve(reference("history", h)) == h
    activation = ActivationState(subject_reference=reference("subject", h.subject))
    assert not activation.eligible and not activation.selected
    with pytest.raises(ValidationError):
        changed(activation, selected=True)
    assert describe_forecaster(KEY).identity.lifecycle == State.EXPERIMENTAL


@pytest.mark.parametrize("decision", ["DENIED", "HELD", "REJECTED"])
def test_unsuccessful_decisions_retained(decision: Any) -> None:
    h = LifecycleHistory(subject=subject())
    record = event(h, State.APPROVED, decision)
    h = changed(h, records=[record])  # normal list input -> immutable tuple -> JSON array
    assert h.records[-1].resulting_state == State.EXPERIMENTAL
    assert isinstance(h.records, tuple) and isinstance(h.model_dump(mode="json")["records"], list)
    assert LifecycleHistory.model_validate_json(h.model_dump_json()) == h


def test_illegal_or_legacy_promotion_denied() -> None:
    h = LifecycleHistory(subject=subject())
    with pytest.raises(ValueError, match="INVALID_OR_EXPIRED"):
        event(h, State.APPROVED)
    legacy = LifecycleHistory(subject=subject("READ_ONLY_LEGACY"))
    with pytest.raises(ValueError, match="LEGACY_PROMOTION"):
        changed(legacy, records=(event(legacy, State.VALIDATED),))


@pytest.mark.parametrize(
    "which", ["approval", "scope", "subject", "expired", "lineage", "predecessor"]
)
def test_bad_lifecycle_authority_or_history(which: str) -> None:
    h = LifecycleHistory(subject=subject())
    r = event(h, State.VALIDATED)
    with pytest.raises(ValueError):
        if which == "approval":
            changed(r, approval=None)
        elif which == "scope":
            changed(r, approval=changed(r.approval, scope="test:wider-scope"))
        elif which == "subject":
            changed(r, approval=changed(r.approval, subject_reference=pin("wrong-model")))
        elif which == "expired":
            changed(r, effective_at=r.approval.expires_at, recorded_at=r.approval.expires_at)
        elif which == "lineage":
            changed(r.approval, dataset_fingerprint="f" * 64)
        else:
            changed(h, records=(r, r))


@pytest.mark.parametrize("custody", list(CustodyClass))
def test_custody_not_availability_or_authority(tmp_path: Path, custody: CustodyClass) -> None:
    store = ForecasterStore(tmp_path / "custody", create=True)
    declaration = ArtifactPersistence(
        artifact_reference=reference("request", request()),
        custody=custody,
        location_reference="test:local-vault",
        declared_at=AT,
    )
    store.put("custody", declaration)
    assert declaration.availability == "NOT_CHECKED" and not declaration.use_authorized
    assert store.inspect_availability(declaration.artifact_reference, at=AT).status == "UNAVAILABLE"
    store.put("request", request())
    assert (
        store.inspect_availability(declaration.artifact_reference, at=AT).status
        == "PRESENT_VERIFIED"
    )


def test_unknown_version_and_corrupt_artifact_fail(tmp_path: Path) -> None:
    store = ForecasterStore(tmp_path / "broken", create=True)
    req = request()
    store.put("request", req)
    with pytest.raises(ValueError, match="UNKNOWN_ARTIFACT"):
        store.resolve(pin("not-a-registry-entry"))
    with pytest.raises(ValueError, match="VERSION_MISMATCH"):
        store.resolve(reference("request", req).model_copy(update={"artifact_version": "9.0"}))
    path = store.root / f"request-{req.fingerprint}.json"
    path.write_text("{}\n", encoding="utf-8")  # deliberately corrupt only this temporary fixture
    with pytest.raises(ValueError):
        store.resolve(reference("request", req))


def test_baserate_bypasses_learned_seams() -> None:
    descriptor = inference_descriptors()[0]
    assert descriptor.identity.role == ForecasterRole.BENCHMARK
    assert not descriptor.supports(ForecasterCapability.TRAINING)
    assert not descriptor.supports(ForecasterCapability.ARTIFACT_BACKED)
    # Optional model identity, not a fake trained model, on a primitive lifecycle view.
    value = LifecycleSubject(
        forecaster=descriptor.identity.key,
        role=descriptor.identity.role,
        initial_state=descriptor.identity.lifecycle,
        purpose="READ_ONLY_LEGACY",
        created_at=AT,
    )
    assert value.model_identity is None


def test_training_execution_status_not_request_state(
    trained: tuple[ForecasterStore, TrainingBundle],
) -> None:
    _, bundle = trained
    assert "status" not in TrainingIdentity.model_fields
    assert "status" in TrainingExecution.model_fields and "status" in TrainingResult.model_fields
    assert "approval" not in TrainingResult.model_fields
    with pytest.raises(ValueError):
        changed(bundle.execution, completed_at=bundle.execution.started_at - timedelta(seconds=1))
    assert not hasattr(bundle.result, "activate") and not hasattr(bundle.result, "approve")


def test_legacy_logistic_views_have_no_byte_or_probability_change(
    tmp_path: Path,
    handoff: TrainingRun,
) -> None:
    # Existing synthetic no-fit FF-1 compatibility corpus, never empirical files.
    original = canonical_json(handoff)
    store = ForecasterStore(tmp_path / "legacy", create=True)
    for job in handoff.jobs:
        assert job.artifact
        req = logistic_request(
            job.artifact.manifest,
            request().experiment,
            created_at=job.artifact.manifest.grant.issued_at,
            purpose="READ_ONLY_LEGACY",
        )
        bundle = persist_training(store, req, job.artifact.manifest, job)
        assert normalize_logistic(req, job.artifact.manifest, job) == bundle
        restored = restore_predictor(store, reference("bundle", bundle))
        assert canonical_json(restored.artifact) == canonical_json(job.artifact)
        assert restored.predict((1.0,) * 5).probability == reconstruct(
            job.artifact.reconstruction, (1.0,) * 5
        )
    assert canonical_json(handoff) == original


@pytest.mark.parametrize("name", ["REGISTERED", "TRAINED", "CALIBRATION_FITTED", "EVALUATED"])
def test_stage_events_do_not_auto_validate(name: Any) -> None:
    sub = subject()
    obs = LifecycleObservation(
        subject_reference=reference("subject", sub),
        predecessor_reference=reference("subject", sub),
        source_event_id="test:stage-event",
        source_event_name=name,
        source_event_schema="a7.stage.1",
        evidence_references=(pin("descriptive-report"),),
        current_state=State.EXPERIMENTAL,
        effective_at=AT,
        recorded_at=AT,
    )
    h = LifecycleHistory(subject=sub, records=(obs,))
    assert h.records[0].resulting_state == State.EXPERIMENTAL
    assert LifecycleHistory.model_validate_json(h.model_dump_json()) == h
    assert "approve" not in type(obs).__dict__


def test_synthetic_model_to_external_lifecycle_record(
    trained: tuple[ForecasterStore, TrainingBundle],
) -> None:
    store, bundle = trained
    assert bundle.result.model_identity
    sub = changed(
        subject(), model_identity=reference("modelidentity", bundle.result.model_identity)
    )
    h = LifecycleHistory(subject=sub)
    # External HELD decision is deliberately not a successful evaluation/promotion.
    record = event(h, State.VALIDATED, "HELD")
    h = changed(h, records=(record,))
    store.put("subject", sub)
    store.put("approval", record.approval)
    store.put("history", h)
    assert (
        store.resolve(cast(ArtifactReference, sub.model_identity)) == bundle.result.model_identity
    )
    assert h.records[0].resulting_state == State.EXPERIMENTAL
    assert not ActivationState(subject_reference=reference("subject", sub)).eligible


def test_write_failure_after_worker_leaves_no_complete_bundle(
    trained: tuple[ForecasterStore, TrainingBundle],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, bundle = trained
    job = source.resolve(bundle.execution.native_job_reference)
    assert isinstance(job, TrainingJob)
    store = ForecasterStore(tmp_path / "disk-failure", create=True)
    # Return an existing synthetic result; this failure test performs no extra fit.
    monkeypatch.setattr(runner, "run_fit", lambda data: job)
    original_put = store.put

    def fail_model(kind: str, value: SealedResearch) -> str:
        if kind == "model":
            raise OSError("synthetic disk failure")
        return original_put(kind, value)

    monkeypatch.setattr(store, "put", fail_model)
    with pytest.raises(OSError, match="disk failure"):
        runner.execute_synthetic_once(
            store, bundle.request, authorization(bundle.request, store.root)
        )
    assert list(store.root.glob("attempt-*.json")) and not list(store.root.glob("bundle-*.json"))


def test_missing_model_closure_replay_fails(
    trained: tuple[ForecasterStore, TrainingBundle],
    tmp_path: Path,
) -> None:
    store, bundle = trained
    incomplete = ForecasterStore(tmp_path / "incomplete", create=True)
    # Typed parent alone does not prove its native dependencies exist.
    incomplete.put("bundle", bundle)
    with pytest.raises((ValueError, OSError)):
        restore_training(incomplete, reference("bundle", bundle))
    assert restore_training(store, reference("bundle", bundle)) == bundle


def test_no_self_approved_initial_state() -> None:
    with pytest.raises(ValueError, match="START_EXPERIMENTAL"):
        changed(subject(), initial_state=State.APPROVED)


def test_predictor_rejects_swapped_identity(
    trained: tuple[ForecasterStore, TrainingBundle],
) -> None:
    store, bundle = trained
    predictor = restore_predictor(store, reference("bundle", bundle))
    with pytest.raises(ValueError, match="IDENTITY_MISMATCH"):
        RestoredLogisticPredictor(
            changed(predictor.identity, artifact=pin("other-model")), predictor.artifact
        )
