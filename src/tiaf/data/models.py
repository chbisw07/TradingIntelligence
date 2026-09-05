"""Frozen provider-neutral market-data models."""

from datetime import date, datetime, timedelta
from typing import Annotated, Self

from pydantic import AfterValidator, BeforeValidator, Field, StringConstraints, model_validator

from tiaf.contracts import ContractModel, DataQuality, FreshnessState, OptionType
from tiaf.contracts.common import Metadata
from tiaf.data.enums import InstrumentType, MarketSegment, QuoteFieldAvailability
from tiaf.data.normalization import (
    normalize_datetime_to_ist,
    normalize_exchange,
    normalize_interval,
    normalize_provider_name,
    normalize_symbol,
)

NormalizedSymbol = Annotated[str, BeforeValidator(normalize_symbol)]
NormalizedExchange = Annotated[str, BeforeValidator(normalize_exchange)]
NormalizedProvider = Annotated[str, BeforeValidator(normalize_provider_name)]
NormalizedInterval = Annotated[str, BeforeValidator(normalize_interval)]
NormalizedDateTime = Annotated[datetime, AfterValidator(normalize_datetime_to_ist)]
NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
NonNegativeFloat = Annotated[float, Field(ge=0)]
PositiveFloat = Annotated[float, Field(gt=0)]
NonNegativeInt = Annotated[int, Field(ge=0)]
PositiveInt = Annotated[int, Field(gt=0)]

MAX_OBSERVED_CLOCK_SKEW = timedelta(days=1)


class InstrumentKey(ContractModel):
    """Provider-neutral identity for a market instrument."""

    symbol: NormalizedSymbol
    exchange: NormalizedExchange
    segment: MarketSegment
    instrument_type: InstrumentType
    expiry: date | None = None
    strike: PositiveFloat | None = None
    option_type: OptionType | None = None
    trading_symbol: NormalizedSymbol | None = None
    provider_instrument_id: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_derivative_identity(self) -> Self:
        """Keep option and non-option identity fields semantically consistent."""
        if self.instrument_type is InstrumentType.CALL_OPTION:
            if self.option_type is not OptionType.CE:
                raise ValueError("CALL_OPTION requires option_type CE")
        elif self.instrument_type is InstrumentType.PUT_OPTION:
            if self.option_type is not OptionType.PE:
                raise ValueError("PUT_OPTION requires option_type PE")
        elif self.option_type is not None:
            raise ValueError("non-option instruments must not set option_type")

        if self.instrument_type is InstrumentType.FUTURE and self.strike is not None:
            raise ValueError("FUTURE must not set strike")
        return self


class QuoteSnapshot(ContractModel):
    """Normalized point-in-time quote and its attribution metadata."""

    instrument: InstrumentKey
    ltp: NonNegativeFloat
    observed_at: NormalizedDateTime
    received_at: NormalizedDateTime
    source_provider: NormalizedProvider
    freshness: FreshnessState
    quality: DataQuality
    availability: QuoteFieldAvailability
    open: NonNegativeFloat | None = None
    high: NonNegativeFloat | None = None
    low: NonNegativeFloat | None = None
    previous_close: NonNegativeFloat | None = None
    volume: NonNegativeInt | None = None
    bid: NonNegativeFloat | None = None
    ask: NonNegativeFloat | None = None
    open_interest: NonNegativeInt | None = None
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_quote(self) -> Self:
        """Validate quote ordering and reject clearly impossible clock skew."""
        if self.bid is not None and self.ask is not None and self.ask < self.bid:
            raise ValueError("ask must be greater than or equal to bid")
        if self.observed_at - self.received_at > MAX_OBSERVED_CLOCK_SKEW:
            raise ValueError("observed_at is implausibly later than received_at")
        return self


class OHLCVBar(ContractModel):
    """Normalized OHLCV bar for one instrument and interval."""

    instrument: InstrumentKey
    interval: NormalizedInterval
    start_at: NormalizedDateTime
    end_at: NormalizedDateTime
    open: NonNegativeFloat
    high: NonNegativeFloat
    low: NonNegativeFloat
    close: NonNegativeFloat
    source_provider: NormalizedProvider
    volume: NonNegativeInt | None = None
    open_interest: NonNegativeInt | None = None
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_bar(self) -> Self:
        """Validate bar time and price envelopes."""
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be later than start_at")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be at least open, close, and low")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be at most open, close, and high")
        return self


class HistoricalSeries(ContractModel):
    """Validated, chronological bars from one provider and interval."""

    instrument: InstrumentKey
    interval: NormalizedInterval
    bars: tuple[OHLCVBar, ...]
    source_provider: NormalizedProvider
    observed_at: NormalizedDateTime
    freshness: FreshnessState
    quality: DataQuality
    requested_from: NormalizedDateTime | None = None
    requested_to: NormalizedDateTime | None = None
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_series(self) -> Self:
        """Validate chronology, identity, interval, and empty-series policy."""
        if not self.bars and self.quality not in {DataQuality.UNAVAILABLE, DataQuality.PARTIAL}:
            raise ValueError("empty bars require UNAVAILABLE or PARTIAL quality")

        starts = tuple(bar.start_at for bar in self.bars)
        if len(starts) != len(set(starts)):
            raise ValueError("duplicate bar start_at values are not allowed")
        if starts != tuple(sorted(starts)):
            raise ValueError("bars must be ordered ascending by start_at")

        if any(bar.instrument != self.instrument for bar in self.bars):
            raise ValueError("all bars must match the series instrument")
        if any(bar.interval != self.interval for bar in self.bars):
            raise ValueError("all bars must match the series interval")
        if (
            self.requested_from is not None
            and self.requested_to is not None
            and self.requested_to <= self.requested_from
        ):
            raise ValueError("requested_to must be later than requested_from")
        return self


class InstrumentRecord(ContractModel):
    """Normalized instrument-master record."""

    instrument: InstrumentKey
    active: bool
    source_provider: NormalizedProvider
    company_name: NonEmptyStr | None = None
    lot_size: PositiveInt | None = None
    tick_size: PositiveFloat | None = None
    underlying_symbol: NormalizedSymbol | None = None
    expiry: date | None = None
    strike: PositiveFloat | None = None
    option_type: OptionType | None = None
    metadata: Metadata = Field(default_factory=dict)
