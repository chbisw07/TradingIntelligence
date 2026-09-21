"""Private artifact integrity and structural-only protected-year admission."""

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from tiaf.evaluation.forecast_retrospective_io import load_reviewed_dataset
from tiaf.forecasting.identity import canonical_json, semantic_fingerprint

ROOT = Path(__file__).resolve().parents[3]


def synthetic_files(directory: Path) -> dict[str, Any]:
    data = (
        b"date,open,high,low,close,volume\n"
        b"2024-12-31,100,101,99,100,1000\n"
        b"2025-01-01,SEALED,SEALED,SEALED,SEALED,SEALED\n"
        b"2025-01-02,SEALED,SEALED,SEALED,SEALED,SEALED\n"
    )
    files = {"reliance_daily_ohlcv.csv": hashlib.sha256(data).hexdigest()}
    (directory / "reliance_daily_ohlcv.csv").write_bytes(data)

    def write(name: str, body: dict[str, Any]) -> str:
        seal = semantic_fingerprint(body)
        content = canonical_json({**body, "fingerprint": seal}).encode()
        (directory / name).write_bytes(content)
        files[name] = hashlib.sha256(content).hexdigest()
        return seal

    source = write(
        "source_manifest.json",
        {
            "csv_sha256": files["reliance_daily_ohlcv.csv"],
            "csv_bytes": len(data),
            "acquisition_kind": "FRESH_HISTORICAL_DOWNLOAD",
            "subject": "RELIANCE",
            "provider": "dhan",
            "security_id": "2885",
            "acquired_at": "2026-09-21T12:00:00+05:30",
            "rights_evidence_status": "UNVERIFIED",
            "row_count": 3,
            "delivered_from": "2024-12-31",
            "delivered_to": "2025-01-02",
        },
    )
    identity = write(
        "security_identity.json",
        {
            "canonical_instrument": {
                "symbol": "RELIANCE",
                "exchange": "NSE",
                "segment": "NSE_EQUITY",
                "instrument_type": "EQUITY",
            },
            "provider_security_id": "2885",
            "master_observed_at": "2026-09-21T11:00:00+05:30",
        },
    )
    write(
        "provisioning_manifest.json",
        {
            "dataset_sha256": files["reliance_daily_ohlcv.csv"],
            "references": {
                name: {"file_sha256": files[name], "fingerprint": fp}
                for name, fp in (
                    ("source_manifest.json", source),
                    ("security_identity.json", identity),
                )
            },
        },
    )
    return {
        "expected_files": files,
        "expected_rows": 3,
        "identity": {"isin": "INE002A01018", "qualified": True},
        "adjustment": {"qualified": True, "basis": "CORPORATE_ACTION_ADJUSTED"},
        "action_review_qualified": True,
        "actions": [],
        "warnings": ["SYNTHETIC_IO_TEST_ONLY"],
        "calendar": {
            "start": "2024-12-31",
            "end": "2025-01-02",
            "closed_dates": [],
            "special_sessions": [],
            "source_urls": ["https://example.test/synthetic-calendar"],
            "reviewed_at": "2026-09-21T12:00:00+05:30",
            "qualified": True,
            "limitations": ["SYNTHETIC"],
        },
    }


def test_protected_prices_and_volume_are_not_even_numeric_parsed(tmp_path: Path) -> None:
    review = synthetic_files(tmp_path)
    dataset = load_reviewed_dataset(tmp_path, review)
    assert dataset.rows[0].bar is not None
    assert all(r.protected and r.bar is None for r in dataset.rows[1:])
    assert "SEALED" not in dataset.model_dump_json()
    assert dataset.acquired_at.year == 2026


def test_existing_data_cannot_change_under_pinned_provisioning(tmp_path: Path) -> None:
    review = synthetic_files(tmp_path)
    with (tmp_path / "reliance_daily_ohlcv.csv").open("ab") as handle:
        handle.write(b"\n")
    with pytest.raises(ValueError, match="PROVISIONING_BYTES_CHANGED"):
        load_reviewed_dataset(tmp_path, review)


def test_manifest_needs_both_bytes_and_semantic_identity(tmp_path: Path) -> None:
    review = synthetic_files(tmp_path)
    path = tmp_path / "source_manifest.json"
    body = json.loads(path.read_text())
    body["provider"] = "other"
    content = json.dumps(body).encode()
    path.write_bytes(content)
    review["expected_files"][path.name] = hashlib.sha256(content).hexdigest()
    with pytest.raises(ValueError, match="MANIFEST_SEAL_MISMATCH"):
        load_reviewed_dataset(tmp_path, review)


def test_unsealed_numeric_corruption_fails(tmp_path: Path) -> None:
    review = synthetic_files(tmp_path)
    # Integrity check rejects it before any empirical feature operation.
    path = tmp_path / "reliance_daily_ohlcv.csv"
    path.write_text(path.read_text().replace(",100,101,99,100,1000", ",INVALID,101,99,100,1000"))
    with pytest.raises(ValueError):
        load_reviewed_dataset(tmp_path, review)


def test_review_cannot_disagree_with_pinned_adjusted_basis(tmp_path: Path) -> None:
    review = synthetic_files(tmp_path)
    review["adjustment"]["basis"] = "UNADJUSTED"
    with pytest.raises(ValueError, match="SOURCE_CONTEXT_MISMATCH"):
        load_reviewed_dataset(tmp_path, review)


@pytest.mark.parametrize(
    "name",
    [
        "forecast_retrospective.py",
        "forecast_retrospective_io.py",
        "forecast_retrospective_contracts.py",
    ],
)
def test_new_research_path_has_no_provider_training_or_broker_imports(name: str) -> None:
    tree = ast.parse((ROOT / "src/tiaf/evaluation" / name).read_text())
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in {"fit", "fit_transform", "predict", "predict_proba"}
    assert not any(
        term in module
        for module in imports
        for term in ("providers", "sklearn", "httpx", "requests", "broker", "learning")
    )
