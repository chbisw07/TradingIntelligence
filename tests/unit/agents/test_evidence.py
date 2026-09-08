"""A3.1 evidence availability, attribution, and missing-evidence tests."""

import pytest
from pydantic import ValidationError

from tiaf.agents import (
    AgentCapability,
    AgentEvidencePack,
    AgentEvidenceReference,
    CitationRole,
    ClaimKind,
    EvidenceCitation,
    EvidenceClaim,
    EvidenceImportance,
    MissingEvidenceRequest,
)
from tiaf.context import EvidenceStatus
from tiaf.contracts import DataQuality, EvidenceSource, EvidenceType, FreshnessState

from ._support import NOW, evidence_pack, evidence_reference


@pytest.mark.parametrize(
    "status",
    [
        EvidenceStatus.AVAILABLE,
        EvidenceStatus.PARTIAL,
        EvidenceStatus.STALE,
        EvidenceStatus.MISSING,
        EvidenceStatus.FAILED,
        EvidenceStatus.NOT_REQUESTED,
    ],
)
def test_evidence_availability_reuses_existing_context_vocabulary(
    status: EvidenceStatus,
) -> None:
    values: dict[str, object] = {
        "evidence_id": "evidence-1",
        "evidence_type": EvidenceType.TECHNICAL,
        "subject": "RELIANCE",
        "producer_id": "producer",
        "producer_version": "1.0",
        "source": EvidenceSource.DERIVED,
        "availability": status,
        "acquired_at": NOW,
    }
    if status in {EvidenceStatus.AVAILABLE, EvidenceStatus.PARTIAL, EvidenceStatus.STALE}:
        values.update(
            quality=DataQuality.PARTIAL,
            freshness=(
                FreshnessState.STALE
                if status is EvidenceStatus.STALE
                else FreshnessState.FRESH
            ),
            observed_at=NOW,
            checksum="checksum",
        )
    if status is EvidenceStatus.FAILED:
        values.update(failure_code="SOURCE_FAILURE", failure_detail="Unavailable")
    assert AgentEvidenceReference.model_validate(values).availability is status


def test_missing_evidence_cannot_claim_factual_quality() -> None:
    with pytest.raises(ValidationError, match="cannot claim"):
        AgentEvidenceReference(
            evidence_id="missing",
            evidence_type=EvidenceType.NEWS,
            subject="RELIANCE",
            producer_id="gateway",
            producer_version="1.0",
            source=EvidenceSource.THIRD_PARTY,
            availability=EvidenceStatus.MISSING,
            quality=DataQuality.GOOD,
            freshness=FreshnessState.FRESH,
            acquired_at=NOW,
        )


def test_stale_availability_cannot_be_silently_upgraded() -> None:
    payload = evidence_reference(availability=EvidenceStatus.STALE).model_dump(mode="python")
    payload["freshness"] = FreshnessState.FRESH
    with pytest.raises(ValidationError, match="requires STALE freshness"):
        AgentEvidenceReference.model_validate(payload)


def test_pack_cannot_silently_upgrade_weakest_quality_or_freshness() -> None:
    stale = evidence_reference(availability=EvidenceStatus.STALE)
    payload = evidence_pack().model_dump(mode="python")
    payload["references"] = (stale,)
    with pytest.raises(ValidationError, match="pack freshness"):
        AgentEvidencePack.model_validate(payload)


def test_claim_requires_structured_evidence_link() -> None:
    with pytest.raises(ValidationError, match="requires at least one citation"):
        EvidenceClaim(
            claim_id="claim",
            kind=ClaimKind.FACTUAL,
            statement="A factual statement.",
            evidence_type=EvidenceType.TECHNICAL,
            citations=(),
            as_of=NOW,
            provenance="A2",
            quality=DataQuality.GOOD,
            freshness=FreshnessState.FRESH,
        )


def test_claim_preserves_support_and_contradiction_links() -> None:
    claim = EvidenceClaim(
        claim_id="claim",
        kind=ClaimKind.INTERPRETIVE,
        statement="Evidence is conflicted.",
        evidence_type=EvidenceType.TECHNICAL,
        citations=(
            EvidenceCitation(evidence_id="support", role=CitationRole.SUPPORTS),
            EvidenceCitation(evidence_id="conflict", role=CitationRole.CONTRADICTS),
        ),
        as_of=NOW,
        provenance="A2",
        quality=DataQuality.PARTIAL,
        freshness=FreshnessState.FRESH,
    )
    assert tuple(item.role for item in claim.citations) == (
        CitationRole.SUPPORTS,
        CitationRole.CONTRADICTS,
    )


def test_missing_evidence_request_is_bounded_and_never_fetches() -> None:
    request = MissingEvidenceRequest(
        missing_request_id="missing-news",
        evidence_type=EvidenceType.NEWS,
        capability=AgentCapability.READ_NEWS,
        subject="RELIANCE",
        reason="A recent filing is material to the thesis.",
        importance=EvidenceImportance.MATERIAL,
        required_freshness=FreshnessState.FRESH,
        requested_at=NOW,
    )
    assert request.capability is AgentCapability.READ_NEWS
    assert not hasattr(request, "fetch")


def test_evidence_pack_preserves_a2_reference_identity_and_json_round_trip() -> None:
    pack = evidence_pack()
    payload = pack.model_dump(mode="json")
    assert pack.deterministic_assessment_id == "a2-assessment-1"
    assert isinstance(payload["references"], list)
    assert AgentEvidencePack.model_validate(payload) == pack


def test_evidence_pack_rejects_duplicate_reference_ids() -> None:
    payload = evidence_pack().model_dump(mode="python")
    payload["references"] = (evidence_reference(), evidence_reference())
    with pytest.raises(ValidationError, match="reference IDs must be unique"):
        AgentEvidencePack.model_validate(payload)
