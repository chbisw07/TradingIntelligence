"""Enums for provider-neutral instrument resolution outcomes."""

from enum import StrEnum


class ResolutionKind(StrEnum):
    """How a unique provider instrument was matched."""

    EXACT = "EXACT"
    UNIQUE_NORMALIZED = "UNIQUE_NORMALIZED"
    PROVIDER_ID = "PROVIDER_ID"
    TRADING_SYMBOL = "TRADING_SYMBOL"
    POLICY_SELECTED = "POLICY_SELECTED"
