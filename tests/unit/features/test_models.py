"""Immutable and serializable A2.1 feature contracts."""

from datetime import UTC, datetime
from typing import Any, cast

import pytest
from pydantic import ValidationError

from tiaf.contracts import DataQuality
from tiaf.features import (
    BUILTIN_FEATURE_DEFINITIONS,
    DeterministicFeatureEngine,
    FeatureDefinition,
    FeatureRequest,
    FeatureStatus,
    builtin_feature_registry,
)

from ._support import context_with_bars


def test_builtin_definitions_are_stable_unique_and_immutable() -> None:
    assert len(BUILTIN_FEATURE_DEFINITIONS) == 7
    assert len({item.feature_id for item in BUILTIN_FEATURE_DEFINITIONS}) == 7
    assert all(item.definition_version == "1.0" for item in BUILTIN_FEATURE_DEFINITIONS)
    assert all(
        item.parameters_schema_version == "1.0"
        for item in BUILTIN_FEATURE_DEFINITIONS
    )
    with pytest.raises(ValidationError):
        BUILTIN_FEATURE_DEFINITIONS[0].name = "changed"


def test_feature_request_accepts_mapping_and_json_collections_canonically() -> None:
    request = FeatureRequest(
        feature_id="return.percent",
        parameters=cast(Any, {"window": "close", "bars": 5}),
        interval="daily",
    )
    assert request.parameters == (("bars", 5), ("window", "close"))
    assert request.interval == "1d"
    dumped = request.model_dump(mode="json")
    assert dumped["parameters"] == [["bars", 5], ["window", "close"]]
    assert FeatureRequest.model_validate(dumped) == request
    with pytest.raises(ValidationError):
        request.required = False


@pytest.mark.parametrize(
    "parameters",
    [
        (("bars", 1), ("bars", 2)),
        (("Bad Name", 1),),
        (("bars", float("nan")),),
        (("bars", {"nested": True}),),
    ],
)
def test_feature_request_rejects_noncanonical_parameters(parameters: object) -> None:
    with pytest.raises(ValidationError):
        FeatureRequest(
            feature_id="return.percent", parameters=cast(Any, parameters)
        )


def test_feature_definition_rejects_duplicate_or_empty_sources() -> None:
    template = BUILTIN_FEATURE_DEFINITIONS[0].model_dump()
    with pytest.raises(ValidationError, match="must not be empty"):
        FeatureDefinition.model_validate({**template, "required_sources": ()})
    source = template["required_sources"][0]
    with pytest.raises(ValidationError, match="must be unique"):
        FeatureDefinition.model_validate(
            {**template, "required_sources": (source, source)}
        )


def test_feature_result_and_bundle_round_trip_with_json_arrays_and_ist_times() -> None:
    context = context_with_bars((100.0, 105.0))
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    result = engine.compute_one(context, FeatureRequest(feature_id="price.current"))
    bundle = engine.compute(
        context,
        (FeatureRequest(feature_id="price.current"),),
        bundle_id="bundle-test",
    )

    result_json = result.model_dump(mode="json")
    bundle_json = bundle.model_dump(mode="json")
    assert isinstance(result_json["source_evidence"], list)
    assert isinstance(result_json["warnings"], list)
    assert isinstance(bundle_json["results"], list)
    assert isinstance(bundle_json["missing_required_features"], list)
    assert result_json["as_of"].endswith("+05:30")
    assert bundle_json["created_at"].endswith("+05:30")
    assert type(result).model_validate(result_json) == result
    assert type(bundle).model_validate(bundle_json) == bundle
    with pytest.raises(ValidationError):
        result.status = FeatureStatus.FAILED
    with pytest.raises(ValidationError):
        bundle.complete = False


def test_feature_timestamps_accept_other_zones_and_reject_naive_values() -> None:
    context = context_with_bars()
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context, FeatureRequest(feature_id="price.current")
    )
    payload = result.model_dump()
    normalized = type(result).model_validate(
        {**payload, "as_of": datetime(2026, 9, 6, 5, tzinfo=UTC)}
    )
    assert normalized.as_of.isoformat() == "2026-09-06T10:30:00+05:30"
    with pytest.raises(ValidationError, match="timezone-aware"):
        type(result).model_validate(
            {**payload, "as_of": datetime(2026, 9, 6, 10, 30)}
        )


def test_feature_result_status_value_and_finite_value_invariants() -> None:
    context = context_with_bars()
    result = DeterministicFeatureEngine(builtin_feature_registry()).compute_one(
        context, FeatureRequest(feature_id="price.current")
    )
    payload = result.model_dump()
    with pytest.raises(ValidationError, match="cannot carry a value"):
        type(result).model_validate(
            {**payload, "status": FeatureStatus.FAILED, "value": 1.0}
        )
    with pytest.raises(ValidationError, match="requires a value"):
        type(result).model_validate(
            {**payload, "status": FeatureStatus.AVAILABLE, "value": None}
        )
    with pytest.raises(ValidationError, match="must be finite"):
        type(result).model_validate({**payload, "value": float("inf")})


def test_feature_metadata_rejects_credential_shaped_keys() -> None:
    template = BUILTIN_FEATURE_DEFINITIONS[0].model_dump()
    with pytest.raises(ValidationError, match="credentials"):
        FeatureDefinition.model_validate(
            {**template, "metadata": {"nested": {"api-key": "not-allowed"}}}
        )


def test_bundle_completeness_is_derived_from_required_result_statuses() -> None:
    context = context_with_bars((100.0,))
    bundle = DeterministicFeatureEngine(builtin_feature_registry()).compute(
        context,
        (
            FeatureRequest(
                feature_id="return.percent",
                parameters=(("bars", 1),),
                interval="1d",
            ),
        ),
    )
    assert not bundle.complete
    assert bundle.missing_required_features == ("return.percent",)
    assert bundle.overall_quality is DataQuality.UNAVAILABLE
    with pytest.raises(ValidationError, match="complete must agree"):
        type(bundle).model_validate({**bundle.model_dump(), "complete": True})
