"""Pure parser for Dhan rolling expired-options parallel arrays."""

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from math import isfinite
from typing import Any

from pydantic import ValidationError

from tiaf.contracts import DataQuality, OptionType
from tiaf.data import (
    ExpiryFlag,
    HistoricalOptionBar,
    HistoricalOptionExpiryCode,
    InstrumentKey,
    ProviderBadResponseError,
    RelativeStrike,
)
from tiaf.data.normalization import TIAF_TIMEZONE

_FIELDS = ("open", "high", "low", "close", "iv", "volume", "strike", "oi", "spot")


def _bad_response(detail: str) -> ProviderBadResponseError:
    return ProviderBadResponseError(detail, provider="DHAN")


def _as_mapping(value: object, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise _bad_response(f"Dhan field {field} must be an object")
    return value


def _parallel_arrays(payload: Mapping[str, Any]) -> dict[str, Sequence[Any]]:
    arrays: dict[str, Sequence[Any]] = {}
    for field in ("timestamp", *_FIELDS):
        value = payload.get(field)
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise _bad_response(f"Dhan rolling-option field {field} must be an array")
        arrays[field] = value
    expected = len(arrays["timestamp"])
    if any(len(arrays[field]) != expected for field in _FIELDS):
        raise _bad_response("Dhan rolling-option arrays have unequal lengths")
    return arrays


def _optional_float(value: Any, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise _bad_response(f"Dhan rolling-option field {field} must be numeric")
    try:
        converted: float = float(value)
    except (TypeError, ValueError) as exc:
        raise _bad_response(f"Dhan rolling-option field {field} must be numeric") from exc
    if not isfinite(converted):
        raise _bad_response(f"Dhan rolling-option field {field} must be finite")
    return converted


def _optional_int(value: Any, field: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise _bad_response(f"Dhan rolling-option field {field} must be an integer")
    try:
        converted: int = int(value)
        numeric: float = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise _bad_response(f"Dhan rolling-option field {field} must be an integer") from exc
    if converted != numeric:
        raise _bad_response(f"Dhan rolling-option field {field} must be an integer")
    return converted


def _timestamp(value: Any) -> datetime:
    if isinstance(value, bool):
        raise _bad_response("Dhan rolling-option timestamp must be a valid epoch")
    try:
        return datetime.fromtimestamp(float(value), tz=UTC).astimezone(TIAF_TIMEZONE)
    except (TypeError, ValueError, OSError, OverflowError) as exc:
        raise _bad_response("Dhan rolling-option timestamp must be a valid epoch") from exc


def _bar_quality(values: tuple[float | int | None, ...]) -> DataQuality:
    if all(value is not None for value in values):
        return DataQuality.GOOD
    ohlc = values[:4]
    if all(value is not None for value in ohlc):
        return DataQuality.PARTIAL
    if any(value is not None for value in values):
        return DataQuality.DEGRADED
    return DataQuality.UNAVAILABLE


def parse_historical_option_response(
    payload: Mapping[str, Any],
    *,
    underlying: InstrumentKey,
    option_type: OptionType,
    expiry_flag: ExpiryFlag,
    expiry_code: HistoricalOptionExpiryCode,
    relative_strike: RelativeStrike,
) -> tuple[tuple[HistoricalOptionBar, ...], DataQuality]:
    """Parse only the requested CE/PE side and validate all parallel arrays."""
    if str(payload.get("status", "")).casefold() in {"failure", "error"}:
        raise _bad_response("Dhan rolling-option response reported failure")
    data = _as_mapping(payload.get("data"), "data")
    side_key = "ce" if option_type is OptionType.CE else "pe"
    side_value = data.get(side_key)
    if side_value is None:
        return (), DataQuality.UNAVAILABLE
    side = _as_mapping(side_value, f"data.{side_key}")
    arrays = _parallel_arrays(side)
    bars: list[HistoricalOptionBar] = []
    for index in range(len(arrays["timestamp"])):
        values = (
            _optional_float(arrays["open"][index], "open"),
            _optional_float(arrays["high"][index], "high"),
            _optional_float(arrays["low"][index], "low"),
            _optional_float(arrays["close"][index], "close"),
            _optional_float(arrays["iv"][index], "iv"),
            _optional_int(arrays["volume"][index], "volume"),
            _optional_int(arrays["oi"][index], "oi"),
            _optional_float(arrays["strike"][index], "strike"),
            _optional_float(arrays["spot"][index], "spot"),
        )
        try:
            bars.append(
                HistoricalOptionBar(
                    underlying=underlying,
                    option_type=option_type,
                    expiry_flag=expiry_flag,
                    expiry_code=expiry_code,
                    relative_strike=relative_strike,
                    start_at=_timestamp(arrays["timestamp"][index]),
                    open=values[0],
                    high=values[1],
                    low=values[2],
                    close=values[3],
                    implied_volatility=values[4],
                    volume=values[5],
                    open_interest=values[6],
                    actual_strike=values[7],
                    spot=values[8],
                    source_provider="DHAN",
                    quality=_bar_quality(values),
                )
            )
        except ValidationError as exc:
            raise _bad_response("Dhan rolling-option bar failed normalized validation") from exc
    if not bars:
        return (), DataQuality.UNAVAILABLE
    qualities = {bar.quality for bar in bars}
    if qualities == {DataQuality.GOOD}:
        quality = DataQuality.GOOD
    elif qualities == {DataQuality.UNAVAILABLE}:
        quality = DataQuality.UNAVAILABLE
    elif DataQuality.UNAVAILABLE in qualities or DataQuality.DEGRADED in qualities:
        quality = DataQuality.DEGRADED
    else:
        quality = DataQuality.PARTIAL
    return tuple(bars), quality
