"""Bounded, explicit live acceptance for the Yahoo secondary provider."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from statistics import median
from typing import Any

from pydantic import JsonValue

from tiaf.agents import AgentBudget
from tiaf.contracts import FreshnessState, Horizon
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.market_intelligence import (
    CapabilityRoutePolicy,
    CapabilitySupport,
    EvidenceOutputType,
    MarketIntelligenceCapability,
    MarketIntelligenceRegistry,
    MarketIntelligenceRequest,
    MarketIntelligenceRouter,
    MarketIntelligenceRun,
    NormalizedEvidenceBatch,
    PointInTimeQuality,
    ProviderCapabilityConstraints,
    ProviderCapabilityDeclaration,
    ProviderFailure,
    ProviderFailureKind,
    ProviderFetchResult,
    ProviderResultStatus,
    RoutingMode,
    RuleBasedNormalizer,
    SemanticMappingQuality,
    SourceAuthority,
    authority_for,
    yahoo_secondary_route_policy,
)
from tiaf.market_intelligence.providers import (
    FixtureMarketIntelligenceProvider,
    YahooConnectorError,
    YahooMarketIntelligenceProvider,
    YahooMcpClient,
    yahoo_normalizer,
)


@dataclass(frozen=True, slots=True)
class LiveCall:
    symbol: str
    capability: MarketIntelligenceCapability
    attributes: tuple[tuple[str, JsonValue], ...] = ()

    @property
    def label(self) -> str:
        return f"{self.symbol}:{self.capability.value}"


CALLS = (
    LiveCall("RELIANCE", MarketIntelligenceCapability.READ_COMPANY_PROFILE),
    LiveCall("HDFCBANK", MarketIntelligenceCapability.READ_COMPANY_PROFILE),
    LiveCall("KAYNES", MarketIntelligenceCapability.READ_COMPANY_PROFILE),
    LiveCall("ATHERENERG", MarketIntelligenceCapability.READ_COMPANY_PROFILE),
    LiveCall(
        "RELIANCE",
        MarketIntelligenceCapability.READ_FINANCIALS,
        (("statement_type", "income"), ("period", "annual"), ("limit", 4)),
    ),
    LiveCall(
        "ATHERENERG",
        MarketIntelligenceCapability.READ_FINANCIALS,
        (("statement_type", "income"), ("period", "annual"), ("limit", 4)),
    ),
    LiveCall(
        "RELIANCE",
        MarketIntelligenceCapability.READ_EARNINGS_CALENDAR,
        (("limit", 12), ("future_only", False)),
    ),
    LiveCall(
        "RELIANCE",
        MarketIntelligenceCapability.READ_NEWS,
        (("limit", 5),),
    ),
    LiveCall(
        "RELIANCE",
        MarketIntelligenceCapability.READ_ANALYST_FORECASTS,
        (("limit", 20),),
    ),
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="authorize exactly 9 Yahoo calls plus 1 deterministic-fallback Yahoo call",
    )
    return parser


def _request(
    spec: LiveCall,
    sequence: int,
    *,
    required_metrics: tuple[str, ...] = (),
) -> MarketIntelligenceRequest:
    authority = authority_for(spec.capability)
    return MarketIntelligenceRequest(
        request_id=f"yahoo-live-a361-{sequence:02d}",
        capability=spec.capability,
        authority=authority,
        allowed_authorities=(authority,),
        subject=spec.symbol,
        # Yahoo observations without provider publication time become available
        # at call acquisition. Keep a small bounded envelope around construction.
        as_of=datetime.now(TIAF_TIMEZONE) + timedelta(seconds=2),
        horizon=Horizon(label="POSITIONAL"),
        required_freshness=FreshnessState.UNKNOWN,
        required_canonical_metrics=required_metrics,
        budget=AgentBudget(
            max_tool_calls=2,
            max_cost_units=1,
            max_elapsed_seconds=60,
        ),
        attributes=dict(spec.attributes),
    )


def _yahoo_only_policy(capability: MarketIntelligenceCapability) -> CapabilityRoutePolicy:
    return CapabilityRoutePolicy(
        policy_id="yahoo-live-only",
        capability=capability,
        mode=RoutingMode.FIRST_SUCCESS,
        provider_ids=("yahoo",),
        maximum_provider_calls=1,
    )


def _semantic_fingerprint(batch: NormalizedEvidenceBatch) -> str:
    semantic = {
        "provider_id": batch.provider_id,
        "capability": batch.capability.value,
        "native_observations": batch.native_observations,
        "normalization_records": batch.normalization_records,
        "canonical_evidence": batch.canonical_evidence,
        "normalized_events": batch.normalized_events,
        "gaps": batch.gaps,
    }
    encoded = json.dumps(
        {
            key: (
                [item.model_dump(mode="json") for item in value]
                if isinstance(value, tuple)
                else value
            )
            for key, value in semantic.items()
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _batch(run: MarketIntelligenceRun) -> NormalizedEvidenceBatch | None:
    return next((item for item in run.batches if item.provider_id == "yahoo"), None)


def _status(run: MarketIntelligenceRun) -> ProviderResultStatus:
    yahoo_audit = next((item for item in run.audits if item.provider_id == "yahoo"), None)
    return yahoo_audit.status if yahoo_audit is not None else ProviderResultStatus.UNAVAILABLE


def _recommendation_result_valid(run: MarketIntelligenceRun) -> bool:
    batch = _batch(run)
    return _status(run) in {
        ProviderResultStatus.SUCCESS,
        ProviderResultStatus.PARTIAL,
    } and (
        bool(batch is not None and batch.native_observations)
        or not any(failure.provider_id == "yahoo" for failure in run.failures)
    )


def _summary(spec: LiveCall, run: MarketIntelligenceRun) -> dict[str, Any]:
    batch = _batch(run)
    qualities = Counter(
        item.mapping_quality.value for item in (batch.normalization_records if batch else ())
    )
    return {
        "label": spec.label,
        "symbol": spec.symbol,
        "capability": spec.capability.value,
        "status": _status(run).value,
        "provider": "yahoo" if batch is not None else "-",
        "latency_seconds": round(run.usage.elapsed_seconds, 6),
        "normalization": (
            f"native={len(batch.native_observations)} "
            f"canonical={len(batch.canonical_evidence)} "
            f"events={len(batch.normalized_events)} gaps={len(batch.gaps)}"
            if batch is not None
            else "no normalized batch"
        ),
        "mapping_qualities": dict(sorted(qualities.items())),
        "run_fingerprint": run.fingerprint,
        "semantic_fingerprint": _semantic_fingerprint(batch) if batch else None,
        "failure_kinds": sorted({item.kind.value for item in run.failures}),
    }


def _provider_isolation_check() -> bool:
    root = Path(__file__).resolve().parents[1]
    specialist_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (root / "src/tiaf/agents/specialists").rglob("*.py")
    ).casefold()
    if any(term in specialist_source for term in ("tapetide", "yahoo", "import mcp")):
        return False
    for relative in (
        "src/tiaf/market_intelligence/models.py",
        "src/tiaf/market_intelligence/graph.py",
        "src/tiaf/market_intelligence/research.py",
    ):
        source = (root / relative).read_text(encoding="utf-8").casefold()
        if any(term in source for term in ("tapetide", "yahoo", "import mcp")):
            return False
    return True


def _semantic_checks(
    collected: list[tuple[LiveCall, MarketIntelligenceRun]],
    replay_matches: list[bool],
) -> dict[str, bool]:
    nonempty = [
        (spec, batch)
        for spec, run in collected
        if (batch := _batch(run)) is not None and batch.native_observations
    ]
    accepted_statuses = {
        ProviderResultStatus.SUCCESS,
        ProviderResultStatus.PARTIAL,
    }
    provider_provenance = all(
        item.provider_id == "yahoo" and item.source_reference is not None
        for _, batch in nonempty
        for item in batch.native_observations
    )
    canonical_identity = all(
        item.subject == spec.symbol and ".NS" not in item.subject
        for spec, batch in nonempty
        for item in batch.native_observations
    ) and all(
        event.primary_entity.canonical_symbol == spec.symbol
        for spec, batch in nonempty
        for event in batch.normalized_events
    )
    suffix_adapter_local = all(
        item.metadata.get("yahoo_ticker") == f"{spec.symbol}.NS"
        for spec, batch in nonempty
        for item in batch.native_observations
    )

    financial_batches = [
        batch
        for spec, run in collected
        if spec.capability is MarketIntelligenceCapability.READ_FINANCIALS
        and (batch := _batch(run)) is not None
    ]
    safe_financial_fields = {"total revenue", "net income"}
    uncertain_financials_protected = all(
        record.native_field.casefold() in safe_financial_fields
        or (
            record.mapping_quality
            in {
                SemanticMappingQuality.PROVIDER_DEFINED,
                SemanticMappingQuality.AMBIGUOUS,
            }
            and record.emitted_evidence_id is None
        )
        for batch in financial_batches
        for record in batch.normalization_records
    )

    earnings_batches = [
        batch
        for spec, run in collected
        if spec.capability is MarketIntelligenceCapability.READ_EARNINGS_CALENDAR
        and (batch := _batch(run)) is not None
    ]
    allowed_earnings_facts = {
        "earnings.date",
        "earnings.eps_estimate",
        "earnings.eps_reported",
        "earnings.surprise_percent",
    }
    earnings_safe = bool(earnings_batches) and all(
        event.structured_facts
        and {fact.field_id for fact in event.structured_facts} <= allowed_earnings_facts
        and "probability" not in event.model_dump_json().casefold()
        and "forecast" not in event.model_dump_json().casefold()
        for batch in earnings_batches
        for event in batch.normalized_events
    )

    news_batches = [
        batch
        for spec, run in collected
        if spec.capability is MarketIntelligenceCapability.READ_NEWS
        and (batch := _batch(run)) is not None
    ]
    news_safe = bool(news_batches) and all(
        event.normalized_title
        and event.source.publisher
        and event.source.source_reference
        and event.publication_time
        and event.acquisition_time
        and event.metadata.get("sentiment_available") is False
        and not event.structured_facts
        for batch in news_batches
        for event in batch.normalized_events
    )

    recommendation_runs = [
        run
        for spec, run in collected
        if spec.capability is MarketIntelligenceCapability.READ_ANALYST_FORECASTS
    ]
    empty_recommendations_valid = bool(recommendation_runs) and all(
        _recommendation_result_valid(run) for run in recommendation_runs
    )

    return {
        "all_scheduled_calls_accepted": len(collected) == len(CALLS)
        and all(_status(run) in accepted_statuses for _, run in collected),
        "all_profile_calls_success": all(
            _status(run) is ProviderResultStatus.SUCCESS
            for spec, run in collected
            if spec.capability is MarketIntelligenceCapability.READ_COMPANY_PROFILE
        ),
        "all_nonempty_calls_reached_canonical_evidence": all(
            batch.canonical_evidence or batch.normalized_events
            for spec, batch in nonempty
            if spec.capability
            is not MarketIntelligenceCapability.READ_ANALYST_FORECASTS
        ),
        "provider_provenance_preserved": provider_provenance,
        "canonical_symbols_provider_neutral": canonical_identity,
        "yahoo_suffixes_adapter_local": suffix_adapter_local,
        "uncertain_financial_semantics_protected": bool(financial_batches)
        and uncertain_financials_protected,
        "earnings_facts_preserved_without_probability": earnings_safe,
        "news_provenance_preserved_without_sentiment": news_safe,
        "empty_recommendations_not_failure": empty_recommendations_valid,
        "offline_replay_and_fingerprints_exact": len(replay_matches) == len(collected)
        and all(replay_matches),
        "provider_import_isolation": _provider_isolation_check(),
    }


def _rate_limited_tapetide_fixture() -> FixtureMarketIntelligenceProvider:
    capability = MarketIntelligenceCapability.READ_COMPANY_PROFILE
    declaration = ProviderCapabilityDeclaration(
        capability=capability,
        support=CapabilitySupport.FULL,
        constraints=ProviderCapabilityConstraints(
            output_types=(EvidenceOutputType.SECONDARY_STRUCTURED,),
            source_authority=SourceAuthority.TRUSTED_SECONDARY,
            point_in_time_quality=PointInTimeQuality.CONSERVATIVE,
            cost_units_per_call=0,
            normalizer_id="deterministic-rate-limit-fixture",
            normalizer_version="1.0",
            native_schema_version="fixture-1.0",
        ),
    )
    failure = ProviderFetchResult(
        provider_id="tapetide",
        capability=capability,
        status=ProviderResultStatus.RATE_LIMITED,
        failures=(
            ProviderFailure(
                kind=ProviderFailureKind.RATE_LIMIT,
                provider_id="tapetide",
                capability=capability,
                message="deterministic acceptance fixture: rate limited",
                retryable=True,
            ),
        ),
    )
    return FixtureMarketIntelligenceProvider(
        "tapetide",
        (declaration,),
        {(capability.value, "RELIANCE"): failure},
        source_authority=SourceAuthority.TRUSTED_SECONDARY,
    )


def _fallback_run(
    yahoo_provider: YahooMarketIntelligenceProvider,
) -> tuple[MarketIntelligenceRun, dict[str, Any]]:
    capability = MarketIntelligenceCapability.READ_COMPANY_PROFILE
    registry = MarketIntelligenceRegistry()
    primary = _rate_limited_tapetide_fixture()
    registry.register(primary, RuleBasedNormalizer("tapetide"))
    registry.register(yahoo_provider, yahoo_normalizer())
    request = _request(
        LiveCall("RELIANCE", capability),
        len(CALLS) + 1,
        required_metrics=("company.name",),
    )
    run = MarketIntelligenceRouter(registry).execute(
        request,
        yahoo_secondary_route_policy(
            capability,
            required_canonical_metrics=("company.name",),
        ),
        run_id="yahoo-live-deterministic-rate-limit-fallback",
    )
    proof: dict[str, Any] = {
        "primary_is_deterministic_fixture_not_live_tapetide": True,
        "audit_providers": [item.provider_id for item in run.audits],
        "audit_statuses": [item.status.value for item in run.audits],
        "latency_seconds": round(run.usage.elapsed_seconds, 6),
        "yahoo_selected": any(item.provider_id == "yahoo" for item in run.audits),
        "canonical_company_name_returned": any(
            item.metric == "company.name"
            for batch in run.batches
            for item in batch.canonical_evidence
        ),
    }
    proof["passed"] = (
        proof["audit_providers"] == ["tapetide", "yahoo"]
        and proof["audit_statuses"][0] == ProviderResultStatus.RATE_LIMITED.value
        and proof["yahoo_selected"] is True
        and proof["canonical_company_name_returned"] is True
    )
    return run, proof


def _print_table(summaries: list[dict[str, Any]], replay_matches: list[bool]) -> None:
    print(
        "symbol       capability                 status       provider latency  "
        "normalization                         fingerprint  replay"
    )
    print("-" * 132)
    for summary, replayed in zip(summaries, replay_matches, strict=True):
        print(
            f"{summary['symbol']:<12} {summary['capability']:<26} "
            f"{summary['status']:<12} {summary['provider']:<8} "
            f"{summary['latency_seconds']:>7.3f}s  "
            f"{summary['normalization']:<38} "
            f"{summary['run_fingerprint'][:10]}  {'YES' if replayed else 'NO'}"
        )


def main() -> int:
    args = _parser().parse_args()
    if not args.live:
        print("Live Yahoo calls are disabled. Re-run with --live to authorize 10 bounded calls.")
        return 0
    if shutil.which("uvx") is None:
        print(
            "Yahoo live acceptance not run: uvx is not installed. "
            "Install uv/uvx, verify `uvx --version`, then rerun with --live."
        )
        return 2

    client = YahooMcpClient()
    provider = YahooMarketIntelligenceProvider(client)
    registry = MarketIntelligenceRegistry()
    registry.register(provider, yahoo_normalizer())
    provider_registered = registry.provider("yahoo") is provider
    normalizer_registered = registry.normalizer("yahoo").provider_id == "yahoo"
    if not provider_registered or not normalizer_registered:
        print("Yahoo preflight failed: provider/normalizer registration is inconsistent.")
        return 2

    collected: list[tuple[LiveCall, MarketIntelligenceRun]] = []
    persisted: list[str] = []
    try:
        with client:
            for sequence, spec in enumerate(CALLS, start=1):
                request = _request(spec, sequence)
                run = MarketIntelligenceRouter(registry).execute(
                    request,
                    _yahoo_only_policy(spec.capability),
                    run_id=f"yahoo-live:{sequence:02d}:{spec.label}",
                )
                collected.append((spec, run))
                persisted.append(run.model_dump_json())
            fallback_run, fallback_proof = _fallback_run(provider)
            persisted.append(fallback_run.model_dump_json())
            server = {"name": client.server_name, "version": client.server_version}
    except YahooConnectorError as exc:
        print(f"Yahoo live connector failed safely: {exc}")
        return 2

    replay_matches: list[bool] = []
    replay_runs = [run for _, run in collected] + [fallback_run]
    with tempfile.TemporaryDirectory(prefix="tiaf-yahoo-replay-") as directory:
        replay_file = Path(directory) / "market_intelligence_runs.jsonl"
        replay_file.write_text("\n".join(persisted) + "\n", encoding="utf-8")
        for original, line in zip(replay_runs, replay_file.read_text().splitlines(), strict=True):
            replayed = MarketIntelligenceRun.model_validate_json(line)
            original_batch = _batch(original)
            replayed_batch = _batch(replayed)
            replay_matches.append(
                replayed == original
                and replayed.compute_fingerprint() == original.fingerprint
                and (
                    original_batch is None
                    or (
                        replayed_batch is not None
                        and replayed_batch.canonical_evidence == original_batch.canonical_evidence
                        and _semantic_fingerprint(replayed_batch)
                        == _semantic_fingerprint(original_batch)
                    )
                )
            )

    scheduled_replay = replay_matches[: len(collected)]
    summaries = [_summary(spec, run) for spec, run in collected]
    checks = _semantic_checks(collected, scheduled_replay)
    checks["fallback_rate_limited_to_yahoo"] = fallback_proof["passed"] is True
    checks["fallback_replay_exact"] = replay_matches[-1]
    elapsed = [float(item["latency_seconds"]) for item in summaries]
    elapsed.append(float(fallback_proof["latency_seconds"]))
    total_live_calls = sum(len(run.audits) for _, run in collected) + sum(
        audit.provider_id == "yahoo" for audit in fallback_run.audits
    )
    accepted = all(checks.values()) and total_live_calls == 10

    _print_table(summaries, scheduled_replay)
    print()
    print(
        json.dumps(
            {
                "accepted": accepted,
                "acceptance_timestamp": datetime.now(TIAF_TIMEZONE).isoformat(),
                "credentials_required": False,
                "server": server,
                "live_yahoo_calls": total_live_calls,
                "latency_seconds": {
                    "minimum": min(elapsed),
                    "median": median(elapsed),
                    "maximum": max(elapsed),
                    "total": round(sum(elapsed), 6),
                },
                "fallback": fallback_proof,
                "semantic_checks": checks,
                "secrets_printed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
