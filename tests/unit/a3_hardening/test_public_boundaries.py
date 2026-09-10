"""Public acceptance, corpus provenance, secrets and authority boundaries."""

import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "src/tiaf/a3_hardening"


def test_public_acceptance_covers_exactly_14_offline_scenarios() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/a3_10_user_acceptance.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "PASS: 14 / FAIL: 0" in completed.stdout
    assert "no live/provider/model calls" in completed.stdout
    for case_id in "ABCDEFGHIJKLMN":
        assert f'"case": "{case_id}"' in completed.stdout


def test_checked_in_manifest_matches_public_case_inventory() -> None:
    data = json.loads((ROOT / "tests/fixtures/a3_hardening/golden_manifest.json").read_text())
    assert data["origin"] == "SYNTHETIC"
    assert data["fixture_builder_version"]
    assert tuple(item["case_id"] for item in data["cases"]) == tuple("ABCDEFGHIJKLMN")


def test_hardening_runtime_has_no_provider_transport_or_framework_imports() -> None:
    forbidden_modules = (
        "httpx",
        "requests",
        "openai",
        "langgraph",
        "langsmith",
        "mcp",
        "tiaf.market_intelligence.providers",
        "tiaf.data.providers",
    )
    for path in SOURCE.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = tuple(
            node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        ) + tuple(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )
        assert not any(
            module == blocked or module.startswith(f"{blocked}.")
            for module in imports
            for blocked in forbidden_modules
        ), (path, imports)


def test_no_execution_or_recommendation_authority_contracts() -> None:
    contracts = (SOURCE / "contracts.py").read_text(encoding="utf-8").lower()
    forbidden_fields = (
        "strike_selection",
        "expiry_selection",
        "order_quantity",
        "stop_loss",
        "target_price",
        "win_probability",
        "profitability",
        "specialist_winner",
    )
    assert not any(term in contracts for term in forbidden_fields)


def test_package_contracts_and_fixtures_contain_no_secret_material() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for root in (SOURCE, ROOT / "tests/fixtures/a3_hardening")
        for path in root.rglob("*")
        if path.is_file() and path.suffix in {".py", ".json"}
    ).lower()
    forbidden = ("api_key=", "access_token=", "client_secret=", "authorization: bearer")
    assert not any(item in text for item in forbidden)
