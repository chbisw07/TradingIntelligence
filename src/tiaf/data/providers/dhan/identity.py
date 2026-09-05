"""Identity-integrity helpers for read-only Dhan diagnostics."""

from tiaf.data.enums import InstrumentType, MarketSegment
from tiaf.data.models import InstrumentKey
from tiaf.data.providers.dhan.instrument_master import DhanInstrumentResolver
from tiaf.data.resolution import InstrumentQuery, InstrumentResolutionError


class DhanIdentityMismatchError(InstrumentResolutionError):
    """A caller-supplied symbol and Dhan security ID identify different instruments."""


def resolve_dhan_diagnostic_instrument(
    *,
    symbol: str | None,
    security_id: str | None,
    exchange: str | None = None,
    segment: MarketSegment | None = None,
    instrument_type: InstrumentType | None = None,
    resolver: DhanInstrumentResolver | None = None,
) -> InstrumentKey:
    """Resolve one factual identity and reject conflicting caller labels before transport."""
    if symbol is None and security_id is None:
        raise InstrumentResolutionError(
            "symbol or security ID is required for a Dhan diagnostic",
            provider="DHAN",
        )
    active_resolver = resolver or DhanInstrumentResolver()
    if symbol is not None:
        result = active_resolver.resolve(
            InstrumentQuery(
                symbol=symbol,
                exchange=exchange,
                segment=segment,
                instrument_type=instrument_type,
                provider="DHAN",
            )
        )
        if result.not_found:
            raise InstrumentResolutionError(
                f"Dhan instrument symbol {symbol!r} was not found in the requested scope",
                provider="DHAN",
            )
        if result.ambiguous or result.resolved is None:
            raise InstrumentResolutionError(
                f"Dhan instrument symbol {symbol!r} is ambiguous in the requested scope",
                provider="DHAN",
            )
        resolved = result.resolved.instrument
        resolved_id = result.resolved.provider_instrument_id
        if security_id is not None and security_id.strip() != resolved_id:
            raise DhanIdentityMismatchError(
                "Identity mismatch:\n"
                f"  requested symbol : {result.resolved.instrument.symbol}\n"
                f"  resolved Dhan ID : {resolved_id}\n"
                f"  supplied Dhan ID : {security_id.strip()}\n\n"
                "No provider request was made.",
                provider="DHAN",
            )
        return resolved

    assert security_id is not None
    result = active_resolver.resolve(
        InstrumentQuery(
            provider_instrument_id=security_id,
            exchange=exchange,
            segment=segment,
            provider="DHAN",
        )
    )
    if result.not_found:
        raise InstrumentResolutionError(
            f"Dhan security ID {security_id!r} was not found in the requested scope",
            provider="DHAN",
        )
    if result.ambiguous or result.resolved is None:
        raise InstrumentResolutionError(
            f"Dhan security ID {security_id!r} is ambiguous in the requested scope",
            provider="DHAN",
        )
    resolved = result.resolved.instrument
    if instrument_type is not None and resolved.instrument_type is not instrument_type:
        raise InstrumentResolutionError(
            f"Dhan security ID {security_id!r} is {resolved.instrument_type.value}, "
            f"not {instrument_type.value}",
            provider="DHAN",
        )
    return resolved
