"""Deterministic A3.3 interpretation cases and policy edges."""

import pytest

from tiaf.agents import AgentRunStatus, AgentStance, BaselineAgreement
from tiaf.agents.specialists.technical import (
    BreakoutState,
    ExtensionState,
    MomentumState,
    MultiTimeframeState,
    StructureState,
    TechnicalSpecialist,
    TrendState,
    technical_assessment_from_opinion,
)
from tiaf.contracts import DataQuality, FreshnessState

from ._technical_support import technical_pack, technical_request


@pytest.mark.parametrize(
    ("case", "overrides", "omit", "expected_stance", "checks"),
    (
        ("clean bullish trend", {}, (), AgentStance.POSITIVE, (TrendState.STRONG_UPTREND,)),
        (
            "clean bearish trend",
            {
                "trend.distance_from_ema_percent": -2.0,
                "trend.linear_slope_percent": -0.2,
                "trend.signed_efficiency": -0.5,
                "structure.higher_high_fraction": 0.2,
                "structure.higher_low_fraction": 0.2,
                "structure.lower_high_fraction": 0.7,
                "structure.lower_low_fraction": 0.7,
                "indicator.rsi": 38.0,
                "indicator.macd": -0.5,
                "return.percent": -3.0,
                "range.move_over_atr": -1.0,
                "participation.signed_volume_balance": -0.3,
                "mtf.positive_return_fraction": 0.2,
                "mtf.negative_return_fraction": 0.8,
                "mtf.price_above_ema_fraction": 0.2,
                "mtf.price_below_ema_fraction": 0.8,
                "mtf.positive_slope_fraction": 0.2,
                "mtf.negative_slope_fraction": 0.8,
                "baseline.direction": "NEGATIVE",
            },
            (),
            AgentStance.NEGATIVE,
            (TrendState.STRONG_DOWNTREND,),
        ),
        (
            "sideways range",
            {
                "trend.distance_from_ema_percent": 0.0,
                "trend.linear_slope_percent": 0.0,
                "trend.signed_efficiency": 0.0,
                "trend.linear_r2": 0.1,
                "structure.higher_high_fraction": 0.5,
                "structure.higher_low_fraction": 0.5,
                "structure.lower_high_fraction": 0.5,
                "structure.lower_low_fraction": 0.5,
                "indicator.rsi": 50.0,
                "indicator.macd": 0.0,
                "return.percent": 0.0,
                "range.move_over_atr": 0.0,
                "participation.signed_volume_balance": 0.0,
                "mtf.positive_return_fraction": 0.3,
                "mtf.negative_return_fraction": 0.3,
                "mtf.price_above_ema_fraction": 0.3,
                "mtf.price_below_ema_fraction": 0.3,
                "mtf.positive_slope_fraction": 0.3,
                "mtf.negative_slope_fraction": 0.3,
            },
            (),
            AgentStance.NEUTRAL,
            (TrendState.SIDEWAYS, StructureState.MIXED),
        ),
        (
            "bullish trend fading momentum",
            {"indicator.rsi": 40.0, "indicator.macd": -0.3, "return.percent": -1.0},
            (),
            AgentStance.MIXED,
            (MomentumState.FADING_POSITIVE,),
        ),
        (
            "confirmed breakout with volume",
            {
                "breakout.above_prior_high_percent": 1.0,
                "breakout.high_above_prior_high_percent": 1.4,
            },
            (),
            AgentStance.POSITIVE,
            (BreakoutState.CONFIRMED_CLOSE_BREAKOUT,),
        ),
        (
            "wick-only breakout",
            {"breakout.high_above_prior_high_percent": 1.0},
            (),
            AgentStance.POSITIVE,
            (BreakoutState.WICK_ONLY_BREAKOUT,),
        ),
        (
            "confirmed breakdown",
            {
                "trend.distance_from_ema_percent": -2.0,
                "trend.linear_slope_percent": -0.2,
                "trend.signed_efficiency": -0.5,
                "structure.higher_high_fraction": 0.2,
                "structure.higher_low_fraction": 0.2,
                "structure.lower_high_fraction": 0.7,
                "structure.lower_low_fraction": 0.7,
                "breakdown.below_prior_low_percent": 1.0,
                "breakdown.low_below_prior_low_percent": 1.2,
                "indicator.rsi": 38.0,
                "indicator.macd": -0.5,
                "return.percent": -3.0,
                "range.move_over_atr": -1.0,
                "participation.signed_volume_balance": -0.3,
                "mtf.positive_return_fraction": 0.2,
                "mtf.negative_return_fraction": 0.8,
                "mtf.price_above_ema_fraction": 0.2,
                "mtf.price_below_ema_fraction": 0.8,
                "mtf.positive_slope_fraction": 0.2,
                "mtf.negative_slope_fraction": 0.8,
            },
            (),
            AgentStance.NEGATIVE,
            (BreakoutState.CONFIRMED_CLOSE_BREAKDOWN,),
        ),
        (
            "MTF conflict",
            {"mtf.disagreement_fraction": 0.8},
            (),
            AgentStance.POSITIVE,
            (MultiTimeframeState.CONFLICTED,),
        ),
        (
            "extended chase risk",
            {
                "range.move_over_atr": 3.2,
                "trend.distance_from_ema_atr": 3.0,
                "resistance.distance_atr": -0.1,
            },
            (),
            AgentStance.POSITIVE,
            (ExtensionState.EXHAUSTION_RISK,),
        ),
        (
            "early positive opportunity",
            {"range.move_over_atr": 0.4, "trend.distance_from_ema_atr": 0.5},
            (),
            AgentStance.POSITIVE,
            (ExtensionState.EARLY,),
        ),
        (
            "technically mixed",
            {
                "indicator.rsi": 40.0,
                "indicator.macd": -0.4,
                "return.percent": -1.0,
                "participation.signed_volume_balance": -0.3,
            },
            (),
            AgentStance.MIXED,
            (MomentumState.FADING_POSITIVE,),
        ),
        (
            "insufficient core evidence",
            {},
            (
                "trend.linear_slope_percent",
                "trend.signed_efficiency",
                "trend.linear_r2",
                "structure.higher_high_fraction",
                "structure.higher_low_fraction",
                "structure.lower_high_fraction",
                "structure.lower_low_fraction",
                "structure.position_in_rolling_range",
                "structure.range_compression_ratio",
                "structure.latest_bar_range_vs_average",
                "breakout.above_prior_high_percent",
                "breakout.high_above_prior_high_percent",
                "breakdown.below_prior_low_percent",
                "breakdown.low_below_prior_low_percent",
                "support.prior_low",
                "resistance.prior_high",
                "resistance.distance_atr",
                "support.distance_atr",
            ),
            AgentStance.INSUFFICIENT_EVIDENCE,
            (TrendState.INSUFFICIENT_EVIDENCE,),
        ),
        (
            "stale/partial optional evidence",
            {},
            (),
            AgentStance.POSITIVE,
            (TrendState.STRONG_UPTREND,),
        ),
    ),
)
def test_thirteen_synthetic_interpretation_cases(
    case: str,
    overrides: dict[str, str | int | float | bool],
    omit: tuple[str, ...],
    expected_stance: AgentStance,
    checks: tuple[object, ...],
) -> None:
    pack = (
        technical_pack(
            overrides=overrides,
            omit=omit,
            optional_quality=DataQuality.PARTIAL,
            optional_freshness=FreshnessState.STALE,
        )
        if case == "stale/partial optional evidence"
        else technical_pack(overrides=overrides, omit=omit)
    )
    opinion = TechnicalSpecialist().analyze(technical_request(), pack)
    detail = technical_assessment_from_opinion(opinion)

    assert opinion.stance is expected_stance, case
    observed = {
        detail.trend_state,
        detail.momentum_state,
        detail.structure_state,
        detail.breakout_state,
        detail.mtf_state,
        detail.extension_state,
    }
    assert set(checks) <= observed, case
    if expected_stance is AgentStance.INSUFFICIENT_EVIDENCE:
        assert opinion.status is AgentRunStatus.INSUFFICIENT_EVIDENCE
    else:
        assert opinion.status in {AgentRunStatus.SUCCESS, AgentRunStatus.PARTIAL}


@pytest.mark.parametrize(
    ("direction", "technical_overrides", "expected"),
    (
        ("POSITIVE", {}, BaselineAgreement.AGREES),
        (
            "NEGATIVE",
            {
                "trend.distance_from_ema_percent": -2.0,
                "trend.linear_slope_percent": -0.2,
                "trend.signed_efficiency": -0.5,
                "structure.higher_high_fraction": 0.2,
                "structure.higher_low_fraction": 0.2,
                "structure.lower_high_fraction": 0.7,
                "structure.lower_low_fraction": 0.7,
                "indicator.rsi": 38.0,
                "indicator.macd": -0.5,
                "return.percent": -3.0,
                "participation.signed_volume_balance": -0.3,
                "mtf.positive_return_fraction": 0.2,
                "mtf.negative_return_fraction": 0.8,
                "mtf.price_above_ema_fraction": 0.2,
                "mtf.price_below_ema_fraction": 0.8,
                "mtf.positive_slope_fraction": 0.2,
                "mtf.negative_slope_fraction": 0.8,
            },
            BaselineAgreement.AGREES,
        ),
        ("NEUTRAL", {}, BaselineAgreement.DISAGREES),
        (
            "CONFLICTED",
            {"indicator.rsi": 40.0, "indicator.macd": -0.4, "return.percent": -1.0},
            BaselineAgreement.AGREES,
        ),
    ),
)
def test_explicit_baseline_agreement(
    direction: str,
    technical_overrides: dict[str, str | int | float | bool],
    expected: BaselineAgreement,
) -> None:
    opinion = TechnicalSpecialist().analyze(
        technical_request(),
        technical_pack(overrides={"baseline.direction": direction, **technical_overrides}),
    )
    assert opinion.baseline_agreement is expected
    detail = technical_assessment_from_opinion(opinion)
    assert detail.baseline_direction is not None
    assert detail.baseline_direction.value == direction
    assert detail.baseline_opportunity_score == 72.0


def test_high_rsi_is_positive_context_not_an_automatic_bearish_signal() -> None:
    opinion = TechnicalSpecialist().analyze(
        technical_request(), technical_pack(overrides={"indicator.rsi": 78.0})
    )
    detail = technical_assessment_from_opinion(opinion)

    assert detail.momentum_state in {MomentumState.POSITIVE, MomentumState.ACCELERATING}
    assert opinion.stance is AgentStance.POSITIVE


def test_wick_only_break_is_not_close_confirmation() -> None:
    opinion = TechnicalSpecialist().analyze(
        technical_request(),
        technical_pack(overrides={"breakout.high_above_prior_high_percent": 1.0}),
    )
    detail = technical_assessment_from_opinion(opinion)

    assert detail.breakout_state is BreakoutState.WICK_ONLY_BREAKOUT
    assert "BREAKOUT_WICK_ONLY" in opinion.reason_codes
    assert "BREAKOUT_CONFIRMED_CLOSE" not in opinion.reason_codes
