"""Deterministic A3.6 Macro Context specialist over bounded supplied evidence."""

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
from tiaf.market_context import SensitivityDirection

from .enums import (
    CommodityContextState,
    CurrencyState,
    MacroReasonCode,
    MacroVolatilityRegime,
    MarketRiskRegime,
    RateRegime,
    SubjectSensitivityState,
)
from .models import MacroAssessment, MacroContradiction
from .policy import MacroInterpretationPolicy, default_macro_policy

SPECIALIST_VERSION = "1.0"
MACRO_DETAIL_SCHEMA = "tiaf.macro-assessment/1.0"


class MacroSpecialist:
    """Interpret explicit market/macro state and sensitivities without acquisition."""

    def __init__(self, policy: MacroInterpretationPolicy | None = None) -> None:
        self._policy = policy or default_macro_policy()

    def capability(self) -> SpecialistCapability:
        return SpecialistCapability(
            specialist=SpecialistId.MACRO,
            specialist_version=SPECIALIST_VERSION,
            display_name="Macro Context Specialist",
            description=(
                "Interprets explicit horizon-relevant market, rates, currency, "
                "commodity, policy, and risk evidence."
            ),
            supported_instrument_types=(InstrumentType.EQUITY, InstrumentType.INDEX),
            required_evidence_types=(EvidenceType.MACRO,),
            optional_evidence_types=(
                EvidenceType.NEWS,
                EvidenceType.MARKET,
                EvidenceType.VOLATILITY,
            ),
            allowed_capabilities=(
                AgentCapability.READ_A2_EVIDENCE,
                AgentCapability.READ_MACRO_CONTEXT,
            ),
            supports_no_llm=True,
            cost_tier=SpecialistCostTier.LOW,
            prohibitions=(
                "NO_ARBITRARY_BROWSING",
                "NO_IMPLICIT_MACRO_SENSITIVITY",
                "NO_MACRO_CAUSALITY_FABRICATION",
                "NO_ONE_CANDLE_REGIME",
                "NO_MODEL_SDK_ACCESS",
                "NO_TRADING_OR_EXECUTION",
            ),
        )

    def analyze(self, request: AgentRequest, evidence: AgentEvidencePack) -> AgentOpinionV2:
        self._validate(request, evidence)
        book = ContextFactBook(evidence)
        macro_records = tuple(
            item
            for item in book.records
            if item.reference.evidence_type is EvidenceType.MACRO
            and item.fact.metric_id.startswith("macro.")
        )
        state_records = tuple(
            item
            for item in macro_records
            if self._context_kind(item) != "EVENT"
            and not item.fact.metric_id.startswith("macro.sensitivity.")
        )
        event_records = tuple(item for item in macro_records if self._context_kind(item) == "EVENT")
        market_values = self._market_dimensions(book)
        risk = self._risk_regime(market_values)
        volatility = self._volatility(book)
        if risk is MarketRiskRegime.RISK_OFF and volatility is MacroVolatilityRegime.EXTREME:
            risk = MarketRiskRegime.STRESS
        rates = self._rates(book)
        currency = self._currency(book)
        sensitivities = self._sensitivities(macro_records)
        commodity = self._commodity(book, sensitivities)
        rate_impact = self._mapped_direction_impact(
            -1 if rates is RateRegime.TIGHTENING else 1 if rates is RateRegime.EASING else 0,
            "interest_rates",
            sensitivities,
        )
        currency_impact = self._mapped_direction_impact(
            1
            if currency is CurrencyState.APPRECIATING
            else -1
            if currency is CurrencyState.DEPRECIATING
            else 0,
            "currency",
            sensitivities,
        )
        sensitivity_state = self._sensitivity_state(
            request.instrument_type, macro_records, sensitivities
        )
        growth = book.text("macro.growth.state")
        policy_context = book.text("macro.policy.state")
        geopolitical = book.text("macro.geopolitical.state")
        impact_signs = self._impact_signs(
            risk,
            commodity,
            rate_impact,
            currency_impact,
            request.instrument_type,
        )
        contradictions = self._contradictions(impact_signs, macro_records)
        complete = (
            bool(state_records)
            and (
                risk is not MarketRiskRegime.UNKNOWN
                or sensitivity_state
                in {SubjectSensitivityState.MAPPED, SubjectSensitivityState.NOT_APPLICABLE}
            )
            and sensitivity_state
            not in {
                SubjectSensitivityState.MAPPING_REQUIRED,
                SubjectSensitivityState.PARTIAL,
            }
        )
        stance = self._stance(impact_signs, complete)
        reasons = self._reasons(
            risk,
            volatility,
            rates,
            commodity,
            currency_impact,
            sensitivity_state,
            contradictions,
            evidence,
            complete,
        )
        agreement = (
            0.5
            if contradictions
            else 1.0
            if impact_signs and len(set(impact_signs)) == 1
            else 0.65
            if impact_signs
            else 0.0
        )
        horizon_relevance = 1.0 if state_records or event_records else 0.0
        market = next(
            (
                item.reference.metadata.get("market")
                for item in macro_records
                if isinstance(item.reference.metadata.get("market"), str)
            ),
            None,
        )
        assessment = MacroAssessment(
            assessment_id=f"{request.run_id}:macro-assessment",
            specialist_version=SPECIALIST_VERSION,
            policy_id=self._policy.policy_id,
            policy_version=self._policy.policy_version,
            stance=stance,
            market=str(market) if market else None,
            market_risk_regime=risk,
            volatility_regime=volatility,
            rate_regime=rates,
            currency_context=currency,
            commodity_context=commodity,
            growth_context=growth,
            policy_context=policy_context,
            geopolitical_risk=geopolitical,
            subject_sensitivity=sensitivity_state,
            horizon_relevance=horizon_relevance,
            contradictions=contradictions,
            evidence_ids_by_dimension=(
                ("MARKET_RISK", reference_ids(self._risk_records(book))),
                ("VOLATILITY", reference_ids(book.prefix("macro.volatility."))),
                (
                    "RATES",
                    reference_ids((*book.prefix("macro.rates."), *book.prefix("macro.yields."))),
                ),
                ("CURRENCY", reference_ids(book.prefix("macro.currency."))),
                ("COMMODITIES", reference_ids(book.prefix("macro.commodity."))),
                ("SUBJECT_SENSITIVITY", reference_ids(book.prefix("macro.sensitivity."))),
                ("MACRO_EVENTS", reference_ids(event_records)),
            ),
            evidence_coverage=evidence.evidence_coverage,
            internal_agreement=agreement,
            confidence_basis=(
                "explicit_point_in_time_macro_state",
                "explicit_subject_sensitivity_mapping",
                "horizon_relevance_and_dimensional_agreement",
                "not_probability_of_market_success",
            ),
            reason_codes=reasons,
            created_at=request.created_at,
        )
        missing = self._missing(request, evidence, complete, sensitivity_state)
        used = self._unique((*macro_records, *book.exact("baseline.direction")))
        ids = reference_ids(used)
        status = (
            AgentRunStatus.INSUFFICIENT_EVIDENCE
            if not complete
            else AgentRunStatus.PARTIAL
            if missing
            or evidence.overall_quality is not DataQuality.GOOD
            or evidence.overall_freshness is not FreshnessState.FRESH
            else AgentRunStatus.SUCCESS
        )
        mapping_factor = (
            1.0
            if sensitivity_state
            in {SubjectSensitivityState.MAPPED, SubjectSensitivityState.NOT_APPLICABLE}
            else 0.75
            if sensitivity_state is SubjectSensitivityState.UNKNOWN
            else 0.5
            if sensitivity_state is SubjectSensitivityState.PARTIAL
            else 0.0
        )
        return AgentOpinionV2(
            opinion_id=f"{request.run_id}:macro-opinion",
            request_id=request.request_id,
            run_id=request.run_id,
            specialist=SpecialistId.MACRO,
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
                        mapping_factor=mapping_factor,
                        relevance=horizon_relevance,
                    ),
                    policy_id=self._policy.policy_id,
                    policy_version=self._policy.policy_version,
                ),
            ),
            summary=(
                f"Macro context is {stance.value}: market risk {risk.value}, "
                f"volatility {volatility.value}, rates {rates.value}, "
                f"currency {currency.value}, commodities {commodity.value}; "
                f"sensitivity {sensitivity_state.value}."
            ),
            reason_codes=tuple(item.value for item in reasons),
            evidence_claims=factual_claims(f"{request.run_id}:macro", used),
            supporting_evidence_ids=ids,
            missing_evidence=missing,
            risks=("Macro dimensions conflict; no single causal narrative is asserted",)
            if contradictions
            else (),
            caveats=(
                "Macro event identity is kept separate from persistent macro state",
                "No macro variable is treated as company impact without explicit sensitivity",
            ),
            deterministic_baseline_reference=request.deterministic_baseline_reference,
            baseline_agreement=baseline_agreement(stance, baseline_direction(book)),
            evidence_fingerprint=request.evidence_fingerprint,
            evidence_quality=evidence.overall_quality,
            evidence_freshness=evidence.overall_freshness,
            policy_version=self._policy.policy_version,
            usage=AgentUsage(),
            produced_at=request.created_at,
            specialist_detail_schema_id=MACRO_DETAIL_SCHEMA,
            specialist_detail_json=assessment.canonical_json(),
        )

    @staticmethod
    def _context_kind(record: FactRecord) -> str | None:
        return next(
            (str(item.value) for item in record.fact.parameters if item.name == "context_kind"),
            None,
        )

    def _market_dimensions(self, book: ContextFactBook) -> tuple[float, ...]:
        values: list[float] = []
        score = book.number("macro.market_risk.score")
        if score is not None:
            values.append(max(-1.0, min(1.0, score)))
        index_return = book.number("macro.market_index.return_percent")
        if index_return is not None:
            values.append(1.0 if index_return > 1 else -1.0 if index_return < -1 else 0.0)
        global_risk = book.number("macro.global_risk.score")
        if global_risk is not None:
            values.append(max(-1.0, min(1.0, global_risk)))
        liquidity = book.number("macro.liquidity.score")
        if liquidity is not None:
            values.append(max(-1.0, min(1.0, liquidity)))
        volatility = book.number("macro.volatility.percentile")
        if volatility is not None and volatility >= self._policy.volatility_high_percentile:
            values.append(-1.0)
        return tuple(values)

    def _risk_regime(self, values: tuple[float, ...]) -> MarketRiskRegime:
        if len(values) < self._policy.minimum_risk_dimensions:
            return MarketRiskRegime.UNKNOWN
        if any(item > self._policy.risk_material_score for item in values) and any(
            item < -self._policy.risk_material_score for item in values
        ):
            return MarketRiskRegime.MIXED
        average = sum(values) / len(values)
        if average >= self._policy.risk_strong_score:
            return MarketRiskRegime.RISK_ON
        if average >= self._policy.risk_material_score:
            return MarketRiskRegime.MILD_RISK_ON
        if average <= -self._policy.risk_strong_score:
            return MarketRiskRegime.RISK_OFF
        if average <= -self._policy.risk_material_score:
            return MarketRiskRegime.MILD_RISK_OFF
        return MarketRiskRegime.NEUTRAL

    def _volatility(self, book: ContextFactBook) -> MacroVolatilityRegime:
        explicit = book.text("macro.volatility.regime")
        if explicit:
            try:
                return MacroVolatilityRegime(explicit)
            except ValueError:
                pass
        value = book.number("macro.volatility.percentile")
        if value is None:
            return MacroVolatilityRegime.UNKNOWN
        if value >= self._policy.volatility_extreme_percentile:
            return MacroVolatilityRegime.EXTREME
        if value >= self._policy.volatility_high_percentile:
            return MacroVolatilityRegime.HIGH
        if value >= self._policy.volatility_elevated_percentile:
            return MacroVolatilityRegime.ELEVATED
        if value <= 0.2:
            return MacroVolatilityRegime.LOW
        return MacroVolatilityRegime.NORMAL

    def _rates(self, book: ContextFactBook) -> RateRegime:
        explicit = book.text("macro.rates.regime")
        if explicit:
            try:
                return RateRegime(explicit)
            except ValueError:
                pass
        change = book.number("macro.rates.change_bps")
        if change is None:
            change = book.number("macro.yields.change_bps")
        if change is None:
            return RateRegime.UNKNOWN
        if change >= self._policy.rate_material_bps:
            return RateRegime.TIGHTENING
        if change <= -self._policy.rate_material_bps:
            return RateRegime.EASING
        return RateRegime.NEUTRAL

    def _currency(self, book: ContextFactBook) -> CurrencyState:
        explicit = book.text("macro.currency.state")
        if explicit:
            try:
                return CurrencyState(explicit)
            except ValueError:
                pass
        change = book.number("macro.currency.change_percent")
        if change is None:
            return CurrencyState.UNKNOWN
        if change >= self._policy.currency_material_percent:
            return CurrencyState.APPRECIATING
        if change <= -self._policy.currency_material_percent:
            return CurrencyState.DEPRECIATING
        return CurrencyState.STABLE

    @staticmethod
    def _sensitivities(records: tuple[FactRecord, ...]) -> dict[str, SensitivityDirection]:
        values: dict[str, SensitivityDirection] = {}
        for item in records:
            if not item.fact.metric_id.startswith("macro.sensitivity.") or not isinstance(
                item.fact.value, str
            ):
                continue
            driver = next(
                (
                    str(parameter.value)
                    for parameter in item.fact.parameters
                    if parameter.name == "driver_id" and parameter.value is not None
                ),
                item.fact.metric_id.removeprefix("macro.sensitivity."),
            )
            try:
                values[driver] = SensitivityDirection(item.fact.value)
            except ValueError:
                continue
        return values

    def _commodity(
        self, book: ContextFactBook, sensitivities: dict[str, SensitivityDirection]
    ) -> CommodityContextState:
        explicit = book.text("macro.commodity.context")
        if explicit:
            try:
                return CommodityContextState(explicit)
            except ValueError:
                pass
        changes = tuple(
            item
            for item in book.prefix("macro.commodity.")
            if item.fact.metric_id.endswith("change_percent")
            and not isinstance(item.fact.value, (str, bool))
        )
        impacts: list[int] = []
        for item in changes:
            driver = next(
                (
                    str(parameter.value)
                    for parameter in item.fact.parameters
                    if parameter.name == "driver_id" and parameter.value is not None
                ),
                "",
            )
            sensitivity = sensitivities.get(driver)
            if sensitivity is None or sensitivity in {
                SensitivityDirection.UNKNOWN,
                SensitivityDirection.NOT_APPLICABLE,
                SensitivityDirection.NEUTRAL,
            }:
                continue
            rising = float(item.fact.value) > 0
            favorable = (sensitivity is SensitivityDirection.BENEFITS_FROM_RISE) == rising
            impacts.append(1 if favorable else -1)
        if 1 in impacts and -1 in impacts:
            return CommodityContextState.VOLATILE
        if 1 in impacts:
            return CommodityContextState.FAVORABLE
        if -1 in impacts:
            return CommodityContextState.ADVERSE
        return CommodityContextState.UNKNOWN

    @staticmethod
    def _sensitivity_state(
        instrument_type: InstrumentType,
        records: tuple[FactRecord, ...],
        sensitivities: dict[str, SensitivityDirection],
    ) -> SubjectSensitivityState:
        if instrument_type is InstrumentType.INDEX:
            return SubjectSensitivityState.NOT_APPLICABLE
        drivers = {
            next(
                (
                    str(parameter.value)
                    for parameter in item.fact.parameters
                    if parameter.name == "driver_id" and parameter.value is not None
                ),
                "",
            )
            for item in records
            if item.fact.metric_id.startswith(
                ("macro.currency.", "macro.commodity.", "macro.rates.", "macro.yields.")
            )
        }
        drivers.discard("")
        mapped = {
            key
            for key, value in sensitivities.items()
            if value not in {SensitivityDirection.UNKNOWN}
        }
        if not drivers:
            return SubjectSensitivityState.UNKNOWN
        if drivers and drivers <= mapped:
            return SubjectSensitivityState.MAPPED
        if drivers & mapped:
            return SubjectSensitivityState.PARTIAL
        if sensitivities and all(
            value is SensitivityDirection.NOT_APPLICABLE for value in sensitivities.values()
        ):
            return SubjectSensitivityState.NOT_APPLICABLE
        return SubjectSensitivityState.MAPPING_REQUIRED

    @staticmethod
    def _impact_signs(
        risk: MarketRiskRegime,
        commodity: CommodityContextState,
        rate_impact: int,
        currency_impact: int,
        instrument_type: InstrumentType,
    ) -> tuple[int, ...]:
        values: list[int] = []
        if risk in {MarketRiskRegime.RISK_ON, MarketRiskRegime.MILD_RISK_ON}:
            values.append(1)
        elif risk in {
            MarketRiskRegime.RISK_OFF,
            MarketRiskRegime.MILD_RISK_OFF,
            MarketRiskRegime.STRESS,
        }:
            values.append(-1)
        elif risk is MarketRiskRegime.MIXED:
            values.extend((1, -1))
        if commodity is CommodityContextState.FAVORABLE:
            values.append(1)
        elif commodity is CommodityContextState.ADVERSE:
            values.append(-1)
        values.extend(item for item in (rate_impact, currency_impact) if item)
        if (
            instrument_type is InstrumentType.INDEX
            and not values
            and risk is MarketRiskRegime.NEUTRAL
        ):
            values.append(0)
        return tuple(values)

    @staticmethod
    def _mapped_direction_impact(
        state_sign: int,
        family_marker: str,
        sensitivities: dict[str, SensitivityDirection],
    ) -> int:
        sensitivity = next(
            (value for key, value in sensitivities.items() if family_marker in key.lower()),
            None,
        )
        if not state_sign or sensitivity not in {
            SensitivityDirection.BENEFITS_FROM_RISE,
            SensitivityDirection.HARMED_BY_RISE,
        }:
            return 0
        return state_sign if sensitivity is SensitivityDirection.BENEFITS_FROM_RISE else -state_sign

    @staticmethod
    def _contradictions(
        signs: tuple[int, ...], records: tuple[FactRecord, ...]
    ) -> tuple[MacroContradiction, ...]:
        if 1 in signs and -1 in signs:
            return (
                MacroContradiction(
                    code="MACRO_DIMENSION_CONFLICT",
                    description="Supplied macro dimensions have opposing subject implications.",
                    evidence_ids=reference_ids(records),
                ),
            )
        return ()

    @staticmethod
    def _stance(signs: tuple[int, ...], complete: bool) -> AgentStance:
        if not complete:
            return AgentStance.INSUFFICIENT_EVIDENCE
        if 1 in signs and -1 in signs:
            return AgentStance.MIXED
        if 1 in signs:
            return AgentStance.POSITIVE
        if -1 in signs:
            return AgentStance.NEGATIVE
        return AgentStance.NEUTRAL

    @staticmethod
    def _reasons(
        risk: MarketRiskRegime,
        volatility: MacroVolatilityRegime,
        rates: RateRegime,
        commodity: CommodityContextState,
        currency_impact: int,
        sensitivity: SubjectSensitivityState,
        contradictions: tuple[MacroContradiction, ...],
        evidence: AgentEvidencePack,
        complete: bool,
    ) -> tuple[MacroReasonCode, ...]:
        values: list[MacroReasonCode] = []
        if risk in {MarketRiskRegime.RISK_ON, MarketRiskRegime.MILD_RISK_ON}:
            values.append(MacroReasonCode.RISK_ON_CONTEXT)
        elif risk in {MarketRiskRegime.RISK_OFF, MarketRiskRegime.MILD_RISK_OFF}:
            values.append(MacroReasonCode.RISK_OFF_CONTEXT)
        elif risk is MarketRiskRegime.STRESS:
            values.append(MacroReasonCode.MARKET_STRESS)
        if volatility in {
            MacroVolatilityRegime.ELEVATED,
            MacroVolatilityRegime.HIGH,
            MacroVolatilityRegime.EXTREME,
            MacroVolatilityRegime.EXPANDING,
        }:
            values.append(MacroReasonCode.VOLATILITY_ELEVATED)
        if rates is RateRegime.TIGHTENING:
            values.append(MacroReasonCode.RATES_TIGHTENING)
        elif rates is RateRegime.EASING:
            values.append(MacroReasonCode.RATES_EASING)
        if currency_impact > 0:
            values.append(MacroReasonCode.CURRENCY_FAVORABLE)
        elif currency_impact < 0:
            values.append(MacroReasonCode.CURRENCY_ADVERSE)
        if commodity is CommodityContextState.FAVORABLE:
            values.append(MacroReasonCode.COMMODITY_FAVORABLE)
        elif commodity is CommodityContextState.ADVERSE:
            values.append(MacroReasonCode.COMMODITY_ADVERSE)
        if sensitivity in {
            SubjectSensitivityState.UNKNOWN,
            SubjectSensitivityState.MAPPING_REQUIRED,
        }:
            values.append(MacroReasonCode.MACRO_SENSITIVITY_UNKNOWN)
        if contradictions:
            values.append(MacroReasonCode.MACRO_CONFLICT)
        if evidence.overall_quality is not DataQuality.GOOD:
            values.append(MacroReasonCode.MACRO_EVIDENCE_PARTIAL)
        if evidence.overall_freshness is FreshnessState.STALE:
            values.append(MacroReasonCode.MACRO_EVIDENCE_STALE)
        if not complete:
            values.append(MacroReasonCode.MACRO_EVIDENCE_INSUFFICIENT)
        return tuple(dict.fromkeys(values))

    @staticmethod
    def _risk_records(book: ContextFactBook) -> tuple[FactRecord, ...]:
        return (
            *book.prefix("macro.market_risk."),
            *book.prefix("macro.market_index."),
            *book.prefix("macro.global_risk."),
            *book.prefix("macro.liquidity."),
            *book.prefix("macro.volatility."),
        )

    @staticmethod
    def _missing(
        request: AgentRequest,
        evidence: AgentEvidencePack,
        complete: bool,
        sensitivity: SubjectSensitivityState,
    ) -> tuple[MissingEvidenceRequest, ...]:
        values = list(evidence.missing_evidence)
        if not complete:
            reason = (
                "Explicit subject macro sensitivity mapping is required"
                if sensitivity
                in {
                    SubjectSensitivityState.UNKNOWN,
                    SubjectSensitivityState.MAPPING_REQUIRED,
                    SubjectSensitivityState.PARTIAL,
                }
                else "Horizon-relevant macro state evidence is required"
            )
            values.append(
                MissingEvidenceRequest(
                    missing_request_id=f"{request.run_id}:missing:macro-core",
                    evidence_type=EvidenceType.MACRO,
                    capability=AgentCapability.READ_MACRO_CONTEXT,
                    subject=request.subject,
                    reason=reason,
                    importance=EvidenceImportance.REQUIRED,
                    requested_at=request.created_at,
                )
            )
        return tuple(values)

    @staticmethod
    def _unique(records: tuple[FactRecord, ...]) -> tuple[FactRecord, ...]:
        values: dict[str, FactRecord] = {}
        for item in records:
            values.setdefault(item.fact.fact_id, item)
        return tuple(values.values())

    @staticmethod
    def _validate(request: AgentRequest, evidence: AgentEvidencePack) -> None:
        if request.specialist is not SpecialistId.MACRO:
            raise ValueError("MacroSpecialist requires MACRO identity")
        if not {AgentCapability.READ_A2_EVIDENCE, AgentCapability.READ_MACRO_CONTEXT} <= set(
            request.allowed_capabilities
        ):
            raise ValueError("MacroSpecialist requires bounded A2 and macro-context authorization")
        if (
            evidence.request_id != request.request_id
            or evidence.subject != request.subject
            or evidence.evidence_fingerprint != request.evidence_fingerprint
            or evidence.deterministic_assessment_id != request.deterministic_baseline_reference
        ):
            raise ValueError("macro evidence does not preserve request/A2 identity")


def macro_assessment_from_opinion(opinion: AgentOpinionV2) -> MacroAssessment:
    if (
        opinion.specialist_detail_schema_id != MACRO_DETAIL_SCHEMA
        or opinion.specialist_detail_json is None
    ):
        raise ValueError("opinion does not contain A3.6 macro detail")
    return MacroAssessment.model_validate_json(opinion.specialist_detail_json)
