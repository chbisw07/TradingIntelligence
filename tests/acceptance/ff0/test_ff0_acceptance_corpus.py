"""Execute the accepted 28-case evidence manifest; never reinterpret it as run data."""

import csv
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
with (HERE / "corpus_manifest.csv").open(newline="") as handle:
    CASES = tuple(csv.DictReader(handle))


@pytest.fixture(scope="module")
def executed_evidence(tmp_path_factory: pytest.TempPathFactory) -> set[str]:
    """One deduplicated, isolated unit-test batch shared by all semantic assertions."""
    plan = (ROOT / "docs/TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md").read_text()
    planned = re.findall(r"^\| (FF0-\d{2}) ([a-z-]+) \|", plan, flags=re.MULTILINE)
    assert len(CASES) == 28
    assert [(c["case_id"], c["requirement"]) for c in CASES] == planned
    selectors = sorted({node for c in CASES for node in c["tests"].split(";")})
    assert all(node.startswith("tests/unit/") and "::test_" in node for node in selectors)
    report = tmp_path_factory.mktemp("ff0-semantic-evidence") / "results.xml"
    process = subprocess.run(
        [sys.executable, "-B", "-m", "pytest", "-q", *selectors, f"--junitxml={report}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    results = ET.parse(report).findall(".//testcase")
    assert results and all(len(case) == 0 for case in results), "No skips/failures permitted"
    executed = {
        case.attrib["classname"].replace(".", "/") + ".py::" + case.attrib["name"].split("[")[0]
        for case in results
    }
    assert set(selectors) <= executed
    print(f"FF-0 evidence batch: {len(results)} passed; 28 named semantic cases")
    return executed


@pytest.mark.parametrize("case", CASES, ids=[c["case_id"] for c in CASES])
def test_ff0_semantic_case(case: dict[str, str], executed_evidence: set[str]) -> None:
    assert case["status"] == "SATISFIED"
    assert case["owning_submilestone"].startswith("FF-0.")
    assert case["evidence"]
    assert set(case["tests"].split(";")) <= executed_evidence
