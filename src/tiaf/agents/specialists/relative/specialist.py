"""Deterministic A3.6 Relative Strength specialist over supplied A2.8 facts."""

from tiaf.agents.budget import AgentUsage
from tiaf.agents.enums import (
    AgentCapability,
    AgentRunStatus,
    AgentStance,
    EvidenceImportance,
    SpecialistCostTier,
    SpecialistId,
)
from tiaf.agents.evidence import AgentEvidencePack, MissingEvidenceRequest
from tiaf.agents.models import (
    AgentConfidence,
    AgentOpinionV2,
    AgentRequest,
    PolicyDerivedConfidence,
    SpecialistCapability,
)
from tiaf.agents.specialists._contextual import (
    ContextFactBook,
    FactRecord,
    baseline_agreement,
    baseline_direction,
    confidence_value,
    factual_claims,
    reference_ids,
)
from tiaf.contracts import DataQuality, EvidenceType, FreshnessState
from tiaf.data import InstrumentType
from tiaf.features.relative import BenchmarkRole

from .enums import (
    RelativeConsistencyState,
    RelativeExtremeState,
    RelativeLeadershipState,
    RelativeMtfState,
    RelativeReasonCode,
    RelativeStrengthState,
)
from .models import RelativeAssessment, RelativeContradiction
from .policy import RelativeInterpretationPolicy, default_relative_policy

SPECIALIST_VERSION = "1.0"
RELATIVE_DETAIL_SCHEMA = "tiaf.relative-assessment/1.0"


class RelativeStrengthSpecialist:
    """Interpret relative facts without provider access or A2 recomputation."""

    def __init__(self, policy: RelativeInterpretationPolicy | None = None) -> None:
        self._policy = policy or default_relative_policy()

    def capability(self) -> SpecialistCapability:
        return SpecialistCapability(
            specialist=SpecialistId.RELATIVE_STRENGTH,
            specialist_version=SPECIALIST_VERSION,
            display_name="Relative Strength Specialist",
            description="Interprets explicit A2.8 benchmark-relative evidence.",
            supported_instrument_types=(InstrumentType.EQUITY, InstrumentType.INDEX),
            required_evidence_types=(EvidenceType.RELATIVE_STRENGTH,),
            optional_evidence_types=(EvidenceType.MARKET, EvidenceType.TECHNICAL),
            allowed_capabilities=(AgentCapability.READ_A2_EVIDENCE,),
            supports_no_llm=True,
            cost_tier=SpecialistCostTier.LOW,
            prohibitions=(
                "NO_A2_RELATIVE_RECOMPUTATION",
                "NO_IMPLICIT_BENCHMARK_MAPPING",
                "NO_PROVIDER_OR_NETWORK_ACCESS",
                "NO_MODEL_SDK_ACCESS",
                "NO_TRADING_OR_EXECUTION",
            ),
        )

    def analyze(self, request: AgentRequest, evidence: AgentEvidencePack) -> AgentOpinionV2:
        self._validate(request, evidence)
        book = ContextFactBook(evidence)
        relative_records = tuple(
            item
            for item in book.records
            if item.reference.evidence_type is EvidenceType.RELATIVE_STRENGTH
            and item.fact.metric_id.startswith("relative.")
        )
        identities = self._benchmark_identities(relative_records)
        mapping_missing = not identities
        mismatch = len(identities) > 1
        benchmark_symbol: str | None = None
        benchmark_role: BenchmarkRole | None = None
        if len(identities) == 1:
            benchmark_symbol, role = identities[0]
            try:
                benchmark_role = BenchmarkRole(role)
            except ValueError:
                mismatch = True
        subject = book.number("relative.subject_return_percent")
        benchmark = book.number("relative.benchmark_return_percent")
        spreads = tuple(
            item
            for item in relative_records
            if item.fact.metric_id == "relative.return_spread_percent"
            and not isinstance(item.fact.value, (str, bool))
        )
        spread_values = tuple(float(item.fact.value) for item in spreads)
        spread = spread_values[0] if spread_values else None
        # A2.9's accepted baseline requests only the A2.8 spread and consistency
        # facts.  Subject and benchmark returns remain useful optional audit detail,
        # but the already-computed spread is sufficient for bounded interpretation.
        complete = spread is not None and not mapping_missing and not mismatch
        strength = (
            self._strength(spread_values)
            if complete
            else RelativeStrengthState.INSUFFICIENT_EVIDENCE
        )
        consistency = self._consistency(book.number("relative.strength_consistency"))
        mtf = self._mtf(spread_values)
        leadership = self._leadership(strength)
        excess_atr = book.number("relative.excess_move_atr")
        extreme = self._extreme(excess_atr)
        contradictions: tuple[RelativeContradiction, ...] = ()
        if mtf is RelativeMtfState.CONFLICT:
            contradictions = (
                RelativeContradiction(
                    code="RELATIVE_TIMEFRAME_CONFLICT",
                    description="Supplied relative-return spreads disagree across timeframes.",
                    evidence_ids=reference_ids(spreads),
                ),
            )
        stance = self._stance(strength, mtf, complete)
        reasons = self._reasons(strength, mtf, extreme, evidence, mapping_missing, mismatch)
        agreement = 0.5 if mtf is RelativeMtfState.CONFLICT else 1.0 if complete else 0.0
        assessment = RelativeAssessment(
            assessment_id=f"{request.run_id}:relative-assessment",
            specialist_version=SPECIALIST_VERSION,
            policy_id=self._policy.policy_id,
            policy_version=self._policy.policy_version,
            stance=stance,
            benchmark_symbol=benchmark_symbol if not mismatch else None,
            benchmark_role=benchmark_role if not mismatch else None,
            relative_strength=strength,
            relative_consistency=consistency,
            mtf_alignment=mtf,
            leadership_state=leadership,
            extreme_state=extreme,
            subject_return_percent=subject,
            benchmark_return_percent=benchmark,
            excess_return_percent=spread,
            excess_move_atr=excess_atr,
            contradictions=contradictions,
            evidence_ids_by_dimension=(
                ("RELATIVE_PERFORMANCE", reference_ids(relative_records)),
                ("MTF_RELATIVE_ALIGNMENT", reference_ids(spreads)),
            ),
            evidence_coverage=evidence.evidence_coverage,
            internal_agreement=agreement,
            confidence_basis=(
                "explicit_benchmark_identity",
                "a2_8_supplied_fact_coverage_quality_freshness",
                (
                    "cross_timeframe_agreement"
                    if mtf
                    in {RelativeMtfState.ALIGNED_POSITIVE, RelativeMtfState.ALIGNED_NEGATIVE}
                    else "cross_timeframe_conflict"
                    if mtf is RelativeMtfState.CONFLICT
                    else "single_timeframe_only"
                    if mtf is RelativeMtfState.SINGLE_TIMEFRAME
                    else "cross_timeframe_unavailable"
                ),
                "not_probability_of_market_success",
            ),
            reason_codes=reasons,
            created_at=request.created_at,
        )
        used = self._unique((*relative_records, *book.exact("baseline.direction")))
        ids = reference_ids(used)
        missing = self._missing(request, evidence, complete, mapping_missing, mismatch)
        status = (
            AgentRunStatus.INSUFFICIENT_EVIDENCE
            if not complete
            else AgentRunStatus.PARTIAL
            if missing
            or evidence.overall_quality is not DataQuality.GOOD
            or evidence.overall_freshness is not FreshnessState.FRESH
            else AgentRunStatus.SUCCESS
        )
        return AgentOpinionV2(
            opinion_id=f"{request.run_id}:relative-opinion",
            request_id=request.request_id,
            run_id=request.run_id,
            specialist=SpecialistId.RELATIVE_STRENGTH,
            specialist_version=SPECIALIST_VERSION,
            subject=request.subject,
            horizon=request.horizon,
            stance=stance,
            status=status,
            confidence=AgentConfidence(
                evidence_coverage=evidence.evidence_coverage,
                evidence_quality=evidence.overall_quality,
                policy_derived=PolicyDerivedConfidence(
                    value=confidence_value(
                        evidence, agreement, mapping_factor=0.0 if not complete else 1.0
                    ),
                    policy_id=self._policy.policy_id,
                    policy_version=self._policy.policy_version,
                ),
            ),
            summary=self._summary(strength, benchmark_symbol, mtf, extreme),
            reason_codes=tuple(item.value for item in reasons),
            evidence_claims=factual_claims(f"{request.run_id}:relative", used),
            supporting_evidence_ids=ids,
            missing_evidence=missing,
            risks=("Strong relative performance is extended and may carry chase risk",)
            if extreme is RelativeExtremeState.EXTENDED_LEADERSHIP
            else (),
            caveats=("Relative stance is context, not a trade action or return forecast",),
            deterministic_baseline_reference=request.deterministic_baseline_reference,
            baseline_agreement=baseline_agreement(stance, baseline_direction(book)),
            evidence_fingerprint=request.evidence_fingerprint,
            evidence_quality=evidence.overall_quality,
            evidence_freshness=evidence.overall_freshness,
            policy_version=self._policy.policy_version,
            usage=AgentUsage(),
            produced_at=request.created_at,
            specialist_detail_schema_id=RELATIVE_DETAIL_SCHEMA,
            specialist_detail_json=assessment.canonical_json(),
        )

    @staticmethod
    def _benchmark_identities(records: tuple[FactRecord, ...]) -> tuple[tuple[str, str], ...]:
        values: set[tuple[str, str]] = set()
        for item in records:
            symbol = item.reference.metadata.get("benchmark_symbol")
            role = item.reference.metadata.get("benchmark_role")
            if isinstance(symbol, str) and isinstance(role, str):
                values.add((symbol.strip().upper(), role))
        return tuple(sorted(values))

    def _strength(self, values: tuple[float, ...]) -> RelativeStrengthState:
        if not values:
            return RelativeStrengthState.INSUFFICIENT_EVIDENCE
        if any(value > self._policy.inline_spread_percent for value in values) and any(
            value < -self._policy.inline_spread_percent for value in values
        ):
            return RelativeStrengthState.MIXED
        value = values[0]
        if value >= self._policy.strong_spread_percent:
            return RelativeStrengthState.STRONGLY_OUTPERFORMING
        if value >= self._policy.outperform_spread_percent:
            return RelativeStrengthState.OUTPERFORMING
        if value > self._policy.inline_spread_percent:
            return RelativeStrengthState.MILDLY_OUTPERFORMING
        if value <= -self._policy.strong_spread_percent:
            return RelativeStrengthState.STRONGLY_UNDERPERFORMING
        if value <= -self._policy.outperform_spread_percent:
            return RelativeStrengthState.UNDERPERFORMING
        if value < -self._policy.inline_spread_percent:
            return RelativeStrengthState.MILDLY_UNDERPERFORMING
        return RelativeStrengthState.INLINE

    def _consistency(self, value: float | None) -> RelativeConsistencyState:
        if value is None:
            return RelativeConsistencyState.UNKNOWN
        if value >= self._policy.consistent_fraction:
            return RelativeConsistencyState.CONSISTENT
        if value <= self._policy.weak_consistency_fraction:
            return RelativeConsistencyState.CONSISTENTLY_WEAK
        return RelativeConsistencyState.VARIABLE

    def _mtf(self, values: tuple[float, ...]) -> RelativeMtfState:
        if not values:
            return RelativeMtfState.UNKNOWN
        if len(values) == 1:
            return RelativeMtfState.SINGLE_TIMEFRAME
        if all(value > self._policy.inline_spread_percent for value in values):
            return RelativeMtfState.ALIGNED_POSITIVE
        if all(value < -self._policy.inline_spread_percent for value in values):
            return RelativeMtfState.ALIGNED_NEGATIVE
        return RelativeMtfState.CONFLICT

    @staticmethod
    def _leadership(state: RelativeStrengthState) -> RelativeLeadershipState:
        if state is RelativeStrengthState.STRONGLY_OUTPERFORMING:
            return RelativeLeadershipState.LEADER
        if state in {
            RelativeStrengthState.OUTPERFORMING,
            RelativeStrengthState.MILDLY_OUTPERFORMING,
        }:
            return RelativeLeadershipState.ABOVE_AVERAGE
        if state is RelativeStrengthState.INLINE:
            return RelativeLeadershipState.INLINE
        if state is RelativeStrengthState.STRONGLY_UNDERPERFORMING:
            return RelativeLeadershipState.SEVERE_LAGGARD
        if state in {
            RelativeStrengthState.UNDERPERFORMING,
            RelativeStrengthState.MILDLY_UNDERPERFORMING,
        }:
            return RelativeLeadershipState.LAGGARD
        return RelativeLeadershipState.UNKNOWN

    def _extreme(self, value: float | None) -> RelativeExtremeState:
        if value is None:
            return RelativeExtremeState.UNKNOWN
        if value >= self._policy.extreme_atr:
            return RelativeExtremeState.EXTENDED_LEADERSHIP
        if value <= -self._policy.extreme_atr:
            return RelativeExtremeState.EXTENDED_WEAKNESS
        return RelativeExtremeState.NOT_EXTREME

    @staticmethod
    def _stance(state: RelativeStrengthState, mtf: RelativeMtfState, complete: bool) -> AgentStance:
        if not complete:
            return AgentStance.INSUFFICIENT_EVIDENCE
        if state is RelativeStrengthState.MIXED or mtf is RelativeMtfState.CONFLICT:
            return AgentStance.MIXED
        if state in {
            RelativeStrengthState.STRONGLY_OUTPERFORMING,
            RelativeStrengthState.OUTPERFORMING,
            RelativeStrengthState.MILDLY_OUTPERFORMING,
        }:
            return AgentStance.POSITIVE
        if state in {
            RelativeStrengthState.STRONGLY_UNDERPERFORMING,
            RelativeStrengthState.UNDERPERFORMING,
            RelativeStrengthState.MILDLY_UNDERPERFORMING,
        }:
            return AgentStance.NEGATIVE
        return AgentStance.NEUTRAL

    @staticmethod
    def _reasons(
        state: RelativeStrengthState,
        mtf: RelativeMtfState,
        extreme: RelativeExtremeState,
        evidence: AgentEvidencePack,
        missing: bool,
        mismatch: bool,
    ) -> tuple[RelativeReasonCode, ...]:
        values: list[RelativeReasonCode] = []
        if missing:
            values.append(RelativeReasonCode.BENCHMARK_MAPPING_MISSING)
        if mismatch:
            values.append(RelativeReasonCode.BENCHMARK_MISMATCH)
        if state in {
            RelativeStrengthState.STRONGLY_OUTPERFORMING,
            RelativeStrengthState.OUTPERFORMING,
            RelativeStrengthState.MILDLY_OUTPERFORMING,
        }:
            values.extend(
                (RelativeReasonCode.RELATIVE_OUTPERFORMANCE, RelativeReasonCode.RELATIVE_LEADERSHIP)
            )
        elif state in {
            RelativeStrengthState.STRONGLY_UNDERPERFORMING,
            RelativeStrengthState.UNDERPERFORMING,
            RelativeStrengthState.MILDLY_UNDERPERFORMING,
        }:
            values.extend(
                (RelativeReasonCode.RELATIVE_UNDERPERFORMANCE, RelativeReasonCode.RELATIVE_LAG)
            )
        elif state is RelativeStrengthState.INLINE:
            values.append(RelativeReasonCode.RELATIVE_INLINE)
        if mtf in {RelativeMtfState.ALIGNED_POSITIVE, RelativeMtfState.ALIGNED_NEGATIVE}:
            values.append(RelativeReasonCode.RELATIVE_MTF_ALIGNED)
        elif mtf is RelativeMtfState.CONFLICT:
            values.append(RelativeReasonCode.RELATIVE_MTF_CONFLICT)
        if extreme in {
            RelativeExtremeState.EXTENDED_LEADERSHIP,
            RelativeExtremeState.EXTENDED_WEAKNESS,
        }:
            values.append(RelativeReasonCode.RELATIVE_EXTENDED)
        if evidence.overall_quality is not DataQuality.GOOD:
            values.append(RelativeReasonCode.RELATIVE_EVIDENCE_PARTIAL)
        if evidence.overall_freshness is FreshnessState.STALE:
            values.append(RelativeReasonCode.RELATIVE_EVIDENCE_STALE)
        if state is RelativeStrengthState.INSUFFICIENT_EVIDENCE:
            values.append(RelativeReasonCode.RELATIVE_EVIDENCE_INSUFFICIENT)
        return tuple(dict.fromkeys(values))

    @staticmethod
    def _missing(
        request: AgentRequest,
        evidence: AgentEvidencePack,
        complete: bool,
        mapping_missing: bool,
        mismatch: bool,
    ) -> tuple[MissingEvidenceRequest, ...]:
        values = list(evidence.missing_evidence)
        if not complete:
            reason = (
                "Explicit benchmark identity is missing"
                if mapping_missing
                else "Benchmark identities conflict"
                if mismatch
                else "An excess-return A2.8 fact is required"
            )
            values.append(
                MissingEvidenceRequest(
                    missing_request_id=f"{request.run_id}:missing:relative-core",
                    evidence_type=EvidenceType.RELATIVE_STRENGTH,
                    capability=AgentCapability.READ_A2_EVIDENCE,
                    subject=request.subject,
                    reason=reason,
                    importance=EvidenceImportance.REQUIRED,
                    requested_at=request.created_at,
                )
            )
        unique: dict[str, MissingEvidenceRequest] = {}
        for item in values:
            unique.setdefault(item.missing_request_id, item)
        return tuple(unique.values())

    @staticmethod
    def _summary(
        state: RelativeStrengthState,
        benchmark: str | None,
        mtf: RelativeMtfState,
        extreme: RelativeExtremeState,
    ) -> str:
        return (
            f"Relative context versus {benchmark or 'an unavailable explicit benchmark'} "
            f"is {state.value}; MTF is {mtf.value}; extreme state is {extreme.value}."
        )

    @staticmethod
    def _unique(records: tuple[FactRecord, ...]) -> tuple[FactRecord, ...]:
        values: dict[str, FactRecord] = {}
        for item in records:
            values.setdefault(item.fact.fact_id, item)
        return tuple(values.values())

    @staticmethod
    def _validate(request: AgentRequest, evidence: AgentEvidencePack) -> None:
        if request.specialist is not SpecialistId.RELATIVE_STRENGTH:
            raise ValueError("RelativeStrengthSpecialist requires RELATIVE_STRENGTH identity")
        if AgentCapability.READ_A2_EVIDENCE not in request.allowed_capabilities:
            raise ValueError("RelativeStrengthSpecialist requires READ_A2_EVIDENCE")
        if (
            evidence.request_id != request.request_id
            or evidence.subject != request.subject
            or evidence.evidence_fingerprint != request.evidence_fingerprint
            or evidence.deterministic_assessment_id != request.deterministic_baseline_reference
        ):
            raise ValueError("relative evidence does not preserve request/A2 identity")


def relative_assessment_from_opinion(opinion: AgentOpinionV2) -> RelativeAssessment:
    if (
        opinion.specialist_detail_schema_id != RELATIVE_DETAIL_SCHEMA
        or opinion.specialist_detail_json is None
    ):
        raise ValueError("opinion does not contain A3.6 relative detail")
    return RelativeAssessment.model_validate_json(opinion.specialist_detail_json)
