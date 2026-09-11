"""Facade operations remain parity wrappers over accepted deterministic services."""

import json

import pytest

from tiaf.a3_hardening import (
    BlobKind,
    canonical_json,
    load_package_json,
    package_blob,
    replay_a3_package,
    verify_a3_package,
)
from tiaf.a4 import evaluate_projection
from tiaf.baseline import BaselineEngine, CandidateClass
from tiaf.context import AnalysisPurpose
from tiaf.facade import (
    A4EvaluateRequest,
    A4InputProjectRequest,
    ArtifactKind,
    BaselineAssessRequest,
    FacadeInvocationError,
    FacadeStatus,
    OpportunityAssembleRequest,
    RecordedReplayRequest,
    ReplayResultKind,
    ReplayVerifyRequest,
    create_local_facade,
)
from tiaf.service.opportunity_intelligence import (
    assemble_opportunity_intelligence,
    default_policy,
    request_from_capture,
)
from tiaf.source_semantics import (
    Missingness,
    ProjectionBuildInput,
    ProjectionGap,
    build_projection,
)
from tiaf.source_semantics import (
    replay_recorded as replay_foundation,
)

from ..baseline._support import baseline_request
from ..source_semantics._support import build_input as foundation_build_input
from ._support import artifact, captured_artifacts, config, owner, scope


def content(ref: str) -> str:
    return next(item.content for item in captured_artifacts() if item.artifact_ref == ref)


def test_baseline_assess_has_direct_a2_parity_and_preserves_no_trade() -> None:
    engine = BaselineEngine()
    policy = next(item for item in engine.policies() if item.trade_style.value == "POSITIONAL")
    baseline = baseline_request(policy, profile="neutral")
    direct = engine.assess(baseline)
    request = BaselineAssessRequest(
        scope=scope(
            request_id="facade-baseline",
            subject=baseline.subject,
            objective=AnalysisPurpose.OPPORTUNITY,
            horizon=baseline.horizon,
            as_of=baseline.requested_at,
        ),
        baseline_request=baseline,
    )
    result = owner().client("caller:test").invoke(request)
    assert result.assessment == direct
    assert result.assessment.policy_id == direct.policy_id
    assert result.assessment.candidate_class == direct.candidate_class
    assert direct.candidate_class is CandidateClass.NO_TRADE
    assert result.assessment.eligible is False


def test_opportunity_assemble_has_direct_a39_parity_without_specialist_rerun() -> None:
    package = load_package_json(content("artifact:a3-package"))
    capture = package_blob(package, BlobKind.A38_CAPTURE).content
    facade_request_id = "facade-opportunity"
    direct = assemble_opportunity_intelligence(
        request_from_capture(capture, request_id=facade_request_id, policy=default_policy())
    )
    request = OpportunityAssembleRequest(
        scope=scope(
            request_id=facade_request_id,
            subject=package.manifest.subject,
            objective=package.manifest.purpose,
            horizon=package.manifest.horizon,
            as_of=package.manifest.as_of,
            artifacts=("artifact:a38",),
        ),
        orchestration_capture_ref="artifact:a38",
    )
    result = owner().client("caller:test").invoke(request)
    assert result.intelligence == direct.result
    assert result.run_fingerprint == direct.fingerprint
    assert result.capture_checksum == direct.request.capture_checksum
    assert "capture_json" not in result.model_dump_json()
    assert result.metadata.usage.tool_calls == 0
    assert result.metadata.usage.model_calls == 0


def test_a4_input_project_has_foundation_parity_and_no_disposition() -> None:
    build_input = ProjectionBuildInput.model_validate_json(
        content("artifact:foundation-input")
    )
    direct = build_projection(build_input)
    request = A4InputProjectRequest(
        scope=scope(
            request_id="facade-a4-input",
            subject=build_input.header.subject,
            objective=AnalysisPurpose(build_input.header.objective),
            horizon=build_input.header.horizon,
            as_of=build_input.header.evidence_as_of,
            artifacts=("artifact:foundation-input",),
        ),
        build_input_ref="artifact:foundation-input",
    )
    result = owner().client("caller:test").invoke(request)
    assert result.projection == direct
    assert not hasattr(result.projection, "disposition")
    assert result.metadata.gaps == tuple(item.code for item in direct.gaps)


def test_a4_input_project_preserves_optional_missing_evidence_as_gap() -> None:
    gap = ProjectionGap(
        gap_id="gap:facade-optional-source-detail",
        missingness=Missingness.OPTIONAL,
        code="OPTIONAL_SOURCE_DETAIL_UNAVAILABLE",
        affected_reference="source:ril",
        reason="not included in captured parent",
    )
    build_input = foundation_build_input().model_copy(update={"gaps": (gap,)})
    custom = artifact(
        "artifact:foundation-input-with-gap",
        ArtifactKind.FOUNDATION_BUILD_INPUT,
        canonical_json(build_input),
    )
    facade = create_local_facade(
        config().model_copy(update={"artifacts": (*captured_artifacts(), custom)})
    )
    request = A4InputProjectRequest(
        scope=scope(
            request_id="facade-a4-input-gap",
            subject=build_input.header.subject,
            objective=AnalysisPurpose(build_input.header.objective),
            horizon=build_input.header.horizon,
            as_of=build_input.header.evidence_as_of,
            artifacts=(custom.artifact_ref,),
        ),
        build_input_ref=custom.artifact_ref,
    )
    result = facade.client("caller:test").invoke(request)
    assert result.projection.gaps == (gap,)
    assert result.metadata.gaps == (gap.code,)


def test_a4_evaluate_has_direct_deterministic_parity_and_zero_external_usage() -> None:
    projection = replay_foundation(content("artifact:foundation-capture"))
    direct = evaluate_projection(
        projection,
        evaluated_at=projection.header.evidence_as_of,
    )
    request = A4EvaluateRequest(
        scope=scope(
            request_id="facade-a4-evaluate",
            subject=projection.header.subject,
            objective=AnalysisPurpose(projection.header.objective),
            horizon=projection.header.horizon,
            as_of=projection.header.evidence_as_of,
            artifacts=("artifact:foundation-capture",),
        ),
        projection_capture_ref="artifact:foundation-capture",
    )
    result = owner().client("caller:test").invoke(request)
    assert result.evaluation == direct.result
    assert result.run_fingerprint == direct.fingerprint
    assert result.metadata.usage.model_calls == 0
    assert result.metadata.usage.tool_calls == 0
    assert "policy" not in A4EvaluateRequest.model_fields


def test_a4_evaluate_rejects_unadmitted_projection_capture() -> None:
    projection = replay_foundation(content("artifact:foundation-capture"))
    with pytest.raises(ValueError, match="exactly its projection capture"):
        A4EvaluateRequest(
            scope=scope(
                request_id="facade-a4-unadmitted",
                subject=projection.header.subject,
                objective=AnalysisPurpose(projection.header.objective),
                horizon=projection.header.horizon,
                as_of=projection.header.evidence_as_of,
            ),
            projection_capture_ref="artifact:foundation-capture",
        )


@pytest.mark.parametrize(
    ("artifact_ref", "expected_kind"),
    (
        ("artifact:a3-package", ReplayResultKind.A3_RECORDED),
        ("artifact:foundation-capture", ReplayResultKind.FOUNDATION_RECORDED),
    ),
)
def test_recorded_replay_parity_and_zero_external_usage(
    artifact_ref: str,
    expected_kind: ReplayResultKind,
) -> None:
    package = load_package_json(content("artifact:a3-package"))
    request = RecordedReplayRequest(
        scope=scope(
            request_id=f"facade-replay-{expected_kind.value.casefold()}",
            subject=package.manifest.subject,
            objective=package.manifest.purpose,
            horizon=package.manifest.horizon,
            as_of=package.manifest.as_of,
            artifacts=(artifact_ref,),
        ),
        artifact_ref=artifact_ref,
    )
    result = owner().client("caller:test").invoke(request)
    assert result.kind is expected_kind
    assert result.metadata.usage.model_calls == result.metadata.usage.tool_calls == 0
    if expected_kind is ReplayResultKind.A3_RECORDED:
        direct = replay_a3_package(package, replayed_at=package.manifest.as_of)
        assert result.a3_replay is not None
        assert result.a3_replay.fingerprint == direct.fingerprint
        assert result.a3_replay.semantic_match == direct.semantic_match
    else:
        assert result.foundation_projection == replay_foundation(content(artifact_ref))


def test_engineering_replay_verify_has_direct_parity() -> None:
    package = load_package_json(content("artifact:a3-package"))
    request = ReplayVerifyRequest(
        scope=scope(
            request_id="facade-verify",
            subject=package.manifest.subject,
            objective=package.manifest.purpose,
            horizon=package.manifest.horizon,
            as_of=package.manifest.as_of,
            artifacts=("artifact:a3-package",),
        ),
        artifact_ref="artifact:a3-package",
    )
    result = owner().client("caller:test").invoke(request)
    direct = verify_a3_package(package, verified_at=package.manifest.as_of)
    assert result.verification.fingerprint == direct.fingerprint
    assert result.verification.components == direct.components
    assert result.verification.passed == direct.passed


@pytest.mark.parametrize("mismatch", ("subject", "horizon", "as_of", "objective"))
def test_wrong_captured_subject_horizon_as_of_or_objective_fails_safe(
    mismatch: str,
) -> None:
    package = load_package_json(content("artifact:a3-package"))
    captured_scope = scope(
        request_id=f"scope-mismatch-{mismatch}",
        subject=package.manifest.subject,
        objective=package.manifest.purpose,
        horizon=package.manifest.horizon,
        as_of=package.manifest.as_of,
        artifacts=("artifact:a3-package",),
    )
    changed = {
        "subject": "RELIANCE",
        "horizon": package.manifest.horizon.model_copy(update={"label": "DAY"}),
        "as_of": package.manifest.as_of.replace(year=package.manifest.as_of.year - 1),
        "objective": AnalysisPurpose.POSITION,
    }
    request = RecordedReplayRequest(
        scope=captured_scope.model_copy(update={mismatch: changed[mismatch]}),
        artifact_ref="artifact:a3-package",
    )
    with pytest.raises(FacadeInvocationError) as exc:
        owner().client("caller:test").invoke(request)
    assert exc.value.record.status is FacadeStatus.FAILED
    assert "SYNTHETIC" not in exc.value.record.model_dump_json()


def test_result_serialization_contains_no_captured_payload_or_credentials() -> None:
    build_input = ProjectionBuildInput.model_validate_json(
        content("artifact:foundation-input")
    )
    request = A4InputProjectRequest(
        scope=scope(
            request_id="safe-result",
            subject=build_input.header.subject,
            objective=AnalysisPurpose(build_input.header.objective),
            horizon=build_input.header.horizon,
            as_of=build_input.header.evidence_as_of,
            artifacts=("artifact:foundation-input",),
        ),
        build_input_ref="artifact:foundation-input",
    )
    result = owner().client("caller:test").invoke(request)
    payload = json.loads(result.model_dump_json())
    assert "access_token" not in json.dumps(payload).casefold()
    assert "build_input_json" not in payload
