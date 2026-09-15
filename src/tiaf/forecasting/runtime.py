"""Internal single-primitive COLD owner; no facade, provider or learned-model training."""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from uuid import uuid4

from .capture import (
    CapturedArtifact,
    ForecastCapture,
    ForecastEvidenceSnapshot,
    capture_artifact,
    references,
    select_artifacts,
    strict_json,
    validate_closure,
)
from .clocks import Clock, SystemClock, read_clock
from .contracts import ForecastAbsence, ForecastRequest, ForecastResult
from .enums import ForecastRealizationMode, ForecastReason, ForecastStatus
from .errors import ForecastAdmissionError, ForecastIntegrityError
from .evidence import validate_required_evidence
from .execution import ForecastExecution, InvocationUsage
from .forecasters import (
    Forecaster,
    GenerationPayload,
    dependency_artifact,
    implementation_artifacts,
    resolve_forecaster,
)
from .identity import ArtifactReference, semantic_fingerprint
from .runtime_contracts import ColdForecastConfig, ForecastBinding, SimulationProfile
from .store import ForecastCorpusStore, StoreOwner
from .support import AdmittedSupport, BaseRateArtifact, admit_support, validate_support_bars

_LOG = logging.getLogger(__name__)


def no_attempt() -> InvocationUsage:
    return InvocationUsage(
        attempt_id=None, attempts=0, started_at=None, completed_at=None, duration_seconds=0.0
    )


def _absence(reason: ForecastReason) -> GenerationPayload:
    state = (
        ForecastStatus.UNSUPPORTED
        if reason in (ForecastReason.SCOPE_UNSUPPORTED, ForecastReason.TARGET_SESSION_UNRESOLVED)
        else ForecastStatus.UNAVAILABLE
    )
    if reason in (
        ForecastReason.INTERNAL_EXECUTION_FAILURE,
        ForecastReason.LOCAL_DEADLINE_EXCEEDED,
    ):
        state = ForecastStatus.FAILED
    return GenerationPayload(status=state, output=ForecastAbsence(reasons=(reason,)))


def _checked_shelf(
    roots: tuple[ArtifactReference, ...], shelf: tuple[CapturedArtifact, ...], clock: Clock
) -> tuple[CapturedArtifact, ...]:
    selected = select_artifacts(roots, shelf)
    validate_closure(
        roots,
        tuple(a.blob_reference for a in selected),
        selected,
        as_of=read_clock(clock),
        retaining=True,
    )
    return selected


@dataclass(frozen=True, slots=True)
class ForecastRuntimeOwner:
    config: ColdForecastConfig
    artifact: BaseRateArtifact
    binding: ForecastBinding
    _root: Path = field(repr=False)
    _shelf: tuple[CapturedArtifact, ...] = field(repr=False)
    _forecaster: Forecaster = field(repr=False)
    _clock: Clock = field(repr=False)
    _new_id: Callable[[], str] = field(repr=False)
    _lock: RLock = field(default_factory=RLock, repr=False, compare=False)
    _used_ids: set[str] = field(default_factory=set, repr=False, compare=False)

    @property
    def configuration_fingerprint(self) -> str:
        return self.binding.configuration_ref.fingerprint

    @property
    def composition_fingerprint(self) -> str:
        return self.binding.composition_ref.fingerprint

    def _input_shelf(
        self,
        request: ForecastRequest,
        snapshot: ForecastEvidenceSnapshot,
        artifacts: tuple[CapturedArtifact, ...],
    ) -> tuple[CapturedArtifact, ...]:
        if (request.configuration_ref, request.profile_ref, request.simulation_profile_ref) != (
            self.binding.configuration_ref,
            self.binding.composition_ref,
            self.config.simulation_profile_ref,
        ) or request.realization_mode is not self.config.composition.nodes[0].realization_mode:
            raise ForecastIntegrityError("REQUEST_COLD_PROFILE_PIN_MISMATCH")
        if snapshot.window != request.window or snapshot.sources != request.evidence:
            raise ForecastIntegrityError("REQUEST_SNAPSHOT_MISMATCH")
        evidence = capture_artifact(request.evidence_ref.artifact_id, snapshot)
        if evidence.reference != request.evidence_ref:
            raise ForecastIntegrityError("REQUEST_EVIDENCE_PIN_MISMATCH")
        return _checked_shelf(
            references(
                {
                    "request": request.model_dump(mode="json"),
                    "binding": self.binding.model_dump(mode="json"),
                    "binding_ref": self.binding_reference.model_dump(mode="json"),
                }
            ),
            (*self._shelf, *artifacts, evidence),
            self._clock,
        )

    @property
    def binding_reference(self) -> ArtifactReference:
        return capture_artifact(
            "binding:" + semantic_fingerprint(self.binding), self.binding
        ).reference

    def _forecast(self, request: ForecastRequest) -> ForecastResult:
        """Trusted internal handoff; run() supplies validated captured inputs and persistence.

        No caller completion/issuance override. This is not broker execution or publication.
        """
        request = ForecastRequest.model_validate(request)
        if (
            request.configuration_ref != self.binding.configuration_ref
            or request.profile_ref != self.binding.composition_ref
        ):
            raise ForecastIntegrityError("REQUEST_COLD_PROFILE_PIN_MISMATCH")
        with self._lock:
            token = self._new_id()
            if token in self._used_ids:
                raise ForecastIntegrityError("DUPLICATE_EXECUTION_ID")
            self._used_ids.add(token)
            now = read_clock(self._clock)
            if now < request.as_of or now < self.binding.bound_at:
                raise ForecastAdmissionError(ForecastReason.TEMPORAL_INELIGIBLE)
            support: AdmittedSupport | None = None
            usage = no_attempt()
            actual = request.realization_mode is ForecastRealizationMode.ACTUAL_ISSUANCE
            try:
                if request.target != self.config.target:
                    raise ForecastAdmissionError(ForecastReason.SCOPE_UNSUPPORTED)
                validate_required_evidence(request.window)
                if actual and now >= request.window.target_open_time:
                    raise ForecastAdmissionError(ForecastReason.TEMPORAL_INELIGIBLE)
                if any(s.admitted_at > now for s in request.all_evidence):
                    raise ForecastAdmissionError(ForecastReason.KNOWLEDGE_CUTOFF_VIOLATION)
                support = admit_support(self.artifact, request)
                if actual and read_clock(self._clock) >= request.window.target_open_time:
                    raise ForecastAdmissionError(ForecastReason.TEMPORAL_INELIGIBLE)
                payload = None
            except ForecastAdmissionError as exc:
                payload = _absence(exc.reason)
            if payload is None:
                assert support is not None
                started = read_clock(self._clock)
                tick = self._clock.monotonic()
                try:
                    payload = GenerationPayload.model_validate(
                        self._forecaster.forecast(request, support)
                    )
                except Exception:
                    payload = _absence(ForecastReason.INTERNAL_EXECUTION_FAILURE)
                elapsed = self._clock.monotonic() - tick
                completed = read_clock(self._clock)
                usage = InvocationUsage(
                    attempt_id=f"ff-attempt:{token}",
                    attempts=1,
                    started_at=started,
                    completed_at=completed,
                    duration_seconds=elapsed,
                )
                if elapsed > self.config.local_deadline_seconds:
                    payload = _absence(ForecastReason.LOCAL_DEADLINE_EXCEEDED)
            issued = None
            if actual and payload.status is ForecastStatus.GENERATED:
                final = read_clock(self._clock)
                if final >= request.window.target_open_time:
                    payload = _absence(ForecastReason.TEMPORAL_INELIGIBLE)
                else:
                    issued = final
            return ForecastResult(
                result_id=f"ff-result:{token}",
                run_id=f"ff-run:{token}",
                request=request,
                composition=self.config.composition,
                artifact_identity=self.artifact.identity,
                binding_ref=self.binding_reference,
                binding_available_at=self.binding.bound_at,
                status=payload.status,
                output=payload.output,
                computed_at=usage.completed_at,
                issued_at=issued,
                usage_state="RECORDED",
                inference=ForecastExecution(
                    descriptor_ref=self.binding.descriptor_ref,
                    configuration_ref=self.binding.configuration_ref,
                    composition_ref=self.binding.composition_ref,
                    support=support.summary if support else None,
                    usage=usage,
                ),
                limitations=(
                    "limitation:synthetic-only",
                    "limitation:unpriced-local-cost",
                    "limitation:raw-research",
                ),
            )

    def run(
        self,
        request: ForecastRequest,
        snapshot: ForecastEvidenceSnapshot,
        artifacts: tuple[CapturedArtifact, ...],
    ) -> ForecastCapture:
        request = ForecastRequest.model_validate(request)
        snapshot = ForecastEvidenceSnapshot.model_validate(snapshot)
        shelf = self._input_shelf(request, snapshot, artifacts)
        result = self._forecast(request)  # Internal handoff/issuance precedes storage, not stdout.
        recorded = read_clock(self._clock)
        capture = ForecastCapture(
            result=result,
            snapshot=snapshot,
            build_ref=self.binding.build_ref,
            dependency_versions_ref=self.binding.dependency_versions_ref,
            closure=tuple(a.blob_reference for a in shelf),
            recorded_at=recorded,
        )
        store = ForecastCorpusStore(self._root, as_of=recorded, owner=StoreOwner.FORECAST)
        store.append_forecast(capture, shelf)
        _LOG.info(
            "forecast captured",
            extra={
                "forecast_run": result.run_id,
                "forecast_request": request.request_id,
                "forecast_capture": capture.capture_id,
                "forecast_mode": request.realization_mode.value,
                "forecast_status": result.status.value,
                "forecast_profile": self.configuration_fingerprint,
                "forecast_composition": self.composition_fingerprint,
                "forecast_forecaster": self.config.forecaster_id,
                "forecast_artifact": self.artifact.artifact_id,
                "forecast_target": request.target.target_id,
                "forecast_target_version": request.target.target_version,
                "forecast_subject": request.target.subject.symbol,
                "forecast_basis": request.data_basis,
                "forecast_result": result.result_id,
                "forecast_replay_fingerprint": result.replay_fingerprint,
                "forecast_reasons": tuple(r.value for r in result.output.reasons)
                if isinstance(result.output, ForecastAbsence)
                else (),
                "forecast_support_count": result.inference.support.qualified_count
                if result.inference is not None and result.inference.support is not None
                else None,
                "forecast_duration_seconds": result.inference.usage.duration_seconds
                if result.inference
                else None,
            },
        )
        return capture


def create_forecast_runtime(
    config: ColdForecastConfig,
    artifact: BaseRateArtifact,
    artifacts: tuple[CapturedArtifact, ...],
    *,
    root: Path,
    build: CapturedArtifact,
    _clock: Clock | None = None,
    _new_id: Callable[[], str] | None = None,
) -> ForecastRuntimeOwner:
    """Explicit trusted Python startup, not a Shell selector, file search or HOT setter."""
    config = ColdForecastConfig.model_validate(config)
    artifact = BaseRateArtifact.model_validate(artifact)
    clock = _clock if _clock is not None else SystemClock()
    bound = read_clock(clock)
    ForecastCorpusStore(root, as_of=bound, owner=StoreOwner.FORECAST)  # Pure root validation.
    primitive = resolve_forecaster(config.forecaster_id, config.implementation_version)
    declarations = implementation_artifacts()
    descriptor = declarations[-1]
    if (
        config.descriptor_ref != descriptor.reference
        or capture_artifact(descriptor.reference.artifact_id, primitive.descriptor()).reference
        != descriptor.reference
        or artifact.configuration_ref != declarations[1].reference
        or artifact.code_ref != declarations[0].reference
    ):
        raise ForecastIntegrityError("COLD_IMPLEMENTATION_PIN_MISMATCH")
    if (
        config.target != artifact.target
        or config.composition.nodes[0].artifact_ref != artifact.reference
    ):
        raise ForecastIntegrityError("COLD_ARTIFACT_OR_TARGET_MISMATCH")
    if artifact.prepared_at > bound:
        raise ForecastAdmissionError(ForecastReason.ARTIFACT_UNAVAILABLE)
    configuration = capture_artifact(config.profile_id, config)
    composition = capture_artifact(config.composition.composition_id, config.composition)
    dependencies = dependency_artifact()
    artifact_blob = capture_artifact(artifact.artifact_id, artifact)
    binding = ForecastBinding(
        configuration_ref=configuration.reference,
        composition_ref=composition.reference,
        descriptor_ref=descriptor.reference,
        artifact_identity=artifact.identity,
        build_ref=build.reference,
        dependency_versions_ref=dependencies.reference,
        bound_at=bound,
    )
    binding_blob = capture_artifact("binding:" + semantic_fingerprint(binding), binding)
    shelf = _checked_shelf(
        (binding_blob.reference,),
        (
            *artifacts,
            *declarations,
            build,
            dependencies,
            artifact_blob,
            configuration,
            composition,
            binding_blob,
        ),
        clock,
    )
    validate_support_bars(artifact, shelf)
    if config.simulation_profile_ref is not None:
        profile_blob = next(b for b in shelf if b.reference == config.simulation_profile_ref)
        SimulationProfile.model_validate(strict_json(profile_blob.content_json))
    return ForecastRuntimeOwner(
        config,
        artifact,
        binding,
        root,
        shelf,
        primitive,
        clock,
        _new_id if _new_id is not None else lambda: uuid4().hex,
    )
