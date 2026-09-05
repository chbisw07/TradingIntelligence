"""Provider-neutral rolling historical-option models and value types."""

import re
from datetime import date
from enum import IntEnum, StrEnum
from typing import Self

from pydantic import ConfigDict, Field, RootModel, field_validator, model_validator

from tiaf.contracts import ContractModel, DataQuality, OptionType
from tiaf.contracts.common import Metadata
from tiaf.data.models import (
    InstrumentKey,
    NonNegativeFloat,
    NonNegativeInt,
    NormalizedDateTime,
    NormalizedInterval,
    NormalizedProvider,
    PositiveFloat,
)

_RELATIVE_STRIKE_PATTERN = re.compile(r"ATM(?:[+-][1-9][0-9]*)?\Z")


class ExpiryFlag(StrEnum):
    """Dhan-independent rolling expiry cadence."""

    WEEK = "WEEK"
    MONTH = "MONTH"


class HistoricalOptionExpiryCode(IntEnum):
    """Rolling expired-options expiry position validated against the live API."""

    NEAR = 1
    NEXT = 2
    FAR = 3


class RelativeStrike(RootModel[str]):
    """Validated ATM-relative strike label such as ATM, ATM+2, or ATM-1."""

    model_config = ConfigDict(frozen=True)

    @field_validator("root", mode="before")
    @classmethod
    def normalize_and_validate(cls, value: object) -> object:
        """Normalize case/whitespace and reject non-relative strike syntax."""
        if not isinstance(value, str):
            raise ValueError("relative strike must be a string")
        normalized = value.strip().upper()
        if not _RELATIVE_STRIKE_PATTERN.fullmatch(normalized):
            raise ValueError("relative strike must be ATM or ATM followed by +/-N")
        return normalized

    @property
    def offset(self) -> int:
        """Return the signed strike-step offset from ATM."""
        if self.root == "ATM":
            return 0
        return int(self.root[3:])

    def __str__(self) -> str:
        """Return the provider-neutral wire value."""
        return self.root


class HistoricalOptionBar(ContractModel):
    """One provider-reported rolling historical option observation."""

    underlying: InstrumentKey
    option_type: OptionType
    expiry_flag: ExpiryFlag
    expiry_code: HistoricalOptionExpiryCode
    relative_strike: RelativeStrike
    start_at: NormalizedDateTime
    open: NonNegativeFloat | None = None
    high: NonNegativeFloat | None = None
    low: NonNegativeFloat | None = None
    close: NonNegativeFloat | None = None
    implied_volatility: NonNegativeFloat | None = None
    volume: NonNegativeInt | None = None
    open_interest: NonNegativeInt | None = None
    actual_strike: PositiveFloat | None = None
    spot: NonNegativeFloat | None = None
    source_provider: NormalizedProvider
    quality: DataQuality
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_ohlc(self) -> Self:
        """Validate OHLC envelopes using only values actually present."""
        comparable = tuple(
            value for value in (self.open, self.close, self.low) if value is not None
        )
        if self.high is not None and comparable and self.high < max(comparable):
            raise ValueError("high must be at least every available open, close, and low")
        comparable = tuple(
            value for value in (self.open, self.close, self.high) if value is not None
        )
        if self.low is not None and comparable and self.low > min(comparable):
            raise ValueError("low must be at most every available open, close, and high")
        return self


class HistoricalOptionSeries(ContractModel):
    """Chronological rolling option history for one factual request context."""

    underlying: InstrumentKey
    option_type: OptionType
    expiry_flag: ExpiryFlag
    expiry_code: HistoricalOptionExpiryCode
    relative_strike: RelativeStrike
    interval: NormalizedInterval
    bars: tuple[HistoricalOptionBar, ...]
    requested_from: date
    requested_to: date
    observed_at: NormalizedDateTime
    source_provider: NormalizedProvider
    quality: DataQuality
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_series(self) -> Self:
        """Validate chronology, request context, bounds, and empty policy."""
        if self.requested_to <= self.requested_from:
            raise ValueError("requested_to must be later than requested_from")
        if not self.bars and self.quality not in {
            DataQuality.PARTIAL,
            DataQuality.UNAVAILABLE,
        }:
            raise ValueError("empty bars require PARTIAL or UNAVAILABLE quality")
        starts = tuple(bar.start_at for bar in self.bars)
        if starts != tuple(sorted(starts)):
            raise ValueError("historical option bars must be ordered ascending")
        if len(starts) != len(set(starts)):
            raise ValueError("duplicate historical option timestamps are not allowed")
        for bar in self.bars:
            if bar.underlying != self.underlying:
                raise ValueError("all bars must match the series underlying")
            if bar.option_type is not self.option_type:
                raise ValueError("all bars must match the series option_type")
            if bar.expiry_flag is not self.expiry_flag or bar.expiry_code is not self.expiry_code:
                raise ValueError("all bars must match the series expiry context")
            if bar.relative_strike != self.relative_strike:
                raise ValueError("all bars must match the series relative strike")
            if bar.source_provider != self.source_provider:
                raise ValueError("all bars must match the series source provider")
            if not self.requested_from <= bar.start_at.date() < self.requested_to:
                raise ValueError("all bars must fall within the requested half-open date range")
        return self
