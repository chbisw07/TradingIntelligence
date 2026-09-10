"""Deterministic A3.7 derivatives, opportunity-quality, and risk specialists."""

from collections.abc import Iterable

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
    EvidenceCitation,
    EvidenceClaim,
    MissingEvidenceRequest,
)
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
from tiaf.baseline.enums import CandidateClass
from tiaf.contracts import DataQuality, EvidenceType, FreshnessState, TradeStyle
from tiaf.data import InstrumentType

from .enums import (
    ConfirmationState,
    CrowdingState,
    DerivativesLiquidityState,
    DerivativesParticipationState,
    DerivativesPositioningState,
    DerivativesReasonCode,
    DerivativesVolatilityState,
    ExpiryProximityState,
    OpportunityMaturityState,
    OpportunityQualityState,
    OpportunityReasonCode,
    OpportunityRiskLevel,
    RemainingRoomQuality,
    RiskReasonCode,
)
from .models import (
    ContextContradiction,
    DerivativesContextAssessment,
    OpportunityQualityAssessment,
    OpportunityRiskAssessment,
)
from .policy import OpportunityInterpretationPolicy, default_opportunity_policy

SPECIALIST_VERSION = "1.0"
DERIVATIVES_DETAIL_SCHEMA = "tiaf.derivatives-context-assessment/1.0"
QUALITY_DETAIL_SCHEMA = "tiaf.opportunity-quality-assessment/1.0"
RISK_DETAIL_SCHEMA = "tiaf.opportunity-risk-assessment/1.0"

_USABLE_INSTRUMENTS = (
    InstrumentType.EQUITY,
    InstrumentType.INDEX,
    InstrumentType.FUTURE,
    InstrumentType.CALL_OPTION,
    InstrumentType.PUT_OPTION,
)
_POSITIVE = {"POSITIVE", "SUPPORTIVE", "STRONG", "GOOD", "LEADING", "OUTPERFORMING"}
_NEGATIVE = {
    "NEGATIVE",
    "ADVERSE",
    "WEAK",
    "LAGGING",
    "UNDERPERFORMING",
    "RISK_OFF",
    "DETERIORATING",
    "FRAGILE",
}


def _unique(records: Iterable[FactRecord]) -> tuple[FactRecord, ...]:
    values: dict[str, FactRecord] = {}
    for item in records:
        values.setdefault(item.fact.fact_id, item)
    return tuple(values.values())


def _family_records(book: ContextFactBook, *prefixes: str) -> tuple[FactRecord, ...]:
    return _unique(
        item
        for item in book.records
        if any(item.fact.metric_id.startswith(prefix) for prefix in prefixes)
    )


def _normalized_text(record: FactRecord) -> str | None:
    if not isinstance(record.fact.value, str):
        return None
    return record.fact.value.strip().upper().replace("-", "_").replace(" ", "_")


def _contains_state(records: tuple[FactRecord, ...], values: set[str]) -> bool:
    def matches(text: str, value: str) -> bool:
        if text.startswith(("NOT_", "NO_")) and not value.startswith(("NOT_", "NO_")):
            return False
        return text == value or text.startswith(f"{value}_") or text.endswith(f"_{value}")

    return any(
        text is not None and any(matches(text, value) for value in values)
        for item in records
        if (text := _normalized_text(item)) is not None
    )


def _has_meaningful_evidence(records: tuple[FactRecord, ...]) -> bool:
    unknown_states = {
        "INSUFFICIENT_EVIDENCE",
        "MISSING",
        "NOT_AVAILABLE",
        "UNAVAILABLE",
        "UNKNOWN",
    }
    return any(
        not isinstance(item.fact.value, str)
        or item.fact.value.strip().upper().replace("-", "_").replace(" ", "_") not in unknown_states
        for item in records
    )


def _horizon_context(request: AgentRequest) -> str:
    label = (request.horizon.label or "").upper()
    if request.trade_style is TradeStyle.DAY or "DAY" in label or "INTRADAY" in label:
        return "DAY"
    if (
        (request.horizon.max_days is not None and request.horizon.max_days > 60)
        or "MEDIUM" in label
        or "INVEST" in label
    ):
        return "MEDIUM"
    return "SHORT_TERM"


def _instrument_context(request: AgentRequest) -> str:
    if request.instrument_type is InstrumentType.EQUITY:
        return "EQUITY_UNDERLYING"
    if request.instrument_type is InstrumentType.INDEX:
        return "INDEX_UNDERLYING"
    if request.instrument_type is InstrumentType.FUTURE:
        return "FUTURES_CONTEXT"
    underlying = request.metadata.get("underlying_instrument_type")
    if underlying == InstrumentType.EQUITY.value:
        return "STOCK_OPTION_UNDERLYING"
    if underlying == InstrumentType.INDEX.value:
        return "INDEX_OPTION_UNDERLYING"
    return "OPTION_UNDERLYING_UNSPECIFIED"


def _baseline_candidate(book: ContextFactBook) -> CandidateClass | None:
    value = book.text("baseline.candidate_class")
    try:
        return CandidateClass(value) if value is not None else None
    except ValueError:
        return None


def _family_map(
    families: tuple[tuple[str, tuple[FactRecord, ...]], ...],
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return tuple((name, reference_ids(records)) for name, records in families)


def _interpretive_claims(
    claim_id: str,
    statement: str,
    records: tuple[FactRecord, ...],
    evidence: AgentEvidencePack,
    request: AgentRequest,
) -> tuple[EvidenceClaim, ...]:
    grouped: dict[EvidenceType, list[FactRecord]] = {}
    for item in records:
        grouped.setdefault(item.reference.evidence_type, []).append(item)
    return tuple(
        EvidenceClaim(
            claim_id=f"{claim_id}:{evidence_type.value.lower()}",
            kind=ClaimKind.INTERPRETIVE,
            statement=statement,
            evidence_type=evidence_type,
            citations=tuple(
                EvidenceCitation(evidence_id=evidence_id, role=CitationRole.SUPPORTS)
                for evidence_id in reference_ids(tuple(items))
            ),
            as_of=max((item.fact.as_of for item in items), default=request.created_at),
            provenance="tiaf.a3-7/deterministic-policy-1.0",
            quality=evidence.overall_quality,
            freshness=evidence.overall_freshness,
        )
        for evidence_type, items in sorted(grouped.items(), key=lambda item: item[0].value)
    )


def _claims(
    prefix: str,
    statement: str,
    records: tuple[FactRecord, ...],
    evidence: AgentEvidencePack,
    request: AgentRequest,
) -> tuple[EvidenceClaim, ...]:
    interpretive = _interpretive_claims(
        f"{prefix}:interpretation", statement, records, evidence, request
    )
    return (*factual_claims(prefix, records), *interpretive)


def _quality_agreement(
    state: OpportunityQualityState, candidate: CandidateClass | None
) -> BaselineAgreement:
    if candidate is None or state is OpportunityQualityState.INSUFFICIENT_EVIDENCE:
        return BaselineAgreement.NOT_COMPARABLE
    positive = candidate in {CandidateClass.TOP_MOVER, CandidateClass.EARLY_OPPORTUNITY}
    negative = candidate in {CandidateClass.MATURE_AVOID_CHASE, CandidateClass.NO_TRADE}
    if state in {OpportunityQualityState.STRONG, OpportunityQualityState.GOOD}:
        return BaselineAgreement.AGREES if positive else BaselineAgreement.DISAGREES
    if state is OpportunityQualityState.WEAK:
        return BaselineAgreement.AGREES if negative else BaselineAgreement.DISAGREES
    return BaselineAgreement.PARTIALLY_AGREES


def _risk_agreement(
    level: OpportunityRiskLevel, candidate: CandidateClass | None
) -> BaselineAgreement:
    if candidate is None or level is OpportunityRiskLevel.INSUFFICIENT_EVIDENCE:
        return BaselineAgreement.NOT_COMPARABLE
    baseline_high_risk = candidate in {
        CandidateClass.MATURE_AVOID_CHASE,
        CandidateClass.NO_TRADE,
    }
    if level in {OpportunityRiskLevel.HIGH, OpportunityRiskLevel.CRITICAL}:
        return BaselineAgreement.AGREES if baseline_high_risk else BaselineAgreement.DISAGREES
    if level is OpportunityRiskLevel.LOW:
        return BaselineAgreement.DISAGREES if baseline_high_risk else BaselineAgreement.AGREES
    return BaselineAgreement.PARTIALLY_AGREES


def _validate(
    request: AgentRequest,
    evidence: AgentEvidencePack,
    specialist: SpecialistId,
    required: set[AgentCapability],
) -> None:
    if request.specialist is not specialist:
        raise ValueError(f"specialist requires {specialist.value} identity")
    if request.instrument_type not in _USABLE_INSTRUMENTS:
        raise ValueError("A3.7 requires a recognized market instrument type")
    if request.instrument_type in {InstrumentType.CALL_OPTION, InstrumentType.PUT_OPTION}:
        underlying = request.metadata.get("underlying_instrument_type")
        if underlying not in {InstrumentType.EQUITY.value, InstrumentType.INDEX.value}:
            raise ValueError("option context requires explicit EQUITY or INDEX underlying identity")
    if not required <= set(request.allowed_capabilities):
        raise ValueError("A3.7 request lacks required bounded evidence capability")
    if (
        evidence.request_id != request.request_id
        or evidence.subject != request.subject
        or evidence.evidence_fingerprint != request.evidence_fingerprint
        or evidence.deterministic_assessment_id != request.deterministic_baseline_reference
    ):
        raise ValueError("A3.7 evidence does not preserve request/A2 identity")


class DerivativesContextSpecialist:
    """Interpret supplied A2.7 derivatives facts without selecting a contract."""

    def __init__(self, policy: OpportunityInterpretationPolicy | None = None) -> None:
        self._policy = policy or default_opportunity_policy()

    def capability(self) -> SpecialistCapability:
        return SpecialistCapability(
            specialist=SpecialistId.DERIVATIVES_CONTEXT,
            specialist_version=SPECIALIST_VERSION,
            display_name="Derivatives Context Specialist",
            description="Interprets supplied option-chain context without option expression.",
            supported_instrument_types=_USABLE_INSTRUMENTS,
            required_evidence_types=(EvidenceType.DERIVATIVES,),
            optional_evidence_types=(
                EvidenceType.TECHNICAL,
                EvidenceType.VOLATILITY,
                EvidenceType.MARKET,
            ),
            allowed_capabilities=(
                AgentCapability.READ_A2_EVIDENCE,
                AgentCapability.READ_DERIVATIVES,
            ),
            supports_no_llm=True,
            cost_tier=SpecialistCostTier.LOW,
            prohibitions=(
                "NO_PROVIDER_OR_NETWORK_ACCESS",
                "NO_A2_DERIVATIVES_RECOMPUTATION",
                "NO_OPTION_TYPE_STRIKE_EXPIRY_OR_QUANTITY_SELECTION",
                "NO_TRADING_OR_POSITION_ACTIONS",
                "NO_FORECAST_OR_PROBABILITY",
                "NO_ARBITRATION",
            ),
        )

    def analyze(self, request: AgentRequest, evidence: AgentEvidencePack) -> AgentOpinionV2:
        _validate(
            request,
            evidence,
            SpecialistId.DERIVATIVES_CONTEXT,
            {AgentCapability.READ_A2_EVIDENCE, AgentCapability.READ_DERIVATIVES},
        )
        book = ContextFactBook(evidence)
        derivatives = _family_records(book, "derivatives.")
        volatility_records = _unique(
            (
                *_family_records(
                    book, "derivatives.atm_", "derivatives.ce_iv", "derivatives.pe_iv"
                ),
                *book.exact("volatility.realized"),
            )
        )
        # Premium, Greeks, and ATM geometry are not volatility-regime evidence.
        iv_metrics = {
            "derivatives.atm_mean_iv",
            "derivatives.atm_ce_iv",
            "derivatives.atm_pe_iv",
            "derivatives.ce_iv_mean",
            "derivatives.pe_iv_mean",
            "volatility.realized",
        }
        volatility_records = tuple(
            item for item in volatility_records if item.fact.metric_id in iv_metrics
        )
        positioning_records = _unique(
            (
                *book.exact("derivatives.oi_put_call_ratio"),
                *book.exact("derivatives.volume_put_call_ratio"),
                *_family_records(book, "derivatives.ce_oi_", "derivatives.pe_oi_"),
            )
        )
        liquidity_records = book.exact(
            "derivatives.atm_ce_bid_ask_spread_percent",
            "derivatives.atm_pe_bid_ask_spread_percent",
        )
        participation_records = book.exact(
            "derivatives.ce_volume_total", "derivatives.pe_volume_total"
        )
        expiry_records = book.exact("derivatives.days_to_expiry", "derivatives.expiry_date")
        baseline_records = book.exact("baseline.direction")
        families = (
            ("IV_VOLATILITY", volatility_records),
            ("OI_PCR", positioning_records),
            ("LIQUIDITY", liquidity_records),
            ("PARTICIPATION", participation_records),
            ("EXPIRY", expiry_records),
            ("UNDERLYING_BASELINE", baseline_records),
        )
        present = tuple(name for name, records in families if _has_meaningful_evidence(records))
        volatility = self._volatility(book)
        positioning = self._positioning(book)
        liquidity = self._liquidity(book)
        participation = self._participation(book)
        crowding = self._crowding(book)
        expiry = self._expiry(book)
        confirmation = self._confirmation(positioning, baseline_direction(book))
        core_count = sum(bool(records) for _, records in families[:3])
        complete = core_count >= self._policy.minimum_core_families and bool(derivatives)
        stale = evidence.overall_freshness is FreshnessState.STALE
        contradictions = self._contradictions(
            positioning, confirmation, volatility_records, positioning_records, baseline_records
        )
        stance = self._stance(positioning, liquidity, participation, complete=complete, stale=stale)
        reasons = self._reasons(
            volatility,
            positioning,
            liquidity,
            participation,
            crowding,
            expiry,
            confirmation,
            evidence,
            complete,
        )
        agreement = 0.5 if contradictions else 1.0 if complete else 0.0
        assessment = DerivativesContextAssessment(
            assessment_id=f"{request.run_id}:derivatives-context-assessment",
            specialist_version=SPECIALIST_VERSION,
            policy_id=self._policy.policy_id,
            policy_version=self._policy.policy_version,
            stance=stance,
            instrument_type=request.instrument_type,
            instrument_context=_instrument_context(request),
            horizon_context=_horizon_context(request),
            evidence_families=present,
            contradictions=contradictions,
            evidence_ids_by_family=_family_map(families),
            internal_agreement=agreement,
            confidence_basis=(
                "grouped_iv_oi_liquidity_families_not_raw_field_count",
                "evidence_coverage_quality_freshness_and_conflict",
                "confidence_is_not_success_probability",
            ),
            created_at=request.created_at,
            volatility_state=volatility,
            positioning_state=positioning,
            liquidity_state=liquidity,
            participation_state=participation,
            crowding_state=crowding,
            expiry_proximity=expiry,
            underlying_confirmation=confirmation,
            reason_codes=reasons,
        )
        missing = self._missing(request, evidence, families, complete)
        status = (
            AgentRunStatus.ABSTAINED
            if stale and complete
            else AgentRunStatus.INSUFFICIENT_EVIDENCE
            if not complete
            else AgentRunStatus.PARTIAL
            if missing or evidence.overall_quality is not DataQuality.GOOD
            else AgentRunStatus.SUCCESS
        )
        used = _unique((*derivatives, *baseline_records))
        ids = reference_ids(used)
        summary = (
            f"Derivatives context is {stance.value}: volatility {volatility.value}, "
            f"positioning {positioning.value}, liquidity {liquidity.value}, and "
            f"expiry proximity {expiry.value}."
        )
        return AgentOpinionV2(
            opinion_id=f"{request.run_id}:derivatives-context-opinion",
            request_id=request.request_id,
            run_id=request.run_id,
            specialist=SpecialistId.DERIVATIVES_CONTEXT,
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
                        evidence,
                        agreement,
                        mapping_factor=min(1.0, core_count / self._policy.minimum_core_families)
                        if complete
                        else 0.0,
                    ),
                    policy_id=self._policy.policy_id,
                    policy_version=self._policy.policy_version,
                ),
            ),
            summary=summary,
            reason_codes=tuple(item.value for item in reasons),
            evidence_claims=_claims(
                f"{request.run_id}:derivatives", summary, used, evidence, request
            ),
            supporting_evidence_ids=ids,
            missing_evidence=missing,
            risks=tuple(
                item
                for item, active in (
                    (
                        "Elevated implied volatility increases premium and volatility risk",
                        volatility is DerivativesVolatilityState.ELEVATED,
                    ),
                    ("Option-chain liquidity is weak", liquidity is DerivativesLiquidityState.WEAK),
                    (
                        "Open interest is concentrated and may reflect crowding",
                        crowding is CrowdingState.CONCENTRATED,
                    ),
                )
                if active
            ),
            caveats=(
                "PCR, OI concentration, and IV are context, not directional or price oracles",
                "No option type, strike, expiry, quantity, target, or probability is produced",
            ),
            deterministic_baseline_reference=request.deterministic_baseline_reference,
            baseline_agreement=baseline_agreement(stance, baseline_direction(book)),
            evidence_fingerprint=request.evidence_fingerprint,
            evidence_quality=evidence.overall_quality,
            evidence_freshness=evidence.overall_freshness,
            policy_version=self._policy.policy_version,
            usage=AgentUsage(),
            produced_at=request.created_at,
            specialist_detail_schema_id=DERIVATIVES_DETAIL_SCHEMA,
            specialist_detail_json=assessment.canonical_json(),
            metadata={"replay_safe": True, "a2_evidence_unchanged": True},
        )

    def _volatility(self, book: ContextFactBook) -> DerivativesVolatilityState:
        values = tuple(
            value
            for metric in (
                "derivatives.atm_mean_iv",
                "derivatives.atm_ce_iv",
                "derivatives.atm_pe_iv",
                "derivatives.ce_iv_mean",
                "derivatives.pe_iv_mean",
            )
            if (value := book.number(metric)) is not None
        )
        if not values:
            return DerivativesVolatilityState.UNKNOWN
        average = sum(values) / len(values)
        if average >= self._policy.elevated_iv:
            return DerivativesVolatilityState.ELEVATED
        if average <= self._policy.compressed_iv:
            return DerivativesVolatilityState.COMPRESSED
        return DerivativesVolatilityState.MODERATE

    def _positioning(self, book: ContextFactBook) -> DerivativesPositioningState:
        values = tuple(
            value
            for metric in (
                "derivatives.oi_put_call_ratio",
                "derivatives.volume_put_call_ratio",
            )
            if (value := book.number(metric)) is not None
        )
        if not values:
            return DerivativesPositioningState.UNKNOWN
        high = any(value > self._policy.balanced_pcr_high for value in values)
        low = any(value < self._policy.balanced_pcr_low for value in values)
        if high and low:
            return DerivativesPositioningState.CONFLICTED
        direction = baseline_direction(book)
        if direction is None or direction.value in {"NEUTRAL", "CONFLICTED"}:
            return DerivativesPositioningState.BALANCED
        supporting = (direction.value == "POSITIVE" and high) or (
            direction.value == "NEGATIVE" and low
        )
        adverse = (direction.value == "POSITIVE" and low) or (
            direction.value == "NEGATIVE" and high
        )
        if supporting:
            return DerivativesPositioningState.SUPPORTIVE_CONTEXT
        if adverse:
            return DerivativesPositioningState.ADVERSE_CONTEXT
        return DerivativesPositioningState.BALANCED

    def _liquidity(self, book: ContextFactBook) -> DerivativesLiquidityState:
        values = tuple(
            value
            for metric in (
                "derivatives.atm_ce_bid_ask_spread_percent",
                "derivatives.atm_pe_bid_ask_spread_percent",
            )
            if (value := book.number(metric)) is not None
        )
        if not values:
            return DerivativesLiquidityState.UNKNOWN
        if max(values) <= self._policy.adequate_spread_percent:
            return DerivativesLiquidityState.ADEQUATE
        if max(values) >= self._policy.weak_spread_percent:
            return DerivativesLiquidityState.WEAK
        return DerivativesLiquidityState.MIXED

    @staticmethod
    def _participation(book: ContextFactBook) -> DerivativesParticipationState:
        values = tuple(
            value
            for metric in ("derivatives.ce_volume_total", "derivatives.pe_volume_total")
            if (value := book.number(metric)) is not None
        )
        if not values:
            return DerivativesParticipationState.UNKNOWN
        return (
            DerivativesParticipationState.PRESENT
            if sum(values) > 0
            else DerivativesParticipationState.ABSENT
        )

    def _crowding(self, book: ContextFactBook) -> CrowdingState:
        values = tuple(
            value
            for metric in (
                "derivatives.ce_oi_top1_fraction",
                "derivatives.pe_oi_top1_fraction",
            )
            if (value := book.number(metric)) is not None
        )
        if not values:
            return CrowdingState.UNKNOWN
        return (
            CrowdingState.CONCENTRATED
            if max(values) >= self._policy.concentrated_oi_fraction
            else CrowdingState.DISTRIBUTED
        )

    def _expiry(self, book: ContextFactBook) -> ExpiryProximityState:
        value = book.number("derivatives.days_to_expiry")
        if value is None:
            return ExpiryProximityState.UNKNOWN
        if value <= self._policy.imminent_expiry_days:
            return ExpiryProximityState.IMMINENT
        if value <= self._policy.near_expiry_days:
            return ExpiryProximityState.NEAR
        return ExpiryProximityState.NOT_NEAR

    @staticmethod
    def _confirmation(
        positioning: DerivativesPositioningState, direction: object
    ) -> ConfirmationState:
        if direction is None:
            return ConfirmationState.UNKNOWN
        if positioning is DerivativesPositioningState.SUPPORTIVE_CONTEXT:
            return ConfirmationState.CONFIRMS
        if positioning is DerivativesPositioningState.ADVERSE_CONTEXT:
            return ConfirmationState.CONFLICTS
        if positioning is DerivativesPositioningState.BALANCED:
            return ConfirmationState.NEUTRAL
        return ConfirmationState.UNKNOWN

    @staticmethod
    def _stance(
        positioning: DerivativesPositioningState,
        liquidity: DerivativesLiquidityState,
        participation: DerivativesParticipationState,
        *,
        complete: bool,
        stale: bool,
    ) -> AgentStance:
        if not complete:
            return AgentStance.INSUFFICIENT_EVIDENCE
        if stale:
            return AgentStance.ABSTAIN
        if positioning is DerivativesPositioningState.CONFLICTED:
            return AgentStance.MIXED
        if (
            liquidity is DerivativesLiquidityState.WEAK
            or participation is DerivativesParticipationState.ABSENT
        ):
            return AgentStance.MIXED
        if positioning is DerivativesPositioningState.SUPPORTIVE_CONTEXT:
            return AgentStance.POSITIVE
        if positioning is DerivativesPositioningState.ADVERSE_CONTEXT:
            return AgentStance.NEGATIVE
        return AgentStance.NEUTRAL

    @staticmethod
    def _contradictions(
        positioning: DerivativesPositioningState,
        confirmation: ConfirmationState,
        volatility: tuple[FactRecord, ...],
        positioning_records: tuple[FactRecord, ...],
        baseline_records: tuple[FactRecord, ...],
    ) -> tuple[ContextContradiction, ...]:
        values: list[ContextContradiction] = []
        if positioning is DerivativesPositioningState.CONFLICTED:
            values.append(
                ContextContradiction(
                    code="DERIVATIVES_PCR_CONFLICT",
                    description="Supplied OI and volume PCR contexts conflict.",
                    evidence_ids=reference_ids(positioning_records),
                )
            )
        if confirmation is ConfirmationState.CONFLICTS:
            values.append(
                ContextContradiction(
                    code="UNDERLYING_DERIVATIVES_CONFLICT",
                    description=(
                        "Derivatives positioning is adverse to the supplied baseline direction."
                    ),
                    evidence_ids=reference_ids((*positioning_records, *baseline_records)),
                )
            )
        # The unused argument is deliberate: elevated IV is not a contradiction by itself.
        _ = volatility
        return tuple(values)

    @staticmethod
    def _reasons(
        volatility: DerivativesVolatilityState,
        positioning: DerivativesPositioningState,
        liquidity: DerivativesLiquidityState,
        participation: DerivativesParticipationState,
        crowding: CrowdingState,
        expiry: ExpiryProximityState,
        confirmation: ConfirmationState,
        evidence: AgentEvidencePack,
        complete: bool,
    ) -> tuple[DerivativesReasonCode, ...]:
        values: list[DerivativesReasonCode] = []
        values.extend(
            {
                DerivativesVolatilityState.ELEVATED: (
                    DerivativesReasonCode.DERIVATIVES_IV_ELEVATED,
                ),
                DerivativesVolatilityState.COMPRESSED: (
                    DerivativesReasonCode.DERIVATIVES_IV_COMPRESSED,
                ),
                DerivativesVolatilityState.MODERATE: (
                    DerivativesReasonCode.DERIVATIVES_IV_MODERATE,
                ),
            }.get(volatility, ())
        )
        values.extend(
            {
                DerivativesPositioningState.SUPPORTIVE_CONTEXT: (
                    DerivativesReasonCode.DERIVATIVES_OI_SUPPORTIVE_CONTEXT,
                ),
                DerivativesPositioningState.ADVERSE_CONTEXT: (
                    DerivativesReasonCode.DERIVATIVES_OI_ADVERSE_CONTEXT,
                ),
                DerivativesPositioningState.BALANCED: (
                    DerivativesReasonCode.DERIVATIVES_OI_BALANCED,
                ),
                DerivativesPositioningState.CONFLICTED: (
                    DerivativesReasonCode.DERIVATIVES_CONFLICTED,
                ),
            }.get(positioning, ())
        )
        if liquidity is DerivativesLiquidityState.ADEQUATE:
            values.append(DerivativesReasonCode.DERIVATIVES_LIQUIDITY_ADEQUATE)
        elif liquidity is DerivativesLiquidityState.WEAK:
            values.append(DerivativesReasonCode.DERIVATIVES_LIQUIDITY_WEAK)
        if participation is DerivativesParticipationState.ABSENT:
            values.append(DerivativesReasonCode.DERIVATIVES_PARTICIPATION_ABSENT)
        if crowding is CrowdingState.CONCENTRATED:
            values.append(DerivativesReasonCode.DERIVATIVES_OI_CONCENTRATED)
        if expiry in {ExpiryProximityState.IMMINENT, ExpiryProximityState.NEAR}:
            values.append(DerivativesReasonCode.DERIVATIVES_EXPIRY_NEAR)
        if confirmation is ConfirmationState.CONFLICTS:
            values.append(DerivativesReasonCode.DERIVATIVES_UNDERLYING_CONFLICT)
        if evidence.overall_freshness is FreshnessState.STALE:
            values.append(DerivativesReasonCode.DERIVATIVES_EVIDENCE_STALE)
        if not complete:
            values.append(DerivativesReasonCode.DERIVATIVES_EVIDENCE_INSUFFICIENT)
        return tuple(dict.fromkeys(values))

    @staticmethod
    def _missing(
        request: AgentRequest,
        evidence: AgentEvidencePack,
        families: tuple[tuple[str, tuple[FactRecord, ...]], ...],
        complete: bool,
    ) -> tuple[MissingEvidenceRequest, ...]:
        values = list(evidence.missing_evidence)
        for name, records in families[:3]:
            if not records:
                values.append(
                    MissingEvidenceRequest(
                        missing_request_id=f"{request.run_id}:missing:derivatives:{name.lower()}",
                        evidence_type=EvidenceType.DERIVATIVES,
                        capability=AgentCapability.READ_DERIVATIVES,
                        subject=request.subject,
                        reason=f"Supplied derivatives {name.lower()} family is unavailable",
                        importance=(
                            EvidenceImportance.REQUIRED
                            if not complete
                            else EvidenceImportance.MATERIAL
                        ),
                        requested_at=request.created_at,
                    )
                )
        return tuple(values)


class OpportunityQualitySpecialist:
    """Interpret whether an existing A2 candidate is clean and worth attention."""

    def __init__(self, policy: OpportunityInterpretationPolicy | None = None) -> None:
        self._policy = policy or default_opportunity_policy()

    def capability(self) -> SpecialistCapability:
        return SpecialistCapability(
            specialist=SpecialistId.OPPORTUNITY_QUALITY,
            specialist_version=SPECIALIST_VERSION,
            display_name="Opportunity Quality Specialist",
            description="Interprets supplied A2/A3 opportunity maturity and evidence breadth.",
            supported_instrument_types=_USABLE_INSTRUMENTS,
            required_evidence_types=(EvidenceType.TECHNICAL,),
            optional_evidence_types=(
                EvidenceType.RELATIVE_STRENGTH,
                EvidenceType.SECTOR,
                EvidenceType.FUNDAMENTAL,
                EvidenceType.NEWS,
                EvidenceType.MACRO,
                EvidenceType.DERIVATIVES,
            ),
            allowed_capabilities=(AgentCapability.READ_A2_EVIDENCE,),
            supports_no_llm=True,
            cost_tier=SpecialistCostTier.LOW,
            prohibitions=(
                "NO_A2_RECOMPUTATION_OR_POLICY_CHANGE",
                "NO_PROVIDER_OR_NETWORK_ACCESS",
                "NO_MODEL_SDK_ACCESS",
                "NO_TRADING_OR_POSITION_ACTIONS",
                "NO_OPTION_EXPRESSION",
                "NO_FINAL_ARBITRATION",
            ),
        )

    def analyze(self, request: AgentRequest, evidence: AgentEvidencePack) -> AgentOpinionV2:
        _validate(
            request,
            evidence,
            SpecialistId.OPPORTUNITY_QUALITY,
            {AgentCapability.READ_A2_EVIDENCE},
        )
        book = ContextFactBook(evidence)
        families = self._families(book)
        present = tuple(name for name, records in families if _has_meaningful_evidence(records))
        candidate = _baseline_candidate(book)
        technical = dict(families)["TECHNICAL"]
        complete = (
            candidate is not None
            and _has_meaningful_evidence(technical)
            and len(present) >= self._policy.minimum_quality_families
        )
        maturity = self._maturity(candidate, technical)
        room = self._room(technical)
        supportive, adverse = self._alignment(families)
        event_near = _contains_state(dict(families)["EVENT"], {"NEAR", "IMMINENT"})
        state = self._state(candidate, maturity, room, supportive, adverse, event_near, complete)
        stance = {
            OpportunityQualityState.STRONG: AgentStance.POSITIVE,
            OpportunityQualityState.GOOD: AgentStance.POSITIVE,
            OpportunityQualityState.MIXED: AgentStance.MIXED,
            OpportunityQualityState.WEAK: AgentStance.NEGATIVE,
            OpportunityQualityState.INSUFFICIENT_EVIDENCE: AgentStance.INSUFFICIENT_EVIDENCE,
        }[state]
        contradictions = (
            (
                ContextContradiction(
                    code="OPPORTUNITY_CROSS_DOMAIN_CONFLICT",
                    description=(
                        "Supplied specialist/evidence families contain both "
                        "supportive and adverse context."
                    ),
                    evidence_ids=reference_ids(
                        _unique(
                            item
                            for name, records in families
                            if name in set((*supportive, *adverse))
                            for item in records
                        )
                    ),
                ),
            )
            if supportive and adverse
            else ()
        )
        agreement = 0.5 if contradictions else 1.0 if complete and (supportive or adverse) else 0.7
        reasons = self._reasons(
            candidate, maturity, room, supportive, adverse, event_near, evidence, complete
        )
        assessment = OpportunityQualityAssessment(
            assessment_id=f"{request.run_id}:opportunity-quality-assessment",
            specialist_version=SPECIALIST_VERSION,
            policy_id=self._policy.policy_id,
            policy_version=self._policy.policy_version,
            stance=stance,
            instrument_type=request.instrument_type,
            instrument_context=_instrument_context(request),
            horizon_context=_horizon_context(request),
            evidence_families=present,
            contradictions=contradictions,
            evidence_ids_by_family=_family_map(families),
            internal_agreement=agreement,
            confidence_basis=(
                "grouped_cross_domain_families_not_raw_fact_count",
                "baseline_maturity_room_conflict_quality_and_freshness",
                "confidence_is_not_success_probability",
            ),
            created_at=request.created_at,
            quality_state=state,
            maturity_state=maturity,
            remaining_room=room,
            baseline_candidate_class=candidate,
            supportive_families=supportive,
            adverse_families=adverse,
            reason_codes=reasons,
        )
        used = _unique(item for _, records in families for item in records)
        ids = reference_ids(used)
        missing = self._missing(request, evidence, complete)
        status = (
            AgentRunStatus.INSUFFICIENT_EVIDENCE
            if not complete
            else AgentRunStatus.PARTIAL
            if missing
            or evidence.overall_quality is not DataQuality.GOOD
            or evidence.overall_freshness is not FreshnessState.FRESH
            else AgentRunStatus.SUCCESS
        )
        summary = (
            f"Opportunity quality is {state.value}; maturity is {maturity.value}; "
            f"remaining room is {room.value}; cross-domain context has "
            f"{len(supportive)} supportive and {len(adverse)} adverse families."
        )
        return AgentOpinionV2(
            opinion_id=f"{request.run_id}:opportunity-quality-opinion",
            request_id=request.request_id,
            run_id=request.run_id,
            specialist=SpecialistId.OPPORTUNITY_QUALITY,
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
                        evidence,
                        agreement,
                        mapping_factor=min(
                            1.0, len(present) / self._policy.minimum_quality_families
                        )
                        if complete
                        else 0.0,
                    ),
                    policy_id=self._policy.policy_id,
                    policy_version=self._policy.policy_version,
                ),
            ),
            summary=summary,
            reason_codes=tuple(item.value for item in reasons),
            evidence_claims=_claims(f"{request.run_id}:quality", summary, used, evidence, request),
            supporting_evidence_ids=ids,
            missing_evidence=missing,
            risks=("Event proximity reduces timing cleanliness",) if event_near else (),
            caveats=(
                "Opportunity quality is attention context, not a recommendation or trade action",
            ),
            deterministic_baseline_reference=request.deterministic_baseline_reference,
            baseline_agreement=_quality_agreement(state, candidate),
            evidence_fingerprint=request.evidence_fingerprint,
            evidence_quality=evidence.overall_quality,
            evidence_freshness=evidence.overall_freshness,
            policy_version=self._policy.policy_version,
            usage=AgentUsage(),
            produced_at=request.created_at,
            specialist_detail_schema_id=QUALITY_DETAIL_SCHEMA,
            specialist_detail_json=assessment.canonical_json(),
            metadata={"replay_safe": True, "a2_evidence_unchanged": True},
        )

    @staticmethod
    def _families(
        book: ContextFactBook,
    ) -> tuple[tuple[str, tuple[FactRecord, ...]], ...]:
        return (
            ("BASELINE", _family_records(book, "baseline.")),
            ("TECHNICAL", _family_records(book, "technical.", "opportunity.")),
            ("RELATIVE", _family_records(book, "relative.")),
            ("SECTOR", _family_records(book, "sector.")),
            ("EVENT", _family_records(book, "event.", "news_event.")),
            ("FUNDAMENTAL", _family_records(book, "fundamental.")),
            ("MACRO", _family_records(book, "macro.")),
            ("DERIVATIVES", _family_records(book, "derivatives_context.")),
            ("LIQUIDITY", _family_records(book, "liquidity.")),
        )

    @staticmethod
    def _maturity(
        candidate: CandidateClass | None, technical: tuple[FactRecord, ...]
    ) -> OpportunityMaturityState:
        if candidate is CandidateClass.EARLY_OPPORTUNITY:
            return OpportunityMaturityState.EARLY
        if candidate in {
            CandidateClass.MATURE_AVOID_CHASE,
            CandidateClass.TOP_MOVER,
        } or _contains_state(technical, {"EXTENDED", "MATURE", "AVOID_CHASE"}):
            return OpportunityMaturityState.MATURE
        if candidate is not None:
            return OpportunityMaturityState.DEVELOPING
        return OpportunityMaturityState.UNKNOWN

    @staticmethod
    def _room(technical: tuple[FactRecord, ...]) -> RemainingRoomQuality:
        if _contains_state(technical, {"LIMITED", "LOW_ROOM", "NO_ROOM"}):
            return RemainingRoomQuality.LIMITED
        if _contains_state(technical, {"SUFFICIENT", "AMPLE", "AVAILABLE"}):
            return RemainingRoomQuality.SUFFICIENT
        return RemainingRoomQuality.UNKNOWN

    @staticmethod
    def _alignment(
        families: tuple[tuple[str, tuple[FactRecord, ...]], ...],
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        supportive: list[str] = []
        adverse: list[str] = []
        for name, records in families:
            if name in {"BASELINE", "TECHNICAL"}:
                continue
            positive = _contains_state(records, _POSITIVE)
            negative = _contains_state(records, _NEGATIVE)
            if positive and not negative:
                supportive.append(name)
            elif negative and not positive:
                adverse.append(name)
            elif positive and negative:
                supportive.append(name)
                adverse.append(name)
        return tuple(supportive), tuple(adverse)

    @staticmethod
    def _state(
        candidate: CandidateClass | None,
        maturity: OpportunityMaturityState,
        room: RemainingRoomQuality,
        supportive: tuple[str, ...],
        adverse: tuple[str, ...],
        event_near: bool,
        complete: bool,
    ) -> OpportunityQualityState:
        if not complete:
            return OpportunityQualityState.INSUFFICIENT_EVIDENCE
        if candidate is CandidateClass.NO_TRADE:
            return OpportunityQualityState.WEAK
        if maturity is OpportunityMaturityState.MATURE or room is RemainingRoomQuality.LIMITED:
            return OpportunityQualityState.WEAK if adverse else OpportunityQualityState.MIXED
        if supportive and adverse:
            return OpportunityQualityState.MIXED
        if event_near:
            return OpportunityQualityState.MIXED
        if candidate is CandidateClass.EARLY_OPPORTUNITY:
            return (
                OpportunityQualityState.STRONG
                if len(supportive) >= 2
                else OpportunityQualityState.GOOD
            )
        if candidate is CandidateClass.TOP_MOVER:
            return OpportunityQualityState.GOOD
        return (
            OpportunityQualityState.GOOD
            if supportive and not adverse
            else OpportunityQualityState.MIXED
        )

    @staticmethod
    def _reasons(
        candidate: CandidateClass | None,
        maturity: OpportunityMaturityState,
        room: RemainingRoomQuality,
        supportive: tuple[str, ...],
        adverse: tuple[str, ...],
        event_near: bool,
        evidence: AgentEvidencePack,
        complete: bool,
    ) -> tuple[OpportunityReasonCode, ...]:
        values: list[OpportunityReasonCode] = []
        if maturity is OpportunityMaturityState.EARLY:
            values.append(OpportunityReasonCode.OPPORTUNITY_EARLY)
        elif maturity is OpportunityMaturityState.MATURE:
            values.extend(
                (
                    OpportunityReasonCode.OPPORTUNITY_MATURE,
                    OpportunityReasonCode.OPPORTUNITY_EXTENDED,
                )
            )
        if room is RemainingRoomQuality.SUFFICIENT:
            values.append(OpportunityReasonCode.OPPORTUNITY_ROOM_SUFFICIENT)
        elif room is RemainingRoomQuality.LIMITED:
            values.append(OpportunityReasonCode.OPPORTUNITY_ROOM_LIMITED)
        if supportive:
            values.append(OpportunityReasonCode.OPPORTUNITY_CROSS_DOMAIN_SUPPORT)
        if supportive and adverse:
            values.append(OpportunityReasonCode.OPPORTUNITY_CROSS_DOMAIN_CONFLICT)
        values.append(
            OpportunityReasonCode.OPPORTUNITY_SETUP_MIXED
            if adverse
            else OpportunityReasonCode.OPPORTUNITY_SETUP_CLEAN
        )
        if candidate is CandidateClass.NO_TRADE:
            values.append(OpportunityReasonCode.OPPORTUNITY_BASELINE_NO_TRADE)
        if event_near:
            values.append(OpportunityReasonCode.EVENT_RISK_NEAR)
        if evidence.overall_freshness is FreshnessState.STALE:
            values.append(OpportunityReasonCode.EVIDENCE_STALE)
        if not complete:
            values.append(OpportunityReasonCode.EVIDENCE_INSUFFICIENT)
        return tuple(dict.fromkeys(values))

    @staticmethod
    def _missing(
        request: AgentRequest, evidence: AgentEvidencePack, complete: bool
    ) -> tuple[MissingEvidenceRequest, ...]:
        if complete:
            return evidence.missing_evidence
        return (
            *evidence.missing_evidence,
            MissingEvidenceRequest(
                missing_request_id=f"{request.run_id}:missing:quality-core",
                evidence_type=EvidenceType.TECHNICAL,
                capability=AgentCapability.READ_A2_EVIDENCE,
                subject=request.subject,
                reason=(
                    "A2 baseline, technical maturity, and adequate cross-domain "
                    "breadth are required"
                ),
                importance=EvidenceImportance.REQUIRED,
                requested_at=request.created_at,
            ),
        )


class OpportunityRiskSpecialist:
    """Expose grouped pre-arbitration opportunity risks without managing a position."""

    def __init__(self, policy: OpportunityInterpretationPolicy | None = None) -> None:
        self._policy = policy or default_opportunity_policy()

    def capability(self) -> SpecialistCapability:
        return SpecialistCapability(
            specialist=SpecialistId.OPPORTUNITY_RISK,
            specialist_version=SPECIALIST_VERSION,
            display_name="Opportunity Risk Specialist",
            description="Interprets supplied downside and invalidation risk families.",
            supported_instrument_types=_USABLE_INSTRUMENTS,
            required_evidence_types=(EvidenceType.TECHNICAL,),
            optional_evidence_types=(
                EvidenceType.RISK,
                EvidenceType.VOLATILITY,
                EvidenceType.NEWS,
                EvidenceType.SECTOR,
                EvidenceType.MACRO,
                EvidenceType.FUNDAMENTAL,
                EvidenceType.DERIVATIVES,
            ),
            allowed_capabilities=(AgentCapability.READ_A2_EVIDENCE,),
            supports_no_llm=True,
            cost_tier=SpecialistCostTier.LOW,
            prohibitions=(
                "NO_A2_RECOMPUTATION_OR_POLICY_CHANGE",
                "NO_PROVIDER_OR_NETWORK_ACCESS",
                "NO_MODEL_SDK_ACCESS",
                "NO_ORDER_STOP_TARGET_EXIT_OR_POSITION_ACTION",
                "NO_OPTION_EXPRESSION",
                "NO_FINAL_ARBITRATION",
            ),
        )

    def analyze(self, request: AgentRequest, evidence: AgentEvidencePack) -> AgentOpinionV2:
        _validate(
            request,
            evidence,
            SpecialistId.OPPORTUNITY_RISK,
            {AgentCapability.READ_A2_EVIDENCE},
        )
        book = ContextFactBook(evidence)
        families = self._families(book)
        present = tuple(name for name, records in families if _has_meaningful_evidence(records))
        active = self._active_risks(families, request)
        candidate = _baseline_candidate(book)
        complete = (
            _has_meaningful_evidence(
                (*dict(families)["BASELINE"], *dict(families)["EXTENSION_ROOM"])
            )
            and len(present) >= self._policy.minimum_quality_families
        )
        level = self._level(active, complete)
        stance = {
            OpportunityRiskLevel.LOW: AgentStance.NEUTRAL,
            OpportunityRiskLevel.MODERATE: AgentStance.MIXED,
            OpportunityRiskLevel.HIGH: AgentStance.NEGATIVE,
            OpportunityRiskLevel.CRITICAL: AgentStance.NEGATIVE,
            OpportunityRiskLevel.INSUFFICIENT_EVIDENCE: AgentStance.INSUFFICIENT_EVIDENCE,
        }[level]
        contradiction_records = dict(families)["CONTRADICTION"]
        if not contradiction_records and "CONTRADICTION" in active:
            contradiction_records = _unique(
                item
                for name, records in families
                if name != "CONTRADICTION"
                and _contains_state(records, {"MIXED", "CONFLICTED", "CONFLICT"})
                for item in records
            )
        contradictions = (
            (
                ContextContradiction(
                    code="OPPORTUNITY_RISK_CONTRADICTION_HIGH",
                    description=(
                        "Supplied evidence explicitly contains mixed or conflicting context."
                    ),
                    evidence_ids=reference_ids(contradiction_records),
                ),
            )
            if "CONTRADICTION" in active
            else ()
        )
        agreement = max(0.0, 1.0 - 0.15 * len(active)) if complete else 0.0
        reasons = self._reasons(active, evidence, complete)
        assessment = OpportunityRiskAssessment(
            assessment_id=f"{request.run_id}:opportunity-risk-assessment",
            specialist_version=SPECIALIST_VERSION,
            policy_id=self._policy.policy_id,
            policy_version=self._policy.policy_version,
            stance=stance,
            instrument_type=request.instrument_type,
            instrument_context=_instrument_context(request),
            horizon_context=_horizon_context(request),
            evidence_families=present,
            contradictions=contradictions,
            evidence_ids_by_family=_family_map(families),
            internal_agreement=agreement,
            confidence_basis=(
                "grouped_risk_families_not_correlated_raw_field_count",
                "evidence_coverage_quality_freshness_and_contradiction_burden",
                "confidence_is_not_success_probability",
            ),
            created_at=request.created_at,
            risk_level=level,
            active_risk_families=active,
            reason_codes=reasons,
        )
        used = _unique(item for _, records in families for item in records)
        ids = reference_ids(used)
        missing = self._missing(request, evidence, complete)
        status = (
            AgentRunStatus.INSUFFICIENT_EVIDENCE
            if not complete
            else AgentRunStatus.PARTIAL
            if missing
            or evidence.overall_quality is not DataQuality.GOOD
            or evidence.overall_freshness is not FreshnessState.FRESH
            else AgentRunStatus.SUCCESS
        )
        summary = (
            f"Opportunity risk is {level.value}; {len(active)} grouped risk families are active "
            f"for the {_horizon_context(request)} horizon."
        )
        return AgentOpinionV2(
            opinion_id=f"{request.run_id}:opportunity-risk-opinion",
            request_id=request.request_id,
            run_id=request.run_id,
            specialist=SpecialistId.OPPORTUNITY_RISK,
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
                        evidence,
                        agreement,
                        mapping_factor=min(
                            1.0, len(present) / self._policy.minimum_quality_families
                        )
                        if complete
                        else 0.0,
                    ),
                    policy_id=self._policy.policy_id,
                    policy_version=self._policy.policy_version,
                ),
            ),
            summary=summary,
            reason_codes=tuple(item.value for item in reasons),
            evidence_claims=_claims(f"{request.run_id}:risk", summary, used, evidence, request),
            supporting_evidence_ids=ids,
            missing_evidence=missing,
            risks=tuple(f"Active risk family: {name}" for name in active),
            caveats=(
                "Risk classification is pre-arbitration context, not a stop, target, "
                "exit, or position action",
            ),
            deterministic_baseline_reference=request.deterministic_baseline_reference,
            baseline_agreement=_risk_agreement(level, candidate),
            evidence_fingerprint=request.evidence_fingerprint,
            evidence_quality=evidence.overall_quality,
            evidence_freshness=evidence.overall_freshness,
            policy_version=self._policy.policy_version,
            usage=AgentUsage(),
            produced_at=request.created_at,
            specialist_detail_schema_id=RISK_DETAIL_SCHEMA,
            specialist_detail_json=assessment.canonical_json(),
            metadata={"replay_safe": True, "a2_evidence_unchanged": True},
        )

    @staticmethod
    def _families(
        book: ContextFactBook,
    ) -> tuple[tuple[str, tuple[FactRecord, ...]], ...]:
        return (
            ("BASELINE", _family_records(book, "baseline.")),
            (
                "EXTENSION_ROOM",
                _family_records(
                    book,
                    "technical.extension",
                    "technical.remaining_room",
                    "opportunity.extension",
                    "opportunity.remaining_room",
                ),
            ),
            ("PARTICIPATION", _family_records(book, "technical.participation", "participation.")),
            (
                "VOLATILITY",
                _family_records(
                    book, "technical.volatility", "volatility.", "derivatives_context.volatility"
                ),
            ),
            ("EVENT", _family_records(book, "event.", "news_event.")),
            ("CONTEXT", _family_records(book, "sector.", "macro.")),
            ("FUNDAMENTAL", _family_records(book, "fundamental.")),
            (
                "DERIVATIVES_CROWDING",
                _family_records(
                    book,
                    "derivatives_context.crowding",
                    "derivatives.ce_oi_top1",
                    "derivatives.pe_oi_top1",
                ),
            ),
            (
                "EXPIRY",
                _family_records(
                    book,
                    "derivatives.days_to_expiry",
                    "derivatives_context.expiry",
                ),
            ),
            (
                "LIQUIDITY",
                _family_records(
                    book,
                    "liquidity.",
                    "derivatives_context.liquidity",
                    "derivatives.atm_ce_bid_ask",
                    "derivatives.atm_pe_bid_ask",
                ),
            ),
            (
                "CONTRADICTION",
                _family_records(
                    book, "contradiction.", "technical.contradiction", "opportunity.contradiction"
                ),
            ),
        )

    @staticmethod
    def _active_risks(
        families: tuple[tuple[str, tuple[FactRecord, ...]], ...], request: AgentRequest
    ) -> tuple[str, ...]:
        values: list[str] = []
        records = dict(families)
        baseline = records["BASELINE"]
        if _contains_state(
            records["EXTENSION_ROOM"], {"EXTENDED", "MATURE", "HIGH_EXTENSION"}
        ) or _contains_state(baseline, {"MATURE_AVOID_CHASE"}):
            values.append("EXTENSION")
        if _contains_state(records["EXTENSION_ROOM"], {"LIMITED", "LOW_ROOM", "NO_ROOM"}):
            values.append("ROOM")
        if _contains_state(records["PARTICIPATION"], {"WEAK", "ABSENT", "NEGATIVE"}):
            values.append("PARTICIPATION")
        if _contains_state(records["VOLATILITY"], {"ELEVATED", "HIGH", "SHOCK"}):
            values.append("VOLATILITY")
        if _contains_state(records["EVENT"], {"NEAR", "IMMINENT", "EARNINGS", "BINARY"}):
            values.append("EVENT")
        if _horizon_context(request) != "MEDIUM" and any(
            not isinstance(item.fact.value, (str, bool)) and float(item.fact.value) <= 3
            for item in records["EXPIRY"]
        ):
            values.append("EXPIRY")
        if _contains_state(records["CONTEXT"], _NEGATIVE | {"CONFLICT"}):
            values.append("SECTOR_MACRO")
        if _horizon_context(request) != "DAY" and _contains_state(
            records["FUNDAMENTAL"], _NEGATIVE | {"HIGH_LEVERAGE", "GOVERNANCE"}
        ):
            values.append("FUNDAMENTAL")
        if _contains_state(records["DERIVATIVES_CROWDING"], {"CONCENTRATED", "CROWDED"}):
            values.append("DERIVATIVES_CROWDING")
        if _contains_state(records["LIQUIDITY"], {"WEAK", "POOR", "ILLIQUID"}):
            values.append("LIQUIDITY")
        if records["CONTRADICTION"] or any(
            _contains_state(items, {"MIXED", "CONFLICTED", "CONFLICT"})
            for name, items in families
            if name != "CONTRADICTION"
        ):
            values.append("CONTRADICTION")
        return tuple(dict.fromkeys(values))

    @staticmethod
    def _level(active: tuple[str, ...], complete: bool) -> OpportunityRiskLevel:
        if not complete:
            return OpportunityRiskLevel.INSUFFICIENT_EVIDENCE
        if len(active) >= 4:
            return OpportunityRiskLevel.CRITICAL
        if len(active) >= 2:
            return OpportunityRiskLevel.HIGH
        if len(active) == 1:
            return OpportunityRiskLevel.MODERATE
        return OpportunityRiskLevel.LOW

    @staticmethod
    def _reasons(
        active: tuple[str, ...], evidence: AgentEvidencePack, complete: bool
    ) -> tuple[RiskReasonCode, ...]:
        mapping = {
            "EXTENSION": RiskReasonCode.RISK_OVEREXTENDED,
            "ROOM": RiskReasonCode.RISK_ROOM_LIMITED,
            "PARTICIPATION": RiskReasonCode.RISK_PARTICIPATION_WEAK,
            "VOLATILITY": RiskReasonCode.RISK_VOLATILITY_SHOCK,
            "EVENT": RiskReasonCode.RISK_EVENT_GAP,
            "EXPIRY": RiskReasonCode.RISK_EXPIRY_PROXIMITY,
            "SECTOR_MACRO": RiskReasonCode.RISK_CONTEXT_CONFLICT,
            "FUNDAMENTAL": RiskReasonCode.RISK_FUNDAMENTAL_FRAGILITY,
            "DERIVATIVES_CROWDING": RiskReasonCode.RISK_DERIVATIVES_CROWDING,
            "LIQUIDITY": RiskReasonCode.RISK_LIQUIDITY_WEAK,
            "CONTRADICTION": RiskReasonCode.CONTRADICTION_HIGH,
        }
        values = [mapping[item] for item in active]
        if evidence.overall_freshness is FreshnessState.STALE:
            values.append(RiskReasonCode.EVIDENCE_STALE)
        if not complete:
            values.append(RiskReasonCode.EVIDENCE_INSUFFICIENT)
        return tuple(dict.fromkeys(values))

    @staticmethod
    def _missing(
        request: AgentRequest, evidence: AgentEvidencePack, complete: bool
    ) -> tuple[MissingEvidenceRequest, ...]:
        if complete:
            return evidence.missing_evidence
        return (
            *evidence.missing_evidence,
            MissingEvidenceRequest(
                missing_request_id=f"{request.run_id}:missing:risk-core",
                evidence_type=EvidenceType.RISK,
                capability=AgentCapability.READ_A2_EVIDENCE,
                subject=request.subject,
                reason="Baseline/extension context and adequate grouped risk evidence are required",
                importance=EvidenceImportance.REQUIRED,
                requested_at=request.created_at,
            ),
        )


def derivatives_context_assessment_from_opinion(
    opinion: AgentOpinionV2,
) -> DerivativesContextAssessment:
    if (
        opinion.specialist_detail_schema_id != DERIVATIVES_DETAIL_SCHEMA
        or opinion.specialist_detail_json is None
    ):
        raise ValueError("opinion does not contain A3.7 derivatives-context detail")
    return DerivativesContextAssessment.model_validate_json(opinion.specialist_detail_json)


def opportunity_quality_assessment_from_opinion(
    opinion: AgentOpinionV2,
) -> OpportunityQualityAssessment:
    if (
        opinion.specialist_detail_schema_id != QUALITY_DETAIL_SCHEMA
        or opinion.specialist_detail_json is None
    ):
        raise ValueError("opinion does not contain A3.7 opportunity-quality detail")
    return OpportunityQualityAssessment.model_validate_json(opinion.specialist_detail_json)


def opportunity_risk_assessment_from_opinion(
    opinion: AgentOpinionV2,
) -> OpportunityRiskAssessment:
    if (
        opinion.specialist_detail_schema_id != RISK_DETAIL_SCHEMA
        or opinion.specialist_detail_json is None
    ):
        raise ValueError("opinion does not contain A3.7 opportunity-risk detail")
    return OpportunityRiskAssessment.model_validate_json(opinion.specialist_detail_json)
