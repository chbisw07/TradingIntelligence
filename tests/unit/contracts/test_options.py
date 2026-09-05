"""Tests for the option-expression contract."""

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from tiaf.contracts import OptionExpression, OptionType, TradeDirection

NOW = datetime(2026, 9, 5, 4, 30, tzinfo=UTC)


def option_expression(**changes: object) -> OptionExpression:
    values: dict[str, object] = {
        "underlying": " reliance ",
        "direction": TradeDirection.BULLISH,
        "exchange": " nfo ",
        "expiry": date(2026, 9, 24),
        "strike": 3000,
        "option_type": OptionType.CE,
        "trading_symbol": "reliance26sep3000ce",
        "lot_size": 75,
        "bid": 30.0,
        "ask": 31.0,
        "ltp": 30.5,
        "liquidity_score": 80,
        "suitability_score": 70,
        "observed_at": NOW,
    }
    values.update(changes)
    return OptionExpression.model_validate(values)


def test_option_expression_normalizes_identifiers() -> None:
    expression = option_expression()

    assert expression.underlying == "RELIANCE"
    assert expression.exchange == "NFO"
    assert expression.trading_symbol == "RELIANCE26SEP3000CE"


def test_option_expression_rejects_inverted_bid_ask() -> None:
    with pytest.raises(ValidationError, match="ask must be greater"):
        option_expression(bid=32, ask=31)


def test_option_expression_requires_positive_strike() -> None:
    with pytest.raises(ValidationError):
        option_expression(strike=0)


def test_option_expression_rejects_negative_prices() -> None:
    with pytest.raises(ValidationError):
        option_expression(ltp=-0.01)


def test_option_expression_json_round_trip() -> None:
    expression = option_expression()

    restored = OptionExpression.model_validate_json(expression.model_dump_json())

    assert restored == expression
    assert restored.model_dump(mode="json")["expiry"] == "2026-09-24"
