"""Tests for normalized instrument identity and master records."""

from datetime import date

import pytest
from pydantic import ValidationError

from tiaf.contracts import OptionType
from tiaf.data import InstrumentKey, InstrumentRecord, InstrumentType, MarketSegment


def test_equity_instrument_key_normalizes_identity() -> None:
    instrument = InstrumentKey(
        symbol=" reliance ",
        exchange=" nse ",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
        trading_symbol=" reliance ",
    )

    assert instrument.symbol == "RELIANCE"
    assert instrument.exchange == "NSE"
    assert instrument.trading_symbol == "RELIANCE"
    assert instrument.option_type is None


def test_call_option_identity_accepts_ce() -> None:
    instrument = InstrumentKey(
        symbol="RELIANCE",
        exchange="NSE",
        segment=MarketSegment.NSE_FNO,
        instrument_type=InstrumentType.CALL_OPTION,
        expiry=date(2026, 9, 24),
        strike=3000,
        option_type=OptionType.CE,
    )

    assert instrument.option_type is OptionType.CE
    assert instrument.strike == 3000


@pytest.mark.parametrize(
    ("instrument_type", "option_type"),
    [
        (InstrumentType.CALL_OPTION, OptionType.PE),
        (InstrumentType.PUT_OPTION, OptionType.CE),
        (InstrumentType.EQUITY, OptionType.CE),
    ],
)
def test_invalid_option_type_combinations_are_rejected(
    instrument_type: InstrumentType,
    option_type: OptionType,
) -> None:
    with pytest.raises(ValidationError):
        InstrumentKey(
            symbol="RELIANCE",
            exchange="NSE",
            segment=MarketSegment.NSE_FNO,
            instrument_type=instrument_type,
            option_type=option_type,
        )


def test_future_rejects_strike() -> None:
    with pytest.raises(ValidationError, match="FUTURE must not set strike"):
        InstrumentKey(
            symbol="NIFTY",
            exchange="NSE",
            segment=MarketSegment.NSE_FNO,
            instrument_type=InstrumentType.FUTURE,
            strike=25000,
        )


@pytest.mark.parametrize(("lot_size", "tick_size"), [(0, 0.05), (75, 0.0)])
def test_instrument_record_rejects_invalid_lot_or_tick(
    lot_size: int,
    tick_size: float,
) -> None:
    instrument = InstrumentKey(
        symbol="RELIANCE",
        exchange="NSE",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
    )

    with pytest.raises(ValidationError):
        InstrumentRecord(
            instrument=instrument,
            active=True,
            source_provider="provider-a",
            lot_size=lot_size,
            tick_size=tick_size,
        )


def test_instrument_record_normalizes_underlying_and_round_trips() -> None:
    instrument = InstrumentKey(
        symbol="RELIANCE",
        exchange="NSE",
        segment=MarketSegment.NSE_FNO,
        instrument_type=InstrumentType.CALL_OPTION,
        expiry=date(2026, 9, 24),
        strike=3000,
        option_type=OptionType.CE,
    )
    record = InstrumentRecord(
        instrument=instrument,
        active=True,
        source_provider=" Provider A ",
        company_name="Reliance Industries",
        lot_size=75,
        tick_size=0.05,
        underlying_symbol=" reliance ",
    )

    restored = InstrumentRecord.model_validate_json(record.model_dump_json())

    assert restored == record
    assert record.underlying_symbol == "RELIANCE"
    assert record.source_provider == "provider a"
