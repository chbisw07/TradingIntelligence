"""Dhan detailed instrument-master ingestion and deterministic resolution."""

from __future__ import annotations

import csv
import io
import os
import tempfile
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Protocol

import httpx

from tiaf.config import Settings
from tiaf.contracts import DataQuality, OptionType
from tiaf.contracts.common import TIAF_TIMEZONE, Metadata
from tiaf.data.enums import InstrumentType, MarketSegment
from tiaf.data.models import InstrumentKey, InstrumentRecord
from tiaf.data.normalization import normalize_exchange
from tiaf.data.resolution import (
    InstrumentMasterParseError,
    InstrumentMasterUnavailableError,
    InstrumentQuery,
    ResolutionKind,
    ResolutionPolicy,
    ResolutionResult,
    ResolvedInstrument,
)

DHAN_DETAILED_INSTRUMENT_MASTER_URL = (
    "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
)
DHAN_PROVIDER_NAME = "dhan"


class InstrumentMasterDownloader(Protocol):
    """Minimal injectable boundary for the public, credential-free CSV."""

    def download(self, url: str) -> bytes:
        """Return the complete resource body or raise an I/O-style error."""
        ...


class HttpxInstrumentMasterDownloader:
    """Download Dhan's public master without credentials or provider transport."""

    def __init__(self, *, timeout_seconds: float = 30.0) -> None:
        self._timeout_seconds = timeout_seconds

    def download(self, url: str) -> bytes:
        """Fetch one public CSV and require a successful HTTP response."""
        response = httpx.get(url, timeout=self._timeout_seconds, follow_redirects=True)
        response.raise_for_status()
        return response.content


@dataclass(frozen=True, slots=True)
class DhanInstrumentMasterSnapshot:
    """One parsed master observation retained in memory by a resolver."""

    records: tuple[InstrumentRecord, ...]
    observed_at: datetime


_HEADERS: dict[str, tuple[str, ...]] = {
    "exchange": ("EXCH_ID", "SEM_EXM_EXCH_ID"),
    "segment": ("SEGMENT", "SEM_SEGMENT"),
    "security_id": ("SECURITY_ID", "SEM_SMST_SECURITY_ID"),
    "isin": ("ISIN",),
    "instrument": ("INSTRUMENT", "SEM_INSTRUMENT_NAME"),
    "underlying_security_id": ("UNDERLYING_SECURITY_ID",),
    "underlying_symbol": ("UNDERLYING_SYMBOL",),
    "symbol": ("SYMBOL_NAME", "SM_SYMBOL_NAME"),
    "trading_symbol": ("TRADING_SYMBOL", "SEM_TRADING_SYMBOL"),
    "display_name": ("DISPLAY_NAME", "SEM_CUSTOM_SYMBOL"),
    "instrument_type": ("INSTRUMENT_TYPE", "SEM_EXCH_INSTRUMENT_TYPE"),
    "lot_size": ("LOT_SIZE", "SEM_LOT_UNITS"),
    "expiry": ("SM_EXPIRY_DATE", "SEM_EXPIRY_DATE"),
    "strike": ("STRIKE_PRICE", "SEM_STRIKE_PRICE"),
    "option_type": ("OPTION_TYPE", "SEM_OPTION_TYPE"),
    "tick_size": ("TICK_SIZE", "SEM_TICK_SIZE"),
    "active": ("ACTIVE", "IS_ACTIVE", "SEM_ACTIVE_FLAG"),
    "buy_sell_indicator": ("BUY_SELL_INDICATOR",),
}
_REQUIRED_HEADERS = {"exchange", "segment", "security_id", "instrument", "symbol"}
_TRUE_VALUES = {"1", "ACTIVE", "TRUE", "Y", "YES"}
_FALSE_VALUES = {"0", "FALSE", "INACTIVE", "N", "NO"}


def _clean(value: str | None) -> str:
    return "" if value is None else value.strip()


def _parse_date(value: str, *, row_number: int) -> date | None:
    if not value:
        return None
    candidate = value[:10]
    for pattern in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(candidate, pattern).date()
        except ValueError:
            continue
    raise InstrumentMasterParseError(
        f"Dhan instrument master row {row_number} has invalid expiry {value!r}",
        provider="DHAN",
    )


def _parse_float(value: str, *, field: str, row_number: int) -> float | None:
    if not value:
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise InstrumentMasterParseError(
            f"Dhan instrument master row {row_number} has invalid {field} {value!r}",
            provider="DHAN",
        ) from exc


def _parse_int(value: str, *, field: str, row_number: int) -> int | None:
    number = _parse_float(value, field=field, row_number=row_number)
    if number is None:
        return None
    if not number.is_integer():
        raise InstrumentMasterParseError(
            f"Dhan instrument master row {row_number} has non-integral {field} {value!r}",
            provider="DHAN",
        )
    return int(number)


def _identity_mapping(
    exchange_value: str,
    segment_value: str,
    instrument_value: str,
    option_value: str,
) -> tuple[str, MarketSegment, InstrumentType, OptionType | None]:
    exchange = exchange_value.upper()
    raw_segment = segment_value.upper()
    instrument = instrument_value.upper()
    option = option_value.upper()

    if instrument == "EQUITY":
        segment = _cash_segment(exchange) if raw_segment == "E" else MarketSegment.UNKNOWN
        return exchange, segment, InstrumentType.EQUITY, None
    if instrument == "INDEX":
        segment = (
            _index_segment(exchange) if raw_segment in {"E", "I"} else MarketSegment.UNKNOWN
        )
        return exchange, segment, InstrumentType.INDEX, None
    if instrument in {"FUTIDX", "FUTSTK"}:
        segment = _fno_segment(exchange) if raw_segment == "D" else MarketSegment.UNKNOWN
        return exchange, segment, InstrumentType.FUTURE, None
    if instrument in {"OPTIDX", "OPTSTK"} and option == "CE":
        segment = _fno_segment(exchange) if raw_segment == "D" else MarketSegment.UNKNOWN
        return exchange, segment, InstrumentType.CALL_OPTION, OptionType.CE
    if instrument in {"OPTIDX", "OPTSTK"} and option == "PE":
        segment = _fno_segment(exchange) if raw_segment == "D" else MarketSegment.UNKNOWN
        return exchange, segment, InstrumentType.PUT_OPTION, OptionType.PE
    return exchange or "UNKNOWN", MarketSegment.UNKNOWN, InstrumentType.UNKNOWN, None


def _cash_segment(exchange: str) -> MarketSegment:
    return {
        "NSE": MarketSegment.NSE_EQUITY,
        "BSE": MarketSegment.BSE_EQUITY,
    }.get(exchange, MarketSegment.UNKNOWN)


def _index_segment(exchange: str) -> MarketSegment:
    return {
        "NSE": MarketSegment.NSE_INDEX,
        "BSE": MarketSegment.BSE_INDEX,
    }.get(exchange, MarketSegment.UNKNOWN)


def _fno_segment(exchange: str) -> MarketSegment:
    return {
        "NSE": MarketSegment.NSE_FNO,
        "BSE": MarketSegment.BSE_FNO,
    }.get(exchange, MarketSegment.UNKNOWN)


class DhanInstrumentMaster:
    """Load Dhan's detailed master from a durable local cache exactly once."""

    def __init__(
        self,
        cache_path: Path | None = None,
        *,
        downloader: InstrumentMasterDownloader | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        settings = Settings()
        self.cache_path = cache_path or (
            settings.data_dir / "instrument_master" / "dhan" / "api-scrip-master-detailed.csv"
        )
        self._downloader = downloader or HttpxInstrumentMasterDownloader()
        self._now = now or (lambda: datetime.now(TIAF_TIMEZONE))
        self._snapshot: DhanInstrumentMasterSnapshot | None = None

    def load(self, *, refresh: bool = False) -> DhanInstrumentMasterSnapshot:
        """Use cache when present; download only if absent or explicitly refreshed."""
        if self._snapshot is not None and not refresh:
            return self._snapshot
        if refresh or not self.cache_path.exists():
            body = self._download()
            self._atomic_write(body)
            observed_at = self._aware_now()
        else:
            try:
                body = self.cache_path.read_bytes()
                observed_at = datetime.fromtimestamp(
                    self.cache_path.stat().st_mtime,
                    tz=TIAF_TIMEZONE,
                )
            except OSError as exc:
                raise InstrumentMasterUnavailableError(
                    f"could not read cached Dhan instrument master: {exc}",
                    provider="DHAN",
                ) from exc
        records = self._parse(body, observed_at=observed_at)
        self._snapshot = DhanInstrumentMasterSnapshot(records=records, observed_at=observed_at)
        return self._snapshot

    def _aware_now(self) -> datetime:
        value = self._now()
        if value.tzinfo is None or value.utcoffset() is None:
            raise InstrumentMasterUnavailableError(
                "instrument-master clock returned a naive datetime",
                provider="DHAN",
            )
        return value.astimezone(TIAF_TIMEZONE)

    def _download(self) -> bytes:
        try:
            body = self._downloader.download(DHAN_DETAILED_INSTRUMENT_MASTER_URL)
        except Exception as exc:
            raise InstrumentMasterUnavailableError(
                f"could not download Dhan instrument master: {exc}",
                provider="DHAN",
            ) from exc
        if not body:
            raise InstrumentMasterUnavailableError(
                "Dhan instrument master download was empty",
                provider="DHAN",
            )
        return body

    def _atomic_write(self, body: bytes) -> None:
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                dir=self.cache_path.parent,
                prefix=f".{self.cache_path.name}.",
                delete=False,
            ) as handle:
                handle.write(body)
                temporary_path = Path(handle.name)
            os.replace(temporary_path, self.cache_path)
        except OSError as exc:
            if "temporary_path" in locals():
                temporary_path.unlink(missing_ok=True)
            raise InstrumentMasterUnavailableError(
                f"could not cache Dhan instrument master atomically: {exc}",
                provider="DHAN",
            ) from exc

    @staticmethod
    def _parse(body: bytes, *, observed_at: datetime) -> tuple[InstrumentRecord, ...]:
        try:
            text = body.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise InstrumentMasterParseError(
                "Dhan instrument master is not UTF-8 CSV",
                provider="DHAN",
            ) from exc

        reader = csv.DictReader(io.StringIO(text))
        if reader.fieldnames is None:
            raise InstrumentMasterParseError(
                "Dhan instrument master has no header row",
                provider="DHAN",
            )
        available = {name.strip().upper(): name for name in reader.fieldnames}
        headers: dict[str, str] = {}
        for logical, aliases in _HEADERS.items():
            match = next((available[alias] for alias in aliases if alias in available), None)
            if match is not None:
                headers[logical] = match
        missing = sorted(_REQUIRED_HEADERS - headers.keys())
        if missing:
            raise InstrumentMasterParseError(
                f"Dhan instrument master is missing required columns: {', '.join(missing)}",
                provider="DHAN",
            )

        def value(row: dict[str, str | None], logical: str) -> str:
            header = headers.get(logical)
            return _clean(row.get(header)) if header is not None else ""

        records: list[InstrumentRecord] = []
        for row_number, row in enumerate(reader, start=2):
            security_id = value(row, "security_id")
            raw_symbol = value(row, "symbol")
            if not security_id or not raw_symbol:
                raise InstrumentMasterParseError(
                    f"Dhan instrument master row {row_number} lacks security ID or symbol",
                    provider="DHAN",
                )
            raw_instrument = value(row, "instrument")
            raw_option = value(row, "option_type")
            exchange, segment, instrument_type, option_type = _identity_mapping(
                value(row, "exchange"),
                value(row, "segment"),
                raw_instrument,
                raw_option,
            )
            expiry = _parse_date(value(row, "expiry"), row_number=row_number)
            strike = _parse_float(value(row, "strike"), field="strike", row_number=row_number)
            if instrument_type not in {
                InstrumentType.CALL_OPTION,
                InstrumentType.PUT_OPTION,
            }:
                strike = None
            elif strike is None or strike <= 0:
                raise InstrumentMasterParseError(
                    f"Dhan instrument master row {row_number} has no positive option strike",
                    provider="DHAN",
                )
            lot_size = _parse_int(value(row, "lot_size"), field="lot size", row_number=row_number)
            tick_size = _parse_float(
                value(row, "tick_size"), field="tick size", row_number=row_number
            )
            if lot_size is not None and lot_size <= 0:
                lot_size = None
            if tick_size is not None and tick_size <= 0:
                tick_size = None

            underlying_symbol = value(row, "underlying_symbol") or None
            canonical_symbol = underlying_symbol or raw_symbol
            trading_symbol = (
                value(row, "trading_symbol") or raw_symbol or value(row, "display_name") or None
            )
            active_value = value(row, "active").upper()
            if active_value in _TRUE_VALUES:
                active = True
            elif active_value in _FALSE_VALUES:
                active = False
            elif expiry is not None:
                active = expiry >= observed_at.date()
            else:
                active = True

            metadata: Metadata = {
                "dhan_instrument": raw_instrument,
                "dhan_instrument_type": value(row, "instrument_type"),
                "dhan_segment": value(row, "segment"),
                "active": active,
            }
            isin = value(row, "isin")
            if isin and isin.upper() != "NA":
                metadata["isin"] = isin
            buy_sell_indicator = value(row, "buy_sell_indicator").upper()
            if buy_sell_indicator:
                metadata["buy_sell_indicator"] = buy_sell_indicator
            metadata["tradable"] = active and (
                not buy_sell_indicator or buy_sell_indicator == "A"
            )
            metadata["provider_test_instrument"] = isin.upper().startswith("DUMMYSAN")
            underlying_id = value(row, "underlying_security_id")
            if underlying_id:
                metadata["underlying_security_id"] = underlying_id

            instrument = InstrumentKey(
                symbol=canonical_symbol,
                exchange=exchange,
                segment=segment,
                instrument_type=instrument_type,
                expiry=expiry,
                strike=strike,
                option_type=option_type,
                trading_symbol=trading_symbol,
                provider_instrument_id=security_id,
            )
            records.append(
                InstrumentRecord(
                    instrument=instrument,
                    active=active,
                    source_provider=DHAN_PROVIDER_NAME,
                    company_name=value(row, "display_name") or None,
                    lot_size=lot_size,
                    tick_size=tick_size,
                    underlying_symbol=underlying_symbol,
                    expiry=expiry,
                    strike=strike,
                    option_type=option_type,
                    metadata=metadata,
                )
            )
        if not records:
            raise InstrumentMasterParseError(
                "Dhan instrument master contains no records",
                provider="DHAN",
            )
        return tuple(records)


class DhanInstrumentResolver:
    """Indexed exact resolver over one locally cached Dhan master observation."""

    def __init__(
        self,
        master: DhanInstrumentMaster | None = None,
        *,
        policy: ResolutionPolicy | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._master = master or DhanInstrumentMaster()
        if policy is None:
            application_settings = settings or Settings()
            policy = ResolutionPolicy(
                primary_exchange=application_settings.primary_exchange,
                primary_fno_exchange=application_settings.primary_fno_exchange,
            )
        self.policy = policy
        self._snapshot: DhanInstrumentMasterSnapshot | None = None
        self._by_id: dict[str, tuple[InstrumentRecord, ...]] = {}
        self._by_symbol: dict[str, tuple[InstrumentRecord, ...]] = {}
        self._by_trading_symbol: dict[str, tuple[InstrumentRecord, ...]] = {}

    def refresh(self) -> None:
        """Explicitly refresh the cache and rebuild in-memory indexes."""
        self._build_indexes(self._master.load(refresh=True))

    def _ensure_indexes(self) -> DhanInstrumentMasterSnapshot:
        if self._snapshot is None:
            self._build_indexes(self._master.load())
        assert self._snapshot is not None
        return self._snapshot

    def _build_indexes(self, snapshot: DhanInstrumentMasterSnapshot) -> None:
        by_id: defaultdict[str, list[InstrumentRecord]] = defaultdict(list)
        by_symbol: defaultdict[str, list[InstrumentRecord]] = defaultdict(list)
        by_trading: defaultdict[str, list[InstrumentRecord]] = defaultdict(list)
        for record in snapshot.records:
            instrument = record.instrument
            if instrument.provider_instrument_id is not None:
                by_id[instrument.provider_instrument_id].append(record)
            by_symbol[instrument.symbol].append(record)
            if instrument.trading_symbol is not None:
                by_trading[instrument.trading_symbol].append(record)
        self._by_id = {key: tuple(value) for key, value in by_id.items()}
        self._by_symbol = {key: tuple(value) for key, value in by_symbol.items()}
        self._by_trading_symbol = {key: tuple(value) for key, value in by_trading.items()}
        self._snapshot = snapshot

    def search(self, query: InstrumentQuery) -> tuple[ResolvedInstrument, ...]:
        """Return all active exact matches, except exact IDs may reveal inactive rows."""
        snapshot = self._ensure_indexes()
        if query.provider is not None and query.provider != DHAN_PROVIDER_NAME:
            return ()

        if query.provider_instrument_id is not None:
            records = self._by_id.get(query.provider_instrument_id, ())
            kind = ResolutionKind.PROVIDER_ID
            include_inactive = True
        elif query.trading_symbol is not None:
            records = self._by_trading_symbol.get(query.trading_symbol, ())
            kind = ResolutionKind.TRADING_SYMBOL
            include_inactive = False
        else:
            assert query.symbol is not None
            records = self._by_symbol.get(query.symbol, ())
            kind = self._symbol_resolution_kind(query)
            include_inactive = False

        filtered = tuple(
            record
            for record in records
            if (include_inactive or record.active) and self._matches(record, query)
        )
        sorted_records = sorted(filtered, key=self._sort_key)
        return tuple(
            self._resolved(record, snapshot.observed_at, kind) for record in sorted_records
        )

    def resolve(self, query: InstrumentQuery) -> ResolutionResult:
        """Represent unique, ambiguous, and missing results without guessing."""
        snapshot = self._ensure_indexes()
        matches = self.search(query)
        result_metadata: Metadata = {
            "policy_applied": False,
            "preferred_exchange": self.policy.primary_exchange,
        }
        selected = self._select_by_policy(query, matches)
        if selected is not None:
            result_metadata.update(
                {
                    "policy_applied": True,
                    "candidate_count_before_policy": len(matches),
                }
            )
            selected_metadata = dict(selected.metadata)
            selected_metadata.update(result_metadata)
            selected = selected.model_copy(
                update={
                    "resolution_kind": ResolutionKind.POLICY_SELECTED,
                    "metadata": selected_metadata,
                }
            )
            matches = (selected,)
        return ResolutionResult(
            query=query,
            matches=matches,
            resolved=matches[0] if len(matches) == 1 else None,
            ambiguous=len(matches) > 1,
            not_found=not matches,
            source_provider=DHAN_PROVIDER_NAME,
            observed_at=snapshot.observed_at,
            metadata=result_metadata,
        )

    def resolve_many(self, queries: tuple[InstrumentQuery, ...]) -> tuple[ResolutionResult, ...]:
        """Resolve each query independently and preserve its input position."""
        return tuple(self.resolve(query) for query in queries)

    def get_fno_underlyings(self, *, exchange: str | None = None) -> tuple[ResolvedInstrument, ...]:
        """List unique active F&O underlyings for one explicit or configured scope."""
        snapshot = self._ensure_indexes()
        selected_exchange = normalize_exchange(exchange or self.policy.primary_fno_exchange)
        candidates: defaultdict[str, dict[str, InstrumentRecord]] = defaultdict(dict)
        derivative_types = {
            InstrumentType.FUTURE,
            InstrumentType.CALL_OPTION,
            InstrumentType.PUT_OPTION,
        }
        for derivative in snapshot.records:
            if (
                not derivative.active
                or derivative.metadata.get("tradable") is False
                or derivative.instrument.instrument_type not in derivative_types
                or derivative.instrument.exchange != selected_exchange
            ):
                continue
            underlying_id = derivative.metadata.get("underlying_security_id")
            underlying_records: list[InstrumentRecord] = []
            if isinstance(underlying_id, str):
                underlying_records.extend(self._by_id.get(underlying_id, ()))
            elif derivative.underlying_symbol is not None:
                underlying_records.extend(
                    self._by_symbol.get(derivative.underlying_symbol, ())
                )
            for underlying in underlying_records:
                if (
                    not underlying.active
                    or underlying.metadata.get("tradable") is False
                    or underlying.metadata.get("provider_test_instrument") is True
                    or underlying.instrument.instrument_type
                    not in {
                        InstrumentType.EQUITY,
                        InstrumentType.INDEX,
                    }
                ):
                    continue
                instrument = underlying.instrument
                if instrument.exchange != selected_exchange:
                    continue
                identity = instrument.provider_instrument_id or ""
                candidates[instrument.symbol][identity] = underlying
        unique_records = [
            next(iter(records.values()))
            for records in candidates.values()
            if len(records) == 1
        ]
        ordered = sorted(unique_records, key=self._sort_key)
        resolved: list[ResolvedInstrument] = []
        for record in ordered:
            item = self._resolved(record, snapshot.observed_at, ResolutionKind.PROVIDER_ID)
            metadata = dict(item.metadata)
            metadata["fno_exchange"] = selected_exchange
            resolved.append(item.model_copy(update={"metadata": metadata}))
        return tuple(resolved)

    def _select_by_policy(
        self,
        query: InstrumentQuery,
        matches: tuple[ResolvedInstrument, ...],
    ) -> ResolvedInstrument | None:
        """Select only one primary cash/index listing when query scope is open."""
        if (
            len(matches) < 2
            or not self.policy.prefer_primary_cash_listing
            or query.symbol is None
            or query.provider_instrument_id is not None
            or query.trading_symbol is not None
            or query.exchange is not None
            or query.segment is not None
            or query.instrument_type
            not in {None, InstrumentType.EQUITY, InstrumentType.INDEX}
            or query.expiry is not None
            or query.strike is not None
            or query.option_type is not None
        ):
            return None
        preferred = tuple(
            match
            for match in matches
            if match.instrument.exchange == self.policy.primary_exchange
        )
        return preferred[0] if len(preferred) == 1 else None

    @staticmethod
    def _matches(record: InstrumentRecord, query: InstrumentQuery) -> bool:
        instrument = record.instrument
        plain_underlying_query = (
            query.provider_instrument_id is None
            and query.trading_symbol is None
            and query.instrument_type is None
            and query.expiry is None
            and query.strike is None
            and query.option_type is None
            and query.segment
            not in {
                MarketSegment.NSE_FNO,
                MarketSegment.BSE_FNO,
            }
        )
        if plain_underlying_query and instrument.instrument_type not in {
            InstrumentType.EQUITY,
            InstrumentType.INDEX,
        }:
            return False
        filters = (
            query.symbol is None or instrument.symbol == query.symbol,
            query.exchange is None or instrument.exchange == query.exchange,
            query.segment is None or instrument.segment is query.segment,
            query.instrument_type is None or instrument.instrument_type is query.instrument_type,
            query.expiry is None or instrument.expiry == query.expiry,
            query.strike is None or instrument.strike == query.strike,
            query.option_type is None or instrument.option_type is query.option_type,
            query.trading_symbol is None or instrument.trading_symbol == query.trading_symbol,
            query.provider_instrument_id is None
            or instrument.provider_instrument_id == query.provider_instrument_id,
        )
        return all(filters)

    @staticmethod
    def _symbol_resolution_kind(query: InstrumentQuery) -> ResolutionKind:
        if query.expiry is not None or query.strike is not None or query.option_type is not None:
            return ResolutionKind.EXACT
        return ResolutionKind.UNIQUE_NORMALIZED

    @staticmethod
    def _sort_key(record: InstrumentRecord) -> tuple[str, str, str, str, str, float]:
        instrument = record.instrument
        return (
            instrument.symbol,
            instrument.exchange,
            instrument.segment.value,
            instrument.instrument_type.value,
            instrument.expiry.isoformat() if instrument.expiry else "",
            instrument.strike or 0.0,
        )

    @staticmethod
    def _resolved(
        record: InstrumentRecord,
        observed_at: datetime,
        kind: ResolutionKind,
    ) -> ResolvedInstrument:
        instrument = record.instrument
        assert instrument.provider_instrument_id is not None
        return ResolvedInstrument(
            instrument=instrument,
            provider_name=DHAN_PROVIDER_NAME,
            provider_instrument_id=instrument.provider_instrument_id,
            company_name=record.company_name,
            underlying_symbol=record.underlying_symbol,
            lot_size=record.lot_size,
            tick_size=record.tick_size,
            source_record_id=(
                f"dhan:{instrument.segment.value}:{instrument.provider_instrument_id}"
            ),
            source_observed_at=observed_at,
            resolution_kind=kind,
            quality=(
                DataQuality.GOOD
                if record.active
                and instrument.segment is not MarketSegment.UNKNOWN
                and instrument.instrument_type is not InstrumentType.UNKNOWN
                else DataQuality.DEGRADED
            ),
            metadata=dict(record.metadata),
        )
