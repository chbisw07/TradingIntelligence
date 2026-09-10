"""Bounded synthetic/captured A3.10 acceptance cases; never live market data."""

import copy
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from _a3_8_fixtures import financial_services
from _a3_8_fixtures import request as a38_request
from _a3_9_cases import load_case

from tiaf.a3_hardening import CaptureOrigin, PortableA3ReplayPackage, capture_a3_package
from tiaf.planner.digests import digest, semantic
from tiaf.service.opportunity_intelligence import (
    assemble_opportunity_intelligence,
    capture_intelligence,
    default_policy,
    request_from_capture,
)
from tiaf.workflows import capture_json, default_registry, run_serial

NOW = datetime(2026, 9, 10, 12, tzinfo=ZoneInfo("Asia/Kolkata"))
BUILDER = "a3.10-public-fixtures/1.0"


@dataclass(frozen=True)
class AcceptanceCase:
    case_id: str
    name: str
    source_case: str
    strata: tuple[str, ...]
    expected_probe: str


CASES = (
    AcceptanceCase("A", "clean aligned", "aligned", ("aligned", "replay"), "ALIGNED"),
    AcceptanceCase(
        "B",
        "A2 NO_TRADE / A3 WATCH",
        "baseline_watch",
        ("NO_TRADE", "watch"),
        "BASELINE_NO_TRADE_WATCH",
    ),
    AcceptanceCase(
        "C",
        "constructive A2 / A3 WAIT",
        "poor_timing",
        ("timing", "restriction"),
        "A3_RESTRICTION_ADDED",
    ),
    AcceptanceCase(
        "D",
        "direction conflict (plus neutral-axis probe)",
        "conflict",
        ("conflict", "neutral-axis-probe"),
        "NEUTRAL_AXIS_NON_COMPARABLE",
    ),
    AcceptanceCase(
        "E",
        "sparse evidence",
        "sparse_kaynes",
        ("sparse", "insufficient"),
        "INSUFFICIENT_EVIDENCE",
    ),
    AcceptanceCase(
        "F",
        "primary rate-limit / fallback",
        "__fallback__",
        ("failure", "fallback", "market-intelligence"),
        "RATE_LIMITED_FALLBACK_CAPTURED",
    ),
    AcceptanceCase(
        "G",
        "optional specialist failure",
        "unknown_fno",
        ("optional-failure", "degradation"),
        "OPTIONAL_FAILURE_ISOLATED",
    ),
    AcceptanceCase(
        "H",
        "required Risk failure",
        "abstain",
        ("risk", "required", "insufficient"),
        "INSUFFICIENT_EVIDENCE",
    ),
    AcceptanceCase(
        "I",
        "budget exhaustion",
        "__budget__",
        ("budget", "held-accounting"),
        "BUDGET_EXHAUSTED_CAPTURED",
    ),
    AcceptanceCase("J", "replay tamper", "aligned", ("integrity", "tamper"), "TAMPER_REJECTED"),
    AcceptanceCase(
        "K",
        "policy mismatch",
        "aligned",
        ("policy", "comparison"),
        "POLICY_MISMATCH_REJECTED",
    ),
    AcceptanceCase(
        "L",
        "serial/LangGraph equivalents",
        "__parity__",
        ("serial", "langgraph", "parity"),
        "SEMANTIC_PARITY",
    ),
    AcceptanceCase(
        "M",
        "unknown provider cost",
        "__fallback__",
        ("cost", "unpriced"),
        "UNPRICED_NOT_ZERO",
    ),
    AcceptanceCase(
        "N",
        "no-LLM",
        "aligned",
        ("no-llm", "known-zero"),
        "NO_LLM_KNOWN_ZERO",
    ),
)


def _package_from_a38(a38: str, name: str) -> PortableA3ReplayPackage:
    request = request_from_capture(
        a38,
        request_id=f"a3.10-public:{name}",
        policy=default_policy(),
    )
    a39 = capture_intelligence(assemble_opportunity_intelligence(request))
    return capture_a3_package(
        a38,
        a39,
        origin=CaptureOrigin.SYNTHETIC,
        source_reference=f"synthetic:a3.10-public/{name}",
        fixture_builder_version=BUILDER,
        created_at=NOW,
    )


def package_for(case: AcceptanceCase) -> PortableA3ReplayPackage:
    if case.source_case == "__parity__":
        return parity_packages()[0]
    if case.source_case == "__fallback__":
        request = a38_request(financials=False)
        record = run_serial(
            request,
            default_registry(),
            financial_services(request, fallback=True),
        )
        return _package_from_a38(capture_json(record), "fallback")
    if case.source_case == "__budget__":
        request = a38_request(financials=False, calls=0)
        record = run_serial(request, default_registry(), financial_services(request))
        return _package_from_a38(capture_json(record), "budget")
    return _package_from_a38(load_case(case.source_case), case.source_case)


def parity_packages() -> tuple[PortableA3ReplayPackage, PortableA3ReplayPackage]:
    source = load_case("aligned")
    changed = copy.deepcopy(json.loads(source)["record"])
    changed["runtime_adapter"] = "langgraph-1.2.11"
    changed["completed_at"] = "2026-09-10T23:59:59+05:30"
    changed["result"]["usage"]["elapsed_seconds"] = 42
    payload: dict[str, Any] = {key: value for key, value in changed.items() if key != "fingerprint"}
    payload["artifacts"] = [
        {
            "artifact_id": item["artifact_id"],
            "kind": item["kind"],
            "content": semantic(json.loads(item["canonical_json"])),
        }
        for item in changed["artifacts"]
    ]
    changed["fingerprint"] = digest(semantic(payload))
    changed_capture = json.dumps({"record": changed, "checksum": digest(changed)}, sort_keys=True)
    return (
        _package_from_a38(source, "parity"),
        _package_from_a38(changed_capture, "parity"),
    )
