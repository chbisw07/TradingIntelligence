"""Deterministic source-quality ordering and weakest-state helpers."""

from tiaf.contracts import DataQuality, FreshnessState

from .enums import FundamentalSourceQuality

SOURCE_QUALITY_ORDER = {
    FundamentalSourceQuality.PRIMARY_FILED: 0,
    FundamentalSourceQuality.EXCHANGE_FILED: 1,
    FundamentalSourceQuality.REGULATORY: 2,
    FundamentalSourceQuality.DERIVED_FROM_PRIMARY: 3,
    FundamentalSourceQuality.COMPANY_REPORTED: 4,
    FundamentalSourceQuality.TRUSTED_AGGREGATOR: 5,
    FundamentalSourceQuality.UNKNOWN: 6,
}

DATA_QUALITY_ORDER = {
    DataQuality.GOOD: 0,
    DataQuality.PARTIAL: 1,
    DataQuality.DEGRADED: 2,
    DataQuality.UNAVAILABLE: 3,
}

FRESHNESS_ORDER = {
    FreshnessState.FRESH: 0,
    FreshnessState.AGING: 1,
    FreshnessState.STALE: 2,
    FreshnessState.UNKNOWN: 3,
}


def weakest_quality(values: tuple[DataQuality, ...]) -> DataQuality:
    """Return the weakest supplied data quality."""
    return max(values, key=DATA_QUALITY_ORDER.__getitem__) if values else DataQuality.UNAVAILABLE


def weakest_freshness(values: tuple[FreshnessState, ...]) -> FreshnessState:
    """Return the weakest supplied freshness state."""
    return max(values, key=FRESHNESS_ORDER.__getitem__) if values else FreshnessState.UNKNOWN

