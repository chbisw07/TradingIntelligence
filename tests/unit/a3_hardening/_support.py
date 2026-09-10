"""Persisted and explicitly synthetic A3.10 test package builders."""

import copy
import json
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from scripts._a3_8_fixtures import financial_services
from scripts._a3_8_fixtures import request as a38_request
from scripts._a3_9_cases import load_case

from tiaf.a3_hardening import CaptureOrigin, PortableA3ReplayPackage, capture_a3_package
from tiaf.evaluation import CapturedBaselineCase, case_json
from tiaf.planner.digests import digest, semantic
from tiaf.service.opportunity_intelligence import (
    assemble_opportunity_intelligence,
    capture_intelligence,
    default_policy,
    request_from_capture,
)
from tiaf.workflows import capture_json, default_registry, run_serial
from tiaf.workflows.ledger import reserved_usage
from tiaf.workflows.records import OrchestrationRunRecord
from tiaf.workflows.replay import replay_recorded

from ..evaluation._support import frozen_case

NOW = datetime(2026, 9, 10, 12, tzinfo=ZoneInfo("Asia/Kolkata"))
BUILDER = "a3.10-test-fixtures/1.0"


def reseal_a38(data: dict[str, Any]) -> str:
    payload = {key: value for key, value in data.items() if key != "fingerprint"}
    payload["artifacts"] = [
        {
            "artifact_id": item["artifact_id"],
            "kind": item["kind"],
            "content": semantic(json.loads(item["canonical_json"])),
        }
        for item in data["artifacts"]
    ]
    data["fingerprint"] = digest(semantic(payload))
    return json.dumps({"record": data, "checksum": digest(data)}, sort_keys=True)


def package_for(name: str = "aligned") -> PortableA3ReplayPackage:
    return package_from_a38(load_case(name), name)


def package_from_a38(a38: str, name: str) -> PortableA3ReplayPackage:
    request = request_from_capture(
        a38,
        request_id=f"a3.10:{name}",
        policy=default_policy(),
    )
    a39 = capture_intelligence(assemble_opportunity_intelligence(request))
    return capture_a3_package(
        a38,
        a39,
        origin=CaptureOrigin.SYNTHETIC,
        source_reference=f"synthetic:a3.10/{name}",
        fixture_builder_version=BUILDER,
        created_at=NOW,
    )


def fallback_package() -> PortableA3ReplayPackage:
    request = a38_request(financials=False)
    a38 = capture_json(
        run_serial(request, default_registry(), financial_services(request, fallback=True))
    )
    return package_from_a38(a38, "fallback")


def budget_exhausted_package() -> PortableA3ReplayPackage:
    request = a38_request(financials=False, calls=0)
    a38 = capture_json(run_serial(request, default_registry(), financial_services(request)))
    return package_from_a38(a38, "budget-exhausted")


def held_reservation_package() -> PortableA3ReplayPackage:
    source = replay_recorded(load_case("aligned"))
    held = source.reservations[0].model_copy(
        update={
            "budget": source.reservations[0].budget.model_copy(update={"max_tool_calls": 1}),
            "actual": None,
            "actual_provider_calls": None,
            "state": "UNKNOWN",
        }
    )
    reservations = (held, *source.reservations[1:])
    result = source.result.model_copy(
        update={
            "usage_is_complete": False,
            "held_usage": reserved_usage(held.budget),
            "held_provider_calls": held.provider_calls,
        }
    )
    fields = {
        name: (
            reservations
            if name == "reservations"
            else result
            if name == "result"
            else getattr(source, name)
        )
        for name in OrchestrationRunRecord.model_fields
        if name != "fingerprint"
    }
    record = OrchestrationRunRecord.seal(**fields)
    return package_from_a38(capture_json(record), "held-reservation")


def operational_variant() -> tuple[PortableA3ReplayPackage, PortableA3ReplayPackage]:
    original_outer = json.loads(load_case("aligned"))
    changed = copy.deepcopy(original_outer["record"])
    changed["runtime_adapter"] = "langgraph-1.2.11"
    changed["completed_at"] = "2026-09-10T23:59:59+05:30"
    changed["result"]["usage"]["elapsed_seconds"] = 42
    changed_a38 = reseal_a38(changed)

    def build(a38: str) -> PortableA3ReplayPackage:
        request = request_from_capture(a38, request_id="a3.10:parity", policy=default_policy())
        a39 = capture_intelligence(assemble_opportunity_intelligence(request))
        return capture_a3_package(
            a38,
            a39,
            origin=CaptureOrigin.SYNTHETIC,
            source_reference="synthetic:a3.10/parity",
            fixture_builder_version=BUILDER,
            created_at=NOW,
        )

    return build(load_case("aligned")), build(changed_a38)


def full_a2_package() -> PortableA3ReplayPackage:
    snapshot, baseline_run = frozen_case()
    request = a38_request(symbol=snapshot.subject)
    old_pack = request.inventory.a2_pack
    baseline = old_pack.references[0]
    replacements = {
        "baseline.direction": baseline_run.direction.value,
        "baseline.opportunity_score": baseline_run.assessment.opportunity_score,
        "baseline.candidate_class": baseline_run.candidate_class.value,
    }
    facts = tuple(
        fact.model_copy(update={"value": replacements[fact.metric_id]}) for fact in baseline.facts
    )
    baseline = baseline.model_copy(
        update={
            "facts": facts,
            "checksum": digest([fact.model_dump(mode="json") for fact in facts]),
        }
    )
    pack = old_pack.model_copy(
        update={
            "evidence_fingerprint": snapshot.fingerprint,
            "deterministic_assessment_id": baseline_run.assessment.assessment_id,
            "references": (baseline, *old_pack.references[1:]),
        }
    )
    request = request.model_copy(
        update={
            "horizon": snapshot.horizon,
            "inventory": request.inventory.model_copy(update={"a2_pack": pack}),
        }
    )
    a38 = capture_json(run_serial(request, default_registry()))
    a39_request = request_from_capture(
        a38,
        request_id="a3.10:full-a2",
        policy=default_policy(),
    )
    a39 = capture_intelligence(assemble_opportunity_intelligence(a39_request))
    return capture_a3_package(
        a38,
        a39,
        case_json(CapturedBaselineCase(snapshot=snapshot, run_record=baseline_run)),
        origin=CaptureOrigin.SYNTHETIC,
        source_reference="synthetic:a2.10/full-case",
        fixture_builder_version=BUILDER,
        created_at=NOW,
    )
