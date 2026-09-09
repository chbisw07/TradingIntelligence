"""Lossless A2.8 relative-result projection with explicit benchmark identity."""

import hashlib
import json

from tiaf.agents.evidence import AgentEvidenceReference, EvidenceFact
from tiaf.agents.specialists.technical.evidence import feature_fact
from tiaf.context import EvidenceStatus
from tiaf.contracts import DataQuality, EvidenceSource, EvidenceType, FreshnessState
from tiaf.contracts.common import Symbol
from tiaf.features.enums import FeatureStatus
from tiaf.features.models import FeatureResult
from tiaf.features.relative import BenchmarkReference


def relative_feature_facts(
    results: tuple[FeatureResult, ...], *, freshness: FreshnessState
) -> tuple[EvidenceFact, ...]:
    """Copy usable scalar A2.8 values; never recalculate returns or alignment."""
    return tuple(
        feature_fact(item, freshness=freshness)
        for item in results
        if item.request.feature_id.startswith("relative.")
        and item.status in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
        and item.value is not None
        and not isinstance(item.value, tuple)
    )


def relative_evidence_reference(
    *,
    evidence_id: str,
    subject: Symbol,
    benchmark: BenchmarkReference,
    results: tuple[FeatureResult, ...],
    freshness: FreshnessState,
    producer_id: str = "tiaf.a2.relative-strength",
    producer_version: str = "1.0",
) -> AgentEvidenceReference:
    """Build a cited reference whose benchmark choice remains caller-explicit."""
    facts = relative_feature_facts(results, freshness=freshness)
    if not facts:
        raise ValueError("relative evidence requires usable A2.8 results")
    qualities = {
        DataQuality.GOOD: 0,
        DataQuality.PARTIAL: 1,
        DataQuality.DEGRADED: 2,
        DataQuality.UNAVAILABLE: 3,
    }
    quality = max((item.quality for item in facts), key=qualities.__getitem__)
    observed_at = max(item.as_of for item in facts)
    payload = {
        "subject": subject,
        "benchmark": benchmark.model_dump(mode="json"),
        "facts": [item.model_dump(mode="json") for item in facts],
    }
    checksum = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return AgentEvidenceReference(
        evidence_id=evidence_id,
        evidence_type=EvidenceType.RELATIVE_STRENGTH,
        subject=subject,
        producer_id=producer_id,
        producer_version=producer_version,
        source=EvidenceSource.DERIVED,
        availability=EvidenceStatus.STALE
        if freshness is FreshnessState.STALE
        else EvidenceStatus.AVAILABLE,
        quality=quality,
        freshness=freshness,
        observed_at=observed_at,
        acquired_at=observed_at,
        checksum=checksum,
        source_reference="A2.8 explicit benchmark relative feature bundle",
        facts=facts,
        metadata={
            "benchmark_symbol": benchmark.symbol,
            "benchmark_role": benchmark.role.value,
            "benchmark_exchange": benchmark.exchange,
        },
    )
