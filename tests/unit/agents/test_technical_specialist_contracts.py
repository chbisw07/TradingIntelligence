"""A3.3 evidence, detail, citation, and degradation contracts."""

import json

import pytest
from pydantic import ValidationError

from tiaf.agents import (
    AgentEvidenceReference,
    AgentRunStatus,
    AgentStance,
    EvidenceFact,
)
from tiaf.agents.specialists.technical import (
    TECHNICAL_DETAIL_SCHEMA,
    TechnicalReasonCode,
    TechnicalSpecialist,
    technical_assessment_from_opinion,
)
from tiaf.contracts import DataQuality, FreshnessState

from ._technical_support import fact, technical_pack, technical_request


def test_evidence_fact_and_reference_collections_are_immutable_json_arrays() -> None:
    evidence_fact = fact("trend.linear_slope_percent", 0.2)
    reference = technical_pack().references[0]

    with pytest.raises(ValidationError):
        evidence_fact.metric_id = "changed"
    with pytest.raises(AttributeError):
        reference.facts.append(evidence_fact)  # type: ignore[attr-defined]

    dumped = reference.model_dump(mode="json")
    assert isinstance(dumped["facts"], list)
    assert AgentEvidenceReference.model_validate(dumped) == reference


def test_evidence_fact_rejects_noncanonical_metric_and_nonfinite_value() -> None:
    base = fact("trend.linear_slope_percent", 0.2).model_dump(mode="python")
    with pytest.raises(ValidationError, match="canonical dotted"):
        EvidenceFact.model_validate({**base, "metric_id": "Trend Slope"})
    with pytest.raises(ValidationError):
        EvidenceFact.model_validate({**base, "value": float("nan")})


def test_typed_detail_round_trips_inside_standard_opinion() -> None:
    opinion = TechnicalSpecialist().analyze(technical_request(), technical_pack())
    detail = technical_assessment_from_opinion(opinion)
    reconstructed = type(opinion).model_validate(opinion.model_dump(mode="json"))

    assert opinion.specialist_detail_schema_id == TECHNICAL_DETAIL_SCHEMA
    assert technical_assessment_from_opinion(reconstructed) == detail
    assert json.loads(opinion.specialist_detail_json or "null")["schema_version"] == "1.0"


def test_all_technical_claims_cite_exact_supplied_facts_and_matching_family() -> None:
    pack = technical_pack()
    opinion = TechnicalSpecialist().analyze(technical_request(), pack)
    supplied = {item.evidence_id: item for item in pack.references}

    assert opinion.evidence_claims
    for claim in opinion.evidence_claims:
        assert claim.citations
        for citation in claim.citations:
            reference = supplied[citation.evidence_id]
            assert reference.evidence_type is claim.evidence_type
            assert citation.locator
            locator_ids = set(citation.locator.split(", "))
            assert locator_ids <= {item.fact_id for item in reference.facts}


def test_contradiction_is_preserved_and_cites_both_directional_sides() -> None:
    opinion = TechnicalSpecialist().analyze(
        technical_request(),
        technical_pack(
            overrides={
                "indicator.rsi": 40.0,
                "indicator.macd": -0.4,
                "return.percent": -1.0,
            }
        ),
    )
    detail = technical_assessment_from_opinion(opinion)
    conflict_claim = next(
        claim for claim in opinion.evidence_claims if ":contradiction:" in claim.claim_id
    )

    assert opinion.stance is AgentStance.MIXED
    assert detail.contradictions
    assert {item.evidence_id for item in conflict_claim.citations} >= {
        "technical-core",
        "technical-momentum",
    }


def test_supplied_level_is_used_only_as_a_non_execution_invalidation() -> None:
    opinion = TechnicalSpecialist().analyze(technical_request(), technical_pack())
    detail = technical_assessment_from_opinion(opinion)

    assert detail.invalidations[0].supplied_level == 95.0
    assert detail.invalidations[0].fact_id == "fact:support.prior_low:1d"
    assert all(word not in opinion.summary for word in ("BUY", "SELL", "STOP"))


def test_missing_optional_evidence_degrades_but_does_not_fail_core_opinion() -> None:
    opinion = TechnicalSpecialist().analyze(
        technical_request(), technical_pack(core_only=True)
    )

    assert opinion.status is AgentRunStatus.PARTIAL
    assert opinion.stance is not AgentStance.INSUFFICIENT_EVIDENCE
    assert opinion.missing_evidence
    assert TechnicalReasonCode.OPTIONAL_EVIDENCE_MISSING.value in opinion.reason_codes


@pytest.mark.parametrize(
    ("quality", "freshness", "reason"),
    (
        (DataQuality.PARTIAL, FreshnessState.FRESH, "EVIDENCE_PARTIAL"),
        (DataQuality.GOOD, FreshnessState.STALE, "EVIDENCE_STALE"),
    ),
)
def test_partial_or_stale_optional_evidence_is_not_upgraded(
    quality: DataQuality,
    freshness: FreshnessState,
    reason: str,
) -> None:
    opinion = TechnicalSpecialist().analyze(
        technical_request(),
        technical_pack(optional_quality=quality, optional_freshness=freshness),
    )

    assert opinion.status is AgentRunStatus.PARTIAL
    assert reason in opinion.reason_codes
    assert any(
        claim.quality is quality or claim.freshness is freshness
        for claim in opinion.evidence_claims
    )
