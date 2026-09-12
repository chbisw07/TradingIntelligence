"""Trusted synthetic facade composition over already-captured fixtures."""

from datetime import datetime
from functools import lru_cache

from tiaf.a3_hardening import (
    BlobKind,
    canonical_json,
    exact_bytes_checksum,
    package_blob,
    package_json,
)
from tiaf.a5 import (
    capture_json as capture_a5_json,
)
from tiaf.a5 import (
    capture_run,
    evaluate_position,
)
from tiaf.context import AnalysisPurpose
from tiaf.contracts import Horizon
from tiaf.facade import (
    ArtifactKind,
    CallerGrant,
    FacadeAuthorityScope,
    InvocationBudget,
    InvocationScope,
    LocalFacadeOwner,
    OperatorPolicy,
    TrustedArtifact,
    TrustedFacadeConfig,
    create_local_facade,
)
from tiaf.source_semantics import capture_json as capture_foundation_json
from tiaf.source_semantics import capture_projection

from ..a3_hardening._support import package_for
from ..a5._support import request as a5_request
from ..source_semantics._support import build_input

ALL_CAPABILITIES = (
    "a4.evaluate",
    "a4_input.project",
    "baseline.assess",
    "capabilities.list",
    "opportunity.assemble",
    "position.assess",
    "replay.recorded",
    "replay.verify",
)
ALL_SCOPES = tuple(FacadeAuthorityScope)
AUTHORITY = "authority:facade-default"
ENTITLEMENT = "entitlement:captured-market-data"
POSITION_ENTITLEMENT = "entitlement:position-synthetic-one"
PROFILE = "profile:deterministic"


def artifact(
    ref: str,
    kind: ArtifactKind,
    content: str,
    *,
    entitlement_refs: tuple[str, ...] = (ENTITLEMENT,),
) -> TrustedArtifact:
    return TrustedArtifact(
        artifact_ref=ref,
        kind=kind,
        content=content,
        checksum=exact_bytes_checksum(content),
        required_authority_refs=(AUTHORITY,),
        required_entitlement_refs=entitlement_refs,
    )


@lru_cache(maxsize=1)
def captured_artifacts() -> tuple[TrustedArtifact, ...]:
    package = package_for()
    a38 = package_blob(package, BlobKind.A38_CAPTURE).content
    foundation_input = build_input(package=package)
    foundation_capture = capture_projection(
        foundation_input,
        captured_at=foundation_input.header.evidence_as_of,
    )
    position_request = a5_request()
    position_request = position_request.model_copy(
        update={
            "snapshot": position_request.snapshot.model_copy(
                update={"authority_refs": (AUTHORITY,)}
            ),
            "authority_refs": (AUTHORITY,),
        }
    )
    position_record = evaluate_position(
        position_request,
        evaluated_at=position_request.as_of,
    )
    position_capture = capture_run(
        position_record,
        captured_at=position_request.as_of,
    )
    return (
        artifact("artifact:a38", ArtifactKind.A38_CAPTURE, a38),
        artifact("artifact:a3-package", ArtifactKind.A3_PACKAGE, package_json(package)),
        artifact(
            "artifact:foundation-input",
            ArtifactKind.FOUNDATION_BUILD_INPUT,
            canonical_json(foundation_input),
        ),
        artifact(
            "artifact:foundation-capture",
            ArtifactKind.FOUNDATION_CAPTURE,
            capture_foundation_json(foundation_capture),
        ),
        artifact(
            "artifact:position-request",
            ArtifactKind.A5_POSITION_REQUEST,
            canonical_json(position_request),
            entitlement_refs=(POSITION_ENTITLEMENT,),
        ),
        artifact(
            "artifact:a5-capture",
            ArtifactKind.A5_CAPTURE,
            capture_a5_json(position_capture),
            entitlement_refs=(POSITION_ENTITLEMENT,),
        ),
    )


def config(
    *,
    caller_capabilities: tuple[str, ...] = ALL_CAPABILITIES,
    caller_scopes: tuple[FacadeAuthorityScope, ...] = ALL_SCOPES,
    caller_entitlements: tuple[str, ...] = (ENTITLEMENT, POSITION_ENTITLEMENT),
    engineering: bool = True,
) -> TrustedFacadeConfig:
    budget = InvocationBudget(max_elapsed_seconds=30)
    caller = CallerGrant(
        caller_id="caller:test",
        grant_id="grant:test",
        allowed_capabilities=caller_capabilities,
        authority_scopes=caller_scopes,
        authority_refs=(AUTHORITY,),
        entitlement_refs=caller_entitlements,
        allowed_profiles=(PROFILE,),
        engineering_allowed=engineering,
        budget_ceiling=budget,
    )
    operator = OperatorPolicy(
        policy_id="operator-policy:local",
        policy_version="1.0",
        allowed_capabilities=ALL_CAPABILITIES,
        authority_scopes=ALL_SCOPES,
        authority_refs=(AUTHORITY,),
        entitlement_refs=(ENTITLEMENT, POSITION_ENTITLEMENT),
        allowed_profiles=(PROFILE,),
        engineering_enabled=True,
        budget_ceiling=budget,
    )
    return TrustedFacadeConfig(
        operator=operator,
        caller_grants=(caller,),
        artifacts=captured_artifacts(),
        artifact_root_ref="artifact-root:test",
    )


def owner(
    *,
    caller_capabilities: tuple[str, ...] = ALL_CAPABILITIES,
    caller_scopes: tuple[FacadeAuthorityScope, ...] = ALL_SCOPES,
    caller_entitlements: tuple[str, ...] = (ENTITLEMENT, POSITION_ENTITLEMENT),
    engineering: bool = True,
) -> LocalFacadeOwner:
    return create_local_facade(
        config(
            caller_capabilities=caller_capabilities,
            caller_scopes=caller_scopes,
            caller_entitlements=caller_entitlements,
            engineering=engineering,
        )
    )


def scope(
    *,
    request_id: str,
    subject: str,
    objective: AnalysisPurpose,
    horizon: Horizon,
    as_of: datetime,
    artifacts: tuple[str, ...] = (),
) -> InvocationScope:
    return InvocationScope(
        request_id=request_id,
        correlation_id=f"correlation:{request_id}",
        subject=subject,
        objective=objective,
        horizon=horizon,
        as_of=as_of,
        profile_ref=PROFILE,
        requested_authority_ref=AUTHORITY,
        requested_budget=InvocationBudget(max_elapsed_seconds=30),
        admitted_artifact_refs=artifacts,
    )
