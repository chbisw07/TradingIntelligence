"""INTERNAL engineering/research provisioner; not production ingestion or a public capability.

One explicit --live invocation, one TI-native Dhan daily-history request. No
automatic retries, master refresh, quotes, features, labels or learned fitting.
"""

import argparse
import csv
import io
import math
import os
import re
import subprocess
from collections.abc import Callable
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from tiaf.a3_hardening.package import exact_bytes_checksum
from tiaf.config import Settings
from tiaf.contracts import DataQuality
from tiaf.data import InstrumentKey, InstrumentType, MarketSegment, TIAFDataError
from tiaf.data.models import HistoricalSeries, OHLCVBar
from tiaf.data.normalization import TIAF_TIMEZONE, normalize_datetime_to_ist
from tiaf.data.provider import MarketDataProvider
from tiaf.data.providers.dhan import DhanConfig, DhanInstrumentResolver, DhanMarketDataProvider
from tiaf.data.providers.dhan.instrument_master import DhanInstrumentMaster
from tiaf.data.providers.dhan.transport import HttpxDhanTransport
from tiaf.data.resolution import InstrumentQuery, ResolutionKind, ResolutionResult
from tiaf.data.resolution.resolver import InstrumentResolver
from tiaf.evaluation.forecast_research_contracts import (
    ResearchRightsConfig,
    RightsAdmissionResult,
    RightsEvidenceStatus,
    rights_admission,
)
from tiaf.evaluation.snapshot import validate_no_secrets
from tiaf.forecasting.identity import canonical_json, semantic_fingerprint

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "data/ff1/reliance"
START = datetime(2017, 11, 1, tzinfo=TIAF_TIMEZONE)
END = datetime(2026, 2, 1, tzinfo=TIAF_TIMEZONE)  # Exclusive: includes January 31.
HEADER = ("date", "open", "high", "low", "close", "volume")
CLASSIFICATION = "ENGINEERING_RESEARCH_SUPPORT_ONLY"
QUERY = InstrumentQuery(
    symbol="RELIANCE",
    exchange="NSE",
    segment=MarketSegment.NSE_EQUITY,
    instrument_type=InstrumentType.EQUITY,
    provider="DHAN",
)


class ProvisioningError(ValueError):
    """Closed, secret-free transport/provisioning failure code."""


def now() -> datetime:
    return datetime.now(TIAF_TIMEZONE)


def check_destination(destination: Path, root: Path) -> None:
    if not destination.is_absolute() or destination != root / "data/ff1/reliance":
        raise ProvisioningError("OUTPUT_OUTSIDE_FIXED_LOCAL_DATA_PATH")
    if any(p.is_symlink() for p in (destination, *destination.parents)):
        raise ProvisioningError("OUTPUT_SYMLINK_DENIED")
    if destination.exists():
        raise ProvisioningError("OUTPUT_ALREADY_EXISTS_NO_OVERWRITE")


def resolve_identity(resolver: InstrumentResolver) -> ResolutionResult:
    return checked_resolution(resolver.resolve(QUERY))


def checked_resolution(result: ResolutionResult) -> ResolutionResult:
    match = result.resolved
    if result.ambiguous or result.not_found or match is None or len(result.matches) != 1:
        raise ProvisioningError("RESOLUTION_NOT_UNIQUE")
    instrument = match.instrument
    if (
        result.query != QUERY
        or result.matches[0] != match
        or result.source_provider != "dhan"
        or match.provider_name != "dhan"
        or match.quality is not DataQuality.GOOD
        or match.resolution_kind is not ResolutionKind.UNIQUE_NORMALIZED
        or instrument.symbol != "RELIANCE"
        or instrument.exchange != "NSE"
        or instrument.segment is not MarketSegment.NSE_EQUITY
        or instrument.instrument_type is not InstrumentType.EQUITY
        or any(
            v is not None for v in (instrument.expiry, instrument.strike, instrument.option_type)
        )
        or instrument.provider_instrument_id != match.provider_instrument_id
        or not match.provider_instrument_id.isdecimal()
    ):
        raise ProvisioningError("RESOLUTION_WRONG_SCOPE_OR_PROVIDER_ID")
    return result


def canonical_csv(series: tuple[HistoricalSeries, ...], instrument: InstrumentKey) -> str:
    """Merge normalized native chunks deterministically, rejecting every duplicate.

    Dates use the existing Dhan parser's IST daily calendar boundaries. They do
    not certify a historical exchange session calendar or per-bar availability.
    """
    bars: list[OHLCVBar] = []
    for item in series:
        if item.instrument != instrument or item.interval != "1d" or item.source_provider != "dhan":
            raise ProvisioningError("SERIES_IDENTITY_OR_FREQUENCY_MISMATCH")
        for bar in item.bars:
            if (
                bar.instrument != instrument
                or bar.interval != "1d"
                or bar.source_provider != "dhan"
            ):
                raise ProvisioningError("BAR_IDENTITY_OR_FREQUENCY_MISMATCH")
            start = normalize_datetime_to_ist(bar.start_at)
            if not START <= start < END:
                raise ProvisioningError("BAR_OUTSIDE_AUTHORIZED_WINDOW")
            if start.time() != time.min or bar.end_at != start + timedelta(days=1):
                raise ProvisioningError("NOT_NORMALIZED_DAILY_BOUNDARIES")
            prices = (bar.open, bar.high, bar.low, bar.close)
            if any(isinstance(v, bool) or not math.isfinite(v) or v <= 0 for v in prices):
                raise ProvisioningError("INVALID_OHLC_NONFINITE_OR_NONPOSITIVE")
            if not bar.low <= min(bar.open, bar.close) <= max(bar.open, bar.close) <= bar.high:
                raise ProvisioningError("INVALID_OHLC_ENVELOPE")
            if type(bar.volume) is not int or not 0 <= bar.volume <= 2**63 - 1:
                raise ProvisioningError("INVALID_VOLUME")
            bars.append(bar)
    if not bars:
        raise ProvisioningError("EMPTY_HISTORICAL_RESPONSE")
    dates = [b.start_at.astimezone(TIAF_TIMEZONE).date() for b in bars]
    if len(dates) != len(set(dates)):
        raise ProvisioningError("DUPLICATE_DAILY_SESSION")
    # Defend against trusted model_copy/model_construct bypasses after explicit checks.
    for item in series:
        HistoricalSeries.model_validate(item.model_dump(mode="python"))
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(HEADER)
    for bar in sorted(bars, key=lambda b: b.start_at):
        writer.writerow(
            (
                normalize_datetime_to_ist(bar.start_at).date().isoformat(),
                bar.open,
                bar.high,
                bar.low,
                bar.close,
                bar.volume,
            )
        )
    return output.getvalue()


def seal(payload: dict[str, Any]) -> dict[str, Any]:
    validate_no_secrets(payload)
    return {**payload, "fingerprint": semantic_fingerprint(payload)}


def _write_new(path: Path, text: str) -> None:
    # Exact UTF-8 bytes, exclusive creation and private local market-data permissions.
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as stream:
        stream.write(text.encode("utf-8"))


def provision(
    provider: MarketDataProvider,
    resolution: ResolutionResult,
    *,
    root: Path,
    master_sha256: str,
    resolved_at: datetime,
    clock: Callable[[], datetime] = now,
    rights_config: ResearchRightsConfig = ResearchRightsConfig(),
) -> dict[str, Any]:
    """One bounded request through the existing neutral provider protocol."""
    destination = root / "data/ff1/reliance"
    check_destination(destination, root)
    resolution = checked_resolution(resolution)
    if provider.provider_name() != "dhan" or resolution.resolved is None:
        raise ProvisioningError("PROVIDER_OR_IDENTITY_MISSING")
    policy = ResearchRightsConfig.model_validate(rights_config.model_dump())
    admission, warnings = rights_admission(
        RightsEvidenceStatus.UNVERIFIED, policy.rights_enforcement_policy
    )
    if admission is RightsAdmissionResult.HOLD:
        raise ProvisioningError("RIGHTS_POLICY_HOLD")
    match = resolution.resolved
    instrument = match.instrument
    started = normalize_datetime_to_ist(clock())
    print(f"Historical request: RELIANCE / NSE / EQUITY / ID {match.provider_instrument_id}")
    print(f"Acquisition start: {started.isoformat()}; one request, no retries")
    series = provider.get_historical(instrument, "1d", START, END)
    finished = normalize_datetime_to_ist(clock())
    print(f"Acquisition end: {finished.isoformat()}; response received")
    if finished < started:
        raise ProvisioningError("ACQUISITION_CLOCK_REVERSED")
    content = canonical_csv((series,), instrument)
    rows = list(csv.DictReader(io.StringIO(content)))
    rights = {
        "rights_evidence_status": RightsEvidenceStatus.UNVERIFIED.value,
        "rights_enforcement_policy": policy.rights_enforcement_policy.value,
        "rights_admission_result": admission.value,
        "rights_warnings": warnings,
        "rights_configuration_fingerprint": policy.fingerprint,
    }
    identity = seal(
        {
            "schema_id": "tiaf.ff1.testdata.security",
            "schema_version": "1.0",
            "canonical_symbol": instrument.symbol,
            "exchange": instrument.exchange,
            "segment": instrument.segment.value,
            "instrument_type": instrument.instrument_type.value,
            "canonical_instrument": instrument.model_dump(mode="json"),
            "provider_security_id": match.provider_instrument_id,
            "resolver_source": "tiaf.data.providers.dhan.DhanInstrumentResolver",
            "resolver_version": "TIAF_PACKAGE_0.1.0",
            "master_sha256": master_sha256,
            "resolved_at": normalize_datetime_to_ist(resolved_at),
            "master_observed_at": match.source_observed_at,
            "master_clock_semantics": "LOCAL_CACHE_MTIME_NOT_HISTORICAL_CAPTURE_PROOF",
            "historical_identity_qualification": "NOT_PERFORMED",
        }
    )
    request = seal(
        {
            "schema_id": "tiaf.ff1.testdata.request",
            "schema_version": "1.0",
            "provider": "dhan",
            "instrument": instrument.model_dump(mode="json"),
            "interval": "1d",
            "from": START,
            "to_exclusive": END,
            "requested_through_inclusive": "2026-01-31",
            "provider_method": "MarketDataProvider.get_historical",
            "adapter": "DhanMarketDataProvider",
            "endpoint": "/v2/charts/historical",
            "chunking_policy": "SINGLE_BOUNDED_DAILY_REQUEST_NO_AUTOMATIC_RETRY",
            "request_count": 1,
            "acquisition_start": started,
            "acquisition_end": finished,
            "chunks": [
                {
                    "from": START,
                    "to_exclusive": END,
                    "started_at": started,
                    "finished_at": finished,
                    "status": "NORMALIZED_RESPONSE_ACCEPTED",
                    "rows": len(rows),
                    "normalized_series_fingerprint": semantic_fingerprint(series),
                }
            ],
        }
    )
    source = seal(
        {
            "schema_id": "tiaf.ff1.testdata.source",
            "schema_version": "1.0",
            "classification": CLASSIFICATION,
            "provider": "dhan",
            "source_system": "TI_NATIVE_DHAN",
            "acquisition_kind": "FRESH_HISTORICAL_DOWNLOAD",
            "acquired_at": finished,
            "requested_from": START.date().isoformat(),
            "requested_to": "2026-01-31",
            "requested_to_semantics": "INCLUSIVE_DATE; API_BOUNDARY_2026-02-01_EXCLUSIVE",
            "delivered_from": rows[0]["date"],
            "delivered_to": rows[-1]["date"],
            "frequency": "1d",
            "timezone": "Asia/Kolkata",
            "row_count": len(rows),
            "csv_bytes": len(content.encode("utf-8")),
            "csv_sha256": exact_bytes_checksum(content),
            "subject": instrument.symbol,
            "exchange": instrument.exchange,
            "segment": instrument.segment.value,
            "instrument_type": instrument.instrument_type.value,
            "security_id": match.provider_instrument_id,
            "price_basis": "UNKNOWN",
            "corporate_action_evidence": "UNKNOWN",
            "calendar_qualification": "NOT_PERFORMED",
            "historical_availability_semantics": "UNKNOWN",
            "later_forecasts": "SIMULATED_ONLY",
            "normalization_performed": [
                "EXISTING_TI_DHAN_IST_DAILY_BOUNDARIES",
                "ASCENDING_DATE_CANONICAL_CSV_COLUMN_ORDER",
            ],
            "numeric_representation": "EXISTING_A1_FLOAT_OHLC_INT_VOLUME_NO_LOCAL_ROUNDING",
            "source_decimal_precision": "NOT_CERTIFIED_BY_FLOAT_NORMALIZATION",
            "raw_response_retained": False,
            "normalized_series_fingerprint": semantic_fingerprint(series),
            "duplicate_sessions": 0,
            "transport_validation": "PASS",
            **rights,
        }
    )
    companions = {
        "source_manifest.json": source,
        "security_identity.json": identity,
        "acquisition_request.json": request,
    }
    encoded = {name: canonical_json(value) + "\n" for name, value in companions.items()}
    manifest = seal(
        {
            "schema_id": "tiaf.ff1.testdata.provisioning",
            "schema_version": "1.0",
            "classification": CLASSIFICATION,
            "production_runtime": False,
            "public_capability": False,
            "final_data_architecture": False,
            "empirical_fitting_authorized": False,
            "dataset_path": "reliance_daily_ohlcv.csv",
            "dataset_sha256": source["csv_sha256"],
            "references": {
                name: {
                    "path": name,
                    "fingerprint": value["fingerprint"],
                    "file_sha256": exact_bytes_checksum(encoded[name]),
                }
                for name, value in companions.items()
            },
            "price_basis": "UNKNOWN",
            "pit_status": "UNKNOWN",
            "raw_data_git_policy": "IGNORED_LOCAL_DATA_NEVER_STAGE",
            **rights,
        }
    )
    # All transport and manifest validation completes before any final file is written.
    check_destination(destination, root)
    destination.mkdir(parents=True, mode=0o700)
    _write_new(destination / "reliance_daily_ohlcv.csv", content)
    for name, text in encoded.items():
        _write_new(destination / name, text)
    # Success marker last; partial filesystem failures never acquire this manifest.
    _write_new(destination / "provisioning_manifest.json", canonical_json(manifest) + "\n")
    verify_package(destination)
    return manifest


def verify_package(destination: Path) -> None:
    """Offline byte/semantic identity checks, no provider call or qualification."""
    import json

    manifest = json.loads((destination / "provisioning_manifest.json").read_bytes())
    payload = {k: v for k, v in manifest.items() if k != "fingerprint"}
    if semantic_fingerprint(payload) != manifest["fingerprint"]:
        raise ProvisioningError("PROVISIONING_FINGERPRINT_MISMATCH")
    if manifest["dataset_path"] != "reliance_daily_ohlcv.csv":
        raise ProvisioningError("UNEXPECTED_DATASET_PATH")
    if set(manifest["references"]) != {
        "source_manifest.json",
        "security_identity.json",
        "acquisition_request.json",
    }:
        raise ProvisioningError("UNEXPECTED_MANIFEST_REFERENCE")
    for name, ref in manifest["references"].items():
        text = (destination / name).read_bytes().decode("utf-8")
        doc = json.loads(text)
        validate_no_secrets(doc)
        if (
            ref["path"] != name
            or exact_bytes_checksum(text) != ref["file_sha256"]
            or doc["fingerprint"] != ref["fingerprint"]
            or semantic_fingerprint({k: v for k, v in doc.items() if k != "fingerprint"})
            != ref["fingerprint"]
        ):
            raise ProvisioningError("COMPANION_FINGERPRINT_MISMATCH")
    csv_text = (destination / "reliance_daily_ohlcv.csv").read_bytes().decode("utf-8")
    if exact_bytes_checksum(csv_text) != manifest["dataset_sha256"]:
        raise ProvisioningError("CSV_FINGERPRINT_MISMATCH")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live", action="store_true", help="authorize the fixed research acquisition"
    )
    args = parser.parse_args(argv)
    if not args.live:
        print(
            "Live acquisition disabled. No external calls; use --live for the fixed RELIANCE scope."
        )
        return 0
    transport: HttpxDhanTransport | None = None
    try:
        check_destination(DESTINATION, ROOT)
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", str(DESTINATION / "reliance_daily_ohlcv.csv")],
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
        if ignored.returncode != 0:
            raise ProvisioningError("LOCAL_DATA_PATH_NOT_GIT_IGNORED")
        settings = Settings()
        if settings.dhan_client_id is None:
            raise ProvisioningError("MISSING_DHAN_CLIENT_ID")
        if settings.dhan_access_token is None:
            raise ProvisioningError("MISSING_DHAN_ACCESS_TOKEN")
        config = DhanConfig.from_settings(settings)
        if str(config.base_url).rstrip("/") != "https://api.dhan.co/v2":
            raise ProvisioningError("NONCANONICAL_DHAN_ENDPOINT_DENIED")
        master = DhanInstrumentMaster()
        if not master.cache_path.is_file() or master.cache_path.is_symlink():
            raise ProvisioningError("LOCAL_MASTER_REQUIRED_NO_AUTOMATIC_DOWNLOAD")
        master_hash = exact_bytes_checksum(master.cache_path.read_bytes().decode("utf-8"))
        resolution = resolve_identity(DhanInstrumentResolver(master, settings=settings))
        resolved_at = now()
        transport = HttpxDhanTransport(config)
        provider = DhanMarketDataProvider(config, transport=transport)
        result = provision(
            provider, resolution, root=ROOT, master_sha256=master_hash, resolved_at=resolved_at
        )
    except (TIAFDataError, ValidationError, ValueError, OSError) as exc:
        # Never echo settings, HTTP response text, credentials, or arbitrary provider errors.
        detail = str(exc) if isinstance(exc, ProvisioningError) else type(exc).__name__
        if isinstance(exc, TIAFDataError):
            codes = re.findall(r"\bDH-\d{3}\b", exc.detail)
            detail += " " + " ".join(sorted(set(codes)))
        print(f"HOLD_RELIANCE_TEST_DATA_PROVISIONING: {detail}")
        print(f"Stopped at: {now().isoformat()}; no automatic retry")
        print("EMPIRICAL_FITTING_AUTHORIZED = NO")
        return 2
    finally:
        if transport is not None:
            transport.close()
    print("RELIANCE_TEST_DATA_PROVISIONED")
    print(f"Output: {DESTINATION}")
    print(f"CSV SHA-256: {result['dataset_sha256']}")
    print(f"Provisioning fingerprint: {result['fingerprint']}")
    print("EMPIRICAL_FITTING_AUTHORIZED = NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
