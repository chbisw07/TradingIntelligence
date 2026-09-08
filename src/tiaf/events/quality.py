"""Source/data/freshness ordering without pretending category is probability."""

from tiaf.contracts import DataQuality, FreshnessState

from .enums import EventSourceClass, SourceQualityState

SOURCE_CLASS_ORDER = {
    EventSourceClass.EXCHANGE_FILING: 0,
    EventSourceClass.REGULATORY_FILING: 0,
    EventSourceClass.OFFICIAL_GOVERNMENT: 1,
    EventSourceClass.COMPANY_RELEASE: 1,
    EventSourceClass.EARNINGS_TRANSCRIPT: 2,
    EventSourceClass.TRUSTED_NEWS: 3,
    EventSourceClass.LICENSED_AGGREGATOR: 4,
    EventSourceClass.OTHER: 5,
    EventSourceClass.UNKNOWN: 6,
}
_QUALITY_ORDER = {
    DataQuality.GOOD: 0,
    DataQuality.PARTIAL: 1,
    DataQuality.DEGRADED: 2,
    DataQuality.UNAVAILABLE: 3,
}
_FRESHNESS_ORDER = {
    FreshnessState.FRESH: 0,
    FreshnessState.AGING: 1,
    FreshnessState.STALE: 2,
    FreshnessState.UNKNOWN: 3,
}


def source_quality_state(source_class: EventSourceClass) -> SourceQualityState:
    if source_class in {EventSourceClass.EXCHANGE_FILING, EventSourceClass.REGULATORY_FILING}:
        return SourceQualityState.PRIMARY
    if source_class in {
        EventSourceClass.OFFICIAL_GOVERNMENT,
        EventSourceClass.COMPANY_RELEASE,
        EventSourceClass.EARNINGS_TRANSCRIPT,
    }:
        return SourceQualityState.OFFICIAL
    if source_class in {EventSourceClass.TRUSTED_NEWS, EventSourceClass.LICENSED_AGGREGATOR}:
        return SourceQualityState.TRUSTED_SECONDARY
    if source_class is EventSourceClass.OTHER:
        return SourceQualityState.OTHER
    return SourceQualityState.UNKNOWN


def weakest_quality(values: tuple[DataQuality, ...]) -> DataQuality:
    return max(values, key=_QUALITY_ORDER.__getitem__) if values else DataQuality.UNAVAILABLE


def weakest_freshness(values: tuple[FreshnessState, ...]) -> FreshnessState:
    return max(values, key=_FRESHNESS_ORDER.__getitem__) if values else FreshnessState.UNKNOWN
