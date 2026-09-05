"""Inbound opportunity and position intelligence requests."""

from pydantic import Field, field_validator

from tiaf.contracts.common import (
    ContractModel,
    Horizon,
    Metadata,
    NonEmptyStr,
    NonNegativeFloat,
    PositiveInt,
    Symbol,
    TiafDateTime,
)
from tiaf.contracts.enums import DirectionPolicy, TradeStyle


class OpportunityRequest(ContractModel):
    """Request to assess a universe for forward opportunities."""

    universe: tuple[Symbol, ...]
    trade_style: TradeStyle
    horizon: Horizon
    direction_policy: DirectionPolicy
    top_n: PositiveInt
    requested_at: TiafDateTime
    request_id: NonEmptyStr | None = None
    correlation_id: NonEmptyStr | None = None
    source_system: NonEmptyStr | None = None
    optional_enrichment: Metadata = Field(default_factory=dict)
    max_analysis_seconds: PositiveInt | None = None

    @field_validator("universe")
    @classmethod
    def normalize_universe(cls, universe: tuple[str, ...]) -> tuple[str, ...]:
        """Deduplicate normalized symbols while retaining their input order."""
        if not universe:
            raise ValueError("universe must not be empty")
        return tuple(dict.fromkeys(universe))


class PositionRequest(ContractModel):
    """Request to evaluate an existing position from the present onward."""

    position_id: NonEmptyStr
    underlying: Symbol
    instrument: Symbol
    quantity: float
    average_price: NonNegativeFloat
    requested_at: TiafDateTime
    current_price: NonNegativeFloat | None = None
    current_pnl: float | None = None
    current_pnl_pct: float | None = None
    horizon: Horizon | None = None
    adopted_at: TiafDateTime | None = None
    source_system: NonEmptyStr | None = None
    request_id: NonEmptyStr | None = None
    correlation_id: NonEmptyStr | None = None
    optional_context: Metadata = Field(default_factory=dict)

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_nonzero(cls, quantity: float) -> float:
        """Accept long or short positions, but reject an empty position."""
        if quantity == 0:
            raise ValueError("quantity must not be zero")
        return quantity
