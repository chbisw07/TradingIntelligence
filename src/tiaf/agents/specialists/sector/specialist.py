"""Deterministic A3.6 Sector / Rotation specialist over explicit context."""

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

from .enums import (
    RotationState,
    SectorBreadthState,
    SectorConcentrationState,
    SectorParticipationState,
    SectorReasonCode,
    SectorState,
    SubjectSectorState,
)
from .models import SectorAssessment, SectorContradiction
from .policy import SectorInterpretationPolicy, default_sector_policy

SPECIALIST_VERSION = "1.0"
SECTOR_DETAIL_SCHEMA = "tiaf.sector-assessment/1.0"


class SectorSpecialist:
    """Interpret explicit sector evidence; no mappings, fetches, or A2 calculations."""

    def __init__(self, policy: SectorInterpretationPolicy | None = None) -> None:
        self._policy = policy or default_sector_policy()

    def capability(self) -> SpecialistCapability:
        return SpecialistCapability(
            specialist=SpecialistId.SECTOR,
            specialist_version=SPECIALIST_VERSION,
            display_name="Sector / Rotation Specialist",
            description=(
                "Interprets explicit sector mapping, relative, breadth, and participation evidence."
            ),
            supported_instrument_types=(InstrumentType.EQUITY, InstrumentType.INDEX),
            required_evidence_types=(EvidenceType.SECTOR,),
            optional_evidence_types=(
                EvidenceType.RELATIVE_STRENGTH,
                EvidenceType.NEWS,
                EvidenceType.MARKET,
            ),
            allowed_capabilities=(
                AgentCapability.READ_A2_EVIDENCE,
                AgentCapability.READ_SECTOR_CONTEXT,
            ),
            supports_no_llm=True,
            cost_tier=SpecialistCostTier.LOW,
            prohibitions=(
                "NO_IMPLICIT_SECTOR_MAPPING",
                "NO_ONE_PERIOD_ROTATION_CLAIM",
                "NO_PROVIDER_OR_NETWORK_ACCESS",
                "NO_MODEL_SDK_ACCESS",
                "NO_TRADING_OR_EXECUTION",
            ),
        )

    def analyze(self, request: AgentRequest, evidence: AgentEvidencePack) -> AgentOpinionV2:
        self._validate(request, evidence)
        book = ContextFactBook(evidence)
        sector_records = tuple(
            item
            for item in book.records
            if item.reference.evidence_type is EvidenceType.SECTOR
            and item.fact.metric_id.startswith("sector.")
        )
        mapping_records = tuple(
            item for item in sector_records if item.fact.metric_id.startswith("sector.mapping.")
        )
        sector_id = book.text("sector.mapping.sector_id")
        benchmark_symbol = book.text("sector.mapping.benchmark_symbol")
        mapping_ref = mapping_records[0].reference if mapping_records else None
        sector_name = mapping_ref.metadata.get("sector_name") if mapping_ref else None
        mapping_version = mapping_ref.metadata.get("mapping_version") if mapping_ref else None
        mapping_quality = mapping_ref.metadata.get("mapping_quality") if mapping_ref else None
        mapping_complete = (
            all(
                isinstance(item, str) and item
                for item in (sector_id, benchmark_symbol, sector_name, mapping_version)
            )
            and mapping_ref is not None
            and mapping_quality not in {"AMBIGUOUS", "UNKNOWN"}
        )
        relative_records = tuple(
            item
            for item in sector_records
            if item.fact.metric_id == "sector.relative_return_percent"
            and not isinstance(item.fact.value, (str, bool))
        )
        relative_values = tuple(
            float(item.fact.value) for item in self._period_order(relative_records)
        )
        absolute_return = book.number("sector.return_percent")
        sector_state = (
            self._sector_state(relative_values, absolute_return)
            if mapping_complete
            else SectorState.INSUFFICIENT_EVIDENCE
        )
        rotation = self._rotation(relative_values)
        subject_spread = book.number("sector.subject_return_spread_percent")
        subject_state = self._subject_state(subject_spread)
        breadth_records = tuple(
            item
            for item in sector_records
            if item.fact.metric_id
            in {"sector.breadth.positive_fraction", "sector.breadth.above_ma_fraction"}
            and not isinstance(item.fact.value, (str, bool))
        )
        breadth = self._breadth(tuple(float(item.fact.value) for item in breadth_records))
        concentration_value = book.number("sector.participation.top_constituent_fraction")
        participation = (
            SectorParticipationState.UNKNOWN
            if concentration_value is None
            else SectorParticipationState.NARROW
            if concentration_value >= self._policy.narrow_concentration_fraction
            else SectorParticipationState.BROAD
        )
        concentration = self._concentration(sector_state, breadth, participation)
        catalyst_records = tuple(
            item
            for item in sector_records
            if item.fact.metric_id == "sector.catalyst_direction"
            and isinstance(item.fact.value, str)
        )
        catalyst_context = tuple(dict.fromkeys(str(item.fact.value) for item in catalyst_records))
        contradictions = self._contradictions(
            sector_state, subject_state, breadth, participation, sector_records
        )
        stance = self._stance(sector_state, subject_state, mapping_complete)
        reasons = self._reasons(
            sector_state,
            rotation,
            subject_state,
            breadth,
            concentration,
            catalyst_context,
            evidence,
            mapping_complete,
            mapping_quality,
        )
        signs = [self._sign(value) for value in relative_values if self._sign(value)]
        agreement = (
            0.5
            if contradictions
            else 1.0
            if signs and len(set(signs)) == 1
            else 0.6
            if mapping_complete
            else 0.0
        )
        assessment = SectorAssessment(
            assessment_id=f"{request.run_id}:sector-assessment",
            specialist_version=SPECIALIST_VERSION,
            policy_id=self._policy.policy_id,
            policy_version=self._policy.policy_version,
            stance=stance,
            sector_id=sector_id if mapping_complete else None,
            sector_name=str(sector_name) if mapping_complete else None,
            benchmark_symbol=benchmark_symbol if mapping_complete else None,
            mapping_source=mapping_ref.producer_id if mapping_complete and mapping_ref else None,
            mapping_version=str(mapping_version) if mapping_complete else None,
            sector_state=sector_state,
            rotation_state=rotation,
            subject_vs_sector=subject_state,
            breadth_state=breadth,
            participation_state=participation,
            concentration_state=concentration,
            catalyst_context=catalyst_context,
            contradictions=contradictions,
            evidence_ids_by_dimension=(
                ("MAPPING", reference_ids(mapping_records)),
                ("SECTOR_VS_MARKET", reference_ids(relative_records)),
                (
                    "SUBJECT_VS_SECTOR",
                    reference_ids(book.exact("sector.subject_return_spread_percent")),
                ),
                ("BREADTH", reference_ids(breadth_records)),
                (
                    "PARTICIPATION",
                    reference_ids(book.exact("sector.participation.top_constituent_fraction")),
                ),
                ("CATALYST", reference_ids(catalyst_records)),
            ),
            evidence_coverage=evidence.evidence_coverage,
            internal_agreement=agreement,
            confidence_basis=(
                "explicit_versioned_sector_mapping",
                "multi_period_relative_evidence_for_rotation",
                "breadth_and_participation_when_supplied",
                "not_probability_of_market_success",
            ),
            reason_codes=reasons,
            created_at=request.created_at,
        )
        complete = mapping_complete and bool(relative_values or absolute_return is not None)
        missing = self._missing(request, evidence, complete, mapping_complete)
        used = self._unique((*sector_records, *book.exact("baseline.direction")))
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
        mapping_factor = 1.0 if mapping_quality == "VERIFIED" else 0.85 if mapping_complete else 0.0
        return AgentOpinionV2(
            opinion_id=f"{request.run_id}:sector-opinion",
            request_id=request.request_id,
            run_id=request.run_id,
            specialist=SpecialistId.SECTOR,
            specialist_version=SPECIALIST_VERSION,
            subject=request.subject,
            horizon=request.horizon,
            stance=stance,
            status=status,
            confidence=AgentConfidence(
                evidence_coverage=evidence.evidence_coverage,
                evidence_quality=evidence.overall_quality,
                policy_derived=PolicyDerivedConfidence(
                    value=confidence_value(evidence, agreement, mapping_factor=mapping_factor),
                    policy_id=self._policy.policy_id,
                    policy_version=self._policy.policy_version,
                ),
            ),
            summary=(
                f"Sector context is {sector_state.value}; rotation is {rotation.value}; "
                f"subject fit is {subject_state.value}; breadth is {breadth.value}."
            ),
            reason_codes=tuple(item.value for item in reasons),
            evidence_claims=factual_claims(f"{request.run_id}:sector", used),
            supporting_evidence_ids=ids,
            missing_evidence=missing,
            risks=("Sector leadership is concentrated rather than broad",)
            if concentration is SectorConcentrationState.CONCENTRATED_LEADERSHIP
            else (),
            caveats=(
                "Rotation requires multiple supplied periods; one return never establishes it",
            ),
            deterministic_baseline_reference=request.deterministic_baseline_reference,
            baseline_agreement=baseline_agreement(stance, baseline_direction(book)),
            evidence_fingerprint=request.evidence_fingerprint,
            evidence_quality=evidence.overall_quality,
            evidence_freshness=evidence.overall_freshness,
            policy_version=self._policy.policy_version,
            usage=AgentUsage(),
            produced_at=request.created_at,
            specialist_detail_schema_id=SECTOR_DETAIL_SCHEMA,
            specialist_detail_json=assessment.canonical_json(),
        )

    @staticmethod
    def _period_order(records: tuple[FactRecord, ...]) -> tuple[FactRecord, ...]:
        def days(interval: str | None) -> float:
            if not interval:
                return 1e9
            suffix = interval[-1].lower()
            try:
                value = float(interval[:-1])
            except ValueError:
                return 1e9
            return value * {"m": 1 / 1440, "h": 1 / 24, "d": 1, "w": 7}.get(
                suffix, 30 if suffix == "o" else 1
            )

        return tuple(
            sorted(records, key=lambda item: (days(item.fact.interval), item.fact.fact_id))
        )

    def _sign(self, value: float) -> int:
        return (
            1
            if value > self._policy.relative_material_percent
            else -1
            if value < -self._policy.relative_material_percent
            else 0
        )

    def _sector_state(self, values: tuple[float, ...], absolute: float | None) -> SectorState:
        signs = tuple(self._sign(item) for item in values)
        if 1 in signs and -1 in signs:
            return SectorState.MIXED
        if signs and all(item >= 0 for item in signs) and any(item > 0 for item in signs):
            return (
                SectorState.STRONG
                if absolute is not None and absolute > 0
                else SectorState.SUPPORTIVE
            )
        if signs and all(item <= 0 for item in signs) and any(item < 0 for item in signs):
            return (
                SectorState.VERY_WEAK if absolute is not None and absolute < 0 else SectorState.WEAK
            )
        if absolute is not None:
            return (
                SectorState.SUPPORTIVE
                if absolute > self._policy.relative_material_percent
                else SectorState.WEAK
                if absolute < -self._policy.relative_material_percent
                else SectorState.NEUTRAL
            )
        return SectorState.INSUFFICIENT_EVIDENCE

    def _rotation(self, values: tuple[float, ...]) -> RotationState:
        if len(values) < self._policy.minimum_rotation_periods:
            return RotationState.INSUFFICIENT_EVIDENCE
        short, long = values[0], values[-1]
        signs = tuple(self._sign(item) for item in values)
        if (
            short > self._policy.relative_material_percent
            and long < -self._policy.relative_material_percent
        ):
            return RotationState.ROTATING_IN
        if (
            short < -self._policy.relative_material_percent
            and long > self._policy.relative_material_percent
        ):
            return RotationState.ROTATING_OUT
        if all(item > 0 for item in signs):
            return RotationState.LEADING
        if all(item < 0 for item in signs):
            return RotationState.LAGGING
        if short > long + self._policy.relative_material_percent:
            return RotationState.IMPROVING
        if short < long - self._policy.relative_material_percent:
            return RotationState.WEAKENING
        if 1 in signs and -1 in signs:
            return RotationState.MIXED
        return RotationState.NEUTRAL

    def _subject_state(self, spread: float | None) -> SubjectSectorState:
        if spread is None:
            return SubjectSectorState.UNKNOWN
        if spread > self._policy.subject_material_percent:
            return SubjectSectorState.OUTPERFORMS_SECTOR
        if spread < -self._policy.subject_material_percent:
            return SubjectSectorState.LAGS_SECTOR
        return SubjectSectorState.INLINE_WITH_SECTOR

    def _breadth(self, values: tuple[float, ...]) -> SectorBreadthState:
        if not values:
            return SectorBreadthState.UNKNOWN
        average = sum(values) / len(values)
        if average >= self._policy.breadth_strong_fraction:
            return SectorBreadthState.STRONG
        if average > 0.5:
            return SectorBreadthState.HEALTHY
        if average <= self._policy.breadth_weak_fraction:
            return SectorBreadthState.WEAK
        return SectorBreadthState.MIXED

    @staticmethod
    def _concentration(
        sector: SectorState, breadth: SectorBreadthState, participation: SectorParticipationState
    ) -> SectorConcentrationState:
        strong = sector in {SectorState.STRONG, SectorState.SUPPORTIVE}
        weak = sector in {SectorState.WEAK, SectorState.VERY_WEAK}
        narrow = (
            participation is SectorParticipationState.NARROW or breadth is SectorBreadthState.WEAK
        )
        if strong:
            return (
                SectorConcentrationState.CONCENTRATED_LEADERSHIP
                if narrow
                else SectorConcentrationState.BROAD_LEADERSHIP
                if breadth is not SectorBreadthState.UNKNOWN
                else SectorConcentrationState.UNKNOWN
            )
        if weak:
            return (
                SectorConcentrationState.CONCENTRATED_WEAKNESS
                if narrow
                else SectorConcentrationState.BROAD_WEAKNESS
                if breadth is not SectorBreadthState.UNKNOWN
                else SectorConcentrationState.UNKNOWN
            )
        return SectorConcentrationState.UNKNOWN

    @staticmethod
    def _contradictions(
        sector: SectorState,
        subject: SubjectSectorState,
        breadth: SectorBreadthState,
        participation: SectorParticipationState,
        records: tuple[FactRecord, ...],
    ) -> tuple[SectorContradiction, ...]:
        values: list[SectorContradiction] = []
        ids = reference_ids(records)
        if (
            sector in {SectorState.STRONG, SectorState.SUPPORTIVE}
            and subject is SubjectSectorState.LAGS_SECTOR
        ):
            values.append(
                SectorContradiction(
                    code="SECTOR_STRONG_SUBJECT_LAGS",
                    description="Sector evidence is supportive while the subject lags its sector.",
                    evidence_ids=ids,
                )
            )
        if (
            sector in {SectorState.WEAK, SectorState.VERY_WEAK}
            and subject is SubjectSectorState.OUTPERFORMS_SECTOR
        ):
            values.append(
                SectorContradiction(
                    code="SECTOR_WEAK_SUBJECT_RESILIENT",
                    description="Sector evidence is weak while the subject outperforms its sector.",
                    evidence_ids=ids,
                )
            )
        if sector in {SectorState.STRONG, SectorState.SUPPORTIVE} and (
            breadth is SectorBreadthState.WEAK or participation is SectorParticipationState.NARROW
        ):
            values.append(
                SectorContradiction(
                    code="SECTOR_STRENGTH_NARROW",
                    description="Headline sector strength is not supported by broad participation.",
                    evidence_ids=ids,
                )
            )
        return tuple(values)

    @staticmethod
    def _stance(sector: SectorState, subject: SubjectSectorState, complete: bool) -> AgentStance:
        if not complete:
            return AgentStance.INSUFFICIENT_EVIDENCE
        if sector is SectorState.MIXED:
            return AgentStance.MIXED
        positive_sector = sector in {SectorState.STRONG, SectorState.SUPPORTIVE}
        negative_sector = sector in {SectorState.WEAK, SectorState.VERY_WEAK}
        if positive_sector and subject is SubjectSectorState.LAGS_SECTOR:
            return AgentStance.MIXED
        if negative_sector and subject is SubjectSectorState.OUTPERFORMS_SECTOR:
            return AgentStance.MIXED
        if positive_sector:
            return AgentStance.POSITIVE
        if negative_sector:
            return AgentStance.NEGATIVE
        return AgentStance.NEUTRAL

    @staticmethod
    def _reasons(
        sector: SectorState,
        rotation: RotationState,
        subject: SubjectSectorState,
        breadth: SectorBreadthState,
        concentration: SectorConcentrationState,
        catalysts: tuple[str, ...],
        evidence: AgentEvidencePack,
        mapping_complete: bool,
        mapping_quality: object,
    ) -> tuple[SectorReasonCode, ...]:
        values: list[SectorReasonCode] = []
        if not mapping_complete:
            values.append(
                SectorReasonCode.SECTOR_MAPPING_AMBIGUOUS
                if mapping_quality == "AMBIGUOUS"
                else SectorReasonCode.SECTOR_MAPPING_MISSING
            )
        if sector in {SectorState.STRONG, SectorState.SUPPORTIVE}:
            values.append(SectorReasonCode.SECTOR_LEADING)
        elif sector in {SectorState.WEAK, SectorState.VERY_WEAK}:
            values.append(SectorReasonCode.SECTOR_LAGGING)
        values.extend(
            {
                RotationState.ROTATING_IN: (SectorReasonCode.SECTOR_ROTATING_IN,),
                RotationState.ROTATING_OUT: (SectorReasonCode.SECTOR_ROTATING_OUT,),
                RotationState.IMPROVING: (SectorReasonCode.SECTOR_IMPROVING,),
                RotationState.WEAKENING: (SectorReasonCode.SECTOR_WEAKENING,),
            }.get(rotation, ())
        )
        if breadth in {SectorBreadthState.STRONG, SectorBreadthState.HEALTHY}:
            values.append(SectorReasonCode.SECTOR_BREADTH_STRONG)
        elif breadth is SectorBreadthState.WEAK:
            values.append(SectorReasonCode.SECTOR_BREADTH_WEAK)
        if concentration is SectorConcentrationState.CONCENTRATED_LEADERSHIP:
            values.append(SectorReasonCode.SECTOR_LEADERSHIP_CONCENTRATED)
        if subject is SubjectSectorState.OUTPERFORMS_SECTOR:
            values.append(SectorReasonCode.SUBJECT_OUTPERFORMS_SECTOR)
        elif subject is SubjectSectorState.LAGS_SECTOR:
            values.append(SectorReasonCode.SUBJECT_LAGS_SECTOR)
        if "POSITIVE" in catalysts:
            values.append(SectorReasonCode.SECTOR_EVENT_SUPPORT)
        if "NEGATIVE" in catalysts:
            values.append(SectorReasonCode.SECTOR_EVENT_CONFLICT)
        if evidence.overall_quality is not DataQuality.GOOD:
            values.append(SectorReasonCode.SECTOR_EVIDENCE_PARTIAL)
        if evidence.overall_freshness is FreshnessState.STALE:
            values.append(SectorReasonCode.SECTOR_EVIDENCE_STALE)
        return tuple(dict.fromkeys(values))

    @staticmethod
    def _missing(
        request: AgentRequest, evidence: AgentEvidencePack, complete: bool, mapping_complete: bool
    ) -> tuple[MissingEvidenceRequest, ...]:
        values = list(evidence.missing_evidence)
        if not complete:
            values.append(
                MissingEvidenceRequest(
                    missing_request_id=f"{request.run_id}:missing:sector-core",
                    evidence_type=EvidenceType.SECTOR,
                    capability=AgentCapability.READ_SECTOR_CONTEXT,
                    subject=request.subject,
                    reason="Explicit valid sector mapping is required"
                    if not mapping_complete
                    else "Sector absolute or relative evidence is required",
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
        if request.specialist is not SpecialistId.SECTOR:
            raise ValueError("SectorSpecialist requires SECTOR identity")
        if not {AgentCapability.READ_A2_EVIDENCE, AgentCapability.READ_SECTOR_CONTEXT} <= set(
            request.allowed_capabilities
        ):
            raise ValueError(
                "SectorSpecialist requires bounded A2 and sector-context authorization"
            )
        if (
            evidence.request_id != request.request_id
            or evidence.subject != request.subject
            or evidence.evidence_fingerprint != request.evidence_fingerprint
            or evidence.deterministic_assessment_id != request.deterministic_baseline_reference
        ):
            raise ValueError("sector evidence does not preserve request/A2 identity")


def sector_assessment_from_opinion(opinion: AgentOpinionV2) -> SectorAssessment:
    if (
        opinion.specialist_detail_schema_id != SECTOR_DETAIL_SCHEMA
        or opinion.specialist_detail_json is None
    ):
        raise ValueError("opinion does not contain A3.6 sector detail")
    return SectorAssessment.model_validate_json(opinion.specialist_detail_json)
