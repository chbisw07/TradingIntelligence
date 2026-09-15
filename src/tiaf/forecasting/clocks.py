"""Trusted local execution clock; injection is a Python test seam, never request data."""

import time
from datetime import datetime
from typing import Protocol

from pydantic import TypeAdapter

from tiaf.contracts.common import TIAF_TIMEZONE

from .identity import ForecastDateTime


class Clock(Protocol):
    def now(self) -> datetime: ...

    def monotonic(self) -> float: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(TIAF_TIMEZONE)

    def monotonic(self) -> float:
        return time.monotonic()


def read_clock(clock: Clock) -> datetime:
    return TypeAdapter(ForecastDateTime).validate_python(clock.now())
