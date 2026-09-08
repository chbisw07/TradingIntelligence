"""Deterministic, cited News / Catalyst / Event specialist."""

from collections.abc import Iterable

from tiaf.agents import (
    AgentCapability,
    AgentConfidence,
    AgentEvidencePack,
    AgentOpinionV2,
    AgentRequest,
    AgentRunStatus,
    AgentStance,
    AgentUsage,
    BaselineAgreement,
    CitationRole,
    ClaimKind,
    EvidenceCitation,
    EvidenceClaim,
    EvidenceImportance,
    MissingEvidenceRequest,
    PolicyDerivedConfidence,
    SpecialistCapability,
    SpecialistCostTier,
    SpecialistId,
)
from tiaf.contracts import DataQuality, EvidenceType, FreshnessState
from tiaf.data import InstrumentType
from tiaf.events import (
    CatalystDirection,
    CatalystHorizon,
    CatalystStrength,
    ContradictionState,
    EventFamily,
    EventMateriality,
    EventNovelty,
    EventRelevance,
    EventSourceClass,
    EventStatus,
    EventType,
    ExecutionRiskState,
    SourceQualityState,
)
from tiaf.events.quality import weakest_freshness, weakest_quality

from .enums import NewsEventReasonCode
from .evidence import EventEvidenceCluster, EventEvidenceRecord, EventFactBook
from .models import EventClusterAssessment, NewsEventAssessment
from .policy import NewsEventInterpretationPolicy, default_news_event_policy

SPECIALIST_VERSION = "1.0"
NEWS_EVENT_DETAIL_SCHEMA = "tiaf.news-event-assessment/1.0"

_POSITIVE_TYPES = {
    EventType.GUIDANCE_RAISED,
    EventType.BUYBACK_APPROVED,
    EventType.ORDER_AWARDED,
    EventType.PLEDGE_RELEASED,
    EventType.REGULATORY_APPROVAL,
    EventType.LITIGATION_RESOLVED,
    EventType.RATING_UPGRADE,
    EventType.PRODUCT_LAUNCHED,
    EventType.EXPANSION_ANNOUNCED,
    EventType.CUSTOMER_WON,
}
_MILD_POSITIVE_TYPES = {
    EventType.DIVIDEND_DECLARED,
    EventType.CAPEX_ANNOUNCED,
    EventType.MANAGEMENT_APPOINTED,
}
_NEGATIVE_TYPES = {
    EventType.GUIDANCE_CUT,
    EventType.ORDER_LOST,
    EventType.CAPEX_DELAYED,
    EventType.PLEDGE_CREATED,
    EventType.REGULATORY_ACTION,
    EventType.LITIGATION_FILED,
    EventType.RATING_DOWNGRADE,
    EventType.CUSTOMER_LOST,
    EventType.SUPPLY_DISRUPTION,
}
_MILD_NEGATIVE_TYPES = {
    EventType.MANAGEMENT_RESIGNED,
    EventType.CAPITAL_RAISE_APPROVED,
}
_MATERIAL = {
    EventMateriality.CRITICAL,
    EventMateriality.HIGH,
    EventMateriality.MODERATE,
}


class NewsEventSpecialist:
    """Interpret supplied event clusters without provider, browser, or model access."""

    def __init__(self, policy: NewsEventInterpretationPolicy | None = None) -> None:
        self._policy = policy or default_news_event_policy()

    def capability(self) -> SpecialistCapability:
        return SpecialistCapability(
            specialist=SpecialistId.NEWS_EVENT,
            specialist_version=SPECIALIST_VERSION,
            display_name="News / Catalyst / Event Specialist",
            description="Cited deterministic interpretation of normalized PIT event evidence",
            supported_instrument_types=(InstrumentType.EQUITY, InstrumentType.INDEX),
            required_evidence_types=(EvidenceType.NEWS,),
            allowed_capabilities=(
                AgentCapability.READ_A2_EVIDENCE,
                AgentCapability.READ_FILINGS,
                AgentCapability.READ_NEWS,
            ),
            supports_no_llm=True,
            cost_tier=SpecialistCostTier.LOW,
            prohibitions=(
                "provider acquisition or arbitrary URL fetching",
                "headline-tone sentiment inference",
                "rumor or unsupported social-media evidence",
                "technical, fundamental, macro, or forecast recalculation",
                "target price, return probability, or trading action",
                "broker or execution operation",
            ),
        )

    def analyze(self, request: AgentRequest, evidence: AgentEvidencePack) -> AgentOpinionV2:
        self._validate_identity(request, evidence)
        fact_book = EventFactBook(evidence)
        cluster_assessments = tuple(self._cluster(item) for item in fact_book.clusters)
        relevant = tuple(
            item
            for item in cluster_assessments
            if item.materiality in _MATERIAL
            and self._horizon_relevant(request, item.catalyst_horizon)
            and any(
                record.relevance
                in {EventRelevance.DIRECT, EventRelevance.HIGH, EventRelevance.MODERATE}
                for cluster in fact_book.clusters
                if cluster.cluster_id == item.cluster_id
                for record in cluster.active_records
            )
        )
        stance = self._stance(cluster_assessments, relevant)
        direction = self._aggregate_direction(relevant)
        materiality = self._strongest_materiality(cluster_assessments)
        source_quality = self._best_source_quality(cluster_assessments)
        contradiction = self._aggregate_contradiction(cluster_assessments)
        novelty = self._aggregate_novelty(cluster_assessments)
        strength = self._aggregate_strength(relevant)
        horizon = self._aggregate_horizon(relevant)
        execution_risk = self._aggregate_execution_risk(cluster_assessments)
        reasons = self._reason_codes(fact_book.clusters, cluster_assessments, stance, evidence)
        confidence = self._confidence(request, evidence, fact_book.clusters, cluster_assessments)
        missing = self._missing(request, evidence, cluster_assessments)
        assessment = NewsEventAssessment(
            assessment_id=f"{request.run_id}:news-event-assessment",
            specialist_version=SPECIALIST_VERSION,
            policy_id=self._policy.policy_id,
            policy_version=self._policy.policy_version,
            stance=stance,
            dominant_event_families=tuple(
                dict.fromkeys(item.dominant_family for item in (relevant or cluster_assessments))
            ),
            catalyst_direction=direction,
            catalyst_strength=strength,
            catalyst_horizon=horizon,
            materiality=materiality,
            novelty=novelty,
            source_quality=source_quality,
            contradiction_state=contradiction,
            execution_risk=execution_risk,
            clusters=cluster_assessments,
            evidence_coverage=evidence.evidence_coverage if cluster_assessments else 0.0,
            confidence_basis=(
                "source_quality",
                "point_in_time_coverage",
                "cross_source_consistency",
                "evidence_freshness",
                "explicit_entity_relevance",
                "materiality_evidence_not_price_probability",
                "requested_horizon_alignment",
            ),
            reason_codes=reasons,
            created_at=request.created_at,
        )
        claims = self._claims(fact_book.clusters, cluster_assessments)
        evidence_ids = tuple(
            dict.fromkeys(citation.evidence_id for claim in claims for citation in claim.citations)
        )
        caveat = evidence.metadata.get("point_in_time_limitation")
        return AgentOpinionV2(
            opinion_id=f"{request.run_id}:news-event-opinion",
            request_id=request.request_id,
            run_id=request.run_id,
            specialist=SpecialistId.NEWS_EVENT,
            specialist_version=SPECIALIST_VERSION,
            subject=request.subject,
            horizon=request.horizon,
            stance=stance,
            status=self._status(stance, evidence, missing),
            confidence=AgentConfidence(
                evidence_coverage=evidence.evidence_coverage if cluster_assessments else 0.0,
                evidence_quality=evidence.overall_quality,
                policy_derived=PolicyDerivedConfidence(
                    value=confidence,
                    policy_id=self._policy.policy_id,
                    policy_version=self._policy.policy_version,
                ),
            ),
            summary=(
                f"Deduplicated event context is {direction.value} across "
                f"{len(cluster_assessments)} cluster(s)."
            ),
            reason_codes=tuple(item.value for item in reasons),
            evidence_claims=claims,
            supporting_evidence_ids=evidence_ids,
            missing_evidence=missing,
            risks=(
                ("Active source records contain explicit structured-fact conflict.",)
                if contradiction is ContradictionState.SOURCE_CONFLICT
                else ()
            ),
            caveats=tuple(
                item
                for item in (
                    caveat if isinstance(caveat, str) else None,
                    (
                        "Direction is deterministic event policy, not headline "
                        "sentiment or a price forecast."
                    ),
                )
                if item is not None
            ),
            deterministic_baseline_reference=request.deterministic_baseline_reference,
            baseline_agreement=BaselineAgreement.NOT_COMPARABLE,
            evidence_fingerprint=request.evidence_fingerprint,
            evidence_quality=evidence.overall_quality,
            evidence_freshness=evidence.overall_freshness,
            policy_version=self._policy.policy_version,
            usage=AgentUsage(),
            produced_at=request.created_at,
            specialist_detail_schema_id=NEWS_EVENT_DETAIL_SCHEMA,
            specialist_detail_json=assessment.canonical_json(),
        )

    def _cluster(self, cluster: EventEvidenceCluster) -> EventClusterAssessment:
        records = cluster.active_records
        directions = {self._record_direction(item) for item in records}
        contradiction_fields = tuple(
            sorted({field for item in records for field in item.contradiction_fields})
        )
        corrected = len(cluster.records) > len(records)
        contradiction = (
            ContradictionState.SOURCE_CONFLICT
            if contradiction_fields or self._opposing(directions)
            else ContradictionState.DISPUTED
            if any(item.status is EventStatus.DISPUTED for item in records)
            else ContradictionState.CORRECTED
            if corrected
            else ContradictionState.NONE
        )
        direction = (
            CatalystDirection.MIXED
            if contradiction is ContradictionState.SOURCE_CONFLICT
            else next(iter(directions))
            if len(directions) == 1
            else CatalystDirection.MIXED
        )
        return EventClusterAssessment(
            cluster_id=cluster.cluster_id,
            event_ids=tuple(item.reference.evidence_id for item in cluster.records),
            active_event_ids=tuple(item.reference.evidence_id for item in records),
            dominant_family=_mode_family(records),
            catalyst_direction=direction,
            catalyst_strength=_strength(_strongest(item.materiality for item in records)),
            catalyst_horizon=_cluster_horizon(records),
            materiality=_strongest(item.materiality for item in records),
            novelty=(EventNovelty.CORRECTION if corrected else _novelty(records)),
            source_quality=_best_quality(item.source_quality for item in records),
            contradiction_state=contradiction,
            execution_risk=_execution_risk(records),
            contradiction_fields=contradiction_fields,
        )

    @staticmethod
    def _record_direction(record: EventEvidenceRecord) -> CatalystDirection:
        if record.status is EventStatus.DISPUTED:
            return CatalystDirection.MIXED
        if record.status in {EventStatus.CANCELLED, EventStatus.DELAYED}:
            return CatalystDirection.NEGATIVE
        facts = {name: value for name, value in record.structured_facts}
        if record.event_type is EventType.RESULTS_REPORTED:
            context = str(facts.get("earnings_context", "")).upper()
            if context == "BEAT":
                return CatalystDirection.POSITIVE
            if context == "MISS":
                return CatalystDirection.NEGATIVE
            return CatalystDirection.NEUTRAL
        if record.event_type in _POSITIVE_TYPES:
            return CatalystDirection.POSITIVE
        if record.event_type in _MILD_POSITIVE_TYPES:
            return CatalystDirection.MILDLY_POSITIVE
        if record.event_type in _NEGATIVE_TYPES:
            return CatalystDirection.NEGATIVE
        if record.event_type in _MILD_NEGATIVE_TYPES:
            return CatalystDirection.MILDLY_NEGATIVE
        return (
            CatalystDirection.NEUTRAL
            if record.event_type is not EventType.UNKNOWN
            else CatalystDirection.UNKNOWN
        )

    @staticmethod
    def _opposing(directions: set[CatalystDirection]) -> bool:
        positive = bool(
            directions
            & {
                CatalystDirection.POSITIVE,
                CatalystDirection.MILDLY_POSITIVE,
                CatalystDirection.STRONGLY_POSITIVE,
            }
        )
        negative = bool(
            directions
            & {
                CatalystDirection.NEGATIVE,
                CatalystDirection.MILDLY_NEGATIVE,
                CatalystDirection.STRONGLY_NEGATIVE,
            }
        )
        return positive and negative

    @staticmethod
    def _stance(
        all_clusters: tuple[EventClusterAssessment, ...],
        relevant: tuple[EventClusterAssessment, ...],
    ) -> AgentStance:
        if not all_clusters:
            return AgentStance.INSUFFICIENT_EVIDENCE
        if not relevant:
            return AgentStance.ABSTAIN
        directions = {item.catalyst_direction for item in relevant}
        if CatalystDirection.MIXED in directions or NewsEventSpecialist._opposing(directions):
            return AgentStance.MIXED
        if directions & {
            CatalystDirection.POSITIVE,
            CatalystDirection.MILDLY_POSITIVE,
            CatalystDirection.STRONGLY_POSITIVE,
        }:
            return AgentStance.POSITIVE
        if directions & {
            CatalystDirection.NEGATIVE,
            CatalystDirection.MILDLY_NEGATIVE,
            CatalystDirection.STRONGLY_NEGATIVE,
        }:
            return AgentStance.NEGATIVE
        return AgentStance.NEUTRAL

    @staticmethod
    def _aggregate_direction(clusters: tuple[EventClusterAssessment, ...]) -> CatalystDirection:
        if not clusters:
            return CatalystDirection.UNKNOWN
        values = {item.catalyst_direction for item in clusters}
        if CatalystDirection.MIXED in values or NewsEventSpecialist._opposing(values):
            return CatalystDirection.MIXED
        return next(iter(values)) if len(values) == 1 else CatalystDirection.MIXED

    @staticmethod
    def _strongest_materiality(clusters: tuple[EventClusterAssessment, ...]) -> EventMateriality:
        return (
            _strongest(item.materiality for item in clusters)
            if clusters
            else EventMateriality.UNKNOWN
        )

    @staticmethod
    def _best_source_quality(clusters: tuple[EventClusterAssessment, ...]) -> SourceQualityState:
        return (
            _best_quality(item.source_quality for item in clusters)
            if clusters
            else SourceQualityState.UNKNOWN
        )

    @staticmethod
    def _aggregate_contradiction(
        clusters: tuple[EventClusterAssessment, ...],
    ) -> ContradictionState:
        values = {item.contradiction_state for item in clusters}
        for state in (
            ContradictionState.SOURCE_CONFLICT,
            ContradictionState.DISPUTED,
            ContradictionState.CORRECTED,
        ):
            if state in values:
                return state
        return ContradictionState.NONE

    @staticmethod
    def _aggregate_novelty(clusters: tuple[EventClusterAssessment, ...]) -> EventNovelty:
        values = {item.novelty for item in clusters}
        for value in (
            EventNovelty.CORRECTION,
            EventNovelty.NEW,
            EventNovelty.UPDATE,
            EventNovelty.REPEAT,
            EventNovelty.DUPLICATE,
        ):
            if value in values:
                return value
        return EventNovelty.UNKNOWN

    @staticmethod
    def _aggregate_strength(clusters: tuple[EventClusterAssessment, ...]) -> CatalystStrength:
        order = {
            CatalystStrength.HIGH: 0,
            CatalystStrength.MODERATE: 1,
            CatalystStrength.LOW: 2,
            CatalystStrength.IMMATERIAL: 3,
            CatalystStrength.UNKNOWN: 4,
        }
        return (
            min((item.catalyst_strength for item in clusters), key=order.__getitem__)
            if clusters
            else CatalystStrength.UNKNOWN
        )

    @staticmethod
    def _aggregate_horizon(clusters: tuple[EventClusterAssessment, ...]) -> CatalystHorizon:
        values = {item.catalyst_horizon for item in clusters}
        return (
            next(iter(values))
            if len(values) == 1
            else CatalystHorizon.MULTI_HORIZON
            if values
            else CatalystHorizon.UNKNOWN
        )

    @staticmethod
    def _aggregate_execution_risk(
        clusters: tuple[EventClusterAssessment, ...],
    ) -> ExecutionRiskState:
        order = {
            ExecutionRiskState.HIGH: 0,
            ExecutionRiskState.MODERATE: 1,
            ExecutionRiskState.LOW: 2,
            ExecutionRiskState.UNKNOWN: 3,
        }
        return (
            min((item.execution_risk for item in clusters), key=order.__getitem__)
            if clusters
            else ExecutionRiskState.UNKNOWN
        )

    def _confidence(
        self,
        request: AgentRequest,
        evidence: AgentEvidencePack,
        clusters: tuple[EventEvidenceCluster, ...],
        assessments: tuple[EventClusterAssessment, ...],
    ) -> float:
        if not clusters:
            return 0.0
        source = {
            SourceQualityState.PRIMARY: self._policy.primary_source_weight,
            SourceQualityState.OFFICIAL: self._policy.official_source_weight,
            SourceQualityState.TRUSTED_SECONDARY: self._policy.trusted_secondary_weight,
            SourceQualityState.OTHER: self._policy.other_source_weight,
            SourceQualityState.UNKNOWN: self._policy.unknown_source_weight,
        }[self._best_source_quality(assessments)]
        relevance_values = [
            item.relevance for cluster in clusters for item in cluster.active_records
        ]
        relevance = max(
            (
                {
                    EventRelevance.DIRECT: self._policy.direct_relevance_weight,
                    EventRelevance.HIGH: self._policy.high_relevance_weight,
                    EventRelevance.MODERATE: self._policy.moderate_relevance_weight,
                    EventRelevance.LOW: self._policy.low_relevance_weight,
                    EventRelevance.INCIDENTAL: self._policy.incidental_relevance_weight,
                    EventRelevance.UNKNOWN: self._policy.unknown_relevance_weight,
                }[item]
                for item in relevance_values
            ),
            default=0.0,
        )
        freshness = {
            FreshnessState.FRESH: self._policy.fresh_weight,
            FreshnessState.AGING: self._policy.aging_weight,
            FreshnessState.STALE: self._policy.stale_weight,
            FreshnessState.UNKNOWN: self._policy.unknown_freshness_weight,
        }[evidence.overall_freshness]
        consistency = (
            self._policy.source_conflict_consistency_weight
            if any(
                item.contradiction_state is ContradictionState.SOURCE_CONFLICT
                for item in assessments
            )
            else 1.0
        )
        materiality = (
            self._policy.unknown_materiality_weight
            if self._strongest_materiality(assessments) is EventMateriality.UNKNOWN
            else 1.0
        )
        horizon = (
            1.0
            if any(self._horizon_relevant(request, item.catalyst_horizon) for item in assessments)
            else self._policy.horizon_mismatch_weight
        )
        return round(
            evidence.evidence_coverage
            * (source + relevance + freshness + consistency + materiality + horizon)
            / 6.0,
            4,
        )

    @staticmethod
    def _horizon_relevant(request: AgentRequest, catalyst: CatalystHorizon) -> bool:
        days = request.horizon.max_days or request.horizon.min_days or 0
        if request.trade_style is not None and request.trade_style.value == "DAY":
            days = min(days, 1)
        if days <= 60:
            accepted = {
                CatalystHorizon.IMMEDIATE,
                CatalystHorizon.SHORT_TERM,
                CatalystHorizon.MULTI_HORIZON,
            }
        else:
            accepted = {
                CatalystHorizon.MEDIUM_TERM,
                CatalystHorizon.LONG_TERM,
                CatalystHorizon.MULTI_HORIZON,
            }
        return catalyst in accepted

    def _reason_codes(
        self,
        clusters: tuple[EventEvidenceCluster, ...],
        assessments: tuple[EventClusterAssessment, ...],
        stance: AgentStance,
        evidence: AgentEvidencePack,
    ) -> tuple[NewsEventReasonCode, ...]:
        reasons: list[NewsEventReasonCode] = []
        records = tuple(item for cluster in clusters for item in cluster.active_records)
        if any(
            str(item.reference.metadata.get("source_class"))
            in {EventSourceClass.EXCHANGE_FILING.value, EventSourceClass.REGULATORY_FILING.value}
            for item in records
        ):
            reasons.append(NewsEventReasonCode.PRIMARY_FILING_CONFIRMED)
        type_reasons = {
            EventType.ORDER_AWARDED: NewsEventReasonCode.ORDER_WIN,
            EventType.ORDER_LOST: NewsEventReasonCode.ORDER_LOSS,
            EventType.GUIDANCE_RAISED: NewsEventReasonCode.GUIDANCE_RAISED,
            EventType.GUIDANCE_CUT: NewsEventReasonCode.GUIDANCE_CUT,
            EventType.CAPEX_ANNOUNCED: NewsEventReasonCode.CAPEX_POSITIVE,
            EventType.CAPEX_DELAYED: NewsEventReasonCode.CAPEX_EXECUTION_RISK,
            EventType.REGULATORY_APPROVAL: NewsEventReasonCode.REGULATORY_POSITIVE,
            EventType.REGULATORY_ACTION: NewsEventReasonCode.REGULATORY_NEGATIVE,
            EventType.RATING_UPGRADE: NewsEventReasonCode.CREDIT_RATING_UPGRADE,
            EventType.RATING_DOWNGRADE: NewsEventReasonCode.CREDIT_RATING_DOWNGRADE,
        }
        reasons.extend(
            type_reasons[item.event_type] for item in records if item.event_type in type_reasons
        )
        if any(
            item.event_type in {EventType.MANAGEMENT_APPOINTED, EventType.MANAGEMENT_RESIGNED}
            for item in records
        ):
            reasons.append(NewsEventReasonCode.MANAGEMENT_CHANGE)
        if any(
            item.event_type
            in {
                EventType.PROMOTER_TRANSACTION,
                EventType.PLEDGE_CREATED,
                EventType.PLEDGE_RELEASED,
            }
            for item in records
        ):
            reasons.append(NewsEventReasonCode.PROMOTER_ACTION)
        if any(
            item.event_type is EventType.CAPEX_ANNOUNCED
            and item.status in {EventStatus.ANNOUNCED, EventStatus.ONGOING}
            for item in records
        ):
            reasons.append(NewsEventReasonCode.CAPEX_EXECUTION_RISK)
        for item in records:
            if item.event_type is EventType.RESULTS_REPORTED:
                context = str(dict(item.structured_facts).get("earnings_context", "")).upper()
                if context == "BEAT":
                    reasons.append(NewsEventReasonCode.EARNINGS_BEAT_CONTEXT)
                elif context == "MISS":
                    reasons.append(NewsEventReasonCode.EARNINGS_MISS_CONTEXT)
        if any(len(item.records) > 1 for item in clusters):
            reasons.append(NewsEventReasonCode.NEWS_DUPLICATE)
        if any(item.contradiction_state is ContradictionState.CORRECTED for item in assessments):
            reasons.append(NewsEventReasonCode.NEWS_CORRECTION)
        if any(
            item.contradiction_state is ContradictionState.SOURCE_CONFLICT for item in assessments
        ):
            reasons.append(NewsEventReasonCode.SOURCE_CONFLICT)
        if stance is AgentStance.MIXED:
            reasons.append(NewsEventReasonCode.CATALYST_MIXED)
        if stance is AgentStance.POSITIVE:
            reasons.append(NewsEventReasonCode.MATERIAL_POSITIVE_EVENT)
        if stance is AgentStance.NEGATIVE:
            reasons.append(NewsEventReasonCode.MATERIAL_NEGATIVE_EVENT)
        if stance is AgentStance.ABSTAIN:
            if all(item.materiality not in _MATERIAL for item in assessments):
                reasons.append(NewsEventReasonCode.EVENT_NOT_MATERIAL)
            if all(
                item.relevance
                in {EventRelevance.LOW, EventRelevance.INCIDENTAL, EventRelevance.UNKNOWN}
                for item in records
            ):
                reasons.append(NewsEventReasonCode.EVENT_LOW_RELEVANCE)
        if not assessments:
            reasons.append(NewsEventReasonCode.EVENT_EVIDENCE_INSUFFICIENT)
        if evidence.overall_quality is not DataQuality.GOOD:
            reasons.append(NewsEventReasonCode.EVENT_PARTIAL)
        if evidence.overall_freshness is FreshnessState.STALE:
            reasons.append(NewsEventReasonCode.EVENT_STALE)
        return tuple(dict.fromkeys(reasons))

    def _claims(
        self,
        clusters: tuple[EventEvidenceCluster, ...],
        assessments: tuple[EventClusterAssessment, ...],
    ) -> tuple[EvidenceClaim, ...]:
        claims: list[EvidenceClaim] = []
        by_id = {item.cluster_id: item for item in assessments}
        for cluster in clusters:
            assessment = by_id[cluster.cluster_id]
            records = cluster.active_records
            citations = tuple(
                EvidenceCitation(
                    evidence_id=item.reference.evidence_id,
                    role=CitationRole.SUPPORTS,
                    locator=item.reference.source_reference,
                )
                for item in records
            )
            quality = weakest_quality(
                tuple(
                    item.reference.quality for item in records if item.reference.quality is not None
                )
            )
            freshness = weakest_freshness(
                tuple(
                    item.reference.freshness
                    for item in records
                    if item.reference.freshness is not None
                )
            )
            as_of = max(
                item.reference.observed_at
                for item in records
                if item.reference.observed_at is not None
            )
            claims.extend(
                (
                    EvidenceClaim(
                        claim_id=f"event:{cluster.cluster_id}:classification",
                        kind=ClaimKind.FACTUAL,
                        statement=(
                            "Supplied records classify this cluster as "
                            f"{assessment.dominant_family.value} "
                            f"with {assessment.materiality.value} materiality."
                        ),
                        evidence_type=EvidenceType.NEWS,
                        citations=citations,
                        as_of=as_of,
                        provenance="supplied normalized event records",
                        quality=quality,
                        freshness=freshness,
                    ),
                    EvidenceClaim(
                        claim_id=f"event:{cluster.cluster_id}:interpretation",
                        kind=ClaimKind.INTERPRETIVE,
                        statement=(
                            f"Deterministic event policy interprets this cluster as "
                            f"{assessment.catalyst_direction.value} with "
                            f"{assessment.catalyst_strength.value} strength."
                        ),
                        evidence_type=EvidenceType.NEWS,
                        citations=citations,
                        as_of=as_of,
                        provenance=f"{self._policy.policy_id}/{self._policy.policy_version}",
                        quality=quality,
                        freshness=freshness,
                    ),
                )
            )
        return tuple(claims)

    @staticmethod
    def _missing(
        request: AgentRequest,
        evidence: AgentEvidencePack,
        clusters: tuple[EventClusterAssessment, ...],
    ) -> tuple[MissingEvidenceRequest, ...]:
        if clusters:
            return evidence.missing_evidence
        return (
            *evidence.missing_evidence,
            MissingEvidenceRequest(
                missing_request_id=f"{request.request_id}:missing:events",
                evidence_type=EvidenceType.NEWS,
                capability=AgentCapability.READ_NEWS,
                subject=request.subject,
                reason="No usable normalized point-in-time event records were supplied",
                importance=EvidenceImportance.REQUIRED,
                required_freshness=FreshnessState.FRESH,
                requested_at=request.created_at,
            ),
        )

    @staticmethod
    def _status(
        stance: AgentStance,
        evidence: AgentEvidencePack,
        missing: tuple[MissingEvidenceRequest, ...],
    ) -> AgentRunStatus:
        if stance is AgentStance.INSUFFICIENT_EVIDENCE:
            return AgentRunStatus.INSUFFICIENT_EVIDENCE
        if stance is AgentStance.ABSTAIN:
            return AgentRunStatus.ABSTAINED
        if (
            missing
            or evidence.overall_quality is not DataQuality.GOOD
            or evidence.overall_freshness is not FreshnessState.FRESH
        ):
            return AgentRunStatus.PARTIAL
        return AgentRunStatus.SUCCESS

    @staticmethod
    def _validate_identity(request: AgentRequest, evidence: AgentEvidencePack) -> None:
        if request.specialist is not SpecialistId.NEWS_EVENT:
            raise ValueError("NewsEventSpecialist requires NEWS_EVENT request identity")
        required = {
            AgentCapability.READ_A2_EVIDENCE,
            AgentCapability.READ_FILINGS,
            AgentCapability.READ_NEWS,
        }
        if not required <= set(request.allowed_capabilities):
            raise ValueError(
                "NewsEventSpecialist requires bounded A2, filing, and news authorization"
            )
        if request.instrument_type not in {InstrumentType.EQUITY, InstrumentType.INDEX}:
            raise ValueError("NewsEventSpecialist supports equities and indices")
        if (
            evidence.request_id != request.request_id
            or evidence.subject != request.subject
            or evidence.evidence_fingerprint != request.evidence_fingerprint
            or evidence.deterministic_assessment_id != request.deterministic_baseline_reference
        ):
            raise ValueError("event evidence does not preserve request/A2 identity")


def news_event_assessment_from_opinion(opinion: AgentOpinionV2) -> NewsEventAssessment:
    if (
        opinion.specialist_detail_schema_id != NEWS_EVENT_DETAIL_SCHEMA
        or opinion.specialist_detail_json is None
    ):
        raise ValueError("opinion does not contain A3.5 news/event detail")
    return NewsEventAssessment.model_validate_json(opinion.specialist_detail_json)


def _strongest(values: Iterable[EventMateriality]) -> EventMateriality:
    order = {
        EventMateriality.CRITICAL: 0,
        EventMateriality.HIGH: 1,
        EventMateriality.MODERATE: 2,
        EventMateriality.LOW: 3,
        EventMateriality.IMMATERIAL: 4,
        EventMateriality.UNKNOWN: 5,
    }
    sequence: tuple[EventMateriality, ...] = tuple(values)
    return min(sequence, key=order.__getitem__) if sequence else EventMateriality.UNKNOWN


def _strength(materiality: EventMateriality) -> CatalystStrength:
    return {
        EventMateriality.CRITICAL: CatalystStrength.HIGH,
        EventMateriality.HIGH: CatalystStrength.HIGH,
        EventMateriality.MODERATE: CatalystStrength.MODERATE,
        EventMateriality.LOW: CatalystStrength.LOW,
        EventMateriality.IMMATERIAL: CatalystStrength.IMMATERIAL,
        EventMateriality.UNKNOWN: CatalystStrength.UNKNOWN,
    }[materiality]


def _best_quality(values: Iterable[SourceQualityState]) -> SourceQualityState:
    order = {
        SourceQualityState.PRIMARY: 0,
        SourceQualityState.OFFICIAL: 1,
        SourceQualityState.TRUSTED_SECONDARY: 2,
        SourceQualityState.OTHER: 3,
        SourceQualityState.UNKNOWN: 4,
    }
    sequence: tuple[SourceQualityState, ...] = tuple(values)
    return min(sequence, key=order.__getitem__) if sequence else SourceQualityState.UNKNOWN


def _mode_family(records: tuple[EventEvidenceRecord, ...]) -> EventFamily:
    counts = {
        item: sum(record.family is item for record in records)
        for item in {record.family for record in records}
    }
    return sorted(counts, key=lambda item: (-counts[item], item.value))[0]


def _novelty(records: tuple[EventEvidenceRecord, ...]) -> EventNovelty:
    values = {item.novelty for item in records}
    for value in (
        EventNovelty.CORRECTION,
        EventNovelty.NEW,
        EventNovelty.UPDATE,
        EventNovelty.REPEAT,
        EventNovelty.DUPLICATE,
    ):
        if value in values:
            return value
    return EventNovelty.UNKNOWN


def _cluster_horizon(records: tuple[EventEvidenceRecord, ...]) -> CatalystHorizon:
    values = {item.event_type for item in records}
    if values & {
        EventType.CAPEX_ANNOUNCED,
        EventType.EXPANSION_ANNOUNCED,
        EventType.ACQUISITION_ANNOUNCED,
    }:
        return CatalystHorizon.LONG_TERM
    if values & {
        EventType.BUYBACK_APPROVED,
        EventType.CAPITAL_RAISE_APPROVED,
        EventType.MANAGEMENT_APPOINTED,
        EventType.MANAGEMENT_RESIGNED,
        EventType.PRODUCT_LAUNCHED,
        EventType.CUSTOMER_WON,
        EventType.CUSTOMER_LOST,
    }:
        return CatalystHorizon.MEDIUM_TERM
    if values & {
        EventType.RESULTS_REPORTED,
        EventType.GUIDANCE_RAISED,
        EventType.GUIDANCE_CUT,
        EventType.ORDER_AWARDED,
        EventType.ORDER_LOST,
    }:
        return CatalystHorizon.MULTI_HORIZON
    if values & {
        EventType.REGULATORY_ACTION,
        EventType.REGULATORY_APPROVAL,
        EventType.RATING_DOWNGRADE,
        EventType.RATING_UPGRADE,
        EventType.DIVIDEND_DECLARED,
        EventType.LITIGATION_FILED,
        EventType.LITIGATION_RESOLVED,
    }:
        return CatalystHorizon.SHORT_TERM
    return CatalystHorizon.UNKNOWN


def _execution_risk(records: tuple[EventEvidenceRecord, ...]) -> ExecutionRiskState:
    if any(
        item.status in {EventStatus.CANCELLED, EventStatus.DELAYED, EventStatus.DISPUTED}
        for item in records
    ):
        return ExecutionRiskState.HIGH
    if any(
        item.event_type
        in {EventType.CAPEX_ANNOUNCED, EventType.ORDER_AWARDED, EventType.EXPANSION_ANNOUNCED}
        and item.status in {EventStatus.ANNOUNCED, EventStatus.ONGOING}
        for item in records
    ):
        return ExecutionRiskState.MODERATE
    if any(item.status is EventStatus.COMPLETED for item in records):
        return ExecutionRiskState.LOW
    return ExecutionRiskState.UNKNOWN
