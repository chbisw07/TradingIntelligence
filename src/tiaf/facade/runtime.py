"""Trusted same-process facade composition and invocation lifecycle owner."""

import threading
from collections.abc import Mapping
from datetime import datetime
from time import monotonic
from typing import Any, overload
from uuid import uuid4

from pydantic import ValidationError

from tiaf.a3_hardening import (
    A3HardeningError,
    load_package_json,
    replay_a3_package,
    verify_a3_package,
)
from tiaf.a4 import (
    A4EvaluationError,
    A4InputIntegrityError,
    evaluate_projection,
)
from tiaf.a5 import (
    A5Capture,
    A5InputIntegrityError,
    A5ReplayIntegrityError,
    PositionIntelligenceRequest,
    deterministic_policy,
    evaluate_position,
)
from tiaf.a5 import (
    replay_recorded as replay_a5,
)
from tiaf.baseline import BaselineEngine, BaselineError
from tiaf.context import AnalysisPurpose
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.planner.digests import digest
from tiaf.service.opportunity_intelligence import (
    CaptureIntegrityError,
    assemble_opportunity_intelligence,
    default_policy,
    request_from_capture,
)
from tiaf.source_semantics import (
    ProjectionBuildInput,
    ProjectionIntegrityError,
    build_projection,
)
from tiaf.source_semantics import (
    replay_recorded as replay_foundation,
)

from .admission import admit, can_discover
from .artifacts import LocalArtifactStore
from .capabilities import capability_catalog, descriptor_for
from .contracts import (
    A4EvaluateRequest,
    A4EvaluateResult,
    A4InputProjectRequest,
    A4InputProjectResult,
    BaselineAssessRequest,
    BaselineAssessResult,
    CallerGrant,
    CapabilityListRequest,
    CapabilityListResult,
    EffectiveAdmission,
    FacadeErrorRecord,
    FacadeOperationRequest,
    FacadeRequest,
    FacadeResult,
    InvocationBudget,
    InvocationMetadata,
    InvocationScope,
    InvocationUsage,
    OpportunityAssembleRequest,
    OpportunityAssembleResult,
    PositionAssessRequest,
    PositionAssessResult,
    RecordedReplayRequest,
    RecordedReplayResult,
    ReplayVerifyRequest,
    ReplayVerifyResult,
    TrustedArtifact,
    TrustedFacadeConfig,
)
from .enums import ArtifactKind, FacadeStatus, LifecycleState, ReplayResultKind
from .errors import FacadeInvocationError

_SECRET_KEYS = {
    "access_token",
    "api_key",
    "authorization",
    "client_secret",
    "password",
    "private_key",
    "refresh_token",
}


def _unsafe_caller_value(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            str(key).casefold().replace("-", "_") in _SECRET_KEYS
            or _unsafe_caller_value(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_unsafe_caller_value(item) for item in value)
    if isinstance(value, str):
        return "://" in value or value.startswith(("/", "~", ".."))
    return False


def _validate_caller_request(request: FacadeOperationRequest) -> None:
    try:
        payload = request.model_dump(mode="json")
    except (TypeError, ValueError) as exc:
        raise ValueError("request contains a non-serializable value") from exc
    if _unsafe_caller_value(payload):
        raise ValueError("request contains a forbidden path, URL, or secret-bearing field")


class LocalFacadeClient:
    """Caller-bound handle exposing no composition, registry or storage object."""

    def __init__(self, owner: "LocalFacadeOwner", caller_id: str) -> None:
        self.__owner = owner
        self.__caller_id = caller_id

    def list_capabilities(self, request: CapabilityListRequest) -> CapabilityListResult:
        return self.__owner._list_capabilities(self.__caller_id, request)

    @overload
    def invoke(self, request: BaselineAssessRequest) -> BaselineAssessResult: ...

    @overload
    def invoke(self, request: OpportunityAssembleRequest) -> OpportunityAssembleResult: ...

    @overload
    def invoke(self, request: A4InputProjectRequest) -> A4InputProjectResult: ...

    @overload
    def invoke(self, request: A4EvaluateRequest) -> A4EvaluateResult: ...

    @overload
    def invoke(self, request: PositionAssessRequest) -> PositionAssessResult: ...

    @overload
    def invoke(self, request: RecordedReplayRequest) -> RecordedReplayResult: ...

    @overload
    def invoke(self, request: ReplayVerifyRequest) -> ReplayVerifyResult: ...

    @overload
    def invoke(self, request: FacadeOperationRequest) -> FacadeResult: ...

    def invoke(self, request: FacadeRequest | FacadeOperationRequest) -> FacadeResult:
        return self.__owner._invoke(self.__caller_id, request)


class LocalFacadeOwner:
    """Trusted composition owner. Mutable request state never escapes an invocation."""

    def __init__(self, config: TrustedFacadeConfig) -> None:
        self._config = TrustedFacadeConfig.model_validate_json(config.model_dump_json())
        self._callers = {item.caller_id: item for item in self._config.caller_grants}
        self._artifacts = LocalArtifactStore()
        self._baseline = BaselineEngine()
        self._state = LifecycleState.CONFIGURING
        self._revoked: set[str] = set()
        self._active: set[str] = set()
        self._lock = threading.RLock()
        for artifact in self._config.artifacts:
            self._artifacts.add(artifact)

    @property
    def state(self) -> LifecycleState:
        return self._state

    def add_startup_artifact(self, artifact: TrustedArtifact) -> None:
        with self._lock:
            if self._state is not LifecycleState.CONFIGURING:
                raise RuntimeError("startup composition is frozen")
            self._artifacts.add(artifact)

    def start(self) -> None:
        with self._lock:
            if self._state is not LifecycleState.CONFIGURING:
                raise RuntimeError("facade can start exactly once")
            self._artifacts.freeze()
            self._state = LifecycleState.STARTED

    def shutdown(self) -> None:
        with self._lock:
            if self._active:
                raise RuntimeError("cannot shut down while invocations are active")
            self._state = LifecycleState.SHUTDOWN

    def revoke_caller(self, caller_id: str) -> None:
        """Trusted policy revocation; checked again on every invocation/artifact read."""
        with self._lock:
            self._revoked.add(caller_id)

    def client(self, caller_id: str) -> LocalFacadeClient:
        if caller_id not in self._callers:
            raise PermissionError("caller has no trusted local grant")
        return LocalFacadeClient(self, caller_id)

    def _caller(self, caller_id: str) -> CallerGrant:
        with self._lock:
            if self._state is not LifecycleState.STARTED:
                raise RuntimeError("facade is not accepting invocations")
            if caller_id in self._revoked:
                raise PermissionError("caller grant is revoked")
            return self._callers[caller_id]

    @staticmethod
    def _error(
        *,
        request_id: str,
        correlation_id: str,
        capability_id: str,
        status: FacadeStatus,
        message: str,
        child_codes: tuple[str, ...] = (),
    ) -> FacadeInvocationError:
        return FacadeInvocationError(
            FacadeErrorRecord(
                request_id=request_id,
                correlation_id=correlation_id,
                capability_id=capability_id,
                status=status,
                message=message,
                child_codes=child_codes,
                occurred_at=datetime.now(TIAF_TIMEZONE),
            )
        )

    def _list_capabilities(
        self,
        caller_id: str,
        request: CapabilityListRequest,
    ) -> CapabilityListResult:
        descriptor = descriptor_for(request.capability_id)
        assert descriptor is not None
        try:
            caller = self._caller(caller_id)
            admission = admit(
                descriptor,
                caller,
                self._config.operator,
                profile_ref=request.profile_ref,
                authority_ref=request.requested_authority_ref,
                requested_budget=InvocationBudget(),
            )
        except PermissionError as exc:
            raise self._error(
                request_id=request.request_id,
                correlation_id=request.correlation_id,
                capability_id=request.capability_id,
                status=FacadeStatus.PERMISSION_DENIED,
                message="capability discovery is not permitted",
                child_codes=(type(exc).__name__,),
            ) from exc
        except RuntimeError as exc:
            raise self._error(
                request_id=request.request_id,
                correlation_id=request.correlation_id,
                capability_id=request.capability_id,
                status=FacadeStatus.UNAVAILABLE,
                message="local facade is unavailable",
                child_codes=(type(exc).__name__,),
            ) from exc
        run_id = f"facade-run:{uuid4().hex}"
        with self._lock:
            if self._state is not LifecycleState.STARTED or caller_id in self._revoked:
                raise self._error(
                    request_id=request.request_id,
                    correlation_id=request.correlation_id,
                    capability_id=request.capability_id,
                    status=FacadeStatus.UNAVAILABLE,
                    message="local facade stopped before discovery began",
                )
            self._active.add(run_id)
        try:
            visible = tuple(
                item
                for item in capability_catalog()
                if can_discover(
                    item,
                    caller,
                    self._config.operator,
                    profile_ref=request.profile_ref,
                    authority_ref=request.requested_authority_ref,
                )
            )
            now = datetime.now(TIAF_TIMEZONE)
            metadata = self._metadata(
                request_id=request.request_id,
                run_id=run_id,
                correlation_id=request.correlation_id,
                scope=None,
                admission=admission,
                started=now,
                completed=now,
            )
            return CapabilityListResult(metadata=metadata, capabilities=visible)
        finally:
            with self._lock:
                self._active.discard(run_id)

    def _invoke(
        self,
        caller_id: str,
        request: FacadeRequest | FacadeOperationRequest,
    ) -> FacadeResult:
        descriptor = descriptor_for(request.capability_id)
        if descriptor is None:
            raise self._error(
                request_id=request.scope.request_id,
                correlation_id=request.scope.correlation_id,
                capability_id=request.capability_id,
                status=FacadeStatus.UNSUPPORTED,
                message="capability is not implemented by this facade",
            )
        expected_type = {
            "baseline.assess": BaselineAssessRequest,
            "opportunity.assemble": OpportunityAssembleRequest,
            "a4_input.project": A4InputProjectRequest,
            "a4.evaluate": A4EvaluateRequest,
            "position.assess": PositionAssessRequest,
            "replay.recorded": RecordedReplayRequest,
            "replay.verify": ReplayVerifyRequest,
        }[request.capability_id]
        if not isinstance(request, expected_type):
            raise self._error(
                request_id=request.scope.request_id,
                correlation_id=request.scope.correlation_id,
                capability_id=request.capability_id,
                status=FacadeStatus.INVALID_REQUEST,
                message="request schema does not match capability descriptor",
            )
        try:
            _validate_caller_request(request)
            caller = self._caller(caller_id)
            admission = admit(
                descriptor,
                caller,
                self._config.operator,
                profile_ref=request.scope.profile_ref,
                authority_ref=request.scope.requested_authority_ref,
                requested_budget=request.scope.requested_budget,
            )
        except PermissionError as exc:
            raise self._error(
                request_id=request.scope.request_id,
                correlation_id=request.scope.correlation_id,
                capability_id=request.capability_id,
                status=FacadeStatus.PERMISSION_DENIED,
                message="capability invocation is not permitted",
                child_codes=(type(exc).__name__,),
            ) from exc
        except RuntimeError as exc:
            raise self._error(
                request_id=request.scope.request_id,
                correlation_id=request.scope.correlation_id,
                capability_id=request.capability_id,
                status=FacadeStatus.UNAVAILABLE,
                message="local facade is unavailable",
                child_codes=(type(exc).__name__,),
            ) from exc
        except (TypeError, ValueError) as exc:
            raise self._error(
                request_id=request.scope.request_id,
                correlation_id=request.scope.correlation_id,
                capability_id=request.capability_id,
                status=FacadeStatus.INVALID_REQUEST,
                message="facade request failed safe input validation",
                child_codes=(type(exc).__name__,),
            ) from exc

        run_id = f"facade-run:{uuid4().hex}"
        started_at = datetime.now(TIAF_TIMEZONE)
        started = monotonic()
        with self._lock:
            if self._state is not LifecycleState.STARTED or caller_id in self._revoked:
                raise self._error(
                    request_id=request.scope.request_id,
                    correlation_id=request.scope.correlation_id,
                    capability_id=request.capability_id,
                    status=FacadeStatus.UNAVAILABLE,
                    message="local facade stopped before invocation began",
                )
            self._active.add(run_id)
        try:
            result = self._dispatch(request, admission, started_at, run_id)
            elapsed = monotonic() - started
            if elapsed > admission.effective_budget.max_elapsed_seconds:
                raise TimeoutError("effective elapsed-time budget exceeded")
            return result
        except FacadeInvocationError:
            raise
        except PermissionError as exc:
            raise self._error(
                request_id=request.scope.request_id,
                correlation_id=request.scope.correlation_id,
                capability_id=request.capability_id,
                status=FacadeStatus.PERMISSION_DENIED,
                message="artifact access is not permitted",
                child_codes=(type(exc).__name__,),
            ) from exc
        except LookupError as exc:
            raise self._error(
                request_id=request.scope.request_id,
                correlation_id=request.scope.correlation_id,
                capability_id=request.capability_id,
                status=FacadeStatus.UNAVAILABLE,
                message="authorized artifact is unavailable",
                child_codes=(type(exc).__name__,),
            ) from exc
        except TimeoutError as exc:
            raise self._error(
                request_id=request.scope.request_id,
                correlation_id=request.scope.correlation_id,
                capability_id=request.capability_id,
                status=FacadeStatus.BUDGET_EXCEEDED,
                message="effective invocation budget was exceeded",
                child_codes=(type(exc).__name__,),
            ) from exc
        except (
            A3HardeningError,
            A4InputIntegrityError,
            A5ReplayIntegrityError,
            CaptureIntegrityError,
            ProjectionIntegrityError,
        ) as exc:
            raise self._error(
                request_id=request.scope.request_id,
                correlation_id=request.scope.correlation_id,
                capability_id=request.capability_id,
                status=FacadeStatus.REPLAY_INTEGRITY_ERROR,
                message="captured artifact failed integrity validation",
                child_codes=(type(exc).__name__,),
            ) from exc
        except A4EvaluationError as exc:
            raise self._error(
                request_id=request.scope.request_id,
                correlation_id=request.scope.correlation_id,
                capability_id=request.capability_id,
                status=FacadeStatus.FAILED,
                message="A4 evaluation failed without exposing internal state",
                child_codes=(type(exc).__name__,),
            ) from exc
        except A5InputIntegrityError as exc:
            raise self._error(
                request_id=request.scope.request_id,
                correlation_id=request.scope.correlation_id,
                capability_id=request.capability_id,
                status=FacadeStatus.FAILED,
                message="position assessment failed safe integrity validation",
                child_codes=(type(exc).__name__,),
            ) from exc
        except (BaselineError, ValidationError, TypeError, ValueError) as exc:
            raise self._error(
                request_id=request.scope.request_id,
                correlation_id=request.scope.correlation_id,
                capability_id=request.capability_id,
                status=FacadeStatus.FAILED,
                message="capability failed without exposing internal state",
                child_codes=(type(exc).__name__,),
            ) from exc
        finally:
            with self._lock:
                self._active.discard(run_id)

    def _dispatch(
        self,
        request: FacadeRequest | FacadeOperationRequest,
        admission: EffectiveAdmission,
        started_at: datetime,
        run_id: str,
    ) -> FacadeResult:
        if isinstance(request, A4EvaluateRequest):
            artifact = self._read(request.projection_capture_ref, admission)
            self._require_kind(artifact, ArtifactKind.FOUNDATION_CAPTURE)
            projection = replay_foundation(artifact.content)
            self._match_scope(
                request.scope,
                subject=projection.header.subject,
                objective=projection.header.objective,
                horizon=projection.header.horizon,
                as_of=projection.header.evidence_as_of,
            )
            a4_record = evaluate_projection(
                projection,
                evaluated_at=request.scope.as_of,
            )
            return A4EvaluateResult(
                metadata=self._metadata(
                    request_id=request.scope.request_id,
                    run_id=run_id,
                    correlation_id=request.scope.correlation_id,
                    scope=request.scope,
                    admission=admission,
                    started=started_at,
                    completed=datetime.now(TIAF_TIMEZONE),
                    policy_refs=(
                        (a4_record.policy.policy_id, a4_record.policy.policy_version),
                        (
                            a4_record.policy.challenge_policy_id,
                            a4_record.policy.challenge_policy_version,
                        ),
                        (
                            a4_record.policy.arbitration_policy_id,
                            a4_record.policy.arbitration_policy_version,
                        ),
                    ),
                    gaps=tuple(
                        item.consequence_code
                        for item in a4_record.result.residual_uncertainties
                    ),
                ),
                evaluation=a4_record.result,
                run_fingerprint=a4_record.fingerprint,
            )
        if isinstance(request, BaselineAssessRequest):
            assessment = self._baseline.assess(request.baseline_request)
            completed = datetime.now(TIAF_TIMEZONE)
            return BaselineAssessResult(
                metadata=self._metadata(
                    request_id=request.scope.request_id,
                    run_id=run_id,
                    correlation_id=request.scope.correlation_id,
                    scope=request.scope,
                    admission=admission,
                    started=started_at,
                    completed=completed,
                    policy_refs=((assessment.policy_id, assessment.policy_version),),
                    warnings=assessment.warnings,
                ),
                assessment=assessment,
            )
        if isinstance(request, OpportunityAssembleRequest):
            artifact = self._read(request.orchestration_capture_ref, admission)
            self._require_kind(artifact, ArtifactKind.A38_CAPTURE)
            opportunity_request = request_from_capture(
                artifact.content,
                request_id=request.scope.request_id,
                policy=default_policy(),
            )
            record = assemble_opportunity_intelligence(opportunity_request)
            self._match_scope(
                request.scope,
                subject=record.result.subject,
                objective=record.result.purpose,
                horizon=record.result.horizon,
                as_of=record.result.as_of,
            )
            return OpportunityAssembleResult(
                metadata=self._metadata(
                    request_id=request.scope.request_id,
                    run_id=run_id,
                    correlation_id=request.scope.correlation_id,
                    scope=request.scope,
                    admission=admission,
                    started=started_at,
                    completed=datetime.now(TIAF_TIMEZONE),
                    policy_refs=((record.result.policy_id, record.result.policy_version),),
                    gaps=record.result.completeness.gaps,
                ),
                intelligence=record.result,
                run_fingerprint=record.fingerprint,
                capture_checksum=record.request.capture_checksum,
            )
        if isinstance(request, PositionAssessRequest):
            artifact = self._read(request.position_request_ref, admission)
            self._require_kind(artifact, ArtifactKind.A5_POSITION_REQUEST)
            position_request = PositionIntelligenceRequest.model_validate_json(
                artifact.content
            )
            if admission.effective_authority_ref not in position_request.authority_refs:
                raise PermissionError("position request authority is not effective")
            if admission.effective_authority_ref not in position_request.snapshot.authority_refs:
                raise PermissionError("position snapshot authority is not effective")
            self._match_scope(
                request.scope,
                subject=position_request.snapshot.underlying,
                objective=AnalysisPurpose.POSITION,
                horizon=position_request.horizon,
                as_of=position_request.as_of,
            )
            policy = deterministic_policy(version=position_request.policy_version)
            position_record = evaluate_position(
                position_request,
                policy=policy,
                evaluated_at=position_request.as_of,
            )
            position_result = position_record.result
            return PositionAssessResult(
                metadata=self._metadata(
                    request_id=request.scope.request_id,
                    run_id=run_id,
                    correlation_id=request.scope.correlation_id,
                    scope=request.scope,
                    admission=admission,
                    started=started_at,
                    completed=datetime.now(TIAF_TIMEZONE),
                    policy_refs=(
                        (position_result.policy_id, position_result.policy_version),
                    ),
                    warnings=("ADVISORY_MONITORING_INTENT_ONLY_NOT_SCHEDULED",),
                    gaps=position_result.gaps,
                ),
                assessment=position_result,
                run_fingerprint=position_record.fingerprint,
                position_request_checksum=artifact.checksum,
            )
        if isinstance(request, A4InputProjectRequest):
            artifact = self._read(request.build_input_ref, admission)
            self._require_kind(artifact, ArtifactKind.FOUNDATION_BUILD_INPUT)
            projection = build_projection(
                ProjectionBuildInput.model_validate_json(artifact.content)
            )
            self._match_scope(
                request.scope,
                subject=projection.header.subject,
                objective=projection.header.objective,
                horizon=projection.header.horizon,
                as_of=projection.header.evidence_as_of,
            )
            return A4InputProjectResult(
                metadata=self._metadata(
                    request_id=request.scope.request_id,
                    run_id=run_id,
                    correlation_id=request.scope.correlation_id,
                    scope=request.scope,
                    admission=admission,
                    started=started_at,
                    completed=datetime.now(TIAF_TIMEZONE),
                    policy_refs=(
                        (
                            projection.header.projection_policy_id,
                            projection.header.projection_policy_version,
                        ),
                        (
                            projection.header.comparison_policy_id,
                            projection.header.comparison_policy_version,
                        ),
                    ),
                    gaps=tuple(item.code for item in projection.gaps),
                ),
                projection=projection,
            )
        if isinstance(request, RecordedReplayRequest):
            artifact = self._read(request.artifact_ref, admission)
            if artifact.kind is ArtifactKind.A5_CAPTURE:
                a5_replay_result = replay_a5(
                    A5Capture.model_validate_json(artifact.content),
                    replayed_at=request.scope.as_of,
                )
                a5_record = a5_replay_result.record
                self._match_scope(
                    request.scope,
                    subject=a5_record.request.snapshot.underlying,
                    objective=AnalysisPurpose.POSITION,
                    horizon=a5_record.request.horizon,
                    as_of=a5_record.request.as_of,
                )
                return RecordedReplayResult(
                    metadata=self._metadata(
                        request_id=request.scope.request_id,
                        run_id=run_id,
                        correlation_id=request.scope.correlation_id,
                        scope=request.scope,
                        admission=admission,
                        started=started_at,
                        completed=datetime.now(TIAF_TIMEZONE),
                        policy_refs=(
                            (
                                a5_record.result.policy_id,
                                a5_record.result.policy_version,
                            ),
                        ),
                        gaps=a5_record.result.gaps,
                    ),
                    kind=ReplayResultKind.A5_RECORDED,
                    a5_replay=a5_replay_result,
                )
            if artifact.kind is ArtifactKind.A3_PACKAGE:
                package = load_package_json(artifact.content)
                a3_replay_result = replay_a3_package(
                    package, replayed_at=request.scope.as_of
                )
                self._match_scope(
                    request.scope,
                    subject=package.manifest.subject,
                    objective=package.manifest.purpose,
                    horizon=package.manifest.horizon,
                    as_of=package.manifest.as_of,
                )
                return RecordedReplayResult(
                    metadata=self._metadata(
                        request_id=request.scope.request_id,
                        run_id=run_id,
                        correlation_id=request.scope.correlation_id,
                        scope=request.scope,
                        admission=admission,
                        started=started_at,
                        completed=datetime.now(TIAF_TIMEZONE),
                    ),
                    kind=ReplayResultKind.A3_RECORDED,
                    a3_replay=a3_replay_result,
                )
            if artifact.kind is ArtifactKind.FOUNDATION_CAPTURE:
                projection = replay_foundation(artifact.content)
                self._match_scope(
                    request.scope,
                    subject=projection.header.subject,
                    objective=projection.header.objective,
                    horizon=projection.header.horizon,
                    as_of=projection.header.evidence_as_of,
                )
                return RecordedReplayResult(
                    metadata=self._metadata(
                        request_id=request.scope.request_id,
                        run_id=run_id,
                        correlation_id=request.scope.correlation_id,
                        scope=request.scope,
                        admission=admission,
                        started=started_at,
                        completed=datetime.now(TIAF_TIMEZONE),
                    ),
                    kind=ReplayResultKind.FOUNDATION_RECORDED,
                    foundation_projection=projection,
                )
            raise ValueError("artifact kind is not eligible for recorded replay")
        if isinstance(request, ReplayVerifyRequest):
            artifact = self._read(request.artifact_ref, admission)
            self._require_kind(artifact, ArtifactKind.A3_PACKAGE)
            package = load_package_json(artifact.content)
            self._match_scope(
                request.scope,
                subject=package.manifest.subject,
                objective=package.manifest.purpose,
                horizon=package.manifest.horizon,
                as_of=package.manifest.as_of,
            )
            verification = verify_a3_package(package, verified_at=request.scope.as_of)
            return ReplayVerifyResult(
                metadata=self._metadata(
                    request_id=request.scope.request_id,
                    run_id=run_id,
                    correlation_id=request.scope.correlation_id,
                    scope=request.scope,
                    admission=admission,
                    started=started_at,
                    completed=datetime.now(TIAF_TIMEZONE),
                ),
                verification=verification,
            )
        raise ValueError("capability request type does not match implemented descriptor")

    def _read(self, artifact_ref: str, admission: EffectiveAdmission) -> TrustedArtifact:
        with self._lock:
            if admission.caller_id in self._revoked:
                raise PermissionError("caller grant was revoked before artifact read")
        return self._artifacts.read(artifact_ref, admission)

    @staticmethod
    def _require_kind(artifact: TrustedArtifact, expected: ArtifactKind) -> None:
        if artifact.kind is not expected:
            raise ValueError("artifact kind is not valid for this capability")

    @staticmethod
    def _match_scope(
        scope: InvocationScope,
        *,
        subject: str,
        objective: object,
        horizon: object,
        as_of: datetime,
    ) -> None:
        objective_value = getattr(objective, "value", objective)
        if (
            scope.subject != subject
            or scope.objective.value != objective_value
            or scope.horizon != horizon
            or scope.as_of != as_of
        ):
            raise ValueError("captured artifact identity differs from admitted invocation scope")

    def _metadata(
        self,
        *,
        request_id: str,
        run_id: str,
        correlation_id: str,
        scope: InvocationScope | None,
        admission: EffectiveAdmission,
        started: datetime,
        completed: datetime,
        policy_refs: tuple[tuple[str, str], ...] = (),
        warnings: tuple[str, ...] = (),
        gaps: tuple[str, ...] = (),
    ) -> InvocationMetadata:
        budget_fingerprint = digest(admission.effective_budget.model_dump(mode="json"))
        elapsed = max(0.0, (completed - started).total_seconds())
        return InvocationMetadata(
            request_id=request_id,
            run_id=run_id,
            correlation_id=correlation_id,
            capability_id=admission.capability_id,
            capability_version=admission.capability_version,
            status=FacadeStatus.COMPLETED,
            subject=scope.subject if scope else None,
            objective=scope.objective if scope else None,
            horizon=scope.horizon if scope else None,
            as_of=scope.as_of if scope else None,
            profile_ref=admission.profile_ref,
            effective_authority_ref=admission.effective_authority_ref,
            budget_ref=f"budget:{budget_fingerprint[:24]}",
            model_policy_ref=admission.model_policy_ref,
            position_context_ref=scope.position_context_ref if scope else None,
            operator_policy_ref=admission.operator_policy_id,
            operator_policy_version=admission.operator_policy_version,
            effect=admission.effect,
            admitted_artifact_refs=scope.admitted_artifact_refs if scope else (),
            policy_refs=policy_refs,
            warnings=warnings,
            gaps=gaps,
            usage=InvocationUsage(elapsed_seconds=elapsed),
            created_at=admission.admitted_at,
            started_at=started,
            completed_at=completed,
        )


def create_local_facade(
    config: TrustedFacadeConfig,
    *,
    start: bool = True,
) -> LocalFacadeOwner:
    """Construct trusted composition; optionally freeze/start before returning."""
    owner = LocalFacadeOwner(config)
    if start:
        owner.start()
    return owner
