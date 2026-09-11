"""Safe facade exception carrying a serializable, redacted error record."""

from .contracts import FacadeErrorRecord


class FacadeInvocationError(ValueError):
    """Capability-level failure; internal objects and payloads are never exposed."""

    def __init__(self, record: FacadeErrorRecord) -> None:
        super().__init__(record.message)
        self.record = record

