"""Dhan instrument-master cache and parsing tests."""

from datetime import datetime
from pathlib import Path

import pytest

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data import InstrumentType, MarketSegment
from tiaf.data.providers.dhan import (
    DHAN_DETAILED_INSTRUMENT_MASTER_URL,
    DhanInstrumentMaster,
)
from tiaf.data.resolution import InstrumentMasterParseError, InstrumentMasterUnavailableError

from ._instrument_master_support import FIXED_MASTER_TIME, MASTER_CSV, RecordingDownloader


def _master(path: Path, downloader: RecordingDownloader) -> DhanInstrumentMaster:
    return DhanInstrumentMaster(path, downloader=downloader, now=lambda: FIXED_MASTER_TIME)


def test_missing_cache_downloads_public_detailed_master_and_writes_cache(tmp_path: Path) -> None:
    downloader = RecordingDownloader()
    path = tmp_path / "nested" / "dhan.csv"
    snapshot = _master(path, downloader).load()
    assert downloader.calls == [DHAN_DETAILED_INSTRUMENT_MASTER_URL]
    assert path.read_bytes() == MASTER_CSV
    assert len(snapshot.records) == 16


def test_existing_cache_is_used_without_download(tmp_path: Path) -> None:
    path = tmp_path / "dhan.csv"
    path.write_bytes(MASTER_CSV)
    downloader = RecordingDownloader(error=AssertionError("must not download"))
    snapshot = _master(path, downloader).load()
    assert len(snapshot.records) == 16
    assert downloader.calls == []


def test_explicit_refresh_downloads_even_when_cache_exists(tmp_path: Path) -> None:
    path = tmp_path / "dhan.csv"
    path.write_bytes(MASTER_CSV)
    downloader = RecordingDownloader()
    _master(path, downloader).load(refresh=True)
    assert len(downloader.calls) == 1


def test_repeated_load_parses_and_downloads_once(tmp_path: Path) -> None:
    downloader = RecordingDownloader()
    master = _master(tmp_path / "dhan.csv", downloader)
    assert master.load() is master.load()
    assert len(downloader.calls) == 1


@pytest.mark.parametrize(
    "body,match",
    [
        (b"", "empty"),
        (b"not,a,master\n1,2,3\n", "missing required columns"),
        (b"\xff\xfe", "not UTF-8"),
        (b"EXCH_ID,SEGMENT,SECURITY_ID,INSTRUMENT,SYMBOL_NAME\nNSE,E,,EQUITY,R\n", "lacks"),
        (
            b"EXCH_ID,SEGMENT,SECURITY_ID,INSTRUMENT,SYMBOL_NAME,SM_EXPIRY_DATE\n"
            b"NSE,D,1,FUTSTK,R,bad-date\n",
            "invalid expiry",
        ),
        (
            b"EXCH_ID,SEGMENT,SECURITY_ID,INSTRUMENT,SYMBOL_NAME,STRIKE_PRICE,OPTION_TYPE\n"
            b"NSE,D,1,OPTSTK,R,abc,CE\n",
            "invalid strike",
        ),
    ],
)
def test_malformed_master_fails_clearly(tmp_path: Path, body: bytes, match: str) -> None:
    master = _master(tmp_path / "bad.csv", RecordingDownloader(body))
    error = InstrumentMasterUnavailableError if body == b"" else InstrumentMasterParseError
    with pytest.raises(error, match=match):
        master.load()


def test_download_failure_is_typed(tmp_path: Path) -> None:
    master = _master(
        tmp_path / "dhan.csv",
        RecordingDownloader(error=OSError("offline")),
    )
    with pytest.raises(InstrumentMasterUnavailableError, match="offline"):
        master.load()


def test_parses_provider_neutral_equity_option_index_and_unknown(tmp_path: Path) -> None:
    records = _master(tmp_path / "dhan.csv", RecordingDownloader()).load().records
    by_id = {record.instrument.provider_instrument_id: record for record in records}
    assert by_id["2885"].instrument.segment is MarketSegment.NSE_EQUITY
    assert by_id["13"].instrument.instrument_type is InstrumentType.INDEX
    assert by_id["8001"].instrument.instrument_type is InstrumentType.CALL_OPTION
    assert by_id["42"].instrument.instrument_type is InstrumentType.UNKNOWN
    assert by_id["42"].instrument.segment is MarketSegment.UNKNOWN
    assert by_id["42"].metadata["dhan_instrument"] == "ALIEN"


def test_inactive_flag_is_preserved(tmp_path: Path) -> None:
    records = _master(tmp_path / "dhan.csv", RecordingDownloader()).load().records
    old = next(record for record in records if record.instrument.provider_instrument_id == "999")
    assert old.active is False


def test_observed_timestamp_is_timezone_aware_ist(tmp_path: Path) -> None:
    observed = _master(tmp_path / "dhan.csv", RecordingDownloader()).load().observed_at
    assert observed.tzinfo == TIAF_TIMEZONE


def test_naive_injected_clock_is_rejected(tmp_path: Path) -> None:
    master = DhanInstrumentMaster(
        tmp_path / "dhan.csv",
        downloader=RecordingDownloader(),
        now=lambda: datetime(2026, 9, 5),
    )
    with pytest.raises(InstrumentMasterUnavailableError, match="naive"):
        master.load()
