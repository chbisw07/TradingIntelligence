"""Tests for the public contract package surface."""

import tiaf.contracts as contracts


def test_expected_contracts_are_publicly_importable() -> None:
    expected = {
        "AgentDecisionBundle",
        "AgentOpinion",
        "DataSnapshot",
        "EvidenceItem",
        "Horizon",
        "OpportunityAssessment",
        "OpportunityRequest",
        "OptionExpression",
        "PositionAssessment",
        "PositionRequest",
    }

    assert expected <= set(contracts.__all__)
    assert all(getattr(contracts, name) is not None for name in expected)
