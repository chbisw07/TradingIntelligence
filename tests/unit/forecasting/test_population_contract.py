"""FF-0 defines A7 §9.1 partitions; no empirical report or metric is produced."""

import pytest
from pydantic import ValidationError

from tiaf.evaluation.forecast_contracts import (
    EvaluationPopulationDispositionReport,
    MetricDisposition,
    MetricDispositionCounts,
    PopulationObservation,
)
from tiaf.forecasting.enums import ForecastRealizationMode, PopulationDisposition

from ._support import instant, ref, request
from .test_contracts import changed


def specimen() -> EvaluationPopulationDispositionReport:
    return EvaluationPopulationDispositionReport(
        report_id="report:synthetic-shape",
        manifest_ref=ref("population"),
        split_ref=ref("split"),
        target=request().target,
        label_policy_ref=ref("label-policy"),
        metric_policy_ref=ref("metric-policy"),
        mode_policy_ref=ref("mode-policy"),
        weighting_policy_ref=ref("weights"),
        evaluation_as_of=instant(7, 12),
        observations=(
            PopulationObservation(
                observation_id="observation:one",
                request_ids=("request:one", "request:duplicate"),
                source_run_refs=(ref("run"),),
                journal_revision_refs=(),
                realization_mode=ForecastRealizationMode.SIMULATED_ISSUANCE,
            ),
        ),
        metric_ids=("metric:brier",),
        arm_ids=("arm:baseline",),
        dispositions=(
            MetricDisposition(
                observation_id="observation:one",
                metric_id="metric:brier",
                arm_id="arm:baseline",
                disposition=PopulationDisposition.NOT_EVALUABLE,
                primary_reason="reason:missing-outcome",
                contributing_reasons=("reason:missing-outcome",),
                source_facet_refs=(ref("absence"),),
            ),
        ),
        counts=(
            MetricDispositionCounts(
                metric_id="metric:brier",
                arm_id="arm:baseline",
                included=0,
                excluded=0,
                not_evaluable=1,
            ),
        ),
        requested_count=2,
        unique_observation_count=1,
        population_complete=True,
    )


def test_population_shape_roundtrip_keeps_request_vs_observation_counts() -> None:
    report = specimen()
    assert report.requested_count == 2 and report.unique_observation_count == 1
    assert (
        EvaluationPopulationDispositionReport.model_validate_json(report.model_dump_json())
        == report
    )
    assert isinstance(report.observations, tuple)
    assert isinstance(report.model_dump(mode="json")["dispositions"], list)


@pytest.mark.parametrize(
    "changes",
    [
        {"requested_count": 1},
        {"unique_observation_count": 2},
        {"dispositions": []},
        {"counts": []},
        {"counts.0.included": 1},
        {"metric_ids": ["metric:brier", "metric:coverage"]},
        {"arm_ids": ["arm:baseline", "arm:baseline"]},
        {"observations.0.request_ids": ["request:one", "request:one"]},
        {"dispositions.0.observation_id": "observation:missing"},
        {"dispositions.0.contributing_reasons": []},
        {"unresolved_refs": ["input:unresolved"]},
        {"forecast_available_observation_ids": ["observation:missing"]},
        {"label_mature_observation_ids": ["observation:one", "observation:one"]},
    ],
)
def test_population_contract_rejects_incomplete_or_double_denominators(
    changes: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        EvaluationPopulationDispositionReport.model_validate(changed(specimen(), changes))


def test_unmapped_request_retained_without_complete_population_claim() -> None:
    report = EvaluationPopulationDispositionReport.model_validate(
        changed(
            specimen(),
            {
                "unmapped_request_ids": ["request:unmapped"],
                "requested_count": 3,
                "population_complete": False,
                "unresolved_refs": ["input:missing"],
            },
        )
    )
    assert report.requested_count == 3 and report.unique_observation_count == 1
