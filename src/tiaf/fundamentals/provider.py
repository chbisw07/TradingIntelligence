"""Provider-neutral fundamental source protocol and bounded in-memory adapter."""

from collections import defaultdict
from datetime import timedelta
from typing import Protocol, runtime_checkable

from .enums import ReportingPeriodKind
from .models import (
    CompanyIdentity,
    FundamentalDataset,
    FundamentalFact,
    FundamentalRequest,
    fundamental_fingerprint,
)
from .normalization import point_in_time_facts
from .quality import weakest_freshness, weakest_quality


class FundamentalProviderError(RuntimeError):
    """Typed provider-neutral acquisition failure."""


@runtime_checkable
class FundamentalProvider(Protocol):
    """Read-only source of normalized point-in-time financial facts."""

    def identity(self) -> tuple[str, str]:
        """Return provider ID and adapter version."""
        ...

    def resolve_company(self, symbol: str) -> CompanyIdentity | None:
        """Resolve an exact canonical company identity without fuzzy matching."""
        ...

    def fetch(self, request: FundamentalRequest) -> FundamentalDataset:
        """Return normalized facts visible at the requested decision time."""
        ...


class InMemoryFundamentalProvider:
    """Deterministic bounded read adapter for fixtures and licensed caller data."""

    def __init__(
        self,
        facts: tuple[FundamentalFact, ...],
        *,
        provider_id: str = "tiaf.in-memory-fundamentals",
        provider_version: str = "1.0",
        validity_days: int = 90,
        point_in_time_limitation: str | None = None,
    ) -> None:
        if validity_days <= 0:
            raise ValueError("fundamental validity_days must be positive")
        self._identity = (provider_id, provider_version)
        self._validity = timedelta(days=validity_days)
        self._limitation = point_in_time_limitation
        self._facts: dict[str, tuple[FundamentalFact, ...]] = {}
        grouped: dict[str, list[FundamentalFact]] = defaultdict(list)
        companies: dict[str, CompanyIdentity] = {}
        for fact in facts:
            grouped[fact.company.symbol].append(fact)
            prior = companies.setdefault(fact.company.symbol, fact.company)
            if prior != fact.company:
                raise ValueError("one symbol cannot map to conflicting company identities")
        self._companies = companies
        for symbol, values in grouped.items():
            self._facts[symbol] = tuple(values)

    def identity(self) -> tuple[str, str]:
        return self._identity

    def resolve_company(self, symbol: str) -> CompanyIdentity | None:
        return self._companies.get(symbol.strip().upper())

    def fetch(self, request: FundamentalRequest) -> FundamentalDataset:
        provider_id, provider_version = self._identity
        stored_company = self._companies.get(request.company.symbol)
        if stored_company is not None and stored_company != request.company:
            raise FundamentalProviderError(
                "requested company does not match canonical provider identity"
            )
        source = self._facts.get(request.company.symbol, ())
        visible = point_in_time_facts(source, as_of=request.as_of)
        family_filtered = tuple(item for item in visible if item.family in request.families)
        selected = _apply_period_requirements(family_filtered, request)
        present = {item.family for item in selected}
        missing = tuple(item for item in request.families if item not in present)
        available_periods = {
            kind: len({item.period.period_id for item in selected if item.period.kind is kind})
            for kind in (item.kind for item in request.periods)
        }
        missing_periods = tuple(
            item
            for item in request.periods
            if available_periods.get(item.kind, 0) < item.count
        )
        acquired_at = max(
            (item.acquired_at for item in selected),
            default=request.as_of,
        )
        quality = weakest_quality(tuple(item.quality for item in selected))
        freshness = weakest_freshness(tuple(item.freshness for item in selected))
        fingerprint = fundamental_fingerprint(
            request.company,
            provider_id,
            provider_version,
            request.as_of,
            selected,
            missing,
            missing_periods,
            self._limitation,
        )
        return FundamentalDataset(
            dataset_id=f"fundamental:{request.request_id}:{fingerprint[:16]}",
            company=request.company,
            provider_id=provider_id,
            provider_version=provider_version,
            requested_as_of=request.as_of,
            acquired_at=acquired_at,
            valid_until=max(request.as_of, acquired_at) + self._validity,
            facts=selected,
            missing_families=missing,
            missing_periods=missing_periods,
            quality=quality,
            freshness=freshness,
            point_in_time_limitation=self._limitation,
            fingerprint=fingerprint,
        )


def _apply_period_requirements(
    facts: tuple[FundamentalFact, ...],
    request: FundamentalRequest,
) -> tuple[FundamentalFact, ...]:
    limits = {item.kind: item.count for item in request.periods}
    allowed_periods: set[tuple[ReportingPeriodKind, str]] = set()
    for kind, count in limits.items():
        periods = sorted(
            {
                (item.period.end_date, item.period.period_id)
                for item in facts
                if item.period.kind is kind
            }
        )
        allowed_periods.update((kind, period_id) for _, period_id in periods[-count:])
    selected = [
        item
        for item in facts
        if (item.period.kind, item.period.period_id) in allowed_periods
    ]
    return tuple(
        sorted(
            selected,
            key=lambda item: (
                item.period.end_date,
                item.metric.value,
                item.source_provider,
                item.fact_id,
            ),
        )
    )
