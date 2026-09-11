"""A4 contracts preserve typed references, immutability and semantic boundaries."""

from datetime import UTC
from pathlib import Path

import pytest
from pydantic import ValidationError

from tiaf.a4 import (
    A4Disposition,
    A4OutputIntegrityError,
    ArgumentPremise,
    PremisePolarity,
    PremiseRole,
    ScopeRelevance,
    SupportState,
    ThesisConstructionError,
    evaluate_projection,
    result_semantic_payload,
    validate_premise,
    validate_premises,
    validate_result,
)
from tiaf.planner.digests import digest
from tiaf.source_semantics import EpistemicRole

from ._support import clean_projection, with_gap


def test_contracts_are_frozen_tuple_backed_and_json_arrays_round_trip() -> None:
    projection = clean_projection()
    result = evaluate_projection(
        projection, evaluated_at=projection.header.evidence_as_of
    ).result
    dumped = result.model_dump(mode="json")
    assert isinstance(dumped["premises"], list)
    assert isinstance(result.premises, tuple)
    assert type(result).model_validate(dumped) == result
    with pytest.raises(ValidationError):
        result.disposition = A4Disposition.AVOID
    with pytest.raises(AttributeError):
        result.premises.append(result.premises[0])  # type: ignore[attr-defined]


def test_a4_timestamps_reject_naive_and_normalize_utc_to_kolkata() -> None:
    projection = with_gap(required=True)
    need = evaluate_projection(
        projection, evaluated_at=projection.header.evidence_as_of
    ).result.evidence_needs[0]
    normalized = type(need).model_validate(
        need.model_dump(mode="json")
        | {"evidence_cutoff": need.evidence_cutoff.astimezone(UTC)}
    )
    assert str(normalized.evidence_cutoff.tzinfo) == "Asia/Kolkata"
    assert normalized.model_dump(mode="json")["evidence_cutoff"].endswith("+05:30")
    with pytest.raises(ValidationError, match="timezone-aware"):
        type(need).model_validate(
            need.model_dump(mode="json")
            | {"evidence_cutoff": need.evidence_cutoff.replace(tzinfo=None)}
        )


def test_projection_only_a2_cannot_support_uncaptured_fact_premise() -> None:
    projection = clean_projection()
    assert not projection.opportunity.full_a2_evidence_available
    premise = ArgumentPremise(
        premise_id="a4-premise:uncaptured-a2-detail",
        role=PremiseRole.FACT,
        polarity=PremisePolarity.SUPPORTS,
        claim_refs=("assertion:uncaptured-a2-detail",),
        evidence_refs=(projection.occurrences[0].evidence_id,),
        reason_refs=(projection.parents.a2_assessment_id,),
        proposition_refs=(projection.assertions[0].proposition.proposition_id,),
        support_state=SupportState.TRUE,
        reason_code="UNSUPPORTED_FULL_A2_DETAIL",
        scope_relevance=ScopeRelevance.APPLICABLE,
        horizon_relevant=True,
    )
    with pytest.raises(ThesisConstructionError, match="not admitted"):
        validate_premise(premise, projection)


def test_hypothesis_cannot_be_promoted_to_fact() -> None:
    projection = clean_projection()
    original = projection.assertions[0]
    promoted_projection = projection.model_copy(
        update={
            "assertions": (
                original.model_copy(update={"epistemic_role": EpistemicRole.HYPOTHESIS}),
            )
        }
    )
    premise = evaluate_projection(
        projection, evaluated_at=projection.header.evidence_as_of
    ).result.premises[-1]
    with pytest.raises(ThesisConstructionError, match="promoted"):
        validate_premise(premise, promoted_projection)


def test_premise_dependency_cycles_are_rejected() -> None:
    projection = clean_projection()
    premises = evaluate_projection(
        projection, evaluated_at=projection.header.evidence_as_of
    ).result.premises
    first = premises[0].model_copy(update={"dependency_refs": (premises[1].premise_id,)})
    second = premises[1].model_copy(update={"dependency_refs": (premises[0].premise_id,)})
    with pytest.raises(ThesisConstructionError, match="cycle"):
        validate_premises((first, second, *premises[2:]), projection)


def test_a2_a3_projection_is_byte_identical_before_and_after_a4() -> None:
    projection = clean_projection()
    before = projection.model_dump_json()
    record = evaluate_projection(
        projection, evaluated_at=projection.header.evidence_as_of
    )
    assert projection.model_dump_json() == before
    assert record.result.original_a2_assessment_ref == projection.parents.a2_assessment_id
    assert (
        record.result.original_a3_semantic_fingerprint
        == projection.parents.a3_package_semantic_fingerprint
    )


def test_public_contracts_have_no_confidence_probability_or_trade_expression_fields() -> None:
    forbidden_fields = {
        "confidence",
        "probability",
        "action",
        "option_type",
        "strike",
        "expiry",
        "quantity",
        "stop_loss",
        "target_price",
    }
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path("src/tiaf/a4").glob("*.py")
    ).casefold()
    for field in forbidden_fields:
        assert f"{field}:" not in source


def test_refingerprinted_forged_thesis_parent_still_fails_structural_validation() -> None:
    projection = clean_projection()
    record = evaluate_projection(projection, evaluated_at=projection.header.evidence_as_of)
    forged_primary = record.result.primary_thesis.model_copy(
        update={"parent_a2_assessment_ref": "a2-assessment:forged"}
    )
    provisional = record.result.model_copy(update={"primary_thesis": forged_primary})
    fingerprint = digest(result_semantic_payload(provisional))
    forged = provisional.model_copy(
        update={
            "result_id": f"a4-result:{fingerprint[:24]}",
            "semantic_fingerprint": fingerprint,
        }
    )
    with pytest.raises(A4OutputIntegrityError, match="thesis input"):
        validate_result(forged, projection, record.policy)


def test_refingerprinted_unadmitted_challenge_citation_fails_validation() -> None:
    projection = with_gap(required=True)
    record = evaluate_projection(projection, evaluated_at=projection.header.evidence_as_of)
    forged_finding = record.result.challenge_findings[0].model_copy(
        update={"cited_opposition_refs": ("evidence:invented",)}
    )
    provisional = record.result.model_copy(
        update={"challenge_findings": (forged_finding,)}
    )
    fingerprint = digest(result_semantic_payload(provisional))
    forged = provisional.model_copy(
        update={
            "result_id": f"a4-result:{fingerprint[:24]}",
            "semantic_fingerprint": fingerprint,
        }
    )
    with pytest.raises(A4OutputIntegrityError, match="challenge reference"):
        validate_result(forged, projection, record.policy)
