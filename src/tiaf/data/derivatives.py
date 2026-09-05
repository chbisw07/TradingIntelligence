"""Provider-neutral live derivatives snapshot models."""

from datetime import date
from typing import Self

from pydantic import Field, model_validator

from tiaf.contracts import ContractModel, DataQuality, FreshnessState, OptionType
from tiaf.contracts.common import Metadata
from tiaf.data.enums import InstrumentType
from tiaf.data.models import (
    InstrumentKey,
    NonNegativeFloat,
    NonNegativeInt,
    NormalizedDateTime,
    NormalizedProvider,
    PositiveFloat,
)


class OptionGreeks(ContractModel):
    """Provider-reported option Greeks, without recomputation."""

    delta: float | None = None
    gamma: float | None = None
    theta: float | None = None
    vega: float | None = None


class OptionMarketSnapshot(ContractModel):
    """One normalized CE or PE contract in a live option chain."""

    instrument: InstrumentKey
    option_type: OptionType
    strike: PositiveFloat
    expiry: date
    security_id: str | None = None
    ltp: NonNegativeFloat | None = None
    previous_close: NonNegativeFloat | None = None
    average_price: NonNegativeFloat | None = None
    bid: NonNegativeFloat | None = None
    bid_quantity: NonNegativeInt | None = None
    ask: NonNegativeFloat | None = None
    ask_quantity: NonNegativeInt | None = None
    volume: NonNegativeInt | None = None
    previous_volume: NonNegativeInt | None = None
    open_interest: NonNegativeInt | None = None
    previous_open_interest: NonNegativeInt | None = None
    implied_volatility: NonNegativeFloat | None = None
    greeks: OptionGreeks = Field(default_factory=OptionGreeks)
    observed_at: NormalizedDateTime
    source_provider: NormalizedProvider
    freshness: FreshnessState
    quality: DataQuality
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_contract(self) -> Self:
        """Keep normalized side, identity, expiry, strike, and spread consistent."""
        expected_instrument_type = (
            InstrumentType.CALL_OPTION
            if self.option_type is OptionType.CE
            else InstrumentType.PUT_OPTION
        )
        if self.instrument.instrument_type is not expected_instrument_type:
            raise ValueError("instrument type must agree with option_type")
        if self.instrument.option_type is not self.option_type:
            raise ValueError("instrument option_type must agree with snapshot option_type")
        if self.instrument.strike != self.strike:
            raise ValueError("instrument strike must agree with snapshot strike")
        if self.instrument.expiry is not None and self.instrument.expiry != self.expiry:
            raise ValueError("instrument expiry must agree with snapshot expiry")
        if (
            self.security_id is not None
            and self.instrument.provider_instrument_id != self.security_id
        ):
            raise ValueError("security_id must agree with instrument provider_instrument_id")
        if self.bid is not None and self.ask is not None:
            if self.bid > 0 and self.ask > 0 and self.ask < self.bid:
                raise ValueError("positive ask must be greater than or equal to positive bid")
        return self


class OptionStrikeSnapshot(ContractModel):
    """The available CE and PE observations for one strike."""

    strike: PositiveFloat
    call: OptionMarketSnapshot | None = None
    put: OptionMarketSnapshot | None = None

    @model_validator(mode="after")
    def validate_sides(self) -> Self:
        """Require at least one correctly keyed side with consistent context."""
        if self.call is None and self.put is None:
            raise ValueError("an option strike requires at least one side")
        if self.call is not None:
            if self.call.option_type is not OptionType.CE:
                raise ValueError("call side must be CE")
            if self.call.strike != self.strike:
                raise ValueError("call strike must agree with strike snapshot")
        if self.put is not None:
            if self.put.option_type is not OptionType.PE:
                raise ValueError("put side must be PE")
            if self.put.strike != self.strike:
                raise ValueError("put strike must agree with strike snapshot")
        if self.call is not None and self.put is not None:
            if self.call.expiry != self.put.expiry:
                raise ValueError("call and put expiry must agree")
        return self


class OptionChainSnapshot(ContractModel):
    """An immutable, ordered live option chain for one underlying and expiry."""

    underlying: InstrumentKey
    expiry: date
    underlying_ltp: NonNegativeFloat | None = None
    strikes: tuple[OptionStrikeSnapshot, ...]
    observed_at: NormalizedDateTime
    received_at: NormalizedDateTime
    source_provider: NormalizedProvider
    freshness: FreshnessState
    quality: DataQuality
    snapshot_id: str | None = None
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_chain(self) -> Self:
        """Validate ordering, uniqueness, underlying context, and empty policy."""
        if not self.strikes and self.quality is not DataQuality.UNAVAILABLE:
            raise ValueError("an empty option chain requires UNAVAILABLE quality")
        values = tuple(item.strike for item in self.strikes)
        if values != tuple(sorted(values)):
            raise ValueError("option strikes must be ordered ascending")
        if len(values) != len(set(values)):
            raise ValueError("duplicate option strikes are not allowed")
        for strike in self.strikes:
            for side in (strike.call, strike.put):
                if side is None:
                    continue
                if side.expiry != self.expiry:
                    raise ValueError("all option contracts must match the chain expiry")
                if side.instrument.symbol != self.underlying.symbol:
                    raise ValueError("all option contracts must match the underlying symbol")
                if side.instrument.exchange != self.underlying.exchange:
                    raise ValueError("all option contracts must match the underlying exchange")
        return self


class ExpiryListSnapshot(ContractModel):
    """Immutable active option expiries for one underlying."""

    underlying: InstrumentKey
    expiries: tuple[date, ...]
    observed_at: NormalizedDateTime
    received_at: NormalizedDateTime
    source_provider: NormalizedProvider
    freshness: FreshnessState
    quality: DataQuality
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_expiries(self) -> Self:
        """Require chronological unique dates and explicit unavailable emptiness."""
        if not self.expiries and self.quality is not DataQuality.UNAVAILABLE:
            raise ValueError("an empty expiry list requires UNAVAILABLE quality")
        if self.expiries != tuple(sorted(self.expiries)):
            raise ValueError("expiries must be ordered ascending")
        if len(self.expiries) != len(set(self.expiries)):
            raise ValueError("duplicate expiries are not allowed")
        return self
