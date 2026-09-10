#!/usr/bin/env python3
"""Bounded read-only live acceptance for official-source confirmation."""

import argparse
import json
from dataclasses import dataclass
from datetime import datetime

from tiaf.agents import AgentBudget, AgentCapability
from tiaf.contracts import Horizon
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.events import EventMateriality, StructuredEventFact, StructuredFactKind
from tiaf.market_intelligence import (
    AuthoritativeConfirmationGateway,
    AuthoritativeConfirmationRequest,
    AuthoritativeConfirmationResult,
    AuthoritativeDocumentKind,
    CapabilityRoutePolicy,
    ConfirmationReasonCode,
    DiscoveredClaim,
    DocumentContentCache,
    MarketIntelligenceCapability,
    MarketIntelligenceRegistry,
    MarketIntelligenceRouter,
    MaterialityTrigger,
    OfficialSourceKind,
    OfficialSourceRegistration,
    RoutingMode,
    SourceAuthority,
)
from tiaf.market_intelligence.providers import (
    AuthoritativeDocumentNormalizer,
    BseOfficialSourceProvider,
    CompanyIrOfficialSourceProvider,
    HttpxOfficialDocumentTransport,
    NseOfficialSourceProvider,
    OfficialDocumentLocator,
    OfficialSourceMarketIntelligenceProvider,
    default_official_source_registry,
)


@dataclass(frozen=True, slots=True)
class LiveCase:
    case_id: str
    subject: str
    source_id: str
    capability: MarketIntelligenceCapability
    authority: AgentCapability
    document_kind: AuthoritativeDocumentKind
    source_url: str
    title: str
    trigger: MaterialityTrigger


CASES = (
    LiveCase(
        case_id="reliance-ir-financial-reporting",
        subject="RELIANCE",
        source_id="reliance_ir",
        capability=MarketIntelligenceCapability.READ_FINANCIALS,
        authority=AgentCapability.READ_FUNDAMENTALS,
        document_kind=AuthoritativeDocumentKind.ANNUAL_REPORT,
        source_url="https://www.ril.com/investors/financial-reporting/annual-reports",
        title="Reliance Industries annual reports",
        trigger=MaterialityTrigger.FINANCIAL_RESULTS,
    ),
    LiveCase(
        case_id="kaynes-nse-announcements",
        subject="KAYNES",
        source_id="nse_official",
        capability=MarketIntelligenceCapability.READ_FILINGS,
        authority=AgentCapability.READ_FILINGS,
        document_kind=AuthoritativeDocumentKind.CORPORATE_ANNOUNCEMENT,
        source_url=(
            "https://www.nseindia.com/api/corporate-announcements"
            "?index=equities&symbol=KAYNES"
        ),
        title="NSE corporate announcements for KAYNES",
        trigger=MaterialityTrigger.MAJOR_ORDER_WIN,
    ),
    LiveCase(
        case_id="reliance-bse-corporate-actions",
        subject="RELIANCE",
        source_id="bse_official",
        capability=MarketIntelligenceCapability.READ_CORPORATE_ACTIONS,
        authority=AgentCapability.READ_FILINGS,
        document_kind=AuthoritativeDocumentKind.CORPORATE_ACTION,
        source_url=(
            "https://api.bseindia.com/BseIndiaAPI/api/CorporateAction/w"
            "?scripcode=500325"
        ),
        title="BSE corporate actions for Reliance Industries",
        trigger=MaterialityTrigger.CORPORATE_ACTION,
    ),
)


def _company_registration() -> OfficialSourceRegistration:
    return OfficialSourceRegistration(
        source_id="reliance_ir",
        provider_id="reliance_ir",
        display_name="Reliance Industries Investor Relations",
        kind=OfficialSourceKind.COMPANY_IR,
        authority=SourceAuthority.AUTHORITATIVE,
        official_domains=("ril.com",),
    )


def _provider(
    case: LiveCase,
    cache: DocumentContentCache,
    transport: HttpxOfficialDocumentTransport,
) -> OfficialSourceMarketIntelligenceProvider:
    registry = default_official_source_registry((_company_registration(),))
    locator = OfficialDocumentLocator(
        locator_id=case.case_id,
        subject=case.subject,
        capability=case.capability,
        document_kind=case.document_kind,
        source_url=case.source_url,
        title=case.title,
        event_materiality=EventMateriality.HIGH,
    )
    if case.source_id == "reliance_ir":
        return CompanyIrOfficialSourceProvider(
            case.source_id,
            registry,
            (locator,),
            transport,
            cache,
        )
    if case.source_id == "nse_official":
        return NseOfficialSourceProvider(registry, (locator,), transport, cache)
    if case.source_id == "bse_official":
        return BseOfficialSourceProvider(registry, (locator,), transport, cache)
    return OfficialSourceMarketIntelligenceProvider(
        case.source_id,
        registry,
        (locator,),
        transport,
        cache,
        maximum_document_bytes=20_000_000,
        timeout_seconds=15,
    )


def _execute_case(
    case: LiveCase,
    cache: DocumentContentCache,
    transport: HttpxOfficialDocumentTransport,
    now: datetime,
) -> AuthoritativeConfirmationResult:
    provider = _provider(case, cache, transport)
    registry = MarketIntelligenceRegistry()
    registry.register(provider, AuthoritativeDocumentNormalizer(provider.identity.provider_id))
    claim = DiscoveredClaim(
        claim_id=f"live-claim:{case.case_id}",
        subject=case.subject,
        capability=case.capability,
        asserted_facts=(
            StructuredEventFact(
                field_id="official_document_reference",
                kind=StructuredFactKind.TEXT,
                value="authoritative document expected",
            ),
        ),
        discovery_evidence_ids=(f"live-discovery:{case.case_id}",),
        materiality=EventMateriality.HIGH,
        available_from=now,
        created_at=now,
    )
    request = AuthoritativeConfirmationRequest(
        request_id=f"live-request:{case.case_id}",
        claim=claim,
        as_of=now,
        horizon=Horizon(label="POSITIONAL"),
        authority=case.authority,
        allowed_authorities=(case.authority,),
        accepted_document_kinds=(case.document_kind,),
        eligible_source_kinds=(
            OfficialSourceKind.COMPANY_IR
            if case.source_id == "reliance_ir"
            else OfficialSourceKind.EXCHANGE_OR_REGULATOR,
        ),
        required_fields=("official_document_reference",),
        materiality_triggers=(case.trigger,),
        budget=AgentBudget(max_tool_calls=1, max_cost_units=0, max_elapsed_seconds=20),
        route_policy_id=f"live-policy:{case.case_id}",
        route_policy_version="1.0",
    )
    policy = CapabilityRoutePolicy(
        policy_id=request.route_policy_id,
        policy_version=request.route_policy_version,
        capability=case.capability,
        mode=RoutingMode.AUTHORITATIVE_CONFIRMATION,
        provider_ids=(provider.identity.provider_id,),
        authoritative_provider_ids=(provider.identity.provider_id,),
        maximum_provider_calls=1,
        required_canonical_metrics=request.required_fields,
        minimum_source_authority=SourceAuthority.AUTHORITATIVE,
        maximum_elapsed_seconds=20,
    )
    return AuthoritativeConfirmationGateway(MarketIntelligenceRouter(registry)).execute(
        request,
        policy,
        run_id=f"live-run:{case.case_id}",
        confirmation_id=f"live-confirmation:{case.case_id}",
    )


def run_live() -> tuple[bool, dict[str, object]]:
    started_at = datetime.now(TIAF_TIMEZONE)
    cache = DocumentContentCache()
    transport = HttpxOfficialDocumentTransport()
    rows: list[dict[str, object]] = []
    document_successes = 0
    restrictions = 0
    for case in CASES:
        result = _execute_case(case, cache, transport, started_at)
        replayed = AuthoritativeConfirmationResult.model_validate_json(result.model_dump_json())
        replay_exact = (
            replayed == result
            and replayed.semantic_fingerprint == result.semantic_fingerprint
        )
        if result.authoritative_documents:
            document_successes += 1
            document = result.authoritative_documents[0]
            source_domain: str | None = document.source.validated_domain
            content_hash: str | None = document.content_hash
            authority: str | None = document.source.authority.value
        else:
            source_domain = None
            content_hash = None
            authority = None
        if ConfirmationReasonCode.ACCESS_RESTRICTED in result.reason_codes:
            restrictions += 1
        rows.append(
            {
                "case": case.case_id,
                "symbol": case.subject,
                "source": case.source_id,
                "domain": source_domain,
                "document_kind": case.document_kind.value,
                "confirmation_status": result.status.value,
                "authority": authority,
                "content_hash": content_hash,
                "replay_exact": replay_exact,
                "failure_kinds": [
                    kind.value for audit in result.route_audits for kind in audit.failure_kinds
                ],
            }
        )
    all_replay = all(bool(row["replay_exact"]) for row in rows)
    accepted = all_replay and (document_successes > 0 or restrictions == len(CASES))
    report: dict[str, object] = {
        "acceptance_timestamp": started_at.isoformat(),
        "accepted": accepted,
        "live_calls": len(CASES),
        "document_successes": document_successes,
        "typed_access_restrictions": restrictions,
        "cache_entries": len(cache),
        "offline_replay_exact": all_replay,
        "cases": rows,
        "read_only": True,
        "secrets_required": False,
    }
    return accepted, report


def _print_report(report: dict[str, object]) -> None:
    print("case                              source          status                 replay")
    print("-" * 82)
    cases = report["cases"]
    assert isinstance(cases, list)
    for row in cases:
        assert isinstance(row, dict)
        print(
            f"{str(row['case']):33} {str(row['source']):15} "
            f"{str(row['confirmation_status']):22} "
            f"{'YES' if row['replay_exact'] else 'NO'}"
        )
    print()
    print(json.dumps(report, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run at most three read-only official-source confirmation calls."
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="perform the bounded live NSE/BSE/company-IR calls",
    )
    args = parser.parse_args(argv)
    if not args.live:
        print("Authoritative live acceptance disabled; pass --live to permit external reads.")
        return 0
    accepted, report = run_live()
    _print_report(report)
    return 0 if accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
