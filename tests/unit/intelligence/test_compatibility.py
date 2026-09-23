"""Synthetic composition and read-only FF mappings; no fit or empirical evidence."""

import ast
import subprocess
import sys
from pathlib import Path

from tiaf.forecasting.contracts import BinaryProbabilityOutput, ForecastRequest
from tiaf.forecasting.forecaster_adapters import resolve_inference_forecaster
from tiaf.forecasting.identity import ArtifactReference, canonical_json, semantic_fingerprint
from tiaf.forecasting.inference_contracts import run_inference
from tiaf.service.intelligence import (
    AbsoluteMaturity,
    ActiveLLMConfiguration,
    BinaryValue,
    CapabilityKind,
    CategoricalValue,
    ClaimKind,
    ContributorReference,
    EventMaturity,
    IntelligenceRequest,
    IntelligenceResponse,
    ProducerType,
    ResponseProvenance,
    validate_response,
)

from ..forecasting.test_forecaster_seams import base_request
from ..forecasting.test_neutral_inference import SyntheticAdapter
from .helpers import (
    SyntheticLocal,
    SyntheticRemote,
    change,
    claim,
    producer,
    ref,
    request,
    resolution,
    response,
)


class SyntheticClassifier(SyntheticLocal):
    def analyze(self, admitted: IntelligenceRequest) -> IntelligenceResponse:
        category = change(
            claim(self.owner),
            claim_id="claim:regime",
            value=CategoricalValue(value="BULL", vocabulary=("BULL", "BEAR")),
            resolution=resolution(ClaimKind.CATEGORICAL),
        )
        result = change(response(self.owner), primary_claim=category)
        return validate_response(admitted, result, self.describe())


def test_central_end_to_end_foundation() -> None:
    regime = producer("regime")
    regime = change(
        regime,
        producer_type=ProducerType.CLASSIFIER,
        capability=change(regime.capability, kind=CapabilityKind.CLASSIFICATION),
    )
    categorical = SyntheticClassifier(regime).analyze(
        change(request(regime), resolution=resolution(ClaimKind.CATEGORICAL))
    )
    forecast = SyntheticRemote().analyze(request())
    assert categorical.primary_claim is not None and forecast.primary_claim is not None
    forecast_claim = change(forecast.primary_claim, claim_id="claim:forecast")
    active = ActiveLLMConfiguration(
        scope_id="scope:app",
        configuration_id="config:primary",
        primary=producer("synthesis", llm=True),
    )
    result = change(
        response(active.primary),
        secondary_claims=(categorical.primary_claim, forecast_claim),
        evidence=(ref("supplied-evidence"),),
        provenance=ResponseProvenance(
            synthesizer=active.primary,
            contributors=(
                ContributorReference(
                    producer=regime, output=ref("regime-capture"), claim_ids=("claim:regime",)
                ),
                ContributorReference(
                    producer=forecast.producer,
                    output=ref("forecast-capture"),
                    claim_ids=("claim:forecast",),
                ),
            ),
        ),
    )
    assert (
        validate_response(
            request(active.primary), result, SyntheticLocal(active.primary).describe()
        )
        == result
    )
    restored = IntelligenceResponse.model_validate_json(canonical_json(result))
    assert restored == result and restored.semantic_fingerprint() == result.semantic_fingerprint()
    assert len(restored.provenance.contributors) == 2
    assert {c.value.kind for c in restored.secondary_claims} == {
        ClaimKind.BINARY,
        ClaimKind.CATEGORICAL,
    }
    assert restored.provenance.synthesizer == active.primary
    assert isinstance(restored.model_dump(mode="json")["secondary_claims"], list)


def test_existing_neutral_inference_maps_without_modification() -> None:
    adapter = SyntheticAdapter()
    native = run_inference(adapter.request(), adapter)
    before = canonical_json(native)
    assert isinstance(native.output, BinaryProbabilityOutput)
    owner = change(
        producer(),
        model=native.descriptor.identity.key,
        model_family=native.descriptor.identity.family,
        artifact_identity=native.artifacts.model,
    )
    target = ArtifactReference(
        artifact_id="synthetic:native-target",
        artifact_version="1.0",
        fingerprint=semantic_fingerprint(native.request.target_id),
    )
    resolved = change(
        resolution(),
        reference_at=native.request.as_of,
        target=target,
        target_semantics=native.request.target_id,
        reference_evidence=(native.request.input_ref,),
        # Neutral inference has no horizon field; an authored synthetic event policy is explicit.
        mode="EVENT",
        maturity=EventMaturity(
            event_id="event:synthetic-next-step", policy=native.artifacts.context
        ),
    )
    mapped = change(
        claim(owner),
        value=BinaryValue(probability=native.output.probability),
        information_cutoff=native.request.information_cutoff,
        as_of=native.request.as_of,
        created_at=native.request.computed_at,
        realization=native.request.mode,
        resolution=resolved,
    )
    captured = ArtifactReference(
        artifact_id="synthetic:native-result",
        artifact_version="1.0",
        fingerprint=semantic_fingerprint(native),
    )
    envelope = change(
        response(owner),
        primary_claim=mapped,
        created_at=native.request.computed_at,
        provenance=ResponseProvenance(native_output=captured),
    )
    restored = IntelligenceResponse.model_validate_json(canonical_json(envelope))
    assert restored == envelope and restored.provenance.synthesizer is None
    assert restored.primary_claim is not None
    assert restored.primary_claim.value.probability == native.output.probability  # type: ignore[union-attr]
    assert restored.primary_claim.realization == native.request.mode
    assert canonical_json(native) == before and native.output.calibration == "RAW"


def test_ff0_actual_target_window_and_raw_probability_preserved() -> None:
    context, admitted = base_request()
    assert isinstance(admitted.native, ForecastRequest)
    native_request = admitted.native
    adapter = resolve_inference_forecaster(admitted.key, context)
    native = adapter.forecast(admitted)  # Existing deterministic synthetic fixture, no fit.
    assert isinstance(native.output, BinaryProbabilityOutput)
    before = canonical_json(native)
    owner = change(
        producer(), model=admitted.key, model_family=adapter.descriptor().identity.family
    )
    target_ref = ArtifactReference(
        artifact_id="synthetic:ff-target",
        artifact_version="1.0",
        fingerprint=semantic_fingerprint(native_request.target),
    )
    window_ref = ArtifactReference(
        artifact_id="synthetic:ff-window",
        artifact_version="1.0",
        fingerprint=semantic_fingerprint(native_request.window),
    )
    pinned_resolution = change(
        resolution(),
        target=target_ref,
        target_semantics=native_request.target.event,
        resolver=native_request.target.labeler_ref,
        subject=f"instrument:{native_request.target.subject.symbol}",
        reference_at=native_request.window.reference.observed_at,
        reference_evidence=(window_ref, native_request.evidence_ref),
        maturity=AbsoluteMaturity(at=native_request.window.target_resolve_time),
    )
    projected = change(
        claim(owner),
        information_cutoff=admitted.information_cutoff,
        as_of=admitted.as_of,
        created_at=admitted.computed_at,
        realization=admitted.mode,
        resolution=pinned_resolution,
        value=BinaryValue(probability=native.output.probability),
    )
    result = change(
        response(owner),
        created_at=admitted.computed_at,
        primary_claim=projected,
        provenance=ResponseProvenance(
            native_output=ArtifactReference(
                artifact_id="synthetic:ff-result",
                artifact_version="1.0",
                fingerprint=semantic_fingerprint(native),
            )
        ),
    )
    assert IntelligenceResponse.model_validate_json(canonical_json(result)) == result
    assert projected.resolution.target.fingerprint == semantic_fingerprint(native_request.target)
    assert projected.resolution.maturity == AbsoluteMaturity(
        at=native_request.window.target_resolve_time
    )
    assert window_ref.fingerprint == semantic_fingerprint(native_request.window)
    assert canonical_json(native) == before


def test_future_raw_calibrated_mapping_keeps_distinct_provenance() -> None:
    raw = claim()
    calibrated_owner = change(raw.producer, configuration_version="calibrated-v1")
    calibrated = change(
        raw,
        claim_id="claim:calibrated",
        producer=calibrated_owner,
        value=BinaryValue(
            probability=0.1,
            calibration="CALIBRATED",
            calibration_reference=ref("synthetic-calibrator"),
        ),
    )
    assert raw.producer.model == calibrated.producer.model  # Same base model, not silently mutated.
    assert raw.semantic_fingerprint() != calibrated.semantic_fingerprint()
    assert isinstance(raw.value, BinaryValue) and raw.value.calibration_reference is None
    assert isinstance(calibrated.value, BinaryValue)
    assert calibrated.value.calibration_reference is not None
    assert raw.value.probability == 0.0
    # Hypothetical synthetic mapping only: no FF-2 execution or empirical authority.


def test_foundation_imports_no_optional_provider_sdk_or_network_runtime() -> None:
    code = """
import sys
from importlib.abc import MetaPathFinder
blocked = {"openai", "anthropic", "google", "httpx", "requests", "grpc", "mcp", "sklearn"}
class Guard(MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in blocked:
            raise AssertionError("Forbidden optional dependency: " + fullname)
sys.meta_path.insert(0, Guard())
import tiaf.service.intelligence
assert not blocked.intersection(sys.modules)
"""
    subprocess.run([sys.executable, "-c", code], check=True, capture_output=True, timeout=30)
    for source in Path("src/tiaf/service/intelligence").glob("*.py"):
        tree = ast.parse(source.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith(
                    ("openai", "anthropic", "google", "httpx")
                )
