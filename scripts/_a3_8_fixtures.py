"""Attributable synthetic inputs, not live data or a policy calibration dataset."""

from datetime import datetime
from zoneinfo import ZoneInfo

from tiaf.agents import AgentBudget, AgentCapability, AgentEvidencePack, AgentEvidenceReference
from tiaf.agents.evidence import EvidenceFact, EvidenceFactKind
from tiaf.context import EvidenceStatus
from tiaf.contracts import DataQuality, EvidenceSource, EvidenceType, FreshnessState, Horizon
from tiaf.data import InstrumentType
from tiaf.market_intelligence import (
    AvailabilityBasis,
    CapabilityRoutePolicy,
    CapabilitySupport,
    DerivationClass,
    EvidenceOutputType,
    MarketIntelligenceCapability,
    MarketIntelligenceRegistry,
    MarketIntelligenceRequest,
    MarketIntelligenceRouter,
    PointInTimeQuality,
    ProviderCapabilityConstraints,
    ProviderCapabilityDeclaration,
    ProviderFailure,
    ProviderFailureKind,
    ProviderFetchResult,
    ProviderNativeObservation,
    ProviderResultStatus,
    RoutingMode,
    RuleBasedNormalizer,
    SemanticMappingQuality,
    SemanticRule,
    SourceAuthority,
)
from tiaf.market_intelligence.providers import FixtureMarketIntelligenceProvider
from tiaf.planner import (
    EvidenceInventory,
    InstrumentContext,
    OrchestrationBounds,
    OrchestrationRequest,
)
from tiaf.planner.digests import digest
from tiaf.workflows import ControlledServices, EvidenceAcquisition

NOW = datetime(2026, 9, 10, 12, tzinfo=ZoneInfo("Asia/Kolkata"))


def reference(
    symbol: str, ref_id: str, kind: EvidenceType, values: dict[str, str | int | float | bool]
) -> AgentEvidenceReference:
    facts = tuple(
        EvidenceFact(
            fact_id=f"{ref_id}:{metric}",
            kind=EvidenceFactKind.FEATURE,
            metric_id=metric,
            value=value,
            as_of=NOW,
            interval="1d",
            quality=DataQuality.GOOD,
            freshness=FreshnessState.FRESH,
            source_evidence=(f"synthetic:{ref_id}",),
        )
        for metric, value in values.items()
    )
    return AgentEvidenceReference(
        evidence_id=ref_id,
        evidence_type=kind,
        subject=symbol,
        producer_id="tiaf.synthetic.a38",
        producer_version="1.0",
        source=EvidenceSource.DERIVED,
        availability=EvidenceStatus.AVAILABLE,
        quality=DataQuality.GOOD,
        freshness=FreshnessState.FRESH,
        observed_at=NOW,
        acquired_at=NOW,
        checksum=digest([f.model_dump(mode="json") for f in facts]),
        source_reference=f"synthetic://{ref_id}",
        facts=facts,
    )


def request(
    *, symbol: str = "KAYNES", fno: bool | None = True, financials: bool = True, calls: int = 4
) -> OrchestrationRequest:
    baseline = reference(
        symbol,
        "baseline",
        EvidenceType.OTHER,
        {
            "baseline.direction": "NEGATIVE",
            "baseline.opportunity_score": 30.0,
            "baseline.candidate_class": "NO_TRADE",
        },
    )
    technical = reference(
        symbol,
        "technical",
        EvidenceType.TECHNICAL,
        {
            "trend.distance_from_ema_percent": 2.0,
            "trend.linear_slope_percent": 0.2,
            "trend.signed_efficiency": 0.5,
            "trend.linear_r2": 0.8,
            "trend.distance_from_ema_atr": 1.0,
            "structure.higher_high_fraction": 0.7,
            "structure.higher_low_fraction": 0.7,
            "structure.lower_high_fraction": 0.2,
            "structure.lower_low_fraction": 0.2,
            "structure.position_in_rolling_range": 80.0,
            "structure.range_compression_ratio": 1.0,
            "structure.latest_bar_range_vs_average": 1.0,
            "breakout.above_prior_high_percent": 0.0,
            "breakout.high_above_prior_high_percent": 0.0,
            "breakdown.below_prior_low_percent": 0.0,
            "breakdown.low_below_prior_low_percent": 0.0,
            "resistance.distance_atr": 2.0,
            "support.distance_atr": 3.0,
            "return.percent": 3.0,
            "range.move_over_atr": 1.0,
            "participation.signed_volume_balance": 0.3,
            "volume.relative": 1.2,
            "volatility.atr_percent": 2.0,
            "volatility.realized": 18.0,
        },
    )
    context = [
        reference(
            symbol,
            "identity",
            EvidenceType.OTHER,
            {
                "identity.fno_eligible": fno if fno is not None else "UNKNOWN",
                "identity.benchmark": "NIFTY",
                "identity.sector": "SYNTHETIC_INDUSTRIAL",
            },
        ),
        reference(
            symbol,
            "relative",
            EvidenceType.RELATIVE_STRENGTH,
            {
                "relative.excess_return_percent": 2.0,
                "relative.stance": "POSITIVE",
            },
        ),
        reference(symbol, "sector", EvidenceType.SECTOR, {"sector.stance": "NEUTRAL"}),
        reference(
            symbol,
            "event",
            EvidenceType.NEWS,
            {"event.materiality": "HIGH", "event.execution_risk": "UNKNOWN"},
        ),
    ]
    if financials:
        context.append(
            reference(
                symbol,
                "financials",
                EvidenceType.FUNDAMENTAL,
                {
                    "fundamental.revenue": 100.0,
                    "fundamental.cash_flow": "UNKNOWN",
                },
            )
        )
    if fno is True:
        context.append(
            reference(
                symbol,
                "chain",
                EvidenceType.DERIVATIVES,
                {
                    "derivatives.atm_mean_iv": 25.0,
                    "derivatives.oi_put_call_ratio": 1.0,
                    "derivatives.volume_put_call_ratio": 1.0,
                    "derivatives.days_to_expiry": 10,
                    "derivatives.ce_volume_total": 1000,
                    "derivatives.pe_volume_total": 1000,
                    "derivatives.atm_ce_bid_ask_spread_percent": 0.3,
                    "derivatives.atm_pe_bid_ask_spread_percent": 0.3,
                },
            )
        )
    pack = AgentEvidencePack(
        pack_id="synthetic:a2",
        request_id="synthetic:a2",
        subject=symbol,
        evidence_fingerprint=digest(
            [baseline.model_dump(mode="json"), technical.model_dump(mode="json")]
        ),
        references=(baseline, technical),
        analysis_context_ids=("synthetic:context",),
        deterministic_assessment_id="synthetic:a2:no-trade",
        overall_quality=DataQuality.GOOD,
        overall_freshness=FreshnessState.FRESH,
        evidence_coverage=1.0,
        created_at=NOW,
    )
    return OrchestrationRequest(
        request_id="acceptance",
        run_id="acceptance",
        instrument=InstrumentContext(
            symbol=symbol,
            instrument_type=InstrumentType.EQUITY,
            fno_eligible=fno,
            eligibility_reference="identity" if fno is not None else None,
            benchmark_reference="identity",
            sector_reference="identity",
        ),
        horizon=Horizon(min_days=14, max_days=42),
        inventory=EvidenceInventory(
            inventory_id="initial", a2_pack=pack, references=tuple(context)
        ),
        allowed_capabilities=tuple(AgentCapability),
        budget=AgentBudget(
            max_tool_calls=calls, max_cost_units=float(calls), max_elapsed_seconds=30
        ),
        bounds=OrchestrationBounds(max_provider_calls=calls),
        as_of=NOW,
    )


def financial_services(req: OrchestrationRequest, *, fallback: bool = False) -> ControlledServices:
    capability = MarketIntelligenceCapability.READ_FINANCIALS
    declaration = ProviderCapabilityDeclaration(
        capability=capability,
        support=CapabilitySupport.FULL,
        constraints=ProviderCapabilityConstraints(
            output_types=(EvidenceOutputType.SECONDARY_STRUCTURED,),
            source_authority=SourceAuthority.TRUSTED_SECONDARY,
            point_in_time_quality=PointInTimeQuality.EXACT,
            cost_units_per_call=1,
            normalizer_id="synthetic-normalizer",
            normalizer_version="1.0",
            native_schema_version="1.0",
        ),
    )
    registry = MarketIntelligenceRegistry()
    provider_ids = ("tapetide", "yahoo") if fallback else ("fixture-financial",)
    for provider_id in provider_ids:
        if fallback and provider_id == "tapetide":
            result = ProviderFetchResult(
                provider_id=provider_id,
                capability=capability,
                status=ProviderResultStatus.RATE_LIMITED,
                failures=(
                    ProviderFailure(
                        kind=ProviderFailureKind.RATE_LIMIT,
                        provider_id=provider_id,
                        capability=capability,
                        message="deterministic offline rate-limit fixture",
                    ),
                ),
            )
        else:
            result = ProviderFetchResult(
                provider_id=provider_id,
                capability=capability,
                status=ProviderResultStatus.SUCCESS,
                observations=(
                    ProviderNativeObservation(
                        observation_id=f"{provider_id}:revenue",
                        provider_id=provider_id,
                        capability=capability,
                        subject=req.subject,
                        native_field="revenue",
                        native_label="Revenue",
                        value=100.0,
                        unit="INR crore",
                        period_label="FY2026",
                        available_from=NOW,
                        acquired_at=NOW,
                        availability_basis=AvailabilityBasis.PROVIDER_AVAILABLE_FROM,
                        point_in_time_quality=PointInTimeQuality.EXACT,
                        source_reference="synthetic://financials",
                        source_quality=DataQuality.GOOD,
                        output_type=EvidenceOutputType.SECONDARY_STRUCTURED,
                        derivation_class=DerivationClass.REPORTED,
                    ),
                ),
            )
        provider = FixtureMarketIntelligenceProvider(
            provider_id, (declaration,), {(capability.value, req.subject): result}
        )
        registry.register(
            provider,
            RuleBasedNormalizer(
                provider_id,
                (
                    SemanticRule(
                        "revenue",
                        "fundamental.revenue",
                        SemanticMappingQuality.EXACT,
                        "synthetic-revenue",
                    ),
                ),
            ),
        )
    child = MarketIntelligenceRequest(
        request_id="financials",
        capability=capability,
        authority=AgentCapability.READ_FUNDAMENTALS,
        allowed_authorities=req.allowed_capabilities,
        subject=req.subject,
        as_of=NOW,
        horizon=req.horizon,
        required_freshness=FreshnessState.UNKNOWN,
        required_canonical_metrics=("fundamental.revenue",),
        budget=AgentBudget(
            max_tool_calls=len(provider_ids), max_cost_units=float(len(provider_ids))
        ),
    )
    route = CapabilityRoutePolicy(
        capability=capability,
        mode=RoutingMode.PRIMARY_WITH_FALLBACK,
        provider_ids=provider_ids,
        maximum_provider_calls=len(provider_ids),
        required_canonical_metrics=("fundamental.revenue",),
    )
    return ControlledServices(
        router=MarketIntelligenceRouter(registry),
        acquisitions=(
            EvidenceAcquisition(
                evidence_type=EvidenceType.FUNDAMENTAL,
                request=child,
                route=route,
                required_metrics=("fundamental.revenue",),
            ),
        ),
    )


def confirmation_services(req: OrchestrationRequest) -> ControlledServices:
    """Existing official adapter and gateway with an explicitly offline HTML transport."""
    from collections.abc import Callable

    from tiaf.events import EventMateriality, StructuredEventFact, StructuredFactKind
    from tiaf.market_intelligence import (
        AuthoritativeConfirmationGateway,
        AuthoritativeConfirmationRequest,
        AuthoritativeConfirmationTask,
        AuthoritativeDocumentKind,
        DiscoveredClaim,
        DocumentContentCache,
        DocumentExtractionRule,
        MaterialityTrigger,
        OfficialSourceKind,
        OfficialSourceRegistration,
    )
    from tiaf.market_intelligence.providers import (
        AuthoritativeDocumentNormalizer,
        CompanyIrOfficialSourceProvider,
        OfficialDocumentLocator,
        OfficialDocumentResponse,
        default_official_source_registry,
    )

    class OfflineTransport:
        def fetch(
            self,
            url: str,
            *,
            validate_url: Callable[[str], None],
            max_bytes: int,
            timeout_seconds: float,
        ) -> OfficialDocumentResponse:
            validate_url(url)
            return OfficialDocumentResponse(
                requested_url=url,
                final_url=url,
                status_code=200,
                mime_type="text/html",
                content=b"<html><body>Revenue: 100</body></html>",
                acquired_at=NOW,
            )

    source = OfficialSourceRegistration(
        source_id="fixture_ir",
        provider_id="fixture_ir",
        display_name="Synthetic offline IR",
        kind=OfficialSourceKind.COMPANY_IR,
        authority=SourceAuthority.AUTHORITATIVE,
        official_domains=("example.test",),
    )
    capability = MarketIntelligenceCapability.READ_FINANCIALS
    provider = CompanyIrOfficialSourceProvider(
        source.provider_id,
        default_official_source_registry((source,)),
        (
            OfficialDocumentLocator(
                locator_id="synthetic-filing",
                subject=req.subject,
                capability=capability,
                document_kind=AuthoritativeDocumentKind.FINANCIAL_RESULT,
                source_url="https://example.test/result",
                title="Synthetic annual results",
                published_at=NOW,
                period="FY2026",
                financial_year="FY2026",
                statement_basis="CONSOLIDATED",
                unit="INR crore",
                currency="INR",
                extraction_rules=(
                    DocumentExtractionRule(
                        field_id="revenue",
                        source_label="Revenue",
                        canonical_metric="revenue",
                        kind="NUMBER",
                        unit="INR crore",
                        currency="INR",
                        period="FY2026",
                        statement_basis="CONSOLIDATED",
                    ),
                ),
            ),
        ),
        OfflineTransport(),
        DocumentContentCache(),
    )
    registry = MarketIntelligenceRegistry()
    registry.register(provider, AuthoritativeDocumentNormalizer(source.provider_id))
    route = CapabilityRoutePolicy(
        policy_id="synthetic-confirmation",
        capability=capability,
        mode=RoutingMode.AUTHORITATIVE_CONFIRMATION,
        provider_ids=(source.provider_id,),
        authoritative_provider_ids=(source.provider_id,),
        maximum_provider_calls=1,
        required_canonical_metrics=("revenue",),
        minimum_source_authority=SourceAuthority.AUTHORITATIVE,
    )
    claim = DiscoveredClaim(
        claim_id="synthetic:claim",
        subject=req.subject,
        capability=capability,
        asserted_facts=(
            StructuredEventFact(
                field_id="revenue",
                kind=StructuredFactKind.NUMBER,
                value=100.0,
                unit="INR crore",
                currency="INR",
            ),
        ),
        discovery_evidence_ids=("event",),
        event_cluster_id="synthetic:results",
        materiality=EventMateriality.HIGH,
        available_from=NOW,
        created_at=NOW,
    )
    child = AuthoritativeConfirmationRequest(
        request_id="synthetic:confirm",
        claim=claim,
        as_of=NOW,
        horizon=req.horizon,
        authority=AgentCapability.READ_FUNDAMENTALS,
        allowed_authorities=req.allowed_capabilities,
        accepted_document_kinds=(AuthoritativeDocumentKind.FINANCIAL_RESULT,),
        eligible_source_kinds=(OfficialSourceKind.COMPANY_IR,),
        required_fields=("revenue",),
        materiality_triggers=(MaterialityTrigger.FINANCIAL_RESULTS,),
        budget=AgentBudget(max_tool_calls=1),
        route_policy_id=route.policy_id,
        route_policy_version=route.policy_version,
    )
    return ControlledServices(
        confirmation_gateway=AuthoritativeConfirmationGateway(MarketIntelligenceRouter(registry)),
        confirmation_tasks=(
            AuthoritativeConfirmationTask(
                request=child,
                route_policy=route,
                run_id="synthetic:official",
                confirmation_id="synthetic:confirmed",
            ),
        ),
    )
