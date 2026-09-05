"""Pure Dhan option-chain translation into provider-neutral snapshots."""

from collections.abc import Mapping
from datetime import date, datetime
from math import isfinite
from typing import Any

from pydantic import ValidationError

from tiaf.contracts import DataQuality, FreshnessState, OptionType
from tiaf.data import (
    ExpiryListSnapshot,
    InstrumentKey,
    InstrumentType,
    MarketSegment,
    OptionChainSnapshot,
    OptionGreeks,
    OptionMarketSnapshot,
    OptionStrikeSnapshot,
    ProviderBadResponseError,
)
from tiaf.data.normalization import normalize_datetime_to_ist


def _bad_response(detail: str) -> ProviderBadResponseError:
    return ProviderBadResponseError(detail, provider="DHAN")


def _as_mapping(value: object, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise _bad_response(f"Dhan field {field} must be an object")
    return value


def _optional_float(payload: Mapping[str, Any], field: str) -> float | None:
    value = payload.get(field)
    if value is None:
        return None
    if isinstance(value, bool):
        raise _bad_response(f"Dhan field {field} must be numeric when present")
    try:
        converted = float(value)
    except (TypeError, ValueError) as exc:
        raise _bad_response(f"Dhan field {field} must be numeric when present") from exc
    if not isfinite(converted):
        raise _bad_response(f"Dhan field {field} must be finite when present")
    return converted


def _optional_int(payload: Mapping[str, Any], field: str) -> int | None:
    value = payload.get(field)
    if value is None:
        return None
    if isinstance(value, bool):
        raise _bad_response(f"Dhan field {field} must be an integer when present")
    try:
        converted = int(value)
        numeric = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise _bad_response(f"Dhan field {field} must be an integer when present") from exc
    if converted != numeric:
        raise _bad_response(f"Dhan field {field} must be an integer when present")
    return converted


def _security_id(payload: Mapping[str, Any]) -> str | None:
    value = payload.get("security_id")
    if value is None:
        return None
    if isinstance(value, bool):
        raise _bad_response("Dhan option security_id must be a positive integer")
    normalized = str(value).strip()
    if not normalized.isdigit() or int(normalized) <= 0:
        raise _bad_response("Dhan option security_id must be a positive integer")
    return normalized


def _derivatives_segment(underlying: InstrumentKey) -> MarketSegment:
    if underlying.segment in {MarketSegment.NSE_EQUITY, MarketSegment.NSE_INDEX}:
        return MarketSegment.NSE_FNO
    if underlying.segment in {MarketSegment.BSE_EQUITY, MarketSegment.BSE_INDEX}:
        return MarketSegment.BSE_FNO
    raise _bad_response("Dhan option chain underlying has no supported derivatives segment")


def _quality(
    *,
    ltp: float | None,
    volume: int | None,
    open_interest: int | None,
    implied_volatility: float | None,
    greeks: OptionGreeks,
    values: tuple[float | int | None, ...],
) -> DataQuality:
    primary = (
        ltp,
        volume,
        open_interest,
        implied_volatility,
        greeks.delta,
        greeks.gamma,
        greeks.theta,
        greeks.vega,
    )
    if all(value is not None for value in primary):
        return DataQuality.GOOD
    if ltp is not None:
        return DataQuality.PARTIAL
    if any(value is not None for value in values):
        return DataQuality.DEGRADED
    return DataQuality.UNAVAILABLE


def _parse_side(
    payload: Mapping[str, Any],
    *,
    underlying: InstrumentKey,
    strike: float,
    expiry: date,
    option_type: OptionType,
    observed_at: datetime,
) -> OptionMarketSnapshot:
    greeks_payload = _as_mapping(payload.get("greeks", {}), "greeks")
    greeks = OptionGreeks(
        delta=_optional_float(greeks_payload, "delta"),
        gamma=_optional_float(greeks_payload, "gamma"),
        theta=_optional_float(greeks_payload, "theta"),
        vega=_optional_float(greeks_payload, "vega"),
    )
    security_id = _security_id(payload)
    ltp = _optional_float(payload, "last_price")
    previous_close = _optional_float(payload, "previous_close_price")
    average_price = _optional_float(payload, "average_price")
    bid = _optional_float(payload, "top_bid_price")
    ask = _optional_float(payload, "top_ask_price")
    bid_quantity = _optional_int(payload, "top_bid_quantity")
    ask_quantity = _optional_int(payload, "top_ask_quantity")
    volume = _optional_int(payload, "volume")
    previous_volume = _optional_int(payload, "previous_volume")
    open_interest = _optional_int(payload, "oi")
    previous_open_interest = _optional_int(payload, "previous_oi")
    implied_volatility = _optional_float(payload, "implied_volatility")

    # Dhan emits zero top prices when there is no executable quote. Preserve real
    # non-zero prices only, and do not present their paired quantity as a quote.
    if bid == 0:
        bid = None
        bid_quantity = None
    if ask == 0:
        ask = None
        ask_quantity = None

    instrument_type = (
        InstrumentType.CALL_OPTION if option_type is OptionType.CE else InstrumentType.PUT_OPTION
    )
    instrument = InstrumentKey(
        symbol=underlying.symbol,
        exchange=underlying.exchange,
        segment=_derivatives_segment(underlying),
        instrument_type=instrument_type,
        expiry=expiry,
        strike=strike,
        option_type=option_type,
        provider_instrument_id=security_id,
    )
    all_values = (
        ltp,
        previous_close,
        average_price,
        bid,
        bid_quantity,
        ask,
        ask_quantity,
        volume,
        previous_volume,
        open_interest,
        previous_open_interest,
        implied_volatility,
        greeks.delta,
        greeks.gamma,
        greeks.theta,
        greeks.vega,
    )
    return OptionMarketSnapshot(
        instrument=instrument,
        option_type=option_type,
        strike=strike,
        expiry=expiry,
        security_id=security_id,
        ltp=ltp,
        previous_close=previous_close,
        average_price=average_price,
        bid=bid,
        bid_quantity=bid_quantity,
        ask=ask,
        ask_quantity=ask_quantity,
        volume=volume,
        previous_volume=previous_volume,
        open_interest=open_interest,
        previous_open_interest=previous_open_interest,
        implied_volatility=implied_volatility,
        greeks=greeks,
        observed_at=observed_at,
        source_provider="DHAN",
        freshness=FreshnessState.UNKNOWN,
        quality=_quality(
            ltp=ltp,
            volume=volume,
            open_interest=open_interest,
            implied_volatility=implied_volatility,
            greeks=greeks,
            values=all_values,
        ),
        metadata={"observed_at_source": "retrieval_time"},
    )


def parse_expiry_list_response(
    payload: Mapping[str, Any],
    *,
    underlying: InstrumentKey,
    received_at: datetime,
) -> ExpiryListSnapshot:
    """Parse Dhan active expiry dates without silently deduplicating them."""
    if str(payload.get("status", "")).casefold() != "success":
        raise _bad_response("Dhan expiry-list response did not report success")
    values = payload.get("data")
    if not isinstance(values, list):
        raise _bad_response("Dhan expiry-list data must be an array")
    if not values:
        raise _bad_response("Dhan successful expiry-list response was empty")
    expiries: list[date] = []
    for value in values:
        if not isinstance(value, str):
            raise _bad_response("Dhan expiry value must be an ISO date string")
        try:
            expiries.append(date.fromisoformat(value))
        except ValueError as exc:
            raise _bad_response("Dhan expiry value must be a valid ISO date") from exc
    expiries.sort()
    normalized_received_at = normalize_datetime_to_ist(received_at)
    try:
        return ExpiryListSnapshot(
            underlying=underlying,
            expiries=tuple(expiries),
            observed_at=normalized_received_at,
            received_at=normalized_received_at,
            source_provider="DHAN",
            freshness=FreshnessState.UNKNOWN,
            quality=DataQuality.GOOD,
            metadata={"observed_at_source": "retrieval_time"},
        )
    except ValidationError as exc:
        raise _bad_response("Dhan expiry list failed normalized model validation") from exc


def parse_option_chain_response(
    payload: Mapping[str, Any],
    *,
    underlying: InstrumentKey,
    expiry: date,
    received_at: datetime,
) -> OptionChainSnapshot:
    """Parse a complete Dhan chain, allowing independently absent CE or PE sides."""
    if str(payload.get("status", "")).casefold() != "success":
        raise _bad_response("Dhan option-chain response did not report success")
    data = _as_mapping(payload.get("data"), "data")
    chain = _as_mapping(data.get("oc"), "data.oc")
    if not chain:
        raise _bad_response("Dhan successful option-chain response was empty")
    normalized_received_at = normalize_datetime_to_ist(received_at)
    strikes: list[OptionStrikeSnapshot] = []
    try:
        for strike_value, entry_value in chain.items():
            try:
                strike = float(strike_value)
            except (TypeError, ValueError) as exc:
                raise _bad_response("Dhan option-chain strike must be numeric") from exc
            if not isfinite(strike) or strike <= 0:
                raise _bad_response("Dhan option-chain strike must be positive")
            entry = _as_mapping(entry_value, f"data.oc.{strike_value}")
            call_value = entry.get("ce")
            put_value = entry.get("pe")
            call = (
                _parse_side(
                    _as_mapping(call_value, "ce"),
                    underlying=underlying,
                    strike=strike,
                    expiry=expiry,
                    option_type=OptionType.CE,
                    observed_at=normalized_received_at,
                )
                if call_value is not None
                else None
            )
            put = (
                _parse_side(
                    _as_mapping(put_value, "pe"),
                    underlying=underlying,
                    strike=strike,
                    expiry=expiry,
                    option_type=OptionType.PE,
                    observed_at=normalized_received_at,
                )
                if put_value is not None
                else None
            )
            strikes.append(OptionStrikeSnapshot(strike=strike, call=call, put=put))
        strikes.sort(key=lambda item: item.strike)
        qualities = {
            side.quality
            for strike in strikes
            for side in (strike.call, strike.put)
            if side is not None
        }
        if qualities == {DataQuality.UNAVAILABLE}:
            quality = DataQuality.UNAVAILABLE
        elif DataQuality.UNAVAILABLE in qualities or DataQuality.DEGRADED in qualities:
            quality = DataQuality.DEGRADED
        elif DataQuality.PARTIAL in qualities:
            quality = DataQuality.PARTIAL
        else:
            quality = DataQuality.GOOD
        return OptionChainSnapshot(
            underlying=underlying,
            expiry=expiry,
            underlying_ltp=_optional_float(data, "last_price"),
            strikes=tuple(strikes),
            observed_at=normalized_received_at,
            received_at=normalized_received_at,
            source_provider="DHAN",
            freshness=FreshnessState.UNKNOWN,
            quality=quality,
            metadata={"observed_at_source": "retrieval_time"},
        )
    except ValidationError as exc:
        raise _bad_response("Dhan option chain failed normalized model validation") from exc
