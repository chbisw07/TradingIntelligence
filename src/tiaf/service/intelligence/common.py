"""IFL value primitives; reuse existing immutable contracts and canonical codec."""

from enum import StrEnum
from typing import Annotated

from pydantic import Field, StringConstraints

from tiaf.forecasting.identity import ForecastContract

Version = Annotated[str, Field(pattern=r"^[A-Za-z0-9_.-]{1,40}$")]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
Finite = Annotated[float, Field(strict=True, allow_inf_nan=False)]
Probability = Annotated[Finite, Field(ge=0, le=1)]


class IntelligenceContract(ForecastContract):
    """Additive schema 1.0, not a change to any existing FF codec."""


class ClaimKind(StrEnum):
    BINARY = "BINARY"
    NUMERIC = "NUMERIC"
    CATEGORICAL = "CATEGORICAL"
    ORDINAL = "ORDINAL"
    RANKING = "RANKING"
    INTERVAL = "INTERVAL"
    EVENT_TIME = "EVENT_TIME"


def unique(values: tuple[object, ...], name: str) -> None:
    if len(set(values)) != len(values):
        raise ValueError(f"DUPLICATE_{name}")
