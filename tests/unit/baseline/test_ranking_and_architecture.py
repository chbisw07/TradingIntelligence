"""A2.9 ranking determinism and strict architectural boundary tests."""

from pathlib import Path

import pytest

from tiaf.baseline import (
    BaselineEngine,
    BaselineRankingError,
    CandidateClass,
    OpportunityAssessment,
    OpportunityRanking,
    default_policy,
    rank_opportunities,
)
from tiaf.contracts import TradeStyle

from ._support import baseline_request, values_for


def _assessment(symbol: str, *, profile: str = "positive") -> OpportunityAssessment:
    policy = default_policy(TradeStyle.POSITIONAL)
    return BaselineEngine((policy,)).assess(
        baseline_request(policy, subject=symbol, profile=profile)
    )


def test_ranking_is_score_descending_and_preserves_all_assessments() -> None:
    first = _assessment("AAA")
    values = values_for("positive")
    values["extension.ema"] = 1.5
    policy = default_policy(TradeStyle.POSITIONAL)
    second = BaselineEngine((policy,)).assess(
        baseline_request(policy, subject="BBB", values=values)
    )
    ranking = rank_opportunities((second, first))
    assert tuple(item.subject for item in ranking.items) == ("AAA", "BBB")
    assert tuple(item.subject for item in ranking.assessments) == ("AAA", "BBB")
    payload = ranking.model_dump(mode="json")
    assert isinstance(payload["input_universe"], list)
    assert isinstance(payload["items"], list)
    assert payload["created_at"].endswith("+05:30")
    assert OpportunityRanking.model_validate(payload) == ranking


def test_tie_break_is_symbol_and_has_no_input_order_dependency() -> None:
    a, b = _assessment("AAA"), _assessment("BBB")
    forward = rank_opportunities((a, b))
    reverse = rank_opportunities((b, a))
    assert forward.items == reverse.items
    assert forward.ranking_id == reverse.ranking_id
    assert forward.input_universe == ("AAA", "BBB")
    assert reverse.input_universe == ("BBB", "AAA")
    assert tuple(item.subject for item in forward.items) == ("AAA", "BBB")


def test_top_n_never_fills_with_no_trade() -> None:
    eligible = _assessment("AAA")
    no_trade = _assessment("BBB", profile="neutral")
    ranking = rank_opportunities((no_trade, eligible), top_n=5)
    assert len(ranking.items) == int(eligible.eligible)
    assert "BBB" in ranking.excluded_no_trade
    assert all(item.candidate_class is not CandidateClass.NO_TRADE for item in ranking.items)


def test_all_no_trade_is_valid_empty_ranking() -> None:
    ranking = rank_opportunities(
        (_assessment("AAA", profile="neutral"), _assessment("BBB", profile="conflicted")),
        top_n=10,
    )
    assert ranking.items == ()
    assert ranking.excluded_no_trade == ("AAA", "BBB")


def test_ranking_rejects_duplicates_and_invalid_top_n() -> None:
    item = _assessment("AAA")
    with pytest.raises(BaselineRankingError, match="unique"):
        rank_opportunities((item, item))
    with pytest.raises(BaselineRankingError, match="positive"):
        rank_opportunities((item,), top_n=0)


def test_baseline_package_has_no_forbidden_architecture_imports_or_language() -> None:
    root = Path("src/tiaf/baseline")
    source = "\n".join(path.read_text() for path in root.glob("*.py"))
    forbidden_imports = (
        "tiaf.data.providers",
        "requests",
        "httpx",
        "TradeMonitor",
        "langgraph",
        "openai",
        "tiaf.agents",
        "tiaf.workflows",
    )
    assert not any(item in source for item in forbidden_imports)
    forbidden_output = ("BUY", "SELL", "TARGET", "STOP_LOSS")
    assert not any(item in source for item in forbidden_output)
