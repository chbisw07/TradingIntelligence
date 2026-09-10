"""Explicit recorded, deterministic-verification and policy-comparison replay."""

from datetime import datetime
from time import monotonic

from tiaf.agents import AgentUsage
from tiaf.baseline import default_policy as default_baseline_policy
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.evaluation import ReplayRequest as BaselineReplayRequest
from tiaf.evaluation import replay as replay_baseline
from tiaf.evaluation.store import load_case_json
from tiaf.planner.digests import digest
from tiaf.service.opportunity_intelligence import (
    OpportunitySynthesisPolicy,
    assemble_opportunity_intelligence,
    replay_intelligence,
    verify_intelligence,
)
from tiaf.workflows import default_registry
from tiaf.workflows.replay import replay_recorded, verify_deterministic

from .contracts import (
    A2CaptureMode,
    A3PolicyComparisonRecord,
    A3ReplayResult,
    A3VerificationResult,
    BlobKind,
    CaptureOrigin,
    PolicyComparisonError,
    PortableA3ReplayPackage,
    ReplayMode,
    VerificationComponent,
    VerificationDisposition,
)
from .package import package_blob, validate_package


def _now(value: datetime | None) -> datetime:
    return value or datetime.now(TIAF_TIMEZONE)


def replay_a3_package(
    package: PortableA3ReplayPackage, *, replayed_at: datetime | None = None
) -> A3ReplayResult:
    """Recorded replay only; missing content cannot fall through to live access."""
    started = monotonic()
    package = validate_package(package)
    a38 = replay_recorded(package_blob(package, BlobKind.A38_CAPTURE).content)
    a39 = replay_intelligence(package_blob(package, BlobKind.A39_CAPTURE).content)
    match = (
        a38.fingerprint == package.manifest.a38_semantic_fingerprint
        and a39.fingerprint == package.manifest.a39_semantic_fingerprint
    )
    when = _now(replayed_at)
    payload = {
        "package_id": package.manifest.package_id,
        "mode": ReplayMode.RECORDED,
        "a2_mode": package.manifest.a2_capture.mode,
        "a38_fingerprint": a38.fingerprint,
        "a39_fingerprint": a39.fingerprint,
        "semantic_match": match,
    }
    fingerprint = digest(payload)
    return A3ReplayResult(
        replay_id=f"recorded:{fingerprint[:24]}",
        package_id=package.manifest.package_id,
        a2_mode=package.manifest.a2_capture.mode,
        a38_fingerprint=a38.fingerprint,
        a39_fingerprint=a39.fingerprint,
        semantic_match=match,
        replay_usage=AgentUsage(elapsed_seconds=monotonic() - started),
        replayed_at=when,
        fingerprint=fingerprint,
    )


def verify_a3_package(
    package: PortableA3ReplayPackage, *, verified_at: datetime | None = None
) -> A3VerificationResult:
    """Re-execute only accepted deterministic logic over complete captured inputs."""
    started = monotonic()
    package = validate_package(package)
    manifest = package.manifest
    a38_content = package_blob(package, BlobKind.A38_CAPTURE).content
    a39_content = package_blob(package, BlobKind.A39_CAPTURE).content
    components: list[VerificationComponent] = []

    if manifest.a2_capture.mode is A2CaptureMode.FULL_BASELINE_CASE:
        case = load_case_json(package_blob(package, BlobKind.A2_CAPTURE).content)
        policy = default_baseline_policy(case.snapshot.trade_style)
        if (
            policy.policy_id == case.snapshot.policy_id
            and policy.policy_version == case.snapshot.policy_version
        ):
            verified = replay_baseline(
                BaselineReplayRequest(
                    snapshot=case.snapshot,
                    policy=policy,
                    expected_assessment=case.run_record.assessment,
                    replay_time=_now(verified_at),
                )
            )
            components.append(
                VerificationComponent(
                    component="A2_BASELINE",
                    disposition=VerificationDisposition.REEXECUTED_DETERMINISTIC,
                    recorded_fingerprint=case.snapshot.fingerprint,
                    verified_fingerprint=verified.evidence_fingerprint,
                    match=verified.exact_match,
                )
            )
        else:
            components.append(
                VerificationComponent(
                    component="A2_BASELINE",
                    disposition=VerificationDisposition.UNVERIFIABLE,
                    recorded_fingerprint=case.snapshot.fingerprint,
                    reason="CAPTURED_POLICY_NOT_AVAILABLE_AS_ACCEPTED_DEFAULT",
                )
            )
    else:
        components.append(
            VerificationComponent(
                component="A2_BASELINE",
                disposition=VerificationDisposition.NOT_APPLICABLE,
                recorded_fingerprint=manifest.a2_evidence_fingerprint,
                reason="ORIGINAL_A38_PROJECTION_IS_NOT_A_FULL_A2_SNAPSHOT",
            )
        )

    a38 = replay_recorded(a38_content)
    has_model_output = any(o.usage.llm_calls for o in a38.result.opinions)
    if has_model_output or manifest.origin is CaptureOrigin.SYNTHETIC:
        components.append(
            VerificationComponent(
                component="A3_8_ORCHESTRATION_SPECIALISTS",
                disposition=VerificationDisposition.RECORDED_ONLY,
                recorded_fingerprint=a38.fingerprint,
                reason=(
                    "MODEL_OUTPUT_RECORDED_ONLY"
                    if has_model_output
                    else "SYNTHETIC_PRECOMPUTED_SPECIALIST_OUTPUTS"
                ),
            )
        )
    else:
        try:
            verified38 = verify_deterministic(a38_content, default_registry())
            components.append(
                VerificationComponent(
                    component="A3_8_ORCHESTRATION_SPECIALISTS",
                    disposition=VerificationDisposition.REEXECUTED_DETERMINISTIC,
                    recorded_fingerprint=a38.fingerprint,
                    verified_fingerprint=verified38.fingerprint,
                    match=verified38.fingerprint == a38.fingerprint,
                )
            )
        except ValueError as exc:
            components.append(
                VerificationComponent(
                    component="A3_8_ORCHESTRATION_SPECIALISTS",
                    disposition=VerificationDisposition.UNVERIFIABLE,
                    recorded_fingerprint=a38.fingerprint,
                    reason=f"CAPTURED_REGISTRY_MISMATCH:{type(exc).__name__}",
                )
            )

    a39 = replay_intelligence(a39_content)
    verified39 = verify_intelligence(a39_content)
    components.append(
        VerificationComponent(
            component="A3_9_SYNTHESIS",
            disposition=VerificationDisposition.REEXECUTED_DETERMINISTIC,
            recorded_fingerprint=a39.fingerprint,
            verified_fingerprint=verified39.verified_fingerprint,
            match=verified39.exact_match,
        )
    )
    passed = all(c.match is not False for c in components) and not any(
        c.disposition is VerificationDisposition.UNVERIFIABLE for c in components
    )
    when = _now(verified_at)
    payload = {
        "package_id": manifest.package_id,
        "components": [c.model_dump(mode="json") for c in components],
        "passed": passed,
    }
    fingerprint = digest(payload)
    return A3VerificationResult(
        verification_id=f"verification:{fingerprint[:24]}",
        package_id=manifest.package_id,
        components=tuple(components),
        passed=passed,
        execution_usage=AgentUsage(elapsed_seconds=monotonic() - started),
        verified_at=when,
        fingerprint=fingerprint,
    )


def compare_a3_policy(
    package: PortableA3ReplayPackage,
    candidate_policy: OpportunitySynthesisPolicy,
    *,
    compared_at: datetime | None = None,
) -> A3PolicyComparisonRecord:
    """Create a new record; never label a policy change as historical replay."""
    started = monotonic()
    package = validate_package(package)
    old = replay_intelligence(package_blob(package, BlobKind.A39_CAPTURE).content)
    try:
        new = assemble_opportunity_intelligence(
            old.request.model_copy(update={"policy": candidate_policy})
        )
    except ValueError as exc:
        raise PolicyComparisonError(
            "candidate A3.9 policy is not implemented as a compatible pure policy version"
        ) from exc
    old_json = old.model_dump(mode="json")
    new_json = new.model_dump(mode="json")
    differences = tuple(
        sorted(
            key
            for key in set(old_json) | set(new_json)
            if key not in {"assembled_at", "assembly_usage"}
            and old_json.get(key) != new_json.get(key)
        )
    )
    when = _now(compared_at)
    payload = {
        "package_id": package.manifest.package_id,
        "old_policy": (old.request.policy.policy_id, old.request.policy.version),
        "new_policy": (candidate_policy.policy_id, candidate_policy.version),
        "old_fingerprint": old.fingerprint,
        "new_fingerprint": new.fingerprint,
        "differences": differences,
    }
    fingerprint = digest(payload)
    return A3PolicyComparisonRecord(
        comparison_id=f"policy-comparison:{fingerprint[:24]}",
        package_id=package.manifest.package_id,
        old_policy_id=old.request.policy.policy_id,
        old_policy_version=old.request.policy.version,
        new_policy_id=candidate_policy.policy_id,
        new_policy_version=candidate_policy.version,
        old_fingerprint=old.fingerprint,
        new_fingerprint=new.fingerprint,
        exact_match=not differences,
        differences=differences,
        execution_usage=AgentUsage(elapsed_seconds=monotonic() - started),
        compared_at=when,
        fingerprint=fingerprint,
    )
