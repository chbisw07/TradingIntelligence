from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from tiaf.agents import AgentCapability
from tiaf.market_intelligence import (
    CapabilitySupport,
    MarketIntelligenceCapability,
    MarketIntelligenceRequest,
    ProviderCapabilityDeclaration,
    ProviderIdentity,
    ProviderManifest,
    SemanticMappingQuality,
    SourceAuthority,
)
from tiaf.market_intelligence.normalization import tapetide_normalizer

from ._support import AS_OF, declaration, observation, request, result


def test_fine_capability_is_bounded_by_existing_coarse_authority() -> None:
    payload = request().model_dump()
    payload["authority"] = AgentCapability.READ_NEWS
    with pytest.raises(ValidationError, match="coarse authority"):
        MarketIntelligenceRequest.model_validate(payload)


def test_disallowed_coarse_authority_is_rejected() -> None:
    payload = request().model_dump()
    payload["allowed_authorities"] = (AgentCapability.READ_A2_EVIDENCE,)
    with pytest.raises(ValidationError, match="authority ceiling"):
        MarketIntelligenceRequest.model_validate(payload)


def test_request_attributes_reject_credentials() -> None:
    payload = request().model_dump()
    payload["attributes"] = {"api_key": "must-not-enter-replay"}
    with pytest.raises(ValidationError, match="secret-bearing"):
        MarketIntelligenceRequest.model_validate(payload)


def test_earnings_context_can_select_filings_or_news_authority_explicitly() -> None:
    original = request(MarketIntelligenceCapability.READ_EARNINGS_CALL_CONTEXT)
    payload = original.model_dump()
    payload["authority"] = AgentCapability.READ_NEWS
    payload["allowed_authorities"] = (
        AgentCapability.READ_A2_EVIDENCE,
        AgentCapability.READ_NEWS,
    )
    validated = MarketIntelligenceRequest.model_validate(payload)
    assert validated.authority is AgentCapability.READ_NEWS


def test_timestamp_is_aware_and_normalized_to_kolkata() -> None:
    payload = request().model_dump()
    payload["as_of"] = datetime(2026, 9, 9, 6, 30, tzinfo=UTC)
    restored = MarketIntelligenceRequest.model_validate(payload)
    assert restored.as_of == AS_OF
    assert restored.model_dump(mode="json")["as_of"].endswith("+05:30")
    payload["as_of"] = datetime(2026, 9, 9, 12)
    with pytest.raises(ValidationError, match="timezone-aware"):
        MarketIntelligenceRequest.model_validate(payload)


def test_contract_collections_are_immutable_and_json_arrays_round_trip() -> None:
    original = request(required=("fundamental.revenue",))
    dumped = original.model_dump(mode="json")
    assert isinstance(dumped["required_canonical_metrics"], list)
    assert MarketIntelligenceRequest.model_validate(dumped) == original
    with pytest.raises((AttributeError, TypeError)):
        original.required_canonical_metrics.append("fundamental.net_income")  # type: ignore[attr-defined]
    with pytest.raises(ValidationError):
        original.subject = "HDFCBANK"


def test_manifest_requires_read_only_and_explicit_unsupported_constraints() -> None:
    identity = ProviderIdentity(provider_id="p", display_name="P", adapter_version="1")
    unsupported = ProviderCapabilityDeclaration(
        capability=MarketIntelligenceCapability.READ_NEWS,
        support=CapabilitySupport.UNSUPPORTED,
    )
    manifest = ProviderManifest(
        identity=identity,
        source_authority=SourceAuthority.TRUSTED_SECONDARY,
        capabilities=(declaration(), unsupported),
    )
    assert manifest.declaration_for(MarketIntelligenceCapability.READ_NEWS) == unsupported
    with pytest.raises(ValidationError, match="read-only"):
        ProviderManifest(
            identity=identity,
            source_authority=SourceAuthority.TRUSTED_SECONDARY,
            capabilities=(declaration(),),
            read_only=False,
        )


@pytest.mark.parametrize("field", ["yearly_revenue", "Sales", "Borrowings"])
def test_unsafe_tapetide_financial_labels_remain_native_only(field: str) -> None:
    native = observation("tapetide", "native-1", field, 100)
    batch = tapetide_normalizer().normalize(request(), result("tapetide", native))
    assert batch.native_observations == (native,)
    assert batch.canonical_evidence == ()
    assert batch.normalization_records[0].mapping_quality in {
        SemanticMappingQuality.AMBIGUOUS,
        SemanticMappingQuality.PROVIDER_DEFINED,
    }


def test_provider_derived_fcf_is_not_promoted_to_reported_fact() -> None:
    native = observation("tapetide", "native-1", "Free Cash Flow", 25)
    batch = tapetide_normalizer().normalize(request(), result("tapetide", native))
    assert batch.canonical_evidence == ()
    assert batch.normalization_records[0].derivation_class.value == "PROVIDER_DERIVED"


def test_exact_mapping_requires_period_and_source_reference() -> None:
    native = observation(
        "tapetide",
        "native-1",
        "Revenue from Operations",
        100,
        source_reference=None,
        period=None,
    )
    batch = tapetide_normalizer().normalize(request(), result("tapetide", native))
    assert batch.canonical_evidence == ()
    assert {item.kind.value for item in batch.gaps} >= {
        "MISSING_SOURCE_REFERENCE",
        "MISSING_PERIOD",
    }


def test_exact_mapping_retains_native_and_emits_linked_canonical_evidence() -> None:
    native = observation("tapetide", "native-1", "Revenue from Operations", 100)
    batch = tapetide_normalizer().normalize(request(), result("tapetide", native))
    canonical = batch.canonical_evidence[0]
    assert canonical.source_observation_id == "native-1"
    assert canonical.metric == "fundamental.revenue"
