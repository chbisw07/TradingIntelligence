"""Tests for opportunity and position request contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from tiaf.contracts import (
    DirectionPolicy,
    Horizon,
    OpportunityRequest,
    PositionRequest,
    TradeStyle,
)

NOW = datetime(2026, 9, 5, 4, 30, tzinfo=UTC)


def opportunity_request(**changes: object) -> OpportunityRequest:
    values: dict[str, object] = {
        "request_id": "req-001",
        "universe": [" reliance ", "TCS", "RELIANCE", " infy "],
        "trade_style": TradeStyle.DAY,
        "horizon": Horizon(label="intraday"),
        "direction_policy": DirectionPolicy.BOTH,
        "top_n": 5,
        "requested_at": NOW,
    }
    values.update(changes)
    return OpportunityRequest.model_validate(values)


def test_opportunity_universe_is_normalized_and_deduplicated_in_order() -> None:
    request = opportunity_request()

    assert request.universe == ("RELIANCE", "TCS", "INFY")
    assert request.top_n > len(request.universe)


def test_opportunity_rejects_empty_universe() -> None:
    with pytest.raises(ValidationError, match="universe must not be empty"):
        opportunity_request(universe=[])


def test_opportunity_rejects_naive_requested_at() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        opportunity_request(requested_at=datetime(2026, 9, 5, 10))


def test_opportunity_rejects_nonpositive_analysis_budget() -> None:
    with pytest.raises(ValidationError):
        opportunity_request(max_analysis_seconds=0)


def test_position_request_normalizes_symbols_without_entry_thesis() -> None:
    request = PositionRequest(
        position_id="position-001",
        underlying=" reliance ",
        instrument=" reliance26sep3000ce ",
        quantity=75,
        average_price=31.5,
        requested_at=NOW,
    )

    assert request.underlying == "RELIANCE"
    assert request.instrument == "RELIANCE26SEP3000CE"
    assert not hasattr(request, "entry_thesis")


def test_position_request_rejects_zero_quantity() -> None:
    with pytest.raises(ValidationError, match="quantity must not be zero"):
        PositionRequest(
            position_id="position-001",
            underlying="RELIANCE",
            instrument="RELIANCE26SEP3000CE",
            quantity=0,
            average_price=31.5,
            requested_at=NOW,
        )


def test_position_request_rejects_negative_price() -> None:
    with pytest.raises(ValidationError):
        PositionRequest(
            position_id="position-001",
            underlying="RELIANCE",
            instrument="RELIANCE26SEP3000CE",
            quantity=-75,
            average_price=-0.01,
            requested_at=NOW,
        )
