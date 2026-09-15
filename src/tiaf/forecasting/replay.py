"""Recorded reconstruction stays execution-free; pinned verification is explicitly separate."""

from typing import TYPE_CHECKING

from .capture import ForecastCapture
from .store import ForecastCorpusStore

if TYPE_CHECKING:
    from .clocks import Clock
    from .execution import PinnedVerification


def verify_replay(store: ForecastCorpusStore, run_id: str) -> ForecastCapture:
    """Load and validate exact captured closure, retaining all original IDs and clocks."""
    return store.get_forecast(run_id)


def verify_pinned(
    store: ForecastCorpusStore, run_id: str, *, _clock: "Clock | None" = None
) -> "PinnedVerification":
    """Exact local generation-payload check, with new usage outside original history."""
    # Optional execution imports belong only to this operation, not recorded replay.
    from uuid import uuid4

    from .capture import capture_artifact, strict_json
    from .clocks import SystemClock, read_clock
    from .contracts import ForecastAbsence
    from .enums import ForecastReason, ForecastStatus
    from .errors import ForecastIntegrityError
    from .execution import InvocationUsage, PinnedVerification
    from .forecasters import (
        GenerationPayload,
        dependency_artifact,
        implementation_artifacts,
        resolve_forecaster,
    )
    from .identity import semantic_fingerprint
    from .runtime_contracts import ColdForecastConfig, ForecastBinding
    from .support import BaseRateArtifact, admit_support, validate_support_bars

    original = verify_replay(store, run_id)
    result = original.result
    clock = _clock if _clock is not None else SystemClock()
    if read_clock(clock) < original.recorded_at:
        raise ForecastIntegrityError("VERIFICATION_CLOCK_PREDATES_CAPTURE")
    usage = InvocationUsage(
        attempt_id=None, attempts=0, started_at=None, completed_at=None, duration_seconds=0.0
    )

    def report(status: str, reason: str, reconstructed: str | None = None) -> PinnedVerification:
        return PinnedVerification.model_validate(
            {
                "capture_ref": original.reference,
                "status": status,
                "reason": reason,
                "verified_at": read_clock(clock),
                "usage": usage,
                "original_result_fingerprint": result.replay_fingerprint,
                "reconstructed_result_fingerprint": reconstructed,
            }
        )

    if result.inference is None or result.artifact_identity is None or result.binding_ref is None:
        return report("UNVERIFIABLE", "verifier:legacy-contract-specimen")
    blobs = store.get_forecast_artifacts(run_id)
    by_ref = {b.reference: b for b in blobs}
    identity = result.artifact_identity
    try:
        primitive = resolve_forecaster(identity.forecaster_id, identity.implementation_version)
    except ForecastIntegrityError:
        return report("UNVERIFIABLE", "verifier:exact-implementation-missing")
    declarations = implementation_artifacts()
    if (
        result.inference.descriptor_ref != declarations[-1].reference
        or identity.code_ref != declarations[0].reference
        or capture_artifact(
            declarations[-1].reference.artifact_id, primitive.descriptor()
        ).reference
        != result.inference.descriptor_ref
    ):
        return report("UNVERIFIABLE", "verifier:implementation-pins-unavailable")
    if original.dependency_versions_ref != dependency_artifact().reference:
        return report("UNVERIFIABLE", "verifier:dependency-profile-unavailable")
    artifact = BaseRateArtifact.model_validate(strict_json(by_ref[identity.artifact].content_json))
    config = ColdForecastConfig.model_validate(
        strict_json(by_ref[result.request.configuration_ref].content_json)
    )
    binding = ForecastBinding.model_validate(strict_json(by_ref[result.binding_ref].content_json))
    if (
        artifact.identity != identity
        or config.composition != result.composition
        or config.target != result.request.target
        or config.forecaster_id != identity.forecaster_id
        or config.implementation_version != identity.implementation_version
        or artifact.configuration_ref != declarations[1].reference
        or binding.configuration_ref != result.request.configuration_ref
        or binding.composition_ref != result.request.profile_ref
        or binding.descriptor_ref != config.descriptor_ref
        or binding.descriptor_ref != result.inference.descriptor_ref
        or binding.artifact_identity != identity
        or binding.bound_at != result.binding_available_at
        or binding.build_ref != original.build_ref
        or binding.dependency_versions_ref != original.dependency_versions_ref
        or config.simulation_profile_ref != result.request.simulation_profile_ref
        or capture_artifact(config.composition.composition_id, config.composition).reference
        != result.request.profile_ref
    ):
        return report("MISMATCH", "verifier:captured-profile-mismatch")
    deterministic_absence = (
        result.status is ForecastStatus.UNAVAILABLE
        and isinstance(result.output, ForecastAbsence)
        and result.output.reasons == (ForecastReason.HISTORY_SUPPORT_INSUFFICIENT,)
    )
    if result.status is not ForecastStatus.GENERATED and not deterministic_absence:
        return report("UNVERIFIABLE", "verifier:non-generation-attempt-record")
    validate_support_bars(artifact, blobs)
    support = admit_support(artifact, result.request)
    started, tick = read_clock(clock), clock.monotonic()
    try:
        payload = GenerationPayload.model_validate(primitive.forecast(result.request, support))
    except Exception:
        usage = InvocationUsage(
            attempt_id="ff-verification:" + uuid4().hex,
            attempts=1,
            started_at=started,
            completed_at=read_clock(clock),
            duration_seconds=clock.monotonic() - tick,
        )
        return report("UNVERIFIABLE", "verifier:invocation-failed")
    elapsed, completed = clock.monotonic() - tick, read_clock(clock)
    usage = InvocationUsage(
        attempt_id="ff-verification:" + uuid4().hex,
        attempts=1,
        started_at=started,
        completed_at=completed,
        duration_seconds=elapsed,
    )
    if elapsed > config.local_deadline_seconds:
        return report("UNVERIFIABLE", "verifier:local-deadline-exceeded")
    data = result.model_dump(mode="json", exclude={"replay_fingerprint"})
    data["status"], data["output"] = payload.status.value, payload.output.model_dump(mode="json")
    data["inference"]["support"] = support.summary.model_dump(mode="json")
    reconstructed = semantic_fingerprint(data)
    exact = reconstructed == result.replay_fingerprint
    return report(
        "VERIFIED" if exact else "MISMATCH",
        "verifier:exact-match" if exact else "verifier:generation-payload-mismatch",
        reconstructed,
    )
