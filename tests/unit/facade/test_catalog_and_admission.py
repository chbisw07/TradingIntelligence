"""Static catalog and trusted admission intersection behavior."""

from datetime import UTC

import pytest
from pydantic import ValidationError

from tiaf.a3_hardening import load_package_json
from tiaf.baseline import BaselineEngine
from tiaf.context import AnalysisPurpose
from tiaf.contracts import Horizon
from tiaf.facade import (
    BaselineAssessRequest,
    CapabilityListRequest,
    FacadeInvocationError,
    FacadeOperationRequest,
    FacadeStatus,
    InterfaceLevel,
    InvocationBudget,
    InvocationScope,
    ReplayVerifyRequest,
    capability_catalog,
)
from tiaf.facade.admission import admit

from ..baseline._support import NOW as BASELINE_NOW
from ..baseline._support import baseline_request
from ._support import AUTHORITY, PROFILE, captured_artifacts, config, owner, scope


def list_request() -> CapabilityListRequest:
    return CapabilityListRequest(
        request_id="catalog-request",
        correlation_id="catalog-correlation",
        profile_ref=PROFILE,
        requested_authority_ref=AUTHORITY,
    )


def test_catalog_is_explicit_static_safe_and_contains_only_implemented_operations() -> None:
    descriptors = capability_catalog()
    assert tuple(item.capability_id for item in descriptors) == (
        "a4.evaluate",
        "a4_input.project",
        "baseline.assess",
        "capabilities.list",
        "opportunity.assemble",
        "replay.recorded",
        "replay.verify",
    )
    assert all(not hasattr(item, "callable") for item in descriptors)
    assert all(item.capability_version == "1.0" for item in descriptors)
    assert all(
        item.request_schema_version == item.result_schema_version == "1.0"
        for item in descriptors
    )
    assert "opportunity.orchestrate" not in {item.capability_id for item in descriptors}


def test_discovery_is_filtered_by_grant_and_engineering_permission() -> None:
    facade = owner(
        caller_capabilities=("capabilities.list", "baseline.assess", "replay.verify"),
        engineering=False,
    )
    visible = facade.client("caller:test").list_capabilities(list_request())
    assert tuple(item.capability_id for item in visible.capabilities) == (
        "baseline.assess",
        "capabilities.list",
    )
    assert all(item.interface_level is InterfaceLevel.PUBLIC for item in visible.capabilities)


def test_discovery_or_static_descriptor_possession_does_not_grant_invocation() -> None:
    facade = owner(caller_capabilities=("capabilities.list",))
    client = facade.client("caller:test")
    assert any(
        item.capability_id == "baseline.assess" for item in capability_catalog()
    )
    policy = BaselineEngine().policies()[1]
    request = baseline_request(policy)
    with pytest.raises(FacadeInvocationError) as exc:
        client.invoke(
            BaselineAssessRequest(
                scope=scope(
                    request_id="denied-baseline",
                    subject=request.subject,
                    objective=AnalysisPurpose.OPPORTUNITY,
                    horizon=request.horizon,
                    as_of=request.requested_at,
                ),
                baseline_request=request,
            )
        )
    assert exc.value.record.status is FacadeStatus.PERMISSION_DENIED


def test_unsupported_and_wrong_request_schema_fail_before_dispatch() -> None:
    client = owner().client("caller:test")
    generic = FacadeOperationRequest(
        capability_id="unsupported.capability",
        scope=scope(
            request_id="unsupported",
            subject="RELIANCE",
            objective=AnalysisPurpose.OPPORTUNITY,
            horizon=Horizon(label="POSITIONAL"),
            as_of=BASELINE_NOW,
        ),
    )
    with pytest.raises(FacadeInvocationError) as exc:
        client.invoke(generic)
    assert exc.value.record.status is FacadeStatus.UNSUPPORTED
    mismatched = generic.model_copy(update={"capability_id": "baseline.assess"})
    with pytest.raises(FacadeInvocationError) as mismatch:
        client.invoke(mismatched)
    assert mismatch.value.record.status is FacadeStatus.INVALID_REQUEST


@pytest.mark.parametrize("field", ("engineering_allowed", "live_allowed", "model_allowed"))
def test_caller_request_cannot_self_grant_privileged_flags(field: str) -> None:
    payload = {
        "capability_id": "baseline.assess",
        "scope": {
            "request_id": "self-grant",
            "correlation_id": "self-grant",
            "subject": "RELIANCE",
            "objective": "OPPORTUNITY",
            "horizon": {"label": "POSITIONAL"},
            "as_of": BASELINE_NOW.isoformat(),
            "profile_ref": PROFILE,
            "requested_authority_ref": AUTHORITY,
            field: True,
        },
        "baseline_request": {},
    }
    with pytest.raises(ValidationError):
        BaselineAssessRequest.model_validate(payload)


def test_developer_label_alone_does_not_grant_engineering_capability() -> None:
    facade = owner(
        caller_capabilities=("capabilities.list", "replay.verify"),
        engineering=False,
    )
    result = facade.client("caller:test").list_capabilities(list_request())
    assert "replay.verify" not in {item.capability_id for item in result.capabilities}


def test_engineering_capability_invocation_requires_trusted_engineering_grant() -> None:
    package_artifact = next(
        item for item in captured_artifacts() if item.artifact_ref == "artifact:a3-package"
    )
    package = load_package_json(package_artifact.content)
    request = ReplayVerifyRequest(
        scope=scope(
            request_id="engineering-denied",
            subject=package.manifest.subject,
            objective=package.manifest.purpose,
            horizon=package.manifest.horizon,
            as_of=package.manifest.as_of,
            artifacts=(package_artifact.artifact_ref,),
        ),
        artifact_ref=package_artifact.artifact_ref,
    )
    facade = owner(
        caller_capabilities=("capabilities.list", "replay.verify"),
        engineering=False,
    )
    with pytest.raises(FacadeInvocationError) as exc:
        facade.client("caller:test").invoke(request)
    assert exc.value.record.status is FacadeStatus.PERMISSION_DENIED


def test_effective_budget_is_caller_operator_and_request_intersection() -> None:
    trusted = config()
    descriptor = next(
        item for item in capability_catalog() if item.capability_id == "baseline.assess"
    )
    caller = trusted.caller_grants[0].model_copy(
        update={
            "budget_ceiling": InvocationBudget(
                max_tool_calls=4,
                max_model_calls=3,
                max_input_tokens=800,
                max_output_tokens=400,
                max_cost_units=7,
                max_elapsed_seconds=12,
            )
        }
    )
    operator = trusted.operator.model_copy(
        update={
            "budget_ceiling": InvocationBudget(
                max_tool_calls=3,
                max_model_calls=2,
                max_input_tokens=700,
                max_output_tokens=300,
                max_cost_units=6,
                max_elapsed_seconds=10,
            )
        }
    )
    requested = InvocationBudget(
        max_tool_calls=5,
        max_model_calls=1,
        max_input_tokens=600,
        max_output_tokens=500,
        max_cost_units=5,
        max_elapsed_seconds=8,
    )
    admission = admit(
        descriptor,
        caller,
        operator,
        profile_ref=PROFILE,
        authority_ref=AUTHORITY,
        requested_budget=requested,
        admitted_at=BASELINE_NOW,
    )
    assert admission.effective_budget == InvocationBudget(
        max_tool_calls=3,
        max_model_calls=1,
        max_input_tokens=600,
        max_output_tokens=300,
        max_cost_units=5,
        max_elapsed_seconds=8,
    )


def test_config_requires_single_writer_and_models_are_frozen_json_safe() -> None:
    value = config()
    assert value.single_writer is True
    dumped = value.model_dump(mode="json")
    assert isinstance(dumped["caller_grants"], list)
    assert type(value).model_validate(dumped) == value
    with pytest.raises(ValidationError):
        value.artifact_root_ref = "artifact-root:other"


def test_invocation_timestamps_reject_naive_and_normalize_utc_to_kolkata() -> None:
    value = scope(
        request_id="utc-scope",
        subject="RELIANCE",
        objective=AnalysisPurpose.OPPORTUNITY,
        horizon=Horizon(label="POSITIONAL"),
        as_of=BASELINE_NOW.astimezone(UTC),
    )
    assert str(value.as_of.tzinfo) == "Asia/Kolkata"
    assert value.model_dump(mode="json")["as_of"].endswith("+05:30")
    payload = value.model_dump(mode="json") | {
        "as_of": BASELINE_NOW.replace(tzinfo=None).isoformat()
    }
    with pytest.raises(ValidationError, match="timezone-aware"):
        InvocationScope.model_validate(payload)


def test_result_metadata_preserves_operator_version_and_position_context_ref() -> None:
    engine = BaselineEngine()
    policy = next(item for item in engine.policies() if item.trade_style.value == "POSITIONAL")
    baseline = baseline_request(policy)
    invocation_scope = scope(
        request_id="position-context",
        subject=baseline.subject,
        objective=AnalysisPurpose.OPPORTUNITY,
        horizon=baseline.horizon,
        as_of=baseline.requested_at,
    ).model_copy(update={"position_context_ref": "position-context:current"})
    result = owner().client("caller:test").invoke(
        BaselineAssessRequest(scope=invocation_scope, baseline_request=baseline)
    )
    assert result.metadata.position_context_ref == "position-context:current"
    assert result.metadata.operator_policy_ref == "operator-policy:local"
    assert result.metadata.operator_policy_version == "1.0"
