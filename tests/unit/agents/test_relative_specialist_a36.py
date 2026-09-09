"""A3.6 Relative Strength specialist policy and boundary tests."""

import pytest

from tiaf.agents import AgentEvidenceReference, AgentRunStatus, AgentStance, SpecialistId
from tiaf.agents.specialists import (
    RelativeExtremeState,
    RelativeMtfState,
    RelativeStrengthSpecialist,
    RelativeStrengthState,
    relative_assessment_from_opinion,
)
from tiaf.contracts import EvidenceType

from ._contextual_support import fact, pack, reference, request


def relative_reference(
    *spreads: tuple[str, float],
    subject_return: float = 5.0,
    benchmark_return: float = 1.0,
    consistency: float = 0.75,
    metadata: dict[str, str] | None = None,
) -> AgentEvidenceReference:
    values = [
        fact("relative.subject_return_percent", subject_return, unit="%"),
        fact("relative.benchmark_return_percent", benchmark_return, unit="%"),
        fact("relative.strength_consistency", consistency, unit="fraction"),
    ]
    values.extend(
        fact(
            "relative.return_spread_percent",
            value,
            fact_id=f"spread:{interval}",
            interval=interval,
            unit="percentage points",
        )
        for interval, value in spreads
    )
    return reference(
        "relative-evidence",
        EvidenceType.RELATIVE_STRENGTH,
        tuple(values),
        metadata=(
            {"benchmark_symbol": "NIFTY", "benchmark_role": "MARKET"}
            if metadata is None
            else metadata
        ),
    )


@pytest.mark.parametrize(
    ("spread", "state", "stance"),
    (
        (7.0, RelativeStrengthState.STRONGLY_OUTPERFORMING, AgentStance.POSITIVE),
        (3.0, RelativeStrengthState.OUTPERFORMING, AgentStance.POSITIVE),
        (0.0, RelativeStrengthState.INLINE, AgentStance.NEUTRAL),
        (-3.0, RelativeStrengthState.UNDERPERFORMING, AgentStance.NEGATIVE),
        (-7.0, RelativeStrengthState.STRONGLY_UNDERPERFORMING, AgentStance.NEGATIVE),
    ),
)
def test_relative_strength_states(
    spread: float, state: RelativeStrengthState, stance: AgentStance
) -> None:
    opinion = RelativeStrengthSpecialist().analyze(
        request(SpecialistId.RELATIVE_STRENGTH), pack((relative_reference(("1d", spread)),))
    )
    detail = relative_assessment_from_opinion(opinion)
    assert detail.relative_strength is state
    assert opinion.stance is stance
    assert opinion.usage.llm_calls == opinion.usage.input_tokens == opinion.usage.output_tokens == 0


def test_mtf_conflict_and_short_strong_long_weak_are_preserved() -> None:
    opinion = RelativeStrengthSpecialist().analyze(
        request(SpecialistId.RELATIVE_STRENGTH),
        pack((relative_reference(("1d", 4.0), ("1h", -2.0)),)),
    )
    detail = relative_assessment_from_opinion(opinion)
    assert detail.mtf_alignment is RelativeMtfState.CONFLICT
    assert detail.relative_strength is RelativeStrengthState.MIXED
    assert detail.contradictions
    assert opinion.stance is AgentStance.MIXED


def test_missing_benchmark_is_insufficient_not_neutral() -> None:
    opinion = RelativeStrengthSpecialist().analyze(
        request(SpecialistId.RELATIVE_STRENGTH),
        pack((relative_reference(("1d", 4.0), metadata={}),)),
    )
    assert opinion.status is AgentRunStatus.INSUFFICIENT_EVIDENCE
    assert opinion.stance is AgentStance.INSUFFICIENT_EVIDENCE
    assert "BENCHMARK_MAPPING_MISSING" in opinion.reason_codes


def test_a2_baseline_spread_is_sufficient_without_optional_component_returns() -> None:
    supplied = relative_reference(("1d", 3.0))
    evidence = supplied.model_copy(
        update={
            "facts": tuple(
                item
                for item in supplied.facts
                if item.metric_id
                not in {
                    "relative.subject_return_percent",
                    "relative.benchmark_return_percent",
                }
            )
        }
    )
    opinion = RelativeStrengthSpecialist().analyze(
        request(SpecialistId.RELATIVE_STRENGTH), pack((evidence,))
    )
    detail = relative_assessment_from_opinion(opinion)
    assert detail.relative_strength is RelativeStrengthState.OUTPERFORMING
    assert detail.subject_return_percent is None
    assert detail.benchmark_return_percent is None
    assert "single_timeframe_only" in detail.confidence_basis
    assert opinion.stance is AgentStance.POSITIVE


def test_benchmark_mismatch_is_rejected_as_insufficient() -> None:
    first = relative_reference(("1d", 4.0))
    second = reference(
        "relative-sector",
        EvidenceType.RELATIVE_STRENGTH,
        (fact("relative.return_spread_percent", 2.0, fact_id="sector-spread", interval="1d"),),
        metadata={"benchmark_symbol": "NIFTYENERGY", "benchmark_role": "SECTOR"},
    )
    opinion = RelativeStrengthSpecialist().analyze(
        request(SpecialistId.RELATIVE_STRENGTH), pack((first, second))
    )
    assert opinion.stance is AgentStance.INSUFFICIENT_EVIDENCE
    assert "BENCHMARK_MISMATCH" in opinion.reason_codes


def test_extended_leader_is_supportive_but_exposes_chase_risk() -> None:
    base = relative_reference(("1d", 7.0))
    changed = base.model_copy(
        update={"facts": (*base.facts, fact("relative.excess_move_atr", 3.0, unit="ATR"))}
    )
    opinion = RelativeStrengthSpecialist().analyze(
        request(SpecialistId.RELATIVE_STRENGTH), pack((changed,))
    )
    assert (
        relative_assessment_from_opinion(opinion).extreme_state
        is RelativeExtremeState.EXTENDED_LEADERSHIP
    )
    assert opinion.risks


def test_every_relative_claim_is_cited_to_supplied_evidence() -> None:
    evidence = pack((relative_reference(("1d", 2.5)),))
    opinion = RelativeStrengthSpecialist().analyze(
        request(SpecialistId.RELATIVE_STRENGTH), evidence
    )
    supplied = {item.evidence_id for item in evidence.references}
    assert opinion.evidence_claims
    assert {
        citation.evidence_id for claim in opinion.evidence_claims for citation in claim.citations
    } <= supplied
