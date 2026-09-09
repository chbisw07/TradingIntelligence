"""A3.6 Sector / Rotation specialist synthetic matrix."""

from typing import Any

import pytest

from tiaf.agents import AgentEvidenceReference, AgentStance, SpecialistId
from tiaf.agents.specialists import (
    RotationState,
    SectorBreadthState,
    SectorConcentrationState,
    SectorSpecialist,
    SubjectSectorState,
    sector_assessment_from_opinion,
)
from tiaf.contracts import EvidenceType

from ._contextual_support import fact, pack, reference, request


def sector_reference(
    *,
    relative: tuple[tuple[str, float], ...] = (("5d", 2.0), ("20d", 3.0)),
    subject_spread: float = 2.0,
    absolute: float = 4.0,
    breadth: float | None = 0.7,
    concentration: float | None = 0.25,
    mapping: bool = True,
) -> AgentEvidenceReference:
    values = [
        fact("sector.return_percent", absolute, unit="%"),
        fact("sector.subject_return_spread_percent", subject_spread, unit="percentage points"),
    ]
    values.extend(
        fact(
            "sector.relative_return_percent",
            value,
            fact_id=f"sector-relative:{interval}",
            interval=interval,
            unit="percentage points",
        )
        for interval, value in relative
    )
    if mapping:
        values.extend(
            (
                fact("sector.mapping.sector_id", "ENERGY"),
                fact("sector.mapping.benchmark_symbol", "NIFTYENERGY"),
            )
        )
    if breadth is not None:
        values.append(fact("sector.breadth.positive_fraction", breadth, unit="fraction"))
    if concentration is not None:
        values.append(
            fact("sector.participation.top_constituent_fraction", concentration, unit="fraction")
        )
    metadata = (
        {"sector_name": "Energy", "mapping_version": "2026.1", "mapping_quality": "VERIFIED"}
        if mapping
        else {}
    )
    return reference("sector-evidence", EvidenceType.SECTOR, tuple(values), metadata=metadata)


@pytest.mark.parametrize(
    ("kwargs", "stance", "subject_state"),
    (
        ({}, AgentStance.POSITIVE, SubjectSectorState.OUTPERFORMS_SECTOR),
        ({"subject_spread": -2.0}, AgentStance.MIXED, SubjectSectorState.LAGS_SECTOR),
        (
            {"relative": (("5d", -2.0), ("20d", -3.0)), "absolute": -4.0, "subject_spread": 2.0},
            AgentStance.MIXED,
            SubjectSectorState.OUTPERFORMS_SECTOR,
        ),
        (
            {"relative": (("5d", -2.0), ("20d", -3.0)), "absolute": -4.0, "subject_spread": -2.0},
            AgentStance.NEGATIVE,
            SubjectSectorState.LAGS_SECTOR,
        ),
    ),
)
def test_sector_subject_combinations(
    kwargs: dict[str, Any], stance: AgentStance, subject_state: SubjectSectorState
) -> None:
    opinion = SectorSpecialist().analyze(
        request(SpecialistId.SECTOR), pack((sector_reference(**kwargs),))
    )
    assert opinion.stance is stance
    assert sector_assessment_from_opinion(opinion).subject_vs_sector is subject_state


@pytest.mark.parametrize(
    ("relative", "state"),
    (
        ((("5d", 3.0), ("20d", -2.0)), RotationState.ROTATING_IN),
        ((("5d", -3.0), ("20d", 2.0)), RotationState.ROTATING_OUT),
        ((("5d", 2.0),), RotationState.INSUFFICIENT_EVIDENCE),
    ),
)
def test_rotation_requires_multiple_periods(
    relative: tuple[tuple[str, float], ...], state: RotationState
) -> None:
    opinion = SectorSpecialist().analyze(
        request(SpecialistId.SECTOR), pack((sector_reference(relative=relative),))
    )
    assert sector_assessment_from_opinion(opinion).rotation_state is state


def test_strong_sector_with_narrow_breadth_is_not_broad_leadership() -> None:
    opinion = SectorSpecialist().analyze(
        request(SpecialistId.SECTOR), pack((sector_reference(breadth=0.25, concentration=0.7),))
    )
    detail = sector_assessment_from_opinion(opinion)
    assert detail.breadth_state is SectorBreadthState.WEAK
    assert detail.concentration_state is SectorConcentrationState.CONCENTRATED_LEADERSHIP
    assert detail.contradictions


def test_missing_mapping_returns_insufficient_evidence() -> None:
    opinion = SectorSpecialist().analyze(
        request(SpecialistId.SECTOR), pack((sector_reference(mapping=False),))
    )
    assert opinion.stance is AgentStance.INSUFFICIENT_EVIDENCE
    assert "SECTOR_MAPPING_MISSING" in opinion.reason_codes


def test_partial_breadth_stays_explicitly_unknown() -> None:
    opinion = SectorSpecialist().analyze(
        request(SpecialistId.SECTOR),
        pack((sector_reference(breadth=None, concentration=None),), coverage=0.7),
    )
    detail = sector_assessment_from_opinion(opinion)
    assert detail.breadth_state is SectorBreadthState.UNKNOWN
    assert detail.concentration_state is SectorConcentrationState.UNKNOWN


def test_sector_catalyst_support_and_conflict_are_preserved() -> None:
    base = sector_reference()
    changed = base.model_copy(
        update={
            "facts": (
                *base.facts,
                fact("sector.catalyst_direction", "POSITIVE", fact_id="event-positive"),
                fact("sector.catalyst_direction", "NEGATIVE", fact_id="event-negative"),
            )
        }
    )
    opinion = SectorSpecialist().analyze(request(SpecialistId.SECTOR), pack((changed,)))
    assert "SECTOR_EVENT_SUPPORT" in opinion.reason_codes
    assert "SECTOR_EVENT_CONFLICT" in opinion.reason_codes
    assert opinion.usage.llm_calls == 0
