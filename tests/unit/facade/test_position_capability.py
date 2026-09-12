"""A5.2 governed position facade parity, authority and replay acceptance."""

import json
from datetime import date

import pytest
from pydantic import ValidationError

from tiaf.a3_hardening import canonical_json, exact_bytes_checksum
from tiaf.a5 import (
    A5ExecutionStatus,
    A5FailureCode,
    PositionFreshness,
    PositionIntelligenceRequest,
    PositionRecommendation,
    PositionShape,
    evaluate_position,
)
from tiaf.context import AnalysisPurpose
from tiaf.data import InstrumentType
from tiaf.facade import (
    ArtifactKind,
    CallerGrant,
    FacadeInvocationError,
    FacadeStatus,
    LocalFacadeOwner,
    PositionAssessRequest,
    RecordedReplayRequest,
    ReplayResultKind,
    TrustedArtifact,
    capability_catalog,
    create_local_facade,
)

from ..a5._support import request as make_a5_request
from ..a5._support import snapshot
from ._support import (
    AUTHORITY,
    ENTITLEMENT,
    POSITION_ENTITLEMENT,
    artifact,
    captured_artifacts,
    config,
    owner,
    scope,
)


def position_request() -> PositionIntelligenceRequest:
    item = next(
        value
        for value in captured_artifacts()
        if value.kind is ArtifactKind.A5_POSITION_REQUEST
    )
    return PositionIntelligenceRequest.model_validate_json(item.content)


def facade_request(
    value: PositionIntelligenceRequest,
    *,
    artifact_ref: str = "artifact:position-request",
    request_id: str = "facade-position",
) -> PositionAssessRequest:
    invocation_scope = scope(
        request_id=request_id,
        subject=value.snapshot.underlying,
        objective=AnalysisPurpose.POSITION,
        horizon=value.horizon,
        as_of=value.as_of,
        artifacts=(artifact_ref,),
    ).model_copy(update={"position_context_ref": artifact_ref})
    return PositionAssessRequest(
        scope=invocation_scope,
        position_request_ref=artifact_ref,
    )


def authorized_request(value: PositionIntelligenceRequest) -> PositionIntelligenceRequest:
    return value.model_copy(
        update={
            "snapshot": value.snapshot.model_copy(
                update={"authority_refs": (AUTHORITY,)}
            ),
            "authority_refs": (AUTHORITY,),
        }
    )


def facade_for_request(
    value: PositionIntelligenceRequest,
    *,
    artifact_ref: str,
) -> LocalFacadeOwner:
    item = artifact(
        artifact_ref,
        ArtifactKind.A5_POSITION_REQUEST,
        canonical_json(value),
        entitlement_refs=(POSITION_ENTITLEMENT,),
    )
    trusted = config().model_copy(
        update={"artifacts": (*captured_artifacts(), item)}
    )
    return create_local_facade(trusted)


def test_descriptor_is_public_captured_read_position_scoped_and_zero_cost() -> None:
    descriptor = next(
        item for item in capability_catalog() if item.capability_id == "position.assess"
    )
    assert descriptor.effect.value == "CAPTURED_READ"
    assert descriptor.required_authority_scope.value == "ASSESS_POSITION"
    assert descriptor.deterministic is True
    assert descriptor.model_supported is False
    assert descriptor.replay_support.value == "DETERMINISTIC"
    assert descriptor.cost_knowledge.value == "KNOWN_ZERO"
    assert not hasattr(descriptor, "callable")


def test_authorized_position_assessment_matches_direct_a5_and_preserves_identity() -> None:
    value = position_request()
    direct = evaluate_position(value, evaluated_at=value.as_of)
    result = owner().client("caller:test").invoke(facade_request(value))
    assert value.a4_result is not None
    assert result.assessment == direct.result
    assert result.run_fingerprint == direct.fingerprint
    assert result.assessment.snapshot_id == value.snapshot.snapshot_id
    assert result.assessment.snapshot_at == value.snapshot.snapshot_at
    assert result.assessment.effective_freshness is PositionFreshness.CURRENT
    assert result.assessment.linked_a4_result_id == value.a4_result.result_id
    assert result.assessment.linked_a4_fingerprint == value.a4_result.semantic_fingerprint
    assert result.assessment.semantic_fingerprint == direct.result.semantic_fingerprint
    assert result.metadata.position_context_ref == "artifact:position-request"
    assert result.metadata.usage.tool_calls == result.metadata.usage.model_calls == 0
    assert result.assessment.usage.provider_calls == result.assessment.usage.model_calls == 0
    assert result.monitoring_statement == "ADVISORY_MONITORING_INTENT_ONLY_NOT_SCHEDULED"
    assert (
        result.assessment.authority_statement
        == "ADVISORY_ONLY_TRADEMONITOR_DECIDES_BROKER_EXECUTION"
    )


def test_position_entitlement_and_capability_grant_are_both_required() -> None:
    value = position_request()
    request = facade_request(value)
    no_position_entitlement = owner(caller_entitlements=(ENTITLEMENT,))
    with pytest.raises(FacadeInvocationError) as entitlement:
        no_position_entitlement.client("caller:test").invoke(request)
    assert entitlement.value.record.status is FacadeStatus.PERMISSION_DENIED

    no_capability = owner(caller_capabilities=("capabilities.list",))
    with pytest.raises(FacadeInvocationError) as capability:
        no_capability.client("caller:test").invoke(request)
    assert capability.value.record.status is FacadeStatus.PERMISSION_DENIED


def test_artifact_id_or_foreign_entitlement_does_not_confer_position_access() -> None:
    value = position_request()
    foreign = artifact(
        "artifact:position-foreign",
        ArtifactKind.A5_POSITION_REQUEST,
        canonical_json(value),
        entitlement_refs=("entitlement:position-other-caller",),
    )
    trusted = config().model_copy(
        update={"artifacts": (*captured_artifacts(), foreign)}
    )
    facade = create_local_facade(trusted)
    with pytest.raises(FacadeInvocationError) as exc:
        facade.client("caller:test").invoke(
            facade_request(value, artifact_ref=foreign.artifact_ref)
        )
    assert exc.value.record.status is FacadeStatus.PERMISSION_DENIED


def test_caller_a_cannot_assess_caller_b_restricted_position() -> None:
    value = position_request()
    caller_b_entitlement = "entitlement:position-caller-b"
    foreign = artifact(
        "artifact:position-caller-b",
        ArtifactKind.A5_POSITION_REQUEST,
        canonical_json(value),
        entitlement_refs=(caller_b_entitlement,),
    )
    trusted = config()
    caller_b = CallerGrant(
        caller_id="caller:b",
        grant_id="grant:b",
        allowed_capabilities=("position.assess",),
        authority_scopes=trusted.caller_grants[0].authority_scopes,
        authority_refs=(AUTHORITY,),
        entitlement_refs=(caller_b_entitlement,),
        allowed_profiles=trusted.caller_grants[0].allowed_profiles,
        budget_ceiling=trusted.caller_grants[0].budget_ceiling,
    )
    trusted = trusted.model_copy(
        update={
            "operator": trusted.operator.model_copy(
                update={
                    "entitlement_refs": (
                        *trusted.operator.entitlement_refs,
                        caller_b_entitlement,
                    )
                }
            ),
            "caller_grants": (*trusted.caller_grants, caller_b),
            "artifacts": (*trusted.artifacts, foreign),
        }
    )
    facade = create_local_facade(trusted)
    request = facade_request(value, artifact_ref=foreign.artifact_ref)
    with pytest.raises(FacadeInvocationError) as denied:
        facade.client("caller:test").invoke(request)
    assert denied.value.record.status is FacadeStatus.PERMISSION_DENIED
    assert facade.client("caller:b").invoke(request).assessment.position_id == (
        value.snapshot.position_id
    )


def test_revoked_caller_is_denied_again_on_position_invocation() -> None:
    value = position_request()
    facade = owner()
    client = facade.client("caller:test")
    facade.revoke_caller("caller:test")
    with pytest.raises(FacadeInvocationError) as exc:
        client.invoke(facade_request(value))
    assert exc.value.record.status is FacadeStatus.PERMISSION_DENIED


@pytest.mark.parametrize(
    ("kind", "shape", "freshness", "expected_status", "expected_recommendation"),
    (
        (
            InstrumentType.EQUITY,
            PositionShape.SINGLE_LEG,
            PositionFreshness.CURRENT,
            A5ExecutionStatus.COMPLETE,
            PositionRecommendation.MAINTAIN,
        ),
        (
            InstrumentType.FUTURE,
            PositionShape.SINGLE_LEG,
            PositionFreshness.CURRENT,
            A5ExecutionStatus.COMPLETE,
            PositionRecommendation.MAINTAIN,
        ),
        (
            InstrumentType.CALL_OPTION,
            PositionShape.SINGLE_LEG,
            PositionFreshness.CURRENT,
            A5ExecutionStatus.COMPLETE,
            PositionRecommendation.MAINTAIN,
        ),
        (
            InstrumentType.EQUITY,
            PositionShape.MULTI_LEG,
            PositionFreshness.CURRENT,
            A5ExecutionStatus.UNSUPPORTED,
            PositionRecommendation.INSUFFICIENT_EVIDENCE,
        ),
        (
            InstrumentType.EQUITY,
            PositionShape.SINGLE_LEG,
            PositionFreshness.STALE,
            A5ExecutionStatus.PARTIAL,
            PositionRecommendation.ABSTAIN,
        ),
    ),
)
def test_position_domain_scenarios_remain_successful_facade_results(
    kind: InstrumentType,
    shape: PositionShape,
    freshness: PositionFreshness,
    expected_status: A5ExecutionStatus,
    expected_recommendation: PositionRecommendation,
) -> None:
    expiry = date(2026, 9, 30) if kind is not InstrumentType.EQUITY else None
    item = snapshot(kind=kind, expiry=expiry, shape=shape, freshness=freshness)
    value = authorized_request(make_a5_request(position_snapshot=item))
    ref = f"artifact:position-{kind.value.lower()}-{shape.value.lower()}-{freshness.value.lower()}"
    facade = facade_for_request(value, artifact_ref=ref)
    result = facade.client("caller:test").invoke(facade_request(value, artifact_ref=ref))
    assert result.assessment.status is expected_status
    assert result.assessment.recommendation is expected_recommendation
    assert result.metadata.status is FacadeStatus.COMPLETED
    if shape is PositionShape.MULTI_LEG:
        assert result.assessment.failure_codes == (A5FailureCode.UNSUPPORTED_SHAPE,)


def test_generic_recorded_replay_supports_a5_capture_without_external_calls() -> None:
    value = position_request()
    request = RecordedReplayRequest(
        scope=scope(
            request_id="facade-a5-replay",
            subject=value.snapshot.underlying,
            objective=AnalysisPurpose.POSITION,
            horizon=value.horizon,
            as_of=value.as_of,
            artifacts=("artifact:a5-capture",),
        ),
        artifact_ref="artifact:a5-capture",
    )
    result = owner().client("caller:test").invoke(request)
    assert result.kind is ReplayResultKind.A5_RECORDED
    assert result.a5_replay is not None
    assert result.a5_replay.record.result.semantic_fingerprint == evaluate_position(
        value, evaluated_at=value.as_of
    ).result.semantic_fingerprint
    assert result.metadata.usage.tool_calls == result.metadata.usage.model_calls == 0


def test_position_request_contract_rejects_paths_urls_and_object_injection() -> None:
    value = position_request()
    valid = facade_request(value).model_dump(mode="json")
    for unsafe in ("/tmp/position.json", "../position.json", "https://example.test/x"):
        payload = json.loads(json.dumps(valid))
        payload["position_request_ref"] = unsafe
        payload["scope"]["position_context_ref"] = unsafe
        payload["scope"]["admitted_artifact_refs"] = [unsafe]
        with pytest.raises(ValidationError):
            PositionAssessRequest.model_validate(payload)
    with pytest.raises(ValidationError):
        PositionAssessRequest.model_validate(valid | {"broker": object()})


def test_corrupt_or_tampered_position_artifact_fails_closed_at_composition() -> None:
    value = position_request()
    valid_content = canonical_json(value)
    bad_checksum = TrustedArtifact(
        artifact_ref="artifact:bad-checksum",
        kind=ArtifactKind.A5_POSITION_REQUEST,
        content=valid_content,
        checksum="0" * 64,
        required_authority_refs=(AUTHORITY,),
        required_entitlement_refs=(POSITION_ENTITLEMENT,),
    )
    with pytest.raises(ValueError, match="checksum"):
        create_local_facade(config().model_copy(update={"artifacts": (bad_checksum,)}))

    tampered = json.loads(valid_content)
    tampered["snapshot"]["underlying"] = "FOREIGN"
    tampered_content = json.dumps(tampered, sort_keys=True)
    invalid = bad_checksum.model_copy(
        update={
            "artifact_ref": "artifact:tampered-position",
            "content": tampered_content,
            "checksum": exact_bytes_checksum(tampered_content),
        }
    )
    with pytest.raises(ValueError):
        create_local_facade(config().model_copy(update={"artifacts": (invalid,)}))


def test_position_facade_request_has_no_execution_or_runtime_injection_fields() -> None:
    forbidden = {
        "account",
        "broker",
        "credentials",
        "execution",
        "filesystem_path",
        "model",
        "order",
        "policy",
        "provider",
        "router",
        "url",
    }
    assert not forbidden & set(PositionAssessRequest.model_fields)
