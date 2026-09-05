"""Common validated types and base models for TIAF contracts."""

from datetime import datetime
from typing import Annotated, Any
from zoneinfo import ZoneInfo

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    JsonValue,
    StringConstraints,
)


def _normalize_symbol(value: Any) -> Any:
    """Normalize string symbols before applying string constraints."""
    if isinstance(value, str):
        return value.strip().upper()
    return value


TIAF_TIMEZONE = ZoneInfo("Asia/Kolkata")


def _normalize_tiaf_datetime(value: datetime) -> datetime:
    """Reject naive datetimes and normalize aware values to the TIAF timezone."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(TIAF_TIMEZONE)


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Symbol = Annotated[
    str,
    BeforeValidator(_normalize_symbol),
    StringConstraints(strip_whitespace=True, min_length=1),
]
TiafDateTime = Annotated[datetime, AfterValidator(_normalize_tiaf_datetime)]
Confidence = Annotated[float, Field(ge=0.0, le=1.0)]
Score = Annotated[float, Field(ge=0.0, le=100.0)]
NonNegativeFloat = Annotated[float, Field(ge=0.0)]
PositiveFloat = Annotated[float, Field(gt=0.0)]
PositiveInt = Annotated[int, Field(gt=0)]
Metadata = dict[str, JsonValue]


class ContractModel(BaseModel):
    """Base for versioned, immutable, strict domain messages."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: NonEmptyStr = "1.0"


class Horizon(ContractModel):
    """Flexible requested or assessed duration, independent of trade style."""

    label: NonEmptyStr | None = None
    min_days: int | None = Field(default=None, ge=0)
    max_days: int | None = Field(default=None, ge=0)
    hard_end_at: TiafDateTime | None = None

    def model_post_init(self, __context: Any) -> None:
        """Validate relationships among optional horizon bounds."""
        if self.label is None and self.min_days is None and self.max_days is None:
            if self.hard_end_at is None:
                raise ValueError("horizon requires a label or structured bound")
        if self.min_days is not None and self.max_days is not None:
            if self.max_days < self.min_days:
                raise ValueError("max_days must be greater than or equal to min_days")
