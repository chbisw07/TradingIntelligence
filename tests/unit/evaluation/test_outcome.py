"""Known-path anti-lookahead and excursion semantics."""

from datetime import timedelta

import pytest

from tiaf.baseline import BaselineDirection, CandidateClass
from tiaf.evaluation import (
    OutcomeEvaluationError,
    OutcomeWindow,
    calculate_excursions,
    evaluate_outcome,
)

from ..baseline._support import NOW
from ._support import frozen_case, future_path


@pytest.mark.parametrize(
    ("direction", "candidate_class", "mfe", "mae"),
    (
        (BaselineDirection.POSITIVE, CandidateClass.EARLY_OPPORTUNITY, 8.0, -4.0),
        (BaselineDirection.NEGATIVE, CandidateClass.EARLY_OPPORTUNITY, 4.0, -8.0),
        (BaselineDirection.NEUTRAL, CandidateClass.EARLY_OPPORTUNITY, None, None),
        (BaselineDirection.CONFLICTED, CandidateClass.EARLY_OPPORTUNITY, None, None),
        (BaselineDirection.POSITIVE, CandidateClass.NO_TRADE, None, None),
    ),
)
def test_exact_positive_negative_neutral_and_no_trade_excursions(
    direction: BaselineDirection,
    candidate_class: CandidateClass,
    mfe: float | None,
    mae: float | None,
) -> None:
    _, run = frozen_case()
    metrics = calculate_excursions(
        future_path(run),
        direction=direction,
        candidate_class=candidate_class,
    )
    assert metrics.ending_return_percent == pytest.approx(2.0)
    assert metrics.maximum_upside_excursion_percent == pytest.approx(8.0)
    assert metrics.maximum_downside_excursion_percent == pytest.approx(-4.0)
    assert metrics.realized_range_percent == pytest.approx(12.0)
    if mfe is None:
        assert metrics.mfe_percent is None
    else:
        assert metrics.mfe_percent == pytest.approx(mfe)
    if mae is None:
        assert metrics.mae_percent is None
    else:
        assert metrics.mae_percent == pytest.approx(mae)


def test_outcome_attachment_does_not_mutate_original_decision() -> None:
    _, run = frozen_case()
    before = run.model_dump_json()
    result = evaluate_outcome(
        run,
        future_path(run),
        evaluated_at=NOW + timedelta(days=3),
    )
    assert run.model_dump_json() == before
    assert result.original_direction is run.direction
    assert result.original_candidate_class is run.candidate_class
    assert "pnl" not in result.model_dump_json().casefold()


def test_outcome_window_before_decision_is_rejected() -> None:
    from tiaf.evaluation import create_outcome_path

    _, run = frozen_case()
    path = future_path(run)
    invalid_window = OutcomeWindow(
        start_at=NOW - timedelta(days=1),
        end_at=NOW + timedelta(days=1),
        source_interval="1d",
    )
    with pytest.raises(OutcomeEvaluationError, match="before decision"):
        create_outcome_path(
            run,
            assessment_reference_price=100.0,
            window=invalid_window,
            observations=path.observations[:1],
            quality=path.quality,
            complete=False,
            captured_at=NOW + timedelta(days=1),
        )
