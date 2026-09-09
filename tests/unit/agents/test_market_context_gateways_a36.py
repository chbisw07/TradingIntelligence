"""A3.6 explicit mapping, point-in-time, gateway, and shared-cache tests."""

from datetime import datetime, timedelta

from tiaf.agents import AgentBudget, AgentCapability, SpecialistId
from tiaf.agents.gateways import (
    EvidenceGatewayContext,
    EvidenceGatewayRequest,
    EvidenceGatewayStatus,
)
from tiaf.context import AnalysisPurpose
from tiaf.contracts import DataQuality, EvidenceType, FreshnessState, Horizon
from tiaf.contracts.common import Metadata
from tiaf.data import InstrumentType
from tiaf.market_context import (
    ContextObservation,
    ContextObservationKind,
    InMemoryMacroContextProvider,
    InMemorySectorContextProvider,
    MacroContextEvidenceGateway,
    MacroContextRequest,
    MacroEvidenceFamily,
    MappingQuality,
    SectorContextEvidenceGateway,
    SectorContextRequest,
    SectorEvidenceFamily,
    SectorIdentity,
    SensitivityDirection,
    SubjectMacroSensitivity,
    macro_gateway_attributes,
    sector_gateway_attributes,
)

from ._contextual_support import NOW


def observation(
    metric: str,
    value: str | int | float | bool,
    family: SectorEvidenceFamily | MacroEvidenceFamily,
    *,
    observation_id: str | None = None,
    available_at: datetime = NOW,
    metadata: Metadata | None = None,
) -> ContextObservation:
    return ContextObservation(
        observation_id=observation_id or f"observation:{metric}",
        metric_id=metric,
        value=value,
        family=family,
        kind=ContextObservationKind.STATE,
        observed_at=available_at,
        available_at=available_at,
        source_id="fixture-source",
        source_version="1.0",
        source_reference=f"source:{metric}",
        quality=DataQuality.GOOD,
        freshness=FreshnessState.FRESH,
        metadata=metadata or {},
    )


def sector_identity() -> SectorIdentity:
    return SectorIdentity(
        sector_id="ENERGY",
        sector_name="Energy",
        benchmark_symbol="NIFTYENERGY",
        mapping_source="nse-classification",
        mapping_version="2026.1",
        quality=MappingQuality.VERIFIED,
        effective_from=NOW - timedelta(days=365),
    )


def gateway_context() -> EvidenceGatewayContext:
    return EvidenceGatewayContext(
        authorized_capabilities=(
            AgentCapability.READ_SECTOR_CONTEXT,
            AgentCapability.READ_MACRO_CONTEXT,
        ),
        remaining_budget=AgentBudget(),
        invoked_at=NOW,
        deadline_at=NOW + timedelta(seconds=5),
    )


def gateway_request(
    capability: AgentCapability, subject: str, attributes: tuple[str, ...]
) -> EvidenceGatewayRequest:
    return EvidenceGatewayRequest(
        request_id=f"gateway:{subject}:{capability.value}",
        capability=capability,
        allowed_capabilities=(AgentCapability.READ_A2_EVIDENCE, capability),
        subject=subject,
        instrument_type=InstrumentType.EQUITY,
        horizon=Horizon(label="POSITIONAL", min_days=2, max_days=20),
        purpose=AnalysisPurpose.OPPORTUNITY,
        evidence_type=EvidenceType.SECTOR
        if capability is AgentCapability.READ_SECTOR_CONTEXT
        else EvidenceType.MACRO,
        requested_attributes=attributes,
        as_of=NOW,
        required_freshness=FreshnessState.FRESH,
        deterministic_baseline_reference="a2-context-baseline",
        requesting_specialist=(
            SpecialistId.SECTOR
            if capability is AgentCapability.READ_SECTOR_CONTEXT
            else SpecialistId.MACRO
        ),
        budget=AgentBudget(),
        timeout_seconds=5,
    )


def test_sector_provider_requires_exact_active_mapping_and_excludes_future_data() -> None:
    identity = sector_identity()
    provider = InMemorySectorContextProvider(
        {"RELIANCE": (identity,)},
        (
            observation(
                "sector.relative_return_percent",
                2.0,
                SectorEvidenceFamily.RELATIVE_TREND,
                metadata={"sector_id": "ENERGY"},
            ),
            observation(
                "sector.event.future",
                "POLICY",
                SectorEvidenceFamily.EVENT,
                observation_id="future-sector-event",
                available_at=NOW + timedelta(days=1),
                metadata={"sector_id": "ENERGY"},
            ),
        ),
    )
    snapshot = provider.fetch(
        SectorContextRequest(
            request_id="sector-request",
            subject="RELIANCE",
            sector_id="ENERGY",
            benchmark_symbol="NIFTYENERGY",
            as_of=NOW,
            horizon=Horizon(label="POSITIONAL"),
            families=(SectorEvidenceFamily.RELATIVE_TREND, SectorEvidenceFamily.EVENT),
            required_freshness=FreshnessState.FRESH,
        )
    )
    assert tuple(item.observation_id for item in snapshot.observations) == (
        "observation:sector.relative_return_percent",
    )
    assert snapshot.missing_families == (SectorEvidenceFamily.EVENT,)
    assert provider.resolve_sector("UNKNOWN", NOW) is None


def test_sector_gateway_reuses_same_sector_source_snapshot_across_subjects() -> None:
    identity = sector_identity()
    provider = InMemorySectorContextProvider(
        {"RELIANCE": (identity,), "ONGC": (identity,)},
        (
            observation(
                "sector.relative_return_percent",
                2.0,
                SectorEvidenceFamily.RELATIVE_TREND,
                metadata={"sector_id": "ENERGY"},
            ),
        ),
    )
    gateway = SectorContextEvidenceGateway(provider)
    attributes = sector_gateway_attributes(
        sector_id="ENERGY",
        benchmark_symbol="NIFTYENERGY",
        families=(SectorEvidenceFamily.RELATIVE_TREND,),
    )
    first = gateway.fetch(
        gateway_request(AgentCapability.READ_SECTOR_CONTEXT, "RELIANCE", attributes),
        gateway_context(),
    )
    second = gateway.fetch(
        gateway_request(AgentCapability.READ_SECTOR_CONTEXT, "ONGC", attributes), gateway_context()
    )
    assert first.status is second.status is EvidenceGatewayStatus.SUCCESS
    assert provider.fetch_count == 1
    assert first.evidence_pack is not None and second.evidence_pack is not None
    assert first.evidence_pack.subject == "RELIANCE"
    assert second.evidence_pack.subject == "ONGC"
    assert first.evidence_pack.evidence_fingerprint != second.evidence_pack.evidence_fingerprint


def test_sector_gateway_does_not_invent_missing_mapping() -> None:
    gateway = SectorContextEvidenceGateway(InMemorySectorContextProvider({}, ()))
    attributes = sector_gateway_attributes(
        sector_id="ENERGY",
        benchmark_symbol="NIFTYENERGY",
        families=(SectorEvidenceFamily.RELATIVE_TREND,),
    )
    result = gateway.fetch(
        gateway_request(AgentCapability.READ_SECTOR_CONTEXT, "RELIANCE", attributes),
        gateway_context(),
    )
    assert result.status is EvidenceGatewayStatus.MISSING
    assert result.evidence_pack is None


def test_macro_provider_excludes_future_release_and_preserves_event_state_kind() -> None:
    current = observation("macro.rates.regime", "TIGHTENING", MacroEvidenceFamily.INTEREST_RATES)
    future = ContextObservation.model_validate(
        {
            **current.model_dump(mode="python"),
            "observation_id": "future-rate-event",
            "metric_id": "macro.rates.event",
            "value": "RATE_DECISION",
            "kind": ContextObservationKind.EVENT,
            "observed_at": NOW + timedelta(days=1),
            "available_at": NOW + timedelta(days=1),
        }
    )
    provider = InMemoryMacroContextProvider({"INDIA": (current, future)})
    snapshot = provider.fetch(
        MacroContextRequest(
            request_id="macro-request",
            subject="RELIANCE",
            market="INDIA",
            as_of=NOW,
            horizon=Horizon(label="POSITIONAL"),
            families=(MacroEvidenceFamily.INTEREST_RATES,),
            required_freshness=FreshnessState.FRESH,
        )
    )
    assert tuple(item.observation_id for item in snapshot.observations) == (current.observation_id,)
    assert snapshot.observations[0].kind is ContextObservationKind.STATE


def test_macro_gateway_reuses_market_snapshot_but_projects_subject_sensitivity() -> None:
    macro = observation("macro.market_risk.score", 0.7, MacroEvidenceFamily.GLOBAL_RISK)
    sensitivities = tuple(
        SubjectMacroSensitivity(
            sensitivity_id=f"sensitivity:{symbol}",
            subject=symbol,
            family=MacroEvidenceFamily.GLOBAL_RISK,
            driver_id="global-risk",
            direction=SensitivityDirection.HARMED_BY_RISE,
            mapping_source="declared-map",
            mapping_version="1.0",
            quality=MappingQuality.DECLARED,
            effective_from=NOW - timedelta(days=1),
        )
        for symbol in ("RELIANCE", "ONGC")
    )
    provider = InMemoryMacroContextProvider({"INDIA": (macro,)}, sensitivities)
    gateway = MacroContextEvidenceGateway(provider)
    attributes = macro_gateway_attributes(
        market="INDIA", families=(MacroEvidenceFamily.GLOBAL_RISK,)
    )
    first = gateway.fetch(
        gateway_request(AgentCapability.READ_MACRO_CONTEXT, "RELIANCE", attributes),
        gateway_context(),
    )
    second = gateway.fetch(
        gateway_request(AgentCapability.READ_MACRO_CONTEXT, "ONGC", attributes), gateway_context()
    )
    assert first.status is second.status is EvidenceGatewayStatus.SUCCESS
    assert provider.fetch_count == 1
    assert first.evidence_pack is not None and second.evidence_pack is not None
    assert any("RELIANCE" in item.evidence_id for item in first.evidence_pack.references)
    assert any("ONGC" in item.evidence_id for item in second.evidence_pack.references)


def test_context_contracts_round_trip_as_json_arrays_with_kolkata_timestamps() -> None:
    item = observation("macro.volatility.percentile", 0.8, MacroEvidenceFamily.VOLATILITY)
    rebuilt = ContextObservation.model_validate(item.model_dump(mode="json"))
    dumped = item.model_dump(mode="json")
    assert rebuilt == item
    assert isinstance(dumped["applicable_horizons"], list)
    assert dumped["observed_at"].endswith("+05:30")
