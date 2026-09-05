"""Typed failures for instrument resolution and master ingestion."""

from tiaf.data.errors import TIAFDataError


class InstrumentResolutionError(TIAFDataError):
    """Base error for resolution operations that cannot be completed."""


class InstrumentAmbiguousError(InstrumentResolutionError):
    """A caller required one instrument but the query matched several."""


class InstrumentMasterUnavailableError(InstrumentResolutionError):
    """An instrument master could not be read or downloaded."""


class InstrumentMasterParseError(InstrumentResolutionError):
    """An instrument master is malformed or has an unsupported schema."""
