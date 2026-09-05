"""Tests for Dhan configuration secrecy and explicit identity mappings."""

from pathlib import Path

import pytest

from tiaf.config import Settings
from tiaf.data import InstrumentType, MarketSegment, ProviderAuthError, UnsupportedCapabilityError
from tiaf.data.providers.dhan import (
    DhanInstrumentType,
    DhanMarketDataProvider,
    to_dhan_instrument_type,
    to_dhan_segment,
)

from ._support import RecordingTransport, dhan_config


def test_provider_requires_credentials_when_instantiated() -> None:
    settings = Settings.model_construct(
        env="test",
        log_level="INFO",
        data_dir=Path("data"),
        dhan_client_id=None,
        dhan_access_token=None,
        dhan_base_url="https://api.dhan.co/v2",
    )
    transport = RecordingTransport(lambda path, payload: {})

    with pytest.raises(ProviderAuthError, match="credentials are required"):
        DhanMarketDataProvider(settings=settings, transport=transport)


def test_credentials_are_absent_from_config_and_provider_repr() -> None:
    token = "highly-sensitive-test-token"
    config = dhan_config(token)
    provider = DhanMarketDataProvider(
        config,
        transport=RecordingTransport(lambda path, payload: {}),
    )

    assert token not in repr(config)
    assert token not in str(config)
    assert token not in repr(provider)


@pytest.mark.parametrize(
    ("segment", "expected"),
    [
        (MarketSegment.NSE_EQUITY, "NSE_EQ"),
        (MarketSegment.NSE_FNO, "NSE_FNO"),
        (MarketSegment.NSE_INDEX, "IDX_I"),
        (MarketSegment.BSE_EQUITY, "BSE_EQ"),
        (MarketSegment.BSE_FNO, "BSE_FNO"),
        (MarketSegment.BSE_INDEX, "IDX_I"),
    ],
)
def test_segment_mapping(segment: MarketSegment, expected: str) -> None:
    assert to_dhan_segment(segment) == expected


def test_unknown_segment_is_not_guessed() -> None:
    with pytest.raises(UnsupportedCapabilityError):
        to_dhan_segment(MarketSegment.UNKNOWN)


@pytest.mark.parametrize(
    ("instrument_type", "derivative_type", "expected"),
    [
        (InstrumentType.EQUITY, None, DhanInstrumentType.EQUITY),
        (InstrumentType.INDEX, None, DhanInstrumentType.INDEX),
        (InstrumentType.FUTURE, DhanInstrumentType.FUTIDX, DhanInstrumentType.FUTIDX),
        (InstrumentType.FUTURE, DhanInstrumentType.FUTSTK, DhanInstrumentType.FUTSTK),
        (
            InstrumentType.CALL_OPTION,
            DhanInstrumentType.OPTIDX,
            DhanInstrumentType.OPTIDX,
        ),
        (
            InstrumentType.PUT_OPTION,
            DhanInstrumentType.OPTSTK,
            DhanInstrumentType.OPTSTK,
        ),
    ],
)
def test_instrument_type_mapping(
    instrument_type: InstrumentType,
    derivative_type: DhanInstrumentType | None,
    expected: DhanInstrumentType,
) -> None:
    assert (
        to_dhan_instrument_type(instrument_type, derivative_type=derivative_type) is expected
    )


def test_ambiguous_derivative_instrument_type_is_not_guessed() -> None:
    with pytest.raises(UnsupportedCapabilityError, match="requires an explicit"):
        to_dhan_instrument_type(InstrumentType.FUTURE)
