"""Frozen provider-neutral instrument resolution contracts."""

from datetime import date
from typing import Self

from pydantic import Field, model_validator

from tiaf.contracts import ContractModel, DataQuality, OptionType
from tiaf.contracts.common import Metadata
from tiaf.data.enums import InstrumentType, MarketSegment
from tiaf.data.models import (
    InstrumentKey,
    NonEmptyStr,
    NormalizedDateTime,
    NormalizedExchange,
    NormalizedProvider,
    NormalizedSymbol,
    PositiveFloat,
    PositiveInt,
)
from tiaf.data.resolution.enums import ResolutionKind


class InstrumentQuery(ContractModel):
    """Explicit lookup criteria without fuzzy or preference semantics."""

    symbol: NormalizedSymbol | None = None
    exchange: NormalizedExchange | None = None
    segment: MarketSegment | None = None
    instrument_type: InstrumentType | None = None
    expiry: date | None = None
    strike: PositiveFloat | None = None
    option_type: OptionType | None = None
    trading_symbol: NormalizedSymbol | None = None
    provider_instrument_id: NonEmptyStr | None = None
    provider: NormalizedProvider | None = None
    exact_only: bool = True
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_query(self) -> Self:
        """Require an identifier and coherent derivative filters."""
        if not (self.symbol or self.trading_symbol or self.provider_instrument_id):
            raise ValueError("query requires symbol, trading_symbol, or provider_instrument_id")

        option_types = {InstrumentType.CALL_OPTION, InstrumentType.PUT_OPTION}
        if self.instrument_type in option_types:
            if self.expiry is None or self.strike is None or self.option_type is None:
                raise ValueError(
                    "option queries require expiry, strike, and option_type"
                )
            expected = (
                OptionType.CE
                if self.instrument_type is InstrumentType.CALL_OPTION
                else OptionType.PE
            )
            if self.option_type is not expected:
                raise ValueError(
                    f"{self.instrument_type.value} requires option_type {expected.value}"
                )
        elif self.option_type is not None:
            raise ValueError("option_type requires an option instrument_type")

        if self.strike is not None and self.instrument_type not in option_types:
            raise ValueError("strike requires an option instrument_type")
        return self


class ResolutionPolicy(ContractModel):
    """Configurable market scope applied only when a query leaves scope open."""

    primary_exchange: NormalizedExchange = "NSE"
    primary_fno_exchange: NormalizedExchange = "NSE"
    prefer_primary_cash_listing: bool = True


class ResolvedInstrument(ContractModel):
    """Canonical identity plus provider attribution for one master record."""

    instrument: InstrumentKey
    provider_name: NormalizedProvider
    provider_instrument_id: NonEmptyStr
    company_name: NonEmptyStr | None = None
    underlying_symbol: NormalizedSymbol | None = None
    lot_size: PositiveInt | None = None
    tick_size: PositiveFloat | None = None
    source_record_id: NonEmptyStr
    source_observed_at: NormalizedDateTime
    resolution_kind: ResolutionKind
    quality: DataQuality
    metadata: Metadata = Field(default_factory=dict)


class ResolutionResult(ContractModel):
    """Explicit unique, ambiguous, or not-found resolution outcome."""

    query: InstrumentQuery
    matches: tuple[ResolvedInstrument, ...] = ()
    resolved: ResolvedInstrument | None = None
    ambiguous: bool = False
    not_found: bool = False
    source_provider: NormalizedProvider | None = None
    observed_at: NormalizedDateTime
    metadata: Metadata = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_outcome(self) -> Self:
        """Forbid contradictory or incomplete outcome states."""
        match_count = len(self.matches)
        if match_count == 0:
            if not self.not_found or self.ambiguous or self.resolved is not None:
                raise ValueError("zero matches require a not-found outcome")
        elif match_count == 1:
            if self.resolved != self.matches[0] or self.ambiguous or self.not_found:
                raise ValueError("one match requires that instrument to be resolved")
        elif not self.ambiguous or self.not_found or self.resolved is not None:
            raise ValueError("multiple matches require an ambiguous outcome")
        return self
