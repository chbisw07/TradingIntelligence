"""Pure admission failures only; no speculative store/runtime exception taxonomy."""

from .enums import ForecastReason


class ForecastAdmissionError(ValueError):
    """Stable qualification reason, without echoing evidence or supplied secrets."""

    def __init__(self, reason: ForecastReason) -> None:
        self.reason = reason
        super().__init__(f"forecast admission rejected: {reason.value}")
