"""R2 typed discovery metadata, compatibility, authority, and freeze guards."""

import ast
import json
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from tiaf.a5 import capture_run, evaluate_position
from tiaf.baseline import BaselineEngine
from tiaf.context import AnalysisPurpose
from tiaf.facade import (
    BaselineAssessRequest,
    CapabilityDescriptor,
    CapabilityDiscoveryState,
    CapabilityListRequest,
    CapabilityListResult,
    CapabilityReadinessState,
    CapabilityRegistrationState,
    FacadeInvocationError,
    FacadeStatus,
    MonitoringCompatibility,
    PluggabilityLevel,
    capability_catalog,
    capability_discovery_catalog,
)

from ..a5._support import request as position_request
from ..baseline._support import baseline_request
from ._support import AUTHORITY, PROFILE, owner, scope

EXPECTED_IDS = (
    "a4.evaluate",
    "a4_input.project",
    "baseline.assess",
    "capabilities.list",
    "opportunity.assemble",
    "position.assess",
    "replay.recorded",
    "replay.verify",
)


def _list() -> CapabilityListResult:
    return owner().client("caller:test").list_capabilities(
        CapabilityListRequest(
            request_id="r2-list",
            correlation_id="r2-list",
            profile_ref=PROFILE,
            requested_authority_ref=AUTHORITY,
        )
    )


def test_registered_descriptor_identity_and_serialization_are_deterministic() -> None:
    first = capability_discovery_catalog()
    second = capability_discovery_catalog()
    assert first is second
    assert tuple(item.capability_id for item in first) == EXPECTED_IDS
    assert tuple(item.descriptor_id for item in first) == tuple(
        f"descriptor:{capability_id}/1.0" for capability_id in EXPECTED_IDS
    )
    payload = [item.model_dump(mode="json") for item in first]
    assert payload == [item.model_dump(mode="json") for item in second]
    assert all(item.descriptor_schema_version == "1.0" for item in first)
    assert all(item.registration_state is CapabilityRegistrationState.REGISTERED for item in first)
    assert json.loads(json.dumps(payload)) == payload
    private_fields = {"binding", "callable", "implementation", "secret", "token"}
    assert all(private_fields.isdisjoint(item) for item in payload)


def test_discovery_descriptors_and_nested_dependencies_are_immutable() -> None:
    descriptor = capability_discovery_catalog()[0]
    dependency = descriptor.required_dependencies[0]
    with pytest.raises(ValidationError, match="frozen"):
        setattr(descriptor, "replaceable", True)
    with pytest.raises(ValidationError, match="frozen"):
        setattr(dependency, "version_specifier", ">=1.0")
    assert isinstance(descriptor.required_dependencies, tuple)
    assert isinstance(descriptor.optional_dependencies, tuple)
    assert isinstance(descriptor.required_authorities, tuple)
    assert isinstance(descriptor.required_entitlements, tuple)
    assert isinstance(descriptor.limitations, tuple)


def test_roles_effects_and_structural_claims_cover_exact_legacy_catalog() -> None:
    legacy = capability_catalog()
    discovery = capability_discovery_catalog()
    assert len(legacy) == len(discovery) == 8
    assert {item.capability_id: item.semantic_role.value for item in discovery} == {
        "a4.evaluate": "CHALLENGE_ARBITRATION",
        "a4_input.project": "CHALLENGE_ARBITRATION",
        "baseline.assess": "BASELINE",
        "capabilities.list": "CAPABILITY_DISCOVERY",
        "opportunity.assemble": "OPPORTUNITY_INTELLIGENCE",
        "position.assess": "POSITION_INTELLIGENCE",
        "replay.recorded": "REPLAY",
        "replay.verify": "ENGINEERING",
    }
    assert all(item.pluggability_level is PluggabilityLevel.STRUCTURAL for item in discovery)
    assert all(not item.replaceable and not item.composable for item in discovery)
    assert all(item.pluggability_level is not PluggabilityLevel.HOT for item in discovery)
    assert all(item.effect == old.effect for item, old in zip(discovery, legacy, strict=True))
    assert all(item.effect.value in {"PURE", "CAPTURED_READ"} for item in discovery)


def test_required_and_optional_dependencies_are_explicit_disjoint_and_stable() -> None:
    descriptors = capability_discovery_catalog()
    assert all(not item.optional_dependencies for item in descriptors)
    dependencies = {
        item.capability_id: tuple(
            dependency.dependency_id for dependency in item.required_dependencies
        )
        for item in descriptors
    }
    assert dependencies == {
        "a4.evaluate": ("contract:tiaf.source-semantics.foundation-capture",),
        "a4_input.project": ("contract:tiaf.source-semantics.projection-build-input",),
        "baseline.assess": ("contract:tiaf.baseline.deterministic-baseline-request",),
        "capabilities.list": (),
        "opportunity.assemble": ("contract:tiaf.a3-hardening.orchestration-capture",),
        "position.assess": ("contract:tiaf.a5.position-intelligence-request",),
        "replay.recorded": ("contract:tiaf.facade.trusted-replay-artifact",),
        "replay.verify": ("contract:tiaf.facade.trusted-replay-artifact",),
    }
    assert all(
        item.required_authorities == (item.required_authority_scope,)
        for item in descriptors
    )


def test_static_registration_and_filtered_discovery_do_not_inflate_readiness() -> None:
    assert all(
        item.discovery_state is CapabilityDiscoveryState.REGISTERED
        for item in capability_discovery_catalog()
    )
    result = _list()
    assert result.schema_version == "1.1"
    assert tuple(item.capability_id for item in result.discovery_metadata) == EXPECTED_IDS
    assert all(
        item.discovery_state is CapabilityDiscoveryState.DISCOVERABLE
        for item in result.discovery_metadata
    )
    assert all(
        item.readiness_state is CapabilityReadinessState.REQUIRES_RUNTIME_CHECK
        for item in result.discovery_metadata
    )
    assert all(item.effect.value != "LIVE_READ" for item in result.discovery_metadata)


def test_monitoring_compatibility_is_semantic_not_runtime_availability() -> None:
    compatibility = {
        item.capability_id: item.monitoring_compatibility
        for item in capability_discovery_catalog()
    }
    assert compatibility["position.assess"] is MonitoringCompatibility.MONITORING_FUTURE
    assert compatibility["baseline.assess"] is MonitoringCompatibility.SEMANTICALLY_REPEATABLE
    assert compatibility["a4.evaluate"] is MonitoringCompatibility.SEMANTICALLY_REPEATABLE
    assert compatibility["capabilities.list"] is MonitoringCompatibility.NOT_MONITORABLE
    assert compatibility["replay.recorded"] is MonitoringCompatibility.NOT_MONITORABLE
    position = next(
        item for item in capability_discovery_catalog() if item.capability_id == "position.assess"
    )
    assert "limitation:no-monitoring-runtime" in position.limitations
    assert "limitation:no-live-freshness" in position.limitations


def test_discovery_metadata_never_grants_invocation_authority() -> None:
    facade = owner(caller_capabilities=("capabilities.list",))
    client = facade.client("caller:test")
    visible = client.list_capabilities(
        CapabilityListRequest(
            request_id="r2-authority",
            correlation_id="r2-authority",
            profile_ref=PROFILE,
            requested_authority_ref=AUTHORITY,
        )
    )
    assert tuple(item.capability_id for item in visible.discovery_metadata) == (
        "capabilities.list",
    )
    request = baseline_request(BaselineEngine().policies()[1])
    with pytest.raises(FacadeInvocationError) as exc:
        client.invoke(
            BaselineAssessRequest(
                scope=scope(
                    request_id="r2-denied",
                    subject=request.subject,
                    objective=AnalysisPurpose.OPPORTUNITY,
                    horizon=request.horizon,
                    as_of=request.requested_at,
                ),
                baseline_request=request,
            )
        )
    assert exc.value.record.status is FacadeStatus.PERMISSION_DENIED


def test_capability_list_v11_round_trip_and_v10_reader_compatibility() -> None:
    result = _list()
    assert CapabilityListResult.model_validate(result.model_dump(mode="json")) == result
    legacy_payload = result.model_dump(mode="json")
    legacy_payload["schema_version"] = "1.0"
    legacy_payload.pop("discovery_metadata")
    legacy = CapabilityListResult.model_validate(legacy_payload)
    assert legacy.discovery_metadata == ()
    assert tuple(item.capability_id for item in legacy.capabilities) == EXPECTED_IDS
    assert CapabilityDescriptor.model_validate(
        result.capabilities[0].model_dump(mode="json")
    ) == result.capabilities[0]


@pytest.mark.parametrize(
    ("case", "message"),
    (
        ("missing", "exactly cover"),
        ("reordered", "exactly cover"),
        ("legacy-mismatch", "preserve legacy descriptor fields"),
    ),
)
def test_capability_list_v11_fails_closed(
    case: str,
    message: str,
) -> None:
    result = _list()
    payload = result.model_dump(mode="json")
    if case == "missing":
        payload.pop("discovery_metadata")
    elif case == "reordered":
        payload["discovery_metadata"] = list(reversed(payload["discovery_metadata"]))
    else:
        payload["discovery_metadata"][0]["effect"] = "PURE"
    with pytest.raises(ValidationError, match=message):
        CapabilityListResult.model_validate(payload)


def test_capability_map_table_matches_runtime_discovery_exactly() -> None:
    text = Path("docs/TIAF_CAPABILITY_MAP.md").read_text(encoding="utf-8")
    section = text.split("## Current public/engineering catalog", 1)[1].split(
        "## Data and evidence", 1
    )[0]
    rows = re.findall(
        r"^\| `([^`]+)` \| (PUBLIC|ENGINEERING) / (PURE|CAPTURED_READ) \| "
        r"([A-Z_]+) \| (STRUCTURAL|COLD|HOT) \| ([A-Z_]+) \| ([A-Z_]+) \|$",
        section,
        re.MULTILINE,
    )
    documented = {
        capability_id: (interface, effect, role, level, monitoring, readiness)
        for capability_id, interface, effect, role, level, monitoring, readiness in rows
    }
    runtime = {
        item.capability_id: (
            item.interface_level.value,
            item.effect.value,
            item.semantic_role.value,
            item.pluggability_level.value,
            item.monitoring_compatibility.value,
            item.readiness_state.value,
        )
        for item in capability_discovery_catalog()
    }
    assert documented == runtime


def test_r2_preserves_frozen_a5_semantic_and_replay_identity() -> None:
    value = position_request()
    before = evaluate_position(value, evaluated_at=value.as_of)
    before_capture = capture_run(before, captured_at=value.as_of)
    capability_discovery_catalog()
    _list()
    after = evaluate_position(value, evaluated_at=value.as_of)
    after_capture = capture_run(after, captured_at=value.as_of)
    assert after == before
    assert after.fingerprint == before.fingerprint
    assert after.result.semantic_fingerprint == before.result.semantic_fingerprint
    assert after.result.replay_identity == before.result.replay_identity
    assert after_capture == before_capture


def test_r2_facade_and_shell_modules_have_no_external_runtime_imports() -> None:
    forbidden = {"aiohttp", "fastapi", "httpx", "mcp", "openai", "requests"}
    violations: list[str] = []
    paths = sorted(Path("src/tiaf/facade").glob("*.py"))
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: tuple[str, ...] = ()
            if isinstance(node, ast.Import):
                names = tuple(item.name for item in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = (node.module,)
            violations.extend(
                f"{path}:{getattr(node, 'lineno', 0)}:{name}"
                for name in names
                if name.split(".", 1)[0] in forbidden
                or name.startswith(("tiaf.providers", "tiaf.a6", "tiaf.a7"))
            )
    assert violations == []
