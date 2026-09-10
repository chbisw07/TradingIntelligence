#!/usr/bin/env python3
"""Bounded read-only live acceptance for A3.6.2 deep-research integration."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from statistics import median

from tiaf.agents import AgentBudget, AgentUsage
from tiaf.contracts import FreshnessState, Horizon
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.events import EventMateriality, StructuredEventFact, StructuredFactKind
from tiaf.market_intelligence import (
    AuthoritativeConfirmationGateway,
    AuthoritativeConfirmationRequest,
    AuthoritativeConfirmationResult,
    AuthoritativeDocumentKind,
    CapabilityRoutePolicy,
    DeepResearchIntegrationController,
    DeepResearchResult,
    DiscoveredClaim,
    DocumentContentCache,
    MarketIntelligenceCapability,
    MarketIntelligenceRegistry,
    MarketIntelligenceRequest,
    MarketIntelligenceResearchController,
    MarketIntelligenceResearchPolicy,
    MarketIntelligenceResearchRequest,
    MarketIntelligenceRouter,
    MaterialityTrigger,
    OfficialSourceKind,
    OfficialSourceRegistration,
    ResearchDepth,
    RoutingMode,
    SourceAuthority,
    authority_for,
    tapetide_normalizer,
    yahoo_secondary_route_policy,
)
from tiaf.market_intelligence.providers import (
    AuthoritativeDocumentNormalizer,
    CompanyIrOfficialSourceProvider,
    HttpxOfficialDocumentTransport,
    OfficialDocumentLocator,
    TapetideConnectorError,
    TapetideMarketIntelligenceProvider,
    TapetideMcpClient,
    YahooConnectorError,
    YahooMarketIntelligenceProvider,
    YahooMcpClient,
    default_official_source_registry,
    yahoo_normalizer,
)


@dataclass(frozen=True, slots=True)
class LiveScenario:
    symbol: str
    capabilities: tuple[MarketIntelligenceCapability, ...]


SCENARIOS = (
    LiveScenario(
        "RELIANCE",
        (
            MarketIntelligenceCapability.READ_COMPANY_PROFILE,
            MarketIntelligenceCapability.READ_FINANCIALS,
        ),
    ),
    LiveScenario(
        "HDFCBANK",
        (
            MarketIntelligenceCapability.READ_COMPANY_PROFILE,
            MarketIntelligenceCapability.READ_FINANCIALS,
        ),
    ),
    LiveScenario(
        "KAYNES",
        (
            MarketIntelligenceCapability.READ_COMPANY_PROFILE,
            MarketIntelligenceCapability.READ_FILINGS,
        ),
    ),
    LiveScenario(
        "ATHERENERG",
        (
            MarketIntelligenceCapability.READ_COMPANY_PROFILE,
            MarketIntelligenceCapability.READ_FINANCIALS,
        ),
    ),
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="authorize at most 12 read-only provider calls across four research cases",
    )
    return parser


def _request(
    scenario: LiveScenario,
    capability: MarketIntelligenceCapability,
    sequence: int,
    as_of: datetime,
) -> MarketIntelligenceRequest:
    authority = authority_for(capability)
    attributes: dict[str, str | int] = {}
    required: tuple[str, ...] = ()
    max_calls = 1
    if capability is MarketIntelligenceCapability.READ_FINANCIALS:
        attributes = {"section": "profit_loss", "period": "annual", "limit": 4}
        required = ("fundamental.revenue",)
        max_calls = 2
    elif capability is MarketIntelligenceCapability.READ_FILINGS:
        attributes = {"limit": 5}
    elif capability is MarketIntelligenceCapability.READ_COMPANY_PROFILE:
        required = ("company.name",)
    return MarketIntelligenceRequest(
        request_id=f"a362-live:{sequence}:{scenario.symbol}:{capability.value}",
        capability=capability,
        authority=authority,
        allowed_authorities=(authority,),
        subject=scenario.symbol,
        as_of=as_of,
        horizon=Horizon(label="POSITIONAL"),
        required_freshness=FreshnessState.UNKNOWN,
        required_canonical_metrics=required,
        budget=AgentBudget(
            max_tool_calls=max_calls,
            max_cost_units=2,
            max_elapsed_seconds=90,
        ),
        attributes=attributes,
    )


def _route(
    scenario: LiveScenario,
    capability: MarketIntelligenceCapability,
) -> CapabilityRoutePolicy:
    if capability is MarketIntelligenceCapability.READ_COMPANY_PROFILE:
        return CapabilityRoutePolicy(
            policy_id="a362-yahoo-profile",
            capability=capability,
            mode=RoutingMode.FIRST_SUCCESS,
            provider_ids=("yahoo",),
            maximum_provider_calls=1,
            required_canonical_metrics=("company.name",),
        )
    if capability is MarketIntelligenceCapability.READ_FILINGS:
        return CapabilityRoutePolicy(
            policy_id="a362-tapetide-filings",
            capability=capability,
            mode=RoutingMode.FIRST_SUCCESS,
            provider_ids=("tapetide",),
            maximum_provider_calls=1,
        )
    return yahoo_secondary_route_policy(
        capability,
        mode=(
            RoutingMode.MULTI_SOURCE
            if scenario.symbol == "RELIANCE"
            else RoutingMode.PRIMARY_WITH_FALLBACK
        ),
        required_canonical_metrics=("fundamental.revenue",),
    )


def _research_request(
    scenario: LiveScenario,
    index: int,
    as_of: datetime,
) -> tuple[MarketIntelligenceResearchRequest, MarketIntelligenceResearchPolicy]:
    requests = tuple(
        _request(scenario, capability, index * 10 + sequence, as_of)
        for sequence, capability in enumerate(scenario.capabilities, start=1)
    )
    routes = tuple(_route(scenario, capability) for capability in scenario.capabilities)
    confirmation_allowance = 1 if scenario.symbol == "RELIANCE" else 0
    return (
        MarketIntelligenceResearchRequest(
            research_request_id=f"a362-live:{scenario.symbol}",
            subject=scenario.symbol,
            as_of=as_of,
            horizon=Horizon(label="POSITIONAL"),
            capability_requests=requests,
            budget=AgentBudget(
                max_tool_calls=sum(item.budget.max_tool_calls for item in requests)
                + confirmation_allowance,
                max_cost_units=sum(item.budget.max_cost_units for item in requests),
                max_elapsed_seconds=240,
            ),
        ),
        MarketIntelligenceResearchPolicy(
            plan_id="a362-live-progressive-enrichment",
            plan_version="1.0",
            routes=routes,
        ),
    )


def _official_confirmation(
    acquisition_id: str,
    as_of: datetime,
) -> AuthoritativeConfirmationResult:
    source_registry = default_official_source_registry(
        (
            OfficialSourceRegistration(
                source_id="reliance_ir",
                provider_id="reliance_ir",
                display_name="Reliance Industries Investor Relations",
                kind=OfficialSourceKind.COMPANY_IR,
                authority=SourceAuthority.AUTHORITATIVE,
                official_domains=("ril.com",),
            ),
        )
    )
    provider = CompanyIrOfficialSourceProvider(
        "reliance_ir",
        source_registry,
        (
            OfficialDocumentLocator(
                locator_id="a362-reliance-annual-report-index",
                subject="RELIANCE",
                capability=MarketIntelligenceCapability.READ_FINANCIALS,
                document_kind=AuthoritativeDocumentKind.ANNUAL_REPORT,
                source_url="https://www.ril.com/investors/financial-reporting/annual-reports",
                title="Reliance Industries annual reports",
                event_materiality=EventMateriality.HIGH,
            ),
        ),
        HttpxOfficialDocumentTransport(),
        DocumentContentCache(),
    )
    registry = MarketIntelligenceRegistry()
    registry.register(provider, AuthoritativeDocumentNormalizer("reliance_ir"))
    claim = DiscoveredClaim(
        claim_id="a362:reliance:material-financial-source",
        subject="RELIANCE",
        capability=MarketIntelligenceCapability.READ_FINANCIALS,
        asserted_facts=(
            StructuredEventFact(
                field_id="official_document_reference",
                kind=StructuredFactKind.TEXT,
                value="official annual-report index expected",
            ),
        ),
        discovery_evidence_ids=(acquisition_id,),
        materiality=EventMateriality.HIGH,
        available_from=as_of,
        created_at=as_of,
    )
    request = AuthoritativeConfirmationRequest(
        request_id="a362:reliance:official-confirmation",
        claim=claim,
        as_of=as_of,
        horizon=Horizon(label="POSITIONAL"),
        authority=authority_for(MarketIntelligenceCapability.READ_FINANCIALS),
        allowed_authorities=(
            authority_for(MarketIntelligenceCapability.READ_FINANCIALS),
        ),
        accepted_document_kinds=(AuthoritativeDocumentKind.ANNUAL_REPORT,),
        eligible_source_kinds=(OfficialSourceKind.COMPANY_IR,),
        required_fields=("official_document_reference",),
        materiality_triggers=(MaterialityTrigger.FINANCIAL_RESULTS,),
        budget=AgentBudget(max_tool_calls=1, max_cost_units=0, max_elapsed_seconds=30),
        route_policy_id="a362-reliance-official",
        route_policy_version="1.0",
    )
    route = CapabilityRoutePolicy(
        policy_id=request.route_policy_id,
        capability=MarketIntelligenceCapability.READ_FINANCIALS,
        mode=RoutingMode.AUTHORITATIVE_CONFIRMATION,
        provider_ids=("reliance_ir",),
        authoritative_provider_ids=("reliance_ir",),
        maximum_provider_calls=1,
        required_canonical_metrics=request.required_fields,
        minimum_source_authority=SourceAuthority.AUTHORITATIVE,
        maximum_elapsed_seconds=30,
    )
    return AuthoritativeConfirmationGateway(MarketIntelligenceRouter(registry)).execute(
        request,
        route,
        run_id="a362:reliance:official-route",
        confirmation_id="a362:reliance:official-result",
    )


def _summary(result: DeepResearchResult, replay_exact: bool) -> dict[str, object]:
    providers = tuple(
        dict.fromkeys(
            audit.provider_id
            for run in result.acquisition.capability_runs
            for audit in run.audits
        )
    )
    return {
        "symbol": result.profile.subject,
        "status": result.profile.status.value,
        "providers": providers,
        "capabilities": [
            item.capability.value for item in result.acquisition.request.capability_requests
        ],
        "tool_calls": result.usage.tool_calls,
        "latency_seconds": round(result.usage.elapsed_seconds, 6),
        "canonical_facts": len(result.context.canonical_facts),
        "ambiguous_evidence": len(result.context.ambiguous_evidence),
        "contradictions": len(result.context.contradictions),
        "research_gaps": len(result.context.research_gaps),
        "graph_edges": len(result.evidence_graph.edges),
        "confirmation_statuses": [item.status.value for item in result.confirmations],
        "llm_calls": result.usage.llm_calls,
        "input_tokens": result.usage.input_tokens,
        "output_tokens": result.usage.output_tokens,
        "replay_exact": replay_exact,
        "semantic_fingerprint": result.semantic_fingerprint,
    }


def _print_table(rows: list[dict[str, object]]) -> None:
    print(
        "symbol       status       providers                 calls facts gaps edges "
        "confirmation replay"
    )
    print("-" * 106)
    for row in rows:
        confirmation = ",".join(str(item) for item in row["confirmation_statuses"]) or "-"
        print(
            f"{str(row['symbol']):<12} {str(row['status']):<12} "
            f"{','.join(str(item) for item in row['providers']):<25} "
            f"{int(row['tool_calls']):>5} {int(row['canonical_facts']):>5} "
            f"{int(row['research_gaps']):>4} {int(row['graph_edges']):>5} "
            f"{confirmation:<12} {'YES' if row['replay_exact'] else 'NO'}"
        )


def run_live(*, yahoo_command: str = "uvx") -> tuple[bool, dict[str, object]]:
    started_at = datetime.now(TIAF_TIMEZONE)
    yahoo_client = YahooMcpClient(command=yahoo_command)
    tapetide_client = TapetideMcpClient.from_environment()
    registry = MarketIntelligenceRegistry()
    registry.register(
        TapetideMarketIntelligenceProvider(tapetide_client), tapetide_normalizer()
    )
    registry.register(
        YahooMarketIntelligenceProvider(yahoo_client), yahoo_normalizer()
    )
    research_controller = MarketIntelligenceResearchController(
        MarketIntelligenceRouter(registry)
    )
    integrator = DeepResearchIntegrationController(research_controller)
    results: list[DeepResearchResult] = []
    try:
        with tapetide_client, yahoo_client:
            for index, scenario in enumerate(SCENARIOS, start=1):
                # Yahoo evidence without a publication timestamp becomes available at
                # acquisition. Use a small bounded live-call envelope after both MCP
                # sessions have initialized so later capability calls remain visible.
                as_of = datetime.now(TIAF_TIMEZONE) + timedelta(seconds=10)
                request, policy = _research_request(scenario, index, as_of)
                acquisition = research_controller.execute(
                    request,
                    policy,
                    research_run_id=f"a362-live:{scenario.symbol}:acquisition",
                )
                confirmations: tuple[AuthoritativeConfirmationResult, ...] = ()
                usage = acquisition.usage
                if scenario.symbol == "RELIANCE":
                    discovery_ids = sorted(
                        {
                            item.evidence_id
                            for run in acquisition.capability_runs
                            for batch in run.batches
                            for item in batch.canonical_evidence
                            if item.metric.startswith("fundamental.")
                        }
                    )
                    if not discovery_ids:
                        discovery_ids = sorted(
                            {
                                item.evidence_id
                                for run in acquisition.capability_runs
                                for batch in run.batches
                                for item in batch.canonical_evidence
                            }
                        )
                    if discovery_ids:
                        confirmation = _official_confirmation(discovery_ids[0], as_of)
                        confirmations = (confirmation,)
                        usage = AgentUsage(
                            tool_calls=acquisition.usage.tool_calls
                            + confirmation.usage.tool_calls,
                            cost_units=acquisition.usage.cost_units
                            + confirmation.usage.cost_units,
                            elapsed_seconds=acquisition.usage.elapsed_seconds
                            + confirmation.usage.elapsed_seconds,
                            metadata={"baseline": "NO_LLM"},
                        )
                results.append(
                    integrator.assemble(
                        acquisition,
                        research_id=f"a362-live:{scenario.symbol}",
                        objective="bounded company research integration acceptance",
                        depth=ResearchDepth.L2_INVESTMENT_RESEARCH,
                        a2_evidence_fingerprint="0" * 64,
                        confirmations=confirmations,
                        usage=usage,
                    )
                )
            server = {
                "tapetide": {
                    "name": tapetide_client.server_name,
                    "version": tapetide_client.server_version,
                },
                "yahoo": {
                    "name": yahoo_client.server_name,
                    "version": yahoo_client.server_version,
                },
            }
    except (TapetideConnectorError, YahooConnectorError) as exc:
        return False, {
            "accepted": False,
            "acceptance_timestamp": started_at.isoformat(),
            "blocker": f"live connector failed safely: {exc}",
            "live_calls": 0,
            "read_only": True,
            "secrets_printed": False,
        }

    replay: list[bool] = []
    with tempfile.TemporaryDirectory(prefix="tiaf-a362-replay-") as directory:
        path = Path(directory) / "deep_research_results.jsonl"
        path.write_text(
            "\n".join(item.model_dump_json() for item in results) + "\n",
            encoding="utf-8",
        )
        for original, line in zip(results, path.read_text().splitlines(), strict=True):
            restored = DeepResearchResult.model_validate_json(line)
            replay.append(
                restored == original
                and restored.semantic_fingerprint == original.semantic_fingerprint
                and restored.context.canonical_facts == original.context.canonical_facts
                and restored.context.contradictions == original.context.contradictions
                and restored.context.research_gaps == original.context.research_gaps
                and restored.evidence_graph == original.evidence_graph
                and restored.confirmations == original.confirmations
            )
    rows = [_summary(result, exact) for result, exact in zip(results, replay, strict=True)]
    total_calls = sum(result.usage.tool_calls for result in results)
    latencies = [result.usage.elapsed_seconds for result in results]
    checks = {
        "all_symbols_represented": {item.profile.subject for item in results}
        == {item.symbol for item in SCENARIOS},
        "canonical_evidence_present_per_symbol": all(
            item.context.canonical_facts for item in results
        ),
        "reliance_multi_source": {
            batch.provider_id
            for run in results[0].acquisition.capability_runs
            for batch in run.batches
        }
        >= {"tapetide", "yahoo"},
        "reliance_authoritative_attempted": bool(results[0].confirmations),
        "sparse_case_keeps_gaps": bool(results[-1].context.research_gaps),
        "all_replay_exact": all(replay),
        "no_llm": all(
            item.usage.llm_calls == item.usage.input_tokens == item.usage.output_tokens == 0
            for item in results
        ),
        "call_bound_respected": total_calls <= 12,
        "provider_neutral_symbols": all(
            "." not in item.profile.subject for item in results
        ),
    }
    accepted = all(checks.values())
    report: dict[str, object] = {
        "accepted": accepted,
        "acceptance_timestamp": started_at.isoformat(),
        "server": server,
        "live_calls": total_calls,
        "latency_seconds": {
            "minimum": min(latencies),
            "median": median(latencies),
            "maximum": max(latencies),
            "total": sum(latencies),
        },
        "cases": rows,
        "checks": checks,
        "read_only": True,
        "secrets_printed": False,
    }
    _print_table(rows)
    return accepted, report


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not args.live:
        print("A3.6.2 live calls are disabled; pass --live to authorize bounded reads.")
        return 0
    sibling_uvx = Path(sys.executable).with_name("uvx")
    yahoo_command = shutil.which("uvx") or (
        str(sibling_uvx) if sibling_uvx.is_file() else None
    )
    missing = tuple(
        command
        for command, location in (("npx", shutil.which("npx")), ("uvx", yahoo_command))
        if location is None
    )
    if missing:
        print(f"A3.6.2 live acceptance not run; missing command(s): {', '.join(missing)}")
        return 2
    assert yahoo_command is not None
    accepted, report = run_live(yahoo_command=yahoo_command)
    print()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
