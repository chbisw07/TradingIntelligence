"""FLC-5 synthetic application, existing custody codecs and offline replay.

No fit/evaluation/diagnostic/optimizer service is called or implemented here.
"""

from types import MappingProxyType
from typing import Literal

from tiaf.forecasting.contracts import ForecastEdge
from tiaf.forecasting.enums import ForecastRealizationMode, ForecastStatus
from tiaf.forecasting.identity import ArtifactReference

from .calibration_contracts import (
    SOURCE_KEY,
    VERSION,
    CalibrationApplyRequest,
    CalibrationApplyResult,
    CalibrationArtifact,
    CalibrationArtifactIdentity,
    CalibrationComponent,
    CalibrationComposition,
    CalibrationEvidence,
    CalibrationFitRequest,
    CalibrationFitResult,
    CalibrationSource,
    synthetic_pin,
)
from .forecaster_custody import ForecasterStore
from .forecaster_training import reference


class CalibrationStore(ForecasterStore):
    """Codec extension only; inherited bounded canonical I/O and custody."""

    record_types = MappingProxyType(
        {
            **ForecasterStore.record_types,
            "calcomponent": CalibrationComponent,
            "calevidence": CalibrationEvidence,
            "calfitrequest": CalibrationFitRequest,
            "calfitresult": CalibrationFitResult,
            "calidentity": CalibrationArtifactIdentity,
            "calartifact": CalibrationArtifact,
            "calsource": CalibrationSource,
            "calrequest": CalibrationApplyRequest,
            "calcomposition": CalibrationComposition,
            "calresult": CalibrationApplyResult,
        }
    )


def _validate_source(request: CalibrationApplyRequest, source: CalibrationSource) -> None:
    node = source.primitive_composition.nodes[0]
    if (
        request.source_reference != reference("calsource", source)
        or request.source_forecast_id != source.forecast_id
        or request.source_forecaster != source.compatible.forecaster.key
        or request.component.source_forecaster != request.source_forecaster
        or request.component.source_model != node.artifact_ref
        or request.component.source_preprocessor is not None
    ):
        raise ValueError("CALIBRATION_SOURCE_DEPENDENCY_MISMATCH")
    if request.target != source.target or request.component.target != source.target:
        raise ValueError("CALIBRATION_TARGET_INCOMPATIBLE")
    if request.mode != node.realization_mode or request.component.mode != request.mode:
        raise ValueError("CALIBRATION_REALIZATION_MODE_INCOMPATIBLE")
    if request.created_at < source.computed_at:
        raise ValueError("CALIBRATION_REQUEST_BEFORE_SOURCE")
    if request.policy != synthetic_pin("apply-policy"):
        raise ValueError("CALIBRATION_POLICY_UNSUPPORTED")


def _supported(request: CalibrationApplyRequest) -> bool:
    component = request.component
    return (
        component.implementation_version == VERSION
        and component.family == "calibrator:authored-monotonic-table"
        and component.calibrator_id == "calibrator:flc5-reference"
        and component.source_forecaster == SOURCE_KEY
        and component.mode is ForecastRealizationMode.SIMULATED_ISSUANCE
    )


def _validate_artifact(
    request: CalibrationApplyRequest, source: CalibrationSource, artifact: CalibrationArtifact
) -> None:
    if (
        reference("calartifact", artifact) != request.artifact_reference
        or artifact.identity.component != request.component
    ):
        raise ValueError("CALIBRATION_ARTIFACT_LINEAGE_MISMATCH")
    # The transformation must already be available at the source decision cutoff.
    # Replaying at a later wall clock does not renew or expire this historical check.
    if not artifact.available_at <= source.information_cutoff < artifact.valid_until:
        raise ValueError("CALIBRATION_ARTIFACT_NOT_VALID_AT_CUTOFF")


def _transform(probability: float, artifact: CalibrationArtifact) -> float:
    for (left, y0), (right, y1) in zip(artifact.knots, artifact.knots[1:]):
        if left <= probability <= right:
            if probability == left:
                return y0
            if probability == right:
                return y1
            return y0 + (probability - left) / (right - left) * (y1 - y0)
    raise ValueError("CALIBRATION_INPUT_OUTSIDE_UNIT_INTERVAL")


def _result(
    request: CalibrationApplyRequest,
    source: CalibrationSource,
    artifact: CalibrationArtifact | None,
    *,
    unavailable: bool = False,
) -> CalibrationApplyResult:
    _validate_source(request, source)
    lineage = (
        reference("calrequest", request),
        request.source_reference,
        request.artifact_reference,
    )
    if not _supported(request):
        return CalibrationApplyResult(
            request=request,
            source=source,
            raw_probability=source.compatible.output.probability,
            lineage=lineage,
            status=ForecastStatus.UNSUPPORTED,
            artifact_checked="NOT_CHECKED",
            reason="calibration:implementation-unsupported",
        )
    if unavailable:
        return CalibrationApplyResult(
            request=request,
            source=source,
            raw_probability=source.compatible.output.probability,
            lineage=lineage,
            status=ForecastStatus.UNAVAILABLE,
            artifact_checked="UNAVAILABLE",
            reason="calibration:artifact-unavailable",
        )
    if artifact is None:
        raise ValueError("CALIBRATION_ARTIFACT_REQUIRED")
    _validate_artifact(request, source, artifact)
    composition = CalibrationComposition(
        primitive=source.primitive_composition,
        primitive_identity=request.source_forecaster,
        component=request.component,
        calibration_artifact=request.artifact_reference,
        target=request.target,
        policy=request.policy,
        edge=ForecastEdge(
            source_node_id=source.primitive_composition.nodes[0].node_id,
            target_node_id=request.component.calibrator_id,
        ),
        root_node_id=request.component.calibrator_id,
    )
    try:
        transformed = _transform(source.compatible.output.probability, artifact)
    except (ArithmeticError, ValueError):
        return CalibrationApplyResult(
            request=request,
            source=source,
            raw_probability=source.compatible.output.probability,
            lineage=lineage,
            status=ForecastStatus.FAILED,
            artifact_checked="PRESENT_VERIFIED",
            reason="calibration:application-failed",
        )
    return CalibrationApplyResult(
        request=request,
        source=source,
        raw_probability=source.compatible.output.probability,
        status=ForecastStatus.GENERATED,
        calibrated_probability=transformed,
        composition=composition,
        artifact_checked="PRESENT_VERIFIED",
        lineage=(*lineage, reference("calcomposition", composition)),
    )


def persist_reference_artifact(
    store: CalibrationStore, artifact: CalibrationArtifact
) -> ArtifactReference:
    """Capture authored parameters and lineage, without a fit or use grant."""
    artifact = CalibrationArtifact.model_validate(artifact.model_dump())
    store.put("calcomponent", artifact.identity.component)
    store.put("calevidence", artifact.identity.evidence)
    store.put("calidentity", artifact.identity)
    store.put("calartifact", artifact)
    return reference("calartifact", artifact)


def _resolve_artifact(store: CalibrationStore, ref: ArtifactReference) -> CalibrationArtifact:
    artifact = store.resolve(ref)
    if not isinstance(artifact, CalibrationArtifact):
        raise ValueError("CALIBRATION_ARTIFACT_CODEC_MISMATCH")
    for kind, value in (
        ("calidentity", artifact.identity),
        ("calcomponent", artifact.identity.component),
        ("calevidence", artifact.identity.evidence),
    ):
        if store.resolve(reference(kind, value)) != value:
            raise ValueError("CALIBRATION_ARTIFACT_CLOSURE_MISMATCH")
    return artifact


def apply_calibration(
    store: CalibrationStore, request: CalibrationApplyRequest
) -> CalibrationApplyResult:
    """Apply only a captured synthetic reference. Missing never means identity."""
    if not store.writable:
        raise ValueError("CALIBRATION_STORE_READ_ONLY")
    request = CalibrationApplyRequest.model_validate(request.model_dump())
    source = store.resolve(request.source_reference)
    if not isinstance(source, CalibrationSource):
        raise ValueError("CALIBRATION_SYNTHETIC_SOURCE_REQUIRED")
    _validate_source(request, source)
    artifact = None
    unavailable = False
    if _supported(request):
        try:
            artifact = _resolve_artifact(store, request.artifact_reference)
        except (OSError, ValueError):
            unavailable = True
    result = _result(request, source, artifact, unavailable=unavailable)
    store.put("calrequest", request)
    if result.composition is not None:
        store.put("calcomposition", result.composition)
    store.put("calresult", result)
    return result


def replay_calibration(
    store: CalibrationStore, result_reference: ArtifactReference
) -> Literal["MATCH", "MISMATCH"]:
    """Recompute synthetic application from captured parameters; no writes or fit."""
    try:
        result = store.resolve(result_reference)
        if not isinstance(result, CalibrationApplyResult):
            raise ValueError("CALIBRATION_RESULT_REQUIRED")
        request = store.resolve(reference("calrequest", result.request))
        source = store.resolve(result.request.source_reference)
        if request != result.request or source != result.source:
            raise ValueError("CALIBRATION_REPLAY_SOURCE_MISMATCH")
        if (
            result.composition is not None
            and store.resolve(reference("calcomposition", result.composition)) != result.composition
        ):
            raise ValueError("CALIBRATION_REPLAY_COMPOSITION_MISMATCH")
        artifact = (
            _resolve_artifact(store, result.request.artifact_reference)
            if result.artifact_checked == "PRESENT_VERIFIED"
            else None
        )
        expected = _result(
            result.request,
            result.source,
            artifact,
            unavailable=result.artifact_checked == "UNAVAILABLE",
        )
        return "MATCH" if result == expected else "MISMATCH"
    except (OSError, ValueError):
        return "MISMATCH"
