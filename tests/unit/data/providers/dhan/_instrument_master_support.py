"""Small Dhan detailed-master fixture for deterministic resolver tests."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tiaf.data.providers.dhan import DhanInstrumentMaster, DhanInstrumentResolver
from tiaf.data.resolution import ResolutionPolicy

FIXED_MASTER_TIME = datetime(2026, 9, 5, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
MASTER_HEADER = (
    "EXCH_ID,SEGMENT,SECURITY_ID,INSTRUMENT,UNDERLYING_SECURITY_ID,"
    "UNDERLYING_SYMBOL,SYMBOL_NAME,TRADING_SYMBOL,DISPLAY_NAME,INSTRUMENT_TYPE,"
    "LOT_SIZE,SM_EXPIRY_DATE,STRIKE_PRICE,OPTION_TYPE,TICK_SIZE,ACTIVE"
)
MASTER_ROWS = (
    "NSE,E,2885,EQUITY,,,RELIANCE,RELIANCE,Reliance Industries,EQ,1,,, ,0.05,Y",
    "BSE,E,500325,EQUITY,,,RELIANCE,RELIANCE-BE,Reliance Industries,EQ,1,,,,0.05,Y",
    "NSE,E,1333,EQUITY,,,HDFCBANK,HDFCBANK,HDFC Bank,EQ,1,,,,0.05,Y",
    "BSE,E,500180,EQUITY,,,HDFCBANK,HDFCBANK-BE,HDFC Bank,EQ,1,,,,0.05,Y",
    "NSE,I,13,INDEX,,,NIFTY,NIFTY 50,Nifty 50,INDEX,1,,,,0.05,Y",
    "NSE,E,999,EQUITY,,,OLDCO,OLDCO,Old Company,EQ,1,,,,0.05,N",
    "NSE,E,1000,EQUITY,,,KAYNES,KAYNES,Kaynes Technology,EQ,1,,,,0.05,Y",
    "NSE,D,7001,FUTSTK,2885,RELIANCE,RELIANCE,RELIANCE SEP FUT,Reliance Future,"
    "FUTSTK,250,2026-09-24,,,0.05,Y",
    "NSE,D,7002,FUTSTK,2885,RELIANCE,RELIANCE,RELIANCE OCT FUT,Reliance Future,"
    "FUTSTK,250,2026-10-29,,,0.05,Y",
    "NSE,D,8001,OPTSTK,2885,RELIANCE,RELIANCE,RELIANCE 24 SEP 3000 CE,"
    "Reliance Call,OPTSTK,250,2026-09-24,3000,CE,0.05,Y",
    "NSE,D,8002,OPTSTK,2885,RELIANCE,RELIANCE,RELIANCE 24 SEP 3000 PE,"
    "Reliance Put,OPTSTK,250,2026-09-24,3000,PE,0.05,Y",
    "NSE,D,8003,OPTSTK,2885,RELIANCE,RELIANCE,RELIANCE 24 SEP 3100 CE,"
    "Reliance Call,OPTSTK,250,2026-09-24,3100,CE,0.05,Y",
    "NSE,D,9001,FUTIDX,13,NIFTY,NIFTY,NIFTY SEP FUT,Nifty Future,FUTIDX,"
    "75,2026-09-24,,,0.05,Y",
    "NSE,D,7100,FUTSTK,1333,HDFCBANK,HDFCBANK,HDFCBANK SEP FUT,HDFC Future,"
    "FUTSTK,550,2026-09-24,,,0.05,Y",
    "BSE,D,97001,FUTSTK,500325,RELIANCE,RELIANCE,RELIANCE BSE SEP FUT,"
    "Reliance BSE Future,FUTSTK,250,2026-09-24,,,0.05,Y",
    "XYZ,Q,42,ALIEN,,,MYSTERY,MYSTERY,Mystery,ALIEN,1,,,,0.01,Y",
)
MASTER_CSV = (MASTER_HEADER + "\n" + "\n".join(MASTER_ROWS) + "\n").encode()


class RecordingDownloader:
    """Return a fixed body and record public download attempts."""

    def __init__(self, body: bytes = MASTER_CSV, *, error: Exception | None = None) -> None:
        self.body = body
        self.error = error
        self.calls: list[str] = []

    def download(self, url: str) -> bytes:
        self.calls.append(url)
        if self.error is not None:
            raise self.error
        return self.body


def resolver_at(
    tmp_path: Path,
    *,
    body: bytes = MASTER_CSV,
    policy: ResolutionPolicy | None = None,
) -> tuple[DhanInstrumentResolver, RecordingDownloader]:
    """Build a resolver whose entire master source is local and deterministic."""
    downloader = RecordingDownloader(body)
    master = DhanInstrumentMaster(
        tmp_path / "dhan.csv",
        downloader=downloader,
        now=lambda: FIXED_MASTER_TIME,
    )
    return DhanInstrumentResolver(master, policy=policy), downloader
