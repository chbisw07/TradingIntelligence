"""Recorded reconstruction only: no forecaster, registry, truth resolver or simulation."""

from .capture import ForecastCapture
from .store import ForecastCorpusStore


def verify_replay(store: ForecastCorpusStore, run_id: str) -> ForecastCapture:
    """Load and validate exact captured closure, retaining all original IDs and clocks."""
    return store.get_forecast(run_id)
