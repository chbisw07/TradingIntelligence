"""Explicit TIAF-to-Dhan market identity mappings."""

from enum import StrEnum

from tiaf.data import InstrumentType, MarketSegment, ProviderCapability
from tiaf.data.errors import UnsupportedCapabilityError


class DhanInstrumentType(StrEnum):
    """Dhan historical API instrument values used by this adapter."""

    EQUITY = "EQUITY"
    INDEX = "INDEX"
    FUTIDX = "FUTIDX"
    FUTSTK = "FUTSTK"
    OPTIDX = "OPTIDX"
    OPTSTK = "OPTSTK"


_DHAN_SEGMENTS = {
    MarketSegment.NSE_EQUITY: "NSE_EQ",
    MarketSegment.NSE_FNO: "NSE_FNO",
    MarketSegment.NSE_INDEX: "IDX_I",
    MarketSegment.BSE_EQUITY: "BSE_EQ",
    MarketSegment.BSE_FNO: "BSE_FNO",
    MarketSegment.BSE_INDEX: "IDX_I",
}


def to_dhan_segment(segment: MarketSegment) -> str:
    """Map a supported TIAF segment to Dhan's exchangeSegment value."""
    try:
        return _DHAN_SEGMENTS[segment]
    except KeyError as exc:
        raise UnsupportedCapabilityError(
            ProviderCapability.QUOTES,
            provider="DHAN",
            detail=f"Dhan does not support TIAF market segment {segment.value}",
        ) from exc


def to_dhan_instrument_type(
    instrument_type: InstrumentType,
    *,
    derivative_type: DhanInstrumentType | None = None,
) -> DhanInstrumentType:
    """Map identity to Dhan terminology without guessing index-versus-stock derivatives."""
    if instrument_type is InstrumentType.EQUITY:
        return DhanInstrumentType.EQUITY
    if instrument_type is InstrumentType.INDEX:
        return DhanInstrumentType.INDEX

    valid_derivative_types: set[DhanInstrumentType]
    if instrument_type is InstrumentType.FUTURE:
        valid_derivative_types = {DhanInstrumentType.FUTIDX, DhanInstrumentType.FUTSTK}
    elif instrument_type in {InstrumentType.CALL_OPTION, InstrumentType.PUT_OPTION}:
        valid_derivative_types = {DhanInstrumentType.OPTIDX, DhanInstrumentType.OPTSTK}
    else:
        valid_derivative_types = set()

    if derivative_type in valid_derivative_types:
        return derivative_type
    raise UnsupportedCapabilityError(
        ProviderCapability.HISTORICAL_OHLCV,
        provider="DHAN",
        detail=(
            f"Dhan historical instrument mapping for {instrument_type.value} "
            "requires an explicit Dhan derivative type"
        ),
    )
