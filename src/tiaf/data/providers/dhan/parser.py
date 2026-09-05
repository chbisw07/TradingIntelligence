"""Pure translation from Dhan response shapes to frozen TIAF models."""

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime, time, timedelta
from typing import Any

from pydantic import ValidationError

from tiaf.contracts import DataQuality, FreshnessState
from tiaf.data import (
    HistoricalSeries,
    InstrumentKey,
    InstrumentNotFoundError,
    InstrumentType,
    OHLCVBar,
    ProviderBadResponseError,
    QuoteFieldAvailability,
    QuoteSnapshot,
)
from tiaf.data.normalization import TIAF_TIMEZONE, normalize_datetime_to_ist
from tiaf.data.providers.dhan.mappings import to_dhan_segment

_DHAN_QUOTE_TIME_FORMAT = "%d/%m/%Y %H:%M:%S"


def _bad_response(detail: str) -> ProviderBadResponseError:
    return ProviderBadResponseError(detail, provider="DHAN")


def _as_mapping(value: object, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise _bad_response(f"Dhan field {field} must be an object")
    return value


def _required_float(payload: Mapping[str, Any], field: str) -> float:
    if field not in payload:
        raise _bad_response(f"Dhan quote is missing {field}")
    try:
        return float(payload[field])
    except (TypeError, ValueError) as exc:
        raise _bad_response(f"Dhan field {field} must be numeric") from exc


def _optional_float(payload: Mapping[str, Any], field: str) -> float | None:
    if field not in payload or payload[field] is None:
        return None
    try:
        return float(payload[field])
    except (TypeError, ValueError) as exc:
        raise _bad_response(f"Dhan field {field} must be numeric when present") from exc


def _optional_int(payload: Mapping[str, Any], field: str) -> int | None:
    if field not in payload or payload[field] is None:
        return None
    value = payload[field]
    if isinstance(value, bool):
        raise _bad_response(f"Dhan field {field} must be an integer when present")
    try:
        converted = int(value)
    except (TypeError, ValueError) as exc:
        raise _bad_response(f"Dhan field {field} must be an integer when present") from exc
    return converted


def _best_depth_price(payload: Mapping[str, Any], side: str) -> float | None:
    depth_value = payload.get("depth")
    if depth_value is None:
        return None
    depth = _as_mapping(depth_value, "depth")
    levels_value = depth.get(side)
    if levels_value is None:
        return None
    if not isinstance(levels_value, Sequence) or isinstance(levels_value, (str, bytes)):
        raise _bad_response(f"Dhan depth.{side} must be an array")

    prices: list[float] = []
    for level_value in levels_value:
        level = _as_mapping(level_value, f"depth.{side} item")
        price = _optional_float(level, "price")
        if price is not None and price > 0:
            prices.append(price)
    if not prices:
        return None
    return max(prices) if side == "buy" else min(prices)


def _quote_observed_at(payload: Mapping[str, Any], received_at: datetime) -> tuple[datetime, str]:
    value = payload.get("last_trade_time")
    if isinstance(value, str):
        try:
            parsed = datetime.strptime(value, _DHAN_QUOTE_TIME_FORMAT).replace(
                tzinfo=TIAF_TIMEZONE
            )
        except ValueError:
            pass
        else:
            if parsed.year >= 2000:
                return parsed, "last_trade_time"
    return normalize_datetime_to_ist(received_at), "retrieval_time"


def _availability_and_quality(
    instrument: InstrumentKey,
    optional_values: tuple[float | int | None, ...],
) -> tuple[QuoteFieldAvailability, DataQuality]:
    required_values = optional_values
    if instrument.instrument_type not in {
        InstrumentType.FUTURE,
        InstrumentType.CALL_OPTION,
        InstrumentType.PUT_OPTION,
    }:
        required_values = optional_values[:-1]

    if required_values and all(value is not None for value in required_values):
        return QuoteFieldAvailability.AVAILABLE, DataQuality.GOOD
    if any(value is not None for value in optional_values):
        return QuoteFieldAvailability.PARTIAL, DataQuality.PARTIAL
    return QuoteFieldAvailability.UNAVAILABLE, DataQuality.DEGRADED


def parse_quote_response(
    payload: Mapping[str, Any],
    instruments: tuple[InstrumentKey, ...],
    received_at: datetime,
) -> tuple[QuoteSnapshot, ...]:
    """Parse one Dhan quote response and preserve requested instrument order."""
    if str(payload.get("status", "")).casefold() != "success":
        raise _bad_response("Dhan quote response did not report success")
    data = _as_mapping(payload.get("data"), "data")
    normalized_received_at = normalize_datetime_to_ist(received_at)
    snapshots: list[QuoteSnapshot] = []

    for instrument in instruments:
        security_id = instrument.provider_instrument_id
        if security_id is None:
            raise InstrumentNotFoundError(
                "Dhan securityId is required on InstrumentKey.provider_instrument_id",
                provider="DHAN",
            )
        segment = to_dhan_segment(instrument.segment)
        segment_value = data.get(segment)
        if segment_value is None:
            raise InstrumentNotFoundError(
                f"Dhan quote omitted segment {segment}",
                provider="DHAN",
            )
        segment_data = _as_mapping(segment_value, f"data.{segment}")
        quote_value = segment_data.get(security_id)
        if quote_value is None:
            raise InstrumentNotFoundError(
                f"Dhan quote omitted securityId {security_id} in {segment}",
                provider="DHAN",
            )
        quote = _as_mapping(quote_value, f"data.{segment}.{security_id}")
        ohlc_value = quote.get("ohlc", {})
        ohlc = _as_mapping(ohlc_value, "ohlc")

        open_price = _optional_float(ohlc, "open")
        high = _optional_float(ohlc, "high")
        low = _optional_float(ohlc, "low")
        previous_close = _optional_float(ohlc, "close")
        volume = _optional_int(quote, "volume")
        open_interest = _optional_int(quote, "oi")
        bid = _best_depth_price(quote, "buy")
        ask = _best_depth_price(quote, "sell")
        observed_at, observed_at_source = _quote_observed_at(quote, normalized_received_at)
        availability, quality = _availability_and_quality(
            instrument,
            (open_price, high, low, previous_close, volume, bid, ask, open_interest),
        )

        try:
            snapshot = QuoteSnapshot(
                instrument=instrument,
                ltp=_required_float(quote, "last_price"),
                open=open_price,
                high=high,
                low=low,
                previous_close=previous_close,
                volume=volume,
                bid=bid,
                ask=ask,
                open_interest=open_interest,
                observed_at=observed_at,
                received_at=normalized_received_at,
                source_provider="DHAN",
                freshness=FreshnessState.UNKNOWN,
                quality=quality,
                availability=availability,
                metadata={
                    "dhan_security_id": security_id,
                    "observed_at_source": observed_at_source,
                },
            )
        except ValidationError as exc:
            raise _bad_response("Dhan quote failed normalized model validation") from exc
        snapshots.append(snapshot)
    return tuple(snapshots)


def _parallel_arrays(payload: Mapping[str, Any]) -> dict[str, Sequence[Any]]:
    required = ("timestamp", "open", "high", "low", "close", "volume")
    arrays: dict[str, Sequence[Any]] = {}
    for field in required:
        value = payload.get(field)
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise _bad_response(f"Dhan historical field {field} must be an array")
        arrays[field] = value

    expected_length = len(arrays["timestamp"])
    if any(len(arrays[field]) != expected_length for field in required):
        raise _bad_response("Dhan historical arrays have unequal lengths")

    oi_value = payload.get("open_interest")
    if oi_value is not None:
        if not isinstance(oi_value, Sequence) or isinstance(oi_value, (str, bytes)):
            raise _bad_response("Dhan historical field open_interest must be an array")
        if len(oi_value) != expected_length:
            raise _bad_response("Dhan historical arrays have unequal lengths")
        arrays["open_interest"] = oi_value
    return arrays


def _epoch_to_ist(value: Any) -> datetime:
    try:
        return datetime.fromtimestamp(float(value), tz=UTC).astimezone(TIAF_TIMEZONE)
    except (TypeError, ValueError, OSError, OverflowError) as exc:
        raise _bad_response("Dhan historical timestamp must be a valid epoch") from exc


def parse_historical_response(
    payload: Mapping[str, Any],
    *,
    instrument: InstrumentKey,
    interval: str,
    interval_minutes: int | None,
    requested_from: datetime,
    requested_to: datetime,
    received_at: datetime,
) -> HistoricalSeries:
    """Parse Dhan parallel arrays without silent truncation."""
    arrays = _parallel_arrays(payload)
    bars: list[OHLCVBar] = []
    oi_values = arrays.get("open_interest")

    for index in range(len(arrays["timestamp"])):
        provider_start = _epoch_to_ist(arrays["timestamp"][index])
        if interval_minutes is None:
            start_at = datetime.combine(provider_start.date(), time.min, tzinfo=TIAF_TIMEZONE)
            end_at = start_at + timedelta(days=1)
        else:
            start_at = provider_start
            end_at = start_at + timedelta(minutes=interval_minutes)

        try:
            current_bar = OHLCVBar.model_validate(
                {
                    "instrument": instrument,
                    "interval": interval,
                    "start_at": start_at,
                    "end_at": end_at,
                    "open": arrays["open"][index],
                    "high": arrays["high"][index],
                    "low": arrays["low"][index],
                    "close": arrays["close"][index],
                    "volume": arrays["volume"][index],
                    "open_interest": oi_values[index] if oi_values is not None else None,
                    "source_provider": "DHAN",
                }
            )
        except ValidationError as exc:
            raise _bad_response("Dhan historical bar failed normalized model validation") from exc
        bars.append(current_bar)

    bars.sort(key=lambda item: item.start_at)
    quality = DataQuality.GOOD if bars else DataQuality.UNAVAILABLE
    try:
        return HistoricalSeries(
            instrument=instrument,
            interval=interval,
            bars=tuple(bars),
            source_provider="DHAN",
            requested_from=requested_from,
            requested_to=requested_to,
            observed_at=received_at,
            freshness=FreshnessState.UNKNOWN,
            quality=quality,
            metadata={"dhan_security_id": instrument.provider_instrument_id or ""},
        )
    except ValidationError as exc:
        raise _bad_response("Dhan historical series failed normalized model validation") from exc
