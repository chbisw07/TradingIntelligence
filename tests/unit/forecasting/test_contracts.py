"""FF0-01/02/03/10/14/15: shape, scope, frozen collections and no authority."""

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from tiaf.evaluation.forecast_contracts import ForecastTargetSpec, ForecastWindow
from tiaf.forecasting.contracts import (
    BinaryProbabilityOutput,
    ForecastAbsence,
    ForecastComposition,
    ForecastRequest,
    ForecastResult,
)
from tiaf.forecasting.enums import ForecastReason, ForecastStatus

from ._support import instant, request, result, result_payload, window


def changed(model: BaseModel, changes: dict[str, object]) -> dict[str, Any]:
    payload: dict[str, Any] = model.model_dump(mode="json", exclude={"replay_fingerprint"})
    patch(payload, changes)
    return payload


def patch(payload: dict[str, Any], changes: dict[str, object]) -> None:
    for path, value in changes.items():
        cursor = payload
        parts = path.split(".")
        for part in parts[:-1]:
            cursor = cursor[int(part)] if isinstance(cursor, list) else cursor[part]
        if isinstance(cursor, list):
            cursor[int(parts[-1])] = value
        else:
            cursor[parts[-1]] = value


@pytest.mark.parametrize("simulated", [False, True])
def test_request_result_roundtrip_and_list_inputs(simulated: bool) -> None:
    for model in (request(simulated=simulated), result(simulated=simulated)):
        payload = model.model_dump(mode="json")
        rebuilt = type(model).model_validate(payload)
        assert rebuilt == model
        assert type(model).model_validate_json(model.model_dump_json()) == model
    req = request(simulated=simulated)
    assert isinstance(req.evidence, tuple)
    assert isinstance(req.window.schedule.sessions, tuple)
    assert isinstance(req.model_dump(mode="json")["evidence"], list)
    out = result(simulated=simulated)
    assert isinstance(out.composition.nodes, tuple)
    assert isinstance(out.composition.model_dump(mode="json")["nodes"], list)


def test_frozen_semantic_collections_cannot_be_replaced_or_mutated() -> None:
    req = request()
    with pytest.raises(ValidationError):
        req.as_of = instant(4, 16, 4)
    for collection in (req.evidence, req.window.schedule.sessions, result().composition.roots):
        assert not hasattr(collection, "append")
        assert not hasattr(collection, "remove")
    with pytest.raises(ValidationError):
        req.evidence += req.evidence


@pytest.mark.parametrize(
    "path,value",
    [
        ("target_id", "equity.volatility"),
        ("target_version", "2.0"),
        ("schema_version", "2.0"),
        ("subject.symbol", "HDFCBANK"),
        ("subject.symbol", "RELIANCE.NS"),
        ("subject.exchange", "BSE"),
        ("subject.segment", "NSE_INDEX"),
        ("subject.instrument_type", "INDEX"),
        ("subject.provider_instrument_id", "broker-specific"),
        ("subject.trading_symbol", "RELIANCE.NS"),
        ("subject.expiry", "2026-02-05"),
        ("equal_close_policy", "DROP_TIES"),
        ("missing_outcome_policy", "CLASS_ZERO"),
        ("price_basis", "ADJUSTED_CLOSE"),
        ("horizon", "MULTI_SESSION"),
    ],
)
def test_target_scope_is_closed(path: str, value: object) -> None:
    with pytest.raises(ValidationError):
        ForecastTargetSpec.model_validate(changed(request().target, {path: value}))


def test_exact_target_equal_missing_and_invalid_policies_without_labeler() -> None:
    target = request().target
    assert target.target_id == "equity.next_session_close.return_gt_zero"
    assert target.target_version == "1.0"
    assert target.subject.symbol == "RELIANCE"
    assert target.equal_close_policy == "CLASS_ZERO"
    assert target.missing_outcome_policy == "PENDING_THEN_CENSORED_NO_LABEL"
    assert target.invalid_outcome_policy == "INELIGIBLE_NO_LABEL"
    assert target.corporate_action_policy == "EXCLUDE_AFFECTED_OR_UNKNOWN"
    assert target.event == "TERMINAL_CLOSE_GT_REFERENCE_CLOSE"


@pytest.mark.parametrize(
    "field,value",
    [
        ("issued_at", "2026-02-04T16:07:00+05:30"),
        ("computed_at", "2026-02-04T16:06:00+05:30"),
        ("simulation_as_of", "2026-02-04T16:05:00+05:30"),
        ("model_path", "/tmp/model.pkl"),
        ("python_import", "os.system"),
        ("api_key", "NEVER-ECHO-THIS"),
        ("broker_order", {"side": "BUY"}),
        ("realization_mode", "ACTUAL"),
        ("realization_mode", "SIMULATED"),
        ("realization_mode", "REPLAY"),
        ("data_basis", "QUALIFIED_CAPTURE"),
    ],
)
def test_request_rejects_mixed_future_clocks_and_unauthorized_fields(
    field: str,
    value: object,
) -> None:
    with pytest.raises(ValidationError) as exc:
        ForecastRequest.model_validate(changed(request(), {field: value}))
    assert "NEVER-ECHO-THIS" not in str(exc.value)


@pytest.mark.parametrize("probability", [0.0, 0.6, 1.0])
def test_probability_is_numeric_raw_and_never_omitted(probability: float) -> None:
    out = result(probability=probability)
    dumped = out.model_dump(mode="json")
    assert dumped["output"]["probability"] == probability
    assert isinstance(dumped["output"]["probability"], float)
    assert dumped["output"]["calibration"] == "RAW"
    assert dumped["output"]["uncertainty"] == "NOT_ESTIMATED"
    assert dumped["output"]["validity"] == "UNKNOWN"
    assert out.authority == "NO_ACTION_AUTHORITY" and out.admission == "RESEARCH_ONLY"
    assert out.usage_state == "NOT_RECORDED_CONTRACT_ONLY"


@pytest.mark.parametrize("value", [-0.01, 1.01, float("nan"), float("inf"), True, "0.6", None])
def test_probability_rejects_invalid_coercions(value: object) -> None:
    with pytest.raises(ValidationError):
        BinaryProbabilityOutput.model_validate({"probability": value})


@pytest.mark.parametrize(
    "status,reason",
    [
        (ForecastStatus.ABSTAINED, ForecastReason.POLICY_ABSTENTION),
        (ForecastStatus.UNSUPPORTED, ForecastReason.SCOPE_UNSUPPORTED),
        (ForecastStatus.UNAVAILABLE, ForecastReason.EVIDENCE_MISSING),
        (ForecastStatus.FAILED, ForecastReason.INTERNAL_EXECUTION_FAILURE),
    ],
)
def test_absence_has_no_estimate_or_fake_issue(
    status: ForecastStatus, reason: ForecastReason
) -> None:
    payload = changed(
        result(),
        {
            "status": status,
            "output": ForecastAbsence(reasons=(reason,)).model_dump(mode="json"),
            "issued_at": None,
            "computed_at": None,
            "artifact_identity": None,
            "binding_ref": None,
            "binding_available_at": None,
        },
    )
    out = ForecastResult.model_validate(payload)
    assert "probability" not in out.model_dump(mode="json")["output"]
    assert ForecastResult.model_validate_json(out.model_dump_json()) == out
    payload["issued_at"] = instant(4, 16, 7)
    with pytest.raises(ValidationError):
        ForecastResult.model_validate(payload)


def test_status_payload_and_reason_are_not_interchangeable() -> None:
    with pytest.raises(ValidationError):
        ForecastResult.model_validate(changed(result(), {"status": "UNAVAILABLE"}))
    with pytest.raises(ValidationError):
        ForecastResult.model_validate(
            changed(
                result(),
                {
                    "status": "ABSTAINED",
                    "issued_at": None,
                    "output": ForecastAbsence(
                        reasons=(ForecastReason.EVIDENCE_MISSING,)
                    ).model_dump(),
                },
            )
        )


@pytest.mark.parametrize("alteration", ["duplicate", "empty", "dangling", "cycle", "type", "role"])
def test_singleton_graph_rejects_invalid_scope(alteration: str) -> None:
    graph = result().composition.model_dump(mode="json")
    if alteration == "duplicate":
        graph["nodes"] *= 2
    elif alteration == "empty":
        graph["nodes"] = []
    elif alteration == "dangling":
        graph["roots"][0]["node_id"] = "node:missing"
    elif alteration == "cycle":
        graph["edges"] = [{"source_node_id": "node:baserate", "target_node_id": "node:baserate"}]
    elif alteration == "type":
        graph["nodes"][0]["output_kind"] = "OPTION_PROFIT_PROBABILITY"
    else:
        graph["roots"][0]["role"] = "PRIMARY"
    with pytest.raises(ValidationError):
        ForecastComposition.model_validate(graph)


@pytest.mark.parametrize(
    "changes",
    [
        {"target_session_id": "session:s22"},
        {"target_session_id": "session:missing"},
        {"target_open_time": "2026-02-05T09:16:00+05:30"},
        {"target_resolve_time": "2026-02-05T09:15:00+05:30"},
        {"outcome_due_at": "2026-02-05T09:15:00+05:30"},
        {"reference.observed_at": "2026-02-04T15:29:00+05:30"},
        {"schedule.sessions.1.session_id": "session:s20"},
        {"schedule.coverage_end": "2026-02-04T15:30:00+05:30"},
        {"schedule.sessions.1.opens_at": "2026-02-04T15:30:00+05:30"},
        {"schedule.revision": 1},
    ],
)
def test_session_identity_never_guesses_or_repairs(changes: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        ForecastWindow.model_validate(changed(window(), changes))


_CASES = json.loads(
    (Path(__file__).parents[2] / "fixtures/forecasting/ff0/foundation_cases.json").read_text()
)["cases"]


@pytest.mark.parametrize("case", _CASES, ids=[case["id"] for case in _CASES])
def test_synthetic_semantic_manifest(case: dict[str, Any]) -> None:
    payload = result_payload(simulated=case["simulated"])
    patch(payload, case["changes"])
    if case["accepted"]:
        assert ForecastResult.model_validate(payload).request.data_basis == "SYNTHETIC_FIXTURE"
    else:
        with pytest.raises(ValidationError):
            ForecastResult.model_validate(payload)
