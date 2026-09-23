"""FLC-6 independent Evaluation normalization over synthetic supplied rows."""

import ast
import math
import socket
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal

import pytest
from pydantic import ValidationError

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.evaluation import forecast_normalization as service
from tiaf.evaluation.forecast_final_protocol import FinalProtocol
from tiaf.evaluation.forecast_final_scoring import FinalEvaluation
from tiaf.evaluation.forecast_final_store import FinalExecution, FinalLedger
from tiaf.evaluation.forecast_normalization_contracts import (
    CoverageAccounting,
    EvaluationIdentity,
    EvaluationInput,
    EvaluationParticipant,
    EvaluationPopulation,
    EvaluationRequest,
    EvaluationTargetIdentity,
    EvidenceUseDeclaration,
    ForecastObservation,
    GroundTruthIdentity,
    GroundTruthObservation,
    GroundTruthSet,
    KnownCount,
    MetricDefinition,
    MetricSetIdentity,
    NormalizedEvaluationLedger,
    NormalizedEvaluationResult,
    PairingIdentity,
    ParticipantForecastSet,
    StatisticalPolicy,
    synthetic_reference,
)
from tiaf.forecasting.enums import ForecastRealizationMode, PopulationDisposition
from tiaf.forecasting.identity import canonical_json
from tiaf.learning.forecast_artifacts import SealedResearch

AT = datetime(2026, 9, 23, 10, 0, tzinfo=TIAF_TIMEZONE)
OBSERVATIONS = tuple(f"synthetic:observation-{index}" for index in range(5))
LABELS = (0, 1, 0, 1, 0)
BENCHMARK = (0.5, 0.5, 0.5, 0.5, 0.5)
CHALLENGER = (0.1, 0.9, 0.2, 0.8, 0.3)


def changed[T: SealedResearch](record: T, **updates: Any) -> T:
    return type(record).model_validate({**record.model_dump(), **updates, "fingerprint": None})


def target() -> EvaluationTargetIdentity:
    return EvaluationTargetIdentity(
        target_id="synthetic:next-step-direction",
        target_version="1.0",
        horizon="synthetic:one-step",
        event="synthetic:terminal-greater-than-reference",
        cutoff_policy=synthetic_reference("cutoff-policy"),
    )


def population() -> EvaluationPopulation:
    return EvaluationPopulation(
        population_id="synthetic:flc6-population",
        population_version="1.0",
        subject="synthetic:asset",
        universe=("synthetic:asset",),
        window_start=AT,
        window_end=AT + timedelta(days=5),
        observation_ids=OBSERVATIONS,
        eligibility_rule=synthetic_reference("eligibility-rule"),
        exclusion_rule=synthetic_reference("exclusion-rule"),
        split_ref=synthetic_reference("split"),
        protection_state="SYNTHETIC_REFERENCE",
        complete=True,
    )


def truth_identity() -> GroundTruthIdentity:
    return GroundTruthIdentity(
        authority_id="evaluation:synthetic-outcome-journal",
        journal_ref=synthetic_reference("outcome-journal"),
        target=target(),
        label_version="1.0",
        resolution_policy=synthetic_reference("label-resolution"),
    )


def metrics() -> MetricSetIdentity:
    return MetricSetIdentity(
        metric_set_id="evaluation:binary-probability-reference",
        metric_set_version="1.0",
        metrics=(
            MetricDefinition(
                metric_id="BRIER",
                tier="PRIMARY",
                direction="LOWER_IS_BETTER",
                numeric_policy=synthetic_reference("brier-policy"),
            ),
            MetricDefinition(
                metric_id="NATURAL_LOG_LOSS",
                tier="SECONDARY_DESCRIPTIVE",
                direction="LOWER_IS_BETTER",
                numeric_policy=synthetic_reference("log-loss-policy"),
            ),
            MetricDefinition(
                metric_id="ACCURACY",
                tier="SECONDARY_DESCRIPTIVE",
                direction="HIGHER_IS_BETTER",
                numeric_policy=synthetic_reference("accuracy-policy"),
            ),
            MetricDefinition(
                metric_id="ECE_FIXED_10",
                tier="DIAGNOSTIC_ONLY",
                direction="DESCRIPTIVE_ONLY",
                numeric_policy=synthetic_reference("ece-policy"),
            ),
        ),
    )


def statistics(minimum_support: int = 5) -> StatisticalPolicy:
    return StatisticalPolicy(
        policy_id="evaluation:ff1-compatible-moving-block",
        policy_version="1.0",
        minimum_support=minimum_support,
    )


def participant(
    participant_id: str,
    role: Literal["BENCHMARK", "CHALLENGER", "SUBJECT"],
    pop: EvaluationPopulation,
) -> EvaluationParticipant:
    return EvaluationParticipant(
        participant_id=participant_id,
        form="ARTIFACT_BACKED_FORECASTER",
        report_role=role,
        forecast_or_composition=synthetic_reference(participant_id.split(":", 1)[1]),
        target=target(),
        population_fingerprint=str(pop.fingerprint),
        realization_mode=ForecastRealizationMode.SIMULATED_ISSUANCE,
        cutoff_policy=target().cutoff_policy,
    )


def request(*, paired: bool = True, minimum_support: int = 5) -> EvaluationRequest:
    pop = population()
    participants: tuple[EvaluationParticipant, ...] = (
        participant("participant:benchmark", "BENCHMARK", pop),
        participant("participant:challenger", "CHALLENGER", pop),
    )
    if not paired:
        participants = participants[:1]
    pairing = PairingIdentity(
        comparison_id="evaluation:synthetic-paired" if paired else "evaluation:synthetic-single",
        comparison_version="1.0",
        mode="PAIRED_COMPARISON" if paired else "SINGLE_PARTICIPANT",
        participant_ids=tuple(item.participant_id for item in participants),
    )
    metric_set = metrics()
    policy = statistics(minimum_support)
    truth = truth_identity()
    identity = EvaluationIdentity(
        evaluation_id="evaluation:flc6-synthetic",
        evaluation_version="1.0",
        subject=pop.subject,
        universe=pop.universe,
        target=target(),
        realization_mode=ForecastRealizationMode.SIMULATED_ISSUANCE,
        population_fingerprint=str(pop.fingerprint),
        split_ref=pop.split_ref,
        ground_truth_fingerprint=str(truth.fingerprint),
        metric_set_fingerprint=str(metric_set.fingerprint),
        comparison_fingerprint=str(pairing.fingerprint),
        statistical_policy_fingerprint=str(policy.fingerprint),
        policy_ref=synthetic_reference("evaluation-policy"),
        created_at=AT,
    )
    return EvaluationRequest(
        request_id="evaluation:flc6-request",
        identity=identity,
        participants=participants,
        population=pop,
        ground_truth=truth,
        pairing=pairing,
        metric_set=metric_set,
        statistics=policy,
        evidence_use=EvidenceUseDeclaration(
            evidence_ref=synthetic_reference("authored-evidence"),
            source_experiment_id="experiment:synthetic-source",
            requesting_experiment_id="experiment:synthetic-evaluation",
            source_state="SYNTHETIC_REFERENCE",
            use_classification="SYNTHETIC_REFERENCE",
            evaluation_execution_authorized=True,
        ),
        decision_policy_ref=synthetic_reference("external-decision-policy"),
        created_at=AT,
    )


def evaluation_input(
    q: EvaluationRequest,
    *,
    missing_forecast: tuple[str, int] | None = None,
    missing_truth: int | None = None,
) -> EvaluationInput:
    probabilities = (BENCHMARK, CHALLENGER)
    forecast_sets = []
    for participant_index, item in enumerate(q.participants):
        rows = []
        for index, (observation_id, probability) in enumerate(
            zip(OBSERVATIONS, probabilities[participant_index], strict=True)
        ):
            absent = missing_forecast == (item.participant_id, index)
            rows.append(
                ForecastObservation(
                    observation_id=observation_id,
                    participant_id=item.participant_id,
                    forecast_ref=None
                    if absent
                    else synthetic_reference(f"{item.participant_id}-{index}"),
                    probability=None if absent else probability,
                    status="MISSING" if absent else "AVAILABLE",
                    reason="evaluation:forecast-missing" if absent else "evaluation:available",
                )
            )
        forecast_sets.append(
            ParticipantForecastSet(
                participant=item,
                population_fingerprint=str(q.population.fingerprint),
                observations=tuple(rows),
            )
        )
    truth_rows = tuple(
        GroundTruthObservation(
            observation_id=observation_id,
            journal_entry_ref=None
            if missing_truth == index
            else synthetic_reference(f"truth-{index}"),
            label=None if missing_truth == index else LABELS[index],
            status="MISSING" if missing_truth == index else "AVAILABLE",
            reason="evaluation:truth-missing" if missing_truth == index else "evaluation:available",
        )
        for index, observation_id in enumerate(OBSERVATIONS)
    )
    return EvaluationInput(
        request=q,
        forecast_sets=tuple(forecast_sets),
        ground_truth=GroundTruthSet(
            identity=q.ground_truth,
            population_fingerprint=str(q.population.fingerprint),
            observations=truth_rows,
        ),
        captured_at=AT,
    )


@pytest.fixture
def store(tmp_path: Path) -> service.NormalizedEvaluationStore:
    return service.NormalizedEvaluationStore(tmp_path / "evaluation", create=True)


def test_exact_toy_metrics_pairing_statistics_and_authority() -> None:
    q = request()
    result = service.evaluate_normalized(q, evaluation_input(q))
    values = {
        (value.participant_id, value.metric_id): value.value for value in result.metrics.values
    }
    expected_log = sum(-math.log(p if y else 1 - p) for p, y in zip(CHALLENGER, LABELS)) / 5
    assert values["participant:benchmark", "BRIER"] == 0.25
    assert values["participant:challenger", "BRIER"] == pytest.approx(0.038)
    assert values["participant:challenger", "NATURAL_LOG_LOSS"] == pytest.approx(expected_log)
    assert values["participant:benchmark", "ACCURACY"] == 0.4
    assert values["participant:challenger", "ACCURACY"] == 1.0
    assert values["participant:benchmark", "ECE_FIXED_10"] == pytest.approx(0.1)
    assert values["participant:challenger", "ECE_FIXED_10"] == pytest.approx(0.18)
    assert result.paired_table is not None and len(result.paired_table.rows) == 5
    assert result.statistics.status == "ESTIMATED"
    assert result.statistics.brier_difference == pytest.approx(0.038 - 0.25)
    assert result.status == "GENERATED" and result.coverage.coverage == 1.0
    assert not any(
        (result.optimizer_selection, result.approval, result.promotion, result.activation)
    )
    assert result.scientific_decision == "NOT_OWNED_BY_EVALUATOR"


def test_primary_secondary_and_diagnostic_tiers_are_preserved() -> None:
    q = request()
    result = service.evaluate_normalized(q, evaluation_input(q))
    tiers = {metric.metric_id: metric.tier for metric in result.metrics.metric_set.metrics}
    assert tiers == {
        "BRIER": "PRIMARY",
        "NATURAL_LOG_LOSS": "SECONDARY_DESCRIPTIVE",
        "ACCURACY": "SECONDARY_DESCRIPTIVE",
        "ECE_FIXED_10": "DIAGNOSTIC_ONLY",
    }
    assert result.metrics.metric_set.fingerprint == q.identity.metric_set_fingerprint


def test_missing_participant_and_truth_retain_denominator_and_reasons() -> None:
    q = request()
    supplied = evaluation_input(q, missing_forecast=("participant:challenger", 1), missing_truth=3)
    result = service.evaluate_normalized(q, supplied)
    assert result.status == "INSUFFICIENT_SUPPORT"
    assert result.coverage.requested.value == 5
    assert result.coverage.evaluated.value == 3
    assert result.coverage.coverage == 0.6
    assert result.coverage.protected_excluded.value == 0
    assert result.coverage.consumed_excluded.value == 0
    assert dict(result.coverage.exclusions_by_reason) == {
        "evaluation:forecast-missing": 1,
        "evaluation:truth-missing": 1,
    }
    assert (
        tuple(row.disposition for row in result.coverage.dispositions).count(
            PopulationDisposition.NOT_EVALUABLE
        )
        == 2
    )
    assert result.paired_table is not None and len(result.paired_table.rows) == 3


def test_single_participant_is_not_fake_pairing() -> None:
    q = request(paired=False)
    result = service.evaluate_normalized(q, evaluation_input(q))
    assert q.pairing.mode == "SINGLE_PARTICIPANT"
    assert result.paired_table is None
    assert result.statistics.status == "NOT_APPLICABLE"
    assert len(result.metrics.values) == 4


@pytest.mark.parametrize(
    "form",
    [
        "PRIMITIVE_FORECASTER",
        "ARTIFACT_BACKED_FORECASTER",
        "CALIBRATED_COMPOSITION",
        "FUTURE_COMPOSITE",
    ],
)
def test_one_participant_contract_supports_all_declared_forms(form: str) -> None:
    original = request().participants[0]
    participant_view = changed(original, form=form)
    assert participant_view.form == form
    assert participant_view.forecast_or_composition == original.forecast_or_composition


def test_statistical_policy_and_result_are_deterministic() -> None:
    q = request()
    supplied = evaluation_input(q)
    first = service.evaluate_normalized(q, supplied)
    second = service.evaluate_normalized(q, supplied)
    assert first == second
    assert first.statistics.policy.fingerprint == q.identity.statistical_policy_fingerprint
    assert first.statistics.sampled_indices_fingerprint is not None


def test_short_grid_reports_statistics_not_estimable() -> None:
    q = request()
    short_population = changed(q.population, observation_ids=OBSERVATIONS[:4])
    participants = tuple(
        changed(item, population_fingerprint=str(short_population.fingerprint))
        for item in q.participants
    )
    identity = changed(
        q.identity,
        population_fingerprint=str(short_population.fingerprint),
        split_ref=short_population.split_ref,
    )
    short_request = changed(
        q, identity=identity, participants=participants, population=short_population
    )
    supplied = evaluation_input(q)
    short_sets = tuple(
        changed(
            forecast_set,
            participant=participant_view,
            population_fingerprint=str(short_population.fingerprint),
            observations=forecast_set.observations[:4],
        )
        for forecast_set, participant_view in zip(supplied.forecast_sets, participants, strict=True)
    )
    short_truth = changed(
        supplied.ground_truth,
        population_fingerprint=str(short_population.fingerprint),
        observations=supplied.ground_truth.observations[:4],
    )
    short_input = changed(
        supplied,
        request=short_request,
        forecast_sets=short_sets,
        ground_truth=short_truth,
    )
    result = service.evaluate_normalized(short_request, short_input)
    assert result.status == "INSUFFICIENT_SUPPORT"
    assert result.statistics.status == "NOT_ESTIMABLE"
    assert result.statistics.brier_interval is None


@pytest.mark.parametrize("field", ["target", "population", "mode", "truth", "pairing"])
def test_request_rejects_incompatible_identity(field: str) -> None:
    q = request()
    updates: dict[str, Any]
    if field == "target":
        participant = changed(q.participants[1], target=changed(target(), horizon="synthetic:two"))
        updates = {"participants": (q.participants[0], participant)}
    elif field == "population":
        updates = {"population": changed(q.population, observation_ids=OBSERVATIONS[:-1])}
    elif field == "mode":
        participant = changed(
            q.participants[1], realization_mode=ForecastRealizationMode.ACTUAL_ISSUANCE
        )
        updates = {"participants": (q.participants[0], participant)}
    elif field == "truth":
        updates = {
            "ground_truth": changed(
                q.ground_truth, target=changed(q.ground_truth.target, target_version="2.0")
            )
        }
    else:
        updates = {
            "pairing": changed(
                q.pairing, participant_ids=tuple(reversed(q.pairing.participant_ids))
            )
        }
    with pytest.raises(ValidationError, match="MISMATCH|INCOMPATIBLE"):
        changed(q, **updates)


def test_external_truth_is_required_and_labels_are_not_reconstructed() -> None:
    q = request()
    supplied = evaluation_input(q)
    row = supplied.ground_truth.observations[0]
    with pytest.raises(ValidationError):
        changed(row, journal_entry_ref=None)
    with pytest.raises(ValidationError):
        changed(row, reference_price=100.0, terminal_price=101.0)
    assert supplied.ground_truth.labels_supplied_externally
    assert supplied.ground_truth.identity.ownership == "EXTERNAL_EVALUATION_OUTCOME_JOURNAL"


@pytest.mark.parametrize("value", [-0.1, 1.1, float("nan"), float("inf"), True, "0.5"])
def test_invalid_probability_is_rejected(value: Any) -> None:
    row = evaluation_input(request()).forecast_sets[0].observations[0]
    with pytest.raises(ValidationError):
        changed(row, probability=value)


@pytest.mark.parametrize(
    "updates",
    [
        {"trains_models": True},
        {"selects_optimizer_candidate": True},
        {"fits_or_applies_calibration": True},
        {"runs_diagnostics": True},
        {"grants_approval": True},
        {"grants_promotion": True},
        {"grants_activation": True},
    ],
)
def test_request_cannot_cross_authority_boundaries(updates: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        changed(request(), **updates)


@pytest.mark.parametrize(
    "updates",
    [
        {"scientific_decision": "SUPPORTED"},
        {"optimizer_selection": True},
        {"approval": True},
        {"promotion": True},
        {"activation": True},
        {"diagnostic_verdict": "HEALTHY"},
    ],
)
def test_result_cannot_become_decision_or_lifecycle_authority(updates: dict[str, Any]) -> None:
    q = request()
    result = service.evaluate_normalized(q, evaluation_input(q))
    with pytest.raises(ValidationError):
        changed(result, **updates)


def test_consumed_population_cannot_enter_executable_request() -> None:
    q = request()
    consumed = changed(q.population, protection_state="CONSUMED_HISTORICAL")
    with pytest.raises(ValidationError, match="MISMATCH"):
        changed(q, population=consumed)


def test_input_grid_order_and_clock_are_pinned() -> None:
    q = request()
    supplied = evaluation_input(q)
    first = supplied.forecast_sets[0]
    reversed_first = changed(first, observations=tuple(reversed(first.observations)))
    with pytest.raises(ValidationError, match="POPULATION"):
        changed(supplied, forecast_sets=(reversed_first, supplied.forecast_sets[1]))
    with pytest.raises(ValidationError):
        changed(supplied, captured_at=AT.replace(tzinfo=None))
    with pytest.raises(ValidationError, match="CLOSURE"):
        changed(supplied, captured_at=AT - timedelta(seconds=1))


@pytest.mark.parametrize(
    "updates",
    [
        {"unseen_claim": True},
        {"protected_claim": True},
        {"evaluation_execution_authorized": True},
        {"use_classification": "SYNTHETIC_REFERENCE"},
    ],
)
def test_consumed_holdout_cannot_be_recycled(updates: dict[str, Any]) -> None:
    historical = EvidenceUseDeclaration(
        evidence_ref=synthetic_reference("ff1-2025-recorded-view"),
        source_experiment_id="experiment:ff1",
        requesting_experiment_id="experiment:ff1",
        source_state="CONSUMED_HISTORICAL",
        use_classification="HISTORICAL_REPLAY_ONLY",
        evaluation_execution_authorized=False,
    )
    with pytest.raises(ValidationError):
        changed(historical, **updates)


def test_consumed_holdout_in_new_experiment_is_development_known() -> None:
    use = EvidenceUseDeclaration(
        evidence_ref=synthetic_reference("ff1-2025-recorded-view"),
        source_experiment_id="experiment:ff1",
        requesting_experiment_id="experiment:new-study",
        source_state="CONSUMED_HISTORICAL",
        use_classification="DEVELOPMENT_KNOWN",
        evaluation_execution_authorized=False,
    )
    assert use.use_classification == "DEVELOPMENT_KNOWN"
    assert not use.unseen_claim and not use.protected_claim
    with pytest.raises(ValidationError):
        changed(use, use_classification="HISTORICAL_REPLAY_ONLY")


def test_unknown_counts_cannot_masquerade_as_zero() -> None:
    assert KnownCount(status="UNKNOWN", value=None).value is None
    with pytest.raises(ValidationError, match="NOT_ZERO"):
        KnownCount(status="UNKNOWN", value=0)
    with pytest.raises(ValidationError):
        CoverageAccounting.model_validate(
            {
                "requested": {"status": "UNKNOWN", "value": None},
                "participant_availability": [],
                "ground_truth_available": {"status": "UNKNOWN", "value": None},
                "paired_eligible": {"status": "UNKNOWN", "value": None},
                "evaluated": {"status": "UNKNOWN", "value": None},
                "protected_excluded": {"status": "UNKNOWN", "value": None},
                "consumed_excluded": {"status": "UNKNOWN", "value": None},
                "exclusions_by_reason": [],
                "dispositions": [],
                "coverage": 0.0,
            }
        )


def test_identity_json_timezone_and_immutability() -> None:
    q = request()
    restored = EvaluationRequest.model_validate_json(q.model_dump_json())
    assert restored == q
    assert q.model_dump(mode="json")["created_at"].endswith("+05:30")
    assert isinstance(q.model_dump(mode="json")["participants"], list)
    with pytest.raises(ValidationError):
        q.request_id = "evaluation:changed"
    with pytest.raises(ValidationError):
        changed(q, created_at=AT.replace(tzinfo=None))
    assert canonical_json(q) == canonical_json(restored)
    result = service.evaluate_normalized(q, evaluation_input(q))
    assert isinstance(result.model_dump(mode="json")["metrics"]["values"], list)
    assert result.created_at.isoformat().endswith("+05:30")


def test_persistence_replay_idempotence_and_semantic_tamper(
    store: service.NormalizedEvaluationStore,
) -> None:
    q = request()
    supplied = evaluation_input(q)
    ledger_ref = service.persist_normalized_evaluation(store, supplied)
    assert (
        service.replay_normalized_evaluation(
            service.NormalizedEvaluationStore(store.root), ledger_ref
        )
        == "MATCH"
    )
    assert service.persist_normalized_evaluation(store, supplied) == ledger_ref

    ledger = store.resolve(ledger_ref)
    assert isinstance(ledger, NormalizedEvaluationLedger)
    result = store.resolve(ledger.result)
    assert isinstance(result, NormalizedEvaluationResult)
    first = result.metrics.values[0]
    forged_value = changed(first, value=cast_float(first.value) + 0.01)
    forged_metrics = changed(result.metrics, values=(forged_value, *result.metrics.values[1:]))
    forged_result = changed(result, metrics=forged_metrics)
    store.put("evalmetrics", forged_metrics)
    store.put("evalresult", forged_result)
    forged_ledger = changed(
        ledger,
        metrics=service.reference("evalmetrics", forged_metrics),
        result=service.reference("evalresult", forged_result),
    )
    store.put("evalledger", forged_ledger)
    assert (
        service.replay_normalized_evaluation(
            service.NormalizedEvaluationStore(store.root),
            service.reference("evalledger", forged_ledger),
        )
        == "MISMATCH"
    )


def cast_float(value: float | None) -> float:
    assert value is not None
    return value


def test_replay_has_no_write_fit_network_provider_or_broker(
    store: service.NormalizedEvaluationStore, monkeypatch: pytest.MonkeyPatch
) -> None:
    q = request()
    ledger_ref = service.persist_normalized_evaluation(store, evaluation_input(q))
    before = {path.name: path.read_bytes() for path in store.root.iterdir()}

    def forbidden(*args: Any, **kwargs: Any) -> None:
        pytest.fail("offline evaluation replay crossed an external boundary")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(service.NormalizedEvaluationStore, "put", forbidden)
    assert (
        service.replay_normalized_evaluation(
            service.NormalizedEvaluationStore(store.root), ledger_ref
        )
        == "MATCH"
    )
    assert before == {path.name: path.read_bytes() for path in store.root.iterdir()}


def _legacy_records() -> tuple[FinalProtocol, FinalExecution, FinalEvaluation, FinalLedger]:
    root = Path("data/ff1/final_holdout_20260922")
    return (
        FinalProtocol.model_validate_json(next(root.glob("protocol-*.json")).read_text()),
        FinalExecution.model_validate_json(next(root.glob("execution-*.json")).read_text()),
        FinalEvaluation.model_validate_json(next(root.glob("evaluation-*.json")).read_text()),
        FinalLedger.model_validate_json(next(root.glob("ledger-*.json")).read_text()),
    )


def test_legacy_ff1_readonly_view_preserves_recorded_semantics() -> None:
    protocol, execution, evaluation, ledger = _legacy_records()
    view = service.adapt_legacy_ff1_final(protocol, execution, evaluation, ledger)
    assert view.protocol_fingerprint == protocol.fingerprint
    assert view.execution_fingerprint == execution.fingerprint
    assert view.evaluation_fingerprint == evaluation.fingerprint
    assert view.ledger_fingerprint == ledger.fingerprint
    assert view.classification == "INSUFFICIENT_EVIDENCE"
    assert view.scientific_reason == "CONFIDENCE_NONDECISIVE"
    assert view.evidence_state == "HISTORICAL_ACCEPTED_CONSUMED"
    assert not view.evaluation_reexecuted and not view.reclassified_as_unseen
    assert view.semantics == "READ_ONLY_VIEW_NO_METRIC_RECOMPUTATION"


def test_legacy_ff1_adapter_rejects_changed_identity_or_conclusion() -> None:
    protocol, execution, evaluation, ledger = _legacy_records()
    with pytest.raises(ValueError, match="LEGACY"):
        service.adapt_legacy_ff1_final(
            protocol,
            execution,
            evaluation,
            changed(ledger, evaluation="0" * 64),
        )


def test_no_duplicate_owner_or_cross_boundary_calls() -> None:
    tree = ast.parse(Path(service.__file__).read_text())
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert "tiaf.evaluation.forecast_comparison_metrics" in imports
    assert "tiaf.forecasting.logistic_store" in imports
    assert not any(
        boundary in module
        for module in imports
        for boundary in (
            "learning.forecaster_training",
            "learning.optimization",
            "learning.calibration",
            "learning.forecaster_diagnostics",
            "forecaster_lifecycle",
            "providers",
            "brokers",
        )
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr
        in ("fit", "train", "select", "optimize", "calibrate", "approve", "promote", "activate")
        for node in ast.walk(tree)
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "now"
        for node in ast.walk(tree)
    )
