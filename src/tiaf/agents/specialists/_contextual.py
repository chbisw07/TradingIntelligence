"""Narrow evidence-reading helpers shared by the three A3.6 specialists."""

from dataclasses import dataclass

from tiaf.agents.enums import AgentStance, BaselineAgreement, CitationRole, ClaimKind
from tiaf.agents.evidence import (
    AgentEvidencePack,
    AgentEvidenceReference,
    EvidenceCitation,
    EvidenceClaim,
    EvidenceFact,
)
from tiaf.baseline.enums import BaselineDirection
from tiaf.context import EvidenceStatus
from tiaf.contracts import DataQuality, FreshnessState


@dataclass(frozen=True)
class FactRecord:
    reference: AgentEvidenceReference
    fact: EvidenceFact


class ContextFactBook:
    """Read only supplied facts; it performs no provider access or A2 calculation."""

    def __init__(self, evidence: AgentEvidencePack) -> None:
        usable = {EvidenceStatus.AVAILABLE, EvidenceStatus.PARTIAL, EvidenceStatus.STALE}
        self.records = tuple(
            sorted(
                (
                    FactRecord(reference, fact)
                    for reference in evidence.references
                    if reference.availability in usable
                    for fact in reference.facts
                ),
                key=lambda item: (item.fact.metric_id, item.fact.interval or "", item.fact.fact_id),
            )
        )

    def exact(self, *metric_ids: str) -> tuple[FactRecord, ...]:
        return tuple(item for item in self.records if item.fact.metric_id in metric_ids)

    def prefix(self, prefix: str) -> tuple[FactRecord, ...]:
        return tuple(item for item in self.records if item.fact.metric_id.startswith(prefix))

    def first(self, metric_id: str) -> FactRecord | None:
        values = self.exact(metric_id)
        return values[0] if values else None

    def number(self, metric_id: str) -> float | None:
        item = self.first(metric_id)
        if item is None or isinstance(item.fact.value, (str, bool)):
            return None
        return float(item.fact.value)

    def text(self, metric_id: str) -> str | None:
        item = self.first(metric_id)
        return item.fact.value if item is not None and isinstance(item.fact.value, str) else None


def reference_ids(records: tuple[FactRecord, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item.reference.evidence_id for item in records))


def factual_claims(
    prefix: str, records: tuple[FactRecord, ...], *, contradictory_ids: tuple[str, ...] = ()
) -> tuple[EvidenceClaim, ...]:
    """Emit one exact scalar claim per used fact with its source citation."""

    claims: list[EvidenceClaim] = []
    contradictory = set(contradictory_ids)
    for index, item in enumerate(records):
        role = (
            CitationRole.CONTRADICTS
            if item.reference.evidence_id in contradictory
            else CitationRole.SUPPORTS
        )
        claims.append(
            EvidenceClaim(
                claim_id=f"{prefix}:claim:{index}:{item.fact.fact_id}",
                kind=ClaimKind.FACTUAL,
                statement=(
                    f"Supplied {item.fact.metric_id} is {item.fact.value}"
                    f"{' ' + item.fact.unit if item.fact.unit else ''}."
                ),
                evidence_type=item.reference.evidence_type,
                citations=(
                    EvidenceCitation(
                        evidence_id=item.reference.evidence_id, role=role, locator=item.fact.fact_id
                    ),
                ),
                as_of=item.fact.as_of,
                provenance=f"{item.reference.producer_id}/{item.reference.producer_version}",
                quality=item.fact.quality,
                freshness=item.fact.freshness,
            )
        )
    return tuple(claims)


def baseline_direction(book: ContextFactBook) -> BaselineDirection | None:
    value = book.text("baseline.direction")
    if value is None:
        return None
    try:
        return BaselineDirection(value)
    except ValueError:
        return None


def baseline_agreement(
    stance: AgentStance, direction: BaselineDirection | None
) -> BaselineAgreement:
    if direction is None or stance in {AgentStance.INSUFFICIENT_EVIDENCE, AgentStance.ABSTAIN}:
        return BaselineAgreement.NOT_COMPARABLE
    baseline_sign = {BaselineDirection.POSITIVE: 1, BaselineDirection.NEGATIVE: -1}.get(
        direction, 0
    )
    stance_sign = {AgentStance.POSITIVE: 1, AgentStance.NEGATIVE: -1}.get(stance, 0)
    if baseline_sign == stance_sign:
        return BaselineAgreement.AGREES
    if baseline_sign == 0 or stance_sign == 0 or stance is AgentStance.MIXED:
        return BaselineAgreement.PARTIALLY_AGREES
    return BaselineAgreement.DISAGREES


def confidence_value(
    evidence: AgentEvidencePack,
    agreement: float,
    *,
    mapping_factor: float = 1.0,
    relevance: float = 1.0,
) -> float:
    quality = {
        DataQuality.GOOD: 1.0,
        DataQuality.PARTIAL: 0.75,
        DataQuality.DEGRADED: 0.45,
        DataQuality.UNAVAILABLE: 0.0,
    }[evidence.overall_quality]
    freshness = {
        FreshnessState.FRESH: 1.0,
        FreshnessState.AGING: 0.75,
        FreshnessState.STALE: 0.4,
        FreshnessState.UNKNOWN: 0.3,
    }[evidence.overall_freshness]
    return round(
        max(
            0.0,
            min(
                1.0,
                evidence.evidence_coverage
                * quality
                * freshness
                * (0.5 + 0.5 * agreement)
                * mapping_factor
                * relevance,
            ),
        ),
        4,
    )
