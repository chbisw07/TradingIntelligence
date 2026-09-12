"""Accepted captured facade fixtures for Shell adapter tests."""

from datetime import datetime
from pathlib import Path

from tiaf.a3_hardening import load_package_json
from tiaf.a5 import PositionIntelligenceRequest
from tiaf.baseline import BaselineEngine, DeterministicBaselineRequest
from tiaf.context import AnalysisPurpose
from tiaf.contracts import Horizon
from tiaf.facade import ArtifactKind, create_local_facade
from tiaf.shell import SessionDefaults, ShellDispatcher, ShellRuntime
from tiaf.source_semantics import (
    A4SemanticInputProjection,
    EpistemicRole,
    capture_json,
    capture_projection,
    replay_recorded,
)

from ..a3_hardening._support import package_for
from ..baseline._support import baseline_request
from ..facade._support import (
    AUTHORITY,
    PROFILE,
    artifact,
    captured_artifacts,
    config,
    owner,
)
from ..source_semantics._support import assertion, build_input


def artifact_content(ref: str) -> str:
    return next(item.content for item in captured_artifacts() if item.artifact_ref == ref)


def captured_context() -> tuple[str, AnalysisPurpose, Horizon, datetime]:
    package = load_package_json(artifact_content("artifact:a3-package"))
    return (
        package.manifest.subject,
        package.manifest.purpose,
        package.manifest.horizon,
        package.manifest.as_of,
    )


def defaults(*, full_context: bool = True) -> SessionDefaults:
    if not full_context:
        return SessionDefaults(profile_ref=PROFILE, authority_ref=AUTHORITY)
    subject, purpose, horizon, as_of = captured_context()
    return SessionDefaults(
        subject=subject,
        objective=purpose,
        horizon=horizon,
        as_of=as_of,
        profile_ref=PROFILE,
        authority_ref=AUTHORITY,
    )


def position_defaults() -> SessionDefaults:
    request = PositionIntelligenceRequest.model_validate_json(
        artifact_content("artifact:position-request")
    )
    return SessionDefaults(
        subject=request.snapshot.underlying,
        objective=AnalysisPurpose.POSITION,
        horizon=request.horizon,
        as_of=request.as_of,
        profile_ref=PROFILE,
        authority_ref=AUTHORITY,
    )


def write_baseline(root: Path, *, name: str = "baseline.json") -> DeterministicBaselineRequest:
    engine = BaselineEngine()
    policy = next(item for item in engine.policies() if item.trade_style.value == "POSITIONAL")
    request = baseline_request(policy, profile="neutral")
    (root / name).write_text(request.model_dump_json(), encoding="utf-8")
    return request


def runtime(
    root: Path,
    *,
    full_context: bool = True,
    engineering: bool = True,
    history_limit: int = 32,
) -> ShellRuntime:
    facade_owner = owner(engineering=engineering)
    dispatcher = ShellDispatcher(
        facade_owner.client("caller:test"),
        baseline_request_root=root,
        defaults=defaults(full_context=full_context),
        history_limit=history_limit,
    )
    return ShellRuntime(dispatcher)


def position_runtime(root: Path) -> ShellRuntime:
    facade_owner = owner()
    return ShellRuntime(
        ShellDispatcher(
            facade_owner.client("caller:test"),
            baseline_request_root=root,
            defaults=position_defaults(),
        )
    )


def a4_state_runtime(root: Path, package_name: str) -> tuple[ShellRuntime, str]:
    if package_name == "unsupported_assumption":
        hypothesis = assertion(
            "assertion:shell-unsupported-hypothesis",
            100.0,
            epistemic=EpistemicRole.HYPOTHESIS,
        )
        foundation_input = build_input(assertion_items=(hypothesis,))
        package = foundation_input.package
    else:
        package = package_for(package_name)
        foundation_input = build_input(package=package)
    capture = capture_projection(
        foundation_input,
        captured_at=foundation_input.header.evidence_as_of,
    )
    artifact_ref = f"artifact:a4-{package_name}"
    state_artifact = artifact(
        artifact_ref,
        ArtifactKind.FOUNDATION_CAPTURE,
        capture_json(capture),
    )
    facade_config = config()
    facade_config = facade_config.model_copy(
        update={"artifacts": (*facade_config.artifacts, state_artifact)}
    )
    facade_owner = create_local_facade(facade_config)
    dispatcher = ShellDispatcher(
        facade_owner.client("caller:test"),
        baseline_request_root=root,
        defaults=SessionDefaults(
            subject=package.manifest.subject,
            objective=package.manifest.purpose,
            horizon=package.manifest.horizon,
            as_of=package.manifest.as_of,
            profile_ref=PROFILE,
            authority_ref=AUTHORITY,
        ),
    )
    return ShellRuntime(dispatcher), artifact_ref


def projection() -> A4SemanticInputProjection:
    return replay_recorded(artifact_content("artifact:foundation-capture"))
