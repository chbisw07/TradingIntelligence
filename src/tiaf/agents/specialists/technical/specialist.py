"""Deterministic evidence-grounded Technical / Market-Structure specialist."""

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from pydantic import ValidationError

from tiaf.agents.budget import AgentUsage
from tiaf.agents.enums import (
    AgentCapability,
    AgentRunStatus,
    AgentStance,
    BaselineAgreement,
    CitationRole,
    ClaimKind,
    EvidenceImportance,
    SpecialistCostTier,
    SpecialistId,
)
from tiaf.agents.evidence import (
    AgentEvidencePack,
    AgentEvidenceReference,
    EvidenceCitation,
    EvidenceClaim,
    EvidenceFact,
    MissingEvidenceRequest,
)
from tiaf.agents.models import (
    AgentConfidence,
    AgentOpinionV2,
    AgentRequest,
    PolicyDerivedConfidence,
    SpecialistCapability,
)
from tiaf.baseline.enums import BaselineDirection, CandidateClass
from tiaf.context import EvidenceStatus
from tiaf.contracts import DataQuality, EvidenceType, FreshnessState
from tiaf.data.enums import InstrumentType

from .enums import (
    BreakoutState,
    ExtensionState,
    MomentumState,
    MultiTimeframeState,
    ParticipationState,
    RemainingRoomState,
    StructureState,
    TechnicalReasonCode,
    TrendState,
    VolatilityState,
)
from .models import TechnicalAssessment, TechnicalContradiction, TechnicalInvalidation
from .policy import TechnicalInterpretationPolicy, default_technical_policy

SPECIALIST_VERSION = "1.0"
TECHNICAL_DETAIL_SCHEMA = "tiaf.technical-assessment/1.0"


@dataclass(frozen=True)
class _FactRecord:
    reference: AgentEvidenceReference
    fact: EvidenceFact


@dataclass(frozen=True)
class _Dimension:
    name: str
    state: str
    sign: int
    records: tuple[_FactRecord, ...]
    reason_codes: tuple[TechnicalReasonCode, ...] = ()


class _FactBook:
    def __init__(self, pack: AgentEvidencePack, interval_priority: tuple[str, ...]) -> None:
        records = tuple(
            _FactRecord(reference, fact)
            for reference in pack.references
            if reference.availability
            in {EvidenceStatus.AVAILABLE, EvidenceStatus.PARTIAL, EvidenceStatus.STALE}
            for fact in reference.facts
        )
        self._records = tuple(sorted(records, key=lambda item: item.fact.fact_id))
        self._interval_priority = {
            interval: index for index, interval in enumerate(interval_priority)
        }

    def records(self, *metric_ids: str) -> tuple[_FactRecord, ...]:
        return tuple(item for item in self._records if item.fact.metric_id in metric_ids)

    def select(self, metric_id: str, *, output_name: str | None = None) -> _FactRecord | None:
        matches = tuple(
            item
            for item in self._records
            if item.fact.metric_id == metric_id
            and (output_name is None or item.fact.output_name == output_name)
        )
        if not matches:
            return None
        return min(
            matches,
            key=lambda item: (
                self._interval_priority.get(item.fact.interval or "", 10_000),
                item.fact.fact_id,
            ),
        )

    def number(self, metric_id: str, *, output_name: str | None = None) -> float | None:
        selected = self.select(metric_id, output_name=output_name)
        if selected is None or isinstance(selected.fact.value, (bool, str)):
            return None
        return float(selected.fact.value)

    def text(self, metric_id: str) -> str | None:
        selected = self.select(metric_id)
        return selected.fact.value if selected and isinstance(selected.fact.value, str) else None


class TechnicalSpecialist:
    """Interpret supplied A2 facts without fetching or recalculating them."""

    def __init__(
        self,
        policy: TechnicalInterpretationPolicy | None = None,
    ) -> None:
        self._policy = policy or default_technical_policy()

    def capability(self) -> SpecialistCapability:
        """Declare the narrow A3.3 identity, evidence, cost, and prohibitions."""
        return SpecialistCapability(
            specialist=SpecialistId.TECHNICAL,
            specialist_version=SPECIALIST_VERSION,
            display_name="Technical / Market-Structure Specialist",
            description="Interprets supplied A2 technical facts without recalculation.",
            supported_instrument_types=(
                InstrumentType.EQUITY,
                InstrumentType.INDEX,
            ),
            required_evidence_types=(EvidenceType.TECHNICAL,),
            optional_evidence_types=(
                EvidenceType.MARKET,
                EvidenceType.VOLUME,
                EvidenceType.VOLATILITY,
                EvidenceType.RELATIVE_STRENGTH,
            ),
            allowed_capabilities=(AgentCapability.READ_A2_EVIDENCE,),
            supports_no_llm=True,
            cost_tier=SpecialistCostTier.LOW,
            prohibitions=(
                "NO_A2_RECOMPUTATION",
                "NO_PROVIDER_OR_NETWORK_ACCESS",
                "NO_MODEL_SDK_ACCESS",
                "NO_TRADING_OR_POSITION_ACTIONS",
                "NO_OPTION_EXPRESSION",
                "NO_ARBITRATION",
            ),
        )

    def analyze(
        self,
        request: AgentRequest,
        evidence: AgentEvidencePack,
    ) -> AgentOpinionV2:
        """Produce a replayable deterministic interpretation of supplied scalar facts."""
        self._validate_identity(request, evidence)
        intervals = (
            self._policy.day_interval_priority
            if request.trade_style is not None and request.trade_style.value == "DAY"
            else self._policy.positional_interval_priority
        )
        facts = _FactBook(evidence, intervals)
        trend = self._trend(facts)
        breakout = self._breakout(facts)
        structure = self._structure(facts, breakout)
        momentum = self._momentum(facts, trend.sign)
        participation = self._participation(facts, trend.sign)
        volatility = self._volatility(facts)
        mtf = self._mtf(facts)
        room = self._remaining_room(facts, trend.sign)
        extension = self._extension(facts, participation, room)
        dimensions = (trend, momentum, structure, participation, volatility, mtf)
        core_trend_metrics = {
            item.fact.metric_id
            for item in facts.records(
                "trend.distance_from_ema_percent",
                "trend.ema_spread_percent",
                "trend.linear_slope_percent",
                "trend.signed_efficiency",
                "trend.linear_r2",
            )
        }
        core_structure = facts.records(
            "structure.higher_high_fraction",
            "structure.higher_low_fraction",
            "structure.lower_high_fraction",
            "structure.lower_low_fraction",
            "structure.position_in_rolling_range",
            "structure.position_vs_prior_range",
            "structure.range_compression_ratio",
            "structure.latest_bar_range_vs_average",
            "breakout.above_prior_high_percent",
            "breakout.high_above_prior_high_percent",
            "breakdown.below_prior_low_percent",
            "breakdown.low_below_prior_low_percent",
        )
        core_complete = len(core_trend_metrics) >= 2 and bool(core_structure)
        stance = self._stance(dimensions) if core_complete else AgentStance.INSUFFICIENT_EVIDENCE
        contradictions = self._contradictions(dimensions)
        invalidations = self._invalidations(facts, trend.sign)
        missing = self._missing_evidence(request, evidence, facts, core_complete)
        reasons = self._reason_codes(
            dimensions,
            breakout,
            extension,
            room,
            contradictions,
            evidence,
            core_complete,
            missing,
            trend.sign,
        )
        baseline_direction, baseline_score, baseline_class, baseline_records = (
            self._baseline(facts)
        )
        baseline_dimension = _Dimension(
            "A2_BASELINE",
            baseline_direction.value if baseline_direction is not None else "UNAVAILABLE",
            0,
            baseline_records,
        )
        baseline_agreement = self._baseline_agreement(stance, baseline_direction)
        internal_agreement = self._internal_agreement(dimensions)
        confidence_value = self._confidence(
            evidence,
            internal_agreement,
            core_complete=core_complete,
        )
        assessment = TechnicalAssessment(
            assessment_id=f"{request.run_id}:technical-assessment",
            specialist_version=SPECIALIST_VERSION,
            policy_id=self._policy.policy_id,
            policy_version=self._policy.policy_version,
            stance=stance,
            trend_state=TrendState(trend.state),
            momentum_state=MomentumState(momentum.state),
            structure_state=StructureState(structure.state),
            breakout_state=BreakoutState(breakout.state),
            participation_state=ParticipationState(participation.state),
            volatility_state=VolatilityState(volatility.state),
            mtf_state=MultiTimeframeState(mtf.state),
            extension_state=extension,
            remaining_room=room,
            invalidations=invalidations,
            contradictions=contradictions,
            positive_timeframes=self._timeframes(facts, positive=True),
            negative_timeframes=self._timeframes(facts, positive=False),
            evidence_ids_by_dimension=tuple(
                (item.name, self._reference_ids(item.records))
                for item in (*dimensions, breakout, baseline_dimension)
            ),
            evidence_coverage=evidence.evidence_coverage,
            internal_agreement=internal_agreement,
            confidence_basis=(
                "dimension_group_agreement_not_individual_indicator_count",
                "evidence_coverage_quality_and_freshness",
                "not_probability_of_market_success",
            ),
            reason_codes=reasons,
            baseline_direction=baseline_direction,
            baseline_opportunity_score=baseline_score,
            baseline_candidate_class=baseline_class,
            created_at=request.created_at,
        )
        if not core_complete:
            return self._insufficient_opinion(
                request,
                evidence,
                assessment,
                missing,
                baseline_agreement,
            )
        all_dimensions = (*dimensions, breakout, baseline_dimension)
        supporting_ids, contradictory_ids = self._classify_references(
            all_dimensions,
            stance,
        )
        claims = self._claims(all_dimensions, supporting_ids, contradictory_ids)
        status = (
            AgentRunStatus.PARTIAL
            if missing
            or evidence.overall_quality is not DataQuality.GOOD
            or evidence.overall_freshness is not FreshnessState.FRESH
            else AgentRunStatus.SUCCESS
        )
        caveat_items: list[str] = []
        if missing:
            caveat_items.append("Optional technical evidence is missing")
        if evidence.overall_quality is not DataQuality.GOOD:
            caveat_items.append(f"Evidence quality is {evidence.overall_quality.value}")
        if evidence.overall_freshness is not FreshnessState.FRESH:
            caveat_items.append(
                f"Evidence freshness is {evidence.overall_freshness.value}"
            )
        caveats = tuple(dict.fromkeys(caveat_items))
        risks = tuple(
            item
            for item in (
                "Move is extended; this is chase risk, not a reversal forecast"
                if extension in {ExtensionState.EXTENDED, ExtensionState.EXHAUSTION_RISK}
                else None,
                "Nearby opposing structure limits remaining technical room"
                if room in {RemainingRoomState.LIMITED, RemainingRoomState.MINIMAL}
                else None,
                "Technical dimensions conflict"
                if contradictions
                else None,
            )
            if item is not None
        )
        return AgentOpinionV2(
            opinion_id=f"{request.run_id}:technical-opinion",
            request_id=request.request_id,
            run_id=request.run_id,
            specialist=SpecialistId.TECHNICAL,
            specialist_version=SPECIALIST_VERSION,
            subject=request.subject,
            horizon=request.horizon,
            stance=stance,
            status=status,
            confidence=AgentConfidence(
                evidence_coverage=evidence.evidence_coverage,
                evidence_quality=evidence.overall_quality,
                policy_derived=PolicyDerivedConfidence(
                    value=confidence_value,
                    policy_id=self._policy.policy_id,
                    policy_version=self._policy.policy_version,
                ),
            ),
            summary=self._summary(assessment),
            reason_codes=tuple(item.value for item in reasons),
            evidence_claims=claims,
            supporting_evidence_ids=supporting_ids,
            contradictory_evidence_ids=contradictory_ids,
            missing_evidence=missing,
            risks=risks,
            caveats=caveats,
            deterministic_baseline_reference=request.deterministic_baseline_reference,
            baseline_agreement=baseline_agreement,
            evidence_fingerprint=request.evidence_fingerprint,
            evidence_quality=evidence.overall_quality,
            evidence_freshness=evidence.overall_freshness,
            policy_version=self._policy.policy_version,
            usage=AgentUsage(),
            produced_at=request.created_at,
            specialist_detail_schema_id=TECHNICAL_DETAIL_SCHEMA,
            specialist_detail_json=assessment.canonical_json(),
        )

    @staticmethod
    def _validate_identity(request: AgentRequest, evidence: AgentEvidencePack) -> None:
        if request.specialist is not SpecialistId.TECHNICAL:
            raise ValueError("TechnicalSpecialist requires TECHNICAL request identity")
        if AgentCapability.READ_A2_EVIDENCE not in request.allowed_capabilities:
            raise ValueError("TechnicalSpecialist requires READ_A2_EVIDENCE authorization")
        if (
            evidence.request_id != request.request_id
            or evidence.subject != request.subject
            or evidence.evidence_fingerprint != request.evidence_fingerprint
            or evidence.deterministic_assessment_id
            != request.deterministic_baseline_reference
        ):
            raise ValueError("technical evidence does not preserve request/A2 identity")

    def _trend(self, facts: _FactBook) -> _Dimension:
        ema_record = facts.select("trend.distance_from_ema_percent") or facts.select(
            "trend.ema_spread_percent"
        )
        selected = tuple(
            item
            for item in (
                ema_record,
                facts.select("trend.linear_slope_percent"),
                facts.select("trend.signed_efficiency"),
                facts.select("trend.linear_r2"),
                facts.select("structure.higher_high_fraction"),
                facts.select("structure.higher_low_fraction"),
                facts.select("structure.lower_high_fraction"),
                facts.select("structure.lower_low_fraction"),
            )
            if item is not None
        )
        if len(selected) < 2:
            return _Dimension("TREND", TrendState.INSUFFICIENT_EVIDENCE, 0, selected)
        slope = facts.number("trend.linear_slope_percent")
        ema = facts.number("trend.distance_from_ema_percent")
        if ema is None:
            ema = facts.number("trend.ema_spread_percent")
        efficiency = facts.number("trend.signed_efficiency")
        r2 = facts.number("trend.linear_r2")
        hh = facts.number("structure.higher_high_fraction")
        hl = facts.number("structure.higher_low_fraction")
        lh = facts.number("structure.lower_high_fraction")
        ll = facts.number("structure.lower_low_fraction")
        votes: list[int] = []
        if slope is not None and abs(slope) >= self._policy.slope_direction_threshold:
            votes.append(1 if slope > 0 else -1)
        if ema is not None and ema != 0:
            votes.append(1 if ema > 0 else -1)
        if efficiency is not None and efficiency != 0:
            votes.append(1 if efficiency > 0 else -1)
        if None not in (hh, hl, lh, ll):
            assert hh is not None and hl is not None
            assert lh is not None and ll is not None
            positive = hh + hl
            negative = lh + ll
            if abs(positive - negative) >= self._policy.structure_margin:
                votes.append(1 if positive > negative else -1)
        positives, negatives = votes.count(1), votes.count(-1)
        strong = (
            r2 is not None
            and r2 >= self._policy.trend_r2_strength_threshold
            and efficiency is not None
            and abs(efficiency) >= self._policy.efficiency_strength_threshold
        )
        if positives and negatives:
            return _Dimension(
                "TREND", TrendState.MIXED, 0, selected, (TechnicalReasonCode.TREND_WEAK,)
            )
        if positives >= 3 and strong:
            state = TrendState.STRONG_UPTREND
        elif positives >= 2:
            state = TrendState.MODERATE_UPTREND
        elif positives == 1:
            state = TrendState.WEAK_UPTREND
        elif negatives >= 3 and strong:
            state = TrendState.STRONG_DOWNTREND
        elif negatives >= 2:
            state = TrendState.MODERATE_DOWNTREND
        elif negatives == 1:
            state = TrendState.WEAK_DOWNTREND
        else:
            state = TrendState.SIDEWAYS
        sign = 1 if positives else -1 if negatives else 0
        reason = (
            TechnicalReasonCode.TREND_UP_ALIGNED
            if sign > 0
            else TechnicalReasonCode.TREND_DOWN_ALIGNED
            if sign < 0
            else TechnicalReasonCode.TREND_WEAK
        )
        return _Dimension("TREND", state, sign, selected, (reason,))

    def _momentum(self, facts: _FactBook, trend_sign: int) -> _Dimension:
        fixed = tuple(
            item
            for item in (
                facts.select("indicator.rsi", output_name="rsi"),
                facts.select("indicator.macd", output_name="histogram"),
                facts.select("range.move_over_atr"),
            )
            if item is not None
        )
        selected = (*fixed, *facts.records("return.percent"))
        if not selected:
            return _Dimension(
                "MOMENTUM", MomentumState.INSUFFICIENT_EVIDENCE, 0, ()
            )
        votes: list[int] = []
        rsi = facts.number("indicator.rsi", output_name="rsi")
        macd = facts.number("indicator.macd", output_name="histogram")
        move_atr = facts.number("range.move_over_atr")
        if rsi is not None:
            if rsi >= self._policy.rsi_positive:
                votes.append(1)
            elif rsi <= self._policy.rsi_negative:
                votes.append(-1)
        return_values = tuple(
            float(item.fact.value)
            for item in facts.records("return.percent")
            if not isinstance(item.fact.value, (bool, str))
        )
        for value in (macd, *return_values, move_atr):
            if value is not None and value != 0:
                votes.append(1 if value > 0 else -1)
        positives, negatives = votes.count(1), votes.count(-1)
        if positives == negatives and positives:
            state, sign = MomentumState.MIXED, 0
        elif positives > negatives:
            state, sign = (
                (MomentumState.ACCELERATING, 1)
                if positives >= 3 and (move_atr or 0) >= 1
                else (MomentumState.POSITIVE, 1)
            )
        elif negatives > positives:
            state, sign = (
                (MomentumState.ACCELERATING_NEGATIVE, -1)
                if negatives >= 3 and (move_atr or 0) <= -1
                else (MomentumState.NEGATIVE, -1)
            )
        else:
            state, sign = MomentumState.NEUTRAL, 0
        if trend_sign > 0 and sign <= 0:
            state = MomentumState.FADING_POSITIVE
        elif trend_sign < 0 and sign >= 0:
            state = MomentumState.FADING_NEGATIVE
        reason = (
            TechnicalReasonCode.MOMENTUM_POSITIVE
            if sign > 0
            else TechnicalReasonCode.MOMENTUM_NEGATIVE
            if sign < 0
            else TechnicalReasonCode.MOMENTUM_FADING
        )
        return _Dimension("MOMENTUM", state, sign, selected, (reason,))

    def _breakout(self, facts: _FactBook) -> _Dimension:
        metrics = (
            "breakout.above_prior_high_percent",
            "breakout.high_above_prior_high_percent",
            "breakdown.below_prior_low_percent",
            "breakdown.low_below_prior_low_percent",
        )
        selected = tuple(item for metric in metrics if (item := facts.select(metric)))
        if not selected:
            return _Dimension(
                "BREAKOUT_STATE", BreakoutState.INSUFFICIENT_EVIDENCE, 0, ()
            )
        close_up = facts.number(metrics[0]) or 0
        wick_up = facts.number(metrics[1]) or 0
        close_down = facts.number(metrics[2]) or 0
        wick_down = facts.number(metrics[3]) or 0
        if (close_up > 0 or wick_up > 0) and (close_down > 0 or wick_down > 0):
            return _Dimension("BREAKOUT_STATE", BreakoutState.CONFLICTED, 0, selected)
        if close_up > 0:
            return _Dimension(
                "BREAKOUT_STATE",
                BreakoutState.CONFIRMED_CLOSE_BREAKOUT,
                1,
                selected,
                (TechnicalReasonCode.BREAKOUT_CONFIRMED_CLOSE,),
            )
        if wick_up > 0:
            return _Dimension(
                "BREAKOUT_STATE",
                BreakoutState.WICK_ONLY_BREAKOUT,
                0,
                selected,
                (TechnicalReasonCode.BREAKOUT_WICK_ONLY,),
            )
        if close_down > 0:
            return _Dimension(
                "BREAKOUT_STATE",
                BreakoutState.CONFIRMED_CLOSE_BREAKDOWN,
                -1,
                selected,
                (TechnicalReasonCode.BREAKDOWN_CONFIRMED_CLOSE,),
            )
        if wick_down > 0:
            return _Dimension(
                "BREAKOUT_STATE",
                BreakoutState.WICK_ONLY_BREAKDOWN,
                0,
                selected,
                (TechnicalReasonCode.BREAKDOWN_WICK_ONLY,),
            )
        return _Dimension("BREAKOUT_STATE", BreakoutState.NO_BREAK, 0, selected)

    def _structure(self, facts: _FactBook, breakout: _Dimension) -> _Dimension:
        records = (
            *facts.records(
                    "structure.higher_high_fraction",
                    "structure.higher_low_fraction",
                    "structure.lower_high_fraction",
                    "structure.lower_low_fraction",
                    "structure.position_in_rolling_range",
                    "structure.position_vs_prior_range",
                    "structure.range_compression_ratio",
                    "structure.latest_bar_range_vs_average",
                ),
            *breakout.records,
        )
        seen: set[tuple[str, str]] = set()
        unique_records: list[_FactRecord] = []
        for item in records:
            key = (item.reference.evidence_id, item.fact.fact_id)
            if key not in seen:
                seen.add(key)
                unique_records.append(item)
        selected = tuple(unique_records)
        if not selected:
            return _Dimension(
                "STRUCTURE", StructureState.INSUFFICIENT_EVIDENCE, 0, ()
            )
        if breakout.state is BreakoutState.CONFIRMED_CLOSE_BREAKOUT:
            return _Dimension("STRUCTURE", StructureState.BREAKOUT_ATTEMPT, 1, selected)
        if breakout.state is BreakoutState.CONFIRMED_CLOSE_BREAKDOWN:
            return _Dimension("STRUCTURE", StructureState.BREAKDOWN_ATTEMPT, -1, selected)
        compression = facts.number("structure.range_compression_ratio")
        expansion = facts.number("structure.latest_bar_range_vs_average")
        if compression is not None and compression < self._policy.compression_ratio:
            return _Dimension(
                "STRUCTURE",
                StructureState.COMPRESSION,
                0,
                selected,
                (TechnicalReasonCode.RANGE_COMPRESSED,),
            )
        if expansion is not None and expansion > self._policy.expansion_ratio:
            return _Dimension(
                "STRUCTURE",
                StructureState.EXPANSION,
                0,
                selected,
                (TechnicalReasonCode.RANGE_EXPANDING,),
            )
        hh = facts.number("structure.higher_high_fraction")
        hl = facts.number("structure.higher_low_fraction")
        lh = facts.number("structure.lower_high_fraction")
        ll = facts.number("structure.lower_low_fraction")
        if None not in (hh, hl, lh, ll):
            assert hh is not None and hl is not None
            assert lh is not None and ll is not None
            positive, negative = hh + hl, lh + ll
            if positive - negative >= self._policy.structure_margin:
                return _Dimension("STRUCTURE", StructureState.BULLISH_STRUCTURE, 1, selected)
            if negative - positive >= self._policy.structure_margin:
                return _Dimension("STRUCTURE", StructureState.BEARISH_STRUCTURE, -1, selected)
            if positive and negative:
                return _Dimension("STRUCTURE", StructureState.MIXED, 0, selected)
        return _Dimension("STRUCTURE", StructureState.RANGE_BOUND, 0, selected)

    def _participation(self, facts: _FactBook, trend_sign: int) -> _Dimension:
        selected = facts.records(
            "participation.signed_volume_balance",
            "participation.return_volume_alignment",
            "volume.relative",
            "volume.coefficient_of_variation",
        )
        if not selected:
            return _Dimension(
                "PARTICIPATION", ParticipationState.INSUFFICIENT_EVIDENCE, 0, ()
            )
        balance = facts.number("participation.signed_volume_balance")
        relative = facts.number("volume.relative")
        if relative is not None and relative >= self._policy.unusual_relative_volume_high:
            unusual = ParticipationState.UNUSUALLY_HIGH
        elif relative is not None and relative <= self._policy.unusual_relative_volume_low:
            unusual = ParticipationState.UNUSUALLY_LOW
        else:
            unusual = None
        sign = (
            1
            if balance is not None and balance >= self._policy.participation_threshold
            else -1
            if balance is not None and balance <= -self._policy.participation_threshold
            else 0
        )
        if trend_sign > 0 and sign < 0:
            state = ParticipationState.CONTRADICTS_POSITIVE_MOVE
        elif trend_sign < 0 and sign > 0:
            state = ParticipationState.CONTRADICTS_NEGATIVE_MOVE
        elif sign > 0:
            state = ParticipationState.CONFIRMS_POSITIVE
        elif sign < 0:
            state = ParticipationState.CONFIRMS_NEGATIVE
        else:
            state = unusual or ParticipationState.NEUTRAL
        reason = (
            TechnicalReasonCode.VOLUME_DIVERGES
            if "CONTRADICTS" in state.value
            else TechnicalReasonCode.VOLUME_CONFIRMS
            if sign
            else None
        )
        return _Dimension(
            "PARTICIPATION",
            state,
            sign,
            selected,
            (reason,) if reason else (),
        )

    def _volatility(self, facts: _FactBook) -> _Dimension:
        selected = facts.records(
            "volatility.atr_percent",
            "volatility.realized",
            "structure.range_compression_ratio",
            "structure.latest_bar_range_vs_average",
        )
        if not selected:
            return _Dimension(
                "VOLATILITY_CONTEXT", VolatilityState.INSUFFICIENT_EVIDENCE, 0, ()
            )
        compression = facts.number("structure.range_compression_ratio")
        expansion = facts.number("structure.latest_bar_range_vs_average")
        atr = facts.number("volatility.atr_percent")
        if compression is not None and compression < self._policy.compression_ratio:
            state = VolatilityState.COMPRESSING
        elif expansion is not None and expansion > self._policy.expansion_ratio:
            state = VolatilityState.EXPANDING
        elif atr is None:
            state = VolatilityState.MIXED
        elif atr < self._policy.atr_low_percent:
            state = VolatilityState.LOW
        elif atr < self._policy.atr_elevated_percent:
            state = VolatilityState.NORMAL
        elif atr < self._policy.atr_extreme_percent:
            state = VolatilityState.ELEVATED
        else:
            state = VolatilityState.EXTREME
        reason = (
            (TechnicalReasonCode.VOLATILITY_ELEVATED,)
            if state in {VolatilityState.ELEVATED, VolatilityState.EXTREME}
            else ()
        )
        return _Dimension("VOLATILITY_CONTEXT", state, 0, selected, reason)

    def _mtf(self, facts: _FactBook) -> _Dimension:
        selected = facts.records(
            "mtf.positive_return_fraction",
            "mtf.negative_return_fraction",
            "mtf.price_above_ema_fraction",
            "mtf.price_below_ema_fraction",
            "mtf.positive_slope_fraction",
            "mtf.negative_slope_fraction",
            "mtf.disagreement_fraction",
        )
        if not selected:
            return _Dimension(
                "MTF_ALIGNMENT", MultiTimeframeState.INSUFFICIENT_EVIDENCE, 0, ()
            )
        disagreement = facts.number("mtf.disagreement_fraction")
        positive = max(
            value
            for value in (
                facts.number("mtf.positive_return_fraction") or 0,
                facts.number("mtf.price_above_ema_fraction") or 0,
                facts.number("mtf.positive_slope_fraction") or 0,
            )
        )
        negative = max(
            value
            for value in (
                facts.number("mtf.negative_return_fraction") or 0,
                facts.number("mtf.price_below_ema_fraction") or 0,
                facts.number("mtf.negative_slope_fraction") or 0,
            )
        )
        if disagreement is not None and disagreement >= self._policy.mtf_conflict_fraction:
            state, sign = MultiTimeframeState.CONFLICTED, 0
        elif positive >= self._policy.mtf_alignment_fraction and negative < positive:
            state, sign = MultiTimeframeState.ALIGNED_POSITIVE, 1
        elif negative >= self._policy.mtf_alignment_fraction and positive < negative:
            state, sign = MultiTimeframeState.ALIGNED_NEGATIVE, -1
        else:
            state, sign = MultiTimeframeState.MIXED, 0
        reason = (
            TechnicalReasonCode.MTF_ALIGNED
            if sign
            else TechnicalReasonCode.MTF_MIXED
        )
        return _Dimension("MTF_ALIGNMENT", state, sign, selected, (reason,))

    def _extension(
        self,
        facts: _FactBook,
        participation: _Dimension,
        room: RemainingRoomState,
    ) -> ExtensionState:
        move = facts.number("range.move_over_atr")
        ema_atr = facts.number("trend.distance_from_ema_atr")
        magnitude = max(abs(value) for value in (move, ema_atr) if value is not None) if (
            move is not None or ema_atr is not None
        ) else None
        if magnitude is None:
            return ExtensionState.UNKNOWN
        if magnitude >= self._policy.exhaustion_move_atr and (
            "CONTRADICTS" in participation.state
            or room is RemainingRoomState.MINIMAL
        ):
            return ExtensionState.EXHAUSTION_RISK
        if magnitude >= self._policy.extended_move_atr:
            return ExtensionState.EXTENDED
        if magnitude >= self._policy.mature_move_atr:
            return ExtensionState.MATURE
        if magnitude >= 0.75:
            return ExtensionState.DEVELOPING
        return ExtensionState.EARLY

    def _remaining_room(self, facts: _FactBook, trend_sign: int) -> RemainingRoomState:
        if trend_sign == 0:
            return RemainingRoomState.UNKNOWN
        distance = (
            facts.number("resistance.distance_atr")
            if trend_sign >= 0
            else facts.number("support.distance_atr")
        )
        if distance is None:
            return RemainingRoomState.UNKNOWN
        room = -distance if trend_sign >= 0 else distance
        if room >= self._policy.room_large_atr:
            return RemainingRoomState.LARGE
        if room >= self._policy.room_moderate_atr:
            return RemainingRoomState.MODERATE
        if room >= self._policy.room_minimal_atr:
            return RemainingRoomState.LIMITED
        return RemainingRoomState.MINIMAL

    @staticmethod
    def _stance(dimensions: tuple[_Dimension, ...]) -> AgentStance:
        directional = tuple(item.sign for item in dimensions if item.name != "VOLATILITY_CONTEXT")
        positive, negative = directional.count(1), directional.count(-1)
        if positive >= 3 and negative == 0:
            return AgentStance.POSITIVE
        if negative >= 3 and positive == 0:
            return AgentStance.NEGATIVE
        if positive and negative:
            return AgentStance.MIXED
        return AgentStance.NEUTRAL

    @staticmethod
    def _internal_agreement(dimensions: tuple[_Dimension, ...]) -> float:
        signs = tuple(
            item.sign
            for item in dimensions
            if item.records and item.name != "VOLATILITY_CONTEXT"
        )
        if not signs:
            return 0.0
        return round(max(signs.count(1), signs.count(-1), signs.count(0)) / len(signs), 4)

    @staticmethod
    def _reference_ids(records: Iterable[_FactRecord]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(item.reference.evidence_id for item in records))

    def _contradictions(
        self,
        dimensions: tuple[_Dimension, ...],
    ) -> tuple[TechnicalContradiction, ...]:
        positive = tuple(item for item in dimensions if item.sign > 0)
        negative = tuple(item for item in dimensions if item.sign < 0)
        if not positive or not negative:
            return ()
        return (
            TechnicalContradiction(
                code="DIRECTIONAL_DIMENSION_CONFLICT",
                description=(
                    f"Positive dimensions {', '.join(item.name for item in positive)} conflict "
                    f"with negative dimensions {', '.join(item.name for item in negative)}."
                ),
                evidence_ids=self._reference_ids(
                    record for item in (*positive, *negative) for record in item.records
                ),
            ),
        )

    @staticmethod
    def _invalidations(facts: _FactBook, trend_sign: int) -> tuple[TechnicalInvalidation, ...]:
        if trend_sign == 0:
            return ()
        metric = "support.prior_low" if trend_sign >= 0 else "resistance.prior_high"
        selected = facts.select(metric)
        if selected is None or isinstance(selected.fact.value, (bool, str)):
            return ()
        direction = "below" if trend_sign >= 0 else "above"
        label = "support" if trend_sign >= 0 else "resistance"
        return (
            TechnicalInvalidation(
                condition=(
                    f"A completed close {direction} the supplied prior {label} would "
                    "invalidate the current structural interpretation."
                ),
                evidence_id=selected.reference.evidence_id,
                fact_id=selected.fact.fact_id,
                supplied_level=float(selected.fact.value),
            ),
        )

    def _missing_evidence(
        self,
        request: AgentRequest,
        pack: AgentEvidencePack,
        facts: _FactBook,
        core_complete: bool,
    ) -> tuple[MissingEvidenceRequest, ...]:
        missing = list(pack.missing_evidence)
        requirements = (
            (
                not core_complete,
                "core",
                EvidenceType.TECHNICAL,
                EvidenceImportance.REQUIRED,
                "Core A2 trend/structure facts are inadequate",
            ),
            (
                not facts.records("indicator.rsi", "indicator.macd", "return.percent"),
                "momentum",
                EvidenceType.TECHNICAL,
                EvidenceImportance.OPTIONAL,
                "Optional A2 momentum evidence is unavailable",
            ),
            (
                not facts.records("participation.signed_volume_balance", "volume.relative"),
                "participation",
                EvidenceType.VOLUME,
                EvidenceImportance.OPTIONAL,
                "Optional A2 participation evidence is unavailable",
            ),
            (
                not facts.records("volatility.atr_percent", "volatility.realized"),
                "volatility",
                EvidenceType.VOLATILITY,
                EvidenceImportance.OPTIONAL,
                "Optional A2 volatility evidence is unavailable",
            ),
            (
                not facts.records("mtf.positive_return_fraction", "mtf.negative_return_fraction"),
                "mtf",
                EvidenceType.TECHNICAL,
                EvidenceImportance.OPTIONAL,
                "Optional supplied A2 multi-timeframe evidence is unavailable",
            ),
            (
                len(
                    facts.records(
                        "baseline.direction",
                        "baseline.opportunity_score",
                        "baseline.candidate_class",
                    )
                )
                < 3,
                "baseline",
                EvidenceType.OTHER,
                EvidenceImportance.OPTIONAL,
                "Optional A2 deterministic baseline comparison is unavailable",
            ),
        )
        existing = {item.missing_request_id for item in missing}
        for needed, suffix, evidence_type, importance, reason in requirements:
            missing_id = f"{request.request_id}:missing:{suffix}"
            if needed and missing_id not in existing:
                missing.append(
                    MissingEvidenceRequest(
                        missing_request_id=missing_id,
                        evidence_type=evidence_type,
                        capability=AgentCapability.READ_A2_EVIDENCE,
                        subject=request.subject,
                        reason=reason,
                        importance=importance,
                        required_freshness=FreshnessState.FRESH,
                        requested_at=request.created_at,
                    )
                )
        return tuple(missing)

    @staticmethod
    def _baseline(
        facts: _FactBook,
    ) -> tuple[
        BaselineDirection | None,
        float | None,
        CandidateClass | None,
        tuple[_FactRecord, ...],
    ]:
        records = facts.records(
            "baseline.direction",
            "baseline.opportunity_score",
            "baseline.candidate_class",
        )
        direction = facts.text("baseline.direction")
        candidate = facts.text("baseline.candidate_class")
        score = facts.number("baseline.opportunity_score")
        try:
            parsed_direction = BaselineDirection(direction) if direction else None
            parsed_candidate = CandidateClass(candidate) if candidate else None
        except ValueError:
            return None, None, None, records
        if parsed_direction is None or parsed_candidate is None or score is None:
            return None, None, None, records
        return parsed_direction, score, parsed_candidate, records

    @staticmethod
    def _baseline_agreement(
        stance: AgentStance,
        baseline: BaselineDirection | None,
    ) -> BaselineAgreement:
        if baseline is None or stance is AgentStance.INSUFFICIENT_EVIDENCE:
            return BaselineAgreement.NOT_COMPARABLE
        pairs = {
            BaselineDirection.POSITIVE: AgentStance.POSITIVE,
            BaselineDirection.NEGATIVE: AgentStance.NEGATIVE,
            BaselineDirection.NEUTRAL: AgentStance.NEUTRAL,
            BaselineDirection.CONFLICTED: AgentStance.MIXED,
        }
        if pairs[baseline] is stance:
            return BaselineAgreement.AGREES
        if baseline is BaselineDirection.CONFLICTED or stance is AgentStance.MIXED:
            return BaselineAgreement.PARTIALLY_AGREES
        return BaselineAgreement.DISAGREES

    def _confidence(
        self,
        evidence: AgentEvidencePack,
        agreement: float,
        *,
        core_complete: bool,
    ) -> float:
        if not core_complete:
            return 0.0
        quality_factor = {
            DataQuality.GOOD: 1.0,
            DataQuality.PARTIAL: 0.8,
            DataQuality.DEGRADED: 0.6,
            DataQuality.UNAVAILABLE: 0.0,
        }[evidence.overall_quality]
        freshness_factor = {
            FreshnessState.FRESH: 1.0,
            FreshnessState.AGING: 0.8,
            FreshnessState.STALE: 0.5,
            FreshnessState.UNKNOWN: 0.6,
        }[evidence.overall_freshness]
        return round(
            evidence.evidence_coverage * agreement * quality_factor * freshness_factor,
            4,
        )

    @staticmethod
    def _timeframes(facts: _FactBook, *, positive: bool) -> tuple[str, ...]:
        suffix = "positive" if positive else "negative"
        explicit = tuple(
            item.fact.interval
            for item in facts.records(f"mtf.timeframe.{suffix}")
            if item.fact.interval is not None and bool(item.fact.value)
        )
        signs_by_interval: dict[str, list[int]] = defaultdict(list)
        for item in facts.records("return.percent"):
            value = item.fact.value
            if item.fact.interval is None or isinstance(value, (bool, str)) or value == 0:
                continue
            signs_by_interval[item.fact.interval].append(1 if value > 0 else -1)
        inferred = tuple(
            interval
            for interval, signs in signs_by_interval.items()
            if (sum(signs) > 0 if positive else sum(signs) < 0)
        )
        return tuple(dict.fromkeys((*explicit, *inferred)))

    def _reason_codes(
        self,
        dimensions: tuple[_Dimension, ...],
        breakout: _Dimension,
        extension: ExtensionState,
        room: RemainingRoomState,
        contradictions: tuple[TechnicalContradiction, ...],
        evidence: AgentEvidencePack,
        core_complete: bool,
        missing: tuple[MissingEvidenceRequest, ...],
        trend_sign: int,
    ) -> tuple[TechnicalReasonCode, ...]:
        codes = [code for item in (*dimensions, breakout) for code in item.reason_codes]
        if extension in {ExtensionState.EXTENDED, ExtensionState.EXHAUSTION_RISK}:
            codes.append(TechnicalReasonCode.EXTENDED_FROM_MEAN)
        if extension is ExtensionState.EXHAUSTION_RISK:
            codes.append(TechnicalReasonCode.EXHAUSTION_RISK)
        if room in {RemainingRoomState.LIMITED, RemainingRoomState.MINIMAL}:
            codes.append(
                TechnicalReasonCode.LIMITED_ROOM_TO_RESISTANCE
                if trend_sign > 0
                else TechnicalReasonCode.LIMITED_ROOM_TO_SUPPORT
            )
        if contradictions:
            codes.append(TechnicalReasonCode.TECHNICAL_CONFLICT)
        if not core_complete:
            codes.append(TechnicalReasonCode.CORE_EVIDENCE_MISSING)
        elif missing:
            codes.append(TechnicalReasonCode.OPTIONAL_EVIDENCE_MISSING)
        if evidence.overall_quality is not DataQuality.GOOD:
            codes.append(TechnicalReasonCode.EVIDENCE_PARTIAL)
        if evidence.overall_freshness is not FreshnessState.FRESH:
            codes.append(TechnicalReasonCode.EVIDENCE_STALE)
        return tuple(dict.fromkeys(codes))

    @staticmethod
    def _classify_references(
        dimensions: tuple[_Dimension, ...],
        stance: AgentStance,
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        votes: dict[str, list[int]] = defaultdict(list)
        for dimension in dimensions:
            for record in dimension.records:
                votes[record.reference.evidence_id].append(dimension.sign)
        contradictory: list[str] = []
        for evidence_id, signs in votes.items():
            score = sum(signs)
            if stance is AgentStance.POSITIVE and score < 0:
                contradictory.append(evidence_id)
            elif stance is AgentStance.NEGATIVE and score > 0:
                contradictory.append(evidence_id)
            elif stance is AgentStance.MIXED and score < 0:
                contradictory.append(evidence_id)
        all_ids = tuple(votes)
        contradictory_ids = tuple(item for item in all_ids if item in contradictory)
        supporting_ids = tuple(item for item in all_ids if item not in contradictory)
        return supporting_ids, contradictory_ids

    def _claims(
        self,
        dimensions: tuple[_Dimension, ...],
        supporting_ids: tuple[str, ...],
        contradictory_ids: tuple[str, ...],
    ) -> tuple[EvidenceClaim, ...]:
        claims: list[EvidenceClaim] = []
        for dimension in dimensions:
            grouped: dict[EvidenceType, list[_FactRecord]] = defaultdict(list)
            for record in dimension.records:
                grouped[record.reference.evidence_type].append(record)
            for evidence_type, records in sorted(
                grouped.items(), key=lambda item: item[0].value
            ):
                by_reference: dict[str, list[_FactRecord]] = defaultdict(list)
                for record in records:
                    by_reference[record.reference.evidence_id].append(record)
                citations = tuple(
                    EvidenceCitation(
                        evidence_id=evidence_id,
                        role=(
                            CitationRole.CONTRADICTS
                            if evidence_id in contradictory_ids
                            else CitationRole.SUPPORTS
                        ),
                        locator=", ".join(item.fact.fact_id for item in reference_records),
                    )
                    for evidence_id, reference_records in by_reference.items()
                )
                references = tuple(item.reference for item in records)
                claims.append(
                    EvidenceClaim(
                        claim_id=f"technical:{dimension.name.casefold()}:{evidence_type.value.casefold()}",
                        kind=ClaimKind.INTERPRETIVE,
                        statement=(
                            f"{dimension.name.replace('_', ' ').title()} is interpreted as "
                            f"{dimension.state}."
                        ),
                        evidence_type=evidence_type,
                        citations=citations,
                        as_of=min(item.fact.as_of for item in records),
                        provenance="Supplied immutable A2 evidence facts",
                        quality=self._worst_quality(references),
                        freshness=self._worst_freshness(references),
                    )
                )
        positive = tuple(item for item in dimensions if item.sign > 0)
        negative = tuple(item for item in dimensions if item.sign < 0)
        if positive and negative:
            conflict_records: dict[EvidenceType, list[_FactRecord]] = defaultdict(list)
            positive_types = {
                record.reference.evidence_type
                for item in positive
                for record in item.records
            }
            negative_types = {
                record.reference.evidence_type
                for item in negative
                for record in item.records
            }
            for item in (*positive, *negative):
                for record in item.records:
                    if record.reference.evidence_type in positive_types & negative_types:
                        conflict_records[record.reference.evidence_type].append(record)
            for evidence_type, records in sorted(
                conflict_records.items(), key=lambda item: item[0].value
            ):
                conflict_by_reference: dict[str, list[_FactRecord]] = defaultdict(list)
                for record in records:
                    conflict_by_reference[record.reference.evidence_id].append(record)
                claims.append(
                    EvidenceClaim(
                        claim_id=(
                            "technical:contradiction:"
                            f"{evidence_type.value.casefold()}"
                        ),
                        kind=ClaimKind.INTERPRETIVE,
                        statement=(
                            "Supplied positive and negative technical dimensions "
                            "conflict within this evidence family."
                        ),
                        evidence_type=evidence_type,
                        citations=tuple(
                            EvidenceCitation(
                                evidence_id=evidence_id,
                                role=(
                                    CitationRole.SUPPORTS
                                    if evidence_id in supporting_ids
                                    else CitationRole.CONTRADICTS
                                ),
                                locator=", ".join(
                                    item.fact.fact_id
                                    for item in reference_records
                                ),
                            )
                            for evidence_id, reference_records in conflict_by_reference.items()
                        ),
                        as_of=min(item.fact.as_of for item in records),
                        provenance="Supplied immutable A2 evidence facts",
                        quality=self._worst_quality(
                            tuple(item.reference for item in records)
                        ),
                        freshness=self._worst_freshness(
                            tuple(item.reference for item in records)
                        ),
                    )
                )
        return tuple(claims)

    @staticmethod
    def _worst_quality(references: tuple[AgentEvidenceReference, ...]) -> DataQuality:
        order = {
            DataQuality.GOOD: 0,
            DataQuality.PARTIAL: 1,
            DataQuality.DEGRADED: 2,
            DataQuality.UNAVAILABLE: 3,
        }
        return max(
            (item.quality for item in references if item.quality is not None),
            key=order.__getitem__,
        )

    @staticmethod
    def _worst_freshness(references: tuple[AgentEvidenceReference, ...]) -> FreshnessState:
        order = {
            FreshnessState.FRESH: 0,
            FreshnessState.AGING: 1,
            FreshnessState.STALE: 2,
            FreshnessState.UNKNOWN: 3,
        }
        return max(
            (item.freshness for item in references if item.freshness is not None),
            key=order.__getitem__,
        )

    @staticmethod
    def _summary(assessment: TechnicalAssessment) -> str:
        return (
            f"Technical stance {assessment.stance.value}: trend "
            f"{assessment.trend_state.value}, momentum {assessment.momentum_state.value}, "
            f"structure {assessment.structure_state.value}, MTF {assessment.mtf_state.value}, "
            f"extension {assessment.extension_state.value}, room "
            f"{assessment.remaining_room.value}."
        )

    def _insufficient_opinion(
        self,
        request: AgentRequest,
        evidence: AgentEvidencePack,
        assessment: TechnicalAssessment,
        missing: tuple[MissingEvidenceRequest, ...],
        baseline_agreement: BaselineAgreement,
    ) -> AgentOpinionV2:
        return AgentOpinionV2(
            opinion_id=f"{request.run_id}:technical-opinion",
            request_id=request.request_id,
            run_id=request.run_id,
            specialist=SpecialistId.TECHNICAL,
            specialist_version=SPECIALIST_VERSION,
            subject=request.subject,
            horizon=request.horizon,
            stance=AgentStance.INSUFFICIENT_EVIDENCE,
            status=AgentRunStatus.INSUFFICIENT_EVIDENCE,
            confidence=AgentConfidence(
                evidence_coverage=evidence.evidence_coverage,
                evidence_quality=evidence.overall_quality,
                policy_derived=PolicyDerivedConfidence(
                    value=0.0,
                    policy_id=self._policy.policy_id,
                    policy_version=self._policy.policy_version,
                ),
            ),
            summary="Core supplied A2 trend/structure facts are insufficient.",
            reason_codes=(TechnicalReasonCode.CORE_EVIDENCE_MISSING.value,),
            evidence_claims=(),
            missing_evidence=missing,
            deterministic_baseline_reference=request.deterministic_baseline_reference,
            baseline_agreement=baseline_agreement,
            evidence_fingerprint=request.evidence_fingerprint,
            evidence_quality=evidence.overall_quality,
            evidence_freshness=evidence.overall_freshness,
            policy_version=self._policy.policy_version,
            usage=AgentUsage(),
            produced_at=request.created_at,
            specialist_detail_schema_id=TECHNICAL_DETAIL_SCHEMA,
            specialist_detail_json=assessment.canonical_json(),
        )


def technical_assessment_from_opinion(opinion: AgentOpinionV2) -> TechnicalAssessment:
    """Reconstruct and validate the typed A3.3 detail retained by an opinion."""
    if (
        opinion.specialist is not SpecialistId.TECHNICAL
        or opinion.specialist_detail_schema_id != TECHNICAL_DETAIL_SCHEMA
        or opinion.specialist_detail_json is None
    ):
        raise ValueError("opinion does not contain A3.3 technical detail")
    try:
        return TechnicalAssessment.model_validate_json(opinion.specialist_detail_json)
    except ValidationError as exc:
        raise ValueError("technical specialist detail is invalid") from exc
