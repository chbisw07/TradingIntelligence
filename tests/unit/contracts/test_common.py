"""Tests for shared identifiers, timestamps, horizons, and immutability."""

from datetime import UTC, datetime, tzinfo
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

import tiaf
from tiaf.contracts import Horizon

KOLKATA = ZoneInfo("Asia/Kolkata")


def test_horizon_accepts_label_or_structured_bound() -> None:
    assert Horizon(label=" intraday ").label == "intraday"
    assert Horizon(min_days=2, max_days=5).model_dump()["max_days"] == 5
    end_at = datetime(2026, 9, 21, tzinfo=KOLKATA)
    assert Horizon(hard_end_at=end_at).hard_end_at == end_at


@pytest.mark.parametrize(
    "values",
    [
        {},
        {"min_days": -1},
        {"min_days": 5, "max_days": 2},
    ],
)
def test_horizon_rejects_invalid_bounds(values: dict[str, int]) -> None:
    with pytest.raises(ValidationError):
        Horizon.model_validate(values)


def test_horizon_rejects_naive_hard_end_timestamp() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        Horizon(hard_end_at=datetime(2026, 9, 21))


@pytest.mark.parametrize("source_zone", [UTC, ZoneInfo("America/New_York")])
def test_aware_timestamp_is_normalized_to_asia_kolkata(source_zone: tzinfo) -> None:
    source = datetime(2026, 9, 21, 10, tzinfo=source_zone)
    horizon = Horizon(hard_end_at=source)

    assert horizon.hard_end_at == source.astimezone(KOLKATA)
    assert horizon.hard_end_at is not None
    assert horizon.hard_end_at.tzinfo == KOLKATA


def test_contract_is_frozen() -> None:
    horizon = Horizon(label="intraday")

    with pytest.raises(ValidationError, match="frozen"):
        setattr(horizon, "label", "positional")


def test_package_and_contract_schema_versions_are_separate() -> None:
    horizon = Horizon(label="intraday")

    assert tiaf.__version__ == "0.1.0"
    assert horizon.schema_version == "1.0"
