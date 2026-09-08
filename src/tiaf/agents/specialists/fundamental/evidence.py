"""Read-only accessors for normalized fundamental facts in Agent evidence."""

from dataclasses import dataclass

from tiaf.agents import AgentEvidencePack, AgentEvidenceReference, EvidenceFact
from tiaf.context import EvidenceStatus
from tiaf.fundamentals import FundamentalMetric, FundamentalSourceQuality
from tiaf.fundamentals.quality import SOURCE_QUALITY_ORDER


@dataclass(frozen=True)
class FundamentalFactRecord:
    """One fact plus its containing evidence reference."""

    reference: AgentEvidenceReference
    fact: EvidenceFact
    period_end: str
    source_quality: FundamentalSourceQuality


class FundamentalFactBook:
    """Deterministic selectors that never calculate new financial metrics."""

    def __init__(self, evidence: AgentEvidencePack) -> None:
        usable = {
            EvidenceStatus.AVAILABLE,
            EvidenceStatus.PARTIAL,
            EvidenceStatus.STALE,
        }
        records: list[FundamentalFactRecord] = []
        for reference in evidence.references:
            if reference.availability not in usable:
                continue
            for fact in reference.facts:
                if not fact.metric_id.startswith("fundamental."):
                    continue
                parameters = {item.name: item.value for item in fact.parameters}
                period_end = str(parameters.get("period_end", ""))
                source_quality = FundamentalSourceQuality(
                    str(parameters.get("source_quality", "UNKNOWN"))
                )
                records.append(
                    FundamentalFactRecord(reference, fact, period_end, source_quality)
                )
        self._records = tuple(records)

    def records(self, *metrics: FundamentalMetric) -> tuple[FundamentalFactRecord, ...]:
        names = {item.value for item in metrics}
        return tuple(item for item in self._records if item.fact.metric_id in names)

    def latest(self, metric: FundamentalMetric) -> tuple[FundamentalFactRecord, ...]:
        records = self.records(metric)
        if not records:
            return ()
        latest_period = max(item.period_end for item in records)
        latest = tuple(item for item in records if item.period_end == latest_period)
        best = min(SOURCE_QUALITY_ORDER[item.source_quality] for item in latest)
        return tuple(
            item for item in latest if SOURCE_QUALITY_ORDER[item.source_quality] == best
        )

    def number(self, metric: FundamentalMetric) -> float | None:
        records = self.latest(metric)
        values = {
            float(item.fact.value)
            for item in records
            if not isinstance(item.fact.value, (str, bool))
        }
        return next(iter(values)) if len(values) == 1 else None

    def has_conflict(self, metric: FundamentalMetric) -> bool:
        records = self.latest(metric)
        return len(
            {
                float(item.fact.value)
                for item in records
                if not isinstance(item.fact.value, (str, bool))
            }
        ) > 1

