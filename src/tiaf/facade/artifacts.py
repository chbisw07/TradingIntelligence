"""Trusted in-memory artifact boundary using logical references only."""

import json
from collections.abc import Mapping
from typing import Any

from tiaf.a3_hardening import exact_bytes_checksum, load_package_json
from tiaf.a5 import (
    A5Capture,
    PositionIntelligenceRequest,
    deterministic_policy,
)
from tiaf.a5 import (
    validate_capture as validate_a5_capture,
)
from tiaf.a5 import (
    validate_request as validate_a5_request,
)
from tiaf.source_semantics import (
    FoundationCapture,
    ProjectionBuildInput,
    validate_foundation_capture,
)
from tiaf.workflows import replay_recorded as replay_orchestration

from .contracts import EffectiveAdmission, TrustedArtifact
from .enums import ArtifactKind

_SECRET_KEYS = {
    "access_token",
    "api_key",
    "authorization",
    "client_secret",
    "password",
    "private_key",
    "refresh_token",
}


def _has_secret_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            str(key).casefold().replace("-", "_") in _SECRET_KEYS
            or _has_secret_key(item)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple)):
        return any(_has_secret_key(item) for item in value)
    return False


def validate_trusted_artifact(artifact: TrustedArtifact) -> TrustedArtifact:
    """Validate captured semantics and reject secret-bearing JSON before startup."""
    if exact_bytes_checksum(artifact.content) != artifact.checksum:
        raise ValueError("trusted artifact checksum mismatch")
    try:
        decoded = json.loads(artifact.content)
    except json.JSONDecodeError as exc:
        raise ValueError("trusted artifact must be JSON") from exc
    if _has_secret_key(decoded):
        raise ValueError("trusted artifact contains a secret-bearing field")
    if artifact.kind is ArtifactKind.A38_CAPTURE:
        replay_orchestration(artifact.content)
    elif artifact.kind is ArtifactKind.A3_PACKAGE:
        load_package_json(artifact.content)
    elif artifact.kind is ArtifactKind.FOUNDATION_BUILD_INPUT:
        ProjectionBuildInput.model_validate_json(artifact.content)
    elif artifact.kind is ArtifactKind.FOUNDATION_CAPTURE:
        validate_foundation_capture(FoundationCapture.model_validate_json(artifact.content))
    elif artifact.kind is ArtifactKind.A5_POSITION_REQUEST:
        request = PositionIntelligenceRequest.model_validate_json(artifact.content)
        validate_a5_request(
            request,
            deterministic_policy(version=request.policy_version),
        )
    elif artifact.kind is ArtifactKind.A5_CAPTURE:
        validate_a5_capture(A5Capture.model_validate_json(artifact.content))
    return artifact


class LocalArtifactStore:
    """Private startup-only artifact map; callers see neither paths nor payloads."""

    def __init__(self) -> None:
        self._artifacts: dict[str, TrustedArtifact] = {}
        self._frozen = False

    def add(self, artifact: TrustedArtifact) -> None:
        if self._frozen:
            raise RuntimeError("startup artifact composition is frozen")
        artifact = validate_trusted_artifact(artifact)
        if artifact.artifact_ref in self._artifacts:
            raise ValueError("duplicate trusted artifact reference")
        self._artifacts[artifact.artifact_ref] = artifact

    def freeze(self) -> None:
        self._frozen = True

    def read(self, artifact_ref: str, admission: EffectiveAdmission) -> TrustedArtifact:
        try:
            artifact = self._artifacts[artifact_ref]
        except KeyError as exc:
            raise LookupError("authorized artifact is unavailable") from exc
        if not set(artifact.required_authority_refs) <= {admission.effective_authority_ref}:
            raise PermissionError("artifact authority is not effective for this invocation")
        if not set(artifact.required_entitlement_refs) <= set(
            admission.effective_entitlement_refs
        ):
            raise PermissionError("artifact entitlement is not effective for this invocation")
        return artifact
