"""A6.3 governed expression facade parity, replay, authority, and safety."""

import json
import socket
from typing import Any

import pytest
from pydantic import ValidationError

from tiaf.a3_hardening import canonical_json, exact_bytes_checksum
from tiaf.context import AnalysisPurpose
from tiaf.contracts import Horizon
from tiaf.facade import (
    ArtifactKind,
    ExpressionAssessInput,
    ExpressionAssessRequest,
    ExpressionAssessResult,
    FacadeInvocationError,
    FacadeStatus,
    RecordedReplayRequest,
    RecordedReplayResult,
    TrustedArtifact,
    create_local_facade,
)
from tiaf.trade_expression import A6ReplayIntegrityError, ExpressionDisposition

from ._support import (
    AUTHORITY,
    artifact,
    captured_artifacts,
    config,
    owner,
    scope,
)


def _capture(ref: str = "artifact:a6-available") -> ExpressionAssessInput:
    item = next(value for value in captured_artifacts() if value.artifact_ref == ref)
    return ExpressionAssessInput.model_validate_json(item.content)


def _request(
    ref: str = "artifact:a6-available",
    *,
    request_id: str = "facade-expression",
) -> ExpressionAssessRequest:
    capture = _capture(ref)
    return ExpressionAssessRequest(
        scope=scope(
            request_id=request_id,
            subject=capture.request.subject,
            objective=AnalysisPurpose.OPPORTUNITY,
            horizon=Horizon(label=capture.request.horizon.horizon_class.value),
            as_of=capture.request.evaluation_cutoff,
            artifacts=(ref,),
        ),
        expression_input_ref=ref,
    )


@pytest.mark.parametrize(
    ("ref", "disposition"),
    (
        ("artifact:a6-available", ExpressionDisposition.EXPRESSION_AVAILABLE),
        ("artifact:a6-no-option-trade", ExpressionDisposition.NO_OPTION_TRADE),
        ("artifact:a6-wait", ExpressionDisposition.WAIT_FOR_EXPRESSION),
        ("artifact:a6-insufficient", ExpressionDisposition.INSUFFICIENT_EVIDENCE),
        ("artifact:a6-unsupported", ExpressionDisposition.UNSUPPORTED),
    ),
)
def test_expression_facade_returns_exact_replayed_a6_assessment(
    ref: str,
    disposition: ExpressionDisposition,
) -> None:
    result = owner().client("caller:test").invoke(_request(ref))
    assert isinstance(result, ExpressionAssessResult)
    assert result.assessment == _capture(ref).recorded_assessment
    assert result.assessment.disposition is disposition
    assert result.input_integrity_verified is True
    assert result.authority_statement == "ADVISORY_ONLY_TM_RETAINS_ACTION_AUTHORITY"
    assert result.metadata.effect.value == "CAPTURED_READ"
    assert result.metadata.usage.model_calls == 0
    assert result.metadata.usage.tool_calls == 0
    assert result.assessment.provider_calls == result.assessment.model_calls == 0


def test_expression_result_is_frozen_json_round_trip_with_full_a6_contract() -> None:
    result = owner().client("caller:test").invoke(_request())
    payload = result.model_dump(mode="json")
    assert ExpressionAssessResult.model_validate(payload) == result
    assert isinstance(payload["assessment"]["candidate_evaluations"], list)
    assert payload["assessment"] == result.assessment.model_dump(mode="json")
    with pytest.raises(ValidationError, match="frozen"):
        result.assessment = result.assessment


def test_input_only_envelope_assesses_but_is_not_a_recorded_replay() -> None:
    capture = _capture().model_copy(update={"recorded_assessment": None})
    item = artifact(
        "artifact:a6-input-only",
        ArtifactKind.A6_EXPRESSION_CAPTURE,
        canonical_json(capture),
    )
    facade = create_local_facade(
        config().model_copy(update={"artifacts": (*captured_artifacts(), item)})
    )
    assessed = facade.client("caller:test").invoke(
        ExpressionAssessRequest(
            scope=_request().scope.model_copy(
                update={"admitted_artifact_refs": (item.artifact_ref,)}
            ),
            expression_input_ref=item.artifact_ref,
        )
    )
    assert assessed.assessment == _capture().recorded_assessment
    replay_request = RecordedReplayRequest(
        scope=_request(request_id="input-only-replay").scope.model_copy(
            update={"admitted_artifact_refs": (item.artifact_ref,)}
        ),
        artifact_ref=item.artifact_ref,
    )
    with pytest.raises(FacadeInvocationError) as error:
        facade.client("caller:test").invoke(replay_request)
    assert error.value.record.status is FacadeStatus.FAILED


def test_existing_recorded_replay_seam_replays_a6_without_live_state() -> None:
    capture = _capture()
    request = RecordedReplayRequest(
        scope=scope(
            request_id="facade-expression-replay",
            subject=capture.request.subject,
            objective=AnalysisPurpose.OPPORTUNITY,
            horizon=Horizon(label=capture.request.horizon.horizon_class.value),
            as_of=capture.request.evaluation_cutoff,
            artifacts=("artifact:a6-available",),
        ),
        artifact_ref="artifact:a6-available",
    )
    result = owner().client("caller:test").invoke(request)
    assert isinstance(result, RecordedReplayResult)
    assert result.kind.value == "A6_RECORDED"
    assert result.a6_assessment == capture.recorded_assessment
    assert result.metadata.usage.tool_calls == result.metadata.usage.model_calls == 0


def test_expression_assessment_and_replay_open_no_network_socket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("captured A6 facade operation attempted network access")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    client = owner().client("caller:test")
    assessed = client.invoke(_request())
    assert assessed.assessment == _capture().recorded_assessment
    replay = client.invoke(
        RecordedReplayRequest(
            scope=_request(request_id="facade-expression-offline-replay").scope,
            artifact_ref="artifact:a6-available",
        )
    )
    assert replay.a6_assessment == assessed.assessment


def test_expression_authority_and_scope_fail_closed() -> None:
    denied = owner(caller_capabilities=("capabilities.list",)).client("caller:test")
    with pytest.raises(FacadeInvocationError) as permission:
        denied.invoke(_request())
    assert permission.value.record.status is FacadeStatus.PERMISSION_DENIED

    mismatched = _request().model_copy(
        update={"scope": _request().scope.model_copy(update={"subject": "OTHER"})}
    )
    with pytest.raises(FacadeInvocationError) as identity:
        owner().client("caller:test").invoke(mismatched)
    assert identity.value.record.status is FacadeStatus.FAILED


def test_expression_unavailable_artifact_is_reported_without_path_leakage() -> None:
    missing_ref = "artifact:a6-unavailable"
    base = _request(request_id="facade-expression-unavailable")
    request = ExpressionAssessRequest(
        scope=base.scope.model_copy(
            update={"admitted_artifact_refs": (missing_ref,)}
        ),
        expression_input_ref=missing_ref,
    )
    with pytest.raises(FacadeInvocationError) as unavailable:
        owner().client("caller:test").invoke(request)
    assert unavailable.value.record.status is FacadeStatus.UNAVAILABLE
    assert missing_ref not in unavailable.value.record.message


def test_tampered_recorded_assessment_is_rejected_at_startup() -> None:
    original = next(
        value for value in captured_artifacts() if value.artifact_ref == "artifact:a6-available"
    )
    payload = json.loads(original.content)
    payload["recorded_assessment"]["semantic_fingerprint"] = "0" * 64
    content = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    tampered = TrustedArtifact(
        artifact_ref="artifact:a6-tampered",
        kind=ArtifactKind.A6_EXPRESSION_CAPTURE,
        content=content,
        checksum=exact_bytes_checksum(content),
        required_authority_refs=(AUTHORITY,),
        required_entitlement_refs=original.required_entitlement_refs,
    )
    with pytest.raises(A6ReplayIntegrityError):
        create_local_facade(config().model_copy(update={"artifacts": (tampered,)}))


def test_expression_facade_request_has_no_execution_or_runtime_injection_fields() -> None:
    fields = set(ExpressionAssessRequest.model_fields)
    forbidden = {
        "account",
        "broker",
        "capital",
        "client",
        "connector",
        "order",
        "provider",
        "quantity",
        "registry",
        "stop",
        "target",
        "tool",
    }
    assert fields.isdisjoint(forbidden)
    assert set(ExpressionAssessInput.model_fields).isdisjoint(forbidden)
