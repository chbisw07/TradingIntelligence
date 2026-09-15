"""Safe admission, store and recorded-integrity failures; no execution runtime."""

from .enums import ForecastReason


class ForecastAdmissionError(ValueError):
    """Stable qualification reason, without echoing evidence or supplied secrets."""

    def __init__(self, reason: ForecastReason) -> None:
        self.reason = reason
        super().__init__(f"forecast admission rejected: {reason.value}")


class ForecastStoreError(ValueError):
    """Storage denial; messages contain safe reasons, never file bodies."""


class ForecastIntegrityError(ForecastStoreError):
    """Corrupt, missing, conflicting or incompatible captured history."""
