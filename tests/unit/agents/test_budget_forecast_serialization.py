"""Budgets, forecast boundary, reasoning protocol, and run serialization tests."""

import pytest
from pydantic import ValidationError

from tiaf.agents import (
    AgentBudget,
    AgentBudgetExceededError,
    AgentRegistry,
    AgentRunRecord,
    AgentRuntime,
    AgentUsage,
    CalibrationStatus,
    ForecastEvidence,
    ForecastQuantile,
    ForecastValidationMetric,
    ReasoningField,
    ReasoningModelIdentity,
    ReasoningProvider,
    ReasoningRequest,
    ReasoningResponse,
    ReasoningStatus,
    agent_record_json,
    load_agent_record_json,
)
from tiaf.contracts import Horizon

from ._support import NOW, DummySpecialist, StepClock, agent_request, evidence_pack


@pytest.mark.parametrize(
    ("field", "actual"),
    [
        ("llm_calls", 1),
        ("tool_calls", 1),
        ("input_tokens", 1),
        ("output_tokens", 1),
        ("cost_units", 0.1),
        ("elapsed_seconds", 30.1),
    ],
)
def test_budget_reports_each_exceeded_dimension(field: str, actual: float) -> None:
    usage = AgentUsage.model_validate({field: actual})
    budget = AgentBudget()
    assert field in budget.violations(usage)
    with pytest.raises(AgentBudgetExceededError, match=field):
        budget.ensure_within(usage)


def test_usage_rejects_negative_or_non_finite_values() -> None:
    with pytest.raises(ValidationError):
        AgentUsage(tool_calls=-1)
    with pytest.raises(ValidationError):
        AgentUsage(cost_units=float("inf"))


def calibrated_forecast() -> ForecastEvidence:
    return ForecastEvidence(
        forecast_id="forecast-1",
        subject="RELIANCE",
        horizon=Horizon(label="six months", max_days=183),
        reference_price=1_300.0,
        return_quantiles=(
            ForecastQuantile(probability=0.1, return_pct=-12.0),
            ForecastQuantile(probability=0.5, return_pct=8.0),
            ForecastQuantile(probability=0.9, return_pct=28.0),
        ),
        expected_return_pct=9.0,
        median_return_pct=8.0,
        model_id="forecast-model",
        model_version="1.0",
        training_window_start=NOW.replace(year=2020),
        training_window_end=NOW.replace(year=2026, month=8),
        calibration_status=CalibrationStatus.CALIBRATED,
        calibration_id="calibration-1",
        calibration_method="held-out-isotonic",
        calibration_sample_size=500,
        validation_metrics=(ForecastValidationMetric(name="brier", value=0.18),),
        regime_applicability="Indian large-cap equities",
        evidence_snapshot_reference="snapshot-1",
        created_at=NOW,
        valid_until=NOW.replace(month=10),
    )


def test_forecast_contract_preserves_calibration_without_generating_it() -> None:
    forecast = calibrated_forecast()
    payload = forecast.model_dump(mode="json")
    assert forecast.calibration_status is CalibrationStatus.CALIBRATED
    assert isinstance(payload["return_quantiles"], list)
    assert ForecastEvidence.model_validate(payload) == forecast


def test_forecast_rejects_calibrated_label_without_evidence() -> None:
    payload = calibrated_forecast().model_dump(mode="python")
    payload["validation_metrics"] = ()
    with pytest.raises(ValidationError, match="requires validation metrics"):
        ForecastEvidence.model_validate(payload)


def test_forecast_rejects_unsorted_or_duplicate_quantiles() -> None:
    payload = calibrated_forecast().model_dump(mode="python")
    payload["return_quantiles"] = tuple(reversed(payload["return_quantiles"]))
    with pytest.raises(ValidationError, match="must be sorted"):
        ForecastEvidence.model_validate(payload)


class FakeReasoningProvider:
    def identity(self) -> ReasoningModelIdentity:
        return ReasoningModelIdentity(
            provider_id="fake",
            model_id="fake-model",
            configuration_id="config-1",
        )

    def reason(self, request: ReasoningRequest) -> ReasoningResponse:
        return ReasoningResponse(
            response_id="response-1",
            reasoning_request_id=request.reasoning_request_id,
            provider_id="fake",
            model_id="fake-model",
            status=ReasoningStatus.SUCCESS,
            fields=(ReasoningField(name="summary", value="structured"),),
            usage=AgentUsage(llm_calls=1, input_tokens=10, output_tokens=2),
            completed_at=NOW,
        )


def test_reasoning_provider_protocol_is_sdk_neutral_and_runtime_checkable() -> None:
    provider = FakeReasoningProvider()
    assert isinstance(provider, ReasoningProvider)
    assert provider.identity().provider_id == "fake"


def test_agent_run_record_serializes_deterministically_and_round_trips() -> None:
    runtime = AgentRuntime(
        AgentRegistry((DummySpecialist(),)),
        wall_clock=lambda: NOW,
        elapsed_clock=StepClock(0.0, 0.25),
    )
    record = runtime.run(agent_request(), evidence_pack())
    encoded = agent_record_json(record, indent=None)
    decoded = load_agent_record_json(encoded)
    assert decoded == record
    assert encoded == agent_record_json(record, indent=None)
    payload = decoded.model_dump(mode="json")
    assert payload["started_at"].endswith("+05:30")
    assert isinstance(payload["evidence_pack"]["references"], list)
    assert AgentRunRecord.model_validate(payload) == record


def test_reasoning_response_rejects_failure_disguised_as_success() -> None:
    payload = ReasoningResponse(
        response_id="response-1",
        reasoning_request_id="reasoning-1",
        provider_id="fake",
        model_id="fake-model",
        status=ReasoningStatus.SUCCESS,
        fields=(ReasoningField(name="summary", value="structured"),),
        usage=AgentUsage(llm_calls=1),
        completed_at=NOW,
    ).model_dump(mode="python")
    payload["fields"] = ()
    with pytest.raises(ValidationError, match="successful reasoning"):
        ReasoningResponse.model_validate(payload)
