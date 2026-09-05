"""Tests for stable enum values and serialization."""

import json

from tiaf.contracts import (
    ActionStrength,
    ConfidenceBand,
    DataQuality,
    DirectionPolicy,
    EvidenceSource,
    EvidenceType,
    FreshnessState,
    OpportunityAction,
    OptionType,
    PositionAction,
    TradeDirection,
    TradeStyle,
)


def test_enums_are_strings_and_json_serializable() -> None:
    values = [
        TradeStyle.DAY,
        DirectionPolicy.BOTH,
        TradeDirection.NEUTRAL,
        OpportunityAction.NO_TRADE,
        PositionAction.WATCH_CLOSELY,
        ActionStrength.URGENT,
        FreshnessState.FRESH,
        EvidenceType.RELATIVE_STRENGTH,
        EvidenceSource.THIRD_PARTY,
        ConfidenceBand.VERY_HIGH,
        DataQuality.PARTIAL,
        OptionType.CE,
    ]

    assert json.loads(json.dumps(values)) == [value.value for value in values]
