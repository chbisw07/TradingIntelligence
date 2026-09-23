"""FLC-5 synthetic composition tests; no fitting, empirical inputs or truth."""

import ast
import socket
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.contracts import (
    BinaryProbabilityOutput,
    ForecastComposition,
    ForecastNode,
    ForecastRoot,
)
from tiaf.forecasting.enums import ForecastRealizationMode, ForecastStatus
from tiaf.forecasting.forecaster_seams import (
    CalibratableOutput,
    ForecasterFamily,
    ForecasterLifecycle,
    ForecasterRole,
    LifecycleIdentity,
)
from tiaf.forecasting.identity import canonical_json, semantic_fingerprint
from tiaf.learning import calibration as service
from tiaf.learning.calibration_contracts import (
    PROBABILITIES,
    SOURCE_KEY,
    VERSION,
    CalibrationApplyRequest,
    CalibrationApplyResult,
    CalibrationArtifact,
    CalibrationArtifactIdentity,
    CalibrationComponent,
    CalibrationEvidence,
    CalibrationFitRequest,
    CalibrationFitResult,
    CalibrationSource,
    synthetic_pin,
    synthetic_target,
)
from tiaf.learning.forecast_artifacts import SealedResearch
from tiaf.learning.forecaster_custody import ArtifactPersistence, CustodyClass
from tiaf.learning.forecaster_training import reference

AT = datetime(2026, 9, 23, 9, 15, tzinfo=TIAF_TIMEZONE)
TABLE = ((0.0, 0.0), (0.5, 0.4), (1.0, 1.0))


def changed[T: SealedResearch](value: T, **updates: Any) -> T:
    return type(value).model_validate({**value.model_dump(), **updates, "fingerprint": None})


def source(index: int = 2) -> CalibrationSource:
    return CalibrationSource(
        index=index,
        forecast_id=f"flc5:authored-{index}",
        compatible=CalibratableOutput(
            output=BinaryProbabilityOutput(probability=PROBABILITIES[index]),
            forecaster=LifecycleIdentity(
                key=SOURCE_KEY,
                family=ForecasterFamily.PRIMITIVE,
                role=ForecasterRole.BENCHMARK,
                lifecycle=ForecasterLifecycle.EXPERIMENTAL,
            ),
            input_forecast=synthetic_pin(f"authored-{index}"),
        ),
        primitive_composition=ForecastComposition(
            composition_id="flc5:synthetic-primitive",
            nodes=(
                ForecastNode(
                    node_id="flc5:primitive",
                    artifact_ref=synthetic_pin("source-model"),
                    realization_mode=ForecastRealizationMode.SIMULATED_ISSUANCE,
                ),
            ),
            roots=(ForecastRoot(root_id="flc5:raw-root", node_id="flc5:primitive"),),
            policy_ref=synthetic_pin("raw-policy"),
        ),
        target=synthetic_target(),
        information_cutoff=AT,
        computed_at=AT,
    )


def artifact(knots: tuple[tuple[float, float], ...] = TABLE) -> CalibrationArtifact:
    return CalibrationArtifact(
        identity=CalibrationArtifactIdentity(
            component=CalibrationComponent(
                calibrator_id="calibrator:flc5-reference",
                implementation_version=VERSION,
                family="calibrator:authored-monotonic-table",
                target=synthetic_target(),
                source_forecaster=SOURCE_KEY,
                source_model=synthetic_pin("source-model"),
                mode=ForecastRealizationMode.SIMULATED_ISSUANCE,
                configuration_fingerprint=semantic_fingerprint(knots),
                created_at=AT,
            ),
            evidence=CalibrationEvidence(
                experiment_id="synthetic:calibration-design",
                source_experiment_id="synthetic:raw-design",
                protocol=synthetic_pin("reference-protocol"),
                source_forecast_population=synthetic_pin("source-population"),
                training_population=synthetic_pin("authored-parameter-population"),
                qualification=synthetic_pin("synthetic-engineering-declaration"),
                evidence_policy=synthetic_pin("synthetic-only"),
            ),
        ),
        knots=knots,
        available_at=AT,
        valid_until=AT + timedelta(days=1),
    )


def request(s: CalibrationSource, a: CalibrationArtifact) -> CalibrationApplyRequest:
    return CalibrationApplyRequest(
        request_id="flc5:apply",
        source_reference=reference("calsource", s),
        source_forecast_id=s.forecast_id,
        source_forecaster=SOURCE_KEY,
        component=a.identity.component,
        artifact_reference=reference("calartifact", a),
        target=s.target,
        mode=ForecastRealizationMode.SIMULATED_ISSUANCE,
        policy=synthetic_pin("apply-policy"),
        created_at=AT,
    )


@pytest.fixture
def store(tmp_path: Path) -> service.CalibrationStore:
    return service.CalibrationStore(tmp_path / "calibration", create=True)


@pytest.mark.parametrize("index,expected", [(0, 0.0), (1, 0.16), (2, 0.4), (3, 0.76), (4, 1.0)])
def test_reference_application_observability_replay(
    store: service.CalibrationStore,
    index: int,
    expected: float,
) -> None:
    s, a = source(index), artifact()
    raw = canonical_json(s)
    store.put("calsource", s)
    service.persist_reference_artifact(store, a)
    result = service.apply_calibration(store, request(s, a))
    assert result.status is ForecastStatus.GENERATED
    assert result.raw_probability == PROBABILITIES[index]
    assert result.calibrated_probability == pytest.approx(expected)
    assert canonical_json(s) == raw
    assert result.source.compatible == s.compatible
    assert result.composition is not None
    assert result.composition.primitive == s.primitive_composition
    assert result.composition.edge.source_node_id == s.primitive_composition.nodes[0].node_id
    assert result.composition.edge.target_node_id == a.identity.component.calibrator_id
    readonly = service.CalibrationStore(store.root)
    assert service.replay_calibration(readonly, reference("calresult", result)) == "MATCH"


def test_explicit_identity_is_separate_from_missing_artifact(
    store: service.CalibrationStore,
) -> None:
    s, a = source(), artifact(((0.0, 0.0), (1.0, 1.0)))
    store.put("calsource", s)
    q = request(s, a)
    absent = service.apply_calibration(store, q)
    assert absent.status is ForecastStatus.UNAVAILABLE and absent.calibrated_probability is None
    assert absent.composition is None and absent.raw_probability == 0.5
    service.persist_reference_artifact(store, a)
    present = service.apply_calibration(store, q)
    assert present.raw_probability == present.calibrated_probability == 0.5
    assert present.interpretation == "SYNTHETIC_TRANSFORM_NOT_CALIBRATION_QUALIFICATION"
    assert present.fingerprint != absent.fingerprint
    assert service.replay_calibration(store, reference("calresult", absent)) == "MATCH"


def test_proposal_fit_never_executes_and_custody_grants_nothing(
    store: service.CalibrationStore,
) -> None:
    a = artifact()
    proposal = CalibrationFitRequest(
        request_id="synthetic:fit-proposal",
        component=a.identity.component,
        evidence=a.identity.evidence,
        created_at=AT,
    )
    result = CalibrationFitResult(request=reference("calfitrequest", proposal))
    for kind, value in (("calfitrequest", proposal), ("calfitresult", result)):
        store.put(kind, value)
        assert store.resolve(reference(kind, value)) == value
    assert not proposal.fit_authorized and result.artifact is None
    assert result.status == "NOT_EXECUTED" and not a.identity.fit_performed
    assert not hasattr(service, "fit")
    ref = service.persist_reference_artifact(store, a)
    custody = ArtifactPersistence(
        artifact_reference=ref,
        custody=CustodyClass.GENERATED_EPHEMERAL,
        location_reference="synthetic:local-custody",
        declared_at=AT,
    )
    store.put("custody", custody)
    assert not custody.use_authorized and not a.identity.promotion
    assert store.inspect_availability(ref, at=AT).status == "PRESENT_VERIFIED"


@pytest.mark.parametrize(
    "field,value",
    [
        ("target_id", "synthetic:different"),
        ("target_version", "2.0"),
        ("positive_event", "synthetic:negative"),
        ("horizon", "synthetic:two-steps"),
        ("cutoff_policy", synthetic_pin("wrong-cutoff")),
    ],
)
def test_target_compatibility(store: service.CalibrationStore, field: str, value: Any) -> None:
    s, a = source(), artifact()
    store.put("calsource", s)
    q = changed(request(s, a), target=changed(s.target, **{field: value}))
    with pytest.raises(ValueError, match="TARGET_INCOMPATIBLE"):
        service.apply_calibration(store, q)


@pytest.mark.parametrize("value", [-0.1, 1.1, float("nan"), float("inf"), True, "0.5"])
def test_invalid_probabilities(value: Any) -> None:
    with pytest.raises(ValidationError):
        BinaryProbabilityOutput.model_validate({"probability": value})


@pytest.mark.parametrize(
    "updates",
    [
        {"input_semantics": "LOGIT"},
        {"output_semantics": "CLASS"},
    ],
)
def test_semantics_mismatch(updates: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        changed(synthetic_target(), **updates)


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_model", synthetic_pin("refitted-model")),
        ("source_preprocessor", synthetic_pin("refitted-scaler")),
        ("mode", ForecastRealizationMode.ACTUAL_ISSUANCE),
    ],
)
def test_dependency_compatibility(store: service.CalibrationStore, field: str, value: Any) -> None:
    s, a = source(), artifact()
    store.put("calsource", s)
    q = changed(request(s, a), component=changed(a.identity.component, **{field: value}))
    with pytest.raises(ValueError, match="MISMATCH|INCOMPATIBLE"):
        service.apply_calibration(store, q)


@pytest.mark.parametrize(
    "updates",
    [
        {"available_at": AT + timedelta(seconds=1)},
        {"available_at": AT - timedelta(days=1), "valid_until": AT},
    ],
)
def test_artifact_availability_at_source_cutoff(
    store: service.CalibrationStore, updates: dict[str, Any]
) -> None:
    s, a = source(), artifact()
    if "valid_until" in updates:
        component = changed(a.identity.component, created_at=AT - timedelta(days=1))
        a = changed(a, identity=changed(a.identity, component=component))
    a = changed(a, **updates)
    store.put("calsource", s)
    service.persist_reference_artifact(store, a)
    with pytest.raises(ValueError, match="NOT_VALID_AT_CUTOFF"):
        service.apply_calibration(store, request(s, a))


@pytest.mark.parametrize(
    "updates",
    [
        {"holdout_state": "CONSUMED"},
        {"holdout_state": "SEALED"},
        {"experiment_state": "CLOSED"},
        {"consumed_2025_reuse": True},
        {"same_experiment_rescue": True},
        {"experiment_id": "synthetic:raw-design"},
        {"training_population": synthetic_pin("2025-consumed")},
        {"source_forecast_population": synthetic_pin("renamed-2025")},
        {"qualification_verified": True},
        {"outcomes": [1, 0]},
    ],
)
def test_evidence_guards(updates: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        changed(artifact().identity.evidence, **updates)


@pytest.mark.parametrize(
    "updates",
    [
        {"fit_authorized": True},
        {"production_apply_authorized": True},
        {"scope": "EMPIRICAL"},
        {"consumed_holdout_reuse": True},
        {"evidence_policy": "OUTCOMES"},
    ],
)
def test_apply_authority_guards(updates: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        changed(request(source(), artifact()), **updates)


def test_synthetic_label_cannot_admit_market_values() -> None:
    s = source()
    raw = s.compatible.model_dump()
    raw["output"] = BinaryProbabilityOutput(probability=0.61)
    with pytest.raises(ValidationError, match="NOT_AUTHORED"):
        changed(s, compatible=CalibratableOutput.model_validate(raw))
    with pytest.raises(ValidationError):
        changed(s, symbol="RELIANCE", provider="DHAN")


def test_unsupported_is_not_failure(store: service.CalibrationStore) -> None:
    s, a = source(), artifact()
    store.put("calsource", s)
    q = changed(request(s, a), component=changed(a.identity.component, family="calibrator:future"))
    result = service.apply_calibration(store, q)
    assert result.status is ForecastStatus.UNSUPPORTED
    assert result.artifact_checked == "NOT_CHECKED" and result.calibrated_probability is None
    assert service.replay_calibration(store, reference("calresult", result)) == "MATCH"


def test_fingerprint_json_and_timezone(store: service.CalibrationStore) -> None:
    s, a = source(), artifact()
    store.put("calsource", s)
    service.persist_reference_artifact(store, a)
    result = service.apply_calibration(store, request(s, a))
    assert CalibrationApplyResult.model_validate_json(result.model_dump_json()) == result
    assert changed(result.request, created_at=AT.astimezone(UTC)) == result.request
    assert result.request.model_dump(mode="json")["created_at"].endswith("+05:30")
    assert isinstance(result.lineage, tuple)
    assert isinstance(result.model_dump(mode="json")["lineage"], list)
    with pytest.raises(ValidationError):
        result.raw_probability = 0.1
    with pytest.raises(ValidationError):
        changed(result.request, created_at=AT.replace(tzinfo=None))
    assert service.apply_calibration(store, result.request) == result
    assert result.composition is not None
    assert result.composition.composition_id.endswith(str(result.composition.fingerprint))
    with pytest.raises(ValidationError):
        changed(result.composition, root_node_id="wrong:root")


@pytest.mark.parametrize(
    "updates",
    [
        {"evaluation_performed": True},
        {"approval": True},
        {"promotion": True},
        {"activation": True},
        {"brier": 0.1},
        {"diagnostic_health": "GOOD"},
        {"selected_trial": "best"},
    ],
)
def test_result_separation(store: service.CalibrationStore, updates: dict[str, Any]) -> None:
    s, a = source(), artifact()
    store.put("calsource", s)
    service.persist_reference_artifact(store, a)
    result = service.apply_calibration(store, request(s, a))
    with pytest.raises(ValidationError):
        changed(result, **updates)


def test_resealed_wrong_value_and_missing_child_fail_replay(
    store: service.CalibrationStore,
) -> None:
    s, a = source(), artifact()
    store.put("calsource", s)
    service.persist_reference_artifact(store, a)
    result = service.apply_calibration(store, request(s, a))
    forged = changed(result, calibrated_probability=0.9)
    store.put("calresult", forged)
    assert service.replay_calibration(store, reference("calresult", forged)) == "MISMATCH"
    path = store.root / f"calartifact-{a.fingerprint}.json"
    path.write_text(path.read_text().replace('"fit_performed":false', '"fit_performed":true'))
    assert service.replay_calibration(store, reference("calresult", result)) == "MISMATCH"


def test_offline_replay_without_writes_external_calls_or_apply(
    store: service.CalibrationStore,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    s, a = source(), artifact()
    store.put("calsource", s)
    service.persist_reference_artifact(store, a)
    result = service.apply_calibration(store, request(s, a))
    before = {p.name: p.read_bytes() for p in store.root.iterdir()}

    def forbidden(*args: Any, **kwargs: Any) -> None:
        pytest.fail("offline replay performed an external operation")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(service, "apply_calibration", forbidden)
    monkeypatch.setattr(service.CalibrationStore, "put", forbidden)
    assert (
        service.replay_calibration(
            service.CalibrationStore(store.root), reference("calresult", result)
        )
        == "MATCH"
    )
    assert before == {p.name: p.read_bytes() for p in store.root.iterdir()}


def test_application_failure_preserves_raw(
    store: service.CalibrationStore, monkeypatch: pytest.MonkeyPatch
) -> None:
    s, a = source(), artifact()
    store.put("calsource", s)
    service.persist_reference_artifact(store, a)

    def broken(*args: Any) -> float:
        raise ArithmeticError("injected transform failure")

    monkeypatch.setattr(service, "_transform", broken)
    result = service.apply_calibration(store, request(s, a))
    assert result.status is ForecastStatus.FAILED and result.raw_probability == 0.5
    assert result.calibrated_probability is None


def test_no_evaluator_trainer_diagnostics_optimizer_or_registry_imports() -> None:
    tree = ast.parse(Path(service.__file__).read_text())
    modules = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert not any(
        word in m
        for m in modules
        for word in ("evaluation", "optimization", "diagnostics", "sklearn", "providers")
    )
    assert not any(
        isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr in ("fit", "evaluate", "register", "activate", "optimize")
        for n in ast.walk(tree)
    )


@pytest.mark.parametrize("field", ["artifact_checked", "lineage", "composition"])
def test_result_rejects_inconsistent_lineage(store: service.CalibrationStore, field: str) -> None:
    s, a = source(), artifact()
    store.put("calsource", s)
    service.persist_reference_artifact(store, a)
    result = service.apply_calibration(store, request(s, a))
    assert result.composition is not None
    value: Any = {
        "artifact_checked": "NOT_CHECKED",
        "lineage": tuple(reversed(result.lineage)),
        "composition": changed(result.composition, policy=synthetic_pin("different-policy")),
    }[field]
    with pytest.raises(ValueError):
        changed(result, **{field: value})


def test_distinct_parameters_change_composition_identity(store: service.CalibrationStore) -> None:
    s = source()
    store.put("calsource", s)
    results = []
    for a in (artifact(), artifact(((0.0, 0.0), (1.0, 1.0)))):
        service.persist_reference_artifact(store, a)
        results.append(service.apply_calibration(store, request(s, a)))
    first, second = results
    assert first.composition is not None and second.composition is not None
    assert first.composition.composition_id != second.composition.composition_id
    assert first.source == second.source == s
    assert first.raw_probability == second.raw_probability == 0.5
    assert first.calibrated_probability != second.calibrated_probability
