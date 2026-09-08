"""Point-in-time, revision, unit, and source normalization for fundamentals."""

import math
from collections import defaultdict
from datetime import datetime

from .enums import FundamentalUnit, ValueScale
from .models import FundamentalFact
from .quality import SOURCE_QUALITY_ORDER

_SCALE_FACTORS = {
    ValueScale.ONES: 1.0,
    ValueScale.THOUSANDS: 1_000.0,
    ValueScale.MILLIONS: 1_000_000.0,
    ValueScale.BILLIONS: 1_000_000_000.0,
    ValueScale.LAKHS: 100_000.0,
    ValueScale.CRORES: 10_000_000.0,
}


class FundamentalNormalizationError(ValueError):
    """A deterministic normalization or conflict error."""


def normalize_scale(fact: FundamentalFact) -> FundamentalFact:
    """Normalize an explicitly scaled monetary/count fact to base units."""
    if fact.scale is ValueScale.ONES:
        return fact
    value = fact.value * _SCALE_FACTORS[fact.scale]
    if not math.isfinite(value):
        raise FundamentalNormalizationError("scaled fundamental value is not finite")
    return fact.model_copy(update={"value": value, "scale": ValueScale.ONES})


def normalize_percent(value: float, *, source_is_fraction: bool) -> float:
    """Normalize a declared decimal fraction or percent-point input to percent points."""
    normalized = value * 100.0 if source_is_fraction else value
    if not math.isfinite(normalized):
        raise FundamentalNormalizationError("normalized percent is not finite")
    return normalized


def point_in_time_facts(
    facts: tuple[FundamentalFact, ...],
    *,
    as_of: datetime,
) -> tuple[FundamentalFact, ...]:
    """Conservatively retain only facts both public and acquired by decision time."""
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise FundamentalNormalizationError("point-in-time boundary must be timezone-aware")
    visible = tuple(
        fact
        for fact in facts
        if fact.published_at <= as_of and fact.acquired_at <= as_of
    )
    return resolve_revisions(visible)


def resolve_revisions(facts: tuple[FundamentalFact, ...]) -> tuple[FundamentalFact, ...]:
    """Select the explicit latest same-source revision and retain cross-source facts."""
    grouped: dict[tuple[str, str, str, str], list[FundamentalFact]] = defaultdict(list)
    for fact in facts:
        grouped[
            (
                fact.company.symbol,
                fact.source_provider,
                fact.metric.value,
                fact.period.period_id,
            )
        ].append(fact)
    selected: list[FundamentalFact] = []
    for key in sorted(grouped):
        candidates = grouped[key]
        latest_revision = max(item.revision for item in candidates)
        latest = [item for item in candidates if item.revision == latest_revision]
        if len(latest) != 1:
            raise FundamentalNormalizationError("ambiguous same-source fundamental revision")
        selected.append(latest[0])
    return tuple(sorted(selected, key=_fact_sort_key))


def preferred_fact(facts: tuple[FundamentalFact, ...]) -> FundamentalFact:
    """Select unique strongest provenance or reject an equally strong conflict."""
    if not facts:
        raise FundamentalNormalizationError("no fundamental facts supplied")
    ensure_compatible_values(facts)
    if any(item.period != facts[0].period for item in facts):
        raise FundamentalNormalizationError(
            "preferred fact selection requires one reporting period"
        )
    normalized = tuple(normalize_scale(item) for item in facts)
    best_rank = min(SOURCE_QUALITY_ORDER[item.source_quality] for item in normalized)
    strongest = tuple(
        item for item in normalized if SOURCE_QUALITY_ORDER[item.source_quality] == best_rank
    )
    signatures = {(item.value, item.unit, item.currency) for item in strongest}
    if len(signatures) != 1:
        raise FundamentalNormalizationError("equally strong fundamental sources conflict")
    return sorted(strongest, key=_fact_sort_key)[-1]


def ensure_compatible_values(facts: tuple[FundamentalFact, ...]) -> None:
    """Reject mixed company, metric, unit, or currency arithmetic."""
    if not facts:
        raise FundamentalNormalizationError("fundamental arithmetic requires facts")
    first = facts[0]
    if any(item.company.symbol != first.company.symbol for item in facts):
        raise FundamentalNormalizationError("fundamental arithmetic cannot mix companies")
    if any(item.metric is not first.metric for item in facts):
        raise FundamentalNormalizationError("fundamental arithmetic cannot mix metrics")
    if any(item.unit is not first.unit for item in facts):
        raise FundamentalNormalizationError("fundamental arithmetic cannot mix units")
    if any(item.currency != first.currency for item in facts):
        raise FundamentalNormalizationError("currency conversion requires an explicit FX source")


def is_financial_company(fact: FundamentalFact) -> bool:
    """Return conservative classification for banking/NBFC policy gating."""
    text = " ".join(
        item.casefold()
        for item in (fact.company.sector, fact.company.industry)
        if item is not None
    )
    return any(term in text for term in ("bank", "nbfc", "financial services", "insurance"))


def _fact_sort_key(fact: FundamentalFact) -> tuple[object, ...]:
    return (
        fact.period.end_date,
        fact.period.period_id,
        fact.metric.value,
        fact.source_provider,
        fact.revision,
        fact.fact_id,
    )


def validate_unit_for_metric(fact: FundamentalFact) -> None:
    """Guard the broadest class of percent-versus-currency mistakes."""
    percent_like = {
        "growth",
        "margin",
        "roe",
        "roce",
        "roa",
        "yield",
        "ownership",
        "pledge",
        "dilution",
        "percentile",
    }
    if any(token in fact.metric.value for token in percent_like):
        if fact.unit is not FundamentalUnit.PERCENT:
            raise FundamentalNormalizationError(
                f"{fact.metric.value} requires explicit PERCENT units"
            )
