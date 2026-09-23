"""In-memory local/remote parity, exact bindings and safe typed failures."""

from datetime import timedelta

import pytest
from pydantic import ValidationError

from tiaf.forecasting.identity import canonical_json
from tiaf.service.intelligence import (
    CapabilityKind,
    IntelligenceRequest,
    IntelligenceResponse,
    IntelligenceService,
    IntelligenceServiceError,
    LocalAdapter,
    RemoteAdapter,
    ServiceErrorCode,
    ServiceFailure,
    validate_request,
    validate_response,
)

from .helpers import AT, SyntheticLocal, SyntheticRemote, change, claim, producer, request, response


def test_local_remote_semantic_equivalence_and_no_llm() -> None:
    local: LocalAdapter = SyntheticLocal()
    remote: RemoteAdapter = SyntheticRemote()
    assert isinstance(local, IntelligenceService) and isinstance(local, LocalAdapter)
    assert isinstance(remote, IntelligenceService) and isinstance(remote, RemoteAdapter)
    left, right = local.analyze(request()), remote.analyze(request())
    assert left == right
    assert left.semantic_fingerprint() == right.semantic_fingerprint()
    assert left.provenance.synthesizer is None and left.producer.llm is None
    assert local.deployment() != remote.deployment()
    assert local.health() == remote.health()
    assert remote.describe() == local.describe()


@pytest.mark.parametrize("code", [ServiceErrorCode.TIMEOUT, ServiceErrorCode.UNAVAILABLE])
@pytest.mark.parametrize("adapter", [SyntheticLocal, SyntheticRemote])
def test_synthetic_failures(code: ServiceErrorCode, adapter: type[SyntheticLocal]) -> None:
    with pytest.raises(IntelligenceServiceError) as caught:
        adapter(failure=code).analyze(request())
    assert caught.value.code == code
    assert str(caught.value) == code.value


@pytest.mark.parametrize("code", list(ServiceErrorCode))
def test_failure_contract_roundtrip(code: ServiceErrorCode) -> None:
    failure = ServiceFailure(code=code, request_id="query:test", service=producer().service)
    assert ServiceFailure.model_validate_json(canonical_json(failure)) == failure


def test_unsupported_capability() -> None:
    service = SyntheticLocal()
    owner = change(
        producer(),
        capability=change(
            producer().capability, capability_id="cap:other", kind=CapabilityKind.ANALYSIS
        ),
    )
    with pytest.raises(IntelligenceServiceError) as caught:
        service.analyze(request(owner))
    assert caught.value.code is ServiceErrorCode.UNSUPPORTED_CAPABILITY


def test_service_version_mismatch() -> None:
    owner = change(producer(), service=change(producer().service, service_version="99"))
    with pytest.raises(IntelligenceServiceError) as caught:
        SyntheticLocal().analyze(request(owner))
    assert caught.value.code is ServiceErrorCode.VERSION_MISMATCH


def test_model_version_mismatch() -> None:
    key = producer().model
    assert key is not None
    owner = change(producer(), model=change(key, implementation_version="99"))
    with pytest.raises(IntelligenceServiceError) as caught:
        SyntheticLocal().analyze(request(owner))
    assert caught.value.code is ServiceErrorCode.PROVENANCE_MISMATCH


@pytest.mark.parametrize("payload", ["broken-json", "{}", '{"schema_version":"99"}'])
def test_invalid_wire_response(payload: str) -> None:
    with pytest.raises(IntelligenceServiceError) as caught:
        SyntheticRemote().decode_response(payload, request())
    assert caught.value.code is ServiceErrorCode.INVALID_RESPONSE


def test_defensive_revalidation_and_frozen_model_copy_bypass() -> None:
    descriptor = SyntheticLocal().describe()
    forged = response().model_copy(update={"primary_claim": None})
    with pytest.raises(IntelligenceServiceError) as caught:
        validate_response(request(), forged, descriptor)
    assert caught.value.code is ServiceErrorCode.INVALID_RESPONSE
    forged_request = request().model_copy(update={"resolution": None})
    with pytest.raises(IntelligenceServiceError) as caught:
        validate_request(forged_request, descriptor)
    assert caught.value.code is ServiceErrorCode.INVALID_REQUEST


@pytest.mark.parametrize("variant", ["request", "clock", "target", "cutoff", "realization"])
def test_response_request_bindings(variant: str) -> None:
    item = response()
    match variant:
        case "request":
            item = change(
                item,
                request_id="query:wrong",
                primary_claim=change(claim(), request_id="query:wrong"),
            )
        case "clock":
            item = change(
                item,
                created_at=AT - timedelta(seconds=1),
                primary_claim=change(
                    claim(),
                    created_at=AT - timedelta(seconds=1),
                    as_of=AT - timedelta(seconds=1),
                    information_cutoff=AT - timedelta(seconds=1),
                    resolution=change(claim().resolution, reference_at=AT - timedelta(seconds=1)),
                ),
            )
        case "target":
            item = change(
                item,
                primary_claim=change(
                    claim(),
                    resolution=change(
                        claim().resolution, target_semantics="Different event entirely"
                    ),
                ),
            )
        case "cutoff":
            item = change(
                item, primary_claim=change(claim(), information_cutoff=AT - timedelta(seconds=1))
            )
        case "realization":
            item = change(item, primary_claim=change(claim(), realization="SIMULATED_ISSUANCE"))
    with pytest.raises(IntelligenceServiceError) as caught:
        validate_response(request(), item, SyntheticLocal().describe())
    assert caught.value.code is ServiceErrorCode.INVALID_RESPONSE


def test_actual_fallback_identity_cannot_masquerade_and_history_survives() -> None:
    original = producer("primary", llm=True)
    fallback = producer("fallback", llm=True)
    captured = canonical_json(response(original))
    fallback_service = SyntheticRemote(fallback)
    actual = fallback_service.analyze(request(fallback))
    assert actual.producer == fallback
    with pytest.raises(IntelligenceServiceError) as caught:
        validate_response(request(original), actual, SyntheticLocal(original).describe())
    assert caught.value.code is ServiceErrorCode.VERSION_MISMATCH
    old = IntelligenceResponse.model_validate_json(captured)
    assert (
        old.producer == original
        and old.semantic_fingerprint() == response(original).semantic_fingerprint()
    )
    assert actual.semantic_fingerprint() != old.semantic_fingerprint()


def test_non_evaluable_analysis_request_and_response() -> None:
    admitted = change(request(), style="NON_EVALUABLE", resolution=None)
    result = change(response(), style="NON_EVALUABLE", primary_claim=None)
    assert validate_response(admitted, result, SyntheticLocal().describe()) == result
    with pytest.raises(ValidationError):
        change(admitted, resolution=claim().resolution)
    with pytest.raises(ValidationError):
        change(request(), style="EVALUABLE", resolution=None)
    assert IntelligenceRequest.model_validate_json(canonical_json(admitted)) == admitted


def test_descriptor_duplicate_and_contradictory_binding() -> None:
    descriptor = SyntheticLocal().describe()
    for updates in (
        {"producers": (producer(), producer())},
        {"capabilities": (producer().capability, producer().capability)},
        {"producers": (producer("different"),)},
    ):
        with pytest.raises(ValidationError):
            change(descriptor, **updates)
