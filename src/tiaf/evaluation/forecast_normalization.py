"""FLC-6 adapter inside the existing independent Evaluation owner.

The executable profile is an authored synthetic reference.  Legacy FF-1 support
is a read-only projection of recorded evidence, never a second evaluation run.
"""

import math
from collections import Counter
from types import MappingProxyType
from typing import Literal, cast

from tiaf.evaluation.forecast_comparison_metrics import bootstrap, losses
from tiaf.evaluation.forecast_final_protocol import FinalProtocol
from tiaf.evaluation.forecast_final_scoring import FinalEvaluation
from tiaf.evaluation.forecast_final_store import FinalExecution, FinalLedger
from tiaf.forecasting.enums import PopulationDisposition
from tiaf.forecasting.identity import ArtifactReference
from tiaf.forecasting.logistic_store import ResearchForecastStore
from tiaf.learning.forecast_artifacts import SealedResearch

from .forecast_normalization_contracts import (
    CoverageAccounting,
    EvaluationDisposition,
    EvaluationInput,
    EvaluationPopulation,
    EvaluationRequest,
    KnownCount,
    LegacyFF1EvaluationView,
    MetricBundle,
    MetricValue,
    NormalizedEvaluationLedger,
    NormalizedEvaluationResult,
    PairedLossObservation,
    PairedTable,
    ParticipantAvailability,
    StatisticalSummary,
)


def reference(kind: str, value: SealedResearch) -> ArtifactReference:
    assert value.fingerprint is not None
    return ArtifactReference(
        artifact_id=f"flc6:{kind}",
        artifact_version=value.schema_version,
        fingerprint=value.fingerprint,
    )


class NormalizedEvaluationStore(ResearchForecastStore):
    """Codec profile on the accepted content-addressed research store."""

    record_types = MappingProxyType(
        {
            **ResearchForecastStore.record_types,
            "evalpopulation": EvaluationPopulation,
            "evalrequest": EvaluationRequest,
            "evalinput": EvaluationInput,
            "evalpairtable": PairedTable,
            "evalmetrics": MetricBundle,
            "evalstatistics": StatisticalSummary,
            "evalresult": NormalizedEvaluationResult,
            "evalledger": NormalizedEvaluationLedger,
            "evallegacyview": LegacyFF1EvaluationView,
        }
    )

    def resolve(self, ref: ArtifactReference) -> SealedResearch:
        ref = ArtifactReference.model_validate(ref.model_dump())
        prefix, _, kind = ref.artifact_id.partition(":")
        if prefix != "flc6" or kind not in self.record_types:
            raise ValueError("UNKNOWN_NORMALIZED_EVALUATION_REFERENCE")
        value = self.get(kind, ref.fingerprint)
        if reference(kind, value) != ref:
            raise ValueError("NORMALIZED_EVALUATION_REFERENCE_MISMATCH")
        return value


def _ece(values: tuple[tuple[float, int], ...]) -> float:
    if not values:
        raise ValueError("ECE_REQUIRES_OBSERVATIONS")
    result = 0.0
    for index in range(10):
        rows = tuple((p, y) for p, y in values if min(9, int(p * 10)) == index)
        if rows:
            mean_p = math.fsum(p for p, _ in rows) / len(rows)
            mean_y = sum(y for _, y in rows) / len(rows)
            result += len(rows) / len(values) * abs(mean_p - mean_y)
    return result


def _metric_value(
    participant_id: str,
    metric_id: Literal["BRIER", "NATURAL_LOG_LOSS", "ACCURACY", "ECE_FIXED_10"],
    metric_version: str,
    tier: Literal["PRIMARY", "SECONDARY_DESCRIPTIVE", "DIAGNOSTIC_ONLY"],
    values: tuple[tuple[float, int], ...],
) -> MetricValue:
    if not values:
        return MetricValue(
            participant_id=participant_id,
            metric_id=metric_id,
            metric_version=metric_version,
            tier=tier,
            status="UNDEFINED",
            value=None,
            evaluated_count=0,
            reason="evaluation:no-eligible-observations",
        )
    loss = tuple(losses(p, y) for p, y in values)
    metric = {
        "BRIER": lambda: math.fsum(item[0] for item in loss) / len(values),
        "NATURAL_LOG_LOSS": lambda: math.fsum(item[1] for item in loss) / len(values),
        "ACCURACY": lambda: sum(int(p >= 0.5) == y for p, y in values) / len(values),
        "ECE_FIXED_10": lambda: _ece(values),
    }.get(metric_id)
    if metric is None:
        raise ValueError("EVALUATION_METRIC_IMPLEMENTATION_UNSUPPORTED")
    return MetricValue(
        participant_id=participant_id,
        metric_id=metric_id,
        metric_version=metric_version,
        tier=tier,
        status="COMPUTED",
        value=metric(),
        evaluated_count=len(values),
        reason="evaluation:computed-under-pinned-policy",
    )


def evaluate_normalized(
    request: EvaluationRequest, supplied: EvaluationInput
) -> NormalizedEvaluationResult:
    """Evaluate supplied forecasts and external labels; never infer, fit, or decide."""
    request = EvaluationRequest.model_validate(request.model_dump())
    supplied = EvaluationInput.model_validate(supplied.model_dump())
    if supplied.request != request:
        raise ValueError("EVALUATION_INPUT_REQUEST_MISMATCH")

    population_ids = request.population.observation_ids
    forecast_maps = {
        forecast_set.participant.participant_id: {
            item.observation_id: item for item in forecast_set.observations
        }
        for forecast_set in supplied.forecast_sets
    }
    truth_map = {item.observation_id: item for item in supplied.ground_truth.observations}
    dispositions: list[EvaluationDisposition] = []
    included_ids: list[str] = []
    exclusion_reasons: list[str] = []
    for observation_id in population_ids:
        available = tuple(
            participant.participant_id
            for participant in request.participants
            if forecast_maps[participant.participant_id][observation_id].status == "AVAILABLE"
        )
        truth = truth_map[observation_id]
        reasons = [
            forecast_maps[participant.participant_id][observation_id].reason
            for participant in request.participants
            if forecast_maps[participant.participant_id][observation_id].status != "AVAILABLE"
        ]
        if truth.status != "AVAILABLE":
            reasons.append(truth.reason)
        included = len(available) == len(request.participants) and truth.status == "AVAILABLE"
        if included:
            included_ids.append(observation_id)
            reasons = ["evaluation:included"]
        else:
            exclusion_reasons.extend(reasons)
        dispositions.append(
            EvaluationDisposition(
                observation_id=observation_id,
                available_participant_ids=available,
                truth_available=truth.status == "AVAILABLE",
                disposition=(
                    PopulationDisposition.INCLUDED
                    if included
                    else PopulationDisposition.NOT_EVALUABLE
                ),
                reasons=tuple(reasons),
            )
        )

    availability = tuple(
        ParticipantAvailability(
            participant_id=participant.participant_id,
            available=KnownCount(
                status="KNOWN",
                value=sum(
                    row.status == "AVAILABLE"
                    for row in forecast_maps[participant.participant_id].values()
                ),
            ),
        )
        for participant in request.participants
    )
    requested_count = len(population_ids)
    evaluated_count = len(included_ids)
    coverage = CoverageAccounting(
        requested=KnownCount(status="KNOWN", value=requested_count),
        participant_availability=availability,
        ground_truth_available=KnownCount(
            status="KNOWN", value=sum(row.status == "AVAILABLE" for row in truth_map.values())
        ),
        paired_eligible=KnownCount(status="KNOWN", value=evaluated_count),
        evaluated=KnownCount(status="KNOWN", value=evaluated_count),
        protected_excluded=KnownCount(status="KNOWN", value=0),
        consumed_excluded=KnownCount(status="KNOWN", value=0),
        exclusions_by_reason=tuple(sorted(Counter(exclusion_reasons).items())),
        dispositions=tuple(dispositions),
        coverage=evaluated_count / requested_count,
    )

    participant_values: dict[str, tuple[tuple[float, int], ...]] = {}
    for participant in request.participants:
        rows = []
        for observation_id in included_ids:
            forecast = forecast_maps[participant.participant_id][observation_id]
            truth = truth_map[observation_id]
            assert forecast.probability is not None and truth.label is not None
            rows.append((forecast.probability, truth.label))
        participant_values[participant.participant_id] = tuple(rows)
    metric_values = tuple(
        _metric_value(
            participant.participant_id,
            metric.metric_id,
            metric.metric_version,
            metric.tier,
            participant_values[participant.participant_id],
        )
        for participant in request.participants
        for metric in request.metric_set.metrics
    )
    metrics = MetricBundle(metric_set=request.metric_set, values=metric_values)

    pair_table = None
    if request.pairing.mode == "PAIRED_COMPARISON":
        first, second = request.participants
        pair_rows: list[PairedLossObservation] = []
        for observation_id in included_ids:
            one = forecast_maps[first.participant_id][observation_id]
            two = forecast_maps[second.participant_id][observation_id]
            truth = truth_map[observation_id]
            assert one.probability is not None and one.forecast_ref is not None
            assert two.probability is not None and two.forecast_ref is not None
            assert truth.label is not None and truth.journal_entry_ref is not None
            first_loss = losses(one.probability, truth.label)
            second_loss = losses(two.probability, truth.label)
            pair_rows.append(
                PairedLossObservation(
                    observation_id=observation_id,
                    ground_truth_ref=truth.journal_entry_ref,
                    first_forecast_ref=one.forecast_ref,
                    second_forecast_ref=two.forecast_ref,
                    label=cast(Literal[0, 1], truth.label),
                    first_probability=one.probability,
                    second_probability=two.probability,
                    first_brier=first_loss[0],
                    second_brier=second_loss[0],
                    brier_difference=second_loss[0] - first_loss[0],
                    first_log_loss=first_loss[1],
                    second_log_loss=second_loss[1],
                    log_loss_difference=second_loss[1] - first_loss[1],
                )
            )
        pair_table = PairedTable(
            pairing=request.pairing,
            population_fingerprint=cast(str, request.population.fingerprint),
            rows=tuple(pair_rows),
        )
        lookup = {row.observation_id: row for row in pair_rows}
        grid = tuple(
            None
            if observation_id not in lookup
            else (
                lookup[observation_id].brier_difference,
                lookup[observation_id].log_loss_difference,
            )
            for observation_id in population_ids
        )
        if len(grid) < request.statistics.block_length:
            statistics = StatisticalSummary(
                policy=request.statistics,
                status="NOT_ESTIMABLE",
                effective_n=evaluated_count,
                brier_difference=None,
                log_loss_difference=None,
                brier_interval=None,
                log_loss_interval=None,
                sampled_indices_fingerprint=None,
            )
        else:
            sampled = bootstrap((grid,))
            statistics = StatisticalSummary(
                policy=request.statistics,
                status=sampled.status,
                effective_n=sampled.effective_n,
                brier_difference=None if sampled.point is None else sampled.point[0],
                log_loss_difference=None if sampled.point is None else sampled.point[1],
                brier_interval=sampled.brier_interval,
                log_loss_interval=sampled.logloss_interval,
                sampled_indices_fingerprint=sampled.sampled_indices_fingerprint,
            )
    else:
        statistics = StatisticalSummary(
            policy=request.statistics,
            status="NOT_APPLICABLE",
            effective_n=evaluated_count,
            brier_difference=None,
            log_loss_difference=None,
            brier_interval=None,
            log_loss_interval=None,
            sampled_indices_fingerprint=None,
        )

    sufficient = evaluated_count >= request.statistics.minimum_support
    limitations = ["evaluation:synthetic-reference-not-empirical-evidence"]
    if not sufficient:
        limitations.append("evaluation:minimum-support-not-met")
    return NormalizedEvaluationResult(
        request=request,
        input_reference=reference("evalinput", supplied),
        status="GENERATED" if sufficient else "INSUFFICIENT_SUPPORT",
        population_fingerprint=cast(str, request.population.fingerprint),
        ground_truth_fingerprint=cast(str, request.ground_truth.fingerprint),
        coverage=coverage,
        metrics=metrics,
        paired_table=pair_table,
        statistics=statistics,
        limitations=tuple(limitations),
        created_at=supplied.captured_at,
    )


def persist_normalized_evaluation(
    store: NormalizedEvaluationStore, supplied: EvaluationInput
) -> ArtifactReference:
    """Persist the normalized closure through the existing bounded store."""
    if not store.writable:
        raise ValueError("NORMALIZED_EVALUATION_STORE_READ_ONLY")
    supplied = EvaluationInput.model_validate(supplied.model_dump())
    result = evaluate_normalized(supplied.request, supplied)
    population_ref = reference("evalpopulation", supplied.request.population)
    request_ref = reference("evalrequest", supplied.request)
    input_ref = reference("evalinput", supplied)
    for kind, value in (
        ("evalpopulation", supplied.request.population),
        ("evalrequest", supplied.request),
        ("evalinput", supplied),
    ):
        store.put(kind, value)
    pair_ref = None
    if result.paired_table is not None:
        store.put("evalpairtable", result.paired_table)
        pair_ref = reference("evalpairtable", result.paired_table)
    store.put("evalmetrics", result.metrics)
    store.put("evalstatistics", result.statistics)
    store.put("evalresult", result)
    ledger = NormalizedEvaluationLedger(
        request=request_ref,
        population=population_ref,
        evaluation_input=input_ref,
        paired_table=pair_ref,
        metrics=reference("evalmetrics", result.metrics),
        statistics=reference("evalstatistics", result.statistics),
        result=reference("evalresult", result),
        completed_at=result.created_at,
    )
    store.put("evalledger", ledger)
    return reference("evalledger", ledger)


def replay_normalized_evaluation(
    store: NormalizedEvaluationStore, ledger_reference: ArtifactReference
) -> Literal["MATCH", "MISMATCH"]:
    """Recompute from captured rows and policies only; no external operation."""
    try:
        ledger = store.resolve(ledger_reference)
        if not isinstance(ledger, NormalizedEvaluationLedger):
            raise ValueError("NORMALIZED_EVALUATION_LEDGER_REQUIRED")
        request = store.resolve(ledger.request)
        population = store.resolve(ledger.population)
        supplied = store.resolve(ledger.evaluation_input)
        result = store.resolve(ledger.result)
        metrics = store.resolve(ledger.metrics)
        statistics = store.resolve(ledger.statistics)
        if (
            not isinstance(request, EvaluationRequest)
            or not isinstance(population, EvaluationPopulation)
            or not isinstance(supplied, EvaluationInput)
            or not isinstance(result, NormalizedEvaluationResult)
            or request.population != population
            or supplied.request != request
        ):
            raise ValueError("NORMALIZED_EVALUATION_REPLAY_CLOSURE_MISMATCH")
        expected = evaluate_normalized(request, supplied)
        if result != expected or metrics != expected.metrics or statistics != expected.statistics:
            raise ValueError("NORMALIZED_EVALUATION_REPLAY_RESULT_MISMATCH")
        if ledger.paired_table is None:
            if expected.paired_table is not None:
                raise ValueError("NORMALIZED_EVALUATION_REPLAY_PAIR_MISSING")
        elif store.resolve(ledger.paired_table) != expected.paired_table:
            raise ValueError("NORMALIZED_EVALUATION_REPLAY_PAIR_MISMATCH")
        return "MATCH"
    except (OSError, ValueError, LookupError, AssertionError):
        return "MISMATCH"


def adapt_legacy_ff1_final(
    protocol: FinalProtocol,
    execution: FinalExecution,
    evaluation: FinalEvaluation,
    ledger: FinalLedger,
) -> LegacyFF1EvaluationView:
    """Map recorded identities/conclusion only; do not score or verify the holdout."""
    protocol = FinalProtocol.model_validate(protocol.model_dump())
    execution = FinalExecution.model_validate(execution.model_dump())
    evaluation = FinalEvaluation.model_validate(evaluation.model_dump())
    ledger = FinalLedger.model_validate(ledger.model_dump())
    if (
        execution.protocol_fingerprint != protocol.fingerprint
        or evaluation.protocol != protocol
        or evaluation.execution_fingerprint != execution.fingerprint
        or ledger.protocol != protocol.fingerprint
        or ledger.execution != execution.fingerprint
        or ledger.evaluation != evaluation.fingerprint
        or ledger.state != "COMPLETE"
        or ledger.replay != "MATCH"
        or evaluation.holdout_status != "CONSUMED"
        or not evaluation.one_shot_consumed
        or evaluation.executions_used != 1
        or evaluation.post_holdout_refit_allowed
        or evaluation.automatic_promotion
        or evaluation.decision.classification != "INSUFFICIENT_EVIDENCE"
        or evaluation.decision.reasons != ("CONFIDENCE_NONDECISIVE",)
    ):
        raise ValueError("FF1_LEGACY_EVALUATION_VIEW_MISMATCH")
    return LegacyFF1EvaluationView(
        protocol_fingerprint=protocol.fingerprint,
        execution_fingerprint=execution.fingerprint,
        evaluation_fingerprint=evaluation.fingerprint,
        ledger_fingerprint=cast(str, ledger.fingerprint),
        paired_population_fingerprint=evaluation.paired_population_fingerprint,
        ground_truth_fingerprint=evaluation.ground_truth_fingerprint,
        metric_policy_fingerprint=cast(str, protocol.policy.fingerprint),
        classification="INSUFFICIENT_EVIDENCE",
        scientific_reason="CONFIDENCE_NONDECISIVE",
        created_at=evaluation.created_at,
    )
