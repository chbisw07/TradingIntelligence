"""Tests for evidence and snapshot contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from tiaf.contracts import (
    DataQuality,
    DataSnapshot,
    EvidenceItem,
    EvidenceSource,
    EvidenceType,
    FreshnessState,
)

NOW = datetime(2026, 9, 5, 4, 30, tzinfo=UTC)


def test_evidence_serializes_nested_metadata_safely() -> None:
    evidence = EvidenceItem(
        evidence_id="evidence-001",
        evidence_type=EvidenceType.NEWS,
        source=EvidenceSource.WEB,
        title="Exchange filing",
        summary="A timestamped public filing was observed.",
        observed_at=NOW,
        freshness=FreshnessState.FRESH,
        confidence=0.75,
        source_ref="provider-item-123",
        metadata={"tags": ["filing", "public"], "sequence": 3},
    )

    dumped = evidence.model_dump(mode="json")
    assert dumped["observed_at"] == "2026-09-05T10:00:00+05:30"
    assert dumped["metadata"] == {"tags": ["filing", "public"], "sequence": 3}


def test_evidence_rejects_confidence_above_one() -> None:
    with pytest.raises(ValidationError):
        EvidenceItem(
            evidence_id="evidence-001",
            evidence_type=EvidenceType.MARKET,
            source=EvidenceSource.DERIVED,
            title="Market context",
            summary="Context only.",
            observed_at=NOW,
            freshness=FreshnessState.FRESH,
            confidence=1.01,
        )


def test_evidence_rejects_non_json_metadata() -> None:
    with pytest.raises(ValidationError):
        EvidenceItem.model_validate(
            {
                "evidence_id": "evidence-001",
                "evidence_type": EvidenceType.OTHER,
                "source": EvidenceSource.INTERNAL,
                "title": "Invalid metadata",
                "summary": "Arbitrary runtime objects cannot enter transport metadata.",
                "observed_at": NOW,
                "freshness": FreshnessState.UNKNOWN,
                "metadata": {"runtime_object": object()},
            }
        )


def test_data_snapshot_normalizes_symbol() -> None:
    snapshot = DataSnapshot(
        snapshot_id="snapshot-001",
        symbol=" nifty ",
        observed_at=NOW,
        freshness=FreshnessState.AGING,
        quality=DataQuality.PARTIAL,
        providers=("provider-a",),
    )

    assert snapshot.symbol == "NIFTY"
    assert snapshot.providers == ("provider-a",)
