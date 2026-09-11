"""Lifecycle, artifact authorization, isolation and forbidden-boundary tests."""

import ast
import json
import socket
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event

import pytest
from pydantic import ValidationError

from tiaf.baseline import (
    BaselineEngine,
    BaselinePolicy,
    DeterministicBaselineRequest,
    OpportunityAssessment,
)
from tiaf.context import AnalysisPurpose
from tiaf.facade import (
    ArtifactKind,
    BaselineAssessRequest,
    FacadeInvocationError,
    FacadeStatus,
    LifecycleState,
    RecordedReplayRequest,
    TrustedArtifact,
    create_local_facade,
)

from ..baseline._support import baseline_request
from ._support import captured_artifacts, config, owner, scope


def baseline_facade_request(
    request_id: str,
    profile: str = "positive",
    trade_style: str = "POSITIONAL",
) -> BaselineAssessRequest:
    engine = BaselineEngine()
    policy = next(item for item in engine.policies() if item.trade_style.value == trade_style)
    baseline = baseline_request(policy, profile=profile)
    return BaselineAssessRequest(
        scope=scope(
            request_id=request_id,
            subject=baseline.subject,
            objective=AnalysisPurpose.OPPORTUNITY,
            horizon=baseline.horizon,
            as_of=baseline.requested_at,
        ),
        baseline_request=baseline,
    )


def test_startup_composition_freezes_and_shutdown_stops_admission() -> None:
    facade = create_local_facade(config(), start=False)
    assert facade.state is LifecycleState.CONFIGURING
    facade.start()
    with pytest.raises(RuntimeError, match="frozen"):
        facade.add_startup_artifact(captured_artifacts()[0])
    facade.shutdown()
    assert facade.state.value == LifecycleState.SHUTDOWN.value
    with pytest.raises(FacadeInvocationError) as exc:
        facade.client("caller:test").invoke(baseline_facade_request("after-shutdown"))
    assert exc.value.record.status is FacadeStatus.UNAVAILABLE


def test_grants_budgets_and_results_do_not_bleed_between_requests() -> None:
    client = owner().client("caller:test")
    first_request = baseline_facade_request("request-a", profile="positive")
    second_request = baseline_facade_request("request-b", profile="negative")
    first = client.invoke(first_request)
    second = client.invoke(second_request)
    assert first.metadata.request_id == "request-a"
    assert second.metadata.request_id == "request-b"
    assert first.assessment != second.assessment
    assert first.metadata.budget_ref == second.metadata.budget_ref
    assert first.metadata.run_id != second.metadata.run_id
    assert first.metadata.usage.tool_calls == second.metadata.usage.tool_calls == 0


def test_concurrent_pure_requests_retain_subject_horizon_and_state_isolation() -> None:
    client = owner().client("caller:test")
    requests = (
        baseline_facade_request("parallel-a", "positive", "DAY"),
        baseline_facade_request("parallel-b", "negative"),
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = tuple(pool.map(client.invoke, requests))
    assert tuple(item.metadata.request_id for item in results) == (
        "parallel-a",
        "parallel-b",
    )
    assert all(item.metadata.subject == "RELIANCE" for item in results)
    assert results[0].metadata.horizon != results[1].metadata.horizon
    assert results[0].assessment != results[1].assessment


def test_concurrent_repeated_request_ids_receive_distinct_run_lifecycles() -> None:
    client = owner().client("caller:test")
    request = baseline_facade_request("repeated-request")
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = tuple(pool.map(client.invoke, (request, request)))
    assert results[0].metadata.request_id == results[1].metadata.request_id
    assert results[0].metadata.run_id != results[1].metadata.run_id


def test_startup_composition_and_shutdown_remain_frozen_during_active_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facade = owner()
    entered = Event()
    release = Event()
    original = BaselineEngine.assess

    def blocking_assess(
        engine: BaselineEngine,
        request: DeterministicBaselineRequest,
        *,
        policy: BaselinePolicy | None = None,
    ) -> OpportunityAssessment:
        entered.set()
        assert release.wait(timeout=5)
        return original(engine, request, policy=policy)

    monkeypatch.setattr(BaselineEngine, "assess", blocking_assess)
    with ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(
            facade.client("caller:test").invoke,
            baseline_facade_request("active-run"),
        )
        assert entered.wait(timeout=5)
        with pytest.raises(RuntimeError, match="frozen"):
            facade.add_startup_artifact(captured_artifacts()[0])
        with pytest.raises(RuntimeError, match="active"):
            facade.shutdown()
        release.set()
        assert pending.result().metadata.request_id == "active-run"


def test_failure_of_one_request_does_not_mutate_completed_other_result() -> None:
    client = owner().client("caller:test")
    completed = client.invoke(baseline_facade_request("completed"))
    frozen_json = completed.model_dump_json()
    malformed = baseline_facade_request("malformed").model_copy(
        update={"capability_id": "opportunity.assemble"}
    )
    with pytest.raises(FacadeInvocationError):
        client.invoke(malformed)
    assert completed.model_dump_json() == frozen_json


def test_revocation_and_missing_entitlement_block_artifact_read() -> None:
    package_artifact = next(
        item for item in captured_artifacts() if item.kind is ArtifactKind.A3_PACKAGE
    )
    package = json.loads(package_artifact.content)["manifest"]
    request = RecordedReplayRequest(
        scope=scope(
            request_id="revoked-read",
            subject=package["subject"],
            objective=AnalysisPurpose(package["purpose"]),
            horizon=package["horizon"],
            as_of=package["as_of"],
            artifacts=(package_artifact.artifact_ref,),
        ),
        artifact_ref=package_artifact.artifact_ref,
    )
    facade = owner()
    client = facade.client("caller:test")
    facade.revoke_caller("caller:test")
    with pytest.raises(FacadeInvocationError) as revoked:
        client.invoke(request)
    assert revoked.value.record.status is FacadeStatus.PERMISSION_DENIED

    no_entitlement = owner(caller_entitlements=())
    with pytest.raises(FacadeInvocationError) as denied:
        no_entitlement.client("caller:test").invoke(request)
    assert denied.value.record.status is FacadeStatus.PERMISSION_DENIED


@pytest.mark.parametrize(
    "artifact_ref",
    ("/tmp/capture.json", "../capture.json", "https://example.test/capture"),
)
def test_arbitrary_paths_and_urls_are_rejected(artifact_ref: str) -> None:
    with pytest.raises(ValidationError):
        RecordedReplayRequest.model_validate(
            {
                "scope": {
                    "request_id": "unsafe-ref",
                    "correlation_id": "unsafe-ref",
                    "subject": "RELIANCE",
                    "objective": "OPPORTUNITY",
                    "horizon": {"label": "POSITIONAL"},
                    "as_of": "2026-09-11T12:00:00+05:30",
                    "profile_ref": "profile:deterministic",
                    "requested_authority_ref": "authority:facade-default",
                    "admitted_artifact_refs": [artifact_ref],
                },
                "artifact_ref": artifact_ref,
            }
        )


def test_provider_router_registry_and_secret_injection_are_rejected() -> None:
    baseline = baseline_facade_request("injection")
    injected = baseline.baseline_request.model_copy(
        update={"metadata": {"access_token": "must-not-appear"}}
    )
    request = baseline.model_copy(update={"baseline_request": injected})
    with pytest.raises(FacadeInvocationError) as exc:
        owner().client("caller:test").invoke(request)
    assert exc.value.record.status is FacadeStatus.INVALID_REQUEST
    assert "must-not-appear" not in exc.value.record.model_dump_json()
    with pytest.raises(ValidationError):
        BaselineAssessRequest.model_validate(
            baseline.model_dump(mode="json") | {"router": object()}
        )


def test_caller_cannot_claim_unconsumed_artifacts_as_admitted() -> None:
    baseline = baseline_facade_request("unconsumed-artifact")
    with pytest.raises(ValidationError, match="scope must match"):
        BaselineAssessRequest.model_validate(
            baseline.model_dump(mode="json")
            | {
                "scope": baseline.scope.model_copy(
                    update={"admitted_artifact_refs": ("artifact:a3-package",)}
                ).model_dump(mode="json")
            }
        )


def test_recorded_replay_never_uses_network_for_integrity_repair(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_artifact = next(
        item for item in captured_artifacts() if item.kind is ArtifactKind.A3_PACKAGE
    )
    package = json.loads(package_artifact.content)["manifest"]
    request = RecordedReplayRequest(
        scope=scope(
            request_id="offline-replay",
            subject=package["subject"],
            objective=AnalysisPurpose(package["purpose"]),
            horizon=package["horizon"],
            as_of=package["as_of"],
            artifacts=(package_artifact.artifact_ref,),
        ),
        artifact_ref=package_artifact.artifact_ref,
    )

    def reject_network(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("facade replay attempted network access")

    monkeypatch.setattr(socket.socket, "connect", reject_network)
    result = owner().client("caller:test").invoke(request)
    assert result.a3_replay is not None and result.a3_replay.semantic_match


def test_corrupt_artifact_is_rejected_at_trusted_startup_without_live_repair() -> None:
    original = captured_artifacts()[0]
    corrupt = TrustedArtifact(
        artifact_ref="artifact:corrupt",
        kind=original.kind,
        content=original.content,
        checksum="f" * 64,
    )
    with pytest.raises(ValueError, match="checksum"):
        create_local_facade(
            config().model_copy(update={"artifacts": (*captured_artifacts(), corrupt)})
        )


def test_facade_has_no_http_cloud_database_queue_provider_model_or_broker_imports() -> None:
    banned = {
        "aiohttp",
        "boto3",
        "celery",
        "django",
        "fastapi",
        "flask",
        "grpc",
        "httpx",
        "kafka",
        "langgraph",
        "openai",
        "psycopg",
        "redis",
        "requests",
        "sqlalchemy",
    }
    imported: set[str] = set()
    classes: set[str] = set()
    for path in Path("src/tiaf/facade").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(item.name.split(".", 1)[0] for item in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.ClassDef):
                classes.add(node.name)
    assert not imported & banned
    assert not {"A4Challenger", "A4Arbitrator", "Broker", "Order"} & classes
    assert "opportunity.orchestrate" not in {
        item.capability_id
        for item in __import__("tiaf.facade", fromlist=["capability_catalog"]).capability_catalog()
    }
