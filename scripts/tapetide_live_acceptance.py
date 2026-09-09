"""Bounded, explicit live acceptance for the A3.6.1 Tapetide connector."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from statistics import median
from typing import Any

from tiaf.agents import AgentBudget
from tiaf.contracts import FreshnessState, Horizon
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.market_intelligence import (
    AvailabilityBasis,
    DerivationClass,
    MarketIntelligenceCapability,
    MarketIntelligenceRequest,
    NormalizedEvidenceBatch,
    ProviderResultStatus,
    authority_for,
    tapetide_normalizer,
)
from tiaf.market_intelligence.providers import (
    TapetideConnectorError,
    TapetideMarketIntelligenceProvider,
    TapetideMcpClient,
)


@dataclass(frozen=True, slots=True)
class LiveCall:
    symbol: str
    capability: MarketIntelligenceCapability
    section: str | None = None
    limit: int | None = None

    @property
    def label(self) -> str:
        suffix = f":{self.section}" if self.section else ""
        return f"{self.symbol}:{self.capability.value}{suffix}"


CALLS = (
    LiveCall("RELIANCE", MarketIntelligenceCapability.READ_COMPANY_PROFILE),
    LiveCall("RELIANCE", MarketIntelligenceCapability.READ_FINANCIALS, "profit_loss"),
    LiveCall("HDFCBANK", MarketIntelligenceCapability.READ_COMPANY_PROFILE),
    LiveCall("HDFCBANK", MarketIntelligenceCapability.READ_FINANCIALS, "profit_loss"),
    LiveCall("KAYNES", MarketIntelligenceCapability.READ_COMPANY_PROFILE),
    LiveCall("KAYNES", MarketIntelligenceCapability.READ_FINANCIALS, "profit_loss"),
    LiveCall("ATHERENERG", MarketIntelligenceCapability.READ_COMPANY_PROFILE),
    LiveCall("ATHERENERG", MarketIntelligenceCapability.READ_FINANCIALS, "profit_loss"),
    LiveCall("RELIANCE", MarketIntelligenceCapability.READ_FINANCIALS, "balance_sheet"),
    LiveCall("RELIANCE", MarketIntelligenceCapability.READ_FINANCIALS, "cash_flow"),
    LiveCall("KAYNES", MarketIntelligenceCapability.READ_FILINGS, limit=10),
    LiveCall("RELIANCE", MarketIntelligenceCapability.READ_SHAREHOLDING),
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="authorize the bounded 12-call live Tapetide acceptance",
    )
    return parser


def _request(spec: LiveCall, sequence: int) -> MarketIntelligenceRequest:
    authority = authority_for(spec.capability)
    attributes: dict[str, Any] = {}
    if spec.section is not None:
        attributes["section"] = spec.section
    if spec.limit is not None:
        attributes["limit"] = spec.limit
    return MarketIntelligenceRequest(
        request_id=f"tapetide-live-a361-{sequence:02d}",
        capability=spec.capability,
        authority=authority,
        allowed_authorities=(authority,),
        subject=spec.symbol,
        # Adapter acquisition is recorded at call start. This prevents request
        # construction latency from excluding acquisition-time evidence.
        as_of=datetime.now(TIAF_TIMEZONE) + timedelta(seconds=2),
        horizon=Horizon(label="POSITIONAL"),
        required_freshness=FreshnessState.UNKNOWN,
        budget=AgentBudget(
            max_tool_calls=1,
            max_cost_units=1,
            max_elapsed_seconds=45,
        ),
        attributes=attributes,
    )


def _fingerprint(batch: NormalizedEvidenceBatch) -> str:
    encoded = json.dumps(
        batch.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _summarize(
    spec: LiveCall,
    result_status: ProviderResultStatus,
    elapsed_seconds: float,
    batch: NormalizedEvidenceBatch,
) -> dict[str, Any]:
    qualities = Counter(record.mapping_quality.value for record in batch.normalization_records)
    gap_kinds = Counter(gap.kind.value for gap in batch.gaps)
    identity_values = {
        str(item.value).upper()
        for item in batch.native_observations
        if item.native_field.casefold() in {"symbol", "nse_symbol", "ticker"}
    }
    return {
        "label": spec.label,
        "symbol": spec.symbol,
        "capability": spec.capability.value,
        "section": spec.section,
        "status": result_status.value,
        "elapsed_seconds": round(elapsed_seconds, 6),
        "native_observations": len(batch.native_observations),
        "normalization_records": len(batch.normalization_records),
        "canonical_projections": len(batch.canonical_evidence),
        "mapping_qualities": dict(sorted(qualities.items())),
        "gap_kinds": dict(sorted(gap_kinds.items())),
        "source_references": sum(
            item.source_reference is not None for item in batch.native_observations
        ),
        "periods": sorted(
            {item.period_label for item in batch.native_observations if item.period_label}
        ),
        "availability_bases": sorted(
            {item.availability_basis.value for item in batch.native_observations}
        ),
        "point_in_time_qualities": sorted(
            {item.point_in_time_quality.value for item in batch.native_observations}
        ),
        "explicit_null_gaps": sum("returned no value" in item.message for item in batch.gaps),
        "identity_match": spec.symbol in identity_values if spec.section is None else None,
        "fingerprint": _fingerprint(batch),
    }


def _semantic_checks(
    batches: list[tuple[LiveCall, NormalizedEvidenceBatch]],
    replay_matches: list[bool],
) -> dict[str, bool]:
    reliance_records = [
        record
        for spec, batch in batches
        if spec.symbol == "RELIANCE"
        for record in batch.normalization_records
    ]
    unsafe_native = {"yearly_revenue", "sales", "borrowings"}
    reliance_ambiguity_safe = all(
        record.emitted_evidence_id is None
        for record in reliance_records
        if record.native_field.casefold() in unsafe_native
    )
    reliance_fcf_safe = all(
        record.emitted_evidence_id is None
        and record.derivation_class is DerivationClass.PROVIDER_DERIVED
        for record in reliance_records
        if record.native_field.casefold() in {"free cash flow", "fcf"}
    )
    hdfc_records = [
        record
        for spec, batch in batches
        if spec.symbol == "HDFCBANK"
        for record in batch.normalization_records
    ]
    hdfc_sector_safe = not any(
        record.emitted_evidence_id is not None
        and any(
            term in (record.canonical_metric or "").casefold()
            for term in ("ebitda", "debt")
        )
        for record in hdfc_records
    )
    ather_batches = [batch for spec, batch in batches if spec.symbol == "ATHERENERG"]
    kaynes_batches = [batch for spec, batch in batches if spec.symbol == "KAYNES"]
    filings = [
        batch
        for spec, batch in batches
        if spec.capability is MarketIntelligenceCapability.READ_FILINGS
    ]
    ownership = [
        batch
        for spec, batch in batches
        if spec.capability is MarketIntelligenceCapability.READ_SHAREHOLDING
    ]
    pit_financial = any(
        item.availability_basis is not AvailabilityBasis.ACQUISITION_TIME
        for spec, batch in batches
        if spec.capability is MarketIntelligenceCapability.READ_FINANCIALS
        for item in batch.native_observations
    )
    return {
        "all_calls_produced_native_observations": all(
            batch.native_observations for _, batch in batches
        ),
        "all_native_observations_were_normalized": all(
            len(batch.native_observations) == len(batch.normalization_records)
            for _, batch in batches
        ),
        "reliance_unsafe_promotions_blocked": reliance_ambiguity_safe,
        "reliance_provider_derived_fcf_protected": reliance_fcf_safe,
        "hdfcbank_industrial_leverage_not_fabricated": hdfc_sector_safe,
        "atherenerg_sparse_response_processed": bool(ather_batches)
        and all(batch.native_observations for batch in ather_batches),
        "kaynes_profile_financial_and_filings_processed": bool(kaynes_batches)
        and all(batch.native_observations for batch in kaynes_batches)
        and bool(filings),
        "filings_event_path_processed": bool(filings and filings[0].native_observations),
        "ownership_path_processed": bool(ownership and ownership[0].native_observations),
        "financial_point_in_time_record_preserved": pit_financial,
        "offline_replay_exact": all(replay_matches),
    }


def main() -> int:
    args = _parser().parse_args()
    if not args.live:
        raise SystemExit("Refusing live provider calls without explicit --live")
    client = TapetideMcpClient.from_environment()
    provider = TapetideMarketIntelligenceProvider(client)
    normalizer = tapetide_normalizer()
    collected: list[tuple[LiveCall, NormalizedEvidenceBatch]] = []
    summaries: list[dict[str, Any]] = []
    persisted: list[str] = []
    try:
        with client:
            for sequence, spec in enumerate(CALLS, start=1):
                request = _request(spec, sequence)
                result = provider.fetch(request)
                if result.status not in {
                    ProviderResultStatus.SUCCESS,
                    ProviderResultStatus.PARTIAL,
                }:
                    failure_kinds = ",".join(
                        sorted({item.kind.value for item in result.failures})
                    )
                    raise SystemExit(
                        f"{spec.label} failed with typed status "
                        f"{result.status.value} ({failure_kinds})"
                    )
                batch = normalizer.normalize(request, result)
                collected.append((spec, batch))
                summaries.append(
                    _summarize(spec, result.status, result.elapsed_seconds, batch)
                )
                persisted.append(batch.model_dump_json())
            server = {"name": client.server_name, "version": client.server_version}
    except TapetideConnectorError as exc:
        raise SystemExit(f"Tapetide live connector failed: {exc}") from None

    replay_matches: list[bool] = []
    with tempfile.TemporaryDirectory(prefix="tiaf-tapetide-replay-") as directory:
        replay_file = Path(directory) / "normalized_batches.jsonl"
        replay_file.write_text("\n".join(persisted) + "\n", encoding="utf-8")
        originals = (batch for _, batch in collected)
        for original, line in zip(originals, replay_file.read_text().splitlines()):
            replayed = NormalizedEvidenceBatch.model_validate_json(line)
            replay_matches.append(
                replayed.model_dump(mode="json") == original.model_dump(mode="json")
                and _fingerprint(replayed) == _fingerprint(original)
            )

    checks = _semantic_checks(collected, replay_matches)
    elapsed = [summary["elapsed_seconds"] for summary in summaries]
    report = {
        "server": server,
        "live_calls": len(summaries),
        "latency_seconds": {
            "minimum": min(elapsed),
            "median": median(elapsed),
            "maximum": max(elapsed),
            "total": round(sum(elapsed), 6),
        },
        "calls": summaries,
        "semantic_checks": checks,
        "accepted": all(checks.values()),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
