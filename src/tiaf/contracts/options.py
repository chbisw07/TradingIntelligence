"""Option-expression data contract; no selection or sizing behavior."""

from datetime import date
from typing import Self

from pydantic import model_validator

from tiaf.contracts.common import (
    ContractModel,
    NonEmptyStr,
    NonNegativeFloat,
    PositiveFloat,
    PositiveInt,
    Score,
    Symbol,
    TiafDateTime,
)
from tiaf.contracts.enums import OptionType, TradeDirection


class OptionExpression(ContractModel):
    """A candidate option representation, independent of selection logic."""

    underlying: Symbol
    direction: TradeDirection
    exchange: Symbol
    expiry: date
    strike: PositiveFloat
    option_type: OptionType
    trading_symbol: Symbol | None = None
    lot_size: PositiveInt | None = None
    delta: float | None = None
    theta: float | None = None
    iv: NonNegativeFloat | None = None
    bid: NonNegativeFloat | None = None
    ask: NonNegativeFloat | None = None
    ltp: NonNegativeFloat | None = None
    liquidity_score: Score | None = None
    suitability_score: Score | None = None
    rationale: NonEmptyStr | None = None
    data_snapshot_id: NonEmptyStr | None = None
    observed_at: TiafDateTime | None = None

    @model_validator(mode="after")
    def validate_market_prices(self) -> Self:
        """Reject an inverted quoted market."""
        if self.bid is not None and self.ask is not None and self.ask < self.bid:
            raise ValueError("ask must be greater than or equal to bid")
        return self
