"""Local artifact admission and holdout-redacting reader; no provider dependencies."""

import csv
import hashlib
import io
import json
from datetime import date
from pathlib import Path
from typing import Any

from tiaf.evaluation.forecast_retrospective_contracts import (
    ResearchCalendar,
    RetrospectiveDataset,
    RetrospectiveRow,
)
from tiaf.forecasting.identity import semantic_fingerprint


def load_reviewed_dataset(directory: Path, review: dict[str, Any]) -> RetrospectiveDataset:
    """Trusted bootstrap supplies reviewed evidence, not arbitrary request policy.

    Whole-file hashes are structural integrity checks. Protected numeric fields
    are never parsed, normalized, summarized or projected in this pass.
    """
    files: dict[str, bytes] = {}
    for name, expected in review["expected_files"].items():
        if Path(name).name != name:
            raise ValueError("UNSAFE_ARTIFACT_NAME")
        content = (directory / name).read_bytes()
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError("PROVISIONING_BYTES_CHANGED")
        files[name] = content
    manifests: dict[str, Any] = {}
    for name, content in files.items():
        if name.endswith(".json"):
            item = json.loads(content)
            fingerprint = item.pop("fingerprint")
            if semantic_fingerprint(item) != fingerprint:
                raise ValueError("MANIFEST_SEAL_MISMATCH")
            manifests[name] = {**item, "fingerprint": fingerprint}
    source, identity = manifests["source_manifest.json"], manifests["security_identity.json"]
    provisioning = manifests["provisioning_manifest.json"]
    for name, ref in provisioning["references"].items():
        if (
            ref["file_sha256"] != review["expected_files"][name]
            or ref["fingerprint"] != manifests[name]["fingerprint"]
        ):
            raise ValueError("MANIFEST_REFERENCE_MISMATCH")
    if (
        source["csv_sha256"] != review["expected_files"]["reliance_daily_ohlcv.csv"]
        or provisioning["dataset_sha256"] != source["csv_sha256"]
        or source["csv_bytes"] != len(files["reliance_daily_ohlcv.csv"])
        or source["acquisition_kind"] != "FRESH_HISTORICAL_DOWNLOAD"
        or source["subject"] != "RELIANCE"
        or source["provider"] != "dhan"
        or source["security_id"] != identity["provider_security_id"]
        or review["identity"]["isin"] != "INE002A01018"
        or review["adjustment"]["basis"] != "CORPORATE_ACTION_ADJUSTED"
    ):
        raise ValueError("SOURCE_CONTEXT_MISMATCH")
    calendar = ResearchCalendar.model_validate(review["calendar"])
    sessions = {d: (opens, closes) for d, opens, closes in calendar.sessions()}
    raw_rows = tuple(csv.DictReader(io.StringIO(files["reliance_daily_ohlcv.csv"].decode("utf-8"))))
    if len(raw_rows) != review["expected_rows"] or len(raw_rows) != source["row_count"]:
        raise ValueError("ROW_COUNT_MISMATCH")
    dates = tuple(date.fromisoformat(row["date"]) for row in raw_rows)
    if (
        dates != tuple(sorted(set(dates)))
        or dates[0].isoformat() != source["delivered_from"]
        or dates[-1].isoformat() != source["delivered_to"]
    ):
        raise ValueError("DATASET_CHRONOLOGY_OR_COVERAGE")
    rows = []
    for day, row in zip(dates, raw_rows, strict=True):
        if day not in sessions:
            raise ValueError("UNEXPLAINED_NON_SESSION_ROW")
        if day.year >= 2025:
            rows.append(RetrospectiveRow(session_date=day, protected=True, bar=None))
            continue
        opens, closes = sessions[day]
        rows.append(
            RetrospectiveRow.model_validate(
                {
                    "session_date": day,
                    "protected": False,
                    "bar": {
                        "instrument": identity["canonical_instrument"],
                        "interval": "1d",
                        "start_at": opens,
                        "end_at": closes,
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": int(row["volume"]),
                        "source_provider": source["provider"],
                    },
                }
            )
        )
    return RetrospectiveDataset.model_validate(
        {
            "dataset_id": "ff1.reliance.dhan.adjusted.20260921",
            "dataset_sha256": source["csv_sha256"],
            "source_manifest_fingerprint": source["fingerprint"],
            "acquired_at": source["acquired_at"],
            "resolved": {
                "instrument": identity["canonical_instrument"],
                "provider_name": source["provider"],
                "provider_instrument_id": identity["provider_security_id"],
                "source_record_id": "provisioned-identity:" + identity["fingerprint"],
                "source_observed_at": identity["master_observed_at"],
                "resolution_kind": "EXACT",
                "quality": "GOOD",
            },
            "rights_status": source["rights_evidence_status"],
            "rights_basis_fingerprint": semantic_fingerprint((source, provisioning)),
            "identity_qualified": review["identity"]["qualified"],
            "identity_evidence_fingerprint": semantic_fingerprint((identity, review["identity"])),
            "adjustment_qualified": review["adjustment"]["qualified"],
            "adjustment_evidence_fingerprint": semantic_fingerprint(review["adjustment"]),
            "action_review_qualified": review["action_review_qualified"],
            "actions": review["actions"],
            "calendar": calendar,
            "rows": rows,
            "warnings": review["warnings"],
        }
    )
