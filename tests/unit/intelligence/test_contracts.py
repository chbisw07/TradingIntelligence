"""Value-level identity, seven-kind, maturity, provenance and JSON regression cases."""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from pydantic import ValidationError

from tiaf.agents.models import ReasoningModelIdentity
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.identity import ForecastContract, canonical_json
from tiaf.service.intelligence import (
    ActiveLLMConfiguration,
    BinaryValue,
    CategoricalValue,
    ClaimKind,
    ContributorReference,
    DurationMaturity,
    EvaluableClaim,
    EventMaturity,
    EventTimeValue,
    Explanation,
    IntelligenceResponse,
    IntervalValue,
    NumericValue,
    OrdinalValue,
    ProducerIdentity,
    ProducerType,
    RankingValue,
    Recommendation,
    ResolutionContract,
    ResponseProvenance,
    ServiceIdentity,
    TradingDayMaturity,
)

from .helpers import AT, change, claim, producer, ref, resolution, response


@pytest.mark.parametrize("kind", list(ProducerType))
def test_producer_kinds_do_not_require_ml_fields(kind: ProducerType) -> None:
    value = producer(llm=kind is ProducerType.LLM)
    value = change(value, producer_type=kind, model=None)
    assert ProducerIdentity.model_validate_json(value.model_dump_json()) == value
    assert hash(value) == hash(ProducerIdentity.model_validate(value.model_dump()))


@pytest.mark.parametrize("provider", ["OpenAI", "Anthropic", "Google", "synthetic-test-provider"])
@pytest.mark.parametrize("observed_version", [None, "observed-revision-1"])
def test_provider_neutral_primary_config(provider: str, observed_version: str | None) -> None:
    owner = change(
        producer(llm=True),
        llm=ReasoningModelIdentity(
            provider_id=provider,
            model_id="test-model",
            model_version=observed_version,
            configuration_id="test-config",
        ),
    )
    config = ActiveLLMConfiguration(
        scope_id="scope:test",
        configuration_id="config:test",
        primary=owner,
    )
    rebuilt = ActiveLLMConfiguration.model_validate_json(canonical_json(config))
    assert rebuilt == config and hash(rebuilt) == hash(config)
    assert owner.llm is not None and owner.llm.model_version == observed_version
    assert config.primary.configuration_version != config.primary.service.service_version


@pytest.mark.parametrize(
    "field", ["llm", "prompt_version", "tool_config_version", "orchestration_version"]
)
def test_llm_required_identity_fields(field: str) -> None:
    with pytest.raises(ValidationError):
        change(producer(llm=True), **{field: None})


@pytest.mark.parametrize("field", ["producer_id", "service", "configuration_version", "capability"])
def test_missing_identity_fields(field: str) -> None:
    data = producer().model_dump()
    del data[field]
    with pytest.raises(ValidationError):
        ProducerIdentity.model_validate(data)


@pytest.mark.parametrize(
    "bad", ["", " ", "bare-name", "https://example.test/model", "model:../secret"]
)
def test_invalid_logical_identity(bad: str) -> None:
    with pytest.raises(ValidationError):
        ServiceIdentity(service_id=bad, service_version="1.0")


@pytest.mark.parametrize("field", ["provider_id", "model_id", "configuration_id", "model_version"])
def test_blank_llm_identity(field: str) -> None:
    data = producer(llm=True).model_dump()
    data["llm"][field] = "   "
    with pytest.raises(ValidationError):
        ProducerIdentity.model_validate(data)


def test_incompatible_identity_and_primary() -> None:
    with pytest.raises(ValidationError):
        change(producer(), prompt_version="1")
    with pytest.raises(ValidationError):
        change(producer(llm=True), model=producer().model)
    with pytest.raises(ValidationError):
        change(producer(), model=None, artifact_identity=ref("artifact"))
    with pytest.raises(ValidationError):
        ActiveLLMConfiguration(
            scope_id="scope:test", configuration_id="config:test", primary=producer()
        )
    with pytest.raises(ValidationError):
        ActiveLLMConfiguration.model_validate(
            {
                "scope_id": "scope:test",
                "configuration_id": "config:test",
                "primary": [producer(llm=True).model_dump(), producer(llm=True).model_dump()],
            }
        )


@pytest.mark.parametrize(
    "value",
    [
        BinaryValue(probability=0.0),
        BinaryValue(assertion=False, calibration="NOT_APPLICABLE"),
        NumericValue(value=0.0, unit="return_fraction"),
        CategoricalValue(value="BULL", vocabulary=("BULL", "BEAR")),
        OrdinalValue(value="LOW", ordered_scale=("LOW", "HIGH")),
        RankingValue(
            universe=("subject:a", "subject:b"), ordered_subjects=("subject:b", "subject:a")
        ),
        IntervalValue(lower=0.0, upper=0.0, unit="return_fraction", nominal_coverage=0.9),
        EventTimeValue(at=AT + timedelta(hours=1)),
    ],
)
def test_seven_typed_claims_roundtrip(value: Any) -> None:
    result = change(claim(), value=value, resolution=resolution(value.kind))
    rebuilt = EvaluableClaim.model_validate_json(canonical_json(result))
    assert rebuilt == result and rebuilt.semantic_fingerprint() == result.semantic_fingerprint()
    assert hash(rebuilt) == hash(result)
    assert rebuilt.resolution.claim_kind == value.kind


@pytest.mark.parametrize(
    "value",
    [
        {"kind": "BINARY"},
        {"kind": "BINARY", "probability": 0.5, "assertion": True},
        {"kind": "BINARY", "probability": -0.01},
        {"kind": "BINARY", "probability": 1.01},
        {"kind": "BINARY", "probability": True},
        {"kind": "BINARY", "assertion": False},
        {"kind": "BINARY", "probability": 0.5, "calibration": "CALIBRATED"},
        {"kind": "NUMERIC", "probability": 0.5},
        {"kind": "NUMERIC", "value": float("nan"), "unit": "x"},
        {"kind": "NUMERIC", "value": float("inf"), "unit": "x"},
        {"kind": "NUMERIC", "value": True, "unit": "x"},
        {"kind": "NUMERIC", "value": 0.0, "unit": " "},
        {"kind": "CATEGORICAL", "value": "UNKNOWN", "vocabulary": ["UP", "DOWN"]},
        {"kind": "CATEGORICAL", "value": "UP", "vocabulary": ["UP", "UP"]},
        {"kind": "ORDINAL", "value": "MID", "ordered_scale": ["LOW", "HIGH"]},
        {"kind": "ORDINAL", "value": "LOW", "ordered_scale": ["LOW", "LOW"]},
        {"kind": "RANKING", "universe": ["s:a", "s:b"], "ordered_subjects": ["s:a", "s:a"]},
        {"kind": "RANKING", "universe": ["s:a", "s:b"], "ordered_subjects": ["s:a", "s:c"]},
        {"kind": "INTERVAL", "lower": 2.0, "upper": 1.0, "unit": "x", "nominal_coverage": 0.9},
        {"kind": "INTERVAL", "lower": 0.0, "upper": 1.0, "unit": "x", "nominal_coverage": 1.0},
        {"kind": "EVENT_TIME", "at": "2030-01-03T10:00:00"},
        {"kind": "UNKNOWN", "value": 1.0},
    ],
)
def test_invalid_values(value: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        change(claim(), value=value)


def test_mismatched_resolution_and_capability() -> None:
    with pytest.raises(ValidationError):
        change(claim(), resolution=resolution(ClaimKind.NUMERIC))
    owner = producer()
    with pytest.raises(ValidationError):
        change(claim(), producer=change(owner, capability=change(owner.capability, claim_kinds=())))


@pytest.mark.parametrize(
    "maturity",
    [
        {"kind": "ABSOLUTE", "at": (AT + timedelta(hours=1)).isoformat()},
        {"kind": "TRADING_DAYS", "sessions": 2, "calendar": ref("calendar").model_dump()},
        {"kind": "CALENDAR_DURATION", "seconds": 60},
        {"kind": "EVENT", "event_id": "event:release", "policy": ref("policy").model_dump()},
    ],
)
def test_four_maturity_modes(maturity: dict[str, Any]) -> None:
    result = change(resolution(), maturity=maturity)
    assert ResolutionContract.model_validate_json(result.model_dump_json()) == result


@pytest.mark.parametrize(
    "maturity",
    [
        {"kind": "ABSOLUTE", "at": AT.isoformat()},
        {"kind": "ABSOLUTE", "at": "2030-01-03T10:00:00"},
        {"kind": "TRADING_DAYS", "sessions": 0, "calendar": ref("calendar").model_dump()},
        {"kind": "TRADING_DAYS", "sessions": 1},
        {"kind": "TRADING_DAYS", "sessions": True, "calendar": ref("calendar").model_dump()},
        {"kind": "CALENDAR_DURATION", "seconds": -1},
        {"kind": "CALENDAR_DURATION", "seconds": 1.5},
        {"kind": "EVENT", "event_id": "event:release"},
        {
            "kind": "EVENT",
            "event_id": "event:release",
            "policy": ref("policy").model_dump(),
            "deadline": AT.isoformat(),
        },
        {"kind": "UNSPECIFIED"},
    ],
)
def test_invalid_maturity(maturity: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        change(resolution(), maturity=maturity)


@pytest.mark.parametrize(
    "field", ["target", "target_semantics", "resolver", "subject", "maturity", "mode"]
)
def test_resolution_required_fields(field: str) -> None:
    data = resolution().model_dump()
    del data[field]
    with pytest.raises(ValidationError):
        ResolutionContract.model_validate(data)


def test_exactly_one_primary_and_secondary_rules() -> None:
    first = response()
    with pytest.raises(ValidationError):
        change(first, primary_claim=None)
    with pytest.raises(ValidationError):
        change(first, primary_claim=[claim().model_dump(), claim().model_dump()])
    with pytest.raises(ValidationError):
        change(first, primary_claims=[claim().model_dump()])
    second = change(claim(), claim_id="claim:secondary")
    assert change(first, secondary_claims=[second]).secondary_claims == (second,)
    with pytest.raises(ValidationError):
        change(first, secondary_claims=[claim()])
    with pytest.raises(ValidationError):
        change(first, style="NON_EVALUABLE")
    with pytest.raises(ValidationError):
        change(first, style="NON_EVALUABLE", primary_claim=None, secondary_claims=[second])


def test_content_separation_and_presentation_independent_fingerprint() -> None:
    result = response()
    modified = change(
        result,
        explanation=Explanation(text="Explanation, not truth."),
        recommendations=[Recommendation(text="WAIT")],
    )
    assert modified.semantic_fingerprint() == result.semantic_fingerprint()
    assert canonical_json(modified) != canonical_json(result)
    assert modified.primary_claim == result.primary_claim
    non_evaluable = change(modified, style="NON_EVALUABLE", primary_claim=None)
    assert non_evaluable.primary_claim is None
    with pytest.raises(ValidationError):
        change(result, primary_claim=Explanation(text="Cannot become a claim."))
    with pytest.raises(ValidationError):
        Recommendation(text="BUY", authority="EXECUTE")  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["information_cutoff", "as_of", "created_at"])
def test_naive_timestamps_rejected(field: str) -> None:
    with pytest.raises(ValidationError):
        change(claim(), **{field: datetime(2030, 1, 2)})


def test_timestamp_normalization_and_clock_order() -> None:
    utc = AT.astimezone(UTC)
    result = change(claim(), created_at=utc, as_of=utc, information_cutoff=utc)
    assert result == claim() and result.created_at.tzinfo == TIAF_TIMEZONE
    assert "+05:30" in result.model_dump(mode="json")["created_at"]
    with pytest.raises(ValidationError):
        change(claim(), information_cutoff=AT + timedelta(seconds=1))
    with pytest.raises(ValidationError):
        change(claim(), created_at=AT - timedelta(seconds=1))
    with pytest.raises(ValidationError):
        change(claim(), resolution=change(resolution(), reference_at=AT + timedelta(seconds=1)))


@pytest.mark.parametrize(
    "value",
    [
        producer(),
        producer(llm=True),
        producer().service,
        claim(),
        resolution(),
        response(),
        ContributorReference(producer=producer(), output=ref("output")),
        ActiveLLMConfiguration(
            scope_id="scope:test", configuration_id="config:test", primary=producer(llm=True)
        ),
        DurationMaturity(seconds=10),
        TradingDayMaturity(sessions=1, calendar=ref("cal")),
        EventMaturity(event_id="event:test", policy=ref("policy")),
    ],
)
def test_value_objects_frozen(value: ForecastContract) -> None:
    with pytest.raises(ValidationError, match="frozen_instance"):
        value.schema_version = "9"  # type: ignore[assignment]
    rebuilt = type(value).model_validate_json(canonical_json(value))
    assert rebuilt == value and hash(rebuilt) == hash(value)


def test_semantic_collections_accept_lists_emit_arrays_and_do_not_mutate() -> None:
    data = response().model_dump(mode="json")
    data["evidence"] = [ref("evidence").model_dump(mode="json")]
    result = IntelligenceResponse.model_validate(data)
    assert isinstance(result.evidence, tuple)
    assert isinstance(result.model_dump(mode="json")["evidence"], list)
    assert isinstance(result.producer.capability.claim_kinds, tuple)
    data["evidence"].clear()
    assert len(result.evidence) == 1
    for name in ("append", "remove", "clear"):
        assert not hasattr(result.evidence, name)


def test_duplicate_and_conflicting_contributors() -> None:
    item = ContributorReference(producer=producer(), output=ref("output"))
    for other in (item, change(item, producer=change(item.producer, configuration_version="99"))):
        with pytest.raises(ValidationError):
            ResponseProvenance(contributors=(item, other))
    with pytest.raises(ValidationError):
        ContributorReference(
            producer=producer(), output=ref("out"), claim_ids=("claim:a", "claim:a")
        )


def test_provenance_mismatches() -> None:
    result = response(producer("llm", llm=True))
    with pytest.raises(ValidationError):
        change(result, provenance=ResponseProvenance(synthesizer=producer("other", llm=True)))
    contribution = ContributorReference(
        producer=producer(), output=ref("out"), claim_ids=("claim:other",)
    )
    with pytest.raises(ValidationError):
        change(result, provenance=ResponseProvenance(contributors=(contribution,)))
    with pytest.raises(ValidationError):
        change(result, secondary_claims=(claim(),))
    with pytest.raises(ValidationError):
        change(result, primary_claim=claim())


def test_versions_and_endpoints_cannot_be_confused() -> None:
    owner = producer(llm=True)
    assert owner.schema_version == "1.0"
    assert (
        len(
            {
                owner.service.service_version,
                owner.configuration_version,
                owner.capability.capability_version,
                owner.prompt_version,
                owner.tool_config_version,
                owner.orchestration_version,
            }
        )
        == 6
    )
    with pytest.raises(ValidationError):
        change(owner.service, endpoint="https://synthetic.test")
    with pytest.raises(ValidationError):
        change(response(), schema_version="2.0")


@pytest.mark.parametrize("instant", [AT + timedelta(days=1), AT + timedelta(days=2)])
def test_expired_actual_claim_is_not_prospective(instant: datetime) -> None:
    with pytest.raises(ValidationError, match="ACTUAL_CLAIM"):
        change(claim(), created_at=instant)
    historical = change(claim(), created_at=instant, realization="SIMULATED_ISSUANCE")
    assert historical.created_at == instant
    with pytest.raises(ValidationError, match="MATURITY_MUST_FOLLOW_AS_OF"):
        change(historical, as_of=instant)


def test_fingerprint_rejects_model_copy_validation_bypass() -> None:
    with pytest.raises(ValidationError):
        response().model_copy(update={"primary_claim": None}).semantic_fingerprint()
    with pytest.raises(ValidationError):
        claim().model_copy(update={"resolution": None}).semantic_fingerprint()


def test_contributor_cannot_claim_ownership_of_primary() -> None:
    owner = producer("synth", llm=True)
    with pytest.raises(ValidationError, match="MULTIPLE_PRODUCERS"):
        change(
            response(owner),
            provenance=ResponseProvenance(
                synthesizer=owner,
                contributors=(
                    ContributorReference(
                        producer=producer(),
                        output=ref("other"),
                        claim_ids=("claim:primary",),
                    ),
                ),
            ),
        )


@pytest.mark.parametrize("model_field", ["forecaster_id", "implementation_version"])
def test_invalid_ml_model_identity(model_field: str) -> None:
    data = producer().model_dump()
    data["model"][model_field] = " "
    with pytest.raises(ValidationError):
        ProducerIdentity.model_validate(data)
