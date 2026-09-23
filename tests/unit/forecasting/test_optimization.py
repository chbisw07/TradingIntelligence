"""FLC-3: six genuine synthetic fits, no empirical input or protected reads."""

import ast
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import ValidationError

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.evaluation import optimization_evaluation as evaluator
from tiaf.forecasting.identity import ArtifactReference, semantic_fingerprint
from tiaf.learning import forecaster_reference as service
from tiaf.learning import optimization as optimizer
from tiaf.learning.forecast_artifacts import SealedResearch
from tiaf.learning.forecaster_authority import TrainingAuthorization, custody_root_fingerprint
from tiaf.learning.forecaster_custody import restore_training
from tiaf.learning.forecaster_training import reference
from tiaf.learning.optimization_contracts import (
    DEVELOPMENT_POPULATION,
    Domain,
    Objective,
    OptimizationBudget,
    OptimizationGrant,
    OptimizationRequest,
    OptimizationResult,
    SearchSpace,
    TrialPlan,
    TrialRecord,
    plan_trials,
)
from tiaf.learning.synthetic_trials import (
    KEY,
    SyntheticModel,
    SyntheticSpec,
    code_pin,
    dependency_pin,
    development_rows,
    training_rows,
)

AT = datetime(2026, 9, 22, tzinfo=TIAF_TIMEZONE)


def changed[T: SealedResearch](value: T, **updates: Any) -> T:
    return type(value).model_validate({**value.model_dump(), **updates, "fingerprint": None})


def pin(name: str) -> ArtifactReference:
    return ArtifactReference(
        artifact_id=f"test:{name}", artifact_version="1.0", fingerprint=semantic_fingerprint(name)
    )


def request(**changes: Any) -> OptimizationRequest:
    result = OptimizationRequest(
        optimization_request_id="flc3:engineering-grid-1",
        experiment_id="flc3:new-synthetic-design",
        search=SearchSpace(
            domains=(
                Domain(name="C", kind="FLOAT", values=(0.05, 1.0)),
                Domain(name="fit_intercept", kind="BOOLEAN", values=(True, False)),
            )
        ),
        objective=Objective(
            metric_id="metric:brier",
            direction="MINIMIZE",
            population_fingerprint=DEVELOPMENT_POPULATION,
        ),
        budget=OptimizationBudget(),
        training_authority_reference=pin("external-owner"),
        dependency_lock_fingerprint=dependency_pin(),
        implementation_fingerprint=code_pin(),
        created_at=AT,
    )
    return changed(result, **changes) if changes else result


def grant(req: OptimizationRequest, root: Path) -> OptimizationGrant:
    plan = plan_trials(req)
    grants = tuple(
        TrainingAuthorization(
            grant_id=f"test:permit-{trial.index}",
            authority_reference=req.training_authority_reference,
            experiment=trial.training.experiment,
            request_reference=reference("request", trial.training),
            input_fingerprint=semantic_fingerprint(trial.spec),
            custody_root_fingerprint=custody_root_fingerprint(root),
            experiment_status="OPEN",
            holdout_status="NONE",
            qualification_reference=ArtifactReference(
                artifact_id="test:authored-synthetic",
                artifact_version="1.0",
                fingerprint=req.qualification_fingerprint,
            ),
            evidence_policy="SYNTHETIC_TRAIN_ONLY",
            issued_at=AT,
            expires_at=datetime(2099, 1, 1, tzinfo=TIAF_TIMEZONE),
        )
        for trial in plan.trials
    )
    return OptimizationGrant(
        request_reference=reference("optrequest", req),
        plan_reference=reference("optplan", plan),
        training_grants=grants,
    )


@pytest.fixture(scope="module")
def campaign(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[optimizer.OptimizationStore, OptimizationResult]:
    store = optimizer.OptimizationStore(tmp_path_factory.mktemp("flc3") / "campaign", create=True)
    req = request()
    result = optimizer.execute_optimization(store, req, grant(req, store.root))
    assert result.failed_trial_count == 0, [store.resolve(r) for r in result.trial_references]
    assert result.status == "SELECTED"
    return store, result


def test_six_real_trials_distinct_configs_artifacts_and_evaluation(
    campaign: tuple[optimizer.OptimizationStore, OptimizationResult],
) -> None:
    store, result = campaign
    plan = cast(TrialPlan, store.resolve(result.plan_reference))
    assert len(plan.trials) == len(result.trial_references) == 6
    assert len({t.training.fingerprint for t in plan.trials}) == 6
    assert len({t.training.configuration_fingerprint for t in plan.trials}) == 3
    assert len({t.training.experiment.experiment_id for t in plan.trials}) == 3
    coefficients = set()
    artifacts = set()
    for definition, ref in zip(plan.trials, result.trial_references, strict=True):
        record = cast(TrialRecord, store.resolve(ref))
        assert record.bundle_reference and record.evaluation_reference and record.model_identity
        bundle = restore_training(store, record.bundle_reference)
        assert bundle.request == definition.training
        assert bundle.execution.worker_identity == "worker:flc3-synthetic-v1"
        assert bundle.execution.resources.numeric_threads == 1
        assert bundle.request.experiment.forecaster == KEY
        model = cast(SyntheticModel, store.resolve(record.model_identity.artifact))
        assert model.artifact_adapter_version == "flc3.synthetic.artifact.1"
        artifacts.add(model.fingerprint)
        if definition.spec.fold == 1:
            coefficients.add(model.reconstruction.coefficients)
        report = cast(
            evaluator.DevelopmentTrialEvaluation, store.resolve(record.evaluation_reference)
        )
        assert report.objective_value == record.objective_value
        assert report.model_identity_reference == reference("modelidentity", record.model_identity)
        assert report.population_fingerprint == semantic_fingerprint(
            development_rows(definition.spec)
        )
        assert len(training_rows(definition.spec)) in (600, 640)
    assert len(artifacts) == 6 and len(coefficients) == 3
    assert result.selected_model_identity and result.selected_model_identity.forecaster == KEY
    assert result.approval is None and not result.activation and not result.promotion
    assert result.lifecycle == "EXPERIMENTAL" and result.evidence_scope == "DEVELOPMENT_ONLY"


def test_recorded_replay_no_training_prediction_or_evaluation(
    campaign: tuple[optimizer.OptimizationStore, OptimizationResult],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, result = campaign

    def forbidden(*args: Any, **kwargs: Any) -> None:
        pytest.fail("Recorded replay must not fit, predict, evaluate or run processes")

    monkeypatch.setattr(service, "execute_synthetic_once", forbidden)
    monkeypatch.setattr(evaluator, "evaluate_trial", forbidden)
    monkeypatch.setattr(evaluator, "reconstruct", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    readonly = optimizer.OptimizationStore(store.root)
    assert optimizer.replay_optimization(readonly, reference("optresult", result)) == "MATCH"


def test_no_repeat_campaign(
    campaign: tuple[optimizer.OptimizationStore, OptimizationResult],
) -> None:
    store, result = campaign
    req = cast(OptimizationRequest, store.resolve(result.request_reference))
    with pytest.raises(ValueError, match="ALREADY_CONSUMED"):
        optimizer.execute_optimization(store, req, grant(req, store.root))


def test_fingerprint_roundtrip_aware_and_tuple() -> None:
    req = request()
    assert OptimizationRequest.model_validate_json(req.model_dump_json()) == req
    assert plan_trials(req) == plan_trials(req)
    assert req.model_dump(mode="json")["search"]["domains"][0]["values"] == [0.05, 1.0]
    assert req.created_at.utcoffset() == AT.utcoffset()
    assert isinstance(req.search.domains, tuple)
    with pytest.raises(ValidationError):
        req.seed = 5  # type: ignore[assignment]
    with pytest.raises(ValidationError):
        changed(req, created_at=datetime(2026, 9, 22))


@pytest.mark.parametrize(
    "kind,values",
    [
        ("INTEGER", [1, 2]),
        ("FLOAT", [0.1, 1.0]),
        ("BOOLEAN", [True, False]),
        ("CATEGORICAL", ["lbfgs", "alternative"]),
    ],
)
def test_generic_typed_domains(kind: str, values: list[Any]) -> None:
    domain = Domain.model_validate(dict(name="parameter", kind=kind, values=values))
    assert Domain.model_validate_json(domain.model_dump_json()) == domain


@pytest.mark.parametrize(
    "kind,values",
    [
        ("INTEGER", [True]),
        ("INTEGER", [1.5]),
        ("FLOAT", [float("nan")]),
        ("FLOAT", [float("inf")]),
        ("BOOLEAN", [1]),
        ("CATEGORICAL", ["lambda x:x"]),
        ("CATEGORICAL", ["__import__('os')"]),
        ("INTEGER", []),
        ("INTEGER", [1, 1]),
        ("INTEGER", list(range(9))),
    ],
)
def test_invalid_domains(kind: str, values: list[Any]) -> None:
    with pytest.raises(ValueError):
        Domain.model_validate(dict(name="parameter", kind=kind, values=values))


@pytest.mark.parametrize(
    "updates",
    [
        {"protected_evidence_allowed": True},
        {"consumed_holdout_allowed": True},
        {"holdout_status": "CONSUMED"},
        {"holdout_status": "PROTECTED"},
        {"experiment_status": "CLOSED"},
        {"evidence_scope": "2025"},
        {"dataset_fingerprint": "a" * 64},
        {"qualification_fingerprint": "b" * 64},
        {"research_profile_fingerprint": "c" * 64},
        {"target_id": "RELIANCE"},
        {"feature_schema_id": "Dhan"},
        {"seed": 13},
        {"approval": "APPROVED"},
        {"data_path": "data/ff1/2025"},
        {
            "forecaster": {
                "forecaster_id": "forecaster:logistic-regression",
                "implementation_version": "1.0",
            }
        },
    ],
)
def test_evidence_and_version_denied(updates: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        request(**updates)


@pytest.mark.parametrize(
    "updates",
    [
        {"max_trials": 7},
        {"max_parallelism": 2},
        {"per_trial_seconds": 61.0},
        {"max_wall_seconds": 361.0},
        {"max_memory_mib": 1024},
        {"max_features": 6},
        {"max_training_observations": 641},
    ],
)
def test_resource_bounds(updates: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        OptimizationBudget.model_validate(updates)


@pytest.mark.parametrize("count", [2, 4, 6])
def test_trial_budget_and_new_experiment_identity(count: int) -> None:
    req = request(budget=OptimizationBudget.model_validate(dict(max_trials=count)))
    plan = plan_trials(req)
    assert len(plan.trials) == count
    changed_plan = plan_trials(changed(req, optimization_request_id="flc3:another-design"))
    assert not {t.training.experiment.experiment_id for t in plan.trials} & {
        t.training.experiment.experiment_id for t in changed_plan.trials
    }


@pytest.mark.parametrize("status", ["CONSUMED", "PROTECTED", "CLOSED"])
def test_external_holdout_authority_before_worker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, status: str
) -> None:
    store = optimizer.OptimizationStore(tmp_path / "campaign", create=True)
    req = request()
    permission = grant(req, store.root)
    first = changed(
        permission.training_grants[0],
        **({"experiment_status": status} if status == "CLOSED" else {"holdout_status": status}),
    )
    permission = changed(permission, training_grants=(first, *permission.training_grants[1:]))
    monkeypatch.setattr(service, "execute_synthetic_once", lambda *a, **k: pytest.fail("fit"))
    with pytest.raises(ValueError):
        optimizer.execute_optimization(store, req, permission)
    assert not tuple(store.root.iterdir())


@pytest.mark.parametrize("failure", ["timeout", "protocol"])
def test_failed_training_persisted_no_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    store = optimizer.OptimizationStore(tmp_path / "campaign", create=True)
    req = request(budget=OptimizationBudget(max_trials=2))
    calls = []

    def fail(*args: Any, **kwargs: Any) -> Any:
        calls.append(kwargs)
        if failure == "timeout":
            raise subprocess.TimeoutExpired("synthetic", kwargs["timeout"])
        return subprocess.CompletedProcess(args[0], 0, stdout='{"bad":true}', stderr="")

    monkeypatch.setattr(subprocess, "run", fail)
    result = optimizer.execute_optimization(store, req, grant(req, store.root))
    assert len(calls) == 2
    assert result.status == "NO_VALID_TRIAL" and result.failed_trial_count == 2
    assert (
        optimizer.replay_optimization(
            optimizer.OptimizationStore(store.root), reference("optresult", result)
        )
        == "MATCH"
    )


def test_expired_wall_budget_never_fits(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = optimizer.OptimizationStore(tmp_path / "campaign", create=True)
    req = request(budget=OptimizationBudget(max_trials=2, max_wall_seconds=0.000001))
    monkeypatch.setattr(service, "execute_synthetic_once", lambda *a, **k: pytest.fail("fit"))
    result = optimizer.execute_optimization(store, req, grant(req, store.root))
    assert result.status == "NO_VALID_TRIAL" and result.budget_exceeded
    assert result.failed_trial_count == 2


def test_selection_tie_and_maximize(
    campaign: tuple[optimizer.OptimizationStore, OptimizationResult],
) -> None:
    store, result = campaign
    req = cast(OptimizationRequest, store.resolve(result.request_reference))
    plan = cast(TrialPlan, store.resolve(result.plan_reference))
    records = tuple(cast(TrialRecord, store.resolve(r)) for r in result.trial_references)
    tied = tuple(changed(r, objective_value=0.5) for r in records)
    scores, selected = optimizer.select_candidate(req, plan, tied)
    assert selected and scores[0].candidate_id == min(t.candidate_id for t in plan.trials)
    assert selected.trial_id == scores[0].trial_ids[1]
    high = changed(req, objective=changed(req.objective, direction="MAXIMIZE"))
    scores, _ = optimizer.select_candidate(high, plan, records)
    assert scores[0].value == max(s.value for s in scores)


def test_resealed_wrong_selection_mismatch(
    campaign: tuple[optimizer.OptimizationStore, OptimizationResult],
) -> None:
    store, result = campaign
    other = next(
        cast(TrialRecord, store.resolve(r))
        for r in result.trial_references
        if cast(TrialRecord, store.resolve(r)).trial_id != result.selected_trial_id
    )
    bad = changed(
        result, selected_trial_id=other.trial_id, selected_model_identity=other.model_identity
    )
    store.put("optresult", bad)
    assert (
        optimizer.replay_optimization(
            optimizer.OptimizationStore(store.root), reference("optresult", bad)
        )
        == "MISMATCH"
    )


def test_missing_root_mismatch(tmp_path: Path) -> None:
    store = optimizer.OptimizationStore(tmp_path / "empty", create=True)
    assert optimizer.replay_optimization(store, pin("absent")) == "MISMATCH"


def test_fixed_flc2_recipe_source_unchanged() -> None:
    filename = "src/tiaf/learning/forecaster_reference.py"
    old = subprocess.run(
        ["git", "show", f"HEAD:{filename}"], check=True, capture_output=True, text=True
    ).stdout

    def recipe(source: str) -> str:
        return ast.dump(
            next(
                n
                for n in ast.parse(source).body
                if isinstance(n, ast.FunctionDef) and n.name == "synthetic_input"
            )
        )

    assert recipe(old) == recipe(Path(filename).read_text())


def test_optimization_does_not_import_training_internals() -> None:
    source = Path(optimizer.__file__).read_text()
    assert "sklearn" not in source and "numpy" not in source
    assert "training.execute_synthetic_once" in source and "evaluation.evaluate_trial" in source


def test_spec_cannot_accept_market_rows_or_dates() -> None:
    spec = plan_trials(request()).trials[0].spec
    for key in ("rows", "provider", "symbol", "year", "path"):
        with pytest.raises(ValueError):
            SyntheticSpec.model_validate({**spec.model_dump(), key: "RELIANCE/Dhan/2025"})


def test_evaluation_failure_retained_without_retry(
    campaign: tuple[optimizer.OptimizationStore, OptimizationResult],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original, prior = campaign
    req = cast(OptimizationRequest, original.resolve(prior.request_reference))
    plan = plan_trials(req)
    store = optimizer.OptimizationStore(tmp_path / "injected-evaluation-failure", create=True)
    bundles = {}
    for definition, ref in zip(plan.trials, prior.trial_references, strict=True):
        record = cast(TrialRecord, original.resolve(ref))
        assert record.bundle_reference and record.model_identity
        bundles[definition.training.fingerprint] = restore_training(
            original, record.bundle_reference
        )
        store.put("trialmodel", original.resolve(record.model_identity.artifact))
    calls = []

    def supplied_bundle(_store: Any, req: Any, _permission: Any, **kwargs: Any) -> Any:
        calls.append(req.fingerprint)
        return bundles[req.fingerprint]

    def evaluation_failure(*args: Any, **kwargs: Any) -> Any:
        raise ValueError("Injected evaluator failure; no additional fitting")

    monkeypatch.setattr(service, "execute_synthetic_once", supplied_bundle)
    monkeypatch.setattr(evaluator, "evaluate_trial", evaluation_failure)
    result = optimizer.execute_optimization(store, req, grant(req, store.root))
    assert len(calls) == 6 and result.failed_trial_count == 6
    assert result.status == "NO_VALID_TRIAL"
    assert all(
        cast(TrialRecord, store.resolve(r)).status == "EVALUATION_FAILED"
        for r in result.trial_references
    )


def test_unexecuted_invalid_domain_is_still_rejected() -> None:
    req = request(
        search=SearchSpace(
            domains=(
                Domain(name="C", kind="FLOAT", values=(0.05, 1.0, 100.0)),
                Domain(name="fit_intercept", kind="BOOLEAN", values=(True,)),
            )
        ),
        budget=OptimizationBudget(max_trials=2),
    )
    with pytest.raises(ValueError):
        plan_trials(req)


def test_stale_code_pin_denied_before_training(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    req = request(implementation_fingerprint="a" * 64)
    store = optimizer.OptimizationStore(tmp_path / "stale", create=True)
    monkeypatch.setattr(service, "execute_synthetic_once", lambda *a, **k: pytest.fail("fit"))
    with pytest.raises(ValueError, match="IMPLEMENTATION_MISMATCH"):
        optimizer.execute_optimization(store, req, grant(req, store.root))
    assert not tuple(store.root.iterdir())


def test_new_grant_cannot_repeat_training(
    campaign: tuple[optimizer.OptimizationStore, OptimizationResult],
) -> None:
    store, result = campaign
    req = cast(OptimizationRequest, store.resolve(result.request_reference))
    definition = plan_trials(req).trials[0]
    permission = changed(grant(req, store.root).training_grants[0], grant_id="test:new-name")
    with pytest.raises(ValueError, match="ALREADY_CONSUMED"):
        service.execute_synthetic_once(
            store, definition.training, permission, trial=definition.spec
        )


def test_blob_tamper_is_mismatch(
    campaign: tuple[optimizer.OptimizationStore, OptimizationResult], tmp_path: Path
) -> None:
    original, result = campaign
    store = optimizer.OptimizationStore(tmp_path / "tamper", create=True)
    store.put("optresult", result)
    path = store.root / f"optresult-{result.fingerprint}.json"
    path.write_text(path.read_text().replace('"activation":false', '"activation":true'))
    assert optimizer.replay_optimization(store, reference("optresult", result)) == "MISMATCH"
    assert (
        optimizer.replay_optimization(
            optimizer.OptimizationStore(original.root), reference("optresult", result)
        )
        == "MATCH"
    )
