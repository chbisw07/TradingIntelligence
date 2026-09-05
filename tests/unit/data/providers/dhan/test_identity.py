"""Identity-integrity tests for Dhan diagnostic utilities."""

from pathlib import Path

import pytest

from tiaf.data import InstrumentType, MarketSegment
from tiaf.data.providers.dhan import (
    DhanIdentityMismatchError,
    resolve_dhan_diagnostic_instrument,
)
from tiaf.data.resolution import InstrumentResolutionError

from ._instrument_master_support import resolver_at


@pytest.mark.parametrize(
    "symbol,expected_id",
    [("RELIANCE", "2885"), ("HDFCBANK", "1333")],
)
def test_symbol_only_identity_uses_resolved_fixture_id(
    tmp_path: Path,
    symbol: str,
    expected_id: str,
) -> None:
    resolver, _ = resolver_at(tmp_path)
    instrument = resolve_dhan_diagnostic_instrument(
        symbol=symbol,
        security_id=None,
        resolver=resolver,
    )
    assert instrument.symbol == symbol
    assert instrument.provider_instrument_id == expected_id


def test_matching_symbol_and_security_id_succeeds(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    instrument = resolve_dhan_diagnostic_instrument(
        symbol="RELIANCE",
        security_id="2885",
        exchange="NSE",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
        resolver=resolver,
    )
    assert instrument.provider_instrument_id == "2885"


def test_mismatching_symbol_and_security_id_refuses_with_secret_safe_detail(
    tmp_path: Path,
) -> None:
    resolver, _ = resolver_at(tmp_path)
    with pytest.raises(DhanIdentityMismatchError) as captured:
        resolve_dhan_diagnostic_instrument(
            symbol="RELIANCE",
            security_id="1333",
            resolver=resolver,
        )
    message = str(captured.value)
    assert "requested symbol : RELIANCE" in message
    assert "resolved Dhan ID : 2885" in message
    assert "supplied Dhan ID : 1333" in message
    assert "No provider request was made" in message
    assert "access-token" not in message.casefold()


def test_provider_id_only_uses_master_identity_instead_of_fabricated_label(
    tmp_path: Path,
) -> None:
    resolver, _ = resolver_at(tmp_path)
    instrument = resolve_dhan_diagnostic_instrument(
        symbol=None,
        security_id="1333",
        resolver=resolver,
    )
    assert instrument.symbol == "HDFCBANK"
    assert instrument.provider_instrument_id == "1333"


def test_identity_requires_symbol_or_provider_id(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    with pytest.raises(InstrumentResolutionError, match="symbol or security ID"):
        resolve_dhan_diagnostic_instrument(
            symbol=None,
            security_id=None,
            resolver=resolver,
        )
