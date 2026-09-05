"""DhanHQ v2 adapter for normalized quotes and historical OHLCV."""

from collections.abc import Callable, Mapping
from datetime import datetime, timedelta

from tiaf.config import Settings
from tiaf.data import (
    HistoricalSeries,
    InstrumentKey,
    InstrumentNotFoundError,
    InstrumentRecord,
    InstrumentType,
    ProviderCapability,
    QuoteSnapshot,
    UnsupportedCapabilityError,
)
from tiaf.data.normalization import TIAF_TIMEZONE, normalize_datetime_to_ist, normalize_interval
from tiaf.data.providers.dhan.config import DhanConfig
from tiaf.data.providers.dhan.mappings import (
    DhanInstrumentType,
    to_dhan_instrument_type,
    to_dhan_segment,
)
from tiaf.data.providers.dhan.parser import parse_historical_response, parse_quote_response
from tiaf.data.providers.dhan.transport import DhanTransport, HttpxDhanTransport

_QUOTE_BATCH_LIMIT = 1000
_MAX_INTRADAY_RANGE = timedelta(days=90)
_INTRADAY_INTERVALS = {
    "1m": ("1", 1),
    "5m": ("5", 5),
    "15m": ("15", 15),
    "25m": ("25", 25),
    "1h": ("60", 60),
}


def _ist_now() -> datetime:
    """Return an aware receipt timestamp in the canonical TIAF timezone."""
    return datetime.now(TIAF_TIMEZONE)


class DhanMarketDataProvider:
    """Read-only Dhan data adapter satisfying the A1.1 provider protocol."""

    def __init__(
        self,
        config: DhanConfig | None = None,
        *,
        settings: Settings | None = None,
        transport: DhanTransport | None = None,
        clock: Callable[[], datetime] = _ist_now,
        historical_instrument_types: Mapping[str, DhanInstrumentType] | None = None,
    ) -> None:
        self._config = config or DhanConfig.from_settings(settings or Settings())
        self._transport = transport or HttpxDhanTransport(self._config)
        self._clock = clock
        self._historical_instrument_types = dict(historical_instrument_types or {})

    def __repr__(self) -> str:
        """Return a credential-free representation."""
        return "DhanMarketDataProvider(provider='dhan')"

    def provider_name(self) -> str:
        """Return normalized provider attribution."""
        return "dhan"

    def capabilities(self) -> frozenset[ProviderCapability]:
        """Advertise only capabilities implemented in A1.2."""
        return frozenset(
            {
                ProviderCapability.QUOTES,
                ProviderCapability.HISTORICAL_OHLCV,
            }
        )

    def get_quote(self, instrument: InstrumentKey) -> QuoteSnapshot:
        """Retrieve one normalized full quote."""
        return self.get_quotes((instrument,))[0]

    def get_quotes(
        self,
        instruments: tuple[InstrumentKey, ...],
    ) -> tuple[QuoteSnapshot, ...]:
        """Retrieve chunked full quotes while preserving caller order."""
        if not instruments:
            return ()

        snapshots: list[QuoteSnapshot] = []
        for offset in range(0, len(instruments), _QUOTE_BATCH_LIMIT):
            chunk = instruments[offset : offset + _QUOTE_BATCH_LIMIT]
            request_body: dict[str, list[int]] = {}
            for instrument in chunk:
                security_id = self._security_id(instrument)
                segment = to_dhan_segment(instrument.segment)
                request_body.setdefault(segment, []).append(int(security_id))

            response = self._transport.post("/marketfeed/quote", request_body)
            received_at = normalize_datetime_to_ist(self._clock())
            snapshots.extend(parse_quote_response(response, chunk, received_at))
        return tuple(snapshots)

    def get_historical(
        self,
        instrument: InstrumentKey,
        interval: str,
        start_at: datetime,
        end_at: datetime,
    ) -> HistoricalSeries:
        """Retrieve normalized daily or supported intraday historical bars."""
        requested_from = normalize_datetime_to_ist(start_at)
        requested_to = normalize_datetime_to_ist(end_at)
        if requested_to <= requested_from:
            raise ValueError("end_at must be later than start_at")

        try:
            normalized_interval = normalize_interval(interval)
        except ValueError as exc:
            raise UnsupportedCapabilityError(
                ProviderCapability.HISTORICAL_OHLCV,
                provider="DHAN",
                detail=f"Dhan historical interval {interval!r} is unsupported or ambiguous",
            ) from exc

        security_id = self._security_id(instrument)
        dhan_instrument_type = self._historical_instrument_type(instrument, security_id)
        request_body: dict[str, object] = {
            "securityId": security_id,
            "exchangeSegment": to_dhan_segment(instrument.segment),
            "instrument": dhan_instrument_type.value,
            "oi": instrument.instrument_type
            in {
                InstrumentType.FUTURE,
                InstrumentType.CALL_OPTION,
                InstrumentType.PUT_OPTION,
            },
        }

        if normalized_interval == "1d":
            path = "/charts/historical"
            interval_minutes = None
            request_body.update(
                {
                    "fromDate": requested_from.strftime("%Y-%m-%d"),
                    "toDate": requested_to.strftime("%Y-%m-%d"),
                }
            )
        elif normalized_interval in _INTRADAY_INTERVALS:
            if requested_to - requested_from > _MAX_INTRADAY_RANGE:
                raise UnsupportedCapabilityError(
                    ProviderCapability.HISTORICAL_OHLCV,
                    provider="DHAN",
                    detail="Dhan intraday requests over 90 days require explicit caller chunking",
                )
            path = "/charts/intraday"
            dhan_interval, interval_minutes = _INTRADAY_INTERVALS[normalized_interval]
            request_body.update(
                {
                    "interval": dhan_interval,
                    "fromDate": requested_from.strftime("%Y-%m-%d %H:%M:%S"),
                    "toDate": requested_to.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        else:
            raise UnsupportedCapabilityError(
                ProviderCapability.HISTORICAL_OHLCV,
                provider="DHAN",
                detail=f"Dhan does not support historical interval {normalized_interval}",
            )

        response = self._transport.post(path, request_body)
        received_at = normalize_datetime_to_ist(self._clock())
        return parse_historical_response(
            response,
            instrument=instrument,
            interval=normalized_interval,
            interval_minutes=interval_minutes,
            requested_from=requested_from,
            requested_to=requested_to,
            received_at=received_at,
        )

    def search_instruments(self, query: str) -> tuple[InstrumentRecord, ...]:
        """Defer instrument-master search to the dedicated resolver target."""
        del query
        raise UnsupportedCapabilityError(
            ProviderCapability.INSTRUMENT_MASTER,
            provider="DHAN",
            detail="Dhan instrument-master search is deferred to TIAF_A1.4",
        )

    @staticmethod
    def _security_id(instrument: InstrumentKey) -> str:
        value = instrument.provider_instrument_id
        if value is None or not value.isdigit() or int(value) <= 0:
            raise InstrumentNotFoundError(
                "A positive numeric Dhan securityId is required in provider_instrument_id",
                provider="DHAN",
            )
        return value

    def _historical_instrument_type(
        self,
        instrument: InstrumentKey,
        security_id: str,
    ) -> DhanInstrumentType:
        derivative_type = self._historical_instrument_types.get(security_id)
        return to_dhan_instrument_type(
            instrument.instrument_type,
            derivative_type=derivative_type,
        )
